"""Database models.

Timestamps are stored as naive local time (America/Sao_Paulo by default) and
money as whole reais, which is the precision every source publishes.
"""

from pydantic import NaiveDatetime
from sqlmodel import Field, SQLModel, UniqueConstraint

from app.config import DEFAULT_NEIGHBORHOODS, RENT, SALE
from app.financing import SAC, FinancingTerms


class Settings(SQLModel, table=True):
    """Single-row table with the monitor configuration editable from the UI.

    Neighborhoods and check times are shared; rentals and sales have their own
    size and price criteria, and sales the terms used to estimate a mortgage.
    """

    id: int | None = Field(default=1, primary_key=True)
    enabled: bool = True
    check_times: str = "08:00,14:00,20:00"
    neighborhoods: str = ",".join(DEFAULT_NEIGHBORHOODS)
    max_bedrooms: int = 1
    max_area: int | None = 70
    min_total: int | None = None
    max_total: int | None = None
    initial_sync_done: bool = False
    sale_enabled: bool = False
    sale_max_bedrooms: int = 2
    sale_max_area: int | None = None
    sale_min_price: int | None = None
    sale_max_price: int | None = None
    sale_max_monthly: int | None = None
    sale_initial_sync_done: bool = False
    financing_down_payment_percent: int = 20
    financing_rate: float = 11.5
    financing_term_years: int = 30
    financing_system: str = SAC
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    last_check_at: NaiveDatetime | None = None
    last_check_status: str = ""

    @property
    def check_time_list(self) -> list[str]:
        """Return the configured check times as a sorted list of "HH:MM" strings."""
        return sorted(time.strip() for time in self.check_times.split(",") if time.strip())

    @property
    def neighborhood_list(self) -> list[str]:
        """Return the configured neighborhoods in the order they were typed."""
        return [name.strip() for name in self.neighborhoods.split(",") if name.strip()]

    @property
    def financing_terms(self) -> FinancingTerms:
        """Mortgage terms used to estimate the installments of listings for sale."""
        return FinancingTerms(
            down_payment_percent=self.financing_down_payment_percent,
            yearly_rate_percent=self.financing_rate,
            term_years=self.financing_term_years,
            system=self.financing_system,
        )

    def businesses(self) -> list[str]:
        """The businesses searched on every check: rentals always, sales when enabled."""
        return [RENT, SALE] if self.sale_enabled else [RENT]

    def initial_sync_done_for(self, business: str) -> bool:
        """Whether a check already filled the listings of this business."""
        return self.sale_initial_sync_done if business == SALE else self.initial_sync_done

    def mark_initial_sync_done(self, business: str) -> None:
        """Record that the listings of this business were filled once."""
        if business == SALE:
            self.sale_initial_sync_done = True
        else:
            self.initial_sync_done = True

    @property
    def telegram_configured(self) -> bool:
        """Whether both the bot token and the chat id are set."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)


class Listing(SQLModel, table=True):
    """A listing to rent or to buy found on one source, kept up to date across checks.

    ``total`` is the headline price tracked in the history and favorite alerts:
    the monthly cost of a rental, or the sale price (``sale_price``) of a sale.
    A unit offered both ways is stored once per business.
    """

    __table_args__ = (UniqueConstraint("source", "business", "external_id"),)

    id: int | None = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    business: str = Field(default=RENT, index=True)
    external_id: str
    url: str
    title: str
    kind: str
    bedrooms: int
    area: int | None = None
    rent: int
    sale_price: int | None = None
    condo: int = 0
    iptu: int = 0
    total: int = Field(index=True)
    neighborhood: str = Field(index=True)
    address: str = ""
    image_url: str = ""
    furnished: bool | None = None
    first_seen: NaiveDatetime
    last_seen: NaiveDatetime
    active: bool = True
    favorite: bool = False
    hidden: bool = False
    group_id: int | None = Field(default=None, index=True)
    notified: bool = False
    watched_total: int | None = None
    watched_active: bool | None = None

    @property
    def base_price(self) -> int:
        """The advertised price: the rent of a rental or the sale price of a sale."""
        return (self.sale_price or 0) if self.business == SALE else self.rent

    def start_watching(self) -> None:
        """Take the current price and availability as the reference for favorite alerts."""
        self.watched_total = self.total
        self.watched_active = self.active


class PriceHistory(SQLModel, table=True):
    """A total price observed for a listing; a row is added only when it changes."""

    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="listing.id", index=True)
    observed_at: NaiveDatetime
    total: int


class SourceStatus(SQLModel, table=True):
    """Outcome of the latest fetch from one source for one business, shown in the UI."""

    source: str = Field(primary_key=True)
    business: str = Field(default=RENT, primary_key=True)
    last_run_at: NaiveDatetime | None = None
    ok: bool = True
    found: int = 0
    error: str = ""
