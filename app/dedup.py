"""Grouping of the same apartment advertised on more than one portal."""

from dataclasses import dataclass

from app.config import RENT
from app.normalize import normalize_text

MAX_AREA_DIFFERENCE_M2 = 3
MAX_PRICE_DIFFERENCE_RATIO = 0.05


@dataclass(frozen=True)
class GroupCandidate:
    """The fields used to decide whether two listings are the same apartment."""

    listing_id: int
    source: str
    neighborhood: str
    area: int | None
    price: int
    business: str = RENT


def assign_groups(candidates: list[GroupCandidate]) -> dict[int, int | None]:
    """Group listings that look like the same apartment on different sources.

    Two listings match when they come from different sources, are offered the
    same way (to rent or to buy), are in the same neighborhood, have known areas
    within 3 m² and prices within 5%. Matches are transitive.

    Args:
        candidates: Active listings to compare.

    Returns:
        Map of listing id to group id (the smallest listing id in the group),
        or None for listings that matched nothing.
    """
    parent = {candidate.listing_id: candidate.listing_id for candidate in candidates}
    for index, first in enumerate(candidates):
        for second in candidates[index + 1 :]:
            if are_same_apartment(first, second):
                _union(parent, first.listing_id, second.listing_id)

    roots = {listing_id: _find(parent, listing_id) for listing_id in parent}
    group_sizes: dict[int, int] = {}
    for root in roots.values():
        group_sizes[root] = group_sizes.get(root, 0) + 1
    return {listing_id: root if group_sizes[root] > 1 else None for listing_id, root in roots.items()}


def are_same_apartment(first: GroupCandidate, second: GroupCandidate) -> bool:
    """Whether two listings from different sources describe the same apartment."""
    if first.source == second.source or first.business != second.business:
        return False
    if first.area is None or second.area is None:
        return False
    if normalize_text(first.neighborhood) != normalize_text(second.neighborhood):
        return False
    if abs(first.area - second.area) > MAX_AREA_DIFFERENCE_M2:
        return False
    higher_price = max(first.price, second.price)
    return higher_price > 0 and abs(first.price - second.price) / higher_price <= MAX_PRICE_DIFFERENCE_RATIO


def _find(parent: dict[int, int], listing_id: int) -> int:
    """Root of a union-find set, compressing the path on the way."""
    while parent[listing_id] != listing_id:
        parent[listing_id] = parent[parent[listing_id]]
        listing_id = parent[listing_id]
    return listing_id


def _union(parent: dict[int, int], first_id: int, second_id: int) -> None:
    """Merge two union-find sets, keeping the smallest id as root."""
    first_root, second_root = _find(parent, first_id), _find(parent, second_id)
    if first_root != second_root:
        parent[max(first_root, second_root)] = min(first_root, second_root)
