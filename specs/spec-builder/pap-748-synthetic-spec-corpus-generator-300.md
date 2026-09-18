---
identifier: "PAP-748"
title: "Synthetic spec corpus generator: 300 valid page specs and 60-page stress apps for validator, pipeline, editor and diff benchmarks"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114"]
blocks: ["PAP-751"]
key: "r4/spec-builder/spec-fixture-corpus"
url: "https://linear.app/paperos/issue/PAP-748/synthetic-spec-corpus-generator-300-valid-page-specs-and-60-page"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:36.492Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-748: Synthetic spec corpus generator: 300 valid page specs and 60-page stress apps for validator, pipeline, editor and diff benchmarks

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Infra S

**Goal**

Five specs measure themselves against fixtures nobody generates: 300 specs under 2 s (PAP-115), a 60-page stress fixture under 20 s (PAP-362), 60 pages times three audiences under 5 s (PAP-361), a 300-component spec in the editor (PAP-377) and 300 pages under 5 s for the graph (PAP-123). Ship one seeded generator so every benchmark, and the weekly rehearsal PAP-114 named, uses the same corpus.

**Scope**

In: `packages/spec/fixtures/generate.ts` with a fixed seed writing `packages/spec/fixtures/corpus/{small,medium,large}/` (10, 60 and 300 pages plus a matching `app.spec.yaml` per size) and one `maximal.spec.yaml` (300 components, every section, 12-level tree); `pnpm spec fixtures:build` and a committed hash manifest; `bench/` scripts wrapping `hyperfine` for the validator, pipeline and graph; `docs/spec/fixtures.md`. Out: the benchmarks' pass thresholds (owned by the consuming issues), business seed packs (PAP-207).

**Spec**

* Corpus shape: audiences `customer.basic`, `staff.admin`, `agent.builder`; entities scale with size (5, 20, 60) using the field grammar when merged, else the frozen union; pages are 60 percent list or detail, 20 percent forms, 20 percent dashboards and settings; every page has `access`, `data`, three edge cases and at least one `events[]` transition so graphs are connected.
* All generated specs validate with zero warnings under PAP-115 `--strict`; the generator fails its own build otherwise.
* Deterministic: same seed, same bytes; the manifest lists sha256 per file; regenerating with a new schema version bumps `corpusVersion` and is a normal PR.
* Sizes stay under 10 MB total committed; `large` is generated on demand in CI (`fixtures:build --size large`) and cached.
* Bench scripts print a table and write `bench/results/<tool>.json` the consuming issues paste into their Linear comments.

**Interface contract**

Provides: corpus folders, `generateCorpus({ size, seed })`, hash manifest, `pnpm spec fixtures:build`, bench scripts. Consumes: `PageSpecSchema` and `AppSpecSchema` (PAP-114, PAP-117), validator (PAP-115, soft), field grammar (soft), `hyperfine` (dev dependency). Consumed by: PAP-115, PAP-362, PAP-361, PAP-377, PAP-123, PAP-743, PAP-470 conformance fixtures (subset), the weekly rehearsal in PAP-306.

**Definition of done**

* Corpus committed for small and medium, generated for large in CI; every spec validates strict; bench scripts run on the template repo and print timings.
* `docs/spec/fixtures.md`; comments on PAP-115, PAP-362, PAP-361, PAP-377 and PAP-123 naming the corpus paths; CHANGELOG entry.

**Test plan**

* Unit: determinism (two runs equal), validity under strict, distribution of page kinds, manifest check.
* Integration: `pnpm spec:validate fixtures/corpus/medium` green; `gen:graph` on medium renders a connected graph.
* E2E: none.

**Demo**

Run `pnpm spec fixtures:build --size large && pnpm bench:validate`, read the 300-spec timing, open one generated spec and see a complete, boring page. Under one minute.

**Edge cases**

* Schema change breaks the corpus: CI fails on the generator, which is the point; regenerate and review the diff summary.
* Corpus page ids collide with real pages: namespaced `fx-`.
* Field grammar unmerged: frozen union with a TODO and a drift test.

**Dependencies**

Hard: PAP-114. Soft: PAP-117, PAP-115, PAP-739.

**Agent**

Builder: Quill (Page Spec Writer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/entity-field-grammar` = PAP-739, `r4/spec-builder/spec-diff-pr-comment` = PAP-743.
