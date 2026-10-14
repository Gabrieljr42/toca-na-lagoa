"""Database engine, session helpers and initial seed."""

from collections.abc import Iterator

from sqlalchemy import Engine, inspect, text
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATA_DIR, DATABASE_URL
from app.models import Settings

engine: Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    """Create tables and seed default settings on first run."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    _add_missing_columns()
    with Session(engine) as session:
        if session.get(Settings, 1) is None:
            session.add(Settings(id=1))
            session.commit()


def _add_missing_columns() -> None:
    """Add model columns created after the database was (``create_all`` never alters tables).

    Only nullable columns are supported, which is all the app has needed so far.
    """
    with engine.begin() as connection:
        for table in SQLModel.metadata.sorted_tables:
            existing = {column["name"] for column in inspect(connection).get_columns(table.name)}
            for column in table.columns:
                if column.name not in existing:
                    column_type = column.type.compile(dialect=connection.dialect)
                    connection.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {column_type}'))


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""
    with Session(engine) as session:
        yield session


def load_settings(session: Session) -> Settings:
    """Return the single settings row."""
    settings = session.get(Settings, 1)
    if settings is None:
        raise RuntimeError("settings row missing; init_db() was not called")
    return settings
