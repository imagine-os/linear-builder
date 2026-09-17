# PaperOS plan audit (round 2)

Snapshot: `round2/linear-snapshot.json`, taken 2026-09-17T03:30Z. Team PAP: 214 non-archived issues (206 canonical PAP-13..PAP-218, PAP-5 origin, PAP-6..12 Duplicate strays), 17 projects, 51 milestones, 284 `blocks` relations, 9 workflow states, 19 labels, 1 document. States: Backlog 186, Ready for Claude 21, Duplicate 7. Phases: P0 75, P1 79, P2 59 (label counts include duplicates). Sizes from spec text: S 27, M 127, L 52.

Method: every one of the 206 descriptions was read in full (Goal, Scope, Spec, DoD, Edge cases, Dependencies, Agent, Size), then compared with plan.json, the relation graph, milestone dates and the live workspace configuration. All 206 specs have all eight sections, 5-8 DoD bullets and 5-7 edge cases; weakness below therefore means contradiction with reality, unbuildable prerequisites, wrong phase or wrong size, not missing sections.

## 1. Project scores (1-5)

| Project | Coverage | Precision | Buildability | Testability | Total | Reasoning |
|---|---|---|---|---|---|---|
| app-shell | 5 | 5 | 4 | 4 | 18/20 | Brief fully covered after round-1 gap fixes (infra bootstrap, deploy, i18n, modules, drill); specs name files and versions; Tauri mobile/macOS signing and iOS CI runners depend on external accounts nobody has asked for; DoD is screenshot- and command-verifiable except the device recordings. |
| data-layer | 5 | 5 | 4 | 5 | 19/20 | Postgres/Drizzle/RLS/sync/files/search/audit/jobs all owned with exact table shapes; buildability drops one point because the local stack, dev stack and VPS chain (13→42→32→33) is serial and the sync ADR gates PAP-36; every DoD has a test or bench with numbers. |
| forge | 4 | 5 | 4 | 5 | 18/20 | Forgejo, mirroring, bots, runners, DR and release automation are precise and each has a proof step; missing a template-upgrade path for generated apps and non-Linux runners; GitHub App install and Hetzner need Justin once. |
| identity | 4 | 5 | 4 | 5 | 18/20 | Auth, tenancy, RBAC/ABAC, agents-as-principals, impersonation, shells and SSO are precise with property tests; no threat model, no per-user privacy (DSAR/erasure), no first-run onboarding, no session/MFA recovery UI; SSO/SCIM (L) is unlikely to ship by 10-01. |
| design-system | 4 | 5 | 5 | 4 | 18/20 | Tokens, primitives, layout, data display, theming, mapping are exact down to CSS variable names; date pickers and the state components codegen emits (ErrorState, OfflineBanner, DeniedState) have no owner; manual screen-reader audit in PAP-73 is not verifiable by an agent. |
| quality | 5 | 4 | 3 | 4 | 16/20 | Four gates, perf, security, flake quarantine, release train and digest cover the brief; artifact JSON contracts are defined in six different issues; gates 2-4 need the Agent SDK, LFS, 4-way sharding and Playwright Docker on runners, and Gate 3 (P0) silently depends on test-mode seeding from PAP-86 (P1). |
| pm-linear | 4 | 4 | 4 | 4 | 16/20 | Queue, orchestrator, webhooks, metering, concurrency, PM mirror are all here; PAP-91/93/95 describe a Linear configuration that no longer matches the live workspace (no Character group, Todo kept, estimates off, Surface ungrouped), so the contract validator as written would bounce every existing issue. |
| agents | 5 | 4 | 3 | 4 | 16/20 | Schema, roster, skills, scopes, logging, handoffs, memory, evals, cost controls and org chart are a complete org design; roster-v1 packs 37 characters and prompts into one L issue; least-privilege relies on Forgejo bots (PAP-48) and on a Docker sandbox no issue builds; eval scoring is measurable. |
| spec-builder | 5 | 5 | 4 | 5 | 19/20 | Schema, validator, access/data/integrations sections, codegen, conformance, canvas graph, editor, docs and business profile form a closed loop with fixtures and drift checks; the shared filter grammar is copied 'with a TODO' rather than owned; spec copy has no i18n path. |
| collab | 4 | 4 | 4 | 4 | 16/20 | Docs engine, prompt log, ADRs, comments, canvas, changelog, rules registry, search are precise; notifications sit in P2 behind comments although the Justin queue (P0), release train and comment mentions need them; no runtime (non-repo) docs store despite PAP-203 assuming one. |
| realtime | 5 | 5 | 4 | 4 | 18/20 | Hocuspocus, presence, editor, record sync, conflict UX, multi-window, agent presence, load test, offline queue and follow mode cover multiplayer end to end with lag budgets; yjs-server (P0) needs Better Auth and the permission engine first, which the relations do not fully encode; load-test DoD needs a second generator host. |
| input | 5 | 5 | 3 | 3 | 16/20 | Command registry, abstraction, focus, keymaps, gestures, dnd, screen reader, pen, gamepad, voice, a11y statement are exhaustive; PAP-156 needs Windows/NVDA and macOS/VoiceOver runners that nothing provisions; PAP-159 adds a Python Whisper service against the TypeScript-only decision; device-dependent DoDs cannot be verified by a cold session. |
| tables | 5 | 5 | 4 | 4 | 18/20 | View model, compiler, 17 field types, all view kinds, formulas, sharing, dashboards, automations are the strongest specs in the plan with SQL-level detail and benches; custom-table creation UX, record detail/history/trash and the shared filter grammar are unowned; grid (P1, 09-23) is blocked by data-display (09-25). |
| business-core | 4 | 5 | 3 | 4 | 16/20 | Finance model, Stripe Billing/Connect/Tax, ledger with hash chain, invoicing, reports, payroll adapter, expenses and cash dashboard are precise to the column; usage metering, dunning/recurring tenant invoices are missing; Stripe live keys, payroll sandbox agreements and Connect KYC need Justin and calendar time; ledger tests are exact. |
| growth | 4 | 4 | 2 | 3 | 13/20 | CRM, social, outreach, content agent, landing pages, attribution, segments, referrals, support inbox map to the brief; five social platforms need OAuth app reviews measured in weeks, Twilio/Resend/Webflow accounts and a Webflow site do not exist, and several integration DoDs require live sends; referral program (L, prio 4) should be cut. |
| migration | 4 | 5 | 3 | 4 | 16/20 | Framework, ID mapping, CSV/Airtable/Notion/ClickUp/Linear/Stripe/QuickBooks importers, export, templates and the migration agent are precise with fixture counts; every integration DoD assumes real test workspaces (Airtable base, Notion workspace, QuickBooks sandbox, Xero demo) that no issue provisions; Monday/HubSpot have sheets but no importer. |
| libraries | 5 | 4 | 5 | 4 | 18/20 | Rubric, MCP catalog, license policy, three landscape surveys, OSS product evaluation, registry, Renovate and Scout make borrow-before-build a process; three research issues are L with 1.5-2 agent-day time boxes that are easy to overrun; the registry drift check is verifiable, ADR 'acceptance' less so. |

