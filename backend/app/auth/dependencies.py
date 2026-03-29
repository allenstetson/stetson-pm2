"""FastAPI dependency that silently resolves the current user from a Bearer token.

Design intent
-------------
Returns ``None`` instead of raising 401/403 so that callers can decide what to
do with an unauthenticated request.  Endpoints that serve public data (project
list, project detail for non-sensitive records) simply treat a ``None`` user as
an unauthenticated visitor.  Endpoints that require admin access check the role
themselves and raise an appropriate error.

This means:
- Unauthenticated visitors receive the public view silently.
- No ``WWW-Authenticate`` challenge header is sent, which prevents browsers
  from showing a native login prompt.
- Sensitive project existence is never revealed by an auth challenge.
"""

from typing import Optional

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Resolve the current user from ``Authorization: Bearer <token>``.

    Returns ``None`` on any failure — missing header, bad token, expired token,
    or unknown username.  Never raises.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:].strip()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: Optional[str] = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.username == username).first()
