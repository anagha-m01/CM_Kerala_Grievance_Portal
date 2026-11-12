"""Additional tests: AI success/failure paths, cross-department isolation,
invalid workflow transitions, escalation/overdue and rate limiting.

Reuses the in-memory SQLite `setup_app` fixture from test_workflow.py.
"""
from datetime import timedelta
from types import SimpleNamespace

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.entities import Department, Grievance, User, utc_now
from test_workflow import login, setup_app  # noqa: F401  (fixture re-used)


def db_session():
    """A session on the same in-memory database the test client uses."""
    return next(app.dependency_overrides[get_db]())


def register_citizen(c, email='citizen@test.com', password='testpassword3'):
    r = c.post('/api/auth/register', json={'name': 'Test Citizen', 'email': email, 'mobile': '9000000002', 'password': password})
    assert r.status_code == 201, r.text
    return login(c, email, password)


def submit_case(c, headers):
    r = c.post('/api/grievances', json={
        'district': 'Thrissur', 'category': 'Road Infrastructure', 'subject': 'Fictional road damage',
        'description': 'This is only a fictional damaged-road scenario for automated testing.'
    }, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()['id']


def fake_gemini(monkeypatch, response_text):
    """Pretend a Gemini key exists and make the SDK return `response_text`."""
    monkeypatch.setattr(get_settings(), 'GEMINI_API_KEY', 'test-key-not-real')

    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=response_text)

    class FakeClient:
        def __init__(self, api_key=None):
            self.models = FakeModels()

    monkeypatch.setattr('google.genai.Client', FakeClient)


def test_ai_success_path_uses_validated_model_output(setup_app, monkeypatch):
    c = setup_app
    fake_gemini(monkeypatch, '{"department": "Public Works Department", "category": "Road Infrastructure", '
                             '"priority": "High", "summary": "Fictional damaged road needs inspection."}')
    citizen = register_citizen(c)
    r = c.post('/api/ai/analyze', json={'description': 'A fictional damaged road is dangerous for scooters.'}, headers=citizen)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body['source'] == 'gemini'
    assert body['priority'] == 'High' and body['department'] == 'Public Works Department'
    assert body['warning'] is None


def test_ai_rejects_unknown_department_and_falls_back(setup_app, monkeypatch):
    c = setup_app
    fake_gemini(monkeypatch, '{"department": "Ministry of Imaginary Things", "category": "Other", '
                             '"priority": "Low", "summary": "x"}')
    citizen = register_citizen(c)
    r = c.post('/api/ai/analyze', json={'description': 'A fictional damaged road is dangerous for scooters.'}, headers=citizen)
    assert r.status_code == 200
    assert r.json()['source'] == 'fallback'
    assert 'NOT AI-generated' in r.json()['warning']


def test_ai_requires_login_and_blocks_officers(setup_app):
    c = setup_app
    body = {'description': 'A fictional damaged road is dangerous for scooters.'}
    assert c.post('/api/ai/analyze', json=body).status_code == 401
    officer = login(c, 'officer@test.com', 'testpassword2')
    assert c.post('/api/ai/analyze', json=body, headers=officer).status_code == 403


def test_officer_of_another_department_has_no_access(setup_app):
    c = setup_app
    with db_session() as db:
        other = Department(name='Health Department', description='Fictional health services')
        db.add(other)
        db.flush()
        db.add(User(name='Other Officer', email='other.officer@test.com', mobile='9000000009', role='officer',
                    department_id=other.id, password_hash=hash_password('testpassword6')))
        db.commit()
        other_id = other.id

    citizen = register_citizen(c)
    cmo = login(c, 'cmo@test.com', 'testpassword1')
    officer = login(c, 'officer@test.com', 'testpassword2')
    other_officer = login(c, 'other.officer@test.com', 'testpassword6')
    gid = submit_case(c, citizen)
    assert c.post(f'/api/grievances/{gid}/review', json={}, headers=cmo).status_code == 200

    pwd = next(d for d in c.get('/api/departments').json() if d['name'] == 'Public Works Department')
    officers = c.get('/api/officers', headers=cmo).json()
    pwd_officer = next(o for o in officers if o['department_id'] == pwd['id'])
    health_officer = next(o for o in officers if o['department_id'] == other_id)

    # An officer must belong to the selected department.
    mismatch = c.post(f'/api/grievances/{gid}/assign', headers=cmo,
                      json={'department_id': pwd['id'], 'officer_id': health_officer['id']})
    assert mismatch.status_code == 422

    assert c.post(f'/api/grievances/{gid}/assign', headers=cmo,
                  json={'department_id': pwd['id'], 'officer_id': pwd_officer['id']}).status_code == 200
    assert len(c.get('/api/grievances', headers=officer).json()) == 1
    assert c.get('/api/grievances', headers=other_officer).json() == []
    assert c.get(f'/api/grievances/{gid}', headers=other_officer).status_code == 403
    assert c.patch(f'/api/grievances/{gid}/status', headers=other_officer,
                   json={'status': 'In Progress', 'remark': 'Trying to hijack'}).status_code == 403