Lowest totals: growth (13), input (16), pm-linear (16), quality (16), agents (16), collab (16), business-core (16), migration (16). Highest: data-layer, spec-builder (19).

## 2. The 15 weakest issues

1. **PAP-91** (P0 Infra S, pm-linear) — Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project   
   Specifies a Linear configuration that the round-1 import already delivered differently: `Todo` was kept and `Ready for Claude` created beside it, Surface labels are ungrouped (Linear enforces one child per group), there is no `Character` label group, `issueEstimationType` is `notUsed`. As written a cold session would 'fix' the live workspace and break the 206 issues that already exist. Needs a rewrite as a reconcile script against the snapshot.

2. **PAP-93** (P0 Spec M, pm-linear) — Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) e  
   The contract requires exactly one Surface label (53 issues legitimately carry two or three), a Character label (none exist), a Linear estimate (Size lives in the description) and a spec-file link for Build issues (none have one yet). The webhook validator would bounce every issue moved to Ready for Claude, including the 21 already there. Metadata rules must be aligned with PAP-91's real outcome before either is built.

3. **PAP-95** (P0 Docs S, pm-linear) — Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and clos  
   Contradicts PAP-29: PAP-95 closes PAP-5 as Done and creates a new 'Startup benchmark' child, PAP-29 keeps PAP-5 as the standing scoreboard and runs the same benchmark weekly. '17 `related` relations to each project's first milestone issue' is undefined (milestones are not issues). One of the two must own PAP-5's closure.

4. **PAP-104** (P0 Build L, agents) — Write the nine lead characters and their sub-characters as .claude/agents definitions with  
   37 character YAMLs plus 37 system prompts of 300-800 words plus smoke tasks per lead plus a classification test, in one L issue that blocks nine others. A cold session will run out of context before the smoke tasks. It also invents a `fallbackModel: claude-opus-5` and cites 'Fable 5.1 guidance' nobody wrote down. Split into schema-to-YAML conversion, lead prompts, sub prompts, build/smoke.

5. **PAP-73** (P1 Review M, design-system) — Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA  
   DoD requires NVDA, VoiceOver and TalkBack columns 'filled' with recorded sessions; an agent on a Linux VPS cannot run any of the three, and the spec's fallback ('accessibility tree dumps as proxy') is not the same thing. Overlaps PAP-156 (which at least specifies guidepup drivers). Recast as automated axe + ARIA snapshot audit and hand manual AT to PAP-156.

6. **PAP-156** (P1 Review M, input) — Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows  
   Requires a self-hosted Windows runner with NVDA and a hosted macOS runner with VoiceOver; PAP-50 provisions Linux docker runners only and nothing else creates these machines or pays for them. 'Three nights green' cannot start until they exist. Needs an infra prerequisite issue (see gaps: forge runners).

7. **PAP-20** (P1 Build L, app-shell) — Add Tauri 2 mobile targets (iOS, Android) with platform capability shims  
   'Debug APK and iOS simulator build succeed in CI on the PR' requires a macOS runner and Xcode; iOS device recordings need an Apple Developer account that no Needs Justin item requests. Android is achievable on Linux; iOS is not on this infrastructure. Split iOS out and file the credential ask.

8. **PAP-159** (P2 Build M, input) — Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through t  
   Adds `apps/voice-server` in Python (`faster-whisper`) against the TypeScript-monorepo decision, on the same 8 GB VPS whose service RAM budget PAP-214 caps at 6 GB, with a sub-800 ms CPU latency target that small.en will not meet on a cpx31. P2 prio 2 for a feature the brief mentions once. Make Web Speech the only backend for this build and record Whisper as a reopen criterion.

9. **PAP-190** (P2 Build L, growth) — Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, YouTube) and  
   Five platform adapters (X, LinkedIn, Instagram, TikTok, YouTube) each need a developer app and, for three of them, a review that takes weeks; the DoD requires a live publish on X and LinkedIn. The spec itself admits 'app reviews pending'. Reduce to the queue, calendar, state machine and one mock adapter plus X; file the app applications on day one as a Needs Justin item.

10. **PAP-136** (P2 Build L, collab) — Build a notification center (in-app, email, Slack) with per-audience preferences  
   Phase P2, blocked by comments (PAP-131), yet `issue.needs_justin`, `review.gate_failed` and `release.candidate` kinds are what PAP-94 (P0), PAP-88 and PAP-89 (P1) deliver through. The dependency points the wrong way: notification delivery needs jobs-queue, not comments. Split core (P1) from inbox UI and Slack (P2).

11. **PAP-82** (P0 Build L, quality) — Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes  
   P0 Gate 3 whose fixtures log in 'with a seeded test user per audience' and seed data via `/__test/seed`, both defined by PAP-86 (P1, blocked by PAP-58). Baselines need Git LFS on both forges and a 4-shard runner pool that PAP-50 does not size for. The gate can render Storybook stories in P0 but not authenticated pages; the spec does not say so.

12. **PAP-88** (P1 Spec L, quality) — Define the release train: nightly staging deploy, weekly release candidate to Needs Justin  
   Typed `Spec` but sized L and builds three workflows plus a certify script; the DoD's rehearsal needs `/approve` 'in a test tenant of Linear' (Linear has no sandbox teams here) and the Coolify deployment API, and it re-specifies the reply grammar PAP-94 owns. Convert to Build, depend on PAP-94 for the grammar, and rehearse against PAP with a `rehearsal` label.

