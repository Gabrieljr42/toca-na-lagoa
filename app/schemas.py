"""Request and response models of the JSON API.

Validation messages are user-facing, so they are written in Portuguese.
"""

import re

from pydantic import BaseModel, NaiveDatetime, field_validator, model_validator

from app.config import SOURCE_LABELS
from app.financing import SYSTEM_LABELS, FinancingEstimate, FinancingTerms
from app.models import Listing, PriceHistory, Settings, SourceStatus
from app.views import ListingCard

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ListingOut(BaseModel):
    """A listing as shown on a card."""

    id: int
    source: str
    business: str
    url: str
    title: str
    kind: str
    bedrooms: int
    area: int | None
    rent: int
    sale_price: int | None
    condo: int
    iptu: int
    total: int
    neighborhood: str
    address: str
    image_url: str
    furnished: bool | None
    first_seen: NaiveDatetime
    last_seen: NaiveDatetime
    active: bool
    favorite: bool
    hidden: bool

    @classmethod
    def from_model(cls, listing: Listing) -> "ListingOut":
        """Build from the database row."""
        return cls.model_validate(listing, from_attributes=True)


class CopyOut(BaseModel):
    """The same apartment advertised on another portal."""

    source: str
    url: str
    total: int


class PricePointOut(BaseModel):
    """One observed total price."""

    observed_at: NaiveDatetime
    total: int


class FinancingOut(BaseModel):
    """Estimated mortgage for a listing for sale."""

    down_payment: int
    financed: int
    first_installment: int
    last_installment: int
    monthly_cost: int

    @classmethod
    def from_estimate(cls, estimate: FinancingEstimate, monthly_cost: int) -> "FinancingOut":
        """Build from the estimate and the card's monthly cost (first installment + condo + IPTU)."""
        return cls(
            down_payment=estimate.down_payment,
            financed=estimate.financed,
            first_installment=estimate.first_installment,
            last_installment=estimate.last_installment,
            monthly_cost=monthly_cost,
        )


class CardOut(BaseModel):
    """One apartment on the listings page, with its copies, price history and, for sales, the mortgage estimate."""

    listing: ListingOut
    copies: list[CopyOut]
    history: list[PricePointOut]
    is_new: bool
    price_per_m2: float | None
    previous_total: int | None
    financing: FinancingOut | None = None

    @classmethod
    def from_card(cls, card: ListingCard) -> "CardOut":
        """Build from the view model assembled by ``app.views``."""
        return cls(
            listing=ListingOut.from_model(card.listing),
            copies=[CopyOut(source=copy.source, url=copy.url, total=copy.total) for copy in card.copies],
            history=[_price_point(point) for point in card.history],
            is_new=card.is_new,
            price_per_m2=card.price_per_m2,
            previous_total=card.previous_total,
            financing=FinancingOut.from_estimate(card.financing, card.monthly_cost) if card.financing else None,
        )


def _price_point(point: PriceHistory) -> PricePointOut:
    """Convert a price history row."""
    return PricePointOut(observed_at=point.observed_at, total=point.total)


class FinancingTermsOut(BaseModel):
    """The mortgage terms behind the estimates, summarized on the page."""

    down_payment_percent: int
    yearly_rate_percent: float
    term_years: int
    system: str
    system_label: str

    @classmethod
    def from_terms(cls, terms: FinancingTerms) -> "FinancingTermsOut":
        """Build from the terms in the settings."""
        return cls(
            down_payment_percent=terms.down_payment_percent,
            yearly_rate_percent=terms.yearly_rate_percent,
            term_years=terms.term_years,
            system=terms.system,
            system_label=SYSTEM_LABELS.get(terms.system, terms.system),
        )


class ListingsOut(BaseModel):
    """The listings page content for the requested business and filters.

    ``search_enabled`` is false when that business is not being searched
    (sales are opt-in), so the page can explain why it is empty.
    """

    cards: list[CardOut]
    neighborhoods: list[str]
    search_enabled: bool = True
    financing: FinancingTermsOut | None = None


class ListingUpdate(BaseModel):
    """Flags the user can toggle on a listing; omitted fields are left unchanged."""

    favorite: bool | None = None
    hidden: bool | None = None


class SourceStatusOut(BaseModel):
    """Outcome of the latest fetch from one portal for one business."""

    source: str
    business: str
    label: str
    ok: bool
    found: int
    error: str

    @classmethod
    def from_model(cls, status: SourceStatus) -> "SourceStatusOut":
        """Build from the database row."""
        return cls(
            source=status.source,
            business=status.business,
            label=SOURCE_LABELS.get(status.source, status.source),
            ok=status.ok,
            found=status.found,
            error=status.error,
        )


class StatusOut(BaseModel):
    """Monitor status, polled by the UI to refresh itself after scheduled checks."""

    last_check_at: NaiveDatetime | None
    last_check_status: str
    running: bool
    sources: list[SourceStatusOut]


