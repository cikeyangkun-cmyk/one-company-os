import pytest

from one_company_os.models import RiskLevel, RiskSignals
from one_company_os.risk import assess_risk


def test_no_signals_is_low_risk() -> None:
    result = assess_risk(RiskSignals())
    assert result.level is RiskLevel.LOW
    assert result.requires_human is False
    assert result.hard_block is False
    assert result.reasons == ()


@pytest.mark.parametrize(
    "signals",
    [
        RiskSignals(involves_minor=True),
        RiskSignals(unconfirmed_casualty=True),
        RiskSignals(privacy_issue=True),
        RiskSignals(medical_conclusion=True),
        RiskSignals(legal_conclusion=True),
        RiskSignals(financial_conclusion=True),
    ],
)
def test_sensitive_signals_pause_for_human(signals: RiskSignals) -> None:
    result = assess_risk(signals)
    assert result.level is RiskLevel.HIGH
    assert result.requires_human is True
    assert result.hard_block is False


@pytest.mark.parametrize(
    "signals",
    [RiskSignals(unverified_only=True), RiskSignals(fabricated_quote_required=True)],
)
def test_unverifiable_or_fabricated_content_is_hard_blocked(
    signals: RiskSignals,
) -> None:
    result = assess_risk(signals)
    assert result.level is RiskLevel.HIGH
    assert result.requires_human is True
    assert result.hard_block is True
