---
identifier: "PAP-768"
title: "Finance permission set and role presets: bookkeeper, accountant read-only, payroll admin and billing admin, with the ledger:post and payroll.approve guards in the permission matrix"
project: "business-core"
projectName: "Business Core: Payments, Finance & Payroll"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Ledger and reports"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-59", "PAP-175", "PAP-227"]
blocks: ["PAP-183", "PAP-394", "PAP-400"]
key: "r4/business-core/finance-permissions-and-roles"
url: "https://linear.app/paperos/issue/PAP-768/finance-permission-set-and-role-presets-bookkeeper-accountant-read"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:14.468Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-768: Finance permission set and role presets: bookkeeper, accountant read-only, payroll admin and billing admin, with the ledger:post and payroll.approve guards in the permission matrix

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

Eleven finance specs each invent permissions (`ledger.post`, `payroll.approve`, `billing.manage`, `payments.manage`, `expense.approve`, `reports.read`, `tax.manage`, `documents.*`) and none registers them or says which role gets them. This issue defines the finance permission set once, ships role presets and wires them into the PAP-64 matrix so separation of duties is testable.

**Scope**

In: `packages/finance/src/permissions.ts` registering resources and actions with PAP-59 (`finance.accounts|periods|journal|documents|payments|payroll|expenses|reports|tax|billing` by `read|write|post|approve|export|manage`), role presets `bookkeeper`, `accountant` (read and export only), `payroll_admin`, `billing_admin` layered on the PAP-55 base roles and installed on finance module enablement, separation-of-duties rules (`payroll.approve` never with `payroll.write` on the same principal unless owner; `expense.approve` denied to the submitter), agent principal defaults (draft only), `finance.access.md` matrix, PAP-64 fixtures per role.

Out: row-level restrictions by dimension (v0.3), customer portal permissions (PAP-62).

**Spec**

* Permissions are `resource:action` strings per the contracts document; conditions use PAP-227 attributes (`actor.attributes.character` for agents, `record.created_by` for self-approval denial).
* Presets are `is_system` roles cloned per tenant; owners may edit copies; the matrix test regenerates when a preset changes.
* Every finance procedure declares its permission in its oRPC meta; a Vitest scan fails when a `finance.*` procedure has none.
* Sensitive actions (`ledger.post`, `payroll.approve`, `payments.manage`, `billing.manage`) require a human session or an agent character carrying the exact scope; `X-PaperOS-Reason` mandatory for agents (PAP-38).

**Interface contract**

Provides: permission registry `financePermissions`, presets, `requireFinance(action)` middleware, matrix fixtures, `docs/finance/access.md`. Consumes: permission engine (PAP-59, PAP-227), base roles (PAP-55), matrix generator (PAP-64), audit (PAP-38), agent principals (PAP-60).

**Definition of done**

* Matrix at policy, HTTP and UI level green for the four presets plus owner and a customer principal on every finance page spec; separation-of-duties tests green.
* Procedure scan finds zero unregistered finance procedures; presets installed by `installFinanceRoles(tenantId)` idempotently.
* `docs/finance/access.md`; CHANGELOG; comments on PAP-394, PAP-400, PAP-183 naming the permission each uses.

**Test plan**

* Unit: registry completeness, preset composition, self-approval denial, agent default scope.
* E2E: an `accountant` can open every report and export CSV but the Post button is absent in `/finance/journal`; a `payroll_admin` cannot approve a run they created.

**Demo**

Reviewer logs in as the seeded accountant, opens the journal, sees no Post action, then as payroll admin tries to approve their own run and reads the separation-of-duties message. Under two minutes.

**Edge cases**

* Tenant with a single owner: separation rules relax for `owner` with an audit note.
* Role deleted while sessions are active: PAP-223 payload refresh applies within one request.
* Agent asks for `ledger:post`: only through a roster change (NJ item), never self-granted.

**Dependencies**

Hard: PAP-175, PAP-59, PAP-227. Soft: PAP-55, PAP-64, PAP-60. Blocks PAP-394, PAP-400, PAP-183 (soft: they may start with inline checks and adopt the registry).

**Agent**

Builder: Ledger (Compliance sub-agent). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
