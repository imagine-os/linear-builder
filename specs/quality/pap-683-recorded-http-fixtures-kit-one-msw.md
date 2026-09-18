---
identifier: "PAP-683"
title: "Recorded HTTP fixtures kit: one `msw` recorder and fixture store for Linear, GitHub, Forgejo, Anthropic and Coolify used by every pipeline test suite"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13"]
blocks: ["PAP-372"]
key: "r4/quality/recorded-http-fixtures-kit"
url: "https://linear.app/paperos/issue/PAP-683/recorded-http-fixtures-kit-one-msw-recorder-and-fixture-store-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.581Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-683: Recorded HTTP fixtures kit: one `msw` recorder and fixture store for Linear, GitHub, Forgejo, Anthropic and Coolify used by every pipeline test suite

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-91, 93, 94, 97, 101, 105, 243, 306, 372 and 373 each say "integration against `nock`-recorded Linear responses" and each would build its own recorder, redaction and fixture layout. One shared kit records once, redacts secrets, replays deterministically in CI and fails loudly when a fixture is stale, so ten suites share fixtures instead of drifting apart.

**Scope**

* In: `packages/testing/http-fixtures/` with `record()`, `replay()`, `msw` handlers for `api.linear.app`, `api.github.com`, the Forgejo API, `api.anthropic.com` (Agent SDK stream shape) and the Coolify API; fixture layout `fixtures/http/<service>/<case>.json` with request matcher and redacted response; redaction rules; staleness check; `pnpm fixtures:record --service linear --case claim-race`; `docs/quality/testing.md` section "Recorded fixtures".
* Out: the suites themselves; live API calls in CI (never); the test-mode seed endpoints (PAP-240).

**Spec**

* Recorder wraps `fetch` (undici interceptor) and the Linear SDK's client; matches on method, URL path, GraphQL `operationName` and a hash of normalised variables; responses stored with `recordedAt`, `service`, `redactions[]`.
* Redaction: authorization headers dropped, ids from `linear-workspace.json` kept (they are not secrets), emails replaced by `user+<n>@fixture.local`, tokens by `<redacted:kind>`; PAP-107 `redact()` reused for bodies.
* Replay mode is the default in CI (`FIXTURES_MODE=replay`); an unmatched request fails the test with the closest fixture named; `FIXTURES_MODE=record` requires the broker placeholders (PAP-300) or a local key and is refused on CI.
* Staleness: fixtures older than 30 days for a service with a changed SDK version print a warning; `pnpm fixtures:verify` re-records against a sandbox team weekly (Atlas job) and diffs shapes.
* Anthropic stream fixtures: NDJSON of SDK messages (assistant, tool_use, result) so PAP-243, PAP-282 and PAP-308 share one mocked session shape.

**Interface contract**

* Provides: `record()`, `replay()`, `fixtures/http/**` layout, `pnpm fixtures:record|verify`, the shared SDK stream fixture format.
* Consumes: `msw` 2.x and undici interceptors, PAP-107 `redact()`, PAP-300 placeholders for recording, Linear sandbox team for `verify`.

**Definition of done**

* Kit used by at least three suites (PAP-93 validator webhooks, PAP-97 signatures, PAP-105 `linear-update`) with fixtures committed; their own `nock` code removed.
* Secret scan of `fixtures/http/**` finds nothing; redaction tests on 20 recorded samples.
* Unmatched request fails with the closest-fixture hint (test); staleness warning fires on a backdated fixture.
* Docs section; changelog under "Quality"; Linear comment listing consuming suites.

**Test plan**

* Unit: matcher normalisation (variable order, whitespace), redaction table, staleness rule.
* E2E: record against a Linear sandbox team locally, replay in CI for the three consuming suites.

**Demo**

Run `pnpm fixtures:record --service linear --case issue-update` locally, open the JSON and see the redacted response; run the PAP-93 suite in replay mode with the network disabled and watch it pass. Under one minute.

**Edge cases**

* GraphQL query with pagination cursors: matcher ignores `after` values and stores pages in order.
* Linear API adds a field: replay still passes (shape superset); `verify` reports the new field.
* Recording a mutation against production by mistake: `record` refuses unless `--team` names the sandbox team.
* Binary responses (attachments): stored as base64 with size cap 1 MB.

**Dependencies**

Hard: PAP-13. Soft: PAP-107, PAP-300, PAP-91.

* Soft dependency (round 4): PAP-105 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-105's (2026-09-24); build against its interface and reconcile when it lands.
* Soft dependency (round 4): PAP-93 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-93's (2026-09-20); build against its interface and reconcile when it lands.
* Soft dependency (round 4): PAP-94 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-94's (2026-09-20); build against its interface and reconcile when it lands.
* Soft dependency (round 4): PAP-97 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-25) is later than PAP-97's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Sentinel (Code Reviewer) with Atlas (Dispatcher) for the Linear shapes. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
