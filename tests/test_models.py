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


def test_score_inputs_reject_out_of_range_component() -> None:
    with pytest.raises(ValueError, match="heat must be between 0 and 25"):
        ScoreInputs(
            heat=26,
            relevance=20,
            conflict=15,
            depth=15,
            longevity=10,
            evidence=10,
            originality=5,
        )


def test_hotspot_requires_at_least_one_source() -> None:
    with pytest.raises(ValueError, match="at least one source"):
        Hotspot(
            hotspot_id="event-1",
            title="医院因违规行为被处罚",
            first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
            category=Category.SOCIAL,
            secondary_categories=(),
            sources=(),
            confirmed_facts=("监管部门已发布处罚通报",),
            unconfirmed_claims=(),
            score_inputs=ScoreInputs(20, 20, 10, 10, 8, 10, 4),
            risk_signals=RiskSignals(),
        )


def test_source_rejects_non_http_url() -> None:
    with pytest.raises(ValueError, match="http or https"):
        Source(title="通报", url="file:///tmp/report", tier=SourceTier.PRIMARY)
