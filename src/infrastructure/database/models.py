from sqlalchemy import (
    Table,
    MetaData,
    ForeignKey,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    UUID,
    func,
    UniqueConstraint,
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("uuid", UUID, primary_key=True, unique=True, nullable=False),
    Column("name", String, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("role", String, nullable=False, default="user"),
    Column("avatar", Text),
    Column("fingerprint", Integer, unique=True, nullable=False),
    Column("status", Boolean, default=True),
    Column("date", DateTime(timezone=True), default=func.now()),
    UniqueConstraint("uuid", name="uq_users_uuid"),
    UniqueConstraint("email", name="uq_users_email"),
    UniqueConstraint("fingerprint", name="uq_users_fingerprint"),
)

sessions = Table(
    "sessions",
    metadata,
    Column("uuid", UUID, primary_key=True, unique=True, nullable=False),
    Column("access_token", Text, nullable=False),
    Column("refresh_token", Text, nullable=False),
    Column("access_token_expires_at", DateTime(timezone=True), nullable=False),
    Column("refresh_token_expires_at", DateTime(timezone=True), nullable=False),
    Column("user_agent", Text),
    Column("ip", String(255)),
    Column("revoked", Boolean, default=False),
    Column(
        "user_uuid",
        UUID,
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("type", String, nullable=False, default="manual"),
    Column("date", DateTime(timezone=True), default=func.now()),
    UniqueConstraint("uuid", name="uq_sessions_uuid"),
    UniqueConstraint("access_token", name="uq_sessions_access_token"),
    UniqueConstraint("refresh_token", name="uq_sessions_refresh_token"),
)
