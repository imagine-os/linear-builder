# Round 4 digest: Quality Pipeline (`quality`)

Benchmarks: GitHub Actions; Chromatic; Percy; Playwright trace viewer; Sentry; CodeRabbit; Greptile; Snyk; SonarQube; Codecov; Stryker; Lighthouse CI; k6; OWASP ZAP; Schemathesis; BuildPulse (flake management); GitHub merge queue; release trains (Chromium-style).

## Feature matrix (69 rows: 48 covered, 6 partial, 15 gap)

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Static checks: typecheck, lint, format, unit tests, build, commitlint, generated drift | covered | PAP-78 |  |
| Affected-only runs and remote cache | covered | PAP-78 | Turbo filter and remote cache |
| Required-checks matrix per PR type (docs-only, infra, code) | partial | PAP-78 | path filters exist; no single aggregate check policy; amendment |
| Package coverage floor | covered | PAP-78 | lines 70 per package |
| Patch (diff) coverage gate with inline annotations | gap | r4/quality/diff-coverage-gate | Codecov-style patch coverage |
| Mutation testing | gap | r4/quality/mutation-testing-nightly | Stryker nightly on three packages; deferred |
| Dependency vulnerability audit and SBOM | covered | PAP-80 | osv-scanner, pnpm audit, CycloneDX |
| Secret scanning (diff and history) | covered | PAP-80 | gitleaks |
| SAST with custom rules tied to threat-model controls | covered | PAP-80, PAP-219 | Semgrep |
| Container image scanning | covered | PAP-80 | Trivy |
| License policy in CI | covered | PAP-211, PAP-80 | libraries project |
| Supply-chain integrity: pinned actions, provenance, signatures | covered | PAP-358 | forge project |
| Dynamic application security testing (ZAP) | covered | PAP-357, r4/quality/dast-zap-nightly-and-authenticated-scans | split into two children this round |
| Security regression suite tagged with control ids | covered | PAP-357, r4/quality/security-regression-suite |  |
| Security telemetry, alerting and weekly digest | covered | PAP-356, r4/quality/security-event-catalogue-emitters, r4/quality/security-alert-rules-routing-digest | split into two children this round |
| Migration safety lint (destructive DDL, locks, RLS gaps, reversibility) | gap | r4/quality/migration-safety-gate | PAP-254 asks for a reversible flag nobody computes |
| AI code review: correctness reviewer | covered | PAP-244 | CodeRabbit/Greptile class |
| AI code review: security reviewer with scanner ingestion | covered | PAP-245 |  |
| AI code review: spec-conformance reviewer | covered | PAP-244 |  |
| AI review of docs, specs, prompts, ADRs, changelogs | gap | r4/quality/docs-and-spec-reviewer | PAP-81 excludes non-code artefacts although PAP-79 has the rubric |
| Review harness: read-only tools, idempotent posting, both forges | covered | PAP-243 |  |
| Reviewer model routing per builder model (cost doc 4b) | partial | PAP-243 | PAP-243 hard-codes Fable 5.1; amendment |
| Review fix loop: blocking review re-queues the builder, round cap, escalation | gap | r4/quality/review-fix-loop | cost model assumes 30 percent bounce; nothing wires it |
| Review calibration, precision and recall, escaped-defect tracking | covered | PAP-241 |  |
| Rubrics and severity taxonomy shared by agents and humans | covered | PAP-79 |  |
| Gate artefact contract and status registry | partial | PAP-239, PAP-462 | kind names disagree between PAP-239 and PAP-462; amendment |
| Visual regression: story capture across widths and themes | covered | PAP-246 | Chromatic class |
| Visual regression: authenticated page capture and baseline workflow | covered | PAP-247 | Percy class |
| Contact sheets, sharding, visual artefact | covered | PAP-248 |  |
| Video replays of critical flows per width | covered | PAP-83 |  |
| Vision agent annotation of screenshots and contact sheets | covered | PAP-84 |  |
| Pseudo-locale and RTL visual run | gap | r4/quality/pseudo-locale-and-rtl-visual-run | deferred |
| Cross-browser functional smoke (WebKit, Firefox) | gap | r4/quality/cross-browser-functional-smoke | deferred; Chromium only today |
| Desktop (Tauri) smoke | gap | r4/quality/desktop-tauri-smoke | deferred; PAP-86 excludes native |
| Mobile device e2e | partial | PAP-260 | device proofs in app-shell; no automated flow |
| Functional e2e: auth, tenancy, CRUD, permissions, presence | covered | PAP-86 |  |
| Test mode: deterministic seed, reset, login-as, clock | covered | PAP-240 |  |
| Ephemeral preview stack per PR | covered | PAP-86, PAP-26 | compose preview and Coolify previews |
| Test-id and fixture conventions | covered | PAP-86, PAP-240 |  |
| Recorded HTTP fixtures shared across suites | gap | r4/quality/recorded-http-fixtures-kit | ten suites each plan their own nock recording |
| Quality sandbox repo and seeded-defect catalogue | gap | r4/quality/quality-sandbox-repo-and-seeded-defects | eleven DoDs depend on a repo no issue creates |
| Edge-case hunter: scenario planning from specs | covered | PAP-249 |  |
| Edge-case hunter: executor and oracles | covered | PAP-250 |  |
| Edge-case hunter: findings, repro tests, nightly library | covered | PAP-251 |  |
| API fuzzing from OpenAPI | gap | r4/quality/api-fuzzing-nightly | PAP-85 excludes API fuzzing |
| Property-based testing in unit suites | partial | PAP-99, PAP-103 | fast-check used ad hoc; no shared guidance |
| Accessibility audit of components (axe, screen reader) | covered | PAP-73, PAP-156 | design-system and input projects |
| Accessibility score budget on pages | covered | PAP-87 | Lighthouse accessibility at or above 95 |
| Web performance budgets (LCP, INP, CLS, bundle size) | covered | PAP-87 | Lighthouse CI, size-limit |
| API and database performance budgets (k6, slow queries, image size) | covered | PAP-242 |  |
| Load testing of realtime | covered | PAP-147 | realtime project |
| Flaky-test detection and quarantine | covered | PAP-90 |  |
| Gate metrics and pipeline health dashboard | gap | r4/quality/gate-metrics-and-pipeline-health | no aggregation of gate durations, cost, bounce, queue time |
| Release train: policy, environments, nightly staging | covered | PAP-252, PAP-253 |  |
| Release certification and Justin approval flow | covered | PAP-254 |  |
| Rollback and hotfix path | covered | PAP-252, PAP-254 |  |
| Canary and flag-based rollout | covered | PAP-435, PAP-366 | module-system and app-shell |
| Release digest for the human reviewer | covered | PAP-89 |  |
| Changelog generation | covered | PAP-133, PAP-52 | collab and forge |
| QA evidence browser in-app | gap | r4/quality/qa-evidence-browser | deferred; PAP-239 names a viewer nobody builds |
| Screenshot and video annotation to Linear issues | covered | PAP-137 | collab, deferred by schedule |
| Quality handbook and how-to front door | gap | r4/quality/quality-handbook | fourteen reference docs, no index |
| Merge queue with speculative-merge gate run | gap | - | cross-project suggestion to forge (PAP-46) |
| Runner capacity and CI cost budget (shards, LFS, Docker) | partial | PAP-50 | audit flagged the assumption; cross-project suggestion to forge |
| Contract conformance in Gate 1 | covered | PAP-441, PAP-463 | module system |
| Contract compatibility matrix | covered | PAP-440 | module system |
| Dependency lint and dependency map | covered | PAP-439 | module system |
| Chaos and DR drills | covered | PAP-354, PAP-53 | data-layer and forge |
| Agent behaviour review of transcripts | covered | PAP-79, PAP-110 | rubric plus evals |

