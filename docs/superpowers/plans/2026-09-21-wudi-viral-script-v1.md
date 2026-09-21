# Wudi Viral Script V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested `wudi-viral-script` Agent Skill that converts one 吴迪 agriculture/business-owner topic into structured, truthful, shoot-ready Douyin and WeChat Video scripts with three-layer hooks and a 100-point review rubric.

**Architecture:** Keep the skill prompt-only and colocated with the existing `.agents/skills` convention. `SKILL.md` orchestrates small reference modules; a JSON Schema defines the machine-readable output contract for later workbench integration; pytest contract tests pin the file layout, safety/truth rules, scoring weights, platform differences, and acceptance-topic fixture. No runtime Python feature or new dependency is required in Phase 1.

**Tech Stack:** Agent Skills Markdown/YAML, JSON Schema document, Python >=3.11, pytest >=8,<9.

**Spec:** `docs/superpowers/specs/2026-09-21-wudi-viral-script-design.md`

## Global Constraints

- V1 ends at a human-usable, shoot-ready draft; no publishing, editing, digital human, AI voice, paid traffic, analytics dashboard, or automatic comment reply features.
- Douyin is the primary platform; WeChat Video is a distinct adaptation, never a word-for-word duplicate.
- Never fabricate customers, prices, sales, incidents, competitor behavior, quotes, statistics, or 吴迪 experiences.
- Unsupported real-story slots must produce an explicit missing-material marker.
- One video carries one core conflict, one viewpoint, and one memorable idea.
- Each hook must contain spoken line, first-frame visual, and on-screen text.
- Viral-structure scoring totals exactly 100: hook 20, tension 15, persona 15, authenticity 15, insight 15, spoken-language 10, comment potential 10.
- Scores 90+ may be called strong candidates but never “guaranteed viral”.
- Do not add runtime dependencies; keep `pyproject.toml` unchanged unless a failing test proves the existing environment cannot validate the files.

## Review Focus

- **Missing real experience:** when source material does not support a story, the skill must emit a missing-material marker rather than invent a customer or event. Pinned in Task 2 contract tests.
- **Unsupported concrete data:** prices, percentages, yields, sales, dates, or competitor claims without support must be flagged or softened, not asserted. Pinned in Task 2 contract tests.
- **Platform `both`:** Douyin and WeChat Video outputs must be separately structured and explicitly required to differ in pacing/depth. Pinned in Task 4 contract tests.
- **Weak/redundant topic:** the skill must not mechanically keep five bad angles; it may discard weak angles while preserving at least three genuinely distinct viable ones when supported. Pinned in Task 3 contract tests.
- **Long or noisy source material:** the workflow must reduce it to one core conflict/viewpoint rather than stuffing multiple unrelated points into a single video. Pinned in Task 5 contract tests.

---

## File Structure

### Create

```text
.agents/skills/wudi-viral-script/
├── SKILL.md                              # orchestration, routing, output mode, boundaries
├── agents/openai.yaml                    # skill display metadata and default prompt
├── references/
│   ├── wudi-persona.md                   # voice, positioning, do/don't language
│   ├── topic-angle.md                    # topic diagnosis and angle generation
│   ├── hook-engine.md                    # hook archetypes + three-layer hook rules
│   ├── six-part-framework.md             # 吴迪 six-part spoken-script framework
│   ├── douyin-rules.md                   # Douyin pacing and adaptation rules
│   ├── wechat-video-rules.md             # WeChat Video pacing and adaptation rules
│   ├── viral-review.md                   # scoring weights, thresholds, deduction rules
│   └── truth-check.md                    # fabrication/data/attack/fearmongering/ad checks
├── schemas/
│   └── wudi-viral-script-output.schema.json  # stable machine-readable output contract
└── templates/
    ├── script-output.md                   # human-readable rendering contract
    ├── scoring-card.md                   # review rendering contract
    └── shooting-card.md                  # shoot-plan rendering contract

tests/
├── test_wudi_viral_skill_contract.py     # deterministic contract tests
└── fixtures/
    └── wudi_viral_topics.json            # 10 representative acceptance topics
```

