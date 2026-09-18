---
identifier: "PAP-893"
title: "Publish @paperos/contract-platform-ops v0.1 with manifest"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Spec"
priority: 2
surfaces: ["Developer"]
milestone: "Ops contract, super-admin console and status page"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-55", "PAP-264", "PAP-279", "PAP-302", "PAP-303", "PAP-305", "PAP-366", "PAP-433", "PAP-556"]
blocks: ["PAP-894", "PAP-895", "PAP-897", "PAP-900", "PAP-906", "PAP-907"]
key: "r4/platform-ops/contract-publish"
url: "https://linear.app/paperos/issue/PAP-893/publish-paperoscontract-platform-ops-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:18.103Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-893: Publish @paperos/contract-platform-ops v0.1 with manifest

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec M

**Goal**

Publish `@paperos/contract-platform-ops` v0.1 and the `platform-ops` module manifest so every other module codes against a versioned package instead of `packages/platform-ops, packages/analytics, apps/web/src/admin` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays in the project's Build issues. Swap risk is declared `medium` and kind `runtime`, which decides how much of the swap playbook a rewrite must follow. This is a new module: the contract is written before the implementation, so the Build issues in this project consume it from day one rather than being retrofitted.

**Scope**

In: `packages/contracts/platform-ops/` published as `@paperos/contract-platform-ops` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`. `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-platform-ops', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Sentinel', project: 'platform-ops' }`, `swapRisk: 'medium'`, `kind: 'runtime'`, plus the generated `module.manifest.json`. `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/platform-ops.md` (a `typedoc` stub until the docs generator PAP-445 lands). A `## Module boundary` paragraph on this project's model or umbrella issue naming the contract version each Build issue implements.

Out: Runtime behaviour, React, Drizzle tables, network calls. The conformance suite and the kernel binding (own issues). Changing contract-zero types; anything missing there is filed against PAP-302, PAP-279 or PAP-303.

**Spec**

* Ports and schemas exported at v0.1: `PlatformAdminPort` (`tenants`, `overrideEntitlement`, `setFlagRule`, `toggleModule`, `jobs`, `impersonate`) with `TenantSummary`, `Override`; `StatusPort` (`components`, `incidents`, `maintenance`, `subscribe`) with `Incident`, `Component`; `AnalyticsPort` (`track`, `identify`, `defineEvent`, `funnels`, `retention`) with `EventSchema`, `Funnel`; `ReplayPort` (`capture`, `list`, `mask`); `ExperimentPort` (`define`, `assign`, `expose`, `readout`) with `Experiment`, `Assignment`; `AbusePort` (`checkSignup`, `quarantine`, `reportAbuse`) and `CaptchaPort` (`verify`) with `RiskScore`; `HealthPort` (`scoreTenant`, `signals`) and `CompliancePort` (`controls`, `evidence`, `profileFor`, `enforce`) with `Control`, `Evidence`, `ComplianceProfile`; `ResidencyPort` (`regionFor`, `route`); slots `admin.nav`, `admin.tenant.tabs`, `trust.sections`
* Events declared with `defineTopic()` (payload schemas, version 1): `platform.tenant.overridden`, `platform.flag.changed`, `status.incident.opened`, `status.incident.updated`, `status.incident.resolved`, `analytics.event`, `experiment.exposed`, `abuse.flagged`, `abuse.quarantined`, `health.score.changed`, `compliance.evidence.collected`, `compliance.control.failed`
* Requires (manifest `requires[]`): `@paperos/contract-identity` ^0.1 (`platform` audience, MFA step-up, impersonation, attribute predicates); `@paperos/contract-data-layer` ^0.1 (audit, jobs, retention, backups, observability, rate limits); `@paperos/contract-app-shell` ^0.1 (flags, module toggles, error reporting, domains, config); `@paperos/contract-business-core` ^0.1 (entitlements, metering); `@paperos/contract-growth` ^0.1 (attribution collector and consent, segments; optional); `@paperos/contract-quality` ^0.1 (gate artefacts, security telemetry, release state); `@paperos/contract-collab` ^0.1 (notifications, docs); `@paperos/contract-tables` ^0.1 (datasets, dashboards)
* Rules: Zod 4 only, JSON Schema generated and committed; no `z.bigint()` on wire schemas (PAP-302 `Money` codec); one sentence of doc and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`, never hand-written
* Every port method that mutates money, sends a message or signs a document carries `Idempotency-Key` semantics from PAP-304 in its signature (`{ idempotencyKey }` option) so adapters cannot forget it
* Error codes reuse the contracts document catalogue (`NOT_FOUND`, `FORBIDDEN`, `CONFLICT`, `MODULE_DISABLED`, `RATE_LIMITED`); module-specific codes are listed in `errors.ts` with user-facing copy keys (PAP-368)

**Interface contract**

Provides: `@paperos/contract-platform-ops@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.platform-ops`. Consumes: the manifest schema and validator (PAP-433), contract-zero (`@paperos/core/types|filter|events`, PAP-302, PAP-279, PAP-303), the base manifest shape (PAP-264) and the ownership map (PAP-305). Consumed by: every module's per-tenant admin actions, quality release digest (PAP-89), growth (churn-risk segment), business-core (usage and health on billing), assistant (safety evidence), migration (compliance profile in onboarding), engagement and commerce (tenant-facing analytics), and this module's conformance and wire issues.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; `pnpm modules:validate` and `pnpm gen:dep-map` green with the new module present
* Generated JSON Schema, `typedoc` stub and ownership entry committed; `compat-matrix.json` (PAP-440) shows every `requires` resolving
* Sentinel confirms no implementation leaked into the package (no React, no Drizzle, no fetch)
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (ten tenant summaries with overrides and health inputs, three incidents across the status machine with subscribers, twenty event schemas and 5,000 synthetic product events with a funnel and a retention cohort, two experiments with assignments and readouts, eight signup risk cases, sixty controls with evidence rows across pass, fail and manual, four compliance profiles, two region routing cases); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel reads the package top to bottom against `docs/module-system.md` section 2 and the contracts document; every port method has a fixture.

**Demo**

`pnpm modules:validate` prints the `platform-ops` manifest with its provides and requires, `pnpm gen:dep-map` shows the new node with only declared edges, and `docs/platform/contracts/platform-ops.md` renders the port list.

**Edge cases**

* A port needed by a Build issue but missing at v0.1 is added as a minor bump (`0.2.0`) with a fixture, never as a direct import of the implementation
* A type that two contracts both want (for example a scheduling `TimeRange`) goes to contract-zero via PAP-302, not into this package, to avoid a dependency between contracts

**Dependencies**

PAP-433 manifest schema (hard), contract-zero PAP-302, PAP-279, PAP-303 (hard), PAP-264 and PAP-305 (soft, shape only). Unblocks every other issue in this project.

**Agent**

Builder: Sentinel. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
