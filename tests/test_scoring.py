import pytest

from one_company_os.models import ScoreInputs
from one_company_os.scoring import ScoreBand, classify_score


@pytest.mark.parametrize(
    ("heat", "expected_total", "expected_band"),
    [
        (25, 75, ScoreBand.IMMEDIATE),
        (24, 74, ScoreBand.CANDIDATE),
        (10, 60, ScoreBand.CANDIDATE),
        (9, 59, ScoreBand.DISCARD),
    ],
)
def test_score_boundaries(
    heat: float, expected_total: float, expected_band: ScoreBand
) -> None:
    inputs = ScoreInputs(
        heat=heat,
        relevance=20,
        conflict=10,
        depth=10,
        longevity=5,
        evidence=5,
        originality=0,
    )
    result = classify_score(inputs)
    assert result.total == expected_total
    assert result.band is expected_band
