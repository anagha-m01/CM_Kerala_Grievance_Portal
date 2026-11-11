"""End-to-end API test with a local in-memory SQLite database (no paid services)."""
from datetime import timedelta
import os
os.environ.setdefault('JWT_SECRET', 'TEST_ONLY_NOT_FOR_DEPLOYMENT_SECRET_12345678901234567890')
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import Base, get_db
from app.models.entities import User, Department
from app.core.security import hash_password
from app.models import entities  # noqa


@pytest.fixture
def setup_app():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override_db():
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    with TestSession() as db:
        d = Department(name='Public Works Department', description='Public roads')
        db.add(d)
        db.flush()
        db.add_all([
            User(name='CMO Test', email='cmo@test.com', mobile='9000000000', role='cmo', password_hash=hash_password('testpassword1')),
            User(name='Officer Test', email='officer@test.com', mobile='9000000001', role='officer', department_id=d.id, password_hash=hash_password('testpassword2')),
        ])
        db.commit()
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def login(client, email, password):
    response = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert response.status_code == 200, response.text
    return {'Authorization': 'Bearer ' + response.json()['access_token']}


def test_full_grievance_lifecycle_and_role_access(setup_app):
    c = setup_app
    r = c.post('/api/auth/register', json={'name': 'Test Citizen', 'email': 'citizen@test.com', 'mobile': '9000000002', 'password': 'testpassword3'})
    assert r.status_code == 201, r.text
    citizen = login(c, 'citizen@test.com', 'testpassword3')
    cmo = login(c, 'cmo@test.com', 'testpassword1')
    officer = login(c, 'officer@test.com', 'testpassword2')

    # A citizen submits a grievance. Other citizens cannot view its private details.
    r = c.post('/api/grievances', json={
        'district': 'Thrissur', 'category': 'Road Infrastructure',
        'subject': 'Broken sample bridge railing', 'description': 'A fictional bridge railing is damaged in the sample town.'
    }, headers=citizen)
    assert r.status_code == 201, r.text
    id = r.json()['id']
    ref = r.json()['reference_no']
    assert c.get(f'/api/grievances/track/{ref}').json()['status'] == 'Submitted'
    assert 'description' not in c.get(f'/api/grievances/track/{ref}').json()
    assert c.get(f'/api/grievances/{id}', headers=officer).status_code == 403
    assert c.post(f'/api/grievances/{id}/review', json={}, headers=citizen).status_code == 403

    r = c.post(f'/api/grievances/{id}/review', json={'priority': 'High', 'remark': 'Review started'}, headers=cmo)
    assert r.status_code == 200, r.text
    officers = c.get('/api/officers', headers=cmo).json()
    departments = c.get('/api/departments').json()
    r = c.post(f'/api/grievances/{id}/assign', json={'department_id': departments[0]['id'], 'officer_id': officers[0]['id'], 'remark': 'Assigned'}, headers=cmo)
    assert r.status_code == 200, r.text
    assert len(c.get('/api/grievances', headers=officer).json()) == 1
    r = c.patch(f'/api/grievances/{id}/status', json={'status':'In Progress', 'remark':'Inspected fictional site'}, headers=officer)
    assert r.status_code == 200, r.text

    report = c.post(f'/api/grievances/{id}/reports', json={'findings':'Test site inspected', 'action_taken':'Fictional repair completed'}, headers=officer)
    assert report.status_code == 201, report.text
    report_id = report.json()['id']
    r = c.post(f'/api/grievances/{id}/reports/{report_id}/review', json={'decision': 'approve', 'remark': 'Demo resolution approved'}, headers=cmo)
    assert r.status_code == 200, r.text
    details = c.get(f'/api/grievances/{id}', headers=citizen).json()
    assert details['status'] == 'Resolved'
    assert len(details['history']) >= 5
    assert all(h['is_public'] for h in details['history'])
    assert c.get('/api/cmo/stats', headers=cmo).json()['resolved'] == 1
    assert c.post(f'/api/grievances/{id}/feedback', json={'rating': 5, 'comment': 'Fictional case resolved'}, headers=citizen).status_code == 201
    assert c.patch(f'/api/grievances/{id}/status', json={'status': 'Reopened', 'remark':'The issue recurred in the fictional scenario'}, headers=citizen).status_code == 200
    assert c.get(f'/api/grievances/{id}', headers=citizen).json()['status'] == 'Reopened'


def test_contact_and_fallback(setup_app):
    c = setup_app
    response = c.post('/api/contact', json={'name': 'Demo Person', 'email': 'demo@test.com', 'subject': 'General enquiry', 'message': 'Fictional message for testing'})
    assert response.status_code == 201
    c.post('/api/auth/register', json={'name': 'Test Citizen', 'email': 'citizen@test.com', 'mobile': '9000000002', 'password': 'testpassword3'})
    citizen = login(c, 'citizen@test.com', 'testpassword3')
    res = c.post('/api/ai/analyze', json={'description': 'A fictional damaged road needs inspection urgently'}, headers=citizen)
    assert res.status_code == 200
    assert res.json()['source'] in ('gemini', 'fallback')
    assert 'summary' in res.json()


def test_internal_remarks_and_file_access(setup_app):
    c = setup_app
    c.post('/api/auth/register', json={
        'name': 'File Test Citizen', 'email': 'files@test.com', 'mobile': '9000000004', 'password': 'testpassword4'
    })
    c.post('/api/auth/register', json={
        'name': 'Other Citizen', 'email': 'other@test.com', 'mobile': '9000000005', 'password': 'testpassword5'
    })
    owner = login(c, 'files@test.com', 'testpassword4')
    other = login(c, 'other@test.com', 'testpassword5')
    cmo = login(c, 'cmo@test.com', 'testpassword1')
    r = c.post('/api/grievances', json={
        'district': 'Thrissur', 'category': 'Road Infrastructure', 'subject': 'Fictional road damage',
        'description': 'This is only a fictional damaged-road scenario for internal testing.'
    }, headers=owner)
    assert r.status_code == 201
    id, ref = r.json()['id'], r.json()['reference_no']
    private = c.post(f'/api/grievances/{id}/remarks', json={'remark': 'Confidential case review note', 'is_public': False}, headers=cmo)
    assert private.status_code == 200
    tracking = c.get(f'/api/grievances/track/{ref}').json()
    assert all('Confidential' not in h['remark'] for h in tracking['history'])
    assert all('Confidential' not in h['remark'] for h in c.get(f'/api/grievances/{id}', headers=owner).json()['history'])

    file_up = c.post(f'/api/grievances/{id}/attachments', headers=owner,
                     files={'file': ('sample.pdf', b'%PDF-1.4\n%%EOF', 'application/pdf')})
    assert file_up.status_code == 201, file_up.text
    attachment_id = file_up.json()['id']
    assert c.get(f'/api/attachments/{attachment_id}', headers=owner).status_code == 200
    assert c.get(f'/api/attachments/{attachment_id}', headers=other).status_code == 403
    bad_type = c.post(f'/api/grievances/{id}/attachments', headers=owner,
                      files={'file': ('wrong.pdf', b'not a real PDF', 'application/pdf')})
    assert bad_type.status_code == 415
    too_big = c.post(f'/api/grievances/{id}/attachments', headers=owner,
                     files={'file': ('large.pdf', b'%PDF-' + b'x' * (2*1024*1024), 'application/pdf')})
    assert too_big.status_code == 413
