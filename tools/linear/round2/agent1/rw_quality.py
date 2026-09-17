DESCRIPTIONS = {}

DESCRIPTIONS["PAP-78"] = """**Goal**

Make Gate 1 the fast, deterministic check every PR in every imagine-os repo passes before any agent looks at it: typecheck, Biome lint and format, Vitest, commitlint, generated-file drift and a production web build, under three minutes warm, with a machine-readable `gate1.json` Gate 2 consumes and a `web-dist` artifact Gate 3 reuses.

**Scope**

* In: `.github/workflows/ci.yml` (Forgejo-compatible) with jobs `setup`, `lint`, `typecheck`, `test`, `build`, `commitlint`, `generated-drift`, aggregating `gate-1`; Turborepo remote cache on the VPS; Vitest coverage and JUnit; drift checks; required checks via PAP-46; `pnpm check` and `lefthook` pre-push; job summary and `reports/gate1.json`; the shared sticky-comment action other gates reuse.
* Out: security scans (PAP-80), Playwright (PAP-82), Lighthouse (PAP-87), release automation (PAP-88).

**Spec**

* Runner `ubuntu-24.04`, Node 22 from `.nvmrc`, pnpm via corepack, store cached on lockfile hash; Turbo cache via `TURBO_API/TOKEN/TEAM` against `ducktors/turborepo-remote-cache` deployed by Coolify; `--filter=...[origin/main]` for affected packages; concurrency group `ci-${{ github.ref }}` with cancel-in-progress.
* `commitlint` validates non-merge commits (last 50) and the PR title against `@commitlint/config-conventional` plus the `Linear:` and `Character:` trailer rule from PAP-46.
* `test`: `pnpm turbo test -- --reporter=default --reporter=junit --outputFile=reports/junit.xml`, coverage floor `lines: 70` per package, `retry: 1` in CI with retried tests written to `reports/flakes-delta.json` (PAP-90 format), failures annotated as `::error file=… line=…`.
* `build`: `pnpm turbo build --filter=web...`, uploads `apps/web/dist` as `web-dist`.
* `generated-drift`: `tokens:build`, `registry:build`, `gen:breakpoints`, `contracts:build`, `versions.json` check, then `git diff --exit-code`.
* `gate-1` runs `if: always()`, writes `reports/gate1.json` as `GateReport<'gate1'>` from `packages/contracts` (PAP-239) with `data: { jobs: [{ name, status, durationMs }], failures: [{ job, file, line, message }] }`, sets status `gate/1-static`, fails if any required job failed.
* Path filters: docs-only changes skip `build` and `test`. Env `TZ=UTC`, `LANG=en_US.UTF-8`. `timeout-minutes: 10` per job; soft alarm comment above 3 minutes total.

**Interface contract**

* Provides: artifact `web-dist`; `reports/gate1.json`; status `gate/1-static`; composite action `ops/ci/actions/sticky-comment` (one PR comment with named sections, used by PAP-80, PAP-82, PAP-83, PAP-84, PAP-85, PAP-87); composite `ops/ci/actions/setup` (pnpm, Turbo, Playwright cache); `workflow_run` completion event that PAP-81 and PAP-82 trigger on; `pnpm check`.
* Requires: PAP-13 `ci.yml` skeleton (hard, same file), PAP-46 required checks and trailer rule, PAP-239 artifact schema (soft: write the shape now, import the schema when it lands), PAP-42 service-container workflow (soft), PAP-25 Coolify for the cache server.
* Consumers: PAP-80, PAP-81, PAP-82, PAP-87, PAP-122, PAP-217, PAP-64, PAP-73.

**Definition of done**

* Green run on a PR touching `packages/ui` under 3 minutes warm and 6 minutes cold; timings in the PR.
* Seeded failures (type error, lint error, failing test, bad commit message, drifted generated file) each produce an inline annotation and a red status; links.
* Turbo cache hit rate visible; cache server deployed and documented in `ops/README.md`.
* Same workflow runs green on the Forgejo runner (link).
* `gate1.json` validates against `packages/contracts`; `docs/quality/gates.md` documents it; changelog entry; Linear comment with green, red and timing links.

**Test plan**

* Workflow: the five seeded failures as separate commits on a sandbox branch; docs-only PR skips build and test; fork PR runs without secrets.
* Unit: `gate1.json` writer against fixtures; JUnit-to-annotation parser.
* Cache: two consecutive runs, second reports hits; cache server unreachable falls back with a warning, not a failure.
* Determinism: `TZ` and `LANG` asserted inside a test.

**Demo**

Open a green PR run: the job summary shows five jobs with durations under 3 minutes and the `web-dist` artifact; then open the seeded red run and click an inline lint annotation. Under one minute.

**Edge cases**

* Lockfile drift: `--frozen-lockfile` fails with a clear message.
* Merge commits in range: skipped by commitlint.
* 200-commit PR: last 50 plus title.
* Cache server down: local cache, warning only.

**Dependencies**

PAP-13 (hard). Soft: PAP-46, PAP-42, PAP-25, PAP-239.

**Agent**

Sentinel with Forge (Ops Runner) deploying the cache server. Reviewed by Forge and Atlas (Merger).

**Size**

M.
"""