class SettingsOut(BaseModel):
    """Search and alert settings; the bot token itself is never sent back."""

    enabled: bool
    check_times: list[str]
    neighborhoods: list[str]
    max_bedrooms: int
    max_area: int | None
    min_total: int | None
    max_total: int | None
    sale_enabled: bool
    sale_max_bedrooms: int
    sale_max_area: int | None
    sale_min_price: int | None
    sale_max_price: int | None
    sale_max_monthly: int | None
    financing_down_payment_percent: int
    financing_rate: float
    financing_term_years: int
    financing_system: str
    telegram_token_set: bool
    telegram_chat_id: str
    telegram_configured: bool

    @classmethod
    def from_model(cls, settings: Settings) -> "SettingsOut":
        """Build from the settings row."""
        return cls(
            enabled=settings.enabled,
            check_times=settings.check_time_list,
            neighborhoods=settings.neighborhood_list,
            max_bedrooms=settings.max_bedrooms,
            max_area=settings.max_area,
            min_total=settings.min_total,
            max_total=settings.max_total,
            sale_enabled=settings.sale_enabled,
            sale_max_bedrooms=settings.sale_max_bedrooms,
            sale_max_area=settings.sale_max_area,
            sale_min_price=settings.sale_min_price,
            sale_max_price=settings.sale_max_price,
            sale_max_monthly=settings.sale_max_monthly,
            financing_down_payment_percent=settings.financing_down_payment_percent,
            financing_rate=settings.financing_rate,
            financing_term_years=settings.financing_term_years,
            financing_system=settings.financing_system,
            telegram_token_set=bool(settings.telegram_bot_token),
            telegram_chat_id=settings.telegram_chat_id,
            telegram_configured=settings.telegram_configured,
        )


class SettingsUpdate(BaseModel):
    """Search settings submitted from the settings page; sale fields fall back to the model defaults."""

    enabled: bool
    check_times: list[str]
    neighborhoods: list[str]
    max_bedrooms: int
    max_area: int | None = None
    min_total: int | None = None
    max_total: int | None = None
    sale_enabled: bool = False
    sale_max_bedrooms: int = 2
    sale_max_area: int | None = None
    sale_min_price: int | None = None
    sale_max_price: int | None = None
    sale_max_monthly: int | None = None
    financing_down_payment_percent: int = 20
    financing_rate: float = 11.5
    financing_term_years: int = 30
    financing_system: str = "sac"

    @field_validator("check_times")
    @classmethod
    def _valid_times(cls, times: list[str]) -> list[str]:
        cleaned = sorted({time.strip() for time in times if time.strip()})
        if not cleaned or not all(TIME_PATTERN.match(time) for time in cleaned):
            raise ValueError("Horários de verificação inválidos")
        return cleaned

    @field_validator("neighborhoods")
    @classmethod
    def _at_least_one_neighborhood(cls, names: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(" ".join(name.split()) for name in names if name.strip()))
        if not cleaned:
            raise ValueError("Informe pelo menos um bairro")
        if any("," in name for name in cleaned):
            raise ValueError("Nome de bairro não pode conter vírgula")
        return cleaned

    @field_validator("max_bedrooms", "sale_max_bedrooms")
    @classmethod
    def _bedrooms_in_range(cls, bedrooms: int) -> int:
        if not 0 <= bedrooms <= 5:
            raise ValueError("Máximo de quartos deve ficar entre 0 e 5")
        return bedrooms

    @field_validator(
        "max_area", "min_total", "max_total", "sale_max_area", "sale_min_price", "sale_max_price", "sale_max_monthly"
    )
    @classmethod
    def _positive_or_blank(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("Use um valor positivo ou deixe em branco")
        return value

    @field_validator("financing_down_payment_percent")
    @classmethod
    def _down_payment_in_range(cls, percent: int) -> int:
        if not 0 <= percent <= 100:
            raise ValueError("A entrada deve ficar entre 0 e 100% do preço")
        return percent

    @field_validator("financing_rate")
    @classmethod
    def _rate_in_range(cls, rate: float) -> float:
        if not 0 <= rate <= 50:
            raise ValueError("Os juros devem ficar entre 0 e 50% ao ano")
        return rate

    @field_validator("financing_term_years")
    @classmethod
    def _term_in_range(cls, years: int) -> int:
        if not 1 <= years <= 35:
            raise ValueError("O prazo deve ficar entre 1 e 35 anos")
        return years

    @field_validator("financing_system")
    @classmethod
    def _known_system(cls, system: str) -> str:
        if system not in SYSTEM_LABELS:
            raise ValueError("Sistema de amortização inválido: use SAC ou Price")
        return system

    @model_validator(mode="after")
    def _min_not_above_max(self) -> "SettingsUpdate":
        if self.min_total is not None and self.max_total is not None and self.min_total > self.max_total:
            raise ValueError("O valor mínimo é maior que o máximo")
        if (
            self.sale_min_price is not None
            and self.sale_max_price is not None
            and self.sale_min_price > self.sale_max_price
        ):
            raise ValueError("O preço mínimo de compra é maior que o máximo")
        return self


class TelegramUpdate(BaseModel):
    """Telegram credentials; a blank token keeps the saved one."""

    bot_token: str = ""
    chat_id: str = ""


class FavoritesSummaryOut(BaseModel):
    """How many favorites are still listed and how many left the portals."""

    available: int
    gone: int


class OptionsOut(BaseModel):
    """Labels and choices the UI needs to render filters and forms."""

    source_labels: dict[str, str]
    kind_labels: dict[str, str]
    sort_labels: dict[str, dict[str, str]]
    financing_system_labels: dict[str, str]
    default_neighborhoods: list[str]
    neighborhood_suggestions: list[str]


class MessageOut(BaseModel):
    """A short user-facing confirmation."""

    message: str
