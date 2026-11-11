from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Boolean, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    mobile: Mapped[str | None] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default='citizen', index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    department = relationship('Department', foreign_keys=[department_id])


class Department(Base):
    __tablename__ = 'departments'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str] = mapped_column(Text, default='')


class Grievance(Base):
    __tablename__ = 'grievances'
    id: Mapped[int] = mapped_column(primary_key=True)
    reference_no: Mapped[str] = mapped_column(String(45), unique=True, index=True)
    citizen_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    district: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default='Medium', index=True)
    status: Mapped[str] = mapped_column(String(25), default='Submitted', index=True)
    department_id: Mapped[int | None] = mapped_column(ForeignKey('departments.id'))
    officer_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_department: Mapped[str | None] = mapped_column(String(150))
    ai_category: Mapped[str | None] = mapped_column(String(120))
    ai_priority: Mapped[str | None] = mapped_column(String(10))
    ai_fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    citizen = relationship('User', foreign_keys=[citizen_id])
    department = relationship('Department', foreign_keys=[department_id])
    officer = relationship('User', foreign_keys=[officer_id])
    history = relationship('GrievanceHistory', back_populates='grievance', order_by='GrievanceHistory.created_at')
    assignments = relationship('DepartmentAssignment', back_populates='grievance')
    attachments = relationship('Attachment', back_populates='grievance')
    reports = relationship('ActionReport', back_populates='grievance')
    feedback = relationship('CitizenFeedback', back_populates='grievance')


class GrievanceHistory(Base):
    __tablename__ = 'grievance_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    grievance_id: Mapped[int] = mapped_column(ForeignKey('grievances.id'), index=True)
    old_status: Mapped[str | None] = mapped_column(String(25))
    new_status: Mapped[str] = mapped_column(String(25))
    action: Mapped[str] = mapped_column(String(80))
    remark: Mapped[str] = mapped_column(Text, default='')
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    grievance = relationship('Grievance', back_populates='history')
    actor = relationship('User')


class DepartmentAssignment(Base):
    __tablename__ = 'department_assignments'
    id: Mapped[int] = mapped_column(primary_key=True)
    grievance_id: Mapped[int] = mapped_column(ForeignKey('grievances.id'), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))
    officer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    assigned_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    grievance = relationship('Grievance', back_populates='assignments')


class Attachment(Base):
    __tablename__ = 'attachments'
    id: Mapped[int] = mapped_column(primary_key=True)
    grievance_id: Mapped[int] = mapped_column(ForeignKey('grievances.id'), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(30), default='support')
    data: Mapped[bytes] = mapped_column(LargeBinary)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    grievance = relationship('Grievance', back_populates='attachments')


class ActionReport(Base):
    __tablename__ = 'action_reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    grievance_id: Mapped[int] = mapped_column(ForeignKey('grievances.id'), index=True)
    officer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    findings: Mapped[str] = mapped_column(Text)
    action_taken: Mapped[str] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(30), default='pending')
    review_remark: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    grievance = relationship('Grievance', back_populates='reports')


class CitizenFeedback(Base):
    __tablename__ = 'citizen_feedback'
    __table_args__ = (UniqueConstraint('grievance_id', 'citizen_id', name='unique_feedback_per_case'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    grievance_id: Mapped[int] = mapped_column(ForeignKey('grievances.id'), index=True)
    citizen_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    grievance = relationship('Grievance', back_populates='feedback')


class ContactEnquiry(Base):
    __tablename__ = 'contact_enquiries'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
