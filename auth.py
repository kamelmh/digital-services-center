"""Auth — SQLite users + JWT. Works offline (SQLite) and cloud (DATABASE_URL).

No new infra: uses dsc_data.db, PyJWT + passlib[bcrypt] (already installed).
Cloud: set DSC_JWT_SECRET and optionally DATABASE_URL=postgresql://...
Offline .exe: auth is opt-in — premium routes stay public unless
DSC_AUTH_REQUIRED=1 is set.
"""

from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import hashlib
import hmac
import secrets

import jwt
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

# ── Config ───────────────────────────────────────────────────────────────────

JWT_SECRET = os.getenv("DSC_JWT_SECRET", "dsc-dev-secret-32-bytes-min-change-in-prod!")
JWT_ALG = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("DSC_JWT_EXPIRE_HOURS", "72"))
AUTH_REQUIRED = os.getenv("DSC_AUTH_REQUIRED", "0") == "1"

bearer_scheme = HTTPBearer(auto_error=False)

# ── Pydantic ─────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field("", max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str = ""
    subscription: str = "free"
    subscription_until: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── DB helpers (reuse dsc_utils.get_db) ─────────────────────────────────────

def _get_db():
    from dsc_utils import get_db
    return get_db()


def init_auth_tables():
    """Ensure users table exists. Safe to call multiple times."""
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT DEFAULT '',
            password_hash TEXT NOT NULL,
            subscription TEXT DEFAULT 'free',
            subscription_until TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """)
    # Add user_id FK columns to existing tables if missing (idempotent)
    for tbl in ("dossiers", "clients", "invoices"):
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
        if "user_id" not in cols:
            conn.execute(f"ALTER TABLE {tbl} ADD COLUMN user_id INTEGER REFERENCES users(id)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{tbl}_user_id ON {tbl}(user_id)")
    conn.commit()
    conn.close()


# Called on import so tables exist for offline too
try:
    init_auth_tables()
except Exception:
    pass


# ── Core ─────────────────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000)
    return f"pbkdf2_sha256$200000${salt}${dk.hex()}"


def verify_password(pw: str, h: str) -> bool:
    # Legacy bcrypt support (old test users)
    if h.startswith("$2b$") or h.startswith("$2a$"):
        try:
            import bcrypt
            return bcrypt.checkpw(pw.encode(), h.encode())
        except Exception:
            return False
    try:
        algo, iters, salt, hexdk = h.split("$")
        it = int(iters)
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), it)
        return hmac.compare_digest(dk.hex(), hexdk)
    except Exception:
        return False


def create_token(user_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def _row_to_user(row) -> UserOut:
    return UserOut(
        id=row["id"],
        email=row["email"],
        name=row["name"] or "",
        subscription=row["subscription"] or "free",
        subscription_until=row["subscription_until"],
        created_at=str(row["created_at"]),
    )


def get_user_by_email(email: str):
    conn = _get_db()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()
    conn.close()
    return row


def get_user_by_id(uid: int):
    conn = _get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return row


def create_user(email: str, password: str, name: str = "") -> UserOut:
    email_n = email.lower().strip()
    if not EMAIL_RE.match(email_n):
        raise HTTPException(400, "Invalid email")
    if get_user_by_email(email_n):
        raise HTTPException(409, "Email already registered")
    h = hash_password(password)
    conn = _get_db()
    cur = conn.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (email_n, name.strip(), h),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    row = get_user_by_id(uid)
    return _row_to_user(row)


def authenticate(email: str, password: str) -> UserOut:
    row = get_user_by_email(email)
    if not row or not verify_password(password, row["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return _row_to_user(row)


# ── FastAPI dependencies ────────────────────────────────────────────────────

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[UserOut]:
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        uid = int(payload["sub"])
    except Exception:
        return None
    row = get_user_by_id(uid)
    if not row:
        return None
    return _row_to_user(row)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> UserOut:
    if not credentials or not credentials.credentials:
        if AUTH_REQUIRED:
            raise HTTPException(401, "Missing token")
        # Auth not required — allow anonymous as None would, but this dep
        # is for protected routes, so require token when used explicitly.
        raise HTTPException(401, "Authentication required")
    try:
        payload = decode_token(credentials.credentials)
        uid = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except Exception:
        raise HTTPException(401, "Invalid token")
    row = get_user_by_id(uid)
    if not row:
        raise HTTPException(401, "User not found")
    return _row_to_user(row)


def get_current_user_or_none(
    authorization: Optional[str] = Header(None),
) -> Optional[UserOut]:
    """Alternative dep that reads raw Authorization header (for Swagger)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:].strip()
    try:
        payload = decode_token(token)
        row = get_user_by_id(int(payload["sub"]))
        return _row_to_user(row) if row else None
    except Exception:
        return None
