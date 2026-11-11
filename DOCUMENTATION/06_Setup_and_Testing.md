# 06 — Setup and Testing

## Requirements

- Python 3.11+, Node 20+, npm, Git, a browser.
- Optional: Neon free-tier PostgreSQL account, Gemini API key from Google AI Studio, Render and Vercel accounts.
- Clone/unzip project at `cm-kerala-grievance-portal/`.

## Local backend

From `backend/`:

```bash
python -m venv .venv
# Activate virtual environment (Windows: .venv\\Scripts\\Activate.ps1; Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
# Copy .env.example to .env and edit it
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`backend/.env` template:

```env
DATABASE_URL=sqlite:///./cm_kerala.db
JWT_SECRET=REPLACE_WITH_AT_LEAST_32_RANDOM_BYTES
JWT_EXPIRE_MINUTES=720
CORS_ORIGINS=http://localhost:5173
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
DEMO_ADMIN_PASSWORD=choose-demo-admin-password
DEMO_OFFICER_PASSWORD=choose-demo-officer-password
DEMO_CITIZEN_PASSWORD=choose-demo-citizen-password
```

Keep `.env` out of version control. Generate a secret with `python -c "import secrets; print(secrets.token_urlsafe(48))"` and paste into `JWT_SECRET`. The demo seed script requires all three account passwords; accounts are created idempotently. Set `DATABASE_URL` to Neon's PostgreSQL connection string to use the hosted database; the code normalizes `postgresql://` to `postgresql+psycopg://`. Use SSL parameters supplied by Neon.

## Local frontend

From `frontend/`:

```bash
npm install
# Copy .env.example to .env
# VITE_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:5173`. API docs: `http://localhost:8000/docs`.

## Tests

```bash
cd backend
python -m pytest -q
```

Tests use an in-memory SQLite database and do **not** need Neon/Gemini or real credentials. They validate full role-separated workflow and contact submission/AI fallback shape. A separate manual check of a live Gemini call is necessary for the real AI feature.

### Manual test matrix

| ID | Test | Expected |
|---|---|---|
| T01 | Register citizen, login/logout | Auth works; role is citizen |
| T02 | Citizen submits case | Unique reference; `Submitted` + first history |
| T03 | Upload/read PDF or JPG <=2 MB | Authorized download succeeds; oversized/wrong MIME refused |
| T04 | Public tracker with reference | Status + department + public history; no PII |
| T05 | Citizen opens another's complaint | 403 |
| T06 | CMO reviews and chooses priority | Status `Under Review`, history event |
| T07 | CMO assigns matching officer | Case appears on officer dashboard; assignment record created |
| T08 | Officer views unassigned/other-department case | 403 or excluded from list |
| T09 | Officer records progress + report | `In Progress`; pending action report |
| T10 | CMO requests changes, officer resubmits | Report history recorded; case still in progress |
| T11 | CMO approves report | `Resolved`, history and counts updated |
| T12 | Citizen feedback / reopen | feedback only after resolution; `Reopened` history |
| T13 | CMO district/category/status/priority filters | matching rows only |
| T14 | Contact form | message stored in contact_enquiries |
| T15 | AI with real key | `source=gemini`, valid structured response |
| T16 | AI missing key | `source=fallback`, explicit non-AI warning |
| T17 | Change due date of test case to past | overdue count increments |
| T18 | CMO escalates unresolved case | escalated flag and internal history |
| T19 | Run app on deployed links | both URLs reachable after cold start |

## Deploy on free hosting

1. **Neon:** Create project/database; obtain Postgres URI. Use a pooled URL for application connections and a direct URL when running migrations if Neon advises it. Store URL privately in Render env vars.
2. **GitHub:** Push `cm-kerala-grievance-portal/` repository. Confirm `.env`, SQLite files and `node_modules` are ignored.
3. **Render API:** Create Python Web Service with Root Directory `backend`. Build command `pip install -r requirements.txt`. Start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Configure `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, Gemini key (optional) and 3 demo passwords as private environment variables. Apply `alembic upgrade head` and `python -m app.seed` **once** using an appropriate shell/job in the deployed environment, or run them against Neon locally with the same database URL. Avoid putting credentials into build logs or version control.
4. **Vercel React:** Import same repo, set Root Directory `frontend`. Build `npm run build`, Output `dist`. Set `VITE_API_URL=https://YOUR-RENDER-HOST` without a trailing `/api` (Axios adds `/api`). `frontend/vercel.json` rewrites SPA routes to `index.html`.
5. **CORS:** Set Render `CORS_ORIGINS=https://YOUR-VERCEL-HOST`; comma-separate multiple origins if needed. Redeploy backend.
6. **Verify:** Visit hosted frontend in private browser; check register/login, save case, role transitions, stats, contact form, files, API documentation and AI (only if key works). Never claim a feature was verified unless actually tested.

**Cold starts:** Free Python hosts can sleep. The frontend allows a 75-second request timeout; opening the API health endpoint before the live demonstration reduces surprise. Free hosting availability, quotas and terms can change; check providers before submission.

## Demo video outline (record externally, 3–5 minutes)

- 0:00–0:25: project banner, public pages and prototype disclaimer.
- 0:25–1:15: citizen login, AI suggestions if active, submit grievance, reference/attachment.
- 1:15–2:10: CMO filters/analytics, review/priority/assign.
- 2:10–2:55: officer investigation and action-taken report.
- 2:55–3:40: CMO report approval; citizen tracking and feedback/reopen.
- 3:40–4:30: architecture diagram, `/docs`, ER diagram, GitHub docs.

## Submission checklist

- Hosted frontend link (works without running code locally).
- GitHub repository with source and `.env.example` (without actual secrets).
- Seven markdown docs and architecture/ER diagram files.
- 3–5 minute video link.
- Disposable demo login credentials (provided to recruiter separately).
- AI tool disclosure and disclaimer.
- Send before 12 Nov 2026, 8:00 PM IST.
