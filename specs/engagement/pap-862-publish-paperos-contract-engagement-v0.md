---
identifier: "PAP-862"
title: "Publish @paperos/contract-engagement v0.1 with manifest"
project: "engagement"
projectName: "Scheduling, Messaging & Customer Engagement"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Engagement contract and booking core"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-264", "PAP-279", "PAP-302", "PAP-303", "PAP-305", "PAP-433", "PAP-556", "PAP-863"]
blocks: ["PAP-864", "PAP-865", "PAP-867", "PAP-868", "PAP-875", "PAP-876"]
key: "r4/engagement/contract-publish"
url: "https://linear.app/paperos/issue/PAP-862/publish-paperoscontract-engagement-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:16.200Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-862: Publish @paperos/contract-engagement v0.1 with manifest

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Publish `@paperos/contract-engagement` v0.1 and the `engagement` module manifest so every other module codes against a versioned package instead of `packages/engagement, apps/web/src/engagement` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays in the project's Build issues. Swap risk is declared `medium` and kind `runtime`, which decides how much of the swap playbook a rewrite must follow. This is a new module: the contract is written before the implementation, so the Build issues in this project consume it from day one rather than being retrofitted.

**Scope**

In: `packages/contracts/engagement/` published as `@paperos/contract-engagement` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`. `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-engagement', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Beacon', project: 'engagement' }`, `swapRisk: 'medium'`, `kind: 'runtime'`, plus the generated `module.manifest.json`. `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/engagement.md` (a `typedoc` stub until the docs generator PAP-445 lands). A `## Module boundary` paragraph on this project's model or umbrella issue naming the contract version each Build issue implements.

Out: Runtime behaviour, React, Drizzle tables, network calls. The conformance suite and the kernel binding (own issues). Changing contract-zero types; anything missing there is filed against PAP-302, PAP-279 or PAP-303.

**Spec**

* Ports and schemas exported at v0.1: `SchedulingPort` (`availability`, `hold`, `book`, `reschedule`, `cancel`, `waitlist`) with `Resource`, `Service`, `AvailabilityRule`, `Hold`, `Booking`; `CalendarSyncPort` (`connect`, `pull`, `push`, `feed`) with `CalendarConnection`; `MessagingChannelPort` (`send`, `receiveWebhook`, `status`, `capabilities`) with `ChannelKind`, `ChannelAccount`, `MessageRef`; `HelpCenterPort` (`publish`, `search`, `feedback`) and `SurveyPort` (`define`, `trigger`, `responses`, `score`); `ReviewsPort` (`request`, `record`) and `FeedbackPort` (`post`, `vote`, `link`); `MembershipPort` (`plans`, `enrol`, `checkIn`, `status`) and `LoyaltyPort` (`earn`, `redeem`, `balance`, `issueGiftCard`, `redeemGiftCard`); `AnnouncementPort` (`publish`, `forPrincipal`, `dismiss`); slots `portal.home.cards`, `portal.nav.items`, `record.panel.tabs.bookings`, `dashboard.blocks.engagement`, `shell.banner`
* Events declared with `defineTopic()` (payload schemas, version 1): `booking.created`, `booking.rescheduled`, `booking.cancelled`, `booking.no_show`, `booking.completed`, `calendar.synced`, `message.received`, `message.sent`, `message.failed`, `survey.responded`, `review.received`, `membership.enrolled`, `membership.lapsed`, `membership.checked_in`, `loyalty.earned`, `loyalty.redeemed`, `giftcard.issued`, `giftcard.redeemed`, `announcement.viewed`, `feedback.posted`
* Requires (manifest `requires[]`): `@paperos/contract-data-layer` ^0.1 (jobs, email, files, search, idempotency, recurrence); `@paperos/contract-tables` ^0.1 (calendar view time model, datasets, views); `@paperos/contract-identity` ^0.1 (`Principal`, audiences, OAuth plumbing); `@paperos/contract-collab` ^0.1 (notification kinds, tenant docs, changelog); `@paperos/contract-growth` ^0.1 (support conversations, outreach provider, consent, segments, CRM contacts); `@paperos/contract-business-core` ^0.1 (Connect, Checkout, posting rules, documents); `@paperos/contract-workflows` ^0.1 (forms runtime, approvals; optional); `@paperos/contract-app-shell` ^0.1 (kiosk mode, domains, flags, native scanner)
* Rules: Zod 4 only, JSON Schema generated and committed; no `z.bigint()` on wire schemas (PAP-302 `Money` codec); one sentence of doc and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`, never hand-written
* Every port method that mutates money, sends a message or signs a document carries `Idempotency-Key` semantics from PAP-304 in its signature (`{ idempotencyKey }` option) so adapters cannot forget it
* Error codes reuse the contracts document catalogue (`NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `MODULE_DISABLED`, `RATE_LIMITED`); module-specific codes are listed in `errors.ts` with user-facing copy keys (PAP-368)

**Interface contract**

Provides: `@paperos/contract-engagement@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.engagement`. Consumes: the manifest schema and validator (PAP-433), contract-zero (`@paperos/core/types|filter|events`, PAP-302, PAP-279, PAP-303), the base manifest shape (PAP-264) and the ownership map (PAP-305). Consumed by: commerce (shift availability, POS loyalty and gift cards, member pricing), assistant (Front Desk booking and help-center answers), workflows (booking and survey triggers), growth (reviews and NPS into segments), platform-ops (engagement metrics), migration (salon, clinic, gym packs), and this module's conformance and wire issues.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; `pnpm modules:validate` and `pnpm gen:dep-map` green with the new module present
* Generated JSON Schema, `typedoc` stub and ownership entry committed; `compat-matrix.json` (PAP-440) shows every `requires` resolving
* Sentinel confirms no implementation leaked into the package (no React, no Drizzle, no fetch)
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (three scheduling scenarios (salon chair, clinic room plus doctor, gym class) with 25 availability days including DST, six bookings across the status machine, two calendar connections with delta fixtures, four channel accounts and eight inbound messages, two surveys with responses, one membership plan with webhook fixtures, a loyalty program with twenty entries and two gift cards, three announcements with targeting); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel reads the package top to bottom against `docs/module-system.md` section 2 and the contracts document; every port method has a fixture.

**Demo**

`pnpm modules:validate` prints the `engagement` manifest with its provides and requires, `pnpm gen:dep-map` shows the new node with only declared edges, and `docs/platform/contracts/engagement.md` renders the port list.

**Edge cases**

* A port needed by a Build issue but missing at v0.1 is added as a minor bump (`0.2.0`) with a fixture, never as a direct import of the implementation
* A type that two contracts both want (for example a scheduling `TimeRange`) goes to contract-zero via PAP-302, not into this package, to avoid a dependency between contracts

**Dependencies**

PAP-433 manifest schema (hard), contract-zero PAP-302, PAP-279, PAP-303 (hard), PAP-264 and PAP-305 (soft, shape only). Unblocks every other issue in this project.

**Agent**

Builder: Beacon. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
