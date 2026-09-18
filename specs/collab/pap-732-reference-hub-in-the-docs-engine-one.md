---
identifier: "PAP-732"
title: "Reference hub in the docs engine: one sidebar section for OpenAPI, the data dictionary, module contracts, the component registry and ADRs"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128"]
blocks: []
key: "r4/collab/docs-reference-hub"
url: "https://linear.app/paperos/issue/PAP-732/reference-hub-in-the-docs-engine-one-sidebar-section-for-openapi-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:32.923Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-732: Reference hub in the docs engine: one sidebar section for OpenAPI, the data dictionary, module contracts, the component registry and ADRs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Five projects generate reference documentation into five places: Scalar OpenAPI (PAP-269), the data dictionary (PAP-41), module and contract pages (PAP-445), the component registry (PAP-74) and the ADR index (PAP-130). A builder session should find them under one `Reference` heading with cross-links, not by knowing five URLs.

**Scope**

In: `docs/reference/_meta.yaml` and loader hooks in `packages/collab/docs/reference.ts` that mount generated sources into the sidebar: `api` (embed the Scalar page or render `openapi.json` through `@scalar/api-reference-react`), `data` (PAP-41 output), `modules` and `contracts` (PAP-445 output), `components` (PAP-74 `registry.json` rendered as prop tables with Storybook links), `adr` (PAP-130 index); cross-link resolver turning `PAP-n`, `ui.<name>`, `@paperos/contract-<m>`, table names and topic names into links anywhere in docs. Out: generating the sources (owned elsewhere), API playground auth.

**Spec**

* Each source declares `{ id, title, path|url, generatedBy: PAP-n, freshness: file mtime or `generatedAt` }`; a missing source renders a placeholder card naming the owning issue instead of a 404.
* Cross-link resolver runs as a rehype plugin over all docs: `PAP-129` links to Linear (PAP-101 mirror when present), `ui.badge` to the component page, `comment_thread` to the dictionary row, `comment.created` to the topic page; unknown tokens are left alone.
* Freshness badge (`generated 3 h ago`) and a Gate 1 lint `docs:reference-stale` warning when a source is older than its generator's last merge.
* Search (PAP-138) indexes reference pages with kind `doc` and tag `reference` so `mod+k` finds a table or a component by name.
* Reference section is `audience: [developer, agent]`; customers never see it.

**Interface contract**

Provides: `docs/reference/` mount, `registerReferenceSource()`, cross-link rehype plugin, lint `docs:reference-stale`. Consumes: `DocEntry`, sidebar and `renderMdx` (PAP-128), `openapi.json` (PAP-269), `docs/data-dictionary/` (PAP-41), `docs/platform/{modules,contracts}/` (PAP-445), `registry.json` (PAP-74), `adr-index.json` (PAP-130), Storybook URL (PAP-69). Consumed by: PAP-727 (`llms.txt` includes the hub), PAP-24 template guide, PAP-92 playbook.

**Definition of done**

* Hub renders with the sources that exist on `main` and placeholders for the rest; cross-links resolve in three fixture docs; screenshots at 375 and 1280 in light and dark; axe clean.
* `docs/collab/reference-hub.md`; CHANGELOG entry; Linear comment.

**Test plan**

* Unit: source registration and freshness computation, cross-link tokeniser (positive and negative fixtures), placeholder rendering.
* Integration: build with PAP-41 output absent and present.
* E2E (Playwright): open Reference, navigate to a component page, follow a cross-link from a doc to a table row.

**Demo**

Open `/_app/docs/reference`, click Components, open `ui.badge`, then search `comment_thread` and land on the dictionary row. Under one minute.

**Edge cases**

* Two sources claim the same slug: build fails naming both.
* OpenAPI spec over 5 MB: rendered lazily per tag group.
* Token collision (a doc literally about the word `file`): resolver only links backticked tokens.

**Dependencies**

Hard: PAP-128. Soft: PAP-269, PAP-41, PAP-445, PAP-74, PAP-130, PAP-69, PAP-138.

**Agent**

Builder: Quill (Changelog Scribe). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/agent-readable-docs` = PAP-727.
