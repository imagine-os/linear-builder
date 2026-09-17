# PaperOS build in $2,500 chunks (discounted terms)

Snapshot: `plan/linear-snapshot-live.json`, takenAt 2026-09-17T13:11:39Z. Generated 2026-09-17T14:30:44Z by `round3/chunks.py` (planning session); raw data in `round3/chunks.json`, per-issue models for mix B in `round3/model-effort-B.json`. Companion to `docs/cost-and-duration-estimate.md`, whose token model, prices and scheduler this document reuses unchanged.

## 1. Terms

* **Discount.** Justin pays **$50 for every $2,500 of list-price Claude spend** (x0.02). Every figure below is given at list price and at the discounted price. A chunk = $2,500 list = $50 to Justin; a started chunk is billed whole, so the "whole chunks billed" line is what the invoice would read.
* **Sessions run 24/7** with **16 concurrent builder sessions**; reviewer and QA sessions run on top of that cap. The clock starts at **2026-09-17T14:23Z**.
* **Scope.** The 326 buildable, non-deferred issues (PAP-13..PAP-432 minus the 52 umbrellas, the 42 deferred leaves and the Duplicate strays). The 42 deferred leaves are priced as an optional final chunk in section 5.
* **Ordering.** List scheduling over the live `blockedBy` graph (umbrella edges mapped onto their children, 1,148 edges, no cycles), ready-first by longest remaining dependency tail. Per-issue wall-clock S 30 / M 75 / L 180 min, plus 20 min review and 15 min QA (code issues). Identical for both mixes; only the price differs.
* **Cutting.** Issues are streamed in finish-time order and their fully loaded cost is accumulated; when the next issue would push the running total past $2,500 a new chunk starts. The four release-candidate reviews are inserted into the stream at the moment their gate set (execution schedule section 3) lands.
* **Cost per issue** (from `cost-and-duration-estimate.md` section 3): builder tokens by Size (S 1.5M in / 60K out, M 4M / 150K, L 10M / 400K; 80% cache reads, 20% cache writes), k = 0.60 for Spec/Research/Docs/Review; per-issue **Effort kept as labeled** (output tokens x0.6 low, x1.0 medium, x1.4 high; all Spec issues are high); reviewer session = 40% of builder tokens on **Fable 5.1 / high** in both mixes; QA gate = 25% on the mix's QA model / low (code issues); x1.25 contingency. Each RC review = one L-size Fable 5.1 / high session = $68.75 list.
* **Prices** ($/MTok, read from the `claude-api` skill on 2026-09-17): Fable 5.1 $10 in / $50 out / $0.25 cache read / $12.50 cache write; Opus 5 $5 / $25 / $0.50 / $6.25.

## 2. The two mixes

| | Mix A | Mix B |
|---|---|---|
| Builders | Fable 5.1 on all 326 | Opus 5 on Build / Infra / Docs / Review issues (275); Fable 5.1 on Spec / Research issues (51) |
| Reviewer sessions | Fable 5.1 / high | Fable 5.1 / high |
| QA gate | Fable 5.1 / low | Opus 5 / low |
| 4 release-candidate reviews | Fable 5.1 / high | Fable 5.1 / high |
| Effort | as labeled | as labeled |
| **Chunks ($2,500 list each)** | 5 | 4 |
| List cost, 326 issues + 4 RC reviews | $11,166 | $7,909 |
| **Discounted cost to Justin** | **$223.32** | **$158.17** |
| Whole chunks billed | 5 x $50 = $250 | 4 x $50 = $200 |
| Wall-clock at 16 builders, 24/7 | 37.3 h (1.56 days), ends 2026-09-19T03:43Z | same |
| By phase (list) P0 / P1 / P2 | $3,112 / $5,354 / $2,425 | $2,284 / $3,707 / $1,642 |
| + 42 deferred (optional chunk, section 5) | +$1,387 list = +$27.75, +5.5 h | +$983 list = +$19.66, +5.5 h |
| Everything (326 + 42) | $12,553 list = **$251.07**, 42.8 h | $8,891 list = **$177.83**, 42.8 h |

