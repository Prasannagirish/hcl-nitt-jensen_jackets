"""Login and "who am I" routes."""

import sqlite3

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app import db, security
from app.api.deps import current_user, get_db, jwt_secret, unauthorized
from app.config import load_config

router = APIRouter()


class LoginRequest(BaseModel):
    """Credentials sent to /auth/login."""

    login: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


@router.post("/auth/login")
def login(body: LoginRequest, conn: sqlite3.Connection = Depends(get_db)) -> dict:
    """Check credentials and return a bearer token. Wrong login and wrong password look the same."""
    row = conn.execute(
        "SELECT user_id, role, password_hash, disabled FROM users WHERE login = ?", (body.login,)
    ).fetchone()
    stored = row["password_hash"] if row else security.DUMMY_HASH
    valid = (
        security.verify_password(body.password, stored) and row is not None and not row["disabled"]
    )
    if not valid:
        db.write_audit(conn, row["user_id"] if row else None, "login", "denied")
        raise unauthorized("Invalid login or password")
    db.write_audit(conn, row["user_id"], "login", "ok")
    hours = load_config()["auth"]["token_hours"]
    token = security.make_token(row["user_id"], row["role"], jwt_secret(), hours)
    return {"access_token": token, "token_type": "bearer", "role": row["role"]}


@router.get("/me")
def me(user: dict = Depends(current_user)) -> dict:
    """The signed-in user's login and role."""
    return {"login": user["login"], "role": user["role"]}
