---
identifier: "PAP-541"
title: "Conformance output normaliser and fixture lock: placeholder rules for UUIDv7, timestamps and signed cursors, set ordering, per-port overrides and `fixtures.lock` hashing shared with shadow diffs"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Kernel and lint live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-302", "PAP-433", "PAP-441", "PAP-542"]
blocks: ["PAP-435", "PAP-442", "PAP-450", "PAP-451", "PAP-452", "PAP-457", "PAP-460", "PAP-463", "PAP-468", "PAP-469", "PAP-470", "PAP-477", "PAP-478", "PAP-479", "PAP-486", "PAP-487", "PAP-488", "PAP-494", "PAP-495", "PAP-538", "PAP-539", "PAP-543", "PAP-545"]
key: "r4/module-system/conformance-normaliser"
url: "https://linear.app/paperos/issue/PAP-541/conformance-output-normaliser-and-fixture-lock-placeholder-rules-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:38.476Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-22"
cycle: null
---

# PAP-541: Conformance output normaliser and fixture lock: placeholder rules for UUIDv7, timestamps and signed cursors, set ordering, per-port overrides and `fixtures.lock` hashing shared with shadow diffs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-441 bundles the suite API, the CLI, the artefact and the normaliser; the normaliser is the one piece PAP-435 (shadow diffs) also needs and it depends on the wire encodings from PAP-302, not on the runner. Splitting it lets the flag swap and the runner proceed in parallel and guarantees both speak the same diff language.

**Scope**

In:

* `packages/kernel/conformance/normalise.ts`: `normalise(value, rules)` replacing UUIDv7 (`<id:n>` stable within one payload), ISO timestamps (`<ts>`), signed keyset cursors from PAP-279 (`<cursor>`), `Money` strings kept verbatim (PAP-302), sorting arrays declared `unordered` by a stable key, dropping fields declared `volatile`.
* Rule declaration per port in the suite: `describePort(name, { unordered: ["rows"], volatile: ["latencyMs"], keyBy: { rows: "id" } })`; defaults cover the contracts document §1 types.
* `fixtures.lock`: SHA-256 per fixture file and per contract version; `loadFixtures()` refuses a changed hash without a contract version bump (`FIXTURE_CHANGED`); `pnpm fixtures:lock` regenerates.
* Shared export used by PAP-435 to hash primary and secondary results (`primary_hash`, `secondary_hash`) and by PAP-442 shadow gate.

Out: suite API, CLI, artefact schema and Gate 1 step (PAP-441 sibling), per-module suites.

**Spec**

* Normalisation is deterministic and pure; two runs over the same payload produce identical JSON text.
* Placeholders are stable within a payload so relational references survive (`<id:1>` referenced twice stays `<id:1>`).
* Unknown volatile fields must be declared; the normaliser never guesses by name.
* Performance: 1 MB payload under 50 ms.

**Interface contract**

Provides: `normalise`, `describePort` rule shape, `fixtures.lock` and `pnpm fixtures:lock`, `FIXTURE_CHANGED`; consumed by PAP-441 (runner), PAP-435 (shadow hashes), PAP-442 (shadow gate), every `Conformance test suite` issue (PAP-450, PAP-452 and siblings).

Consumes: wire encodings and `Money` (PAP-302), cursor format (PAP-279), Zod schemas of fixtures (PAP-433).

**Definition of done**

* Fixture payloads with ids, timestamps, cursors and unordered rows normalise to golden text; hash refusal test; PAP-435 imports the same function (import check in lint).
* `docs/platform/conformance.md` normalisation section; Linear comment.

**Test plan**

* Unit: placeholder stability; unordered sort by key; volatile drop; cursor and Money handling; lock regeneration and refusal.
* E2E: sample suite (PAP-542) run twice yields byte-identical `conformance.json` results.

**Demo**

Reviewer runs `pnpm tsx packages/kernel/conformance/normalise.ts fixtures/sample/rows.json` and sees ids and timestamps replaced while row order is sorted by id; edits a fixture and `pnpm conformance sample` fails with `FIXTURE_CHANGED`. Under a minute.

**Edge cases**

* Nested unordered arrays: rules apply by JSON path; a missing path is a declaration error, not silent.
* Timestamp inside a string message: not replaced (only whole-value ISO strings), documented.
* BigInt at runtime (PAP-302 `Money` minor units): serialised through the codec before normalisation.

**Dependencies**

Hard: PAP-302. Sibling: PAP-441. Soft: PAP-279, PAP-433. Blocks PAP-435.

**Agent**

Builder: Sentinel (Code Reviewer sub-agent as builder) with Forge. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/sample-module` = PAP-542.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-441 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-441 blocks this issue (`blocks` relation).
