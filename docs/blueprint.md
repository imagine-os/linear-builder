# PaperOS Core Platform Blueprint

Full blueprint (architecture diagram, org chart, timeline, budget chart, full index): [https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU](<https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU>)

## Vision

PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo template that ships to web, desktop (Linux/macOS/Windows) and mobile with a shared data layer, design system, multiplayer, table/views engine, identity for every audience, and business plumbing (payments, ledger, payroll, CRM) already wired. It is built and reviewed primarily by a roster of Claude agent characters working from Linear, behind a four-gate automated quality pipeline, so that by 2026-10-01 a new app goes from blank screen to running product in hours, and Justin only ever reviews release candidates, not pull requests.

**Ten-second summary:** 23 projects (5 new in round 4), 991 issues in team PAP (983 canonical: 901 spec-complete, 82 in Triage; 3,275 blocking relations), 69 milestones, 5 initiatives, 30 issues Ready for Claude today, 2,214 Fibonacci points, 29 documents, 13 days to the 2026-10-01 deadline. Round 4 details below.

## Key decisions

* **Stack: TypeScript monorepo, React 19 + Vite, Tauri 2 for native.** One pnpm + Turborepo monorepo. Web is React 19 + Vite + TanStack Router. Desktop (Linux, macOS, Windows) and mobile (iOS, Android) are Tauri 2 wrapping the same web bundle. PWA is the zero-install baseline. *Why:* A single codebase reaches every device class the brief lists; Tauri gives real multi-window (multi-monitor) and OS integration with a tiny Rust core, and Claude agents are strongest in TypeScript, which maximizes credit efficiency.
* **Hosting: self-hosted VPS via Coolify, GitHub Pages for demos.** Postgres, Forgejo, the API, the Yjs server and MinIO run in Docker on a Hetzner VPS managed by Coolify. Static demos and Storybook deploy to GitHub Pages. Vercel is not used for deploys (read-only). *Why:* Owns the data and the forge, costs tens of dollars a month, and avoids depending on a platform we cannot write to; Pages already exists as the public demo convention.
* **Data: Postgres as source of truth, Drizzle schema-as-code, local-first sync.** Postgres 17 with row-level security for tenancy, Drizzle ORM for typed schema and migrations, ElectricSQL shapes + PGlite for local-first reads and an offline write queue. Yjs handles document/canvas CRDTs; records stay relational. *Why:* Relational data with RLS is the safest multi-tenant model for agent-written code; local-first sync gives instant UI on every device; separating documents (CRDT) from records (SQL) avoids reinventing either.
* **Realtime: Yjs via Hocuspocus for documents and presence, Electric for records.** Self-hosted Hocuspocus server persists Yjs docs to Postgres and provides presence/awareness; Electric streams record changes. One WebSocket transport, auth via Better Auth session tokens. *Why:* Both are mature open-source pieces the brief's multiplayer, comments, canvas and multi-window requirements map onto directly; no custom sync protocol in two weeks.
* **Auth and audiences: Better Auth, agents as first-class principals.** Better Auth (self-hosted, TypeScript) with passkeys, magic links and OAuth, organization/tenant plugin, plus a permission engine combining roles with attribute policies declared in page specs. Audiences are composable segments (customer tiers, staff roles, partners, admins, agents). Every agent gets a scoped API key and visible attribution. *Why:* Covers customer vs staff vs everything between without a vendor lock-in, and making agents principals is what makes audit logs, permissions and presence honest when most contributors are Claude.
* **Repo template shape.** paperos-template contains apps/web, apps/desktop, apps/mobile, packages/{ui,core,spec,views,agents}, specs/ (app.spec.yaml + page specs), docs/, .claude/ (CLAUDE.md, agents, skills, rules), ops/ (compose, CI). `paperos create <app>` clones it into a pre-provisioned imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project. *Why:* Agents need a predictable place for everything; the template is the product, apps are instances.
* **Version control: Git as the format, Forgejo as our forge, GitHub mirrored.** Do not build a VCS. Self-host Forgejo as the primary forge with bidirectional push mirroring to the GitHub org imagine-os, Forgejo Actions runners as CI fallback, and a disaster-recovery drill that rebuilds everything with GitHub offline. *Why:* The intent is independence from GitHub, not a new data format; Git + Forgejo delivers that in two days, while a custom VCS would eat the whole budget and break every tool agents rely on.
* **Project management: Linear stays system of record, thin PM module syncs to it.** Linear is the queue through Oct 1 with states Backlog -> Ready for Claude -> In Progress -> In Review -> Needs Justin -> Done. PaperOS ships a PM data model mirroring Linear and a bidirectional sync; boards are rendered by the views engine. Rebuilding Linear is explicitly out of scope for this build. *Why:* The orchestrator needs a stable queue today; a mirrored data model preserves the option to cut over later at low cost.
* **Spec-first: every page has a page.spec.yaml.** Each page declares purpose, logic, access, data, integrations, layout, components, states and edge cases. A validator blocks PRs without specs; codegen scaffolds pages; conformance and permission tests are derived from specs; the canvas UX-flow view is generated from them. *Why:* Specs are the contract between Justin and agents: they let many parallel sessions build consistently and let review be mechanical.
* **Design system: DTCG tokens, Base UI/Radix primitives, Tailwind v4, Storybook.** Tokens in W3C DTCG JSON compile to CSS variables; components built on headless primitives with Tailwind v4; Storybook with a11y and interaction tests is the living doc; runtime theming per tenant. *Why:* Headless primitives give accessibility for free, tokens make per-tenant branding trivial, and Storybook gives the quality pipeline something to screenshot.
* **Quality pipeline: four automated gates before anything reaches Justin.** Gate 1 static (typecheck, Biome, Vitest, build). Gate 2 three Claude reviewer agents (correctness, security, spec-conformance). Gate 3 Playwright screenshots + video replays across a 7-width breakpoint matrix and themes, inspected by a vision agent. Gate 4 edge-case hunter. Weekly release candidates land in Needs Justin with a one-page digest. *Why:* Justin is the only human reviewer; the budget is spent on machines reviewing machines so his queue stays under five items.
* **Agent runtime: Claude Code sessions orchestrated from Linear.** An orchestrator polls Ready for Claude, spawns one Claude Code session per issue in its own git worktree, with the character's .claude/agents definition, skills and MCP allowlist, and moves the issue through states. Every prompt, response and tool call is logged to the prompt-log store. *Why:* Matches how the credits are spent (many parallel sessions) and makes the agent org observable, budgetable and auditable.
* **Business core: Stripe for money movement, our own ledger, payroll via adapters.** Stripe Billing + Connect + Tax for payments; a double-entry ledger in Postgres we own; payroll behind a provider interface with Check or Gusto Embedded as the first adapter. *Why:* Money movement and payroll are regulated and not worth building; the ledger is the one finance primitive every business type shares and must be ours to report on.
* **Libraries: borrow before build, ADR per adoption, license policy in CI.** A Scout character evaluates libraries and whole OSS products against a rubric; every adoption gets an ADR in the decision log; a CI license check blocks disallowed licenses. *Why:* The brief asks to find and factor in libraries; making that a governed, logged process keeps 20 parallel agents from importing 20 different table libraries.
* **Credit stance: 30% of spend on automated review and QA.** Roughly 12% planning/specs, 45% building, 30% automated review/QA, 8% docs/knowledge, 5% research; per-character budgets and a kill switch enforce it. *Why:* Unreviewed agent code is the fastest way to waste the remaining 55%; review spend is what keeps Justin's queue small.

