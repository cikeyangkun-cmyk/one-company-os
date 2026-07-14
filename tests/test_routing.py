from dataclasses import replace
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
from one_company_os.routing import route_account


def base_hotspot(category: Category) -> Hotspot:
    return Hotspot(
        hotspot_id=f"event-{category.value}",
        title="测试热点",
        first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
        category=category,
        secondary_categories=(),
        sources=(Source("通报", "https://example.com/notice", SourceTier.PRIMARY),),
        confirmed_facts=("已确认事实",),
        unconfirmed_claims=(),
        score_inputs=ScoreInputs(20, 20, 10, 10, 8, 10, 4),
        risk_signals=RiskSignals(),
    )


@pytest.mark.parametrize(
    ("category", "account"),
    [
        (Category.SOCIAL, 1),
        (Category.LEGAL, 2),
        (Category.MONEY, 3),
        (Category.INTERNATIONAL, 4),
        (Category.PEOPLE, 5),
    ],
)
def test_primary_category_routes_to_expected_account(
    category: Category, account: int
) -> None:
    assert route_account(base_hotspot(category), {}) == account


def test_secondary_category_can_win_on_historical_performance() -> None:
    hotspot = replace(
        base_hotspot(Category.SOCIAL),
        secondary_categories=(Category.LEGAL,),
    )
    assert route_account(hotspot, {1: 20.0, 2: 50.0}) == 2


def test_primary_category_wins_tie() -> None:
    hotspot = replace(
        base_hotspot(Category.SOCIAL),
        secondary_categories=(Category.LEGAL,),
    )
    assert route_account(hotspot, {1: 20.0, 2: 20.0}) == 1
