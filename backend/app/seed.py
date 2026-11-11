"""Run `python -m app.seed` after `alembic upgrade head`.
Requires DEMO_*_PASSWORD in .env. Only fictional sample data is created.
"""
from datetime import timedelta
from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Department, User, Grievance, GrievanceHistory, utc_now

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


def seed():
    settings = get_settings()
    if not all((settings.DEMO_ADMIN_PASSWORD, settings.DEMO_OFFICER_PASSWORD, settings.DEMO_CITIZEN_PASSWORD)):
        raise RuntimeError('Set DEMO_ADMIN_PASSWORD, DEMO_OFFICER_PASSWORD and DEMO_CITIZEN_PASSWORD in .env before running seed.')
    with SessionLocal() as db:
        for name, desc in DEPARTMENTS:
            if not db.scalar(select(Department).where(Department.name == name)):
                db.add(Department(name=name, description=desc))
        db.commit()
        public_works = db.scalar(select(Department).where(Department.name == 'Public Works Department'))
        health = db.scalar(select(Department).where(Department.name == 'Health Department'))
        accounts = [
            ('CMO Demo Admin', 'cmo@example.com', 'cmo', None, settings.DEMO_ADMIN_PASSWORD),
            ('Demo PWD Officer', 'officer@example.com', 'officer', public_works.id, settings.DEMO_OFFICER_PASSWORD),
            ('Demo Citizen', 'citizen@example.com', 'citizen', None, settings.DEMO_CITIZEN_PASSWORD),
        ]
        for name, email, role, department_id, password in accounts:
            if not db.scalar(select(User).where(User.email == email)):
                db.add(User(name=name, email=email, mobile='9000000000', role=role, department_id=department_id, password_hash=hash_password(password)))
        db.commit()
        citizen = db.scalar(select(User).where(User.email == 'citizen@example.com'))
        if not db.scalar(select(Grievance).where(Grievance.reference_no == 'CMK-DEMO-0001')):
            examples = [
                ('CMK-DEMO-0001', 'Thrissur', 'Road Infrastructure', 'Potholes near sample junction', 'Fictional example: Potholes near the sample junction are making bus travel difficult.', 'Submitted', None),
                ('CMK-DEMO-0002', 'Kozhikode', 'Healthcare', 'Clinic equipment needs repair', 'Fictional example: A public clinic has a broken examination table.', 'Under Review', None),
            ]
            for ref, district, category, subject, desc, status, dept_id in examples:
                g = Grievance(reference_no=ref, citizen_id=citizen.id, district=district, category=category, subject=subject,
                              description=desc, status=status, department_id=dept_id, due_at=utc_now() + timedelta(days=7))
                db.add(g)
                db.flush()
                db.add(GrievanceHistory(grievance_id=g.id, old_status=None, new_status='Submitted', action='Seeded Demo', remark='Fictional sample case', actor_id=citizen.id))
                if status == 'Under Review':
                    cmo = db.scalar(select(User).where(User.role == 'cmo'))
                    db.add(GrievanceHistory(grievance_id=g.id, old_status='Submitted', new_status='Under Review', action='CMO Review', remark='Under initial review', actor_id=cmo.id))
            db.commit()
    print('Demo departments, users, and fictional grievances are ready.')
    print('Demo emails: cmo@example.com / officer@example.com / citizen@example.com')
    print('Passwords are the DEMO_*_PASSWORD values from your .env file (never print or commit them).')


if __name__ == '__main__':
    seed()
