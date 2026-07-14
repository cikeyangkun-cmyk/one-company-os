---
name: one-company-os-hotspot-writing
description: Use when evaluating, assigning, or drafting a Chinese social-hotspot article for the One Company OS Toutiao five-account matrix.
---

# One Company OS Hotspot Writing

Treat the deterministic pipeline result as the authority for whether writing may begin. The five accounts may share verified intelligence and structured data, but never finished copy.

## Required sequence

1. Build one structured hotspot JSON record with at least one HTTP(S) source.
2. Separate confirmed facts from unconfirmed claims. Never invent missing facts, promote an inference to fact, or treat a traffic-source article as proof.
3. Run `one-company-os evaluate --input <path-to-json>`.
4. Stop when the result is `duplicate` or `discard`; do not assign an account or draft.
5. For `risk_pause`, stop all account assignment and writing. Require Human review before continuing; do not supply a headline, angle, outline, or draft while paused.
6. For `candidate`, retain the record but do not treat it as a same-day priority or begin writing.
7. For `immediate`, use the returned `account_id` and follow that account's reader question in `references/account-matrix.md`.
8. Before handing off a draft, apply every gate in `references/quality-gates.md`.

## Mandatory safeguards

- Content involving a minor and any legal or financial conclusion require Human review before account assignment or writing. Set the matching risk signal and require a `risk_pause`; if the output differs, stop and correct the record before re-evaluating.
- One event routes to one account. A second account is allowed only after a human approves and records a distinct event-angle identity; different wording, framing, or added context is insufficient.
- Urgency, deadlines, traffic pressure, and competitor activity never override the pipeline output or Human review.
- Scores of 75 or more are `immediate`, scores from 60 through 74 are `candidate`, and scores below 60 are `discard`; any high risk pauses regardless of score.

## Boundaries

- Never log in to Toutiao, publish automatically, or invoke an external publishing connector. V1 ends at a human-reviewed draft handoff.
- Never convert inference into confirmed fact or fabricate a fact, source, attribution, quote, or certainty.
- Never send one finished article to multiple accounts or lightly rewrite it for another account.
- Never bypass a risk pause because the score is high or time is short.

## References

- Account duties: `references/account-matrix.md`
- Fact, originality, and human approval gates: `references/quality-gates.md`