### Do not modify in Phase 1

```text
src/one_company_os/*
pyproject.toml
.agents/skills/one-company-os-hotspot-writing/*
```

The existing hotspot skill is a pattern reference only; the new skill must not inherit Toutiao routing behavior.

---

### Task 1: Lock the machine-readable output contract

**Files:**
- Create: `.agents/skills/wudi-viral-script/schemas/wudi-viral-script-output.schema.json`
- Create: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: approved design spec output fields.
- Produces: JSON object contract with required keys `topic_analysis`, `angles`, `hooks`, `recommended_direction`, `script`, `douyin_version`, `wechat_video_version`, `shooting`, `package`, `viral_score`, `missing_material`.

- [ ] **Step 1: Write the failing schema contract tests**

Create `tests/test_wudi_viral_skill_contract.py` with:

```python
import json
from pathlib import Path


ROOT = Path(".agents/skills/wudi-viral-script")
SCHEMA = ROOT / "schemas/wudi-viral-script-output.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def test_output_schema_exists_and_has_stable_top_level_contract() -> None:
    schema = load_schema()
    assert schema["type"] == "object"
    required = {
        "topic_analysis",
        "angles",
        "hooks",
        "recommended_direction",
        "script",
        "douyin_version",
        "wechat_video_version",
        "shooting",
        "package",
        "viral_score",
        "missing_material",
    }
    assert set(schema["required"]) == required
    assert required <= set(schema["properties"])


def test_script_schema_requires_all_six_parts() -> None:
    script = load_schema()["properties"]["script"]
    assert script["type"] == "object"
    assert set(script["required"]) == {
        "conflict_hook",
        "stance",
        "real_story",
        "insight",
        "viewpoint",
        "ending",
    }


def test_hook_schema_requires_three_layers() -> None:
    hook = load_schema()["properties"]["hooks"]["items"]
    assert {"type", "spoken", "visual", "screen_text"} <= set(hook["required"])


def test_score_schema_uses_seven_dimensions_and_total() -> None:
    score = load_schema()["properties"]["viral_score"]
    assert set(score["required"]) == {
        "hook",
        "tension",
        "persona",
        "authenticity",
        "insight",
        "spoken_language",
        "comment_potential",
        "total",
        "deductions",
        "classification",
    }
```

- [ ] **Step 2: Run tests and verify they fail because the schema is absent**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -v
```

Expected: FAIL with `FileNotFoundError` for `wudi-viral-script-output.schema.json`.

- [ ] **Step 3: Create the minimal JSON Schema**

Create `.agents/skills/wudi-viral-script/schemas/wudi-viral-script-output.schema.json` as Draft 2020-12 JSON Schema. Required structural details:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Wudi Viral Script Output",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "topic_analysis",
    "angles",
    "hooks",
    "recommended_direction",
    "script",
    "douyin_version",
    "wechat_video_version",
    "shooting",
    "package",
    "viral_score",
    "missing_material"
  ]
}
```

Define every listed property, including:
- `angles`: array of objects requiring `name`, `type`, `core_idea`, `reason`;
- `hooks`: array of objects requiring `type`, `spoken`, `visual`, `screen_text`;
- `script`: object requiring all six framework fields;
- `shooting`: object requiring `opening_frame`, `location`, `camera`, `b_roll`, `subtitle_notes`;
- `package`: object requiring `titles`, `cover_text`, `publish_caption`, `comment_prompt`;
- `viral_score`: object requiring seven dimensions, `total`, `deductions`, `classification`;
- `missing_material`: array of strings.

Use integer score ranges matching their maxima: hook `0..20`; tension/persona/authenticity/insight `0..15`; spoken_language/comment_potential `0..10`; total `0..100`.

- [ ] **Step 4: Run schema tests and verify they pass**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -v
```

Expected: all Task 1 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/wudi-viral-script/schemas/wudi-viral-script-output.schema.json tests/test_wudi_viral_skill_contract.py
git commit -m "feat: define wudi viral script output contract"
```

---

### Task 2: Encode 吴迪 persona and truth boundaries

