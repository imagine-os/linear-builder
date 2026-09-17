# New issues for the quality project: gaps and children of PAP-81, PAP-82, PAP-85, PAP-88.
P = "quality"
MS1 = "Gates 1 and 2 on every PR"
MS2 = "Visual and video gates"
MS3 = "Edge-case hunting and release trains"

GAPS = [
{
 "key": "quality/gate-artifact-contract", "project": P, "milestone": MS1, "phase": "P0", "type": "Spec",
 "surfaces": ["Developer", "Agent"], "priority": 1, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-79"], "blocks": ["PAP-80", "PAP-81", "PAP-82", "PAP-83", "PAP-84", "PAP-85", "PAP-89"],
 "title": "Specify the gate artifact contract: one schema package for gate1.json, security.json, visual.json, videos.json, vision.json, edgecases.json, finding IDs and artifact paths",
 "description": """**Goal**

Create `packages/contracts`, the one place every gate artifact shape lives, so CI jobs, the orchestrator webhooks, the release digest and the QA viewer read the same JSON. Today PAP-78, 80, 82, 83, 84, 85, 89 and 137 each define their own shape; this issue centralises them before any gate is built.

**Scope**

* In: `packages/contracts` with Zod schemas and exported JSON Schema for `gate1.json`, `security.json`, `visual.json`, `videos.json`, `vision.json`, `edgecases.json`, `perf.json`, `review-cost.json`, `flakes-delta.json`, plus the shared `Finding` (moved from PAP-79's draft location), `GateStatus`, `ArtifactRef`, `Evidence`; artifact path conventions; finding ID function; status name registry; a `validateArtifact(kind, json)` CLI used by every gate job; versioning rules.
* Out: producing the artifacts (each gate), rendering (PAP-89, PAP-137).

**Spec**

* Package layout: `src/finding.ts`, `src/gates/<kind>.ts`, `src/artifacts.ts`, `src/status.ts`, `src/index.ts`; `pnpm contracts:build` writes `schemas/*.schema.json`; drift-checked in Gate 1.
* `Finding = { id, reviewer, rubricId, severity: 'S0'|'S1'|'S2'|'S3'|'question'|'praise', title, body, file?, line?, endLine?, suggestion?, evidence: Evidence[], confidence, autofixable, waiver? }`; `findingId(reviewer, rubricId, file, title) = sha1(...)[:10]`.
* `GateReport<K> = { kind: K, version: 1, sha, pr?, startedAt, finishedAt, status: 'pass'|'fail'|'error'|'skipped', findings: Finding[], summary: string, artifacts: ArtifactRef[], data: KindSpecific }` where `KindSpecific` is per kind (for example `visual: { images: [{ id, project, theme, status, diffRatio, paths }] }`).
* `ArtifactRef = { kind: 'screenshot'|'video'|'report'|'log'|'sarif', path, url?, sha256?, expiresAt? }`; paths relative to `reports/` in the run; URL form `https://<pages>/pr/<n>/<kind>/...`.
* Status registry: `gate/1-static`, `gate/1-security`, `gate/1-perf`, `gate/2-correctness`, `gate/2-security`, `gate/2-spec`, `gate/2-review`, `gate/3-visual`, `gate/3-video`, `gate/3-vision`, `gate/3-e2e`, `gate/4-edge`; exported as a const so typos fail typecheck.
* Versioning: `version` field; breaking changes bump and keep a reader for the previous version for 30 days.

**Interface contract**

* Provides: all types above, `validateArtifact()`, `findingId()`, `GATE_STATUSES`, `artifactUrl(pr, path)`; JSON Schemas for non-TypeScript consumers (orchestrator in PAP-96 and webhooks in PAP-97).
* Requires: PAP-79 severity taxonomy and rubric IDs (the finding schema moves here; PAP-79 documents it).
* Consumers: PAP-78, 80, 81, 82, 83, 84, 85, 87, 88, 89, 90, 97, 137, PAP-110.

**Definition of done**

* Package builds; JSON Schemas generated and committed; drift check wired into Gate 1 (or `pnpm check` until PAP-78 merges).
* Fixture artifacts for every kind validate; a fixture with a wrong severity fails with a path.
* `findingId` stability test across whitespace and case changes in the title.
* PAP-78, 80, 81, 82, 84, 85, 89 each carry a comment confirming they import from `packages/contracts` (left by this issue's session).
* `docs/quality/gates.md` section "Artifacts and statuses"; changelog under "Quality".

**Test plan**

* Unit: every schema against fixtures (valid and invalid), `artifactUrl` for GitHub Pages and Forgejo hosting, status registry completeness against the docs table.
* Integration: `validateArtifact` CLI exit codes in a shell test.

**Demo**

Run `pnpm contracts:validate fixtures/visual.pass.json` (exit 0) then `fixtures/visual.bad-severity.json` (exit 1 with the path), and open `schemas/finding.schema.json`. Under one minute.

**Edge cases**

* Gate produces no findings but errored: `status: 'error'` with `summary`, never an empty pass.
* Two gates report the same finding ID: allowed; consumers dedupe by `(reviewer, id)`.
* Artifact over the Pages size limit: `url` omitted, `path` remains with a run-artifact reference.
* Forgejo-hosted PR: `artifactUrl` falls back to the run artifact link.

**Dependencies**

PAP-79 (hard). Consumers listed above.

**Agent**

Written by Sentinel with Atlas (contract owner). Reviewed by Forge (CI consumers) and Quill (digest consumer).

**Size**

S: a schema package; agreement is the work.
"""},
{
 "key": "quality/test-mode-seed", "project": P, "milestone": MS1, "phase": "P0", "type": "Build",
 "surfaces": ["Developer"], "priority": 1, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-32", "PAP-57"], "blocks": ["PAP-82", "PAP-85", "PAP-86", "PAP-87", "PAP-64"],
 "title": "Build test-mode seed and reset endpoints (`/__test/seed`, `/__test/reset`) with deterministic fixtures per audience, before Gate 3",
 "description": """**Goal**

Give every automated suite the same deterministic world: a `PAPEROS_TEST_MODE` guarded `/__test/*` API that seeds named fixture sets, mints sessions for one test user per audience and resets test tenants, so Gate 3 can screenshot authenticated pages in P0 instead of waiting for the P1 e2e issue.

**Scope**

* In: `apps/api/src/test-mode/` routes `seed`, `reset`, `login-as`, `clock`; fixture catalogue `packages/testing/fixtures/` (`minimal`, `portal`, `console`, `tables-100`, `tables-10k`, `finance`), `testUsers` per built-in audience from PAP-55, Playwright fixtures `apps/web/e2e/support/` (`seed()`, `loginAs(audience)`, `reset()`, cached storage state), build-time stripping outside test mode, docs.
* Out: production data seeding (PAP-32 owns migrations and dev seed), mail sink (PAP-42), e2e specs (PAP-86).

**Spec**

* Guard: routes registered only when `PAPEROS_TEST_MODE=1`; the production Docker build sets the flag off and a Vite define removes client helpers; a Gate 1 check greps the production bundle for `__test` and fails on a hit.
* `POST /__test/seed { fixture, tenantSlug? } -> { tenantId, users: Record<audience, { id, email }>, records }`: fixtures are TypeScript modules exporting a deterministic builder using `@faker-js/faker` with seed 42; ids are UUIDv5 from `(fixture, entity, index)` so screenshots are stable.
* `POST /__test/login-as { audience, tenantId } -> Set-Cookie` minting a Better Auth session directly through the adapter (no sign-in routes, no rate limits).
* `POST /__test/reset { tenantSlugPrefix = 'e2e-' }` truncates tenants matching the prefix in dependency order; refuses non-prefixed slugs.
* `POST /__test/clock { now }` pins server time for the request context (jobs, `RelativeTime`).
* Playwright: `loginAs('staff-support')` caches storage state per audience per worker; `seed('portal')` once per project.

**Interface contract**

* Provides: routes above; `testUsers` map keyed by `AudienceId`; fixtures `FixtureName`; Playwright fixtures `seed`, `loginAs`, `reset`, `clock`; `PAPEROS_TEST_MODE` env contract.
* Requires: PAP-32 schema and migrations, PAP-57 server child (session minting via adapter), PAP-55 audience ids, PAP-33 core entities.
* Consumers: PAP-82, PAP-83, PAP-84, PAP-85, PAP-86, PAP-87, PAP-64, PAP-110.

**Definition of done**

* `seed('portal')` twice yields identical ids and row counts (test); `reset` removes only `e2e-` tenants.
* `loginAs` for all twelve built-in audiences returns a session whose principal matches that audience and no narrower one (`matches` check).
* Production bundle check passes; a seeded leak of `__test` fails it.
* Playwright smoke: log in as customer, open `/portal`, screenshot at 375 and 1280 in CI.
* `docs/quality/testing.md` section "Test mode"; changelog under "Quality".

**Test plan**

* Unit: fixture determinism, UUIDv5 ids, reset prefix guard.
* Integration: routes absent when the flag is off (404), present when on; `login-as` cookie works against a protected procedure.
* Security: Sentinel Security Auditor verifies the guard and the build check.

**Demo**

`PAPEROS_TEST_MODE=1 pnpm dev`, then `curl -X POST :3000/__test/seed -d '{"fixture":"portal"}'`, `curl -c c.txt -X POST :3000/__test/login-as -d '{"audience":"customer-pro"}'`, open `/portal` with that cookie and see Ada's seeded dashboard. Under two minutes.

**Edge cases**

* Two shards seeding the same fixture: tenant slug includes shard and worker index.
* Fixture references a module not installed (finance before PAP-175): fixture skipped with a clear message.
* Clock pinned and forgotten: reset on `reset()` and at request end.
* Test mode accidentally on in staging: `/healthz` reports `testMode: true` and the release certification (PAP-88) blocks.

**Dependencies**

PAP-32, PAP-57 (hard; the server child suffices). Soft: PAP-33, PAP-55, PAP-42.

**Agent**

Built by Sentinel (Code Reviewer sub-agent) with Forge on the session minting. Reviewed by Forge and Sentinel Security Auditor.

**Size**

M: a handful of routes and fixtures; determinism and the guard are what matter.
"""},
{
 "key": "quality/gate2-calibration", "project": P, "milestone": MS2, "phase": "P1", "type": "Review",
 "surfaces": ["Agent"], "priority": 1, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-81"], "blocks": [],
 "title": "Run Gate 2 calibration and false-negative tracking: weekly manual spot check of five verdicts, precision and recall trend, reviewer prompt tuning loop",
 "description": """**Goal**

Measure the thing that replaced human code review: each week, sample five Gate 2 verdicts, have a second independent reviewer session judge them blind, record precision and recall against bugs found later (production incidents, Gate 4 findings, reverts), trend it, and tune reviewer prompts when agreement drops. Without this, the miss rate of PAP-81 is never known.

**Scope**

* In: `ops/quality/calibration/` with the weekly sampler, the blind re-review runner (a separate Sentinel session with a different prompt and no access to the original verdict), the escaped-defect linker (maps reverts, hotfixes, S0/S1 findings from later gates and incidents back to the PR that introduced them), metrics store, weekly report comment, prompt tuning procedure and a Needs Justin escalation when precision or recall falls under threshold twice.
* Out: the reviewers (PAP-81), eval harness for other characters (PAP-110; this issue feeds it).

**Spec**

* Sampler: every Monday pick 5 PRs merged in the last 7 days weighted toward risky paths (auth, permissions, ledger, migrations); store `ops/quality/calibration/samples/<yyyy-ww>.json`.
* Blind re-review: `pnpm review:blind --pr N` runs the correctness and security reviewers with `mode: 'audit'`, a stricter prompt and `maxTurns: 60`, output in the contracts `Finding` shape; a diff script classifies each original finding as `confirmed | disputed` and each new finding as `missed`.
* Escaped defects: script scans conventional commits `fix:` and `revert:`, hotfix labels, Gate 4 S0/S1 findings and incident records for `Introduced-By: <sha>` trailers or `git blame` of the fix hunk, then attributes to the original PR; weekly recall = caught / (caught + escaped).
* Metrics: `qa_calibration (week, reviewer, sampled, confirmed, disputed, missed, escaped, precision, recall, cost)`; rendered into `docs/quality/calibration.md` and PAP-89 section 3.
* Thresholds: precision 0.8, recall 0.7; two consecutive misses open a Needs Justin item with the failing examples and a proposed prompt change; prompt changes go through PAP-110 golden tasks before merge.

**Interface contract**

* Provides: `qa_calibration` table and `calibration.json` weekly artifact (contracts package kind `calibration`), `Introduced-By:` trailer convention for fixes, `calibrationHealth` consumed by PAP-89.
* Requires: PAP-81 reviewers and `runReview()`, `packages/contracts`, PAP-52 commit conventions, PAP-97 webhooks for the weekly comment.

**Definition of done**

* Three weekly cycles run (rehearsed on compressed history if needed) with reports committed and the digest section populated.
* Seeded escaped defect (a revert with `Introduced-By`) is attributed to the right PR and lowers recall (test).
* Blind re-review disputes at least one seeded false positive in the calibration set.
* Justin reads one weekly report and confirms the format in a comment.
* `docs/quality/calibration.md`; changelog under "Quality".

**Test plan**

* Unit: sampler weighting, attribution from trailers and blame, metric math.
* Integration: blind re-review against the PAP-79 15-case set reproduces expected severities within tolerance.
* Manual: one weekly run reviewed by Atlas.

**Demo**

Run `pnpm calibration:week --dry` and open the generated Markdown: five sampled PRs, confirmed and disputed counts, one escaped defect with its link, and the trend line for the last three weeks. Under two minutes.

**Edge cases**

* Fewer than five PRs merged: sample all, mark the week low-confidence.
* Escaped defect spans several PRs: attributed fractionally, documented.
* Blind reviewer costs more than budget: cap at $10 per week, sample fewer.
* Reviewer prompt changed mid-week: metrics tagged with prompt version.

**Dependencies**

PAP-81 (hard). Soft: PAP-89, PAP-110, PAP-97, PAP-52.

**Agent**

Run by Sentinel (a dedicated Calibration Auditor sub-agent, separate from the reviewers). Reviewed by Atlas; Justin sees the weekly summary.

**Size**

S: scripts around existing reviewers; the discipline of running it is the deliverable.
"""},
{
 "key": "quality/api-perf-budgets", "project": P, "milestone": MS3, "phase": "P1", "type": "Infra",
 "surfaces": ["Developer"], "priority": 3, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-87", "PAP-35"], "blocks": ["PAP-88"],
 "title": "Enforce API and database performance budgets: k6 smoke per release candidate, p95 per procedure, slow-query gate, `apps/api` image size",
 "description": """**Goal**

Give the server the same discipline PAP-87 gives the web bundle: a k6 smoke run against every release candidate with p95 budgets per oRPC procedure, a slow-query gate from Postgres statistics, and an `apps/api` image-size budget, all wired into the release certification so an API regression cannot ship.

**Scope**

* In: `ops/perf/k6/` scenarios generated from the oRPC procedure registry (read-heavy list, detail, mutation, search) with seeded data via test mode, `ops/perf/budgets.yaml` (p95 and error-rate per procedure class), `perf.json` artifact in the contracts shape, slow-query extraction from `pg_stat_statements` on staging after the run, `apps/api` image size check with `dive`-style layer report, nightly trend in the LHCI-style SQLite store or Postgres `qa_perf`, release certification hook.
* Out: full load testing (PAP-147), web budgets (PAP-87), APM dashboards (PAP-40 provides the data).

**Spec**

* k6 1.x scripts read `procedures.json` exported by PAP-35 (`pnpm api:procedures`) and run 3-minute smoke at 20 virtual users against the RC on staging after PAP-88 deploys it; auth via test-mode `login-as`.
* Budgets: `list.*` p95 150 ms, `get.*` 80 ms, `mutate.*` 250 ms, `search.*` 300 ms, error rate under 0.5 percent; overrides per procedure with a reason and expiry.
* Slow queries: after the run, `SELECT ... FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20` compared to `main`'s last run; any query over 200 ms mean or a 50 percent regression is an S1 finding with the normalised SQL.
* Image: `apps/api` image under 250 MB compressed; report of top 10 layers.
* Output: `reports/perf.json` `{ procedures: [{ name, p50, p95, errorRate, budget, status }], slowQueries, image }` plus a Markdown summary posted on the RC PR; status `gate/1-perf` (server section).

**Interface contract**

* Provides: `perf.json` kind in `packages/contracts`, `ops/perf/budgets.yaml` schema, `perfHealth` summary for PAP-89 section 3, certification input `perf` for PAP-88 `certify.ts`.
* Requires: PAP-35 procedure registry, PAP-87 status and comment pattern, test-mode seed and `login-as`, PAP-40 `pg_stat_statements`, PAP-88 RC deploy hook.

**Definition of done**

* Smoke runs against a rehearsal RC and posts the table with budgets (link); `certify.ts` reads the artifact.
* Seeded regression (N+1 in a list procedure) breaches p95 and appears in slow queries; gate red; fix restores green (links).
* Image budget check fails on a seeded 300 MB layer.
* Nightly trend for 3 nights stored; `docs/quality/performance.md` gains a server section; changelog under "Quality".

**Test plan**

* Unit: budget matching, regression math, artifact schema.
* Integration: k6 run against the ephemeral compose stack in CI with reduced VUs (informational on PRs).
* Release: full smoke on staging, blocking.

**Demo**

Run `pnpm perf:smoke --target staging --duration 60s` and open the generated Markdown: procedures with p95 against budget, two slow queries with SQL, image size. Under two minutes.

**Edge cases**

* Staging cold cache: 30-second warm-up excluded from percentiles.
* Procedure added without a budget class: defaults to `mutate.*` budget and warns.
* `pg_stat_statements` disabled: gate posts `unknown` for slow queries, still enforces p95.
* k6 runner network jitter: compare against `main` p95 of the same night, not absolute only.

**Dependencies**

PAP-87, PAP-35 (hard). Soft: PAP-40, PAP-88, test-mode seed issue.

**Agent**

Built by Sentinel with Forge (Ops Runner). Reviewed by Forge and Nova (query realism).

**Size**

S: k6 and `pg_stat_statements` are mature; the budget file and certification hook are small.
"""},
]