DESCRIPTIONS["PAP-79"] = """**Goal**

Write the shared vocabulary for judging work: a severity taxonomy, per-domain review checklists with IDs, and a structured finding format used by the three reviewer agents, the vision inspector, the edge-case hunter, the a11y audit and Justin, so a "blocker" means the same thing everywhere and findings can be counted, trended and turned into gate decisions automatically.

**Scope**

* In: `docs/quality/rubrics/` with `severity.md`, `correctness.md`, `security.md`, `spec-conformance.md`, `visual.md`, `accessibility.md`, `performance.md`, `docs-and-changelog.md`, `agent-behaviour.md`, `README.md`; the `Finding` schema (authored here, homed in `packages/contracts` by PAP-239); the calibration set of 15 cases; the Markdown rendering template; `pnpm rubrics:calibrate`.
* Out: the agents (PAP-81), posting tooling, performance thresholds (PAP-87), the other artifact schemas (PAP-239).

**Spec**

* Severity: `S0 blocker` (data loss, security, broken build, access-rule violation), `S1 major` (user-visible bug, missing declared state, serious a11y), `S2 minor`, `S3 nit`, plus kinds `question` and `praise`. Gate rule: any S0 blocks; more than 3 S1 blocks; S2 and S3 never block. Confidence under 0.5 posts as `question`.
* Checklist items `RUB-<DOMAIN>-<nn>` with a one-line test ("Can I construct an input that…"), typical severity, how to verify, false-positive notes; each rubric file has purpose, scope, examples of S0/S1/S2 and "what this does not cover".
* Domains: correctness (types vs runtime, null and empty, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, cleanup, meaningful tests); security (authz per procedure, RLS context, validation, secrets, SSRF, injection, uploads, rate limits, dependency risk, sensitive logging; cites PAP-219 `SEC-*` controls); spec-conformance (spec exists, components match `registry.json`, access implemented, all declared states rendered, events wired, spec edge cases tested, `rules.json` respected); visual (overflow, clipping, truncation without tooltip, 4 px misalignment, contrast, spacing, target size, theme leaks); accessibility, performance, docs, agent behaviour.
* `Finding = { id, reviewer, rubricId, severity, title, body, file?, line?, endLine?, suggestion?, evidence: { kind: 'code' | 'screenshot' | 'video' | 'log', ref }[], confidence, autofixable, waiver? }`; `id = sha1(reviewer + rubricId + file + normalizedTitle)[:10]`.
* Rendering template: header with counts by severity, findings grouped by severity with file link, rubric ID and suggestion diff block.

**Interface contract**

* Provides: rubric IDs (`RUB-*`) and severity names used by PAP-80 mapping, PAP-73 gate, PAP-84 vision, PAP-85 oracles, PAP-244 and PAP-245 prompts; `Finding` schema source (`docs/quality/rubrics/finding.schema.json` plus the TypeScript moved into `packages/contracts/src/finding.ts` when PAP-239 lands); calibration set format `calibration/<case>/{input.md, expected.json}`; the review comment template; waiver shape `{ reason, approvedBy, expires }`.
* Requires: nothing. Soft: PAP-219 control ids for the security rubric.
* Consumers: PAP-81 children, PAP-84, PAP-85, PAP-89, PAP-73, PAP-76, PAP-49, PAP-110, PAP-239, PAP-241.

**Definition of done**

* Nine rubric docs plus README merged; every checklist item has an ID and verification note.
* `Finding` schema with Vitest tests and exported JSON Schema; PAP-239 comment confirms it as the canonical home.
* Calibration set of 15 cases with expected severities and rationales; `pnpm rubrics:calibrate <output.json>` prints agreement.
* Rendering template snapshot test; reviewed in comments by Iris (visual and a11y), Forge (correctness), Ledger (financial correctness note).
* Changelog entry; Linear comment linking README and schema.

**Test plan**

* Unit: schema accepts the 15 expected files and rejects a wrong severity, a confidence over 1 and a missing evidence kind; `findingId` stable under whitespace and case changes.
* Script: `rubrics:calibrate` on a fixture output reports the expected agreement number.
* Docs: every `RUB-*` referenced by the calibration cases exists; link check.

**Demo**

Open `docs/quality/rubrics/README.md`, follow the gate rule to `severity.md`, then run `pnpm rubrics:calibrate fixtures/sample-review.json` and read the agreement score and the two disagreements it lists. Under one minute.

**Edge cases**

* Finding in generated files: capped at S2, points at the generator.
* Two reviewers on the same line: both kept, highest governs; dedupe only within a reviewer.
* Not-applicable rubric: reviewers emit `n/a` so silence differs from skipped.
* Justin overrides severity: recorded as a waiver, never a silent edit.
* Third-party code: S3 with a pointer to PAP-216.

**Dependencies**

None blocking. Soft: PAP-219.

**Agent**

Sentinel writes; Quill edits. Reviewed by Atlas, Iris, Forge, Ledger.

**Size**

M.
"""

DESCRIPTIONS["PAP-80"] = """**Goal**

Catch leaked secrets, vulnerable dependencies, dangerous code patterns and unsafe images automatically on every PR and nightly on `main`, normalised into the shared finding schema, so the security reviewer starts from a clean baseline and no release ships with a known critical vulnerability.

**Scope**

* In: `.github/workflows/security.yml` with jobs `secrets` (gitleaks 8.x), `deps` (`osv-scanner` on `pnpm-lock.yaml` and `Cargo.lock`, `pnpm audit --prod`), `sast` (Semgrep with `p/typescript`, `p/react`, `p/nodejs`, `p/owasp-top-ten`, `p/secrets` plus local rules), `containers` (Trivy on compose images), `licenses` hook for PAP-211, aggregating `gate-security`; SARIF merge into `reports/security.json`; waiver file with expiry; SBOM; nightly full-history run with Linear issues.
* Out: runtime WAF, penetration testing, secret rotation automation (PAP-219 runbook), posture management, upgrades (PAP-217).

**Spec**

* Local Semgrep rules in `ops/security/semgrep/`, each annotated with the PAP-219 control it enforces: oRPC procedure without `authorize` (`SEC-API-01`), Drizzle query outside `withTenant` (`SEC-DB-02`), `dangerouslySetInnerHTML` without `dompurify`, `eval`/`new Function`, Tauri capability widening, hard-coded imagine-os tokens, `/__test` routes reachable without `PAPEROS_TEST_MODE` (PAP-240).
* Severity mapping to PAP-79: gitleaks hit S0; OSV critical/high with fix S0, without fix S1 plus waiver; Semgrep `ERROR` S1 (S0 for authz and tenant rules), `WARNING` S2; Trivy critical S0, high S1.
* `ops/security/merge-sarif.ts` produces `reports/security.json` as `GateReport<'security'>` (PAP-239) with `data.tools: [{ name, version, findings }]`; SARIF to GitHub code scanning when available, artifact on Forgejo.
* Waivers `ops/security/waivers.yaml`: `{ id, tool, reason, approvedBy: 'Justin' | 'Sentinel', expires }`; expired waivers fail; Sentinel may approve S1, S0 needs Justin via Needs Justin. Suppressions `// nosemgrep: rule -- reason (expires YYYY-MM-DD)` and `gitleaks:allow` with the same expiry check.
* Nightly 03:00 UTC on `main`: full-history gitleaks, full-repo Semgrep, opens or updates one Linear issue per new S0/S1 finding via PAP-97 deduped by finding ID.
* SBOM via `@cyclonedx/cyclonedx-npm` per build; Trivy scans `postgres`, `forgejo`, `hocuspocus`, `minio`, `api` images with `--ignore-unfixed=false`. Runtime under 4 minutes; Semgrep on changed files for PRs.

**Interface contract**

* Provides: `reports/security.json`, status `gate/1-security`, waiver file schema, suppression grammar, SBOM artifact `sbom.cdx.json`, the local rule ids and their `SEC-*` mapping, "Security" section in the sticky comment.
* Requires: PAP-78 setup action, sticky comment and status pattern (hard); PAP-239 schema; PAP-219 controls (hard: rule ids reference them); PAP-211 job slot (soft); PAP-97 (soft) for nightly issues; PAP-50 runner.
* Consumers: PAP-245 security reviewer (reads `security.json` and waivers), PAP-88 certification (no open S0/S1, no expired waivers), PAP-217, PAP-89.

**Definition of done**

* Workflow green on `main`; seeded PR with a fake AWS key, `lodash@4.17.15`, a `dangerouslySetInnerHTML` misuse and an oRPC procedure without `authorize` yields four findings at the mapped severities and a red status (link).
* Expired waiver fails the job (test); active S1 waiver shows as waived.
* SBOM present; `security.json` validates against `packages/contracts`.
* Nightly dry run shows the Linear issue it would create (screenshot).
* Same workflow green on the Forgejo runner; `docs/quality/security-scans.md`; changelog entry.

**Test plan**

* Rule tests: Semgrep `--test` fixtures (positive and negative) for every local rule.
* Unit: `merge-sarif.ts` on fixture SARIF from each tool; severity mapping table; waiver expiry with a faked date.
* Workflow: seeded PR above; fork PR skips upload with a comment; missing `Cargo.lock` skips with a notice.
* Perf: PR run under 4 minutes on a warm cache.

**Demo**

Open the seeded PR's "Security" comment: four findings with severities and rule ids; click the `SEC-API-01` link to the threat model control; open `waivers.yaml` and the nightly dry-run summary. Under one minute.

**Edge cases**

* Fixture secrets: allowed only under `**/__fixtures__/**` with a documented pattern.
* Git or workspace dependencies: skipped and listed.
* Generated and vendored paths excluded from Semgrep.
* Long-unfixed vulnerability: S1 waiver with expiry plus a Linear issue, re-checked nightly.

**Dependencies**

PAP-78, PAP-219 (hard). Soft: PAP-239, PAP-211, PAP-97, PAP-50.

**Agent**

Sentinel (Security Auditor). Reviewed by Forge (Ops Runner, images) and Atlas (waiver policy).

**Size**

M.
"""

