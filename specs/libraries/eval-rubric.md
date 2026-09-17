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
blocks: ["PAP-211", "PAP-212", "PAP-213", "PAP-214", "PAP-215", "PAP-216"]
key: "libraries/eval-rubric"
url: "https://linear.app/paperos/issue/PAP-209/define-the-library-evaluation-rubric-license-maintenance-bundle-size"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-209: Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template

**Goal**

Define the single rubric and ADR table format every "should we adopt X" question in PaperOS is answered with, so that twenty parallel sessions score libraries the same way and Atlas can compare ADRs written by different characters. Six research issues already cite this rubric (`data-layer/sync-research`, `identity/auth-research`, `collab/collab-research`, `realtime/realtime-research`, `growth/growth-research`, `business-core/payroll-research`); this issue makes it real and machine-checkable.

**Scope**

In:
- `docs/libraries/rubric.md`: six core criteria (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness), 0-4 scale with written anchors per score, default weights, hard-fail gates, and the rule for adding domain-specific extra criteria.
- Machine-readable rubric `packages/spec/libraries/rubric.yaml` with Zod 4 schema `packages/spec/src/libraries/rubric.ts` (`RubricSchema`, `ScorecardSchema`).
- Scorecard template `docs/libraries/scorecard.template.yaml` and CLI `pnpm lib score <scorecard.yaml>` that validates, computes weighted totals and renders the Alternatives Markdown table ADRs paste in.
- Facts collector `scripts/lib-facts.ts` (npm downloads, last publish, GitHub stars/last commit/open-issue median age, `license` field, `types` field, gzipped size of the imported entry points via a local esbuild `--metafile` run) writing `facts.json` so scorecards cite facts, not guesses.
- ADR template additions (Alternatives table columns, Re-open criteria section) in `docs/adr/template.md`, created here if `collab/decision-log` has not merged.
- One worked example: TanStack Table v8 vs AG Grid Community, under `docs/libraries/examples/`.

Out: the surveys themselves (`libraries/ui-landscape`, `data-landscape`, `backend-landscape`), the license allow/deny mechanics (`libraries/license-policy`), the registry UI (`libraries/registry`).

**Spec**

- Default weights (sum 100): license 20, maintenance 20, bundle size 15, accessibility 15, TypeScript quality 15, agent-friendliness 15. A criterion marked `n/a` (a11y for a server library, bundle size for a Docker image) is dropped and remaining weights rescale proportionally; the scorecard records the rescaled weights.
- Anchors, examples: maintenance 4 = release in the last 90 days, 3+ active maintainers or company backing, median issue first-response under 14 days; 0 = archived or no release in 18 months. Bundle size 4 = under 10 KB gzipped for the imports used, 0 = over 250 KB. Agent-friendliness 4 = plain-Markdown docs or `llms.txt`, TypeScript examples, stable API with typed errors, small surface, widely known so Claude writes it correctly without docs.
- Hard gates (any failure = verdict `reject` regardless of score): license outside `libraries/license-policy` allow tier with no approved waiver; no types for a runtime JS library; UI library that does not run in Tauri WebViews (WebView2, WKWebView, webkit2gtk); requires a vendor cloud with no self-host path.
- Scorecard YAML: `{ candidate, version, evaluatedBy, date, issue, facts, scores: { <criterionId>: { score, evidence } }, extras: [{ id, weight, score, evidence }], gates: { <gateId>: pass|fail|n/a }, migrationCostHours, verdict: adopt|trial|reject }`. Every score of 3 or 4 must cite a URL or repo path in `evidence`; the CLI fails otherwise.
- Extras rule: a research issue may add criteria with explicit weights; core weights scale down so the total stays 100, keeping ADRs comparable across domains.
- Tie rule: candidates within 5 points are decided by `migrationCostHours` to the runner-up and by the owning character's judgement written in the ADR, never by re-scoring.
- Facts collector caches to `.cache/lib-facts/` and accepts `GITHUB_TOKEN` to avoid rate limits.

**Definition of done**

- Rubric doc, `rubric.yaml`, Zod schemas, scorecard template and `pnpm lib score` merged in paperos-template.
- Vitest: schema validation, weight rescaling on `n/a`, gate logic, evidence rule, Markdown table rendering snapshot.
- Worked example committed and rendered table matches the snapshot.
- `docs/adr/template.md` contains Alternatives table and Re-open criteria sections consistent with `collab/decision-log` frontmatter.
- Atlas approves weights and gates; Iris confirms the a11y anchors; Sentinel Code Reviewer passes the CLI.
- CHANGELOG entry; Linear comment linking rubric and example; one comment on each of the six research issues pointing at the final paths.

**Edge cases**

- Monorepo library with many entry points: score only the packages imported and list them in `facts`.
- Non-npm candidate (Rust crate, Docker image, SaaS API): collector pulls crates.io or Docker Hub facts; size `n/a`.
- Dual-licensed or open-core (tldraw watermark, AG Grid Enterprise): score the free tier only and list excluded paid features.
- Single-maintainer project: maintenance capped at 2 unless foundation or company backed.
- Whole product rather than library: rubric applies with the extras defined in `libraries/oss-products`.
- GitHub API rate limited in CI: cached facts older than 7 days produce a warning, not a failure.

**Dependencies**

None; ready now. Consumed by every research issue, `libraries/license-policy`, `libraries/registry`, `libraries/scout-agent`. Soft: `collab/decision-log` (adopts the template sections if it merges later).

**Agent**

Written by Scout (Library Evaluator). Reviewed by Atlas (weights, gates) and Sentinel (Code Reviewer for CLI and tests).

**Size**

S: one document, one small schema and CLI, one fixture; the value is in the anchors being sharp.