Mix A costs $3,257 more at list, which is **$65.15 more to Justin**; it buys Fable 5.1 on every builder and QA session. Both mixes run the same 37-hour schedule because durations are per Size, not per model. Recommendation: **mix B**. Fable already sits where judgement compounds (every spec, every review, every RC), and the $65.15 saved is one more chunk of headroom for retries. If Justin prefers Fable everywhere, mix A is 5 chunks instead of 4.

Reading the clock: the 37 hours are session time with dependencies respected and nothing else in the way. The chunks overlap at their edges (16 builders are mid-issue when a chunk's dollar boundary passes; `firstIssueStart` in the JSON shows how far back each chunk's earliest issue started). Not in the clock: `Needs Justin` answers, merge-queue conflicts on shared files, the 30% re-review bounce (its tokens are in the x1.25 contingency, its minutes are not). The Execution Schedule's 15-day plan was governed by those gates and by daily PR-landing limits, and still is; 24/7 sessions remove the half-day cadence, not the human decisions. Section 3 lists, per chunk, which decisions must be answered before it starts (section 4 gives the mapping for mix A). The `Needs Justin` queue holds five open items at a time (PAP-94), so chunk 1's items have to be batched into two or three cards.

## 3. Mix B: Opus 5 builders and QA; Fable 5.1 for Spec/Research issues, all reviewer sessions and the 4 RC reviews

| Chunk | Issues | List | To Justin | Hours | Start | End | Builders (Fable / Opus) | Release candidates | Milestones done |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 114 | $2,496 | $49.91 | 12.1 | 2026-09-17T14:23Z | 2026-09-18T02:28Z | 38 / 76 | - | 3 |
| 2 | 92 | $2,486 | $49.72 | 9.8 | 2026-09-18T02:28Z | 2026-09-18T12:13Z | 5 / 87 | RC0, RC1 | 5 |
| 3 | 97 | $2,498 | $49.96 | 10.6 | 2026-09-18T12:13Z | 2026-09-18T22:48Z | 5 / 92 | RC2 | 27 |
| 4 | 23 | $429 | $8.58 | 4.9 | 2026-09-18T22:48Z | 2026-09-19T03:43Z | 3 / 20 | RC3 | 15 |
| **Total** | **326** | **$7,909** | **$158.17** | **37.3** | 2026-09-17T14:23Z | 2026-09-19T03:43Z | | RC0-RC3 | 50 |

### Chunk 1: $2,496 list, $49.91 to Justin, 12.1 h (2026-09-17T14:23Z to 2026-09-18T02:28Z)

