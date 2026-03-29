import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Local user account for admin access and sensitive project gating."""

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default="gen_random_uuid()",
        nullable=False,
    )
    username = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text, nullable=False)
    # role: admin | viewer
    role = Column(Text, nullable=False, server_default="viewer")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
