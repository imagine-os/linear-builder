---
identifier: "PAP-22"
title: "Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-47", "PAP-91"]
blocks: ["PAP-266", "PAP-28", "PAP-29"]
key: "app-shell/create-cli"
url: "https://linear.app/paperos/issue/PAP-22/write-paperos-create-app-cli-that-clones-the-template-into-an-imagine"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-22: Write `paperos create <app>` CLI that clones the template into an imagine-os repo and wires Forgejo mirror, CI, Pages and a Linear project

**Goal**

`paperos create <app>` takes a blank imagine-os repo to a running, tracked, deployable app in one command: it clones the template, renames identifiers, pushes to GitHub and Forgejo, configures CI and Pages, and creates a Linear project seeded with the standard starter issues. This is the direct answer to PAP-5.

**Scope**

In:
- `packages/cli/` published as `@paperos/cli` (bin `paperos`), built with `tsup`, using `commander` 13, `@clack/prompts`, `execa`, `simple-git`, `octokit`, `@linear/sdk`.
- Commands: `create <name> [--repo imagine-os/<name>] [--linear-project] [--no-push] [--template <ref>] [--yes]`, `doctor` (checks tokens/tools), `demo:url`.
- Steps: validate name; verify target repo exists and is empty; degit template at pinned tag; run `rename` (package names, `identifier`, manifest, README, CLAUDE.md); `pnpm i`; `pnpm check`; initial commit; push `main`; call `forge bootstrap` (`forge/repo-bootstrap`) for mirror, secrets, labels, webhooks; enable Pages; create Linear project with description, milestones and starter issues from `templates/linear/starter-issues.yaml`; print URLs.
- Idempotent re-run: each step records completion in `.paperos/create.state.json` and skips.
- Dry-run mode printing the plan.

Out: provisioning the GitHub repo itself (pre-provisioned by convention), VPS deploy (Coolify hookup is `data-layer/postgres-provision`/ops), interactive spec interview (`spec-builder/spec-authoring-skill`).

**Spec**

- Tokens read from env (`GITHUB_TOKEN`, `FORGEJO_TOKEN`, `LINEAR_API_KEY`) or `SecretStore` (`app-shell/env-config`); `doctor` reports which are present without printing values.
- Name rules: kebab-case, 3-40 chars, not reserved; derived `PascalName`, `identifier os.imagine.paperos.<name>`.
- Rename implemented as a token-replacement map applied to a curated glob list (no blind sed on binaries); tested against a fixture template.
- Linear: team `PAP` by default (`--team`), project state `planned`, labels from `pm-linear/configure-workspace`; starter issues include "Write app.spec.yaml", "First page spec", "Enable design tokens", each in Backlog with the `Spec` label.
- Output summary: repo URLs (GitHub, Forgejo), Pages URL, Linear project URL, next steps.
- Exit codes: 0 success, 2 validation, 3 external API failure with retry hint.
- Logs written to `.paperos/create.log` for agent post-mortems; also emits a Linear comment on the new project's first issue linking the log if `--linear-project`.
- Unit-test external calls behind interfaces (`GitHubClient`, `ForgejoClient`, `LinearClient`) with fakes.

**Definition of done**

- Running against a throwaway imagine-os repo produces a green CI, a live Pages URL and a Linear project within 10 minutes; recording attached.
- Re-running is a no-op (state file) and `--force` redoes steps.
- Vitest covering name validation, rename map, state machine, fakes for all clients; e2e script in CI using a sandbox repo (nightly, not per-PR).
- `paperos doctor` output screenshot; generated app's home screenshots at 375, 1024, 1920.
- `docs/cli/create.md`; README quick start updated; CHANGELOG; Linear comment with the demo app's links.

**Edge cases**

- Target repo not empty: abort unless `--force-empty` explicitly given; never delete history.
- Rate-limited GitHub API: exponential backoff, resume from state.
- Linear project name collision: suffix with date and warn.
- Missing Forgejo token: skip mirror step with a warning, mark state `pending` so `forge bootstrap` can finish later.
- Template tag not found: list available tags.
- Running inside an existing git repo directory: refuse.

**Dependencies**

`app-shell/router-layouts` (template must be real), `forge/mirror` and `forge/repo-bootstrap` (mirror step), `pm-linear/configure-workspace` (labels/states), `app-shell/gh-pages-demo` (Pages settings). Feeds `agents/skills-library` (a `create-app` skill wraps it).

**Agent**

Built by Forge with Atlas's Dispatcher sub-agent reviewing the Linear side. Reviewed by Sentinel (Code Reviewer) and Quill (docs).

**Size**

M: orchestration of known APIs; complexity is idempotency and clean failure modes.