13. **PAP-196** (P2 Build L, growth) — Implement a referral and affiliate program with Stripe Connect payouts  
   Referral and affiliate program: L, priority 4, P2, hard-blocked by Stripe Connect which is itself P2; adds fraud rules, tax-form status and cash payouts. Lowest value-to-cost issue in the plan; recommend Canceled-after-deadline scope, not a build target before 10-01.

14. **PAP-65** (P2 Build L, identity) — Add SAML/OIDC SSO and SCIM provisioning for enterprise tenants  
   SAML + OIDC SSO + a full SCIM 2.0 server + domain verification + enforcement, L, P2, prio 3, for enterprise tenants that do not exist yet. Buildable but not in the window; its DoD (Okta and Entra guides, mock IdPs) is a week of work on its own. Defer or split to 'OIDC SSO only'.

15. **PAP-54** (P2 Build L, forge) — Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API  
   In-app repo browsing with seven page specs and routes, L, prio 3, duplicating Forgejo's own UI one click away; depends on rbac, api-layer, spec validator and conformance tests. Low value for the deadline; keep as P2 stretch or reduce to 'commit and PR links from Linear issues'.

## 3. Structural gaps

### 3a. Interfaces between projects that no issue specifies

- Interface: no domain event bus. PAP-28 requires cross-module coupling only via `emit('invoice.paid')` in `packages/core/events`; PAP-136 kinds, PAP-174 triggers, PAP-195 segment events, PAP-177/181 webhooks and PAP-97 all need one; only the orchestrator has an in-process emitter. Owner: data-layer (new Spec issue).
- Interface: three filter/condition grammars. PAP-59 `Condition`, PAP-161 `FilterGroup`, PAP-119 copies the view filter 'with a TODO'; PAP-166, PAP-195 and PAP-174 extend it. No canonical package. Owner: data-layer (Spec, P0) consumed by tables, identity, spec-builder, growth.
- Interface: gate artifact JSON contracts (gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs, screenshot paths) are defined separately in PAP-78, 80, 82, 83, 84, 85, 89, 97 and 137; PAP-97 asks for a shared `packages/contracts` that no issue creates. Owner: quality (Spec, P0).
- Interface: codegen emits `ui.errorState`, `ui.offlineBanner`, `ui.integrationUnavailable`, `ui.dataTable`, `ui.dashboardBlocks` (PAP-120, 121, 125) but design-system ships EmptyState only (PAP-71); OfflineBanner lives in `packages/core/pwa` (PAP-18). Owner: design-system.
- Interface: `Money` is `{ amountMinor: number }` in PAP-71/164 and `{ amountMinor: bigint }` in PAP-175; PAP-187 uses `amount_cents bigint`. Pick one runtime type in `packages/core` and one JSON wire encoding (string) before PAP-164 and PAP-175 both land.
- Interface: `Principal`/actor shape differs between PAP-55 (`Principal` in packages/core), PAP-35 context (`{id, kind, tenantId, roles[]}`), PAP-59 and PAP-60 (`principalType` on users). PAP-55 should be declared the canonical type and PAP-35 should import it.
- Interface: server-side secret encryption is assumed by PAP-190, PAP-65, PAP-174, PAP-193 and PAP-199 ('encrypted via app-shell/env-config helpers') but PAP-17 only defines client keychains. Owner: data-layer (new Build issue).
- Interface: idempotency and rate limiting. PAP-148 expects an `idempotency_keys` middleware and `/api/rpc/batch` in api-layer; PAP-35 offers an in-memory token bucket and a 24 h idempotency header without a table; PAP-172/193/194 hand-roll per-IP limits. Owner: data-layer.
- Interface: test-mode seeding. PAP-82 (P0), PAP-85 and PAP-87 seed via `/__test/seed` and log in with per-audience test users; both are defined by PAP-86 (P1, blocked by PAP-58). Owner: quality (pull into a P0 issue).
- Interface: transactional email. PAP-57, 58, 136, 180, 191 each call Resend directly; sandbox/allowlist mode exists only in PAP-191; PAP-214 chooses the provider but no package wraps it. Owner: data-layer.
- Interface: `packages/core` is created empty by PAP-13 and written to by 12 issues across six projects (shell, config, pwa, windows, devices, audience, nav, flags, modules, native, pm schema). PAP-100 puts the PM Drizzle schema in `packages/core/src/pm`; it belongs in its own package. Declare a `packages/core` index owner (app-shell) and move PM to `packages/pm`.
- Interface: heartbeat and status. PAP-102 (15-minute heartbeat timeout), PAP-113 (`agents.status` shape) and PAP-96 (`/status`) assume a session status contract nobody specifies. Owner: agents.

### 3b. Cross-cutting concerns

- Cross-cutting missing: security threat model and hardening baseline (identity, P0 Spec); agent runtime sandbox (agents, P0 Infra); runtime feature flags (app-shell); notification core in P1 (collab); onboarding wizard for the customer half of PAP-5 (app-shell); object-storage backup and platform DR drill (data-layer); tenant purge and quotas (data-layer); privacy DSAR and legal pages (identity); tenant API keys, outbound webhooks and SDK (identity); custom domains for white-label (app-shell); usage metering (business-core); consent centre (growth); date pickers (design-system); custom table editor, record detail and trash (tables); template upgrade path and non-Linux runners (forge); importer test accounts (migration); email/PDF theme (design-system); push transport (realtime); runtime docs store and in-app help (collab); spec i18n and versioning (spec-builder); API perf budgets and Gate 2 calibration (quality); workspace reconcile, weekly re-audit and inbound triage (pm-linear).
- Cross-cutting adequately covered: i18n/l10n (PAP-27, PAP-126), offline (PAP-18, 36, 148), web performance budgets (PAP-87), search (PAP-39, 138), file storage (PAP-37), observability (PAP-40), backups for Postgres and forge (PAP-30, 45, 53), plugin/module system (PAP-28), analytics for acquisition (PAP-194), plans and entitlements (PAP-177, 178), compliance flags declared (PAP-126) but not enforced.

### 3c. Proposed new issues by project (44 total; full objects in `gaps.json`)

