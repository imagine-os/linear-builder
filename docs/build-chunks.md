# PaperOS build in $2,500 chunks (discounted terms)

Round 4 (2026-09-18). Live graph: `plan/round4/sched/graph.json`, takenAt 2026-09-18T14:12:52Z (901 PAP issues after excluding PAP-1..PAP-12 and the 82 Triage ideas; 105 umbrellas, 796 leaves of which 195 carry `Deferred`). Generated 2026-09-18T14:22:23Z by `plan/round4/sched/model.py`; raw data in `plan/round4/chunks-v2.json` (same shape as the round-3 `plan/chunks.json`, plus `round: 4`), per-issue schedule and cost in `plan/round4/sched/sched-A.json` / `sched-B.json`. Companion to `docs/cost-and-duration-estimate.md` (token model and prices, unchanged; round-4 results in its section 9) and `docs/execution-schedule.md` (block-by-block table and credit burn). The Chunk labels in Linear follow **mix B** of this document (`Chunk 1`..`Chunk 5` on the 601 scheduled leaves, `Chunk: v0.2` on the 195 deferred leaves, none on umbrellas; log `plan/round4/changes/chunks-relabel.json`).

## 1. Terms

* **Discount.** Justin pays **$50 for every $2,500 of list-price Claude spend** (x0.02). Every figure is given at list price and at the discounted price. A chunk = $2,500 list = $50 to Justin; a started chunk is billed whole, so the "whole chunks billed" line is what the invoice would read.
* **Sessions run 24/7** with **16 concurrent builder sessions**; reviewer and QA sessions run on top of that cap. The clock starts at **2026-09-18T14:15Z** (the graph pull, rounded to the quarter hour).
* **Scope.** The **601 buildable, non-deferred leaves** (every PAP issue except PAP-1..PAP-12, the 82 Triage ideas, the 105 umbrellas and the 195 deferred leaves). Umbrellas are never claimed; they complete when their last child lands. The deferred leaves are priced as the final `v0.2` chunk in section 5.
* **Sizes** come from the Linear estimate (Fibonacci, set in round 4): 2 = S (half a session-day), 3 = M (one), 5 = L (two). Scheduled set: S 198 / M 401 / L 2; 1609 points.
* **Ordering.** List scheduling over the live `blocks` graph (3,041 relations; umbrella edges mapped onto their children give 3,551 effective leaf edges; no cycles), ready-first by longest remaining build tail, then phase, priority, size. **Branch-start rule**: a dependent starts as soon as every blocker's PR is open, i.e. when the blocker's build minutes end; the blocker's review and QA run in parallel. Per-issue wall-clock S 30 / M 75 / L 180 min of build, plus 20 min review and 15 min QA (code issues). Identical for both mixes; only the price differs.
* **Cutting.** Issues are streamed in landing order (build + review + QA) and their fully loaded cost is accumulated; when the next issue would push the running total past $2,500 a new chunk starts. The four release-candidate reviews are inserted into the stream when their gate set (execution schedule section 3) lands.
* **Cost per issue** (`cost-and-duration-estimate.md` section 3): builder tokens by Size (S 1.5M in / 60K out, M 4M / 150K, L 10M / 400K; 80% cache reads, 20% cache writes), k = 0.60 for Spec/Research/Docs/Review; **Effort from the `Reasoning effort` label** scales output tokens (low x0.6, medium x1.0, high x1.4, max x2.0); reviewer session = 40% of builder tokens; QA gate = 25% (code issues); x1.25 contingency. Each RC review = one L-size Fable 5.1 / high session = $68.75 list.
* **Prices** ($/MTok, `claude-api` skill, 2026-09-17): Fable 5.1 $10 in / $50 out / $0.25 cache read / $12.50 cache write; Opus 5 $5 / $25 / $0.50 / $6.25; Sonnet 5 $2 / $10 / $0.20 / $2.50; Haiku 4.5 $1 / $5 / $0.10 / $1.25.

## 2. The mixes

| | Mix A | **Mix B (canonical)** | Mix B, round-3 definition (reference) |
|---|---|---|---|
| Builders | Fable 5.1 on all 601 | the issue's `Model` label (Sonnet 374, Opus 139, Fable 80, Haiku 8); Fable 5.1 on every Spec / Research issue | Opus 5 on every Build / Infra / Docs / Review issue (522); Fable 5.1 on Spec / Research (79) |
| Reviewer sessions | Fable 5.1 / high | Fable 5.1 / high | Fable 5.1 / high |
| QA gate (code issues) | Fable 5.1 / low | Opus 5 / low | Opus 5 / low |
| 4 release-candidate reviews | Fable 5.1 / high | Fable 5.1 / high | Fable 5.1 / high |
| Effort | as labeled | as labeled | as labeled |
| **Chunks ($2,500 list each)** | **8** | **5** | 6 |
| List cost, 601 issues + 4 RC reviews | $18,522 | $10,450 | $12,892 |
| **Discounted cost to Justin** | **$370.44** | **$209.00** | $257.85 |
| Whole chunks billed | 8 x $50 = $400 | 5 x $50 = $250 | 6 x $50 = $300 |
| Wall-clock at 16 builders, 24/7 | 38.6 h (1.61 days), ends 2026-09-20T04:50Z | same | same |
| By phase (list) P0 / P1 / P2 | $4,204 / $9,964 / $4,079 | $2,728 / $5,272 / $2,175 | $3,024 / $6,786 / $2,808 |
| + 195 deferred (`v0.2` chunk, section 5) | +$6,572 list = +$131.43, +14.3 h | +$3,418 list = +$68.36, +14.3 h | +$4,412 list = +$88.23 |
| Everything (601 + 195) | $25,093 list = **$501.87**, 52.9 h | $13,868 list = **$277.35**, 52.9 h | $17,304 list = $346.08 |

