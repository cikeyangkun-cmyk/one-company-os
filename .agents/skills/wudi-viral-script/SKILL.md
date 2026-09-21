---
name: wudi-viral-script
description: Use when turning a 吴迪 agriculture or seed-industry topic, source material, or draft into a truthful, shoot-ready Douyin or WeChat Video script with multi-angle ideation, three-layer hooks, 吴迪 six-part structure, platform adaptation, shooting notes, and a 100-point viral-structure review.
---

# Wudi Viral Script

This skill is the short-video writing brain for the 「吴迪吹牛」 personal IP. It does not write generic agriculture articles or corporate propaganda. It turns one focused topic into a truthful, conversational, shoot-ready script while preserving 吴迪's real voice and experience.

## Inputs

Accept the user's topic plus any available fields:

- `topic` (required): one concrete question or content idea.
- `platform`: `douyin`, `wechat_video`, or `both`; default `platform` to `both` when omitted.
- `source_material`: transcripts, interview notes, verified customer context, public data, 吴迪's own recollections, or other grounding material. Empty is valid and must never be silently filled with invented facts.
- `target_duration`: requested seconds if supplied; otherwise follow the selected platform reference.
- `goal`: reach, comments, persona building, industry influence, or customer trust.

Do not interrogate the user when enough information already exists. If factual material is missing, continue with an explicit `missing_material` list instead of making facts up.

## Required references

- Voice and positioning: `references/wudi-persona.md`
- Topic diagnosis and angle generation: `references/topic-angle.md`
- Three-layer hooks: `references/hook-engine.md`
- Six-part script: `references/six-part-framework.md`
- Douyin adaptation: `references/douyin-rules.md`
- WeChat Video adaptation: `references/wechat-video-rules.md`
- Structural scoring: `references/viral-review.md`
- Truth and risk gate: `references/truth-check.md`
- Machine output contract: `schemas/wudi-viral-script-output.schema.json`
- Human rendering: `templates/script-output.md`, `templates/scoring-card.md`, `templates/shooting-card.md`

## Required workflow

1. Parse input and default `platform` to `both` unless the user specifies one.
2. Load persona + truth rules before adding specific facts.
3. Diagnose the topic and reduce noisy input to **one core conflict** and one viewpoint.
4. Generate 3–5 distinct viable angles; discard weak/redundant ones.
5. Generate a batch of at least six three-layer hooks (`spoken`, `visual`, `screen_text`).
6. Recommend one direction based on real support and fit; never claim certainty or guaranteed virality.
7. Build the six-part script. When a real story is unsupported, keep `real_story` honest and add a concrete request to `missing_material` rather than inventing one.
8. Apply `douyin`, `wechat_video`, or both adapters. Under `both`, the two versions must differ in opening, pacing, information order, and depth.
9. Add a lightweight, one-person-friendly shooting plan plus titles, cover text, publish caption, and comment prompt.
10. Run `references/truth-check.md` on the complete draft.
11. **先真实性检查，再评分** with `references/viral-review.md`; `viral_score.total` must be the arithmetic sum of seven dimensions and `deductions` must be concrete.
12. Return schema-conforming structured output; render with templates when the user wants a human-readable view.

**不得编造** customers, prices, sales, incidents, competitor behavior, quotations, statistics, or 吴迪 experiences. Never expose confidential seed-production processes or customer private information.

## Platform rules

- `platform=douyin`: produce `douyin_version`; `wechat_video_version` may be empty.
- `platform=wechat_video`: produce `wechat_video_version`; `douyin_version` may be empty.
- `platform=both`: produce both independently; the WeChat Video version is not a word-for-word copy of the Douyin version.

## Output modes

For workbench/API use, return valid **JSON** conforming to `schemas/wudi-viral-script-output.schema.json`, with no prose outside the object. For direct human reading/editing, render the same contract with `templates/script-output.md`.

## Selective regeneration

Support module-level edits without destroying human work: `只重写Hook`, `只重写某一段`, `重新生成角度`, `优化口语`, `更像吴迪`, `转视频号`, `转抖音`.

For every selective action, **preserve untouched human-edited fields** exactly. Only the requested module and fields that logically depend on it may change. Human edits always beat regenerated defaults.

## Boundaries

- V1 ends at a human-usable draft and shooting plan. Do not publish, schedule, auto-edit, create a digital human, run paid traffic, or reply to comments automatically.
- Never claim a high score means a video will go viral. “Strong candidate” describes structure only.
- Never let urgency, platform pressure, or a desired score override the truth gate.
- Do not turn this into an enterprise account script. The content must preserve 吴迪's human point of view.
