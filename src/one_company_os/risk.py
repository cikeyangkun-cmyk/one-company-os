from dataclasses import dataclass

from .models import RiskLevel, RiskSignals, Source, SourceTier


@dataclass(frozen=True)
class RiskAssessment:
    level: RiskLevel
    requires_human: bool
    hard_block: bool
    reasons: tuple[str, ...]


def assess_risk(
    signals: RiskSignals,
    sources: tuple[Source, ...] = (),
) -> RiskAssessment:
    traffic_sources_only = bool(sources) and all(
        source.tier is SourceTier.TRAFFIC for source in sources
    )
    values = {
        "unverified_only": signals.unverified_only,
        "traffic_sources_only": traffic_sources_only,
        "involves_minor": signals.involves_minor,
        "unconfirmed_casualty": signals.unconfirmed_casualty,
        "privacy_issue": signals.privacy_issue,
        "medical_conclusion": signals.medical_conclusion,
        "legal_conclusion": signals.legal_conclusion,
        "financial_conclusion": signals.financial_conclusion,
        "fabricated_quote_required": signals.fabricated_quote_required,
    }
    reasons = tuple(name for name, enabled in values.items() if enabled)
    hard_block = (
        signals.unverified_only
        or traffic_sources_only
        or signals.fabricated_quote_required
    )
    if reasons:
        return RiskAssessment(
            level=RiskLevel.HIGH,
            requires_human=True,
            hard_block=hard_block,
            reasons=reasons,
        )
    return RiskAssessment(
        level=RiskLevel.LOW,
        requires_human=False,
        hard_block=False,
        reasons=(),
    )
