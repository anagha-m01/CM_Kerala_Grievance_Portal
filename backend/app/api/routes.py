import re
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.core.config import get_settings
from app.core.ratelimit import rate_limit
from app.core.security import current_user, require_roles, hash_password, verify_password, create_token
from app.db.session import get_db
from app.models.entities import (
    User, Department, Grievance, GrievanceHistory, DepartmentAssignment,
    Attachment, ActionReport, CitizenFeedback, ContactEnquiry, utc_now
)
from app.schemas.inputs import (
    RegisterIn, LoginIn, ContactIn, GrievanceIn, ReviewIn, AssignIn,
    RemarkIn, StatusIn, ReportIn, ReportReviewIn, FeedbackIn, AIIn
)
from app.services.helpers import get_case, case_data, history_event, stats_for, public_tracking
from app.services.ai import analyze

router = APIRouter(prefix='/api')


def base_case_query():
    return select(Grievance).options(
        selectinload(Grievance.department), selectinload(Grievance.history).selectinload(GrievanceHistory.actor),
        selectinload(Grievance.attachments), selectinload(Grievance.reports), selectinload(Grievance.feedback),
    )


def case_by_id(db, id: int, user: User) -> Grievance:
    g = db.scalars(base_case_query().where(Grievance.id == id)).first()
    if not g:
        raise HTTPException(404, 'Grievance not found')
    from app.services.helpers import assert_access
    assert_access(g, user)
    return g


@router.get('/health')
def health():
    return {'status': 'ok', 'service': 'CM Kerala recruitment prototype'}


@router.post('/auth/register', status_code=201, dependencies=[Depends(rate_limit('register', 5))])
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(409, 'Email already registered')
    user = User(name=body.name.strip(), email=body.email.lower(), mobile=body.mobile, password_hash=hash_password(body.password), role='citizen')
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'id': user.id, 'email': user.email, 'message': 'Account created'}


