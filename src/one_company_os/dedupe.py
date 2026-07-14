from difflib import SequenceMatcher
import unicodedata

from .models import Hotspot


def normalize_title(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower()
    return "".join(char for char in normalized if char.isalnum())


def find_duplicate(
    candidate: Hotspot,
    existing: tuple[Hotspot, ...],
    threshold: float = 0.88,
) -> Hotspot | None:
    candidate_title = normalize_title(candidate.title)
    for item in existing:
        if item.hotspot_id == candidate.hotspot_id:
            return item
        item_title = normalize_title(item.title)
        if (
            candidate_title
            and item_title
            and SequenceMatcher(None, candidate_title, item_title).ratio() >= threshold
        ):
            return item
    return None
