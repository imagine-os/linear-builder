---
identifier: "PAP-89"
title: "Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent", "Staff"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-88", "PAP-239", "PAP-254", "PAP-356"]
blocks: []
key: "quality/review-report"
url: "https://linear.app/paperos/issue/PAP-89/generate-a-one-page-human-review-digest-per-release-candidate-what"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:05.970Z"
---

# PAP-89: Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions

**Goal**

Generate the one page Justin actually reads per release candidate: what changed in plain language, what the gates found and how it was resolved, the risks and questions needing his decision, and the screenshots and replays that let him see the product in under ten minutes. Everything else stays in the machines.

**Scope**

* In: `packages/agents/src/digest/buildDigest({ from, to, rcBranch })` collecting PRs and Linear issues, changelog, every gate artifact, waivers, open S1s, cost from PAP-98, nightly trends and calibration health; a constrained Claude summarisation step; Markdown, HTML (Pages) and Linear-body outputs; screenshot selection; citation validation.
* Out: marketing notes (PAP-192), tenant-facing changelog rendering (PAP-133), PR-level digests, the trigger (PAP-254).

**Spec**

* Inputs are all `packages/contracts` artifacts (PAP-239): `gate1.json`, `security.json`, `visual.json`, `videos.json`, `vision.json`, `edgecases.json`, `perf.json`, `certification.json`, `calibration.json`, `flakes-delta.json`, plus forge and Linear GraphQL for PRs and characters, PAP-133 changelog or `git log` fallback.
* Digest schema `digest.schema.ts`: `{ version, range: { fromSha, toSha, fromDate, toDate }, decision: { ask, approveCommand, rejectCommand, deadline }, changes: [{ project, title, prs: [{ number, url, linearKey, character }], userFacing, summary, screenshots }], quality: { gates: [{ name, status, link }], findings: { S0, S1, S2, S3, fixed, waived }, calibration, perf }, risks: [{ id, title, detail, recommendation, requiresAnswer }], replays, cost, links }`.
* Sections: 1 Decision needed (one paragraph and the two PAP-94 commands); 2 What changed (by project, user-facing first, before/after where visual diffs exist); 3 Quality evidence (gate table, findings by severity, fixed vs waived, calibration and perf health); 4 Risks and open questions (each with a recommended default and checkbox); 5 Replays (posters at 375 and 1280); 6 Cost and velocity; 7 Appendix links.
* Summarisation prompt `.claude/agents/digest-writer.md` receives only schema-shaped data and returns prose fields; every claim cites a PR or finding ID; a validator drops uncited sentences and logs them; prose under 900 words.
* Renderers: Markdown `docs/releases/<version>.md`; HTML via PAP-235's `PdfLayout`/`EmailLayout` kit when available, else a static template on PAP-66 tokens, no client JS beyond video posters, under 5 MB, published at `/releases/<version>/`; Linear body truncated to 4 000 characters with a link.
* Screenshots: pages with diffs in range at 375 and 1280, max 12; expired replay URLs re-signed.

**Interface contract**

* Provides: `buildDigest()`, `DigestSchema`, `pnpm digest --from --to --out`, `docs/releases/<version>.md`, `/releases/<version>/` page, Linear body variant consumed by PAP-254, `calibrationHealth` and `perfHealth` rendering expectations for PAP-241 and PAP-242.
* Requires: PAP-88 children (hard: trigger and inputs), PAP-239 schemas (hard), PAP-82, PAP-83, PAP-84, PAP-85, PAP-87, PAP-242, PAP-241, PAP-133, PAP-98, PAP-94, PAP-15 hosting, PAP-235 kit (all soft with fallbacks).
* Consumers: PAP-254 RC issue, PAP-94 queue, PAP-108 handoffs, PAP-192 (reads the changelog, not the digest), Justin.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. The digest is a pure reader of `GateReport` artifacts and emits `release.candidate` (§3) through PAP-97; the Linear body variant must render through the §2 "Notification" contract once PAP-136 work package 1 exists.

**Definition of done**

* Digest for a rehearsal range with all seven sections populated from real artifacts; HTML on Pages and Markdown committed (links).
* Citation validator drops a seeded unsupported claim (test).
* Justin reads the rehearsal digest and confirms in a comment it answers what changed, is it safe, what must he decide; one adjustment round.
* Screenshots of the HTML digest at 375, 1280 and 1920 light and dark.
* Vitest for schema, renderer snapshots and length checks; `docs/quality/review-report.md`; changelog entry.

**Test plan**

* Unit: collector per artifact kind on fixtures including a missing artifact (`unknown` with re-run link); grouping of 40+ PRs; screenshot selection cap; Linear truncation.
* Prompt: validator on fixture prose with one uncited sentence; word cap.
* Integration: `pnpm digest` on the sandbox repo history; HTML size and two-screen height check at 1280.
* Visual: HTML digest at three widths × two themes.

**Demo**

Run `pnpm digest --from v0.1.0 --to release/2026-39 --out tmp/` and open the HTML: read the decision paragraph, scan the gate table, click a replay poster. Under two minutes.

**Edge cases**

* Zero user-facing changes: section 2 says so and leads with infrastructure.
* Missing artifact: `unknown`, never omitted.
* Cost unavailable: `n/a` with reason, never invented.

**Dependencies**

PAP-88 (hard), PAP-239 (hard). Soft: PAP-82, PAP-83, PAP-84, PAP-85, PAP-87, PAP-241, PAP-242, PAP-133, PAP-98, PAP-94, PAP-15, PAP-235.

**Agent**

Sentinel builds; Quill (Changelog Scribe) owns prose rules and templates. Reviewed by Atlas and, for the rehearsal, Justin.

**Size**

M.
