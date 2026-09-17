---
identifier: "PAP-209"
title: "Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Evaluation process"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-211", "PAP-212", "PAP-213", "PAP-214", "PAP-215", "PAP-216", "PAP-292", "PAP-295", "PAP-350", "PAP-493"]
key: "libraries/eval-rubric"
url: "https://linear.app/paperos/issue/PAP-209/define-the-library-evaluation-rubric-license-maintenance-bundle-size"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:56.716Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-209: Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Define the single rubric and ADR table every "should we adopt X" question in PaperOS is answered with, so twenty parallel sessions score libraries the same way and Atlas can compare ADRs from different characters. Six research issues already cite it (PAP-31, PAP-56, PAP-127, PAP-139, PAP-188, PAP-182); this issue makes it real and machine-checkable.

**Scope**

In:

* `docs/libraries/rubric.md`: six criteria (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness), 0-4 anchors, default weights, hard-fail gates, rule for domain extras.
* `packages/spec/libraries/rubric.yaml` with Zod 4 schema `packages/spec/src/libraries/rubric.ts` (`RubricSchema`, `ScorecardSchema`).
* `docs/libraries/scorecard.template.yaml` and CLI `pnpm lib score <scorecard.yaml>`: validate, compute weighted totals, render the Alternatives table ADRs paste in.
* Facts collector `scripts/lib-facts.ts` (npm downloads, last publish, stars, last commit, median issue age, `license`, `types`, gzipped size via esbuild metafile) writing `facts.json`; cache `.cache/lib-facts/`, `GITHUB_TOKEN` support.
* ADR template additions (Alternatives table, Re-open criteria) in `docs/adr/template.md`, created here if PAP-130 has not merged.
* Worked example: TanStack Table v8 versus AG Grid Community under `docs/libraries/examples/`.

Out: the surveys (PAP-212, PAP-213, PAP-214), license mechanics (PAP-211), registry UI (PAP-216).

**Spec**

* Weights (sum 100): license 20, maintenance 20, bundle 15, a11y 15, TS 15, agent-friendliness 15; `n/a` criteria drop and the rest rescale, recorded on the scorecard.
* Anchors, examples: maintenance 4 = release in 90 days, 3+ maintainers or company backing, median first response under 14 days; 0 = archived or 18 months silent. Bundle 4 = under 10 KB gzipped for used imports, 0 = over 250 KB. Agent-friendliness 4 = Markdown docs or `llms.txt`, typed examples, typed errors, small surface, well known to Claude.
* Hard gates (any fail = `reject`): license outside PAP-211 allow tier without waiver; no types; UI library failing in Tauri WebViews; vendor cloud with no self-host path.
* Scorecard `{ candidate, version, evaluatedBy, date, issue, facts, scores: { <id>: { score, evidence } }, extras[], gates, migrationCostHours, verdict: adopt|trial|reject }`; scores of 3 or 4 need a URL or repo path in `evidence` or the CLI fails.
* Ties within 5 points decided by `migrationCostHours` and the owning character's written judgement, never re-scoring.

**Interface contract**

Provides: `RubricSchema`, `ScorecardSchema`, `pnpm lib score` (also `--facts-only` for PAP-218 pre-scores), `scripts/lib-facts.ts` and `facts.json` shape, the ADR sections, `docs/libraries/scorecards/` as the canonical scorecard folder every research issue writes into. Consumes: PAP-211 tiers for the license gate (draft acceptable), PAP-130 ADR frontmatter (soft). Consumers: PAP-211, PAP-212, PAP-213, PAP-214, PAP-215, PAP-216 (facts and scorecard paths), PAP-218, and the six research issues above.

**Definition of done**

* Rubric doc, `rubric.yaml`, schemas, template and CLI merged.
* Worked example committed; rendered table matches its snapshot.
* `docs/adr/template.md` carries both sections consistent with PAP-130 frontmatter.
* Atlas approves weights and gates; Iris confirms a11y anchors; Sentinel passes the CLI.
* CHANGELOG; Linear comment linking rubric and example; one comment on each of the six research issues with final paths.

**Test plan**

* Vitest: schema validation, rescaling on `n/a`, gate logic, evidence rule failure, tie rule, Markdown rendering snapshot, facts collector against recorded npm and GitHub responses.
* CLI smoke in Gate 1: `pnpm lib score docs/libraries/examples/*.yaml` exits 0.
* Docs lint: every anchor cell in `rubric.md` is non-empty (table parser test).

**Demo**

Reviewer runs `pnpm lib score docs/libraries/examples/tanstack-vs-aggrid.yaml`, reads the weighted table, then removes an `evidence` URL and reruns to see the CLI fail with the criterion named. Under one minute.

**Edge cases**

* Monorepo library: score only imported packages, list them in `facts`.
* Non-npm candidate (crate, Docker image, SaaS): [crates.io](<http://crates.io>) or Docker Hub facts; size `n/a`.
* Open-core (tldraw watermark, AG Grid Enterprise): score the free tier, list excluded features.
* Single maintainer: maintenance capped at 2 unless backed.
* GitHub rate limited in CI: facts older than 7 days warn, not fail.

**Dependencies**

None; ready now. Blocks PAP-211, PAP-212, PAP-213, PAP-214, PAP-215, PAP-216. Soft: PAP-130.

**Agent**

Written by Scout (Library Evaluator). Reviewed by Atlas (weights, gates) and Sentinel (Code Reviewer).

**Size**

S: one document, one small schema and CLI, one fixture; the value is sharp anchors.