DESCRIPTIONS["PAP-81"] = """**Goal**

Build Gate 2: three Claude reviewer agents (correctness, security, spec-conformance) that run after Gate 1 on every PR, review against the shared rubrics, post one structured GitHub or Forgejo review each with inline comments, and set statuses that block merge on blockers. This replaces the human code review Justin cannot supply. Umbrella for three children.

**Children**

1. PAP-243 Review harness: SDK runner, input assembly, finding validation and posting (M) - blocks the other two.
2. PAP-244 Correctness and spec-conformance reviewer definitions (M).
3. PAP-245 Security reviewer definition and `security.json` ingestion (S).

**Scope**

* In (across children): `packages/agents/src/review/`, three reviewer definitions under `.claude/agents/reviewers/`, `review.yml` workflow, posting to both forges, idempotent re-review, cost capture, calibration.
* Out: autofix PRs, non-code artifacts, human review UI, ongoing calibration measurement (PAP-241), vision review (PAP-84).

**Spec**

Details live in the children. Cross-child rules:

* Reviewers never `APPROVE`; `REQUEST_CHANGES` on any S0 or more than 3 S1, else `COMMENT`; aggregate `gate/2-review` is the merge gate.
* All findings are `packages/contracts` `Finding`s with deterministic IDs; inline comments carry `<!-- finding:<id> -->` so re-runs update instead of duplicate.
* Tools are read-only; any write or network attempt is denied and logged as an S2 agent-behaviour finding.
* Every reviewer emits `rubricCoverage` so silence is distinguishable from a skipped check.

**Interface contract**

* Provides: `runReview()`, `ReviewerDefinition`, `postReview()`; statuses `gate/2-correctness`, `gate/2-security`, `gate/2-spec`, `gate/2-review`; `reports/review-cost.json`; label `re-review` trigger; the review comment format from PAP-79.
* Requires: PAP-78 `workflow_run` and `gate1.json`, PAP-79 rubrics and calibration set, PAP-239 schemas, PAP-80 `security.json`, PAP-48 bot identities, PAP-49 PR template fields, PAP-74 `registry.json` and PAP-76 `rules.json` (soft), PAP-107 prompt-log hook (soft).
* Consumers: PAP-85 (reuses the harness), PAP-84 (runner with image input), PAP-88 certification, PAP-241 calibration, PAP-110 evals, PAP-89.

**Definition of done**

* All three children Done.
* Integration test below green on the sandbox repo; example review links and a cost table in the Linear comment.
* `docs/quality/review-agents.md` (how to read, re-run, waive); changelog entry.

**Test plan**

Umbrella run on the sandbox repo:

* Seeded PR containing an authz bug, a null-handling bug and a missing empty state: security catches the first at S0, correctness the second at S1, spec-conformance the third at S1; a clean PR yields `COMMENT` with zero blockers and green statuses.
* Push a fix commit: fixed findings get "Resolved in <sha>", no duplicate comments, incremental diff reviewed.
* Calibration: all three reviewers at or above 0.8 agreement on the 15-case set.
* Cost: under $6 average per PR across 10 PRs; each reviewer under 6 minutes, gate under 10.
* Posting works on GitHub and on the Forgejo dev instance.

**Demo**

Open the seeded PR: three reviews, inline comments with rubric ids and suggestion diffs, red `gate/2-review`; open the clean PR beside it with green statuses and the cost line in the job summary. Under one minute.

**Edge cases**

Cross-child: PR over 10 000 lines gets one S1 "split this PR" and a spec-plus-security-only review; API outage yields `status: error` never green; a reviewer contradicting `gate1.json` must cite command output or is downgraded; Sentinel's own PRs are still reviewed.

**Dependencies**

PAP-78, PAP-79, PAP-239 (hard). Soft: PAP-80, PAP-48, PAP-49, PAP-74, PAP-76, PAP-107.

**Agent**

Sentinel (Code Reviewer and Security Auditor write their own prompts) with Atlas providing the SDK harness pattern shared with PAP-96. Reviewed by Atlas and Forge; Quill checks the spec-conformance prompt.

**Size**

L, split into 3 children (M, M, S).
"""

DESCRIPTIONS["PAP-82"] = """**Goal**

Build Gate 3's screenshot suite: Playwright renders every `visual`-tagged story and every key page across seven widths and three themes, compares against LFS baselines, fails the PR on unexpected change and makes intended change a one-label update. The images feed PAP-83 and PAP-84. Umbrella for three children; stories ship in P0 without authentication, pages follow once PAP-240 provides seeding and login.

**Children**

1. PAP-246 Playwright project matrix, deterministic fixtures and Storybook story capture (M) - blocks the other two.
2. PAP-247 Page capture with authenticated audiences and baseline update workflow (M) - also blocked by PAP-240.
3. PAP-248 Contact-sheet reporter, 4-way sharding and the `visual.json` artifact (S).

**Scope**

* In (across children): `apps/web/playwright.visual.config.ts` and projects, determinism fixtures, story and page capture, LFS baselines, `update-baselines` workflow, reporter, sharding, `visual.json`, Pages report upload, sticky comment, status.
* Out: video (PAP-83), vision inspection (PAP-84), functional e2e (PAP-86), seeding and login (PAP-240).

**Spec**

Details live in the children. Cross-child rules:

* Project names `xs-320, sm-375, md-768, lg-1024, xl-1280, 2xl-1536, 3xl-1920` are the canonical width keys used by PAP-83, PAP-84, PAP-87 and PAP-89.
* Screenshot IDs `story:<storyId>` and `page:<routeId>`; baselines under `__screenshots__/<project>/<theme>/<id>.png` in LFS; thresholds `maxDiffPixelRatio: 0.002`, `threshold: 0.2`.
* Runs only inside the pinned Playwright Docker image against `web-dist` from Gate 1 and `storybook-static`; never rebuilds.
* Baseline changes land only through the `update-baselines` label workflow with the bot signature.

**Interface contract**

* Provides: `visualTest` fixture, project names, ID grammar, `reports/visual.json` (`GateReport<'visual'>` with `data.images`), contact sheets, Pages URLs `/pr/<n>/visual/`, status `gate/3-visual`, scripts `pnpm shots`, `shots:update`, `shots:report`, spec keys `screenshot: true | false | fullScroll` and `screenshot.as`, story tag `visual`.
* Requires: PAP-78 `web-dist` and comment action, PAP-14 `breakpoints.json`, PAP-69 `index.json`, PAP-240 seed and `loginAs`, PAP-239 schema, PAP-48 bot, PAP-45 LFS, PAP-15 hosting (soft), PAP-75 theme attribute (soft).
* Consumers: PAP-83, PAP-84, PAP-87, PAP-88, PAP-89, PAP-137, PAP-64 UI suite, PAP-62 and PAP-63 DoDs.

**Definition of done**

* All three children Done.
* Integration run below green; links to the red run, the label-update run and the green run in the Linear comment.
* `docs/quality/visual-testing.md` complete; changelog entry.

**Test plan**

Umbrella run on a PR:

* Suite covers all `visual` stories and all example, portal and console pages at 21 combinations across 4 shards in under 8 minutes; sticky comment shows contact sheets.
* Seeded 2 px padding change on Button and a heading colour change on `/portal` fail with visible diffs; `update-baselines` label commits new baselines and the gate turns green.
* Flake check: 10 consecutive `main` runs with zero diffs.
* `visual.json` validates and a PAP-84 stub lists the diff images from it.
* Direct baseline push without the bot signature fails Gate 1.

**Demo**

Open the PR "Visual" comment, click the `/portal` contact sheet (7 widths × 3 themes, one red badge), then the Pages report; add the `update-baselines` label and watch the bot commit land. Under two minutes of watching.

**Edge cases**

Cross-child: fonts differ outside Docker (warning, informational); renamed story or route leaves a `missing` baseline that must be deleted explicitly; LFS conflicts between two baseline PRs are resolved by rerunning the label workflow after rebase; count cap 600 images.

**Dependencies**

PAP-78, PAP-14, PAP-239 (hard); PAP-240 (hard for PAP-247 only). Soft: PAP-69, PAP-15, PAP-48, PAP-45, PAP-75.

**Agent**

Sentinel (Visual Inspector) builds all children; Iris consults on story tagging. Reviewed by Forge (CI, LFS, image) and Iris.

**Size**

L, split into 3 children (M, M, S).
"""

