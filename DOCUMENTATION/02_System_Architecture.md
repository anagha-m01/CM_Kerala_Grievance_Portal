# 02 — System Architecture

## Context and layering

```
Public / Citizen / CMO / Department Officer
                  |
              React + Vite
          (pages, forms, charts)
                  |
             Axios / JSON
                  |
                FastAPI
          routes + Pydantic validation
            RBAC + JWT checks
          services / workflow logic
             /           \\
 SQLAlchemy + Alembic     Gemini SDK
          |                |
     Neon PostgreSQL     Gemini LLM API
  (data + small files)  (optional free tier)
```

Architecture diagram: [`diagrams/system_architecture.png`](diagrams/system_architecture.png); source DOT provided alongside it.

## Rationale

React/Vite supports a simple responsive SPA. FastAPI is an acceptable backend equivalent to the brief's Express example and allows Python-native AI integration. SQLAlchemy maps relational entities and relationships; Alembic handles schema migrations. Neon supplies standard hosted PostgreSQL. Binary uploads are stored in database only for this small demonstration; production should use dedicated object storage.

## Backend components

- `app/api/routes.py`: REST endpoint layer; dependencies enforce authentication and roles.
- `app/core/security.py`: password hashing, signed JWTs and RBAC dependencies.
- `app/models/entities.py`: database tables and relationships.
- `app/schemas/inputs.py`: Pydantic input validation, statuses and district choices.
- `app/services/helpers.py`: case visibility, status-history entries, stats and safe public tracking.
- `app/services/ai.py`: Gemini structured-response generation, exact-department validation and labelled fallback.
- `app/seed.py`: fictional sample accounts, departments and grievances.
- `alembic/`: schema migrations.

## Data flow: grievance submission

1. Citizen logs in, receives short-lived signed JWT, includes it on API calls.
2. React posts validated grievance fields to FastAPI; optionally sends text to `/api/ai/analyze` first.
3. FastAPI checks the citizen role, creates grievance and first history record in one database commit.
4. API returns random unique reference number and grievance ID.
5. Optional supporting document uploads through a separate endpoint after submission.

## Data flow: assignment / resolution

CMO review changes status to `Under Review`; assignment records department/officer in grievance and `department_assignments`; officer progress changes status to `In Progress`; action report enters a pending-review state; CMO approval resolves complaint or requests further action; citizen can reopen from `Resolved`.

## Authentication and trust boundaries

- Passwords are PBKDF2-HMAC-SHA256 hashed; JWTs are HS256 signed with a backend secret.
- All role gating occurs on the API, independent of navigation/UI hiding.
- Token stored in frontend `sessionStorage` is a **prototype trade-off**: exposed to XSS; use HttpOnly cookies and CSRF mitigation for production.
- Public tracking displays no citizen identity, original description or internal remarks.
- Gemini key stays on backend. Citizen complaint text is treated as untrusted input.
- Cross-origin requests are limited using `CORS_ORIGINS`; exact frontend host must be configured.
- Login (10/min), registration (5/min) and AI analysis (10/min) are rate limited per client IP by `app/core/ratelimit.py`; HTTP 429 is returned when exceeded. The limiter is in-memory, which suits a single-instance prototype.

## Deployment shape

Vercel static React site (project root `frontend`, build `npm run build`, output `dist`) → HTTPS → Render Python service (root `backend`, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`) → Neon Postgres. Set `VITE_API_URL` on Vercel, `CORS_ORIGINS` on Render; secrets only on Render.