## Phases

* **P0 Foundation** (2026-09-17 to 2026-09-20): Linear pipeline, orchestrator and agent roster live; template monorepo runs on web + desktop; Postgres, Forgejo mirror, auth, tokens, spec schema and CI gates 1-3 exist so parallel sessions can start safely.
* **P1 Core systems** (2026-09-21 to 2026-09-26): Spec builder, design system components, multiplayer, table/views engine, collaboration (comments, canvas, docs, prompt logs), multi-input and permission engine reach usable v1 with conformance tests.
* **P2 Business layer + hardening** (2026-09-27 to 2026-10-01): Payments, ledger, payroll adapter, CRM/growth, migration/import tools ship; load, DR and accessibility drills pass; first release candidate and handbook delivered to Justin.

## Credit budget

* **12%** Planning, specs and ADRs: Every page and system gets a spec before code; specs are what make parallel agent work coherent and reviewable.
* **45%** Building (code, infra, integrations): Seventeen projects and \~200 issues in two weeks; the bulk of tokens go to implementation sessions in worktrees.
* **30%** Automated review and QA: Three reviewer agents, vision screenshot inspection, video replays, edge-case hunting and evals on every PR replace the human review Justin cannot supply.
* **8%** Docs, changelogs, prompt logs and handbooks: Documentation is the memory of the agent org and the onboarding path for every future app.
* **5%** Research and library scouting: Borrow-before-build saves far more than it costs, but research must be time-boxed and ADR-bound.