DESCRIPTIONS["PAP-83"] = """**Goal**

Record short video replays of the critical user flows on every PR at each responsive width, with step captions and a contact sheet, and attach them to the PR and the Linear issue so reviewer agents, the vision inspector and Justin can watch a change instead of reading it.

**Scope**

* In: flow definitions `specs/flows/*.flow.yaml` with a Zod schema, Playwright runner `apps/web/e2e/flows/` recording per flow per width, ffmpeg post-processing (MP4, captions, poster, contact sheet), `reports/videos.json`, MinIO upload with signed URLs, sticky comment section, Linear comment, status `gate/3-video`.
* Out: production session replay, frame diffing, native mobile recordings, audio.

**Spec**

* Flow YAML `{ id, title, audience, critical: true, steps: [{ action: goto | click | fill | press | expect | wait, target, value?, note }], at?: { sm: [extra steps] } }`, max 40 steps; `target` resolves via `getByTestId` or `getByRole(name)`; ambiguous targets fail fast listing candidates. Starter flows: sign-in, create workspace, switch tenant, create and edit a record, open inspector and detach panel (desktop only), theme switch.
* Runner: `recordVideo` at `{ width, height: 900 }`, `slowMo: 150`, caption overlay `data-testid="flow-caption"` via `addInitScript`; default widths `sm-375, md-768, xl-1280, 3xl-1920`, all seven plus dark theme on `main` nightly; seeds and logs in through PAP-240 per `audience`.
* Post-processing `ops/ci/video/`: ffmpeg (pinned in the Playwright image) WebM to MP4 H.264 720p CRF 28, burned step captions with timestamps, poster frame, 3×4 contact sheet PNG; `reports/videos.json` as `GateReport<'videos'>` with `data.videos: [{ flowId, width, theme, mp4, poster, sheet, durationMs, steps: [{ note, atMs }] }]`.
* Storage: run artifacts plus MinIO `qa-videos/<repo>/<pr>/<sha>/` with 30-day lifecycle (180 days for `main` nightly critical flows); signed URLs valid 30 days; comment notes expiry.
* Budget: 6 flows × 4 widths under 6 minutes across 2 shards; per-flow timeout 90 s. `pnpm flows`, `pnpm flows:record <flowId>`.

**Interface contract**

* Provides: `FlowSpec` schema (`packages/spec/src/flows.ts`), `reports/videos.json`, contact sheets, poster URLs, status `gate/3-video`, "Replays" sticky-comment section, Linear comment format, `flow-caption` overlay.
* Requires: PAP-246 projects and fixtures, PAP-240 seed and `loginAs`, PAP-239 schema, PAP-37 or compose MinIO, PAP-97 Linear comments (soft), PAP-78 comment action.
* Consumers: PAP-84 (contact sheets), PAP-89 section 5, PAP-137 annotations, PAP-72 (motion evidence), PAP-29 drill recording.

**Definition of done**

* Six flows recorded at four widths on a PR; sticky comment shows posters and links; Linear comment posted (links).
* Nightly `main` covers seven widths and both themes; `videos.json` validates.
* Seeded broken flow (renamed button) fails `gate/3-video` and the MP4 shows the failing step (link).
* Videos play in Chrome, Safari and Firefox; under 4 MB average.
* `docs/quality/flows.md`; changelog entry; Linear comment with a sample video and contact sheet.

**Test plan**

* Unit: flow schema validation (40-step cap, `at` overrides), caption timing math, contact-sheet frame sampling.
* Integration: runner on the example app for two flows at 375 and 1280 in CI; ffmpeg pipeline on a fixture WebM; MinIO unavailable falls back to artifact links.
* Visual: contact sheet snapshot for one flow.
* Cross-browser: MP4 playback smoke in the three engines (Playwright).

**Demo**

Open the PR "Replays" section, click the `switch-tenant` poster at 375 and watch the 20-second MP4 with captions; open its contact sheet. Under one minute.

**Edge cases**

* Step target inside a collapsed drawer at small widths: `at.sm` extra steps open it.
* ffmpeg missing locally: WebM with a warning.
* Flow over 60 s: split into two flows.
* Signed URL expiry in Linear: date noted; PAP-89 re-signs.

**Dependencies**

PAP-82 children (hard: PAP-246 fixtures), PAP-240 (hard). Soft: PAP-37, PAP-97, PAP-239.

**Agent**

Sentinel (Visual Inspector). Reviewed by Forge (storage, ffmpeg in the image) and Nova (flow realism).

**Size**

M.
"""