Mix A costs $8,072 more at list than mix B, which is **$161.44 more to Justin**. Both mixes run the same 38.6-hour schedule because durations are per Size, not per model. **Mix B stays the recommendation and is what the Chunk labels encode.** Two things changed in its definition since round 3: builder models now come from the `Model` labels every leaf carries (the CLAUDE.md model/effort rule, so the plan prices what the sessions will actually run: Sonnet 374, Opus 139, Fable 80, Haiku 8), and Spec / Research issues stay on Fable 5.1. Because 374 of the builders are Sonnet 5, the Fable 5.1 reviewer overlay (40% of builder tokens at 5x the price) is now the largest line: reviewer + QA + RC sessions are 61% of the mix-B list cost. Switching reviewers to the `cost-and-duration-estimate.md` section 4b rule (Opus 5 after an Opus or Fable builder, Sonnet 5 after a Sonnet builder) would take roughly a chunk off; it is not applied here because every reviewer-session prompt in the plan names Fable. The round-3 definition (Opus 5 on every code builder) is kept as a reference column: 6 chunks, $257.85.

Reading the clock: 38.6 hours is session time with dependencies respected and nothing else in the way; 16 builders are busy 15.7 of the time on average, so the build is capacity-bound (the branch-start critical path is 27.8 h; without the branch-start rule the longest chain alone is 40.4 h). Not in the clock: `Needs Justin` answers, merge-queue conflicts on shared files, the 30% re-review bounce (its tokens are in the x1.25 contingency, its minutes are not). Section 3 lists, per chunk, which decisions must be answered before it starts. The `Needs Justin` queue holds five open items at a time (PAP-94), so chunk 1's items have to be batched into two cards.

## 3. Mix B (canonical): builders from the Model labels, Fable 5.1 on Spec/Research, reviewers and RC reviews; Opus 5 QA gate

| Chunk | Issues | Points | List | To Justin | Hours | Start | End | Builders by model | Release candidates | Milestones done | Issues from the 5 new projects |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 135 | 360 | $2,486 | $49.72 | 9.6 | 2026-09-18T14:15Z | 2026-09-18T23:50Z | Sonnet 53, Fable 46, Opus 36 | RC0 | 2 | 0 |
| 2 | 125 | 353 | $2,498 | $49.96 | 8.5 | 2026-09-18T23:50Z | 2026-09-19T08:20Z | Sonnet 88, Opus 24, Fable 13 | RC1 | 2 | 1 |
| 3 | 136 | 378 | $2,498 | $49.95 | 9.5 | 2026-09-19T08:20Z | 2026-09-19T17:50Z | Sonnet 70, Opus 46, Fable 19, Haiku 1 | - | 4 | 10 |
| 4 | 143 | 394 | $2,493 | $49.85 | 9.2 | 2026-09-19T17:50Z | 2026-09-20T03:05Z | Sonnet 111, Opus 27, Haiku 4, Fable 1 | RC2 | 25 | 7 |
| 5 | 62 | 124 | $475 | $9.51 | 1.8 | 2026-09-20T03:05Z | 2026-09-20T04:50Z | Sonnet 52, Opus 6, Haiku 3, Fable 1 | RC3 | 26 | 1 |
| **Total** | **601** | **1609** | **$10,450** | **$209.00** | **38.6** | 2026-09-18T14:15Z | 2026-09-20T04:50Z | Sonnet 374, Opus 139, Fable 80, Haiku 8 | RC0-RC3 | 59 | 19 |

### Chunk 1: $2,486 list, $49.72 to Justin, 9.6 h (2026-09-18T14:15Z to 2026-09-18T23:50Z)

