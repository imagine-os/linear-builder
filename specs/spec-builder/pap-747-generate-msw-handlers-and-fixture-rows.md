---
identifier: "PAP-747"
title: "Generate MSW handlers and fixture rows from the data section for Storybook stories, the editor preview and Gate 3 story capture"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-312", "PAP-314"]
blocks: []
key: "r4/spec-builder/msw-fixtures-from-data"
url: "https://linear.app/paperos/issue/PAP-747/generate-msw-handlers-and-fixture-rows-from-the-data-section-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:36.361Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-26"
cycle: null
---

# PAP-747: Generate MSW handlers and fixture rows from the data section for Storybook stories, the editor preview and Gate 3 story capture

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Generated stories (PAP-314), conformance tests (PAP-122) and the editor preview (PAP-378) each mock data hooks their own way with `vi.fn` or `vi.mock`. Generate one MSW handler set and deterministic fixture rows per page from the `data` section, so every consumer renders the same success, empty and error states and Gate 3 screenshots stay stable.

**Scope**

In: generator `mocks` in `packages/spec/src/codegen/mocks.ts` writing `apps/web/src/generated/__mocks__/<id>.handlers.ts` (MSW 2 `http` handlers for the oRPC procedures the page's queries and mutations map to) and `<id>.fixtures.ts` (rows typed from the API contract, generated with a fixed seed and the entity field grammar); story decorators in PAP-314's stories template switching handler sets per state (`success`, `empty`, `error`, `slow`); `docs/spec/mocks.md`. Out: E2E seeds (PAP-240 owns the real database), shape mocking for `live|local` beyond a static snapshot.

**Spec**

* Fixture rows respect field constraints (PAP-742, entity grammar): enum values from options, dates within the last 90 days, currency as decimal strings, relations resolving to sibling fixtures; 12 rows by default, `x-mock-rows` overrides.
* Handlers: `list` paginates with signed-looking cursors, `get` by id, `create|update` echo with optimistic ids, `error` set returns the PAP-267 error body with `VALIDATION` or `FORBIDDEN`; `slow` adds 1500 ms.
* `live|local` queries: a `useShape` mock provider returning the fixture rows as a snapshot with `isStale: false`; documented as the one place shapes are faked.
* PAP-378 preview imports the same handlers inside its iframe (worker-registered MSW) so preview and stories never diverge; PAP-122 keeps `vi.mock` but points it at the generated fixtures.
* Deterministic: same spec hash, same rows; Gate 3 story capture (PAP-246) relies on it for baseline stability.

**Interface contract**

Provides: `mocks` generator, generated handlers and fixtures, story decorator `withSpecMocks(state)`, `useShape` mock provider. Consumes: hook and procedure mapping (PAP-312), stories template (PAP-314), API contract types (PAP-268), error body (PAP-267), entity grammar and constraints (soft), Storybook (PAP-69), preview (PAP-378), story capture (PAP-246). Consumed by: PAP-316 example screenshots, PAP-378, PAP-122, PAP-246, PAP-125 docs screenshots.

**Definition of done**

* Three example pages render all four states in Storybook from generated mocks; PAP-378 preview uses them; two runs byte-identical.
* Screenshots of the four states at 375 and 1280; `docs/spec/mocks.md`; CHANGELOG entry.

**Test plan**

* Unit: fixture generation per field type and constraint, handler responses per state, determinism.
* Integration: Storybook interaction test loads a story per state; preview worker registers handlers.
* E2E: Gate 3 story capture on the example stories is stable across three runs.

**Demo**

Open `Generated/customer-invoices` in Storybook, switch the state toolbar to `error`, then `slow`, then open the editor preview and see the same rows. Under one minute.

**Edge cases**

* Procedure hand-written (not generated): handler stub generated with a `TODO` body returning `[]`.
* Fixture relation cycle: depth-limited to 2 hops.
* Page with 40 queries: handlers still generated; story loads under 2 s (asserted).

**Dependencies**

Hard: PAP-312, PAP-314. Soft: PAP-739, PAP-742, PAP-268, PAP-267, PAP-69, PAP-378, PAP-246, PAP-122.

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/entity-field-grammar` = PAP-739, `r4/spec-builder/mutation-input-constraints` = PAP-742.
