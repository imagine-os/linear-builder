---
identifier: "PAP-551"
title: "Schema fixture factory: `fixtureFor(schema, { seed, overrides })` generating valid instances for any contract Zod schema, `invalidFor(schema)` for negatives, used by conformance doubles, Gate 4 and the test kernel"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Contracts and conformance wired"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-302", "PAP-433"]
blocks: []
key: "r4/module-system/schema-fixture-factory"
url: "https://linear.app/paperos/issue/PAP-551/schema-fixture-factory-fixtureforschema-seed-overrides-generating"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:05.673Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-551: Schema fixture factory: `fixtureFor(schema, { seed, overrides })` generating valid instances for any contract Zod schema, `invalidFor(schema)` for negatives, used by conformance doubles, Gate 4 and the test kernel

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Seventeen conformance suites, their memory doubles, the edge-case hunter (PAP-85) and the demo seed (PAP-507) all need valid instances of contract types. Each writing its own generators means seventeen interpretations of `Money`, `ActorRef` and `FilterTree`. One factory that reads the Zod schema and knows the contract-zero types gives every module the same realistic data and a negative generator for free.

**Scope**

In:

* `packages/kernel/fixtures/factory.ts`: `fixtureFor(schema, opts)` walking Zod 4 schemas (objects, arrays with min and max, unions, discriminated unions, enums, literals, records, refinements by retry) with a seeded PRNG (`seedrandom`) and `faker` for strings by `.describe()` hints (`email`, `url`, `name`, `sentence`); registered generators for contract-zero types: UUIDv7 in time order, `Money` in minor units and valid ISO 4217, `ActorRef`, `EntityRef`, `FilterTree` (valid against PAP-279 grammar), signed cursors.
* `invalidFor(schema)` producing one instance per top-level field that violates exactly that field (wrong type, out of range, missing required) with the expected Zod issue path, for negative conformance cases.
* `fixtureSet(schema, n, { unique: ["email"] })` for lists; `pnpm fixtures:gen <contract> <schema> --count 5 --out fixtures/` to materialise golden fixtures (then locked by `fixtures.lock`).
* Docs `docs/platform/fixtures.md` with the hint vocabulary for `.describe()`.

Out: fixture curation per contract (their issues), the lock (PAP-541), UI stories data (PAP-69 may reuse).

**Spec**

* Determinism: same schema, seed and version produce the same instance; the factory version is part of the seed so upgrades are explicit.
* Refinements are satisfied by bounded retry (100 attempts) then a clear error naming the refinement; contract authors add a custom generator via `registerGenerator(schemaId, fn)`.
* Generated strings are readable (faker), never lorem ipsum; dates within the last 90 days unless the hint says otherwise.
* Performance: 1,000 instances of a 30-field object under 200 ms.

**Interface contract**

Provides: `fixtureFor`, `invalidFor`, `fixtureSet`, `registerGenerator`, `pnpm fixtures:gen`, the hint vocabulary; consumed by every conformance suite and memory double, PAP-85 (Gate 4 adversarial inputs seeded from `invalidFor`), PAP-240 and PAP-507 (value generators), PAP-122 (conformance test data), PAP-545.

Consumes: contract layout and Zod 4 (PAP-433), contract-zero types (PAP-302), filter grammar (PAP-279), cursor format (PAP-279).

**Definition of done**

* Every schema exported by `contract-sample` and `contract-data-layer` fixtures produces valid instances (parse round trip) and `invalidFor` produces exactly one failing path per field (tests).
* `pnpm fixtures:gen` materialises the sample fixtures byte-identically across two runs; doc merged; Linear comment.

**Test plan**

* Unit: each Zod kind; contract-zero generators validate against their schemas; refinement retry and failure; determinism; `invalidFor` path assertions.
* E2E: sample conformance suite uses factory output for its memory double and passes.

**Demo**

Reviewer runs `pnpm fixtures:gen sample Greeting --count 3 --seed demo` and reads three realistic greetings with UUIDv7 ids and recent timestamps, then `invalidFor(Greeting)` printing the four violating instances with their paths. Under a minute.

**Edge cases**

* Recursive schema (`FilterTree`): depth capped at 4 with leaves at the cap.
* `z.bigint()` at runtime (PAP-302 minor units): generated as bigint, serialised through the codec when written to JSON.
* Schema with `.transform()`: factory generates the input type; output type is obtained by parsing.

**Dependencies**

Hard: PAP-433, PAP-302. Soft: PAP-279, PAP-85, PAP-240, PAP-542.

**Agent**

Builder: Sentinel (Edge Case Hunter sub-agent as builder) with Forge. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/app-shell/starter-kit-demo-seed` = PAP-507, `r4/module-system/conformance-normaliser` = PAP-541, `r4/module-system/sample-module` = PAP-542, `r4/module-system/test-kernel` = PAP-545.
