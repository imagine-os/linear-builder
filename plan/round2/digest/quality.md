# quality — Quality Pipeline
PHASE P0 prio 1 dependsOn ['app-shell']
SUMMARY: Four automated gates: static checks, three Claude reviewer agents, screenshot and video replay across the breakpoint matrix, and edge-case hunting; weekly release digests for Justin.
DESC: Goal: nothing reaches Justin unless machines have already reviewed it several ways. Gate 1 runs typecheck, Biome, Vitest and builds. Gate 2 runs three Claude reviewer agents (correctness, security, spec-conformance) against shared rubrics and posts structured reviews. Gate 3 captures Playwright screenshots and video replays of key flows across seven widths and all themes, diffs them against baselines and has a vision agent annotate layout defects. Gate 4 is an edge-case hunter that derives adversarial scenarios from page specs. Performance budgets, security scans and flake quarantine keep the pipeline trustworthy. A release train produces weekly candidates with a one-page digest into Needs Justin. Non-goal: manual QA as a routine step.
MILESTONES: ['Gates 1 and 2 on every PR 2026-09-20: Static checks, reviewer agents, rubrics, security scans, screenshot matrix', 'Visual and video gates 2026-09-25: Video replays, vision inspection, edge-case hunter, e2e flows, perf budgets', 'Edge-case hunting and release trains 2026-09-30: Release train, review digest, flake quarantine']


## PAP-78 [P0 Infra M prio1 Backlog] Set up CI gate 1: typecheck, Biome lint, Vitest unit tests and web build on every PR
key=quality/ci-gate1 milestone=Gates 1 and 2 on every PR agent=Built by Sentinel with Forge (Ops Runner) deploying the Turb
blockedBy=['PAP-13'] blocks=['PAP-217', 'PAP-122', 'PAP-87', 'PAP-82', 'PAP-81', 'PAP-80']
GOAL: Make Gate 1 the fast, deterministic check every pull request in every imagine-os repo passes before any agent or human looks at it: typecheck, Biome lint and format, Vitest unit tests, commit message lint and a production web build, finishing in under three minutes with clear, machine-readable results that Gate 2 can consume.
SCOPE: In:

