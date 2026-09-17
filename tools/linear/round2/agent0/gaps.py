# Gap issues from round2/gaps.json for app-shell, data-layer, forge.
GAPS = []
def add(project, slug, title, type_, phase, priority, milestone, surfaces, state="Backlog", **s):
    GAPS.append(dict(project=project, slug=slug, title=title, type=type_, phase=phase, priority=priority,
                     milestone=milestone, surfaces=surfaces, state=state, sections=s))

# ============================ app-shell ============================
add("app-shell","runtime-flags",
"Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards",
"Build","P1",2,"Multi-monitor and PWA polish",["Staff","Developer"],
Goal="""Replace the env-only `VITE_FLAGS` bootstrap from PAP-17 with a real flag service in `packages/core/flags`: flags stored in Postgres per tenant and per audience, evaluated server-side and streamed to clients, with kill switches, segment targeting and a `flags:` guard in page specs, so risky work lands behind a flag (PAP-88) and in-app targeting (PAP-195) has a home. PAP-214 chose to own a flag service; this issue builds it.""",
Scope="""In:

* Tables `flag` (`key`, `description`, `kind boolean|variant`, `default`, `killSwitch`, `owner`) and `flag_rule` (`flag_id`, `tenant_id` nullable, `audience` nullable, `segment_id` nullable, `value`, `priority`).
* Evaluator `evaluate(flags, ctx: { tenantId, principal, audience, segments })` deterministic and pure; server evaluates and ships a `FlagSnapshot` to the client on session start and through the PAP-36 shape `flag_rules`.
* Hooks `useFlag(key)`, `useVariant(key)`; server helper `flagGuard(key)` for procedures; spec `flags: { requires: [...] }` enforced by PAP-118 validator and PAP-120 codegen (page renders `ui.flagDisabled` state).
* Settings page `/settings/flags` for staff with kill switches and per-tenant overrides; audit events on every change.
* Env `VITE_FLAGS` remains as a local override in development only.

Out: experimentation statistics, remote config of non-boolean settings (tenant settings own that).""",
Spec="""* Evaluation order: kill switch, tenant rule, audience rule, segment rule, default; highest `priority` wins within a level.
* Snapshot is versioned (`etag`); clients refetch on `flags.changed` event (data-layer event bus) or on shape update.
* Flag keys are `domain.feature` and must be declared in `flags.yaml` in the repo; undeclared keys fail typecheck via a generated `FlagKey` union.
* Kill switch flips every rule to `false` within 5 s on all clients; measured.
* Segments resolved through PAP-195 when present; otherwise only tenant and audience rules apply.""",
**{"Interface contract": """Provides: `useFlag`, `useVariant`, `flagGuard`, `FlagKey` type, tables above, oRPC `flags.list|update|kill`, spec section `flags:`, event `flags.changed`, `ui.flagDisabled` state name for PAP-120. Consumes: `VITE_FLAGS` bootstrap and env schema (PAP-17), oRPC host (PAP-35), tables and migrations (PAP-33, PAP-32), `can()` for the settings page (PAP-59), shapes (PAP-36), segments (PAP-195, soft), event bus (`contracts/domain-events`, soft)."""},
**{"Definition of done": """* Flip a flag for one tenant and see the page change without reload; kill switch propagates within 5 s (recording).
* Page spec with `flags.requires` renders the disabled state when off (codegen test).
* Vitest for the evaluator across rule combinations; `FlagKey` typecheck fails on an undeclared key.
* Settings page screenshots at 375, 768, 1280, 1920; audit events present; `docs/platform/flags.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: evaluator table covering kill, tenant, audience, segment and default with conflicting priorities; snapshot etag changes only when rules change.
* Integration (CI compose): `flags.update` as staff writes an audit event; `callAs(customer)` forbidden.
* E2E: Playwright toggles a flag in settings and asserts the dashboard element appears; kill switch timing measured.
* Static: generated `FlagKey` union check in Gate 1.
* Visual: settings page at four widths, light and dark."""},
Demo="""Reviewer opens `/settings/flags`, turns on `dashboard.newChart` for the Acme tenant, switches to a customer tab and sees the new chart appear, then hits Kill and watches it vanish within seconds. Under 90 seconds.""",
**{"Edge cases": """* Flag referenced by a spec but deleted: validator error names the page.
* Offline client: last snapshot used; flags never default to on when unknown.
* Two staff edit the same flag: last write wins with both audit events.
* Thousands of tenants with overrides: rules indexed by `(flag_id, tenant_id)`."""},
Dependencies="""PAP-17, PAP-33, PAP-35 (hard). Soft: PAP-36, PAP-59, PAP-118, PAP-120, PAP-195, `contracts/domain-events`. Consumed by PAP-88, PAP-195, PAP-178.""",
Agent="""Built by Forge (Platform Engineer) with Iris on the settings page. Reviewed by Sentinel.""",
Size="""M""")

add("app-shell","onboarding-wizard",
"Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard",
"Build","P1",1,"Multi-monitor and PWA polish",["Customer","Staff"],
Goal="""Own the customer-facing half of PAP-5: a new user goes from first sign-in to a useful workspace in under five minutes. PAP-58 redirects new users to `/org/new` and PAP-33 says the UI handles onboarding, but no issue owns the flow; templates (PAP-207) and billing (PAP-177) have no entry point. This wizard is that entry point, with each step optional and resumable.""",
Scope="""In:

* Route `/onboarding` with steps: organisation (name, slug, locale, timezone), business template (PAP-207 list with a blank option), invite team (emails and roles, sent through the email package), connect billing (Stripe Checkout via PAP-177, skippable on free plan), finish (seeded dashboard tour).
* Spec `specs/pages/onboarding.spec.yaml` driving the steps; progress persisted in `tenant.settings.onboarding` so refresh resumes.
* Seed application: chosen template imports through PAP-199 in the background with a progress banner.
* Staff view `/admin/onboarding` listing tenants by step reached (funnel), feeding PAP-194.

Out: marketing sign-up pages, plan pricing content, template authoring.""",
Spec="""* Slug availability checked live; suggestions on collision.
* Steps are idempotent procedures `onboarding.createOrg|applyTemplate|invite|connectBilling|complete`; each records `completedAt`.
* Skipping billing marks the tenant `plan: free` with entitlements from PAP-178.
* Under 5 minutes measured by the PAP-29 harness as checkpoint C3a.
* Every step has empty, loading, error and success states per PAP-120 codegen.""",
**{"Interface contract": """Provides: procedures above, `tenant.settings.onboarding` shape `{ step, completed: string[], templateId?, startedAt }`, route `/onboarding`, funnel query `onboarding.funnel`. Consumes: organisation creation (PAP-58), templates (PAP-207, soft; blank template until then), invites and email (PAP-58 and the email package issue), Stripe Checkout (PAP-177, soft), import runner (PAP-199, soft), `AppShell` and routes (PAP-16), core entities (PAP-33)."""},
**{"Definition of done": """* New user completes all five steps and lands on a seeded dashboard in under 5 minutes (recording, timed).
* Refresh mid-flow resumes at the same step; skipping billing yields a free-plan tenant.
* Playwright flow at 375 and 1280; screenshots of each step at seven widths; funnel page for staff.
* `docs/product/onboarding.md`; CHANGELOG; Linear comment with recording."""},
**{"Test plan": """* Unit: slug validation and suggestion; step state machine resume logic.
* Integration: each procedure via `callAs` twice (idempotent); invite sends one email per address through the email sandbox.
* E2E: Playwright full flow with the blank template; skip billing path; resume after reload.
* Visual: five steps at seven widths, light and dark.
* Timing: PAP-29 harness stamps the duration."""},
Demo="""Reviewer signs in with a fresh magic link, names the organisation "Demo Clinic", picks the clinic template, invites one colleague, skips billing and arrives on a dashboard with sample bookings. Under 3 minutes.""",
**{"Edge cases": """* Invited user already has an account: membership added, no duplicate user.
* Template import fails midway: banner offers retry; dashboard still usable empty.
* Browser closed after org creation: next login resumes at step two.
* Stripe unavailable: billing step shows retry and can be skipped."""},
Dependencies="""PAP-58, PAP-16, PAP-33 (hard). Soft: PAP-207, PAP-177, PAP-199, PAP-178, email package issue. Feeds PAP-29, PAP-194.""",
Agent="""Built by Forge with Iris (Component Crafter) and Quill on copy. Reviewed by Sentinel (Visual Inspector).""",
Size="""M""")

