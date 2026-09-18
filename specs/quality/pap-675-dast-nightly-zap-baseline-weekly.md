---
identifier: "PAP-675"
title: "DAST: nightly ZAP baseline, weekly authenticated full scan per seeded audience, SARIF merge and `gate/dast` status"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-357"
children: []
blockedBy: ["PAP-26", "PAP-80", "PAP-240", "PAP-505"]
blocks: ["PAP-254", "PAP-676"]
key: "r4/quality/dast-zap-nightly-and-authenticated-scans"
url: "https://linear.app/paperos/issue/PAP-675/dast-nightly-zap-baseline-weekly-authenticated-full-scan-per-seeded"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:28.800Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-675: DAST: nightly ZAP baseline, weekly authenticated full scan per seeded audience, SARIF merge and `gate/dast` status

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

First half of PAP-357: attack the running staging application automatically. OWASP ZAP runs a nightly baseline scan against the web app and the OpenAPI document and a weekly authenticated full scan as each seeded audience, findings land in `reports/security.json` with deterministic ids and new S0/S1 findings open deduplicated Linear issues. The hand-written regression suite is the sibling child.

**Scope**

* In: `.github/workflows/dast.yml` (nightly 03:30 UTC after the PAP-253 deploy, `workflow_dispatch`, label `dast` on PR previews), `ops/security/zap/` (baseline and full-scan configs, context file, authentication script using `/__test/login-as`), SARIF conversion into the PAP-80 merge step, status `gate/dast` on the RC branch, Linear issue template `DAST finding`, `docs/quality/dast.md` sections "ZAP".
* Out: the regression suite (sibling), external penetration testing, fuzzing of the formula engine (PAP-85), load (PAP-242), WAF tuning.

**Spec**

* `zaproxy/zap-stable` on the self-hosted runner (PAP-50); nightly `zap-baseline.py -t https://staging.<domain>` and `zap-api-scan.py -t https://api.staging.<domain>/api/openapi.json -f openapi` (PAP-269 document); weekly `zap-full-scan.py` authenticated as `customer-pro`, `staff-support` and `admin` via a ZAP script that calls `POST /__test/login-as` (PAP-240) and stores the cookie.
* Context excludes `/__test/*`, sign-out and destructive routes; the `e2e-dast` tenant is reset by `/__test/reset` after each run; a dedicated `dast` actor is allowlisted in the PAP-35 rate limiter.
* Severity mapping to PAP-79: ZAP High = S0, Medium = S1, Low = S2, Informational dropped; finding id = `findingId('zap', pluginId, url path class, alert name)` so re-runs dedupe.
* Output merged by `ops/security/merge-sarif.ts` (PAP-80) into `reports/security.json` with `tool: zap`; new S0/S1 open or update one Linear issue via PAP-97, deduped by finding id; `gate/dast` set on the RC branch head and required by PAP-254 certification within 7 days.
* Runtime budgets: baseline under 10 min, API scan under 10 min, weekly full scan under 45 min; staging down at run time retries once after 60 min then posts `dast.skipped` to the security digest.

**Interface contract**

* Provides: workflow `dast.yml`, ZAP configs and auth script, `reports/security.json` entries with `tool: zap`, status `gate/dast`, issue template `DAST finding`, the shared waiver file usage.
* Consumes: PAP-80 merge step and waivers, PAP-240 `login-as` and `reset`, PAP-26 staging, PAP-269 OpenAPI, PAP-50 runner, PAP-97 issue creation, PAP-239 schema.

**Definition of done**

* Nightly baseline and API scan green for a week with every finding fixed or waived with expiry (waiver table in the comment).
* Weekly authenticated scan runs as three audiences; the run summary shows per-audience alert counts.
* A seeded missing `HttpOnly` flag and a reflected parameter on a preview are reported at the mapped severity (links).
* `gate/dast` required in the PAP-46 ruleset for `release/*` branches.
* Docs section; changelog under "Security"; Linear comment with the first scan summary.

**Test plan**

* Unit: severity mapping table, finding id determinism across two ZAP reports, waiver expiry.
* E2E: on-demand run against a PR preview with label `dast`; nightly staging run; reset of the `e2e-dast` tenant verified.

**Demo**

Open the latest `dast.yml` run summary: baseline and API scan with zero High, three authenticated contexts; then add label `dast` to a preview PR carrying a seeded header regression and watch the S1 appear in the Security comment. Ninety seconds.

**Edge cases**

* ZAP spider hits a destructive route despite the exclusions: the tenant is disposable and reset; the route is added to the context file by PR.
* False positives (CSP report-only, framework fingerprints): waived by rule id with expiry in the shared waiver file.
* Rate limiter trips for other jobs: dedicated actor and IP allowlisted; the limiter test in the sibling uses its own actor.
* OpenAPI document missing: API scan skipped with a notice, baseline still runs.

**Dependencies**

Hard: PAP-80, PAP-240, PAP-26. Soft: PAP-269, PAP-50, PAP-97, PAP-239, PAP-46.

**Agent**

Builder: Sentinel (Security Auditor) with Forge (Ops Runner) for the runner. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
