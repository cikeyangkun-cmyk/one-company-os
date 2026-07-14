from pathlib import Path


SKILL = Path(".agents/skills/one-company-os-hotspot-writing/SKILL.md")


def test_skill_declares_required_workflow_and_references() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\nname: one-company-os-hotspot-writing\n")
    for required in (
        "one-company-os evaluate",
        "Never invent missing facts",
        "Human review",
        "references/account-matrix.md",
        "references/quality-gates.md",
    ):
        assert required in text


def test_skill_reference_files_exist() -> None:
    root = SKILL.parent
    assert (root / "agents/openai.yaml").is_file()
    assert (root / "references/account-matrix.md").is_file()
    assert (root / "references/quality-gates.md").is_file()
