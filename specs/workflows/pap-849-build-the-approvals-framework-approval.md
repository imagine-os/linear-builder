---
identifier: "PAP-849"
title: "Build the approvals framework: approval requests, policies (thresholds, roles, quorum), delegation, SLA escalation and adoption by the five existing approval steps"
project: "workflows"
projectName: "Workflows, Approvals, Forms, Documents & E-Signature"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Workflow contract and approvals"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-43", "PAP-59", "PAP-136", "PAP-229", "PAP-565", "PAP-725", "PAP-847", "PAP-848"]
blocks: ["PAP-850", "PAP-851", "PAP-861"]
key: "r4/workflows/approvals-framework"
url: "https://linear.app/paperos/issue/PAP-849/build-the-approvals-framework-approval-requests-policies-thresholds"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:46.522Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-849: Build the approvals framework: approval requests, policies (thresholds, roles, quorum), delegation, SLA escalation and adoption by the five existing approval steps

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Replace five bespoke approval steps with one: an `approval_request` entity with a policy (who may approve, thresholds by `Money`, quorum, order), decisions with reasons, delegation while away, SLA escalation through notifications, and adapters so PAP-94 Needs Justin, PAP-401 social posts, PAP-408 referral rewards, PAP-185 expenses and PAP-400 payroll totals all become approval requests with the same inbox and audit shape.

**Scope**

In: `packages/workflows/src/approvals/`: tables `approval_policy` (`subjectType`, `rules: [{ when: FilterTree, approvers: RoleRef|PrincipalRef[]|'manager-of:<field>', quorum, order: parallel|sequence, sla }]`), `approval_request` (`subject EntityRef`, `policy_version`, `status pending|approved|rejected|expired|cancelled`, `amount Money?`, `summary`, `preview jsonb`), `approval_decision` (`approver`, `decision`, `reason`, `on_behalf_of?`). `ApprovalPort.request(subject, { policyKey, amount, summary, preview })` resolves approvers now (snapshot) and emits `approval.requested`; `decide` enforces quorum and order; `delegate(from, to, range)` with PAP-227 attribute check; `expire` job with escalation chain. Adapters: `pm.needs-justin` (PAP-94 `/approve` comment grammar becomes a decision), `social.post` (PAP-401 queue reads `approval_request`), `referral.reward` (PAP-408), `expense` (PAP-185 threshold policy), `payroll.run` (PAP-400 typed-total as a `confirmation` field on the decision). Console page `/console/approvals` as a saved list view (PAP-169) with decision drawer, preview rendering (diff, document, post), bulk approve within policy limits.

Out: Workflow engine (this framework works standalone and as a step kind). Portal customer approvals (v0.3: customers approving quotes is a signature).

**Spec**

* Segregation of duties: the requester can never be an approver of their own request even if a role matches; policies can require `distinctFrom: [requester, creator]`
* Money thresholds compare in the tenant reporting currency using PAP-766 when present, else refuse cross-currency policies at publish
* Decisions are immutable rows; changing one's mind is a new decision that supersedes within the window the policy allows; the audit trail (PAP-38) shows both
* SLA: `sla.hours` then escalate to `escalateTo` (manager-of, role) with notification kind `approval.escalated`; a second breach auto-rejects or auto-approves only when the policy says so explicitly
* Everything decided through Slack (PAP-325) or email links uses signed one-time tokens bound to the approver principal; no anonymous approval

**Interface contract**

Provides: `ApprovalPort` default adapter, tables and `approvals.*` procedures, the five adapters, `/console/approvals` page, notification kinds `approval.*`, `<ApprovalCard/>` component. Consumes: permission engine and attribute policies (PAP-59, PAP-227), notifications (PAP-136), jobs (PAP-43), audit (PAP-38), list view (PAP-169), Slack channel (PAP-325), `Money` (PAP-302). Consumed by: PAP-94, PAP-401, PAP-408, PAP-185, PAP-400 (adopters), commerce purchasing, assistant `send|money` tool classes, engagement (refund approvals).

**Definition of done**

* The five adopters open and decide through the framework in the demo tenant; each adopter issue receives a comment naming the adapter file and the removed bespoke code
* Quorum, sequence, delegation, expiry and escalation each covered by an integration test; segregation-of-duties fuzzed
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: policy resolution over 20 fixture policies; quorum math; supersede window; token binding.
* Integration: expense over threshold → request → manager approves via email token → ledger posting (PAP-394) proceeds; below threshold auto-approves; SLA breach escalates.
* E2E: approvals page bulk approve, keyboard-only decision drawer, screenshots.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Submit a $700 expense as staff; the manager gets a Slack message, approves with a reason; the approvals page shows the trail; a second request is delegated to a colleague while the manager is on leave.

**Edge cases**

* Approver leaves the organisation (membership removed, PAP-58): pending requests re-resolve approvers from the policy and note the change
* Policy edited while requests are pending: pending requests keep `policy_version`; the page marks them "under a previous policy"
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-848 and PAP-847 (hard), PAP-59 and PAP-227 (hard), PAP-136, PAP-43, PAP-38 (hard), PAP-325 (soft), PAP-766 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/business-core/fx-rates` = PAP-766, `r4/workflows/contract-publish` = PAP-847, `r4/workflows/workflow-model` = PAP-848.
