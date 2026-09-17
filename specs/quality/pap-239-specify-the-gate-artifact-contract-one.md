---
identifier: "PAP-239"
title: "Specify the gate artifact contract: one schema package for gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs and artifact paths"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-79"]
blocks: ["PAP-80", "PAP-81", "PAP-82", "PAP-83", "PAP-84", "PAP-85", "PAP-89", "PAP-243", "PAP-248", "PAP-249", "PAP-429"]
key: "quality/gate-artifact-contract"
url: "https://linear.app/paperos/issue/PAP-239/specify-the-gate-artifact-contract-one-schema-package-for-gate1json"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:43:12.833Z"
---

# PAP-239: Specify the gate artifact contract: one schema package for gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs and artifact paths

**Goal**

Create `packages/contracts`, the one place every gate artifact shape lives, so CI jobs, the orchestrator webhooks, the release digest and the QA viewer read the same JSON. Today PAP-78, 80, 82, 83, 84, 85, 89 and 137 each define their own shape; this issue centralises them before any gate is built.

**Scope**

* In: `packages/contracts` with Zod schemas and exported JSON Schema for `gate1.json`, `security.json`, `visual.json`, `videos.json`, `vision.json`, `edgecases.json`, `perf.json`, `review-cost.json`, `flakes-delta.json`, plus the shared `Finding` (moved from PAP-79's draft location), `GateStatus`, `ArtifactRef`, `Evidence`; artifact path conventions; finding ID function; status name registry; a `validateArtifact(kind, json)` CLI used by every gate job; versioning rules.
* Out: producing the artifacts (each gate), rendering (PAP-89, PAP-137).

**Spec**

* Package layout: `src/finding.ts`, `src/gates/<kind>.ts`, `src/artifacts.ts`, `src/status.ts`, `src/index.ts`; `pnpm contracts:build` writes `schemas/*.schema.json`; drift-checked in Gate 1.
* `Finding = { id, reviewer, rubricId, severity: 'S0'|'S1'|'S2'|'S3'|'question'|'praise', title, body, file?, line?, endLine?, suggestion?, evidence: Evidence[], confidence, autofixable, waiver? }`; `findingId(reviewer, rubricId, file, title) = sha1(...)[:10]`.
* `GateReport<K> = { kind: K, version: 1, sha, pr?, startedAt, finishedAt, status: 'pass'|'fail'|'error'|'skipped', findings: Finding[], summary: string, artifacts: ArtifactRef[], data: KindSpecific }` where `KindSpecific` is per kind (for example `visual: { images: [{ id, project, theme, status, diffRatio, paths }] }`).
* `ArtifactRef = { kind: 'screenshot'|'video'|'report'|'log'|'sarif', path, url?, sha256?, expiresAt? }`; paths relative to `reports/` in the run; URL form `https://<pages>/pr/<n>/<kind>/...`.
* Status registry: `gate/1-static`, `gate/1-security`, `gate/1-perf`, `gate/2-correctness`, `gate/2-security`, `gate/2-spec`, `gate/2-review`, `gate/3-visual`, `gate/3-video`, `gate/3-vision`, `gate/3-e2e`, `gate/4-edge`; exported as a const so typos fail typecheck.
* Versioning: `version` field; breaking changes bump and keep a reader for the previous version for 30 days.

**Interface contract**

* Provides: all types above, `validateArtifact()`, `findingId()`, `GATE_STATUSES`, `artifactUrl(pr, path)`; JSON Schemas for non-TypeScript consumers (orchestrator in PAP-96 and webhooks in PAP-97).
* Requires: PAP-79 severity taxonomy and rubric IDs (the finding schema moves here; PAP-79 documents it).
* Consumers: PAP-78, 80, 81, 82, 83, 84, 85, 87, 88, 89, 90, 97, 137, PAP-110.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` row: owned by quality, contents "gate artifacts"; every other project adds shapes only through this package's registration); §1 (Zod 4 is the schema language, JSON Schema generated, never hand-written; agent authors on findings are the §1 `ActorRef`); §3 (the 30-day reader rule for `version` bumps is shared with the event envelope); §6 row "Gate artifacts" (consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). This issue is the provider.

**Definition of done**

* Package builds; JSON Schemas generated and committed; drift check wired into Gate 1 (or `pnpm check` until PAP-78 merges).
* Fixture artifacts for every kind validate; a fixture with a wrong severity fails with a path.
* `findingId` stability test across whitespace and case changes in the title.
* PAP-78, 80, 81, 82, 84, 85, 89 each carry a comment confirming they import from `packages/contracts` (left by this issue's session).
* `docs/quality/gates.md` section "Artifacts and statuses"; changelog under "Quality".

**Test plan**

* Unit: every schema against fixtures (valid and invalid), `artifactUrl` for GitHub Pages and Forgejo hosting, status registry completeness against the docs table.
* Integration: `validateArtifact` CLI exit codes in a shell test.

**Demo**

Run `pnpm contracts:validate fixtures/visual.pass.json` (exit 0) then `fixtures/visual.bad-severity.json` (exit 1 with the path), and open `schemas/finding.schema.json`. Under one minute.

**Edge cases**

* Gate produces no findings but errored: `status: 'error'` with `summary`, never an empty pass.
* Two gates report the same finding ID: allowed; consumers dedupe by `(reviewer, id)`.
* Artifact over the Pages size limit: `url` omitted, `path` remains with a run-artifact reference.
* Forgejo-hosted PR: `artifactUrl` falls back to the run artifact link.

**Dependencies**

PAP-79 (hard). Consumers listed above, except PAP-97, which is soft: PAP-97 ships its own `orchestrator-event.json` schema and adopts `packages/contracts` when it lands. The `blocks` relation to PAP-97 was removed on 2026-09-17 (round-2 FIX-1) because this milestone (09-25) is later than PAP-97's (09-22).

**Agent**

Written by Sentinel with Atlas (contract owner). Reviewed by Forge (CI consumers) and Quill (digest consumer).

**Size**

S: a schema package; agreement is the work.