**Files:**
- Create: `.agents/skills/wudi-viral-script/references/wudi-persona.md`
- Create: `.agents/skills/wudi-viral-script/references/truth-check.md`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: `source_material` plus the approved persona and truth rules.
- Produces: reusable voice rules and a pre-handoff truth gate used by `SKILL.md` in Task 5.

- [ ] **Step 1: Add failing persona/truth contract tests**

Append:

```python

def test_persona_reference_enforces_spoken_owner_voice() -> None:
    text = (ROOT / "references/wudi-persona.md").read_text(encoding="utf-8")
    for required in (
        "朴实",
        "直接",
        "老板视角",
        "真人一口气",
        "随着",
        "在当前市场环境下",
    ):
        assert required in text


def test_truth_reference_requires_missing_material_instead_of_fabrication() -> None:
    text = (ROOT / "references/truth-check.md").read_text(encoding="utf-8")
    for required in (
        "missing_material",
        "不得编造",
        "客户",
        "价格",
        "销量",
        "统计",
        "竞争对手",
        "真实经历",
    ):
        assert required in text


def test_truth_reference_flags_unsupported_concrete_data() -> None:
    text = (ROOT / "references/truth-check.md").read_text(encoding="utf-8")
    assert "未经来源支持" in text
    assert "模糊表达" in text or "标记待核实" in text
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "persona or truth" -v
```

Expected: FAIL because both reference files are absent.

- [ ] **Step 3: Create `wudi-persona.md`**

The file must define:
- persona: agriculture/seed-industry business owner, experienced but not professor-like;
- preferred traits: 朴实、直接、有判断、有魄力、不装专家、老板视角、有生活感;
- short breath-length sentences that a real person can say in one breath;
- preferred phrases such as “这个事情很多人搞反了”, “说实话”, “我不建议”, “这个钱该花”;
- banned/report-style examples containing “随着…发展”, “在当前市场环境下”, “对于广大种植户而言”;
- rule: if replacing 吴迪 with any generic agriculture boss leaves the script unchanged, persona strength is insufficient.

- [ ] **Step 4: Create `truth-check.md`**

The file must require a final five-part gate:
1. fabricated 吴迪 experience/customer/event → delete and add to `missing_material`;
2. price/percentage/yield/sales/date/statistic/competitor claim without source support → soften or mark for verification;
3. named-peer attack without evidence → discuss the phenomenon instead;
4. agricultural fearmongering → reduce certainty and explain limits;
5. heavy product advertising not explicitly requested → remove sales language.

Include the exact rule that a missing real-story slot is never silently filled.

- [ ] **Step 5: Run focused tests and verify pass**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "persona or truth" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/wudi-viral-script/references/wudi-persona.md .agents/skills/wudi-viral-script/references/truth-check.md tests/test_wudi_viral_skill_contract.py
git commit -m "feat: add wudi persona and truth gates"
```

---

### Task 3: Encode topic diagnosis, angle generation, and three-layer hooks

**Files:**
- Create: `.agents/skills/wudi-viral-script/references/topic-angle.md`
- Create: `.agents/skills/wudi-viral-script/references/hook-engine.md`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: `topic`, optional `source_material`, persona rules.
- Produces: `topic_analysis`, 3–5 viable `angles`, and at least six `hooks` for the chosen candidate direction.

- [ ] **Step 1: Add failing angle/hook tests**

Append:

```python

def test_topic_angle_reference_prefers_distinct_angles_over_fixed_count() -> None:
    text = (ROOT / "references/topic-angle.md").read_text(encoding="utf-8")
    for required in (
        "core_conflict",
        "target_audience",
        "wudi_authority",
        "行业内幕",
        "老板观点",
        "真实经历",
        "客户痛点",
        "反常识",
        "弱角度",
    ):
        assert required in text
    assert "至少3" in text or "至少 3" in text


