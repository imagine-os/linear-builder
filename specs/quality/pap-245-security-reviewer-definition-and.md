---
identifier: "PAP-245"
title: "Security reviewer definition and security.json ingestion"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-81"
children: []
blockedBy: ["PAP-243"]
blocks: ["PAP-85", "PAP-88", "PAP-241"]
key: "quality/review-agents/security"
url: "https://linear.app/paperos/issue/PAP-245/security-reviewer-definition-and-securityjson-ingestion"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:40.934Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-245: Security reviewer definition and security.json ingestion

**Goal**

Write and calibrate the security reviewer: it reads PAP-80's `security.json`, checks the threat model controls, hunts authorisation and tenant-isolation mistakes the scanners cannot see, and respects waivers.

**Scope**

* In: `.claude/agents/reviewers/security.md` embedding PAP-79 `security.md` and the control ids from the threat model (`controls.yaml`), `security.json` ingestion so scanner findings are referenced not duplicated, waiver awareness (`ops/security/waivers.yaml`), seeded authz bug fixture, calibration, cost report.
* Out: scanners (PAP-80), harness (sibling).

**Spec**

* Checks: `authorize()` on every new oRPC procedure, `withTenant` before queries, RLS session variables, input validation, secrets in code or logs, SSRF and injection, file uploads, rate limits, dependency risk from `security.json`, sensitive logging; each finding cites a rubric ID and, where applicable, a `SEC-*` control.
* Ingestion: scanner findings appear in the review as a summary table with links, marked `from: scanner`; the reviewer adds findings only for what scanners missed; waived findings show the waiver expiry.
* Severity: authz and tenant leaks S0; unvalidated input on mutating routes S1.

**Interface contract**

* Provides: `ReviewerDefinition` for security; `securitySummary` block consumed by PAP-89.
* Requires: sibling harness; PAP-80 `security.json`; threat model `controls.yaml`; PAP-79 rubric.

**Definition of done**

* Seeded oRPC procedure without `authorize` and a seeded cross-tenant query are caught at S0; a waived OSV finding is shown as waived, not blocking.
* Calibration agreement at or above 0.8 on the security cases.
* Cost under $2 average per PR across 10 PRs.
* Docs section "Security reviewer".

**Test plan**

* Integration: seeded PRs through the harness; waiver expiry path.
* Calibration: `pnpm review:calibrate --reviewer security`.

**Demo**

Open the seeded "missing authorize" PR: the review shows S0 with the procedure line, the `SEC-API-01` control and a suggestion diff adding the middleware. Under one minute.

**Edge cases**

* `security.json` missing (scanner errored): reviewer posts S1 "scanner results missing" and continues.
* False positive from Semgrep: reviewer may recommend a `nosemgrep` with expiry, never approve silently.

**Dependencies**

Sibling harness child (hard). Soft: PAP-80, threat model issue.

**Agent**

Built by Sentinel (Security Auditor sub-agent). Reviewed by Atlas.

**Size**

S.
