"""Seed fictional demonstration data.

Run `python -m app.seed` after `alembic upgrade head`.
Requires DEMO_*_PASSWORD in .env. Only fictional sample data is created.

The script is idempotent: departments, accounts and grievances are created only
if they do not already exist, so it is safe to run again on a deployed database.
"""
from datetime import timedelta

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import (
    ActionReport, CitizenFeedback, Department, DepartmentAssignment,
    Grievance, GrievanceHistory, User, utc_now,
)

DEPARTMENTS = [
    ('Public Works Department', 'Roads, public buildings and bridges'),
    ('Health Department', 'Public hospitals, healthcare services and facilities'),
    ('Education Department', 'Public education and school infrastructure'),
    ('Local Self Government Department', 'Local civic services, sanitation and public spaces'),
    ('Kerala Water Authority', 'Drinking water supply and pipelines'),
    ('Kerala State Electricity Board', 'Electricity distribution and supply issues'),
    ('Agriculture Department', 'Agricultural services and farmer support'),
    ('Police Department', 'Public safety and community policing'),
]

# One fictional officer per department so every department can receive assignments.
OFFICERS = [
    ('Demo PWD Officer', 'officer@example.com', 'Public Works Department'),
    ('Demo Health Officer', 'officer.health@example.com', 'Health Department'),
    ('Demo Education Officer', 'officer.education@example.com', 'Education Department'),
    ('Demo LSGD Officer', 'officer.lsgd@example.com', 'Local Self Government Department'),
    ('Demo Water Officer', 'officer.water@example.com', 'Kerala Water Authority'),
    ('Demo Electricity Officer', 'officer.kseb@example.com', 'Kerala State Electricity Board'),
    ('Demo Agriculture Officer', 'officer.agri@example.com', 'Agriculture Department'),
    ('Demo Police Officer', 'officer.police@example.com', 'Police Department'),
]

CITIZENS = [
    ('Demo Citizen', 'citizen@example.com'),
    ('Demo Citizen Two', 'citizen2@example.com'),
    ('Demo Citizen Three', 'citizen3@example.com'),
]

# Lifecycle states used to build realistic fictional history.
# submitted -> review -> assigned -> progress -> report_pending -> resolved -> reopened
STATE_ORDER = ['submitted', 'review', 'assigned', 'progress', 'report_pending', 'resolved', 'reopened']

