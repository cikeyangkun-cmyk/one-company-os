from dataclasses import dataclass
from enum import StrEnum

from .models import ScoreInputs


class ScoreBand(StrEnum):
    IMMEDIATE = "immediate"
    CANDIDATE = "candidate"
    DISCARD = "discard"


@dataclass(frozen=True)
class ScoreResult:
    total: float
    band: ScoreBand


def classify_score(inputs: ScoreInputs) -> ScoreResult:
    total = inputs.total
    if total >= 75:
        band = ScoreBand.IMMEDIATE
    elif total >= 60:
        band = ScoreBand.CANDIDATE
    else:
        band = ScoreBand.DISCARD
    return ScoreResult(total=total, band=band)