* `.github/workflows/ci.yml` (readable natively by Forgejo Actions per `forge/actions-runner`) with jobs `setup` (pnpm cache, Turbo cache), `lint`, `typecheck`, `test`, `build`, `commitlint`, `generated-drift`, and an aggregating `gate-1` job that sets the commit status `gate/1-static`.
* Turborepo remote cache on the VPS (`ducktors/turborepo-remote-cache` in Docker via Coolify) keyed by team token stored as a secret; `--filter=...[origin/main]` so only affected packages run.
* Vitest with coverage (`@vitest/coverage-v8`), JUnit reporter to `reports/junit.xml`, and a coverage floor per package in `vitest.config.ts` (`lines: 70` initially).
* Drift checks: `tokens:build`, `registry:build`, `gen:breakpoints` outputs must be committed (`git diff --exit-code`).
* Required status checks configured through `forge/branch-policy`'s `apply-branch-policy.ts`.
* `pnpm check` local equivalent; 
SPEC(first 1200): * Runner: `ubuntu-24.04`; Node 22 from `.nvmrc`; pnpm via `corepack`; `actions/cache` for the pnpm store keyed on lockfile; Turbo cache via `TURBO_API`, `TURBO_TOKEN`, `TURBO_TEAM` env.
* Concurrency group `ci-${{ github.ref }}` with cancel-in-progress.
* `commitlint` job validates all commits in the PR range against `@commitlint/config-conventional` plus the `Linear:` and `Character:` trailer rule from `forge/branch-policy`; also validates the PR title.
* `test` runs `pnpm turbo test -- --reporter=default --reporter=junit --outputFile=reports/junit.xml`; failures annotated inline using `dorny/test-reporter`-style annotations or a small script parsing JUnit into `::error file=...` lines.
* `build` runs `pnpm turbo build --filter=web...` and uploads `apps/web/dist` as artifact `web-dist` for Gate 3 and the Pages preview to reuse, so the app is built once per PR.
* `gate-1` job runs `if: always()`, collects job outcomes, writes `gate1.json`, posts commit status via `actions/github-script`, and fails if any required job failed.
* Time budget enforced: a `timeout-minutes: 10` per job and a soft alarm when total exceeds 3 minutes (comment on PR, tracked in `quality/flake-quarantine` lat
DOD:
* Green run on a PR touching `packages/ui` completes in under 3 minutes with warm cache; cold cache under 6 minutes; both timings pasted in the PR.
* Seeded failures for each job (type error, lint error, failing test, bad commit message, drifted generated file) each produce an inline annotation and a red `gate/1-static` status; evidence linked.
* Remote cache hit rate visible in Turbo summary; cache server deployed and documented in `ops/README.md`.
* Same workflow file runs on the Forgejo runner (link to run).
* `gate1.json` artifact schema documented in `docs/quality/gates.md`; CHANGELOG entry.
* Linear comment with links to a green run, a red run and timings.
EDGE:
* Lockfile changed without `pnpm install` locally: `--frozen-lockfile` fails with a clear message.
* Merge commits in the PR range confuse commitlint: lint only non-merge commits, and also the squash title.
* Turbo remote cache unreachable: fall back to local cache, never fail the build; emit a warning.
* Tests that pass locally but fail in CI due to timezone: CI sets `TZ=UTC` and `LANG=en_US.UTF-8`; tests must set their own TZ when relevant.
* Flaky unit tests: allow `retry: 1` in Vitest CI config and report retried tests to the flake DB.
* PR with 200 commits: commitlint runs on the last 50 plus the title; documented.
DEPS: `app-shell/monorepo-scaffold` (hard: this issue extends the `ci.yml` it creates; starting in parallel would conflict on the same file). `data-layer/local-dev-stack` (soft: reusable service-container workflow for database-backed tests). `forge/branch-policy` (required checks, trailer rule). Consumed by `quality/security-scans`, `quality/review-agents`, `quality/playwright-matrix`, `quality/perf-budgets`, `spec-builder/conformance-tests`, `libraries/upgrade-bot`.


## PAP-79 [P0 Spec M prio1 Ready for Claude] Write review rubrics and a severity taxonomy shared by all reviewer agents and humans
key=quality/review-rubrics milestone=Gates 1 and 2 on every PR agent=Written by Sentinel with Quill editing for clarity. Reviewed
blockedBy=[] blocks=['PAP-81']
GOAL: Write the shared vocabulary for judging work: a severity taxonomy, per-domain review checklists and a structured finding format that the three reviewer agents, the vision inspector, the edge-case hunter and Justin all use, so a "blocker" means the same thing everywhere and findings can be counted, trended and turned into gate decisions automatically.
SCOPE: In:

* `docs/quality/rubrics/` with `severity.md`, `correctness.md`, `security.md`, `spec-conformance.md`, `visual.md`, `accessibility.md`, `performance.md`, `docs-and-changelog.md`, `agent-behaviour.md` (did the session follow the playbook), and `README.md` explaining how rubrics feed gates.
* Severity taxonomy: `S0 blocker` (data loss, security, broken build, spec violation of access rules), `S1 major` (user-visible bug, missing state, a11y serious), `S2 minor` (polish, naming, moderate a11y), `S3 nit` (style), plus `praise` and `question` non-severity kinds. Gate rule: any S0 blocks; more than 3 S1 blocks; S2/S3 never block.
* Finding schema `packages/agents/src/review/finding.schema.ts` (Zod) and JSON Schema export: `{ id, reviewer, rubricId, severity, title, body, file?, line?, endLine?, suggestion?, evidence: { kind: 'code'|'screenshot'|'video'|'log', ref }[], confidence: 0-1, auto
SPEC(first 1200): * Each rubric file: purpose, scope, checklist table (ID, check, typical severity, how to verify, false-positive notes), examples of S0/S1/S2 findings, and "what this rubric does not cover".
* Correctness checklist covers: types vs runtime, null and empty handling, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, resource cleanup, tests present and meaningful.
* Security checklist covers: authz on every procedure, RLS context set, input validation, secrets, SSRF, injection (SQL, HTML, shell), file upload, rate limits, dependency risk, logging of sensitive data.
* Spec-conformance checklist covers: page has a spec, components match `registry.json`, access section implemented, all declared states rendered (loading, empty, error, offline, no-permission), events wired, edge cases from spec have tests, guidelines `rules.json` respected.
* Visual checklist (for `quality/screenshot-annotation`): overflow, clipping, truncation without tooltip, misalignment to 4px grid, contrast, inconsistent spacing, touch target size, theme leaks.
* Finding IDs deterministic: `sha1(reviewer + rubricId + file + normalizedTitle)[:10]` so re-reviews dedupe.
* Confidence
DOD:
* Nine rubric docs plus README merged; every checklist item has an ID and verification note.
* `finding.schema.ts` with Vitest tests and exported JSON Schema at `docs/quality/rubrics/finding.schema.json`.
* Calibration set of 15 cases with expected severities and rationales; a script `pnpm rubrics:calibrate` prints agreement for a given reviewer output file.
* Rendering template tested with a fixture producing the expected Markdown snapshot.
* Reviewed and approved in comments by Iris (visual and a11y rubrics), Forge (correctness), Ledger (a note on financial correctness checks).
* CHANGELOG entry; Linear comment linking the README and schema.
EDGE:
* Finding spans generated files: severity capped at S2 and points to the generator source.
* Conflicting findings from two reviewers on the same line: both kept, highest severity governs the gate, dedupe only within a reviewer.
* Rubric item not applicable (e.g. no UI change): reviewers must emit `n/a` per rubric so silence is distinguishable from a skipped check.
* Severity inflation by agents: calibration agreement below 0.8 flags the reviewer prompt for tuning in `agents/eval-harness`.
* Justin overrides a severity: recorded as a `waiver` with reason and expiry on the finding, never a silent edit.
* Findings in third-party code under `node_modules` or vendored: `S3` with a pointer to `libraries/registry`.
DEPS: None blocking. Consumed by `quality/review-agents`, `quality/screenshot-annotation`, `quality/edge-case-hunter`, `quality/review-report`, `design-system/a11y-audit`, `design-system/guidelines-docs`, `forge/pr-templates`, `agents/eval-harness`.


## PAP-80 [P0 Infra M prio2 Backlog] Add dependency audit, secret scanning, Semgrep SAST and container scanning to CI
key=quality/security-scans milestone=Gates 1 and 2 on every PR agent=Built by Sentinel (Security Auditor sub-agent). Reviewed by 
blockedBy=['PAP-78'] blocks=[]
GOAL: Catch leaked secrets, vulnerable dependencies, dangerous code patterns and unsafe container images automatically on every PR and nightly on `main`, so the security reviewer agent starts from a clean baseline and Justin never receives a release with a known critical vulnerability.
SCOPE: In:

* Workflow `.github/workflows/security.yml` with jobs: `secrets` (gitleaks 8.x over the full PR diff and, nightly, full history), `deps` (`osv-scanner` against `pnpm-lock.yaml` and `Cargo.lock` for Tauri, plus `pnpm audit --prod` as a second opinion), `sast` (Semgrep CLI with `p/typescript`, `p/react`, `p/nodejs`, `p/owasp-top-ten`, `p/secrets` and a local ruleset `ops/security/semgrep/`), `containers` (Trivy on every image built from `ops/compose/`), `licenses` hook point for `libraries/license-policy`, and `gate-security` aggregating into commit status `gate/1-security`.
* Local rules in `ops/security/semgrep/`: oRPC procedure without `authorize` middleware, Drizzle query without tenant filter outside `withTenant`, `dangerouslySetInnerHTML` without `dompurify`, `eval`/`new Function`, Tauri `allowlist` widening, hard-coded imagine-os tokens.
* Suppression policy: inline `// nosemgr
SPEC(first 1200): * Severity mapping to `quality/review-rubrics`: gitleaks any hit = S0; OSV `CRITICAL`/`HIGH` with fix available = S0, without fix = S1 with waiver flow; Semgrep `ERROR` = S1 (S0 for the authz and tenant rules), `WARNING` = S2; Trivy `CRITICAL` = S0, `HIGH` = S1.
* All tools output SARIF; a merge script `ops/security/merge-sarif.ts` produces `reports/security.json` in the finding schema and a Markdown job summary; SARIF uploaded to GitHub code scanning when available and stored as artifact on Forgejo.
* Nightly job on `main` at 03:00 UTC also runs full-history gitleaks and opens or updates a Linear issue via `pm-linear/webhooks` when new S0/S1 findings appear, deduped by finding ID.
* Waiver file `ops/security/waivers.yaml`: `{ id, tool, reason, approvedBy: 'Justin'|'Sentinel', expires }`; expired waivers fail the job. Sentinel may approve S1 waivers; S0 waivers require Justin via Needs Justin.
* Trivy scans `postgres`, `forgejo`, `hocuspocus`, `minio`, `api` images defined in compose; `--ignore-unfixed` false, results per image.
* Runtime under 4 minutes; Semgrep runs on changed files for PRs and full repo nightly.
* Documentation `docs/quality/security-scans.md`: tools, versions, 
DOD:
* Workflow green on `main`; seeded test PR with a fake AWS key, a vulnerable `lodash@4.17.15`, a `dangerouslySetInnerHTML` misuse and an oRPC procedure without authorize produces four findings with correct severities and a red status (link).
* Waiver expiry test: an expired waiver fails the job.
* SBOM artifact present on a build; `reports/security.json` validates against the finding schema.
* Nightly run created a Linear issue in a dry-run mode (screenshot).
* Same workflow passes on the Forgejo runner; docs and CHANGELOG entry; Linear comment with run links.
EDGE:
* False-positive secrets in test fixtures: place under `**/__fixtures__/**` with a documented allowlist path pattern, never blanket ignores.
* Lockfile with git dependencies or workspace links: OSV skips them; the script lists skipped packages.
* Semgrep timeouts on generated files: exclude `**/generated/**`, `storybook-static`, `dist`.
* Tauri Rust deps without Cargo.lock in the repo yet: job skips with a notice until `app-shell/tauri-desktop` merges.
* Fork PRs without secrets: run everything that needs no token; skip SARIF upload with a comment.
* Vulnerability with no upstream fix for weeks: S1 waiver with expiry and a Linear issue, re-checked nightly.
DEPS: `quality/ci-gate1` (hard: shares setup and status pattern). Soft: `libraries/license-policy` (job slot), `pm-linear/webhooks` (issue creation), `forge/actions-runner`. Consumed by `quality/review-agents` (security reviewer reads `security.json`), `quality/release-train`, `libraries/upgrade-bot`.


## PAP-81 [P0 Build L prio1 Backlog] Build gate 2: three Claude reviewer agents (correctness, security, spec-conformance) posting structured PR reviews
key=quality/review-agents milestone=Gates 1 and 2 on every PR agent=Built by Sentinel (Code Reviewer and Security Auditor sub-ag
blockedBy=['PAP-79', 'PAP-78'] blocks=['PAP-88', 'PAP-85']
GOAL: Build Gate 2: three Claude reviewer agents (correctness, security, spec-conformance) that run on every PR after Gate 1 passes, review against the shared rubrics, post one structured GitHub or Forgejo review each with inline comments, and set commit statuses that block merge on blockers. This replaces the human code review Justin cannot supply.
SCOPE: In:

* `packages/agents/src/review/`: `runReview({ pr, reviewer })` using the Claude Agent SDK (TypeScript) with model `claude-fable-5-1`, tools limited to read-only repo access (`Read`, `Grep`, `Glob`, `Bash` allowlisted to `git diff`, `pnpm test --filter`, `pnpm typecheck`), plus the rubric and spec files.
* Three reviewer definitions in `.claude/agents/reviewers/{correctness,security,spec-conformance}.md` (Sentinel sub-characters) with system prompts embedding the relevant rubric, the finding schema and output rules.
* Inputs assembled per PR: diff, changed files with context, PR body (from `forge/pr-templates`), linked Linear issue text, relevant `page.spec.yaml` files, `gate1.json`, `security.json`, `registry.json`, guidelines `rules.json`.
* Output: findings validated against `finding.schema.ts`, deduped by ID, posted as a single review (event `REQUEST_CHANGES` if S0 or more than 3
SPEC(first 1200): * SDK usage: `query({ prompt, options: { model, systemPrompt, allowedTools, permissionMode: 'bypassPermissions', cwd: worktreePath, maxTurns: 40 } })`; final message must be JSON matching `{ findings: Finding[], rubricCoverage: { [rubricId]: 'checked'|'n/a' }, summary: string }`; parse failures retry once with the error appended.
* Diff over 3,000 changed lines: split by package and review in chunks; over 10,000 lines: post S1 "PR too large, split" and review only specs and security-critical paths.
* Context budget: cap included file content at 150k tokens by prioritising changed files, their tests, referenced specs; log what was omitted.
* Posting via `@octokit/rest` for GitHub and Forgejo's Gitea-compatible API for Forgejo; the same review is posted to whichever forge hosts the PR (primary per `forge/mirror`).
* Findings with `confidence < 0.5` become `question` comments; `autofixable: true` findings include a `suggestion` diff block.
* Idempotency: existing review comments carrying the finding ID in a hidden HTML comment are updated, not duplicated; resolved findings get a reply "Resolved in <sha>".
* Time budget: each reviewer under 6 minutes; total gate under 10 minutes; timeo
DOD:
* Three reviewers run on a real PR and post structured reviews with inline comments and statuses (links).
* Seeded PR with an authz bug, a null-handling bug and a missing empty state: each reviewer catches its case at S0/S1; a clean PR yields `COMMENT` with zero blockers.
* Calibration agreement at or above 0.8 for all three reviewers on the 15-case set.
* Re-push resolves fixed findings and does not duplicate comments (evidence screenshot).
* Cost per PR review reported in the summary and under $6 average across 10 PRs.
* `docs/quality/review-agents.md` (how to read, how to re-run, how to waive); CHANGELOG entry; Linear comment with example review links and cost table.
EDGE:
* PR body missing the Linear link: spec-conformance posts S1 and proceeds with the spec files it can infer from changed routes.
* Agent tries to write files or run network commands: tool allowlist denies; the attempt is logged as an S2 agent-behaviour finding.
* Rate limits or API outage: exponential backoff, then status `error` with a retry label, never green.
* Reviewer contradicts Gate 1 (claims tests fail when they pass): findings citing test results must include the command output as evidence or are downgraded.
* Binary or generated files in diff: skipped with a note; generated drift is Gate 1's job.
* Agent's own PR (Sentinel fixing rubrics): still reviewed; self-review is fine because the reviewer sessions are separate.
DEPS: `quality/ci-gate1` and `quality/review-rubrics` (hard). Soft: `forge/pr-templates`, `forge/bot-accounts` (posting identity), `quality/security-scans` (input), `spec-builder/validator`, `design-system/guidelines-docs` (`rules.json`), `collab/prompt-log-store`. Consumed by `quality/edge-case-hunter`, `quality/release-train`, `agents/eval-harness`.


## PAP-82 [P0 Build L prio1 Backlog] Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs
key=quality/playwright-matrix milestone=Gates 1 and 2 on every PR agent=Built by Sentinel (Visual Inspector sub-agent) with Iris con
blockedBy=['PAP-14', 'PAP-78'] blocks=['PAP-88', 'PAP-84', 'PAP-83']
GOAL: Build Gate 3's screenshot suite: Playwright renders every key page and every Storybook story across the seven-width breakpoint matrix and the three themes, compares against committed baselines, and fails the PR on unexpected visual change while making intended changes a one-command baseline update. These images are also the input for the vision agent.
SCOPE: In:

* `apps/web/e2e/visual/` Playwright 1.5x project set generated from `ops/ci/breakpoints.json`: projects `xs-320, sm-375, md-768, lg-1024, xl-1280, 2xl-1536, 3xl-1920` each with viewport, `deviceScaleFactor`, `hasTouch`, `isMobile` from the device matrix mapping; theme handled via `data-theme` set in a fixture, giving 21 combinations.
* Page list `apps/web/e2e/visual/pages.ts` derived from route files with `staticData.spec` plus `specs/pages/*.spec.yaml` `screenshot: true` flag; Storybook stories from `storybook-static/index.json` filtered by tag `visual`.
* Deterministic rendering: fixed clock (`page.clock.setFixedTime`), seeded data via a `/__test/seed` endpoint or MSW, `animations: 'disabled'`, fonts preloaded, `caret: 'hide'`, `reducedMotion: 'reduce'`, masked dynamic regions via `data-testid="volatile"`.
* Baselines committed under `apps/web/e2e/visual/__screenshots__/<project>/
SPEC(first 1200): * Runs against the `web-dist` artifact from Gate 1 served by `vite preview` and `storybook-static`; no rebuild.
* Playwright config `apps/web/playwright.visual.config.ts`: `fullyParallel`, `workers: 4` in CI, `retries: 1`, reporter `html` + `json` + custom `contact-sheet` reporter (`sharp` composing a grid PNG per page across widths).
* Screenshot ID grammar: `page:<routeId>` or `story:<storyId>`; file names sanitised; total budget under 600 images initially, enforced by a count check so the suite stays under 8 minutes with sharding (`--shard=i/4` across 4 runners).
* Full-page screenshots for pages (`fullPage: true`, capped at 4000px height) and element screenshots for stories (`#storybook-root`).
* Volatile masking: elements with `data-volatile` masked in `--pos-color-accent-500` so masks are visible in diffs.
* `pnpm shots` (local run), `pnpm shots:update` (regenerate), `pnpm shots:report` (open report); Docker image `mcr.microsoft.com/playwright:v1.5x-noble` pinned so local and CI fonts match; local runs outside Docker are informational only.
* Diff artifact JSON `reports/visual.json`: `[{ id, project, theme, status: 'pass'|'diff'|'new'|'missing', diffRatio, paths }]` consumed 
DOD:
* Suite runs on a PR across 4 shards in under 8 minutes and posts the sticky comment with contact sheets (link).
* Seeded 2px padding change fails the gate with a visible diff; `update-baselines` label workflow commits new baselines and turns the gate green (links to both runs).
* Flake check: 10 consecutive runs on `main` with zero diffs.
* Baselines exist for all example routes and all `visual` stories at 21 combinations; LFS configured and documented.
* `docs/quality/visual-testing.md` explains adding pages, masking, updating; CHANGELOG entry.
* Linear comment with report link and contact sheet images.
EDGE:
* Font rendering differences between local and CI: enforce the Docker image; report shows an "environment mismatch" warning if run outside it.
* Lazy-loaded images and skeletons: wait for `networkidle` plus `document.fonts.ready` and a `data-ready` attribute set by the app when initial data is loaded.
* Pages requiring auth: fixture logs in with a seeded test user per audience (`identity/*`), storage state cached per shard.
* Extremely tall pages: capped height with a note; full content covered by scrolling screenshots only for pages flagged `screenshot: fullScroll`.
* Baseline update PR conflicts with another baseline PR: LFS binary conflict resolved by re-running the update workflow after rebase (documented).
* Storybook story ids renamed: old baseline marked `missing`, requires explicit deletion so orphaned images do not accumulate.
DEPS: `quality/ci-gate1` (artifact reuse) and `app-shell/device-matrix-research` (`breakpoints.json`) hard. Soft: `design-system/storybook` (story source), `app-shell/gh-pages-demo` (report hosting), `forge/bot-accounts` (baseline commits), `design-system/theming` (theme attribute). Consumed by `quality/video-replays`, `quality/screenshot-annotation`, `quality/release-train`.


## PAP-83 [P1 Build M prio2 Backlog] Record video replays of critical flows per PR at each responsive size and attach them to the PR
key=quality/video-replays milestone=Visual and video gates agent=Built by Sentinel (Visual Inspector). Reviewed by Forge (sto
blockedBy=['PAP-82'] blocks=['PAP-137']
GOAL: Record short video replays of the critical user flows on every PR at each responsive width, with a step overlay and a contact sheet, and attach them to the PR and the Linear issue so reviewer agents, the vision inspector and Justin can watch a change instead of reading it.
SCOPE: In:

* Flow definitions in `specs/flows/*.flow.yaml`: `{ id, title, audience, critical: true, steps: [{ action: goto|click|fill|press|expect|wait, target (testid or role), value?, note }] }`; starter flows: sign-in, create workspace, switch tenant, create and edit a record, open inspector and detach panel (desktop only), theme switch.
* Runner `apps/web/e2e/flows/` in Playwright with `recordVideo` per test, one test per flow per width from `breakpoints.json` (default subset `sm-375, md-768, xl-1280, 3xl-1920`; full 7 on `main` nightly), light theme by default and dark on `main`.
* Post-processing `ops/ci/video/`: ffmpeg (pinned in the Playwright Docker image) converts WebM to MP4 (H.264, 720p max height, CRF 28), burns a step caption from step notes with timestamps, generates a poster frame and a 3x4 contact sheet PNG, and writes `reports/videos.json` `[{ flowId, width, theme, mp4, poste
SPEC(first 1200): * Flow YAML validated by Zod schema `packages/spec/src/flows.ts`; `target` resolves via `getByTestId` or `getByRole(name)`; `expect` supports `visible`, `text`, `url`.
* Fixture seeds the same deterministic data as `quality/playwright-matrix` and logs in per `audience`.
* Video size `{ width, height: 900 }` per project; `slowMo: 150` for legibility; a translucent overlay component `data-testid="flow-caption"` injected via `page.addInitScript` shows the current step note bottom-left.
* Contact sheet: 12 frames sampled at step boundaries (or evenly if fewer steps) labelled with step index.
* Total budget: 6 flows x 4 widths under 6 minutes across 2 shards; per-flow timeout 90s.
* `pnpm flows` runs locally with `--headed` option; `pnpm flows:record <flowId>` writes MP4s to `tmp/videos/`.
* Retention: PR videos 30 days; `main` nightly videos of critical flows kept 180 days for the release digest.
DOD:
* Six flows recorded at four widths on a PR; sticky comment shows posters and links; Linear comment posted (links).
* Nightly `main` run covers all seven widths and both themes; report JSON validates.
* A seeded broken flow (button renamed) fails `gate/3-video` and the MP4 shows the failing step (link).
* Videos play in Chrome, Safari and Firefox; MP4 under 4 MB each on average.
* `docs/quality/flows.md` documents writing a flow; CHANGELOG entry; Linear comment with a sample video and contact sheet.
EDGE:
* Flow step target ambiguous (multiple matches): fail fast with the candidates listed; never pick the first.
* Width where a step target is inside a collapsed drawer: flows may declare `at: { sm: [extra steps] }` overrides to open the drawer first.
* ffmpeg missing locally: fall back to WebM with a warning; CI always has it.
* MinIO unavailable: keep run artifacts, comment includes artifact link instead of signed URLs.
* Very long flow (over 60s): split into two flows; the schema caps steps at 40.
* Signed URL expiry in Linear comments: comment notes the expiry date; release digest re-signs when built.
DEPS: `quality/playwright-matrix` (hard: fixtures, projects, image). Soft: `data-layer/file-storage` or MinIO from `data-layer/postgres-provision` compose, `pm-linear/webhooks` (Linear comments), `identity/*` for real auth flows (use seeded test users). Consumed by `quality/screenshot-annotation` (contact sheets), `quality/review-report`, `collab/screenshot-annotations`, `design-system/motion` (motion evidence).


## PAP-84 [P1 Build M prio1 Backlog] Have a vision agent inspect screenshots for overflow, misalignment, contrast and truncation and post annotated findings
key=quality/screenshot-annotation milestone=Visual and video gates agent=Built by Sentinel (Visual Inspector sub-agent). Reviewed by 
blockedBy=['PAP-82'] blocks=[]
GOAL: Turn Gate 3's pixels into review findings: a vision-capable Claude agent inspects new and changed screenshots and video contact sheets for overflow, clipping, misalignment, truncation, contrast and theme leaks, draws annotated boxes on the images, and posts findings in the shared rubric format so layout defects block or get fixed without a human looking.
SCOPE: In:

* `packages/agents/src/vision/inspectScreenshots({ reportPath })` reading `reports/visual.json` and `reports/videos.json`, selecting images with status `diff` or `new` (all images on `main` nightly), and sending each with its context (page or story id, width, theme, the page spec's layout and components sections, guidelines `rules.json` items marked `vision`) to `claude-fable-5-1` with image input.
* Structured output per image: `{ findings: [{ rubricId, severity, title, body, bbox: { x, y, w, h } (normalised 0-1), confidence }], layoutScore: 0-100 }` validated by Zod; findings mapped into `finding.schema.ts` with `evidence: [{ kind: 'screenshot', ref }]`.
* Annotation renderer using `sharp` 0.33: draws boxes and numbered labels in the accent colour, writes `<id>.annotated.png` next to the original; a composite "findings sheet" per PR.
* Cross-width consistency check: the agent rece
SPEC(first 1200): * Prompt in `.claude/agents/reviewers/visual-inspector.md`: role, rubric `visual.md` checklist with IDs, instructions to report only defects visible in the image, to use bounding boxes in normalised coordinates, to compare against the spec's declared components and states, and to output JSON only.
* Contrast check is computed, not guessed: for each finding of type contrast the tool samples the bbox region with `sharp` and computes the ratio; findings below 3:1 keep severity, otherwise downgraded to `question`.
* Text truncation heuristics assisted by DOM: the visual suite also emits `reports/dom-metrics.json` per screenshot (`elements with scrollWidth > clientWidth`, `text-overflow: ellipsis` hits, elements outside viewport) so the agent can cross-check; DOM-confirmed findings get `confidence 0.9`.
* Deterministic IDs per rubric schema so re-runs update comments.
* Calibration set `docs/quality/rubrics/calibration/visual/` with 20 screenshots (10 defective with known bboxes, 10 clean); `pnpm vision:calibrate` reports precision and recall; target precision 0.85, recall 0.7.
* Output artifacts: `reports/vision.json`, annotated images, findings sheet uploaded alongside visual report t
DOD:
* Runs on a PR with visual diffs and posts annotated findings with boxes landing on the real defects (screenshot of the comment).
* Calibration precision at or above 0.85 and recall at or above 0.7 on the 20-image set, numbers in the PR.
* Seeded overflow at 375px and a low-contrast badge in dark theme are caught at S1 and S1 respectively; a clean PR produces zero blockers.
* Cost per PR under $4 across 10 runs; token and image counts in the job summary.
* `docs/quality/vision-inspection.md`; CHANGELOG entry; Linear comment with example annotated images.
EDGE:
* Masked volatile regions: agent told masks are intentional (coloured rectangles), never a finding.
* Intentional truncation with tooltip: DOM metrics include `title` presence so the finding downgrades to S3.
* Extremely tall full-page screenshots: split into 1568px tiles with overlap; bboxes remapped to page coordinates.
* Same defect at all seven widths: dedupe into one finding listing widths.
* Model hallucinated bbox outside the image: clamp and mark `confidence 0.3` (posted as question).
* Vision API unavailable: gate reports `error` and the review report lists inspection as missing; never silently green.
DEPS: `quality/playwright-matrix` (hard). Soft: `quality/video-replays` (contact sheets), `quality/review-rubrics` (`visual.md`, schema), `design-system/guidelines-docs` (`rules.json`), `spec-builder/schema` (layout sections). Consumed by `quality/release-train`, `quality/review-report`, `collab/screenshot-annotations`, `identity/customer-portal-shell` (DoD).


## PAP-85 [P1 Build L prio1 Backlog] Build gate 4: edge-case hunter agent generating adversarial inputs, empty/huge/unicode states, network failure and slow-device scenarios from page specs
key=quality/edge-case-hunter milestone=Visual and video gates agent=Built by Sentinel (Edge Case Hunter sub-agent). Reviewed by 
blockedBy=['PAP-81', 'PAP-114'] blocks=[]
GOAL: Build Gate 4: an agent that reads each changed page's spec and derives adversarial scenarios (empty, huge, unicode and RTL data, invalid input, network failure, slow device, permission denied, concurrent edits) then executes them with Playwright, files structured findings, and hands failing scenarios back as reproducible tests so happy-path coverage stops being the ceiling.
SCOPE: In:

* `packages/agents/src/edgecases/`: `planScenarios(spec, diff)` (Claude generates a scenario matrix from the page spec's data, logic, states, access and edge-cases sections plus the rubric's edge-case checklist), `runScenarios(plan)` (Playwright executor with fixtures for each scenario class), `report()` (findings in the shared schema).
* Scenario classes and fixtures: `data.empty`, `data.huge` (10k rows, 50k-char strings), `data.unicode` (emoji, combining marks, RTL Arabic and Hebrew, CJK, zero-width), `input.invalid` (types, bounds, injection strings), `network.offline|slow3g|flaky` (Playwright `route` with delays and aborts), `device.slowCpu` (CDP `Emulation.setCPUThrottlingRate 6`), `auth.denied|expired`, `concurrency.doubleSubmit|staleWrite`, `time.dstBoundary|leapDay|farFuture`.
* Generic oracles: no unhandled exception, no console error, no infinite spinner beyond 10s, declar
SPEC(first 1200): * Plan schema: `{ pageId, scenarios: [{ id, class, description, setup: { seed?, route?, viewport?, auth? }, steps, expect: [oracleId or custom] , severityIfFails }] }`, capped at 30 scenarios per page, prioritised by spec-declared risk and diff size.
* Prompt `.claude/agents/reviewers/edge-case-hunter.md` includes the spec, the diff summary, the fixture catalogue, prior scenarios for the same component types, and outputs JSON only.
* Executor uses `quality/playwright-matrix` fixtures; runs at `sm-375` and `xl-1280` by default; seeds via the test seed endpoint with generated payloads from `@faker-js/faker` with a fixed seed and unicode corpora in `ops/quality/corpora/`.
* Budget: planning under $2 and execution under 8 minutes per PR across 2 shards; excess scenarios deferred to the nightly run on `main`.
* Findings include the reproduction command `pnpm edge:run --page <id> --scenario <sid>` and a screenshot or video evidence ref.
* Nightly run on `main` executes the full scenario library for all pages and opens Linear issues for new S1 findings (deduped by finding ID) via `pm-linear/webhooks`.
DOD:
* On a PR touching a page with a spec, the hunter posts a matrix with at least 15 scenarios executed and evidence for failures (link).
* Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) are each caught with correct severity.
* Generated repro tests PR opened for failures and passes lint and typecheck.
* Clean page yields zero S0/S1 and a green `gate/4-edge`.
* Nightly run wired with dry-run Linear issue creation shown; `docs/quality/edge-cases.md`; CHANGELOG entry; Linear comment with matrix screenshot.
EDGE:
* Page without a spec: hunter posts S1 "no spec" (validator should already block) and runs only generic oracles.
* Scenario itself is flaky (network fixture timing): repeat 3 times, report only consistent failures, log flakes to `quality/flake-quarantine`.
* Huge data seeding slow: cap seeding at 20s and fall back to client-side mock via MSW for `data.huge`.
* Destructive scenarios against shared staging: hunter only runs against the ephemeral preview with its own seeded tenant.
* Scenario plan generation returns duplicates or invalid classes: schema validation drops them and logs counts.
* Findings duplicating `quality/screenshot-annotation` overflow findings: dedupe by page and bbox overlap over 0.6.
DEPS: `spec-builder/schema` and `quality/review-agents` (hard: spec shape and SDK harness). Soft: `quality/playwright-matrix` fixtures, `quality/screenshot-annotation` DOM metrics, `data-layer/api-layer` seed endpoint, `pm-linear/webhooks`. Consumed by `quality/release-train`, `quality/review-report`, `agents/eval-harness`.


## PAP-86 [P1 Build M prio2 Backlog] Write end-to-end flow tests for auth, tenant switch, CRUD and realtime presence
key=quality/e2e-flows milestone=Visual and video gates agent=Built by Sentinel (Code Reviewer sub-agent writing tests) wi
blockedBy=['PAP-26', 'PAP-58'] blocks=['PAP-90']
GOAL: Provide functional end-to-end smoke coverage of the core platform, distinct from screenshots: sign-in with each method, organisation and workspace creation, invitation and tenant switch, record CRUD through the API-backed UI, and realtime presence between two users, run on every PR against the preview build and nightly against staging.
SCOPE: In:

* `apps/web/e2e/functional/` Playwright project `functional` (Chromium at 1280, plus a `mobile` run at 375 for the same specs nightly) with specs: `auth.spec.ts` (passkey via virtual authenticator, magic link via a test mail sink, OAuth via stubbed provider), `tenancy.spec.ts` (create org, create workspace, invite, accept as second user, switch, leave), `crud.spec.ts` (create, edit, list filter, delete, undo on the example entity from `data-layer/core-entities`), `presence.spec.ts` (two browser contexts, cursors and avatars appear and disappear, agent participant badge if `realtime/agent-presence` exists), `permissions.spec.ts` (customer cannot reach staff console; staff without role denied).
* Test infrastructure: `apps/web/e2e/support/` with `testUsers` per audience, `seed()` and `reset()` against the `/__test/*` endpoints (enabled only when `PAPEROS_TEST_MODE=1`), `mailsink` clie
SPEC(first 1200): * Playwright config `apps/web/playwright.functional.config.ts`: `baseURL` from env, `storageState` per audience cached in `beforeAll`, `retries: 2` in CI with flake reporting to `quality/flake-quarantine`, `trace: 'on-first-retry'`, `video: 'retain-on-failure'`.
* Passkeys: `CDPSession.send('WebAuthn.enable')` and `addVirtualAuthenticator({ protocol: 'ctap2', transport: 'internal', hasResidentKey: true, hasUserVerification: true, isUserVerified: true })`.
* Magic link: poll Mailpit API `GET /api/v1/messages` filtered by recipient, extract link, visit; timeout 15s.
* OAuth: `identity/better-auth` exposes a `mock` provider in test mode; tests assert callback handling only.
* Presence: contexts A and B join the same document route; assert `getByTestId('presence-avatar')` count and cursor element for the other user within 3s; disconnect B and assert removal within 10s.
* Data isolation: every test creates its own tenant with a unique slug; `reset()` only truncates test tenants (slug prefix `e2e-`).
* Test IDs: `data-testid` naming convention `area.element[.modifier]` documented in `docs/quality/testing.md`; components accept `testId` prop where dynamic.
DOD:
* Five specs pass on a PR against the ephemeral stack in under 5 minutes for `@smoke` (link).
* Nightly `@full` including the 375 run passes on staging (link).
* Seeded regression (breaking tenant switch) fails with a trace attached (link).
* Traces and videos retained on failure and linked in the job summary.
* `docs/quality/testing.md` covers running locally with `pnpm e2e`, test-mode endpoints and test IDs; CHANGELOG entry; Linear comment with report links.
EDGE:
* Test-mode endpoints must be impossible to enable in production: guarded by env and by a build-time check that strips them unless `PAPEROS_TEST_MODE` is set; security reviewer verifies.
* Two shards creating tenants with the same slug: slug includes shard and worker index.
* Mail arrives out of order or duplicated: match by a unique token embedded in the email address (`user+<uuid>@e2e.local`).
* Presence test timing on slow runners: use generous timeouts and `expect.poll`, not sleeps.
* OAuth provider not stubbed yet: test skipped with a clear reason, not silently passed.
* Ephemeral Postgres slow to start: healthcheck wait loop with 60s cap and readable failure.
DEPS: `identity/org-tenancy` (hard, and by extension `identity/better-auth`). Soft: `data-layer/api-layer` (CRUD target and test endpoints), `realtime/presence` (presence spec skipped until merged), `quality/playwright-matrix` (shared image and fixtures), `data-layer/postgres-provision` (compose pieces). Consumed by `quality/flake-quarantine`, `quality/release-train`, `identity/permission-tests` (pattern).


## PAP-87 [P1 Infra S prio2 Backlog] Enforce performance budgets (LCP, INP, bundle size) with Lighthouse CI
key=quality/perf-budgets milestone=Visual and video gates agent=Built by Sentinel with Forge (Ops Runner) deploying the LHCI
blockedBy=['PAP-78'] blocks=[]
GOAL: Make speed a gate: Lighthouse CI measures LCP, INP proxies, CLS, TBT and PWA installability on key pages of every PR preview, `size-limit` guards JavaScript bundle weight per route, and any regression beyond the budget fails the PR with a diff against `main`.
SCOPE: In:

* `ops/ci/lighthouserc.json` and workflow job `perf` in `.github/workflows/perf.yml` triggered after Gate 1 build, serving `web-dist` with `vite preview` and running `@lhci/cli` 0.15.x on the page list from `quality/playwright-matrix` (`perf: true` in page specs; defaults: `/`, `/_app/dashboard`, `/_app/settings`, `/auth/sign-in`), 3 runs each, mobile and desktop presets.
* Budgets: mobile LCP under 2.5s, TBT under 200ms, CLS under 0.1, performance score at or above 90, accessibility at or above 95, PWA installable (from `app-shell/pwa`); desktop LCP under 1.5s.
* Bundle budgets with `size-limit` 11.x and `@size-limit/file` on `apps/web/dist`: initial JS under 180 KB gzipped, per-route chunk under 120 KB, CSS under 60 KB, `packages/ui` Button import under 6 KB (shared with `design-system/primitives`).
* LHCI server: self-hosted `lhci server` in Docker via Coolify on the VPS with SQL
SPEC(first 1200): * `lighthouserc.json`: `ci.collect.url` templated from `BASE_URL`, `numberOfRuns: 3`, `settings.preset: 'desktop'` for the desktop run and default mobile with `throttlingMethod: 'simulate'`; `ci.assert.assertions` per budget with `aggregationMethod: 'median-run'`; `ci.upload.target: 'lhci'`.
* Budgets also as `ops/ci/budget.json` (Lighthouse budgets format) for resource counts and sizes per type.
* `size-limit` config in `apps/web/.size-limit.json`; runs `pnpm build` output only (no rebuild); comment produced by `size-limit`'s JSON output merged into our sticky comment rather than a second comment.
* Comparison: script `ops/ci/perf-compare.ts` fetches the latest `main` LHCI run for each URL and computes deltas; if `main` has no baseline yet, comment says so and only absolute budgets apply.
* Tauri and PWA offline shell excluded; PWA category asserted only on `/`.
* Documentation of how to fix common regressions (code splitting with `React.lazy`, image sizing, font preload) in `docs/quality/performance.md`.
DOD:
* Perf job runs on a PR and posts the table with deltas against `main` (link); LHCI server dashboard shows both runs.
* Seeded regression (importing a 300 KB library on the dashboard) fails `size-limit` and drops LCP; gate red (link). Removing it restores green.
* All default pages meet budgets on `main` at the time of merge; numbers in the PR.
* `web-vitals` hook sends metrics in dev to the console and to the observability endpoint when configured.
* `docs/quality/performance.md`; CHANGELOG entry; Linear comment with dashboard link and table screenshot.
EDGE:
* Runner CPU variance producing noisy LCP: 3 runs with median, and budgets applied with a 10 percent tolerance band for warnings before failing.
* Pages requiring auth: use Lighthouse `puppeteerScript` (or `extraHeaders` cookie) with the seeded test user storage state.
* Preview served from a subpath (`/pr/<n>/`): use local `vite preview` in CI rather than Pages to avoid CDN variance; Pages measured only informationally on nightly.
* Third-party scripts (analytics) inflating budgets: none allowed without an ADR; flagged by `budget.json` third-party count 0.
* Bundle chunk names change per build: `size-limit` matches by glob and reports per-route via a manifest, not file names.
* LHCI server down: job posts absolute results and marks comparison unavailable; still enforces budgets.
DEPS: `quality/ci-gate1` (hard: artifact and status pattern). Soft: `app-shell/pwa` (installability), `quality/playwright-matrix` (page list and auth state), `data-layer/observability` (vitals sink), `design-system/primitives` (Button budget). Consumed by `quality/release-train`, `quality/review-report`, `libraries/upgrade-bot` (bundle impact of upgrades).


## PAP-88 [P1 Spec L prio1 Backlog] Define the release train: nightly staging deploy, weekly release candidate to Needs Justin with consolidated review report
key=quality/release-train milestone=Edge-case hunting and release trains agent=Written and built by Sentinel with Atlas (Merger sub-agent) 
blockedBy=['PAP-26', 'PAP-82', 'PAP-81'] blocks=['PAP-89', 'PAP-29']
GOAL: Define and automate the cadence that keeps Justin out of pull requests: every merge to `main` deploys to staging nightly, every Monday a release candidate is cut from `main`, all gate evidence is consolidated, and a single Linear issue in Needs Justin asks for one approve or reject decision that promotes the candidate to production and tags a release.
SCOPE: In:

* Written policy `docs/quality/release-train.md`: branches (`main` always releasable, `release/<yyyy-ww>` cut Monday 08:00 UTC), what may be merged when (freeze rules for the RC branch: fixes only, labelled `rc-fix`), hotfix path, rollback procedure, environments (preview per PR, staging, production), and who decides what (Atlas merges, Sentinel certifies, Justin approves releases only).
* Workflow `.github/workflows/staging-nightly.yml`: 02:00 UTC build and deploy `main` to staging through the Coolify deploy webhook, run `@full` e2e (`quality/e2e-flows`), full visual matrix, edge-case library, perf; write `reports/nightly-<date>.json`.
* Workflow `.github/workflows/release-candidate.yml`: Monday cut creates `release/<yyyy-ww>`, opens a release PR labelled `release-candidate` (feeds `forge/release-tags` prerelease `-rc.N`), deploys it to staging, runs all gates, then calls `quality/
SPEC(first 1200): * Environment config in `ops/release/environments.yaml`: `{ name, url, coolifyWebhookSecretName, database, allowedBranches }`.
* Coolify deploy via `POST /api/v1/deploy?uuid=...` with bearer token secret; wait for deployment status API to report `finished`; smoke `GET /healthz` and `/__version` equals the SHA.
* Migrations run in the deploy job before app rollout, with `drizzle-kit migrate`; a `pre-deploy-backup` step calls the backup script and records the snapshot id in the release record.
* Release record `ops/release/records/<version>.json`: SHA, date, gates summary, digest link, approver, deployed-at, rollback target; committed by the bot.
* Rollback: `pnpm release:rollback <version>` redeploys the previous image tag and, if flagged, restores the pre-deploy snapshot (with confirmation). Documented drill in the policy.
* Linear issue template for the RC: title `Release candidate <yyyy-ww> (vX.Y.Z-rc.N)`, body with digest link, gate table, one-line ask, and the two commands.
* Feature flags for risky work land behind `packages/core/src/flags` defaults off, so RCs are always shippable (policy).
DOD:
* Policy doc merged and linked from CLAUDE.md and the PR template.
* Nightly staging deploy ran three nights in a row with reports (links).
* A rehearsal RC cut end to end: branch, PR, gates, digest, Needs Justin issue created, `/approve` in a test tenant of Linear promotes to a staging-as-production target and tags `v0.1.0-rc.1` (links, screenshots of the Linear issue).
* `/reject` path tested and documented.
* `certify.ts` blocks promotion when a gate status is missing (seeded test).
* CHANGELOG entry; Linear comment with rehearsal links; ADR `docs/adr/0008-release-train.md`.
EDGE:
* `main` red on Monday: RC not cut; Linear comment on the previous RC issue explains; Atlas gets a task to fix.
* Hotfix needed mid-week: branch from the last tag, PR labelled `hotfix`, gates run, Justin approval via a short Needs Justin issue, cherry-pick back to `main`.
* Justin approves but production deploy fails: auto-rollback, issue reopened with logs, status stays Needs Justin.
* Two approvals within seconds (duplicate webhook): idempotency key on the release record prevents double deploy.
* Database migration irreversible: certification requires a Justin acknowledgement checkbox in the digest.
* Coolify API down: promotion job retries for 30 minutes then fails loudly with manual steps documented.
DEPS: `quality/review-agents` and `quality/playwright-matrix` (hard: gates to consolidate). Soft: `quality/e2e-flows`, `quality/edge-case-hunter`, `quality/perf-budgets`, `forge/release-tags`, `pm-linear/justin-queue`, `pm-linear/webhooks`, `collab/changelog`, `data-layer/postgres-provision`. Consumed by `quality/review-report`, `forge/release-tags`, `agents/handoffs`.


## PAP-89 [P1 Build M prio1 Backlog] Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions
key=quality/review-report milestone=Edge-case hunting and release trains agent=Built by Sentinel with Quill (Changelog Scribe) owning prose
blockedBy=['PAP-88'] blocks=[]
GOAL: Generate the one page Justin actually reads for each release candidate: what changed in plain language, what the gates found and how it was resolved, the risks and open questions that need his decision, and the screenshots and replays that let him see the product in under ten minutes. Everything else stays in the machines.
SCOPE: In:

* `packages/agents/src/digest/buildDigest({ from, to, rcBranch })` collecting: merged PRs with Linear issues and characters (forge API and Linear GraphQL), conventional-commit changelog (`collab/changelog` output or `git log` fallback), gate results per PR (`gate1.json`, `security.json`, `visual.json`, `vision.json`, `edgecases.json`, perf tables, e2e reports), waivers granted, open S1 findings, cost spent per project from `pm-linear/credit-metering`, and nightly staging trends.
* A Claude summarisation step (model `claude-fable-5-1`) producing structured sections from the collected JSON, with strict rules: cite the PR or finding ID for every claim, no adjectives without numbers, max 900 words of prose.
* Output formats: Markdown `docs/releases/<version>.md` committed to the repo, an HTML page with embedded screenshots and replay posters published to Pages at `/releases/<version>/`,
SPEC(first 1200): * Digest schema `packages/agents/src/digest/digest.schema.ts` (Zod): `{ version, range: { fromSha, toSha, fromDate, toDate }, decision: { ask, approveCommand, rejectCommand, deadline }, changes: [{ project, title, prs: [{ number, url, linearKey, character }], userFacing: boolean, summary, screenshots: [...] }], quality: { gates: [{ name, status, link }], findings: { S0, S1, S2, S3, fixed, waived }, calibration: {...} }, risks: [{ id, title, detail, recommendation, requiresAnswer: boolean }], replays: [...], cost: {...}, links: {...} }`.
* Renderer: Markdown via template literals; HTML via a small static template using the design tokens CSS so it looks like the product; no client JS beyond video posters.
* Summarisation prompt `.claude/agents/digest-writer.md` receives only the schema-shaped data and returns the prose fields; a validation pass checks every cited ID exists in the data, else the sentence is dropped and logged.
* Length checks: prose under 900 words, page renders under 2 screens at 1280 excluding appendix; HTML under 5 MB with images.
* `pnpm digest --from v0.1.0 --to release/2026-39 --out docs/releases/` for local runs; the release workflow calls the same.
* Linear bo
DOD:
* Digest generated for a rehearsal range with all seven sections populated from real gate artifacts; HTML published to Pages and Markdown committed (links).
* Citation validator drops a seeded unsupported claim (test).
* Justin reads the rehearsal digest and confirms via a Linear comment it answers his three questions (what changed, is it safe, what do I need to decide); adjust once based on feedback.
* Screenshots at 375, 1280 and 1920 of the HTML digest itself in light and dark attached.
* Vitest for schema, renderer snapshots and length checks; `docs/quality/review-report.md`; CHANGELOG entry; Linear comment with the digest link.
EDGE:
* Range with zero user-facing changes: section 2 says so explicitly and leads with infrastructure changes.
* Missing gate artifact for one PR (expired): shown as `unknown` with a link to re-run, never omitted.
* More than 40 PRs in range: group by project and collapse minor ones into counts with a link list.
* Signed replay URLs expired: digest build re-signs or falls back to run artifacts.
* Cost data unavailable: section 6 shows `n/a` with reason; never invented numbers.
* Justin asks a question in the Linear issue: `agents/handoffs` routes it; the digest page links the thread.
DEPS: `quality/release-train` (hard: trigger and inputs). Soft: `quality/playwright-matrix`, `quality/video-replays`, `quality/screenshot-annotation`, `quality/edge-case-hunter`, `quality/perf-budgets`, `collab/changelog`, `pm-linear/credit-metering`, `pm-linear/justin-queue` (comment commands), `app-shell/gh-pages-demo` (hosting).


## PAP-90 [P2 Build M prio3 Backlog] Build flaky-test detection and quarantine so agents are not blocked by nondeterminism
key=quality/flake-quarantine milestone=Edge-case hunting and release trains agent=Built by Sentinel (Edge Case Hunter sub-agent, who sees flak
blockedBy=['PAP-86'] blocks=[]
GOAL: Stop nondeterministic tests from blocking twenty parallel agent sessions: detect flaky unit, e2e, visual and flow tests from retry data, score them, automatically quarantine repeat offenders with a Linear issue assigned to the owning character, keep running them out of band, and un-quarantine when they stabilise.
SCOPE: In:

* Flake database `ops/quality/flakes.json` (committed, bot-updated) plus a nightly aggregate in the LHCI-style SQLite store or Postgres table `qa_flakes` (`test_id, suite, first_seen, last_seen, runs, failures, retried_passes, score, state: active|quarantined|resolved, linear_key, owner`).
* Collectors: Vitest JUnit and JSON reports (`retry` flag), Playwright JSON reports (`status: flaky`), visual suite `reports/visual.json` (diffs that vanish on rerun), flow and edge-case reports; a reporter step `ops/quality/collect-flakes.ts` runs at the end of every gate workflow and posts to `POST /api/qa/flakes` on the API (`data-layer/api-layer`) or appends to the JSON in a bot commit on `main` runs.
* Scoring: `score = retriedPasses / runs` over the last 20 runs; `>= 0.15` for three runs = quarantine candidate; auto-quarantine when candidate persists for 24h or when the same test blocks two 
SPEC(first 1200): * Test ID grammar: `<suite>::<file>::<fullTitle>` with paths relative to repo root; stable across renames only if title unchanged (documented).
* `collect-flakes.ts` inputs: report paths via CLI flags; outputs `reports/flakes-delta.json`; on PRs it comments a one-line note when a retried pass occurred ("1 flaky test detected, not blocking, tracked as FL-123").
* Quarantine file schema (Zod) with `expires` (default 14 days, extended on activity) so no test stays quarantined silently; expired entries fail the collect step until renewed or resolved.
* The `quarantine` Playwright project runs quarantined tests with `retries: 0` to gather clean statistics.
* Weekly summary comment on the release digest (`quality/review-report` section 3) with counts and top 5 flakes.
* Ownership mapping: `ops/quality/owners.yaml` overrides blame when a file is shared.
DOD:
* Collector runs at the end of Gate 1, e2e, visual and flow workflows and updates the DB (links).
* A seeded flaky test (random 30 percent failure) gets detected within 5 runs, quarantined automatically with a Linear issue created (screenshot), and the PR that contains it goes green with the note.
* Fixing the test (remove randomness) leads to auto-resolution after the configured runs in a compressed test (runs threshold overridable for the demo).
* Quarantine cap test: exceeding 5 percent fails the gate with a clear message.
* `docs/quality/flakes.md` generated and linked; CHANGELOG entry; Linear comment with the seeded flake issue link and dashboard.
EDGE:
* Test that fails deterministically only on one shard or width: score per environment key; quarantine scoped to that environment.
* Renamed test title resets history: collector detects same file and near-identical title (Levenshtein under 5) and links histories.
* Flaky because of a real race condition in product code: quarantine issue template asks the owner to classify `test-bug` vs `product-bug`; product bugs escalate to S1 finding, not quarantine.
* Bot commit of `flakes.json` racing with agent PRs: only `main` runs commit; PR runs post deltas as artifacts.
* Test removed from the codebase: entry resolved with reason `deleted`.
* Quarantined visual baseline drifts silently: quarantined visual tests still record diffs to the report as informational.
DEPS: `quality/e2e-flows` (hard: first real flake source and Playwright report shape). Soft: `quality/ci-gate1`, `quality/playwright-matrix`, `quality/video-replays`, `pm-linear/webhooks`, `data-layer/api-layer` (storage), `forge/bot-accounts` (commits). Consumed by `quality/release-train`, `quality/review-report`, `agents/eval-harness`.
