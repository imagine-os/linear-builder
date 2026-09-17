---
identifier: "PAP-485"
title: "Publish @paperos/contract-growth v0.1 with manifest"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "CRM core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-187", "PAP-188", "PAP-433"]
blocks: ["PAP-192", "PAP-193", "PAP-194", "PAP-195", "PAP-488", "PAP-491"]
key: "module/growth/contract"
url: "https://linear.app/paperos/issue/PAP-485/publish-paperoscontract-growth-v01-with-manifest"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T15:00:38.913Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-485: Publish @paperos/contract-growth v0.1 with manifest

**Model / Effort:** Sonnet 5 / high

**Goal**

Publish `@paperos/contract-growth` v0.1 and the `growth` module manifest so every other module codes against a versioned package instead of `packages/crm` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `medium`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/growth/` published as `@paperos/contract-growth` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-growth', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Beacon', project: 'growth' }`, `swapRisk: 'medium'`, `kind: 'runtime'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/growth.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-187, PAP-188 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* CRM entities lead, contact, company, deal, pipeline stage, activity, segment as Zod with dataset registrations (PAP-187)
* `SocialAdapterPort` (`publish`, `dryRun`, `capabilities`; PAP-402, PAP-403) and `OutreachProviderPort` (email and SMS send, reply detection, suppression; PAP-404, PAP-405)
* `LandingPagePublisherPort` (Webflow adapter; PAP-193) and `FormCapturePort`
* `AttributionEvent` schema and `SegmentPort` (`evaluate`, `members`, `subscribe`; PAP-194, PAP-195)
* `SupportChannelPort` (inbound email, chat; PAP-410 to PAP-412) and `ContentDraftPort` for the content agent (PAP-192); slot fills `shell.nav:crm`, `record.panel.tabs:activity`

Events declared with `defineTopic()` (payload schemas, version 1): `lead.created|converted`, `segment.entered|exited`, `campaign.sent|failed`, `support.conversation.opened`.

Requires (manifest `requires[]`): \* `@paperos/contract-tables` ^0.1

* `@paperos/contract-data-layer` ^0.1
* `@paperos/contract-business-core` ^0.1 (referral payouts; optional)
* `@paperos/contract-collab` ^0.1 (support inbox comments)
* `@paperos/contract-agents` ^0.1 (content agent; optional)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-growth@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.growth`. Consumes: the manifest schema and validator (`module-system/manifest-schema`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-187 (Model CRM entities: lead, contact, company, deal, pipeline s), PAP-188 (Survey open-source CRM and marketing stacks (Twenty, Postiz,). Consumed by: PAP-192 (content agent), PAP-193 (landing pages), PAP-194 (attribution), PAP-195 (segments), PAP-408 referral rewards, PAP-136 in-app targeting, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (eight CRM records with relations, four social posts with per-platform variants, three outreach sequences (including STOP handling), six attribution events, two segments with expected membership); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Nova confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/growth.md` generated; short ADR `docs/adr/00xx-contract-growth.md` recording what was pinned.
* Comments on PAP-192, PAP-193, PAP-194, PAP-195 that their Interface contract sections now import from `@paperos/contract-growth`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `module-system/manifest-schema` and PAP-187, PAP-188. Blocks PAP-192, PAP-193, PAP-194, PAP-195, `module/growth/conformance` and `module/growth/wire`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Beacon (Growth: Marketing, Outreach & CRM owner). Reviewed by Nova and Atlas (contract ownership).

**Size**

S

**Demo**

Reviewer runs `pnpm contract:show growth` and evaluates the two segment fixtures with the reference evaluator, getting the expected member sets. Under a minute.
