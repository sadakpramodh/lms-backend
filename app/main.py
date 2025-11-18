"""FastAPI entrypoint."""
from __future__ import annotations

from fastapi import FastAPI

from .api.routes import admin, auth, disputes, health, litigation, profile
from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(profile.router)
    app.include_router(disputes.router)
    app.include_router(litigation.router)
    app.include_router(admin.router)
    return app


app = create_app()