DESCRIPTIONS["PAP-84"] = """**Goal**

Turn Gate 3's pixels into review findings: a vision-capable Claude agent inspects new and changed screenshots and video contact sheets for overflow, clipping, misalignment, truncation, contrast and theme leaks, draws annotated boxes, and posts findings in the shared schema so layout defects block or get fixed without a human looking.

**Scope**

* In: `packages/agents/src/vision/inspectScreenshots()` on the PAP-243 runner with image input, prompt `.claude/agents/reviewers/visual-inspector.md`, Zod-validated per-image output, DOM metrics emitted by the visual suite, computed contrast check, `sharp` annotation renderer and findings sheet, cross-width consistency call, calibration set and `pnpm vision:calibrate`, posting, `reports/vision.json`, cost controls.
* Out: pixel diffing (PAP-82), generating fixes, accessibility tree analysis (PAP-73).

**Spec**

* Input: `reports/visual.json` and `reports/videos.json`; images with status `diff` or `new` (all on `main` nightly), each with story or route id, width, theme, the spec's layout and components sections and `rules.json` items marked `vision` (PAP-76).
* Output per image `{ findings: [{ rubricId, severity, title, body, bbox: { x, y, w, h } normalised 0-1, confidence }], layoutScore: 0-100 }` mapped to `Finding`s with `evidence: [{ kind: 'screenshot', ref }]`; deterministic IDs.
* DOM metrics: the visual suite writes `reports/dom-metrics.json` per screenshot (`scrollWidth > clientWidth`, `text-overflow: ellipsis` hits with `title` presence, elements outside viewport); DOM-confirmed findings get confidence 0.9; intentional truncation with tooltip downgrades to S3.
* Contrast is computed: sample the bbox with `sharp`, compute the ratio; below 3:1 keeps severity, otherwise downgrade to `question`.
* Cross-width: one call receives the same page at all seven widths to spot content missing at one width; identical defects across widths dedupe into one finding listing widths.
* Annotation: boxes and numbered labels in the accent colour, `<id>.annotated.png` beside originals, a composite findings sheet per PR, uploaded with the visual report.
* Cost: downscale to 1 568 px longest side, at most 60 images per PR (diffs, then new, then sample), $4 cap with a sampling notice; runs after PAP-82 via `workflow_run`, under 6 minutes.

**Interface contract**

* Provides: `reports/vision.json` (`GateReport<'vision'>` with `data.images: [{ id, layoutScore, findings }]`), annotated images and findings sheet, status `gate/3-vision`, "Visual inspection" comment section, `dom-metrics.json` shape (produced in PAP-246 fixtures, specified here).
* Requires: PAP-82 children (hard), PAP-243 runner, PAP-79 `visual.md` rubric, PAP-239 schema, PAP-83 contact sheets (soft), PAP-76 `rules.json` (soft), PAP-114 layout sections (soft).
* Consumers: PAP-88 certification, PAP-89 section 3, PAP-137 (annotations become comments), PAP-62 and PAP-63 DoDs, PAP-85 dedupe by bbox overlap.

**Definition of done**

* Runs on a PR with visual diffs and posts annotated findings whose boxes land on the real defects (comment screenshot).
* Calibration set `docs/quality/rubrics/calibration/visual/` (10 defective with known bboxes, 10 clean): precision at or above 0.85, recall at or above 0.7, numbers in the PR.
* Seeded overflow at 375 px and a low-contrast badge in dark theme are both caught at S1; a clean PR yields zero blockers.
* Cost under $4 per PR across 10 runs; tokens and image counts in the job summary.
* `docs/quality/vision-inspection.md`; changelog entry; Linear comment with example annotated images.

**Test plan**

* Unit: bbox clamping and remapping for tiled tall screenshots, dedupe across widths, contrast computation on fixture crops, DOM-metric cross-check rules.
* Calibration: `pnpm vision:calibrate` on the 20-image set.
* Integration: full run on the seeded PR; API unavailable yields `status: error`.
* Visual: annotated image snapshot for one calibration case.

**Demo**

Open the "Visual inspection" comment on the seeded PR: two annotated thumbnails with numbered boxes; click one to see the overflow box at 375; open `vision.json` for the same image. Under one minute.

**Edge cases**

* Masked volatile regions: never a finding.
* Very tall screenshots: 1 568 px tiles with overlap, bboxes remapped.
* Hallucinated bbox outside the image: clamped, confidence 0.3, posted as `question`.
* Model unavailable: `error`, listed as missing in the digest.

**Dependencies**

PAP-82 children (hard), PAP-243 (hard). Soft: PAP-83, PAP-76, PAP-79, PAP-239, PAP-114.

**Agent**

Sentinel (Visual Inspector). Reviewed by Iris (design correctness of findings) and Atlas (cost).

**Size**

M.
"""

DESCRIPTIONS["PAP-85"] = """**Goal**

Build Gate 4: an agent that reads each changed page's spec and derives adversarial scenarios (empty, huge, unicode and RTL data, invalid input, network failure, slow device, permission denied, concurrent edits, odd dates), executes them with Playwright, files structured findings and hands failures back as reproducible tests, so happy-path coverage stops being the ceiling. Umbrella for three children.

**Children**

1. PAP-249 Scenario planner from specs with fixture catalogue (M) - blocks the executor.
2. PAP-250 Playwright executor and generic oracles (M) - also blocked by PAP-240.
3. PAP-251 Findings, generated repro tests and nightly library run (S).

**Scope**

* In (across children): `packages/agents/src/edgecases/` planner, executor, oracles, report; nine scenario classes with fixtures and corpora; scenario memory; `edgecases.json`; PR matrix comment; repro PR generation; nightly library run with Linear issues.
* Out: API fuzzing, load testing (PAP-147), security exploitation (PAP-80), flake handling (PAP-90 consumes).

**Spec**

Details live in the children. Cross-child rules:

* Plans are schema-validated JSON capped at 30 scenarios per page; invalid entries are dropped and counted, never executed.
* Oracles are generic and pure; page-specific expectations come only from the spec's declared states and edge cases.
* Destructive scenarios run only against the ephemeral preview with a tenant seeded by PAP-240; never staging.
* Budget: planning under $2 and execution under 8 minutes per PR across 2 shards; overflow defers to nightly.

**Interface contract**

* Provides: `ScenarioPlan`, `SCENARIO_CLASSES`, `Oracle` interface, `planScenarios()`, `runScenarios()`, `report()`; `reports/edgecases.json` (`GateReport<'edgecases'>` with `data.matrix`), status `gate/4-edge`, "Edge cases" comment section, repro test convention `apps/web/e2e/generated/<page>/<scenarioId>.spec.ts`, nightly Linear issue template, `ops/quality/edge-scenarios.yaml` memory, corpora in `ops/quality/corpora/`.
* Requires: PAP-114 spec schema, PAP-243 runner, PAP-240 seed and `loginAs`, PAP-246 projects and DOM metrics, PAP-239 schema, PAP-79 checklist, PAP-97 webhooks (soft), PAP-48 bot (soft), PAP-84 `vision.json` for dedupe (soft).
* Consumers: PAP-88 certification, PAP-89 section 3, PAP-110 evals, PAP-90 flake input, PAP-241 escaped-defect source.

**Definition of done**

* All three children Done.
* Integration run below green; matrix screenshot and repro PR link in the Linear comment.
* `docs/quality/edge-cases.md`; changelog entry.

**Test plan**

Umbrella run on a PR touching an example page:

* At least 15 scenarios executed across six or more classes with evidence for failures; the matrix comment and `gate/4-edge` status post.
* Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) each caught by the correct oracle at the planned severity.
* Repro PR opened for the failures, passing lint and typecheck; a clean page yields zero S0/S1.
* Nightly dry run lists Linear issues it would create; planning under $2 and execution under 8 minutes.

**Demo**

Open the "Edge cases" comment on the seeded PR, click the red `data.unicode` cell, copy the `pnpm edge:run --page … --scenario …` command, run it locally and watch the emoji crash reproduce with a screenshot. Under two minutes.

**Edge cases**

Cross-child: a page without a spec gets S1 "no spec" and generic oracles only; flaky scenarios are repeated three times and only consistent failures are reported; findings overlapping PAP-84 overflow boxes above 0.6 IoU are deduped.

**Dependencies**

PAP-114, PAP-81 (PAP-243 harness) (hard); PAP-240 (hard for PAP-250). Soft: PAP-246, PAP-84, PAP-97, PAP-48, PAP-239.

**Agent**

Sentinel (Edge Case Hunter) builds all children. Reviewed by Nova (data realism), Forge (fixtures) and Atlas (budget, Linear policy).

**Size**

L, split into 3 children (M, M, S).
"""

