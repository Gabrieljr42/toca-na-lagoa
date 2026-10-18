"""Tests for parsing helpers and the listing filter."""

from dataclasses import replace

import pytest

from app.config import SALE
from app.financing import FinancingTerms
from app.normalize import canonical_neighborhood, format_brl, matches_criteria, normalize_text, parse_area, parse_brl
from app.sources.base import FoundListing, SearchCriteria

CRITERIA = SearchCriteria(neighborhoods=["São Luiz", "Ouro Preto"], max_bedrooms=1, max_area=70)


def make_listing(**overrides) -> FoundListing:
    """A matching listing; override fields to break one rule at a time."""
    fields = {
        "source": "zap",
        "external_id": "1",
        "url": "https://example.com/1",
        "title": "Apto",
        "kind": "apartment",
        "bedrooms": 1,
        "area": 40,
        "rent": 1500,
        "condo": 300,
        "iptu": 50,
        "neighborhood": "Ouro Preto",
    }
    return FoundListing(**(fields | overrides))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("R$ 2.500", 2500), ("R$ 1.234,56", 1234), ("R$ 0", 0), ("", 0), (None, 0), ("350", 350)],
)
def test_should_parse_brl_into_whole_reais(raw, expected):
    assert parse_brl(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("105m²", 105), ("1.050 m²", 1050), ("", None), (None, None)])
def test_should_parse_area(raw, expected):
    assert parse_area(raw) == expected


def test_should_ignore_accents_and_case_when_normalizing_text():
    assert normalize_text("  São   Luíz ") == normalize_text("sao luiz")


def test_should_format_brl_with_thousands_dot():
    assert format_brl(12500) == "R$ 12.500"


def test_should_total_rent_condo_and_iptu():
    assert make_listing().total == 1850


def test_should_prefer_source_total_when_available():
    assert make_listing(total_override=2013).total == 2013


def test_should_accept_listing_matching_every_rule():
    assert matches_criteria(make_listing(), CRITERIA)


def test_should_match_neighborhood_through_alternative_name():
    listing = make_listing(neighborhood="Bairro Qualquer", alt_neighborhood="São Luíz")
    assert matches_criteria(listing, CRITERIA)


@pytest.mark.parametrize(
    "overrides",
    [
        {"neighborhood": "Savassi"},
        {"bedrooms": 2},
        {"area": 120},
        {"kind": None},
        {"rent": 0},
    ],
)
def test_should_reject_listing_breaking_a_rule(overrides):
    assert not matches_criteria(make_listing(**overrides), CRITERIA)


def test_should_reject_listing_above_max_total():
    criteria = SearchCriteria(neighborhoods=["Ouro Preto"], max_bedrooms=1, max_area=None, max_total=1800)
    assert not matches_criteria(make_listing(), criteria)
    assert matches_criteria(make_listing(rent=1450), criteria)


def test_should_reject_listing_below_min_total():
    criteria = SearchCriteria(neighborhoods=["Ouro Preto"], max_bedrooms=1, max_area=None, min_total=1500)
    assert not matches_criteria(make_listing(rent=1000), criteria)
    assert matches_criteria(make_listing(total_override=1500), criteria)


def test_should_compare_max_total_with_source_total():
    criteria = SearchCriteria(neighborhoods=["Ouro Preto"], max_bedrooms=1, max_area=None, max_total=1800)
    assert matches_criteria(make_listing(total_override=1800), criteria)


def test_should_accept_unknown_area_when_area_is_limited():
    assert matches_criteria(make_listing(area=None), CRITERIA)


def test_should_use_configured_spelling_of_neighborhood():
    listing = make_listing(neighborhood="São Luíz")
    assert canonical_neighborhood(listing, CRITERIA.neighborhoods) == "São Luiz"


def test_should_fall_back_to_alternative_name_for_canonical_neighborhood():
    listing = make_listing(neighborhood="Vila Qualquer", alt_neighborhood="ouro preto")
    assert canonical_neighborhood(listing, CRITERIA.neighborhoods) == "Ouro Preto"


SALE_CRITERIA = SearchCriteria(
    neighborhoods=["Ouro Preto"],
    max_bedrooms=2,
    max_area=None,
    max_total=400_000,
    business=SALE,
    max_monthly=3_400,
    financing=FinancingTerms(down_payment_percent=20, yearly_rate_percent=12, term_years=30),
)


def test_should_use_sale_price_as_total_of_a_sale():
    listing = make_listing(business=SALE, rent=0, sale_price=350_000, total_override=500)
    assert (listing.base_price, listing.total) == (350_000, 350_000)


@pytest.mark.parametrize(
    ("sale_price", "expected"),
    [(300_000, True), (450_000, False), (0, False)],
)
def test_should_apply_price_range_to_sale_price(sale_price, expected):
    listing = make_listing(business=SALE, rent=0, sale_price=sale_price, condo=0, iptu=0)
    assert matches_criteria(listing, replace(SALE_CRITERIA, max_monthly=None)) is expected


def test_should_reject_sale_whose_monthly_cost_is_above_limit():
    listing = make_listing(business=SALE, rent=0, sale_price=320_000, condo=300, iptu=50)
    first_installment = 3_140
    assert listing.monthly_cost(SALE_CRITERIA.financing) == first_installment + 350
    assert matches_criteria(listing, SALE_CRITERIA) is False
    assert matches_criteria(listing, replace(SALE_CRITERIA, max_monthly=3_600)) is True
