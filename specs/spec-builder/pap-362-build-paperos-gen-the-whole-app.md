---
identifier: "PAP-362"
title: "Build `paperos gen`: the whole-app generation pipeline that runs every generator in dependency order with a manifest, incremental cache, deterministic output and a `--check` drift mode"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-115", "PAP-119", "PAP-120", "PAP-122", "PAP-123"]
blocks: ["PAP-364", "PAP-430"]
key: "gp/spec-builder/gen-pipeline"
url: "https://linear.app/paperos/issue/PAP-362/build-paperos-gen-the-whole-app-generation-pipeline-that-runs-every"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:11.039Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-362: Build `paperos gen`: the whole-app generation pipeline that runs every generator in dependency order with a manifest, incremental cache, deterministic output and a `--check` drift mode

**Goal**

One command regenerates everything derived from specs: `paperos gen` runs the app generator (PAP-117), entity-derived page specs, data hooks (PAP-119), page scaffolds (PAP-120), conformance tests (PAP-122), access policies (PAP-116 to PAP-59), the flow graph (PAP-123), i18n catalogs (PAP-27) and the seed, in dependency order, incrementally, deterministically, and reports drift in CI. It is checkpoint C3 of the golden path and the thing every agent runs after editing a spec.

**Scope**

In:

* `packages/spec/src/pipeline/` with `registry.ts` (generators declare `id`, `inputs` globs, `outputs` globs, `dependsOn`), `runner.ts` (topological order, parallel where independent, per-generator timing), `manifest.ts` (`.paperos/gen-manifest.json` with input hashes, output hashes and generator versions), `check.ts` (`--check`: run in a temp dir and diff against the tree).
* CLI `paperos gen [--only <id>] [--check] [--force] [--json]` in `packages/cli` and `pnpm gen` script; `--json` prints the per-generator timing table used by the golden path report.
* Generators registered in this issue: `app`, `entity-pages`, `data-hooks`, `page-scaffolds`, `conformance`, `access-policies`, `flow-graph`, `i18n`, `seed`; each existing generator gets a ten-line adapter file, no rewrites.
* Incremental mode: a generator runs only when an input hash or its own version changed; `--force` ignores the manifest.
* Post-emit: Biome format on all outputs (as PAP-120 does), banner with spec hash, `generated/` folders listed in `.gitattributes` as `linguist-generated` and in CODEOWNERS for Sentinel.
* Gate 1 job `gen-check` (PAP-78) replacing the per-generator drift jobs of PAP-120 and entity-pages.

Out: the generators' own templates, watch mode (later), remote caching.

**Spec**

* Determinism contract: two runs on the same inputs produce byte-identical outputs; a determinism test runs the pipeline twice in CI and diffs.
* Order is derived, not configured: `app` before `entity-pages` before `data-hooks` and `page-scaffolds` before `conformance` and `flow-graph`; `i18n` and `seed` after `page-scaffolds`; a cycle in `dependsOn` fails at startup.
* Errors from one generator stop dependents but not siblings; the exit code is 1 with a table of failed generators; partial outputs are rolled back from a temp dir so the tree is never half-written.
* Timing: full run for the 60-page stress fixture under 20 s warm and under 60 s cold on the CI runner; each generator's ms is written to the manifest and, when present, stamped as sub-steps of checkpoint `C3` in `.paperos/golden-path.json`.
* Generator version bump invalidates its outputs only; the manifest schema is versioned and a mismatch triggers `--force` with a notice.
* `--check` output lists stale files and the generator that owns each, ready to paste into a PR comment.

**Interface contract**

Provides: `defineGenerator({ id, version, inputs, outputs, dependsOn, run(ctx) })`, `runPipeline(opts): PipelineReport` and the `PipelineReport` Zod schema (`{ generators: { id, status, ms, outputs }[], totalMs, drift: string[] }`) from `@paperos/spec/pipeline`; the `gen-check` CI job. Consumes: PAP-117 `gen:app`, entity-derived page specs generator, PAP-119 `gen:data`, PAP-120 `gen:page`, PAP-122 conformance generator, PAP-123 flow graph, PAP-116 policy compiler (soft: skipped when absent), PAP-27 extraction (soft), PAP-115 validator (runs first, aborts on errors). Consumed by: golden path driver, golden path acceptance test, `paperos upgrade`, PAP-29, every agent session via `pnpm gen`.

**Test plan**

* Unit: topological order with a fixture registry; cycle detection; incremental skip when hashes match; version bump reruns exactly one generator.
* Determinism: run twice, `git diff --exit-code` between outputs.
* Failure isolation: a generator that throws leaves the tree untouched (temp dir rollback) and marks dependents `skipped`.
* Integration: full run on the clinic fixture produces a tree that passes `pnpm check`; `--check` after touching one spec names exactly the outputs that changed.
* Performance: stress fixture timed in CI with a 20 s warm budget.

**Definition of done**

* Pipeline merged with the nine adapters; `pnpm gen` and `pnpm gen --check` documented in CLAUDE.md as the post-spec-edit command.
* `gen-check` job green on the template repo and the three canned apps; old per-generator drift jobs removed.
* Determinism and rollback tests in CI; stress fixture under budget.
* `docs/spec/codegen.md` extended with the pipeline section and the manifest format; CHANGELOG; Linear comment with the timing table.

**Edge cases**

* A generator writes outside its declared `outputs`: detected by diffing the temp dir, fails with the offending path (prevents accidental overwrites of human files).
* Manifest missing or corrupt: treated as `--force` with a notice, never an error.
* Two generators declare the same output path: startup error naming both.
* Spec validator warnings but no errors: pipeline runs and prints warnings once, not per generator.
* Running on Windows: paths normalised in hashes so manifests are portable across contributors.

**Dependencies**

Hard: PAP-115, PAP-119, PAP-120, PAP-122, PAP-123. Soft: PAP-116/PAP-59 policy compiler, PAP-27 i18n extraction, PAP-78 gate 1 job slot, entity-derived page specs (adapter added when it merges). Blocks the golden path driver.

**Agent**

Built by Forge (Spec Tooling sub-agent); reviewed by Sentinel (correctness) and Atlas for the CLAUDE.md wording.

**Size**

M: a runner, manifest, nine thin adapters and CI wiring; the generators already exist.

**Demo**

Terminal recording of `paperos gen --json` on the clinic app showing the ordered timing table, then a spec edit and `paperos gen --check` naming the stale files.