def test_invalid_workflow_transitions_are_rejected(setup_app):
    c = setup_app
    citizen = register_citizen(c)
    cmo = login(c, 'cmo@test.com', 'testpassword1')
    officer = login(c, 'officer@test.com', 'testpassword2')
    gid = submit_case(c, citizen)

    pwd = c.get('/api/departments').json()[0]
    officer_id = c.get('/api/officers', headers=cmo).json()[0]['id']
    assign_body = {'department_id': pwd['id'], 'officer_id': officer_id}

    # Assignment before CMO review is not allowed.
    assert c.post(f'/api/grievances/{gid}/assign', json=assign_body, headers=cmo).status_code == 409
    # The CMO cannot mark a case resolved directly; it must go through report review.
    assert c.patch(f'/api/grievances/{gid}/status', json={'status': 'Resolved', 'remark': 'skip ahead'}, headers=cmo).status_code == 409
    # Citizens may only reopen resolved cases, and feedback needs a resolved case.
    assert c.patch(f'/api/grievances/{gid}/status', json={'status': 'Reopened', 'remark': 'not resolved yet'}, headers=citizen).status_code == 403
    assert c.post(f'/api/grievances/{gid}/feedback', json={'rating': 5, 'comment': 'too early'}, headers=citizen).status_code == 409

    assert c.post(f'/api/grievances/{gid}/review', json={}, headers=cmo).status_code == 200
    assert c.post(f'/api/grievances/{gid}/assign', json=assign_body, headers=cmo).status_code == 200
    # Reports require the officer to start the investigation first.
    assert c.post(f'/api/grievances/{gid}/reports', json={'findings': 'Too early', 'action_taken': 'Nothing'}, headers=officer).status_code == 409
    # Officers can only move a case to "In Progress".
    assert c.patch(f'/api/grievances/{gid}/status', json={'status': 'Resolved', 'remark': 'officer shortcut'}, headers=officer).status_code == 409


def test_escalation_and_overdue_statistics(setup_app):
    c = setup_app
    citizen = register_citizen(c)
    cmo = login(c, 'cmo@test.com', 'testpassword1')
    gid = submit_case(c, citizen)
    assert c.get('/api/cmo/stats', headers=cmo).json()['overdue'] == 0

    with db_session() as db:
        db.get(Grievance, gid).due_at = utc_now() - timedelta(days=2)
        db.commit()

    stats = c.get('/api/cmo/stats', headers=cmo).json()
    assert stats['overdue'] == 1 and stats['pending'] == 1
    assert c.post(f'/api/grievances/{gid}/escalate', json={'remark': 'Delayed beyond SLA', 'is_public': False}, headers=cmo).status_code == 200
    detail = c.get(f'/api/grievances/{gid}', headers=cmo).json()
    assert detail['escalated'] is True and detail['is_overdue'] is True
    # Citizens may not escalate.
    assert c.post(f'/api/grievances/{gid}/escalate', json={'remark': 'Please hurry'}, headers=citizen).status_code == 403


def test_login_is_rate_limited(setup_app):
    c = setup_app
    codes = [c.post('/api/auth/login', json={'email': 'cmo@test.com', 'password': 'wrong-password'}).status_code
             for _ in range(11)]
    assert codes[:10] == [401] * 10
    assert codes[10] == 429