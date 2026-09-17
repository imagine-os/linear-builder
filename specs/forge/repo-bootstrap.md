---
identifier: "PAP-51"
title: "Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer", "Agent"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-48"]
blocks: ["PAP-276"]
key: "forge/repo-bootstrap"
url: "https://linear.app/paperos/issue/PAP-51/script-forge-bootstrap-repo-to-configure-imagine-os-repos-with-mirrors"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-51: Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks

**Goal**

Provide `forge bootstrap <repo>`, one idempotent command that turns a pre-provisioned, empty imagine-os repository into a fully wired PaperOS repo: Forgejo twin and mirrors, secrets, labels, webhooks, branch protection, templates and workflows, and Pages. The `paperos create` CLI (app-shell/create-cli) and the orchestrator call it rather than repeating the steps.

**Scope**

- In: the CLI package, its config files (labels, secrets manifest, webhook list), dry-run and check modes, tests against recorded API responses, and a runbook.
- Out: cloning template code into the repo (app-shell/create-cli does that after bootstrap), and creating Linear projects (pm-linear/configure-workspace owns the Linear side; this CLI only accepts a `--linear-project <id>` to write into the repo metadata).

**Spec**

Package `packages/forge-cli` in `imagine-os/paperos-template` (published later to the internal registry; for now run via `pnpm forge`). TypeScript, `citty` for commands, `octokit` for GitHub, a thin typed client for the Forgejo API (`packages/forge-cli/src/forgejo.ts`, generated from the Forgejo OpenAPI spec with `openapi-typescript`), `sops` invoked via child process for secrets.

Command `forge bootstrap <repo> [--dry-run] [--check] [--linear-project <id>] [--visibility private|public]` performs, in order, each step idempotent and logged as `[ok]`, `[changed]` or `[skip]`:

1. Verify `imagine-os/<repo>` exists on GitHub; abort with exit 3 if not (repos are pre-provisioned; do not create).
2. Create the Forgejo repo `imagine-os/<repo>` if missing with matching visibility.
3. Configure mirrors both ways by calling the functions exported from `ops/forge/mirror-all.ts` (moved into this package as `mirror.ts`) and register in `repos.yml`.
4. Secrets: read `ops/forge/secrets-manifest.yml` (names, which forge, source key in sops) and set repository/org Actions secrets on both forges; never print values.
5. Labels: sync from `ops/forge/labels.yml` (Type, Surface and Phase groups mirroring the Linear label groups) creating, recolouring or renaming by stable `id` comment; never delete unknown labels unless `--prune`.
6. Webhooks: orchestrator PR/push webhook (pm-linear/webhooks URL from config) with HMAC secret; drift-check webhook; delete duplicates.
7. Branch protection via `apply-branch-policy.ts` from forge/branch-policy.
8. If the default branch is empty, commit `README.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.forgejo/PULL_REQUEST_TEMPLATE.md`, `.github/workflows/{pr-lint,mirror-to-forgejo}.yml`, `CODEOWNERS` and `.paperos/repo.json` (`{ name, linearProject, forgejoUrl, githubUrl, createdAt, bootstrapVersion }`).
9. Enable GitHub Pages from the `gh-pages` branch (app-shell/gh-pages-demo convention) and store the URL in `repo.json`.
10. Print a summary table and a Linear-ready markdown block.

`--check` runs steps in read-only mode and exits 1 on any `[changed]`, for use as a nightly drift audit. Tests: Vitest with `msw` recordings for both APIs; a fixture repo `paperos-bootstrap-fixture` on both forges is used for one live integration test gated behind `FORGE_LIVE=1`.

**Definition of done**

- `forge bootstrap paperos-bootstrap-fixture` on a real empty repo completes with all ten steps `[ok]`/`[changed]`; second run is all `[ok]`/`[skip]` (both transcripts in PR).
- `--dry-run` performs zero write calls (asserted by msw).
- `--check` exits 1 after a label is manually altered, 0 after re-bootstrap.
- Unit coverage of each step above 80 per cent; typecheck clean.
- Runbook `docs/runbooks/repo-bootstrap.md` merged; `CLAUDE.md` mentions the command.
- Sentinel Security Auditor confirms secrets never appear in logs (test greps captured output).
- Linear comment with fixture repo links on both forges and the summary table.
- Changelog entry under "Tooling".

**Edge cases**

- Repo exists on Forgejo but not GitHub: exit 3 with guidance; GitHub remains the pre-provisioning source of truth.
- Partial failure at step 6: rerun resumes safely because every step is idempotent; no state file required.
- Rate limited by GitHub secondary limits during bulk bootstrap: exponential backoff with jitter, max 5 retries, then exit 4 listing remaining steps.
- Label exists with the same name but different colour: recolour, log `[changed]`.
- Pages cannot be enabled on a private repo under the current GitHub plan: log `[skip]` with reason; do not fail.
- Webhook secret rotated: `--rotate-webhook-secret` flag regenerates and updates the orchestrator config.

**Dependencies**

- forge/mirror (mirror functions), forge/bot-accounts (tokens and deploy keys). Soft: forge/branch-policy, forge/pr-templates, app-shell/gh-pages-demo, pm-linear/webhooks. Consumer: app-shell/create-cli.

**Agent**

- Builds: Forge (lead) with Ops Runner for live verification.
- Reviews: Sentinel (Code Reviewer, Security Auditor); Atlas checks the Linear metadata contract.

**Size**

M: ten well-defined idempotent steps over two APIs with recorded tests.
