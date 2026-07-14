from datetime import datetime, timezone

import pytest

from one_company_os.models import (
    Category,
    Hotspot,
    RiskSignals,
    ScoreInputs,
    Source,
    SourceTier,
)
from one_company_os.pipeline import DecisionStatus, evaluate_hotspot


def make_hotspot(category: Category) -> Hotspot:
    return Hotspot(
        hotspot_id=f"acceptance-{category.value}",
        title=f"{category.value} acceptance event",
        first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
        category=category,
        secondary_categories=(),
        sources=(
            Source(
                title="Official source",
                url=f"https://example.com/{category.value}",
                tier=SourceTier.PRIMARY,
            ),
        ),
        confirmed_facts=("A responsible body published a formal notice.",),
        unconfirmed_claims=(),
        score_inputs=ScoreInputs(25, 20, 10, 10, 5, 5, 0),
        risk_signals=RiskSignals(),
    )


@pytest.mark.parametrize(
    ("category", "expected_account"),
    [
        (Category.SOCIAL, 1),
        (Category.LEGAL, 2),
        (Category.MONEY, 3),
        (Category.INTERNATIONAL, 4),
        (Category.PEOPLE, 5),
    ],
)
def test_each_category_reaches_one_expected_account(
    category: Category, expected_account: int
) -> None:
    decision = evaluate_hotspot(make_hotspot(category), (), {})
    assert decision.status is DecisionStatus.IMMEDIATE
    assert decision.account_id == expected_account


def test_minor_content_never_reaches_an_account() -> None:
    hotspot = make_hotspot(Category.SOCIAL)
    risky = Hotspot(
        hotspot_id=hotspot.hotspot_id,
        title=hotspot.title,
        first_seen=hotspot.first_seen,
        category=hotspot.category,
        secondary_categories=hotspot.secondary_categories,
        sources=hotspot.sources,
        confirmed_facts=hotspot.confirmed_facts,
        unconfirmed_claims=hotspot.unconfirmed_claims,
        score_inputs=hotspot.score_inputs,
        risk_signals=RiskSignals(involves_minor=True),
    )
    decision = evaluate_hotspot(risky, (), {})
    assert decision.status is DecisionStatus.RISK_PAUSE
    assert decision.account_id is None


def test_package_exports_the_typed_pipeline_surface() -> None:
    import one_company_os

    expected = [
        "Category",
        "DecisionStatus",
        "Hotspot",
        "PipelineDecision",
        "RiskSignals",
        "ScoreInputs",
        "Source",
        "SourceTier",
        "evaluate_hotspot",
    ]
    assert one_company_os.__all__ == expected
    assert one_company_os.Category is Category
    assert one_company_os.DecisionStatus is DecisionStatus
    assert one_company_os.evaluate_hotspot is evaluate_hotspot
