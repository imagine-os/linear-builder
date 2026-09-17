---
identifier: "PAP-79"
title: "Write review rubrics and a severity taxonomy shared by all reviewer agents and humans"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Gates 1 and 2 on every PR"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-239", "PAP-243", "PAP-81"]
key: "quality/review-rubrics"
url: "https://linear.app/paperos/issue/PAP-79/write-review-rubrics-and-a-severity-taxonomy-shared-by-all-reviewer"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-79: Write review rubrics and a severity taxonomy shared by all reviewer agents and humans

**Goal**

Write the shared vocabulary for judging work: a severity taxonomy, per-domain review checklists and a structured finding format that the three reviewer agents, the vision inspector, the edge-case hunter and Justin all use, so a "blocker" means the same thing everywhere and findings can be counted, trended and turned into gate decisions automatically.

**Scope**

In:
- `docs/quality/rubrics/` with `severity.md`, `correctness.md`, `security.md`, `spec-conformance.md`, `visual.md`, `accessibility.md`, `performance.md`, `docs-and-changelog.md`, `agent-behaviour.md` (did the session follow the playbook), and `README.md` explaining how rubrics feed gates.
- Severity taxonomy: `S0 blocker` (data loss, security, broken build, spec violation of access rules), `S1 major` (user-visible bug, missing state, a11y serious), `S2 minor` (polish, naming, moderate a11y), `S3 nit` (style), plus `praise` and `question` non-severity kinds. Gate rule: any S0 blocks; more than 3 S1 blocks; S2/S3 never block.
- Finding schema `packages/agents/src/review/finding.schema.ts` (Zod) and JSON Schema export: `{ id, reviewer, rubricId, severity, title, body, file?, line?, endLine?, suggestion?, evidence: { kind: 'code'|'screenshot'|'video'|'log', ref }[], confidence: 0-1, autofixable }`.
- Checklists as numbered items with IDs `RUB-<domain>-<nn>`, each with a one-line test ("Can I construct an input that...").
- Calibration set: 15 historical or synthetic PR excerpts with expected severities, in `docs/quality/rubrics/calibration/`, used to test reviewer agents.
- Human-facing summary format for PR comments and the release digest.

Out: implementing the agents (`quality/review-agents`), tooling to post reviews, performance thresholds themselves (`quality/perf-budgets`).

**Spec**

- Each rubric file: purpose, scope, checklist table (ID, check, typical severity, how to verify, false-positive notes), examples of S0/S1/S2 findings, and "what this rubric does not cover".
- Correctness checklist covers: types vs runtime, null and empty handling, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, resource cleanup, tests present and meaningful.
- Security checklist covers: authz on every procedure, RLS context set, input validation, secrets, SSRF, injection (SQL, HTML, shell), file upload, rate limits, dependency risk, logging of sensitive data.
- Spec-conformance checklist covers: page has a spec, components match `registry.json`, access section implemented, all declared states rendered (loading, empty, error, offline, no-permission), events wired, edge cases from spec have tests, guidelines `rules.json` respected.
- Visual checklist (for `quality/screenshot-annotation`): overflow, clipping, truncation without tooltip, misalignment to 4px grid, contrast, inconsistent spacing, touch target size, theme leaks.
- Finding IDs deterministic: `sha1(reviewer + rubricId + file + normalizedTitle)[:10]` so re-reviews dedupe.
- Confidence guidance: below 0.5 the finding is posted as `question`, not as a severity.
- Markdown rendering template for a review comment: header with counts by severity, then findings grouped by severity, each with file link, rubric ID and suggestion in a diff block.

**Definition of done**

- Nine rubric docs plus README merged; every checklist item has an ID and verification note.
- `finding.schema.ts` with Vitest tests and exported JSON Schema at `docs/quality/rubrics/finding.schema.json`.
- Calibration set of 15 cases with expected severities and rationales; a script `pnpm rubrics:calibrate` prints agreement for a given reviewer output file.
- Rendering template tested with a fixture producing the expected Markdown snapshot.
- Reviewed and approved in comments by Iris (visual and a11y rubrics), Forge (correctness), Ledger (a note on financial correctness checks).
- CHANGELOG entry; Linear comment linking the README and schema.

**Edge cases**

- Finding spans generated files: severity capped at S2 and points to the generator source.
- Conflicting findings from two reviewers on the same line: both kept, highest severity governs the gate, dedupe only within a reviewer.
- Rubric item not applicable (e.g. no UI change): reviewers must emit `n/a` per rubric so silence is distinguishable from a skipped check.
- Severity inflation by agents: calibration agreement below 0.8 flags the reviewer prompt for tuning in `agents/eval-harness`.
- Justin overrides a severity: recorded as a `waiver` with reason and expiry on the finding, never a silent edit.
- Findings in third-party code under `node_modules` or vendored: `S3` with a pointer to `libraries/registry`.

**Dependencies**

None blocking. Consumed by `quality/review-agents`, `quality/screenshot-annotation`, `quality/edge-case-hunter`, `quality/review-report`, `design-system/a11y-audit`, `design-system/guidelines-docs`, `forge/pr-templates`, `agents/eval-harness`.

**Agent**

Written by Sentinel with Quill editing for clarity. Reviewed by Atlas, Iris and Forge (domain sign-offs above).

**Size**

M: mostly writing, but the schema and calibration set are what make the agents measurable.
