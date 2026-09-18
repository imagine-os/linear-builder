---
identifier: "PAP-684"
title: "API fuzzing nightly: Schemathesis against the OpenAPI document with test-mode auth, per-procedure crash and 5xx findings into `edgecases.json`"
project: "quality"
projectName: "Quality Pipeline"
phase: "P2"
type: "Infra"
priority: 3
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-240", "PAP-251", "PAP-269"]
blocks: []
key: "r4/quality/api-fuzzing-nightly"
url: "https://linear.app/paperos/issue/PAP-684/api-fuzzing-nightly-schemathesis-against-the-openapi-document-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.771Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-684: API fuzzing nightly: Schemathesis against the OpenAPI document with test-mode auth, per-procedure crash and 5xx findings into `edgecases.json`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Gate 4 hunts edge cases through the UI and explicitly leaves API fuzzing out. The oRPC layer exposes an OpenAPI document (PAP-269) that Schemathesis can turn into thousands of property-based requests per night, catching 5xx responses, schema violations and idempotency breaks that no Playwright scenario reaches.

**Scope**

* In: `ops/quality/fuzz/` with `schemathesis` config and hooks, nightly job `api-fuzz.yml` after the PAP-253 deploy against staging (and on demand against a preview), auth via `/__test/login-as` per audience, results mapped to `Finding[]` and appended to `reports/edgecases.json` with `class: api.fuzz`, Linear issues via the PAP-251 nightly template, `docs/quality/edge-cases.md` section "API fuzzing".
* Out: UI scenarios (PAP-85), load (PAP-242), security exploitation (PAP-357), fuzzing of the formula engine (tables project).

**Spec**

* `schemathesis run https://api.staging.<domain>/api/openapi.json --checks all --hypothesis-max-examples 200 --workers 4 --header 'Cookie: <login-as>'` per audience `customer-pro`, `staff-support`, `anonymous`; `--exclude-path-regex '/__test/'`; stateful phase enabled where links exist.
* Checks mapped to PAP-79 severities: `server_error` (5xx) S1, `response_schema_conformance` S1, `not_a_server_error` on auth routes S0 when a 5xx leaks details, `status_code_conformance` S2, `content_type_conformance` S3; idempotency check: same `Idempotency-Key` twice must yield one row (PAP-304).
* Findings carry the reproducing `curl` from Schemathesis, deterministic `findingId('fuzz', operationId, check, statusCode)`; deduped against PAP-85 findings and prior nights.
* Destructive operations run only against the `e2e-fuzz` tenant seeded by PAP-240 and reset afterwards; a `--dry-run` mode lists operations without calling.
* Budget: under 20 minutes per night; over budget reduces `max-examples` and notes it.

**Interface contract**

* Provides: workflow `api-fuzz.yml`, `edgecases.json` entries with `class: api.fuzz`, the operationId to finding mapping, `pnpm fuzz:api --target <url>`.
* Consumes: PAP-269 OpenAPI document, PAP-240 `login-as` and `reset`, PAP-251 report and Linear template, PAP-304 idempotency semantics, PAP-253 nightly slot.

**Definition of done**

* Three nightly runs against staging with reports; a seeded unhandled `null` in a list procedure is caught as S1 with a repro `curl` (link).
* Zero findings on `/__test/*` (excluded); tenant reset verified after the run.
* Docs section; changelog under "Quality"; Linear comment with the first report.

**Test plan**

* Unit: severity mapping, finding id determinism, dedupe against fixture findings.
* E2E: on-demand run against a PR preview; nightly staging run.

**Demo**

Trigger `api-fuzz.yml` against a preview carrying the seeded null bug, open the Edge cases comment and copy the repro `curl`; run it and see the 500. Under two minutes.

**Edge cases**

* OpenAPI document out of date versus the router: schema conformance findings flood; the job first diffs the document against `pnpm api:procedures` and fails fast with `openapi-stale`.
* Rate limiter trips: `fuzz` actor allowlisted like the DAST actor.
* Long-running procedure (exports): per-request timeout 10 s, finding `timeout` at S2.
* Stateful phase creates data the next night sees: tenant reset covers it.

**Dependencies**

Hard: PAP-269, PAP-240, PAP-251. Soft: PAP-304, PAP-253, PAP-85.

**Agent**

Builder: Sentinel (Edge Case Hunter). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
