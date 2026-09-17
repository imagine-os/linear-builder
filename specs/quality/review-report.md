---
identifier: "PAP-89"
title: "Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff", "Agent"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-239", "PAP-254", "PAP-88"]
blocks: []
key: "quality/review-report"
url: "https://linear.app/paperos/issue/PAP-89/generate-a-one-page-human-review-digest-per-release-candidate-what"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-89: Generate a one-page human review digest per release candidate: what changed, risks, screenshots, open questions

**Goal**

Generate the one page Justin actually reads for each release candidate: what changed in plain language, what the gates found and how it was resolved, the risks and open questions that need his decision, and the screenshots and replays that let him see the product in under ten minutes. Everything else stays in the machines.

**Scope**

In:
- `packages/agents/src/digest/buildDigest({ from, to, rcBranch })` collecting: merged PRs with Linear issues and characters (forge API and Linear GraphQL), conventional-commit changelog (`collab/changelog` output or `git log` fallback), gate results per PR (`gate1.json`, `security.json`, `visual.json`, `vision.json`, `edgecases.json`, perf tables, e2e reports), waivers granted, open S1 findings, cost spent per project from `pm-linear/credit-metering`, and nightly staging trends.
- A Claude summarisation step (model `claude-fable-5-1`) producing structured sections from the collected JSON, with strict rules: cite the PR or finding ID for every claim, no adjectives without numbers, max 900 words of prose.
- Output formats: Markdown `docs/releases/<version>.md` committed to the repo, an HTML page with embedded screenshots and replay posters published to Pages at `/releases/<version>/`, and a condensed Linear issue body for the Needs Justin item (`quality/release-train`).
- Sections: 1 Decision needed (one paragraph and the two commands); 2 What changed (grouped by project, user-facing first, with before/after screenshots where visual diffs exist); 3 Quality evidence (gate table, counts of findings by severity, fixed vs waived, calibration health); 4 Risks and open questions (each with recommended default and a checkbox); 5 Replays (posters linking to critical flow videos at 375 and 1280); 6 Cost and velocity (credits by project, issues closed, days to next milestone); 7 Appendix links (full reports, changelog, PR list).
- Screenshot selection: pages with visual diffs in the range, current baseline at 375 and 1280 in light theme, plus dark for pages with theme-related changes; max 12 images.

Out: marketing release notes (`growth/content-agent` uses the changelog), tenant-facing changelog rendering, PR-level digests.

**Spec**

- Digest schema `packages/agents/src/digest/digest.schema.ts` (Zod): `{ version, range: { fromSha, toSha, fromDate, toDate }, decision: { ask, approveCommand, rejectCommand, deadline }, changes: [{ project, title, prs: [{ number, url, linearKey, character }], userFacing: boolean, summary, screenshots: [...] }], quality: { gates: [{ name, status, link }], findings: { S0, S1, S2, S3, fixed, waived }, calibration: {...} }, risks: [{ id, title, detail, recommendation, requiresAnswer: boolean }], replays: [...], cost: {...}, links: {...} }`.
- Renderer: Markdown via template literals; HTML via a small static template using the design tokens CSS so it looks like the product; no client JS beyond video posters.
- Summarisation prompt `.claude/agents/digest-writer.md` receives only the schema-shaped data and returns the prose fields; a validation pass checks every cited ID exists in the data, else the sentence is dropped and logged.
- Length checks: prose under 900 words, page renders under 2 screens at 1280 excluding appendix; HTML under 5 MB with images.
- `pnpm digest --from v0.1.0 --to release/2026-39 --out docs/releases/` for local runs; the release workflow calls the same.
- Linear body variant truncates to 4,000 characters with a link to the full page.

**Definition of done**

- Digest generated for a rehearsal range with all seven sections populated from real gate artifacts; HTML published to Pages and Markdown committed (links).
- Citation validator drops a seeded unsupported claim (test).
- Justin reads the rehearsal digest and confirms via a Linear comment it answers his three questions (what changed, is it safe, what do I need to decide); adjust once based on feedback.
- Screenshots at 375, 1280 and 1920 of the HTML digest itself in light and dark attached.
- Vitest for schema, renderer snapshots and length checks; `docs/quality/review-report.md`; CHANGELOG entry; Linear comment with the digest link.

**Edge cases**

- Range with zero user-facing changes: section 2 says so explicitly and leads with infrastructure changes.
- Missing gate artifact for one PR (expired): shown as `unknown` with a link to re-run, never omitted.
- More than 40 PRs in range: group by project and collapse minor ones into counts with a link list.
- Signed replay URLs expired: digest build re-signs or falls back to run artifacts.
- Cost data unavailable: section 6 shows `n/a` with reason; never invented numbers.
- Justin asks a question in the Linear issue: `agents/handoffs` routes it; the digest page links the thread.

**Dependencies**

`quality/release-train` (hard: trigger and inputs). Soft: `quality/playwright-matrix`, `quality/video-replays`, `quality/screenshot-annotation`, `quality/edge-case-hunter`, `quality/perf-budgets`, `collab/changelog`, `pm-linear/credit-metering`, `pm-linear/justin-queue` (comment commands), `app-shell/gh-pages-demo` (hosting).

**Agent**

Built by Sentinel with Quill (Changelog Scribe) owning prose rules and templates. Reviewed by Atlas and, for the rehearsal, Justin himself.

**Size**

M: data collection across many artifacts and one carefully constrained summarisation step.
