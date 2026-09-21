# Wudi Viral Script V1 Design

## Goal

Build a dedicated short-video copywriting Agent Skill for the “吴迪吹牛” personal IP. The skill turns one agriculture/business-owner topic into a shoot-ready Douyin-first script, with a distinct WeChat Video adaptation, concrete hook options, shooting notes, a deterministic scoring rubric, and explicit missing-material flags instead of fabricated stories.

## Scope

V1 covers: topic diagnosis → multi-angle generation → three-layer hooks → 吴迪 six-part script → Douyin adaptation → WeChat Video adaptation → shooting package → viral-structure review.

V1 does not cover publishing, editing, digital humans, AI voice, paid traffic, analytics dashboards, or automatic comment replies.

## Audience and positioning

Primary persona: 吴迪, an agriculture/seed-industry business owner with more than ten years of field and business experience.

Primary content themes:
- agriculture business-owner viewpoints
- broccoli seed industry
- entrepreneurship and customer experience
- market observations and industry misconceptions
- domestic seed development and industry information gaps
- owner daily life when it supports the persona

The skill must build the person before the knowledge: facts → 吴迪 stance → real experience → industry insight.

## Core principles

1. Write spoken Chinese, not article prose.
2. One video carries one core conflict, one viewpoint, and one memorable idea.
3. Real experience outranks elegant copy.
4. Never fabricate customers, prices, sales, incidents, competitor behavior, quotes, statistics, or 吴迪 experiences.
5. If a real-story slot is unsupported, emit an explicit missing-material marker instead of inventing it.
6. Strong hooks may create tension but must match the actual payoff.
7. Never claim a script will definitely go viral.

## Workflow

### 1. Topic diagnosis

For each topic determine:
- core conflict
- target audience
- why the audience would stop
- why 吴迪 has authority to speak
- weaknesses or factual risks

### 2. Angle generation

Generate genuinely different angles, preferring these five families:
- industry-insider
- owner-viewpoint
- real-experience
- customer-pain
- contrarian/conflict

Weak or redundant angles may be discarded. At least three distinct viable angles must remain when the topic supports them.

### 3. Hook engine

For each final candidate direction, generate at least six hooks across multiple archetypes. Each hook has three layers:
- spoken line
- first-frame visual
- on-screen text

Preferred archetypes: conflict, contrarian, money, experience, authority, insider, question, concrete-scene, comparison, stance.

### 4. 吴迪 six-part framework

1. Conflict hook (0–3s)
2. 吴迪 stance (3–8s)
3. Real experience (8–25s)
4. Industry information gap (25–40s)
5. 吴迪 viewpoint (40–50s)
6. Open-ended ending (50–60s)

The real-experience section must either use supplied/verified material or contain an explicit missing-material marker.

### 5. Platform adapters

Douyin:
- first sentence enters conflict immediately
- preferred duration 35–60s; 60–90s only when needed
- one problem per video
- second stimulus around 15–25s
- comments over generic follow prompts

WeChat Video:
- slower pacing is acceptable
- more emphasis on experience, credibility, causal explanation, and values
- preferred duration 60–120s
- must not be a word-for-word duplicate of the Douyin script

### 6. Viral-structure scoring

Total 100 points:
- Hook: 20
- tension/conflict: 15
- 吴迪 persona: 15
- authenticity: 15
- industry insight: 15
- spoken-language naturalness: 10
- comment potential: 10

Thresholds:
- 0–64: reject
- 65–74: rewrite core angle
- 75–84: candidate
- 85–89: priority candidate
- 90+: strong candidate, never “guaranteed viral”

Every score must include concrete deduction reasons.

## Language style

吴迪 voice should be plain, direct, decisive, experienced, unpretentious, and owner-like. Short breath-length sentences are preferred.

Avoid report language such as “随着…发展”, “在当前市场环境下”, or “对于广大种植户而言”. Avoid forced internet slang, motivational-guru tone, professor-style lectures, and empty corporate publicity.

## Truth and safety checks

Before final output:
- remove fabricated 吴迪 stories
- flag unsupported concrete data
- discuss industry phenomena instead of attacking named peers without evidence
- avoid agricultural fearmongering
- remove heavy product-advertising language unless the user explicitly requests an ad

## Input contract

Required:
- `topic`

Optional:
- `platform`: `douyin | wechat_video | both`
- `source_material`
- `target_duration`
- `goal`: reach, comments, persona, industry influence, customer trust, etc.

## Output contract

The machine-readable form must expose:
- `topic_analysis`
- `angles`
- `hooks`
- `recommended_direction`
- `script` with the six parts
- `douyin_version`
- `wechat_video_version`
- `shooting`
- `package`
- `viral_score`
- `missing_material`

A JSON Schema must define this contract so the later workbench can consume it without prompt-specific parsing.

## File layout

```text
.agents/skills/wudi-viral-script/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── wudi-persona.md
│   ├── topic-angle.md
│   ├── hook-engine.md
│   ├── six-part-framework.md
│   ├── douyin-rules.md
│   ├── wechat-video-rules.md
│   ├── viral-review.md
│   └── truth-check.md
├── schemas/
│   └── wudi-viral-script-output.schema.json
└── templates/
    ├── script-output.md
    ├── scoring-card.md
    └── shooting-card.md
```

## Acceptance criteria

Test at least ten representative 吴迪 topics. V1 passes when:
1. all ten produce shootable spoken drafts;
2. obvious article/AI prose is absent;
3. missing real experience is never fabricated;
4. each viable topic exposes at least three distinct angles;
5. hooks include spoken, visual, and on-screen-text layers;
6. Douyin and WeChat Video versions are meaningfully different;
7. scoring gives concrete deduction reasons;
8. individual modules can be regenerated independently;
9. output maps cleanly to the JSON Schema;
10. the voice remains recognizably 吴迪 rather than generic agriculture-expert copy.

## Delivery boundary

Phase 1 delivers and tests the standalone Agent Skill in `one-company-os`.
Phase 2, planned separately after Phase 1 acceptance, integrates the schema into the 吴迪 workbench topic-card UI and selective regeneration controls.