## New issues (18: 5 children, 13 gaps, 5 deferred to v0.2)

| Key | Title | Parent | Type / Phase | Prio | Size (est.) | Model / effort | Milestone (due) | Blocked by |
|---|---|---|---|---|---|---|---|---|
| `r4/quality/security-event-catalogue-emitters` | Security telemetry: event catalogue, emitters in API, auth, orchestrator, proxy and Postgres, and the `security_event` table | PAP-356 | Build P1 | 2 | M (3) | Opus 5 / high | Edge-case hunting and release trains (2026-09-30) | PAP-40, PAP-38 |
| `r4/quality/security-alert-rules-routing-digest` | Security telemetry: rules engine, S0 routing to the pinned alerts issue and Needs Justin, weekly digest and Grafana dashboard | PAP-356 | Build P1 | 2 | M (3) | Opus 5 / high | Edge-case hunting and release trains (2026-09-30) | r4/quality/security-event-catalogue-emitters, PAP-97 |
| `r4/quality/dast-zap-nightly-and-authenticated-scans` | DAST: nightly ZAP baseline, weekly authenticated full scan per seeded audience, SARIF merge and `gate/dast` status | PAP-357 | Infra P1 | 2 | M (3) | Opus 5 / high | Edge-case hunting and release trains (2026-09-30) | PAP-80, PAP-240, PAP-26 |
| `r4/quality/security-regression-suite` | Security regression suite: 30+ control-tagged tests (headers, CSRF, IDOR across tenants, rate limits, upload abuse, webhook replay, SSRF, Tauri origin) blocking the release candidate | PAP-357 | Build P1 | 2 | M (3) | Opus 5 / high | Edge-case hunting and release trains (2026-09-30) | PAP-80, PAP-240, PAP-64, r4/quality/dast-zap-nightly-and-authenticated-scans |
| `r4/quality/docs-and-spec-reviewer` | Docs and spec reviewer definition: fourth Gate 2 reviewer for PRs that change specs, docs, prompts, ADRs or changelogs | PAP-81 | Build P1 | 3 | S (2) | Sonnet 5 / medium | Gates 1 and 2 on every PR (2026-09-25) | PAP-243, PAP-79 |
| `r4/quality/quality-sandbox-repo-and-seeded-defects` | Create the quality sandbox repo `imagine-os/paperos-qa-sandbox` with the seeded-defect catalogue every gate's Definition of done rehearses against | - | Infra P0 | 1 | S (2) | Opus 5 / high | Gates 1 and 2 on every PR (2026-09-25) | PAP-13, PAP-51 |
| `r4/quality/review-fix-loop` | Review fix loop: turn a Gate 2 `REQUEST_CHANGES` into a builder re-queue with the findings in the prompt, two rounds maximum, then escalate | - | Build P0 | 1 | M (3) | Opus 5 / high | Gates 1 and 2 on every PR (2026-09-25) | PAP-243, PAP-281, PAP-108 |
| `r4/quality/gate-metrics-and-pipeline-health` | Gate metrics and pipeline health: `qa_gate_runs` table, duration and pass-rate trends, reviewer cost per PR, bounce rate and queue time, with a Grafana board and a digest section | - | Build P1 | 3 | S (2) | Sonnet 5 / medium | Edge-case hunting and release trains (2026-09-30) | PAP-239, PAP-40 |
| `r4/quality/diff-coverage-gate` | Diff coverage gate: per-PR patch coverage from Vitest `lcov`, 80 percent floor on changed lines, uncovered-line annotations and a coverage delta in the sticky comment | - | Infra P1 | 3 | S (2) | Sonnet 5 / medium | Gates 1 and 2 on every PR (2026-09-25) | PAP-78 |
| `r4/quality/migration-safety-gate` | Migration safety gate: lint Drizzle migrations for destructive DDL, missing down path, long locks and RLS gaps; require the `migration-ack` checkbox for irreversible changes | - | Infra P1 | 2 | S (2) | Opus 5 / medium | Gates 1 and 2 on every PR (2026-09-25) | PAP-78, PAP-32 |
| `r4/quality/recorded-http-fixtures-kit` | Recorded HTTP fixtures kit: one `msw` recorder and fixture store for Linear, GitHub, Forgejo, Anthropic and Coolify used by every pipeline test suite | - | Build P0 | 2 | S (2) | Sonnet 5 / medium | Gates 1 and 2 on every PR (2026-09-25) | PAP-13 |
| `r4/quality/api-fuzzing-nightly` | API fuzzing nightly: Schemathesis against the OpenAPI document with test-mode auth, per-procedure crash and 5xx findings into `edgecases.json` | - | Infra P2 | 3 | S (2) | Sonnet 5 / medium | Edge-case hunting and release trains (2026-09-30) | PAP-269, PAP-240, PAP-251 |
| `r4/quality/quality-handbook` | Quality handbook: one page that explains the four gates, how to read a PR's evidence, how to update baselines, waive a finding, quarantine a flake and rehearse a release | - | Docs P1 | 3 | S (2) | Haiku 4.5 / low | Visual and video gates (2026-09-26) | PAP-78, PAP-243, PAP-246 |
| `r4/quality/mutation-testing-nightly` | Mutation testing nightly with Stryker on `packages/core`, `packages/permissions` and `packages/finance`: mutation score floor and survivors as S2 findings | - | Infra P2 | 4 deferred | S (2) | Sonnet 5 / medium | Edge-case hunting and release trains (2026-09-30) | PAP-78, r4/quality/diff-coverage-gate |
| `r4/quality/cross-browser-functional-smoke` | Cross-browser functional smoke: run the `@smoke` e2e tag on WebKit and Firefox nightly and on PRs touching input, auth or realtime packages | - | Infra P2 | 4 deferred | S (2) | Sonnet 5 / medium | Visual and video gates (2026-09-26) | PAP-86 |
| `r4/quality/pseudo-locale-and-rtl-visual-run` | Pseudo-locale and RTL visual run: capture the Gate 3 page set in `en-XA` pseudo-locale and `ar` RTL at three widths nightly, flagging truncation and mirrored-layout defects | - | Build P2 | 4 deferred | S (2) | Sonnet 5 / medium | Visual and video gates (2026-09-26) | PAP-247, PAP-27 |
| `r4/quality/qa-evidence-browser` | QA evidence browser: staff page `/qa` that lists PRs and release candidates with their gate reports, screenshots, replays, traces and findings read from `GateReport` artefacts | - | Build P2 | 4 deferred | M (3) | Sonnet 5 / high | Edge-case hunting and release trains (2026-09-30) | PAP-239, PAP-248, PAP-83, PAP-165 |
| `r4/quality/desktop-tauri-smoke` | Desktop smoke via `tauri-driver` on Linux: launch the packaged app, sign in through the deep link, open a record and detach a panel, recorded nightly | - | Infra P2 | 4 deferred | S (2) | Sonnet 5 / medium | Visual and video gates (2026-09-26) | PAP-256, PAP-257, PAP-240 |