114 issues: P0 82 / P1 31 / P2 1; Build 54, Docs 2, Infra 20, Research 16, Spec 22; sizes S 27 / M 87 / L 0. Earliest issue in the chunk started 2026-09-17T14:23Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-1 (resolved): Linear: upgrade the workspace plan (PAP-91). Resolved: workspace is on Linear Basic. Gates: 91.
* NJ-2: Infra batch (PAP-25): Hetzner account and cpx41, registrar or Cloudflare token (or accept sslip.io), Resend sign-up, sops recovery key. Gates: 25.
* NJ-3: GitHub App on org imagine-os with repo+workflow scope (PAP-47). Gates: 47.
* NJ-5: Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97). Gates: 92, 97.
* NJ-6: Code signing (PAP-256): Apple Developer Program + Azure Trusted Signing, or accept unsigned v0.1.0 installers (default after 48 h: unsigned). Gates: 256.
* NJ-7: License of the template code (PAP-211): MIT, Apache-2.0 or proprietary; default Apache-2.0. Gates: 211.
* NJ-8: Approve docs/pm/justin-queue.md (PAP-94) and the issue contract (PAP-93). Gates: 94, 93.
* NJ-9: Hire the roster (PAP-104, PAP-210): nine leads, 28 sub-characters, tool scope classes. Gates: 284, 285, 286, 287, 210.
* NJ-10: Stripe test-mode account and restricted key (PAP-177); Google Cloud OAuth consent screen (PAP-224, PAP-200). Gates: 177, 224, 200.
* NJ-12: Payroll provider (PAP-176): sign the Check sandbox agreement (default) or Gusto Embedded. Gates: 176.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Umbrellas completed |
|---|---|---|
| Agent Characters & Orgs (`agents`) | 103, 105, 106, 284, 285, 286, 287, 298, 308 | **104** Write the nine lead characters and their sub-characters as . |
| Universal App Shell & Repo Template (`app-shell`) | 13, 14, 15, 16, 17, 22, 25, 26, 27, 255, 256, 257, 258, 261, 262, 264, 305 | **19** Add Tauri 2 desktop target for Linux, macOS and Windows shar |
| Business Core: Payments, Finance & Payroll (`business-core`) | 175, 176, 392 | - |
| In-App Collaboration & Knowledge (`collab`) | 127, 128, 133 | - |
| Data Layer & Database (`data-layer`) | 30, 31, 32, 33, 34, 37, 38, 42, 43, 267, 268, 269, 279, 302, 303, 304 | **35** Expose a typed API via oRPC with Zod schemas generated from  |
| Design System (`design-system`) | 66, 68, 69, 70, 71, 74, 233, 234, 236, 237, 238 | **67** Adopt Base UI/Radix primitives with Tailwind v4 and build 20 |
| Version Control & Forge Independence (`forge`) | 46, 47, 48, 50, 52, 273, 274, 275, 358 | **45** Deploy Forgejo on the VPS behind Caddy with SSO from Better  |
| Identity, Roles & Audiences (`identity`) | 55, 56, 219, 223, 224, 225, 226, 227, 228, 229, 301 | **57** Install Better Auth with passkeys, magic link, Google/GitHub, **59** Build permission engine combining role-based grants with att |
| Multi-Input Control & Accessibility (`input`) | 150, 152, 289, 290 | - |
| Library Discovery & Integration (`libraries`) | 209, 210, 211, 212, 292, 293, 294, 295, 296, 297, 350 | **213** Survey table, canvas, editor and chart libraries (TanStack, , **214** Survey backend building blocks (Better Auth, Drizzle, Electr |
| Migration & Import Tools (`migration`) | 198 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 91, 92, 94, 100 | - |
| Quality Pipeline (`quality`) | 78, 79, 80, 239 | - |
| Multiplayer & Realtime (`realtime`) | 139 | - |
| Spec Builder (`spec-builder`) | 114, 115, 117, 118, 121, 123, 360 | - |
| Table & Views Engine (`tables`) | 161, 162, 338 | - |

**Deliverable at the end of the chunk**

* Milestones completed (non-deferred scope): Library Discovery & Integration / Evaluation process (4 issues, 2026-09-17T22:23Z); Design System / Tokens and primitives (8 issues, 2026-09-18T01:28Z); Data Layer & Database / Postgres + Drizzle baseline (13 issues, 2026-09-18T01:48Z).

### Chunk 2: $2,486 list, $49.72 to Justin, 9.8 h (2026-09-18T02:28Z to 2026-09-18T12:13Z)

92 issues: P0 18 / P1 60 / P2 14; Build 77, Docs 1, Infra 7, Research 1, Review 2, Spec 4; sizes S 12 / M 79 / L 1. Earliest issue in the chunk started 2026-09-18T00:23Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-4: Anthropic Console: orchestrator API key, hard spend limit, usage export (PAP-98). Gates: 98.
* NJ-11: Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0 (RC1). Gates: RC1.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Umbrellas completed |
|---|---|---|
| Agent Characters & Orgs (`agents`) | 288, 299, 309 | - |
| Universal App Shell & Repo Template (`app-shell`) | 259, 260, 263, 265, 266, 363, 364, 365, 429 | **20** Add Tauri 2 mobile targets (iOS, Android) with platform capa, **21** Build responsive breakpoint matrix and multi-monitor window , **28** Make every platform capability a removable module: module ma |
| Business Core: Payments, Finance & Payroll (`business-core`) | 177, 178, 359, 393, 394, 395, 396, 397, 398, 399 | **179** Build a double-entry ledger (accounts, journal entries, peri, **180** Implement invoices, quotes and receipts with PDF generation  |
| In-App Collaboration & Knowledge (`collab`) | 129, 317, 318, 319, 320, 321, 322 | **131** Implement in-app comments anchored to any entity, page eleme, **132** Build the canvas view (tldraw or React Flow) showing the UX  |
| Data Layer & Database (`data-layer`) | 39, 270, 271, 272, 354 | **36** Integrate PGlite and ElectricSQL shapes for local-first read |
| Design System (`design-system`) | 73 | - |
| Growth: Marketing, Outreach & CRM (`growth`) | 187 | - |
| Identity, Roles & Audiences (`identity`) | 58, 60 | - |
| Multi-Input Control & Accessibility (`input`) | 291, 329, 330, 331 | **151** Build the global command registry with keyboard shortcuts, c, **155** Build accessible drag-and-drop (dnd-kit) for tables, kanban  |
| Library Discovery & Integration (`libraries`) | 351 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 93, 97, 98, 99, 281, 282, 283, 300, 372 | **96** Build the orchestrator that polls Ready for Claude, spawns o |
| Quality Pipeline (`quality`) | 86, 87, 240, 242, 243, 246, 247, 248, 356, 357 | **82** Build gate 3: Playwright screenshot suite across the 7-width |
| Multiplayer & Realtime (`realtime`) | 140, 141, 142, 326, 327, 328 | **143** Stream record changes via Electric shapes to all connected c |
| Spec Builder (`spec-builder`) | 116, 122, 311, 312, 313, 314, 315, 316, 361, 362, 376 | **119** Specify the data section (entities, queries, mutations, sync, **120** Generate page scaffolds (layout, component tree, loading/emp |
| Table & Views Engine (`tables`) | 167, 170, 335, 336, 337, 339, 340, 341, 342, 344, 345, 382, 383 | **163** Build the view query compiler from view model to SQL and Ele, **164** Implement field types: text, number, currency, date, select, |

**Deliverable at the end of the chunk**

* **RC0** review runs at 2026-09-18T06:13Z: RC0 staging + sign-in + orchestrator claiming.
* **RC1** review runs at 2026-09-18T06:03Z: RC1 v0.1.0-rc.1: RLS permissions, installers, Yjs server, codegen, Stripe test mode, story baselines.
* Milestones completed (non-deferred scope): Identity, Roles & Audiences / Auth works across web and desktop (12 issues, 2026-09-18T02:53Z); Multi-Input Control & Accessibility / Keyboard and command system (5 issues, 2026-09-18T03:03Z); Spec Builder / Spec schema and validator (5 issues, 2026-09-18T04:38Z); Spec Builder / Codegen and conformance tests (12 issues, 2026-09-18T08:18Z); Multiplayer & Realtime / Yjs server and presence (4 issues, 2026-09-18T12:13Z).

### Chunk 3: $2,498 list, $49.96 to Justin, 10.6 h (2026-09-18T12:13Z to 2026-09-18T22:48Z)

97 issues: P0 5 / P1 55 / P2 37; Build 77, Docs 4, Infra 5, Research 1, Review 6, Spec 4; sizes S 8 / M 89 / L 0. Earliest issue in the chunk started 2026-09-18T10:58Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-13: Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136). Gates: 414, 415, 416, 323, 324, 325.
* NJ-15: Release candidate v0.1.0-rc.2 from PAP-254: /approve or /reject (RC2). Gates: RC2.
* NJ-16: Approve the content agent (PAP-192) and migration agent (PAP-208). Gates: 192, 208.
* NJ-18: Industry list and terminology defaults (PAP-126). Gates: 126.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Umbrellas completed |
|---|---|---|
| Agent Characters & Orgs (`agents`) | 107, 108, 109, 111, 112, 113, 280, 310 | **110** Create an eval harness with golden tasks per character, scor |
| Universal App Shell & Repo Template (`app-shell`) | 18, 24, 29, 366, 367, 368, 369, 430, 431 | - |
| Business Core: Payments, Finance & Payroll (`business-core`) | 181, 183, 186, 391, 400 | **184** Define the payroll provider interface and implement the firs |
| In-App Collaboration & Knowledge (`collab`) | 134, 135, 138, 323, 324, 379 | - |
| Data Layer & Database (`data-layer`) | 40, 353, 355, 370, 432 | - |
| Design System (`design-system`) | 72, 75, 76 | - |
| Version Control & Forge Independence (`forge`) | 51, 53, 371 | - |
| Growth: Marketing, Outreach & CRM (`growth`) | 188, 189, 192 | - |
| Identity, Roles & Audiences (`identity`) | 61, 62, 63, 64, 220 | - |
| Multi-Input Control & Accessibility (`input`) | 153, 154, 156, 159 | - |
| Library Discovery & Integration (`libraries`) | 216, 217 | - |
| Migration & Import Tools (`migration`) | 201, 347, 348, 349 | **199** Build the import framework: source connector, schema-mapping |
| Project Management & Claude Pipeline (`pm-linear`) | 102, 306, 307, 373 | - |
| Quality Pipeline (`quality`) | 83, 84, 89, 90, 244, 245, 249, 250, 252, 253, 254 | **81** Build gate 2: three Claude reviewer agents (correctness, sec, **88** Define the release train: nightly staging deploy, weekly rel |
| Multiplayer & Realtime (`realtime`) | 144, 145, 147, 148, 381 | - |
| Spec Builder (`spec-builder`) | 125, 126, 375, 377, 378 | **124** Build the spec editor UI with form and YAML views and live p |
| Table & Views Engine (`tables`) | 166, 169, 172, 332, 333, 334, 343, 346, 384, 385, 386, 387, 388, 389, 390 | **165** Build the virtualized grid view (TanStack Table) with inline, **168** Build calendar, timeline and Gantt views with dependencies, **171** Build a formula engine compatible with common Airtable and N, **173** Compose views into dashboard pages with drag-arranged blocks, **174** Build table automations: triggers (record change, schedule,  |

**Deliverable at the end of the chunk**

* **RC2** review runs at 2026-09-18T21:43Z: RC2 v0.1.0-rc.2, first real cut: gates 1-4, grid + compiler, comments, record sync, ledger + invoices, imports, drill.
* Milestones completed (non-deferred scope): Quality Pipeline / Gates 1 and 2 on every PR (11 issues, 2026-09-18T13:33Z); Agent Characters & Orgs / Agent org visible in app (1 issue, 2026-09-18T14:43Z); Multiplayer & Realtime / Record sync and conflict UX (5 issues, 2026-09-18T14:48Z); Multi-Input Control & Accessibility / Touch, pen, gamepad (6 issues, 2026-09-18T15:13Z); Table & Views Engine / Grid with sort, filter, group (12 issues, 2026-09-18T15:43Z); Business Core: Payments, Finance & Payroll / Ledger and reports (8 issues, 1 deferred excluded, 2026-09-18T16:38Z); Growth: Marketing, Outreach & CRM / Campaigns and social (1 issue, 7 deferred excluded, 2026-09-18T16:38Z); Library Discovery & Integration / Registry live (2 issues, 1 deferred excluded, 2026-09-18T16:58Z); Identity, Roles & Audiences / Roles and audiences enforced end to end (4 issues, 2026-09-18T17:03Z); Agent Characters & Orgs / Roster defined and installed (11 issues, 2026-09-18T17:08Z); Table & Views Engine / All view types (9 issues, 2026-09-18T18:23Z); Universal App Shell & Repo Template / Desktop and mobile shells build (14 issues, 2026-09-18T18:58Z); Data Layer & Database / Local-first sync working (8 issues, 2026-09-18T19:38Z); Version Control & Forge Independence / CI runs on both forges (5 issues, 2026-09-18T19:53Z); Quality Pipeline / Edge-case hunting and release trains (8 issues, 2026-09-18T20:23Z); Business Core: Payments, Finance & Payroll / Stripe billing live (6 issues, 2026-09-18T20:38Z); Table & Views Engine / View sharing, formulas, dashboards (10 issues, 2026-09-18T21:13Z); Universal App Shell & Repo Template / Multi-monitor and PWA polish (13 issues, 1 deferred excluded, 2026-09-18T21:43Z); Version Control & Forge Independence / Disaster recovery proven (1 issue, 3 deferred excluded, 2026-09-18T21:43Z); Identity, Roles & Audiences / Agent principals and enterprise (2 issues, 5 deferred excluded, 2026-09-18T21:48Z); Agent Characters & Orgs / Sub-agents, skills and evals live (8 issues, 2026-09-18T21:53Z); Spec Builder / Spec editor UI (6 issues, 2026-09-18T22:13Z); Business Core: Payments, Finance & Payroll / Payroll adapter and cash dashboard (4 issues, 1 deferred excluded, 2026-09-18T22:13Z); Growth: Marketing, Outreach & CRM / CRM core (3 issues, 2026-09-18T22:18Z); Project Management & Claude Pipeline / Orchestrator claims and ships issues (9 issues, 2026-09-18T22:23Z); Universal App Shell & Repo Template / Template scaffolds and runs on web (8 issues, 2026-09-18T22:48Z); Design System / Component library covers app shell needs (5 issues, 2026-09-18T22:48Z).

### Chunk 4: $429 list, $8.58 to Justin, 4.9 h (2026-09-18T22:48Z to 2026-09-19T03:43Z)

23 issues: P0 4 / P1 4 / P2 15; Build 15, Docs 4, Research 2, Review 1, Spec 1; sizes S 14 / M 9 / L 0. Earliest issue in the chunk started 2026-09-18T21:13Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-17: Accessibility statement wording (PAP-160). Gates: 160.
* NJ-19: Scope freeze: deferred list becomes milestone v0.2. Gates: RC3.
* NJ-20: Release candidate v0.1.0: /approve promotes and tags (RC3, PAP-254). Gates: RC3.
* NJ-21: PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29). Gates: RC3.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Umbrellas completed |
|---|---|---|
| In-App Collaboration & Knowledge (`collab`) | 130, 325, 380 | **136** Build a notification center (in-app, email, Slack) with per- |
| Data Layer & Database (`data-layer`) | 41 | - |
| Design System (`design-system`) | 77 | - |
| Version Control & Forge Independence (`forge`) | 44, 49 | - |
| Multi-Input Control & Accessibility (`input`) | 160 | - |
| Library Discovery & Integration (`libraries`) | 352 | **215** Evaluate whole OSS products to embed or fork (Twenty CRM, No |
| Migration & Import Tools (`migration`) | 200, 208, 413, 414, 415, 416, 420, 421, 422 | **202** Import Airtable bases (tables, views, relations, attachments, **205** Export everything (tables, docs, files, ledger) to open form |
| Project Management & Claude Pipeline (`pm-linear`) | 95, 374 | **101** Build bidirectional Linear sync (GraphQL + webhooks) with co |
| Quality Pipeline (`quality`) | 241, 251 | **85** Build gate 4: edge-case hunter agent generating adversarial  |
| Multiplayer & Realtime (`realtime`) | 146 | - |

**Deliverable at the end of the chunk**

* **RC3** review runs at 2026-09-19T03:43Z: RC3 = v0.1.0: every non-deferred issue Done.
* Milestones completed (non-deferred scope): In-App Collaboration & Knowledge / Docs and prompt log stores (5 issues, 2026-09-18T22:53Z); Multiplayer & Realtime / Scale and offline tested (4 issues, 1 deferred excluded, 2026-09-18T22:53Z); In-App Collaboration & Knowledge / Comments and canvas (11 issues, 2026-09-18T22:58Z); Data Layer & Database / Tenant-safe and observable (6 issues, 2026-09-18T23:03Z); Project Management & Claude Pipeline / PM module syncs both ways (5 issues, 2026-09-18T23:03Z); Migration & Import Tools / Import framework and CSV (6 issues, 2026-09-18T23:03Z); Library Discovery & Integration / Core adoptions decided (9 issues, 2026-09-18T23:03Z); Version Control & Forge Independence / Forgejo live and mirrored (8 issues, 2026-09-18T23:13Z); In-App Collaboration & Knowledge / Knowledge surfaced everywhere (3 issues, 1 deferred excluded, 2026-09-18T23:18Z); Migration & Import Tools / Business migrations (1 issue, 6 deferred excluded, 2026-09-18T23:18Z); Design System / Themable per tenant with docs (3 issues, 1 deferred excluded, 2026-09-18T23:38Z); Project Management & Claude Pipeline / Linear configured for the pipeline (5 issues, 2026-09-18T23:38Z); Quality Pipeline / Visual and video gates (8 issues, 2026-09-18T23:43Z); Multi-Input Control & Accessibility / Voice and accessibility certification (2 issues, 2 deferred excluded, 2026-09-18T23:43Z); Migration & Import Tools / Airtable, Notion, ClickUp importers (7 issues, 4 deferred excluded, 2026-09-19T03:43Z).

## 4. Mix A: all Fable 5.1 (builders, reviewers, QA, RC reviews)

| Chunk | Issues | List | To Justin | Hours | Start | End | Builders (Fable / Opus) | Release candidates | Milestones done |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 90 | $2,499 | $49.98 | 9.5 | 2026-09-17T14:23Z | 2026-09-17T23:53Z | 90 / 0 | - | 1 |
| 2 | 66 | $2,500 | $50.00 | 6.7 | 2026-09-17T23:53Z | 2026-09-18T06:33Z | 66 / 0 | RC0, RC1 | 5 |
| 3 | 65 | $2,495 | $49.90 | 7.3 | 2026-09-18T06:33Z | 2026-09-18T13:53Z | 65 / 0 | - | 3 |
| 4 | 61 | $2,466 | $49.32 | 6.8 | 2026-09-18T13:53Z | 2026-09-18T20:38Z | 61 / 0 | - | 15 |
| 5 | 44 | $1,206 | $24.11 | 7.1 | 2026-09-18T20:38Z | 2026-09-19T03:43Z | 44 / 0 | RC2, RC3 | 26 |
| **Total** | **326** | **$11,166** | **$223.32** | **37.3** | 2026-09-17T14:23Z | 2026-09-19T03:43Z | | RC0-RC3 | 50 |

Same schedule and the same issue order as mix B; only the dollar boundaries move, so the chunk contents differ. Chunk contents, milestones and Needs Justin items per chunk are in `round3/chunks.json` under `mixes.A.chunks`. The Needs Justin items map to mix A chunks as follows: chunk 1: NJ-1, NJ-2, NJ-3, NJ-5, NJ-6, NJ-7, NJ-8, NJ-9, NJ-12; chunk 2: NJ-10, NJ-11; chunk 3: NJ-4, NJ-13; chunk 4: NJ-16; chunk 5: NJ-15, NJ-17, NJ-18, NJ-19, NJ-20, NJ-21.

## 5. Optional final chunk: the 42 deferred issues

Claimable only after NJ-14 (stop-loss go) and rescoped to v0.2 at NJ-19; each carries the `Deferred` label and `Effort: low` from the deferral rule, kept as labeled here. Scheduled with the same 16 builders after RC3: **5.5 h** (2026-09-19T03:43Z to 2026-09-19T09:13Z) in both mixes.

| Mix | List | To Justin | Equivalent chunks | Builders |
|---|---|---|---|---|
| A | $1,387 | $27.75 | 0.55 | fable-5-1 42 |
| B | $983 | $19.66 | 0.39 | opus-5 42 |

Issues by project: `app-shell` 23; `business-core` 182, 185; `collab` 137; `design-system` 235; `forge` 276, 277, 278; `growth` 193, 194, 195, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412; `identity` 221, 222, 230, 231, 232; `input` 157, 158; `libraries` 218; `migration` 204, 417, 418, 419, 423, 424, 425, 426, 427, 428; `realtime` 149.

Milestones that hold only deferred work (close with this chunk): Growth: Marketing, Outreach & CRM / Acquisition analytics (8).

Needs Justin before it starts: NJ-14: Stop-loss checkpoint: go or no-go on the stretch pool (deferred set).

## 6. Reconciliation with the September estimate

`cost-and-duration-estimate.md` priced mix A at $9,910 without effort scaling and without the RC reviews; with Effort as labeled (all specs high, most builds high) and 4 RC reviews it is $11,166. Its mix B was a 90/10 Opus/Fable token split ($6,035); the mix B here is defined by role (Opus builders and QA, Fable on specs, research, every reviewer and the RCs) and comes to $7,909. Scenario E ($3,490) is still the cheapest plan; under the discount it would be $69.80, so the whole spread between E and mix A is $153.52 of Justin's money, which is why this document stops optimising for tokens and spends them where the plan is most fragile.

## 7. How to use this

1. Answer the chunk-1 Needs Justin items (NJ-2, 3, 5, 6, 7, 8, 9, 10, 12; NJ-1 is done) before the first session starts; batch them into cards of five.
2. Run chunk 1 at 16 builders. Ledger reports list spend per chunk in the daily burn report (PAP-98) so the x0.02 invoice can be checked against the console.
3. Re-baseline after chunk 1: real per-size token burn replaces the S / M / L assumptions and this document is regenerated from `chunks.py`.
4. Each chunk boundary is a natural stop: nothing in a later chunk is needed to keep an earlier chunk's deliverable working, so Justin can pause after any $50.