add("app-shell","client-errors",
"Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability",
"Build","P1",2,"Desktop and mobile shells build",["Customer","Staff","Developer"],
Goal="""One `reportError()` and one `<ErrorBoundary>` used by the shell, codegen and Tauri, with an error code catalogue and user-facing copy, and browser and Rust panic reports flowing into the PAP-40 collector through `/api/otel`. PAP-17 declares `VITE_SENTRY_DSN` and every spec has an error state, but nobody owns client error reporting today.""",
Scope="""In:

* `packages/core/src/errors/`: `AppError` with `code`, `message`, `hint`, `requestId`, `cause`; catalogue `errors.yaml` mapping codes to user copy (i18n keys via PAP-27); `reportError(err, ctx)` batching to `/api/otel` with breadcrumbs.
* `<ErrorBoundary>` (route-level and slot-level) with retry, "copy diagnostics" and the short request id; `ui.errorState` component in `@paperos/ui` that PAP-120 codegen targets.
* Tauri: Rust panic hook and `tauri-plugin-log` forwarding to the same endpoint; unhandled promise and `window.onerror` capture; service worker errors.
* Sentry-compatible envelope export optional behind `VITE_SENTRY_DSN` for teams that prefer it.
* Dedupe and rate limit: same fingerprint reported once per minute per client.

Out: server error handling (PAP-35 error mapping), alert rules (PAP-40).""",
Spec="""* Fingerprint = code plus top stack frame plus route; PII scrubbed with the PAP-40 denylist before send.
* API errors (`ApiErrorCode`) map one-to-one to catalogue entries; unknown codes render the generic entry and log a catalogue miss.
* Offline: reports queued in IndexedDB, flushed on reconnect, capped at 200.
* Copy rules in `errors.yaml`: what happened, what to do, no blame; reviewed by Quill.""",
**{"Interface contract": """Provides: `AppError`, `reportError`, `ErrorBoundary`, `ErrorState` (the `ui.errorState` target), `errors.yaml` catalogue and generated `ErrorCode` union, Tauri panic forwarding. Consumes: `/api/otel` and PII denylist (PAP-40), `ApiErrorCode` (PAP-35), `VITE_SENTRY_DSN` (PAP-17), i18n (PAP-27), routes (PAP-16), Tauri crate (PAP-19). Consumed by PAP-120 codegen, PAP-71, every page."""},
**{"Definition of done": """* Throwing in a route loader shows the boundary with retry and request id; the report appears in Tempo or Loki with route and code (screenshot).
* Rust panic in the desktop app produces a report and the app relaunches to the last route (recording).
* Vitest for fingerprinting, dedupe, offline queue and catalogue mapping; every `ApiErrorCode` has copy.
* `ErrorState` screenshots at seven widths light and dark; `docs/shell/errors.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: fingerprint stability across renders; one report per minute per fingerprint; PII scrub on messages containing emails; catalogue completeness test against `ApiErrorCode`.
* Integration: report reaches a local collector in CI compose with expected attributes.
* E2E: Playwright triggers a loader error, asserts boundary copy and copy-diagnostics content; offline queue flushes on reconnect.
* Rust: panic hook unit test with a mocked transport.
* Visual: boundary and inline error state at seven widths."""},
Demo="""Reviewer appends `?__throw=1` to the dashboard URL on staging, sees the error boundary with a short id, clicks "copy diagnostics", pastes the id into Grafana Explore and finds the report. Under 90 seconds.""",
**{"Edge cases": """* Error inside the boundary's own render: fallback to a static HTML message.
* Collector unreachable: queue, cap, drop oldest.
* Error storms (render loop): circuit breaker stops reporting after 50 in a minute and reports one summary.
* Service worker update mid-report: queue survives."""},
Dependencies="""PAP-16, PAP-17 (hard). Soft: PAP-19, PAP-27, PAP-35, PAP-40. Consumed by PAP-120, PAP-71.""",
Agent="""Built by Forge with Quill on copy. Reviewed by Sentinel (Code Reviewer).""",
Size="""M""")

