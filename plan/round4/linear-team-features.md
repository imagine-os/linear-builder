# Linear team features: round 4 (2026-09-18)

Requested by Justin: "use more features of Linear if possible." Workspace `paperos`, team **PAP** (`0ee78894-89f8-4376-a829-f8685dbc1868`), Linear Basic. Every mutation is logged in `changes/linear-team-features.json` (55 entries: 3 `teamUpdate`, 1 `cycleUpdate` x3 aliases, 1 `issueLabelUpdate` x4 aliases, 2 `issueLabelCreate` (1 + 5 aliases), 48 `issueUpdate` batches of <=10). Nothing was deleted, archived or moved between states; PAP-1..PAP-12 were not touched; no document was modified. Linear refused nothing.

## 1. Team settings (before -> after)

| Setting | Before | After |
| -- | -- | -- |
| `issueEstimationType` | `notUsed` | `fibonacci` |
| `issueEstimationAllowZero` | false | false |
| `issueEstimationExtended` | false | false |
| `cyclesEnabled` | false | true |
| `cycleDuration` | 2 (unused) | 1 week |
| `cycleCooldownTime` | 0 | 0 |
| `cycleStartDay` | 1 (Monday) | 4 (Thursday; Linear uses 0 = Sunday) |
| `upcomingCycleCount` | 2 | 2 |
| `cycleIssueAutoAssignStarted` / `...Completed` / `cycleLockToActive` | false | false (set explicitly) |
| `cycleEnabledStartDate` | - | 2026-09-18T00:00Z (so cycle 1 starts today rather than next Thursday) |
| `triageEnabled` | false | true |
| `triageIssueState` | null | **Triage** (`185d9592-5ff4-4e22-a276-1855a30f69e0`, type `triage`) |

Triage is where Justin's Slack voice memos and agent-found bugs land for Atlas to sort; Backlog stays the default state for orchestrator-created issues.

## 2. Cycles (real dates from the API; boundaries are midnight America/Los_Angeles = 07:00Z)

| # | Name | startsAt | endsAt | Id |
| -- | -- | -- | -- | -- |
| 1 (active) | C1 Foundation & core systems | 2026-09-18T00:00Z | 2026-09-25T07:00Z | `e8272686-b4d3-4ac7-a89e-ba227bd63250` |
| 2 | C2 Business layer & hardening | 2026-09-25T07:00Z | 2026-10-02T07:00Z | `e49d64c2-f2c2-491b-a0a6-24f0b9ce9555` |
| 3 | C3 v0.2 stretch | 2026-10-02T07:00Z | 2026-10-09T07:00Z | `eded55ec-07ed-45ca-94fe-0603663e15bc` |

Each cycle also got a description (scope, RC checkpoints). C1 covers schedule days 09-18..09-24, C2 covers 09-25..10-01, as planned; no adaptation of the mapping was needed. C3 has no issues.

## 3. Label groups

* **Surface**: `Customer`, `Staff`, `Developer`, `Agent` re-parented under the existing `Surface` group (`086b098d-a94f-4bae-815c-3e6d56d514dc`) with `issueLabelUpdate { parentId }`. Linear accepted it despite the labels being in use (99 / 189 / 278 / 87 issues).
* **Chunk** (new team group, `aa0b8939-6d0f-4894-a105-6aa0538fd9a5`, #0EA5E9) with children `Chunk 1` (`1cc2bc15-b0f1-41ad-90cc-90c24b82a886`), `Chunk 2` (`d2b1ae15-d90e-4fdb-a063-03d301f15aee`), `Chunk 3` (`0566fac3-212e-4800-ae54-b451ded74b9a`), `Chunk 4` (`ae3e5cf0-d021-4c98-9052-64c13d420989`), `Chunk 5` (`ef74ff9c-a960-45bd-8be9-183bb9ede29a`), one sky-blue family from light to dark. Membership comes from `plan/chunks.json` `mixes.A.chunks[].issues` (mix A is the five-chunk plan; the docs recommend mix B, which has four chunks, so a switch would mean re-labelling). Applied with `addedLabelIds` (append only): 90 / 66 / 65 / 61 / 44 = **326 leaves**. Not labelled: the 42 Deferred leaves (the "optional" chunk), the 65 leaves PAP-433..PAP-497 (created after `chunks.json` was generated on 09-17T14:30Z; they need a chunk re-run), and all umbrellas.

## 4. Bulk issue fields (485 issues = 493 team issues minus PAP-1..PAP-12)

Mapping per issue is in `issue-fields.json` (`identifier, estimate, dueDate, cycle, chunk`). Rules:

* **estimate** (leaves only, from the `**Size**` section of the description; the first-line `— <Type> <Size>` suffix was the fallback and was never needed): S -> 2 (74 issues), M -> 3 (358), L -> 5 (1). The 52 umbrellas (issues with sub-issues) stay null so Linear rolls up their children. Total **1,227 points**: 484 in C1, 620 in C2, 123 on Deferred issues (no cycle).
* **dueDate** = target date of the issue's project milestone: set on **436** issues; the 49 `Deferred` issues (42 leaves + 7 umbrellas) got none. Most common: 09-30 (91), 09-24 (57), 09-29 (56), 09-25 (49).
* **cycle** (leaves only, not Deferred): start day from `docs/execution-schedule.md` section 2 (194 issues: day <= 09-24 -> C1, else C2); issues absent from that table (197, mostly PAP-280+ and PAP-433+) by milestone target date (<= 09-24 -> C1). Result: **C1 175, C2 216 = 391**. Umbrellas and Deferred: none. 29 umbrellas listed in the schedule table (PAP-96, 104, 120, 163, ...) are tracked through their children and got no cycle.
* 7 Deferred umbrellas (PAP-190, 191, 196, 197, 203, 206, 207) had nothing to set and were skipped.

478 `issueUpdate` calls, 478 `success: true`, 0 failures, no rate limiting.

## 5. Verification (read back after the writes)

All 493 team issues paged: **433 with estimate, 436 with dueDate, 391 with cycle** (C1 175 / C2 216), chunk labels 90 / 66 / 65 / 61 / 44; **0 mismatches** against the mapping. PAP-5, PAP-6, PAP-12 confirmed untouched (no estimate, due date or cycle; states unchanged). Spot checks: PAP-162 (M -> 3, due 09-28, C1 from schedule 09-21, Chunk 1), PAP-220 (M -> 3, due 09-25, C2 from schedule 09-25, Chunk 4), PAP-77 (S -> 2, due 09-30, C2 from 09-30, Chunk 5), PAP-434 (M -> 3, due 09-22, C1 from milestone, no chunk), PAP-267 (M -> 3, due 09-22, C1 from schedule 09-20, Chunk 1).

## 6. Follow-ups (not done here)

* Re-run the chunk planner so PAP-433..PAP-497 get a Chunk label; decide mix A vs mix B for good.
* Point the orchestrator (PAP-96) at `team.activeCycle` and the Triage state; consider `requirePriorityToLeaveTriage`.
* Cycle 3 is empty by design; at NJ-19 (scope freeze) move the Deferred set into it or into a v0.2 project.
