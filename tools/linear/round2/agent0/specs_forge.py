SPECS = {}

SPECS["PAP-44"] = dict(
Goal="""Record as an ADR why PaperOS keeps Git as its storage format, self-hosts Forgejo as the primary forge, mirrors to the GitHub org imagine-os and defers any custom VCS. It must be concrete enough that a future agent can tell whether the reopen conditions are met, and it is the reference every forge issue links to.""",
Scope="""In:

* `docs/decisions/ADR-0001-version-control-and-forge.md` in `imagine-os/paperos-template` (MADR 4), a comparison table, numerically testable reopen criteria, a one-paragraph summary for the project description.
* Index row in `docs/decisions/README.md`.

Out: implementation (PAP-45, PAP-47), CI runner and backup tool choices (their own issues).""",
Spec="""* Headings in order: Status (Accepted, 2026-09-17, deciders Atlas, Forge, Justin), Context, Decision, Alternatives Considered, Consequences, Reopen Criteria, Links.
* Alternatives table rows: GitHub only; GitLab CE; Gitea; Forgejo; Jujutsu on a Git backend; Pijul; from-scratch PaperOS VCS. Columns: agent tooling compatibility, self-host cost (RAM, disk, ops hours per week), migration effort in days, licence (Forgejo GPLv3+ since v9; GitLab CE MIT with proprietary EE), vendor-capture risk, 1-5 score using PAP-210's rubric or the six criteria inline.
* Decision: Git stays the format; Forgejo (pinned stable major) is primary; GitHub is mirror and public front door; Forgejo Actions is the CI fallback; custom VCS deferred.
* Consequences: at least five, including "every repo exists twice and drift is monitored" (PAP-47) and "agents authenticate with bot identities on both forges" (PAP-48).
* Reopen criteria, each measurable: for example monthly forge ops above 4 hours, Forgejo licence change, GitHub outage above 24 h in a quarter, a Git-format limitation blocking a spec-builder feature.""",
**{"Interface contract": """Provides:

* The ADR path and number that PAP-45, PAP-47, PAP-50, PAP-53 and the project description link to.
* Decision-log index format (`docs/decisions/README.md` table: number, title, status, date) that PAP-130 adopts.
* A `Reopen Criteria` block with a checklist that PAP-88's release digest can quote when a criterion trips.

Consumes: PAP-210 rubric if merged; otherwise the six criteria are stated inline with a TODO link."""},
**{"Definition of done": """* ADR at the path above passes `pnpm biome check` and renders on GitHub without broken tables.
* Seven alternatives, every column filled, no "TBD"; every cost figure has a source footnote.
* Reopen criteria all numeric.
* Index row added; PR uses the PAP-49 template or the interim one.
* Sentinel (Code Reviewer) approves; Quill reviews wording.
* Linear comment with the rendered ADR link and a three-line summary; changelog entry under Docs."""},
**{"Test plan": """* Static: `biome check` on Markdown; a small `scripts/adr-lint.ts` asserts the seven headings exist in order and the table has seven rows and six columns.
* Review: Sentinel verifies each source URL resolves; Quill checks the summary paragraph is under 120 words.
* Visual: GitHub render screenshot at 1280 showing the table intact."""},
Demo="""Reviewer opens the ADR on GitHub, scrolls the alternatives table, reads the five consequences and the reopen checklist, then opens `docs/decisions/README.md` to see the index row. Under a minute.""",
**{"Edge cases": """* Rubric not merged: six criteria inline plus TODO.
* ADR-0001 already taken by PAP-130: use the next number and update the index.
* Licence changes mid-build: record version and licence checked.
* Justin disagrees with deferring a custom VCS: Status becomes Proposed and the issue moves to Needs Justin with the table as the decision aid."""},
Dependencies="""None; ready now. Soft: PAP-210, PAP-130. Consumers: PAP-45, PAP-47, PAP-50, PAP-53.""",
Agent="""Drafted by Forge (lead) personally. Reviewed by Sentinel (Code Reviewer) and Quill.""",
Size="""S: one document with a sourced table.""",
)