DESCRIPTIONS["PAP-86"] = """**Goal**

Provide functional end-to-end coverage of the core platform, distinct from screenshots: sign-in with each method, organisation and workspace creation, invitation and tenant switch, record CRUD, permissions and realtime presence between two users, run on every PR against an ephemeral stack and nightly against staging.

**Scope**

* In: Playwright project `functional` (`apps/web/e2e/functional/`) with `auth`, `tenancy`, `crud`, `presence`, `permissions` specs; `@smoke` (PRs, under 5 minutes) and `@full` (nightly, plus a 375 mobile run); ephemeral backend `ops/compose/preview.yml` (Postgres, API, Hocuspocus, Mailpit); Mailpit client; WebAuthn virtual authenticator; reporter, traces and videos on failure; status `gate/3-e2e`.
* Out: visual comparison (PAP-82), load, payment flows (business-core), native Tauri e2e, seeding and login fixtures (PAP-240 owns `seed()`, `loginAs()`, `reset()`, `testUsers`; this issue consumes them).

**Spec**

* Config `apps/web/playwright.functional.config.ts`: `baseURL` from env, storage state per audience from PAP-240, `retries: 2` in CI writing retried tests to `flakes-delta.json` (PAP-90), `trace: 'on-first-retry'`, `video: 'retain-on-failure'`.
* `auth.spec.ts`: passkey via CDP `WebAuthn.enable` and `addVirtualAuthenticator({ protocol: 'ctap2', transport: 'internal', hasResidentKey: true, hasUserVerification: true, isUserVerified: true })`; magic link by polling Mailpit `GET /api/v1/messages` for `user+<uuid>@e2e.local` within 15 s; OAuth via PAP-224's test-mode mock provider; each asserts the same user id.
* `tenancy.spec.ts`: create org and workspace, invite, accept as a second context, switch, leave (PAP-58); `crud.spec.ts`: create, edit, list filter, delete, undo on the PAP-33 example entity; `permissions.spec.ts`: customer cannot reach `/console`, staff without role denied; `presence.spec.ts`: two contexts on one document, avatar and cursor appear within 3 s and vanish within 10 s of disconnect (PAP-141), agent badge when PAP-146 exists; skipped with reason until PAP-141 merges.
* Isolation: every test creates its own `e2e-<shard>-<worker>-<uuid>` tenant; `reset()` truncates only that prefix.
* `data-testid` convention `area.element[.modifier]` documented in `docs/quality/testing.md`; components accept `testId`.

**Interface contract**

* Provides: the `functional` project and tags, `docs/quality/testing.md` test-id convention (used by PAP-83 flows and PAP-64 UI suite), `ops/compose/preview.yml` reused by PAP-85, PAP-242 and PAP-253, `mailsink` client, `webauthn` fixture, status `gate/3-e2e`, JUnit and HTML reports.
* Requires: PAP-58 (hard), PAP-57 (hard), PAP-240 fixtures (hard), PAP-35 CRUD target, PAP-42 compose pieces, PAP-141 (soft), PAP-26 images for staging.
* Consumers: PAP-90 (first flake source, report shape), PAP-88 nightly and certification, PAP-64, PAP-253.

**Definition of done**

* Five specs pass on a PR against the ephemeral stack in under 5 minutes for `@smoke` (link).
* Nightly `@full` including the 375 run passes on staging (link).
* Seeded regression (broken tenant switch) fails with a trace attached (link).
* Traces and videos retained on failure and linked in the job summary.
* `docs/quality/testing.md` covers `pnpm e2e`, tags and test ids; changelog entry; Linear comment with report links.

**Test plan**

* The suite itself at 1280 (PR) and 375 (nightly).
* Infrastructure: Postgres health wait with a 60 s cap and readable failure; Mailpit out-of-order delivery matched by token; OAuth mock missing skips with reason.
* Isolation: two workers creating tenants concurrently never collide (slug includes shard and worker).
* Flake: `expect.poll` everywhere, no sleeps; three consecutive green `@smoke` runs.

**Demo**

Run `pnpm e2e --grep @smoke --headed` against `pnpm dev:preview` and watch sign-in, org creation, invitation acceptance in a second window and a tenant switch complete; open the HTML report. Under two minutes.

**Edge cases**

* Test-mode endpoints in production: impossible by PAP-240's guard and bundle check; Security Auditor verifies here too.
* Duplicate magic links: token match, not recipient match.
* Slow runners: generous timeouts via `expect.poll`.
* Presence not merged: spec skipped visibly, never silently passing.

**Dependencies**

PAP-58, PAP-57, PAP-240 (hard). Soft: PAP-35, PAP-42, PAP-141, PAP-146, PAP-26.

**Agent**

Sentinel (Code Reviewer writes tests) with Forge (Ops Runner) on the compose stack. Reviewed by Forge and Nova (presence).

**Size**

M.
"""

DESCRIPTIONS["PAP-87"] = """**Goal**

Make web speed a gate: Lighthouse CI measures LCP, TBT, CLS, performance and accessibility scores and PWA installability on key pages of every PR, `size-limit` guards JavaScript and CSS weight per route, and any regression beyond budget fails the PR with a delta against `main`. Server-side budgets live in PAP-242.

**Scope**

* In: `ops/ci/lighthouserc.json`, `ops/ci/budget.json`, workflow `perf.yml` after Gate 1 serving `web-dist` with `vite preview`, `@lhci/cli` 0.15.x with 3 runs mobile and desktop, self-hosted LHCI server via Coolify, `apps/web/.size-limit.json`, `ops/ci/perf-compare.ts`, "Performance" sticky-comment section, status `gate/1-perf`, `packages/core/src/perf/vitals.ts` runtime hook, docs.
* Out: API and database budgets (PAP-242), load testing, image CDN.

**Spec**

* Pages: `perf: true` in page specs plus defaults `/`, `/_app/dashboard`, `/_app/settings`, `/auth/sign-in`; authenticated pages use PAP-240 storage state through `puppeteerScript`.
* Budgets: mobile LCP under 2.5 s, TBT under 200 ms, CLS under 0.1, performance at or above 90, accessibility at or above 95, PWA installable on `/` (PAP-18); desktop LCP under 1.5 s; 10 percent tolerance band warns before failing; `aggregationMethod: 'median-run'`.
* Bundles: initial JS under 180 KB gzipped, per-route chunk under 120 KB, CSS under 60 KB, `@paperos/ui` Button import under 6 KB (shared with PAP-236); matched by glob and reported per route via the Vite manifest.
* Compare: `perf-compare.ts` fetches the latest `main` run per URL from the LHCI server and computes deltas; no baseline means absolute budgets only with a note; server down means absolute results and "comparison unavailable".
* Output: `reports/perf.json` as `GateReport<'perf'>` (PAP-239) with `data.web: [{ url, preset, lcp, tbt, cls, scores, budget, status }]` and `data.bundles`; PAP-242 adds `data.api` later. Severity S1 on breach, S0 if performance drops more than 10 points.
* Runtime: `web-vitals` 4.x metrics to the PAP-40 endpoint when configured, console in dev.

**Interface contract**

* Provides: `reports/perf.json` web section, status `gate/1-perf`, "Performance" comment section, LHCI server URL, `perf: true` spec key, `.size-limit.json` conventions, `reportVitals()` hook.
* Requires: PAP-78 `web-dist` and comment action (hard), PAP-239 schema, PAP-240 auth state (soft), PAP-18 installability (soft), PAP-40 sink (soft), PAP-25 Coolify for the server.
* Consumers: PAP-242 (extends the artifact and status), PAP-88 certification, PAP-89 section 3, PAP-217 (bundle impact of upgrades), PAP-62 and PAP-63 Lighthouse DoDs.

**Definition of done**

* Perf job posts the table with deltas against `main` (link); LHCI dashboard shows both runs.
* Seeded regression (300 KB library imported on the dashboard) fails `size-limit` and drops LCP; gate red; removal restores green (links).
* All default pages meet budgets on `main` at merge; numbers in the PR.
* `web-vitals` hook logs in dev and posts when configured.
* `docs/quality/performance.md`; changelog entry; Linear comment with dashboard link and table screenshot.

**Test plan**

* Unit: `perf-compare.ts` delta math and missing-baseline path; `perf.json` writer against fixtures; budget tolerance band.
* Workflow: seeded regression PR; LHCI server stopped yields absolute results only.
* Perf: job under 5 minutes; 3-run median variance under 5 percent on `main`.
* Runtime: vitals hook unit test with mocked `web-vitals`.

**Demo**

Open a PR's "Performance" section: four pages with mobile and desktop LCP, deltas and budgets, bundle table per route; click through to the LHCI report and the trend chart. Under one minute.

**Edge cases**

* Runner CPU noise: median of 3, tolerance band.
* Subpath previews: measured on local `vite preview`, Pages only informationally nightly.
* Third-party scripts: none without an ADR; `budget.json` third-party count 0.
* Chunk names change per build: glob plus manifest.

**Dependencies**

PAP-78 (hard). Soft: PAP-239, PAP-240, PAP-18, PAP-40, PAP-25.

**Agent**

Sentinel with Forge (Ops Runner) deploying the LHCI server. Reviewed by Forge and Iris (which pages matter).

**Size**

S.
"""

