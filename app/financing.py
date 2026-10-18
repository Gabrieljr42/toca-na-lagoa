"""Mortgage estimate for listings for sale.

Uses the two amortization systems offered by Brazilian banks: SAC (constant
amortization, installments fall over time) and Price (constant installment).
Insurance (MIP/DFI) and bank fees are left out, so the result is an estimate.
"""

from dataclasses import dataclass

SAC = "sac"
PRICE = "price"
SYSTEM_LABELS: dict[str, str] = {SAC: "SAC", PRICE: "Price"}


@dataclass(frozen=True)
class FinancingTerms:
    """The loan the user expects to get, as configured in the UI."""

    down_payment_percent: int
    yearly_rate_percent: float
    term_years: int
    system: str = SAC

    @property
    def term_months(self) -> int:
        """Number of monthly installments."""
        return self.term_years * 12

    @property
    def monthly_rate(self) -> float:
        """Monthly rate equivalent to the effective yearly rate banks advertise."""
        return (1 + self.yearly_rate_percent / 100) ** (1 / 12) - 1


@dataclass(frozen=True)
class FinancingEstimate:
    """Down payment and installments for one sale price, in whole reais."""

    down_payment: int
    financed: int
    first_installment: int
    last_installment: int


def estimate(price: int, terms: FinancingTerms) -> FinancingEstimate:
    """Estimate the down payment and the first and last installments of a loan.

    Args:
        price: Sale price of the property.
        terms: Down payment, interest rate, term and amortization system.

    Returns:
        The estimate; with SAC the first installment is the highest one.
    """
    down_payment = round(price * terms.down_payment_percent / 100)
    financed = price - down_payment
    months = terms.term_months
    rate = terms.monthly_rate
    if financed <= 0 or months <= 0:
        return FinancingEstimate(down_payment=price, financed=0, first_installment=0, last_installment=0)
    if terms.system == PRICE:
        installment = financed / months if rate == 0 else financed * rate / (1 - (1 + rate) ** -months)
        return FinancingEstimate(
            down_payment=down_payment,
            financed=financed,
            first_installment=round(installment),
            last_installment=round(installment),
        )
    amortization = financed / months
    return FinancingEstimate(
        down_payment=down_payment,
        financed=financed,
        first_installment=round(amortization + financed * rate),
        last_installment=round(amortization * (1 + rate)),
    )