# (reference, citizen index, district, category, subject, description, priority,
#  department (or None), state, age in days, escalated, feedback rating (or None))
CASES = [
    ('CMK-DEMO-0001', 0, 'Thrissur', 'Road Infrastructure', 'Potholes near sample junction',
     'Fictional example: Potholes near the sample junction are making bus travel difficult.', 'Medium', None, 'submitted', 2, False, None),
    ('CMK-DEMO-0002', 0, 'Kozhikode', 'Healthcare', 'Clinic equipment needs repair',
     'Fictional example: A public clinic has a broken examination table.', 'Medium', None, 'review', 3, False, None),
    ('CMK-DEMO-0003', 1, 'Ernakulam', 'Water Supply', 'Irregular drinking water supply',
     'Fictional example: Households in a sample ward receive drinking water only twice a week.', 'Medium', None, 'submitted', 1, False, None),
    ('CMK-DEMO-0004', 2, 'Thiruvananthapuram', 'Electricity', 'Frequent power cuts in sample colony',
     'Fictional example: A sample residential colony faces daily evening power cuts.', 'High', 'Kerala State Electricity Board', 'assigned', 4, False, None),
    ('CMK-DEMO-0005', 0, 'Kollam', 'Sanitation', 'Uncollected waste near sample market',
     'Fictional example: Waste has not been collected near the sample market for a week.', 'Medium', 'Local Self Government Department', 'progress', 6, False, None),
    ('CMK-DEMO-0006', 1, 'Malappuram', 'Road Infrastructure', 'Damaged sample bridge approach road',
     'Fictional example: The approach road to a sample bridge has deep cracks and is unsafe for two-wheelers.', 'High', 'Public Works Department', 'progress', 12, True, None),
    ('CMK-DEMO-0007', 2, 'Palakkad', 'Education', 'Leaking roof in sample school',
     'Fictional example: A sample government school classroom roof leaks during heavy rain.', 'Low', 'Education Department', 'resolved', 20, False, 4),
    ('CMK-DEMO-0008', 0, 'Kannur', 'Healthcare', 'Medicine shortage at sample hospital',
     'Fictional example: A sample public hospital reports a shortage of basic medicines.', 'High', 'Health Department', 'resolved', 15, False, 5),
    ('CMK-DEMO-0009', 1, 'Alappuzha', 'Water Supply', 'Leaking pipeline on sample road',
     'Fictional example: A water pipeline on a sample road has been leaking for several days.', 'Medium', 'Kerala Water Authority', 'resolved', 18, False, 3),
    ('CMK-DEMO-0010', 2, 'Kottayam', 'Electricity', 'Hanging power line near sample school',
     'Fictional example: A low-hanging power line near a sample school is a safety hazard.', 'High', 'Kerala State Electricity Board', 'report_pending', 9, False, None),
    ('CMK-DEMO-0011', 0, 'Idukki', 'Road Infrastructure', 'Landslide debris on sample hill road',
     'Fictional example: Debris from a small landslide is blocking part of a sample hill road.', 'Medium', 'Public Works Department', 'resolved', 25, False, 5),
    ('CMK-DEMO-0012', 1, 'Wayanad', 'Agriculture Support', 'Delay in sample crop damage assessment',
     'Fictional example: Farmers in a sample village are awaiting crop damage assessment after heavy rain.', 'Medium', 'Agriculture Department', 'assigned', 5, False, None),
    ('CMK-DEMO-0013', 2, 'Kasaragod', 'Public Safety', 'Poor street lighting near sample bus stand',
     'Fictional example: Street lights near a sample bus stand have not worked for weeks.', 'High', None, 'review', 8, True, None),
    ('CMK-DEMO-0014', 0, 'Pathanamthitta', 'Sanitation', 'Blocked drain near sample temple road',
     'Fictional example: A blocked drain causes waterlogging near a sample road.', 'Medium', 'Local Self Government Department', 'reopened', 22, False, None),
    ('CMK-DEMO-0015', 1, 'Thrissur', 'Healthcare', 'Long waiting time at sample clinic',
     'Fictional example: Patients at a sample clinic wait several hours for a basic consultation.', 'Low', None, 'submitted', 10, False, None),
    ('CMK-DEMO-0016', 2, 'Ernakulam', 'Education', 'Sample school lacks drinking water facility',
     'Fictional example: A sample school has no working drinking water facility for students.', 'Medium', 'Education Department', 'progress', 3, False, None),
    ('CMK-DEMO-0017', 0, 'Kozhikode', 'Road Infrastructure', 'Missing road signs at sample junction',
     'Fictional example: A busy sample junction has no road signs or markings.', 'High', 'Public Works Department', 'resolved', 30, False, 4),
    ('CMK-DEMO-0018', 1, 'Thiruvananthapuram', 'Water Supply', 'Contaminated water reported in sample area',
     'Fictional example: Residents of a sample area report muddy drinking water.', 'High', None, 'submitted', 0, False, None),
    ('CMK-DEMO-0019', 2, 'Malappuram', 'Public Safety', 'Speeding vehicles near sample school',
     'Fictional example: Vehicles speed past a sample school during opening and closing hours.', 'Medium', 'Police Department', 'progress', 7, False, None),
    ('CMK-DEMO-0020', 0, 'Palakkad', 'Agriculture Support', 'Seed distribution delay in sample block',
     'Fictional example: Subsidised seed distribution has been delayed in a sample block.', 'Low', 'Agriculture Department', 'resolved', 14, False, 5),
    ('CMK-DEMO-0021', 1, 'Kollam', 'Electricity', 'Faulty transformer in sample locality',
     'Fictional example: A transformer in a sample locality trips whenever it rains.', 'Medium', 'Kerala State Electricity Board', 'resolved', 11, False, None),
    ('CMK-DEMO-0022', 2, 'Kannur', 'Sanitation', 'Overflowing public bin at sample beach',
     'Fictional example: Public bins at a sample beach overflow at weekends.', 'Low', 'Local Self Government Department', 'assigned', 2, False, None),
]


def _get_or_create_user(db, name, email, role, password, department_id=None):
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(name=name, email=email, mobile='9000000000', role=role,
                    department_id=department_id, password_hash=hash_password(password))
        db.add(user)
        db.flush()
    return user


