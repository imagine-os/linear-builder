# 0003: Integrator owns Linear state moves and lands non-clean branches by rebase

## Status

Accepted, 2026-09-19 02:40 UTC. Made by the coordinating session after review batch 3, on evidence from the integrator log (`build-log/2026-09-19.md`, 02:40 UTC section). Extends 0002 (integrator merge queue); does not replace it.

## Context

Decision 0002 made a dedicated integrator the only path to `main`. Two things went wrong in its first hour:

1. **Union merges corrupt JSON.** The first integrator resolved conflicts in "allowed paths" with `git merge-file --union` (after `git merge -X union` turned out to be unsupported by the installed git build and had produced two false "merged" rows). Union is fine for line-oriented registry docs but not for `package.json`: concatenating both sides of a `dependencies` block drops the comma between them, `pnpm` fails with `package_json_parse_error`, and the branch fails `pnpm check` on every retry. PAP-302 and PAP-210 were stuck exactly this way; PAP-55, PAP-139 and PAP-42 queued behind them as `needs-manual-merge` or `check-failed`.
2. **Builders may not push `main`, and now often may not even move their own issue.** The permission checker denies unreviewed direct pushes to `main` for some builder sessions ("Merge Without Review"), so a builder cannot wait for its commit to be on `main` before moving its issue to In Review; several sessions ended with the branch pushed and the issue still In Progress. The integrator, meanwhile, declined a channel instruction to move states with a hard-coded state id it could not verify against the live workflow, which was the right call for an unverifiable instruction but left every landed issue's state stale.

## Decision

* **The integrator moves Linear states when it lands a branch.** On landing `feat/PAP-<n>-<slug>` onto `main` (green check, pushed), the integrator moves PAP-<n> `In Progress → In Review` and posts the `integrated: ... merged to main as <sha>` comment. Exceptions: `*-review-fixes` branches (the review pass owns those issues), `feat/PAP-90-*` (flake quarantine hotfix, coordinator-owned) and `feat/PAP-92-*` (playbook mirror, already reviewed). If the issue has already been marked pass by the review pass while its branch waited (PAP-302 and PAP-139 today), the integrator moves it straight to `Done` on landing, since the review pass's only outstanding condition was "content on `main`".
* **State ids come from `team-pap.json`**, the workspace snapshot the promotion passes already use, never from an inline literal in a chat instruction. The integrator verifies the id resolves to the expected state name before the first move of a run.
* **Non-clean branches are landed by rebase, not by union merge.** A branch that does not fast-forward is rebased onto `origin/main` in the integrator's checkout, with these resolution rules per conflict class: registry docs (`docs/adr/README.md`, `docs/platform/README.md`, `docs/reference/surfaces.md`, `packages/core/README.md`) keep both sides; `packages/core/src/index.ts` keeps every export line from both sides; `package.json` files get a JSON-aware 3-way merge (parse base, ours, theirs; merge object keys; re-serialize) and must parse afterwards; `pnpm-lock.yaml` takes `main`'s copy and is regenerated with `pnpm install --lockfile-only`. Any other conflict is `needs-manual-merge` as before. Then `pnpm check`, then push. The landed history is linear per issue.
* **Builders do the same rebase before their final push** (builder brief v1.3 rule 14), pushing their branch with `--force-with-lease`, so that most branches arrive clean and the integrator fast-forwards them; a branch that is stale against `main` waits until its builder or the integrator rebases it.

## Consequences

* Linear state reflects `main` within one integrator cycle of a landing, without depending on a builder session still being alive or permitted to act.
* Review-pass verdicts of "pass, awaiting integration" close themselves when the branch lands; no separate Done pass is needed for them.
* `package.json` conflicts stop failing the check for syntactic reasons; genuine dependency conflicts (two branches pinning different versions of the same package) still surface as a real check failure.
* The integrator now writes to Linear beyond comments, so its comment and state move are logged in the integrator log with the sha, and it must keep obeying the deny list (no Done except reviewed-pass on landing, no moves on issues it did not land, never Canceled, archive or delete).
* Rebasing rewrites the builder's commit shas on `main`; Session ended comments that cite branch shas may not match `main`. The `integrated:` comment carries the authoritative main sha.

## Revert

Reversible in two independent parts. If Justin prefers builders to own their state moves, drop the state-move step and keep the comment. If rebase landing proves brittle, fall back to merge commits with the same per-class resolution rules; the JSON-aware merge for `package.json` should stay in either mode.

## Alternatives rejected

* **Keep union merges but exclude `package.json` (manual merge).** Rejected: `package.json` is touched by nearly every package-adding issue, so it would send most of the queue to manual merge.
* **Let builders keep moving their own issues after polling `main`.** Rejected: some builder sessions cannot push and end before their branch lands; the state move would be lost or done against a branch that is not on `main` yet (the very cause of the premature "PAP-302 landed" comments on PAP-71, PAP-164 and PAP-175).
* **A separate Linear-sync worker polling `git log --merges`.** Rejected for now: one more moving part, and the integrator already knows the sha, the branch and the issue at the moment of landing. Revisit if the integrator becomes the bottleneck (0002's consequence still stands).
