---
identifier: "PAP-676"
title: "Security regression suite: 30+ control-tagged tests (headers, CSRF, IDOR across tenants, rate limits, upload abuse, webhook replay, SSRF, Tauri origin) blocking the release candidate"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: "PAP-357"
children: []
blockedBy: ["PAP-64", "PAP-80", "PAP-240", "PAP-675"]
blocks: ["PAP-254", "PAP-903"]
key: "r4/quality/security-regression-suite"
url: "https://linear.app/paperos/issue/PAP-676/security-regression-suite-30-control-tagged-tests-headers-csrf-idor"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:26.513Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-676: Security regression suite: 30+ control-tagged tests (headers, CSRF, IDOR across tenants, rate limits, upload abuse, webhook replay, SSRF, Tauri origin) blocking the release candidate

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-357: encode the PAP-219 hardening baseline as failing tests. `packages/security-tests` holds Playwright and Vitest cases, each tagged with a `SEC-*` control id, that run in Gate 1 for PRs touching auth, files, webhooks or tenancy and nightly against staging, feeding `reports/security.json` and `gate/dast`.

**Scope**

* In: `packages/security-tests/` (Vitest for API cases, Playwright for browser cases), `SEC-*` tagging and `pnpm security:controls --verify test`, path-filtered Gate 1 job `security-tests`, JUnit to SARIF conversion into the PAP-80 merge, seeded-defect fixtures, `docs/quality/dast.md` section "Regression suite".
* Out: ZAP scans (sibling), permission matrix tests (PAP-64 owns policy-level checks; this suite reuses its fixtures for IDOR), load (PAP-242).

**Spec**

* Cases, each citing a control: headers and CSP on `/`, `/auth/sign-in`, `/api/*` (no `unsafe-inline`, nonce differs per response); CSRF: mutating oRPC call with a session cookie and a foreign `Origin` returns 403; IDOR: for every entity in the PAP-64 fixtures, tenant B ids fetched as tenant A via `get`, `update`, `archive`, signed file URL (PAP-37) and Electric shape with a forged `where` (PAP-36) return 403, 404 or empty; enumeration: ids are uuid v7, numeric ids flagged; rate limit: 700 requests in a minute as one actor returns 429 with `Retry-After` (PAP-35); auth: no session fixation after login, cookie flags, account-existence parity on passwordless flows (timing and message), magic link single use and 15 min expiry, impersonation read-only (PAP-61); uploads: polyglot image rejected by sniffing, SVG served with `sandbox` CSP, 101 MB rejected (PAP-37); webhooks: Linear, forge and Stripe receivers reject bad signatures, replayed `webhookId`, timestamps older than 60 s (PAP-97, PAP-177); batch abuse of `/api/rpc/batch` capped; open redirect on `redirect_to`; SSRF on webhook endpoint creation (`169.254.169.254`, `localhost`, `10.0.0.0/8`) rejected (PAP-222); Tauri: `tauri://localhost` origin accepted only with a bearer token (PAP-225).
* Every test is `test('SEC-API-01 ...')` and registers in `ops/security/controls.yaml` `verify: test`; `pnpm security:controls --verify test` lists unverified controls.
* Gate 1 job runs the suite when the PR touches `apps/api/**`, `packages/auth/**`, `packages/files/**`, `packages/permissions/**`; nightly runs against staging after the ZAP baseline; results converted to SARIF (`tool: security-tests`) and merged.
* Seeded defects under `packages/security-tests/fixtures/defects/`: route without origin check, missing `HttpOnly`, IDOR on a fixture entity, webhook receiver accepting a replay; each toggled by an env flag on the local stack.

**Interface contract**

* Provides: `packages/security-tests` with the `SEC-*` convention, Gate 1 job `security-tests`, SARIF entries, `pnpm security:controls --verify test`, seeded-defect flags for the calibration of the security reviewer (PAP-245).
* Consumes: PAP-80 merge step, PAP-240 test users, PAP-64 fixtures, PAP-219 `controls.yaml`, PAP-42 local stack, sibling scan job for the nightly slot.

**Definition of done**

* At least 30 controls covered; every test names its `SEC-*` id; `--verify test` shows them verified.
* Each seeded defect fails exactly its tests (table of defect to test ids).
* Suite under 4 minutes in Gate 1; nightly staging run green for three nights.
* PAP-81 security reviewer prompt gains the rule that routes touching auth, files, webhooks or tenancy must reference a `SEC-*` test (comment on PAP-245).
* Docs section; changelog under "Security"; Linear comment with the control coverage table.

**Test plan**

* Unit: IDOR matrix generator from PAP-64 fixtures, signature and replay helpers, control tagging lint.
* E2E: suite against the local stack in Gate 1 and staging nightly; seeded defect toggles.

**Demo**

Run `pnpm security:test` against the local stack (30 green), flip `securityHeaders({ csp: false })` and watch three tests fail naming their `SEC-*` ids; open `pnpm security:controls --verify test`. Ninety seconds.

**Edge cases**

* A control that cannot be tested automatically (physical key policy): marked `verify: manual` with an owner, never silently unverified.
* New route added without a security test: the reviewer rule above flags it; the suite lint lists untagged tests.
* Rate-limit test contaminates other suites: dedicated `sectest` actor with a reset hook.
* Tauri case needs a desktop runner: runs as a unit test of the origin check middleware, not a real Tauri process.

**Dependencies**

Hard: PAP-80, PAP-240, PAP-64, PAP-675. Soft: PAP-219, PAP-37, PAP-36, PAP-35, PAP-61, PAP-97, PAP-177, PAP-222, PAP-225, PAP-42.

**Agent**

Builder: Sentinel (Security Auditor). Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/dast-zap-nightly-and-authenticated-scans` = PAP-675.
