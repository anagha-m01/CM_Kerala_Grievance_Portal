# 01 — Project Overview

## Problem statement

WhiteMatrix machine-test scenario: a fictional Chief Minister's Office for Kerala needs to receive grievances from citizens, forward cases to appropriate departments, monitor action, and communicate outcomes through a transparent and traceable portal.

## Objectives

1. Citizen self-service submission, tracking and feedback.
2. CMO oversight: review, priority selection, department/officer assignment, escalation, action-report approval and statistics.
3. Department officers: assigned-only visibility, investigations, progress remarks and action reports.
4. Complete timestamped grievance audit trail with user attribution.
5. Advisory LLM categorization, priority recommendation and short summary, with human review.
6. Documented APIs, meaningful role authorization, and free-tier-friendly deployment.

## Scope

**Included:** public Home, About, How It Works, Departments, Contact and FAQ; citizen register/login/logout, submit/track/dashboard/feedback; CMO dashboard with district/category/priority/status filters and overdue counts; officer dashboard; assignment; support/document upload and authorized download; history; real-LLM integration code plus transparent fallback; API docs and tests.

**Prototype limitations:** Only fictional cases; manual status checks in the portal (no email/SMS), no official integration; no SLA configuration UI (7-day prototype due dates); no autonomous case decisions; no real government endorsement.

## Roles and acceptance criteria

| Role | Needs | Acceptance signal |
|---|---|---|
| Public | Browse information, track with reference, contact form | Pages load, enquiry saved, tracker exposes limited data |
| Citizen | Submit and manage own grievances | Unique reference, dashboard only own cases, feedback post-resolution |
| CMO | Review all cases and route appropriately | All-case list, real counts/charts, role-gated assignment and report approval |
| Officer | Investigate assigned grievances | Sees assigned cases, can update progress and submit report |

## Success scenario

Citizen submits → CMO reviews → CMO assigns → officer starts investigation → officer submits report → CMO approves → citizen receives portal update and gives feedback or reopens. The reference and history remain accessible throughout.

## Nonfunctional goals

Clear RBAC checks on every protected backend action; input validation using Pydantic; hashed passwords; bounded file uploads; safe LLM model selection and structured output validation; no API keys in frontend; user-visible demo disclaimers.

## Agile/SDLC approach

Incremental sprints: (0) planning/scaffold; (1) database/auth; (2) citizen journey; (3) CMO/officer workflow; (4) AI; (5) testing/security; (6) docs/demo/deploy. A sprint is considered done only when associated API, database persistence, UI, authorization and a manual success/failure test pass. Prioritize end-to-end workflow before animations or optional duplicate detection.