def test_hook_engine_requires_batch_and_three_layers() -> None:
    text = (ROOT / "references/hook-engine.md").read_text(encoding="utf-8")
    for required in (
        "至少6",
        "spoken",
        "visual",
        "screen_text",
        "冲突型",
        "反常识型",
        "经历型",
        "内幕型",
        "对比型",
    ):
        assert required in text
    assert "匹配" in text and "payoff" in text.lower()
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "angle or hook" -v
```

Expected: FAIL because both reference files are absent.

- [ ] **Step 3: Create `topic-angle.md`**

Define diagnosis fields exactly as schema keys where applicable: `core_conflict`, `target_audience`, `audience_interest`, `wudi_authority`, `risk`.

Define the five preferred angle families. Require:
- diversity of premise, not synonym rewrites;
- discard weak/redundant angles;
- retain at least 3 distinct viable angles when the topic supports them;
- do not invent source material to rescue a weak “真实经历” angle;
- reduce long/noisy source material to one core conflict and one viewpoint.

- [ ] **Step 4: Create `hook-engine.md`**

Require at least six candidate hooks across multiple archetypes. Every hook must expose the exact schema fields `type`, `spoken`, `visual`, `screen_text`.

Include the ten archetypes from the spec and these quality gates:
- no greeting or throat-clearing;
- concrete beats vague;
- first-frame visual must carry information with sound off;
- on-screen text is short enough to scan immediately;
- the hook promise must match the actual payoff;
- never claim that a hook guarantees virality.

- [ ] **Step 5: Run focused tests and verify pass**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "angle or hook" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/wudi-viral-script/references/topic-angle.md .agents/skills/wudi-viral-script/references/hook-engine.md tests/test_wudi_viral_skill_contract.py
git commit -m "feat: add wudi topic and hook engines"
```

---

### Task 4: Encode the six-part framework and platform adapters

**Files:**
- Create: `.agents/skills/wudi-viral-script/references/six-part-framework.md`
- Create: `.agents/skills/wudi-viral-script/references/douyin-rules.md`
- Create: `.agents/skills/wudi-viral-script/references/wechat-video-rules.md`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: recommended angle, selected hook, supported source material.
- Produces: schema `script`, `douyin_version`, and `wechat_video_version` fields.

- [ ] **Step 1: Add failing framework/platform tests**

Append:

```python

def test_six_part_reference_matches_schema_and_missing_story_rule() -> None:
    text = (ROOT / "references/six-part-framework.md").read_text(encoding="utf-8")
    for required in (
        "conflict_hook",
        "stance",
        "real_story",
        "insight",
        "viewpoint",
        "ending",
        "missing_material",
    ):
        assert required in text


def test_douyin_reference_requires_fast_conflict_and_second_stimulus() -> None:
    text = (ROOT / "references/douyin-rules.md").read_text(encoding="utf-8")
    assert "35–60" in text or "35-60" in text
    assert "15–25" in text or "15-25" in text
    assert "第一句话" in text
    assert "一个问题" in text


def test_wechat_video_reference_requires_distinct_deeper_adaptation() -> None:
    text = (ROOT / "references/wechat-video-rules.md").read_text(encoding="utf-8")
    assert "60–120" in text or "60-120" in text
    assert "经历" in text
    assert "因果" in text
    assert "价值观" in text
    assert "逐字" in text or "照搬" in text
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "six_part or douyin or wechat" -v
```

Expected: FAIL because reference files are absent.

- [ ] **Step 3: Create `six-part-framework.md`**

Map exact output keys to timing and purpose:
- `conflict_hook` 0–3s;
- `stance` 3–8s;
- `real_story` 8–25s;
- `insight` 25–40s;
- `viewpoint` 40–50s;
- `ending` 50–60s.

Require `real_story` to use supported material only. If unavailable, populate `missing_material` with a concrete request such as “需要吴迪补充一次与该选题相关的真实客户/田间/经营经历”, and keep the script honest rather than fabricating a replacement.

- [ ] **Step 4: Create platform references**

`douyin-rules.md` must require conflict in the first sentence, 35–60s preferred length, one problem per video, a second stimulus around 15–25s, early face/information, and comment-driven ending.

`wechat-video-rules.md` must require 60–120s preferred length, more experience/credibility/causal explanation/values, calmer pacing, and a meaningful rewrite rather than a verbatim copy.

