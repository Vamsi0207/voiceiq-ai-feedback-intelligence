# API contract
FastAPI publishes detailed schemas at /docs and /openapi.json. JSON errors use detail; CSV errors retain row numbers.

- GET /api/dashboard/executive-summary: deterministic overview with calculated categories, urgency, recurring issues and active-date comparison.
- GET /api/health: database readiness and application version.
- POST /api/complaints/upload: multipart file, detailed persisted batch results.
- GET /api/complaints/example: downloadable UTF-8 CSV.
- GET /api/complaints: q, category, sentiment, urgency, source, date_from, date_to, sort (created_at/urgency/confidence), direction, page, page_size (max 100).
- GET /api/complaints/{id}: persisted complaint detail.
- POST /api/complaints/analyze: returns 202 and job; GET /api/jobs/{id} polls progress. 409 if busy.
- GET /api/dashboard/overview and /trends: same filters; authoritative counts/distributions.
- GET /api/clusters and /{id}: members, summaries, category and sentiment distribution.
- GET /api/insights: category and priority filters; POST /generate returns evidence-grounded recommendations, optional bounded provider output.
- GET /api/evaluation/summary: last executed evaluation, 404 until evaluated.
- GET /api/settings/ai-status: provider/model/configuration presence, never keys; reports embedding method.

Uploads accept ISO-8601 dates, 1–5,000 character text, ≤120 character external IDs and ≤80 character source. Invalid input 422; unavailable models 503; absent entities 404. Read endpoints never trigger training or clustering.
