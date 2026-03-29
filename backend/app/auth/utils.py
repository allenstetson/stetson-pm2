"""Password hashing and JWT creation utilities."""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

# bcrypt is the only active scheme; deprecated="auto" downgrades stale hashes silently.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return the bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


def create_access_token(username: str, role: str) -> str:
    """Return a signed HS256 JWT for *username* / *role*."""
    expire = datetime.now(tz=timezone.utc) + timedelta(hours=settings.token_expire_hours)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
