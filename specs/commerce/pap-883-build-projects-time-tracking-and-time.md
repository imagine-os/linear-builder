---
identifier: "PAP-883"
title: "Build projects, time tracking and time-and-materials billing: projects over PM tasks, time entries and timers, billable rates and budgets, retainers, expenses to projects, time to invoice, utilisation reports"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Orders, POS, purchasing, projects and HR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-100", "PAP-102", "PAP-185", "PAP-346", "PAP-395", "PAP-877", "PAP-878"]
blocks: ["PAP-884", "PAP-885", "PAP-888", "PAP-892"]
key: "r4/commerce/projects-time-billing"
url: "https://linear.app/paperos/issue/PAP-883/build-projects-time-tracking-and-time-and-materials-billing-projects"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:00.743Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-883: Build projects, time tracking and time-and-materials billing: projects over PM tasks, time entries and timers, billable rates and budgets, retainers, expenses to projects, time to invoice, utilisation reports

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make agencies, law firms, consultancies and studios billable: projects as containers over PM tasks (PAP-100), time entries with a running timer and manual entry, billable rates by person, role or project, budgets with burn alerts, retainers drawn down monthly, expenses attached to projects (PAP-185), one-click invoicing of unbilled time and expenses through PAP-395, and utilisation and profitability reports as views.

**Scope**

In: `ProjectsPort`: `projects` (client `fin_party`, budget hours or Money, rate card, retainer, status), `timeEntries` (person, task, duration, billable, rate snapshot, notes, status draft|submitted|approved|invoiced), `timer` (one running per person, multi-window aware via PAP-145), `invoiceFromTime` (grouping by project, task or person, rounding rules, write-up/down, creates PAP-395 invoice lines and marks entries invoiced). Pages: `/projects` (grid and Gantt PAP-346 over tasks), project detail with budget burn, time tab, expenses tab, unbilled summary; `/time` (weekly timesheet grid, timer bar in the shell `shell.header.actions` slot); portal `/portal/projects` for clients (status, approved time, invoices). Rate cards: precedence person-on-project > role-on-project > project default > person default; currency from the project; retainers as prepaid `fin_document`s drawn down by posting rules. Reports as datasets: utilisation (billable vs available from HR shifts when present), realisation, project profitability (revenue vs cost rates plus expenses), budget alerts via notifications.

Out: Resource planning and capacity forecasting (v0.3). Trust accounting for law firms (pack adds a restricted ledger account set; IOLTA rules v0.3).

**Spec**

* Time entries snapshot the rate at approval so later rate changes do not alter unbilled value; write-ups and write-downs are explicit lines with reasons
* Timers survive reloads and multiple windows (PAP-145) and stop automatically after 12 hours with a review prompt
* Invoicing groups per tenant setting; invoiced entries become immutable; a credit note un-invoices them explicitly
* Client portal shows only approved, billable entries unless the project allows detail

**Interface contract**

Provides: `ProjectsPort` default adapter, tables and datasets, projects and time pages, timer slot fill, portal pages, posting rules for retainers, `time.entry.logged`, `project.*` events. Consumes: PM entities and boards (PAP-100, PAP-102), Gantt (PAP-346), documents (PAP-395), expenses (PAP-185), window bus (PAP-145), notifications (PAP-136), HR shifts (soft). Consumed by: PAP-884 (timesheets), packs (agency, law, construction), growth (client activity), assistant ("how many hours on Acme this month?").

**Definition of done**

* Agency demo: two people log time via timer and timesheet across three projects, one retainer; approve; invoice unbilled time grouped by task with a write-down; utilisation and profitability views render; client sees approved time in the portal
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: rate precedence; rounding rules; budget burn; timer auto-stop.
* Integration: invoice from time marks entries and reverses on credit note; retainer drawdown postings; multi-window timer.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Start a timer on a task from one window, stop it from another, submit the week, approve as a manager, invoice the project with 15-minute rounding and show the retainer drawdown.

**Edge cases**

* Entry logged against a task moved to another project: the entry keeps its project unless re-assigned explicitly; report shows the mismatch
* Person without a rate: entry is non-billable with a warning until a rate exists
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-878 (hard), PAP-100, PAP-395 (hard), PAP-102, PAP-346, PAP-185, PAP-145 (soft).

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/commerce/domain-model` = PAP-878, `r4/commerce/hr-core` = PAP-884.
