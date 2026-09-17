---
identifier: "PAP-130"
title: "Add an ADR/decision log with status, alternatives and links to issues"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Docs and prompt log stores"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128"]
blocks: []
key: "collab/decision-log"
url: "https://linear.app/paperos/issue/PAP-130/add-an-adrdecision-log-with-status-alternatives-and-links-to-issues"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:28.676Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-130: Add an ADR/decision log with status, alternatives and links to issues

**Goal**

Give every significant choice a findable, linked record: ADR files with strict frontmatter, a CLI to create and lint them, an in-app index with status and supersession graph, and Linear comments when a decision changes. The plan's fifteen decisions become entries 0001 to 0015.

**Scope**

In:

* Format `docs/adr/NNNN-PAP-<issue>-<slug>.md`; frontmatter (Zod 4 `AdrFrontmatter`): `id`, `title`, `status: proposed|accepted|rejected|superseded|deprecated`, `date`, `deciders[]`, `issue`, `supersedes[]`, `supersededBy?`, `tags[]`, `reviewDate?`; body headings Context, Decision, Alternatives, Consequences, References.
* CLI `pnpm adr new "<title>" --issue PAP-12 --tags stack`, `pnpm adr lint [--fix]`, `pnpm adr index` writing `docs/.generated/adr-index.json`.
* In-app index `/_app/docs/adr` rendered by PAP-128: filterable table and a small supersession graph (React Flow).
* Status hook: workflow on merge to `main` diffs `adr-index.json`, posts a Linear comment on the linked issue via the `linear-update` skill, and moves the issue to Needs Justin when status becomes `proposed` with Justin among deciders (PAP-94 rules).
* Seed: fifteen plan decisions as accepted ADRs; `docs/adr/README.md` on when an ADR is required.

Out: a decisions table (files are the truth), voting, analytics.

**Spec**

* Parallel-branch numbering collisions: keep both files, `adr lint` requires a renumber on the later merge.
* `superseded` requires `supersededBy`; `--fix` adds the reverse link.
* ADRs registered as `doc` search entities with tag `adr`.
* Nightly job comments on the issue when `reviewDate` passes while `accepted`.

**Interface contract**

Exposes: `AdrFrontmatter` type and `adr-index.json` `{ generatedAt, adrs: [{ id, title, status, date, deciders, issue, tags, supersedes, supersededBy, path }] }` consumed by PAP-216 (registry links), PAP-138 (search) and PAP-44; CLI commands above, reused by the `write-adr` skill (PAP-105) which imports the numbering function; MDX `AdrRef` component; Linear comment format `ADR 0007 accepted: <title> <link>`. Consumes: `renderMdx` and route from PAP-128, `linear-update` script from PAP-105 (a local copy ships here if unmerged), Needs Justin rules from PAP-94.

**Definition of done**

* Fifteen seed ADRs merged, lint clean, index generated.
* In-app index at 375, 1024 and 1920 with filters and graph; axe clean.
* A test ADR status change produces the Linear comment and the Needs Justin move.
* `docs/adr/README.md`; CHANGELOG entry; Linear comment with index link and screenshots.

**Test plan**

* Vitest: frontmatter validation (each status, missing `supersededBy`), numbering with a simulated collision, `--fix` reverse links, index generation snapshot, status-diff detection between two index files, `reviewDate` overdue detection.
* Integration: workflow dry-run on a fixture diff posts to a mocked Linear endpoint with the exact comment string; the Needs Justin transition is asserted on a `rehearsal`-labelled issue.
* Playwright: index filters by status and tag; clicking a node in the graph opens the ADR; run at 375 and 1280.
* Visual: index page baselines at 375, 1024 and 1920, both themes.

**Demo**

Run `pnpm adr new “Try it” --issue PAP-130`, fill Decision, run `pnpm adr lint && pnpm adr index`, open `/_app/docs/adr` and find it as `proposed`; flip a fixture ADR to `superseded` and watch the graph draw the edge. Under two minutes.

**Edge cases**

* ADR without an issue: `issue: none` allowed with a lint warning; no comment.
* Two ADRs supersede the same one: fan-out in the graph.
* Issue archived in Linear: comment written to `artifacts/pending-comments/`.
* Status flips back to `proposed`: allowed, logged as a reopen with a References link.
* Long alternatives table: horizontal scroll at 320 and 375.

**Dependencies**

PAP-128 (hard, encoded). Soft: PAP-105, PAP-94. Consumed by PAP-44, PAP-127, PAP-139, PAP-216 and every research issue.

**Agent**

Built by Quill (Changelog Scribe). Reviewed by Atlas (decision policy) and Sentinel (Code Reviewer).

**Size**

S: files, a small CLI, one docs page and fifteen seeds.
