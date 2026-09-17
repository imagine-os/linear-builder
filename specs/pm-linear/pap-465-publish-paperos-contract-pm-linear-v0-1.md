---
identifier: "PAP-465"
title: "Publish @paperos/contract-pm-linear v0.1 with manifest"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-93", "PAP-433"]
blocks: ["PAP-100", "PAP-102", "PAP-307", "PAP-372", "PAP-468", "PAP-471"]
key: "module/pm-linear/contract"
url: "https://linear.app/paperos/issue/PAP-465/publish-paperoscontract-pm-linear-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:11:29.499Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-465: Publish @paperos/contract-pm-linear v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-pm-linear` v0.1 and the `pm-linear` module manifest so every other module codes against a versioned package instead of `paperos-orchestrator repo, packages/pm` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `high`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/pm-linear/` published as `@paperos/contract-pm-linear` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-pm-linear', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Atlas', project: 'pm-linear' }`, `swapRisk: 'high'`, `kind: 'service and runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/pm-linear.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-93 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `IssueContract` (PAP-93): required sections, labels, states enum `Backlog|Todo|Ready for Claude|In Progress|In Review|Needs Justin|Done|Canceled|Duplicate`, validator result codes
* `PmEntities`: project, issue, cycle, milestone, comment, label, relation (PAP-100) as Zod with `EntityRef` keys
* `PmSourcePort`: `list`, `get`, `claim` (atomic), `transition`, `comment`, `relate`, `webhook(envelope)`; the Linear adapter today, a native PM adapter later (PAP-281, PAP-372)
* `QueuePort`: promotion checks (PAP-96 rule), concurrency hints (PAP-99), `NeedsJustinCard` shape (PAP-94)
* Slot fills: `shell.nav:pm`, `record.panel.tabs:issue`

Events declared with `defineTopic()` (payload schemas, version 1): `issue.needs_justin`, `issue.claimed|released`, `review.ready`, `pm.sync.conflict`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1

* `@paperos/contract-tables` ^0.1 (board and list views; PAP-102)
* `@paperos/contract-collab` ^0.1 (comment anchors on issues)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-pm-linear@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.pm-linear`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-93 (Define the issue contract (spec link, acceptance criteria, s). Consumed by: PAP-100 (PM entities), PAP-102 (board views), PAP-372 (Linear sync backfill), PAP-204 (Linear and ClickUp import), PAP-307 (inbound triage), PAP-97 (webhooks), and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (twelve issues covering every state, three claim races (two sessions, one wins), four webhook payloads from Linear, one Needs Justin card, one relation graph with a cycle); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/pm-linear.md` generated; short ADR `docs/adr/00xx-contract-pm-linear.md` recording what was pinned.
* Comments on PAP-100, PAP-102, PAP-372, PAP-307 that their Interface contract sections now import from `@paperos/contract-pm-linear`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-93. Blocks PAP-100, PAP-102, PAP-372, PAP-307, `module/pm-linear/conformance` and `module/pm-linear/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Atlas (Project Management & Claude Pipeline owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show pm-linear`, then feeds the twelve issue fixtures to the `IssueContract` validator and sees the expected codes (`UMBRELLA_NOT_CLAIMABLE`, `BLOCKED_BY_OPEN`, ok). Under a minute.
