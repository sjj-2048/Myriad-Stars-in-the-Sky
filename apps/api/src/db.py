from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from config import get_settings


settings = get_settings()


DATABASE_URL = "postgresql+psycopg://mystar:mystar@localhost:5432/mystar"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def init_db() -> None:
    """创建所有 ORM 表。真实项目中会使用 Alembic 迁移，这里仅用于本地快速起步。"""

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