SPECS["PAP-45"] = dict(
Goal="""Umbrella: stand up PaperOS's own forge, Forgejo in Docker on the PAP-25 host under Coolify, served over TLS by Caddy, with org `imagine-os`, nightly backups proven restorable and an OIDC login path from Better Auth ready to switch on. Three children; closes when the restore drill passes and every later forge issue has a live server.""",
Scope="""Children:

1. Forgejo compose stack behind Caddy with hardened `app.ini` (services, volumes, Coolify resource, TLS, admin and service accounts, org).
2. Backups and restore drill (`restic` sidecar to `paperos-backups/forgejo`, `restore.sh` into a scratch stack, timing).
3. OIDC auth source preparation and runbook (documented switch-on path, upgrade procedure, monitoring hooks).

Out: mirroring (PAP-47), runners (PAP-50), bots (PAP-48), using the application Postgres (Forgejo gets its own database container).""",
Spec="""* Repository `imagine-os/paperos-infra`, files under `ops/forgejo/`: `docker-compose.yml` with `forgejo` (`codeberg.org/forgejo/forgejo`, pinned digest), `forgejo-db` (`postgres:17-alpine`), `forgejo-backup`; volumes `forgejo-data`, `forgejo-db`; HTTP 3000 internal, SSH host port 2222.
* `app.ini.tmpl`: `ROOT_URL=https://git.${PAPEROS_DOMAIN}/`, `DISABLE_REGISTRATION=true`, `[actions] ENABLED=true`, `DEFAULT_ACTIONS_URL=https://code.forgejo.org`, `[lfs] enabled`, `[webhook] ALLOWED_HOST_LIST=private,${ORCHESTRATOR_HOST}`, `[mailer]` via Resend SMTP, `[oauth2_client] ENABLE_AUTO_REGISTRATION=true`, `[repository] DEFAULT_BRANCH=main`, `[security] INSTALL_LOCK=true`, `[packages] ENABLED=true` (container registry for PAP-26 and PAP-50).
* Coolify Docker Compose resource, domain `git.${PAPEROS_DOMAIN}`, health `GET /api/healthz` every 30 s.
* Accounts: admin `justin` (must change password), service `paperos-admin` with an API token in sops; org `imagine-os` with teams `owners`, `agents`, `reviewers` (filled by PAP-48).""",
**{"Interface contract": """Provides:

* URLs `https://git.PAPEROS_DOMAIN` (web and API `/api/v1`), SSH `ssh://git@git.PAPEROS_DOMAIN:2222`, container registry `git.PAPEROS_DOMAIN/imagine-os/<image>`.
* Secret `FORGEJO_ADMIN_TOKEN` in `ops/secrets/forge.enc.yaml` used by PAP-46 (`apply-branch-policy.ts`), PAP-47, PAP-48 until bot tokens exist.
* Org `imagine-os` and team names above.
* Backup repo `paperos-backups/forgejo` and `restore.sh <snapshot> <target-dir>` used by PAP-53 and the object-storage DR issue.
* Webhook allowlist including the orchestrator host (PAP-97).
* OIDC auth source name `paperos` expecting issuer `https://app.PAPEROS_DOMAIN/api/auth` (PAP-57 provides).

Consumes: host, Caddy proxy, `git.` DNS, sops keys, bucket, Resend SMTP (PAP-25)."""},
**{"Definition of done": """* All three children Done.
* Integration test: `git clone` over HTTPS with a deploy token and over SSH 2222 from a fresh machine; registration disabled; only `justin` and `paperos-admin` exist; `restore.sh` restores the latest snapshot into a scratch stack whose UI lists the same repos (timing recorded).
* Sentinel (Security Auditor) confirms no plaintext secret; runbook `docs/runbooks/forgejo.md`; Playwright screenshots of the landing page at 1280 and 375; Linear comment with URL, bucket and restore timing."""},
**{"Test plan": """* Unit: `app.ini.tmpl` render test with fixture env asserting every hardened key; compose file validated with `docker compose config`.
* Integration: `curl /api/healthz` 200 over TLS; `git clone` HTTPS and SSH from a CI job on a different network.
* Security: `POST /user/sign_up` returns 403; `gitleaks` on the infra repo.
* Backup: nightly cron produces a snapshot; `restore.sh` into `ops/forgejo/scratch` and compare repo lists via API.
* Visual: landing page at 1280 and 375."""},
Demo="""Reviewer opens `https://git.PAPEROS_DOMAIN`, sees the imagine-os org with the mirrored repos, runs `git clone https://git.PAPEROS_DOMAIN/imagine-os/paperos-template.git` with a token, then runs `restic snapshots` against the forge bucket. Under 2 minutes.""",
**{"Edge cases": """* Under 4 GB RAM: conservative cron settings; no runners on this host.
* Coolify default proxy is Traefik: switch to Caddy first.
* Let's Encrypt rate limits: staging CA during retries.
* Rotated storage credentials: backup fails loudly and posts to the orchestrator webhook.
* Major upgrade: pre-upgrade snapshot then `forgejo migrate` in the runbook.
* SSH 2222 blocked on some networks: HTTPS token auth is the primary agent path."""},
Dependencies="""PAP-25 (hard). Soft: PAP-57 SSO, PAP-40 metrics, PAP-44 rationale. Unblocks PAP-47, PAP-48, PAP-50, PAP-54.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).""",
Size="""L as an umbrella; children are M, S, S.""",
)

SPECS["PAP-46"] = dict(
Goal="""Define and enforce the conventions that let twenty Claude Code sessions commit in parallel without colliding: branch naming, one worktree per Linear issue, Conventional Commits with Linear trailers, and protection rules on `main` applied identically on Forgejo and GitHub. Output is a document and machine-applied configuration.""",
Scope="""In:

* `docs/engineering/branch-policy.md`; rulesets as JSON applied by `scripts/apply-branch-policy.ts` to both forges; `commitlint` and `lefthook` config; `scripts/worktree.sh`; CODEOWNERS per character plus generated `ownership.json`.

Out: the orchestrator (PAP-96) and scheduler (PAP-102); release tagging (PAP-52).""",
Spec="""* Branches `<character>/<PAP-n>-<kebab-slug>` (slug max 40); `release/<yyyy-mm-dd>`; `hotfix/<PAP-n>` only by Atlas with a Needs Justin comment; no direct pushes to `main`.
* Worktrees at `../paperos-worktrees/PAP-<n>` via `scripts/worktree.sh new|done PAP-<n>` (creates branch, copies `.env.example`, runs `pnpm install --offline` when possible, runs PAP-42 `stack up`).
* Conventional Commits 1.0 types `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`; scope = package or app; mandatory trailers `Linear: PAP-<n>` and `Character: <Name>`; optional `Sub-Agent:` and `Co-Authored-By`; enforced by `commitlint` via `lefthook` `commit-msg` and again in PAP-78.
* Rulesets: required PRs, required checks `ci / check`, linear history, signed commits preferred, bypass allowlist for the mirror token (PAP-47) and `bot-atlas` merges (PAP-48).
* CODEOWNERS mirrored to `.forgejo/CODEOWNERS`; `ownership.json` generated from it for PAP-102's file-lock hints; cross-owner PRs need both bot reviews or the `cross-owner` label from Atlas.""",
**{"Interface contract": """Provides:

* Commit-message grammar and trailer names consumed by PAP-52 (release notes links), PAP-133 (changelog), PAP-97 (PR status back to Linear), PAP-114 (session attribution).
* `ownership.json` schema `{ paths: [{ glob, owner: CharacterName }] }` consumed by PAP-102.
* `scripts/worktree.sh` CLI contract (exit codes 0, 2 refusal on dirty worktree) consumed by PAP-96 and PAP-93.
* Ruleset JSON files `ops/forge/rulesets/{github,forgejo}.json` reapplied by PAP-51 for each new repo.
* Required check name `ci / check` (PAP-13, PAP-78).

Consumes: `FORGEJO_ADMIN_TOKEN` (PAP-45) until bot tokens (PAP-48); roster names from plan.json (PAP-104)."""},
**{"Definition of done": """* Document merged and linked from the template README.
* `lefthook.yml` and `commitlint.config.ts` present; a commit without `Linear:` is rejected locally and in CI (test in `scripts/__tests__/commitlint.test.ts`).
* `worktree.sh new PAP-999` and `done` covered by a shell test.
* `apply-branch-policy.ts` applied to `paperos-template` on both forges; a direct push to `main` rejected on each (transcripts).
* CODEOWNERS and `ownership.json` round-trip test; Atlas confirms the ownership map; Linear comment with links; changelog entry under Engineering."""},
**{"Test plan": """* Unit: commitlint fixtures (valid, missing trailer, wrong type, long subject); `ownership.json` generation from CODEOWNERS and back.
* Shell: `bats` for `worktree.sh` new, done, refusal on uncommitted changes, long slug truncation.
* Integration: `apply-branch-policy.ts --dry-run` diff against live rulesets is empty after apply; direct push attempts to `main` on both forges rejected (transcripts).
* Parity: script prints which GitHub-only ruleset features could not be applied on Forgejo."""},
Demo="""Reviewer runs `scripts/worktree.sh new PAP-999`, commits a change without the `Linear:` trailer and watches lefthook reject it, fixes the message, then attempts `git push origin HEAD:main` and gets the protection error from both remotes. Under 2 minutes.""",
**{"Edge cases": """* Issue spanning two characters' paths: both reviews or `cross-owner`.
* Hotfix while `main` is red: Atlas-only branch with Needs Justin comment.
* Ruleset parity gaps degrade gracefully with a printed list.
* Human commit without lefthook: CI catches it with a clear message.
* Existing worktree with changes: script refuses and prints the path."""},
Dependencies="""None; ready now. Consumers: PAP-49, PAP-52, PAP-96, PAP-102, PAP-133, PAP-78.""",
Agent="""Built by Forge (lead). Reviewed by Sentinel (Code Reviewer); Atlas confirms ownership.""",
Size="""M: policy plus four scripts with tests.""",
)

