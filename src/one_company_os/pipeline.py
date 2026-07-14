from dataclasses import dataclass
from enum import StrEnum

from .dedupe import find_duplicate
from .models import Hotspot, WorkflowState
from .risk import assess_risk
from .routing import route_account
from .scoring import ScoreBand, classify_score


class DecisionStatus(StrEnum):
    IMMEDIATE = "immediate"
    CANDIDATE = "candidate"
    DISCARD = "discard"
    RISK_PAUSE = "risk_pause"
    DUPLICATE = "duplicate"


@dataclass(frozen=True)
class PipelineDecision:
    hotspot_id: str
    status: DecisionStatus
    state: WorkflowState
    score: float | None
    account_id: int | None
    duplicate_of: str | None
    reasons: tuple[str, ...]


ALLOWED_TRANSITIONS: dict[WorkflowState, set[WorkflowState]] = {
    WorkflowState.NEW: {
        WorkflowState.VERIFYING,
        WorkflowState.RISK_PAUSED,
        WorkflowState.MANUAL_QUEUE,
    },
    WorkflowState.VERIFYING: {
        WorkflowState.SCORING,
        WorkflowState.RISK_PAUSED,
        WorkflowState.DISCARDED,
    },
    WorkflowState.SCORING: {
        WorkflowState.CANDIDATE,
        WorkflowState.ASSIGNED,
        WorkflowState.DISCARDED,
        WorkflowState.RISK_PAUSED,
    },
    WorkflowState.CANDIDATE: {
        WorkflowState.ASSIGNED,
        WorkflowState.RISK_PAUSED,
        WorkflowState.DISCARDED,
    },
    WorkflowState.ASSIGNED: {WorkflowState.MATERIAL_READY, WorkflowState.RISK_PAUSED},
    WorkflowState.MATERIAL_READY: {
        WorkflowState.WRITING,
        WorkflowState.RISK_PAUSED,
    },
    WorkflowState.WRITING: {
        WorkflowState.QUALITY_REVIEW,
        WorkflowState.RISK_PAUSED,
        WorkflowState.MANUAL_QUEUE,
    },
    WorkflowState.QUALITY_REVIEW: {
        WorkflowState.HUMAN_REVIEW,
        WorkflowState.WRITING,
        WorkflowState.RISK_PAUSED,
        WorkflowState.DISCARDED,
    },
    WorkflowState.HUMAN_REVIEW: {
        WorkflowState.PUBLISHED,
        WorkflowState.WRITING,
        WorkflowState.RISK_PAUSED,
        WorkflowState.DISCARDED,
    },
    WorkflowState.PUBLISHED: {WorkflowState.REVIEW_PENDING},
    WorkflowState.REVIEW_PENDING: {WorkflowState.ARCHIVED},
    WorkflowState.RISK_PAUSED: {
        WorkflowState.VERIFYING,
        WorkflowState.DISCARDED,
    },
    WorkflowState.MANUAL_QUEUE: {
        WorkflowState.VERIFYING,
        WorkflowState.RISK_PAUSED,
        WorkflowState.DISCARDED,
    },
    WorkflowState.DISCARDED: {WorkflowState.ARCHIVED},
    WorkflowState.ARCHIVED: set(),
}


def transition(current: WorkflowState, target: WorkflowState) -> WorkflowState:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"invalid workflow transition: {current} -> {target}")
    return target


def evaluate_hotspot(
    hotspot: Hotspot,
    existing: tuple[Hotspot, ...],
    performance_by_account: dict[int, float],
) -> PipelineDecision:
    duplicate = find_duplicate(hotspot, existing)
    if duplicate is not None:
        return PipelineDecision(
            hotspot_id=hotspot.hotspot_id,
            status=DecisionStatus.DUPLICATE,
            state=WorkflowState.DISCARDED,
            score=None,
            account_id=None,
            duplicate_of=duplicate.hotspot_id,
            reasons=("duplicate_event",),
        )

    risk = assess_risk(hotspot.risk_signals, hotspot.sources)
    if risk.requires_human:
        return PipelineDecision(
            hotspot_id=hotspot.hotspot_id,
            status=DecisionStatus.RISK_PAUSE,
            state=WorkflowState.RISK_PAUSED,
            score=hotspot.score_inputs.total,
            account_id=None,
            duplicate_of=None,
            reasons=risk.reasons,
        )

    score = classify_score(hotspot.score_inputs)
    if score.band is ScoreBand.DISCARD:
        return PipelineDecision(
            hotspot_id=hotspot.hotspot_id,
            status=DecisionStatus.DISCARD,
            state=WorkflowState.DISCARDED,
            score=score.total,
            account_id=None,
            duplicate_of=None,
            reasons=("score_below_60",),
        )

    account_id = route_account(hotspot, performance_by_account)
    status = (
        DecisionStatus.IMMEDIATE
        if score.band is ScoreBand.IMMEDIATE
        else DecisionStatus.CANDIDATE
    )
    state = (
        WorkflowState.ASSIGNED
        if status is DecisionStatus.IMMEDIATE
        else WorkflowState.CANDIDATE
    )
    return PipelineDecision(
        hotspot_id=hotspot.hotspot_id,
        status=status,
        state=state,
        score=score.total,
        account_id=account_id,
        duplicate_of=None,
        reasons=(),
    )
