# lms-backend

FastAPI backend for a lightweight Learning Management System using SQLite. Ready for deployment on Vercel.

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run locally:
   ```bash
   uvicorn api.index:app --reload
   ```
3. Deploy to Vercel (requires the Vercel CLI):
   ```bash
   vercel --prod
   ```

## API

- `GET /health` — health check.
- `GET /courses` — list all courses.
- `POST /courses` — create a course. Body: `{ "title": "...", "description": "..." }`.
- `GET /courses/{course_id}` — fetch a course by ID.

The service persists data to `lms.db` using SQLite.
