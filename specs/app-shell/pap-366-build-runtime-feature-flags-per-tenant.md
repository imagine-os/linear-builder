---
identifier: "PAP-366"
title: "Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: []
blocks: []
key: "gap/app-shell/runtime-flags"
url: "https://linear.app/paperos/issue/PAP-366/build-runtime-feature-flags-per-tenant-and-per-audience-flags-with"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:01:27.454Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-366: Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards

**Goal**

Replace the env-only `VITE_FLAGS` bootstrap from PAP-17 with a real flag service in `packages/core/flags`: flags stored in Postgres per tenant and per audience, evaluated server-side and streamed to clients, with kill switches, segment targeting and a `flags:` guard in page specs, so risky work lands behind a flag (PAP-88) and in-app targeting (PAP-195) has a home. PAP-214 chose to own a flag service; this issue builds it.

**Scope**

In:

* Tables `flag` (`key`, `description`, `kind boolean|variant`, `default`, `killSwitch`, `owner`) and `flag_rule` (`flag_id`, `tenant_id` nullable, `audience` nullable, `segment_id` nullable, `value`, `priority`).
* Evaluator `evaluate(flags, ctx: { tenantId, principal, audience, segments })` deterministic and pure; server evaluates and ships a `FlagSnapshot` to the client on session start and through the PAP-36 shape `flag_rules`.
* Hooks `useFlag(key)`, `useVariant(key)`; server helper `flagGuard(key)` for procedures; spec `flags: { requires: [...] }` enforced by PAP-118 validator and PAP-120 codegen (page renders `ui.flagDisabled` state).
* Settings page `/settings/flags` for staff with kill switches and per-tenant overrides; audit events on every change.
* Env `VITE_FLAGS` remains as a local override in development only.

Out: experimentation statistics, remote config of non-boolean settings (tenant settings own that).

**Spec**

* Evaluation order: kill switch, tenant rule, audience rule, segment rule, default; highest `priority` wins within a level.
* Snapshot is versioned (`etag`); clients refetch on `flags.changed` event (data-layer event bus) or on shape update.
* Flag keys are `domain.feature` and must be declared in `flags.yaml` in the repo; undeclared keys fail typecheck via a generated `FlagKey` union.
* Kill switch flips every rule to `false` within 5 s on all clients; measured.
* Segments resolved through PAP-195 when present; otherwise only tenant and audience rules apply.

**Interface contract**

Provides: `useFlag`, `useVariant`, `flagGuard`, `FlagKey` type, tables above, oRPC `flags.list|update|kill`, spec section `flags:`, event `flags.changed`, `ui.flagDisabled` state name for PAP-120. Consumes: `VITE_FLAGS` bootstrap and env schema (PAP-17), oRPC host (PAP-35), tables and migrations (PAP-33, PAP-32), `can()` for the settings page (PAP-59), shapes (PAP-36), segments (PAP-195, soft), event bus (`contracts/domain-events`, soft).

**Definition of done**

* Flip a flag for one tenant and see the page change without reload; kill switch propagates within 5 s (recording).
* Page spec with `flags.requires` renders the disabled state when off (codegen test).
* Vitest for the evaluator across rule combinations; `FlagKey` typecheck fails on an undeclared key.
* Settings page screenshots at 375, 768, 1280, 1920; audit events present; `docs/platform/flags.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: evaluator table covering kill, tenant, audience, segment and default with conflicting priorities; snapshot etag changes only when rules change.
* Integration (CI compose): `flags.update` as staff writes an audit event; `callAs(customer)` forbidden.
* E2E: Playwright toggles a flag in settings and asserts the dashboard element appears; kill switch timing measured.
* Static: generated `FlagKey` union check in Gate 1.
* Visual: settings page at four widths, light and dark.

**Demo**

Reviewer opens `/settings/flags`, turns on `dashboard.newChart` for the Acme tenant, switches to a customer tab and sees the new chart appear, then hits Kill and watches it vanish within seconds. Under 90 seconds.

**Edge cases**

* Flag referenced by a spec but deleted: validator error names the page.
* Offline client: last snapshot used; flags never default to on when unknown.
* Two staff edit the same flag: last write wins with both audit events.
* Thousands of tenants with overrides: rules indexed by `(flag_id, tenant_id)`.

**Dependencies**

PAP-17, PAP-33, PAP-35 (hard). Soft: PAP-36, PAP-59, PAP-118, PAP-120, PAP-195, `contracts/domain-events`. Consumed by PAP-88, PAP-195, PAP-178.

**Agent**

Built by Forge (Platform Engineer) with Iris on the settings page. Reviewed by Sentinel.

**Size**

M
