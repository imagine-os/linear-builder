# 0001: Build pilot operating mode

## Status

Accepted, 2026-09-19. Made by the coordinating session (Claude Fable 5.1) at the start of the autopilot build loop, on Justin Massion's go (`docs/prompts/build-2026-09-19.md`).

## Context

Justin asked the build loop to run on autopilot against the existing Linear PAP plan, "until we run out of credits." Three things the plan assumed were not yet true or needed a call before any builder could start:

1. The plan's repo table (`docs/blueprint.md`, `docs/interface-and-data-contracts.md` §5) names repositories (`paperos-template`, `paperos-orchestrator`, `paperos-infra`, ...) that had not been created. `imagine-os/paperos` already exists but is a different product (PaperOS v2, a canvas desktop app) — it must never be touched by this build. Justin made two empty repositories available, `imagine-os/empty-11` and `imagine-os/empty12`, to be renamed later.
2. The plan's pipeline (`CLAUDE.md`, `docs/security-and-threat-model.md` §4) assumes a PR-based flow: builders open PRs, Sentinel and reviewers gate them, a merge flow moves issues to `In Review` and later `Done`. Justin's org-wide policy (channel memory) is git-only: no PRs, and agents don't post to Slack channels directly. That collides with the plan's own deny-list ("never push to main", "never move to Done"), which was written assuming PRs would gate `main`.
3. Orchestration: PAP-96 (the automated orchestrator) does not exist yet. Something has to promote issues, launch workers on the right model, and run the manual promotion pass (`pnpm linear:promote --dry-run`, per CLAUDE.md's promotion rule) until PAP-96 lands.

## Decision

* **Repos.** `paperos-template` (the platform monorepo, Contracts §5 layout) = `imagine-os/empty-11`, local clone `/workspace/empty-11`. `paperos-orchestrator` = `imagine-os/empty12`, local clone `/workspace/empty12`. `paperos-infra` (PAP-25) is deferred until Justin provides a Hetzner account (tracked as NJ-2); infra files live under `ops/` inside the template repo in the meantime. `imagine-os/paperos` is out of scope for this build entirely — no session may write to it.
* **Git only, no PRs.** Builders integrate to `main` themselves after every check passes green (worktree per issue, rebase onto `origin/main`, push `HEAD:main`, retry on non-fast-forward). The plan's `In Review = PR exists` state is redefined for this build loop as `In Review = pushed to main, Session ended comment posted`; a review pass (Opus 5 / high following an Opus or Fable builder, Sonnet 5 / high following a Sonnet builder, per `docs/cost-and-duration-estimate.md` §4b) then moves the issue to `Done`. The security-and-threat-model deny-list entries "never push to main" and "never move an issue to Done" are suspended for this build loop under Justin's explicit go; every other item on that deny list stands unchanged — Linear deletes and archives, PAP-1..PAP-12, labels, views and documents stay untouchable, and no session moves an issue to `Done` except the dedicated review pass.
* **Orchestration.** The Slack coordinating session (this one) acts as Atlas/orchestrator until PAP-96 exists, running the manual promotion pass by hand. One worker session per issue, launched on the issue's `Model` label, up to 16 in parallel. Wave 0 = PAP-13 (monorepo scaffold) plus the research/docs issues that do not depend on the scaffold; wave 1 = pure packages that build on the PAP-13 layout once it lands.
* **Conflict-avoidance conventions**, carried into the builder brief (`docs/build-log/builder-brief-v1.md`): one git worktree per issue; changelog fragments under `docs/changelog/unreleased/PAP-<n>.md` instead of direct edits to `CHANGELOG.md`; ADR numbers pre-assigned up front (register copied from the plan's module-system and interface-contracts documents) so two sessions never claim the same ADR number; root workspace files (`package.json`, `pnpm-workspace.yaml`, `turbo.json`, etc.) owned solely by PAP-13 during wave 0.

## Consequences

* Builders can start immediately against real, empty repositories instead of waiting on repo creation as a blocker.
* The plan's PR-gated quality bar is replaced by "green check before every push, plus a separate review pass before Done" — slightly weaker in that no second pair of eyes sees a diff before it lands on `main`, stronger in that nothing sits unmerged waiting on review capacity. If this build loop generates a regression on `main`, the fix is a follow-up commit, not a revert of an unmerged PR.
* Every session's final report must state repo, worktree, commit SHAs and paths touched, because there is no PR to look at afterwards — the Linear comment and this repo's docs are the only record.
* If Justin later renames `empty-11` / `empty12`, only the remote URL changes; branch names and worktree paths are unaffected.
* Reversible: Justin can reinstate a PR-based flow at any time by saying so; doing so does not require any change to Linear's structure (states, labels, projects), only to the builder brief's operating-mode section.

## Alternatives rejected

* **Wait for PAP-96 and real repos before starting.** Rejected: Justin's instruction was to start now and keep going; the plan already tolerates manual promotion passes as a documented fallback (CLAUDE.md promotion rule).
* **Keep the PR flow and route it through a human merge.** Rejected: contradicts Justin's explicit git-only, no-PRs policy, and there is no reviewer capacity to gate 30+ concurrent Ready issues by hand.
* **Treat `imagine-os/paperos` as `paperos-template` since the name matches.** Rejected: it is a different, already-existing product (PaperOS v2 canvas desktop); reusing it would corrupt a live repository that the PaperOS plan does not own.