## Agent roster

* **Atlas** (reports to Justin): Chief Architect and Orchestrator: owns the master plan, decomposes work, dispatches Ready for Claude issues to characters, guards dependencies and budget. Sub-characters: Dispatcher, Decomposer, Merger. Access: linear:admin; forgejo:org-admin; github:imagine-os admin; budget:read-write; prod:read-only.
* **Forge** (reports to Atlas): Platform Engineer: app shell, Tauri targets, data layer, forge/mirroring, hosting and CI infrastructure. Sub-characters: Tauri Smith, Schema Wright, Ops Runner. Access: repo:write (all); vps:deploy; postgres:migrate (staging); secrets:infra.
* **Iris** (reports to Atlas): Design Systems Lead: tokens, components, theming, motion, Storybook and accessibility of the component library. Sub-characters: Token Keeper, Component Crafter, Motion and Input Stylist. Access: repo:write packages/ui; storybook:deploy; design-tokens:write.
* **Quill** (reports to Atlas): Spec and Documentation Lead: page/app specs, docs engine content, changelogs, ADRs and prompt-log curation. Sub-characters: Page Spec Writer, Changelog Scribe, Prompt Logger. Access: repo:write specs/ docs/; notion:read-write; drive:read; linear:comment.
* **Sentinel** (reports to Atlas): Quality Lead: owns the four review gates, reviewer agents, visual and video inspection, edge-case discovery and release digests. Sub-characters: Code Reviewer, Security Auditor, Visual Inspector, Edge Case Hunter. Access: repo:review + request-changes; ci:admin; artifacts:write; linear:comment; no merge rights.
* **Nova** (reports to Atlas): Product Systems Engineer: multiplayer, collaboration surfaces, canvas, tables and views engine, multi-input control. Sub-characters: CRDT Engineer, Views Engineer, Canvas Cartographer. Access: repo:write packages/views packages/collab apps/web; yjs-server:deploy (staging).
* **Ledger** (reports to Atlas): Business Systems Lead: Stripe billing and Connect, double-entry ledger, invoicing, finance reports, payroll adapters. Sub-characters: Payments Integrator, Bookkeeper, Payroll Adapter. Access: stripe:test-mode write; stripe:live read-only; repo:write packages/finance; ledger:post (staging).
* **Beacon** (reports to Atlas): Growth Lead: CRM, outreach sequences, social scheduling, landing pages, attribution and support inbox. Sub-characters: Campaign Composer, CRM Builder, Outreach Sequencer. Access: webflow:write; crm:write; email:send (sandbox until approved); repo:write packages/growth.
* **Scout** (reports to Atlas): Library and Migration Researcher: evaluates libraries and OSS products, maintains the registry, builds importers and business templates. Sub-characters: Library Evaluator, Import Mapper, Template Packager. Access: repo:write docs/registry packages/import; external-apis:read; no prod write.

## Pipeline

Backlog → Ready for Claude → In Progress → In Review → Needs Justin → Done. Justin watches only the Needs Justin column (weekly release candidate, credentials, spend increases, roster changes; kept under five open items).

## Round 2 (2026-09-17, snapshot 2026-09-17T06:53Z)

Round 2 read every spec against the brief, the relation graph and the live workspace, scored each project on coverage, precision, buildability and testability (1-5 each), sent seven agents to deepen the weakest parts, then fixed the eight regressions a second critique found. Full page with the interface map, day-by-day schedule and per-issue index: [https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU](https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU)

| Fact | 03:30Z | now |
|---|---|---|
| Non-archived issues (PAP-13 and up) | 206 | 267 (49 children of 16 split parents, 12 gap issues) |
| `blocks` relations | 284 | 534 (zero cycles, zero milestone date inversions) |
| Ready for Claude | 21 | 25 (none has an open inbound blocker) |
| Needs Justin | 0 | 1 (NJ-1 on PAP-91: upgrade the Linear plan) |
| Issues labelled `Deferred` (v0.2) | 0 | 28 |
| Documents | 1 | 26 |
| Spec sections per issue | 8 | 11 (Interface contract, Test plan, Demo added) |
| Specified issues waiting on the free-plan issue cap | 0 | 156 |
| Milestones re-dated by the Execution Schedule | 0 | 20 of 51 |