## Amendments to existing specs (8)

* **PAP-243** (Spec): * Reviewer model routing (round 4, cost doc section 4b): `runReview()` does not hard-code `claude-fable-5-1`. It reads the PR's issue `Model` label through `lin…
* **PAP-78** (Spec): * Required-checks matrix (round 4): one aggregate status `gates/required` computed by the `gate-1` job from the PR class: `docs-only` (paths `docs/**`, `specs/*…
* **PAP-462** (Spec): * Artefact kind names (round 4 consistency fix): the contract exports exactly the kinds PAP-239 registers: `gate1`, `security`, `visual`, `videos`, `vision`, `e…
* **PAP-253** (Spec): * Nightly schedule table (round 4): the self-hosted runner pool is shared, so nightly jobs are staggered and documented in `ops/ci/nightly-schedule.yaml`: 02:00…
* **PAP-89** (Edge cases): * Range with more than 40 PRs (a full week at 16 builders): section 2 groups by project and lists the ten most user-facing PRs in full, the rest as one line eac…
* **PAP-241** (Definition of done): * Round 4 clarification of the cadence: the calendar has room for two real weekly cycles before 2026-10-01 (weeks 39 and 40); the third cycle in the first bulle…
* **PAP-90** (Spec): * Environment keys (round 4): the score key gains `engine` (chromium, webkit, firefox) and `target` (web, desktop-linux) so cross-browser and desktop smoke flak…
* **PAP-84** (Spec): * Focus mode (round 4): `inspectScreenshots({ focus?: ('truncation'|'mirroring'|'overflow'|'contrast')[] })` restricts the prompt and the rubric subset for spec…

## Cross-project suggestions (6)

* **forge**: Merge queue with speculative-merge Gate 1 run and auto-rebase for the Merger
* **forge**: Size and budget the self-hosted runner pool for 4 visual shards, 2 edge shards, reviewers and nightly heavy jobs with queue-time alerts
* **design-system**: Storybook interaction tests as a Gate 1 job with the a11y addon failing on violations
* **libraries**: Mark every MCP catalog tool with a `scope` class (`readOnly`, `write`, `destructive`) and a `lastVerified` date
* **collab**: Linear status comment and digest link into the QA evidence browser
* **spec-builder**: Spec quality reviewer before build: run the docs-and-spec reviewer on `specs/**` PRs and block Ready for Claude on failing specs

## What was missing and why it matters

1. Eleven gate Definitions of done rehearse against a sandbox repo and seeded defects that no issue created; the sandbox and catalogue are now a P0 Infra issue every gate consumes.
2. Reviewers block PRs but nothing re-queued the builder: the review fix loop makes the 30 percent bounce the cost model assumes mechanical, with a two-round cap and escalation.
3. Agent-written migrations had no gate: destructive DDL, missing down paths and tables without RLS are now caught in Gate 1 with an explicit `migration-ack` for irreversible changes.
4. The two largest security issues (PAP-356 telemetry, PAP-357 DAST) were single M issues with two sessions of work each; both are split into children so cold sessions finish them.
5. Reviewer model routing contradicted the cost document (PAP-243 hard-coded Fable 5.1) and artefact kind names disagreed between PAP-239 and PAP-462; both are fixed by amendments, and diff coverage, API fuzzing, pipeline metrics and a quality handbook fill the remaining benchmark gaps.