SPECS["PAP-47"] = dict(
Goal="""Every imagine-os repository exists on Forgejo too, with commits pushed to either side arriving on the other within a minute, so either forge can be primary and agents never care which is up. Drift is detected automatically and never resolved by force-push.""",
Scope="""In:

* Forgejo to GitHub push mirrors; GitHub to Forgejo via a reusable workflow plus a Forgejo Actions cron fallback (PAP-50); `mirror-all.ts` configuring all repos; `mirror-check.ts` drift monitor; a documented conflict rule.

Out: creating repos for new apps (PAP-51), issue and PR metadata (Linear owns issues), wikis, Discussions, Projects.""",
Spec="""* `ops/forge/mirror-all.ts` (infra repo, `pnpm tsx`): lists `GET /orgs/imagine-os/repos`; per repo creates the Forgejo twin if missing (visibility copied), sets a push mirror to GitHub with a fine-grained PAT (contents read and write, org-scoped), `interval=10m`, `sync_on_commit=true`; records pairs in `ops/forge/repos.yml`. Idempotent; `--dry-run`; `--only <repo>`.
* `.github/workflows/mirror-to-forgejo.yml` on `push` to any branch or tag: `git push --mirror` excluding `refs/pull/*` using the PAP-48 mirror token (interim `paperos-admin`).
* Fallback: Forgejo Actions cron (PAP-50) fetches from GitHub every 10 minutes when the workflow has not run.
* Loop safety: mirror pushes carry a `paperos-mirror` marker commit message check; Forgejo push mirror ignores pushes whose only change came from GitHub within the last interval.
* `mirror-check.ts` hourly compares heads and tags; divergence opens a Linear issue via PAP-97 (interim: comment on this issue) and never force-pushes.""",
**{"Interface contract": """Provides:

* `ops/forge/repos.yml` schema `{ repos: [{ name, githubId, forgejoId, visibility, archived, lfs, mirror: { pushToGithub: boolean, lastSyncAt } }] }` consumed by PAP-51 (registration), PAP-53 (restore manifest), the template-upgrade issue.
* Exported functions `ensureForgejoRepo(name)`, `configurePushMirror(name)`, `checkDrift(name)` moved into `packages/forge-cli/src/mirror.ts` by PAP-51.
* Reusable workflow `imagine-os/paperos-infra/.github/workflows/mirror-to-forgejo.yml@main`.
* Secret names `FORGEJO_MIRROR_TOKEN`, `GITHUB_MIRROR_PAT` in `ops/forge/secrets-manifest.yml`.
* Bypass actor requirement registered in PAP-46 rulesets.

Consumes: Forgejo instance and admin token (PAP-45), bot token (PAP-48, soft), runner cron (PAP-50, soft), alert path (PAP-97, soft)."""},
**{"Definition of done": """* Every imagine-os repo on Forgejo with identical heads and tags (`mirror-check.ts` zero drift).
* Forgejo to GitHub and GitHub to Forgejo each within 60 s on a test repo (timings in PR).
* Divergence test produces a Linear issue, not a force-push.
* Second `mirror-all.ts` run makes zero writes (asserted on recorded HTTP calls).
* Secrets only in sops; Sentinel confirms minimal scopes; runbook merged; Linear comment with drift output and timings; changelog under Infra."""},
**{"Test plan": """* Unit: `mirror-all.ts` against `msw`-recorded GitHub and Forgejo responses: create, skip, rename by id, archived handling; `--dry-run` zero writes.
* Integration: push to Forgejo `main` on `mirror-fixture`, poll GitHub head until equal, record ms; reverse direction likewise.
* Divergence: force different commits on both sides; assert issue created and both heads unchanged.
* Monitor: expired PAT simulated with 401; distinct "credential expired" message.
* Portability: workflow runs unchanged on Forgejo Actions (PAP-50 check)."""},
Demo="""Reviewer pushes an empty commit to `mirror-fixture` on Forgejo and refreshes the GitHub commits page within a minute, then runs `pnpm tsx ops/forge/mirror-check.ts` and reads the zero-drift table. Under 2 minutes.""",
**{"Edge cases": """* Repos over 1 GB or with LFS: LFS flag on; initial sync may exceed a minute.
* Repo renamed on GitHub: detected by id, renamed on Forgejo.
* Archived repo: read-only mirror, push mirror disabled.
* Protected branch rejects mirror push: bypass allowlist in rulesets.
* Forgejo down during GitHub pushes: workflow retries; cron catches up."""},
Dependencies="""PAP-45 (hard). Soft: PAP-48, PAP-50, PAP-46, PAP-97. Unblocks PAP-22, PAP-51, PAP-53.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor on tokens; Edge Case Hunter runs divergence).""",
Size="""M: two propagation paths and a monitor with timing evidence.""",
)

