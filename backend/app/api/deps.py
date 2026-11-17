"""Shared request dependencies: database connection, signed-in user, admin check.

Access control is enforced here, on the server, for every protected route.
"""

import sqlite3
from collections.abc import Iterator

from fastapi import Depends, Header, HTTPException

from app import db, security
from app.config import require_env


def jwt_secret() -> str:
    """The token signing secret from the environment."""
    return require_env(["JWT_SECRET"])["JWT_SECRET"]


def get_db() -> Iterator[sqlite3.Connection]:
    """A database connection for one request, closed afterwards."""
    conn = db.connect()
    try:
        yield conn
    finally:
        conn.close()


def unauthorized(message: str = "Sign in required") -> HTTPException:
    """401 with the header that tells clients to send a bearer token."""
    return HTTPException(status_code=401, detail=message, headers={"WWW-Authenticate": "Bearer"})


def current_user(
    authorization: str | None = Header(default=None), conn: sqlite3.Connection = Depends(get_db)
) -> dict:
    """The signed-in user, or a 401 when the token is missing, invalid, expired or disabled."""
    scheme, _, token = (authorization or "").partition(" ")
    claims = security.read_token(token, jwt_secret()) if scheme.lower() == "bearer" else None
    if claims is None:
        raise unauthorized()
    row = conn.execute(
        "SELECT user_id, login, role, disabled FROM users WHERE user_id = ?", (claims["sub"],)
    ).fetchone()
    if row is None or row["disabled"]:
        raise unauthorized()
    return {"user_id": row["user_id"], "login": row["login"], "role": row["role"]}


def require_admin(user: dict = Depends(current_user)) -> dict:
    """The signed-in user, only if they are an admin; otherwise 403."""
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
