from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

from .models import (
    Category,
    Hotspot,
    RiskSignals,
    ScoreInputs,
    Source,
    SourceTier,
)
from .pipeline import PipelineDecision, evaluate_hotspot


def _require_object(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _parse_hotspot(data: dict[str, Any]) -> Hotspot:
    return Hotspot(
        hotspot_id=data["hotspot_id"],
        title=data["title"],
        first_seen=datetime.fromisoformat(data["first_seen"]),
        category=Category(data["category"]),
        secondary_categories=tuple(
            Category(item) for item in data.get("secondary_categories", [])
        ),
        sources=tuple(
            Source(
                title=item["title"],
                url=item["url"],
                tier=SourceTier(item["tier"]),
            )
            for item in data["sources"]
        ),
        confirmed_facts=tuple(data.get("confirmed_facts", [])),
        unconfirmed_claims=tuple(data.get("unconfirmed_claims", [])),
        score_inputs=ScoreInputs(**data["score_inputs"]),
        risk_signals=RiskSignals(**data.get("risk_signals", {})),
    )


def _decision_to_dict(decision: PipelineDecision) -> dict[str, object]:
    output = asdict(decision)
    output["status"] = decision.status.value
    output["state"] = decision.state.value
    output["reasons"] = list(decision.reasons)
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="one-company-os")
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--input", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
        payload = _require_object(json.loads(raw), "input")
        hotspot = _parse_hotspot(_require_object(payload["hotspot"], "hotspot"))
        existing = tuple(
            _parse_hotspot(_require_object(item, "existing item"))
            for item in payload.get("existing", [])
        )
        performance_data = _require_object(
            payload.get("performance_by_account", {}), "performance_by_account"
        )
        performance = {
            int(key): float(value)
            for key, value in performance_data.items()
        }
        decision = evaluate_hotspot(hotspot, existing, performance)
    except (
        AttributeError,
        KeyError,
        OSError,
        OverflowError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"error": "invalid_input", "message": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(_decision_to_dict(decision), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
