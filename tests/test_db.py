"""Tests for upgrading a database created by an older version of the app."""

from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, select

from app.db import engine, init_db
from app.models import Listing, PriceHistory, Settings, SourceStatus

OLD_SCHEMA = [
    """CREATE TABLE listing (
        id INTEGER PRIMARY KEY, source VARCHAR NOT NULL, external_id VARCHAR NOT NULL, url VARCHAR NOT NULL,
        title VARCHAR NOT NULL, kind VARCHAR NOT NULL, bedrooms INTEGER NOT NULL, area INTEGER,
        rent INTEGER NOT NULL, condo INTEGER NOT NULL, iptu INTEGER NOT NULL, total INTEGER NOT NULL,
        neighborhood VARCHAR NOT NULL, address VARCHAR NOT NULL, image_url VARCHAR NOT NULL, furnished BOOLEAN,
        first_seen DATETIME NOT NULL, last_seen DATETIME NOT NULL, active BOOLEAN NOT NULL,
        favorite BOOLEAN NOT NULL, hidden BOOLEAN NOT NULL, group_id INTEGER, notified BOOLEAN NOT NULL,
        watched_total INTEGER, watched_active BOOLEAN, UNIQUE (source, external_id))""",
    """CREATE TABLE pricehistory (
        id INTEGER PRIMARY KEY, listing_id INTEGER NOT NULL REFERENCES listing (id),
        observed_at DATETIME NOT NULL, total INTEGER NOT NULL)""",
    """CREATE TABLE sourcestatus (
        source VARCHAR PRIMARY KEY, last_run_at DATETIME, ok BOOLEAN NOT NULL, found INTEGER NOT NULL,
        error VARCHAR NOT NULL)""",
    """CREATE TABLE settings (
        id INTEGER PRIMARY KEY, enabled BOOLEAN NOT NULL, check_times VARCHAR NOT NULL,
        neighborhoods VARCHAR NOT NULL, max_bedrooms INTEGER NOT NULL, max_area INTEGER, min_total INTEGER,
        max_total INTEGER, initial_sync_done BOOLEAN NOT NULL, telegram_bot_token VARCHAR NOT NULL,
        telegram_chat_id VARCHAR NOT NULL, last_check_at DATETIME, last_check_status VARCHAR NOT NULL)""",
    """INSERT INTO listing VALUES (7, 'zap', '42', 'https://example.com/42', 'Apto', 'apartment', 1, 40,
        1500, 0, 0, 1500, 'São Luiz', '', '', NULL, '2026-10-01 08:00:00', '2026-10-01 08:00:00', 1, 1, 0,
        NULL, 1, 1500, 1)""",
    "INSERT INTO pricehistory VALUES (1, 7, '2026-10-01 08:00:00', 1500)",
    "INSERT INTO sourcestatus VALUES ('zap', '2026-10-01 08:00:00', 1, 1, '')",
    """INSERT INTO settings VALUES (1, 1, '08:00', 'São Luiz', 1, 70, NULL, 2500, 1, 'token', 'chat', NULL,
        'ok')""",
]


def test_should_upgrade_old_database_keeping_its_rows(session):
    session.close()
    SQLModel.metadata.drop_all(engine)
    with engine.begin() as connection:
        for statement in OLD_SCHEMA:
            connection.execute(text(statement))

    init_db()

    with Session(engine) as db_session:
        listing = db_session.get(Listing, 7)
        assert (listing.business, listing.favorite, listing.sale_price) == ("rent", True, None)
        assert db_session.exec(select(PriceHistory)).one().listing_id == 7
        assert db_session.get(SourceStatus, ("zap", "rent")).found == 1
        settings = db_session.get(Settings, 1)
        assert (settings.max_total, settings.telegram_chat_id) == (2500, "chat")
        assert (settings.sale_enabled, settings.financing_rate, settings.financing_system) == (False, 11.5, "sac")
    unique_keys = [unique["column_names"] for unique in inspect(engine).get_unique_constraints("listing")]
    assert sorted(map(sorted, unique_keys)) == [["business", "external_id", "source"]]
    assert "ix_listing_business" in {index["name"] for index in inspect(engine).get_indexes("listing")}


def test_should_not_rebuild_an_up_to_date_database(session, monkeypatch):
    rebuilt: list[str] = []
    monkeypatch.setattr("app.db._rebuild_table", lambda connection, table: rebuilt.append(table.name))
    init_db()
    assert rebuilt == []
