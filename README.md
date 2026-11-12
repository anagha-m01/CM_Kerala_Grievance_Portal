# CM Kerala — Public Grievance Redressal Portal

### AI-Powered Public Grievance Management System

An AI-assisted, full-stack grievance redressal platform designed to streamline citizen complaint submission, departmental assignment, investigation, resolution, and transparent status tracking.

Built as part of the **AI Full Stack Engineer Technical Assessment — WhiteMatrix Software Solutions**.

### Live Application

- **Frontend:** https://cm-kerala-grievance-portal-orcin.vercel.app/
- **Backend API:** https://cm-kerala-api.onrender.com/
- **Swagger API Documentation:** https://cm-kerala-api.onrender.com/docs

> **Disclaimer:** This application is a recruitment assessment prototype. It is not affiliated with, endorsed by, or operated by the Government of Kerala or the Chief Minister's Office. All demonstration accounts and grievances are fictional. Do not submit real grievances or sensitive personal information.

---

## 1. Project Overview

The CM Kerala Public Grievance Redressal Portal is a web-based application that enables citizens to submit public grievances and track their resolution.

The system provides dedicated dashboards for citizens, Chief Minister's Office (CMO) administrators, and department officers.

An integrated AI Grievance Assistant analyzes complaint descriptions and recommends appropriate departments, complaint categories, priority levels, and concise summaries.

The application follows a structured, role-based workflow in which official decisions remain under human control.

### Objectives

- Provide a centralized platform for citizen grievances.
- Enable transparent tracking using unique reference numbers.
- Simplify departmental assignment and complaint management.
- Support AI-assisted grievance classification.
- Maintain an auditable history of grievance activities.
- Improve accountability through officer reports and CMO review.
- Allow citizens to provide feedback after resolution.

---

## 2. Key Features

### Citizen Portal

- Citizen registration and secure login.
- Grievance submission with district, category, subject, and description.
- Optional PDF and image attachments.
- Unique grievance reference number generation.
- AI-assisted department and priority suggestions.
- Personal dashboard showing submitted grievances.
- Complaint tracking and status history.
- Citizen-visible administrative remarks.
- Feedback submission after resolution.
- Option to reopen resolved grievances.

### Chief Minister's Office Dashboard

- Centralized grievance management.
- Total, pending, resolved, and overdue statistics.
- District-wise and department-wise visualization.
- Filtering by district, category, status, and priority.
- Individual grievance review.
- AI recommendation review.
- Department and officer assignment.
- Administrative remarks.
- Escalation of grievances.
- Action-taken report review.
- Resolution approval or request for further action.
- Complete grievance history.

### Department Officer Dashboard

- Role-based officer authentication.
- Access to assigned departmental grievances.
- Complaint and attachment review.
- Investigation remarks.
- Grievance status updates.
- Action-taken report submission.
- Resolution details sent to the CMO for approval.

### AI Grievance Assistant

The AI assistant uses Google's Gemini API to analyze complaint descriptions and generate:

1. Recommended government department.
2. Suggested grievance category.
3. Priority classification: Low, Medium, or High.
4. A concise summary for CMO administrators.

AI results are validated through Pydantic and remain advisory.

When the model is unavailable, the application provides a clearly labelled rule-based fallback.

**AI does not independently approve, assign, or resolve grievances.**

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React.js, Vite, JavaScript (JSX) |
| Styling | Custom CSS (Tailwind CSS v4 enabled in the Vite build) |
| Routing | React Router |
| HTTP Client | Axios |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| API Validation | Pydantic |
| Database | PostgreSQL |
| Database Hosting | Neon |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Authentication | JWT, password hashing |
| AI Integration | Google Gemini API |
| AI SDK | google-genai |
| Containerization | Docker, Docker Compose |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |
| Testing | Pytest, FastAPI TestClient |
| Version Control | Git, GitHub |

### Why FastAPI?

FastAPI was selected as the backend framework because it provides:

- High-performance REST API development.
- Native Python integration for AI services.
- Pydantic-based data validation.
- Automatic Swagger/OpenAPI documentation.
- Support for dependency-based authentication.
- Straightforward integration with SQLAlchemy.

The assignment accepts backend frameworks equivalent to Node.js and Express.

---

## 4. System Architecture

The application follows a modular client-server architecture.

```text
                  CITIZEN / CMO / OFFICER
                            |
                            v
                    React + Vite
                      (Vercel)
                            |
                       HTTPS / REST
                            |
                            v
                        FastAPI
                        (Render)
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
     Authentication    Business Logic      AI Service
       JWT / RBAC       and REST APIs      Gemini API
          |                 |
          +--------+--------+
                   |
                   v
                SQLAlchemy
                   |
                   v
             Neon PostgreSQL
                   |
       +-----------+-----------+
       |           |           |
      Users    Grievances    History
       |           |           |
   Departments  Attachments  Reports
                   |
                Feedback
```

### Architecture Components

**Frontend**

React handles user interactions, routing, forms, dashboards, and API communication.

**Backend**

FastAPI manages business logic, authentication, authorization, grievance operations, and AI integration.

**Database**

PostgreSQL stores users, departments, grievances, assignments, status history, reports, attachments, feedback, and contact enquiries.

**AI Service**

The backend communicates with Gemini through the Google GenAI SDK and validates the structured response using Pydantic.

Architecture diagrams:

- [System Architecture](DOCUMENTATION/diagrams/system_architecture.png)
- [Database ER Diagram](DOCUMENTATION/diagrams/database_er.png)

---

## 5. Grievance Management Workflow

The application implements the following lifecycle:

```text
Citizen Submits Grievance
          |
          v
    SUBMITTED
          |
          v
    CMO Reviews
          |
          v
    UNDER REVIEW
          |
          v
CMO Assigns Department / Officer
          |
          v
Officer Starts Investigation
          |
          v
    IN PROGRESS
          |
          v
Officer Submits Action-Taken Report
          |
          v
CMO Reviews Department Response
          |
          +---- Request Further Action
          |              |
          |              v
          |      Officer Investigation
          |
          v
    RESOLVED
          |
          v
Citizen Views Outcome
          |
          v
Citizen Submits Feedback
          |
          v
REOPENED (if further review is needed)
```

### Supported Statuses

- `Submitted`
- `Under Review`
- `In Progress`
- `Resolved`
- `Reopened`

Every status change is recorded with its timestamp, responsible user, and relevant remarks.

---

## 6. Project Structure

```text
CM_Kerala_Grievance_Portal/
|
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- contexts/
|   |   |-- lib/
|   |   |-- pages/
|   |   |-- App.jsx
|   |   |-- main.jsx
|   |   `-- styles.css
|   |-- Dockerfile
|   |-- package.json
|   |-- vite.config.js
|   `-- vercel.json
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- routes.py
|   |   |-- core/
|   |   |   |-- config.py
|   |   |   `-- security.py
|   |   |-- db/
|   |   |   `-- session.py
|   |   |-- models/
|   |   |   `-- entities.py
|   |   |-- schemas/
|   |   |   `-- inputs.py
|   |   |-- services/
|   |   |   |-- ai.py
|   |   |   `-- helpers.py
|   |   |-- main.py
|   |   `-- seed.py
|   |-- alembic/
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- alembic.ini
|   `-- .env.example
|
|-- DOCUMENTATION/
|   |-- 01_Project_Overview.md
|   |-- 02_System_Architecture.md
|   |-- 03_Database_Design.md
|   |-- 04_API_Documentation.md
|   |-- 05_AI_Integration.md
|   |-- 06_Setup_and_Testing.md
|   |-- 07_User_Guide.md
|   `-- diagrams/
|
|-- compose.yaml
|-- .env.example
|-- .gitignore
`-- README.md
```

---

## 7. Database Design

The application uses PostgreSQL with SQLAlchemy ORM and Alembic migrations.

### Main Entities

| Entity | Purpose |
|---|---|
| Users | Citizen, CMO, and officer accounts |
| Departments | Government department information |
| Grievances | Complaint details and current status |
| Grievance History | Timestamped status and activity records |
| Department Assignments | Department and officer assignments |
| Attachments | Supporting documents and files |
| Action Reports | Officer investigation and action reports |
| Citizen Feedback | Feedback after resolution |
| Contact Enquiries | Public contact form submissions |

### Database Design Principles

- Primary and foreign key relationships.
- Relational data integrity.
- Unique grievance reference numbers.
- Historical audit records.
- Department-based access restrictions.
- Persistent complaint and attachment storage.

---

## 8. REST API

The FastAPI backend exposes REST endpoints for application operations.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Citizen registration |
| POST | `/api/auth/login` | User authentication |

### Grievance Management

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/grievances` | Submit grievance |
| GET | `/api/grievances` | Retrieve authorized grievances |
| GET | `/api/grievances/{id}` | View grievance details |
| GET | `/api/grievances/track/{reference}` | Track grievance |
| POST | `/api/grievances/{id}/review` | CMO review |
| POST | `/api/grievances/{id}/assign` | Assign department/officer |
| PATCH | `/api/grievances/{id}/status` | Update grievance status |
| POST | `/api/grievances/{id}/reports` | Submit action report |

