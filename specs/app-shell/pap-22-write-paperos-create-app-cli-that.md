---
identifier: "PAP-22"
title: "Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-47", "PAP-91", "PAP-520"]
blocks: ["PAP-28", "PAP-29", "PAP-266", "PAP-364", "PAP-365", "PAP-430", "PAP-498", "PAP-499", "PAP-500", "PAP-503", "PAP-512"]
key: "app-shell/create-cli"
url: "https://linear.app/paperos/issue/PAP-22/write-paperos-create-app-cli-that-clones-the-template-into-an-imagine"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:43.366Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-22: Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

`paperos create <app>` takes a blank imagine-os repo to a running, tracked, deployable app in one command: clone the template at a pinned tag, rename identifiers, push to GitHub and Forgejo, configure CI, Pages and Coolify, and create a Linear project seeded with starter issues. It is the direct answer to PAP-5 and the entry point the drill (PAP-29) times.

**Scope**

In:

* `packages/cli` published as `@paperos/cli` (bin `paperos`), `tsup`, `commander` 13, `@clack/prompts`, `execa`, `simple-git`, `octokit`, `@linear/sdk`.
* `create <name> [--repo] [--linear-project] [--no-push] [--template <ref>] [--without <modules>] [--yes] [--dry-run]`, `doctor`, `demo:url`.
* Idempotent state in `.paperos/create.state.json`; logs in `.paperos/create.log`.
* Starter issues from `templates/linear/starter-issues.yaml`.

Out: repo provisioning (repos pre-exist), mirror and secrets wiring (delegated to `forge bootstrap`, PAP-51), template upgrades (forge upgrade-path issue).

**Spec**

* Steps: validate name; verify repo exists and is empty; `degit` template at tag; rename map over a curated glob list; `pnpm i && pnpm check`; commit; push `main`; `forge bootstrap <repo> --linear-project <id>`; enable Pages; copy `deploy.yml` and `preview.yml` (PAP-26) with app name templated; create Linear project (team PAP, state planned, milestones, starter issues with the `Spec` label); print URLs.
* Name rules: kebab-case 3-40 chars, not reserved; derived `PascalName`, `identifier os.imagine.paperos.<name>`.
* Tokens from env or `SecretStore`; `doctor` reports presence, never values.
* Exit codes 0 success, 2 validation, 3 external API failure with retry hint.
* Clients behind interfaces `GitHubClient`, `ForgejoClient`, `LinearClient` with fakes.
* `--without` passes through to PAP-28 module removal once it lands; until then it warns and continues.

**Interface contract**

Provides:

* Bin `paperos` with `create`, `doctor`, `demo:url`, later `upgrade` (forge upgrade issue) and `kiosk install` (PAP-23); machine-readable `--json` summary `{ repo: { github, forgejo }, pages, linearProject, steps: [{ name, status, ms }] }` that PAP-29's timer harness reads.
* State file schema `.paperos/create.state.json` v1.
* `templates/linear/starter-issues.yaml` schema `{ title, description, labels[], state }`.

Consumes: `forge bootstrap` CLI contract (PAP-51: exit codes, `[ok]/[changed]/[skip]` lines), Linear label and state ids (PAP-91), Pages settings (PAP-15), `deploy.yml` template (PAP-26), `SecretStore` (PAP-17).

*Round 4 amendment (2026-09-18):*

* Writes `.paperos/template.json` `{ ref, tag, appliedAt, ownership: "templates/ownership.yaml" }` at creation (PAP-430 reads it and lists it as written here); the schema is co-owned with PAP-430. Step 9 (Linear project and starter issues) is delivered by PAP-503; the `--json` summary includes its `linearProject` block.

**Definition of done**

* Against a throwaway repo: green CI, live Pages URL, staging URL and Linear project within 10 minutes (recording).
* Re-run is a no-op; `--force` redoes steps.
* Vitest: name validation, rename map, state machine, client fakes; nightly e2e against a sandbox repo.
* `paperos doctor` screenshot; generated app at 375, 1024, 1920.
* `docs/cli/create.md`; README quick start; CHANGELOG; Linear comment with the demo app's links.

**Test plan**

* Unit: name validator table (40 cases), rename map on a fixture template (binary files untouched), state machine resume from each step, exit codes.
* Contract: fake clients record calls; snapshot of the Linear `projectCreate` and `issueCreate` payloads.
* Integration: `--dry-run` prints the plan and performs zero writes (asserted by fakes).
* E2E nightly: real run on `imagine-os/cli-sandbox`, then teardown; duration and step timings posted to the workflow summary.
* Visual: generated app home at 375, 1024, 1920 from its Pages URL.

**Demo**

Reviewer runs `paperos doctor`, then `paperos create demo-clinic --repo imagine-os/demo-clinic --linear-project --yes`, watches ten steps complete, opens the printed Pages URL and the Linear project with three starter issues. Roughly 8 minutes wall clock; the reviewer watches the first two and last one.

**Edge cases**

* Target repo not empty: abort without `--force-empty`; never delete history.
* GitHub rate limit: backoff and resume from state.
* Linear project name collision: suffix date and warn.
* Missing Forgejo token: skip mirror, mark `pending`, `forge bootstrap` finishes later.
* Running inside an existing git directory: refuse.

**Dependencies**

PAP-16 (real template), PAP-47 and PAP-51 (mirror and bootstrap), PAP-91 (labels and states), PAP-15, PAP-26. Feeds PAP-28, PAP-29, PAP-108.

*Round 4 amendment (2026-09-18):*

* Soft dependency (round 4): PAP-715 (claude-code-plugin-packaging) would block this issue but sits in a later milestone (2026-09-25 > 2026-09-24); no `blocks` relation was created. Build against its interface and reconcile when it lands.

**Agent**

Built by Forge; Atlas (Dispatcher) reviews the Linear seeding. Reviewed by Sentinel.

**Size**

M: orchestration of existing pieces with strong tests.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/cli-linear-seeding` = PAP-503.

*Round 4 critique fix (2026-09-18):* PAP-503 was split out as a follow-on issue (FIX-R4-1); this issue is a leaf again with its Model / Effort labels and estimate restored, and it blocks PAP-503.
