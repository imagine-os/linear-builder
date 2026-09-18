---
identifier: "PAP-673"
title: "Security telemetry: event catalogue, emitters in API, auth, orchestrator, proxy and Postgres, and the `security_event` table"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-356"
children: []
blockedBy: ["PAP-38", "PAP-40", "PAP-97"]
blocks: ["PAP-674"]
key: "r4/quality/security-event-catalogue-emitters"
url: "https://linear.app/paperos/issue/PAP-673/security-telemetry-event-catalogue-emitters-in-api-auth-orchestrator"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:29.926Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-673: Security telemetry: event catalogue, emitters in API, auth, orchestrator, proxy and Postgres, and the `security_event` table

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-356: define the security event catalogue once as Zod types in `packages/core`, emit the events from every boundary the threat model names (Better Auth hooks, oRPC middleware, RLS denials, orchestrator, egress proxy, webhook receivers, backup jobs) and persist S0 events in Postgres so detection survives a Loki outage. Rules, routing and the digest are the sibling child; this child makes the events exist and flow.

**Scope**

* In: `packages/core/src/security-events.ts` (catalogue, `emitSecurityEvent()`), emitters wired into `packages/auth` hooks (PAP-223), `apps/api` oRPC middleware (PAP-35, PAP-267), a Postgres log parser job for `42501` via Loki (PAP-40), orchestrator and broker emitters (PAP-298, PAP-300, PAP-299, PAP-111), webhook receivers (PAP-97, PAP-177), backup metrics (PAP-354); migration `security_event`; `docs/security/telemetry.md` section "Events".
* Out: alert rules, Linear routing, Needs Justin cards, weekly digest, Grafana dashboard (sibling child); SIEM products; user-facing notifications (PAP-220).

**Spec**

* Catalogue of at least 25 events named `security.<area>.<name>` with `severity: S0|S1|S2`, `fields` Zod schema and `source` enum; areas `auth`, `authz`, `db`, `agent`, `webhook`, `files`, `backup`, `scan`, `keys`; the list in PAP-356 Spec is the minimum set.
* `emitSecurityEvent(event)` writes an OTel log record with attribute `paperos.security.event=<name>` and, for S0, inserts into `security_event(id, name, severity, tenant_id?, actor_id?, fields jsonb, request_id, at)` in the platform tenant with 13-month retention (PAP-355 policy).
* Emitters: `auth.login_failed|login_new_device|passkey_removed|mfa_disabled|impersonation_started|session_revoked_all` from Better Auth hooks; `authz.denied` from the oRPC FORBIDDEN path with procedure and actor; `db.rls_denied` from a Loki query job counting `42501` per role every minute; `db.bypass_used` from PAP-38 when `app.bypass` is set; `agent.*` from the deny-list hook, broker proxy and kill switch; `webhook.signature_invalid|replay_detected`; `files.mime_rejected|sha_mismatch`; `backup.stale|check_failed`; `scan.new_s0_finding` from the PAP-80 nightly; `keys.rotation_overdue` from the PAP-219 runbook cadence file.
* Every emitter is behind a single helper so a missing OTel exporter never throws in the request path; events are sampled never (security events are complete).
* `pnpm security:simulate <scenario>` produces each event class against the local stack for the sibling's rule tests.

**Interface contract**

* Provides: `emitSecurityEvent()`, `SecurityEvent` union type and JSON Schema, table `security_event`, `pnpm security:simulate`, the catalogue table in `docs/security/telemetry.md`.
* Consumes: PAP-40 collector and Loki, PAP-38 audit bypass hook, the emitter host issues listed in Scope (soft: interim emitters from API and orchestrator only).

**Definition of done**

* Catalogue with 25+ events validates; JSON Schema generated and committed.
* Every listed emitter fires in an integration test on the compose stack (PAP-42); table of event name to test.
* S0 events appear in both Loki and `security_event` within 5 s; a Loki outage test still records the row.
* `pnpm security:simulate login-burst` produces 25 `auth.login_failed` events (recording).
* Docs section; changelog under "Security"; Linear comment with the catalogue table.

**Test plan**

* Unit: catalogue schema per event; helper never throws when the exporter is down; Loki `42501` parser on fixture log lines.
* E2E: compose stack scenario per emitter; Postgres row assertions for S0.

**Demo**

Run `pnpm security:simulate login-burst` against the local stack, then query `security_event` and the Loki explorer for `paperos.security.event` and see 25 matching records. Under one minute.

**Edge cases**

* Emitter host issue not merged yet (for example PAP-177 Stripe): the emitter ships in this child behind a feature check and is listed as `pending` in the docs table.
* Event flood from a hostile client: emission is unsampled but the sibling's cooldown handles alert noise; Postgres insert batches 100 rows per transaction.
* Tenant context missing (platform-level event): `tenant_id` null is allowed only for `agent.*`, `backup.*`, `keys.*`, `scan.*`.
* PII in event fields: schemas forbid free-text fields except `reason`, which is redacted by PAP-107 `redact()`.

**Dependencies**

Hard: PAP-40, PAP-38. Soft: PAP-223, PAP-35, PAP-298, PAP-300, PAP-299, PAP-111, PAP-97, PAP-177, PAP-354, PAP-355.

**Agent**

Builder: Sentinel (Security Auditor) with Forge (Ops Runner) for the Loki job. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
