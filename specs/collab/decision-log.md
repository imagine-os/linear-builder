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
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-130: Add an ADR/decision log with status, alternatives and links to issues

**Goal**

Give every significant choice a findable, linked record: ADR files in the repo with a strict frontmatter, a CLI to create and lint them, an in-app index with status and supersession graph, and automatic Linear comments when a decision changes. The plan's fifteen decisions become the first entries.

**Scope**

In:
- Format `docs/adr/NNNN-PAP-<issue>-<slug>.md` with frontmatter (Zod 4 `AdrFrontmatter`): `id` (NNNN), `title`, `status: proposed|accepted|rejected|superseded|deprecated`, `date`, `deciders[]` (characters or Justin), `issue` (PAP key), `supersedes[]`, `supersededBy?`, `tags[]`, `reviewDate?`; body headings in order: Context, Decision, Alternatives (table with score columns when a rubric applies), Consequences, References.
- CLI `pnpm adr new "<title>" --issue PAP-12 --tags stack` (numbering per the `write-adr` skill rule: next number plus issue suffix, reconciled on merge), `pnpm adr lint` (frontmatter, headings, unique ids, supersession links resolve, `reviewDate` past due warns), `pnpm adr index` writing `docs/.generated/adr-index.json`.
- In-app index `/_app/docs/adr` rendered by `collab/docs-engine`: table (id, title, status, date, deciders, tags) with filters, and a supersession graph (small React Flow) showing chains.
- Status change hook: a GitHub/Forgejo workflow on merge to `main` diffs `adr-index.json` and, for each changed status, posts a Linear comment on the linked issue via the `linear-update` skill script ("ADR 0007 accepted: <title> <link>") and, when `status` becomes `proposed` with `deciders` including Justin, moves the issue to Needs Justin per `pm-linear/justin-queue`.
- Seed: the fifteen decisions from `plan.json` written as ADRs 0001 to 0015 with `status: accepted` and `issue` pointing to the relevant Linear issue.
- `docs/adr/README.md` explaining when an ADR is required (new library, schema change affecting two projects, security model, external dependency) and the template.

Out: a database table for decisions (files are the source of truth), voting workflows, decision analytics.

**Spec**

- Numbering collisions from parallel branches resolve by keeping both files and letting `adr lint` require a renumber on the later merge; the index uses `id` from the filename.
- `superseded` requires `supersededBy`; setting it also adds the reverse `supersedes` entry via `adr lint --fix`.
- Index JSON shape: `{ generatedAt, adrs: [{ id, title, status, date, deciders, issue, tags, supersedes, supersededBy, path }] }`; consumed by `libraries/registry` and `collab/knowledge-search`.
- ADRs are registered as `doc` search entities with tag `adr` so one search covers them.
- Review dates: nightly job comments on the issue when `reviewDate` passes and status is still `accepted`.

**Definition of done**

- Fifteen seed ADRs merged, lint clean, index generated.
- Vitest: frontmatter validation, numbering script, supersession fix, index generation, status-diff detection.
- In-app index screenshot at 375, 1024 and 1920 with filters and graph; axe clean.
- Seeded status change on a test ADR produces the Linear comment (link) and the Needs Justin move.
- `docs/adr/README.md`; CHANGELOG entry; Linear comment with index link and screenshots.

**Edge cases**

- ADR without an issue (pre-existing decision): `issue: none` allowed with a lint warning; no Linear comment.
- Two ADRs supersede the same one: allowed; graph shows a fan-out.
- Frontmatter edited manually with invalid status: lint fails in gate 1 via `docs:lint`.
- Issue key archived or deleted in Linear: comment fails gracefully and is written to `artifacts/pending-comments/`.
- Very long alternatives table: rendered with horizontal scroll at 320 and 375.
- Status flips back from `accepted` to `proposed`: allowed, logged as a reopen with a required `References` link.

**Dependencies**

`collab/docs-engine` (hard for the index page). Uses `agents/skills-library` `write-adr` and `linear-update` scripts (soft; ship the numbering script here if the skill is not merged and the skill imports it). Consumed by `forge/vcs-decision-adr`, `collab/collab-research`, `libraries/registry`, every research issue.

**Agent**

Built by Quill (Changelog Scribe). Reviewed by Atlas (decision policy) and Sentinel (Code Reviewer).

**Size**

S: files, a small CLI and one docs page, plus seeding fifteen entries.