SPECS["PAP-48"] = dict(
Goal="""Give every agent character a least-privilege identity on both forges so commits, PRs and API calls are attributable to Atlas, Forge, Iris and the rest rather than to Justin or a shared token. Access matches each character's `access` list exactly and rotation is one command. This sits on the P0 critical path to PAP-106.""",
Scope="""In:

* Forgejo bot accounts per lead character; one GitHub App with per-character commit identities; deploy keys for CI; scoped tokens; sops layout; rotation script; access matrix document; `.mailmap` and `allowed_signers`.

Out: MCP tool enforcement (PAP-106 consumes the tokens), human accounts, sub-character identities (sub-agents act under their lead with a `Sub-Agent:` trailer).""",
Spec="""* `ops/forge/bots.ts` creates `bot-atlas`, `bot-forge`, `bot-iris`, `bot-quill`, `bot-sentinel`, `bot-nova`, `bot-ledger`, `bot-beacon`, `bot-scout` with emails `<name>@agents.<domain>`, reading the roster file so new characters are added, never deleted without `--prune`.
* Teams: `agents` (write) for builders; `reviewers` (read plus PR review) for `bot-sentinel`; `owners` adds `bot-atlas` for merges; `bot-scout` read plus `docs/registry` via CODEOWNERS.
* Token scopes: builders `write:repository`, `write:issue`; Sentinel `read:repository`, `write:issue`; Atlas adds `write:organization`. Stored in `ops/secrets/bots.enc.yaml` (recipients Justin and orchestrator) and mirrored into Coolify for PAP-96.
* GitHub App `paperos-agents` on imagine-os: contents, pull requests, checks, metadata; installation token minted per session; commit author `"<Character> (PaperOS agent) <bot-<name>@agents.<domain>>"`; SSH signing keys per character with `allowed_signers`.
* `bots.ts audit` compares live state with `ops/forge/access-matrix.yml`; `bots.ts rotate <name>` completes in under 5 minutes.""",
**{"Interface contract": """Provides:

* Secret keys in `bots.enc.yaml`: `FORGEJO_TOKEN_<CHARACTER>`, `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_APP_INSTALLATION_ID`, `SIGNING_KEY_<CHARACTER>` consumed by PAP-96 (session env), PAP-106 (tool scopes), PAP-47 (mirror token `FORGEJO_TOKEN_MIRROR`), PAP-51 (bootstrap).
* `ops/forge/access-matrix.yml` schema `{ characters: [{ name, forgejoUser, teams[], scopes[], paths[] }] }` consumed by PAP-104 and PAP-106.
* Helper `mintGithubToken(character)` in `packages/forge-cli/src/github-app.ts`.
* Commit identity convention and `.mailmap` consumed by PAP-133, PAP-114.

Consumes: Forgejo org and admin token (PAP-45), roster (PAP-104; plan.json roster until then), sops recipients (PAP-25)."""},
**{"Definition of done": """* Nine bots exist; `bots.ts audit` prints the matrix and exits non-zero on deviation (test).
* GitHub App installed; a session mints a token and opens a PR attributed to the App with a character author.
* `bot-sentinel` push to `main` rejected; its review accepted (transcripts).
* Rotation run once end to end; old token verified revoked.
* `gitleaks` clean; `.mailmap` and `allowed_signers` committed; `git log --show-signature` prints Good signature; matrix doc merged; Linear comment; changelog under Infra."""},
**{"Test plan": """* Unit: `bots.ts` plan against recorded Forgejo responses (create, skip, prune-guard); matrix diff detection with a mutated fixture.
* Integration: mint an installation token in CI and call `GET /installation/repositories`; open and close a PR on a fixture repo with the character author.
* Permission: `bot-sentinel` push rejected, review accepted; `bot-scout` write outside `docs/registry` rejected by CODEOWNERS review requirement.
* Rotation: `rotate bot-forge` then old token returns 401 (log, timed).
* Security: `gitleaks` in Gate 1 for the infra repo."""},
Demo="""Reviewer runs `pnpm tsx ops/forge/bots.ts audit` and reads the nine-row matrix, opens the fixture PR on GitHub authored by "Forge (PaperOS agent)" with a verified signature badge, then checks Forgejo's `agents` team membership page. Under 90 seconds.""",
**{"Edge cases": """* Org blocks Apps: fine-grained PAT per character on a machine user, documented degraded mode.
* New character later: `bots.ts` creates it from the roster.
* Token in a prompt log: rotate under 5 minutes; purge via PAP-129 redaction.
* Bot rate-limited: per-bot limits documented; orchestrator backoff.
* Two sessions share a character: attribution stays per character; sessions distinguished by the `Linear:` trailer."""},
Dependencies="""PAP-45 (hard). Soft: PAP-104. Unblocks PAP-51, PAP-106, PAP-96; feeds PAP-47.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).""",
Size="""M: one script, one App, a matrix and a rotation proof.""",
)

