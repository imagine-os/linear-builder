---
identifier: "PAP-702"
title: "Configure Linear's GitHub integration for `imagine-os`: branch-name format, PR autolinking, merge-to-Done as the only automatic transition, and reconciliation with the orchestrator's own state moves"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 2
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-91", "PAP-97", "PAP-520"]
blocks: ["PAP-254"]
key: "r4/pm-linear/linear-github-integration-and-state-automation"
url: "https://linear.app/paperos/issue/PAP-702/configure-linears-github-integration-for-imagine-os-branch-name-format"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:25.189Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-702: Configure Linear's GitHub integration for `imagine-os`: branch-name format, PR autolinking, merge-to-Done as the only automatic transition, and reconciliation with the orchestrator's own state moves

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Linear's native GitHub integration can move issues on PR open, review and merge, and the orchestrator (PAP-97, PAP-281) moves the same states itself; left unconfigured the two will fight, and left disabled Linear loses PR autolinks and the sanctioned merge-to-Done path that CLAUDE.md says only the merge flow may perform. This issue decides and configures both sides once.

**Scope**

* In: GitHub integration settings for the workspace (documented as a `Needs Justin` one-click since integration install is admin UI): connect org `imagine-os`, branch format `feat/PAP-{issueNumber}-{title}` (PAP-46), autolink on branch name and `Closes PAP-n`, automation: PR opened = no state change (orchestrator owns In Review), PR merged = Done, PR closed unmerged = no change; orchestrator reconciliation rules in `src/linear/reconcile.ts`; Forgejo mirror handling; `docs/pm/github-integration.md`.
* Out: GitHub App for CI and bot tokens (PAP-47, PAP-48), the webhook receivers (PAP-97), the merge itself (Atlas Merger), Forgejo native integration (none exists; PAP-97 covers).

**Spec**

* Decision recorded in `docs/pm/github-integration.md`: Linear owns autolinking and merge-to-Done; the orchestrator owns Ready, In Progress, In Review, Needs Justin and retries; nothing else moves Done or Canceled (Threat Model section 4).
* Branch format matches PAP-46 so Linear links PRs by branch name; `Closes PAP-n` in the PR body (PAP-49 template) is the fallback; mirrored Forgejo PRs are linked by PAP-97 with `attachmentCreate`, never by the integration.
* Reconciliation: on the `Issue.update` webhook where `actor` is the Linear GitHub integration and the new state is Done, the orchestrator verifies the merge SHA is on `main` of the GitHub mirror and that the RC or merge-flow record exists; otherwise it posts `done-without-merge-record` on the issue and the Plan audit (never reverts Done, per the deny list).
* PR opened by a session before any claim (PAP-97 edge): the integration links it; the orchestrator sets In Review and notes `no session record`.
* Umbrella issues: the integration never links an umbrella PR (children carry the branches); `UMBRELLA_CLOSE` moves the parent to In Review by hand.

**Interface contract**

* Provides: the integration configuration record, `reconcile.ts` rules, the `done-without-merge-record` comment, branch-format constant shared with PAP-46 and PAP-282.
* Consumes: Linear GitHub integration (admin UI, Needs Justin one-click), PAP-47 mirror, PAP-97 webhooks and actor ids, PAP-46 branch naming, PAP-49 template.

**Definition of done**

* Integration connected; a rehearsal PR autolinks by branch name and, when merged on the sandbox repo, moves the issue to Done with the merge record verified (recording).
* PR opened and closed unmerged leaves the state untouched (test on a rehearsal issue).
* Reconciliation posts `done-without-merge-record` on a seeded hand-move to Done (test); docs; changelog; Linear comment with the recording.

**Test plan**

* Unit: actor detection for the integration, merge-record verification, branch-name parsing shared with PAP-282.
* E2E: rehearsal PRs on the sandbox repo for open, merge and close-unmerged.

**Demo**

Open a rehearsal issue: the PR appears in the sidebar via the integration; merge the PR on the sandbox repo and watch the issue turn Done with no orchestrator write. Under two minutes.

**Edge cases**

* Squash merge rewrites the SHA: verification checks the PR merge commit, not the branch head.
* GitHub down, Forgejo primary (DR drill PAP-53): the integration is silent; PAP-97 Forgejo events link PRs and the Merger moves Done through the sanctioned flow.
* Justin merges a PR by hand outside the Merger: Done is honoured; the audit records it as `merge-outside-flow`.
* Two Linear issues in one branch name: the integration links the first; PAP-97 links the rest by `Closes`.

**Dependencies**

Hard: PAP-91, PAP-47, PAP-97. Soft: PAP-46, PAP-48, PAP-49, PAP-53, PAP-254.

**Agent**

Builder: Atlas (Dispatcher) with Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