- [ ] **Step 5: Run focused tests and verify pass**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "six_part or douyin or wechat" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/wudi-viral-script/references/six-part-framework.md .agents/skills/wudi-viral-script/references/douyin-rules.md .agents/skills/wudi-viral-script/references/wechat-video-rules.md tests/test_wudi_viral_skill_contract.py
git commit -m "feat: add wudi script framework and platform adapters"
```

---

### Task 5: Add deterministic review rules and rendering templates

**Files:**
- Create: `.agents/skills/wudi-viral-script/references/viral-review.md`
- Create: `.agents/skills/wudi-viral-script/templates/script-output.md`
- Create: `.agents/skills/wudi-viral-script/templates/scoring-card.md`
- Create: `.agents/skills/wudi-viral-script/templates/shooting-card.md`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: complete candidate script and platform adaptations.
- Produces: `viral_score`, human-readable script rendering, score-card rendering, and shooting instructions.

- [ ] **Step 1: Add failing scoring/template tests**

Append:

```python

def test_viral_review_weights_sum_to_100_and_define_thresholds() -> None:
    text = (ROOT / "references/viral-review.md").read_text(encoding="utf-8")
    expected = {
        "hook": 20,
        "tension": 15,
        "persona": 15,
        "authenticity": 15,
        "insight": 15,
        "spoken_language": 10,
        "comment_potential": 10,
    }
    for key, weight in expected.items():
        assert f"{key}: {weight}" in text
    assert sum(expected.values()) == 100
    for threshold in ("0–64", "65–74", "75–84", "85–89", "90+"):
        assert threshold in text
    assert "deductions" in text
    assert "必爆" in text


def test_templates_expose_editable_modules_and_shooting_fields() -> None:
    script = (ROOT / "templates/script-output.md").read_text(encoding="utf-8")
    shooting = (ROOT / "templates/shooting-card.md").read_text(encoding="utf-8")
    scoring = (ROOT / "templates/scoring-card.md").read_text(encoding="utf-8")
    for field in ("冲突钩子", "吴迪表态", "真实经历", "行业信息差", "吴迪观点", "开放式结尾"):
        assert field in script
    for field in ("opening_frame", "location", "camera", "b_roll", "subtitle_notes"):
        assert field in shooting
    assert "扣分原因" in scoring
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "viral_review or templates" -v
```

Expected: FAIL because files are absent.

- [ ] **Step 3: Create `viral-review.md`**

Use exact machine keys and weights:

```text
hook: 20
tension: 15
persona: 15
authenticity: 15
insight: 15
spoken_language: 10
comment_potential: 10
```

Define concrete deduction examples for each dimension. Require `deductions` to contain actionable reasons, not generic statements. Define thresholds exactly from the design spec. Explicitly ban “必爆”, “100%爆”, “一定爆”; 90+ means only “强候选”.

- [ ] **Step 4: Create rendering templates**

`script-output.md` renders topic analysis, angle cards, hook candidates, the six editable sections, Douyin/WeChat tabs, and `missing_material`.

`scoring-card.md` renders seven dimensions, total, classification, and deduction reasons.

`shooting-card.md` renders `opening_frame`, `location`, `camera`, `b_roll`, `subtitle_notes`, and must prefer a lightweight executable shoot plan over elaborate production.

- [ ] **Step 5: Run focused tests and verify pass**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "viral_review or templates" -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/wudi-viral-script/references/viral-review.md .agents/skills/wudi-viral-script/templates tests/test_wudi_viral_skill_contract.py
git commit -m "feat: add wudi viral review and output templates"
```

---

### Task 6: Add the orchestrating Skill and agent metadata

**Files:**
- Create: `.agents/skills/wudi-viral-script/SKILL.md`
- Create: `.agents/skills/wudi-viral-script/agents/openai.yaml`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: user input `topic`, optional `platform`, `source_material`, `target_duration`, `goal`.
- Produces: one response conforming to the JSON Schema plus a human-readable rendering when requested.

- [ ] **Step 1: Add failing top-level Skill tests**

Append:

