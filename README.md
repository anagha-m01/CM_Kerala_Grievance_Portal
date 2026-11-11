# CM Kerala — Public Grievance Redressal Portal

> **RECRUITMENT PROTOTYPE — NOT AN OFFICIAL GOVERNMENT WEBSITE.** Built for the WhiteMatrix Software Solutions AI Full Stack Engineer machine test. Uses fictional demonstration grievances. This project is not operated, authorized or endorsed by the Government of Kerala or the Chief Minister's Office (CMO). Do not submit real citizen data or use official government credentials.

A full-stack role-based complaint redressal **source-code prototype** with citizen, CMO and department-officer dashboards, review/assignment, action reports, a timestamped grievance history, a public reference tracker, limited attachments, statistics, and advisory AI complaint classification.

## Technology

- **Frontend:** React 18 + Vite + JSX, React Router, Tailwind CSS 4, Recharts, Axios
- **Backend:** Python + FastAPI + Pydantic, SQLAlchemy 2, Alembic
- **Database:** PostgreSQL (Neon for hosting); SQLite can be used for local development and automated tests
- **AI:** Google Gemini SDK (`google-genai`) with Pydantic structured output; clearly labeled rules fallback when unavailable — **the fallback is not real AI**
- **Files:** PDF/PNG/JPEG <= 2 MB stored in database `BYTEA` (demo only); authorized download endpoint
- **Hosting suggestion:** React on Vercel and FastAPI on Render; both require configuration in your own accounts

## Quick start — local

Requirements: Python 3.11+; Node 20+; npm. Use a Neon PostgreSQL `DATABASE_URL` in backend `.env` for a hosted database; SQLite is useful for initial local testing.

### 1. Backend

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env        # On Windows: copy .env.example .env
```

Edit `backend/.env`. **Change `JWT_SECRET` to a random secret at least 32 bytes long**. For local demo, default `DATABASE_URL=sqlite:///./cm_kerala.db`. To use Neon set `DATABASE_URL` to your Postgres connection string (SSL parameters supplied by Neon). Set 3 `DEMO_*_PASSWORD` variables to different strong test-account passwords. Optionally set `GEMINI_API_KEY`.

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

Backend at http://localhost:8000, OpenAPI at http://localhost:8000/docs, health at http://localhost:8000/api/health.

### 2. Frontend (second terminal)

```bash
cd frontend
npm install
cp .env.example .env       # Windows: copy .env.example .env
npm run dev
```

Open http://localhost:5173. For local development `VITE_API_URL=http://localhost:8000`. `VITE_*` variables are public browser configuration — never put secrets in them.

### 3. Demo accounts

The seed script creates test users:

| Role | Email | Password |
|---|---|---|
| CMO | `cmo@example.com` | `DEMO_ADMIN_PASSWORD` value in `backend/.env` |
| Officer (PWD) | `officer@example.com` | `DEMO_OFFICER_PASSWORD` value in `backend/.env` |
| Citizen | `citizen@example.com` | `DEMO_CITIZEN_PASSWORD` value in `backend/.env` |

**Important:** Share only separate, disposable demo account credentials with evaluators after deployment. Do not publish the real database URL, JWT secret or Gemini key. The seed sample data is fictional.

## Primary demo workflow

1. Sign in as citizen, submit grievance, optionally analyze text using AI and upload a small file. Copy the reference number.
2. Sign in as CMO, review a new grievance and set its priority; assign it to a department officer.
3. Sign in as officer; open assigned grievance, set `In Progress`, record investigation details, optionally attach evidence and submit an action-taken report.
4. Sign in as CMO; inspect the report and either approve its resolution or request further action.
5. Sign in as citizen; track status/history, give feedback on a resolved case or reopen it.
6. Open `/track` without signing in to view a **limited** reference-based tracker; private fields are omitted.

Statuses: `Submitted`, `Under Review`, `In Progress`, `Resolved`, `Reopened`. Internal comments are excluded from public/citizen history. CMO review of a submitted action report is an operation, not a sixth grievance status.

## API and tests

- Interactive OpenAPI documentation: `/docs`
- Tests (from `backend/`): `python -m pytest -q`
- Full API contracts and examples: [API documentation](DOCUMENTATION/04_API_Documentation.md)
- Test cases: [Setup and testing](DOCUMENTATION/06_Setup_and_Testing.md)

## Deployment

See [Setup and testing](DOCUMENTATION/06_Setup_and_Testing.md) for Neon, Vercel and Render instructions. **This ZIP is source code only**: it does not include a hosted URL, external service credentials, a tested live Gemini call or a recorded demo video. These require your accounts and verification after deployment.

## Limitations / security notes

- Demo uses bearer JWT held in `sessionStorage`; this is simpler than production hardened HttpOnly-cookie session management. Use stronger browser session security and CSRF mitigation in production.
- Small binary attachments are stored in PostgreSQL. This consumes database storage and is **not suitable for a scaled government platform**.
- Free Python hosts may sleep and take time to wake; monitor application health and disclose free-host limitations.
- In the absence of `GEMINI_API_KEY`, AI analysis returns an explicit `source: "fallback"` label; keyword rules do **not** count as the real AI requirement.
- Contact form saves messages to the database but does not email a government department. No real email/SMS notifications are implemented; citizens see updates on the portal.
- Registration creates **citizens only**; officer and CMO accounts are provisioned by the server-side demo seed script.
- No real Kerala government branding, authorization or production security guarantee is implied.

## AI and external tools disclosure

Source code and documentation were prepared with assistance from OpenAI ChatGPT. Open-source libraries used are specified in `requirements.txt` and `package.json`. Google Gemini (when configured) provides LLM text analysis. Neon, Render and Vercel are suggested external services and are **not pre-connected**. AI suggestions are non-binding and reviewed by citizen/CMO.

## Mandatory documentation

All seven required documents are in [`DOCUMENTATION/`](DOCUMENTATION/), plus architecture and ER diagrams. The submission also requires a working URL, public GitHub repository and a 3–5-minute video recorded separately.