| Project | Phase | Type | Prio | Title | Why |
|---|---|---|---|---|---|
| app-shell | P1 | Build | 2 | Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards | PAP-17 only reads flags from env; PAP-88 assumes risky work lands behind flags; PAP-195 wants in-app targeting; PAP-214 decides a flag service but nothing builds it. |
| app-shell | P1 | Build | 1 | Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard | PAP-58 redirects new users to `/org/new` and PAP-33 says 'UI handles onboarding' but no issue owns the flow; templates (PAP-207) and billing (PAP-177) have no entry point. |
| app-shell | P1 | Build | 2 | Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability | PAP-17 declares `VITE_SENTRY_DSN`, PAP-40 traces server errors, every spec has an error state, but nobody owns client error reporting or Rust panic capture. |
| app-shell | P1 | Infra | 2 | Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask | PAP-19 leaves notarisation as a TODO, PAP-20 needs an Apple account, PAP-29 will record unsigned builds as friction; no issue files the credential request. |
| app-shell | P2 | Build | 3 | Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI | PAP-178 sells a `whiteLabel` entitlement and PAP-35 resolves tenants by subdomain, but nothing provisions custom domains or certificates. |
| data-layer | P1 | Spec | 1 | Specify and build the domain event catalogue, transactional outbox and subscriber registry (`packages/core/events`) | PAP-28 mandates cross-module coupling only via events; PAP-136 kinds, PAP-174 triggers, PAP-195 enter/exit events and PAP-177 webhooks all need a bus; only PAP-97 has one, inside the orchestrator. |
| data-layer | P0 | Spec | 1 | Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators | PAP-59, PAP-161, PAP-119 (copied 'with a TODO'), PAP-166, PAP-195 and PAP-174 each define or import a filter tree; nobody owns the canonical one. |
| data-layer | P1 | Build | 1 | Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev | PAP-57, PAP-58, PAP-136, PAP-180 and PAP-191 each wire Resend independently; only PAP-191 defines sandbox mode; PAP-214 picks the provider but ships no package. |
| data-layer | P1 | Build | 1 | Build server-side field encryption for stored secrets (OAuth tokens, SCIM tokens, webhook secrets, connector auth) with key rotation | PAP-190, PAP-65, PAP-174, PAP-199 and PAP-193 all say 'encrypted via app-shell/env-config helpers', which PAP-17 does not provide (it covers client keychains only). |
| data-layer | P1 | Build | 2 | Build shared rate limiting and idempotency middleware backed by Postgres (per actor, per API key, per IP for public routes) | PAP-35 uses an in-memory bucket 'Redis later'; PAP-148 expects an idempotency table in api-layer that PAP-35 does not include; PAP-172, PAP-193 and PAP-194 each hand-roll limits. |
| data-layer | P1 | Infra | 2 | Add object-storage backups and a platform-wide disaster-recovery drill (Postgres + MinIO + Yjs + orchestrator state restored on a fresh host) | PAP-30 covers Postgres PITR and PAP-53 covers the forge; tenant files in MinIO and the orchestrator database have no backup and no issue restores the whole platform. |
| data-layer | P2 | Build | 2 | Build the tenant lifecycle jobs: hard-delete purge after grace period (export first), archive schema for legal retention, per-tenant storage and row quotas | PAP-33 says 'hard purge is a separate job', PAP-205 is its precondition, PAP-178 needs a storage counter; no owner. |
| data-layer | P2 | Build | 3 | Enforce data retention and PII policy: retention per table, scheduled anonymisation jobs, `pii.json` driving audit redaction and OTel filters | PAP-41 generates PII flags and PAP-38 keeps 24 months of audit, but nothing enforces retention or anonymisation; PAP-126 compliance flags have no consumer. |
| identity | P0 | Spec | 1 | Write the security threat model and hardening baseline: STRIDE per trust boundary, CSP and security headers, CSRF, secret rotation runbook, incident response playbook | Round-1 critique risk 3 calls the orchestrator a total-compromise point; PAP-80/81/106 scan, review and scope but nothing states the model, headers or incident process. |
| identity | P1 | Build | 2 | Build session and device management: list and revoke sessions, TOTP fallback for passkeys, account recovery codes | PAP-62 mentions a security page and PAP-57 is passkey-first, but neither specifies recovery, MFA fallback or session revocation. |
| identity | P2 | Build | 2 | Build privacy tooling: per-user data export and erasure (DSAR), consent records, privacy/terms/cookie pages in the portal | PAP-205 exports a whole tenant; per-user erasure, consent capture for portal users and the legal pages the brief's 'every business' will need are unowned. |
| identity | P2 | Build | 2 | Build tenant API keys and outbound webhooks for developers: scoped keys, per-key limits, signed webhook deliveries with retries, developer settings page and generated TypeScript SDK | PAP-35 serves OpenAPI at /api/v1 and PAP-60 issues agent keys only; the brief's developer audience has no key issuance, webhooks or SDK. |
| design-system | P1 | Build | 1 | Build date, time, date-range and calendar pickers plus form-state adapters (react-hook-form Field, arrays, async validation) | PAP-67 lists date pickers as out of scope, PAP-164 requires `DatePicker` from primitives, PAP-166 needs relative-date pickers, PAP-212 names React Aria as fallback; no owner. |
| design-system | P1 | Build | 1 | Build the state components codegen emits: ErrorState, DeniedState, OfflineBanner, IntegrationUnavailable, LoadingPage as spec-mapped `ui.*` components | PAP-120 and PAP-121 reference `ui.errorState`, `ui.offlineBanner`, `ui.integrationUnavailable`; PAP-71 ships EmptyState only and PAP-18 puts OfflineBanner in packages/core. |
| design-system | P2 | Build | 3 | Build the email and PDF rendering theme: `brandingToInlineCss`, print stylesheet and a template kit shared by invoices, receipts, digests and the ACR export | PAP-75 mentions the helper 'for later business-core use'; PAP-180 PDFs, PAP-89 HTML digest and PAP-160 ACR PDF each need it and none owns it. |
| quality | P0 | Spec | 1 | Specify the gate artifact contract: one schema package for gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs and artifact paths | PAP-97 says to 'coordinate names via a shared packages/contracts'; PAP-78, 80, 82, 83, 84, 85, 89 and 137 each define their own JSON shape today. |
| quality | P0 | Build | 1 | Build test-mode seed and reset endpoints (`/__test/seed`, `/__test/reset`) with deterministic fixtures per audience, before Gate 3 | PAP-82 (P0) and PAP-85 depend on seeding and per-audience logins that PAP-86 (P1, blocked by PAP-58) defines; the gate cannot screenshot authenticated pages without it. |
| quality | P1 | Review | 1 | Run Gate 2 calibration and false-negative tracking: weekly manual spot check of five verdicts, precision and recall trend, reviewer prompt tuning loop | Round-1 critique risk 4: automated review replaces human review but its miss rate is never measured after launch; PAP-110 evals agents, not reviewer misses on real PRs. |
| quality | P1 | Infra | 3 | Enforce API and database performance budgets: k6 smoke per release candidate, p95 per procedure, slow-query gate, `apps/api` image size | PAP-87 is web-only and PAP-40 has one k6 script for dashboards; no gate fails on API regressions. |
| pm-linear | P0 | Infra | 1 | Reconcile the live Linear workspace with the round-1 import: Character label group, `Files:` scope lines, estimates vs Size, Surface multi-label rule; align PAP-91 and PAP-93 to it | PAP-91/93 describe a configuration that differs from the live team (Todo kept, Surface ungrouped, no Character labels, estimation notUsed); the validator as specified would bounce all 206 issues. |
| pm-linear | P1 | Review | 2 | Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear | With up to 20 sessions creating relations and issues daily, the structure will drift; only a one-off audit exists. |
| pm-linear | P1 | Build | 2 | Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view | PAP-93 bounces non-conforming issues but nothing helps the only human file conforming ones; PAP-108 covers agent-to-agent handoffs only. |
| agents | P0 | Infra | 1 | Build the agent runtime sandbox: per-session container or worktree isolation, egress allowlist, CPU/RAM limits, no production credentials inside the sandbox | PAP-106 admits the hook is best-effort and 'Docker isolation and branch protection remain the real wall'; PAP-96 runs sessions on the VPS that holds every credential; no issue builds the isolation. |
| agents | P1 | Build | 2 | Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls | PAP-102 and PAP-113 assume a heartbeat timeout and a status shape; PAP-96 exposes `/status` informally; no owner defines them. |
| spec-builder | P2 | Build | 3 | Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule | PAP-27 lists spec-builder as a soft dependency and PAP-114 stores copy as plain strings; codegen would bake English into every app. |
| spec-builder | P2 | Build | 3 | Build spec versioning tooling: `specVersion` bumps, codemods for renamed keys, deprecation warnings and a rehearsed v1-to-v2 migration across 300 fixture specs | PAP-114 ships only a `migrations/v1-to-v2.ts` skeleton and PAP-74 deprecates components; no issue exercises a schema migration. |
| collab | P1 | Build | 1 | Build notification core independent of comments: kinds registry, delivery worker, in-app badge and email channel, `issue.needs_justin` and gate kinds | PAP-136 is P2 and blocked by PAP-131, yet PAP-94 (P0), PAP-88 and PAP-89 (P1) deliver Justin's decisions and gate failures through it. |
| collab | P2 | Build | 3 | Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX | PAP-203 writes 'to the tenant docs table when the runtime docs store exists' and PAP-128 is repo-only; 'every feature Notion has' needs editable docs at runtime. |
| collab | P2 | Build | 3 | Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay | Docs, guidelines and handbook exist, but nothing links a page to its help; part of the onboarding golden path. |
| realtime | P2 | Build | 3 | Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM) | PAP-136 targets 2 s 'or Electric shape', PAP-199 and PAP-113 fall back to polling, PAP-20 bundles `tauri-plugin-notification` with no server side. |
| forge | P1 | Infra | 2 | Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets | PAP-50 sizes Linux docker runners only; iOS builds, macOS signing and screen-reader CI cannot run anywhere today. |
| forge | P1 | Build | 2 | Define the template upgrade path for generated apps: versioned `paperos-template` releases, `paperos upgrade` applying template diffs, and an internal package registry for `@paperos/*` | PAP-22 clones a pinned tag and PAP-51 says packages are 'published later to the internal registry'; the brief's 'build everything in, remove later' implies downstream apps keep receiving the platform. |
| tables | P1 | Build | 1 | Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill | PAP-161 stores custom datasets and PAP-165's column menu can 'edit field', but no issue owns creating a table or converting types (PAP-164 documents conversions without a job). |
| tables | P1 | Build | 2 | Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo | PAP-165 has a `RecordPanel` in scope but detail routes, history/undo (PAP-144), activity (PAP-71 Timeline) and row comments (PAP-131) are stitched together by no one. |
| tables | P1 | Build | 2 | Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast | PAP-165 exposes a bulk actions bar and PAP-86 `crud.spec` expects 'undo'; no issue implements trash, restore or bulk server APIs. |
| business-core | P2 | Build | 2 | Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings | PAP-177 defers usage-based metering, PAP-178 counts limits live at creation only, `agentSessionsPerDay` and `storageGb` have no meter. |
| business-core | P2 | Build | 3 | Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing | PAP-180 says recurring is 'handled by Stripe Billing', which is PaperOS-to-tenant billing; a clinic or agency billing its own customers monthly has no recurring path. |
| growth | P2 | Build | 2 | Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules | PAP-187 stores consent, PAP-191 checks it at send time, PAP-136 has an unsubscribe link, PAP-193 writes consent from forms; no shared preference centre or suppression list. |
| migration | P1 | Infra | 2 | Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item | PAP-202/203/204/206 DoDs reference 'the PaperOS demo base', 'the PaperOS Notion test workspace' and sandboxes that no issue creates. |