SPECS["PAP-49"] = dict(
Goal="""Every PR opened by an agent or human carries the same structure: Linear issue, specs touched, summary, screenshot matrix, test plan, review-gate checklist, risk and rollback. Reviewer agents and Justin always know where to look, and a lint rejects PRs missing the essentials.""",
Scope="""In:

* Template files for both forges kept byte-identical by `scripts/sync-templates.ts`; generator `scripts/pr-body.ts --issue PAP-n`; CI check `pr-lint`; guidance in PAP-93.

Out: reviewer agents (PAP-81), screenshot capture (PAP-82); this reserves their sections.""",
Spec="""* `.github/PULL_REQUEST_TEMPLATE.md` and `.forgejo/PULL_REQUEST_TEMPLATE.md`; sections as level-2 headings with an HTML comment each: Linear (`Closes PAP-<n>` plus title); Specs (files or `No spec changes (infra/docs)`); Summary (three to six plain bullets); Screenshots (seven widths from PAP-14 by light and dark, or `Not applicable (no UI change)`); Test plan (commands and results); Review gates (checkboxes for Gate 1 static, Gate 2 correctness, security, spec conformance, Gate 3 visual, Gate 4 edge cases, ticked only by bots via the checks API); Risk and rollback; Interface changes (new: any change to a contract listed in an issue's Interface contract section).
* `pr-body.ts` fills Linear and Specs from the Linear API and `git diff --name-only`.
* `pr-lint` (GitHub Action and Forgejo workflow) fails on missing Linear key, missing required headings, or hand-ticked gate boxes.""",
**{"Interface contract": """Provides:

* Heading names and order as the parsing contract for PAP-81 (posts findings under Review gates), PAP-82 (fills Screenshots), PAP-89 (review report reads Summary and Test plan), PAP-97 (reads `Closes` lines), PAP-133 (reads Summary for changelog).
* Sentinel phrases `Not applicable (no UI change)` and `No spec changes (infra/docs)` accepted by lint.
* `scripts/pr-body.ts` CLI used by PAP-93 and PAP-96 when opening PRs.
* Check name `pr-lint` required by PAP-46 rulesets.

Consumes: commit and PR conventions (PAP-46), widths (PAP-14), bot author list (PAP-48, soft)."""},
**{"Definition of done": """* Both template files byte-identical (test).
* `pr-body.ts --issue PAP-5` produces a valid body with the issue title (output in PR).
* `pr-lint` fails a PR without a Linear key and passes a compliant one (two demo PRs linked).
* Template referenced from `docs/engineering/branch-policy.md` and `CLAUDE.md`.
* Sentinel approves; Quill reviews the comments; rendered screenshots on GitHub and Forgejo at 1280; Linear comment; changelog under Docs."""},
**{"Test plan": """* Unit: `sync-templates.ts` equality; `pr-body.ts` with a mocked Linear response and a fixture diff; lint parser fixtures (missing key, multiple `Closes`, hand-ticked gate, docs-only phrase).
* Integration: two demo PRs on the fixture repo, one failing and one passing `pr-lint` on both forges.
* Visual: rendered PR screenshots on GitHub and Forgejo at 1280 showing task lists render."""},
Demo="""Reviewer runs `pnpm tsx scripts/pr-body.ts --issue PAP-13 | head -40`, opens the passing demo PR on GitHub and the same PR mirrored on Forgejo, and compares the rendered checklists. Under a minute.""",
**{"Edge cases": """* Unknown issue key: exit 2 with a hint, no partial body.
* PR closing several issues: multiple `Closes` lines accepted.
* Docs-only PR: Screenshots replaced by the sentinel phrase.
* Forgejo task-list rendering verified by screenshot.
* Body over 65,536 characters: Test plan truncated with a CI link."""},
Dependencies="""PAP-46 (hard). Soft: PAP-14, PAP-48, PAP-93.""",
Agent="""Built by Quill (Changelog Scribe) for the template, Forge for scripts. Reviewed by Sentinel (Code Reviewer).""",
Size="""S: two templates, two small scripts.""",
)

SPECS["PAP-50"] = dict(
Goal="""Run Forgejo Actions runners on our own infrastructure so the same workflow files execute on Forgejo when GitHub is unavailable, giving CI independence to match repo independence. Linux only; macOS and Windows capacity is the separate forge non-Linux runner issue.""",
Scope="""In:

* Runner deployment (docker-in-docker), labels matching the GitHub images we use, action source pointed at `code.forgejo.org`, cache, artifacts, a proof that Gate 1 passes on Forgejo, `check-workflow-portability.ts`, and `docs/engineering/ci-portability.md`.

Out: writing the gate workflows (PAP-78 onward), Playwright browser images (added when PAP-82 needs them per the guide), non-Linux runners.""",
Spec="""* `ops/forgejo-runner/docker-compose.yml`: `runner-1`, `runner-2` on `code.forgejo.org/forgejo/runner` (pinned) with `docker:dind` sidecars, `capacity: 2` each (four concurrent jobs); profile `heavy` for a future Playwright runner on a bigger host. Registered against `git.${PAPEROS_DOMAIN}` with a token minted by `paperos-admin`.
* `config.yml` labels `ubuntu-latest:docker://ghcr.io/catthehacker/ubuntu:act-22.04`, `ubuntu-22.04` alias, `node-22:docker://node:22-bookworm`; `cache.enabled: true` on a named volume; `DEFAULT_ACTIONS_URL=https://code.forgejo.org` in `app.ini` (PAP-45).
* Workflows live only in `.github/workflows/`; Forgejo reads that directory natively.
* `check-workflow-portability.ts` flags GitHub-only actions not mirrored on `code.forgejo.org`, `github.*` context use without fallbacks, and secrets missing from `ops/forge/secrets-manifest.yml`.
* Nightly `docker system prune -af --filter until=72h`.""",
**{"Interface contract": """Provides:

* Runner labels `ubuntu-latest`, `ubuntu-22.04`, `node-22` usable in `runs-on` on both forges; concurrency figure (four jobs) documented for PAP-102 scheduling.
* Script `pnpm tsx scripts/check-workflow-portability.ts <workflow>` run in Gate 1 (PAP-78) and by PAP-51 during bootstrap.
* `ops/forge/secrets-manifest.yml` as the single list of CI secret names for both forges (PAP-51 sets them).
* Cron workflow `ops/forge/mirror-fallback.yml` fetching from GitHub every 10 minutes (PAP-47 fallback).
* Guide `ci-portability.md` linked from PAP-46.

Consumes: Actions enabled and `DEFAULT_ACTIONS_URL` (PAP-45), host capacity (PAP-25; runners on a second host if RAM is under 8 GB)."""},
**{"Definition of done": """* Two runners online in org settings (screenshot at 1280).
* Smoke or Gate 1 workflow passes on Forgejo and GitHub from the same commit (both URLs).
* Forgejo job log proves `actions/checkout` came from `code.forgejo.org`, no `github.com` access.
* Cache hit on second run with before and after timings; artifact upload and download shown.
* Portability script has passing and failing fixtures; guide merged; Linear comment with both run URLs and the concurrency figure; changelog under Infra."""},
**{"Test plan": """* Unit: portability checker fixtures (GitHub-only action, missing secret, `github.token` use).
* Integration: `ci-smoke.yml` (or PAP-78 Gate 1) runs on both forges; job log grep for `code.forgejo.org`; `pnpm store` cache restore timing recorded.
* Capacity: launch five jobs; assert four run concurrently and one queues (screenshot).
* Ops: prune cron verified by disk usage before and after."""},
Demo="""Reviewer opens the Forgejo Actions tab on `paperos-template`, watches the smoke workflow run on `runner-1`, opens the checkout step to see `code.forgejo.org` in the log, then compares with the same commit's GitHub run. Under 90 seconds.""",
**{"Edge cases": """* DinD needs privileged mode: dedicated VM or firewall documented; runners off the Forgejo host under 8 GB.
* Unmirrored action: vendor under `.github/actions/` or pin a Forgejo mirror URL.
* Secret names differ per forge: identical names enforced by the manifest.
* Twenty sessions spike: jobs queue; `heavy` profile scale-out documented.
* Fork `pull_request` events disabled on Forgejo."""},
Dependencies="""PAP-45 (hard). Consumers: PAP-78, PAP-47, PAP-53, the non-Linux runner issue.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).""",
Size="""M: compose, config, one checker script and proofs.""",
)

