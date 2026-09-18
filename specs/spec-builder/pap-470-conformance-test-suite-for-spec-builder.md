---
identifier: "PAP-470"
title: "Conformance test suite for spec-builder contract"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Review"
priority: 2
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-441", "PAP-467", "PAP-541"]
blocks: ["PAP-473"]
key: "module/spec-builder/conformance"
url: "https://linear.app/paperos/issue/PAP-470/conformance-test-suite-for-spec-builder-contract"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:04.606Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-26"
cycle: null
---

# PAP-470: Conformance test suite for spec-builder contract

**Model / Effort:** Opus 5 / high

**Goal**

Give `@paperos/contract-spec-builder` an executable meaning: a Vitest suite that any implementation of the spec-builder ports must pass, plus the golden fixtures both old and new implementations are diffed against during a swap (`docs/module-system.md` section 5). Without this, "plug and play" is a promise; with it, `paperos module conformance spec-builder --impl a,b` is a fact the gates can check.

**Scope**

In:

* `packages/contracts/spec-builder/conformance/`: `defineConformanceSuite('spec-builder', factory)` covering every port exported at v0.1, one `describe` per port, one `it` per fixture; `unsupported` capability handling so partial adapters report honestly.
* `fixtures/`: the three fully specified example pages (PAP-125), one `app.spec.yaml`, eight invalid specs (one per rule family), two flow graphs, one generator run manifest; every fixture validated against the contract schemas in CI.
* In-memory reference doubles (`memory/` inside `conformance/`) for the data-bearing ports so the suite runs without Postgres, Stripe, Hocuspocus or network.
* Registration with the conformance runner (`module-system/conformance-runner`): suite id, ports, fixture manifest, expected duration.
* `conformance.json` output per run in the PAP-239 artefact shape (pass, fail, pending, unsupported, per-case diff).

Out: the implementation itself; performance budgets (PAP-242); visual checks (Gate 3).

**Spec**

* The suite is parametrised by `factory: () => Promise<Impl>` and a `capabilities` set; a case whose capability is absent is `unsupported`, a case for an `@experimental` port is `pending`; both are visible in the report and neither fails the run unless `--strict`.
* Cases assert behaviour, not shape: for example idempotency (`same key twice yields one row`), ordering guarantees, error codes from the contracts document (`NOT_FOUND` on RLS read denial), event emission with the right topic and version.
* Golden fixtures are immutable within a contract version: adding is a minor bump, changing is a major bump; the runner refuses fixtures whose hash changed without a version bump.
* Runtime under 60 s against the memory doubles, under 5 min against the real adapter on the compose stack.
* Every case id is stable (`spec-builder.<port>.<n>`) so shadow-run diffs and Linear comments can cite it.

**Interface contract**

Provides: `@paperos/contract-spec-builder/conformance` (`defineConformanceSuite`, `memory` doubles, `fixtures` index, `capabilities` list), `conformance.json` artefact for this module. Consumes: `@paperos/contract-spec-builder@0.1` (`module/spec-builder/contract`), the runner and artefact schema (`module-system/conformance-runner`, PAP-239), the PAP-42 compose stack for the real-adapter run, `callAs` from PAP-268 where routes are exercised. Consumed by: `module/spec-builder/wire`, the swap CLI, Gate 1, and every future implementation of the contract.

**Test plan**

* The suite passes against the memory doubles in CI on every PR that touches the contract or the module.
* The suite passes against the real implementation (PAP-115, PAP-314, PAP-312) on the compose stack nightly; failures open a Linear comment on the implementation issue with the case ids.
* Mutation check: one deliberately broken double per port (committed under `conformance/negative/`) fails exactly its cases and no others.
* Fixture validation: every fixture file parses against its schema; hash manifest committed and checked.
* Report: `conformance.json` validates against the PAP-239 schema; the contact sheet reporter lists pass, fail, pending, unsupported counts.

**Definition of done**

* Suite and fixtures merged; memory doubles pass 100 percent; real adapter passes or every failing case has a linked fix issue; negative doubles fail exactly as predicted.
* Registered with the runner; Gate 1 step `conformance:spec-builder` green; `conformance.json` attached to the PR.
* `docs/platform/contracts/spec-builder.md` gains a "Conformance" section listing case ids; Linear comment with the report.

**Edge cases**

* A port that needs a secret (Stripe, X, Linear): the real-adapter run uses recorded HTTP fixtures (`msw` or `nock`), never live credentials in CI; the live run is a nightly job on staging with the credential broker.
* Implementation faster than the fixtures assume (for example cursor pages of different size): cases assert set equality across pages, not page boundaries.
* Nondeterministic output (ids, timestamps): fixtures use placeholders and the runner normalises before diffing.
* An adapter that passes only the memory suite: it is not conformant; the wire issue refuses to bind it.

**Dependencies**

Blocked by `module/spec-builder/contract` and `module-system/conformance-runner`. Blocks `module/spec-builder/wire`. Soft: PAP-115, PAP-314, PAP-312 for the real-adapter run (the memory run is enough to merge).

**Agent**

Built by Sentinel (Quality Lead, conformance owner) with Quill supplying port semantics. Reviewed by Quill and Atlas.

**Size**

M

**Demo**

Reviewer runs the suite against the real validator and codegen and against a stub generator plugin; both pass the schema and diagnostics fixtures; the stub is reported `unsupported` for layout emission, not failed. Two minutes.