Not proposed on purpose (out of scope or already owned): eye tracking/BCI, native Swift/Kotlin UI, third-party plugin marketplace (PAP-28 modules suffice for this build), bank feeds, multi-entity consolidation, Monday/HubSpot importers (sheets exist in PAP-198), Figma (PAP-77 decides).

## 4. L-sized issues that should be split (28 of 52 L issues; children in `gaps.json`)

Rule applied: split when a cold session cannot finish the DoD in one context window, when the issue blocks three or more others, or when sub-parts have different external prerequisites (accounts, runners, app reviews).

- **PAP-57** (P0, blocks 2) — Install Better Auth with passkeys, magic link, Google/GitHub OAuth and sessions 
  - Better Auth server, Drizzle schema merge and session helpers: Server config, generated schema adapted to core `user`, `requireSession()`, oRPC context.
  - Auth UI pages and email delivery: Sign-in/up/verify pages with specs, magic-link email, axe and screenshots.
  - Tauri deep-link and secure-token session flow: `paperos://` callback, keychain storage, restart persistence on Linux and macOS.
  - OIDC provider endpoints for Forgejo SSO: Provider plugin, Forgejo auth source, login proof.
- **PAP-59** (P0, blocks 6) — Build permission engine combining role-based grants with attribute policies decl
  - Policy model, evaluator and explain mode: Zod model, `can()` with deny-wins, benchmarks, 100 percent branch coverage.
  - SQL predicate compiler and RLS helpers: `toPredicate`, `toRlsPolicy`, PGlite property test against `can()`.
  - Spec adapter, oRPC middleware and `useCan` hook: Draft access-section adapter, 403 explain, PermissionProvider and Storybook.
