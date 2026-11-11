# 04 — API Documentation

**Base URL:** local `http://localhost:8000`. All endpoints below are prefixed `/api`. FastAPI also generates OpenAPI at `/docs` and `/openapi.json`. JSON is used unless a file upload is specified. Protected endpoints require `Authorization: Bearer <JWT>`.

| Method | Route | Role | Request / response |
|---|---|---|---|
| GET | `/health` | Public | service health |
| POST | `/auth/register` | Public | `{name,email,mobile,password}` → created citizen ID |
| POST | `/auth/login` | Public | `{email,password}` → JWT and role/user |
| POST | `/auth/logout` | Public | Stateless acknowledgment; browser deletes bearer token |
| GET | `/auth/me` | Authenticated | current user profile |
| GET | `/departments` | Public | department list |
| GET | `/officers?department_id=N` | CMO | eligible officers |
| POST | `/contact` | Public | `{name,email,subject,message}` persisted |
| POST | `/ai/analyze` | Citizen/CMO | `{description}` → department, category, priority, summary, `source`, warning |
| POST | `/grievances` | Citizen | grievance form with optional AI suggestions → `id`, `reference_no` |
| GET | `/grievances` | Authenticated | role-filtered list, optional `district`, `category`, `priority`, `status` |
| GET | `/grievances/{id}` | Authorized participant | complete role-filtered case |
| GET | `/grievances/track/{reference_no}` | Public | reference, status, department and public history only |
| POST | `/grievances/{id}/review` | CMO | `{priority,remark}` → `Under Review` |
| POST | `/grievances/{id}/assign` | CMO | `{department_id,officer_id,remark}` → assignment |
| PATCH | `/grievances/{id}/status` | Authorized transition | `{status,remark}`; respects status machine |
| POST | `/grievances/{id}/remarks` | CMO/Officer | `{remark,is_public}` |
| POST | `/grievances/{id}/escalate` | CMO | `{remark,is_public}` |
| POST | `/grievances/{id}/reports` | Assigned officer | `{findings,action_taken}` |
| POST | `/grievances/{id}/reports/{report_id}/review` | CMO | `{decision:"approve"|"request_changes",remark}` |
| POST | `/grievances/{id}/feedback` | Citizen owner | `{rating:1..5,comment}`; after resolution |
| POST | `/grievances/{id}/attachments?kind=support` | Authorized participant | multipart field `file` (PNG/JPG/PDF <=2 MB) |
| GET | `/attachments/{attachment_id}` | Authorized participant | streamed file |
| GET | `/cmo/stats` | CMO | total/pending/resolved/overdue; district, department and status counts |
| GET | `/citizen/stats` | Citizen | owner-scoped counts |
| GET | `/officer/stats` | Officer | assigned-scoped counts |

## Example: register / login

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Sample Citizen","email":"sample@example.com","mobile":"9000000123","password":"example-long-password"}'

curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"sample@example.com","password":"example-long-password"}'
```

Example login response (token shortened):

```json
{"access_token":"eyJ...","token_type":"bearer","user":{"id":4,"name":"Sample Citizen","email":"sample@example.com","role":"citizen"}}
```

## Example: create / track

```bash
curl -X POST http://localhost:8000/api/grievances \
  -H 'Content-Type: application/json' -H 'Authorization: Bearer TOKEN' \
  -d '{"district":"Thrissur","category":"Road Infrastructure","subject":"Damaged fictional road","description":"Fictional road damage at the sample junction affects local travel."}'

curl http://localhost:8000/api/grievances/track/CMK-DEMO-0001
```

Example creation response:

```json
{"id":3,"reference_no":"CMK-2026-0A1B2C3D4E","status":"Submitted"}
```

## Example: model analysis

```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H 'Content-Type: application/json' -H 'Authorization: Bearer TOKEN' \
  -d '{"description":"The fictional bridge railing is damaged and needs inspection."}'
```

With a valid Gemini API key and quota, expected fields: `department`, `category`, `priority`, `summary`, `source:"gemini"`, `warning:null`. Without the model, `source:"fallback"` and a warning explicitly say the result is **not AI output**.

## Errors

- 400/422: invalid data, unsupported state or failed validation.
- 401: absent/expired/invalid JWT.
- 403: forbidden role or case access.
- 404: missing record or reference.
- 409: duplicate account, invalid transition or conflict (e.g., pending report).
- 413: file larger than maximum; 415: unsupported/invalid file MIME.

## API notes

- CMO alone chooses final priority and assignment; model suggestions never alter official workflow automatically.
- Public tracking intentionally omits original descriptions, email, internal remarks and attachments.
- New grievances use random unique references with a database unique constraint.
- This is a REST interface, fulfilling the brief's backend-equivalent requirement.