### Other Services

- Department retrieval.
- CMO statistics.
- Officer statistics.
- File upload and retrieval.
- Grievance remarks.
- Citizen feedback.
- Contact enquiries.
- AI grievance analysis.

### API Documentation

FastAPI automatically generates interactive Swagger documentation.

**Live Swagger UI:**

https://cm-kerala-api.onrender.com/docs

Detailed endpoint descriptions and request/response examples are available in:

[04_API_Documentation.md](DOCUMENTATION/04_API_Documentation.md)

---

## 9. AI Integration

The AI Grievance Assistant uses the Google Gemini API through the official `google-genai` Python SDK.

### Processing Pipeline

```text
Citizen Complaint Description
             |
             v
       FastAPI Endpoint
             |
             v
     Input Validation
             |
             v
        Gemini API
             |
             v
     Structured Response
             |
             v
     Pydantic Validation
             |
             v
  Human-Reviewable Suggestions
             |
             v
      Grievance Submission
```

### Example AI Response

```json
{
  "department": "Health Department",
  "category": "Healthcare",
  "priority": "High",
  "summary": "A government health centre is experiencing a shortage of essential medicines."
}
```

### AI Safeguards

- Structured response validation using Pydantic.
- Restricted department and priority values.
- Human review of AI recommendations.
- Graceful handling of API failures.
- Explicitly labelled non-AI fallback.
- Gemini API key stored only on the backend.

The application uses direct LLM integration rather than LangChain or LangGraph because the required grievance analysis is a focused classification and summarization task.

---

## 10. Local Setup

### Prerequisites

- Git
- Docker Desktop
- Neon PostgreSQL database
- Gemini API key for real AI functionality

### Clone the Repository

```bash
git clone https://github.com/anagha-m01/CM_Kerala_Grievance_Portal.git

cd CM_Kerala_Grievance_Portal
```

### Configure Environment Variables

Create `backend/.env` from `backend/.env.example`.

Required configuration:

```dotenv
DATABASE_URL=YOUR_NEON_POSTGRESQL_URL

JWT_SECRET=YOUR_SECURE_RANDOM_SECRET
JWT_EXPIRE_MINUTES=720

CORS_ORIGINS=http://localhost:5173

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.5-flash-lite

DEMO_ADMIN_PASSWORD=YOUR_ADMIN_PASSWORD
DEMO_OFFICER_PASSWORD=YOUR_OFFICER_PASSWORD
DEMO_CITIZEN_PASSWORD=YOUR_CITIZEN_PASSWORD
```

Use a Gemini model that is available to your account. Free-tier model availability and usage limits may change.

Generate a secure JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Never commit real secrets to GitHub.

### Start with Docker

From the project root:

```bash
docker compose up --build -d
```

Check container status:

