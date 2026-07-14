import json
from pathlib import Path

import pytest

from one_company_os.cli import main


def valid_payload() -> dict[str, object]:
    return {
        "hotspot": {
            "hotspot_id": "social-001",
            "title": "医院因违规行为被处罚",
            "first_seen": "2026-07-14T08:00:00+08:00",
            "category": "social",
            "secondary_categories": ["legal"],
            "sources": [
                {
                    "title": "正式通报",
                    "url": "https://example.com/notice",
                    "tier": "primary",
                }
            ],
            "confirmed_facts": ["监管部门已经发布处罚通报"],
            "unconfirmed_claims": [],
            "score_inputs": {
                "heat": 25,
                "relevance": 20,
                "conflict": 10,
                "depth": 10,
                "longevity": 5,
                "evidence": 5,
                "originality": 0,
            },
            "risk_signals": {},
        },
        "existing": [],
        "performance_by_account": {"1": 20.0, "2": 10.0},
    }


def test_cli_emits_stable_json(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "input.json"
    input_path.write_text(json.dumps(valid_payload(), ensure_ascii=False), encoding="utf-8")
    assert main(["evaluate", "--input", str(input_path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {
        "account_id": 1,
        "duplicate_of": None,
        "hotspot_id": "social-001",
        "reasons": [],
        "score": 75,
        "state": "assigned",
        "status": "immediate",
    }


def test_cli_returns_2_for_invalid_input(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "bad.json"
    input_path.write_text('{"hotspot": {}}', encoding="utf-8")
    assert main(["evaluate", "--input", str(input_path)]) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["error"] == "invalid_input"
    assert "hotspot_id" in error["message"]


def test_cli_returns_2_when_input_file_is_missing(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "missing.json"

    assert main(["evaluate", "--input", str(input_path)]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error["error"] == "invalid_input"
    assert str(input_path) in error["message"]


def test_cli_returns_2_when_performance_is_not_an_object(
    tmp_path: Path, capsys
) -> None:
    payload = valid_payload()
    payload["performance_by_account"] = []
    input_path = tmp_path / "bad-shape.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["evaluate", "--input", str(input_path)]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error == {
        "error": "invalid_input",
        "message": "performance_by_account must be a JSON object",
    }


@pytest.mark.parametrize("non_finite", ["NaN", "Infinity", "-Infinity"])
def test_cli_returns_2_for_non_finite_performance(
    non_finite: str, tmp_path: Path, capsys
) -> None:
    payload = valid_payload()
    payload["performance_by_account"] = {"1": non_finite}
    input_path = tmp_path / "non-finite.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["evaluate", "--input", str(input_path)]) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error == {
        "error": "invalid_input",
        "message": "performance for account 1 must be finite",
    }
