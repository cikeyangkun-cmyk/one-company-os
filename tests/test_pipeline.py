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
    source_tier: SourceTier = SourceTier.PRIMARY,
) -> Hotspot:
    return Hotspot(
        hotspot_id=hotspot_id,
        title="医院因违规行为被处罚",
        first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
        category=Category.SOCIAL,
        secondary_categories=(),
        sources=(Source("正式通报", "https://example.com/notice", source_tier),),
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


def test_candidate_hotspot_is_retained_with_one_account() -> None:
    candidate_score = ScoreInputs(24, 20, 10, 10, 5, 5, 0)

    decision = evaluate_hotspot(make_hotspot(score=candidate_score), (), {})

    assert decision.status is DecisionStatus.CANDIDATE
    assert decision.state is WorkflowState.CANDIDATE
    assert decision.account_id == 1


def test_duplicate_is_discarded_before_scoring() -> None:
    existing = make_hotspot(hotspot_id="event-1")
    candidate = replace(existing, title="完全不同的展示标题")
    decision = evaluate_hotspot(candidate, (existing,), {})
    assert decision.status is DecisionStatus.DUPLICATE
    assert decision.duplicate_of == "event-1"
    assert decision.account_id is None


def test_duplicate_takes_precedence_over_risk_pause() -> None:
    existing = make_hotspot(hotspot_id="event-1")
    risky_duplicate = replace(
        existing,
        risk_signals=RiskSignals(involves_minor=True),
    )

    decision = evaluate_hotspot(risky_duplicate, (existing,), {})

    assert decision.status is DecisionStatus.DUPLICATE
    assert decision.state is WorkflowState.DISCARDED
    assert decision.duplicate_of == "event-1"
    assert decision.account_id is None


def test_risky_hotspot_is_paused_even_with_high_score() -> None:
    decision = evaluate_hotspot(
        make_hotspot(risk=RiskSignals(involves_minor=True)), (), {}
    )
    assert decision.status is DecisionStatus.RISK_PAUSE
    assert decision.state is WorkflowState.RISK_PAUSED
    assert decision.account_id is None


def test_traffic_only_sources_pause_even_when_caller_marks_facts_confirmed() -> None:
    hotspot = make_hotspot(source_tier=SourceTier.TRAFFIC)
    assert hotspot.confirmed_facts
    assert hotspot.risk_signals.unverified_only is False

    decision = evaluate_hotspot(hotspot, (), {})

    assert decision.status is DecisionStatus.RISK_PAUSE
    assert decision.state is WorkflowState.RISK_PAUSED
    assert decision.account_id is None
    assert "traffic_sources_only" in decision.reasons


@pytest.mark.parametrize("source_tier", [SourceTier.PRIMARY, SourceTier.SECONDARY])
def test_reliable_source_preserves_account_assignment(source_tier: SourceTier) -> None:
    decision = evaluate_hotspot(make_hotspot(source_tier=source_tier), (), {})

    assert decision.status is DecisionStatus.IMMEDIATE
    assert decision.state is WorkflowState.ASSIGNED
    assert decision.account_id == 1


def test_low_score_is_discarded() -> None:
    low = ScoreInputs(9, 20, 10, 10, 5, 5, 0)
    decision = evaluate_hotspot(make_hotspot(score=low), (), {})
    assert decision.status is DecisionStatus.DISCARD
    assert decision.score == 59
    assert decision.state is WorkflowState.DISCARDED


@pytest.mark.parametrize(
    "current",
    [
        WorkflowState.NEW,
        WorkflowState.VERIFYING,
        WorkflowState.SCORING,
        WorkflowState.CANDIDATE,
        WorkflowState.ASSIGNED,
        WorkflowState.MATERIAL_READY,
        WorkflowState.WRITING,
        WorkflowState.QUALITY_REVIEW,
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.MANUAL_QUEUE,
    ],
)
def test_every_prepublication_state_can_enter_risk_pause(
    current: WorkflowState,
) -> None:
    assert transition(current, WorkflowState.RISK_PAUSED) is WorkflowState.RISK_PAUSED


def test_valid_review_lifecycle_reaches_published() -> None:
    human_review = transition(WorkflowState.QUALITY_REVIEW, WorkflowState.HUMAN_REVIEW)
    assert transition(human_review, WorkflowState.PUBLISHED) is WorkflowState.PUBLISHED


@pytest.mark.parametrize(
    "current",
    [state for state in WorkflowState if state is not WorkflowState.HUMAN_REVIEW],
)
def test_direct_publication_from_non_human_review_state_is_rejected(
    current: WorkflowState,
) -> None:
    with pytest.raises(ValueError, match="invalid workflow transition"):
        transition(current, WorkflowState.PUBLISHED)
