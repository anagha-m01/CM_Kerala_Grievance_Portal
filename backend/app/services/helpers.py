from collections import Counter
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.entities import Grievance, GrievanceHistory, User, Department


def assert_access(g: Grievance, user: User):
    if user.role == 'cmo':
        return
    if user.role == 'citizen' and g.citizen_id == user.id:
        return
    if user.role == 'officer' and g.officer_id == user.id and g.department_id == user.department_id:
        return
    raise HTTPException(403, 'You cannot access this grievance')


def get_case(db: Session, grievance_id: int, user: User) -> Grievance:
    g = db.get(Grievance, grievance_id)
    if not g:
        raise HTTPException(404, 'Grievance not found')
    assert_access(g, user)
    return g


def history_event(db: Session, g: Grievance, user: User, action: str, remark: str = '', new_status: str | None = None, public: bool = True):
    old = g.status
    if new_status:
        g.status = new_status
    db.add(GrievanceHistory(
        grievance_id=g.id, old_status=old, new_status=g.status,
        action=action, remark=remark, actor_id=user.id, is_public=public,
    ))


def overdue(g: Grievance) -> bool:
    if not g.due_at or g.status == 'Resolved':
        return False
    due = g.due_at.replace(tzinfo=timezone.utc) if g.due_at.tzinfo is None else g.due_at
    return due < datetime.now(timezone.utc)


def public_tracking(g: Grievance) -> dict:
    return {
        'reference_no': g.reference_no, 'status': g.status, 'department': g.department.name if g.department else 'Awaiting CMO assignment',
        'updated_at': g.updated_at, 'created_at': g.created_at,
        'history': [
            {'new_status': h.new_status, 'action': h.action, 'remark': h.remark, 'created_at': h.created_at}
            for h in g.history if h.is_public
        ],
    }


def case_data(g: Grievance, user: User, full: bool = False) -> dict:
    data = {
        'id': g.id, 'reference_no': g.reference_no, 'district': g.district, 'category': g.category,
        'subject': g.subject, 'description': g.description, 'priority': g.priority,
        'status': g.status, 'department_id': g.department_id,
        'department': g.department.name if g.department else None,
        'officer_id': g.officer_id, 'ai_summary': g.ai_summary,
        'ai_department': g.ai_department, 'ai_category': g.ai_category,
        'ai_priority': g.ai_priority, 'ai_fallback': g.ai_fallback,
        'escalated': g.escalated, 'is_overdue': overdue(g),
        'due_at': g.due_at, 'created_at': g.created_at, 'updated_at': g.updated_at,
    }
    if full:
        data['history'] = [
            {'id': h.id, 'old_status': h.old_status, 'new_status': h.new_status, 'action': h.action,
             'remark': h.remark, 'actor': h.actor.name, 'is_public': h.is_public, 'created_at': h.created_at}
            for h in g.history if user.role != 'citizen' or h.is_public
        ]
        data['attachments'] = [
            {'id': a.id, 'filename': a.filename, 'mime_type': a.mime_type, 'size': a.size, 'kind': a.kind}
            for a in g.attachments if user.role != 'citizen' or a.kind != 'report' or g.status == 'Resolved'
        ]
        data['reports'] = [
            {'id': r.id, 'findings': r.findings, 'action_taken': r.action_taken,
             'review_status': r.review_status, 'review_remark': r.review_remark, 'submitted_at': r.submitted_at}
            for r in g.reports
        ] if user.role != 'citizen' else [
            {'id': r.id, 'findings': r.findings, 'action_taken': r.action_taken, 'submitted_at': r.submitted_at}
            for r in g.reports if r.review_status == 'approved'
        ]
        data['feedback'] = [{'rating': f.rating, 'comment': f.comment} for f in g.feedback]
    return data


def stats_for(grievances: list[Grievance]) -> dict:
    return {
        'total': len(grievances),
        'pending': sum(g.status != 'Resolved' for g in grievances),
        'resolved': sum(g.status == 'Resolved' for g in grievances),
        'overdue': sum(overdue(g) for g in grievances),
        'by_district': [{'name': k, 'count': v} for k, v in Counter(g.district for g in grievances).most_common()],
        'by_department': [{'name': k, 'count': v} for k, v in Counter(g.department.name if g.department else 'Unassigned' for g in grievances).most_common()],
        'by_status': [{'name': k, 'count': v} for k, v in Counter(g.status for g in grievances).most_common()],
    }
