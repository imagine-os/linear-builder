---
identifier: "PAP-903"
title: "Build automated compliance evidence collection: nightly snapshots of access reviews, backup verification, vulnerability scans, change management gates, incident records and agent policy checks into compliance_evidence with retention and an auditor export"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Compliance evidence, residency and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-43", "PAP-80", "PAP-239", "PAP-298", "PAP-354", "PAP-357", "PAP-563", "PAP-565", "PAP-676", "PAP-712", "PAP-896"]
blocks: ["PAP-904"]
key: "r4/platform-ops/evidence-automation"
url: "https://linear.app/paperos/issue/PAP-903/build-automated-compliance-evidence-collection-nightly-snapshots-of"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-903: Build automated compliance evidence collection: nightly snapshots of access reviews, backup verification, vulnerability scans, change management gates, incident records and agent policy checks into compliance_evidence with retention and an auditor export

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Stop collecting screenshots for auditors: a nightly job that runs each control's `testProcedure` from `controls.yaml`, stores the result and artefact (query output, gate file hash, backup drill report, scan summary, policy diff) in `compliance_evidence` with 7-year retention, flags failed controls as `compliance.control.failed` with a Linear issue, and produces an auditor export (zip with an index) per period.

**Scope**

In: `packages/platform-ops/src/compliance/collectors/`: one collector per evidence kind: `access-review` (memberships and roles snapshot with diffs, PAP-58, PAP-227), `backup` (PAP-354 drill and PAP-30 PITR reports), `vuln-scan` (PAP-80 SAST and dependency audit, PAP-357 DAST summaries), `change-management` (every production release PAP-254 with its gate artefacts PAP-239 and approvals), `incidents` (status incidents and PAP-356 S0 events with response times), `agent-policy` (PAP-298 deny list and PAP-106 allowlist hashes unchanged or diffed), `retention` (PAP-355 job outcomes), `training` (agent character rule versions as the platform equivalent of awareness). `compliance_evidence` (control id, period, collected_at, status pass|fail|manual, artefact file id, summary); job schedule nightly plus on release; failures open a Linear issue on the control owner project via PAP-97 patterns. Auditor export: `compliance.export(period)` zip with `index.json`, control statements, evidence files and hashes, signed manifest; staff page `/admin/compliance` with control status grid and evidence drill-down.

Out: Manual evidence upload workflows beyond a simple attach (v0.3). Auditor portal access.

**Spec**

* Collectors are idempotent per `(control, period)`; re-runs overwrite the same row and keep prior artefacts as versions
* Evidence artefacts are immutable files with hashes; the export manifest lets an auditor verify nothing changed
* A control with no collector is `manual` and appears in the grid for a human to attach evidence, never silently `pass`
* Access review diffs highlight privilege increases and dormant admins (no login 90 days) for review sign-off

**Interface contract**

Provides: collectors, `compliance_evidence` dataset, nightly job, failure issues, auditor export, `/admin/compliance`, `compliance.evidence.collected|control.failed` events. Consumes: controls framework, DR and backups (PAP-354, PAP-30), scans (PAP-80, PAP-357), gate artefacts and releases (PAP-239, PAP-254), security telemetry (PAP-356), agent policies (PAP-298, PAP-106), retention jobs (PAP-355), memberships (PAP-58), jobs (PAP-43), status incidents. Consumed by: PAP-904 (live control status), PAP-89 digest (compliance section), assistant safety evidence, sales.

**Definition of done**

* Nightly run stores evidence for every automated control on staging; a broken control fixture opens an issue; export zip verifies; `/admin/compliance` grid renders with drill-down
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: each collector against fixtures; manifest signing and verification.
* Integration: idempotent re-run; failure → issue; access review diff detection of a privilege increase.

**Demo**

Open `/admin/compliance`, click CC6.1 to see last night's access review diff showing a new admin, then export the quarter and verify the manifest hash offline.

**Edge cases**

* Collector source unavailable (Grafana down): the row is `fail:unavailable` with retry, not `pass`; three consecutive failures escalate
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-896 (hard), PAP-354, PAP-80, PAP-357, PAP-239, PAP-43 (hard), PAP-298, PAP-254, PAP-356 (soft).

**Agent**

Builder: Sentinel. Reviewer: Atlas (Merger).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/platform-ops/compliance-controls` = PAP-896, `r4/platform-ops/trust-center` = PAP-904.