CHILDREN = {
"PAP-81": [
{
 "key": "quality/review-agents/harness", "type": "Build", "size": "M",
 "title": "Review harness: SDK runner, input assembly, finding validation and posting",
 "description": """**Goal**

Build the engine the three reviewers run on: a Claude Agent SDK runner with read-only tools, PR context assembly under a token budget, finding validation against `packages/contracts`, idempotent posting to GitHub and Forgejo, and cost capture.

**Scope**

* In: `packages/agents/src/review/runReview()`, context assembler, `postReview()` for both forges, status setter, cost and prompt-log capture, `review.yml` workflow skeleton, re-review incremental mode.
* Out: reviewer prompts (siblings), rubrics (PAP-79).

**Spec**

* `runReview({ pr, reviewer, cwd }) => GateReport<'review'>` using `query({ prompt, options: { model: 'claude-fable-5-1', systemPrompt, allowedTools: ['Read','Grep','Glob','Bash'], permissionMode: 'bypassPermissions', cwd, maxTurns: 40 } })` with Bash allowlisted to `git diff`, `pnpm test --filter`, `pnpm typecheck`; final message must parse as `{ findings, rubricCoverage, summary }`, one retry with the parse error appended.
* Context: diff, changed files with 40 lines of context, PR body, Linear issue text, referenced `page.spec.yaml`, `gate1.json`, `security.json`, `registry.json`, `rules.json`; cap 150k tokens, priority order documented, omissions logged; over 3 000 changed lines split by package; over 10 000 post S1 "PR too large".
* Posting: `@octokit/rest` and the Gitea-compatible API; one review per reviewer, event `REQUEST_CHANGES` if any S0 or more than 3 S1 else `COMMENT`; inline comments carry `<!-- finding:<id> -->`; re-runs update in place; resolved findings get "Resolved in <sha>".
* Statuses via contracts `GATE_STATUSES`; cost to `reports/review-cost.json` and the prompt log hook (PAP-107) when present.

**Interface contract**

* Provides: `runReview()`, `assembleContext()`, `postReview()`, `ReviewerDefinition` type `{ name, promptPath, rubricIds, statusName }`, workflow `review.yml`.
* Requires: `packages/contracts` (Finding, GateReport, statuses), PAP-78 `gate1.json` and `workflow_run` trigger, PAP-48 bot identities, PAP-49 PR template fields.
* Consumers: sibling reviewers, PAP-84 (reuses runner with image input), PAP-85, PAP-110.

**Definition of done**

* Runner executes a stub reviewer on a real PR and posts a review with one inline comment and a status (links).
* Re-push updates the same comment and resolves a fixed finding (screenshot).
* Tool allowlist test: a prompt that tries `curl` is denied and logged as an S2 agent-behaviour finding.
* Context budget test: a 200-file PR logs omitted files and stays under 150k tokens.
* Posting works on Forgejo dev instance (link).

**Test plan**

* Unit: context prioritisation, JSON parse retry, event selection rules, comment idempotency keys.
* Integration: mocked SDK stream to end-to-end post on a sandbox repo.
* Cost: 10 stub runs under $0.50 each.

**Demo**

`pnpm review:run --pr 12 --reviewer stub` against the sandbox repo, then open the PR: one review, one inline comment, `gate/2-review` status. Under two minutes.

**Edge cases**

* API outage: backoff then `status: error`, never green.
* Binary files in diff: skipped with a note.
* PR from a fork without secrets: review skipped with a comment.

**Dependencies**

PAP-78, PAP-79, `packages/contracts` (hard). Blocks the two sibling children.

**Agent**

Built by Sentinel with Atlas (SDK harness pattern shared with PAP-96). Reviewed by Forge.

**Size**

M.
"""},
{
 "key": "quality/review-agents/correctness-spec", "type": "Build", "size": "M",
 "title": "Correctness and spec-conformance reviewer definitions",
 "description": """**Goal**

Write and calibrate the two reviewers that judge whether the code works and whether it matches its page spec, each embedding its rubric and proving itself on seeded bugs and the calibration set.

**Scope**

* In: `.claude/agents/reviewers/correctness.md` and `spec-conformance.md` (Sentinel sub-characters), rubric embedding from PAP-79 `correctness.md` and `spec-conformance.md`, spec resolution from changed routes, seeded-bug fixtures, calibration run, docs.
* Out: harness (sibling), security reviewer (sibling).

**Spec**

* Correctness prompt: checks types versus runtime, null and empty handling, error paths, async ordering, idempotency, transactions, timezone and locale, pagination, cleanup, test presence and meaning; must run `pnpm test --filter <pkg>` for changed packages and cite output for any claim about tests.
* Spec-conformance prompt: resolves specs from changed route files and PR body; checks page has a spec, components match `registry.json` (PAP-74), access section implemented (PAP-59 adapter output), all declared states rendered, events wired, spec edge cases have tests, `rules.json` respected (PAP-76); missing Linear link is S1.
* Both output `rubricCoverage` with `checked | n/a` per rubric ID; confidence under 0.5 becomes `question`; `autofixable` findings include a suggestion diff.
* Seeded fixtures under `ops/quality/seeded-prs/`: null-handling bug, missing empty state, off-by-one pagination, unwired event.

**Interface contract**

* Provides: two `ReviewerDefinition`s registered with the harness; rubric coverage report shape.
* Requires: sibling harness; PAP-79 rubrics and calibration set; PAP-74 `registry.json`; PAP-76 `rules.json` (soft, skip when absent).

**Definition of done**

* Seeded null-handling and pagination bugs caught at S1 by correctness; seeded missing empty state and unwired event caught by spec-conformance; clean PR yields zero blockers.
* Calibration agreement at or above 0.8 for both on the 15-case set (numbers in PR).
* Cost per reviewer under $2 average across 10 PRs.
* `docs/quality/review-agents.md` sections for both reviewers.

**Test plan**

* Integration: seeded PRs through the harness in CI (nightly, mocked SDK on PRs).
* Calibration: `pnpm review:calibrate --reviewer correctness`.
* Regression: prompt changes must keep agreement above threshold (PAP-110 later).

**Demo**

Open the seeded "missing empty state" PR in the sandbox repo and read the spec-conformance review: the finding cites the spec line and `registry.json` entry. Under one minute.

**Edge cases**

* Spec absent: S1 "no spec" and generic review.
* Tests fail in Gate 1 already: reviewer references `gate1.json`, does not re-run.
* Generated files changed: capped at S2 pointing to the generator.

**Dependencies**

Sibling harness child (hard). Soft: PAP-74, PAP-76.

**Agent**

Built by Sentinel (Code Reviewer sub-agent); Quill checks the spec-conformance prompt. Reviewed by Atlas.

**Size**

M.
"""},
{
 "key": "quality/review-agents/security", "type": "Build", "size": "S",
 "title": "Security reviewer definition and security.json ingestion",
 "description": """**Goal**

Write and calibrate the security reviewer: it reads PAP-80's `security.json`, checks the threat model controls, hunts authorisation and tenant-isolation mistakes the scanners cannot see, and respects waivers.

**Scope**

* In: `.claude/agents/reviewers/security.md` embedding PAP-79 `security.md` and the control ids from the threat model (`controls.yaml`), `security.json` ingestion so scanner findings are referenced not duplicated, waiver awareness (`ops/security/waivers.yaml`), seeded authz bug fixture, calibration, cost report.
* Out: scanners (PAP-80), harness (sibling).

**Spec**

* Checks: `authorize()` on every new oRPC procedure, `withTenant` before queries, RLS session variables, input validation, secrets in code or logs, SSRF and injection, file uploads, rate limits, dependency risk from `security.json`, sensitive logging; each finding cites a rubric ID and, where applicable, a `SEC-*` control.
* Ingestion: scanner findings appear in the review as a summary table with links, marked `from: scanner`; the reviewer adds findings only for what scanners missed; waived findings show the waiver expiry.
* Severity: authz and tenant leaks S0; unvalidated input on mutating routes S1.

**Interface contract**

* Provides: `ReviewerDefinition` for security; `securitySummary` block consumed by PAP-89.
* Requires: sibling harness; PAP-80 `security.json`; threat model `controls.yaml`; PAP-79 rubric.

**Definition of done**

* Seeded oRPC procedure without `authorize` and a seeded cross-tenant query are caught at S0; a waived OSV finding is shown as waived, not blocking.
* Calibration agreement at or above 0.8 on the security cases.
* Cost under $2 average per PR across 10 PRs.
* Docs section "Security reviewer".

**Test plan**

* Integration: seeded PRs through the harness; waiver expiry path.
* Calibration: `pnpm review:calibrate --reviewer security`.

**Demo**

Open the seeded "missing authorize" PR: the review shows S0 with the procedure line, the `SEC-API-01` control and a suggestion diff adding the middleware. Under one minute.

**Edge cases**

* `security.json` missing (scanner errored): reviewer posts S1 "scanner results missing" and continues.
* False positive from Semgrep: reviewer may recommend a `nosemgrep` with expiry, never approve silently.

**Dependencies**

Sibling harness child (hard). Soft: PAP-80, threat model issue.

**Agent**

Built by Sentinel (Security Auditor sub-agent). Reviewed by Atlas.

**Size**

S.
"""},
],
"PAP-82": [
{
 "key": "quality/playwright-matrix/projects-fixtures-stories", "type": "Build", "size": "M",
 "title": "Playwright project matrix, deterministic fixtures and Storybook story capture",
 "description": """**Goal**

Create the 21-combination visual project matrix from `breakpoints.json`, the determinism fixtures, and the first baselines for every `visual`-tagged Storybook story, which needs no authentication and can therefore ship in P0 ahead of test-mode seeding.

**Scope**

* In: `apps/web/playwright.visual.config.ts` generating projects `xs-320 … 3xl-1920` with viewport, `deviceScaleFactor`, `hasTouch`, `isMobile` from the device matrix; theme fixture setting `data-theme`; determinism fixtures (fixed clock, `animations: 'disabled'`, `reducedMotion`, `caret: 'hide'`, fonts ready, `data-ready` wait, volatile masking); story capture from `storybook-static/index.json`; screenshot ID grammar; Docker image pin; `pnpm shots*` scripts.
* Out: authenticated page capture and baseline workflow (sibling), reporter and sharding (sibling).

**Spec**

* Projects from `ops/ci/breakpoints.json` (PAP-14); 7 widths × 3 themes = 21 project-theme combinations; `toHaveScreenshot` thresholds `maxDiffPixelRatio: 0.002`, `threshold: 0.2`.
* Stories opt in with `tags: ['visual']`; element screenshots of `#storybook-root`; ID `story:<storyId>`.
* Masks: elements with `data-volatile` painted `--pos-color-accent-500`.
* Image `mcr.microsoft.com/playwright:v1.5x-noble` pinned; outside Docker runs print an environment-mismatch warning and are informational.
* Baselines under `apps/web/e2e/visual/__screenshots__/<project>/<theme>/<id>.png` with Git LFS (`.gitattributes` and LFS enabled on both forges).

**Interface contract**

* Provides: `visualTest` fixture (`{ theme, width, seedReady }`), project names as the canonical width keys used by PAP-83, PAP-84, PAP-87; screenshot ID grammar; `pnpm shots`.
* Requires: PAP-14 `breakpoints.json`, PAP-69 `storybook-static`, PAP-78 artifacts; LFS on Forgejo (PAP-45 config).

**Definition of done**

* Storybook stories for PAP-66 tokens and PAP-67 components captured at 21 combinations with baselines committed via LFS.
* 10 consecutive runs on `main` with zero diffs (flake check).
* Seeded 2 px padding change on Button fails with a visible diff image (link).
* `docs/quality/visual-testing.md` sections "Matrix", "Determinism", "Stories".

**Test plan**

* Unit: project generation from JSON snapshot; ID sanitising.
* Integration: determinism run repeated 10 times; mask rendering check.
* Visual: the suite itself.

**Demo**

`pnpm shots --project sm-375 --grep story:ui-button` inside the Docker image, then `pnpm shots:report` to open the HTML report with the 3 theme captures. Under two minutes.

**Edge cases**

* Story renders a portal: capture `body` for stories tagged `visual-portal`.
* Fonts not ready: `document.fonts.ready` awaited with a 5 s cap.
* LFS quota: baselines capped at 600 images with a count check.

**Dependencies**

PAP-78, PAP-14 (hard). Soft: PAP-69. Blocks the two sibling children.

**Agent**

Built by Sentinel (Visual Inspector sub-agent). Reviewed by Forge (LFS, image) and Iris (story tags).

**Size**

M.
"""},
{
 "key": "quality/playwright-matrix/pages-auth-baselines", "type": "Build", "size": "M",
 "title": "Page capture with authenticated audiences and baseline update workflow",
 "description": """**Goal**

Extend the suite from stories to real pages: derive the page list from route files and specs, log in per audience through test mode, seed deterministic data, and give agents a one-label baseline update workflow with bot commits.

**Scope**

* In: `apps/web/e2e/visual/pages.ts` (routes with `staticData.spec` plus specs with `screenshot: true`), per-audience storage state via `loginAs` and `seed('portal' | 'console')`, full-page capture rules, `update-baselines` label workflow committing with the bot account, guard flagging baseline pushes without the label, `screenshot: false` opt-out with reason.
* Out: matrix and fixtures (sibling), reporter (sibling).

**Spec**

* Page IDs `page:<routeId>`; `fullPage: true` capped at 4 000 px; `screenshot: fullScroll` for scrolling capture; `data-ready` attribute awaited.
* Audience per page from the spec `access.view` (first audience) unless `screenshot.as` overrides; anonymous pages skip login.
* Workflow `.github/workflows/update-baselines.yml`: on label, run the suite with `--update-snapshots`, commit via PAP-48 bot with message `test(visual): update baselines for #<pr>`, remove the label, comment the diff count; a Gate 1 check fails when `__screenshots__` changes without that commit signature.
* Test-mode dependence stated: without the seed issue the suite runs stories only and posts "pages skipped: test mode unavailable".

**Interface contract**

* Provides: page list module used by PAP-83 flows and PAP-87 URLs, `screenshot` spec keys (`true | false | fullScroll`, `as`), `update-baselines` label contract for agents (PAP-92 playbook).
* Requires: sibling matrix child, test-mode seed and `loginAs`, PAP-48 bot, PAP-16 routes, PAP-115 spec keys (soft).

**Definition of done**

* All example routes and portal/console pages captured for their audiences at 21 combinations; baselines committed.
* Label workflow turns a red gate green in one run (links to both).
* Direct baseline push without the signature fails Gate 1 (seeded).
* Docs sections "Pages", "Audiences", "Updating baselines".

**Test plan**

* Unit: page list derivation and opt-out handling.
* Integration: login state caching per shard; anonymous versus customer captures differ on `/portal`.
* Workflow: rehearsal on the sandbox repo.

**Demo**

Change a portal heading colour, push, watch `gate/3-visual` fail with a contact sheet; add the `update-baselines` label and watch the bot commit land and the gate pass. Under two minutes of watching after CI runs.

**Edge cases**

* Two baseline PRs conflict in LFS: rerun the label workflow after rebase (documented).
* Renamed route: old baseline `missing` requires explicit deletion.
* Page needs data the fixture lacks: `screenshot.fixture` key selects another fixture.

**Dependencies**

Sibling matrix child, test-mode seed issue (hard). Soft: PAP-48, PAP-115.

**Agent**

Built by Sentinel (Visual Inspector). Reviewed by Forge (workflow) and Quill (spec keys).

**Size**

M.
"""},
{
 "key": "quality/playwright-matrix/reporter-sharding", "type": "Build", "size": "S",
 "title": "Contact-sheet reporter, 4-way sharding and the visual.json artifact",
 "description": """**Goal**

Make the suite fast and legible: a custom reporter that composes contact sheets per page across widths, 4-shard CI with merged reports, the `visual.json` artifact in the contracts shape, the sticky PR comment and the Pages report upload.

**Scope**

* In: `ops/ci/visual/contact-sheet-reporter.ts` (`sharp` grid per page, thumbnails of top 6 diffs), `--shard=i/4` matrix in `visual.yml` with `merge-reports`, `reports/visual.json` writer, sticky comment section "Visual", upload to `/pr/<n>/visual/`, `gate/3-visual` status, 8-minute budget check.
* Out: capture (siblings), vision inspection (PAP-84).

**Spec**

* Reporter listens to test results, groups by page ID, renders a grid (columns widths, rows themes) with status badges; output `reports/visual/sheets/<id>.png`.
* `visual.json`: `GateReport<'visual'>` with `data.images: [{ id, project, theme, status: pass|diff|new|missing, diffRatio, paths: { actual, expected?, diff? } }]` validated by `packages/contracts`.
* CI: 4 runners, blob reporter, `npx playwright merge-reports`, HTML report and sheets uploaded to run artifacts and to Pages via PAP-15's branch strategy; comment via the shared sticky-comment action (PAP-78).
* Budget: total wall time under 8 minutes; a count check fails when images exceed 600.

**Interface contract**

* Provides: `visual.json`, contact sheets, Pages URLs `artifactUrl(pr, 'visual/...')`, status `gate/3-visual`.
* Requires: sibling children, `packages/contracts`, PAP-78 comment action, PAP-15 Pages hosting (soft; artifacts otherwise).
* Consumers: PAP-84 (reads `visual.json`), PAP-89, PAP-137.

**Definition of done**

* Suite runs on a PR across 4 shards in under 8 minutes and posts the sticky comment with sheets (link).
* `visual.json` validates; PAP-84 stub consumer lists diff images from it.
* Count check fails on a seeded 601st image.
* Docs section "Reports and sharding".

**Test plan**

* Unit: grid layout math, JSON writer against fixtures.
* Integration: merge of 4 blob reports in CI.
* Visual: a contact sheet snapshot itself.

**Demo**

Open a PR's "Visual" comment, click the contact sheet for `/portal`, see 7 widths × 3 themes with one red badge; open the Pages report link. Under one minute.

**Edge cases**

* Shard failure: merge marks missing results `error`, never pass.
* Pages upload over size: sheets only, full images in run artifacts.
* Zero visual-tagged tests: comment says so, status pass.

**Dependencies**

Both sibling children (hard), `packages/contracts` (hard). Soft: PAP-15.

**Agent**

Built by Sentinel (Visual Inspector). Reviewed by Forge (CI).

**Size**

S.
"""},
],
"PAP-85": [
{
 "key": "quality/edge-case-hunter/planner", "type": "Build", "size": "M",
 "title": "Scenario planner from specs with fixture catalogue",
 "description": """**Goal**

Turn a page spec and a diff into a prioritised scenario plan: a Claude planning step constrained by a schema, a catalogue of nine scenario classes with fixtures and corpora, and scenario memory that reuses good scenarios per component type.

**Scope**

* In: `packages/agents/src/edgecases/planScenarios(spec, diff)`, plan schema, prompt `.claude/agents/reviewers/edge-case-hunter.md`, fixture catalogue definitions (`data.empty|huge|unicode`, `input.invalid`, `network.offline|slow3g|flaky`, `device.slowCpu`, `auth.denied|expired`, `concurrency.doubleSubmit|staleWrite`, `time.dstBoundary|leapDay|farFuture`), corpora in `ops/quality/corpora/`, scenario memory `ops/quality/edge-scenarios.yaml`, budget cap.
* Out: execution (sibling), findings and repros (sibling).

**Spec**

* Plan schema: `{ pageId, scenarios: [{ id, class, description, setup: { seed?, route?, viewport?, auth? }, steps, expect: oracleId[], severityIfFails }] }`; cap 30 per page prioritised by spec-declared risk and diff size.
* Prompt inputs: spec sections `data`, `logic`, `states`, `access`, `edge cases`, diff summary, fixture catalogue, prior scenarios for the same component types (from memory), PAP-79 edge-case checklist; output JSON only, validated by Zod, invalid entries dropped and counted.
* Corpora: unicode (emoji, combining marks, RTL Arabic and Hebrew, CJK, zero-width), injection strings, boundary numbers, dates around DST and leap day; `@faker-js/faker` seed 42.
* Budget: planning under $2 per PR; over budget defers to nightly.

**Interface contract**

* Provides: `ScenarioPlan` type, `SCENARIO_CLASSES`, `planScenarios()`, corpora files, memory format.
* Requires: PAP-114 spec schema, PAP-79 checklist, sibling harness from PAP-81 (SDK runner).
* Consumers: sibling executor, PAP-110 evals.

**Definition of done**

* Plans for the three example specs (PAP-125) contain 15 to 30 valid scenarios each covering at least six classes.
* Invalid model output is dropped with counts (test with a corrupted fixture).
* Memory grows after a run and is reused on the next plan (test).
* Planning cost under $2 across 10 runs.

**Test plan**

* Unit: schema validation, prioritisation, memory merge.
* Integration: planner against fixture specs with mocked SDK and one live run nightly.

**Demo**

`pnpm edge:plan --spec specs/pages/examples/customer-list.page.spec.yaml` and read the JSON: 20 scenarios across empty, huge, unicode, offline, denied and double-submit. Under one minute.

**Edge cases**

* Spec without edge cases section: planner relies on classes and warns.
* Duplicate scenarios across runs: deduped by class plus normalised description.

**Dependencies**

PAP-114, PAP-81 harness child (hard). Blocks the executor sibling.

**Agent**

Built by Sentinel (Edge Case Hunter sub-agent). Reviewed by Nova (data realism) and Atlas (budget).

**Size**

M.
"""},
{
 "key": "quality/edge-case-hunter/executor-oracles", "type": "Build", "size": "M",
 "title": "Playwright executor and generic oracles",
 "description": """**Goal**

Execute a scenario plan deterministically with Playwright: fixtures for every scenario class, generic oracles that decide pass or fail without page-specific code, and evidence capture.

**Scope**

* In: `runScenarios(plan)` with fixture implementations (route interception for network, CDP CPU throttling, clock control, seeded data via test mode, auth via `loginAs`, double-submit and stale-write helpers), oracle set (no unhandled exception, no console error, no spinner over 10 s, declared states render, no overflow via DOM metrics, form errors announced, data survives reload), evidence capture (screenshot or video per failure), two-shard run at `sm-375` and `xl-1280`.
* Out: planning (sibling), reporting and repros (sibling).

**Spec**

* Fixtures: `network.slow3g` = 400 ms latency and 400 kbps via `route`; `network.flaky` aborts 20 percent of requests deterministically by hash; `device.slowCpu` = `Emulation.setCPUThrottlingRate 6`; `data.huge` seeds 10k rows or falls back to MSW mocks after 20 s; `time.*` via `page.clock` and the test-mode `clock` route.
* Oracles are pure functions over `{ page, console, network, domMetrics, spec }` returning `Finding[]` in the contracts shape with `severityIfFails` from the plan.
* Flaky scenario rule: repeat failures 3 times, report only consistent ones, log flakes to PAP-90's delta format.
* Budget: execution under 8 minutes per PR across 2 shards; deferred scenarios listed.

**Interface contract**

* Provides: `runScenarios()`, `Oracle` interface, fixture registry, `reports/edgecases.raw.json`.
* Requires: sibling planner, PAP-82 matrix fixtures and DOM metrics (PAP-84 emits them), test-mode seed, `loginAs`.

**Definition of done**

* Seeded defects (unhandled empty list, crash on emoji name, missing offline state, double submit creating duplicates) each fail the correct oracle with evidence.
* Clean example page yields zero S0/S1.
* Fixture determinism: same plan twice gives identical outcomes (test).
* Docs section "Executor and oracles".

**Test plan**

* Unit: each oracle on synthetic inputs; flaky request hashing.
* Integration: seeded defect pages in the example app.
* Perf: budget check on the two-shard run.

**Demo**

`pnpm edge:run --page customer-list --scenario data.unicode-1` against the dev app and watch the emoji-name crash reproduce with a screenshot in `reports/`. Under two minutes.

**Edge cases**

* Destructive scenario on shared staging: refused; executor only targets ephemeral previews.
* Huge seeding too slow: MSW fallback flagged in the finding.

**Dependencies**

Sibling planner child (hard), test-mode seed issue (hard). Soft: PAP-82, PAP-84.

**Agent**

Built by Sentinel (Edge Case Hunter). Reviewed by Forge (fixtures) and Nova.

**Size**

M.
"""},
{
 "key": "quality/edge-case-hunter/findings-repros-nightly", "type": "Build", "size": "S",
 "title": "Findings, generated repro tests and nightly library run",
 "description": """**Goal**

Close the loop: publish `edgecases.json` and the PR matrix comment, generate reproducible Playwright tests for failures in a companion PR, and run the full scenario library nightly on `main` with deduplicated Linear issues for new S1 findings.

**Scope**

* In: `report()` producing `GateReport<'edgecases'>`, "Edge cases" sticky comment with the pass/fail matrix, status `gate/4-edge`, repro generator writing `apps/web/e2e/generated/<page>/<scenarioId>.spec.ts` marked `test.fixme` into an `edge-case-repros` PR against the same branch via the bot, nightly `edge-nightly.yml` over all pages with Linear issue creation through PAP-97 (dry-run first), dedupe by finding ID and with PAP-84 overflow findings by bbox overlap.
* Out: planning and execution (siblings).

**Spec**

* Findings include `repro: 'pnpm edge:run --page <id> --scenario <sid>'` and evidence refs.
* Repro test template renders the scenario steps as Playwright code with the fixture setup; lint and typecheck clean; PR body links the finding IDs.
* Nightly: all pages, full library, results to `reports/edgecases.json` on `main`, Linear issues titled `Edge case: <page> <scenario>` labelled `Bug`, assigned to the owning character via `.mailmap`; dedupe key stored in the issue body.

**Interface contract**

* Provides: `edgecases.json`, comment section, repro PR convention, nightly Linear issue template.
* Requires: siblings, `packages/contracts`, PAP-97 webhooks, PAP-48 bot, PAP-84 `vision.json` for dedupe.
* Consumers: PAP-88 certification, PAP-89 digest, PAP-110.

**Definition of done**

* PR touching an example page shows the matrix with at least 15 executed scenarios and evidence for failures (link).
* Repro PR opened for a seeded failure, passes lint and typecheck (link).
* Nightly dry run lists the Linear issues it would create (screenshot); one live creation verified and then closed by Atlas.
* `docs/quality/edge-cases.md` complete; changelog under "Quality".

**Test plan**

* Unit: report writer, repro template snapshot, dedupe.
* Integration: nightly workflow on the sandbox repo.

**Demo**

Open the PR's "Edge cases" comment, click a failed cell, copy the repro command, run it locally and see the same failure. Under two minutes.

**Edge cases**

* More than 10 failures: repro PR groups by page, caps at 10 with a list of the rest.
* Linear rate limit: batched creation, retry after 60 s.

**Dependencies**

Both sibling children (hard). Soft: PAP-97, PAP-48, PAP-84.

**Agent**

Built by Sentinel (Edge Case Hunter). Reviewed by Atlas (Linear policy).

**Size**

S.
"""},
],
"PAP-88": [
{
 "key": "quality/release-train/policy-environments", "type": "Spec", "size": "S",
 "title": "Release train policy document and environments config",
 "description": """**Goal**

Write the rules before the automation: branches, cadence, freeze and hotfix rules, environments, rollback, and who decides what, as a document plus a machine-readable environments file the workflows read.

**Scope**

* In: `docs/quality/release-train.md`, ADR `docs/adr/0008-release-train.md`, `ops/release/environments.yaml` with schema, release record schema `ops/release/records/<version>.json`, RC Linear issue template text, links from CLAUDE.md and the PR template.
* Out: workflows (siblings).

**Spec**

* Policy: `main` always releasable; `release/<yyyy-ww>` cut Monday 08:00 UTC; RC freeze accepts only PRs labelled `rc-fix`; hotfix branches from the last tag with label `hotfix`; rollback procedure with snapshot restore rules; environments preview, staging, production; roles: Atlas merges, Sentinel certifies, Justin approves releases only; feature flags default off for risky work (PAP-17 `Flags`, runtime flags later).
* Queue rule: never more than one open RC issue; skip the cut and comment if last week's is open.
* `environments.yaml`: `[{ name, url, coolifyWebhookSecretName, database, allowedBranches, testMode: false }]` validated by Zod in `packages/contracts`.
* Release record: `{ version, sha, date, gates, digestUrl, approver, deployedAt, rollbackTarget, snapshotId }`.
* Approval grammar: uses PAP-94's `/approve` and `/reject <reason>` comment commands exactly; this document references, not redefines, them.

**Interface contract**

* Provides: `environments.yaml` schema and file, `ReleaseRecord` type, policy rules cited by `certify.ts`, RC issue template.
* Requires: PAP-94 command grammar, PAP-46 branch conventions, PAP-52 tag format.

**Definition of done**

* Policy and ADR merged, linked from CLAUDE.md and PAP-49's template.
* `environments.yaml` validates; staging and production entries filled with secret names (not values).
* Atlas, Forge and Justin each confirm their role in a comment.

**Test plan**

* Unit: schema validation of the YAML and a sample record.
* Review: Quill edits for clarity; Sentinel checks every rule has an enforcing step in a sibling.

**Demo**

Open `docs/quality/release-train.md`, read the one-page calendar table (Monday cut, nightly staging, approval window), then `pnpm release:env --validate`. Under one minute.

**Edge cases**

* Two RCs needed in a week (urgent feature): policy says hotfix path or wait; documented.
* Production and staging share a database by mistake: schema forbids duplicate `database` values.

**Dependencies**

PAP-94 (hard for the grammar). Soft: PAP-46, PAP-52. Blocks the two sibling children.

**Agent**

Written by Sentinel with Atlas. Reviewed by Forge and Justin (roles).

**Size**

S.
"""},
{
 "key": "quality/release-train/nightly-staging", "type": "Build", "size": "M",
 "title": "Nightly staging workflow with full gate run",
 "description": """**Goal**

Deploy `main` to staging every night through Coolify, run the full suites (e2e `@full`, visual matrix, edge-case library, perf), and write a nightly report so the RC on Monday starts from known-good evidence.

**Scope**

* In: `.github/workflows/staging-nightly.yml` at 02:00 UTC and `workflow_dispatch`, Coolify deploy step with status polling and smoke (`/healthz`, `/__version` equals SHA), pre-deploy backup call and snapshot id capture, migrations via `drizzle-kit migrate`, suite invocations, `reports/nightly-<date>.json` aggregate in the contracts shape, failure notification comment on a pinned "Nightly" Linear issue.
* Out: RC cut and promotion (sibling), the suites themselves.

**Spec**

* Deploy: `POST /api/v1/deploy?uuid=<staging>` with bearer secret; poll deployment status until `finished` (cap 15 minutes); smoke checks; on failure stop and report.
* Backup: call PAP-30's backup script before migrations, record `snapshotId`.
* Suites: PAP-86 `@full` including 375 run, PAP-82 full 21 combinations, PAP-85 nightly library, PAP-87 informational Pages run, API perf smoke when available.
* Aggregate: `{ date, sha, deploy: { status, durationMs }, suites: [{ name, status, reportUrl }], trends }`; three consecutive nights of reports are the DoD evidence.
* Notification: comment on the pinned Linear issue via PAP-97 with a one-line status and links; red nights also open a task for Atlas.

**Interface contract**

* Provides: nightly report artifact and Pages URL `/nightly/<date>/`, `deployToEnvironment(name, sha)` composite action reused by the RC sibling, staging trend data for PAP-89.
* Requires: sibling policy (`environments.yaml`), PAP-26 images and Coolify, PAP-30 backup script, PAP-86, PAP-82, PAP-85, PAP-97.

**Definition of done**

* Three consecutive nightly runs with reports (links).
* Seeded failing deploy (bad SHA) stops before suites and reports `deploy: failed` (link).
* `deployToEnvironment` reused by the RC workflow (PR reference).
* Docs section "Nightly".

**Test plan**

* Unit: aggregate writer, status polling with fake responses.
* Integration: `workflow_dispatch` rehearsal against staging.

**Demo**

Trigger `workflow_dispatch` on `staging-nightly`, watch the deploy step finish, then open the nightly report page for that date. Two minutes of watching after the run.

**Edge cases**

* Migration fails: no app rollout; report flags it; snapshot id retained for restore.
* Coolify API down: retry 30 minutes then fail loudly.
* Suites exceed runner capacity: sequential fallback with a duration warning.

**Dependencies**

Sibling policy child (hard), PAP-26 (hard). Soft: PAP-30, PAP-86, PAP-82, PAP-85, PAP-97.

**Agent**

Built by Forge (Ops Runner) with Sentinel. Reviewed by Atlas.

**Size**

M.
"""},
{
 "key": "quality/release-train/rc-certify-approve", "type": "Build", "size": "M",
 "title": "Release candidate cut, certification and Justin approval flow",
 "description": """**Goal**

Automate the weekly decision: cut the RC branch and PR, deploy it to staging, run gates, generate the digest, open one Needs Justin issue, and on `/approve` promote to production with a tag while `/reject` reopens fixes, all idempotent and rehearsed.

**Scope**

* In: `.github/workflows/release-candidate.yml` (Monday cut, `release/<yyyy-ww>` branch, PR labelled `release-candidate`, prerelease tag `-rc.N` via PAP-52), `ops/release/certify.ts`, digest call (PAP-89), Needs Justin issue creation with the RC template, `promote.yml` triggered by PAP-97 on `/approve` or Done, production deploy with `deployToEnvironment`, tag `vX.Y.Z`, release notes from PAP-133, `/reject` handling, rollback command, queue rule enforcement, rehearsal with a `rehearsal` label on the PAP team.
* Out: policy (sibling), nightly (sibling), digest content (PAP-89).

**Spec**

* `certify.ts` checks: all `GATE_STATUSES` green on the RC head, no open S0/S1 findings across artifacts, no expired waivers, `perf.json` within budget when present, migrations reversible flag from PAP-32, backup fresher than 24 h, staging `testMode: false`; output `certification.json` and a Markdown table for the issue.
* Needs Justin issue: title `Release candidate <yyyy-ww> (vX.Y.Z-rc.N)`, body with digest link, gate table, one-line ask, `/approve` and `/reject <reason>`; label `rehearsal` marks dry runs so PAP-94's queue metrics ignore them.
* Promotion: idempotency key = RC head SHA in the release record; merge release PR, tag, deploy production, post release notes, close the issue; failure triggers auto-rollback and reopens the issue with logs.
* `pnpm release:rollback <version>` redeploys the previous image and optionally restores the snapshot with confirmation.

**Interface contract**

* Provides: `certification.json` (contracts kind), release records, `promote.yml` webhook contract with PAP-97 (`event: 'release.approve' | 'release.reject'`), tags for PAP-52 and PAP-19 updater.
* Requires: siblings, PAP-89 digest, PAP-94 grammar, PAP-97 webhooks, PAP-52 tags, PAP-133 notes, PAP-26 production target.

**Definition of done**

* Rehearsal RC end to end with the `rehearsal` label: branch, PR, gates, digest, Needs Justin issue, `/approve` promotes to a staging-as-production target and tags `v0.1.0-rc.1` (links, screenshots).
* `/reject` path tested; `certify.ts` blocks on a seeded missing status and on `testMode: true`.
* Duplicate approval webhook does not double deploy (test).
* Docs section "Release candidate and promotion"; changelog under "Quality".

**Test plan**

* Unit: certification rules table, idempotency key, queue rule.
* Integration: promote workflow against the sandbox with a fake Coolify.
* Rehearsal: live once on the PAP team with the label.

**Demo**

Open the rehearsal Needs Justin issue, read the gate table and digest link, comment `/approve`, watch `promote.yml` tag and deploy, and see the issue close. Under two minutes after the comment.

**Edge cases**

* `main` red on Monday: no cut; comment on the previous RC issue.
* Justin approves while a hotfix is deploying: promotion waits for the deploy lock.
* Irreversible migration: certification requires the acknowledgement checkbox from the digest.

**Dependencies**

Both sibling children (hard), PAP-94, PAP-89 (hard). Soft: PAP-97, PAP-52, PAP-133.

**Agent**

Built by Sentinel with Atlas (Merger sub-agent) on promotion and Forge (Ops Runner) on deploys. Reviewed by Atlas; Justin confirms via the rehearsal.

**Size**

M.
"""},
],
}

