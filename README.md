# LMS Python Backend

A FastAPI reference implementation that mirrors the Supabase-powered LMS frontend. It exposes the same REST contracts documented in `docs/python-backend-endpoints.md` and uses in-memory stores so you can iterate quickly before wiring a real database or auth provider.

## Features
- Email/password auth with refresh tokens and admin bootstrap hooks.
- Profile, alert settings, disputes, litigation cases, and document metadata endpoints.
- Admin dashboards for managing permissions and toggling account access.
- Pluggable storage and notification abstractions for future integrations.

## Getting started
```bash
cd python-backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

The API will be served at `http://127.0.0.1:8000`. Interactive docs are available at `/docs`.

## Environment variables
Create a `.env` file or export the following variables:

| Variable | Description |
| --- | --- |
| `APP_SECRET_KEY` | Secret used to sign access and refresh tokens. |
| `DEFAULT_ADMIN_EMAIL` | Email that should receive full permissions on first login. |
| `STORAGE_BUCKET` | Path or URL where uploaded files should be persisted. |

Defaults exist for local development, but never ship them to production.

## Project layout
```
python-backend/
├── app/
│   ├── api/
│   │   └── routes/        # FastAPI routers grouped by resource
│   ├── services/          # Storage and notification adapters
│   ├── config.py          # Settings management
│   ├── database.py        # In-memory persistence (swap with real DB)
│   ├── dependencies.py    # Auth and permission helpers
│   ├── main.py            # FastAPI entrypoint
│   └── schemas.py         # Pydantic models shared across routes
├── pyproject.toml
└── README.md
```

## Next steps
1. Replace the in-memory `database.py` with PostgreSQL or any persistence layer.
2. Swap the naive auth service with your identity provider (e.g., Django, Auth0, Supabase Auth migration).
3. Implement document storage in `services/storage.py` to push files to S3, GCS, or local disk.
4. Wire your notification system inside `services/notifications.py` for dispute/litigation events.

This repo gives you a fully documented baseline so you can migrate the existing frontend to a Python backend without rewriting the UI.