- **PAP-81** (P0, blocks 2) — Build gate 2: three Claude reviewer agents (correctness, security, spec-conforma
  - Review harness: SDK runner, input assembly, finding validation and posting: `runReview()`, context budget, GitHub and Forgejo posting, idempotent comments.
  - Correctness and spec-conformance reviewer definitions: Prompts embedding rubrics, seeded-bug tests, calibration run.
  - Security reviewer definition and security.json ingestion: Prompt, authz seeded bug, waiver awareness, cost report.
- **PAP-82** (P0, blocks 3) — Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, 
  - Playwright project matrix, deterministic fixtures and Storybook story capture: 21 projects from breakpoints.json, masking, first baselines for stories.
  - Page capture with authenticated audiences and baseline update workflow: Test-user login fixtures, `update-baselines` label workflow, LFS setup.
  - Contact-sheet reporter, sharding and visual.json contract: Custom reporter, 4-shard CI, sticky comment, flake check.
- **PAP-96** (P0, blocks 3) — Build the orchestrator that polls Ready for Claude, spawns one Claude Code sessi
  - Linear polling, atomic claim and state transitions: Poll loop, claim guard, `linearComment()` helper, SQLite/Postgres tables.
  - Worktree lifecycle and Claude session launch: Worktree create/reuse/crash recovery, prompt rendering, SDK stream parsing, footer capture.
  - Deployment, `/status` endpoint and runbook: Coolify service, restart semantics, drain, README.
- **PAP-104** (P0, blocks 9) — Write the nine lead characters and their sub-characters as .claude/agents defini
  - Convert plan.json roster to validated character YAML: 37 YAML files, budgets, defaults, `pnpm agents tree` matches plan.
  - Write the nine lead system prompts: 300-800 words each, shared fragments, word-count test.
  - Write the 28 sub-character prompts and delegation descriptions: Classification test of 20 tasks routes correctly.
  - Build `.claude/agents` generation, CI check and smoke tasks: Deterministic build, `--check` in Gate 1, smoke transcripts per lead.
- **PAP-19** (P0, blocks 3) — Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle
  - Tauri desktop scaffold, capabilities and plugins: `apps/desktop`, least-privilege capabilities, menu, tray, dev scripts.
  - Desktop CI installers for Linux, macOS and Windows: tauri-action workflow, artifacts on a draft release, Rust lint.
  - Updater, single instance and deep links: `latest.json`, 0.0.1 to 0.0.2 proof, `paperos://` routing.
- **PAP-35** (P0, blocks 4) — Expose a typed API via oRPC with Zod schemas generated from Drizzle
  - API server, middleware chain and error mapping: Hono host, request id, auth stub, tenant context, `withTenant`, OTel hook.
  - API contract package and typed client: Zod from drizzle-zod, core routers, `@orpc/tanstack-query` hooks, `callAs` test utility.
  - OpenAPI docs, staging deploy and health: Scalar docs, `/api/health`, Coolify deploy, redocly lint.
- **PAP-36** (P1, blocks 1) — Integrate PGlite and ElectricSQL shapes for local-first reads with an offline wr
  - Electric service deployment and tenant-scoped shape proxy: Compose file, replication role, `/api/sync/shape` with server-set where clause.
  - PGlite client, schema generation and read hooks: `gen:pglite`, `useShape`, `useLiveQuery`, IndexedDB and Tauri persistence.
  - Offline write outbox and sync indicator: `_outbox` table, replay with backoff, leader election, demo route.
- **PAP-45** (P0, blocks 4) — Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly bac
  - Forgejo compose stack behind Caddy with hardened app.ini: Stack, TLS, admin and service accounts, org.
  - Backups and restore drill: restic sidecar, `restore.sh` into a scratch stack, timing.
  - OIDC auth source preparation and runbook: Documented switch-on path, upgrade procedure.
- **PAP-67** (P0, blocks 6) — Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Bu
  - Component infrastructure and form controls: `cn()`, variants, meta.ts convention, Button, IconButton, Input, Textarea, Checkbox, Radio, Switch, Slider, Field.
  - Overlay components: Dialog, AlertDialog, Popover, Tooltip, Menu, Toast with focus and dismiss layers.
  - Selection and navigation components: Select, Combobox (virtualised), Tabs, Avatar, Separator, size-limit check.
- **PAP-165** (P1, blocks 5) — Build the virtualized grid view (TanStack Table) with inline edit, column resize
  - Grid core: virtualisation, data binding, selection and keyboard model: Rows and columns virtualised, `useViewQuery`, active cell, range selection.
  - Inline editing, clipboard and bulk actions: Editors, optimistic commit, TSV paste in chunks, bulk bar.
  - Column operations, grouping headers and record panel: Resize, reorder, freeze, hide, aggregates footer, `RecordPanel`.
- **PAP-164** (P1, blocks 3) — Implement field types: text, number, currency, date, select, multi-select, relat
  - Field type framework and primitive types: `defineFieldType`, registry, text, number, currency, percent, date, checkbox, rating, url, email, phone.
  - Choice, people and attachment types: select, multiSelect, user, attachment with cell registry integration.
  - Relational and computed types: relation, lookup, rollup, formula storage with lateral-join contracts.
- **PAP-163** (P1, blocks 5) — Build the view query compiler from view model to SQL and Electric shapes with se
  - Compiler core: dataset resolution, filters and sorts with keyset cursors: `compileView`, per-type ops, signed cursors.
  - Groups, aggregates and Electric shape eligibility: `views.groups`, `views.distinct`, shape registration.
  - oRPC procedures, `useViewQuery` hook and 100k-row bench: Procedures, infinite pagination, p95 under 150 ms evidence.
- **PAP-143** (P1, blocks 2) — Stream record changes via Electric shapes to all connected clients and reconcile
  - Live query hooks and shape registry additions: `useLiveQuery`, `useShape`, `useRecord`, PM and tables shapes.
  - Reconciler for optimistic writes and conflict events: `mutation_id` echo matching, `expect` comparison, conflict emission.
  - Permission-driven resubscribe and lag measurement: 409 shape-invalid handling, 500 ms p95 test with Electric in CI.
- **PAP-131** (P1, blocks 3) — Implement in-app comments anchored to any entity, page element or doc block with
  - Comment schema, anchors, RLS and oRPC procedures: Threads, comments, anchor keys, visibility policies, `callAs` tests.
  - Comment panel, pins and composer UI: Panel/drawer, pins with clustering, Tiptap composer, mentions.
  - Live updates, deep links and Linear escalation: Realtime refresh, `?thread=` links, create-issue action.
- **PAP-132** (P1, blocks 3) — Build the canvas view (tldraw or React Flow) showing the UX flow of the whole ap
  - Canvas node and edge types with graph loader: Custom nodes, locked spec-derived elements, `canvas.graph.get`.
  - Collaborative overlay: notes, regions, overrides in Yjs: Position overrides, notes, presence cursors, reset layout.
  - Filters, deep links, export and 300-node performance run: Audience filter, `?node=` links, PNG export, fps evidence.
- **PAP-119** (P1, blocks 0) — Specify the data section (entities, queries, mutations, sync mode) and generate 
  - Data section schema and validator rules: Zod `DataSection`, filter import, `DATA_UNSCOPED` and param rules.
  - Hook generator for server, live and local modes: `gen:data`, typed hooks, optimistic updaters, drift check.
  - Example page end to end with offline test: `customer-invoices` hooks rendering from seed, mutation in second context.
- **PAP-120** (P1, blocks 0) — Generate page scaffolds (layout, component tree, loading/empty/error states) fro
  - Codegen templates and two-file ownership rules: Printer, route and view templates, refusal to overwrite, determinism.
  - State wiring, slot mapping and event binding: States switch, `useLayout` slots, `actions.*` binding, search-param schema.
  - Example specs generated, screenshotted and conformance-tested: Three examples at 7 widths, Storybook stories.
- **PAP-151** (P0, blocks 2) — Build the global command registry with keyboard shortcuts, command palette and p
  - Command registry core, scoping and chord matcher: `defineCommand`, scope stack, sequences, duplicate-ID manifest.
  - Command palette and help sheet UI: Combobox palette, virtualised results, `CommandButton`, shortcuts sheet.
  - Agent execution endpoint, telemetry and default commands: oRPC execute with `can()`, audit rows, `nav.*` and `ui.*` defaults.
- **PAP-155** (P1, blocks 2) — Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a ke
  - dnd-kit sensors on the input abstraction and `SortableList`: Pointer, touch, pen sensors, fractional indexing helper.
  - Keyboard alternative, announcements and focus restore: Pick up/move/drop grammar, `LiveAnnouncer` strings, snapshot tests.
  - KanbanDnd, SortableGrid, DropZone and cross-window drag: Cross-container moves, `canDrop`, multi-select overlay, Tauri transfer.
- **PAP-179** (P2, blocks 5) — Build a double-entry ledger (accounts, journal entries, periods) in Postgres wit
  - Journal tables, balance trigger and immutability constraints: Entries, lines, `UNBALANCED` and `IMMUTABLE_ENTRY` triggers, gapless numbering.
  - Hash chain, reversals and period close: `prev_hash`, `ledger.reverse`, `verifyChain`, lock workflow.
  - Posting rule registry, manual journal UI and trial balance: First five rules, `/finance/journal`, balance materialisation.
- **PAP-180** (P2, blocks 0) — Implement invoices, quotes and receipts with PDF generation and Stripe payment l
  - Document model, totals and state machine: `fin_document`, lines, sequences, taxes, quote to invoice conversion.
  - PDF rendering and public pay page: Branded templates, `/pay/:token`, Stripe Checkout, receipts.
  - Ledger postings, portal list and emails: `invoice.*` rules, customer portal invoices, notifications templates.
- **PAP-199** (P1, blocks 9) — Build the import framework: source connector, schema-mapping UI, dry run, valida
  - Connector interface, mapping model and engine: `SourceConnector`, `import_mapping`, batching, resumability, in-memory fixture connector.
  - Dry run, commit and rollback semantics: Transaction-rolled dry run, `import_run_item` before-state, exact rollback.
  - Mapping wizard UI and run history: Type-inference suggestions, report view, history grid.
- **PAP-190** (P2, blocks 1) — Build a social media scheduler with adapters (X, LinkedIn, Instagram, TikTok, Yo
  - Post model, approval state machine and calendar UI: Schema, transitions, composer, queue, calendar (list fallback).
  - Adapter interface with mock and X adapters: `validate/publish/fetchMetrics/refreshAuth`, mock adapter, X v2.
  - LinkedIn, Instagram, TikTok and YouTube adapters behind app review: Dry-run payload snapshots, OAuth connect, reauth banners.
- **PAP-136** (P2, blocks 0) — Build a notification center (in-app, email, Slack) with per-audience preferences
  - Notification core: kinds registry, delivery worker, in-app and email channels: Independent of comments; consumed by Justin queue and gates.
  - Inbox UI and preferences with quiet hours and digests: Inbox route, preference resolution, digest grouping.
  - Slack channel and tenant Slack configuration: Webhook config, templates, revoked-webhook banner.
- **PAP-88** (P1, blocks 2) — Define the release train: nightly staging deploy, weekly release candidate to Ne
  - Release train policy document and environments config: `release-train.md`, `environments.yaml`, freeze and hotfix rules.
  - Nightly staging workflow with full gate run: `staging-nightly.yml`, reports, three-night proof.
  - Release candidate cut, certification and Justin approval flow: `release-candidate.yml`, `certify.ts`, promotion and rollback via Coolify.
- **PAP-85** (P1, blocks 0) — Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/u
  - Scenario planner from specs with fixture catalogue: `planScenarios`, scenario classes, corpora, plan schema.
  - Playwright executor and generic oracles: Network, CPU, auth, concurrency, time fixtures; oracle set.
  - Findings, repro tests and nightly library run: Shared-schema findings, generated repro PRs, nightly Linear issues.

Remaining L issues judged fine as one unit (single builder, one external prerequisite): PAP-20, PAP-21, PAP-28, PAP-54, PAP-65, PAP-101, PAP-110, PAP-124, PAP-168, PAP-171, PAP-173, PAP-174, PAP-184, PAP-191, PAP-196, PAP-197, PAP-202, PAP-203, PAP-205, PAP-206, PAP-207, PAP-213, PAP-214, PAP-215. Of these PAP-65, PAP-196 and PAP-54 should be deferred rather than split.

## 5. Dependency errors

- Cycles: none (284 `blocks` relations, DAG verified). Phase inversions (P0 blocked by P1/P2): none.
- Relations in plan.json missing in Linear: PAP-25 blocks PAP-96 (orchestrator deploys onto the VPS); PAP-120 blocks PAP-29 and PAP-28 blocks PAP-29 (drill uses codegen and modules). Add these three.
- Hard dependencies stated in spec text but not encoded as relations (25 found, most important first): PAP-59 → PAP-140 (yjs-server calls `can()`), PAP-35 → PAP-129 and PAP-32 → PAP-129 (prompt-log ingest API and migrations), PAP-34 → PAP-35 and PAP-57 → PAP-35 (context contract and session verification; PAP-35 stubs auth so keep soft), PAP-34 → PAP-36, PAP-30 → PAP-36 (logical replication), PAP-34/35/59 → PAP-39, PAP-30 → PAP-40, PAP-59 → PAP-116, PAP-117 → PAP-123, PAP-123 → PAP-132, PAP-15 and PAP-66 → PAP-18, PAP-14 and PAP-17 → PAP-20, PAP-16 → PAP-21, PAP-33 → PAP-205, PAP-57 → PAP-86. PAP-188 lists five downstream issues as 'hard' consumers (reverse direction, informational). Encode the first eleven as `blocks`; leave the auth-stubbed ones soft.
- Milestone date inversions (blocker's milestone later than the blocked issue's): PAP-71 (09-25) blocks PAP-165 (09-23); PAP-70 (09-25) blocks PAP-152 (09-23); PAP-129 (09-21) blocks PAP-107 (09-20); PAP-212 (09-24) blocks PAP-67 (09-20); PAP-133 (09-26) blocks PAP-52 (09-24); PAP-88 (09-30) blocks PAP-29 (09-29). Fix by moving PAP-71/70 to the first design-system milestone, PAP-129 to 09-20, PAP-133 to the second collab milestone, and by making PAP-212 → PAP-67 soft (PAP-67 already says 'proceed with Base UI if not merged by 09-19').
- Wrong-direction dependency: PAP-136 (notifications) is blocked by PAP-131 (comments) although the Justin queue, release train and digest need notifications first; it should depend on PAP-43 only and be split (see splits).
- Ready set mismatch: PAP-198, PAP-188 and PAP-176 have no blockers, are Research, and sit in Backlog; move them to Ready for Claude. Conversely PAP-91 is Ready but partly obsolete (see weakest).
- Hidden infrastructure dependencies: PAP-82, PAP-85, PAP-87 on test-mode endpoints (PAP-86); PAP-156, PAP-73, PAP-19, PAP-20 on macOS/Windows runners (none); PAP-202/203/204/206 on external test workspaces (none); PAP-106 on PAP-48 (Forgejo bots) puts a P0 infra chain (25 → 45 → 48 → 106) on the agents critical path.
- Type/size anomalies: PAP-88 is `Spec` but builds three workflows (L); PAP-110 is `Review` but builds a harness (L); PAP-213/214/215 are `Research` L with 1.5-2 agent-day time boxes. Convert PAP-88 and PAP-110 to Build or split.
- Contradictions: PAP-95 closes PAP-5 while PAP-29 keeps it as the scoreboard; PAP-91/93 versus the live workspace (Character labels, estimates, Surface); PAP-100 puts PM schema in `packages/core`; PAP-133 and PAP-52 depend on each other informally (acknowledged in both specs; agree the feed JSON in PAP-133 first).
- Effort versus calendar: by size weights (S 0.5, M 1, L 2 agent-days) P0 is 72.5 days, P1 95.5, P2 76.5. The longest chain is 13 → 42 → 32 → 33 → 35 → 163 → 165 → 173 → 186 at 12.5 serial days; the P0-only chain 13 → 42 → 32 → 33 → 57 → 140 is 6.5 serial days against a 4-day P0 window (09-17 to 09-20). P0 will spill to roughly 09-23 even with unlimited parallelism.

## 6. Recommended order of fixes for the next agents

1. pm-linear reconcile (gap) and rewrite of PAP-91/93/95 before any orchestrator work, or the contract validator will fight the existing queue.
2. Add the three missing plan relations and the eleven hard spec dependencies; fix the six milestone inversions; move PAP-176/188/198 to Ready for Claude.
3. Create the P0 gap issues: filter grammar spec, gate artifact contract, test-mode seeding, threat model, agent sandbox.
4. Split PAP-104, PAP-57, PAP-96, PAP-81, PAP-82, PAP-67 first (they are P0 and block the most).
5. Re-phase notifications (core to P1), file the single Needs Justin credential ask for Apple/Windows signing, social app reviews and importer test accounts.
6. Defer PAP-65, PAP-196, PAP-54 and reduce PAP-159 to Web Speech so P2 fits the 09-27 to 10-01 window.
