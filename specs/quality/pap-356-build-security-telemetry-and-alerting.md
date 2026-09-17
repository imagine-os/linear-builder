---
identifier: "PAP-356"
title: "Build security telemetry and alerting: auth anomalies, RLS denials, agent policy and egress denials, canary hits, webhook signature failures and backup age routed to Linear with a weekly security digest"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent", "Developer", "Staff"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-97"]
blocks: ["PAP-89"]
key: "security/security-telemetry"
url: "https://linear.app/paperos/issue/PAP-356/build-security-telemetry-and-alerting-auth-anomalies-rls-denials-agent"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:03.842Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-356: Build security telemetry and alerting: auth anomalies, RLS denials, agent policy and egress denials, canary hits, webhook signature failures and backup age routed to Linear with a weekly security digest

**Goal**

Detection is the STRIDE column nobody has filled: PAP-40 alerts on latency and disk, PAP-80 finds vulnerabilities in code, but nothing watches the running platform for attack or agent misbehaviour. This issue defines security events once, emits them from the API, auth server, orchestrator, proxy and database, evaluates rules, and routes S0 alerts to a pinned Linear issue with Needs Justin escalation and everything else into a weekly digest Sentinel writes.

**Scope**

* In: `packages/core/src/security-events.ts` (Zod event catalogue), emitters in Better Auth hooks (PAP-57/PAP-223), oRPC middleware (PAP-35), RLS denial capture (Postgres log parser for `42501` via Loki), orchestrator and proxy events (PAP-298, PAP-300, PAP-280, PAP-299), webhook receivers (PAP-97, PAP-177), backup metrics (PAP-354); rules engine (Grafana alerting or a small evaluator in the API worker), Linear routing via PAP-97 helper, pinned issue `PAP-SECURITY-ALERTS`, weekly digest job, `docs/security/telemetry.md`.
* Out: SIEM products, WAF, user-facing security notifications (PAP-220 sends new-device emails), incident handling (PAP-219 playbook).

**Spec**

* Event catalogue (`security.<area>.<name>`, severity, fields): `auth.login_failed`, `auth.login_new_device`, `auth.passkey_removed`, `auth.mfa_disabled`, `auth.impersonation_started` (PAP-61), `auth.session_revoked_all`; `authz.denied` (oRPC FORBIDDEN with procedure and actor), `db.rls_denied` (`42501` count per role), `db.bypass_used` (PAP-34 `app.bypass`); `agent.deny_list_hit`, `agent.egress_denied`, `agent.credential_anomaly`, `agent.canary_seen`, `agent.injection_flagged`, `agent.budget_killed` (PAP-111); `webhook.signature_invalid` (Linear, forge, Stripe), `webhook.replay_detected`; `files.mime_rejected`, `files.sha_mismatch` (PAP-37); `backup.stale`, `backup.check_failed`; `scan.new_s0_finding` (PAP-80 nightly); `keys.rotation_overdue` (per PAP-219 runbook cadence).
* Transport: events are OTel log records with `paperos.security.event` attribute exported to Loki (PAP-40) and, for S0, also inserted into `security_event` (Postgres, platform tenant, 13-month retention per PAP-355) so alerts survive a Loki outage.
* Rules (`ops/security/alerts.yaml`): thresholds such as `auth.login_failed > 20 per account per 10 min` or `> 200 per IP per 10 min`; any `agent.canary_seen`; any `db.bypass_used` outside the impersonation and purge paths; `db.rls_denied > 5 per minute` from `paperos_app`; `webhook.signature_invalid > 3 per hour`; `backup.stale`; any `agent.credential_anomaly` for a `destructive` host; `scan.new_s0_finding`; each rule has `severity`, `route: alert|digest`, `runbook` link into PAP-219.
* Routing: S0 posts a comment on `PAP-SECURITY-ALERTS` (created once, pinned in the Quality project) and, when the rule says `page`, creates a Needs Justin decision card (PAP-94) with containment options from the playbook; the queue governor treats security cards as priority Urgent; S1 and S2 accumulate into the weekly digest.
* Digest: Sunday 18:00 UTC job renders `templates/security-digest.md` (counts per event, top actors, new findings, rotation status, backup and drill status, open S0s) posted as a comment on the alerts issue and linked from the PAP-89 release digest.
* Suppression: `ops/security/alert-suppressions.yaml` with expiry, same rules as PAP-80 waivers.

**Interface contract**

* Provides: `emitSecurityEvent(event)` in `packages/core`, catalogue types, `alerts.yaml` schema, pinned issue id in orchestrator config, digest template, Grafana dashboard `Security` (JSON in `ops/observability/dashboards/security.json`).
* Consumers: PAP-89 (digest link), PAP-219 (runbook links, controls `SEC-DETECT-*`), PAP-94 (escalation cards), PAP-113 org chart (agent denials per character), PAP-241 calibration (reviewer false negatives cross-checked with `scan.new_s0_finding`).
* Requires: PAP-40 collector and Loki, PAP-97 Linear helper, PAP-38 for `db.bypass_used` source, emitters in the listed issues (interim: events from API and orchestrator only).

**Definition of done**

* Catalogue with at least 25 events; every listed emitter fires in an integration test.
* Induced scenarios on staging each produce the expected route within 5 minutes: 25 failed logins (alert), a canary in an outbound request (alert plus Needs Justin card), an invalid Stripe signature (digest), a paused backup job (alert after threshold).
* Dashboard screenshot at 1280 in light and dark.
* One weekly digest posted with real data.
* Docs; changelog under "Security"; Linear comment with the scenario table.

**Test plan**

* Unit: rule evaluator thresholds and windows, suppression expiry, digest renderer.
* Integration: Loki query fixtures; Postgres `security_event` writes; Linear helper mocked.
* e2e: staging induced scenarios.
* Visual: dashboard screenshot.

**Demo**

Run `pnpm security:simulate login-burst` against staging, watch the alert comment appear on `PAP-SECURITY-ALERTS` and the Grafana panel spike; then open last Sunday's digest. Ninety seconds.

**Edge cases**

* Alert storms: per-rule cooldown 30 min and one comment edited in place with a counter (PAP-97 pattern).
* Loki down: S0 path via Postgres continues; a `telemetry.degraded` event is itself S1.
* Attacker floods failed logins to spam Justin: only the first alert pages; subsequent ones edit the comment; IP-level rate limits (PAP-35 and the pending data-layer rate-limit issue) throttle the source.
* Agent legitimately hits deny rules while exploring: `agent.deny_list_hit` is digest-only unless three S0 hits in one session (PAP-111 kill).
* Justin on holiday: `page` cards keep the 48 h default rule from PAP-94 except containment defaults, which apply immediately (revoke-all, pause claiming) and are reversible.

**Dependencies**

Blocked by PAP-40, PAP-97, PAP-38. Blocks PAP-89. Soft: PAP-298, PAP-300, PAP-299, PAP-354, PAP-111, PAP-94.

**Agent**

Built by Sentinel (Security Auditor sub-agent) with Forge (Ops Runner) for the dashboard; reviewed by Atlas.

**Size**

M
