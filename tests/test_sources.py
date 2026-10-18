"""Tests for parsing recorded responses of each source."""

import json
from dataclasses import replace

import httpx
import pytest
import respx

from app.config import RENT, SALE
from app.sources import netimoveis, quintoandar, zap
from app.sources.base import SearchCriteria, SourceError
from tests.conftest import load_fixture

CRITERIA = SearchCriteria(neighborhoods=["São Luiz"], max_bedrooms=1, max_area=None)


def test_should_parse_quintoandar_hit():
    hits = load_fixture("quintoandar_search.json")["hits"]["hits"]
    listing = quintoandar.parse_hit(hits[0]["_source"])
    assert listing.external_id == "894801089"
    assert listing.url == "https://www.quintoandar.com.br/imovel/894801089"
    assert listing.kind == "apartment"
    assert (listing.rent, listing.total) == (4500, 6031)
    assert (listing.neighborhood, listing.alt_neighborhood) == ("São Luíz", "Pampulha")
    assert listing.image_url.startswith("https://www.quintoandar.com.br/img/med/")


def test_should_mark_quintoandar_houses_as_unwanted_kind():
    hits = load_fixture("quintoandar_search.json")["hits"]["hits"]
    kinds = {hit["_source"]["type"]: quintoandar.parse_hit(hit["_source"]).kind for hit in hits}
    assert kinds == {"Apartamento": "apartment", "StudioOuKitchenette": "studio", "Casa": None}


def test_should_parse_zap_residential_listing():
    items = load_fixture("zap_listings.json")["search"]["result"]["listings"]
    listing = zap.parse_item(items[0], "zap", "https://www.zapimoveis.com.br")
    assert listing.external_id == "2911269940"
    assert listing.kind == "penthouse"
    assert (listing.rent, listing.condo, listing.iptu) == (6500, 600, 0)
    assert listing.url.startswith("https://www.zapimoveis.com.br/imovel/")
    assert "{" not in listing.image_url


def test_should_skip_zap_commercial_listing():
    items = load_fixture("zap_listings.json")["search"]["result"]["listings"]
    commercial = [item for item in items if "COMMERCIAL" in item["listing"]["usageTypes"]]
    assert zap.parse_item(commercial[0], "zap", "https://www.zapimoveis.com.br") is None


def test_should_parse_netimoveis_item():
    items = load_fixture("netimoveis_search.json")["imovelCampos"]
    listing = netimoveis.parse_item(items[0])
    assert listing.external_id == "1080699"
    assert listing.kind == "penthouse"
    assert (listing.rent, listing.condo, listing.iptu, listing.area) == (3500, 250, 109, 121)
    assert listing.neighborhood == "Castelo"
    assert listing.url.startswith("https://www.netimoveis.com/imovel/")


@respx.mock
async def test_should_page_through_zap_until_total_count(monkeypatch):
    first_page = load_fixture("zap_listings.json")
    first_page["search"]["totalCount"] = 35
    second_page = {"search": {"totalCount": 35, "result": {"listings": []}}}
    route = respx.get(zap.API_URL).mock(
        side_effect=[httpx.Response(200, json=first_page), httpx.Response(200, json=second_page)],
    )
    monkeypatch.setattr(zap, "SECONDS_BETWEEN_REQUESTS", 0)
    async with httpx.AsyncClient() as client:
        listings = await zap.GlueSource("vivareal").fetch(client, CRITERIA)
    assert route.call_count == 2
    assert route.calls[0].request.headers["x-domain"] == ".vivareal.com.br"
    assert {listing.source for listing in listings} == {"vivareal"}


@respx.mock
async def test_should_raise_source_error_on_http_failure():
    respx.post(quintoandar.SEARCH_URL).mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as client:
        with pytest.raises(SourceError):
            await quintoandar.QuintoAndarSource().fetch(client, CRITERIA)


@respx.mock
async def test_should_stop_netimoveis_paging_at_total():
    body = load_fixture("netimoveis_search.json")
    route = respx.post(netimoveis.SEARCH_URL).mock(return_value=httpx.Response(200, json=body))
    async with httpx.AsyncClient() as client:
        listings = await netimoveis.NetimoveisSource().fetch(client, CRITERIA)
    assert route.call_count == 1
    assert len(listings) == len(body["imovelCampos"])


def test_should_parse_quintoandar_sale_hit():
    hits = load_fixture("quintoandar_sale_search.json")["hits"]["hits"]
    listing = quintoandar.parse_hit(hits[0]["_source"], SALE)
    assert listing.business == SALE
    assert (listing.sale_price, listing.rent, listing.condo) == (380_000, 0, 430)
    assert listing.total == 380_000
    assert listing.url == "https://www.quintoandar.com.br/imovel/895802180/comprar"


def test_should_read_zap_price_of_the_requested_business():
    items = load_fixture("zap_sale_listings.json")["search"]["result"]["listings"]
    listing = zap.parse_item(items[0], "zap", "https://www.zapimoveis.com.br", SALE)
    assert (listing.business, listing.sale_price, listing.condo) == (SALE, 559_760, 350)
    assert listing.total == 559_760
    assert zap.parse_item(items[0], "zap", "https://www.zapimoveis.com.br", RENT) is None


def test_should_parse_netimoveis_sale_item():
    items = load_fixture("netimoveis_sale_search.json")["imovelCampos"]
    listing = netimoveis.parse_item(items[1], SALE)
    assert (listing.sale_price, listing.condo, listing.iptu, listing.area) == (380_000, 320, 120, 49)
    assert listing.neighborhood == "Castelo"


@respx.mock
async def test_should_request_sales_from_every_portal(monkeypatch):
    monkeypatch.setattr(zap, "SECONDS_BETWEEN_REQUESTS", 0)
    quintoandar_route = respx.post(quintoandar.SEARCH_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("quintoandar_sale_search.json")),
    )
    zap_route = respx.get(zap.API_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("zap_sale_listings.json")),
    )
    netimoveis_route = respx.post(netimoveis.SEARCH_URL).mock(
        return_value=httpx.Response(200, json=load_fixture("netimoveis_sale_search.json")),
    )
    criteria = replace(CRITERIA, business=SALE)
    async with httpx.AsyncClient() as client:
        await quintoandar.QuintoAndarSource().fetch(client, criteria)
        await zap.GlueSource("zap").fetch(client, criteria)
        await netimoveis.NetimoveisSource().fetch(client, criteria)
    assert json.loads(quintoandar_route.calls[0].request.content)["filters"]["businessContext"] == "SALE"
    assert zap_route.calls[0].request.url.params["business"] == "SALE"
    assert json.loads(netimoveis_route.calls[0].request.content)["transacao"] == "venda"