```bash
docker compose ps
```

The backend Dockerfile applies Alembic migrations during startup.

### Seed Demo Data

```bash
docker compose exec backend python -m app.seed
```

### Access the Application

Frontend:

http://localhost:5173

FastAPI backend:

http://localhost:8000

Swagger documentation:

http://localhost:8000/docs

### View Backend Logs

```bash
docker compose logs -f backend
```

### Stop Containers

```bash
docker compose down
```

---

## 11. Development Without Docker

### Backend

```bash
cd backend

python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Configure `backend/.env`, then initialize the database:

```bash
alembic upgrade head
```

Seed the database:

```bash
python -m app.seed
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

### Frontend

In a separate terminal:

```bash
cd frontend

npm install
```

Configure `frontend/.env`:

```dotenv
VITE_API_URL=http://localhost:8000
```

Start the React application:

```bash
npm run dev
```

---

## 12. Demo Accounts

The database seed script creates fictional accounts for testing.

| Role | Email | Department |
|---|---|---|
| CMO Administrator | cmo@example.com | n/a |
| Department Officer | officer@example.com | Public Works Department |
| Department Officer | officer.health@example.com | Health Department |
| Department Officer | officer.education@example.com | Education Department |
| Department Officer | officer.lsgd@example.com | Local Self Government Department |
| Department Officer | officer.water@example.com | Kerala Water Authority |
| Department Officer | officer.kseb@example.com | Kerala State Electricity Board |
| Department Officer | officer.agri@example.com | Agriculture Department |
| Department Officer | officer.police@example.com | Police Department |
| Citizen | citizen@example.com (also citizen2@ and citizen3@example.com) | n/a |

Passwords are configured through the corresponding `DEMO_*_PASSWORD` environment variables.

There is one fictional officer per department, so a grievance can be forwarded to any department. All officers share the `DEMO_OFFICER_PASSWORD` value. The seed also creates 22 fictional grievances across all 14 districts in every workflow status (including overdue, escalated and reopened cases) so the CMO charts are populated. Run `python -m app.seed` again at any time; it only adds what is missing.

**For evaluators:** Demo passwords should be provided separately in the submission email. They are intentionally not included in this public repository.

---

## 13. Testing and Validation

Backend testing is implemented using Pytest and FastAPI TestClient.

### Run Automated Tests

Using Docker:

```bash
docker compose exec backend python -m pytest -q
```

Or from the local backend environment:

```bash
python -m pytest -q
```

### Latest Local Test Result

```text
... [100%]

10 passed
```

The suite covers the full lifecycle, role isolation between departments, invalid status transitions, file validation, escalation and overdue statistics, the Gemini success and fallback paths (with the SDK mocked) and rate limiting.

### Validated Local Workflows

- Citizen authentication.
- Grievance submission and reference generation.
- Gemini-based grievance classification.
- Supporting document upload.
- CMO review and priority management.
- Department and officer assignment.
- Officer investigation and status update.
- Action-taken report submission.
- CMO resolution approval.
- Reference-based grievance tracking.
- Citizen feedback after resolution.

The application also includes role-based authorization and grievance history tracking.

These workflows were tested locally. Deployed end-to-end validation should be completed separately.

---

## 14. Deployment

The application is deployed using free-tier cloud services.

### Frontend — Vercel

**URL:**

https://cm-kerala-grievance-portal-orcin.vercel.app/

Configuration:

```text
Framework: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

Frontend environment variable:

```dotenv
VITE_API_URL=https://cm-kerala-api.onrender.com
```

### Backend — Render

**URL:**

https://cm-kerala-api.onrender.com/

Configuration:

```text
Runtime: Docker
Root Directory: backend
Dockerfile: backend/Dockerfile
Health Check: /
```

Render stores the backend's environment variables separately from the local `.env` file.

### Database — Neon PostgreSQL

The PostgreSQL database is hosted on Neon.

SQLAlchemy handles ORM operations, while Alembic manages schema migrations.

### CORS Configuration

The Render backend should allow requests from the deployed frontend.

```dotenv
CORS_ORIGINS=http://localhost:5173,https://cm-kerala-grievance-portal-orcin.vercel.app
```

### Free-Tier Considerations

- Render free services may enter a sleep state after inactivity.
- The first backend request may have additional latency.
- Gemini API requests are subject to provider availability and quotas.
- Production traffic and government use would require additional infrastructure and security controls.

---

## 15. Security Considerations

The prototype implements:

- JWT-based authentication.
- Role-based authorization.
- Password hashing.
- Backend request validation.
- Restricted grievance access.
- Controlled file retrieval.
- Environment-based secret management.
- Timestamped activity history.
- Separation of public and internal remarks.
- Per-client rate limiting on login, registration and AI analysis (in-memory, single instance).

### Known Limitations

- Authentication tokens are stored in browser session storage.
- File uploads are limited to 2 MB and stored in PostgreSQL.
- Real-time email and SMS notifications are not implemented.
- The AI service depends on external API availability. Rate limiting is per process and would need a shared store (for example Redis) with multiple instances.
- The application is intended for demonstration, not production government operations.

A production deployment would require stronger session management, content scanning, monitoring, auditing, and comprehensive security testing.

---

## 16. Technical Documentation

The repository includes the following documentation under `DOCUMENTATION/`.

1. [Project Overview](DOCUMENTATION/01_Project_Overview.md)
2. [System Architecture](DOCUMENTATION/02_System_Architecture.md)
3. [Database Design](DOCUMENTATION/03_Database_Design.md)
4. [API Documentation](DOCUMENTATION/04_API_Documentation.md)
5. [AI Integration](DOCUMENTATION/05_AI_Integration.md)
6. [Setup and Testing](DOCUMENTATION/06_Setup_and_Testing.md)
7. [User Guide](DOCUMENTATION/07_User_Guide.md)

Additional diagrams:

- [System Architecture Diagram](DOCUMENTATION/diagrams/system_architecture.png)
- [Database Entity Relationship Diagram](DOCUMENTATION/diagrams/database_er.png)

---

## 17. Development Approach

The project follows an iterative, Agile-based software development lifecycle.

### Development Phases

1. Requirements analysis and planning.
2. Architecture and database design.
3. Backend API and authentication development.
4. Citizen and administrative workflow implementation.
5. AI service integration.
6. Integration testing and debugging.
7. Docker configuration and deployment.
8. Documentation and demonstration preparation.

Development prioritized a working end-to-end grievance lifecycle over optional enhancements.

---

## 18. Tools and Services Used

### Development Technologies

- Python
- JavaScript
- React
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Git and GitHub

### Third-Party Services

- Google Gemini API — AI grievance analysis.
- Neon — PostgreSQL hosting.
- Render — FastAPI hosting.
- Vercel — Frontend hosting.

### AI-Assisted Development

OpenAI ChatGPT and Anthropic Claude were used as development assistants for planning, code generation, code review, debugging, and documentation. All code was reviewed and is understood by the author.

The application integrates Google's Gemini API to provide AI-assisted grievance recommendations.

---

## 19. Future Improvements

Potential enhancements include:

- Email and SMS status notifications.
- Duplicate grievance detection using semantic similarity.
- Advanced grievance analytics.
- File storage using private object storage.
- Improved authentication and session management.
- Automated integration and end-to-end tests.
- Accessibility improvements.
- More comprehensive audit and monitoring capabilities.

These enhancements are outside the scope of the current recruitment prototype.

---

## 20. Project Purpose

This application was developed as part of the recruitment assessment.

It demonstrates practical experience in:

- Full-stack web application development.
- REST API design and integration.
- Relational database design.
- Authentication and authorization.
- AI model integration.
- Workflow automation.
- Docker containerization.
- Cloud deployment.
- Software testing and technical documentation.

---

**Project:** CM Kerala — Public Grievance Redressal Portal

**Developer:** Anagha M

**Note:** This is an independent technical demonstration and is not an official Government of Kerala platform.