SPECS["PAP-51"] = dict(
Goal="""Provide `forge bootstrap <repo>`, one idempotent command that turns a pre-provisioned, empty imagine-os repository into a fully wired PaperOS repo: Forgejo twin and mirrors, secrets, labels, webhooks, branch protection, templates and workflows, Pages. `paperos create` (PAP-22) and the orchestrator call it instead of repeating the steps.""",
Scope="""In:

* `packages/forge-cli` (`citty`, `octokit`, generated Forgejo client via `openapi-typescript`, `sops` via child process); config files `labels.yml`, `secrets-manifest.yml`, `webhooks.yml`; `--dry-run` and `--check`; tests against recorded responses; runbook.

Out: cloning template code (PAP-22 does that after bootstrap), creating Linear projects (PAP-91; this accepts `--linear-project <id>` for repo metadata), publishing the package (template-upgrade issue).""",
Spec="""* `forge bootstrap <repo> [--dry-run] [--check] [--linear-project <id>] [--visibility private|public] [--rotate-webhook-secret]`; each step logs `[ok]`, `[changed]` or `[skip]`:
  1. verify `imagine-os/<repo>` exists on GitHub (exit 3 otherwise; never create);
  2. create the Forgejo twin if missing;
  3. mirrors both ways via `mirror.ts` (from PAP-47) and register in `repos.yml`;
  4. secrets from `secrets-manifest.yml` on both forges, values from sops, never printed;
  5. labels from `labels.yml` (Type, Surface, Phase mirroring Linear);
  6. webhooks from `webhooks.yml` to the orchestrator (PAP-97) with a generated secret;
  7. rulesets from PAP-46 on both forges;
  8. PR template, CODEOWNERS and `.github/workflows/mirror-to-forgejo.yml` committed if absent;
  9. Pages enabled on the `gh-pages` branch (PAP-15);
  10. `.paperos/repo.json` written with Linear project id, Forgejo id and bootstrap version.
* Exit codes 0, 3 missing repo, 4 rate limited after 5 retries with jitter.""",
**{"Interface contract": """Provides:

* Bin `forge` with `bootstrap`, later `upgrade-check` (template-upgrade issue); JSON output `--json` `{ repo, steps: [{ name, status, ms }] }` that PAP-22 relays into its own summary.
* Typed Forgejo client `packages/forge-cli/src/forgejo.ts` reused by PAP-54 (`packages/forge-client`) and PAP-53.
* `.paperos/repo.json` schema `{ linearProjectId, forgejoRepoId, githubRepoId, bootstrapVersion, modules?: string[] }` read by PAP-28 and PAP-96.
* Config schemas for `labels.yml`, `secrets-manifest.yml`, `webhooks.yml` (Zod).

Consumes: mirror functions and `repos.yml` (PAP-47), bot tokens and deploy keys (PAP-48), rulesets (PAP-46), PR template (PAP-49), Pages convention (PAP-15), webhook receiver URL and secret format (PAP-97)."""},
**{"Definition of done": """* `forge bootstrap paperos-bootstrap-fixture` completes all ten steps `[ok]`/`[changed]`; second run all `[ok]`/`[skip]` (transcripts).
* `--dry-run` performs zero writes (asserted by `msw`); `--check` exits 1 after a manual label edit, 0 after re-bootstrap.
* Unit coverage above 80 percent; typecheck clean; secrets never in logs (test greps captured output).
* `docs/runbooks/repo-bootstrap.md` merged; `CLAUDE.md` mentions the command; Linear comment with fixture links; changelog under Tooling."""},
**{"Test plan": """* Unit: every step against recorded GitHub and Forgejo responses in fresh, already-configured and drifted states; label recolour path; rate-limit retry with fake timers; log redaction grep.
* Integration nightly: real run on the fixture repo, second run idempotent, `--check` after a manual drift.
* Contract: `--json` output validated against schema; PAP-22 fixture consumes it.
* Security: Sentinel reviews token scopes used per step."""},
Demo="""Reviewer runs `pnpm forge bootstrap paperos-bootstrap-fixture --dry-run` to read the ten planned steps, then without `--dry-run`, and opens the fixture repo on both forges to see labels, the mirror and the webhook. Under 2 minutes.""",
**{"Edge cases": """* Repo on Forgejo but not GitHub: exit 3; GitHub is the provisioning source of truth.
* Partial failure at step 6: rerun resumes safely; no state file.
* Label with same name, different colour: recolour, `[changed]`.
* Pages unavailable on a private repo: `[skip]` with reason.
* Webhook secret rotated: flag regenerates and updates the orchestrator."""},
Dependencies="""PAP-47, PAP-48 (hard). Soft: PAP-46, PAP-49, PAP-15, PAP-97. Consumer: PAP-22, PAP-29, template-upgrade issue.""",
Agent="""Built by Forge (lead) with Ops Runner for live verification. Reviewed by Sentinel (Security Auditor).""",
Size="""M: ten idempotent steps with recorded-response tests.""",
)