SIBLING_BLOCKS = {
 "quality/review-agents/harness": ["quality/review-agents/correctness-spec", "quality/review-agents/security"],
 "quality/playwright-matrix/projects-fixtures-stories": ["quality/playwright-matrix/pages-auth-baselines", "quality/playwright-matrix/reporter-sharding"],
 "quality/playwright-matrix/pages-auth-baselines": ["quality/playwright-matrix/reporter-sharding"],
 "quality/edge-case-hunter/planner": ["quality/edge-case-hunter/executor-oracles"],
 "quality/edge-case-hunter/executor-oracles": ["quality/edge-case-hunter/findings-repros-nightly"],
 "quality/release-train/policy-environments": ["quality/release-train/nightly-staging", "quality/release-train/rc-certify-approve"],
 "quality/release-train/nightly-staging": ["quality/release-train/rc-certify-approve"],
}

# Extra relations involving new issues and existing ones (from -> to, by key or identifier)
EXTRA_RELATIONS = [
 ("quality/test-mode-seed", "quality/playwright-matrix/pages-auth-baselines"),
 ("quality/test-mode-seed", "quality/edge-case-hunter/executor-oracles"),
 ("quality/gate-artifact-contract", "quality/review-agents/harness"),
 ("quality/gate-artifact-contract", "quality/playwright-matrix/reporter-sharding"),
 ("PAP-94", "PAP-88"),
]
