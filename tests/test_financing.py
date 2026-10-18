"""Tests for the mortgage estimate shown on listings for sale."""

import pytest

from app.financing import PRICE, SAC, FinancingEstimate, FinancingTerms, estimate


def test_should_estimate_sac_with_falling_installments():
    loan = estimate(400_000, FinancingTerms(down_payment_percent=20, yearly_rate_percent=12, term_years=30))
    assert loan == FinancingEstimate(
        down_payment=80_000, financed=320_000, first_installment=3925, last_installment=897
    )


def test_should_estimate_price_with_constant_installment():
    loan = estimate(400_000, FinancingTerms(20, 12, 30, PRICE))
    assert (loan.first_installment, loan.last_installment) == (3141, 3141)


def test_should_split_principal_evenly_without_interest():
    assert estimate(400_000, FinancingTerms(20, 0, 30, PRICE)).first_installment == 889


@pytest.mark.parametrize("system", [SAC, PRICE])
def test_should_have_no_installment_when_paid_in_cash(system):
    loan = estimate(400_000, FinancingTerms(100, 12, 30, system))
    assert loan == FinancingEstimate(down_payment=400_000, financed=0, first_installment=0, last_installment=0)


def test_should_convert_effective_yearly_rate_to_monthly():
    terms = FinancingTerms(20, 12, 30)
    assert (1 + terms.monthly_rate) ** 12 == pytest.approx(1.12)
    assert terms.term_months == 360
