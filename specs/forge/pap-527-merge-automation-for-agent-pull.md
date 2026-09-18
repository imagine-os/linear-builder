---
identifier: "PAP-527"
title: "Merge automation for agent pull requests: auto-merge when gates are green, GitHub merge queue, `forge merge` for Forgejo with rebase-and-retest, and the `merge-when-green` label contract"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46", "PAP-48", "PAP-521"]
blocks: ["PAP-88"]
key: "r4/forge/merge-automation"
url: "https://linear.app/paperos/issue/PAP-527/merge-automation-for-agent-pull-requests-auto-merge-when-gates-are"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:02.618Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-527: Merge automation for agent pull requests: auto-merge when gates are green, GitHub merge queue, `forge merge` for Forgejo with rebase-and-retest, and the `merge-when-green` label contract

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

The Blueprint says Justin never reviews PRs and Atlas merges when gates are green, yet no issue owns the merge step: PAP-46 protects `main`, PAP-81 to PAP-85 post verdicts, PAP-96 spawns sessions, PAP-88 cuts candidates. With twenty parallel PRs, merging by hand or by a session polling checks is the bottleneck GitHub and GitLab solved with merge queues. This issue makes merging mechanical on both forges.

**Scope**

In:

* Label contract: `merge-when-green` set by the PAP-89 digest or the session at PR open; `hold` blocks; the gates (PAP-239 artefacts) are the required checks `ci / check`, `gate2 / review`, `gate3 / visual`, `gate4 / edge` (the last two required from their milestone dates).
* GitHub: repository merge queue enabled by PAP-46 rulesets (`required_merge_queue`, squash, max 5 in queue, `ci / check` rerun on the queue branch); `paperos-agents` App (PAP-521) enqueues on label.
* Forgejo: `scripts/forge/merge.ts` (`forge merge <pr>`) run by a Forgejo Actions cron every 2 minutes: for labelled PRs in order of PAP-99 priority, rebase on `main`, wait for required checks on the rebased head, squash-merge with the PAP-46 commit grammar (`Linear:` and `Character:` trailers preserved), delete the branch; one at a time to emulate a queue.
* Post-merge: comment on the Linear issue through PAP-97 (`merged <sha>`), move to `In Review` → `Done` per PAP-92, trigger the staging deploy (PAP-26).
* Safety: never merge with a red or pending required check, an unresolved `request-changes` review from `bot-sentinel`, a `hold` label, a `Deferred` Linear issue, or when `main` is red; cross-owner PRs need the PAP-46 `cross-owner` label.

Out: the gates themselves (quality), release cuts (PAP-88), human review flows.

**Spec**

* Squash message: `<type>(<scope>): <title> (PAP-n)` plus trailers from the PR body; body includes the PR Summary section (PAP-49).
* Rebase conflicts: label `needs-rebase`, comment with the conflicting files, Linear comment; the owning session is re-woken by PAP-96.
* Idempotent: a PR already merged or closed is skipped; the queue state is derived from labels and checks, never stored.
* Throughput target: a green PR merges within 10 minutes of its last check on either forge.

**Interface contract**

Provides: labels `merge-when-green`, `hold`, `needs-rebase`; `forge merge`; merge-queue ruleset fragment; the required-check names list; consumed by PAP-88 (RC cut), PAP-89 (digest sets the label), PAP-96 (wake on `needs-rebase`), PAP-97 (status), PAP-99 (priority order), PAP-92 playbook.

Consumes: rulesets and commit grammar (PAP-46), bot identities and App (PAP-48, PAP-521), Gate 1 check names (PAP-78), gate artefacts (PAP-239, soft), Linear status path (PAP-97, soft), staging deploy (PAP-26, soft).

**Definition of done**

* Fixture repo: two labelled PRs with green checks merge in priority order on Forgejo within one cron cycle each; the same on GitHub through the queue (run URLs).
* A PR with a red `ci / check` or a `hold` label is never merged (negative tests); conflict path labels `needs-rebase` with the file list.
* `docs/engineering/merging.md`; PAP-92 and PAP-46 comments; CHANGELOG; Linear comment.

**Test plan**

* Unit: eligibility matrix (labels × checks × reviews × main state); squash message builder preserving trailers; priority ordering from PAP-99 fixtures.
* E2E: fixture PRs on both forges; conflict fixture; red-check fixture.

**Demo**

Reviewer labels a green fixture PR `merge-when-green` on Forgejo and within two minutes it is squash-merged with the Linear trailer and the branch deleted; the Linear issue shows the `merged` comment. Under 3 minutes.

**Edge cases**

* Check re-run flips red after enqueue: GitHub queue ejects it; Forgejo script re-waits and gives up after 30 minutes with a comment.
* Two PRs touch the same file: second rebases and re-tests; PAP-99 file-lock hints reduce this.
* Forgejo cron and GitHub queue both see the same mirrored PR: PRs are merged on the forge they were opened on; the mirror carries the result.
* `main` red: queue paused with a comment on the failing commit's Linear issue.

**Dependencies**

Hard: PAP-46, PAP-48. Soft: PAP-78 (the required check `ci / check` exists from PAP-13; gate checks are added to the required list as their milestones land), PAP-239, PAP-97, PAP-26, PAP-99, PAP-521. Blocks PAP-88.

**Agent**

Builder: Forge (Platform Engineer); Atlas (Merger) reviews policy. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/github-app-identities` = PAP-521.
