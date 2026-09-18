# Round 4 verification (phases 1 and 2, fresh queries, 2026-09-18T14:09:57Z)

Total issues in team PAP: 991 (493 this morning; 416 specified issues created in round 4 — 335 in phase 1, 81 in phase 2 — plus 82 Triage issues).

## Round-4 issues per project (specified issues; Triage issues in a separate column)

| project | new | children | deferred | triage |
|---|---|---|---|---|
| Agent Characters & Orgs | 16 | 6 | 2 | 6 |
| Business Core: Payments, Finance & Payroll | 25 | 1 | 20 | 3 |
| Commerce, Operations & Vertical Packs | 16 | 0 | 13 | 0 |
| Data Layer & Database | 25 | 13 | 3 | 5 |
| Design System | 19 | 6 | 1 | 4 |
| Growth: Marketing, Outreach & CRM | 23 | 4 | 20 | 1 |
| Identity, Roles & Audiences | 22 | 10 | 2 | 8 |
| In-App Collaboration & Knowledge | 15 | 1 | 5 | 10 |
| Library Discovery & Integration | 12 | 0 | 1 | 2 |
| Migration & Import Tools | 20 | 4 | 17 | 2 |
| Module System & Swap Tooling | 18 | 5 | 1 | 2 |
| Multi-Input Control & Accessibility | 14 | 4 | 1 | 1 |
| Multiplayer & Realtime | 14 | 8 | 0 | 5 |
| Platform Operations, Analytics & Compliance | 15 | 0 | 11 | 0 |
| Project Management & Claude Pipeline | 18 | 2 | 2 | 4 |
| Quality Pipeline | 18 | 5 | 5 | 9 |
| Scheduling, Messaging & Customer Engagement | 15 | 0 | 12 | 0 |
| Spec Builder | 14 | 0 | 2 | 3 |
| Table & Views Engine | 28 | 13 | 9 | 5 |
| Tenant AI Assistant & Business Agents | 14 | 0 | 9 | 0 |
| Universal App Shell & Repo Template | 22 | 10 | 6 | 9 |
| Version Control & Forge Independence | 18 | 8 | 2 | 3 |
| Workflows, Approvals, Forms, Documents & E-Signature | 15 | 0 | 11 | 0 |

## Checks

- PASS: every new leaf has an estimate
- PASS: every new leaf has dueDate unless deferred
- PASS: every new leaf has Phase/Type/Model/Effort labels
- PASS: every new leaf has exactly one Surface label
- PASS: every new specified issue is in Backlog (or Ready for Claude after promotion)
- PASS: deferred new issues have priority 4 and the Deferred label
- PASS: no Backlog issue carries a cycle (cycles hold in-flight work only)
- PASS: 0 issues in Todo that were Backlog this morning
- PASS: 0 issues in Todo at all
- PASS: every Ready for Claude issue is in cycle C1
- PASS: Triage issues: state Triage, priority 3, no estimate/dueDate/cycle, Type + Surface label

Total `blocks` relations: 3041.
- PASS: no cycles in the full blocks graph
- PASS: zero milestone inversions across all blocks edges
- PASS: no edge from a deferred issue to a scheduled one
- PASS: zero Ready for Claude issues with an open inbound blocker
- PASS: zero Ready for Claude umbrellas
- PASS: zero Ready for Claude issues labelled Deferred
- PASS: umbrellas carry no Model/Effort label and no estimate

## New projects (5)

| project | milestones | links | updates | initiative | state |
|---|---|---|---|---|---|
| Tenant AI Assistant & Business Agents | Business characters, evals and swap (2026-10-16), Actions, copilots and portal assistant (2026-10-09), Assistant contract and grounded chat (2026-10-01) | 3 | 1 | Product surfaces for every audience | Planned |
| Workflows, Approvals, Forms, Documents & E-Signature | E-signature, canvas editor and swap (2026-10-16), Forms builder and document templates (2026-10-09), Workflow contract and approvals (2026-10-01) | 3 | 1 | Product surfaces for every audience | Planned |
| Scheduling, Messaging & Customer Engagement | Memberships, loyalty, announcements and swap (2026-10-16), Messaging channels, help center and surveys (2026-10-09), Engagement contract and booking core (2026-10-01) | 3 | 1 | Business-ready for any business | Planned |
| Commerce, Operations & Vertical Packs | Operations packs, marketplace and swap (2026-10-16), Orders, POS, purchasing, projects and HR (2026-10-09), Commerce contract and catalog (2026-10-01) | 3 | 1 | Business-ready for any business | Planned |
| Platform Operations, Analytics & Compliance | Compliance evidence, residency and swap (2026-10-16), Product analytics, experiments and abuse controls (2026-10-09), Ops contract, super-admin console and status page (2026-10-01) | 3 | 1 | Operate, measure and comply | Planned |

- PASS: each new project has 3 milestones, 3 links, a project update and one initiative
- PASS: team PAP has cycleIssueAutoAssignStarted = true

Ready for Claude count: 29. State distribution: {'Triage': 82, 'Backlog': 873, 'Ready for Claude': 29, 'Duplicate': 7}. Team issueCount: 991.

