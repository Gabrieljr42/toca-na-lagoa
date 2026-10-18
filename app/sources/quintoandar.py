"""QuintoAndar, via the JSON search API used by its website.

The API searches a map viewport and ranks out-of-area matches too, so the
viewport covers the whole Pampulha region and the neighborhood filter is
applied afterwards.
"""

import asyncio
import logging

import httpx

from app.config import RENT, SALE, SECONDS_BETWEEN_REQUESTS, USER_AGENT
from app.sources.base import FoundListing, SearchCriteria, SourceError

logger = logging.getLogger(__name__)

SEARCH_URL = "https://apigw.prod.quintoandar.com.br/house-listing-search/v2/search/list"
LISTING_URL = "https://www.quintoandar.com.br/imovel/{id}"
SALE_LISTING_URL = "https://www.quintoandar.com.br/imovel/{id}/comprar"
IMAGE_URL = "https://www.quintoandar.com.br/img/med/{name}"
PAGE_SIZE = 100
MAX_PAGES = 10

PAMPULHA_CENTER = {"lat": -19.8527226, "lng": -43.9559969}
PAMPULHA_VIEWPORT = {"north": -19.80, "south": -19.89, "west": -44.03, "east": -43.93}
BUSINESS_CONTEXTS = {RENT: "RENT", SALE: "SALE"}

KINDS: dict[str, str] = {
    "Apartamento": "apartment",
    "StudioOuKitchenette": "studio",
}
FIELDS = [
    "id",
    "coverImage",
    "rent",
    "salePrice",
    "totalCost",
    "iptuPlusCondominium",
    "area",
    "address",
    "regionName",
    "neighbourhood",
    "type",
    "bedrooms",
    "isFurnished",
    "shortRentDescription",
]


class QuintoAndarSource:
    """Searches rentals or sales on QuintoAndar."""

    name = "quintoandar"

    async def fetch(self, client: httpx.AsyncClient, criteria: SearchCriteria) -> list[FoundListing]:
        """Fetch every listing up to ``criteria.max_bedrooms`` bedrooms inside the Pampulha viewport."""
        listings: list[FoundListing] = []
        for page in range(MAX_PAGES):
            if page:
                await asyncio.sleep(SECONDS_BETWEEN_REQUESTS)
            payload = _search_payload(criteria.max_bedrooms, page * PAGE_SIZE, criteria.business)
            body = await _post_search(client, payload)
            hits = body["hits"]["hits"]
            listings.extend(parse_hit(hit["_source"], criteria.business) for hit in hits)
            if len(hits) < PAGE_SIZE:
                break
        return listings


def _search_payload(max_bedrooms: int, offset: int, business: str = RENT) -> dict:
    """Request body mirroring what the website sends for a list search."""
    return {
        "context": {"mapShowing": False, "listShowing": True, "numPhotos": 1, "isSSR": False},
        "filters": {
            "businessContext": BUSINESS_CONTEXTS[business],
            "blocklist": [],
            "selectedHouses": [],
            "location": {
                "coordinate": PAMPULHA_CENTER,
                "viewport": PAMPULHA_VIEWPORT,
                "neighborhoods": [],
                "countryCode": "BR",
            },
            "priceRange": [],
            "specialConditions": [],
            "excludedSpecialConditions": [],
            "houseSpecs": {
                "area": {"range": {}},
                "houseTypes": [],
                "amenities": [],
                "installations": [],
                "bathrooms": {"range": {}},
                "bedrooms": {"range": {"min": 0, "max": max_bedrooms}},
                "parkingSpace": {"range": {}},
                "suites": {"range": {}},
            },
            "availability": "ANY",
            "occupancy": "ANY",
            "partnerIds": [],
            "categories": [],
        },
        "sorting": {"criteria": "MOST_RECENT", "order": "DESC"},
        "pagination": {"pageSize": PAGE_SIZE, "offset": offset},
        "slug": "pampulha-belo-horizonte-mg-brasil",
        "fields": FIELDS,
        "locationDescriptions": [{"description": "pampulha-belo-horizonte-mg-brasil"}],
    }


async def _post_search(client: httpx.AsyncClient, payload: dict) -> dict:
    """POST a search and return the decoded body."""
    try:
        response = await client.post(
            SEARCH_URL,
            json=payload,
            headers={
                "User-Agent": USER_AGENT,
                "Origin": "https://www.quintoandar.com.br",
                "Referer": "https://www.quintoandar.com.br/",
            },
        )
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise SourceError(f"QuintoAndar: {error.__class__.__name__}") from error


def parse_hit(item: dict, business: str = RENT) -> FoundListing:
    """Convert one search hit into a FoundListing.

    QuintoAndar's ``regionName`` is the actual bairro, while ``neighbourhood`` is
    sometimes a broader label such as "Pampulha"; both are kept for matching.
    For sales, ``rent`` is zero and ``totalCost`` covers only condo and IPTU.
    """
    rent = int(item.get("rent") or 0)
    condo_and_iptu = int(item.get("iptuPlusCondominium") or 0)
    cover = item.get("coverImage") or ""
    description = item.get("shortRentDescription") or ""
    is_sale = business == SALE
    return FoundListing(
        source="quintoandar",
        external_id=str(item["id"]),
        url=(SALE_LISTING_URL if is_sale else LISTING_URL).format(id=item["id"]),
        title=description or f"{item.get('type', 'Imóvel')} em {item.get('regionName', '')}",
        kind=KINDS.get(item.get("type", "")),
        bedrooms=int(item.get("bedrooms") or 0),
        area=item.get("area"),
        rent=rent,
        condo=condo_and_iptu,
        iptu=0,
        neighborhood=item.get("regionName") or "",
        alt_neighborhood=item.get("neighbourhood") or "",
        address=item.get("address") or "",
        image_url=IMAGE_URL.format(name=cover) if cover else "",
        furnished=item.get("isFurnished"),
        total_override=int(item["totalCost"]) if item.get("totalCost") and not is_sale else None,
        business=business,
        sale_price=int(item.get("salePrice") or 0) if is_sale else None,
    )
