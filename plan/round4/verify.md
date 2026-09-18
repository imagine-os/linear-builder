# Round 4 verification (fresh queries, 2026-09-18T13:53:13Z)

Total issues in team PAP: 828 (493 before round 4; 335 created this round).

## New issues per project

| project | new | children | deferred |
|---|---|---|---|
| Agent Characters & Orgs | 16 | 6 | 2 |
| Business Core: Payments, Finance & Payroll | 25 | 1 | 20 |
| Data Layer & Database | 23 | 13 | 2 |
| Design System | 18 | 6 | 0 |
| Growth: Marketing, Outreach & CRM | 23 | 4 | 20 |
| Identity, Roles & Audiences | 21 | 10 | 1 |
| In-App Collaboration & Knowledge | 14 | 1 | 4 |
| Library Discovery & Integration | 12 | 0 | 1 |
| Migration & Import Tools | 20 | 4 | 17 |
| Module System & Swap Tooling | 18 | 5 | 1 |
| Multi-Input Control & Accessibility | 14 | 4 | 1 |
| Multiplayer & Realtime | 14 | 8 | 0 |
| Project Management & Claude Pipeline | 18 | 2 | 2 |
| Quality Pipeline | 18 | 5 | 5 |
| Spec Builder | 14 | 0 | 2 |
| Table & Views Engine | 28 | 13 | 9 |
| Universal App Shell & Repo Template | 21 | 10 | 6 |
| Version Control & Forge Independence | 18 | 8 | 2 |

## Checks

- PASS: every new leaf has an estimate
- PASS: every new leaf has dueDate unless deferred
- FAIL: every new leaf has a cycle unless deferred (240 offenders) (see note below)
    - PAP-575
    - PAP-750
    - PAP-695
    - PAP-814
    - PAP-725
    - PAP-720
    - PAP-543
    - PAP-557
    - PAP-512
    - PAP-745
    - PAP-654
    - PAP-663
    - PAP-669
    - PAP-619
    - PAP-615
    - PAP-533
    - PAP-506
    - PAP-534
    - PAP-681
    - PAP-765
    - PAP-755
    - PAP-693
    - PAP-548
    - PAP-570
    - PAP-561
    - PAP-532
    - PAP-588
    - PAP-559
    - PAP-729
    - PAP-529
    - PAP-501
    - PAP-498
    - PAP-546
    - PAP-505
    - PAP-509
    - PAP-652
    - PAP-586
    - PAP-753
    - PAP-622
    - PAP-578
- PASS: every new leaf has Phase/Type/Model/Effort labels
- PASS: every new leaf has exactly one Surface label
- PASS: every new issue is in Backlog (or Ready for Claude after promotion)
- PASS: deferred new issues have priority 4 and Deferred label

Total `blocks` relations: 2583.
- PASS: no cycles in the full blocks graph
- FAIL: zero milestone inversions across all blocks edges (18 offenders)
    - PAP-161 (2026-09-28) -> PAP-361 (2026-09-26)
    - PAP-239 (2026-09-25) -> PAP-441 (2026-09-22)
    - PAP-298 (2026-09-24) -> PAP-96 (2026-09-22)
    - PAP-301 (2026-09-23) -> PAP-48 (2026-09-20)
    - PAP-332 (2026-09-29) -> PAP-199 (2026-09-28)
    - PAP-334 (2026-09-29) -> PAP-199 (2026-09-28)
    - PAP-366 (2026-09-29) -> PAP-435 (2026-09-27)
    - PAP-433 (2026-09-22) -> PAP-447 (2026-09-20)
    - PAP-442 (2026-10-01) -> PAP-430 (2026-09-29)
    - PAP-446 (2026-10-01) -> PAP-29 (2026-09-29)
    - PAP-471 (2026-09-30) -> PAP-266 (2026-09-29)
    - PAP-480 (2026-09-30) -> PAP-266 (2026-09-29)
    - PAP-481 (2026-09-30) -> PAP-266 (2026-09-29)
    - PAP-482 (2026-09-30) -> PAP-266 (2026-09-29)
    - PAP-489 (2026-09-30) -> PAP-266 (2026-09-29)
    - PAP-490 (2026-10-01) -> PAP-266 (2026-09-29)
    - PAP-491 (2026-10-01) -> PAP-266 (2026-09-29)
    - PAP-496 (2026-10-01) -> PAP-266 (2026-09-29)
- FAIL: no edge from a deferred issue to a scheduled one (3 offenders)
    - PAP-276 -> PAP-455
    - PAP-402 -> PAP-491
    - PAP-404 -> PAP-491
- PASS: zero Ready for Claude issues with an open inbound blocker
- PASS: zero Ready for Claude umbrellas
- PASS: zero Ready for Claude issues labelled Deferred
- PASS: umbrellas carry no Model/Effort label and no estimate
- FAIL: every new child has at least one inbound blocker or is first-in-family (1 offenders) (informational)
    - PAP-555

Ready for Claude count: 29. State distribution: {'Backlog': 430, 'Ready for Claude': 29, 'Todo': 362, 'Duplicate': 7}.

## Notes on the failed checks

1. **Cycles on new leaves (240 offenders).** Every `issueCreate` sent `cycleId` (C1 `e8272686-b4d3-4ac7-a89e-ba227bd63250` for milestone <= 09-24, C2 `e49d64c2-f2c2-491b-a0a6-24f0b9ce9555` otherwise) together with `stateId` = Backlog, and Linear silently dropped the cycle: Backlog issues cannot belong to a cycle. The same rule is why the sibling's cycle assignment earlier today moved 362 existing issues from Backlog to Todo (inventory 12:50Z: 457 Backlog / 0 Todo; now 430 Backlog / 362 Todo). Setting the cycle on the new issues would move them to Todo, which CLAUDE.md defines as human parking that is never polled, and state changes beyond the two permitted ones are out of scope for this run, so the new issues stay in Backlog without a cycle. Decision needed: either accept Todo + cycle as the scheduled state (and update CLAUDE.md, PAP-92/93/96 and the promotion rule), or drop cycles and move the 362 Todo issues back to Backlog.
2. **Milestone inversions (18) and deferred -> scheduled edges (3).** All 21 offending edges pre-date round 4 (they are in the 12:50Z inventory and in this run's opening snapshot; every endpoint is <= PAP-497, i.e. round-3 module-system relations such as PAP-4xx -> PAP-266 and the PAP-276/402/404 -> PAP-455/491 edges). Round 4 introduced none: its 947 file edges and 412 umbrella edges were filtered against both rules before creation (14 file edges dropped with soft-dependency notes, 12 umbrella edges skipped; see merge-report.md and `changes/create-issues.json`). Nothing was deleted because deleting relations is outside this run's allowed changes; a follow-up (soft-dependency notes plus `issueRelationDelete`, or milestone moves) should resolve them.
3. **PAP-555 (informational).** First child of PAP-303, which was in Ready for Claude with no open blockers; PAP-303 moved to Backlog (umbrella) and PAP-555 was promoted to Ready for Claude, so it correctly has no inbound blocker.
