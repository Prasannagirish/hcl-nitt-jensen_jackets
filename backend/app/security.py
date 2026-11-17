"""Passwords and login tokens.

Passwords are stored as salted scrypt hashes (standard library). Login tokens are signed JWTs with
an expiry; the signing secret comes from the environment, never from code.
"""

import hashlib
import hmac
import os
from datetime import UTC, datetime, timedelta

import jwt

SCRYPT = {"n": 2**14, "r": 8, "p": 1, "dklen": 32}
ALGORITHM = "HS256"
# A fixed hash checked when the login is unknown, so unknown and wrong-password logins take
# the same time and the answer does not reveal which logins exist.
DUMMY_HASH = "scrypt$" + "00" * 16 + "$" + "00" * 32


def hash_password(password: str) -> str:
    """Salted scrypt hash in the form scrypt$salt$key (both hex)."""
    salt = os.urandom(16)
    key = hashlib.scrypt(password.encode(), salt=salt, **SCRYPT)
    return f"scrypt${salt.hex()}${key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """True when the password matches the stored hash."""
    try:
        _, salt_hex, key_hex = stored.split("$")
        key = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **SCRYPT)
    except ValueError:
        return False
    return hmac.compare_digest(key.hex(), key_hex)


def make_token(user_id: int, role: str, secret: str, hours: int) -> str:
    """A signed token carrying the user ID and role, valid for the given number of hours."""
    expires = datetime.now(UTC) + timedelta(hours=hours)
    return jwt.encode({"sub": str(user_id), "role": role, "exp": expires}, secret, ALGORITHM)


def read_token(token: str, secret: str) -> dict | None:
    """The token's claims, or None when it is invalid, tampered with or expired."""
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
