# PaperOS plan critique (round 4, after the gap, phase-2 and triage agents)

Snapshots: `plan/round4/critique-snapshot-before.json` (2026-09-18T14:18Z, before this critique's fixes) and `plan/round4/critique-snapshot.json` (14:40Z, after). Both hold every PAP issue except PAP-1..PAP-12 and the Duplicate/Canceled strays: identifier, title, project, milestone and target date, state, labels, estimate, dueDate, parent, children, relations both ways, description. Tools: `plan/round4/critique-tools/{snapshot,checks,fixes,fixes_propagate}.py`; check results in `critique-snapshot*-checks.json`; every mutation in `plan/round4/changes/critique-fixes.json`. Compared against `plan/round2/critique.md` (method and round-2 scores), `plan/round4/merge-report.md`, `verify.md`, the 19 digests, `unfiled-suggestions.md`, `r4-ids.json`, `docs/module-system.md` and `docs/execution-schedule.md`. Chunk labels were being relabelled by another worker during this pass and are ignored here.

Method as in round 2: every project scored 1-5 on Coverage (does the issue set cover the brief and the round-4 feature matrices), Precision (do the specs say exactly what to build, with no unresolved references), Buildability (can a cold session claim and finish the work in the window: blockers encoded, umbrellas claimable through children, capacity) and Testability (is every DoD verifiable on a Linux session without Justin). Round 3 added the module system without rescoring, so "before" is the round-2 "after" column in `docs/blueprint.md`; the module system and the five new projects have no before.

## 0. Facts

| Fact | Round 3 end (09-18 morning, `verify.md` baseline) | Before fixes (14:18Z) | After fixes (14:40Z) |
|---|---|---|---|
| Issues in team PAP (non-archived) | 493 | 991 (983 kept: 901 specified, 82 Triage) | 991 (983 kept) |
| Projects / milestones | 18 / 54 | 23 / 69 | 23 / 69 |
| Leaves / umbrellas (specified) | 485 / ~40 | 796 / 105 | 796 / 105 |
| `blocks` relations | 1224 | 3041 | 3100 (+52 hard-dependency edges, +7 umbrella propagations) |
| Cycles / milestone inversions / dueDate inversions | 0 / 21 softened | 0 / 0 / 0 | 0 / 0 / 0 |
| States | Backlog 464, Ready 29 | Backlog 872, Ready 29, Triage 82 | unchanged |
| `Deferred` issues (priority 4, no dueDate) | 28 | 204 | 204 |
| Descriptions carrying unresolved `r4/<project>/<key>` file keys | 0 | 435 (804 mentions; 6 keys pointed at issues dropped as duplicates) | 0 |
| Specified issues whose Dependencies text names a hard blocker with no `blocks` relation | not measured | 40 (56 edges; 5 of them PAP-363..PAP-432 gap issues with zero inbound relations, i.e. promotable at once) | 0 (52 edges created, 4 turned into explicit soft notes) |
| Children in a different milestone than their parent | 0 | 2 (PAP-627, PAP-636) | 0 |
| Umbrellas whose dueDate precedes their last child's | not measured | 1 (PAP-164) | 0 |
| Leaf issues converted to umbrellas today ("fresh umbrellas") | 0 | 53 (19 with a single child, 11 of them P0) | 53 (design brief FIX-R4-1) |
| Scheduled (non-deferred) leaf work, session-days (S 0.5, M 1, L 2) | ~223 units | 504 over 601 leaves | 504 |

## 1. Integrity checks (before → after)

| Check | Before | After | Offenders / note |
|---|---|---|---|
| Duplicate titles within a project | 0 | 0 | |
| Relation to a missing issue | 7 | 7 | all seven are the `duplicate` relations from the PAP-6..12 strays to PAP-13..19; no `blocks` relation points at a missing issue |
| Orphan child | 0 | 0 | |
| Child in a different project than its parent | 0 | 0 | |
| Child in a different milestone than its parent | 2 | 0 | PAP-636 → PAP-170's "All view types"; PAP-627 → PAP-164's "Grid with sort, filter, group" with dueDate 09-29 → 09-28 (all seven blockers due ≤ 09-28, dependents due 09-29+) |
| Leaf without Phase / Type / Model / Effort label | 0 | 0 | |
| Leaf with other than exactly one Surface label | 0 | 0 | |
| Umbrella with Model or Effort label / with estimate | 0 / 0 | 0 / 0 | |
| Leaf without estimate | 0 | 0 | S = 2, M = 3, L = 5 points; Size letter and estimate agree on all 639 leaves that carry a letter |
| Non-deferred leaf without dueDate / deferred leaf with dueDate | 0 / 0 | 0 / 0 | |
| Deferred issue not at priority 4 | 0 | 0 | |
| Ready issue with an open blocker / with children / labelled Deferred / outside cycle C1 | 0 / 0 / 0 / 0 | same | 29 Ready issues; the fix pass refused to add PAP-13 → PAP-302 because PAP-302 is Ready (its text says "None hard" anyway) |
| Backlog issue carrying a cycle | 0 | 0 | |
| Deferred issue blocking a scheduled one | 0 | 0 | the fix pass refused PAP-235 → PAP-396 and wrote a soft note instead |
| Milestone-date inversions / dueDate inversions | 0 / 0 | 0 / 0 | the fix pass refused PAP-40 → PAP-288, PAP-19 → PAP-225, PAP-132 → PAP-123 (soft notes) |
| Cycles in `blocks` | 0 | 0 | |
| Description missing one of the 11 sections or the `**Model / Effort:**` line (901 specified issues) | 0 | 0 | Triage skeletons (82) are excluded; they carry Goal and Source only by design |
| Model / Effort line vs labels | 0 mismatches | 0 | |
| Dependencies text names a hard blocker with no relation, refined parser ("Hard:", "Blocked by", "X, Y (hard)", "X (hard), Y"), all 901 issues | 40 issues (2 round-4, 38 older) | 0 | list in `critique-snapshot-before-checks.json` `hard_drift_all`; the same parser flagged no round-4 issue except PAP-770 and PAP-772 |
| Same check, round-2 heuristic (any identifier in Dependencies without relation, minus soft) on PAP-498+ and 100 random older issues | 0 / 15 | 0 / 15 | the 15 are "Uses PAP-43", "Informs PAP-37", "consumed by" mentions, which are not blockers; kept for comparability with round 2 |
| Round-4 file keys (`r4/...`) in descriptions | 435 issues | 0 | 342 round-4, 93 older (amendments), 34 Triage; the 6 mentions of keys dropped as duplicates were mapped to the surviving issue (`fx-rates` → PAP-766, `bulk-campaigns` → PAP-799, `file-scanning-previews` → PAP-574, `scheduled-view-delivery` → PAP-639) |
| Fresh umbrellas whose inbound blockers reach no child | 0 | 0 | 7 propagations added after the drift fix landed blockers on PAP-366/367/368 |
| Fresh umbrellas whose outbound `blocks` reach no child (FIX-3 rule 2) | 120 edges (61 umbrellas) | 126 | not applied; see FIX-R4-3 |
| Umbrellas (sample 20, seed 7) whose children cover the parent's Scope | 15 full, 5 partial | same | the 5 partial are single-child fresh umbrellas (PAP-367, PAP-365, PAP-442, PAP-368, PAP-363); see FIX-R4-1 |
| Issues in the 5 new projects with no inbound `blocks` / no transitive path from their contract-publish issue or the kernel | 0 / 0 | 0 / 0 | each contract issue depends on PAP-433, PAP-302, PAP-303, PAP-305, PAP-264, PAP-279 |
| Triage issues (PAP-914+) duplicating a specified issue (title Jaccard or ratio ≥ 0.5) | 1 | 1 | PAP-950 vs PAP-70 (`SplitPane`); note appended to PAP-950 |
| Backlog leaves with zero inbound blockers and no parent (promotable today) | 5 | 1 | PAP-431, PAP-432, PAP-369, PAP-371 now carry the blockers their text named; PAP-754 (`compose-smoke` workflow, "ready on creation") remains and is a legitimate promotion candidate |

## 2. Scores before and after (Coverage / Precision / Buildability / Testability, 1-5 each)

| Project | Before (round 2 after) | After | Reasoning |
|---|---|---|---|
| app-shell | 5/5/4/4 = 18 | 5/5/3/4 = 17 | 22 new issues close the matrix (previews, warm pools, crash reporting, translation CI, desktop E2E harness); but 9 leaves became umbrellas today and 6 of them (PAP-26 P0 deploy pipeline blocking 13, PAP-22, PAP-27, PAP-363, PAP-365, PAP-366, PAP-367, PAP-368) have a single child that covers one bullet of the parent's Scope, so the deploy pipeline, the CLI, i18n, flags and the onboarding wizard are unclaimable until FIX-R4-1 lands. |
| data-layer | 5/5/4/5 = 19 | 5/5/4/5 = 19 | Preview databases, migration safety, entity factory, backups and DR split into children whose titles cover the parents (PAP-303, 304, 39, 43, 354, 355 all ≥ 0.7 scope coverage); serial chain 13 → 42 → 32 → 33 unchanged; 14 leaves due 09-30. |
| forge | 4/5/4/5 = 18 | 5/5/3/5 = 18 | Coverage complete (merge automation, dependent branches, Playwright runner image, GitHub App, mirror drift, DR reporting). Buildability drops: PAP-47 and PAP-48 (P0, due 09-20, blocking 11 each) became single-child umbrellas whose child is the monitor or the GitHub half, so mirroring and bot accounts have no claimable core two days before they are due. |
| identity | 5/5/4/5 = 19 | 5/5/4/5 = 19 | Device flow, abuse controls, MFA and step-up, tenancy split; 5 fresh umbrellas all have two children covering ≥ 0.5 of Scope; 13 leaves due 09-30; 8 Triage skeletons unspecified. |
| design-system | 5/5/5/5 = 20 | 5/5/5/5 = 20 | Navigation, surface, specialised inputs, dataviz tokens filed; the 3 fresh umbrellas (PAP-71, 75, 233) are fully covered by their children; a11y gate suggestion sits in Triage. |
| quality | 5/5/4/5 = 19 | 5/5/4/5 = 19 | Diff coverage, migration gate, DAST and telemetry splits; runners for 4 shards still assumed (PAP-371 now correctly blocked by PAP-25/PAP-50); 13 leaves due 09-30. |
| pm-linear | 4/5/3/4 = 16 | 5/5/4/4 = 18 | Every Linear feature the digest listed as a gap has an issue (initiatives, cycles, estimates, due dates, triage state machine, SLAs, Slack intake); PAP-96/101/104 children exist and the promotion rule is specified; 12 leaves due 09-30; tests need a sandbox Linear workspace nobody owns. |
| agents | 5/5/3/4 = 17 | 5/5/4/5 = 19 | Sandbox PAP-280, bundles, probes, deny list, injection evals and canaries all exist as leaves with blockers; PAP-106/298/299 children cover their parents (≥ 0.6); the probe suite and eval suite make the security DoDs runnable. |
| spec-builder | 5/5/4/5 = 19 | 5/5/4/5 = 19 | Backend codegen, field grammar, v1.1 schema extension and corpus generator close the golden-path C3 gap; 106 scheduled points on a single chain (114 → 117 → 120 → 362 → backend codegen). |
| collab | 4/5/4/4 = 17 | 5/5/4/5 = 19 | Notification core is a P1 Opus child of PAP-136 blocked only by jobs and the event bus; build journals, agent-readable docs, watchers filed; a fixtures issue seeds the six DoDs that assumed data; 10 Triage skeletons (the most of any project) are unspecified. |
| realtime | 5/5/4/4 = 18 | 5/5/4/5 = 19 | Doc history, headless client, ephemeral signals, connection status; PAP-147's load test is split into a k6 harness and staging runs, so the second generator host is now a named issue rather than an assumption. |
| input | 5/5/4/4 = 18 | 5/5/4/4 = 18 | Context menus, native menus, macros, undo manager, clipboard port; Tier-2 assistive-technology checks still wait for the non-Linux runners (PAP-371, 09-24). |
| tables | 5/5/4/4 = 18 | 5/5/4/5 = 19 | Records CRUD, view host, system fields, extra field types and a demo seed that makes every `/demo/*` DoD real; PAP-627 re-homed; 142 scheduled points (the largest project) with 14 leaves due 09-30. |
| business-core | 4/5/4/4 = 17 | 5/5/4/4 = 18 | 24 gaps filed (FX, item catalogue, refunds, AP, bank feeds, deposits, dimensions), 20 deferred; 18 text-only hard dependencies now encoded; PAP-396 still names deferred PAP-235 as hard (soft note written). |
| growth | 4/5/3/4 = 16 | 5/5/4/4 = 18 | Consent centre and CRM schema are children of PAP-187; 39 of 43 leaves deferred, which leaves a coherent scheduled core (187 children, 188, 189, 192) of 25 points. |
| migration | 4/5/3/4 = 16 | 5/5/4/4 = 18 | Importer test accounts (PAP-814), conformance harness and OAuth connections exist; 30 of 46 leaves deferred; PAP-770/772 hard blockers encoded; test accounts still need Justin. |
| libraries | 5/5/5/4 = 19 | 5/5/5/5 = 20 | Spike harness kit and `compose-smoke` (PAP-754, ready on creation) make the five spikes measure the same way; usage notes and guardrails give sessions the borrow-before-build path. |
| module-system | — | 5/5/3/5 = 18 | Contract diff, sample module, scaffold and kernel integrations close the matrix and the conformance runner plus sample module make swaps testable; but all 5 umbrellas are fresh single-child umbrellas (PAP-434 P0 blocking 34, PAP-441 P0 blocking 26, PAP-435 blocking 26, PAP-442, PAP-443), so the kernel's registry, conformance runner and flag swap have no claimable leaf today. |
| assistant (new) | — | 5/4/3/4 = 16 | Grounded chat, retrieval, actions, copilots and business characters cover the brief; precision 4 because the contract shapes are not yet in the Contracts document; 5 scheduled issues all due 10-01 (RC day) behind kernel and event-bus issues; evals and golden tasks named. |
| workflows (new) | — | 5/4/3/4 = 16 | Workflow model, approvals framework and My Tasks inbox are the scheduled core; 11 of 15 deferred; the approvals framework replaces five hand-rolled approval steps only if those issues are amended to consume it (they are not yet). |
| engagement (new) | — | 5/4/3/4 = 16 | Booking engine and scheduling model scheduled, 12 deferred; depends on the recurrence engine PAP-908 (data-layer, 09-30) landing one day before its own due date. |
| commerce (new) | — | 5/4/3/3 = 15 | Catalog and inventory plus the domain model scheduled, 13 deferred; POS hardware, marketplace and vertical-pack DoDs lean on external devices and accounts with no mock named. |
| platform-ops (new) | — | 5/4/3/4 = 16 | Control framework, super-admin console and status page scheduled; the control mapping is testable from CI artefacts; 11 deferred; milestones 10-09 and 10-16 sit outside the window. |
| **Total, 17 projects scored in round 2** | **304 / 340** | **317 / 340** | +13: coverage is 5 everywhere; the deficit is buildability, and today it has one dominant cause (FIX-R4-1) plus capacity (FIX-R4-2). |
| **Total, all 23 projects** | — | **414 / 460** | module-system 18, five new projects 79. |

## 3. What round 4 got right

- 416 new specified issues and 82 Triage skeletons landed with zero label, estimate, dueDate, milestone, cycle or state defects (every check in section 1 that concerns fields is 0 before and after); the merge report's title de-duplication held (0 duplicate titles).
- The graph stayed clean at 3041 → 3100 edges: no cycles, no milestone or dueDate inversions, no deferred → scheduled edge, no Ready issue blocked, every fresh umbrella's inbound blockers reach a child.
- Every one of the 75 new-project issues depends, directly or through its project's contract-publish issue, on the kernel (PAP-433) and the shared contracts (PAP-302, PAP-303, PAP-305, PAP-264, PAP-279), so the module boundary rule is encoded for the new modules on day one.
- The five gaps the cross-cutting analysis called out (assistant, workflows, engagement, commerce, platform-ops) are filed honestly: 19 scheduled issues, 56 deferred at priority 4 with the label, none blocking scheduled work.

## 4. Fix briefs

Each brief is self-contained for one agent editing Linear through the API (`linear:linear-api` skill, aliases of up to 10 mutations, 300 ms between requests, ids from `critique-snapshot.json`, log to your own `changes/*.json`). FIX-R4-4 to FIX-R4-6 were applied by this critique; the rest are design-level and left open.

### FIX-R4-1 (open, design) — 53 claimable leaves became umbrellas today and 19 of them, 11 P0, lost their claimable core

**Wrong.** Round 4 attached 100 children to existing issues. For 53 parents this was their first child, which under the umbrella rule (PAP-92/93/96, `UMBRELLA_NOT_CLAIMABLE`) removed the parent from the claimable set, stripped its Model/Effort labels and estimate, and left only the children to build. Where the children are genuine halves (PAP-43 jobs core + admin page, PAP-303 envelope + dispatcher, PAP-58, PAP-60, PAP-63, PAP-141, PAP-142, PAP-154, PAP-159, PAP-166, PAP-169, PAP-172, PAP-220, PAP-233, PAP-298, PAP-299, PAP-304, PAP-355, PAP-356, PAP-357, PAP-381 and others: 34 umbrellas with scope coverage ≥ 0.6) this is fine. Where the child is an add-on, the parent's own spec has no leaf: the 19 single-child fresh umbrellas are PAP-434 (P0, kernel registry, blocks 34; child: host integrations), PAP-441 (P0, conformance runner, blocks 26; child: normaliser), PAP-435 (flag swap, blocks 26; child: settings page), PAP-26 (P0, deploy pipeline, blocks 13; child: PR previews), PAP-47 and PAP-48 (P0, due 09-20, blocking 11 each; children: drift monitor, GitHub App), PAP-22 (`paperos create`; child: Linear seeding), PAP-27 (i18n; child: translation skill), PAP-366 (flags; child: settings page), PAP-367 (onboarding wizard; child: staff funnel), PAP-368 (error contract; child: Tauri crash hook), PAP-363, PAP-365, PAP-442, PAP-443, PAP-50, PAP-51, PAP-52, PAP-53. Six more two-child umbrellas cover under half of the parent's Scope (PAP-430, PAP-62, PAP-434's neighbours in the table in `critique-tools` output). The orchestrator will never promote PAP-434 or PAP-26 again, and nothing else carries their spec.

**Fixed looks like.** Every fresh umbrella either has a child that carries the parent's core spec or is a leaf again. Two mechanical options per parent, choose per row: (a) **create a core child** "`<parent title>` (core)" with the parent's Goal/Scope/Spec/Interface/Test plan/DoD text minus the bullets the existing child owns, the Model/Effort from the parent's `**Model / Effort:**` line, the estimate implied by its Size letter, the parent's milestone and dueDate, and every inbound blocker of the parent (`issueRelationCreate`), then relate `core blocks <add-on child>`; or (b) **de-parent the add-on** (`issueUpdate(child, {parentId: null})`), restore the parent's Model and Effort labels and estimate from its own line, and add `parent blocks child`. Prefer (b) for the 19 single-child rows above (19 × 3 mutations, no new issues, restores 11 P0 leaves, of which PAP-47 and PAP-48 are due in two days) and (a) for the six two-child rows. After either, re-run `checks.py`: `fresh_umbrellas_single_child` must be 0 and `ready_umbrella` must stay 0. Update `docs/module-system.md` and `specs/` through `gen_specs.py`.

### FIX-R4-2 (open, design) — 504 session-days of scheduled work for 208 of capacity, 119 of them due on 09-30

**Wrong.** The 601 non-deferred leaves sum to 504 session-days at the schedule's own sizes (S 0.5, M 1, L 2; points 2/3/5). Sixteen builders over the 13 remaining days give 208. The due-date histogram shows the overflow was resolved by piling work on the last two days: 09-20 23, 09-22 39, 09-23 24.5, 09-24 53.5, 09-25 69, 09-26 26, 09-27 24, 09-28 35, 09-29 59, **09-30 119**, 10-01 32 session-days. Data-layer, tables, quality, identity, collab and pm-linear each have 12-14 leaves due 09-30, and the 19 scheduled issues of the five new projects (all 3-point) are due 10-01, RC day. Every dueDate is consistent with milestones and blockers (0 inversions), so the graph is honest; the calendar is not.

**Fixed looks like.** Either capacity or scope moves, in Linear, before the orchestrator starts promoting. Recommended, in `plan/round4/sched/`: re-run the model with 16 builders and the branch-start rule; whatever does not finish by 10-01 receives the `Deferred` label, priority 4, no dueDate and the Goal line "Deferred to v0.2 by the round-4 schedule (NJ-14)", chosen by lowest priority then latest dueDate, never P0, never a blocker of a scheduled issue (re-check `deferred_blocks_scheduled` = 0). Expect roughly 250-300 session-days to move, concentrated in the P2 leaves due 09-29/09-30 and the 19 new-project issues (keep the five contract-publish issues and the five model specs scheduled). Put the resulting capacity curve and the RC dates back into the Execution Schedule document and PAP-91's milestone dates.

### FIX-R4-3 (open, decision) — an umbrella's dependents wait for the umbrella, not for its last child

**Wrong.** FIX-3 rule 2 (round 2) said "for each `P blocks D`, add `Clast blocks D`". Round 2 applied it partially (53 of 185 old edges unpropagated); round 4 did not apply it at all: 120 edges from the 61 new umbrellas (126 after this critique's propagations) reach no child. `fix-plan.json` `outbound_plan` lists all 185 candidate edges (183 pass every safety check; the 2 failures are PAP-627 → PAP-341/347 milestone inversions). This critique did not create them: 185 edges the Dependencies text does not name would create the opposite drift, and the promotion rule already gates D on the umbrella's In Review, which the session finishing the last child performs.

**Fixed looks like.** One sentence decides it, then either 183 relations or none. Recommended: keep the graph as is and write into PAP-92 (session playbook), PAP-93 (`BLOCKED_BY_OPEN`) and PAP-96 (promotion): "A dependent of an umbrella waits for the umbrella. The umbrella reaches In Review when its last child does; its `BASE_BRANCHES` are the union of its children's PR branches, which the promoting orchestrator collects from the children." If the team prefers the FIX-3 wording instead, create the 183 safe edges from `outbound_plan` and add "Blocks <D>" to each last child's Dependencies text in the same pass.

### FIX-R4-4 (applied) — 435 descriptions referenced round-4 issues by file key, not identifier

**Wrong.** Round 4 wrote cross-references as `` `r4/<project>/<key>` `` in 342 new, 93 amended and 34 Triage descriptions (804 mentions), including the hard-blocker sentences ("Blocked by `r4/realtime/live-events-channel` and PAP-18 (hard)"), so a cold session could not resolve a dependency without `plan/round4/r4-ids.json`. Six mentions pointed at keys dropped as duplicates in phase 2 and resolved to nothing.

**Fixed.** 443 `issueUpdate` calls (fresh description fetched first) replaced every key in place with its identifier and appended `_Round 4 critique fix (2026-09-18):_ resolved N round-4 file keys ...: \`key\` = PAP-n` so the mapping stays visible; the six dropped keys map to their surviving issue (PAP-766, PAP-799, PAP-574, PAP-639). After: 0 keys outside the marker lines. `gen_specs.py` should be re-run so `specs/` mirrors the text.

### FIX-R4-5 (applied) — 40 issues named a hard blocker their graph did not have; five of them had no blockers at all

**Wrong.** PAP-431, PAP-432, PAP-366, PAP-367, PAP-368, PAP-369, PAP-370, PAP-371 (round-2 gap issues created 09-17) say "PAP-25, PAP-35, PAP-178 (hard)" and similar yet carried zero inbound `blocks`, so the promotion pass would have moved custom domains, tenant lifecycle, flags, onboarding, code signing and non-Linux runners to Ready before the scaffold exists. Thirty-two more issues (business-core and migration children, PAP-83/84/85, PAP-171/175/183, PAP-267, PAP-290-296, PAP-318-327, PAP-770, PAP-772) named one or two hard blockers without the relation.

**Fixed.** 52 `issueRelationCreate` calls, each checked for milestone and dueDate order, deferral direction, Ready state, parent/child and cycles; 4 edges failed the checks and received a soft note on the blocked issue instead: PAP-235 → PAP-396 (deferred blocker), PAP-40 → PAP-288 and PAP-19 → PAP-225 and PAP-132 → PAP-123 (milestone inversions; the authors should decide whether PAP-40 observability and PAP-19 belong in earlier milestones, and whether PAP-123 and PAP-132 are mutually hard, which the text currently claims). Seven blockers that landed on PAP-366/367/368 were propagated to their children PAP-501/506/502. A fifth refusal, PAP-13 → PAP-302, came from the parser misreading "None hard (pure package on the PAP-13 layout)"; its note was removed and the parser now skips "None hard" sentences. Ten issues whose Hard list and round-4 soft note contradicted each other (PAP-699, 706, 714, 717, 799, 361, 435, 441, 455, 491) received a one-line clarification. After: 0 hard-dependency drift on all 901 specified issues.

### FIX-R4-6 (applied) — two children outside their parent's milestone, one umbrella due before its last child

**Fixed.** PAP-636 (deferred chart types) moved to PAP-170's milestone; PAP-627 (extra field types) moved to PAP-164's milestone with dueDate 09-28 (its seven blockers are due ≤ 09-28, its three dependents 09-29+), which also makes PAP-164 close with its last child. PAP-950 (Triage) received a note that PAP-70 already ships `SplitPane`.

### FIX-R4-7 (open) — 82 Triage skeletons carry a one-line Goal and no spec; ten sit on collab, nine each on quality and app-shell

**Wrong.** The 82 Triage issues (PAP-914+) have Goal and Source only, priority 3, provisional Type and Surface labels, no estimate or dueDate. That is the agreed intake shape, but nothing schedules their disposition, and `PAP-307` (the Decomposer) does not exist yet as a running service. Several restate work other issues already own (PAP-950 vs PAP-70; the a11y Storybook gate vs PAP-73/PAP-78; "PAP-27 provides `useUiStrings()`" is an amendment, not an issue).

**Fixed looks like.** Atlas triages in one pass before 09-22: for each Triage issue either (a) accept: write the 11 sections with `**Model / Effort:**`, estimate, dueDate or `Deferred`, Phase, Model and Effort labels, blockers, and move to Backlog; (b) fold: append the sentence to the owning issue's Spec as a `_Round 4 triage (date):_` amendment and mark the Triage issue Duplicate with the relation; or (c) decline with a comment. Expected split from the titles: about 25 accept (mostly deferred), 45 fold, 12 decline. Record the decisions in `plan/round4/unfiled-suggestions.md`.

### FIX-R4-8 (open) — the Ready set is 13 Spec, 9 Research, 3 Build, and day-two Build issues depend on hand promotion

**Wrong.** Of 29 Ready issues only PAP-13, PAP-66 and PAP-555 are Build. Twelve Backlog leaves are due 09-20 (PAP-753, 701, 700, 695, 693, 692, 530, 520, 521, 447, 305, 275) and are blocked only by PAP-13, PAP-91, PAP-45/273 or PAP-46, which will be In Review within hours; the branch-start promotion exists as a rule (PAP-96) but not as running code, so day two still depends on Atlas's `pnpm linear:promote --dry-run`. PAP-754 (`compose-smoke`, "ready on creation") has no blockers at all and sits in Backlog.

**Fixed looks like.** Promote PAP-754 now (zero blockers, no parent, not deferred, Sonnet S). Add to the 09-19 evening step of the Execution Schedule the twelve identifiers above with their base branches, and make PAP-13's and PAP-91's DoD say "PR open within 2 hours of claim; post the branch name for the branch-start rule". No other state change.

### FIX-R4-9 (open) — the five new projects are scheduled for RC day and their milestones lie outside the window

**Wrong.** All 19 scheduled issues of assistant, workflows, engagement, commerce and platform-ops are due 10-01 (3 points each, 19 session-days on the last day) and every one of their milestones is dated 10-01, 10-09 or 10-16, while the plan's window ends 10-01 and `Deferred` means v0.2. The 56 deferred issues therefore carry a milestone date that looks like a commitment. The engagement booking engine (PAP-864) depends on the recurrence engine PAP-908 due 09-30.

**Fixed looks like.** Keep the five contract-publish issues (PAP-833, 847, 862, 877, 893) and five model specs (PAP-834, 848, 863, 878, 896) at 10-01; move the other nine scheduled issues to `Deferred` unless FIX-R4-2 finds capacity; rename the 10-09 and 10-16 milestones with a "v0.2:" prefix so the board reads correctly, and put the assistant, workflow, engagement, commerce and platform-ops contract shapes into the Contracts document (PAP-130 ADR) so precision reaches 5.

### FIX-R4-10 (open) — the approvals framework and workflow engine exist, but the five issues that hand-roll approvals still do

**Wrong.** The cross-cutting analysis filed PAP-849 (approvals framework) and PAP-850 (My Tasks inbox) because five existing issues each build their own approval step (expense approval in business-core, deal stage approval in growth, import commit approval in migration, content approval queue PAP-192, Needs Justin cards PAP-94). None of the five was amended to consume `ApprovalPort` from `@paperos/contract-workflows`, so the platform will ship six approval implementations.

**Fixed looks like.** Append to each of the five a `_Round 4 amendment:_` line under Interface contract: "Approval steps go through `ApprovalPort` (PAP-849) once it is In Review; until then keep the local step behind the port interface so the swap is a one-line change", and add soft-dependency sentences (no `blocks`, since PAP-849 is due 10-01 and the five are earlier).

## 5. Order for the next agents

1. FIX-R4-1 first: 19 × 3 mutations restore eleven P0 leaves, two of them due 09-20.
2. FIX-R4-2 and FIX-R4-9 together in the schedule model; they decide what `Deferred` covers before promotion starts.
3. FIX-R4-3 (one paragraph in three issues, or 183 edges), FIX-R4-8 (one promotion, two DoD lines).
4. FIX-R4-7 and FIX-R4-10 as text work over the next two days; FIX-R4-5's four soft notes need their authors' decision on milestones.

## 6. After-fix integrity (14:40Z snapshot)

All field checks 0; cycles 0; milestone and dueDate inversions 0; deferred → scheduled 0; Ready blocked/umbrella/deferred 0; child milestone mismatch 0; umbrella-due-before-last-child 0; hard-dependency drift 0 of 901; `r4/` keys in bodies 0; fresh-umbrella inbound propagation gaps 0; new-project issues without a path to their contract or the kernel 0; Backlog leaves with no gate 1 (PAP-754, intended). Open by design: 53 fresh umbrellas (19 single-child), 126 unpropagated umbrella outbound edges, 82 Triage skeletons, 504 scheduled session-days. Mutations this pass: 444 description updates, 59 relations created, 2 milestone/dueDate updates, 0 deletions, 0 state changes (`changes/critique-fixes.json`).


## 7. After final fixes (snapshot `critique-snapshot-final.json`, 2026-09-18T14:54:47Z)

Applied by `critique-tools/final_fixes.py` (log `changes/final-fixes.json`, 241 mutations, 0 failures, 0 deletions):

- **FIX-R4-1**: all 19 single-child fresh umbrellas judged from the two descriptions; in every case the child is an add-on (an integration, monitor, settings page, CI shim or reporting layer), so option (b) was applied to all 19: child de-parented (`parentId: null`, note in its Dependencies), `parent blocks child` created (19 relations, none inverted a milestone or a due date, none made a cycle), parent's Model and Reasoning-effort labels and estimate (3 points each) restored from the 12:50Z inventory and `issue-fields.json`, the split comment amended. None of the 19 had been Ready for Claude in the 12:50Z inventory (all Backlog), so no state was restored. Umbrellas 105 -> 86, leaves 796 -> 815; `fresh_umbrellas_single_child` 19 -> 0.
- **FIX-R4-3**: the last-child rule applied to every umbrella with children: 155 `Clast blocks D` edges over 86 umbrellas (fresh snapshot after FIX-R4-1; 0 skips: no candidate edge would have made a cycle, a milestone or due-date inversion or a deferred -> scheduled edge), plus 1 propagation where a new edge landed on another umbrella (PAP-328 -> PAP-381's child). The rule sentence was added to the Dependencies section of PAP-92 and PAP-96 (marker `_Round 4 critique fix (2026-09-18):_`). `new_umbrella_unpropagated_outbound` 126 -> 0.
- **FIX-R4-8**: PAP-754 (`compose-smoke`, zero inbound blockers, no children, not Deferred) promoted Backlog -> Ready for Claude in cycle C1 with the comment `promoted: no blockers (round 4 critique)`. Ready 29 -> 30.
- **FIX-R4-9**: the five new projects (assistant, workflows, engagement, commerce, platform-ops) got `targetDate` 2026-10-16 (their latest milestone; was 2026-10-01) and the content line "v0.1 scope is the first milestone (2026-10-01); the later milestones are v0.2 (deferred)" at the top.

| Check | After final fixes |
|---|---|
| Issues / specified / Triage | 983 / 901 / 82 |
| Leaves / umbrellas (specified) | 815 / 86 |
| `blocks` relations | 3275 |
| States | Backlog 871, Ready for Claude 30, Triage 82 |
| Deferred | 204 |
| Cycles / milestone inversions / dueDate inversions | 0 / 0 / 0 |
| Deferred -> scheduled edges | 0 |
| Ready blocked / umbrella / Deferred / outside C1 | 0 / 0 / 0 / 0 |
| Backlog with cycle / promotable Backlog leaves | 0 / 0 |
| Leaf label / estimate / dueDate defects; umbrella with Model, Effort or estimate | 0 / 0 / 0; 0 |
| Child project / milestone mismatch; umbrella due before last child | 0 / 0; 0 |
| Description sections missing; hard-dependency drift; `r4/` keys in bodies | 0 / 0 / 0 |
| Fresh umbrellas / single-child fresh umbrellas | 34 / 0 |
| Fresh-umbrella unpropagated inbound / outbound edges | 0 / 0 |
| New-project issues without inbound blockers | 0 |
| Children with no inbound blocker | 1 (PAP-555, Ready for Claude by design) |
| Triage duplicates | 1 (PAP-950 vs PAP-70, noted) |

Still open by design: FIX-R4-2 (504 scheduled session-days for 208 of capacity), FIX-R4-7 (82 Triage skeletons), FIX-R4-10 (five hand-rolled approval steps not yet amended to consume `ApprovalPort`).