@router.post('/auth/login', dependencies=[Depends(rate_limit('login', 10))])
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, 'Incorrect email or password')
    return {'access_token': create_token(user), 'token_type': 'bearer', 'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}}


@router.post('/auth/logout')
def logout():
    # Bearer tokens are stateless; client removes the session token. Tokens also expire.
    return {'message': 'Remove the session token on the client to log out'}


@router.get('/auth/me')
def me(user: User = Depends(current_user)):
    return {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role, 'department_id': user.department_id}


@router.get('/departments')
def departments(db: Session = Depends(get_db)):
    return [{'id': d.id, 'name': d.name, 'description': d.description} for d in db.scalars(select(Department).order_by(Department.name)).all()]


@router.get('/officers')
def officers(department_id: int | None = None, user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    stmt = select(User).where(User.role == 'officer')
    if department_id:
        stmt = stmt.where(User.department_id == department_id)
    return [{'id': u.id, 'name': u.name, 'department_id': u.department_id} for u in db.scalars(stmt).all()]


@router.post('/contact', status_code=201)
def contact(body: ContactIn, db: Session = Depends(get_db)):
    db.add(ContactEnquiry(**body.model_dump()))
    db.commit()
    return {'message': 'Enquiry received (demo only; no official government service)'}


@router.post('/ai/analyze', dependencies=[Depends(rate_limit('ai', 10))])
def ai_analyze(body: AIIn, user: User = Depends(require_roles('citizen', 'cmo')), db: Session = Depends(get_db)):
    names = list(db.scalars(select(Department.name)).all())
    return analyze(body.description, names)


@router.post('/grievances', status_code=201)
def create_grievance(body: GrievanceIn, user: User = Depends(require_roles('citizen')), db: Session = Depends(get_db)):
    # Random reference avoids collisions under concurrent submissions.
    reference_no = f'CMK-{utc_now().year}-{uuid4().hex[:10].upper()}'
    g = Grievance(
        reference_no=reference_no, citizen_id=user.id, district=body.district, category=body.category,
        subject=body.subject.strip(), description=body.description.strip(), status='Submitted', priority='Medium',
        ai_summary=body.ai_summary, ai_department=body.ai_department, ai_category=body.ai_category,
        ai_priority=body.ai_priority, ai_fallback=body.ai_fallback,
        due_at=utc_now() + timedelta(days=7),
    )
    db.add(g)
    db.flush()
    db.add(GrievanceHistory(grievance_id=g.id, old_status=None, new_status='Submitted', action='Submitted', remark='Grievance received', actor_id=user.id))
    db.commit()
    return {'id': g.id, 'reference_no': g.reference_no, 'status': g.status}


@router.get('/grievances/track/{reference_no}')
def track(reference_no: str, db: Session = Depends(get_db)):
    g = db.scalars(base_case_query().where(Grievance.reference_no == reference_no.upper())).first()
    if not g:
        raise HTTPException(404, 'Reference not found')
    return public_tracking(g)


@router.get('/grievances')
def list_grievances(
    district: str | None = None, category: str | None = None, priority: str | None = None,
    status: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)
):
    stmt = base_case_query().order_by(Grievance.created_at.desc())
    if user.role == 'citizen':
        stmt = stmt.where(Grievance.citizen_id == user.id)
    elif user.role == 'officer':
        stmt = stmt.where(Grievance.officer_id == user.id, Grievance.department_id == user.department_id)
    elif user.role != 'cmo':
        raise HTTPException(403, 'Unknown role')
    if district:
        stmt = stmt.where(Grievance.district == district)
    if category:
        stmt = stmt.where(Grievance.category == category)
    if priority:
        stmt = stmt.where(Grievance.priority == priority)
    if status:
        stmt = stmt.where(Grievance.status == status)
    return [case_data(g, user) for g in db.scalars(stmt).all()]


@router.get('/grievances/{grievance_id}')
def grievance_details(grievance_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return case_data(case_by_id(db, grievance_id, user), user, full=True)


@router.post('/grievances/{grievance_id}/review')
def review(grievance_id: int, body: ReviewIn, user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if g.status not in ('Submitted', 'Reopened', 'Under Review'):
        raise HTTPException(409, 'Only submitted or reopened grievances can be reviewed')
    if body.priority:
        g.priority = body.priority
    history_event(db, g, user, 'CMO Review', body.remark or 'CMO started reviewing this grievance', 'Under Review', True)
    db.commit()
    return {'status': g.status, 'priority': g.priority}


@router.post('/grievances/{grievance_id}/assign')
def assign(grievance_id: int, body: AssignIn, user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if g.status not in ('Under Review', 'Reopened'):
        raise HTTPException(409, 'CMO must review the case before assignment')
    department = db.get(Department, body.department_id)
    officer = db.get(User, body.officer_id)
    if not department or not officer or officer.role != 'officer' or officer.department_id != department.id:
        raise HTTPException(422, 'Officer must belong to the selected department')
    g.department_id, g.officer_id = department.id, officer.id
    db.add(DepartmentAssignment(grievance_id=g.id, department_id=department.id, officer_id=officer.id, assigned_by=user.id))
    history_event(db, g, user, 'Assigned to Department', body.remark or f'Assigned to {department.name}', public=True)
    db.commit()
    return {'status': g.status, 'department': department.name, 'officer': officer.name}


@router.patch('/grievances/{grievance_id}/status')
def update_status(grievance_id: int, body: StatusIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if user.role == 'officer':
        if body.status != 'In Progress' or g.status not in ('Under Review', 'Reopened'):
            raise HTTPException(409, 'Officer may only start investigation after assignment')
    elif user.role == 'cmo':
        if body.status == 'Under Review' and g.status not in ('Submitted', 'Reopened'):
            raise HTTPException(409, 'Invalid review transition')
        if body.status == 'Reopened' and g.status != 'Resolved':
            raise HTTPException(409, 'Only resolved cases can be reopened')
        if body.status == 'Resolved':
            raise HTTPException(409, 'Resolve cases through CMO action-report review')
        if body.status not in ('Under Review', 'Reopened'):
            raise HTTPException(422, 'Unsupported CMO status transition')
    elif user.role == 'citizen':
        if body.status != 'Reopened' or g.status != 'Resolved':
            raise HTTPException(403, 'Citizen can only reopen a resolved grievance')
    else:
        raise HTTPException(403, 'Unauthorized role')
    history_event(db, g, user, 'Status Updated', body.remark, body.status)
    db.commit()
    return {'status': g.status}


@router.post('/grievances/{grievance_id}/remarks')
def remark(grievance_id: int, body: RemarkIn, user: User = Depends(require_roles('cmo', 'officer')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    history_event(db, g, user, 'Administrative Remark', body.remark, public=body.is_public)
    db.commit()
    return {'message': 'Remark added'}


@router.post('/grievances/{grievance_id}/escalate')
def escalate(grievance_id: int, body: RemarkIn, user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if g.status == 'Resolved':
        raise HTTPException(409, 'Resolved cases cannot be escalated')
    g.escalated = True
    history_event(db, g, user, 'Escalated', body.remark, public=body.is_public)
    db.commit()
    return {'escalated': True}


@router.post('/grievances/{grievance_id}/reports', status_code=201)
def create_report(grievance_id: int, body: ReportIn, user: User = Depends(require_roles('officer')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if g.status != 'In Progress':
        raise HTTPException(409, 'Start investigation before submitting a report')
    existing = db.scalar(select(ActionReport).where(ActionReport.grievance_id == g.id, ActionReport.review_status == 'pending'))
    if existing:
        raise HTTPException(409, 'The previous report is awaiting CMO review')
    report = ActionReport(grievance_id=g.id, officer_id=user.id, findings=body.findings, action_taken=body.action_taken)
    db.add(report)
    history_event(db, g, user, 'Action Report Submitted', 'Department submitted an action-taken report for CMO review', public=True)
    db.commit()
    return {'id': report.id, 'review_status': report.review_status}


@router.post('/grievances/{grievance_id}/reports/{report_id}/review')
def review_report(grievance_id: int, report_id: int, body: ReportReviewIn, user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    report = db.get(ActionReport, report_id)
    if not report or report.grievance_id != g.id:
        raise HTTPException(404, 'Report not found')
    if report.review_status != 'pending' or g.status != 'In Progress':
        raise HTTPException(409, 'Report is not awaiting review')
    if body.decision not in ('approve', 'request_changes'):
        raise HTTPException(422, 'Choose approve or request_changes')
    report.review_status = 'approved' if body.decision == 'approve' else 'changes_requested'
    report.review_remark, report.reviewed_by, report.reviewed_at = body.remark, user.id, utc_now()
    if body.decision == 'approve':
        history_event(db, g, user, 'CMO Approved Resolution', body.remark, 'Resolved', True)
    else:
        history_event(db, g, user, 'CMO Requested Further Action', body.remark, public=True)
    db.commit()
    return {'status': g.status, 'report_review_status': report.review_status}


@router.post('/grievances/{grievance_id}/feedback', status_code=201)
def feedback(grievance_id: int, body: FeedbackIn, user: User = Depends(require_roles('citizen')), db: Session = Depends(get_db)):
    g = get_case(db, grievance_id, user)
    if g.status != 'Resolved':
        raise HTTPException(409, 'Feedback is available only after resolution')
    if db.scalar(select(CitizenFeedback).where(CitizenFeedback.grievance_id == g.id, CitizenFeedback.citizen_id == user.id)):
        raise HTTPException(409, 'Feedback already submitted')
    db.add(CitizenFeedback(grievance_id=g.id, citizen_id=user.id, **body.model_dump()))
    db.commit()
    return {'message': 'Feedback saved'}


ALLOWED_MIME = {'application/pdf': b'%PDF-', 'image/png': b'\x89PNG\r\n\x1a\n', 'image/jpeg': b'\xff\xd8\xff'}


@router.post('/grievances/{grievance_id}/attachments', status_code=201)
async def upload_attachment(
    grievance_id: int, file: UploadFile = File(...), kind: str = Query('support'),
    user: User = Depends(current_user), db: Session = Depends(get_db)
):
    g = get_case(db, grievance_id, user)
    if kind not in ('support', 'report') or (kind == 'report' and user.role != 'officer'):
        raise HTTPException(403, 'Invalid attachment type')
    if kind == 'report' and g.status != 'In Progress':
        raise HTTPException(409, 'Report attachments require an in-progress grievance')
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(415, 'Only PNG, JPG and PDF files are supported')
    # Read only MAX+1 bytes to prevent oversized body persistence.
    content = await file.read(get_settings().MAX_FILE_SIZE + 1)
    if len(content) > get_settings().MAX_FILE_SIZE:
        raise HTTPException(413, 'File exceeds 2 MB limit')
    if not content.startswith(ALLOWED_MIME[file.content_type]):
        raise HTTPException(415, 'File contents do not match the declared type')
    safe_filename = re.sub(r'[^A-Za-z0-9._-]', '_', Path((file.filename or 'attachment').replace('\\', '/')).name)[:200]
    attachment = Attachment(grievance_id=g.id, filename=safe_filename, mime_type=file.content_type, size=len(content), data=content, uploaded_by=user.id, kind=kind)
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return {'id': attachment.id, 'filename': attachment.filename, 'size': attachment.size}


@router.get('/attachments/{attachment_id}')
def download_attachment(attachment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    attachment = db.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(404, 'Attachment not found')
    g = get_case(db, attachment.grievance_id, user)
    if attachment.kind == 'report' and user.role == 'citizen' and g.status != 'Resolved':
        raise HTTPException(403, 'Officer report attachments are unavailable before resolution')
    return StreamingResponse(
        BytesIO(attachment.data), media_type=attachment.mime_type,
        headers={'Content-Disposition': f'attachment; filename="{attachment.filename}"', 'X-Content-Type-Options': 'nosniff'}
    )


@router.get('/cmo/stats')
def cmo_stats(user: User = Depends(require_roles('cmo')), db: Session = Depends(get_db)):
    return stats_for(db.scalars(select(Grievance).options(selectinload(Grievance.department))).all())


@router.get('/citizen/stats')
def citizen_stats(user: User = Depends(require_roles('citizen')), db: Session = Depends(get_db)):
    return stats_for(db.scalars(select(Grievance).options(selectinload(Grievance.department)).where(Grievance.citizen_id == user.id)).all())


@router.get('/officer/stats')
def officer_stats(user: User = Depends(require_roles('officer')), db: Session = Depends(get_db)):
    return stats_for(db.scalars(select(Grievance).options(selectinload(Grievance.department)).where(Grievance.officer_id == user.id, Grievance.department_id == user.department_id)).all())