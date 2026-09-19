# 0004: Stopping point: loop paused, coordinator hotfixes on `fix/*` branches, parked branches stay open

## Status

Accepted, 2026-09-19 19:45 UTC. Made by the coordinating session (Claude Fable 5.1) that took the Slack thread over at 19:18 UTC, on Justin Massion's instruction of 19:17 UTC ("finish what you were just doing, but bring it to a stopping point"; `../prompts/build-2026-09-19.md`). Justin also said, at 03:19, "I don't wanna make any decisions yet": this record covers only how the loop is held while paused, not any of the questions he raised (one repository, rename, Pages source), which stay proposals in `../build-log/2026-09-19.md` (19:18 section) until he answers.

## Context

1. **Credits out, thread orphaned.** The previous coordinating session ended at 03:19 UTC when the organization ran out of Claude Tag usage credits (bot notice in the thread, 03:19:03Z). 22 issues were In Progress with builder sessions that no longer exist; 25 `feat/*` branches on `imagine-os/empty-11` carry commits that never reached `main`; the integrator, review and promotion passes stopped mid-cycle. Nobody answered the thread for sixteen hours, and the Needs Justin cards' 48-hour defaults (execution schedule) would otherwise start counting against a loop that is not running.
2. **`main` is red.** Every CI run on `empty-11` `main` since 02:06:10Z is failure or cancelled (last green `820a1b75`, 02:04:54Z). The direct cause is Biome `organizeImports` on the union-merged barrel `packages/core/src/index.ts`; locally, a stale dependency map, a missing `ownership.json` entry for `packages/core/src/config` and a root-runner-only failure in `apps/web/src/config.test.ts` fail the gate too. Decision 0001 requires a green check before anything lands, so no parked branch can be landed on a red `main` with any confidence.
3. **The permission checker denies direct `main` pushes for the coordinator too.** Decision 0003 recorded that builders may not push `main` ("Merge Without Review"). This session's own push of the prepared fix to `main` was denied as well ("Modify Shared Resources"). The only path to `main` is the integrator merge queue (0002), which is not running while the loop is paused.
4. **None of the 25 parked branches has ever run in CI.** `ci.yml` runs on push to `main` and on pull requests only; the loop opens no PRs (0001). The only evidence per branch is the builder's own local check, and 22 of those builders are gone.

## Decision

* **The loop is paused.** No builder wave, review batch, promotion pass or integrator run starts until Justin says continue. The wrap-up session surveys, diagnoses, documents and prepares fixes; it does not build.
* **Coordinator hotfixes go on `fix/<what>-<date>` branches, never direct to `main`.** The first is `fix/main-green-2026-09-19` (`280e1453`) on `empty-11`, local gate green. The next pass's integrator lands it first, before any `feat/*` branch, and confirms CI green on `main` before the queue continues. The permission denial is treated as policy, not as an obstacle to route around.
* **Parked branches stay open, documented and unmerged.** The 25 branches are listed with head sha, ahead count, subject and Linear state in the 19:18 section of the build log. Nothing is merged on the strength of a local check from a dead session; nothing is deleted or force-pushed. They enter the merge queue when the loop resumes, `feat/PAP-754-review-fixes` (an S1 security fix for a Done issue) and `feat/PAP-433-module-manifest-schema` (top Backlog blocker) first.
* **Linear is not touched while paused.** No state moves, no comments beyond what the previous session already posted. The 22 In Progress issues keep their state; their reconciliation (land the branch and move to In Review, or comment and return to Ready for Claude) is the first coordinator job of the next pass, not of this one.
* **Needs Justin defaults are suspended while paused.** The four cards (PAP-1040, PAP-1039, PAP-1041, PAP-25) keep their proposed defaults but the 48-hour clock does not run; it restarts from the moment Justin says continue.

## Consequences

* `main` on `empty-11` stays red until the next pass merges the fix branch; anyone reading the repo in the meantime sees a failing badge and this record explains why.
* The work of 22 builder sessions is preserved but invisible to Linear (their issues read In Progress with no live session). The build log table is the only complete inventory; it must be the first thing the next coordinator reads.
* Landing 25 branches that never saw CI will surface failures in bulk; the next pass budgets a red-fix cycle per landing rather than assuming fast-forwards.
* The permission checker's denial of direct `main` pushes now applies uniformly: builders (0003), integrator excepted (0002), and coordinator (this record). Every path to `main` is the merge queue.
* The Pages URL for `empty-11` keeps serving a Jekyll README until Justin flips the source to Actions and PAP-15 lands; the demo link handed to Justin today is the blueprint site on `linear-builder`, not the app.

## Revert

Justin says continue: the pause lifts, the next pass runs the order in the build log's *What the next pass does first*, and the Needs Justin clock restarts. If Justin instead wants the parked work landed without the merge queue (for example by granting the coordinator a direct-push exception), the `fix/*` rule drops and the branch inventory stays as the merge order. If Justin decides to consolidate into one repository first, the parked branches are imported with their history before anything is landed, and this record is superseded by the consolidation decision.

## Alternatives rejected

* **Merge the unverified branches now, to leave `main` "complete".** Rejected: none has a CI run, 22 of their builders are gone, `main` is already red, and decision 0001's green-check rule is the only quality gate the loop has without PRs. Merging would make the red harder to bisect and hand the next pass 25 unattributed failures at once.
* **Push the fix straight to `main`, retrying around the permission checker.** Rejected: the denial is the same policy that governs builders (0003); working around it would make the coordinator the one actor with unreviewed write access to `main`, which is exactly what 0002 removed. The fix loses nothing by waiting on a branch.
* **Move the 22 In Progress issues back to Ready for Claude so the board reads clean.** Rejected for this session: it would hide that work exists on branches, it is a Linear mutation during a pause Justin asked for, and whether an issue should return to Ready or go to In Review depends on whether its branch lands, which only the next pass knows. The board is stale on purpose and the build log says so.