135 issues, 360 points: P0 93 / P1 40 / P2 2; Build 73, Docs 2, Infra 15, Research 14, Spec 31; sizes S 45 / M 90 / L 0; builders Sonnet 53, Fable 46, Opus 36. Earliest issue in the chunk started 2026-09-18T14:15Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-1 (resolved): Linear: upgrade the workspace plan (PAP-91). Resolved: workspace is on Linear Basic. Gates: 91.
* NJ-2: Infra batch (PAP-25): Hetzner account and cpx41, registrar or Cloudflare token (or accept sslip.io), Resend sign-up, sops recovery key. Gates: 25.
* NJ-3: GitHub App on org imagine-os with repo+workflow scope (PAP-47). Gates: 47.
* NJ-5: Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97). Gates: 92, 97.
* NJ-6: Code signing (PAP-256): Apple Developer Program + Azure Trusted Signing, or accept unsigned v0.1.0 installers (default after 48 h: unsigned). Gates: 256.
* NJ-8: Approve docs/pm/justin-queue.md (PAP-94) and the issue contract (PAP-93). Gates: 94, 93.
* NJ-9: Hire the roster (PAP-104, PAP-210): nine leads, 28 sub-characters, tool scope classes. Gates: 284, 285, 286, 287, 210.
* NJ-10: Stripe test-mode account and restricted key (PAP-177); Google Cloud OAuth consent screen (PAP-224, PAP-200). Gates: 177, 224, 200.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Points | Umbrellas completed |
|---|---|---|---|
| Agent Characters & Orgs (`agents`) | 103 105 108 284 285 286 287 713 | 22 | **104** Write the nine lead characters and their sub-characters as . |
| Universal App Shell & Repo Template (`app-shell`) | 13 14 16 17 25 255 256 257 258 259 260 264 305 447 503 508 | 44 | **19** Add Tauri 2 desktop target for Linux, macOS and Windows shar, **20** Add Tauri 2 mobile targets (iOS, Android) with platform capa, **22** Write `paperos create <app>` CLI that clones the template in |
| Business Core: Payments, Finance & Payroll (`business-core`) | 175 392 768 | 8 | - |
| In-App Collaboration & Knowledge (`collab`) | 127 | 2 | - |
| Data Layer & Database (`data-layer`) | 30 31 32 33 34 37 38 42 267 268 269 270 279 302 448 555 556 557 558 564 565 | 59 | **35** Expose a typed API via oRPC with Zod schemas generated from , **43** Build the background jobs and scheduler package (pg-boss) wi, **303** Specify the domain event contract: envelope, topic catalogue, **304** Specify and build request idempotency and rate limiting: `Id |
| Design System (`design-system`) | 66 68 70 72 74 236 237 238 459 655 656 657 659 660 661 662 665 666 | 50 | **67** Adopt Base UI/Radix primitives with Tailwind v4 and build 20, **71** Build data display components: cell renderers, Badge, Avatar, **233** Build date, time, date-range and calendar pickers plus form- |
| Version Control & Forge Independence (`forge`) | 44 46 273 274 275 449 519 520 521 526 | 23 | **45** Deploy Forgejo on the VPS behind Caddy with SSO from Better , **47** Configure bidirectional push mirroring between Forgejo and t, **48** Create scoped bot accounts and deploy keys for each agent ch, **50** Run Forgejo Actions runners so CI works even when GitHub is , **51** Script `forge bootstrap <repo>` to configure imagine-os repo |
| Identity, Roles & Audiences (`identity`) | 55 56 219 223 224 225 226 227 228 229 456 578 | 34 | **57** Install Better Auth with passkeys, magic link, Google/GitHub, **59** Build permission engine combining role-based grants with att |
| Multi-Input Control & Accessibility (`input`) | 150 152 289 290 291 476 641 642 643 644 | 24 | **151** Build the global command registry with keyboard shortcuts, c |
| Library Discovery & Integration (`libraries`) | 209 210 212 292 293 294 295 296 297 350 | 27 | **213** Survey table, canvas, editor and chart libraries (TanStack, , **214** Survey backend building blocks (Better Auth, Drizzle, Electr |
| Migration & Import Tools (`migration`) | 198 | 3 | - |
| Module System & Swap Tooling (`module-system`) | 433 436 438 537 | 10 | **434** Build the module registry and dependency-injection container |
| Project Management & Claude Pipeline (`pm-linear`) | 91 92 93 94 97 281 282 283 691 704 | 26 | **96** Build the orchestrator that polls Ready for Claude, spawns o |
| Quality Pipeline (`quality`) | 78 79 239 | 8 | - |
| Multiplayer & Realtime (`realtime`) | 139 | 2 | - |
| Spec Builder (`spec-builder`) | 114 115 117 121 311 739 | 15 | - |
| Table & Views Engine (`tables`) | 161 | 3 | - |

**Deliverable at the end of the chunk**

* **RC0** review runs at 2026-09-18T22:20Z: RC0 staging + sign-in + orchestrator claiming.
* Milestones completed (non-deferred scope): Data Layer & Database / Postgres + Drizzle baseline (16 issues, target 2026-09-22, done 2026-09-18T22:20Z); Multi-Input Control & Accessibility / Keyboard and command system (10 issues, target 2026-09-23, done 2026-09-18T23:35Z).

### Chunk 2: $2,498 list, $49.96 to Justin, 8.5 h (2026-09-18T23:50Z to 2026-09-19T08:20Z)

125 issues, 353 points: P0 25 / P1 85 / P2 15; Build 98, Infra 13, Research 3, Review 1, Spec 10; sizes S 24 / M 100 / L 1; builders Sonnet 88, Opus 24, Fable 13. Earliest issue in the chunk started 2026-09-18T22:00Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-7: License of the template code (PAP-211): MIT, Apache-2.0 or proprietary; default Apache-2.0. Gates: 211.
* NJ-11: Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0 (RC1). Gates: RC1.
* NJ-12: Payroll provider (PAP-176): sign the Check sandbox agreement (default) or Gusto Embedded. Gates: 176.
* NJ-13: Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136). Gates: 414, 415, 416, 323, 324, 325.
* NJ-18: Industry list and terminology defaults (PAP-126). Gates: 126.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Points | Umbrellas completed |
|---|---|---|---|
| Agent Characters & Orgs (`agents`) | 709 710 714 | 7 | **106** Implement per-character MCP allowlists and permission modes , **299** Build prompt-injection defences for agent sessions: trust ti |
| Universal App Shell & Repo Template (`app-shell`) | 15 18 261 262 265 266 504 505 912 | 23 | **26** Build the app deploy pipeline: Docker images for apps/web an, **27** Add internationalisation and localisation: ICU message catal, **28** Make every platform capability a removable module: module ma |
| Tenant AI Assistant & Business Agents (`assistant`) | 834 | 3 | - |
| Business Core: Payments, Finance & Payroll (`business-core`) | 177 178 393 394 395 396 397 484 | 24 | **179** Build a double-entry ledger (accounts, journal entries, peri |
| In-App Collaboration & Knowledge (`collab`) | 128 129 133 317 318 319 320 725 | 23 | **131** Implement in-app comments anchored to any entity, page eleme |
| Data Layer & Database (`data-layer`) | 40 271 272 353 370 562 563 566 | 24 | **36** Integrate PGlite and ElectricSQL shapes for local-first read, **354** Add object-storage, Yjs, orchestrator and sops-key backups a |
| Design System (`design-system`) | 69 234 658 663 664 667 668 | 18 | **75** Implement light, dark and high-contrast themes plus per-tena |
| Version Control & Forge Independence (`forge`) | 522 527 | 6 | **52** Automate semantic release tags and changelog generation on m |
| Growth: Marketing, Outreach & CRM (`growth`) | 790 791 | 6 | **187** Model CRM entities: lead, contact, company, deal, pipeline s |
| Identity, Roles & Audiences (`identity`) | 64 579 582 583 584 585 586 587 | 23 | **58** Implement organizations, workspaces, invitations and tenant , **60** Make agents first-class principals with scoped API keys, rat, **62** Ship the customer-facing portal shell (login, profile, billi, **63** Ship the staff console shell with tenant switcher, audience  |
| Multi-Input Control & Accessibility (`input`) | 329 330 331 645 651 652 | 16 | **154** Implement a touch gesture system (swipe, pinch, long-press) , **155** Build accessible drag-and-drop (dnd-kit) for tables, kanban  |
| Library Discovery & Integration (`libraries`) | 351 352 | 6 | **215** Evaluate whole OSS products to embed or fork (Twenty CRM, No |
| Migration & Import Tools (`migration`) | 347 348 349 | 9 | **199** Build the import framework: source connector, schema-mapping |
| Module System & Swap Tooling (`module-system`) | 542 | 2 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 465 | 3 | - |
| Quality Pipeline (`quality`) | 80 87 240 242 243 244 245 246 247 248 675 678 679 | 34 | **81** Build gate 2: three Claude reviewer agents (correctness, sec, **82** Build gate 3: Playwright screenshot suite across the 7-width |
| Multiplayer & Realtime (`realtime`) | 140 326 327 328 475 599 603 604 | 23 | **142** Add collaborative rich text (Tiptap + Yjs) as the shared edi, **143** Stream record changes via Electric shapes to all connected c |
| Spec Builder (`spec-builder`) | 116 118 122 123 126 312 313 314 315 316 361 467 740 741 | 43 | **119** Specify the data section (entities, queries, mutations, sync, **120** Generate page scaffolds (layout, component tree, loading/emp |
| Table & Views Engine (`tables`) | 162 335 336 337 338 339 340 341 342 343 344 483 613 614 615 616 619 621 627 629 630 | 60 | **163** Build the view query compiler from view model to SQL and Ele, **164** Implement field types: text, number, currency, date, select,, **165** Build the virtualized grid view (TanStack Table) with inline |

**Deliverable at the end of the chunk**

* **RC1** review runs at 2026-09-19T07:20Z: RC1 v0.1.0-rc.1: RLS permissions, installers, Yjs server, codegen, Stripe test mode, story baselines.
* Milestones completed (non-deferred scope): Design System / Tokens and primitives (9 issues, target 2026-09-22, done 2026-09-19T06:20Z); Universal App Shell & Repo Template / Template scaffolds and runs on web (9 issues, target 2026-09-20, done 2026-09-19T08:20Z).
* New projects (round 4): `assistant` 1.

### Chunk 3: $2,498 list, $49.95 to Justin, 9.5 h (2026-09-19T08:20Z to 2026-09-19T17:50Z)

136 issues, 378 points: P0 27 / P1 71 / P2 38; Build 84, Docs 2, Infra 11, Research 2, Review 20, Spec 17; sizes S 32 / M 103 / L 1; builders Sonnet 70, Opus 46, Fable 19, Haiku 1. Earliest issue in the chunk started 2026-09-19T07:00Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-4: Anthropic Console: orchestrator API key, hard spend limit, usage export (PAP-98). Gates: 98.
* NJ-17: Accessibility statement wording (PAP-160). Gates: 160.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Points | Umbrellas completed |
|---|---|---|---|
| Agent Characters & Orgs (`agents`) | 280 288 308 309 466 469 711 712 716 718 | 27 | **298** Define and enforce the agent destructive-action deny list: p |
| Universal App Shell & Repo Template (`app-shell`) | 263 364 450 500 501 507 | 16 | **21** Build responsive breakpoint matrix and multi-monitor window , **363** Build the default surfaces starter kit: customer portal and , **365** Build golden path provisioning: parallel idempotent steps, w, **366** Build runtime feature flags: per-tenant and per-audience fla |
| Tenant AI Assistant & Business Agents (`assistant`) | 833 835 836 | 9 | - |
| Business Core: Payments, Finance & Payroll (`business-core`) | 176 183 359 398 399 487 765 766 767 769 | 25 | **180** Implement invoices, quotes and receipts with PDF generation  |
| In-App Collaboration & Knowledge (`collab`) | 321 322 323 324 325 474 477 | 19 | **132** Build the canvas view (tldraw or React Flow) showing the UX , **136** Build a notification center (in-app, email, Slack) with per- |
| Commerce, Operations & Vertical Packs (`commerce`) | 877 878 | 6 | - |
| Data Layer & Database (`data-layer`) | 451 567 568 | 11 | **39** Add full-text and vector search (tsvector + pgvector) over a |
| Design System (`design-system`) | 73 460 670 | 8 | - |
| Scheduling, Messaging & Customer Engagement (`engagement`) | 862 863 | 6 | - |
| Version Control & Forge Independence (`forge`) | 452 523 524 531 | 10 | **358** Add supply-chain integrity: lockfile and minimum-release-age |
| Growth: Marketing, Outreach & CRM (`growth`) | 188 189 485 488 | 11 | - |
| Identity, Roles & Audiences (`identity`) | 61 457 580 581 | 12 | **220** Build session and device management: list and revoke session |
| Multi-Input Control & Accessibility (`input`) | 153 156 479 647 653 | 15 | - |
| Library Discovery & Integration (`libraries`) | 211 216 493 495 | 11 | - |
| Migration & Import Tools (`migration`) | 201 414 415 420 421 492 494 | 19 | - |
| Module System & Swap Tooling (`module-system`) | 437 439 440 538 541 | 12 | **435** Build the feature-flag swap mechanism: `module.<id>.impl` va, **441** Build the conformance test runner and golden fixture kit: `d |
| Platform Operations, Analytics & Compliance (`platform-ops`) | 893 | 3 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 98 99 100 300 307 372 468 692 693 694 699 702 703 | 34 | - |
| Quality Pipeline (`quality`) | 86 249 252 253 254 462 463 673 674 676 677 682 683 | 35 | **88** Define the release train: nightly staging deploy, weekly rel, **356** Build security telemetry and alerting: auth anomalies, RLS d, **357** Add dynamic security testing: nightly ZAP baseline and authe |
| Multiplayer & Realtime (`realtime`) | 144 145 478 600 605 | 14 | **381** Build the push transport: server-to-client notification and  |
| Spec Builder (`spec-builder`) | 360 362 376 470 | 12 | - |
| Table & Views Engine (`tables`) | 167 332 333 334 345 382 383 385 386 388 389 486 617 618 620 622 623 624 625 | 57 | **166** Build the filter builder (AND/OR groups), multi-sort and mul, **169** Build gallery, list and form views, **170** Build map view and chart view (bar, line, pie, number) bound, **172** Add saved views, personal vs shared views, public embeds and |
| Workflows, Approvals, Forms, Documents & E-Signature (`workflows`) | 847 848 | 6 | - |

