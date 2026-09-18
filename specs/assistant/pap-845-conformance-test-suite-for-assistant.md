---
identifier: "PAP-845"
title: "Conformance test suite for assistant contract"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Review"
priority: 4
surfaces: ["Developer"]
milestone: "Business characters, evals and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-42", "PAP-239", "PAP-441", "PAP-833"]
blocks: ["PAP-846"]
key: "r4/assistant/conformance"
url: "https://linear.app/paperos/issue/PAP-845/conformance-test-suite-for-assistant-contract"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:53.614Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: null
cycle: null
---

# PAP-845: Conformance test suite for assistant contract

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review M

**Goal**

Give `@paperos/contract-assistant` an executable meaning: a Vitest suite that any implementation of the assistant ports must pass, plus the golden fixtures both old and new implementations are diffed against during a swap (`docs/module-system.md` section 5). Without this, "plug and play" is a promise; with it, `paperos module conformance assistant --impl a,b` is a fact the gates can check.

**Scope**

In: `packages/contracts/assistant/conformance/`: `defineConformanceSuite('assistant', factory)` covering every port exported at v0.1, one `describe` per port, one `it` per fixture; `unsupported` capability handling so partial adapters report honestly. `fixtures/`: four conversations (console, portal, view, record), twelve message part fixtures, six tool calls across the status machine, eight grounding results with citations, three tenant characters, two provider capability sets; every fixture validated against the contract schemas in CI. In-memory reference doubles (`memory/` inside `conformance/`) for the data-bearing ports so the suite runs without Postgres, Stripe, Twilio, Hocuspocus or network. Registration with the conformance runner (PAP-441): suite id, ports, fixture manifest, expected duration; `conformance.json` output per run in the PAP-239 artefact shape (pass, fail, pending, unsupported, per-case diff).

Out: The implementation itself. Performance budgets (PAP-242). Visual checks (Gate 3).

**Spec**

* The suite is parametrised by `factory: () => Promise<Impl>` and a `capabilities` set; a case whose capability is absent is `unsupported`, a case for an `@experimental` port is `pending`; both are visible in the report and neither fails the run unless `--strict`
* Cases assert behaviour, not shape: idempotency (same key twice yields one row or one send), ordering guarantees, permission filtering (a principal without the audience sees nothing), error codes from the contracts document, event emission with the right topic and version
* Golden fixtures are immutable within a contract version: adding is a minor bump, changing is a major bump; the runner refuses fixtures whose hash changed without a version bump
* Runtime under 60 s against the memory doubles, under 5 min against the real adapter on the compose stack
* Every case id is stable (`assistant.<port>.<n>`) so shadow-run diffs and Linear comments can cite it

**Interface contract**

Provides: `@paperos/contract-assistant/conformance` (`defineConformanceSuite`, `memory` doubles, `fixtures` index, `capabilities` list), `conformance.json` artefact for this module. Consumes: `@paperos/contract-assistant@0.1`, the runner and artefact schema (PAP-441, PAP-239), the PAP-42 compose stack for the real-adapter run, `callAs` from PAP-268 where routes are exercised. Consumed by: PAP-846, the swap CLI (PAP-442), Gate 1, and every future implementation of the contract.

**Definition of done**

* Suite and fixtures merged; memory doubles pass 100 percent; real adapter passes or every failing case has a linked fix issue; negative doubles fail exactly as predicted
* Registered with the runner; Gate 1 step `conformance:assistant` green; `conformance.json` attached to the PR
* `docs/platform/contracts/assistant.md` gains a "Conformance" section listing case ids
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* The suite passes against the memory doubles in CI on every PR that touches the contract or the module.
* The suite passes against the real implementation on the compose stack nightly; failures open a Linear comment on the implementation issue with the case ids.
* Mutation check: one deliberately broken double per port (committed under `conformance/negative/`) fails exactly its cases and no others.
* Fixture validation: every fixture file parses against its schema; hash manifest committed and checked.
* Report: `conformance.json` validates against the PAP-239 schema; the contact-sheet reporter lists pass, fail, pending, unsupported counts.

**Demo**

`paperos module conformance assistant --impl memory,default` prints two green columns and the case ids, then a deliberately broken negative double turns exactly its cases red.

**Edge cases**

* A port that needs a secret (Stripe, Twilio, Google Calendar, Anthropic): the real-adapter run uses recorded HTTP fixtures (`msw`), never live credentials in CI; the live run is a nightly job on staging through the credential broker (PAP-300)
* Nondeterministic output (ids, timestamps, model text): fixtures use placeholders and normalisers; assistant and drafting ports assert structure and citations, not prose

**Dependencies**

PAP-833 (hard), PAP-441 runner and PAP-239 artefact schema (hard), PAP-42 compose stack (soft, real-adapter run only).

**Agent**

Builder: Sentinel. Reviewer: Atlas (Merger).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/assistant/contract-publish` = PAP-833, `r4/assistant/wire` = PAP-846.