def _build_case(db, spec, citizens, cmo, officers_by_dept, departments):
    (ref, citizen_idx, district, category, subject, description, priority,
     dept_name, state, age_days, escalated, rating) = spec
    if db.scalar(select(Grievance).where(Grievance.reference_no == ref)):
        return False

    citizen = citizens[citizen_idx]
    reached = STATE_ORDER.index(state)
    # Start a little earlier than "age" so every history timestamp is in the past.
    created = utc_now() - timedelta(days=age_days, hours=2)
    minute = [0]

    def when(fraction):
        minute[0] += 7  # keeps events strictly ordered even for brand-new cases
        return created + timedelta(days=age_days * fraction, minutes=minute[0])

    department = departments[dept_name] if dept_name else None
    officer = officers_by_dept[dept_name] if dept_name else None

    g = Grievance(
        reference_no=ref, citizen_id=citizen.id, district=district, category=category,
        subject=subject, description=description, priority=priority, status='Submitted',
        escalated=escalated, due_at=created + timedelta(days=7), created_at=created, updated_at=created,
    )
    db.add(g)
    db.flush()

    def log(old, new, action, remark, actor, fraction, public=True):
        db.add(GrievanceHistory(
            grievance_id=g.id, old_status=old, new_status=new, action=action, remark=remark,
            actor_id=actor.id, is_public=public, created_at=when(fraction),
        ))

    log(None, 'Submitted', 'Seeded Demo', 'Fictional sample case', citizen, 0)
    status = 'Submitted'

    if reached >= 1:
        log(status, 'Under Review', 'CMO Review', 'Under initial review', cmo, 0.15)
        status = 'Under Review'
    if reached >= 2 and department:
        g.department_id, g.officer_id = department.id, officer.id
        db.add(DepartmentAssignment(
            grievance_id=g.id, department_id=department.id, officer_id=officer.id,
            assigned_by=cmo.id, assigned_at=when(0.25),
        ))
        log(status, status, 'Assigned to Department', f'Assigned to {department.name}', cmo, 0.25)
    if reached >= 3 and department:
        log(status, 'In Progress', 'Status Updated', 'Investigation started (fictional)', officer, 0.4)
        status = 'In Progress'
    if reached >= 4 and department:
        report = ActionReport(
            grievance_id=g.id, officer_id=officer.id,
            findings='Fictional site inspection completed; issue confirmed.',
            action_taken='Fictional corrective work completed by the department.',
            submitted_at=when(0.6),
        )
        db.add(report)
        log(status, status, 'Action Report Submitted',
            'Department submitted an action-taken report for CMO review', officer, 0.6)
        if reached >= 5:
            report.review_status = 'approved'
            report.review_remark = 'Fictional resolution approved.'
            report.reviewed_by, report.reviewed_at = cmo.id, when(0.8)
            log(status, 'Resolved', 'CMO Approved Resolution', 'Fictional resolution approved.', cmo, 0.8)
            status = 'Resolved'
    if reached >= 5 and rating is not None:
        db.add(CitizenFeedback(
            grievance_id=g.id, citizen_id=citizen.id, rating=rating,
            comment='Fictional feedback: thank you for the update.', created_at=when(0.9),
        ))
    if reached >= 6:
        log(status, 'Reopened', 'Status Updated', 'The issue recurred (fictional scenario)', citizen, 0.95)
        status = 'Reopened'

    g.status = status
    g.updated_at = when(0.95)
    return True


def seed():
    settings = get_settings()
    if not all((settings.DEMO_ADMIN_PASSWORD, settings.DEMO_OFFICER_PASSWORD, settings.DEMO_CITIZEN_PASSWORD)):
        raise RuntimeError('Set DEMO_ADMIN_PASSWORD, DEMO_OFFICER_PASSWORD and DEMO_CITIZEN_PASSWORD in .env before running seed.')

    with SessionLocal() as db:
        for name, desc in DEPARTMENTS:
            if not db.scalar(select(Department).where(Department.name == name)):
                db.add(Department(name=name, description=desc))
        db.commit()
        departments = {d.name: d for d in db.scalars(select(Department)).all()}

        cmo = _get_or_create_user(db, 'CMO Demo Admin', 'cmo@example.com', 'cmo', settings.DEMO_ADMIN_PASSWORD)
        officers_by_dept = {}
        for name, email, dept_name in OFFICERS:
            officers_by_dept[dept_name] = _get_or_create_user(
                db, name, email, 'officer', settings.DEMO_OFFICER_PASSWORD, departments[dept_name].id)
        citizens = [_get_or_create_user(db, name, email, 'citizen', settings.DEMO_CITIZEN_PASSWORD)
                    for name, email in CITIZENS]
        db.commit()

        created = sum(_build_case(db, spec, citizens, cmo, officers_by_dept, departments) for spec in CASES)
        db.commit()

    print(f'Demo departments, users and fictional grievances are ready ({created} new grievances created).')
    print('Demo emails: cmo@example.com, citizen@example.com (also citizen2/citizen3@example.com),')
    print('officer@example.com (Public Works) and officer.<health|education|lsgd|water|kseb|agri|police>@example.com')
    print('Passwords are the DEMO_*_PASSWORD values from your .env file (never print or commit them).')


if __name__ == '__main__':
    seed()