**Deliverable at the end of the chunk**

* Milestones completed (non-deferred scope): Module System & Swap Tooling / Kernel and lint live (5 issues, target 2026-09-22, done 2026-09-19T09:20Z); Table & Views Engine / Grid with sort, filter, group (20 issues, target 2026-09-28, done 2026-09-19T10:35Z); Design System / Component library covers app shell needs (16 issues, target 2026-09-25, done 2026-09-19T14:05Z); Growth: Marketing, Outreach & CRM / CRM core (5 issues, 3 deferred excluded, target 2026-09-29, done 2026-09-19T16:50Z).
* New projects (round 4): `assistant` 3, `workflows` 2, `engagement` 2, `commerce` 2, `platform-ops` 1.

### Chunk 4: $2,493 list, $49.85 to Justin, 9.2 h (2026-09-19T17:50Z to 2026-09-20T03:05Z)

143 issues, 394 points: P0 9 / P1 85 / P2 49; Build 108, Docs 8, Infra 20, Review 6, Spec 1; sizes S 35 / M 108 / L 0; builders Sonnet 111, Opus 27, Haiku 4, Fable 1. Earliest issue in the chunk started 2026-09-19T16:15Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-15: Release candidate v0.1.0-rc.2 from PAP-254: /approve or /reject (RC2). Gates: RC2.
* NJ-16: Approve the content agent (PAP-192) and migration agent (PAP-208). Gates: 192, 208.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Points | Umbrellas completed |
|---|---|---|---|
| Agent Characters & Orgs (`agents`) | 107 109 111 112 113 310 472 715 717 722 | 28 | **110** Create an eval harness with golden tasks per character, scor |
| Universal App Shell & Repo Template (`app-shell`) | 24 29 369 429 431 453 498 502 509 510 511 512 | 34 | **368** Define the client error handling and crash reporting contrac |
| Tenant AI Assistant & Business Agents (`assistant`) | 837 | 3 | - |
| Business Core: Payments, Finance & Payroll (`business-core`) | 181 186 391 400 490 | 15 | **184** Define the payroll provider interface and implement the firs |
| In-App Collaboration & Knowledge (`collab`) | 130 134 135 138 379 480 728 729 731 | 25 | - |
| Commerce, Operations & Vertical Packs (`commerce`) | 879 | 3 | - |
| Data Layer & Database (`data-layer`) | 432 454 559 560 561 569 570 571 572 | 24 | **355** Enforce data retention, PII classification and tenant hard-p |
| Design System (`design-system`) | 76 461 669 672 | 10 | - |
| Scheduling, Messaging & Customer Engagement (`engagement`) | 864 | 3 | - |
| Version Control & Forge Independence (`forge`) | 371 455 528 529 530 532 533 534 | 19 | - |
| Growth: Marketing, Outreach & CRM (`growth`) | 192 491 | 6 | - |
| Identity, Roles & Audiences (`identity`) | 301 458 588 589 590 593 594 | 20 | - |
| Multi-Input Control & Accessibility (`input`) | 160 482 646 648 654 | 14 | **159** Integrate voice commands and dictation (Web Speech with Whis |
| Library Discovery & Integration (`libraries`) | 217 497 753 754 756 757 | 16 | - |
| Migration & Import Tools (`migration`) | 200 208 416 422 496 814 815 | 21 | **202** Import Airtable bases (tables, views, relations, attachments, **205** Export everything (tables, docs, files, ledger) to open form |
| Module System & Swap Tooling (`module-system`) | 444 445 446 539 540 543 544 545 546 547 548 549 550 551 | 34 | **442** Build the swap playbook automation: `paperos module swap <id, **443** Build the data migration adapter kit: expand-contract table  |
| Platform Operations, Analytics & Compliance (`platform-ops`) | 894 895 896 | 9 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 102 306 373 471 695 696 697 | 19 | - |
| Quality Pipeline (`quality`) | 83 84 89 90 250 251 464 680 | 22 | **85** Build gate 4: edge-case hunter agent generating adversarial  |
| Multiplayer & Realtime (`realtime`) | 148 481 601 602 606 607 608 | 20 | **141** Build the presence layer: cursors, avatars, selections and ', **147** Load test 500 concurrent users per room and 10k rooms; tune  |
| Spec Builder (`spec-builder`) | 125 375 377 378 473 742 743 749 | 24 | **124** Build the spec editor UI with form and YAML views and live p |
| Table & Views Engine (`tables`) | 346 384 387 390 489 626 628 631 | 22 | **168** Build calendar, timeline and Gantt views with dependencies, **171** Build a formula engine compatible with common Airtable and N, **173** Compose views into dashboard pages with drag-arranged blocks, **174** Build table automations: triggers (record change, schedule,  |
| Workflows, Approvals, Forms, Documents & E-Signature (`workflows`) | 849 | 3 | - |

**Deliverable at the end of the chunk**

* **RC2** review runs at 2026-09-20T02:20Z: RC2 v0.1.0-rc.2, first real cut: gates 1-4, grid + compiler, comments, record sync, ledger + invoices, imports, drill.
* Milestones completed (non-deferred scope): Multiplayer & Realtime / Yjs server and presence (7 issues, target 2026-09-25, done 2026-09-19T18:05Z); Agent Characters & Orgs / Roster defined and installed (18 issues, target 2026-09-24, done 2026-09-19T19:20Z); In-App Collaboration & Knowledge / Comments and canvas (14 issues, target 2026-09-29, done 2026-09-19T19:50Z); Growth: Marketing, Outreach & CRM / Acquisition analytics (1 issues, 21 deferred excluded, target 2026-10-01, done 2026-09-19T21:05Z); Universal App Shell & Repo Template / Desktop and mobile shells build (17 issues, target 2026-09-24, done 2026-09-19T21:50Z); Business Core: Payments, Finance & Payroll / Ledger and reports (14 issues, 4 deferred excluded, target 2026-09-29, done 2026-09-19T23:35Z); Agent Characters & Orgs / Agent org visible in app (2 issues, 1 deferred excluded, target 2026-09-30, done 2026-09-19T23:35Z); Migration & Import Tools / Business migrations (2 issues, 14 deferred excluded, target 2026-10-01, done 2026-09-20T00:20Z); Table & Views Engine / View sharing, formulas, dashboards (14 issues, 7 deferred excluded, target 2026-09-30, done 2026-09-20T00:35Z); Commerce, Operations & Vertical Packs / Commerce contract and catalog (3 issues, target 2026-10-01, done 2026-09-20T00:50Z); Scheduling, Messaging & Customer Engagement / Engagement contract and booking core (3 issues, target 2026-10-01, done 2026-09-20T00:50Z); Business Core: Payments, Finance & Payroll / Payroll adapter and cash dashboard (5 issues, 18 deferred excluded, target 2026-10-01, done 2026-09-20T00:50Z); Business Core: Payments, Finance & Payroll / Stripe billing live (7 issues, target 2026-09-27, done 2026-09-20T00:50Z); In-App Collaboration & Knowledge / Docs and prompt log stores (6 issues, target 2026-09-23, done 2026-09-20T01:20Z); Tenant AI Assistant & Business Agents / Assistant contract and grounded chat (5 issues, target 2026-10-01, done 2026-09-20T02:05Z); Multi-Input Control & Accessibility / Voice and accessibility certification (7 issues, 3 deferred excluded, target 2026-09-30, done 2026-09-20T02:05Z); Table & Views Engine / All view types (15 issues, 2 deferred excluded, target 2026-09-29, done 2026-09-20T02:05Z); Identity, Roles & Audiences / Auth works across web and desktop (14 issues, target 2026-09-23, done 2026-09-20T02:05Z); Library Discovery & Integration / Evaluation process (5 issues, target 2026-09-20, done 2026-09-20T02:20Z); Platform Operations, Analytics & Compliance / Ops contract, super-admin console and status page (4 issues, target 2026-10-01, done 2026-09-20T02:35Z); Version Control & Forge Independence / CI runs on both forges (10 issues, target 2026-09-24, done 2026-09-20T02:35Z); Multiplayer & Realtime / Record sync and conflict UX (10 issues, target 2026-09-28, done 2026-09-20T03:05Z); Identity, Roles & Audiences / Roles and audiences enforced end to end (9 issues, target 2026-09-25, done 2026-09-20T03:05Z); Data Layer & Database / Local-first sync working (16 issues, target 2026-09-25, done 2026-09-20T03:05Z); Module System & Swap Tooling / Contracts and conformance wired (13 issues, target 2026-09-27, done 2026-09-20T03:05Z).
* New projects (round 4): `assistant` 1, `workflows` 1, `engagement` 1, `commerce` 1, `platform-ops` 3.

### Chunk 5: $475 list, $9.51 to Justin, 1.8 h (2026-09-20T03:05Z to 2026-09-20T04:50Z)

62 issues, 124 points: P0 2 / P1 33 / P2 27; Build 46, Docs 5, Infra 9, Research 1, Review 1; sizes S 62 / M 0 / L 0; builders Sonnet 52, Opus 6, Haiku 3, Fable 1. Earliest issue in the chunk started 2026-09-20T02:00Z (overlap with the previous chunk).

**Needs Justin before this chunk starts**

* NJ-19: Scope freeze: deferred list becomes milestone v0.2. Gates: RC3.
* NJ-20: Release candidate v0.1.0: /approve promotes and tags (RC3, PAP-254). Gates: RC3.
* NJ-21: PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29). Gates: RC3.

**Issues by project** (identifiers omit `PAP-`; umbrellas in bold complete in this chunk)

| Project | Issues | Points | Umbrellas completed |
|---|---|---|---|
| Agent Characters & Orgs (`agents`) | 719 720 721 | 6 | - |
| Universal App Shell & Repo Template (`app-shell`) | 499 506 | 4 | **367** Build the first-run tenant onboarding wizard: create organis, **430** Build `paperos upgrade`: apply template updates to generated |
| In-App Collaboration & Knowledge (`collab`) | 380 726 727 730 732 733 734 | 14 | - |
| Data Layer & Database (`data-layer`) | 41 573 574 575 908 | 10 | - |
| Design System (`design-system`) | 77 671 | 4 | - |
| Version Control & Forge Independence (`forge`) | 49 525 | 4 | **53** Run a disaster-recovery drill rebuilding all repos and CI fr |
| Growth: Marketing, Outreach & CRM (`growth`) | 792 | 2 | - |
| Identity, Roles & Audiences (`identity`) | 591 592 595 596 597 | 10 | - |
| Multi-Input Control & Accessibility (`input`) | 649 | 2 | - |
| Library Discovery & Integration (`libraries`) | 755 758 759 760 761 762 763 | 14 | - |
| Migration & Import Tools (`migration`) | 413 813 | 4 | - |
| Module System & Swap Tooling (`module-system`) | 552 553 | 4 | - |
| Project Management & Claude Pipeline (`pm-linear`) | 95 374 698 700 701 705 706 | 14 | **101** Build bidirectional Linear sync (GraphQL + webhooks) with co |
| Quality Pipeline (`quality`) | 241 681 684 685 | 8 | - |
| Multiplayer & Realtime (`realtime`) | 146 609 610 611 612 | 10 | - |
| Spec Builder (`spec-builder`) | 744 745 746 747 748 750 | 12 | - |
| Workflows, Approvals, Forms, Documents & E-Signature (`workflows`) | 850 | 2 | - |

**Deliverable at the end of the chunk**

* **RC3** review runs at 2026-09-20T04:50Z: RC3 = v0.1.0: every non-deferred issue Done.
* Milestones completed (non-deferred scope): Spec Builder / Spec schema and validator (9 issues, target 2026-09-24, done 2026-09-20T03:20Z); Project Management & Claude Pipeline / Orchestrator claims and ships issues (16 issues, target 2026-09-22, done 2026-09-20T03:20Z); Migration & Import Tools / Import framework and CSV (9 issues, target 2026-09-28, done 2026-09-20T03:35Z); Agent Characters & Orgs / Sub-agents, skills and evals live (14 issues, 1 deferred excluded, target 2026-09-25, done 2026-09-20T03:35Z); Quality Pipeline / Gates 1 and 2 on every PR (18 issues, target 2026-09-25, done 2026-09-20T03:35Z); Library Discovery & Integration / Core adoptions decided (13 issues, target 2026-09-24, done 2026-09-20T03:50Z); Spec Builder / Codegen and conformance tests (20 issues, target 2026-09-26, done 2026-09-20T03:50Z); Universal App Shell & Repo Template / Multi-monitor and PWA polish (19 issues, 7 deferred excluded, target 2026-09-29, done 2026-09-20T04:05Z); Growth: Marketing, Outreach & CRM / Campaigns and social (3 issues, 10 deferred excluded, target 2026-09-30, done 2026-09-20T04:05Z); Library Discovery & Integration / Registry live (11 issues, 2 deferred excluded, target 2026-09-30, done 2026-09-20T04:05Z); Project Management & Claude Pipeline / PM module syncs both ways (12 issues, 2 deferred excluded, target 2026-09-30, done 2026-09-20T04:05Z); Version Control & Forge Independence / Disaster recovery proven (7 issues, 5 deferred excluded, target 2026-09-30, done 2026-09-20T04:05Z); Module System & Swap Tooling / Shell swap drill passes (8 issues, 1 deferred excluded, target 2026-10-01, done 2026-09-20T04:20Z); Identity, Roles & Audiences / Agent principals and enterprise (13 issues, 7 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); In-App Collaboration & Knowledge / Knowledge surfaced everywhere (12 issues, 6 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); Data Layer & Database / Tenant-safe and observable (14 issues, 3 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); Workflows, Approvals, Forms, Documents & E-Signature / Workflow contract and approvals (4 issues, target 2026-10-01, done 2026-09-20T04:35Z); Migration & Import Tools / Airtable, Notion, ClickUp importers (9 issues, 12 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); Project Management & Claude Pipeline / Linear configured for the pipeline (10 issues, target 2026-09-20, done 2026-09-20T04:35Z); Quality Pipeline / Visual and video gates (10 issues, 3 deferred excluded, target 2026-09-26, done 2026-09-20T04:35Z); Quality Pipeline / Edge-case hunting and release trains (13 issues, 2 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); Multi-Input Control & Accessibility / Touch, pen, gamepad (10 issues, target 2026-09-27, done 2026-09-20T04:35Z); Multiplayer & Realtime / Scale and offline tested (9 issues, 1 deferred excluded, target 2026-09-30, done 2026-09-20T04:35Z); Version Control & Forge Independence / Forgejo live and mirrored (9 issues, target 2026-09-20, done 2026-09-20T04:35Z); Design System / Themable per tenant with docs (9 issues, 2 deferred excluded, target 2026-09-30, done 2026-09-20T04:50Z); Spec Builder / Spec editor UI (9 issues, 2 deferred excluded, target 2026-09-30, done 2026-09-20T04:50Z).
* New projects (round 4): `workflows` 1.

## 4. Mix A: all Fable 5.1 (builders, reviewers, QA, RC reviews)

| Chunk | Issues | Points | List | To Justin | Hours | Start | End | Builders by model | Release candidates | Milestones done | Issues from the 5 new projects |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 96 | 253 | $2,474 | $49.49 | 6.8 | 2026-09-18T14:15Z | 2026-09-18T21:05Z | Fable 96 | - | 0 | 0 |
| 2 | 69 | 191 | $2,489 | $49.79 | 5.0 | 2026-09-18T21:05Z | 2026-09-19T02:05Z | Fable 69 | RC0 | 2 | 0 |
| 3 | 66 | 191 | $2,482 | $49.65 | 4.8 | 2026-09-19T02:05Z | 2026-09-19T06:50Z | Fable 66 | - | 1 | 0 |
| 4 | 76 | 208 | $2,486 | $49.71 | 4.8 | 2026-09-19T06:50Z | 2026-09-19T11:35Z | Fable 76 | RC1 | 3 | 2 |
| 5 | 75 | 213 | $2,469 | $49.38 | 5.2 | 2026-09-19T11:35Z | 2026-09-19T16:50Z | Fable 75 | - | 2 | 4 |
| 6 | 77 | 210 | $2,485 | $49.71 | 5.5 | 2026-09-19T16:50Z | 2026-09-19T22:20Z | Fable 77 | - | 5 | 6 |
| 7 | 65 | 187 | $2,490 | $49.80 | 4.2 | 2026-09-19T22:20Z | 2026-09-20T02:35Z | Fable 65 | RC2 | 16 | 5 |
| 8 | 77 | 156 | $1,145 | $22.91 | 2.2 | 2026-09-20T02:35Z | 2026-09-20T04:50Z | Fable 77 | RC3 | 30 | 2 |
| **Total** | **601** | **1609** | **$18,522** | **$370.44** | **38.6** | 2026-09-18T14:15Z | 2026-09-20T04:50Z | Fable 601 | RC0-RC3 | 59 | 19 |

Same schedule and the same issue order as mix B; only the dollar boundaries move, so the chunk contents differ. Chunk contents, milestones and Needs Justin items per chunk are in `plan/round4/chunks-v2.json` under `mixes.A.chunks`. The Needs Justin items map to mix A chunks as follows: chunk 1: NJ-1, NJ-2, NJ-3, NJ-5, NJ-6, NJ-8, NJ-9, NJ-10; chunk 2: none; chunk 3: NJ-18; chunk 4: NJ-7, NJ-11, NJ-12, NJ-13; chunk 5: NJ-4; chunk 6: NJ-16, NJ-17; chunk 7: NJ-15; chunk 8: NJ-19, NJ-20, NJ-21.

## 5. Final chunk `v0.2`: the 195 deferred leaves

Claimable only after NJ-14 (stop-loss go) and rescoped to v0.2 at NJ-19; each carries the `Deferred` label (own or inherited from a deferred umbrella) and now the `Chunk: v0.2` label. 548 points. Scheduled with the same 16 builders after RC3: **14.3 h** (2026-09-20T04:50Z to 2026-09-20T19:10Z) in both mixes. It is one chunk in the plan but 1.37 chunks of money under mix B, so billed whole it is $100.

| Mix | List | To Justin | Equivalent chunks | Builders |
|---|---|---|---|---|
| A | $6,572 | $131.43 | 2.63 | Fable 195 |
| B | $3,418 | $68.36 | 1.37 | Sonnet 154, Opus 38, Fable 2, Haiku 1 |

Issues by project: `agents` 723 724 (4 pts); `app-shell` 23 513 514 515 516 517 518 (17 pts); `assistant` 838 839 840 841 842 843 844 845 846 (26 pts); `business-core` 182 185 770 771 772 773 774 775 776 777 778 779 780 781 782 783 784 785 786 787 788 789 (62 pts); `collab` 137 735 736 737 738 910 (16 pts); `commerce` 880 881 882 883 884 885 886 887 888 889 890 891 892 (45 pts); `data-layer` 576 577 909 (7 pts); `design-system` 235 911 (5 pts); `engagement` 865 866 867 868 869 870 871 872 873 874 875 876 (33 pts); `forge` 276 277 278 535 536 (14 pts); `growth` 194 195 401 402 403 404 405 406 407 408 409 410 411 412 793 794 795 796 797 798 799 800 801 802 803 804 805 806 807 808 809 810 811 812 (96 pts); `identity` 221 222 230 231 232 598 913 (21 pts); `input` 157 158 650 (9 pts); `libraries` 218 764 (5 pts); `migration` 417 418 419 423 424 425 426 427 428 816 817 818 819 820 821 822 823 824 825 826 827 828 829 830 831 832 (69 pts); `module-system` 554 (3 pts); `platform-ops` 897 898 899 900 901 902 903 904 905 906 907 (31 pts); `pm-linear` 707 708 (5 pts); `quality` 686 687 688 689 690 (11 pts); `realtime` 149 (3 pts); `spec-builder` 751 752 (5 pts); `tables` 632 633 634 635 636 637 638 639 640 (24 pts); `workflows` 851 852 853 854 855 856 857 858 859 860 861 (37 pts).

Needs Justin before it starts: NJ-14: Stop-loss checkpoint: go or no-go on the stretch pool (deferred set).

## 6. The five round-4 projects

Each has three milestones (10-01 contract, 10-09 surfaces, 10-16 swap and hardening) and mostly deferred work: the 10-01 contract slice is scheduled, the rest is `v0.2`.

| Project | Key | Leaves | Scheduled | Deferred | Points | Scheduled issues by chunk | Milestones |
|---|---|---|---|---|---|---|---|
| Tenant AI Assistant & Business Agents | `assistant` | 14 | 5 | 9 | 41 | chunk 2: 834; chunk 3: 833 835 836; chunk 4: 837 | Assistant contract and grounded chat (2026-10-01); Actions, copilots and portal assistant (2026-10-09); Business characters, evals and swap (2026-10-16) |
| Workflows, Approvals, Forms, Documents & E-Signature | `workflows` | 15 | 4 | 11 | 48 | chunk 3: 847 848; chunk 4: 849; chunk 5: 850 | Workflow contract and approvals (2026-10-01); Forms builder and document templates (2026-10-09); E-signature, canvas editor and swap (2026-10-16) |
| Scheduling, Messaging & Customer Engagement | `engagement` | 15 | 3 | 12 | 42 | chunk 3: 862 863; chunk 4: 864 | Engagement contract and booking core (2026-10-01); Messaging channels, help center and surveys (2026-10-09); Memberships, loyalty, announcements and swap (2026-10-16) |
| Commerce, Operations & Vertical Packs | `commerce` | 16 | 3 | 13 | 54 | chunk 3: 877 878; chunk 4: 879 | Commerce contract and catalog (2026-10-01); Orders, POS, purchasing, projects and HR (2026-10-09); Operations packs, marketplace and swap (2026-10-16) |
| Platform Operations, Analytics & Compliance | `platform-ops` | 15 | 4 | 11 | 43 | chunk 3: 893; chunk 4: 894 895 896 | Ops contract, super-admin console and status page (2026-10-01); Product analytics, experiments and abuse controls (2026-10-09); Compliance evidence, residency and swap (2026-10-16) |

## 7. Delta versus round 3

| | Round 3 (2026-09-17) | Round 4 (2026-09-18) |
|---|---|---|
| Scheduled leaves | 326 | 601 |
| Deferred leaves | 42 | 195 |
| Umbrellas | 52 | 105 |
| `blocks` relations | 1,148 effective | 3,041 live, 3,551 effective |
| Critical path | 36.8 h (full durations) | 27.8 h branch-start, 40.4 h full durations |
| Wall-clock at 16 builders | 37.3 h | 38.6 h (mean builders busy 15.7 of 16) |
| Mix B chunks / list / to Justin | 4 / $7,909 / $158.17 | 5 / $10,450 / $209.00 |
| Mix A chunks / list / to Justin | 5 / $11,166 / $223.32 | 8 / $18,522 / $370.44 |
| Deferred chunk, mix B | $983 / $19.66 / 5.5 h | $3,418 / $68.36 / 14.3 h |

Why: (1) **Scope.** 601 scheduled leaves instead of 326: 280 of the round-3 leaves are still leaves, 46 became umbrellas when round 4 gave them sub-issues (their children are counted instead), 60 are the round-3 module-system issues PAP-433..497 that had no chunk yet, and 261 are round-4 issues; 155 of the 416 round-4 issues are deferred (`v0.2`). (2) **Models.** Builder models now follow the `Model` labels (scenario E of the estimate: mostly Sonnet 5), so the per-issue price fell while the issue count rose 84%: list cost +32% for +84% issues. Under the round-3 definition (Opus 5 on every code builder) the same graph would be 6 chunks / $12,892 / $257.85. (3) **Clock.** The branch-start rule shortened the longest chain (27.8 h instead of a would-be 40.4 h), but with 84% more build minutes 16 builders are saturated, so the wall clock moved only from 37.3 h to 38.6 h; the schedule is now capacity-bound, and 20 builders would bring it near the 27.8-hour critical path. (4) **Recount.** The token model recomputed over the round-3 issue set with round-4 sizes gives $7,714 versus the $7,634 booked then (1%, from estimates that moved when Size text became Fibonacci points).

## 8. How to use this

1. Answer the chunk-1 Needs Justin items (NJ-2, NJ-3, NJ-5, NJ-6, NJ-8, NJ-9, NJ-10) before the first session starts; batch them into cards of five.
2. Run chunk 1 at 16 builders. The orchestrator uses the Chunk label order as its tie-breaker among Ready for Claude issues; sessions still claim from Ready for Claude only. Ledger reports list spend per chunk in the daily burn report (PAP-98) so the x0.02 invoice can be checked against the console.
3. Re-baseline after chunk 1: real per-size token burn replaces the S / M / L assumptions, `plan/round4/sched/pull_graph.py` then `model.py` regenerate this document, and `relabel.py` moves the Chunk labels.
4. Each chunk boundary is a natural stop: nothing in a later chunk is needed to keep an earlier chunk's deliverable working, so Justin can pause after any $50.
