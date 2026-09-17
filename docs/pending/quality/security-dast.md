---
key: "security/dast"
title: "Add dynamic security testing: nightly ZAP baseline and authenticated scan of staging plus a security regression suite (CSRF, IDOR across tenants, headers, rate limits, upload abuse, webhook replay) that blocks the release candidate"
project: "quality"
parent: null
phase: "P1"
type: "Infra"
priority: 2
size: "M"
surfaces: ["Developer", "Agent"]
milestone: "Edge-case hunting and release trains"
intendedState: "Backlog"
blockedBy: ["PAP-80", "PAP-240", "PAP-26"]
blocks: ["PAP-254"]
source: "round2/agent6/pending-issues.json (Security & Threat Model)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-security-11-27d8ebfcd8d0"
identifier: "PAP-357"
status: "created"
createdAt: "2026-09-17"
---

# Add dynamic security testing: nightly ZAP baseline and authenticated scan of staging plus a security regression suite (CSRF, IDOR across tenants, headers, rate limits, upload abuse, webhook replay) that blocks the release candidate

**Goal**

PAP-80 scans code and images; PAP-64 tests permissions; PAP-34 tests RLS. Nobody attacks the running application. This issue adds OWASP ZAP against staging every night, unauthenticated and as each seeded audience, plus a hand-written security regression suite that encodes the PAP-219 hardening baseline as failing tests, so a release candidate (PAP-254) cannot be certified with an open S0 or S1 dynamic finding.

**Scope**

* In: `.github/workflows/dast.yml` (nightly and on demand), ZAP baseline and full scan configuration (`ops/security/zap/`), authentication scripts using PAP-240 test users, `packages/security-tests` Playwright and Vitest suite, SARIF merge into `reports/security.json` (PAP-239 schema), commit status `gate/dast` on the RC branch, `docs/quality/dast.md`.
* Out: external penetration testing, fuzzing of the formula engine (Gate 4, PAP-85), load testing (PAP-242), WAF tuning.

**Spec**

* ZAP: `zaproxy/zap-stable` container on the self-hosted runner (PAP-50); nightly `zap-baseline.py` against `https://staging.<domain>` and `https://api.staging.<domain>/api/openapi.json` (API scan with the OpenAPI import from PAP-35); weekly `zap-full-scan.py` authenticated as `customer-pro`, `staff` and `admin` fixtures via a ZAP authentication script that performs the magic-link test flow exposed by PAP-240 (`/__test/login-as`); context excludes `/__test/*`, logout and destructive routes; alert thresholds: High = S0, Medium = S1 (mapped to PAP-79 severities).
* Regression suite (`packages/security-tests`), each test cites a `SEC-*` control id from PAP-219 `controls.yaml`: headers and CSP present on `/`, `/auth/sign-in`, `/api/*` (no `unsafe-inline`, nonce differs); CSRF: mutating oRPC call with a session cookie but a foreign `Origin` returns 403; IDOR: for each entity in the PAP-64 fixtures, fetch tenant B's ids as tenant A via `get`, `update`, `archive`, signed file URL (PAP-37) and Electric shape (PAP-36 proxy with a forged `where`) expecting 403, 404 or empty; enumeration: sequential ids are not guessable (uuid v7 accepted, numeric ids flagged); rate limits: 700 requests in a minute as one actor returns 429 with `Retry-After` (PAP-35); auth: session fixation after login, cookie flags (`Secure`, `HttpOnly`, `SameSite`), password-less flows do not leak account existence (timing and message parity), magic link single use and 15-minute expiry, impersonation read-only enforcement (PAP-61); uploads: polyglot file with image extension rejected by sniffing, SVG served with `sandbox` CSP, 101 MB upload rejected (PAP-37); webhooks: Linear, forge and Stripe receivers reject bad signatures, replayed `webhookId`, and timestamps older than 60 s (PAP-97, PAP-177); GraphQL-style batching abuse of `/api/rpc/batch` capped; open redirects on `redirect_to`; SSRF: webhook endpoint creation with `169.254.169.254`, `localhost`, `10.0.0.0/8` rejected (PAP-222); Tauri: `tauri://localhost` origin accepted only with a bearer token, not cookies (PAP-225).
* Outputs: ZAP SARIF plus suite JUnit merged into `reports/security.json` with deterministic finding ids; new S0/S1 open a Linear issue via PAP-97 deduped by id; `gate/dast` status on the RC branch is required by PAP-254 certification.
* Runtime: baseline under 10 min, full scan under 45 min weekly; suite under 4 min and also runs in Gate 1 for PRs touching `apps/api/**`, `packages/auth/**`, `packages/files/**`, `packages/permissions/**`.

**Interface contract**

* Provides: workflow `dast.yml`, `packages/security-tests` with `SEC-*` tagging, `reports/security.json` entries with `tool: zap|security-tests`, status `gate/dast`, Linear issue template `DAST finding`.
* Consumers: PAP-254 (certification requires green `gate/dast` within 7 days), PAP-89 digest (open dynamic findings), PAP-219 (control verification `verify: test` filled by this suite), PAP-241 (calibration cross-check), `security/security-telemetry` (`scan.new_s0_finding`).
* Requires: PAP-80 SARIF merge, PAP-240 test users and `/__test/login-as`, PAP-26 staging, PAP-239 finding schema, PAP-50 runner.

**Definition of done**

* Nightly baseline and weekly authenticated scan green for a week with all findings triaged (fixed or waived with expiry in `ops/security/waivers.yaml`).
* Regression suite covers at least 30 controls; every test names its `SEC-*` id; `pnpm security:controls --verify test` shows them as verified.
* Seeded defects each fail the suite: a route without origin check, a missing `HttpOnly`, an IDOR on a fixture entity, a webhook receiver accepting a replay.
* `gate/dast` required by the RC branch protection (PAP-46 ruleset updated).
* Docs; changelog under "Security"; Linear comment with the first scan summary.

**Test plan**

* Unit: severity mapping, finding id determinism, waiver expiry.
* Integration: the suite against the local stack (PAP-42) in CI; ZAP baseline against a PR preview (PAP-26) on demand with label `dast`.
* e2e: nightly staging runs.
* No UI.

**Demo**

Open the latest `dast.yml` run: ZAP summary with zero High, the suite's 30 green controls, then flip `securityHeaders({ csp: false })` on a preview and watch three tests fail with their `SEC-*` ids. Ninety seconds.

**Edge cases**

* ZAP spider hits destructive routes on staging: context excludes them and the test tenant is reset by `/__test/reset` after the run (PAP-240).
* Rate-limit test trips the limiter for other jobs: dedicated `dast` actor and IP allowlisted for reset.
* False positives from ZAP (CSP report-only, framework fingerprints): waived by rule id with expiry; the waiver file is shared with PAP-80.
* Staging down at 03:00: job retries once at 04:00, then posts `dast.skipped` to the digest.
* New route added without a security test: PAP-81 security reviewer prompt requires a `SEC-*` test reference for routes touching auth, files, webhooks or tenancy.

**Dependencies**

Blocked by PAP-80, PAP-240, PAP-26. Blocks PAP-254. Soft: PAP-239, PAP-50, PAP-64, PAP-46.

**Agent**

Built by Sentinel (Security Auditor sub-agent) with Forge (Ops Runner) for the runner and workflow; reviewed by Atlas.

**Size**

M
