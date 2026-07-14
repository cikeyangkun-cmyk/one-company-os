from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Category(StrEnum):
    SOCIAL = "social"
    LEGAL = "legal"
    MONEY = "money"
    INTERNATIONAL = "international"
    PEOPLE = "people"


class SourceTier(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TRAFFIC = "traffic"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class WorkflowState(StrEnum):
    NEW = "new"
    VERIFYING = "verifying"
    SCORING = "scoring"
    CANDIDATE = "candidate"
    DISCARDED = "discarded"
    ASSIGNED = "assigned"
    RISK_PAUSED = "risk_paused"
    MATERIAL_READY = "material_ready"
    WRITING = "writing"
    QUALITY_REVIEW = "quality_review"
    HUMAN_REVIEW = "human_review"
    PUBLISHED = "published"
    REVIEW_PENDING = "review_pending"
    ARCHIVED = "archived"
    MANUAL_QUEUE = "manual_queue"


def _bounded(name: str, value: float, maximum: float) -> None:
    if not 0 <= value <= maximum:
        raise ValueError(f"{name} must be between 0 and {maximum:g}")


@dataclass(frozen=True)
class ScoreInputs:
    heat: float
    relevance: float
    conflict: float
    depth: float
    longevity: float
    evidence: float
    originality: float

    def __post_init__(self) -> None:
        for name, maximum in (
            ("heat", 25),
            ("relevance", 20),
            ("conflict", 15),
            ("depth", 15),
            ("longevity", 10),
            ("evidence", 10),
            ("originality", 5),
        ):
            _bounded(name, float(getattr(self, name)), maximum)

    @property
    def total(self) -> float:
        return sum(
            (
                self.heat,
                self.relevance,
                self.conflict,
                self.depth,
                self.longevity,
                self.evidence,
                self.originality,
            )
        )


@dataclass(frozen=True)
class RiskSignals:
    unverified_only: bool = False
    involves_minor: bool = False
    unconfirmed_casualty: bool = False
    privacy_issue: bool = False
    medical_conclusion: bool = False
    legal_conclusion: bool = False
    financial_conclusion: bool = False
    fabricated_quote_required: bool = False


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    tier: SourceTier

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("source title must not be empty")
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("source URL must use http or https")


@dataclass(frozen=True)
class Hotspot:
    hotspot_id: str
    title: str
    first_seen: datetime
    category: Category
    secondary_categories: tuple[Category, ...]
    sources: tuple[Source, ...]
    confirmed_facts: tuple[str, ...]
    unconfirmed_claims: tuple[str, ...]
    score_inputs: ScoreInputs
    risk_signals: RiskSignals = field(default_factory=RiskSignals)

    def __post_init__(self) -> None:
        if not self.hotspot_id.strip():
            raise ValueError("hotspot_id must not be empty")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.sources:
            raise ValueError("hotspot requires at least one source")