SPECS["PAP-52"] = dict(
Goal="""Turn merges to `main` into versions automatically: Conventional Commits determine semver bumps per package and app, tags and releases are created on both forges, and structured release notes feed the in-app changelog (PAP-133). No one edits version numbers by hand. The feed JSON shape is agreed in PAP-133's comments before implementation begins.""",
Scope="""In:

* `release-please` manifest mode for the monorepo; a release workflow that runs on either forge; per-package CHANGELOGs; `releases/feed.json`; artifact attachment; docs.

Out: the in-app changelog UI (PAP-133), store submission for Tauri builds (signing issue).""",
Spec="""* `release-please-config.json` and `.release-please-manifest.json` with entries for `apps/web`, `apps/desktop`, `apps/mobile`, `apps/api`, `apps/worker`, every `packages/*`; `release-type: node`, `include-component-in-tag: true`, `separate-pull-requests: false`; tags `<component>-v<semver>` (`web-v0.4.0`); Tauri apps get `extra-files` for `tauri.conf.json`.
* Bumps: `feat` minor, `fix` and `perf` patch, `feat!` or `BREAKING CHANGE:` major; `bump-minor-pre-major: true`.
* Plugin `scripts/release/linear-links.ts` appends `(PAP-n)` links from trailers.
* `.github/workflows/release.yml`: on push to `main` open or update the release PR; on merge create tags and releases, upload artifacts, write `releases/feed.json`, comment on referenced Linear issues via PAP-97.
* Forgejo: same file runs the `release-please` CLI through `scripts/release/forgejo-provider.ts`.
* Lock: check for an open PR labelled `autorelease: pending` before creating.
* `scripts/check-no-manual-version.ts` in Gate 1 fails PRs editing `version` fields outside release PRs.
* `release-candidate` label produces `-rc.N` prereleases for PAP-88.""",
**{"Interface contract": """Provides:

* Tag format `<component>-v<semver>` consumed by PAP-26 (production deploys on `web-v*` and `api-v*`), PAP-19 (desktop artifacts on `desktop-v*`), the template-upgrade issue (`template-v*`).
* `releases/feed.json` validated by `scripts/release/feed.schema.json`: `{ releases: [{ component, version, tag, date, notes: [{ type, scope, subject, linear: 'PAP-n'|null, sha }], artifacts: [{ name, url, sha256 }] }] }` consumed by PAP-133.
* Gate 1 check `check-no-manual-version` (PAP-78).
* Label `release-candidate` and prerelease semantics for PAP-88.

Consumes: commit grammar and trailers (PAP-46), feed shape agreement (PAP-133), artifacts (PAP-19, soft), Linear comment path (PAP-97, soft)."""},
**{"Definition of done": """* A `feat(ui):` merge yields a release PR; merging it creates `ui-v*` tag and release on both forges (URLs).
* `fix(web):` and `feat!` produce patch and major bumps in a fixture-branch run (screenshots of the release PR diff).
* `feed.json` validates (Vitest); Linear comments posted on referenced issues.
* Forgejo provider shim unit-tested with recorded responses; live Forgejo run URL included.
* `check-no-manual-version` in Gate 1; `docs/engineering/releases.md` merged; Sentinel approves; Quill reviews note readability."""},
**{"Test plan": """* Unit: `linear-links` plugin on fixture commits; feed generator against schema; Forgejo provider against recorded API responses; manual-version checker with passing and failing diffs.
* Integration: fixture branch with `fix(web):`, `feat(ui):`, `feat!(api):` commits; run release-please in dry mode; assert bumps.
* E2E: merge the release PR on the fixture repo; assert tags and releases exist on both forges and `feed.json` updated.
* Race: two workflow runs; second detects the `autorelease: pending` PR and exits."""},
Demo="""Reviewer opens the latest release PR, reads the generated per-package CHANGELOG diff with `(PAP-n)` links, then opens `releases/feed.json` on `main` and the matching release page on Forgejo. Under 90 seconds.""",
**{"Edge cases": """* Non-conventional commit slipped through: ignored; recovery documented.
* Tag exists on GitHub via mirror before the Forgejo run: idempotent skip, upload missing assets only.
* Monorepo commit touching several packages: each component bumps.
* First release: `bootstrap-sha` in the manifest.
* Milestone note: PAP-133 lands 09-26, after this issue's 09-24 milestone; the feed shape is agreed in comments first so this issue is not blocked on PAP-133's UI."""},
Dependencies="""PAP-46 (hard), PAP-133 (feed shape agreement; implementation may proceed once the shape is commented). Soft: PAP-19, PAP-88, PAP-97.""",
Agent="""Built by Forge (lead) with Atlas (Merger) validating. Reviewed by Sentinel (Code Reviewer) and Quill (Changelog Scribe).""",
Size="""M: configuration, one plugin, one provider shim, one checker.""",
)

SPECS["PAP-53"] = dict(
Goal="""Prove, not assume, that PaperOS survives GitHub disappearing: rebuild the forge, every repository and a working CI pipeline on a fresh host from Forgejo backups while `github.com` is blocked, then record recovery time and data loss. The drill is scripted so it repeats monthly. Application data recovery is PAP-30's drill and the object-storage DR issue.""",
Scope="""In:

* `ops/forge/dr/drill.sh`, a throwaway Hetzner host created and destroyed by the script, real network isolation from GitHub, restoration of Forgejo and one runner, a gate-1 PR on the restored forge, a timed report, and follow-up issues for gaps.

Out: application database recovery (PAP-30), Linear restoration (external SaaS).""",
Spec="""* Phases: (1) `hcloud server create` `cpx31` from cloud-init with Docker; (2) `/etc/hosts` blackhole for `github.com`, `api.github.com`, `objects.githubusercontent.com`, `ghcr.io` plus `nftables` drop for GitHub ranges from `/meta`; (3) `restic restore` latest from `paperos-backups/forgejo` with the read-only credential; (4) Forgejo stack up on `dr-git.${PAPEROS_DOMAIN}` (Hetzner DNS API, Let's Encrypt staging); (5) one PAP-50 runner registered; (6) every repo in `repos.yml` present and `git ls-remote` heads match the snapshot manifest; (7) push `chore(dr): drill <date>` to a branch, open a PR via API, wait for Gate 1; (8) `report.json` timestamps per phase; (9) teardown unless `--keep`.
* Webhooks disabled after restore so production is never triggered.
* Monthly cron via Forgejo Actions on the production instance; report committed to the infra repo.""",
**{"Interface contract": """Provides:

* `ops/forge/dr/report.json` schema `{ startedAt, phases: [{ name, startedAt, endedAt, ok }], rtoMinutes, rpoMinutes, snapshotId, reposChecked, mismatches: [] }` rendered to `docs/runbooks/dr-reports/<date>.md` and quoted by PAP-88's digest.
* Runbook `docs/runbooks/disaster-recovery.md` including the "backup bucket unavailable" branch (secondary copy recommendation feeding the object-storage DR issue).
* Snapshot manifest format `manifest.json` `{ snapshotAt, repos: [{ name, heads: { [ref]: sha } }] }` written nightly by PAP-45's backup sidecar (this issue adds the manifest step).

Consumes: `repos.yml` (PAP-47), runner compose (PAP-50), backups and `restore.sh` (PAP-45), Gate 1 workflow (PAP-78), Hetzner token (PAP-25)."""},
**{"Definition of done": """* One full drill executed; `report.json` and the rendered report committed.
* Isolation proven: `curl https://api.github.com` fails from the drill host (in report).
* All repos restored with matching heads; mismatches explained.
* Gate 1 PR passed on the restored forge without GitHub access (run URL and screenshot).
* RTO and RPO reported; missed targets have linked follow-up issues; monthly cron configured with first run date; runbook merged; Sentinel (Edge Case Hunter) reviews; Linear comment with headline numbers."""},
**{"Test plan": """* Unit: `bats` for phase ordering and `--keep`; manifest comparison with a fixture containing one mismatch.
* Integration: the drill itself, run once for this issue and monthly after; assert isolation (`curl` failure), repo count, Gate 1 success.
* Failure: corrupt latest snapshot simulated by pointing at a bad id; script falls back to the previous snapshot and records the extra RPO.
* Cost: report includes Hetzner hours consumed; target under 2 EUR per drill."""},
Demo="""Reviewer opens the latest `dr-reports/<date>.md`, reads the phase table with minutes per phase and the RTO and RPO lines, then opens the linked Gate 1 run on `dr-git` (if kept) or its screenshot. Under a minute.""",
**{"Edge cases": """* Corrupt snapshot: previous snapshot, extra RPO recorded.
* Hetzner capacity exhausted: retry in a second location.
* Staging certificates untrusted by git: `GIT_SSL_CAINFO` on the drill host only.
* Runner images from `ghcr.io` unavailable: pre-mirrored on Forgejo's registry; list documented.
* Production pushes during the drill: compare against snapshot time, not live heads."""},
Dependencies="""PAP-47, PAP-50 (hard). Soft: PAP-45, PAP-78, PAP-25.""",
Agent="""Executed by Forge (Ops Runner); Sentinel (Edge Case Hunter) reviews the report.""",
Size="""M: one script and one real run with evidence.""",
)

