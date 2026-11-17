"""The ResearchIQ web API. Start with: make serve

Startup refuses to run unless the signing secret and both seed accounts are set in .env.
Errors never expose stack traces, file paths or prompts: a failure returns a request ID, and the
details go to the server log only.
"""

import logging
import sqlite3
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import db
from app.api import admin_routes, auth_routes, query_routes
from app.config import load_config, load_env, require_env

log = logging.getLogger("researchiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Check the environment, create the database and seed accounts and papers."""
    load_env()
    env = require_env(
        ["JWT_SECRET", "ADMIN_LOGIN", "ADMIN_PASSWORD", "USER_LOGIN", "USER_PASSWORD"]
    )
    conn = db.connect()
    db.create_schema(conn)
    db.seed_users(
        conn,
        [
            (env["ADMIN_LOGIN"], env["ADMIN_PASSWORD"], "ADMIN"),
            (env["USER_LOGIN"], env["USER_PASSWORD"], "USER"),
        ],
    )
    db.seed_papers(conn)
    conn.close()
    yield


def create_app() -> FastAPI:
    """Build the application with its routes, CORS and error handlers."""
    app = FastAPI(title="ResearchIQ", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=load_config()["server"]["cors_origins"],
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(auth_routes.router)
    app.include_router(query_routes.router)
    app.include_router(admin_routes.router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        """422 that names the offending fields and never echoes the submitted values."""
        fields = [
            {"field": ".".join(str(p) for p in e["loc"] if p != "body"), "problem": e["msg"]}
            for e in error.errors()
        ]
        return JSONResponse(
            status_code=422, content={"detail": "Invalid request", "errors": fields}
        )

    @app.exception_handler(sqlite3.OperationalError)
    async def database_busy(request: Request, error: sqlite3.OperationalError):
        """503 when the database is locked or unavailable; the reader can simply try again."""
        log.warning("database error on %s %s: %s", request.method, request.url.path, error)
        return JSONResponse(
            status_code=503, content={"detail": "The database is busy. Try again in a moment."}
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception):
        """500 with a request ID only; the details are logged on the server."""
        request_id = uuid.uuid4().hex[:12]
        log.exception(
            "unhandled error on %s %s, request %s", request.method, request.url.path, request_id
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal error", "request_id": request_id}
        )

    return app


app = create_app()
