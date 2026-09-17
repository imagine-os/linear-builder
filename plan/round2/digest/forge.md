# forge — Version Control & Forge Independence
PHASE P0 prio 1 dependsOn []
SUMMARY: Git stays the format; a self-hosted Forgejo becomes our forge, mirrored both ways with GitHub, with its own CI runners and a proven recovery drill.
DESC: Goal: PaperOS is never hostage to GitHub while keeping every Git-based tool agents rely on. We deploy Forgejo on our VPS behind Caddy with SSO, mirror every imagine-os repo bidirectionally, run Forgejo Actions runners so CI survives a GitHub outage, and script repo bootstrap so pre-provisioned repos get mirrors, secrets, labels and webhooks automatically. Branch protection, conventional commits and worktree-per-issue conventions make parallel agent work safe. A disaster-recovery drill rebuilds everything from Forgejo backups with GitHub offline. Non-goal: a from-scratch version control system; the ADR records why. Later, repo browsing and diffs surface inside PaperOS via the Forgejo API.
MILESTONES: ['Forgejo live and mirrored 2026-09-19: Forgejo deployed, all repos mirrored, bot accounts and branch policy in place', 'CI runs on both forges 2026-09-24: Actions runners, bootstrap script and release automation', 'Disaster recovery proven 2026-09-30: Drill passes; in-app git browsing']


## PAP-44 [P0 Spec S prio1 Ready for Claude] Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS
key=forge/vcs-decision-adr milestone=Forgejo live and mirrored agent=* Builds: Forge (lead), drafting personally rather than via 
blockedBy=[] blocks=[]
GOAL: Record, as an Architecture Decision Record, why PaperOS keeps Git as its storage format, self-hosts Forgejo as the primary forge, mirrors to the GitHub org imagine-os, and defers any custom version control system. The ADR must be concrete enough that a future agent can tell whether the conditions that would reopen the decision have been met, and it becomes the reference every forge issue links to.
SCOPE: * In: the ADR document, a comparison table of alternatives, explicit reopen criteria, and a one-paragraph summary for the Linear project description.
* In: registering the ADR in the decision log index (`docs/decisions/README.md`).
* Out: any implementation work (covered by forge/forgejo-deploy and forge/mirror).
* Out: choosing the CI runner or backup tooling; those get their own ADR notes inside their issues.
SPEC(first 1200): Create `docs/decisions/ADR-0001-version-control-and-forge.md` in the `imagine-os/paperos-template` repo (create `docs/decisions/` if absent). Use MADR 4 structure with these headings in order: Status (Accepted, date 2026-09-17, deciders: Atlas, Forge, Justin), Context, Decision, Alternatives Considered, Consequences, Reopen Criteria, Links.

Alternatives Considered must be a table with rows for: (a) GitHub only; (b) self-hosted GitLab CE; (c) Gitea; (d) Forgejo; (e) Jujutsu (jj) on a Git backend; (f) Pijul as a new format; (g) a from-scratch PaperOS VCS. Columns: agent tooling compatibility (Claude Code, gh CLI, Actions), self-host cost (RAM, disk, ops hours/week), migration effort in days, license (note GitLab CE is MIT but EE features are proprietary; Forgejo is GPLv3+ since v9), risk of vendor capture, and a 1-5 score using the rubric from libraries/eval-rubric if it has landed, otherwise state the six criteria inline.

Decision section states: Git remains the format; Forgejo (pin the current stable major) is the primary forge; GitHub is a mirror and public front door; Forgejo Actions is the CI fallback; a custom VCS is deferred. Consequences lists at least five, including "ever
DOD:
* ADR file exists at the path above, passes `pnpm biome check` for markdown formatting, and renders in GitHub preview without broken tables.
* Comparison table has all seven alternatives with every column filled; no "TBD".
* Reopen criteria are all numerically testable.
* `docs/decisions/README.md` index row added.
* PR opened using the forge/pr-templates template (or the interim template if that issue has not merged), linked to this Linear issue.
* Sentinel's Code Reviewer sub-agent approves; Quill reviews wording.
* Linear comment posted with the rendered ADR link on GitHub and a three-line summary.
* Changelog entry under "Docs" in the PR summary.
EDGE:
* libraries/eval-rubric has not merged: write the six criteria inline and add a TODO link to the rubric issue rather than blocking.
* `docs/decisions/` already contains an ADR-0001 from collab/decision-log: take the next free number and update the index accordingly.
* Forgejo licence changes mid-build: the ADR must record the version and licence checked.
* Justin disagrees with deferring a custom VCS: the ADR Status becomes "Proposed" and the issue moves to Needs Justin with the table as the decision aid.
* Reviewer cannot verify a cost figure: cite a source URL in a footnote; unsourced numbers are a review blocker.
DEPS: * None blocking. Soft references: libraries/eval-rubric (criteria), collab/decision-log (ADR index format), forge/forgejo-deploy and forge/mirror (consumers of this decision).


## PAP-45 [P0 Infra L prio1 Backlog] Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups
key=forge/forgejo-deploy milestone=Forgejo live and mirrored agent=* Builds: Forge, via the Ops Runner sub-agent.
* Reviews: Se
blockedBy=['PAP-25'] blocks=['PAP-54', 'PAP-50', 'PAP-48', 'PAP-47']
GOAL: Stand up PaperOS's own Git forge: Forgejo running in Docker on the Hetzner VPS under Coolify, served over TLS by Caddy, with an org structure that mirrors imagine-os, nightly backups that are proven restorable, and an OIDC login path from Better Auth ready to switch on. After this issue, every later forge issue has a live server to configure.
SCOPE: * In: Docker Compose stack (Forgejo, its Postgres, backup sidecar), Caddy/Coolify routing, `app.ini` hardening, admin and service accounts, org `imagine-os`, backup and restore scripts, runbook.
* In: OIDC auth source configuration prepared and documented; enabled when identity/better-auth ships.
* Out: mirroring (forge/mirror), runners (forge/actions-runner), per-character bots (forge/bot-accounts).
* Out: using the application Postgres from data-layer/postgres-provision; Forgejo gets its own isolated database container.
SPEC(first 1200): Repository: `imagine-os/paperos-infra` (one of the pre-provisioned empty imagine-os repos; if it does not exist, create it with that exact name). Files:

* `ops/forgejo/docker-compose.yml`: services `forgejo` (image `codeberg.org/forgejo/forgejo:<current stable major, pinned to a digest>`), `forgejo-db` (`postgres:17-alpine`), `forgejo-backup` (alpine with `restic` cron). Volumes `forgejo-data`, `forgejo-db`. Forgejo HTTP on 3000 internal; SSH on host port 2222.
* `ops/forgejo/app.ini.tmpl` rendered by Coolify env vars: `ROOT_URL=https://git.${PAPEROS_DOMAIN}/`, `DISABLE_REGISTRATION=true`, `REQUIRE_SIGNIN_VIEW=false`, `ENABLE_PUSH_CREATE_ORG=false`, `[actions] ENABLED=true`, `[lfs] enabled`, `[webhook] ALLOWED_HOST_LIST=private,${ORCHESTRATOR_HOST}`, `[mailer]` via Resend SMTP, `[oauth2_client] ENABLE_AUTO_REGISTRATION=true`, `[repository] DEFAULT_BRANCH=main`, `[security] INSTALL_LOCK=true`.
* Coolify: create a "Docker Compose" resource pointing at this file; proxy set to Caddy; domain `git.${PAPEROS_DOMAIN}` with automatic Let's Encrypt; health check `GET /api/healthz` every 30 s.
* Accounts: admin `justin` (created via `forgejo admin user create`, must-change-password), service
DOD:
* `https://git.<domain>/` loads with a valid certificate; `/api/healthz` returns 200.
* `git clone` over HTTPS and over SSH port 2222 works from a fresh machine using a deploy token.
* Registration is disabled; only `justin` and `paperos-admin` exist.
* One backup snapshot exists in object storage and `restore.sh` restores it into a scratch stack whose UI shows the same repos.
* Compose file and `app.ini.tmpl` committed; secrets only in sops-encrypted files (Sentinel Security Auditor confirms no plaintext).
* Runbook `docs/runbooks/forgejo.md` covers deploy, upgrade, backup, restore and the SSO switch.
* Playwright screenshot of the Forgejo landing page at 1280 and 375 widths attached to the PR (proves TLS and branding).
* Linear comment with the forge URL, backup bucket name and the restore drill timing.
EDGE:
* VPS has under 4 GB RAM: set `FORGEJO__cron__ENABLED` conservatively and document the minimum spec; do not co-locate runners on the same host yet.
* Coolify's default proxy is Traefik: switch the server proxy to Caddy before creating the resource, or document the equivalent Traefik labels as a fallback.
* Let's Encrypt rate limit hit during retries: use the staging CA for testing, switch to production once.
* Object storage credentials rotate: backup script must fail loudly (exit non-zero, post to the orchestrator webhook) rather than silently skipping.
* Forgejo major upgrade requires migration: runbook includes a pre-upgrade snapshot step and a `forgejo migrate` command.
* SSH port 2222 blocked on some networks: document HTTPS token auth as the primary agent path.
DEPS: * app-shell/vps-coolify-bootstrap (hard: the Hetzner host, Coolify with Caddy proxy, `git.` DNS record, sops keys and backup bucket). Soft: identity/better-auth (SSO switch), data-layer/observability (metrics scrape), forge/vcs-decision-adr (rationale).


## PAP-46 [P0 Spec M prio1 Ready for Claude] Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents
key=forge/branch-policy milestone=Forgejo live and mirrored agent=* Builds: Forge (lead).
* Reviews: Sentinel (Code Reviewer) 
blockedBy=[] blocks=['PAP-133', 'PAP-96', 'PAP-52', 'PAP-49']
GOAL: Define and enforce the conventions that let up to twenty Claude Code sessions commit in parallel without colliding: branch naming, one git worktree per Linear issue, Conventional Commits with Linear trailers, and protection rules on `main` applied identically on Forgejo and GitHub. The output is both a document and machine-applied configuration.
SCOPE: * In: policy document, branch-protection rulesets as JSON applied by script to both forges, commitlint and lefthook configuration in the template repo, a worktree helper script, CODEOWNERS ownership map per character.
* Out: the orchestrator that spawns sessions (pm-linear/orchestrator) and the concurrency scheduler (pm-linear/concurrency); this issue only gives them rules and hints to consume.
* Out: release tagging (forge/release-tags).
SPEC(first 1200): Document `docs/engineering/branch-policy.md` in `imagine-os/paperos-template` covering:

* Branch names: `<character>/<PAP-n>-<kebab-slug>` (e.g. `forge/PAP-42-mirror-setup`); release branches `release/<yyyy-mm-dd>`; no direct pushes to `main`.
* Worktrees: every session works in `../paperos-worktrees/PAP-<n>` created by `scripts/worktree.sh new PAP-<n>` (which also creates the branch, copies `.env.example`, runs `pnpm install --offline` when possible); `scripts/worktree.sh done PAP-<n>` removes it after merge.
* Commits: Conventional Commits 1.0 (`feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`), scope = package or app name; body wraps at 100; mandatory trailers `Linear: PAP-<n>` and `Character: <Name>`, optional `Co-Authored-By`. Enforced by `commitlint` (`@commitlint/config-conventional` plus a custom rule for the trailers) run via `lefthook` `commit-msg` hook and again in quality/ci-gate1.
* File ownership: `.github/CODEOWNERS` (mirrored to `.forgejo/CODEOWNERS`) maps paths to character bot accounts (packages/ui -> Iris, specs/ docs/ -> Quill, ops/ -> Forge, and so on) matching the access lists in plan.json; it doubles as the file-lock hint source for p
DOD:
* Policy document merged and linked from the template README.
* `lefthook.yml`, `commitlint.config.ts` present; a commit lacking `Linear:` trailer is rejected locally and in CI (test committed under `scripts/__tests__/commitlint.test.ts`).
* `scripts/worktree.sh new PAP-999` creates a worktree and branch; `done` removes both; covered by a bats or Vitest shell test.
* `apply-branch-policy.ts` applied to `paperos-template` on both forges; a direct push to `main` is rejected on each (evidence: terminal output in PR).
* CODEOWNERS and `ownership.json` generated and consistent (test asserts round-trip).
* Sentinel Code Reviewer approves; Atlas confirms the ownership map matches the roster.
* Linear comment with links to the document and the two rejected-push transcripts.
* Changelog entry under "Engineering".
EDGE:
* An issue spans two characters' paths: the PR requires both owners' bot review or an Atlas override label `cross-owner`; document the override.
* Hotfix needed while `main` checks are red: `hotfix/<PAP-n>` branches allowed only by Atlas with a Needs Justin comment.
* Forgejo and GitHub ruleset feature parity differs (GitHub rulesets support required workflows; Forgejo does not): the script degrades gracefully and prints what could not be applied.
* Commit made by a human without lefthook installed: CI check catches it; error message explains the trailer format.
* Worktree directory already exists with uncommitted changes: script refuses and prints the path rather than deleting.
* Branch name exceeds 100 characters because of a long slug: slug truncated to 40 characters.
DEPS: * None blocking. Consumers: pm-linear/orchestrator, pm-linear/concurrency, quality/ci-gate1, forge/pr-templates, forge/release-tags. Tokens from forge/bot-accounts are needed to run `apply-branch-policy.ts` against Forgejo; use `paperos-admin` until then.


## PAP-47 [P0 Infra M prio1 Backlog] Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos
key=forge/mirror milestone=Forgejo live and mirrored agent=* Builds: Forge, via the Ops Runner sub-agent.
* Reviews: Se
blockedBy=['PAP-45'] blocks=['PAP-53', 'PAP-51', 'PAP-22']
GOAL: Make every repository in the GitHub org imagine-os exist on Forgejo as well, with commits pushed to either side arriving on the other within one minute, so that either forge can act as primary and agents never have to care which one is up. Drift must be detected automatically.
SCOPE: * In: Forgejo -> GitHub push mirrors, GitHub -> Forgejo propagation via a workflow plus a Forgejo pull-mirror fallback, a script that configures all repos, a drift monitor, and a documented conflict rule.
* Out: creating new repos for new apps (forge/repo-bootstrap) and issue/PR metadata sync (issues live in Linear).
* Out: mirroring wikis or GitHub-only features (Discussions, Projects).
SPEC(first 1200): In `imagine-os/paperos-infra`:

* `ops/forge/mirror-all.ts` (TypeScript, run with `pnpm tsx`): lists imagine-os repos via GitHub REST (`GET /orgs/imagine-os/repos`), and for each: creates the Forgejo repo under `imagine-os` if missing (private flag copied), sets a Forgejo push mirror to `https://github.com/imagine-os/<repo>.git` with a fine-grained GitHub PAT (contents: read/write, scoped to the org) and `interval=10m` plus `sync_on_commit=true`, and records the pair in `ops/forge/repos.yml`. Idempotent; `--dry-run` prints planned changes; `--only <repo>` limits scope.
* GitHub -> Forgejo: a reusable workflow `.github/workflows/mirror-to-forgejo.yml` added to every repo (via the bootstrap script later, by hand for the first set) triggered on `push` to any branch and tag; it does `git push --mirror` (excluding `refs/pull/*`) to Forgejo using a deploy token from forge/bot-accounts (interim: `paperos-admin` token). Fallback: a Forgejo pull mirror is not used for the same repo (Forgejo forbids push and pull mirror on one repo); instead the fallback is a Forgejo Actions cron in forge/actions-runner that fetches from GitHub every 10 minutes when the workflow has not run.
* Loop safety: m
DOD:
* Every current imagine-os repo appears on Forgejo with identical branch heads and tags (`mirror-check.ts` reports zero drift).
* A commit pushed to Forgejo `main` on a test repo appears on GitHub within 60 s; a commit pushed to GitHub appears on Forgejo within 60 s; timings recorded in the PR.
* Divergence test: force-different commits on both sides produce a Linear issue, not a force-push (evidence linked).
* `mirror-all.ts --dry-run` and real run are idempotent (second run makes no API writes; test asserts on recorded HTTP calls).
* Secrets only in sops or forge secret stores; Sentinel Security Auditor confirms token scopes are minimal.
* Runbook merged; Linear comment with the drift dashboard output and timing evidence.
* Changelog entry under "Infra".
EDGE:
* Repo over 1 GB or with LFS objects: enable LFS mirroring flag; document that initial sync may exceed a minute.
* GitHub PAT expires (fine-grained tokens max 1 year): monitor treats 401 as drift with a distinct message "credential expired".
* Repo renamed on GitHub: script detects by repo id, renames on Forgejo, updates `repos.yml`.
* Archived GitHub repo: mirrored read-only, flagged `archived: true` in `repos.yml`; push mirror disabled.
* Protected branch on GitHub rejects the mirror push: the mirror token must bypass rulesets via an actor allowlist (set in forge/branch-policy rulesets).
* Forgejo down while GitHub receives pushes: the workflow fails and retries with backoff; the cron fallback catches up.
DEPS: * forge/forgejo-deploy (must exist to host repos). Soft: forge/bot-accounts (dedicated mirror token), forge/actions-runner (cron fallback), forge/branch-policy (bypass allowlist), pm-linear/webhooks (alert path).


