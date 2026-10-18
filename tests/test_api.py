"""Tests for the JSON API used by the Vue front end."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.db import load_settings
from app.main import app
from app.models import Listing

NOW = datetime(2026, 10, 14, 9, 0)


@pytest.fixture
def client(session) -> TestClient:
    """API client over a fresh database (the lifespan, and so the scheduler, is not started)."""
    return TestClient(app)


@pytest.fixture
def listing(session) -> Listing:
    """One stored, active listing."""
    stored = Listing(
        source="zap",
        external_id="1",
        url="https://example.com/1",
        title="Apto",
        kind="apartment",
        bedrooms=1,
        area=40,
        rent=1500,
        total=1500,
        neighborhood="São Luiz",
        first_seen=NOW,
        last_seen=NOW,
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)
    return stored


def valid_settings(**overrides) -> dict:
    """A settings payload the API accepts."""
    return {
        "enabled": True,
        "check_times": ["20:00", "08:00"],
        "neighborhoods": ["Pampulha", " São  Luiz ", "Pampulha"],
        "max_bedrooms": 1,
        "max_area": 70,
        "min_total": 1200,
        "max_total": 2500,
    } | overrides


def test_should_serve_the_vue_shell_for_page_routes(client):
    for path in ("/", "/comprar", "/settings"):
        response = client.get(path)
        assert response.status_code == 200
        assert 'id="app"' in response.text


def test_should_list_cards_with_filters(client, listing):
    assert len(client.get("/api/listings").json()["cards"]) == 1
    assert client.get("/api/listings", params={"favorites": "1"}).json()["cards"] == []


def test_should_start_watching_when_favorited(client, session, listing):
    response = client.patch(f"/api/listings/{listing.id}", json={"favorite": True})
    assert response.status_code == 200
    assert response.json()["favorite"] is True
    session.refresh(listing)
    assert listing.watched_total == 1500
    assert listing.watched_active is True


def test_should_return_404_for_unknown_listing(client, session):
    response = client.patch("/api/listings/999", json={"hidden": True})
    assert response.status_code == 404
    assert response.json()["detail"] == "Anúncio não encontrado"


def test_should_save_and_clean_settings(client):
    response = client.put("/api/settings", json=valid_settings())
    assert response.status_code == 200
    saved = response.json()
    assert saved["check_times"] == ["08:00", "20:00"]
    assert saved["neighborhoods"] == ["Pampulha", "São Luiz"]
    assert (saved["min_total"], saved["max_total"]) == (1200, 2500)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"min_total": 3000, "max_total": 2000}, "O valor mínimo é maior que o máximo"),
        ({"neighborhoods": [" "]}, "Informe pelo menos um bairro"),
        ({"check_times": ["25:00"]}, "Horários de verificação inválidos"),
        ({"max_bedrooms": 9}, "Máximo de quartos deve ficar entre 0 e 5"),
        ({"sale_min_price": 500_000, "sale_max_price": 300_000}, "O preço mínimo de compra é maior que o máximo"),
        ({"financing_down_payment_percent": 120}, "A entrada deve ficar entre 0 e 100% do preço"),
        ({"financing_term_years": 40}, "O prazo deve ficar entre 1 e 35 anos"),
        ({"financing_system": "sacre"}, "Sistema de amortização inválido: use SAC ou Price"),
    ],
)
def test_should_reject_invalid_settings_with_portuguese_message(client, overrides, message):
    response = client.put("/api/settings", json=valid_settings(**overrides))
    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_should_never_return_the_bot_token(client):
    client.put("/api/telegram", json={"bot_token": "secret-token", "chat_id": "42"})
    settings = client.get("/api/settings").json()
    assert "secret-token" not in str(settings)
    assert settings["telegram_token_set"] is True
    assert settings["telegram_configured"] is True


def test_should_report_status_and_favorites_summary(client, listing):
    client.patch(f"/api/listings/{listing.id}", json={"favorite": True})
    assert client.get("/api/favorites/summary").json() == {"available": 1, "gone": 0}
    status = client.get("/api/status").json()
    assert status["running"] is False
    assert status["last_check_at"] is None


@pytest.fixture
def sale_listing(session) -> Listing:
    """One stored, active listing for sale in the same neighborhood as ``listing``."""
    stored = Listing(
        source="zap",
        business="sale",
        external_id="1",
        url="https://example.com/sale/1",
        title="Apto à venda",
        kind="apartment",
        bedrooms=2,
        area=50,
        rent=0,
        sale_price=400_000,
        condo=300,
        iptu=50,
        total=400_000,
        neighborhood="Castelo",
        first_seen=NOW,
        last_seen=NOW,
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)
    return stored


def test_should_list_each_business_on_its_own_page(client, listing, sale_listing):
    rentals = client.get("/api/listings").json()
    sales = client.get("/api/listings", params={"business": "sale"}).json()
    assert [card["listing"]["business"] for card in rentals["cards"]] == ["rent"]
    assert [card["listing"]["business"] for card in sales["cards"]] == ["sale"]
    assert (rentals["neighborhoods"], sales["neighborhoods"]) == (["São Luiz"], ["Castelo"])
    assert rentals["cards"][0]["financing"] is None


def test_should_estimate_financing_with_saved_terms(client, sale_listing):
    client.put(
        "/api/settings",
        json=valid_settings(
            sale_enabled=True,
            financing_down_payment_percent=20,
            financing_rate=12,
            financing_term_years=30,
            financing_system="price",
        ),
    )
    page = client.get("/api/listings", params={"business": "sale", "sort": "monthly"}).json()
    assert page["search_enabled"] is True
    assert page["financing"]["system_label"] == "Price"
    financing = page["cards"][0]["financing"]
    assert (financing["down_payment"], financing["first_installment"]) == (80_000, 3141)
    assert financing["monthly_cost"] == 3141 + 350


def test_should_flag_sale_page_while_sale_search_is_off(client, sale_listing):
    assert client.get("/api/listings", params={"business": "sale"}).json()["search_enabled"] is False


def test_should_forget_first_sale_fill_when_sales_are_turned_off(client, session):
    settings = load_settings(session)
    settings.sale_enabled = True
    settings.sale_initial_sync_done = True
    session.add(settings)
    session.commit()
    client.put("/api/settings", json=valid_settings(sale_enabled=False))
    session.refresh(settings)
    assert settings.sale_initial_sync_done is False


def test_should_offer_sort_labels_per_business(client):
    sort_labels = client.get("/api/options").json()["sort_labels"]
    assert "monthly" in sort_labels["sale"]
    assert "monthly" not in sort_labels["rent"]