```python

def test_skill_declares_workflow_references_and_schema() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: wudi-viral-script\n")
    for required in (
        "references/wudi-persona.md",
        "references/topic-angle.md",
        "references/hook-engine.md",
        "references/six-part-framework.md",
        "references/douyin-rules.md",
        "references/wechat-video-rules.md",
        "references/viral-review.md",
        "references/truth-check.md",
        "schemas/wudi-viral-script-output.schema.json",
        "missing_material",
        "one core conflict",
    ):
        assert required in skill


def test_skill_support_files_exist() -> None:
    for path in (
        "agents/openai.yaml",
        "references/wudi-persona.md",
        "references/topic-angle.md",
        "references/hook-engine.md",
        "references/six-part-framework.md",
        "references/douyin-rules.md",
        "references/wechat-video-rules.md",
        "references/viral-review.md",
        "references/truth-check.md",
        "schemas/wudi-viral-script-output.schema.json",
        "templates/script-output.md",
        "templates/scoring-card.md",
        "templates/shooting-card.md",
    ):
        assert (ROOT / path).is_file(), path


def test_skill_supports_module_level_regeneration() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for mode in (
        "只重写Hook",
        "只重写某一段",
        "重新生成角度",
        "优化口语",
        "更像吴迪",
        "转视频号",
        "转抖音",
    ):
        assert mode in skill
```

- [ ] **Step 2: Run focused tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "skill_" -v
```

Expected: FAIL because `SKILL.md` and metadata are absent.

- [ ] **Step 3: Create `SKILL.md`**

Use concise front matter:

```yaml
---
name: wudi-viral-script
description: Use when turning a 吴迪 agriculture or seed-industry topic, source material, or draft into a truthful, shoot-ready Douyin or WeChat Video script with multi-angle ideation, three-layer hooks, 吴迪 six-part structure, platform adaptation, shooting notes, and a 100-point viral-structure review.
---
```

Required sequence:
1. parse input and default `platform` to `both` unless the user specifies one;
2. load persona + truth rules;
3. diagnose topic and reduce noisy inputs to one core conflict/viewpoint;
4. generate/distill distinct angles;
5. generate three-layer hook batch;
6. select/recommend one direction without claiming certainty;
7. build six-part script, leaving missing real experience in `missing_material`;
8. apply Douyin/WeChat adapters according to requested platform;
9. create shooting and publication package;
10. run truth check;
11. run viral review and attach deduction reasons;
12. return schema-conforming structured output; render with templates when a human-readable view is requested.

Include selective-regeneration modes exactly as tested, and state that selective regeneration must preserve untouched human-edited fields.

- [ ] **Step 4: Create `agents/openai.yaml`**

Use:

```yaml
interface:
  display_name: "Wudi Viral Script"
  short_description: "Turn 吴迪 topics into shoot-ready viral-structure scripts"
  default_prompt: "Turn this 吴迪 topic into a truthful Douyin-first script with multiple angles, three-layer hooks, the six-part 吴迪 structure, platform adaptation, shooting notes, and a scored review."
```

- [ ] **Step 5: Run the full contract test**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/wudi-viral-script/SKILL.md .agents/skills/wudi-viral-script/agents/openai.yaml tests/test_wudi_viral_skill_contract.py
git commit -m "feat: add wudi viral script skill"
```

---

### Task 7: Add the 10-topic acceptance fixture and final verification

**Files:**
- Create: `tests/fixtures/wudi_viral_topics.json`
- Modify: `tests/test_wudi_viral_skill_contract.py`

**Interfaces:**
- Consumes: ten representative topics spanning price, customer pain, industry insight, owner stance, real-story dependency, weak-topic behavior, and both platforms.
- Produces: stable manual/agent acceptance set for future prompt regression checks.

- [ ] **Step 1: Add failing fixture tests**

Append:

