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
    WorkflowState,
)
from one_company_os.pipeline import (
    DecisionStatus,
    evaluate_hotspot,
    transition,
)


def make_hotspot(
    *,
    hotspot_id: str = "event-1",
    score: ScoreInputs | None = None,
    risk: RiskSignals | None = None,
) -> Hotspot:
    return Hotspot(
        hotspot_id=hotspot_id,
        title="医院因违规行为被处罚",
        first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
        category=Category.SOCIAL,
        secondary_categories=(),
        sources=(Source("正式通报", "https://example.com/notice", SourceTier.PRIMARY),),
        confirmed_facts=("监管部门已经发布通报",),
        unconfirmed_claims=(),
        score_inputs=score or ScoreInputs(25, 20, 10, 10, 5, 5, 0),
        risk_signals=risk or RiskSignals(),
    )


def test_immediate_hotspot_is_assigned() -> None:
    decision = evaluate_hotspot(make_hotspot(), (), {})
    assert decision.status is DecisionStatus.IMMEDIATE
    assert decision.account_id == 1
    assert decision.score == 75
    assert decision.state is WorkflowState.ASSIGNED


def test_duplicate_is_discarded_before_scoring() -> None:
    existing = make_hotspot(hotspot_id="event-1")
    candidate = replace(existing, title="完全不同的展示标题")
    decision = evaluate_hotspot(candidate, (existing,), {})
    assert decision.status is DecisionStatus.DUPLICATE
    assert decision.duplicate_of == "event-1"
    assert decision.account_id is None


def test_risky_hotspot_is_paused_even_with_high_score() -> None:
    decision = evaluate_hotspot(
        make_hotspot(risk=RiskSignals(involves_minor=True)), (), {}
    )
    assert decision.status is DecisionStatus.RISK_PAUSE
    assert decision.state is WorkflowState.RISK_PAUSED
    assert decision.account_id is None


def test_low_score_is_discarded() -> None:
    low = ScoreInputs(9, 20, 10, 10, 5, 5, 0)
    decision = evaluate_hotspot(make_hotspot(score=low), (), {})
    assert decision.status is DecisionStatus.DISCARD
    assert decision.score == 59
    assert decision.state is WorkflowState.DISCARDED


def test_invalid_state_transition_raises() -> None:
    with pytest.raises(ValueError, match="invalid workflow transition"):
        transition(WorkflowState.NEW, WorkflowState.PUBLISHED)