SPECS["PAP-54"] = dict(
Goal="""Umbrella: let developers and agents browse repositories, commit history, diffs and pull requests inside PaperOS next to the specs and Linear issues those commits reference, read-only, with Forgejo as the backend. Three children. Deferral note from the audit: this is the lowest-priority forge issue and may slip past 10-01 without affecting any other project; children are ordered so the backend proxy lands first and stays useful on its own.""",
Scope="""Children:

1. Forge client, oRPC procedures and permission checks (`packages/forge-client`, `repos.list|tree|file|commits|commit`, `pulls.list|get`, `can(actor, 'forge.read', { repo })`, caching).
2. Repo, tree, file and commit-list pages (`/dev/repos`, `/dev/repos/$repo`, `tree/$ref/$path`, `commits/$ref`) with specs and layout slots.
3. Diff view, PR pages and Linear links (`commit/$sha`, `pulls`, `pulls/$n`, syntax highlighting, `Linear:` trailer links, character avatars, mocked data for the Pages demo).

Out: editing files, merging PRs, review comments (PAP-131 may anchor to diffs later), GitHub as a data source.""",
Spec="""* Specs under `specs/pages/dev/*.spec.yaml` with `access: { audiences: [developer, agent] }` (PAP-59 shape).
* Routes in TanStack Router; layout slots from PAP-16: sidebar repo and branch picker, main content, inspector linked issue and spec panel.
* Server token: read-only Forgejo token of the `bot-scout` class (PAP-48); cache keyed by ref SHA fetched cheaply first; 30 s max staleness for membership filtering.
* Diff rendering handles binary, rename and mode changes; `shiki` highlighting lazy-loaded per language.
* Public Pages demo uses a mocked Forgejo fixture so no token ships to the client.""",
**{"Interface contract": """Provides:

* oRPC `forge.repos.*` and `forge.pulls.*` with DTOs `RepoDto`, `TreeEntryDto`, `CommitDto = { sha, message, author: { name, character?: CharacterName }, linearKeys: string[], date }`, `DiffDto`, `PullDto`.
* Permission action `forge.read` registered with PAP-59.
* Component `CommitLink` and `DiffView` in `@paperos/ui` reusable by PAP-131 and PAP-89.
* `packages/forge-client` wrapping the generated client from PAP-51.

Consumes: Forgejo API (PAP-45), routes and slots (PAP-16), `can()` (PAP-59), oRPC host (PAP-35), token (PAP-48), `EmptyState` and avatars (PAP-71), validator (PAP-118)."""},
**{"Definition of done": """* All three children Done.
* Integration test: all seven pages render against live Forgejo; a customer principal gets 403 on every `forge.*` procedure; a commit with a `Linear:` trailer shows a working link; Lighthouse performance above 85 on the commits page at 1280.
* Screenshots at all seven widths in light and dark; `docs/product/in-app-git.md`; changelog under Developer; Linear comment with the Pages demo link."""},
**{"Test plan": """* Unit: DTO mappers from Forgejo payloads; trailer parser; diff parser fixtures for binary, rename, mode change, huge minified line.
* Permission: `callAs(customer)` forbidden on every procedure; developer sees only permitted repos.
* Integration: procedures against a Forgejo fixture container in CI compose.
* E2E: Playwright navigates the seven routes with mocked data at seven widths; ref with slashes; Forgejo-down state shows `EmptyState` with retry.
* Performance: Lighthouse on the commits page."""},
Demo="""Reviewer opens `/dev/repos/paperos-template/commits/main`, clicks a commit by "Forge (PaperOS agent)", reads the diff with highlighting, clicks the `PAP-n` link in the inspector to reach Linear, then opens the PR list. Under 90 seconds.""",
**{"Edge cases": """* 50,000-file repo: one directory per request.
* Ref names with slashes: splat route with safe encoding.
* Forgejo unreachable: cached data plus retry, never blank.
* Force-pushed branch: cache key includes current SHA.
* Wide diff lines: horizontal scroll inside the diff at 320."""},
Dependencies="""PAP-16, PAP-45 (hard). Soft: PAP-35, PAP-48, PAP-59, PAP-71, PAP-118. No downstream consumers; safe to defer.""",
Agent="""Built by Forge (lead) for backend and client; Nova's Views team advises on the diff grid. Reviewed by Sentinel.""",
Size="""L as an umbrella; children are M, M, M.""",
)