add("app-shell","code-signing",
"Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask",
"Infra","P1",2,"Desktop and mobile shells build",["Developer"],
Goal="""Make desktop and mobile builds installable without security warnings: Apple Developer ID signing and notarisation, a Windows code-signing certificate, and an Android upload keystore, with keys in sops and signing steps in the PAP-19 and PAP-20 CI workflows. Files the single Needs Justin item for the accounts and payments so PAP-29 stops recording unsigned builds as friction.""",
Scope="""In:

* Needs Justin issue listing exactly what to buy and share: Apple Developer Program membership, App Store Connect API key, Windows OV or EV certificate (or Azure Trusted Signing), Google Play upload keystore; costs and links.
* sops entries `ops/secrets/signing.enc.yaml`; CI secrets set by PAP-51.
* `desktop.yml` steps: macOS `codesign` plus `notarytool` via tauri-action env; Windows `signtool` or Trusted Signing action; Linux unchanged.
* Android release signing config; iOS provisioning profiles for TestFlight.
* Verification scripts `ops/signing/verify.sh` (`spctl`, `codesign -dv`, `signtool verify`, `apksigner verify`).

Out: store listings and review submissions, Linux package signing (deferred to `gp/app-shell/upgrade`).""",
Spec="""* Signing keys never on developer laptops; CI-only; rotation runbook.
* Notarisation waits with a 20-minute timeout and staples the ticket.
* Windows builds produce a SmartScreen-clean installer after reputation warm-up; documented.
* Unsigned fallback remains available with `SIGN=0` for PRs.""",
**{"Interface contract": """Provides: secret names `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_API_KEY_*`, `WINDOWS_CERT_*`, `ANDROID_KEYSTORE_*` in the PAP-50 secrets manifest; workflow steps consumed by PAP-19 child 2 and PAP-20 child 1; `verify.sh`. Consumes: installers (PAP-19), mobile builds (PAP-20), sops (PAP-25), non-Linux runners (forge runner issue) for macOS and Windows jobs."""},
**{"Definition of done": """* Needs Justin item filed with costs and links on day one; credentials received and stored.
* macOS `.dmg` passes Gatekeeper with no warning; `spctl --assess` output attached; Windows installer shows the publisher name; Android release APK verified.
* `verify.sh` runs in CI after signing; `docs/shell/signing.md` and rotation runbook; CHANGELOG; Linear comment."""},
**{"Test plan": """* CI: signing steps run on a tag; `verify.sh` asserts signatures on all artifacts.
* Manual recorded: fresh macOS VM opens the `.dmg` without warning; Windows VM installs with publisher shown; Android device installs the release APK.
* Negative: `SIGN=0` still builds for PRs; missing secret fails with a clear message."""},
Demo="""Reviewer downloads the signed `.dmg` from the release on a Mac, double-clicks it and the app opens with no Gatekeeper dialog; `codesign -dv --verbose=2 PaperOS.app` prints the team id. Under a minute.""",
**{"Edge cases": """* Apple account approval takes days: file first, proceed with unsigned builds meanwhile.
* Notarisation rejected for a hardened-runtime entitlement: documented entitlements list.
* Certificate expiry: calendar reminder in the runbook 30 days before.
* EV certificate on a hardware token: prefer Azure Trusted Signing to keep signing in CI."""},
Dependencies="""PAP-19, PAP-25 (hard). Soft: PAP-20, forge non-Linux runner issue. Consumed by PAP-29, PAP-88.""",
Agent="""Built by Forge (Ops Runner); Justin supplies credentials once. Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("app-shell","custom-domains",
"Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI",
"Build","P2",3,"Multi-monitor and PWA polish",["Customer","Staff"],
Goal="""Let a tenant serve PaperOS at `app.acme.com` with its own branding: Caddy issues certificates on demand for verified hosts, the API resolves the tenant by host, and a settings UI walks the tenant through CNAME plus TXT verification. PAP-178 sells a `whiteLabel` entitlement and PAP-35 resolves by subdomain, but nothing provisions domains today.""",
Scope="""In:

* Table `tenant_domain` (`tenant_id`, `host`, `status pending|verified|active|failed`, `verification_token`, `verified_at`).
* Caddy on-demand TLS with an `ask` endpoint `GET /api/domains/allow?host=` that answers only for `active` hosts.
* Tenant resolution middleware in PAP-35 extended: header, subdomain, then `tenant_domain` lookup with a 60 s cache.
* Settings page `/settings/domains` with instructions, verification button and status; PAP-72 branding applied per host.
* Job `domains.verify` re-checking DNS hourly; entitlement check `whiteLabel` (PAP-178).

Out: email sending domains, apex domains without CNAME flattening (documented), custom domains for the marketing site.""",
Spec="""* Verification: CNAME `app.acme.com -> tenants.PAPEROS_DOMAIN` and TXT `_paperos.acme.com = <token>`; both required.
* `ask` endpoint responds in under 50 ms from cache; certificates issued at first request.
* Removing a domain revokes routing immediately and lets the certificate expire.
* Auth cookies scoped per host; PAP-57 session works across the custom host through the same-origin API path.""",
**{"Interface contract": """Provides: table, oRPC `domains.add|verify|remove|list`, `GET /api/domains/allow`, host resolution in the tenant middleware, `useTenantHost()`. Consumes: Caddy on the host (PAP-25), tenant middleware (PAP-35), jobs (PAP-43), entitlements (PAP-178), branding (PAP-72), sessions (PAP-57)."""},
**{"Definition of done": """* A test domain pointed at staging verifies, gets a certificate and serves the tenant with its branding (recording).
* Unverified host returns 404 from Caddy `ask`; removal stops routing within 60 s.
* Vitest for verification logic and resolution order; `docs/platform/domains.md`; settings page at 375, 768, 1280, 1920; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: DNS answer parsing with fixtures (missing TXT, wrong CNAME target, both correct); resolution order with header, subdomain and host conflicts.
* Integration: `ask` endpoint against `active`, `pending` and unknown hosts; cache expiry.
* E2E: staging with a real test domain; Playwright asserts branding and sign-in on the custom host.
* Visual: settings page states at four widths."""},
Demo="""Reviewer adds `demo.paperos-test.dev` in settings, sets the two DNS records shown, clicks Verify, then opens the domain in a new tab and lands on the tenant's branded sign-in page over HTTPS. Under 2 minutes once DNS propagates.""",
**{"Edge cases": """* Apex domain: instruct ALIAS or CNAME flattening; otherwise unsupported.
* Domain moved between tenants: old mapping removed first; unique `host`.
* Cloudflare proxied CNAME: works but documented certificate mode.
* Rate limits from Let's Encrypt: on-demand TLS limited to verified hosts only."""},
Dependencies="""PAP-25, PAP-35, PAP-178 (hard). Soft: PAP-43, PAP-57, PAP-72.""",
Agent="""Built by Forge (Ops Runner and Platform Engineer). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

# ============================ data-layer ============================
add("data-layer","event-bus",
"Specify and build the domain event catalogue, transactional outbox and subscriber registry (`packages/core/events`)",
"Spec","P1",1,"Local-first sync working",["Developer","Agent"],
Goal="""Give the platform one event bus: typed `emit('invoice.paid', payload)` written in the same database transaction as the change, delivered at least once to in-process and job-queue subscribers with idempotency. PAP-28 mandates cross-module coupling only through events; PAP-136 kinds, PAP-174 triggers, PAP-195 segment events and PAP-177 webhooks all need one; only the orchestrator (PAP-97) has an in-process emitter today.""",
Scope="""In:

* Catalogue `events.yaml` declaring `name`, Zod payload schema, `tenantScoped`, `pii` fields, `owner` module; generated `EventName` union and `EventPayload<N>` types.
* Table `event_outbox` (`id uuidv7`, `tenant_id`, `name`, `payload`, `occurred_at`, `actor`, `request_id`, `dispatched_at`) written by `emit()` inside the caller's transaction.
* Dispatcher job `events.dispatch` (PAP-43) polling the outbox, fanning out to subscribers registered with `subscribe(name, handler, { idempotencyKey })`, retrying per subscriber.
* In-process subscribers for same-request effects; queue subscribers for async work; `event_delivery` table for per-subscriber status.
* Spec section: `docs/platform/events.md` with the catalogue rendered from `events.yaml`.

Out: outbound webhooks to tenants (identity webhooks issue consumes this), CRDT document events (PAP-140).""",
Spec="""* `emit(name, payload, ctx)` validates against the schema and requires `ctx.db` to be inside a transaction; outside one it throws.
* Delivery guarantee: at least once; handlers wrap `withIdempotency(eventId + subscriberId)`.
* Ordering per aggregate key (`payload.aggregateId`) preserved within a subscriber.
* Poison events after 5 failures land in `jobs.dead_letter` with the subscriber name.
* Catalogue changes are reviewed: removing or renaming an event requires an ADR; adding is a PR.""",
**{"Interface contract": """Provides (from `@paperos/core/events`): `emit`, `subscribe`, `EventName`, `EventPayload`, `events.yaml`, tables `event_outbox` and `event_delivery`, job `events.dispatch`. Consumes: transactions and migrations (PAP-32), jobs and `withIdempotency` (PAP-43), audit vars (PAP-38). Consumed by PAP-28 (coupling rule), PAP-136, PAP-174, PAP-177, PAP-181, PAP-195, PAP-97 (adapts its emitter), runtime flags (`flags.changed`)."""},
**{"Definition of done": """* Catalogue with the first ten events (`tenant.created`, `membership.invited`, `file.ready`, `invoice.paid`, `record.changed`, `flags.changed` and four more from consumers) merged and rendered.
* Emit inside a rolled-back transaction leaves no outbox row (test); emit inside a committed transaction is delivered to two subscribers exactly once each despite a forced retry (test).
* Bench: 10,000 events dispatched under 60 s with two workers.
* `docs/platform/events.md`; ADR; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: schema validation, `EventName` union generation, ordering per aggregate, poison handling.
* Integration (CI compose): rollback leaves no row; retry does not double an effect; dead-letter after 5 failures; per-subscriber status rows.
* Bench committed.
* Static: catalogue lint (owner exists, pii fields declared)."""},
Demo="""Reviewer runs `pnpm events:catalogue` to print the ten events, then in the API console completes a file upload and watches `event_delivery` rows for `file.ready` appear for the search and notification subscribers in Drizzle Studio. Under 90 seconds.""",
**{"Edge cases": """* Subscriber registered after events were emitted: no replay by default; `replayFrom(date)` admin command.
* Payload with PII: fields declared and redacted in logs.
* Tenant deleted: dispatcher skips with `skipped` status.
* Very large payload: reference to PAP-37 blob."""},
Dependencies="""PAP-32, PAP-43 (hard). Soft: PAP-38. Consumed by PAP-28, PAP-136, PAP-174, PAP-177, PAP-195, PAP-97, runtime-flags issue.""",
Agent="""Specified by Quill with Forge; built by Forge (Platform Engineer). Reviewed by Sentinel and Nova.""",
Size="""M""")

add("data-layer","filter-grammar",
"Specify the shared filter and condition grammar (`packages/core/filter`): one Zod FilterTree with SQL and in-memory evaluators",
"Spec","P0",1,"Postgres + Drizzle baseline",["Developer"],state="Ready for Claude",
Goal="""Define the single filter and condition grammar that permissions `Condition` (PAP-59), the view model `FilterGroup` (PAP-161), the spec data section (PAP-119, currently a copy with a TODO), the filter builder (PAP-166), segments (PAP-195) and automations (PAP-174) all import instead of redefining. One Zod schema, one SQL compiler for Drizzle, one in-memory evaluator, proven equivalent by property tests.""",
Scope="""In:

* `packages/core/src/filter/`: `FilterTree = Group | Condition`; `Group = { op: 'and'|'or'|'not', children }`; `Condition = { field, operator, value }` with operators per field type (`eq`, `neq`, `in`, `nin`, `lt`, `lte`, `gt`, `gte`, `contains`, `startsWith`, `isNull`, `isNotNull`, `between`, `has` for arrays, `matches` for jsonb path).
* Field typing via a `FieldSchema` map so `value` is validated per operator; variables `{ $var: 'principal.id' }` resolved at evaluation.
* `toSql(tree, table, ctx)` returning a Drizzle `SQL` fragment; `evaluate(tree, row, ctx)` in memory; `normalize(tree)` canonical form; `explain(tree)` human text.
* Property-based equivalence test between `toSql` on PGlite and `evaluate`.

Out: UI (PAP-166), full-text search operators (PAP-39), aggregation.""",
Spec="""* Max depth 8, max 200 conditions; validation errors name the path.
* Case-insensitive text operators use `citext` or `ILIKE`; documented per type.
* Null semantics follow SQL (three-valued) in both evaluators; tests cover it.
* Serialised form is JSON; a compact URL encoding `encodeFilter`/`decodeFilter` for view links (PAP-172).
* Versioned `v: 1`; migrations for future versions.""",
**{"Interface contract": """Provides (from `@paperos/core/filter`): `FilterTree`, `filterTreeSchema`, `toSql`, `evaluate`, `normalize`, `explain`, `encodeFilter`, `decodeFilter`, `FieldSchema`, `Variables`. Consumed by PAP-59 (`Condition` becomes an alias), PAP-161 (`FilterGroup` alias), PAP-119, PAP-163 (compiler), PAP-166, PAP-172, PAP-174, PAP-195, PAP-35 list inputs. Consumes: Drizzle `sql` helper (PAP-32) and PGlite for tests (PAP-42); no runtime dependency on the database."""},
**{"Definition of done": """* Package merged with schema, both evaluators and 500-case property test green on PGlite.
* PAP-59, PAP-161 and PAP-119 owners comment approval and their specs reference this package.
* `docs/platform/filter.md` with the operator table per field type; ADR; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: schema accepts and rejects fixtures (depth, count, operator versus type, variables); `normalize` idempotent; `explain` snapshots.
* Property: fast-check generates trees and rows; `evaluate` equals `toSql` result on PGlite for 500 cases including nulls.
* Type: `FieldSchema` narrows `value` types (`expectTypeOf`).
* Perf: `toSql` under 1 ms for a 50-condition tree."""},
Demo="""Reviewer runs `pnpm --filter core test filter` and watches the property test pass, then `pnpm tsx examples/filter.ts` printing a tree, its SQL and its explanation in English. Under a minute.""",
**{"Edge cases": """* Unknown field: validation error with suggestions.
* `in` with empty list: always false, documented.
* jsonb `matches` on a non-jsonb field: rejected at validation.
* Variables unresolved at evaluation: throw, never default."""},
Dependencies="""None hard (pure package on PAP-13 layout); PAP-42 for the PGlite test only. Ready now. Blocks PAP-59, PAP-161, PAP-119, PAP-166, PAP-174, PAP-195.""",
Agent="""Specified and built by Forge (Platform Engineer) with Nova. Reviewed by Sentinel (Code Reviewer).""",
Size="""M""")

add("data-layer","email-package",
"Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev",
"Build","P1",1,"Local-first sync working",["Customer","Staff","Developer"],
Goal="""Every sender (magic links, invites, notifications, receipts, digests) calls one `sendEmail()` with the same sandbox, branding and compliance rules. PAP-57, PAP-58, PAP-136, PAP-180 and PAP-191 each wire Resend independently and only PAP-191 defines sandbox mode; PAP-214 picks the provider but ships no package. P0 identity issues call Resend directly at first and migrate here without changing their tests.""",
Scope="""In:

* `packages/email`: `defineTemplate(name, schema, Component)` with React Email 4; `sendEmail(template, props, { to, tenantId, tags })` through a `Provider` adapter (`resend` default, `smtp` for Mailpit and self-hosted, `noop` for tests).
* Sandbox mode: outside production every address not on `EMAIL_ALLOWLIST` is rewritten to `sandbox+<hash>@PAPEROS_DOMAIN` and the original recorded.
* Suppression list `email_suppression` (bounces, complaints, unsubscribes) fed by provider webhooks; `sendEmail` refuses suppressed addresses.
* Per-tenant branding (logo, colours, footer) from PAP-72; layout components; plain-text alternative generated.
* `pnpm email:check` verifying SPF, DKIM and DMARC for the sending domain; `pnpm email:preview` dev server.
* Delivery through PAP-43 job `email.send` with retry; `email_log` table.

Out: marketing campaigns and sequences (PAP-191 builds on this), inbound parsing.""",
Spec="""* Templates render in under 50 ms; total size under 100 KB; images hosted, not inlined.
* Every message carries `List-Unsubscribe` for non-transactional kinds and a tenant footer.
* Rate: provider limits respected by job concurrency.
* Logs never store bodies, only template name, props hash and status.""",
**{"Interface contract": """Provides (from `@paperos/email`): `defineTemplate`, `sendEmail`, `Provider` interface, tables `email_log` and `email_suppression`, job `email.send`, webhook route `POST /api/email/events`, env `EMAIL_PROVIDER`, `RESEND_API_KEY`, `SMTP_URL`, `EMAIL_ALLOWLIST`. Consumes: Resend domain and key (PAP-25), Mailpit (PAP-42), jobs (PAP-43), branding (PAP-72, soft), i18n (PAP-27, soft). Consumed by PAP-57, PAP-58 (migrate after landing), PAP-136, PAP-180, PAP-191, onboarding wizard."""},
**{"Definition of done": """* Magic-link and invite templates migrated; `sendEmail` in sandbox delivers to Mailpit locally and to the sandbox address on staging (screenshots).
* Suppression: a bounced address is refused on the next send (test).
* `email:check` passes on the sending domain; previews for every template at 375 and 600 px widths in light and dark.
* Vitest for allowlist rewriting, suppression, template schema; `docs/platform/email.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: sandbox rewrite for allowed, disallowed and mixed recipients; suppression refusal; template props validation.
* Integration (CI compose with Mailpit): send through `smtp`, assert message and plain-text part; provider webhook inserts a suppression row.
* Snapshot: HTML output per template.
* Visual: previews at two widths, light and dark; Gmail and Outlook rendering checked once via Litmus-style screenshots or documented manual check."""},
Demo="""Reviewer runs `pnpm email:preview`, opens the invite template with sample props, then triggers an invite from the app and finds it in Mailpit at `localhost:8025` with the tenant footer. Under a minute.""",
**{"Edge cases": """* Provider outage: job retries; status `deferred` visible in the log.
* Recipient on suppression list but transactional (password reset): still refused; UI explains to contact support.
* Tenant branding missing: platform default.
* Large recipient list: one job per recipient, not one giant send."""},
Dependencies="""PAP-25, PAP-43 (hard). Soft: PAP-42, PAP-72, PAP-27. Consumed by PAP-136, PAP-180, PAP-191, onboarding wizard; PAP-57 and PAP-58 migrate after landing.""",
Agent="""Built by Forge with Iris on templates. Reviewed by Sentinel (Security Auditor for webhooks).""",
Size="""M""")

add("data-layer","field-encryption",
"Build server-side field encryption for stored secrets (OAuth tokens, SCIM tokens, webhook secrets, connector auth) with key rotation",
"Build","P1",1,"Local-first sync working",["Developer"],
Goal="""Provide the `encrypted<T>()` Drizzle column helper that PAP-190, PAP-65, PAP-174, PAP-199 and PAP-193 assume exists ("encrypted via app-shell/env-config helpers"), which PAP-17 does not provide because it covers client keychains only. Values are encrypted at rest with an application key from sops, keyed per tenant, with a re-encrypt job for rotation.""",
Scope="""In:

* `packages/db/src/crypto/`: `encrypted<T>(name)` column helper storing `{ v, kid, iv, ct, tag }` as `bytea` or jsonb, transparent encrypt on write and decrypt on read through Drizzle custom types.
* Keys: `APP_ENCRYPTION_KEYS` (JSON of `kid` to base64 key) from sops via PAP-17 `serverEnvSchema`; AES-256-GCM; per-row data key derived with HKDF from the master key and `tenant_id`.
* Rotation job `crypto.reencrypt` (PAP-43) walking tables with encrypted columns in batches; `pnpm crypto:rotate --new-kid`.
* Redaction: encrypted columns excluded from PAP-38 diffs and PAP-41 dictionary marks them `secret`.
* Helper `hashLookup(value)` for searchable secrets (HMAC) where equality lookup is needed.

Out: client-side encryption, envelope encryption with a cloud KMS (documented as an upgrade path), TLS.""",
Spec="""* Decrypt failures raise `CRYPTO_UNAVAILABLE`, never return ciphertext.
* Key ids are immutable; the active `kid` is the last in the list; old keys remain for reads until rotation completes.
* Bench: encrypt and decrypt under 0.1 ms per value; batch of 10,000 rows re-encrypted under 30 s.
* Migration helper converts a plaintext column to encrypted in place with a two-step deploy documented.""",
**{"Interface contract": """Provides (from `@paperos/db/crypto`): `encrypted<T>`, `hashLookup`, `rotateKeys`, job `crypto.reencrypt`, env `APP_ENCRYPTION_KEYS`, error `CRYPTO_UNAVAILABLE`, schema tag `@secret`. Consumes: env schema (PAP-17), Drizzle helpers (PAP-32), sops (PAP-25), jobs (PAP-43), `pgcrypto` not required (Node crypto). Consumed by PAP-65, PAP-174, PAP-190, PAP-193, PAP-199, identity API-keys and webhooks issues."""},
**{"Definition of done": """* A fixture table with an encrypted column round-trips through Drizzle; raw SQL shows ciphertext only (screenshot).
* Rotation: add a new key, run the job, old key removed, reads still work (test log).
* Audit diff for an encrypted column shows `[secret]`; dictionary marks it.
* Vitest for helper, HKDF derivation and failure modes; bench committed; `docs/data/encryption.md`; ADR; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: encrypt and decrypt round trip; tamper detection (modified tag fails); wrong tenant derivation fails; missing key raises `CRYPTO_UNAVAILABLE`.
* Integration (CI compose): rotation job over 10,000 rows with two workers; concurrent writes during rotation preserved.
* Static: lint that columns named `*_token`, `*_secret`, `*_key` use `encrypted()` (fixtures).
* Security: Sentinel reviews key handling and log redaction."""},
Demo="""Reviewer inserts a connector token through the API, runs `psql -c "select auth from connector"` and sees ciphertext, then reads it back through the API in plaintext, and runs `pnpm crypto:rotate --new-kid k2` to watch rows re-encrypt. Under 2 minutes.""",
**{"Edge cases": """* Key removed while rows still use it: rotation refuses removal with a count.
* Very large values: chunked; documented limit 1 MB.
* Backup restore to a host without keys: `CRYPTO_UNAVAILABLE` with a clear runbook link.
* Test databases: a fixed test key in `.env.test`."""},
Dependencies="""PAP-32, PAP-25 (hard). Soft: PAP-17, PAP-43, PAP-38, PAP-41. Consumed by PAP-65, PAP-174, PAP-190, PAP-193, PAP-199.""",
Agent="""Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("data-layer","rate-limit-idempotency",
"Build shared rate limiting and idempotency middleware backed by Postgres (per actor, per API key, per IP for public routes)",
"Build","P1",2,"Local-first sync working",["Developer"],
Goal="""Replace the in-memory token bucket in PAP-35 ("Redis later") with Postgres-backed rate limiting and an `idempotency_keys` table so that PAP-148's offline replay, PAP-172 public embeds, PAP-193 form capture and PAP-194 collectors stop hand-rolling limits. Consistent `Retry-After` and `Idempotency-Key` semantics across every route.""",
Scope="""In:

* `packages/api-contract/server/limits.ts`: `rateLimit({ key: 'actor'|'apiKey'|'ip'|'tenant', limit, windowS })` middleware using token buckets in an `UNLOGGED` table `rate_bucket` with `FOR UPDATE SKIP LOCKED`; local in-process cache to avoid a query per request when far from the limit.
* Idempotency: `idempotency_key` table (`key`, `actor_id`, `request_hash`, `response`, `status`, `expires_at`); middleware replays the stored response for a repeated key within 24 h and returns `CONFLICT` on a different request body with the same key.
* Batch endpoint `/api/rpc/batch` honouring per-call keys (PAP-148).
* Headers `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`; error `RATE_LIMITED`.
* Defaults: 600 per minute per actor, 60 per minute per IP on public routes, per-tenant 5,000 per minute; overrides by plan through PAP-178.

Out: DDoS protection at the edge (Caddy and Hetzner), abuse detection.""",
Spec="""* Buckets keyed `(scope, key, route)`; cleanup job hourly removes idle buckets.
* Idempotent by default for `create` and `update` procedures when the header is present; required for financial procedures (PAP-179).
* Response cache capped at 64 KB; larger responses store status only and replay `409` with a hint.
* Clock: server time; `Retry-After` in seconds.""",
**{"Interface contract": """Provides: `rateLimit`, `idempotent` middleware, tables `rate_bucket` and `idempotency_key`, `/api/rpc/batch`, headers and `RATE_LIMITED`, job `limits.cleanup`. Consumes: API chain (PAP-35 child 1), migrations (PAP-32), jobs (PAP-43), plan limits (PAP-178, soft). Consumed by PAP-148, PAP-172, PAP-179, PAP-193, PAP-194, identity API-keys issue."""},
**{"Definition of done": """* Hammering a procedure at 700 per minute yields `RATE_LIMITED` with correct headers after 600 (k6 script committed).
* Same `Idempotency-Key` twice returns the identical response and one database effect; changed body returns `CONFLICT` (tests).
* Two API replicas share limits (test with two processes).
* `docs/data/limits.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: bucket refill math with fake time; header computation; request hash stability.
* Integration (CI compose): two server processes, 1,000 requests, exactly 600 allowed in the window; idempotent replay under concurrent duplicates yields one effect.
* Load: k6 script asserting headers and 429 rate.
* Negative: key over 255 chars rejected; expired key allows a new request."""},
Demo="""Reviewer runs `pnpm tsx scripts/limits-demo.ts` which fires 650 calls and prints the first `RATE_LIMITED` response with headers, then sends the same `create` twice with one key and shows a single row in Studio. Under a minute.""",
**{"Edge cases": """* Postgres slow: middleware fails open for rate limits (logged) and fails closed for idempotency.
* Shared NAT IPs: per-IP limits only on public routes; documented.
* Clock skew between replicas: buckets use database `now()`.
* Very bursty legitimate agents: per-actor overrides for `kind: 'agent'`."""},
Dependencies="""PAP-35, PAP-32 (hard). Soft: PAP-43, PAP-178. Consumed by PAP-148, PAP-172, PAP-179, PAP-193, PAP-194.""",
Agent="""Built by Forge (Platform Engineer). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("data-layer","platform-dr",
"Add object-storage backups and a platform-wide disaster-recovery drill (Postgres + MinIO + Yjs + orchestrator state restored on a fresh host)",
"Infra","P1",2,"Tenant-safe and observable",["Developer"],
Goal="""Back up everything PAP-30 and PAP-45 do not: tenant files in MinIO, Yjs document persistence and the orchestrator database, and prove the whole platform restores on a fresh host with a scripted drill that records RTO and RPO like PAP-53 does for the forge.""",
Scope="""In:

* `restic` backups of MinIO buckets (`paperos-prod`, `paperos-staging`) via `mc mirror` to a staging directory then restic to `paperos-backups/minio`; Yjs documents (PAP-140 Postgres tables are covered by PAP-30; file-based state if any); orchestrator database (PAP-96) dumped nightly.
* `ops/dr/platform-drill.sh`: create a throwaway Hetzner host, restore Postgres via `pgbackrest` to the latest point, restore MinIO objects, bring up API, worker, Electric and Hocuspocus from images in the Forgejo registry (PAP-50), run smoke tests (sign-in, list workspaces, open a file, open a Yjs document), record `report.json`, tear down.
* Secondary copy: weekly `restic copy` to a second bucket in another region.
* Runbook `docs/runbooks/platform-dr.md`; quarterly cron.

Out: forge DR (PAP-53), Linear (SaaS), DNS failover automation.""",
Spec="""* Targets: RPO 1 h (Postgres WAL) and 24 h (objects), RTO 2 h; report flags misses.
* Restore uses only artifacts from our own storage and registry; GitHub blocked as in PAP-53.
* Smoke tests reuse PAP-86 flows against the drill host.
* Encryption keys (field-encryption issue) restored from sops; the drill proves decryption works.""",
**{"Interface contract": """Provides: `report.json` (same schema as PAP-53 with `services[]`), runbook, backup repo paths, weekly secondary copy, quarterly drill cron. Consumes: `pgbackrest` stanza (PAP-30), MinIO buckets (PAP-37), Forgejo registry images (PAP-26, PAP-50), Yjs persistence (PAP-140), orchestrator database (PAP-96), sops keys (PAP-25), e2e flows (PAP-86), drill scaffolding from PAP-53."""},
**{"Definition of done": """* One full drill executed; `report.json` and rendered report committed with RTO and RPO; misses have follow-up issues.
* Restored host passes the four smoke flows (recording).
* Secondary copy exists in a second region; quarterly cron configured.
* Runbook merged; Sentinel (Edge Case Hunter) reviews; Linear comment with headline numbers."""},
**{"Test plan": """* Unit: `bats` for phase ordering and teardown.
* Integration: the drill itself; assert object count and checksums match the manifest; Postgres row counts match the snapshot.
* Failure: corrupt latest MinIO snapshot falls back to previous with extra RPO recorded.
* Cost: Hetzner hours under 4 EUR per drill in the report."""},
Demo="""Reviewer opens the drill report, reads per-service restore times and the smoke results table, then runs `restic snapshots -r <minio-repo>` to see the nightly cadence. Under a minute.""",
**{"Edge cases": """* Object storage provider down: secondary copy used; documented.
* Encryption key missing on the drill host: smoke fails with `CRYPTO_UNAVAILABLE` and the report names the fix.
* Very large buckets: incremental restore by tenant prefix documented.
* Production writes during the drill: compare against snapshot time."""},
Dependencies="""PAP-30, PAP-37, PAP-26 (hard). Soft: PAP-50, PAP-53, PAP-86, PAP-96, PAP-140, field-encryption issue.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Edge Case Hunter).""",
Size="""M""")

add("data-layer","tenant-lifecycle",
"Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`)",
"Build","P2",2,"Tenant-safe and observable",["Staff","Developer"],
Goal="""Own the tenant state machine around PAP-33's `deleted_at`: request and cancel deletion with a grace period, the archive metadata kept for legal retention, and per-tenant storage and row counters that feed PAP-178's `storageGb` entitlement. The hard-purge job itself (`tenant.purge`: export first, delete rows, files, docs and keys, tombstone) is owned by `security/retention-pii`; this issue triggers it and displays its progress. Merged: the purge half of this gap moved to `security/retention-pii` on 2026-09-17 (FIX-6).""",
Scope="""In:

* States on `tenant`: `active`, `suspended`, `deleted` (soft, `deleted_at`), `purging`, `purged`; grace period default 30 days, configurable per plan.
* Deletion flow: `requestDeletion` sets `deleted_at`, enqueues the PAP-205 export and schedules `tenant.purge` (`security/retention-pii`) at the end of the grace period; `cancelDeletion` clears it; `tenant_archive` (legal minimum: name, owner email, invoice references, dates) is written before the purge runs.
* Quotas: `tenant_usage` (`storage_bytes`, `rows_by_table`, `files`, `users`) refreshed nightly and incrementally on file completion; `checkQuota(tenantId, kind)` helper used by PAP-37 and PAP-35 create procedures; staff usage page.
* Needs Justin gate for purging tenants with paid history in the last 90 days.

Out: the purge job and tombstone (`security/retention-pii`), billing proration (PAP-177), data export format (PAP-205).""",
Spec="""* Purge progress is read from the `security/retention-pii` job run and shown on the staff usage page; a tenant in `purging` is inaccessible to every principal.
* Quota overage: soft limit warns at 80 percent, hard limit blocks new writes of that kind with `QUOTA_EXCEEDED`.
* Archive rows encrypted with the `security/field-encryption` helper.""",
**{"Interface contract": """Provides: tenant states, tables `tenant_archive`, `tenant_usage`, helper `checkQuota`, error `QUOTA_EXCEEDED`, events `tenant.deletion_requested|deletion_cancelled`, oRPC `tenants.usage|requestDeletion|cancelDeletion`. Consumes: entities (PAP-33), jobs (PAP-43), export (PAP-205), files (PAP-37), audit (PAP-38), entitlements (PAP-178), event bus (`contracts/domain-events`), encryption (`security/field-encryption`), purge job and `tenant.purged` event (`security/retention-pii`)."""},
**{"Definition of done": """* Demo tenant deletion requested, export enqueued, grace period fast-forwarded in test, `tenant.purge` (`security/retention-pii`) invoked once and the state reaches `purged` (harness output).
* `cancelDeletion` inside the grace period restores `active` (test).
* Quota: uploading past the hard limit returns `QUOTA_EXCEEDED`; usage page screenshots at 768, 1280, 1920.
* `docs/data/tenant-lifecycle.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: state machine; dependency ordering from the table list; quota thresholds.
* Integration (CI compose): request, cancel, re-request; grace expiry invokes the purge job exactly once (idempotency asserted).
* Permission: customer cannot call `requestDeletion` for another tenant.
* Visual: usage page at three widths."""},
Demo="""Reviewer requests deletion of a test tenant in the staff console, fast-forwards the grace in test, and watches the state move `deleted` to `purging` to `purged` as the `security/retention-pii` job runs. Under 2 minutes.""",
**{"Edge cases": """* User deletes tenant then wants it back within grace: `cancelDeletion` restores `active`.
* Tables added later without a tenant column mapping: the `security/retention-pii` FK-order generator fails the purge dry run; the usage page counts them as unknown.
* Objects still referenced by another tenant (shared templates): reference count check.
* Export older than the grace period: re-export required."""},
Dependencies="""PAP-33, PAP-43, PAP-205 (hard). Soft: PAP-37, PAP-38, PAP-178, `contracts/domain-events`, `security/field-encryption`, `security/retention-pii` (purge job).""",
Agent="""Built by Forge (Schema Wright). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("data-layer","retention-pii",
"Enforce data retention and PII policy: retention per table, scheduled anonymisation jobs, `pii.json` driving audit redaction and OTel filters",
"Build","P2",3,"Tenant-safe and observable",["Staff","Developer"],
Goal="""Turn declared sensitivity into enforcement: retention durations declared next to the schema (`@retention`) are applied nightly by anonymisation and deletion jobs, `pii.json` from PAP-41 drives audit redaction and OTel filtering at runtime, and the release digest reports what was purged. PAP-41 generates flags and PAP-38 keeps audit for 24 months, but nothing enforces retention; PAP-126 compliance flags gain a consumer.""",
Scope="""In:

* Schema tags `@retention <duration> <delete|anonymise>` and `@pii` parsed by the PAP-41 generator into `retention.json` and `pii.json`.
* Job `retention.apply` (PAP-43) per table: delete or anonymise rows older than the duration using deterministic pseudonyms (`user_<hash>`) so joins survive; batched, resumable, audited in summary mode.
* Runtime loaders: PAP-38 `audit_redactions` synced from `pii.json` on deploy; PAP-40 span processor reads the same file.
* Tenant-level overrides within legal bounds (`tenant.settings.retention`) exposed on a staff settings page; PAP-126 compliance profile picks defaults (for example 7-year finance retention).
* Report section in the PAP-88 digest: rows anonymised and deleted per table.

Out: DSAR request handling UI (identity privacy issue), legal texts.""",
Spec="""* Finance tables (PAP-179, PAP-180) are `retain 7y` and immutable; the job refuses to touch tables tagged `@immutable`.
* Anonymisation never touches `audit_event` content beyond redaction rules.
* Dry run prints counts per table; CI runs the dry run on the `load` seed to catch misconfigured durations.
* Durations parsed as ISO 8601 (`P30D`, `P7Y`).""",
**{"Interface contract": """Provides: tags, `retention.json` schema, job `retention.apply`, `retention.dryRun` procedure, settings page, digest section. Consumes: generator and `pii.json` (PAP-41), redactions (PAP-38), span filter (PAP-40), jobs (PAP-43), compliance profile (PAP-126), digest (PAP-88)."""},
**{"Definition of done": """* Tagging a fixture table `@retention P30D anonymise` and seeding old rows results in pseudonymised rows after the job (test); `@immutable` table untouched.
* `pii.json` change redeploys redactions without a migration (test).
* Dry run in CI on the `load` seed; settings page at 768, 1280, 1920; digest section rendered once.
* `docs/data/retention.md`; CHANGELOG; Linear comment."""},
**{"Test plan": """* Unit: duration parsing; pseudonym determinism; refusal on `@immutable`.
* Integration (CI compose): job over 100k rows batched and resumable; audit summary events written; redaction sync reloads.
* Static: every tenant table has a retention tag or an explicit `@retention forever` (lint).
* Visual: settings page at three widths."""},
Demo="""Reviewer runs `pnpm retention:dry-run` to see per-table counts, then `pnpm jobs:run retention.apply --table contact --now` on the demo seed and opens Studio to see old contacts pseudonymised while recent ones are intact. Under 90 seconds.""",
**{"Edge cases": """* Row referenced by a retained finance document: anonymised, never deleted.
* Tenant override longer than legal maximum: rejected with the bound.
* Job interrupted: resumes from the last batch.
* New PII column without a tag: lint fails the PR."""},
Dependencies="""PAP-41, PAP-38, PAP-43 (hard). Soft: PAP-40, PAP-126, PAP-88.""",
Agent="""Built by Forge (Schema Wright) with Quill on policy wording. Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

# ============================ forge ============================
add("forge","non-linux-runners",
"Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets",
"Infra","P1",2,"CI runs on both forges",["Developer"],
Goal="""Provide the runners PAP-19, PAP-20, PAP-156 and PAP-73 silently require: GitHub-hosted macOS runners for Xcode builds, notarisation and VoiceOver checks, and a self-hosted Windows VM registered to both forges for NVDA screen-reader tests and MSI signing, with spend caps and the secrets each needs. PAP-50 sizes Linux docker runners only; iOS builds and screen-reader CI cannot run anywhere today.""",
Scope="""In:

* GitHub: `macos-14` usage policy (tags and `workflow_dispatch` only, plus a nightly a11y job), spending limit set in org billing, reusable workflow `imagine-os/paperos-infra/.github/workflows/macos-job.yml` with Xcode selection and simulator boot; cost report job posting monthly minutes to Linear.
* Windows: Hetzner Windows Server VM (or a Windows 11 VM on a dedicated host) with the GitHub runner and Forgejo runner both installed as services, labels `windows-self-hosted`, NVDA installed with the `nvda-remote` speech viewer for PAP-156, `signtool`, PowerShell scripts for reset between jobs.
* Secrets: signing (code-signing issue) and Apple keys wired; `ops/forge/secrets-manifest.yml` updated.
* Portability notes added to PAP-50's guide; `if` guards pattern for jobs that need these runners.

Out: buying Apple accounts (code-signing issue files the ask), Android emulator capacity (Linux with KVM in PAP-50).""",
Spec="""* macOS budget: 300 minutes per week; jobs fail fast if the monthly cap is within 10 percent.
* Windows VM snapshot restored nightly; runner ephemeral mode for GitHub; Forgejo runner `capacity: 1`.
* NVDA speech log captured to an artifact for PAP-156 assertions.
* All non-Linux jobs skip cleanly on Forgejo when the label is absent.""",
**{"Interface contract": """Provides: labels `macos-14` (hosted) and `windows-self-hosted`, reusable macOS workflow, NVDA speech-log artifact name `nvda-speech.log`, secrets names in the manifest, monthly cost report. Consumes: Forgejo runner registration (PAP-50), secrets (PAP-51), Hetzner project (PAP-25), signing keys (code-signing issue, soft). Consumed by PAP-19 child 2, PAP-20 child 1, PAP-73, PAP-156, code-signing issue."""},
**{"Definition of done": """* iOS simulator build (PAP-20) and macOS installer (PAP-19) jobs run green on hosted macOS with the cost cap in place (run URLs).
* Windows VM shows online in both forges; a job runs `signtool /?` and launches NVDA producing a speech log artifact.
* Cost report posted once; `docs/engineering/ci-runners.md`; Linear comment; changelog under Infra."""},
**{"Test plan": """* Workflow: dispatch the macOS reusable workflow with `xcodebuild -version`; assert minutes recorded.
* Windows: job runs a PowerShell smoke (`signtool`, NVDA start and stop, speech log non-empty).
* Portability: PAP-50 checker recognises the labels and guards.
* Cost: simulated cap breach makes the job fail fast with a clear message."""},
Demo="""Reviewer opens the Actions tab, dispatches `ci-runners-smoke`, and watches a macOS job print the Xcode version while the Windows job uploads `nvda-speech.log`; then opens the cost report comment on this issue. Under 5 minutes of wall clock, 1 minute of attention.""",
**{"Edge cases": """* Hosted macOS queue delays: jobs have a 60-minute timeout and are not on the PR critical path.
* Windows VM update reboots mid-job: job retried once by the workflow.
* NVDA licence and telemetry prompts: pre-configured in the snapshot.
* Forgejo has no macOS runner: jobs guarded; documented gap in the DR drill."""},
Dependencies="""PAP-50, PAP-25 (hard). Soft: PAP-51, code-signing issue. Unblocks PAP-20 (iOS CI), PAP-73, PAP-156; feeds PAP-19.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for runner isolation).""",
Size="""M""")

add("forge","template-upgrade",
"Define the template upgrade path for generated apps: versioned `paperos-template` releases, `paperos upgrade` applying template diffs, and an internal package registry for `@paperos/*`",
"Build","P1",2,"CI runs on both forges",["Developer","Agent"],
Goal="""An app created from template v0.3 receives the v0.5 shell fixes without a manual merge. PAP-22 clones a pinned tag and PAP-51 says packages are published later to an internal registry; the brief's "build everything in, remove later" only works if downstream apps keep receiving the platform. This issue versions the template, publishes `@paperos/*` to the Forgejo npm registry, and ships `paperos upgrade`.""",
Scope="""In:

* Template releases `template-v<semver>` from PAP-52 with a machine-readable `template-manifest.json` (files owned by the template versus app-owned, codemods per version).
* Publishing `@paperos/*` packages to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) on release; `.npmrc` template; GitHub Packages mirror.
* `paperos upgrade [--to <version>] [--dry-run]` in PAP-22's CLI: bumps `@paperos/*` versions, applies template-owned file diffs with three-way merge (`git merge-file`), runs codemods (`jscodeshift`), leaves conflicts marked, records `.paperos/template-version`.
* `forge upgrade-check` reporting each imagine-os repo's template version versus latest; weekly Linear comment on a pinned issue.
* Documentation of the ownership boundary in PAP-24's guide.

Out: automatic merges without review, Linux package signing.""",
Spec="""* Template-owned paths listed in `template-manifest.json` (`ops/ci/*`, `packages/config-*`, `.claude/rules/*`, `CLAUDE.md` header block); app-owned paths never touched.
* Codemods are versioned scripts `codemods/<from>-<to>.ts` with tests on fixtures.
* Upgrade opens a PR via PAP-49 template with the changelog excerpt from `feed.json`.
* Registry auth via the PAP-48 bot token in CI and the developer's Forgejo token locally.""",
**{"Interface contract": """Provides: `template-manifest.json` schema, tag `template-v*`, npm registry URL and `.npmrc` template, `paperos upgrade`, `forge upgrade-check`, `.paperos/template-version`. Consumes: releases and feed (PAP-52), CLI (PAP-22), Forgejo packages (PAP-45), bootstrap (PAP-51), bot tokens (PAP-48), PR template (PAP-49), repo list (PAP-47 `repos.yml`). Consumed by PAP-29 (drill scenario: upgrade a drill app), every generated app."""},
**{"Definition of done": """* Create an app at `template-v0.1.0-test`, release `template-v0.2.0-test` with a shell fix and a codemod, run `paperos upgrade`: PR opened with the fix applied, codemod run, app-owned files untouched (recording).
* `@paperos/ui` installs from the Forgejo registry in a fresh app (log).
* `forge upgrade-check` lists repos with versions; Vitest for manifest ownership rules, three-way merge conflicts, codemod fixtures.
* `docs/engineering/template-upgrades.md`; CHANGELOG; Linear comment; PAP-24 guide section added."""},
**{"Test plan": """* Unit: ownership classifier on path fixtures; merge with clean, conflicting and deleted-file cases; codemod fixture tests.
* Integration nightly: fixture app upgraded across two test releases on the sandbox repo; PR body validated by `pr-lint`.
* Registry: publish a prerelease to Forgejo npm in CI and install it in a scratch project.
* Static: `template-manifest.json` validated in Gate 1."""},
Demo="""Reviewer runs `paperos upgrade --dry-run` in a demo app and reads the plan (packages bumped, files updated, codemods), then without `--dry-run` and opens the resulting PR with the changelog excerpt. Under 2 minutes.""",
**{"Edge cases": """* App modified a template-owned file: three-way merge; conflicts left for review, never overwritten.
* Skipped versions: codemods applied in sequence.
* Registry down: `pnpm install` falls back to the GitHub Packages mirror.
* Template major bump: upgrade refuses without `--allow-major` and links the ADR."""},
Dependencies="""PAP-22, PAP-52 (hard). Soft: PAP-45, PAP-47, PAP-48, PAP-49, PAP-51. Consumed by PAP-29, all generated apps.""",
Agent="""Built by Forge (lead). Reviewed by Sentinel (Code Reviewer) and Quill (guide section).""",
Size="""M""")


# FIX-6 (2026-09-17): merged duplicates are filtered out so create_issues.py never creates them.
MERGED = {
    "gap/data-layer/event-bus": "contracts/domain-events",
    "gap/data-layer/field-encryption": "security/field-encryption",
    "gap/data-layer/platform-dr": "security/platform-dr",
    "gap/data-layer/rate-limit-idempotency": "contracts/idempotency-rate-limits",
    "gap/data-layer/retention-pii": "security/retention-pii",
    "gap/forge/template-upgrade": "gp/app-shell/upgrade",
}
GAPS = [g for g in GAPS if f"gap/{g['project']}/{g['slug']}" not in MERGED]