DESCRIPTIONS["PAP-88"] = """**Goal**

Define and automate the cadence that keeps Justin out of pull requests: nightly staging deploys of `main`, a Monday release candidate with consolidated gate evidence, and one Needs Justin issue whose `/approve` promotes to production and tags a release. Re-typed from Spec to Build per the round-2 audit and split into three children; the approval grammar comes from PAP-94, not from here.

**Children**

1. PAP-252 Release train policy document and environments config (S, Spec) - blocks the other two.
2. PAP-253 Nightly staging workflow with full gate run (M).
3. PAP-254 Release candidate cut, certification and Justin approval flow (M).

**Scope**

* In (across children): `docs/quality/release-train.md` and ADR, `ops/release/environments.yaml`, `staging-nightly.yml`, `release-candidate.yml`, `promote.yml`, `certify.ts`, release records, rollback command, queue rule, rehearsal.
* Out: digest content (PAP-89), changelog generation (PAP-133), Tauri packaging (PAP-52), the command grammar (PAP-94), runtime feature flags (app-shell gap issue).

**Spec**

Details live in the children. Cross-child rules:

* `main` is always releasable; `release/<yyyy-ww>` is cut Monday 08:00 UTC only when `main` is green and last week's RC issue is closed.
* Certification is the only path to production: every `GATE_STATUSES` entry green on the RC head, no open S0/S1, no expired waivers, `perf.json` within budget, reversible migrations or an acknowledged checkbox, fresh backup, staging `testMode: false`.
* Promotion is idempotent on the RC head SHA; failure auto-rolls back and reopens the issue.
* Rehearsals use the `rehearsal` label on the PAP team so PAP-94's queue metrics ignore them.

**Interface contract**

* Provides: `environments.yaml` schema, `ReleaseRecord` and `certification.json` (PAP-239 kinds), composite action `deployToEnvironment(name, sha)`, nightly report URLs `/nightly/<date>/`, RC issue template, webhook contract with PAP-97 (`release.approve`, `release.reject`), tags for PAP-52 and PAP-19 updater, `pnpm release:rollback`.
* Requires: PAP-81 and PAP-82 gates (hard), PAP-94 grammar (hard), PAP-26 images and Coolify (hard), PAP-89 digest, PAP-97 webhooks, PAP-86, PAP-85, PAP-87, PAP-242, PAP-30 backups, PAP-52 tags, PAP-133 notes (soft).
* Consumers: PAP-89 (trigger and inputs), PAP-52, PAP-108 handoffs, PAP-29 drill, PAP-94 (RC issues are its largest item class).

**Definition of done**

* All three children Done.
* Integration rehearsal below completed with links and screenshots in the Linear comment.
* Policy linked from CLAUDE.md and the PR template; `docs/quality/release-train.md` and ADR `0008-release-train.md` merged; changelog entry.

**Test plan**

Umbrella rehearsal:

* Three consecutive nightly staging runs with reports.
* RC cut end to end with the `rehearsal` label: branch, PR, gates, digest, Needs Justin issue; `/approve` promotes to a staging-as-production target and tags `v0.1.0-rc.1`; `/reject <reason>` on a second rehearsal reopens fixes and keeps the branch.
* `certify.ts` blocks on a seeded missing status, an expired waiver and `testMode: true`; duplicate approval webhook does not double deploy; rollback command redeploys the previous image.

**Demo**

Open the rehearsal RC issue in Needs Justin: one-line ask, gate table, digest link; comment `/approve`, watch `promote.yml` tag and deploy, and see the issue close with the release record link. Under two minutes after the comment.

**Edge cases**

Cross-child: `main` red on Monday means no cut and a comment on the previous RC; hotfixes branch from the last tag with a short Needs Justin issue; Coolify API down retries 30 minutes then fails loudly; an irreversible migration needs the digest checkbox.

**Dependencies**

PAP-81, PAP-82, PAP-94, PAP-26, PAP-242 (hard). Soft: PAP-89, PAP-97, PAP-86, PAP-85, PAP-87, PAP-30, PAP-52, PAP-133.

**Agent**

Sentinel with Atlas (Merger) on promotion and Forge (Ops Runner) on deploys. Reviewed by Atlas and Forge; Justin confirms the mechanics via the rehearsal.

**Size**

L, split into 3 children (S, M, M).
"""

