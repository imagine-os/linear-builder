---
identifier: "PAP-503"
title: "`paperos create` Linear seeding: project with milestones, starter issues from `templates/linear/starter-issues.yaml`, module list in the project description and the `--json` step summary"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-22", "PAP-47", "PAP-91", "PAP-520"]
blocks: ["PAP-28", "PAP-29", "PAP-266", "PAP-364", "PAP-365", "PAP-430", "PAP-498", "PAP-499", "PAP-500", "PAP-512"]
key: "r4/app-shell/cli-linear-seeding"
url: "https://linear.app/paperos/issue/PAP-503/paperos-create-linear-seeding-project-with-milestones-starter-issues"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:43.216Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-503: `paperos create` Linear seeding: project with milestones, starter issues from `templates/linear/starter-issues.yaml`, module list in the project description and the `--json` step summary

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The Linear half of `paperos create` is independent of the git and forge steps and is what makes a new app appear in the orchestrator queue with work already decomposed. Splitting it lets Atlas review the seeding payloads while Forge finishes the clone and push steps of PAP-22.

**Scope**

In:

* `packages/cli/src/create/linear.ts`: `LinearClient` interface with a fake; `ensureProject(name)` (team PAP, state planned, three milestones from `templates/linear/milestones.yaml`, description containing the module list and the six URLs), `seedIssues(projectId)` from `templates/linear/starter-issues.yaml`.
* Schema (Zod) for `starter-issues.yaml`: `{ title, description, labels: string[], state, milestone?, priority?, blockedBy?: string[] }` with label and state ids resolved from the PAP-91 workspace config; descriptions use the PAP-93 issue contract sections.
* Default starter set (five issues): second page spec, connect billing, invite team, first import, first release candidate; each `Type: Spec` or `Build`, state Backlog, one `Ready for Claude` (the second page spec).
* Idempotency: project looked up by name before create; issues deduplicated by a `paperos-starter:<slug>` marker in the description; `--dry-run` prints the payloads.

Out: clone, rename, push and forge bootstrap (PAP-22), golden path report posting (PAP-364), Linear webhooks (PAP-97).

**Spec**

* Project name collision: suffix `-<yyyymmdd>` and warn (PAP-22 rule).
* `RATELIMITED` handled with the header wait; total Linear time budgeted at 20 s (PAP-365 budget table).
* The `--json` summary gains `linearProject: { id, url, issues: [{ identifier, title }] }` read by PAP-29 and PAP-364.
* Descriptions pass the PAP-93 validator (`pnpm linear:validate --file`) in a unit test so starter issues never bounce from Ready.

**Interface contract**

Provides: `ensureProject`, `seedIssues`, `starter-issues.yaml` and `milestones.yaml` schemas, `linearProject` in the `--json` summary; consumed by PAP-22 (step 9), PAP-364 (first issue comment), PAP-29, PAP-96 (queue).

Consumes: label and state ids (PAP-91), issue contract sections (PAP-93), `@linear/sdk`, the module list from `--without` (PAP-266, soft).

**Definition of done**

* Fake-client snapshot of `projectCreate` and five `issueCreate` payloads committed; validator passes on every starter description.
* Real run against a sandbox project recorded; rerun creates nothing; `--dry-run` writes nothing.
* `docs/cli/create.md` Linear section; CHANGELOG; Linear comment with the sandbox project link.

**Test plan**

* Unit: schema rejects unknown label; marker dedupe; collision suffix; rate-limit wait with fake timers.
* E2E: nightly `cli-sandbox` run (PAP-22) asserts the project and issue count, then archives the project.

**Demo**

Reviewer runs `paperos create demo-clinic --linear-project --dry-run` and reads the five issue payloads, then the real run and opens the Linear project with milestones and one Ready issue. Under 2 minutes.

**Edge cases**

* Workspace issue cap (`USAGE_LIMIT_EXCEEDED`, NJ-1): the step records `pending` with the payload file so it can be replayed, and the summary says so instead of failing the create.
* Milestone names already used elsewhere: milestones are per project, no collision.
* `--without pm-linear`: seeding still runs (Linear is external), the description notes the module is off.

**Dependencies**

Hard: PAP-91. Soft: PAP-93 validator, PAP-266. Parent PAP-22 calls this as step 9.

**Agent**

Builder: Forge (Platform Engineer); Atlas (Dispatcher) reviews payloads. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-22 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-22 blocks this issue (`blocks` relation).