```python
FIXTURE = Path("tests/fixtures/wudi_viral_topics.json")


def test_acceptance_fixture_has_ten_unique_topics_and_required_cases() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert len(rows) == 10
    assert len({row["topic"] for row in rows}) == 10
    assert all(row["platform"] in {"douyin", "wechat_video", "both"} for row in rows)
    tags = {tag for row in rows for tag in row["covers"]}
    assert {
        "price",
        "customer_pain",
        "industry_insight",
        "owner_stance",
        "missing_story",
        "weak_topic",
        "both_platforms",
    } <= tags


def test_acceptance_fixture_never_supplies_invented_story_as_expected_content() -> None:
    rows = json.loads(FIXTURE.read_text(encoding="utf-8"))
    missing_story = [row for row in rows if "missing_story" in row["covers"]]
    assert missing_story
    assert all(row.get("source_material") in (None, "") for row in missing_story)
```

- [ ] **Step 2: Run fixture tests and verify failure**

Run:

```bash
pytest tests/test_wudi_viral_skill_contract.py -k "acceptance_fixture" -v
```

Expected: FAIL because the fixture is absent.

- [ ] **Step 3: Create the fixture with exactly these ten topics**

Create `tests/fixtures/wudi_viral_topics.json`:

```json
[
  {"topic":"为什么国外西兰花种子敢卖这么贵？","platform":"both","covers":["price","industry_insight","both_platforms"],"source_material":null},
  {"topic":"种子越便宜，种植户真的越省钱吗？","platform":"douyin","covers":["customer_pain","owner_stance"],"source_material":null},
  {"topic":"我为什么不建议客户只看种子价格？","platform":"douyin","covers":["owner_stance","customer_pain"],"source_material":null},
  {"topic":"国产西兰花种子真正难的是什么？","platform":"wechat_video","covers":["industry_insight"],"source_material":null},
  {"topic":"农业老板最怕客户问的一句话是什么？","platform":"douyin","covers":["missing_story","customer_pain"],"source_material":null},
  {"topic":"一个种子老板做了十几年之后，最看重客户什么？","platform":"wechat_video","covers":["missing_story","owner_stance"],"source_material":null},
  {"topic":"为什么同一个西兰花品种，在不同地方结果差很多？","platform":"both","covers":["industry_insight","both_platforms"],"source_material":null},
  {"topic":"做农业生意，到底该不该赚快钱？","platform":"wechat_video","covers":["owner_stance"],"source_material":null},
  {"topic":"西兰花很好吃","platform":"douyin","covers":["weak_topic"],"source_material":null},
  {"topic":"客户说进口种子就是智商税，我会怎么回答？","platform":"both","covers":["price","customer_pain","owner_stance","both_platforms"],"source_material":null}
]
```

- [ ] **Step 4: Run all repository tests**

Run:

```bash
pytest -v
```

Expected: all existing One Company OS tests plus the new Wudi Skill contract tests PASS.

- [ ] **Step 5: Perform manual Skill regression on the ten fixtures**

For each row, invoke `wudi-viral-script` and check the approved acceptance criteria:
- spoken, shootable draft;
- no report/AI prose;
- no invented story when source material is empty;
- at least three distinct viable angles when topic supports them;
- hooks contain spoken/visual/screen text;
- platform differences when `both`;
- score includes concrete deductions;
- output conforms to schema field names;
- weak topic is diagnosed rather than inflated into fake authority;
- 吴迪 voice remains owner-like and specific.

Record any prompt defect by adding a failing deterministic contract assertion first, then update the owning reference file.

- [ ] **Step 6: Final commit**

```bash
git add tests/fixtures/wudi_viral_topics.json tests/test_wudi_viral_skill_contract.py
git commit -m "test: add wudi viral script acceptance set"
```

---

## Final Verification

Run:

```bash
python -m pytest -v
```

Expected: complete repository test suite passes with no regressions.

Then inspect:

```bash
git status --short
git log --oneline -7
```

Expected: clean working tree and one reviewable commit per task group.

## Phase 2 Boundary

Do not modify the 吴迪 workbench UI in this plan. After Phase 1 passes the ten-topic acceptance set, write a separate implementation plan that maps `wudi-viral-script-output.schema.json` into the existing topic detail UI: angle cards, Hook section, editable six-part blocks, Douyin/WeChat tabs, shooting card, score display, missing-material prompts, and module-level regenerate actions.
