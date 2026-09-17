# PaperOS Execution Schedule

Day-by-day plan from 2026-09-17T03:30Z to 2026-10-01 for team PAP: 251 schedulable units (PAP-13..PAP-218 plus children and gap issues PAP-219..PAP-279; split parents PAP-19, 20, 21, 28, 35, 36, 45, 54, 57, 59, 65, 67, 81, 82, 85, 88 are tracked through their children), of which 223 are scheduled and 28 deferred. Simulated over the live `blocks` graph (444 relations, no cycles); model in `round2/sched/`.

## 1. Scheduling rules

* **Sizes.** S = half a session-day, M = one, L = two; sessions start 03:30Z (am) or 15:30Z (pm). S lands the same half-day, M the next, L two days on.
* **Branch-start rule.** A dependent may start once every blocker is `In Review` with a PR open; it works against the PR branch and owns the rebase. Without it the 11-deep chains of section 2 do not fit before 10-01 at any parallelism. Implemented by the PAP-96 promotion work package (`promote()` every poll cycle; `pnpm linear:promote --dry-run` as the operator tool) and enforced by PAP-93 `BLOCKED_BY_OPEN` (error): an inbound blocker is open when it is in Backlog, Todo, Ready for Claude, In Progress or Needs Justin, or in In Review without a PR; a Backlog issue is promoted to Ready for Claude when it has no `Deferred` label, no sub-issues, no open blocker and no contract error. Promoted issues get `BASE_BRANCHES` (the In Review blockers' branches) in their session prompt and merge them before coding (PAP-92 "How your issue got to Ready"). Defined 2026-09-17 (FIX-8).
* **Claim order.** Least slack first (milestone target minus remaining critical path), then priority, then size. The orchestrator (PAP-96, live 09-20pm) refills `Ready for Claude` through its promotion pass; before that (09-17..09-20) Atlas runs `pnpm linear:promote --dry-run` from the orchestrator repo at each half-day boundary (03:30Z, 15:30Z), applies the listed promotions by hand (state to Ready for Claude, the `promoted:` comment, `BASE_BRANCHES` in the launch prompt) and launches the sessions; until the repo exists (PAP-96 claimed 09-19) the same list is produced by hand from the `blocks` graph with the four checks and recorded as a comment on PAP-96.
* **Capacity.** Peak parallel builder sessions 8, 12, 16, then 20 from 09-20 to 09-26, tapering 18, 16, 14, 10, 6. Reviewer sessions are on top of the cap.
* **Deferred to v0.2 (not claimable before 10-01):** PAP-23, 137, 149, 157, 158, 182, 185, 190, 191, 193, 194, 195, 196, 197, 203, 204, 206, 207, 218, 221, 222, 230, 231, 232, 235, 276, 277, 278 ($812 of allowances). Each carries the team label `Deferred`, priority 4 and a deferral line under Goal (FIX-4, 2026-09-17); PAP-96 never claims a `Deferred` issue and promotion skips them. Two scheduled issues used to depend on this set and both edges were made soft on 2026-09-17: PAP-235 → PAP-180 (FIX-1; invoices render PDFs with their own template until the theme lands) and PAP-190 → PAP-192 (FIX-4; the content agent drafts into its own `campaign_draft` queue and never publishes). After those two deletions no `blocks` edge runs from a deferred issue to a scheduled one; the only edges out of the set stay inside it (PAP-230/231 → 232, PAP-276 → 277 → 278).
* **Justin.** `Needs Justin` holds at most five open items (PAP-94). Conditional escalations (ADR contradictions from PAP-44 or PAP-56, S0 waivers from PAP-80, cycles from PAP-99) are not pre-scheduled.

## 2. Day by day

Identifiers omit `PAP-`. In flight on a day = that day's starts plus M and L starts still running from the previous two days. *Peak* = concurrent builder sessions.

| Day | Starts | Peak | Reviewer sessions | Needs Justin / checkpoint |
| -- | -- | -- | -- | -- |
| 09-17 | 13 14 25 31 55 56 66 79 209 212 | 8 | manual `/code-review` | NJ-1 Linear: upgrade the workspace plan (Basic is enough; issueCreate returns USAGE_LIMIT_EXCEEDED at 275 issues; \~165 specified issues in the "Round 2 pending issues" documents wait on it). Filed on PAP-91, which sits in Needs Justin until `/approve` or `/reject`; also posted as a comment on PAP-5. Nothing waits on the answer: the 12 hard dependencies on pending issues were folded into PAP-198 (WP2 test accounts), PAP-187 (WP0 consent centre), PAP-180 (WP4 recurring and dunning) and PAP-114 (spec versioning out of scope) on 09-17 (FIX-5). On approve, create `agents/runtime-sandbox` first, then PAP-96 and PAP-104 children, then `agents/session-observability`, then the rest by phase (order and scripts in PAP-91). NJ-2 Infra batch (PAP-25): Hetzner account and cpx41, registrar or Cloudflare token (or accept [sslip.io](<http://sslip.io>)), Resend sign-up, sops recovery key. NJ-3 GitHub App on org `imagine-os` with repo+workflow scope (PAP-47). NJ-4 Anthropic Console: orchestrator API key, $10K hard limit, usage export (PAP-98). |
| 09-18 | 16 17 30 32 42 46 78 91 92 94 127 150 214 236 239 273 279 | 12 | manual; Gate 1 CI live (PAP-78) | NJ-5 Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97). |
| 09-19 | 26 33 68 96 103 104 105 114 128 139 161 210 213 219 237 243 255 274 275 | 16 | manual; harness PAP-243 lands | NJ-6 Code signing (PAP-256): enroll in the Apple Developer Program and pick Azure Trusted Signing for Windows, or accept unsigned v0.1.0 installers. Default after 48 h: unsigned. |
| 09-20 | 15 18 34 43 44 47 48 49 93 95 115 117 133 175 211 223 238 244 245 256 267 | 20 | Gate 2 dry run | NJ-7 License of the template code (PAP-211): MIT, Apache-2.0 or proprietary; default Apache-2.0. NJ-8 Approve `docs/pm/justin-queue.md` (PAP-94) and the issue contract (PAP-93). |
| 09-21 | 22 27 38 69 70 71 80 97 98 99 130 151 162 198 224 225 226 227 233 257 268 | 20 | Gate 2 on every PR from here | NJ-9 Hire the roster (PAP-104, PAP-210): nine leads, 28 sub-characters, tool scope classes. **RC0.** |
| 09-22 | 37 50 58 74 106 110 118 121 152 164 179 215 228 229 234 240 258 261 262 269 | 20 | Gate 2; SAST (PAP-80) | NJ-10 Stripe test-mode account and restricted key (PAP-177); Google Cloud OAuth consent screen for PAP-224 and PAP-200. One item. |
| 09-23 | 51 52 73 87 116 119 120 129 140 163 177 246 259 260 263 264 270 | 20 | Gate 2; evals (PAP-110) | Queue drains. |
| 09-24 | 39 61 63 86 107 108 111 122 132 141 142 155 180 199 247 249 271 | 20 | Gate 2; story baselines (PAP-246) | NJ-11 Domain: set `PAPEROS_DOMAIN` or keep [sslip.io](<http://sslip.io>) for v0.1.0. **RC1.** |
| 09-25 | 62 72 109 112 123 131 134 145 156 165 168 170 176 220 241 242 248 250 265 272 | 20 | Gates 2-3; calibration (PAP-241) | NJ-12 Payroll provider (PAP-176): sign the Check sandbox agreement (default) or Gusto Embedded. NJ-13 Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136). |
| 09-26 | 60 83 84 100 124 143 153 154 167 169 178 187 188 200 201 251 252 253 266 | 20 | Gates 2-3; PAP-83, 84, 251 land | Queue drains. |
| 09-27 | 24 64 101 102 135 136 166 171 172 181 183 184 189 202 205 254 | 18 | Gates 2-4; nightly staging (PAP-253) | NJ-14 Stop-loss checkpoint: go or no-go on the stretch pool (section 5). |
| 09-28 | 29 75 89 125 138 144 147 173 174 192 216 | 16 | Gates 2-4; calibration sample; RC2 certify | NJ-15 `Release candidate 2026-40 (v0.1.0-rc.2)` from PAP-254: `/approve` or `/reject`. **RC2.** PAP-29 result on PAP-5 (informational). |
| 09-29 | 40 41 53 76 90 113 126 146 148 159 160 217 | 14 | Gates 2-4; PAP-147, PAP-53 drills | NJ-16 Approve the content agent (PAP-192) and migration agent (PAP-208). NJ-17 Accessibility statement wording (PAP-160). |
| 09-30 | 77 186 208 | 10 | Gates 2-4; no new claims after 12:00Z | NJ-18 Industry list and terminology defaults (PAP-126). NJ-19 Scope freeze: deferred list becomes milestone v0.2. |
| 10-01 | (none; RC3 regression only) | 2 | Gates 2-4 on RC3 | NJ-20 `Release candidate v0.1.0`: `/approve` promotes and tags. **RC3.** NJ-21 PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29). |

Zero-slack chains (a slip moves the section 7 milestone by the same amount): orchestrator PAP-25 → 96 → 97/98/99 (09-21pm); API and sync PAP-33 → 267 → 268 → 269 → 270 → 271 → 272 → 143 (09-27pm); permissions PAP-279/34 → 227 → 228/229 → 140 → 142 → 131 (09-27pm); gates PAP-239 → 243 → 244/245 (09-20pm) then 240 → 246 → 247 → 248 (09-25pm); tables PAP-228 → 163 → 165 → 166/172 → 173/174 (09-30am). Two half-days of slack: release train 248 → 252 → 253 → 254 → 89 (09-29am); auth 33 → 223 → 224 → 58 (09-23am). Atlas re-simulates nightly and republishes this table.

## 3. Release-candidate checkpoints

| RC | When | Cut by | Must be true | Justin |
| -- | -- | -- | -- | -- |
| RC0 | 09-21 pm | Atlas by hand | Staging on the VPS (PAP-25, 30, 269); sign-in (PAP-223, 224); seeded tenant; Gates 1-2 green; orchestrator claiming (PAP-96); PAP-29 checkpoints C1-C3 timed. | Informational comment on PAP-5. |
| RC1 | 09-24 pm | Atlas, tag `v0.1.0-rc.1` via PAP-52 | RLS-backed permissions (PAP-227-229); installers (PAP-256, 257); Yjs server (PAP-140); codegen (PAP-120); Stripe test mode (PAP-177); story baselines (PAP-246). | NJ-11. |
| RC2 | 09-28 am | PAP-254, first real cut | Gates 1-4 green; grid and compiler (PAP-163, 165); comments (PAP-131); record sync (PAP-143); ledger and invoices (PAP-179, 180); imports (PAP-199); drill C1-C5 (PAP-29). Digest by hand (PAP-89 lands 09-29). | NJ-15 `/approve` or `/reject <reason>`. |
| RC3 = v0.1.0 | 10-01 am | PAP-254 + PAP-89 digest | Every non-deferred issue Done or Canceled with a reason; evidence from PAP-112, 160, 53, 147 attached; final burn report. | NJ-20 `/approve` promotes and tags. |

Freeze: no new claims after 09-30 12:00Z except `release-blocker` issues.

## 4. Credit burn model

Allowance per builder session: **S $10, M $22, L $50**; PAP-98 meters, PAP-111 enforces 2x as the hard stop (S $20, M $44, L $100). Overlays per landed PR: Gate 2 $6 (three reviewers), vision and video $1.50, re-review $1.80 average (30 percent bounce rate), Quill changelog $2; plus Gate 4 hunter $30 per night from 09-27 and Atlas $20 per day. Rounds 1-2 of planning are booked at $300 until Ledger has the console figure.

| Day | Sessions S/M/L | Build starts P0/P1/P2 | Build $ | QA $ | Plan $ | Docs $ | Research $ | Day $ | Plan line $ |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 09-17 | 3/7/0 | 3/0/0 | 66 | 84 | 74 | 18 | 64 | 306 | 306 |
| 09-18 | 6/10/1 | 9/0/0 | 174 | 121 | 106 | 36 | 60 | 497 | 803 |
| 09-19 | 5/11/3 | 11/0/0 | 274 | 140 | 118 | 40 | 60 | 632 | 1,435 |
| 09-20 | 7/14/0 | 13/2/0 | 294 | 195 | 84 | 62 | 0 | 635 | 2,070 |
| 09-21 | 2/18/1 | 12/7/0 | 422 | 195 | 20 | 42 | 44 | 723 | 2,793 |
| 09-22 | 3/13/4 | 6/10/1 | 422 | 167 | 64 | 36 | 50 | 739 | 3,532 |
| 09-23 | 2/12/3 | 3/12/0 | 390 | 289 | 42 | 36 | 0 | 757 | 4,289 |
| 09-24 | 0/13/4 | 2/13/1 | 464 | 167 | 42 | 36 | 0 | 709 | 4,998 |
| 09-25 | 5/12/3 | 1/14/1 | 400 | 199 | 20 | 58 | 10 | 687 | 5,685 |
| 09-26 | 3/14/2 | 0/11/4 | 362 | 158 | 74 | 34 | 22 | 650 | 6,335 |
| 09-27 | 0/10/6 | 0/4/10 | 476 | 182 | 20 | 50 | 0 | 728 | 7,063 |
| 09-28 | 1/8/2 | 0/3/4 | 210 | 245 | 30 | 48 | 0 | 533 | 7,596 |
| 09-29 | 3/9/0 | 0/1/6 | 142 | 192 | 42 | 72 | 0 | 448 | 8,044 |
| 09-30 | 1/2/0 | 0/0/2 | 44 | 132 | 20 | 22 | 10 | 228 | 8,272 |
| 10-01 | 0/0/0 | 0/0/0 | 0 | 49 | 20 | 4 | 0 | 73 | 8,345 |

Reconciliation to the 12/45/30/8/5 split of $10,000:

| Bucket | Scheduled | Pools and reserves | Total | Share |
| -- | -- | -- | -- | -- |
| Planning | 776 (26 Spec units $476, Atlas $300) | 300 rounds 1-2, 124 reserve | 1,200 | 12% |
| Building | 4,140 (166 Build/Infra units: 20 S, 120 M, 26 L; P0 $1,272 / P1 $1,974 / P2 $894) | 360 retry pool (about 16 M retries) | 4,500 | 45% |
| Automated QA | 2,515 (per-PR gates $2,335, 7 Review units $142, hunter, calibration) | 485 evals (PAP-110), RC3 regression | 3,000 | 30% |
| Docs, changelog, prompt logs | 594 (10 Docs units $148, Quill $446) | 206 handbook and release notes (PAP-112, PAP-89) | 800 | 8% |
| Research and scouting | 320 (14 Research units, cap $30 each) | 180 spikes and Scout | 500 | 5% |

## 5. Stop-loss rules

1. **Plan line.** Ledger compares cumulative spend with the plan-line column at 09:00Z. Two consecutive days above 115 percent: no more P2 claims, stretch pool cancelled. Any day above 125 percent, or 09-27 above 110 percent: only zero-slack-chain issues may be claimed, and one `Needs Justin` item offers cut list (PAP-174, 173, 101, 102, 113, 159, 186, 208, 192, in order) or top-up.
2. **Per issue.** At 80 percent of the 2x cap the session gets a wrap-up turn (PAP-111); at 100 percent it commits `wip:`, pushes and returns the issue to `Ready for Claude` with `retry-1`. Second failure: Decomposer splits it. Third: `Needs Justin`. Retries draw on the $360 pool, flagged at 75 percent.
3. **Reserve.** $500 is locked from 09-29 for RC3 fixes; only Justin releases it.
4. **Stretch pool.** Deferred issues are claimable only after NJ-14 says go and while the plan line is under 100 percent; cheapest first, never an L. Reinstating one means Atlas removes its `Deferred` label, restores its priority and deletes the deferral line under Goal; until then PAP-96 refuses to claim it.
5. **Throughput.** Fewer than 12 PRs landing on a day from 09-20 to 09-26: Atlas re-simulates and moves milestones instead of adding sessions.

## 6. Daily burn report (Ledger, 09:00Z, comment on the PAP-98 report issue)

```
Burn report <date> (day n of 15)
Spend yesterday $x | Cumulative $x of 10,000 (plan line $y, ratio r)
By bucket: plan $ / build $ / QA $ / docs $ / research $ (shares vs 12/45/30/8/5)
Sessions: started n (S/M/L), landed n, bounced n, retried n, killed at cap n
Retry pool $x of 360 | Reserve locked/unlocked
Most expensive: PAP-a $x (size, ratio), PAP-b, PAP-c
Chains (half-days vs plan): orchestrator, API/sync, permissions, gates, tables, release
Milestones moved: <name> <before> -> <after> (why)
Needs Justin open n/5 (ids) | Stop-loss: green / amber (rule 1a) / red (rule 1b)
Tomorrow: n claims (ids), peak sessions n
```

## 7. Milestone target dates moved by this schedule

Set via `projectMilestoneUpdate` on 2026-09-17 (before -> after, last issue in brackets). Early finishers keep their dates.

* agents / Roster defined and installed: 09-20 -> 09-24 (PAP-107)
* app-shell / Desktop and mobile shells build: 09-23 -> 09-24 (PAP-263)
* app-shell / Template scaffolds and runs on web: 09-19 -> 09-20 (PAP-18)
* collab / Comments and canvas: 09-26 -> 09-29 (PAP-136)
* collab / Docs and prompt log stores: 09-20 -> 09-23 (PAP-129)
* data-layer / Local-first sync working: 09-24 -> 09-25 (PAP-272)
* data-layer / Postgres + Drizzle baseline: 09-19 -> 09-22 (PAP-269)
* design-system / Tokens and primitives: 09-20 -> 09-22 (PAP-71)
* forge / Forgejo live and mirrored: 09-19 -> 09-20 (PAP-49)
* identity / Auth works across web and desktop: 09-20 -> 09-23 (PAP-58)
* libraries / Evaluation process: 09-19 -> 09-20 (PAP-211)
* pm-linear / Linear configured for the pipeline: 09-18 -> 09-20 (PAP-93)
* quality / Gates 1 and 2 on every PR: 09-20 -> 09-25 (PAP-248)
* quality / Visual and video gates: 09-25 -> 09-26 (PAP-84)
* realtime / Record sync and conflict UX: 09-26 -> 09-28 (PAP-144)
* realtime / Yjs server and presence: 09-22 -> 09-25 (PAP-142)
* spec-builder / Spec schema and validator: 09-22 -> 09-24 (PAP-116)
* tables / Grid with sort, filter, group: 09-23 -> 09-28 (PAP-166)
* tables / All view types: 09-27 -> 09-29 (PAP-167..170; round-2 FIX-1, must follow Grid at 09-28 because PAP-163 blocks all four views)
* growth / CRM core: 09-28 -> 09-29 (PAP-189; round-2 FIX-1, the CRM kanban needs PAP-167)

Round-2 FIX-1 (2026-09-17, milestone inversions): app-shell / Template scaffolds and runs on web stays at 09-20; PAP-26 deploy pipeline alone moved to Desktop and mobile shells build (09-24) because its staging deploy needs PAP-30 Postgres (09-22). Three `blocks` relations became soft dependencies with matching Dependencies text on both ends: PAP-239 -> PAP-97 (PAP-97 ships its own `orchestrator-event.json` schema and adopts `packages/contracts` later), PAP-235 -> PAP-180 (invoices use their own PDF template until `packages/ui-print` lands), PAP-88 -> PAP-29 (the first drill run does not need the release train). After these edits no blocker sits in a milestone dated later than the issue it blocks, across all remaining `blocks` relations.

Milestones holding deferred work (identity / Agent principals and enterprise, forge / Disaster recovery proven, growth / Campaigns and social, migration / Business migrations, input / Voice and accessibility certification) are not moved; their deferred issues go to a `v0.2` milestone at NJ-19.

## 8. Risks

* The issue cap (NJ-1) blocks the pending children of PAP-96, 101, 104, 110, 163, 164, 165, 171, 173, 174, 179, 180, 184, 199, 202, 205, 213, 214, 215; until it lifts those parents run as single L sessions using the pending specs, and the retry pool goes there first.
* PAP-256 and PAP-156 need macOS and Windows runners; if NJ-6 defaults, v0.1.0 ships unsigned installers and guidepup dumps.
* NJ-10, 12 and 13 have lead times; PAP-177, 184, 200 and 202 start against mocks.