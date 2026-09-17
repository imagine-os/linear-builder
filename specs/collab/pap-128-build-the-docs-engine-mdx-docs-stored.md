---
identifier: "PAP-128"
title: "Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer", "Staff"]
milestone: "Docs and prompt log stores"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16"]
blocks: ["PAP-41", "PAP-76", "PAP-109", "PAP-130", "PAP-134", "PAP-138", "PAP-203", "PAP-205", "PAP-216", "PAP-379", "PAP-380", "PAP-418", "PAP-420"]
key: "collab/docs-engine"
url: "https://linear.app/paperos/issue/PAP-128/build-the-docs-engine-mdx-docs-stored-in-the-repo-rendered-in-app"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:28.407Z"
---

# PAP-128: Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git

**Goal**

Make documentation part of the product: MDX under `docs/` renders inside PaperOS with navigation, search, git history and audience filtering, so agents write docs beside code and Justin, staff and customers read them in-app. ADRs, changelog, rules, guidelines and the registry all publish through this engine.

**Scope**

In:

* `packages/collab/docs/`: Vite plugin chain `@mdx-js/rollup` 3, `remark-gfm`, `remark-frontmatter`, `rehype-slug`, `rehype-autolink-headings`, `@shikijs/rehype`; loader `import.meta.glob('/docs/**/*.{md,mdx}')` producing `DocEntry`.
* Frontmatter (Zod 4): `title`, `owner`, `audience: (developer|staff|customer|agent)[]`, `tags[]`, `updated`, `status: draft|published|archived`, `specRef?`, `issue?`, `redirectFrom[]`.
* Sidebar from folder tree plus `_meta.yaml`; breadcrumbs; on-page TOC; previous and next links.
* Routes: `/_app/docs/$` (staff, developer) inside the shell from PAP-16; `/_public/docs/$` for `audience: customer` pages.
* MDX components: `Callout`, `Steps`, `Tabs`, `FileRef` (build-time file or line-range include), `SpecRef`, `Mermaid` (lazy), `IssueRef` (live state via PAP-101 when available).
* Search: `pnpm docs:index` registers docs with PAP-39 `registerSearchable({ entity: 'doc' })`; a client-side Pagefind index in CI until then.
* History: `pnpm docs:history` runs `git log --follow` per file into `docs/.generated/history.json`; footer "Updated by X on Y", History drawer, "Edit this page" to the Forgejo URL (PAP-45).
* Lint `pnpm docs:lint`: frontmatter, broken links, `FileRef` paths, unique headings.

Out: WYSIWYG editing (planned runtime docs store), Notion import (PAP-203), block comments (PAP-131 anchors to heading ids).

**Spec**

* Slugs are paths without extension; `index.mdx` maps to its folder.
* Audience enforced at build for `/_public` and at runtime with `useCan('doc.view')`; drafts hidden outside dev.
* Code blocks: copy button, file name, Shiki light and dark themes bound to the `data-theme` attribute from PAP-75.
* Headings expose `data-block-id` for comment anchoring.
* A doc page renders within 100 ms after route load; MDX code-split per file.

**Interface contract**

Exposes: `DocEntry { path, slug, frontmatter, headings[], Component, wordCount }`, `useDocs()`, `DocPage`, `renderMdx(source)` (used by PAP-134 and the planned runtime docs store), MDX component set, `docs/.generated/history.json` and `sidebar.json`, search entity `doc` with facets `audience`, `tags`, `owner`, anchor scheme `doc:<path>#<blockId>` consumed by PAP-131, lint `pnpm docs:lint` wired into Gate 1 (PAP-78). Consumes: route layouts and slots from PAP-16, `registerSearchable` from PAP-39, theme attribute from PAP-75, Forgejo base URL env from PAP-17.

**Definition of done**

* Twenty existing docs render with sidebar, TOC and history; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Public route hides staff docs; drafts hidden in production build.
* axe clean on doc pages; `docs/collab/docs-engine.md`; CHANGELOG entry; Linear comment with Pages preview and in-app screenshots.

**Test plan**

* Vitest: frontmatter schema (valid, missing title, bad audience), `_meta.yaml` ordering, link lint on a fixture tree with one broken link, `FileRef` line-range resolution, redirect map generation.
* Integration: `pnpm docs:history` against a fixture repo with one renamed file keeps history; shallow-clone detection fetches `docs/` history.
* Playwright: navigate three pages via sidebar, search returns a known page, `/_public/docs` as anonymous hides a staff doc (403 and no sidebar entry), History drawer lists commits; run at 375 and 1280.
* Visual: Gate 3 baselines for one long doc and the index at the seven widths, both themes; Mermaid and code block stories in Storybook with axe.

**Demo**

Open `/_app/docs`, click the template guide, use the TOC, open History and click the commit, press “Edit this page” and land in Forgejo. Search “quality gates” in the docs search box and open the hit. Under two minutes.

**Edge cases**

* MDX compile error in one file: dev renders an error card with file and line; CI fails.
* 10k-word page: TOC collapses to h2; images lazy-load.
* Same slug in two folders with different audiences: allowed; routes resolve separately.
* Invalid Mermaid: source shown in a code block with a warning.
* File renamed: `--follow` keeps history; lint suggests a redirect.

**Dependencies**

PAP-16 (hard). Soft: PAP-39, PAP-75, PAP-45. Blocks PAP-130, PAP-134, PAP-138, PAP-41, PAP-76, PAP-109, PAP-203, PAP-216 and the planned runtime docs store and in-app help.

**Agent**

Built by Nova with Quill owning frontmatter and content conventions. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Quill.

**Size**

M: standard MDX tooling; history, audiences and search touch several systems.