DESCRIPTIONS["PAP-89"] = """**Goal**

Generate the one page Justin actually reads per release candidate: what changed in plain language, what the gates found and how it was resolved, the risks and questions needing his decision, and the screenshots and replays that let him see the product in under ten minutes. Everything else stays in the machines.

**Scope**

* In: `packages/agents/src/digest/buildDigest({ from, to, rcBranch })` collecting PRs and Linear issues, changelog, every gate artifact, waivers, open S1s, cost from PAP-98, nightly trends and calibration health; a constrained Claude summarisation step; Markdown, HTML (Pages) and Linear-body outputs; screenshot selection; citation validation.
* Out: marketing notes (PAP-192), tenant-facing changelog rendering (PAP-133), PR-level digests, the trigger (PAP-254).

**Spec**

* Inputs are all `packages/contracts` artifacts (PAP-239): `gate1.json`, `security.json`, `visual.json`, `videos.json`, `vision.json`, `edgecases.json`, `perf.json`, `certification.json`, `calibration.json`, `flakes-delta.json`, plus forge and Linear GraphQL for PRs and characters, PAP-133 changelog or `git log` fallback.
* Digest schema `digest.schema.ts`: `{ version, range: { fromSha, toSha, fromDate, toDate }, decision: { ask, approveCommand, rejectCommand, deadline }, changes: [{ project, title, prs: [{ number, url, linearKey, character }], userFacing, summary, screenshots }], quality: { gates: [{ name, status, link }], findings: { S0, S1, S2, S3, fixed, waived }, calibration, perf }, risks: [{ id, title, detail, recommendation, requiresAnswer }], replays, cost, links }`.
* Sections: 1 Decision needed (one paragraph and the two PAP-94 commands); 2 What changed (by project, user-facing first, before/after where visual diffs exist); 3 Quality evidence (gate table, findings by severity, fixed vs waived, calibration and perf health); 4 Risks and open questions (each with a recommended default and checkbox); 5 Replays (posters at 375 and 1280); 6 Cost and velocity; 7 Appendix links.
* Summarisation prompt `.claude/agents/digest-writer.md` receives only schema-shaped data and returns prose fields; every claim cites a PR or finding ID; a validator drops uncited sentences and logs them; prose under 900 words.
* Renderers: Markdown `docs/releases/<version>.md`; HTML via PAP-235's `PdfLayout`/`EmailLayout` kit when available, else a static template on PAP-66 tokens, no client JS beyond video posters, under 5 MB, published at `/releases/<version>/`; Linear body truncated to 4 000 characters with a link.
* Screenshots: pages with diffs in range at 375 and 1280, max 12; expired replay URLs re-signed.

**Interface contract**

* Provides: `buildDigest()`, `DigestSchema`, `pnpm digest --from --to --out`, `docs/releases/<version>.md`, `/releases/<version>/` page, Linear body variant consumed by PAP-254, `calibrationHealth` and `perfHealth` rendering expectations for PAP-241 and PAP-242.
* Requires: PAP-88 children (hard: trigger and inputs), PAP-239 schemas (hard), PAP-82, PAP-83, PAP-84, PAP-85, PAP-87, PAP-242, PAP-241, PAP-133, PAP-98, PAP-94, PAP-15 hosting, PAP-235 kit (all soft with fallbacks).
* Consumers: PAP-254 RC issue, PAP-94 queue, PAP-108 handoffs, PAP-192 (reads the changelog, not the digest), Justin.

**Definition of done**

* Digest for a rehearsal range with all seven sections populated from real artifacts; HTML on Pages and Markdown committed (links).
* Citation validator drops a seeded unsupported claim (test).
* Justin reads the rehearsal digest and confirms in a comment it answers what changed, is it safe, what must he decide; one adjustment round.
* Screenshots of the HTML digest at 375, 1280 and 1920 light and dark.
* Vitest for schema, renderer snapshots and length checks; `docs/quality/review-report.md`; changelog entry.

**Test plan**

* Unit: collector per artifact kind on fixtures including a missing artifact (`unknown` with re-run link); grouping of 40+ PRs; screenshot selection cap; Linear truncation.
* Prompt: validator on fixture prose with one uncited sentence; word cap.
* Integration: `pnpm digest` on the sandbox repo history; HTML size and two-screen height check at 1280.
* Visual: HTML digest at three widths × two themes.

**Demo**

Run `pnpm digest --from v0.1.0 --to release/2026-39 --out tmp/` and open the HTML: read the decision paragraph, scan the gate table, click a replay poster. Under two minutes.

**Edge cases**

* Zero user-facing changes: section 2 says so and leads with infrastructure.
* Missing artifact: `unknown`, never omitted.
* Cost unavailable: `n/a` with reason, never invented.

**Dependencies**

PAP-88 (hard), PAP-239 (hard). Soft: PAP-82, PAP-83, PAP-84, PAP-85, PAP-87, PAP-241, PAP-242, PAP-133, PAP-98, PAP-94, PAP-15, PAP-235.

**Agent**

Sentinel builds; Quill (Changelog Scribe) owns prose rules and templates. Reviewed by Atlas and, for the rehearsal, Justin.

**Size**

M.
"""

DESCRIPTIONS["PAP-90"] = """**Goal**

Stop nondeterministic tests from blocking twenty parallel agent sessions: detect flaky unit, e2e, visual, flow and edge-case tests from retry data, score them, quarantine repeat offenders automatically with a Linear issue for the owning character, keep running them out of band, and un-quarantine when they stabilise.

**Scope**

* In: `ops/quality/flakes.json` (bot-updated) plus `qa_flakes` table, collector `ops/quality/collect-flakes.ts` run at the end of every gate workflow, scoring, quarantine wrappers for Vitest and Playwright, Linear automation via PAP-97, ownership mapping, dashboard page, guardrails.
* Out: fixing the flaky tests, infrastructure flakiness (PAP-40), CI retry policy (set per gate).

**Spec**

* Test ID `<suite>::<file>::<fullTitle>`; near-identical titles (Levenshtein under 5) in the same file link histories.
* Collector inputs: Vitest JUnit/JSON (`retry`), Playwright JSON (`status: flaky`), `visual.json` diffs that vanish on rerun, `videos.json`, `edgecases.json`; each gate already writes `reports/flakes-delta.json` (PAP-239 kind `flakes-delta`); on PRs the collector comments one line ("1 flaky test detected, not blocking, tracked as FL-123") and uploads the delta; on `main` it posts to `POST /api/qa/flakes` (PAP-35) or bot-commits `flakes.json`.
* `qa_flakes (test_id, suite, env_key, first_seen, last_seen, runs, failures, retried_passes, score, state: active | quarantined | resolved, linear_key, owner, expires)`; `score = retriedPasses / runs` over the last 20 runs; candidate at `>= 0.15` for three runs; auto-quarantine after 24 h as candidate or when the same test blocks two PRs; scoring per environment key (shard, width, theme).
* Quarantine: Vitest `isQuarantined(id)` wrapper in `packages/core/src/testing/quarantine.ts`; Playwright annotations plus a `quarantine` project running quarantined tests with `retries: 0`; visual tests informational; `expires` default 14 days, extended on activity; expired entries fail the collector.
* Linear: issue `Flaky: <test id>` labelled `Bug` with evidence links, owner from `git blame` through `.mailmap` with `ops/quality/owners.yaml` overrides; template asks `test-bug` vs `product-bug` (product bugs become S1 findings); auto-close and un-quarantine under 0.05 over 30 runs.
* Guardrail: quarantine above 5 percent of a suite fails the gate "too many quarantined". Dashboard `docs/quality/flakes.md` generated; weekly top-5 in PAP-89 section 3.

**Interface contract**

* Provides: `flakes-delta.json` writer used by PAP-78, PAP-82, PAP-83, PAP-85, PAP-86; `isQuarantined()`; `quarantine` Playwright project; `qa_flakes` table and `POST /api/qa/flakes`; `owners.yaml`; `flakeSummary` for PAP-89.
* Requires: PAP-86 (hard: first real flake source and Playwright report shape), PAP-78 Vitest retry output, PAP-239 schema, PAP-97 webhooks, PAP-35 endpoint (soft: JSON commit fallback), PAP-48 bot commits.
* Consumers: PAP-88 certification (guardrail), PAP-89, PAP-110, PAP-241 (flake-vs-defect classification).

**Definition of done**

* Collector runs at the end of Gate 1, e2e, visual and flow workflows and updates the store (links).
* Seeded flaky test (30 percent random failure) is detected within 5 runs, quarantined with a Linear issue (screenshot), and the PR containing it goes green with the note.
* Removing the randomness leads to auto-resolution after a compressed run threshold (test).
* Quarantine cap test: exceeding 5 percent fails the gate with a clear message.
* `docs/quality/flakes.md` generated; changelog entry; Linear comment with the seeded issue and dashboard links.

**Test plan**

* Unit: score window math, per-environment keys, title linking, expiry, ownership resolution with overrides, cap computation.
* Integration: collector on fixture reports from each of the five formats; quarantine wrapper skips and the `quarantine` project still runs the test.
* Workflow: seeded flake on the sandbox repo end to end including Linear dry run.
* Guardrail: fixture with 6 percent quarantined fails.

**Demo**

Open the seeded PR: the one-line flake note; open the auto-created `Flaky:` Linear issue with evidence links; run `pnpm flakes:report` and read the dashboard table with scores and states. Under one minute.

**Edge cases**

* Deterministic failure on one shard or width only: scored and quarantined per environment.
* Product race condition: classified `product-bug`, escalates to S1, not quarantined.
* Bot commit racing agent PRs: only `main` runs commit.
* Deleted test: resolved with reason `deleted`.

**Dependencies**

PAP-86 (hard). Soft: PAP-78, PAP-82, PAP-83, PAP-85, PAP-239, PAP-97, PAP-35, PAP-48.

**Agent**

Sentinel (Edge Case Hunter). Reviewed by Forge (CI plumbing) and Atlas (Linear issue policy).

**Size**

M.
"""