**New documents, in reading order**

1. [PaperOS Interface & Data Contracts](https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c): ids, RLS context, `Principal`, `Money`, `FilterTree`, shared data model, event envelope, API conventions, package boundaries, provide/consume matrix.
2. [PaperOS Security & Threat Model](https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c): STRIDE per boundary, agent deny list, secrets, prompt-injection tiers, DR, PCI posture.
3. [PaperOS Execution Schedule](https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795): day-by-day starts 09-17 to 10-01, capacity 8 → 20 → 2 sessions, RC0-RC3, NJ-1..NJ-21, credit burn model, stop-loss.
4. [PaperOS Agent Roster](https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3) and character sheets: [Atlas](https://linear.app/paperos/document/character-sheet-atlas-chief-architect-and-orchestrator-b4725358adc1), [Beacon](https://linear.app/paperos/document/character-sheet-beacon-growth-lead-12b0b4eda18b), [Forge](https://linear.app/paperos/document/character-sheet-forge-platform-engineer-6b19c5679dd0), [Iris](https://linear.app/paperos/document/character-sheet-iris-design-systems-lead-43ca4e29d4a9), [Ledger](https://linear.app/paperos/document/character-sheet-ledger-business-systems-lead-b876b4a0d809), [Nova](https://linear.app/paperos/document/character-sheet-nova-product-systems-engineer-a736fa0dc023), [Quill](https://linear.app/paperos/document/character-sheet-quill-spec-and-documentation-lead-1ba00329d4c8), [Scout](https://linear.app/paperos/document/character-sheet-scout-library-and-migration-researcher-44cef400dbbc), [Sentinel](https://linear.app/paperos/document/character-sheet-sentinel-quality-lead-fc3ada07f9e3).
5. [New App in Ten Minutes: the golden path](https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e): the answer to PAP-5, with its acceptance test.

Pending-issue documents (full specs of the 156 issues Linear refused to create):

* [Round 2 pending issues: tables (24)](https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc)
* [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
* [Round 2 pending issues: growth (13)](https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012)
* [Round 2 pending issues: security (11)](https://linear.app/paperos/document/round-2-pending-issues-security-11-27d8ebfcd8d0)
* [Round 2 pending issues: business-core (11)](https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9)
* [Round 2 pending issues: spec-builder (11)](https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b)
* [Round 2 pending issues: libraries (9)](https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d)
* [Round 2 pending issues: agents (9)](https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d)
* [Round 2 pending issues: pm-linear (9)](https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859)
* [Round 2 pending issues: golden path (8)](https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f)
* [Round 2 pending issues: contracts (4)](https://linear.app/paperos/document/round-2-pending-issues-contracts-4-734961df9c59)

**Project scores, before → after** (coverage + precision + buildability + testability, max 20)

| Project | Before | After | Δ |
|---|---|---|---|
| app-shell | 18 | 18 | ±0 |
| data-layer | 19 | 19 | ±0 |
| forge | 18 | 18 | ±0 |
| identity | 18 | 19 | +1 |
| design-system | 18 | 20 | +2 |
| quality | 16 | 19 | +3 |
| pm-linear | 16 | 16 | ±0 |
| agents | 16 | 17 | +1 |
| spec-builder | 19 | 19 | ±0 |
| collab | 16 | 17 | +1 |
| realtime | 18 | 18 | ±0 |
| input | 16 | 18 | +2 |
| tables | 18 | 18 | ±0 |
| business-core | 16 | 17 | +1 |
| growth | 13 | 16 | +3 |
| migration | 16 | 16 | ±0 |
| libraries | 18 | 19 | +1 |
| **Total** | **289** / 340 | **304** / 340 | **+15** |

Precision is 5 everywhere; the remaining deficit is buildability, mostly caused by the issue cap (NJ-1).

**Eight fixes from the second critique**

1. Milestone date inversions 8 → 0 (three milestone dates moved, PAP-26 re-homed, three edges made soft with matching Dependencies text).
2. Ready-but-blocked 2 → 0; `READY_BUT_BLOCKED` is a validator error in PAP-93.
3. +103 relations so every child inherits its parent's blockers; umbrella rule in PAP-92, PAP-93, PAP-96.
4. `Deferred` label on 28 v0.2 issues, priority 4, claim filter in PAP-96; PAP-235 → PAP-180 and PAP-190 → PAP-192 softened.
5. NJ-1 filed on PAP-91 (Needs Justin) with the create order; Plan B folds four pending specs into PAP-198, PAP-187, PAP-180, PAP-114.
6. Pending documents deduplicated: 10 twins merged, one obsolete issue removed, runtime sandbox rewritten.
7. Read-first path: this section list, `Read first` lines on 9 P0 issues, `Contract source` citations on 29 issues.
8. Promotion rule: PAP-96 promotes Backlog → Ready when every blocker is Done or In Review with a PR (branch-start rule); `BLOCKED_BY_OPEN` is an error.

## Round 4 (2026-09-18, snapshot 2026-09-18T14:58Z)

Justin asked to "make the Linear plan better and better: fill in the plan further, use more features of Linear if possible, get more detailed on sub-features, identify any features you missed." Round 4 benchmarked every project against the brief and the best products in its category (18 per-project digests in `plan/round4/digest/`, one cross-cutting capability map of 167 capabilities), filed the gaps as issues and amendments, created five projects for what no module owned, turned on the Linear features the workspace had left off, re-ran the schedule and chunk model over the expanded graph, then critiqued the result and applied the mechanical fixes. Every Linear mutation is logged in `plan/round4/changes/` (seven files); the prompts and replies are in `docs/prompts/round-4-2026-09-18.md`. Page: [https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU](https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU) (v5), mirrored at https://imagine-os.github.io/linear-builder/.

| Fact | Round 3 end (09-18 morning) | After round 4 (14:58Z) |
|---|---|---|
| Non-archived issues in team PAP | 493 (485 canonical) | 991 (983 canonical: 901 specified, 82 Triage skeletons) |
| Projects / milestones / initiatives | 18 / 54 / 0 | 23 / 69 / 5 |
| Leaves / umbrellas (specified issues) | 445 / 40 | 815 / 86 |
| `blocks` relations | 1,224 | 3,275 (zero cycles, zero milestone or due-date inversions, zero deferred -> scheduled edges) |
| Ready for Claude (none with an open blocker) | 29 | 30 |
| Issues labelled `Deferred` (v0.2, priority 4, no due date) | 49 | 204 |
| Estimates / due dates / cycles | none | 815 leaves estimated (2,214 points; S 2, M 3, L 5), 697 due dates, cycle C1 active with the 30 Ready issues |
| Chunk labels (mix B) | none | Chunk 1..5 on the 601 scheduled leaves (135 / 125 / 136 / 143 / 62) |
| Templates / views / project updates and links | 1 / 6 / 0 | 8 / 18 / 23 updates, 69 links |
| Documents | 27 | 29 (this section as a document, plus "How PaperOS uses Linear") |
| Scheduled leaf work (S 0.5, M 1, L 2 session-days) | about 223 | 504 (see risk FIX-R4-2) |
| Chunk plan, mix B (recommended) | 4 chunks, $7,909 list, $158 to Justin, 37.3 h | 5 chunks, $10,450 list, $209 to Justin, 38.6 h at 16 builders 24/7; v0.2 set +$3,418 / +$68 |
| Chunk plan, mix A (all Fable 5.1) | 5 chunks, $11,166 / $223 | 8 chunks, $18,522 / $370 |

**Linear features turned on** (`docs/linear-features.md`, "How PaperOS uses Linear" in Linear): Fibonacci estimates on every leaf; due dates from the schedule and milestones; one-week cycles (C1 Foundation & core systems, C2 Business layer & hardening, C3 v0.2 stretch) with `cycleIssueAutoAssignStarted`, under the rule that cycles hold in-flight work only and planned timing lives in due dates and Chunk labels; a Triage state where Slack, GitHub and agent-found items land for Atlas; five initiatives (A new app in ten minutes, The agent org runs the build, Product surfaces for every audience, Business-ready for any business, Operate, measure and comply) owning the 23 projects; lead, priority, health, three resource links and a first update on every project; the `Surface` label group made exclusive and a `Chunk` label group; six issue templates and a project template; twelve shared views (Needs Justin, Ready for Claude by project, Umbrellas, Deferred, Blocked, Current cycle, Chunk 1-5, Triage inbox). Features the Basic plan lacks (SLAs, customer requests, insights, asks, team initiatives) carry a named substitute.

**Five new projects** (one contract-publish issue, one keystone model spec and one wire issue each, all depending on the kernel PAP-433 and the shared contracts; 19 issues scheduled for 2026-10-01, 56 deferred to v0.2 at priority 4; project target dates 2026-10-16, content line "v0.1 scope is the first milestone (2026-10-01); the later milestones are v0.2 (deferred)"):

1. **Tenant AI Assistant & Business Agents** (`assistant`, 14 issues): grounded chat with cited answers, retrieval, actions with confirmation, copilots and tenant-configurable business characters behind a `ModelProviderPort`.
2. **Workflows, Approvals, Forms, Documents & E-Signature** (`workflows`, 15): workflow model and run engine, approvals framework (`ApprovalPort`) and My Tasks inbox scheduled; form builder, document templates and e-signature deferred.
3. **Scheduling, Messaging & Customer Engagement** (`engagement`, 15): booking engine and scheduling model on the shared recurrence engine (PAP-908); messaging channels, help center, surveys, memberships and loyalty deferred.
4. **Commerce, Operations & Vertical Packs** (`commerce`, 16): catalog, inventory and the commerce domain model scheduled; orders, POS, purchasing, projects and time, HR shifts, assets, marketplace and the vertical packs deferred.
5. **Platform Operations, Analytics & Compliance** (`platform-ops`, 15): control framework mapping the security issues to SOC 2, GDPR and HIPAA, super-admin console and status page scheduled; product analytics, experiments, abuse controls, compliance evidence and residency deferred.

**Twelve gaps the round closed** (from the digests; the page's Round 4 section lists the issues per gap):

1. Tenant AI assistant: nobody could talk to the product -> project `assistant`.
2. Workflows and approvals: processes stopped at one table and five issues hand-rolled approvals -> project `workflows` (see risk FIX-R4-10).
3. Forms, documents and signatures were invoices only -> form builder, document templates and e-signature in `workflows` (v0.2).
4. Customer engagement: the customer was won and then forgotten -> project `engagement`.
5. Commerce and operations: finance had no operations under it -> project `commerce`.
6. Platform operations and compliance: no console for PaperOS, controls unmapped -> project `platform-ops`.
7. Data layer: no generic entity path, migrations never rehearsed, no lost-device story -> `defineEntity()`, migration safety lint and dry run, cache wipe on sign-out, per-PR databases, tenant sequences.
8. Identity: authorization stopped at roles and rows -> custom roles, resource grants, field permissions, permission propagation, delegated authority, device-flow login.
9. Tables and views: the `records.*` write path was owned by nobody and every DoD pointed at demo pages nobody built -> records write path, view renderer registry, demo pages and seed, export, conditional formatting, system fields.
10. Quality and forge: gate DoDs rehearsed against a sandbox nobody created; no merge queue, no review fix loop -> gate sandbox and defect catalogue, review fix loop, migration gate, merge automation, dependent branches.
11. Agent org and pipeline: P0 security issues each hid two sessions; cold sessions read 150 KB; Linear's planning features unused -> security issues split, character identity card, context packs under 8k tokens, plugin packaging, session-end guard hooks, every Linear feature above.
12. Small shared engines owned by nobody -> recurrence engine PAP-908, CDN and edge cache PAP-909, SMS channel PAP-910, labels and barcodes PAP-911, settings registry PAP-912, OAuth provider apps PAP-913; FX rates, bank feeds, scheduled view delivery, address field, file scanning and bulk campaigns folded into their existing issues (PAP-766, PAP-770, PAP-639, PAP-622, PAP-574, PAP-799).

**Project scores, round 2 after -> round 4 after** (coverage + precision + buildability + testability, max 20): app-shell 18 -> 17, data-layer 19 -> 19, forge 18 -> 18, identity 19 -> 19, design-system 20 -> 20, quality 19 -> 19, pm-linear 16 -> 18, agents 17 -> 19, spec-builder 19 -> 19, collab 17 -> 19, realtime 18 -> 19, input 18 -> 18, tables 18 -> 19, business-core 17 -> 18, growth 16 -> 18, migration 16 -> 18, libraries 19 -> 20: **304 -> 317 of 340** over the 17 projects scored in round 2; module-system 18 and the five new projects 16, 16, 16, 15, 16 bring the total to **414 of 460 over 23 projects**. Coverage is 5 everywhere; the deficit is buildability (capacity) and the precision of the new projects' contract shapes, which are not yet in the Contracts document. Full critique with the check tables: `plan/round4/critique.md`.

**Critique fixes applied** (`plan/round4/changes/critique-fixes.json`, `final-fixes.json`): 443 descriptions had their `r4/<project>/<key>` file keys replaced with identifiers; 52 hard dependencies named in text but missing from the graph were created (4 kept soft with a note); two children moved to their parent's milestone; the 19 single-child umbrellas created that day were unwound (child de-parented, `parent blocks child`, labels and estimate restored) so PAP-434, PAP-441, PAP-26, PAP-47, PAP-48 and fourteen more are claimable leaves again; 156 last-child edges give every umbrella's dependents a real gate (rule sentence in PAP-92 and PAP-96); PAP-754 promoted; the five new projects re-dated. All integrity checks are 0 after the fixes.

**Open risks from the critique** (briefs in `plan/round4/critique.md` section 4):

* **FIX-R4-2, capacity.** The 601 scheduled leaves sum to 504 session-days against about 208 of capacity (16 builders, 13 days); 119 session-days are due on 09-30. Either the schedule model moves 250-300 session-days of P2 work to `Deferred` before promotion starts, or the calendar is not honest. The chunk model's 38.6 h assumes 24/7 builders and the branch-start rule.
* **FIX-R4-7, Triage.** 82 Triage skeletons carry a Goal and a Source only; Atlas should accept, fold or decline each before 09-22 and record the decisions in `plan/round4/unfiled-suggestions.md`.
* **FIX-R4-10, approvals.** The approvals framework (PAP-849) exists, but the five issues that hand-roll an approval step (expense approval, deal stage approval, import commit approval, PAP-192, PAP-94) have not been amended to consume `ApprovalPort`, so the platform would ship six approval implementations.

## Documents (read in this order)

Updated 2026-09-17 (round 2). Every Claude Code session reads these in this order before writing code; the session playbook (PAP-92) repeats the list and the orchestrator prompt (PAP-96, PAP-104) links it. Documents hold the decisions; issue bodies say what to build. If an issue body and a document disagree, the document wins and the difference is filed as an ADR (PAP-130) with a comment on the owning issue.

1. **This Blueprint** ([link](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>)): vision, key decisions, phases, credit budget, agent roster, pipeline.
2. [PaperOS Interface & Data Contracts](https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c): ids and RLS session variables, `Principal` and `ActorRef`, `Money`, `FilterTree`, the shared data model, the event envelope and topic catalogue, API conventions (paths, headers, errors, idempotency), monorepo package boundaries, and the provide/consume matrix per issue. Owned by Data Layer (Forge, reviewed by Sentinel).
3. **Your project's** `Contract` **section**: the Linear project content of the project your issue belongs to lists what each issue provides and consumes; read it after the Contracts document and before your issue's Interface contract.
4. [**PaperOS Agent Roster**](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>) and your **character sheet**: org chart, routing (who picks up which issue), shared rules every session obeys, escalation matrix. Character sheets: [Atlas](<https://linear.app/paperos/document/character-sheet-atlas-chief-architect-and-orchestrator-b4725358adc1>) (Chief Architect and Orchestrator), [Forge](<https://linear.app/paperos/document/character-sheet-forge-platform-engineer-6b19c5679dd0>) (Platform Engineer), [Iris](<https://linear.app/paperos/document/character-sheet-iris-design-systems-lead-43ca4e29d4a9>) (Design Systems Lead), [Quill](<https://linear.app/paperos/document/character-sheet-quill-spec-and-documentation-lead-1ba00329d4c8>) (Spec and Documentation Lead), [Sentinel](<https://linear.app/paperos/document/character-sheet-sentinel-quality-lead-fc3ada07f9e3>) (Quality Lead), [Nova](<https://linear.app/paperos/document/character-sheet-nova-product-systems-engineer-a736fa0dc023>) (Product Systems Engineer), [Ledger](<https://linear.app/paperos/document/character-sheet-ledger-business-systems-lead-b876b4a0d809>) (Business Systems Lead), [Beacon](<https://linear.app/paperos/document/character-sheet-beacon-growth-lead-12b0b4eda18b>) (Growth Lead), [Scout](<https://linear.app/paperos/document/character-sheet-scout-library-and-migration-researcher-44cef400dbbc>) (Library and Migration Researcher).
5. [PaperOS Security & Threat Model](https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c): STRIDE per trust boundary, destructive-action deny list for agents, secrets handling, prompt-injection tiers T0-T4, backup and DR, compliance posture, gap register. Mandatory for identity, quality, agents, infra, business-core and any issue that touches secrets, payments or personal data; PAP-219 turns it into `controls.yaml`.
6. [PaperOS Execution Schedule](https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795): scheduling rules including the branch-start rule, day-by-day claims 09-17 to 10-01, capacity curve, RC0-RC3 checkpoints, numbered Needs Justin items, credit burn model and stop-loss. Find your issue's start half-day before claiming.
7. [New App in Ten Minutes: the golden path](https://linear.app/paperos/document/new-app-in-ten-minutes-the-golden-path-0f49429f566e): the end-to-end experience the platform exists for (the answer to PAP-5): what `paperos create` asks, generates and deploys, and the acceptance test. Read it if your issue is in app-shell, spec-builder, forge, design-system or touches the CLI.

**Waiting on the issue cap.** Linear refused about 165 `issueCreate` calls on 2026-09-17 (`USAGE_LIMIT_EXCEEDED`, free plan). Their full specs live in these documents and are created in the order given on PAP-91 (Needs Justin NJ-1) once the plan is upgraded; until then a live issue that cites a bracketed key such as `[agents/runtime-sandbox]` means "see the pending document for that project", and umbrella issues carry their work packages inline. Four pending specs were folded into live issues instead (test accounts into PAP-198, consent centre into PAP-187, recurring dunning into PAP-180, spec versioning into PAP-114); their documents say so at the entry.

* [Round 2 pending issues: contracts (4)](https://linear.app/paperos/document/round-2-pending-issues-contracts-4-734961df9c59) (Data Layer & Database): shared value types (`Money`, `ActorRef`, `EntityRef`, cursors), domain event contract and outbox, idempotency and rate limiting, package boundary map (issues A-D of Contracts §6).
* [Round 2 pending issues: security (11)](https://linear.app/paperos/document/round-2-pending-issues-security-11-27d8ebfcd8d0) (Quality Pipeline): agent deny list, prompt-injection defences, credential broker, field encryption, platform DR drill, retention and PII, security telemetry, DAST, founder break-glass, supply chain, PCI SAQ-A posture (Threat Model §9).
* [Round 2 pending issues: golden path (8)](https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f) (Universal App Shell & Repo Template): app interview, entity pages, generation pipeline, starter surfaces, `paperos create` driver, provisioning, acceptance test, template upgrade (Golden Path §8).
* [Round 2 pending issues: pm-linear (9)](https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859) (Project Management & Claude Pipeline): workspace reconcile (merged into PAP-91), weekly plan re-audit, inbound triage, the three PAP-96 orchestrator children, the three PAP-101 Linear-sync children.
* [Round 2 pending issues: agents (9)](https://linear.app/paperos/document/round-2-pending-issues-agents-9-85624b15630d) (Agent Characters & Orgs): runtime sandbox, session observability, the four PAP-104 roster children, the three eval-harness children.
* [Round 2 pending issues: spec-builder (11)](https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b) (Spec Builder): spec i18n, spec versioning (folded into PAP-114), children of PAP-119 data section, PAP-120 layout codegen and PAP-124 spec editor.
* [Round 2 pending issues: tables (24)](https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc) (Table & Views Engine): custom dataset schema editor, record-level features, bulk ops and trash, and 21 children of the compiler, field types, grid, calendar/timeline/gantt, formulas, dashboards and automations.
* [Round 2 pending issues: business-core (11)](https://linear.app/paperos/document/round-2-pending-issues-business-core-11-7c8c2526b3c9) (Business Core: Payments, Finance & Payroll): usage metering, recurring invoices and dunning (folded into PAP-180), and 9 children of the ledger, invoicing and payroll umbrellas.
* [Round 2 pending issues: growth (13)](https://linear.app/paperos/document/round-2-pending-issues-growth-13-3fd4406e8012) (Growth: Marketing, Outreach & CRM): consent and marketing compliance centre (folded into PAP-187), and 12 children of social scheduling, outreach, referrals and support inbox.
* [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6) (Migration & Import Tools): importer test accounts (folded into PAP-198), Monday and HubSpot CSV recipes, and 18 children of the import engine, Airtable, Notion, export, Stripe, QuickBooks/Xero and template packs.
* [Round 2 pending issues: libraries (9)](https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d) (Library Discovery & Integration): table, chart, map, canvas and editor spikes with ADRs; jobs, email, PDF, search, observability, flags and storage decisions; OSS product spikes (NocoDB, Baserow, Plane, Twenty, Chatwoot, Listmonk, Postiz, [Cal.com](<http://Cal.com>), Formbricks).

Risks and the full per-issue index are on the blueprint page: [https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU](<https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU>)