# Round 4 digest: Version Control & Forge Independence (`forge`)

Benchmarks: GitHub (merge queue, push protection, Actions, Packages, attestations); GitLab (stacked MRs, protected tags, runner autoscaling); Forgejo / Gitea (Actions, packages, mirrors, indexer); Gerrit (submit queue); Graphite (stacked PRs); Renovate and Dependabot; Sigstore / SLSA.

Feature matrix: 45 rows, 26 covered, 8 partial, 11 gap. New issues: 18 (8 children of existing issues, 10 gap issues, 2 deferred to v0.2). Amendments to existing specs: 8. Cross-project suggestions: 3.

## Feature matrix

| Feature | Covered by | Status | Note |
|---|---|---|---|
| Decision record: Git format, Forgejo primary, GitHub mirror, custom VCS deferred | PAP-44 | covered |  |
| Forgejo deployment behind Caddy with hardened app.ini | PAP-45, PAP-273 | covered | Repo unit defaults and package retention missing (amendment). |
| Backups with restic and timed restore drill | PAP-274 | covered |  |
| OIDC SSO from Better Auth | PAP-275, PAP-226 | covered |  |
| Bidirectional push mirroring | PAP-47 | covered | Drift monitor split out (r4/forge/mirror-drift-monitor). |
| Scoped bot accounts on Forgejo | PAP-48 | covered | GitHub App half split out (r4/forge/github-app-identities). |
| Branch protection and rulesets on both forges | PAP-46 | covered | Protected tags missing (amendment). |
| Conventional commits, Linear and Character trailers, commitlint | PAP-46 | covered |  |
| Worktree per issue | PAP-46 | covered |  |
| Dependent branches and stacked PRs for the branch-start rule | PAP-46, PAP-96 | gap | The schedule depends on it; nothing creates, retargets or rebases dependent branches (r4/forge/dependent-branches). |
| PR template with Linear, specs, screenshots, gates | PAP-49 | covered | PR size lint and draft convention missing (amendment). |
| Merge automation and merge queue | PAP-88, PAP-96 | gap | Justin never reviews PRs, yet no issue merges them (r4/forge/merge-automation). |
| CODEOWNERS routing and cross-owner reviews | PAP-46 | covered |  |
| Forgejo Actions runners on Linux | PAP-50 | covered | Portability checker split out. |
| Runner image with Playwright browsers for Gates 3 and 4 | PAP-50 | gap | Forge independence stops at Gate 1 today (r4/forge/playwright-runner-image). |
| Non-Linux CI capacity: macOS and Windows | PAP-371 | covered |  |
| Runner autoscaling for the twenty-session peak | PAP-50 | gap | Deferred (r4/forge/runner-autoscaling). |
| Workflow portability checker | PAP-50 | partial | Child r4/forge/portability-checker. |
| Repo bootstrap: mirrors, secrets, labels, webhooks, rulesets | PAP-51 | covered | `--check` and nightly split out (r4/forge/bootstrap-check-mode). |
| Semantic release tags and changelog feed | PAP-52 | covered | Forgejo provider split out (r4/forge/release-forgejo-provider). |
| Signed tags, release assets, prereleases for release trains | PAP-52, PAP-358 | covered |  |
| Install and pin policy: release age, ignore-scripts, lockfile, digests | PAP-358 | partial | Child r4/forge/supply-chain-install-policy. |
| Provenance attestations and cosign signatures with verification | PAP-358 | partial | Child r4/forge/supply-chain-provenance. |
| Secret scanning in CI | PAP-80 | covered | quality |
| Secret push protection: pre-commit, pre-receive, GitHub push protection | PAP-80, PAP-46 | gap | CI catches secrets after they are in history on two forges (r4/forge/push-protection). |
| Git LFS on both forges and artefact retention policy | PAP-47, PAP-441 | gap | Critique: "LFS still assumed" (r4/forge/lfs-and-artifacts). |
| Container and npm registries on Forgejo with GitHub mirrors | PAP-273, PAP-26, PAP-430 | covered | Publishing owned by r4/app-shell/upgrade-package-registry; retention amendment on PAP-273. |
| Disaster recovery drill with GitHub offline | PAP-53 | covered | Cron and report split out; Gate 3 proof missing (amendment). |
| Vendored actions and base images for DR | PAP-53, PAP-50 | partial | Listed as an edge case only (PAP-50 amendment). |
| Throwaway repo cleanup, stale branch and worktree reaper | PAP-429, PAP-29, PAP-22 | gap | Four issues assume a cleanup command (r4/forge/repo-cleanup). |
| Code search across repos | PAP-138 | gap | Deferred (r4/forge/code-search). |
| In-app repo browsing, diffs and PRs | PAP-54, PAP-276, PAP-277, PAP-278 | covered | Deferred by schedule. |
| Webhooks to the orchestrator and PR status back to Linear | PAP-97, PAP-51 | covered | pm-linear |
| PR review and checks API parity in the forge contract | PAP-449, PAP-81 | partial | `ForgePort` lacks `pulls.review` and `checks.set` (amendment). |
| Forge observability: metrics, mirror lag, queue depth, backup age | PAP-40, PAP-275 | gap | r4/forge/forge-observability. |
| Git credential helper: no raw tokens in sessions | PAP-300, PAP-48 | gap | The broker exists on paper; git still needs an adapter (r4/forge/git-credential-helper). |
| Access matrix audit and token rotation | PAP-48 | covered |  |
| Forgejo upgrade procedure and runbook | PAP-275 | covered |  |
| Repository unit defaults: issues, wiki and projects off (Linear is the system of record) | PAP-273 | partial | Amendment. |
| Community health files: SECURITY.md, CODE_OF_CONDUCT, issue templates redirecting to Linear | PAP-51 | partial | Amendment. |
| Contract package, conformance suite, kernel wiring for forge | PAP-449, PAP-452, PAP-455 | covered | PAP-455 demo names a GitHub adapter nobody builds (amendment; r4/module-system/service-swap-drill). |
| Engineering metrics: cycle time, review latency, CI duration | — | gap | Cross-project suggestion to pm-linear. |
| Fork PR handling | PAP-15, PAP-50 | covered | Disabled by design. |
| API rate-limit budgets across twenty agents | PAP-48, PAP-99 | partial | Edge cases only; the App token budget line is added in r4/forge/github-app-identities. |
| Monthly forge ops hours and reopen criteria | PAP-44 | covered |  |

