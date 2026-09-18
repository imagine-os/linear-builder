---
identifier: "PAP-674"
title: "Security telemetry: rules engine, S0 routing to the pinned alerts issue and Needs Justin, weekly digest and Grafana dashboard"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-356"
children: []
blockedBy: ["PAP-97", "PAP-673"]
blocks: ["PAP-89", "PAP-895", "PAP-896", "PAP-900"]
key: "r4/quality/security-alert-rules-routing-digest"
url: "https://linear.app/paperos/issue/PAP-674/security-telemetry-rules-engine-s0-routing-to-the-pinned-alerts-issue"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:26.347Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-674: Security telemetry: rules engine, S0 routing to the pinned alerts issue and Needs Justin, weekly digest and Grafana dashboard

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-356: turn the event stream into decisions. A small rule evaluator reads `ops/security/alerts.yaml`, routes S0 hits to the pinned `PAP-SECURITY-ALERTS` issue (and to a PAP-94 decision card when the rule says `page`), accumulates S1 and S2 into a Sunday digest, and renders the `Security` Grafana dashboard, so Justin hears about an attack within five minutes and about everything else once a week.

**Scope**

* In: `ops/security/alerts.yaml` with Zod schema, evaluator `apps/api/src/security/alerts.ts` (worker job on PAP-43 or Grafana alerting where simpler), Linear routing through the PAP-97 `linearComment` helper and the pinned issue id in orchestrator config, `ops/security/alert-suppressions.yaml`, weekly digest job and `templates/security-digest.md`, `ops/observability/dashboards/security.json`, `docs/security/telemetry.md` sections "Rules" and "Digest".
* Out: the events and emitters (sibling child), incident handling steps (PAP-219 playbook), the release digest itself (PAP-89 links this digest).

**Spec**

* Rule shape `{ id, event, window, threshold, groupBy, severity, route: alert|digest, page?: true, runbook, cooldownMin: 30 }`; initial rules are the PAP-356 list: `auth.login_failed > 20 per account per 10 min` or `> 200 per IP`, any `agent.canary_seen` (page), any `db.bypass_used` outside impersonation and purge paths, `db.rls_denied > 5 per minute` from `paperos_app`, `webhook.signature_invalid > 3 per hour`, `backup.stale`, `agent.credential_anomaly` on a `destructive` host (page), `scan.new_s0_finding`.
* Evaluator runs every minute over Loki (or `security_event` for S0) with sliding windows; a hit posts one comment on `PAP-SECURITY-ALERTS` and edits it in place with a counter during the cooldown (PAP-97 pattern); `page` rules also call `requestDecision()` (PAP-94) with containment options from the runbook, priority Urgent; containment defaults (revoke-all via PAP-300, pause claiming via PAP-283 drain) apply immediately and are reversible.
* Digest job Sunday 18:00 UTC renders counts per event, top actors, new findings, rotation status, backup and drill status, open S0s; posted as a comment on the alerts issue and linked from PAP-89 section 3.
* Suppressions file with expiry, same rules and checker as PAP-80 waivers; expired suppressions fail the job.
* Dashboard: events per minute by area, top rules firing, open S0 count, backup age, rotation status.

**Interface contract**

* Provides: `alerts.yaml` schema, `evaluateRules()`, pinned issue id `security.alertsIssueId` in orchestrator config, digest template, dashboard JSON, `securityDigestHealth` summary for PAP-89.
* Consumes: sibling catalogue and `security_event`, PAP-97 Linear helper, PAP-94 `requestDecision()`, PAP-43 jobs, PAP-40 Grafana, PAP-300 `revoke --all`, PAP-283 `/admin/drain`.

**Definition of done**

* Induced scenarios on staging each route within 5 minutes: 25 failed logins (alert), canary in an outbound request (alert plus Needs Justin card), invalid Stripe signature (digest), paused backup job (alert after threshold); table with timestamps.
* Alert storm test: 500 hits in a minute produce one comment edited in place.
* One weekly digest posted with real staging data; dashboard screenshot at 1280 px light and dark.
* Docs sections; changelog under "Security"; Linear comment with the scenario table.

**Test plan**

* Unit: window and threshold arithmetic with a fake clock, cooldown edit-in-place, suppression expiry, digest renderer snapshot.
* E2E: staging induced scenarios from `pnpm security:simulate`; Needs Justin card appears for the canary case and is answerable with `approve`.

**Demo**

Run `pnpm security:simulate canary-exfil` against staging, watch the alert comment appear on `PAP-SECURITY-ALERTS`, the decision card land in Needs Justin and the Grafana panel spike; open last Sunday's digest. Ninety seconds.

**Edge cases**

* Justin on holiday: `page` cards keep the PAP-94 48 h default except containment defaults, which apply immediately and are reversible.
* Loki down: S0 evaluation continues from `security_event`; a `telemetry.degraded` event is itself S1 and appears in the digest.
* Rule references an event the catalogue lacks: schema validation fails CI with the rule id.
* Agent legitimately hitting deny rules while exploring: `agent.deny_list_hit` is digest-only unless three S0 hits in one session (PAP-111 kill).

**Dependencies**

Hard: PAP-673, PAP-97. Soft: PAP-94, PAP-43, PAP-40, PAP-300, PAP-283, PAP-89.

**Agent**

Builder: Sentinel (Security Auditor) with Forge (Ops Runner) for the dashboard. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/security-event-catalogue-emitters` = PAP-673.
