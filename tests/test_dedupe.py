from datetime import datetime, timezone

from one_company_os.dedupe import find_duplicate, normalize_title
from one_company_os.models import (
    Category,
    Hotspot,
    RiskSignals,
    ScoreInputs,
    Source,
    SourceTier,
)


def make_hotspot(hotspot_id: str, title: str) -> Hotspot:
    return Hotspot(
        hotspot_id=hotspot_id,
        title=title,
        first_seen=datetime(2026, 7, 14, tzinfo=timezone.utc),
        category=Category.SOCIAL,
        secondary_categories=(),
        sources=(Source("通报", "https://example.com/notice", SourceTier.PRIMARY),),
        confirmed_facts=("已发布正式通报",),
        unconfirmed_claims=(),
        score_inputs=ScoreInputs(20, 20, 10, 10, 8, 10, 4),
        risk_signals=RiskSignals(),
    )


def test_normalize_title_removes_spacing_and_punctuation() -> None:
    assert normalize_title("医院回应：老人看牙，遭全口拔牙！") == "医院回应老人看牙遭全口拔牙"


def test_same_id_is_duplicate() -> None:
    existing = make_hotspot("event-1", "医院发布情况说明")
    candidate = make_hotspot("event-1", "另一种标题")
    assert find_duplicate(candidate, (existing,)) is existing


def test_nearly_identical_title_is_duplicate() -> None:
    existing = make_hotspot("event-1", "老人看牙遭全口拔光医院被处罚")
    candidate = make_hotspot("event-2", "老人看牙遭全口拔光，医院被处罚")
    assert find_duplicate(candidate, (existing,)) is existing


def test_distinct_event_is_not_duplicate() -> None:
    existing = make_hotspot("event-1", "老人看牙遭全口拔光医院被处罚")
    candidate = make_hotspot("event-2", "多地公布养老金调整方案")
    assert find_duplicate(candidate, (existing,)) is None


def test_empty_normalized_titles_with_different_ids_are_not_duplicates() -> None:
    existing = make_hotspot("event-1", "!!!")
    candidate = make_hotspot("event-2", "🔥")
    assert find_duplicate(candidate, (existing,)) is None
