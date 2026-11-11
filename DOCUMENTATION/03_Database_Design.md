# 03 — Database Design

## Entity relationship diagram

See [`diagrams/database_er.png`](diagrams/database_er.png), also available as DOT source. SQLAlchemy model definitions live at `backend/app/models/entities.py`; initial Alembic migration at `backend/alembic/versions/0001_initial.py`.

## Tables

| Table | Key columns | Purpose |
|---|---|---|
| `users` | `id` PK, `email` unique, `role`, `department_id` FK | Citizen / CMO / officer login and accountability |
| `departments` | `id` PK, `name` unique | Sample public service departments |
| `grievances` | `id` PK, `reference_no` unique, `citizen_id` FK, `department_id` FK, `officer_id` FK, district, category, status, priority, due date, AI suggestion columns | Core case records |
| `grievance_history` | `id` PK, `grievance_id` FK, `actor_id` FK, old/new statuses, timestamp, `is_public`, action, remark | Traceable record of all stages and remarks |
| `department_assignments` | `id` PK, `grievance_id`, `department_id`, `officer_id`, `assigned_by` FK, timestamp | Assignment history (including reassignment) |
| `attachments` | `id` PK, `grievance_id` FK, `data` binary, MIME, size, uploader, kind | Demo file upload and retrieval |
| `action_reports` | `id` PK, `grievance_id` FK, `officer_id` FK, findings, action, review status, review actor/time | Investigation records awaiting CMO review |
| `citizen_feedback` | `id` PK, `grievance_id` FK, `citizen_id` FK, rating, comment | Resolution feedback, once per citizen per grievance |
| `contact_enquiries` | `id` PK, email, subject, message, timestamp | Public contact form persistence |

## Relationships

- Department 1:N officers; citizen user 1:N grievances.
- Grievance N:1 citizen; N:1 current department; N:1 current officer.
- Grievance 1:N history rows, assignments, attachments and action reports.
- Grievance 1:N feedback rows (unique combination of grievance + citizen).
- History row N:1 responsible user; action report N:1 submitting officer.

## Status machine

1. `Submitted` → `Under Review` (CMO)
2. `Under Review` → `In Progress` (assigned officer; assignment is recorded separately)
3. `In Progress` → `Resolved` (CMO approves a pending officer report)
4. `Resolved` → `Reopened` (citizen owner or CMO)
5. `Reopened` → `Under Review` (CMO) → `In Progress` (officer)

An action report can be `pending`, `approved`, or `changes_requested`. Those are **report review states**, not extra grievance statuses. Officer/CMO remarks create history events without changing grievance status. Every transition is recorded with actor and timestamp.

## Trade-offs

- The 7-day `due_at` is a fictional demonstration default; production needs department/category-based SLA settings and scheduled notifications.
- PostgreSQL `BYTEA` storage for files <=2 MB is intentionally simple and bounded; external object storage is better for large-scale production.
- The schema uses SQLAlchemy models as the source of truth for the initial migration. Later changes should be explicit Alembic revisions.
- Indexes on email, reference number, status, priority, district, category and key foreign keys support prototype queries.
- Use Neon PostgreSQL for hosted persistence; SQLite test database ensures tests run without external services.
