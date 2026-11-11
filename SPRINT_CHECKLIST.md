# Agile Development and Final Submission Checklist

## Sprint 0: Setup
- [x] React/Vite + FastAPI folder structure
- [x] Initial SQLAlchemy models and Alembic migration
- [x] `.env.example` files and `.gitignore`
- [ ] Connect YOUR Neon DB; apply initial migrations
- [ ] Set YOUR Gemini API key and test a real response

## Sprint 1: Backend
- [x] Citizen registration/login, hashed passwords, bearer JWT and role guards
- [x] Department list, seeded users and fictional grievances
- [x] CRUD-style grievance API, tracking and status history
- [x] File upload/retrieval, contact form persistence

## Sprint 2: Citizen and public UI
- [x] Home, About, How It Works, Departments, Contact, FAQ
- [x] Citizen dashboard, complaint submission, reference tracking and feedback
- [x] AI suggestions UI with explicit fallback warning
- [ ] Complete browser walkthrough after local npm installation

## Sprint 3: CMO/officer lifecycle
- [x] CMO/Officer dashboards, statistics, filters
- [x] CMO review/assignment/escalation/internal remarks
- [x] Officer investigation and action reports, CMO approval/rejection
- [x] Reopening, timestamps and responsible-user history

## Sprint 4: AI
- [x] Direct Gemini SDK integration code and Pydantic structured output
- [x] Labelled non-AI rules fallback when model unavailable
- [ ] Verify real Gemini model response with personal key and current free quota

## Sprint 5: Testing and deployment
- [x] Automated backend end-to-end tests (local SQLite)
- [ ] Build frontend (`npm install && npm run build`) and verify in browser
- [ ] Deploy backend, frontend and Postgres with your accounts
- [ ] Check authorizations, attachment upload and all workflows on hosted URLs

## Sprint 6: Submission
- [x] Mandatory seven markdown documents
- [x] ER and architecture diagrams
- [x] Root README with AI-service/tool disclosure
- [ ] Record 3–5 minute demo video
- [ ] Add disposable demo account passwords to recruiter message (not GitHub)
- [ ] Submit hosted URL, GitHub URL and video before 12 Nov 2026 20:00 IST

[x] = source feature prepared or local backend test passed; it does not mean a live deployment exists.
