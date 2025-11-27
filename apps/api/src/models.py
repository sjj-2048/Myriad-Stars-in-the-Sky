from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    email: str = Field(index=True, unique=True)
    display_name: str | None = None
    avatar_url: str | None = None
    role: str = Field(default="star_owner")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    stars: list["Star"] = Relationship(back_populates="owner")


class Star(SQLModel, table=True):
    __tablename__ = "stars"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    domain: str
    persona: Optional[str] = None
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: Optional[User] = Relationship(back_populates="stars")


class MagnitudeHistory(SQLModel, table=True):
    __tablename__ = "magnitude_history"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    star_id: UUID = Field(foreign_key="stars.id", index=True)
    overall: float = 0.0
    level: str = "L1"
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeTask(SQLModel, table=True):
    __tablename__ = "knowledge_tasks"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    star_id: UUID = Field(foreign_key="stars.id", index=True)
    source_type: str = "upload"
    status: str = "completed"  # PoC 阶段直接标记完成
    payload_uri: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class StarTrial(SQLModel, table=True):
    __tablename__ = "star_trials"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str
    prompt: str
    status: str = "ongoing"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Skill(SQLModel, table=True):
    __tablename__ = "skills"  # type: ignore[assignment]

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str
    description: str | None = None
    api_endpoint: str | None = None
    status: str = "published"
    created_at: datetime = Field(default_factory=datetime.utcnow)