## Rules recorded for the docs

- **Cycles hold in-flight work only.** Linear moves a Backlog issue to the default unstarted state (Todo) when it joins a cycle, so planned issues never carry a cycle; planned timing lives in due dates and Chunk labels. `cycleIssueAutoAssignStarted` is on for team PAP, so an issue joins the active cycle the moment it moves to In Progress. Ready for Claude issues (unstarted type) sit in the current cycle C1. Phase 2 reverted the 362 issues that had been pushed to Todo this morning back to Backlog with no cycle.
- **Surface label group is exclusive**: one Surface label per issue (first-listed surface); other surfaces stay in the description.
- **Pre-existing edge violations from round 3** (18 milestone inversions, 3 deferred -> scheduled) were softened per FIX-1: the 21 `blocks` relations were deleted and a `_Round 4 (2026-09-18): PAP-x soft: ..._` line appended to the Dependencies section of both ends (decisions with relation ids in `changes/phase2.json` and below).

## Round-3 edge decisions

| blocker | blocked | relation id | decision | reason |
|---|---|---|---|---|
| PAP-161 | PAP-361 | `4aa90609-b5ab-47f0-b290-765e2e799fb2` | soften (deleted) | the view-model spec (PAP-161, Ready, spec-complete) lands 09-28 after the 09-26 codegen milestone |
| PAP-239 | PAP-441 | `7166a494-d6b7-4622-9bce-9cbdd1e3a933` | soften (deleted) | the gate artifact contract (09-25) lands after the kernel milestone (09-22), same pattern as the PAP-239 -> PAP-97 softening on 2026-09-17 |
| PAP-298 | PAP-96 | `6fca04b4-eb1c-437e-b461-4f4d8536bcd2` | soften (deleted) | the deny-list hook (09-24) lands after the orchestrator milestone (09-22) |
| PAP-301 | PAP-48 | `2263a2e4-f8f5-4588-b156-c1a70b8d92e5` | soften (deleted) | the founder root-of-trust hardening (09-23) lands after the forge milestone (09-20) |
| PAP-332 | PAP-199 | `c57c6ac0-91cc-4a0c-b616-696441ea9412` | soften (deleted) | the in-app schema editor (09-29) lands after the import framework milestone (09-28) |
| PAP-334 | PAP-199 | `0f696956-2e02-427f-80a5-6f2a8c1be979` | soften (deleted) | bulk operations, trash and restore (09-29) land after the import framework milestone (09-28) |
| PAP-366 | PAP-435 | `3340734a-b026-4b23-afb4-71ea1f7d9e9e` | soften (deleted) | runtime feature flags (09-29) land after the contracts milestone (09-27) |
| PAP-433 | PAP-447 | `d9f7ae50-e349-4d8d-94a1-d366a1f28121` | soften (deleted) | the manifest schema and validator (09-22, Ready, spec-complete) land after the app-shell scaffold milestone (09-20) |
| PAP-442 | PAP-430 | `5142478e-907a-4da3-9a1d-a1e81753aef4` | soften (deleted) | the swap playbook automation (10-01) lands after `paperos upgrade` (09-29) |
| PAP-446 | PAP-29 | `1bd149a2-a38b-4f32-809b-72297e99048f` | soften (deleted) | the shell swap drill (10-01) lands after the blank-screen drill (09-29) |
| PAP-471 | PAP-266 | `270afcf5-d68d-4140-b4ff-a726948d313b` | soften (deleted) | the pm-linear wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-480 | PAP-266 | `65c4943d-80b7-48d6-95f4-fe684a115bb6` | soften (deleted) | the collab wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-481 | PAP-266 | `62bb50f0-0278-481e-8c83-059421919a0a` | soften (deleted) | the realtime wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-482 | PAP-266 | `356c81ef-790b-4600-af52-ce285a45a52b` | soften (deleted) | the input wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-489 | PAP-266 | `1d507697-dc12-440c-b393-401612694da5` | soften (deleted) | the tables wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-490 | PAP-266 | `17eadd4c-3391-4267-a9a7-c134fe15aa2c` | soften (deleted) | the business-core wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-491 | PAP-266 | `67372ffc-5042-4fbc-b2da-8b7272c248b6` | soften (deleted) | the growth wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-496 | PAP-266 | `19270167-dedc-40d3-b219-053139a65b8a` | soften (deleted) | the migration wire issue lands (09-30/10-01) after the `--without` milestone (09-29) |
| PAP-276 | PAP-455 | `61c6ade0-8f6a-4311-a425-5805f998bf37` | soften (deleted) | PAP-276 is deferred to v0.2 and must not block scheduled work |
| PAP-402 | PAP-491 | `eb422af5-441e-4ab9-a7f7-380d25030f32` | soften (deleted) | PAP-402 is deferred to v0.2 and must not block scheduled work |
| PAP-404 | PAP-491 | `7848700e-a494-40ab-9350-e86c7f44d715` | soften (deleted) | PAP-404 is deferred to v0.2 and must not block scheduled work |
