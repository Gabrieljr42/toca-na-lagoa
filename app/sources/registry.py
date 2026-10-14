"""Registry of the listing sources searched on every check."""

from app.sources.base import Source
from app.sources.netimoveis import NetimoveisSource
from app.sources.quintoandar import QuintoAndarSource
from app.sources.zap import GlueSource


def all_sources() -> list[Source]:
    """Every source, in the order they are fetched."""
    return [QuintoAndarSource(), GlueSource("zap"), GlueSource("vivareal"), NetimoveisSource()]