## New issues

| Key | Title | Parent | Type | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|---|
| `r4/forge/portability-checker` | `check-workflow-portability.ts`: GitHub-only action detection, `github.*` context fallbacks, secrets-manifest cross-check and the vendored-action allowlist for both forges | PAP-50 | Build P1 | S (2) | Sonnet 5 / medium | 2 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/mirror-drift-monitor` | Mirror drift monitor: hourly `mirror-check.ts` comparing heads and tags on both forges, divergence issue through PAP-97, credential-expiry detection and the loop-safety marker test | PAP-47 | Infra P0 | S (2) | Sonnet 5 / medium | 1 | Forgejo live and mirrored (2026-09-20) |  |
| `r4/forge/github-app-identities` | GitHub App `paperos-agents`: installation on imagine-os, `mintGithubToken(character)`, per-character commit identities, SSH signing keys, `.mailmap` and `allowed_signers` | PAP-48 | Infra P0 | M (3) | Opus 5 / high | 1 | Forgejo live and mirrored (2026-09-20) |  |
| `r4/forge/release-forgejo-provider` | release-please Forgejo provider shim: dual-forge tags and releases, asset upload, the `autorelease: pending` lock and recorded-response tests | PAP-52 | Build P1 | M (3) | Sonnet 5 / medium | 2 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/supply-chain-install-policy` | Install and pin policy: pnpm `minimum-release-age`, `ignore-scripts` allowlist, lockfile integrity lint, action and image digest pinning lint in Gate 1 | PAP-358 | Infra P1 | S (2) | Opus 5 / high | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/supply-chain-provenance` | Provenance and signatures: SLSA attestations and cosign signing for container images and Tauri artifacts on both forges, verified in the Coolify pre-deploy step and the desktop updater | PAP-358 | Infra P1 | M (3) | Opus 5 / high | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/dr-cron-and-report` | DR drill scheduling and reporting: monthly Forgejo Actions cron, `report.json` renderer into `docs/runbooks/dr-reports/`, RTO and RPO trend and automatic follow-up issue filing | PAP-53 | Build P2 | S (2) | Sonnet 5 / medium | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/bootstrap-check-mode` | `forge bootstrap --check` drift detection with per-step diff output and the nightly fixture-repo run publishing `[ok]/[changed]/[skip]` transcripts | PAP-51 | Build P1 | S (2) | Sonnet 5 / medium | 3 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/merge-automation` | Merge automation for agent pull requests: auto-merge when gates are green, GitHub merge queue, `forge merge` for Forgejo with rebase-and-retest, and the `merge-when-green` label contract | — | Build P1 | M (3) | Opus 5 / high | 1 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/dependent-branches` | Dependent-branch tooling for the branch-start rule: `worktree.sh new --base`, PR base tracking in `.paperos/branch.json`, auto-retarget and rebase when the base PR merges | — | Build P1 | M (3) | Opus 5 / high | 1 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/lfs-and-artifacts` | Git LFS on both forges with mirror support, large-file and repository-size lint, and the retention policy for screenshot, video and fixture artefacts | — | Infra P1 | S (2) | Sonnet 5 / medium | 2 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/push-protection` | Secret push protection: gitleaks pre-commit through lefthook, Forgejo pre-receive hook, GitHub push protection, and the leaked-secret revocation runbook | — | Infra P0 | S (2) | Opus 5 / high | 1 | Forgejo live and mirrored (2026-09-20) |  |
| `r4/forge/repo-cleanup` | `forge cleanup`: TTL-labelled throwaway repos (`gp-`, `drill-`, `slot-`, `cli-sandbox-`), stale branch and worktree reaper, protected list, nightly sweep on both forges and pool slot release | — | Build P1 | S (2) | Sonnet 5 / medium | 2 | CI runs on both forges (2026-09-24) |  |
| `r4/forge/playwright-runner-image` | Forgejo runner `heavy` profile with a Playwright browsers image so Gates 3 and 4 and the golden path run on Forgejo without GitHub | — | Infra P1 | S (2) | Sonnet 5 / medium | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/git-credential-helper` | `paperos-git-credential`: git credential helper and SSH configuration that fetch short-lived per-session tokens from the credential broker for both forges, with host-key pinning | — | Build P1 | S (2) | Opus 5 / high | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/forge-observability` | Forge observability: Forgejo and runner metrics in Grafana, mirror lag, runner queue depth, disk, backup age and hook health alerts | — | Infra P1 | S (2) | Sonnet 5 / medium | 2 | Disaster recovery proven (2026-09-30) |  |
| `r4/forge/code-search` | Enable Forgejo code indexing and expose `forge.search` in `ForgePort` for the in-app repo browser and agent sessions | — | Build P2 | S (2) | Sonnet 5 / medium | 4 | Disaster recovery proven (2026-09-30) | yes |
| `r4/forge/runner-autoscaling` | Ephemeral runner autoscaling: start docker runners on a second Hetzner host when the Forgejo job queue exceeds capacity and stop them when idle, with a cost cap | — | Infra P2 | M (3) | Sonnet 5 / medium | 4 | Disaster recovery proven (2026-09-30) | yes |

## Amendments to existing specs

* **PAP-449** (Spec): * `ForgePort` also exports `pulls.review(pr, { verdict, findings })` and `checks.set(sha, { name, status, summaryUrl })` so Gate 2 (PAP-81, PAP-243) and the merge automation (`r4/forge/merge-automation`) post verdicts and required checks through the contract on both forges instead of calling the GitHub and Forgejo APIs directly; the Forgejo adapter maps `checks.set` to commit statuses. `mirrorStatus` reads `mirror-status.json` from `r4/forge/mirror-drift-monitor`.
* **PAP-273** (Spec): * `[repository] DEFAULT_REPO_UNITS = repo.code,repo.releases,repo.actions,repo.packages` (issues, wiki, projects and pull-request discussions beyond review are disabled: Linear is the system of record). * `[packages]` retention: `LIMIT_TOTAL_OWNER_SIZE = 20 GiB`, a weekly `forgejo admin packages cleanup` cron keeping the last 20 versions per package (shared with `r4/app-shell/upgrade-package-registry`) and container images referenced by no Coolify resource for 30 days.
* **PAP-46** (Spec): * Tag protection: `*-v*` tags may be created only by the release workflow identity (`bot-forge` on Forgejo, the `paperos-agents` App on GitHub); humans and other bots are rejected; documented in `branch-policy.md`. * `worktree.sh new` accepts `--base <branch>[,<branch>]` (delivered by `r4/forge/dependent-branches`) and installs the session git config from `r4/forge/git-credential-helper` when the broker socket exists.
* **PAP-49** (Spec): * `pr-lint` also warns above 800 changed lines (excluding generated paths from `ownership.yaml` and lockfiles) and fails above 2,000 without the `large-change` label set by Atlas; draft PRs skip the Screenshots requirement until marked ready. * New section `Stacked on` (list of base PRs) written by `pr-body.ts` when `.paperos/branch.json` exists (`r4/forge/dependent-branches`).
* **PAP-50** (Spec): * Vendored inventory for DR: every third-party action and base image the workflows need is listed in `ops/forge/vendored-actions.yml` (`r4/forge/portability-checker`) with a mirror on `code.forgejo.org` or a copy under `.github/actions/`, and every runner and job image is mirrored into the Forgejo registry nightly by `ops/forge/mirror-images.yml`; PAP-53 asserts the list is complete by running with `ghcr.io` and `github.com` blackholed.
* **PAP-53** (Definition of done): * Phase 7 runs Gate 1 and, once `r4/forge/playwright-runner-image` exists, Gate 3 at three widths on the restored forge with `heavy` capacity requested from the drill host; the report records which gates ran. * Post-restore checks include `forge bootstrap --check` over `repos.yml` (`r4/forge/bootstrap-check-mode`), `git lfs fsck` on one repo (`r4/forge/lfs-and-artifacts`) and a `cosign verify` of the restored registry image (`r4/forge/supply-chain-provenance`).
* **PAP-455** (Demo): * Clarification: at merge time the second implementation is the `next` stub named in Scope; the `forgejo` to `github` flip described here becomes possible only when the read-only GitHub adapter from `r4/module-system/service-swap-drill` (deferred) is bound. Until then the demo flips `default` to `next` for the demo tenant and shows `X-PaperOS-Impl: next` on `forge.*` procedures.
* **PAP-51** (Spec): * Step 8 also commits the community health files when absent: `SECURITY.md` (disclosure address and the PAP-219 policy link), `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false` and a single contact link to the Linear intake (PAP-307), and `.github/dependabot.yml` disabled in favour of Renovate (PAP-217). * `--ttl <duration>` writes the `paperos-ttl` marker consumed by `r4/forge/repo-cleanup`.

## Cross-project suggestions

* **pm-linear**: Engineering metrics from forge webhooks: PR cycle time, review latency, CI duration and merge-queue wait per character and project, rendered as a dashboard block. DORA-style visibility for Atlas and the weekly re-audit (PAP-306); the data arrives through PAP-97 already.
* **quality**: Required-check name contract: one file `ops/ci/required-checks.json` listing the check names each gate posts, consumed by PAP-46 rulesets and r4/forge/merge-automation. Gate check names are scattered across PAP-78, PAP-81, PAP-82 and PAP-85; merging by check name needs one source of truth.
* **agents**: Session sandbox image installs `paperos-git-credential` and the pinned `known_hosts` by default, and runs `git` only through the helper (PAP-280). The credential helper (r4/forge/git-credential-helper) is only a guarantee if the sandbox cannot bypass it.

## What was missing and why it matters

* The merge step had no owner: the Blueprint promises Justin never reviews PRs and Atlas merges on green gates, but no issue merges anything; with twenty parallel PRs a merge queue on GitHub and a `forge merge` cron on Forgejo is the difference between a pipeline and a pile.
* The Execution Schedule only fits because of the branch-start rule, yet nothing creates worktrees on PR branches, tracks the base, retargets or rebases when the base merges; `r4/forge/dependent-branches` is the tooling the schedule silently assumed.
* Forge independence stopped at Gate 1: no Playwright runner image, no LFS decision, no code search and no observability meant the DR drill could prove a lint run but not a visual gate, and screenshots and videos had no home.
* Security controls that cost half a session each were missing: push protection at commit and pre-receive time, a git credential helper so sessions hold no raw tokens, and the GitHub App identity work that PAP-106 (P0) waits on was buried inside PAP-48.
* Housekeeping was assumed by four issues (golden path, drill, CLI sandbox, warm pool) and owned by none; `forge cleanup` with TTL markers, a protected list and slot release makes the nightly acceptance test safe to run.
