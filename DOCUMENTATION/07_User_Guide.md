# 07 — User Guide

> Fictional recruitment prototype only. No real grievances should be uploaded.

## Public visitor

- Home: overview, Submit and Track buttons, example lifecycle.
- About: goals/mission and explicit prototype disclaimer.
- How It Works: explanation of submission, CMO review, assignment and resolution.
- Departments: sample department directory loaded from backend database.
- Contact: submit name, email, subject, message; persisted to DB (no real email dispatch).
- FAQ: submission, tracking, AI and file questions.
- Track grievance: enter reference like `CMK-DEMO-0001`; view limited status, assigned department and public history.

## Citizen

1. Register (`/register`) with name, email, mobile and password (minimum eight characters) or log in (`/login`).
2. Open Dashboard `/citizen`; view personal case list, pending/resolved counts.
3. Select **New grievance**, choose Kerala district, enter category, subject and detailed explanation.
4. Optionally select **Analyze complaint**. If Gemini is configured, a real model suggests department, category, priority and a CMO summary. Otherwise a prominent **non-AI fallback** warning appears. Review/edit suggestions.
5. Optionally attach a PNG/JPEG/PDF less than 2 MB. Submit and preserve the unique reference number.
6. Open case details to see citizen-visible notes, progress history and authorized supporting documents.
7. After `Resolved`, provide a rating/comment. A resolved grievance may be reopened with a reason.
8. Log out using the header; the current session token is removed from the browser.

## CMO administrator

1. Sign in with a server-seeded CMO demo account (`cmo@example.com`).
2. Open `/cmo` to see all cases, total/pending/resolved/overdue counts and district/department charts.
3. Filter by district, category, priority or status; open grievance details.
4. Review a `Submitted` case, choose official priority and add a review note (`Under Review`). AI recommendations are not official decisions.
5. Assign to selected department and eligible officer; record assignment event.
6. Monitor attachments, status history, action reports and department progress.
7. Add internal notes (uncheck **Make remark visible to citizen**), issue visible remarks or escalate unresolved cases.
8. Review officer's pending action report: **Approve resolution** (`Resolved`) or **Request further action** (stays `In Progress`).
9. Reopen resolved cases when justified.

## Department officer

1. Sign in with a server-seeded officer account. There is one per department, for example `officer@example.com` (Public Works) or `officer.health@example.com` (Health); see the README for the full list. An officer sees only cases forwarded to their own department.
2. Dashboard `/officer` lists only grievances assigned to that officer/department.
3. Open a case and select **Mark In Progress** with an investigation note.
4. Add notes and, if appropriate, supporting files and report attachments.
5. Submit an action-taken report with findings and actions performed.
6. Await CMO review. If changes are requested, submit a revised report; after approval the case is resolved.

## Status meanings

| Status | Meaning |
|---|---|
| `Submitted` | Citizen filed the case; awaiting CMO review |
| `Under Review` | CMO reviewing / forwarded; officer may start investigation after assignment |
| `In Progress` | Assigned officer investigating and reporting |
| `Resolved` | CMO approved action report |
| `Reopened` | Previously resolved case brought back for reassessment |

All status transitions are timestamped and attributed to a responsible user. Public tracking excludes internal remarks. No notifications are sent outside the portal in this prototype.

## Troubleshooting

- **Login fails:** ensure backend seeded accounts after migration; correct password and backend URL.
- **No departments:** run `python -m app.seed` and verify DB URI.
- **AI shows rules fallback:** add valid `GEMINI_API_KEY`, choose eligible model, verify free quota and server logs; don't claim rules are AI.
- **Network error:** check backend `/api/health`, Vite `VITE_API_URL`, Render `CORS_ORIGINS` and cold start.
- **Upload refused:** accepted only PNG/JPEG/PDF <=2 MB; file content signature is checked on backend.
- **Missing case:** current user may not own or be assigned to it; 403/404 is expected.
