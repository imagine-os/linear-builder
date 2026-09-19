# 0002: Integrator merge queue

## Status

Accepted, 2026-09-19. Made by the coordinating session (Claude Sonnet 5) after wave 1 launched, on evidence from the first hour of the build loop.

## Context

The builder brief (`docs/build-log/builder-brief-v1.md`, rule 3) had each builder integrate to `main` itself: fetch, rebase, re-run its check, `git push origin HEAD:main`, retry up to 5 times on non-fast-forward. With PAP-13 landed and wave 1 launching ~20 concurrent builder sessions against the same `paperos-template` repo, that assumption broke down fast: PAP-176 alone lost 10 consecutive races to push `main` before giving up. Every failed race burns a check re-run (lint + typecheck + test + build) for no result, and a builder stuck retrying against `main` is not doing its own issue's work.

## Decision

Replace self-service serial pushes to `main` with a merge queue:

* A builder pushes its own branch (`git push -u origin feat/PAP-<n>-<slug>`) as soon as its check is green, before attempting `main` at all, so the work is durable regardless of what happens next.
* It then rebases onto `origin/main`, re-runs the check, and tries `git push origin HEAD:main` at most **twice**. Two tries, not five: past that, contention (not a real conflict) is almost certainly the cause, and more retries just burn check runs.
* If both tries are rejected, the builder stops, records `branch pushed, awaiting integrator` in its Session ended comment and final report, and moves on to other work. It does not sit in a retry loop.
* A dedicated integrator worker (Opus 5, high effort) merges `feat/*` branches into `main` one at a time: rebase, green check, push, delete the branch. Serial by construction, so it never races itself.
* Builder brief updated to v1.1 (`docs/build-log/builder-brief-v1.1.md`) to reflect this; v1 is kept for history.

## Consequences

* Builders spend their time on their own issue, not on repeated rebase-and-check cycles against a moving `main`.
* `main` only ever receives pushes from one actor (the integrator) plus PAP-13's original scaffold push, so non-fast-forward rejections on `main` should approach zero going forward.
* A branch that loses both its own tries waits on the integrator's queue depth; under heavy wave launches that queue can back up, trading builder time for integrator throughput. If the integrator itself becomes the bottleneck, the fix is more integrator capacity (parallel integrators partitioned by path, or a stricter path-ownership scheme), not reverting to self-service pushes.
* Every builder must still leave its branch on `origin` (never only local) so no work is lost if the session ends before the integrator gets to it.

## Revert

Reversible: if the integrator queue becomes the bottleneck or Justin prefers self-service pushes again, drop the integrator worker and restore brief rule 3 to its v1 form (fetch/rebase/push with up to 5 tries), or raise the retry cap. No Linear or repo-structure change is required either way.

## Alternatives rejected

* **Keep 5 self-service retries per builder.** Rejected: with ~20 concurrent builders the retry storm itself is the problem; more retries per builder makes contention worse, not better.
* **Partition `main` by directory so builders never collide.** Rejected for now: most wave-1 issues legitimately touch shared registry files (ADR index, surfaces reference) as well as their own package, so path partitioning would still collide; revisit if the integrator queue becomes a real bottleneck.
* **Batch all of wave 1 into one big merge instead of per-issue commits.** Rejected: loses per-issue attribution and Linear traceability, and makes a single bad diff block everyone instead of just its own issue.
