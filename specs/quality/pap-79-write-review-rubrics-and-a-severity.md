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
blocks: ["PAP-81", "PAP-239", "PAP-243"]
key: "quality/review-rubrics"
url: "https://linear.app/paperos/issue/PAP-79/write-review-rubrics-and-a-severity-taxonomy-shared-by-all-reviewer"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:15.177Z"
---

# PAP-79: Write review rubrics and a severity taxonomy shared by all reviewer agents and humans

**Goal**

Write the shared vocabulary for judging work: a severity taxonomy, per-domain review checklists with IDs, and a structured finding format used by the three reviewer agents, the vision inspector, the edge-case hunter, the a11y audit and Justin, so a "blocker" means the same thing everywhere and findings can be counted, trended and turned into gate decisions automatically.

**Scope**

* In: `docs/quality/rubrics/` with `severity.md`, `correctness.md`, `security.md`, `spec-conformance.md`, `visual.md`, `accessibility.md`, `performance.md`, `docs-and-changelog.md`, `agent-behaviour.md`, `README.md`; the `Finding` schema (authored here, homed in `packages/contracts` by PAP-239); the calibration set of 15 cases; the Markdown rendering template; `pnpm rubrics:calibrate`.
* Out: the agents (PAP-81), posting tooling, performance thresholds (PAP-87), the other artifact schemas (PAP-239).

**Spec**

* Severity: `S0 blocker` (data loss, security, broken build, access-rule violation), `S1 major` (user-visible bug, missing declared state, serious a11y), `S2 minor`, `S3 nit`, plus kinds `question` and `praise`. Gate rule: any S0 blocks; more than 3 S1 blocks; S2 and S3 never block. Confidence under 0.5 posts as `question`.
* Checklist items `RUB-<DOMAIN>-<nn>` with a one-line test ("Can I construct an input that…"), typical severity, how to verify, false-positive notes; each rubric file has purpose, scope, examples of S0/S1/S2 and "what this does not cover".
* Domains: correctness (types vs runtime, null and empty, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, cleanup, meaningful tests); security (authz per procedure, RLS context, validation, secrets, SSRF, injection, uploads, rate limits, dependency risk, sensitive logging; cites PAP-219 `SEC-*` controls); spec-conformance (spec exists, components match `registry.json`, access implemented, all declared states rendered, events wired, spec edge cases tested, `rules.json` respected); visual (overflow, clipping, truncation without tooltip, 4 px misalignment, contrast, spacing, target size, theme leaks); accessibility, performance, docs, agent behaviour.
* `Finding = { id, reviewer, rubricId, severity, title, body, file?, line?, endLine?, suggestion?, evidence: { kind: 'code' | 'screenshot' | 'video' | 'log', ref }[], confidence, autofixable, waiver? }`; `id = sha1(reviewer + rubricId + file + normalizedTitle)[:10]`.
* Rendering template: header with counts by severity, findings grouped by severity with file link, rubric ID and suggestion diff block.

**Interface contract**

* Provides: rubric IDs (`RUB-*`) and severity names used by PAP-80 mapping, PAP-73 gate, PAP-84 vision, PAP-85 oracles, PAP-244 and PAP-245 prompts; `Finding` schema source (`docs/quality/rubrics/finding.schema.json` plus the TypeScript moved into `packages/contracts/src/finding.ts` when PAP-239 lands); calibration set format `calibration/<case>/{input.md, expected.json}`; the review comment template; waiver shape `{ reason, approvedBy, expires }`.
* Requires: nothing. Soft: PAP-219 control ids for the security rubric.
* Consumers: PAP-81 children, PAP-84, PAP-85, PAP-89, PAP-73, PAP-76, PAP-49, PAP-110, PAP-239, PAP-241.

**Definition of done**

* Nine rubric docs plus README merged; every checklist item has an ID and verification note.
* `Finding` schema with Vitest tests and exported JSON Schema; PAP-239 comment confirms it as the canonical home.
* Calibration set of 15 cases with expected severities and rationales; `pnpm rubrics:calibrate <output.json>` prints agreement.
* Rendering template snapshot test; reviewed in comments by Iris (visual and a11y), Forge (correctness), Ledger (financial correctness note).
* Changelog entry; Linear comment linking README and schema.

**Test plan**

* Unit: schema accepts the 15 expected files and rejects a wrong severity, a confidence over 1 and a missing evidence kind; `findingId` stable under whitespace and case changes.
* Script: `rubrics:calibrate` on a fixture output reports the expected agreement number.
* Docs: every `RUB-*` referenced by the calibration cases exists; link check.

**Demo**

Open `docs/quality/rubrics/README.md`, follow the gate rule to `severity.md`, then run `pnpm rubrics:calibrate fixtures/sample-review.json` and read the agreement score and the two disagreements it lists. Under one minute.

**Edge cases**

* Finding in generated files: capped at S2, points at the generator.
* Two reviewers on the same line: both kept, highest governs; dedupe only within a reviewer.
* Not-applicable rubric: reviewers emit `n/a` so silence differs from skipped.
* Justin overrides severity: recorded as a waiver, never a silent edit.
* Third-party code: S3 with a pointer to PAP-216.

**Dependencies**

None blocking. Soft: PAP-219.

**Agent**

Sentinel writes; Quill edits. Reviewed by Atlas, Iris, Forge, Ledger.

**Size**

M.