## PAP-48 [P0 Infra M prio2 Backlog] Create scoped bot accounts and deploy keys for each agent character on both forges
key=forge/bot-accounts milestone=Forgejo live and mirrored agent=* Builds: Forge (Ops Runner sub-agent).
* Reviews: Sentinel 
blockedBy=['PAP-45'] blocks=['PAP-106', 'PAP-51']
GOAL: Give every agent character a least-privilege identity on both forges so that commits, PRs and API calls are attributable to Atlas, Forge, Iris and the rest rather than to Justin or a shared token. Access must match each character's `access` list in plan.json exactly, and rotation must be one command.
SCOPE: * In: Forgejo bot accounts per lead character, a single GitHub App for API actions with per-character commit identities, deploy keys for CI, scoped tokens, a secrets layout, a rotation script and an access matrix document.
* Out: enforcing which MCP tools a character may call (agents/tool-scopes consumes this issue's tokens), and human accounts.
* Out: sub-character identities; sub-agents act under their lead's identity with a `Sub-Agent:` commit trailer.
SPEC(first 1200): Forgejo (in `imagine-os/paperos-infra`, script `ops/forge/bots.ts`):

* Create users `bot-atlas`, `bot-forge`, `bot-iris`, `bot-quill`, `bot-sentinel`, `bot-nova`, `bot-ledger`, `bot-beacon`, `bot-scout` with emails `<name>@agents.<domain>` (must-change-password disabled, `restricted=false`, `is_bot` semantics via a `bot` prefix and profile description linking to the character handbook).
* Team membership in org `imagine-os`: `agents` team (write) for builders; `bot-sentinel` gets a `reviewers` team with read plus PR review rights but no push to protected branches; `bot-atlas` additionally in `owners` for merges; `bot-scout` read-only plus write to `docs/registry` enforced by CODEOWNERS rather than Forgejo (Forgejo has no path-scoped write).
* Per-bot access token with the minimal scopes (`write:repository`, `write:issue` for builders; `read:repository` plus `write:issue` for Sentinel; `write:organization` for Atlas). Tokens stored in `ops/secrets/bots.enc.yaml` (sops + age; age recipients: Justin's key and the orchestrator host key) and mirrored into the Coolify secrets store for the orchestrator.

GitHub:

* One GitHub App `paperos-agents` installed on imagine-os with permissions
DOD:
* Nine Forgejo bots exist; `ops/forge/bots.ts audit` prints the matrix and exits non-zero on any deviation from `ops/forge/access-matrix.yml` (test committed).
* GitHub App installed; a session can mint a token and open a PR attributed to the App with a `Forge (PaperOS agent)` commit author.
* A `bot-sentinel` push to `main` on a test repo is rejected; a review from it is accepted (transcripts in PR).
* Rotation script run once end to end; old token verified revoked.
* No plaintext secret in git history (Sentinel Security Auditor runs gitleaks).
* `.mailmap` and `allowed_signers` committed; `git log --show-signature` on a test commit prints "Good signature".
* Access matrix document merged; Linear comment with audit output.
* Changelog entry under "Infra".
EDGE:
* GitHub organisation policy blocks Apps: fall back to one fine-grained PAT per character on a machine user, documented as the degraded mode with cost noted.
* A character is added later (agents/roster-v1 changes): `bots.ts` reads the roster file and creates missing bots; never deletes without `--prune`.
* Token leaked in a prompt log: rotation must complete in under 5 minutes; runbook includes the exact command and how to purge the log via collab/prompt-log-store redaction.
* Forgejo rate limit for a bot hit by a busy session: document per-bot limits and the orchestrator's backoff.
* Two sessions share a character concurrently: tokens are per character not per session, so attribution stays correct but the audit log distinguishes sessions via the `Linear:` trailer.
DEPS: * forge/forgejo-deploy (server must exist). Consumers: agents/tool-scopes, forge/repo-bootstrap, forge/mirror (dedicated mirror token), pm-linear/orchestrator.


## PAP-49 [P0 Docs S prio2 Backlog] Author PR template linking Linear issue, page spec, screenshots and the review-gate checklist
key=forge/pr-templates milestone=Forgejo live and mirrored agent=* Builds: Quill (Changelog Scribe sub-agent) for the templat
blockedBy=['PAP-46'] blocks=[]
GOAL: Every pull request opened by an agent or a human carries the same structure: the Linear issue, the page specs touched, a summary, the screenshot matrix, the test plan, the review-gate checklist, risk and rollback. Reviewer agents and Justin then always know where to look, and a lint step rejects PRs missing the essentials.
SCOPE: * In: PR template files for both forges, a generator script that pre-fills the template from Linear, a lightweight CI check that validates the body, and guidance in the session playbook.
* Out: the reviewer agents themselves (quality/review-agents) and screenshot capture (quality/playwright-matrix); this issue only reserves the sections they fill.
SPEC(first 1200): In `imagine-os/paperos-template`:

* `.github/PULL_REQUEST_TEMPLATE.md` and an identical `.forgejo/PULL_REQUEST_TEMPLATE.md` (Forgejo also honours `.gitea/`; keep one source and copy via `scripts/sync-templates.ts` so they never diverge; a test asserts byte equality).
* Template sections, in order, each a level-2 heading with an HTML comment explaining what to put there (comments are the only HTML permitted):
  1. `Linear` - `Closes PAP-<n>` line plus the issue title.
  2. `Specs` - list of `specs/**/page.spec.yaml` files added or changed, or the literal `No spec changes (infra/docs)`.
  3. `Summary` - three to six bullets, plain language for Justin.
  4. `Screenshots` - a table with rows for the seven widths from app-shell/device-matrix-research (placeholders `320`, `375`, `768`, `1024`, `1280`, `1536`, `1920` until that issue lands) and columns light/dark; Gate 3 replaces placeholders with image links.
  5. `Test plan` - commands run and their results.
  6. `Review gates` - checkboxes: Gate 1 static, Gate 2 correctness, Gate 2 security, Gate 2 spec conformance, Gate 3 visual, Gate 4 edge cases; bots tick these via the checks API, agents must not tick them by hand.
  7. `Risk and 
DOD:
* Both template files exist and are byte-identical (test).
* `pnpm tsx scripts/pr-body.ts --issue PAP-5` produces a valid body with the issue title (recorded output in PR).
* `pr-lint` fails a PR with no Linear key and passes one that complies (two demo PRs linked).
* Template referenced from `docs/engineering/branch-policy.md` and `CLAUDE.md`.
* Sentinel Code Reviewer approves; Quill reviews wording of the HTML comments.
* Screenshot of a rendered PR on GitHub and on Forgejo at 1280 width attached.
* Linear comment with the demo PR links; changelog entry under "Docs".
EDGE:
* Issue not found in Linear (typo): generator exits 2 with the key and a hint; does not print a partial body.
* PR closes several issues: multiple `Closes` lines allowed; lint accepts one or more.
* Docs-only PR with no screenshots: the Screenshots table may be replaced by `Not applicable (no UI change)`, and lint accepts that exact phrase.
* Forgejo renders task lists differently from GitHub: verify the checkbox syntax `- [ ]` renders on both; screenshot proves it.
* Body over 65 536 characters (GitHub limit) from long test output: generator truncates the Test plan section with a link to the CI run.
DEPS: * forge/branch-policy (defines commit and PR conventions the template references). Soft: app-shell/device-matrix-research (final width list), forge/bot-accounts (bot author list), pm-linear/session-playbook (usage instructions).


## PAP-50 [P1 Infra M prio2 Backlog] Run Forgejo Actions runners so CI works even when GitHub is unavailable
key=forge/actions-runner milestone=CI runs on both forges agent=* Builds: Forge (Ops Runner sub-agent).
* Reviews: Sentinel 
blockedBy=['PAP-45'] blocks=['PAP-53']
GOAL: Run Forgejo Actions runners on our own infrastructure so that the same workflow files execute on Forgejo when GitHub is unavailable, giving CI independence to match repo independence. Workflows stay single-sourced and action dependencies are fetched from a mirror we control.
SCOPE: * In: runner deployment (docker-in-docker), labels matching the GitHub images we use, action-source configuration, caching, artifact storage, a proof that the gate-1 workflow passes on Forgejo, and a workflow-compatibility guide.
* Out: writing the gate workflows themselves (quality/ci-gate1 and later gates), and Playwright browser images (added when quality/playwright-matrix needs them, following this guide).
SPEC(first 1200): In `imagine-os/paperos-infra`:

* `ops/forgejo-runner/docker-compose.yml`: service `runner` using `code.forgejo.org/forgejo/runner:<current stable, pinned>` with a `docker:dind` sidecar, registered against `https://git.${PAPEROS_DOMAIN}` with a registration token minted by `paperos-admin`. Two runner instances (`runner-1`, `runner-2`) with `capacity: 2` each so four jobs run concurrently; a separate compose profile `heavy` for a future Playwright runner on a bigger host.
* `ops/forgejo-runner/config.yml`: labels `ubuntu-latest:docker://ghcr.io/catthehacker/ubuntu:act-22.04`, `ubuntu-22.04` alias, `node-22:docker://node:22-bookworm`; `container.network: host` disabled; `cache.enabled: true` with `cache.dir` on a named volume; `actions.url` left default but `DEFAULT_ACTIONS_URL` in Forgejo `app.ini` set to `https://code.forgejo.org` so `actions/checkout@v4` and friends resolve to the Forgejo mirror instead of [github.com](<http://github.com>).
* Workflow single-sourcing: workflows live only in `.github/workflows/*.yml`; Forgejo reads that directory natively. A compatibility test in this issue runs the current gate-1 workflow from quality/ci-gate1 (or a placeholder `ci-smoke.yml` that
DOD:
* Two runners show as online in Forgejo org settings (screenshot at 1280 attached).
* The smoke or gate-1 workflow passes on Forgejo and on GitHub from the same commit; both run URLs in the PR.
* Runs on Forgejo fetch `actions/checkout` from [code.forgejo.org](<http://code.forgejo.org>) (job log excerpt proves no [github.com](<http://github.com>) access).
* Cache hit demonstrated on a second run (`pnpm store` restored; timing before/after recorded).
* Artifact upload and download demonstrated.
* `check-workflow-portability.ts` has tests with one passing and one failing fixture.
* `ci-portability.md` merged and linked from the branch policy.
* Linear comment with both run URLs and the concurrency figure.
* Changelog entry under "Infra".
EDGE:
* Docker-in-docker needs privileged mode: document the host hardening (dedicated VM or firewall) and keep runners off the Forgejo host if RAM is under 8 GB.
* An action pinned to a GitHub-hosted repo not mirrored on [code.forgejo.org](<http://code.forgejo.org>): guide says vendor it under `.github/actions/` or pin a Forgejo mirror URL.
* Secrets differ per forge: use identical secret names on both; `check-workflow-portability.ts` warns on any secret referenced but missing from `ops/forge/secrets-manifest.yml`.
* Runner disk fills with images: nightly `docker system prune -af --filter until=72h` cron.
* Concurrency spike from twenty sessions: jobs queue; document expected wait and the `heavy` profile scale-out.
* `pull_request` events from forks: disabled on Forgejo (no forks allowed for agents) and documented.
DEPS: * forge/forgejo-deploy (Actions enabled in `app.ini`). Consumers: quality/ci-gate1, forge/mirror (cron fallback), forge/dr-drill.


## PAP-51 [P1 Build M prio2 Backlog] Script `forge bootstrap <repo>` to configure imagine-os repos with mirrors, secrets, labels and webhooks
key=forge/repo-bootstrap milestone=CI runs on both forges agent=* Builds: Forge (lead) with Ops Runner for live verification
blockedBy=['PAP-48', 'PAP-47'] blocks=[]
GOAL: Provide `forge bootstrap <repo>`, one idempotent command that turns a pre-provisioned, empty imagine-os repository into a fully wired PaperOS repo: Forgejo twin and mirrors, secrets, labels, webhooks, branch protection, templates and workflows, and Pages. The `paperos create` CLI (app-shell/create-cli) and the orchestrator call it rather than repeating the steps.
SCOPE: * In: the CLI package, its config files (labels, secrets manifest, webhook list), dry-run and check modes, tests against recorded API responses, and a runbook.
* Out: cloning template code into the repo (app-shell/create-cli does that after bootstrap), and creating Linear projects (pm-linear/configure-workspace owns the Linear side; this CLI only accepts a `--linear-project <id>` to write into the repo metadata).
SPEC(first 1200): Package `packages/forge-cli` in `imagine-os/paperos-template` (published later to the internal registry; for now run via `pnpm forge`). TypeScript, `citty` for commands, `octokit` for GitHub, a thin typed client for the Forgejo API (`packages/forge-cli/src/forgejo.ts`, generated from the Forgejo OpenAPI spec with `openapi-typescript`), `sops` invoked via child process for secrets.

Command `forge bootstrap <repo> [--dry-run] [--check] [--linear-project <id>] [--visibility private|public]` performs, in order, each step idempotent and logged as `[ok]`, `[changed]` or `[skip]`:

 1. Verify `imagine-os/<repo>` exists on GitHub; abort with exit 3 if not (repos are pre-provisioned; do not create).
 2. Create the Forgejo repo `imagine-os/<repo>` if missing with matching visibility.
 3. Configure mirrors both ways by calling the functions exported from `ops/forge/mirror-all.ts` (moved into this package as `mirror.ts`) and register in `repos.yml`.
 4. Secrets: read `ops/forge/secrets-manifest.yml` (names, which forge, source key in sops) and set repository/org Actions secrets on both forges; never print values.
 5. Labels: sync from `ops/forge/labels.yml` (Type, Surface and Phase groups mir
DOD:
* `forge bootstrap paperos-bootstrap-fixture` on a real empty repo completes with all ten steps `[ok]`/`[changed]`; second run is all `[ok]`/`[skip]` (both transcripts in PR).
* `--dry-run` performs zero write calls (asserted by msw).
* `--check` exits 1 after a label is manually altered, 0 after re-bootstrap.
* Unit coverage of each step above 80 per cent; typecheck clean.
* Runbook `docs/runbooks/repo-bootstrap.md` merged; `CLAUDE.md` mentions the command.
* Sentinel Security Auditor confirms secrets never appear in logs (test greps captured output).
* Linear comment with fixture repo links on both forges and the summary table.
* Changelog entry under "Tooling".
EDGE:
* Repo exists on Forgejo but not GitHub: exit 3 with guidance; GitHub remains the pre-provisioning source of truth.
* Partial failure at step 6: rerun resumes safely because every step is idempotent; no state file required.
* Rate limited by GitHub secondary limits during bulk bootstrap: exponential backoff with jitter, max 5 retries, then exit 4 listing remaining steps.
* Label exists with the same name but different colour: recolour, log `[changed]`.
* Pages cannot be enabled on a private repo under the current GitHub plan: log `[skip]` with reason; do not fail.
* Webhook secret rotated: `--rotate-webhook-secret` flag regenerates and updates the orchestrator config.
DEPS: * forge/mirror (mirror functions), forge/bot-accounts (tokens and deploy keys). Soft: forge/branch-policy, forge/pr-templates, app-shell/gh-pages-demo, pm-linear/webhooks. Consumer: app-shell/create-cli.


## PAP-52 [P1 Build M prio2 Backlog] Automate semantic release tags and changelog generation on merge to main
key=forge/release-tags milestone=CI runs on both forges agent=* Builds: Forge (lead), with Atlas's Merger sub-agent valida
blockedBy=['PAP-133', 'PAP-46'] blocks=[]
GOAL: Turn merges to `main` into versions automatically: Conventional Commits determine semver bumps per package and app, tags and GitHub/Forgejo releases are created, and structured release notes are emitted in a form the in-app changelog (collab/changelog) can render. No agent or human edits version numbers by hand.
SCOPE: * In: release automation configuration for the monorepo, a release workflow that runs on either forge, per-package CHANGELOG files, a machine-readable release feed, attachment of build artifacts, and documentation.
* Out: the in-app changelog UI (collab/changelog) and app store submission for Tauri builds (later app-shell work); this issue only attaches artifacts to releases.
SPEC(first 1200): In `imagine-os/paperos-template`:

* Tool: `release-please` in manifest mode (`release-please-config.json`, `.release-please-manifest.json`) with a package entry for `apps/web`, `apps/desktop`, `apps/mobile` and every `packages/*` directory, `release-type: node`, `include-component-in-tag: true`, `separate-pull-requests: false` so one release PR aggregates. Tag format `<component>-v<semver>` (for example `web-v0.4.0`, `ui-v0.2.1`). Tauri apps additionally get `extra-files` entries for `tauri.conf.json` version fields.
* Bump rules: `feat` -> minor, `fix`/`perf` -> patch, `feat!` or `BREAKING CHANGE:` footer -> major (pre-1.0 uses `bump-minor-pre-major: true`). Commit trailers `Linear: PAP-<n>` are parsed by a small `release-please` plugin (`scripts/release/linear-links.ts`) that appends `(PAP-<n>)` links to each changelog line.
* Workflow `.github/workflows/release.yml`: on push to `main`, run `release-please` to open or update the release PR; when that PR merges, create tags and releases. On Forgejo the same file runs with the `release-please` CLI against the Forgejo API through a compatibility shim (`scripts/release/forgejo-provider.ts`) because the official action targets GitHub
DOD:
* A `feat(ui):` commit merged to `main` results in a release PR; merging it creates `ui-v*` tag and release on both forges (URLs in PR).
* A `fix(web):` and a `feat!` commit produce patch and major bumps respectively in a test run on a fixture branch (screenshots of the release PR diff).
* `releases/feed.json` validates against `scripts/release/feed.schema.json` (Vitest test); Linear comments posted on referenced issues.
* Forgejo provider shim has unit tests with recorded responses; live run URL on Forgejo included.
* No manual version edits remain; `scripts/check-no-manual-version.ts` in gate 1 fails PRs that touch `version` fields outside release PRs.
* `docs/engineering/releases.md` merged, explaining bump rules and how to hotfix.
* Sentinel Code Reviewer approves; Quill (Changelog Scribe) reviews note readability.
* Changelog entry (self-referential, produced by the tool itself).
EDGE:
* Non-conventional commit slips through (hook bypassed): release-please ignores it; gate-1 commitlint from forge/branch-policy should already block; the docs note the recovery (`git commit --amend` on the branch).
* Two release PRs open at once due to a race on both forges: the workflow acquires a lock by checking for an open PR labelled `autorelease: pending` before creating.
* Tag exists on GitHub via mirror before Forgejo run: idempotent check skips creation and only uploads missing assets.
* Prerelease needed for a release candidate (quality/release-train): `prerelease: true` with `-rc.N` suffix supported via a `release-candidate` label on the release PR.
* Monorepo commit touching several packages: each affected component bumps; the commit appears in each CHANGELOG.
* Very first release with no prior tag: `bootstrap-sha` set in the manifest to the template's initial commit.
DEPS: * forge/branch-policy (Conventional Commits and trailers), collab/changelog (consumer contract for the feed; agree the JSON shape in that issue's comments before implementing). Soft: app-shell/tauri-desktop (artifacts), quality/release-train (RC labels).


## PAP-53 [P2 Review M prio2 Backlog] Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline
key=forge/dr-drill milestone=Disaster recovery proven agent=* Builds: Forge (Ops Runner sub-agent) executes; Sentinel's 
blockedBy=['PAP-50', 'PAP-47'] blocks=[]
GOAL: Prove, not assume, that PaperOS survives GitHub disappearing: rebuild the forge, every repository and a working CI pipeline on a fresh host from Forgejo backups while [github.com](<http://github.com>) is blocked, then record recovery time and data loss. The drill is scripted so it can be repeated monthly.
SCOPE: * In: a drill script, a throwaway Hetzner host provisioned and destroyed by the script, network isolation from GitHub, restoration of Forgejo and runners, verification that a PR passes gate 1 on the restored forge, a timed report, and fixes for any gap found.
* Out: application database recovery (data-layer/postgres-provision owns its own PITR drill) and restoring Linear (external SaaS).
SPEC(first 1200): In `imagine-os/paperos-infra`, `ops/forge/dr/`:

* `drill.sh` orchestrates: (1) `hcloud server create` a `cpx31`-class VM from a cloud-init that installs Docker; (2) adds `0.0.0.0 github.com api.github.com objects.githubusercontent.com ghcr.io` to `/etc/hosts` and an `nftables` drop rule for GitHub IP ranges fetched beforehand from `https://api.github.com/meta` so isolation is real; (3) installs `restic`, restores the latest snapshot from the `paperos-forgejo-backups` bucket (forge/forgejo-deploy) using the read-only restore credential; (4) brings up the Forgejo compose stack from the restored dump with a temporary domain `dr-git.${PAPEROS_DOMAIN}` (DNS record created via the Hetzner DNS API, TLS via Let's Encrypt staging to avoid rate limits); (5) starts one Forgejo runner from forge/actions-runner registered to the restored instance; (6) verifies every repo in `repos.yml` exists and that `git ls-remote` heads match the snapshot manifest; (7) pushes a `chore(dr): drill <date>` commit to a branch of `paperos-template`, opens a PR via the API and waits for the gate-1 workflow to pass; (8) records timestamps for each phase into `report.json`; (9) tears down the VM and DNS record unle
DOD:
* One full drill executed; `report.json` and the rendered markdown report committed.
* Isolation proven: the report includes `curl -sS https://api.github.com` failing from the drill host.
* All repos in `repos.yml` restored with matching heads; any mismatch explained.
* Gate-1 PR passed on the restored forge without GitHub access (run URL and screenshot).
* RTO and RPO figures reported; if a target is missed, a follow-up issue exists and is linked.
* Monthly cron configured and its first scheduled run date noted.
* Runbook `docs/runbooks/disaster-recovery.md` explains manual execution and what to do if the backup bucket itself is unavailable (secondary copy recommendation).
* Sentinel (Edge Case Hunter) reviews the report; Linear comment with the report link and headline numbers.
EDGE:
* Latest snapshot is corrupt: script falls back to the previous snapshot and records the extra RPO.
* Hetzner API quota or region capacity exhausted: retry in a second location; report the delay.
* Let's Encrypt staging certificates are untrusted by the runner's git: configure `GIT_SSL_CAINFO` with the staging root in the drill host only; never in production.
* Runner images cached from [ghcr.io](<http://ghcr.io>) are unavailable: the runner must pull from `code.forgejo.org` or a pre-pushed copy in the Forgejo container registry; document which images are pre-mirrored.
* Restored Forgejo still has webhooks pointing at production orchestrator: drill disables webhooks after restore to avoid triggering production actions.
* Someone pushes to production during the drill: manifests are compared against the snapshot time, not the live heads, to avoid false drift.
DEPS: * forge/mirror (repo list and manifests), forge/actions-runner (runner and action-source independence). Soft: forge/forgejo-deploy (backups), quality/ci-gate1 (workflow to run).


## PAP-54 [P2 Build L prio3 Backlog] Expose repo browsing, diffs and commit history inside PaperOS via the Forgejo API
key=forge/in-app-git milestone=Disaster recovery proven agent=* Builds: Forge (lead) for backend and client; Nova's Views 
blockedBy=['PAP-16', 'PAP-45'] blocks=[]
GOAL: Let developers and agents browse repositories, commit history, diffs and pull requests inside PaperOS, next to the specs and Linear issues those commits reference, using the Forgejo API as the backend. This is the first surface where code history becomes a first-class product object rather than an external tab.
SCOPE: * In: page specs and routes for repo list, file tree and file view, commit list and commit diff, PR list and PR detail; a server-side proxy to Forgejo with permission checks; syntax highlighting; links from commits to Linear issues and spec files; read-only.
* Out: editing files, merging PRs, code review comments (collab/comments may anchor to diffs later), and GitHub as a data source (Forgejo is the primary; mirrored content is identical).
SPEC(first 1200): In `imagine-os/paperos-template`:

* Specs: `specs/pages/dev/repos.spec.yaml`, `dev/repo.spec.yaml`, `dev/repo-file.spec.yaml`, `dev/repo-commits.spec.yaml`, `dev/repo-commit.spec.yaml`, `dev/repo-pulls.spec.yaml`, `dev/repo-pull.spec.yaml`, each with `access: { audiences: [developer, agent] }` in the format from spec-builder/access-section (if unmerged, use the draft shape and flag it).
* Routes (TanStack Router, apps/web): `/dev/repos`, `/dev/repos/$repo`, `/dev/repos/$repo/tree/$ref/$path`, `/dev/repos/$repo/commits/$ref`, `/dev/repos/$repo/commit/$sha`, `/dev/repos/$repo/pulls`, `/dev/repos/$repo/pulls/$n`. Layout slots from app-shell/router-layouts: sidebar = repo and branch picker, main = content, inspector = linked issue and spec panel.
* Backend: `packages/forge-client` wrapping the Forgejo API (reuse the generated client from forge/repo-bootstrap) and oRPC procedures in `apps/api/src/routes/forge.ts` (data-layer/api-layer): `repos.list`, `repos.tree`, `repos.file`, `repos.commits`, `repos.commit`, `pulls.list`, `pulls.get`. The server holds a read-only Forgejo token from forge/bot-accounts (`bot-scout` class scope); every procedure calls `can(actor, 'forge.read', { repo })
DOD:
* All seven pages render against the live Forgejo with real repos; Playwright screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark attached.
* Permission test: a customer-audience principal receives 403 on every `forge.*` procedure; a developer sees only repos they may read (Vitest integration tests).
* Commit with a `Linear:` trailer shows a working link; agent commits show the character avatar.
* Diff view handles binary files, renames and mode changes without crashing (fixture tests).
* Specs pass `spec validate` (spec-builder/validator); conformance tests generated.
* Lighthouse performance on `/dev/repos/$repo/commits/main` above 85 at 1280.
* Docs page `docs/product/in-app-git.md`; changelog entry under "Developer".
* Linear comment with the GitHub Pages demo link (mocked Forgejo data for the public demo) and screenshots.
EDGE:
* Repo with 50 000 files: tree loads one directory per request; breadcrumb navigation avoids full expansion.
* Ref name containing slashes (`release/2026-09-25`): route uses a splat and encodes the ref safely.
* Forgejo unreachable: pages show the design-system `EmptyState` with the last cached data and a retry, never a blank screen.
* Force-pushed branch invalidates cached commit list: cache key includes the ref's current SHA fetched cheaply first.
* Very wide diff lines (minified code): horizontal scroll within the diff, no page overflow at 320 width.
* Private repo becomes public: membership filter re-evaluates per request; no stale cache beyond 30 s.
DEPS: * forge/forgejo-deploy (data source), app-shell/router-layouts (routes and slots). Soft: identity/rbac-abac (`can`), data-layer/api-layer (oRPC), forge/bot-accounts (read token), design-system/data-display (avatars, empty states), spec-builder/validator.
