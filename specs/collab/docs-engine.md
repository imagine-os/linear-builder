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
blocks: ["PAP-109", "PAP-130", "PAP-134", "PAP-138", "PAP-203", "PAP-205", "PAP-216", "PAP-41", "PAP-76"]
key: "collab/docs-engine"
url: "https://linear.app/paperos/issue/PAP-128/build-the-docs-engine-mdx-docs-stored-in-the-repo-rendered-in-app"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-128: Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git

**Goal**

Make documentation part of the product: MDX files stored in the repo under `docs/` render inside PaperOS with navigation, search, version history from git and audience filtering, so agents write docs next to code and Justin, staff and customers read them in-app. Every other knowledge feature (ADRs, changelog, rules, guidelines, registry) publishes through this engine.

**Scope**

In:
- `packages/collab/docs/`: Vite plugin setup with `@mdx-js/rollup` 3, `remark-gfm`, `remark-frontmatter`, `rehype-slug`, `rehype-autolink-headings`, `@shikijs/rehype` for code; loader `import.meta.glob('/docs/**/*.{md,mdx}')` producing `DocEntry { path, slug, frontmatter, headings[], Component, wordCount }`.
- Frontmatter Zod 4 schema: `title`, `owner` (character or person), `audience: developer|staff|customer|agent` (array), `tags[]`, `updated`, `status: draft|published|archived`, `specRef?`, `issue?`.
- Sidebar from folder tree plus `_meta.yaml` ordering and labels; breadcrumbs; on-page table of contents; previous and next links.
- Routes: `/_app/docs/$` splat for staff and developer audiences inside the shell (`app-shell/router-layouts`), `/_public/docs/$` for `audience: customer` pages with the public layout.
- MDX components: `Callout`, `Steps`, `Tabs`, `FileRef` (includes a file or line range from the repo at build time), `SpecRef` (links to a page spec and shows its status), `Mermaid` (lazy-loaded), `IssueRef` (Linear link with live state via `pm-linear/linear-sync` when available).
- Search: build script `pnpm docs:index` writes docs into `data-layer/search` via `registerSearchable({ entity: 'doc' })` when the API is available; until then a client-side Pagefind index built in CI.
- Version history: `pnpm docs:history` runs `git log --follow` per file at build time into `docs/.generated/history.json` (author, date, sha, message, PR); the page footer shows "Updated by X on Y" and a History drawer; "Edit this page" links to the Forgejo edit URL (`forge/forgejo-deploy` base URL from env).
- Lint `pnpm docs:lint`: frontmatter valid, no broken internal links, `FileRef` paths exist, headings unique.

Out: WYSIWYG editing (Tiptap docs come via `realtime/collab-text` later), Notion import (`migration/notion`), comments on blocks (`collab/comments` anchors to heading ids).

**Spec**

- Slugs are file paths without extension; `index.mdx` maps to the folder; redirects via `redirectFrom[]` frontmatter.
- Audience filter is enforced at build for `/_public` and at runtime with `useCan('doc.view')` in the shell; drafts hidden outside dev.
- Code blocks have copy buttons and file names; dark and light Shiki themes bound to the theme attribute from `design-system/theming`.
- Heading anchors expose `data-block-id` for comment anchoring.
- Each doc page renders within 100 ms after route load; MDX is code-split per file.

**Definition of done**

- Twenty existing docs (template guide, ADRs, quality gates) render with sidebar, TOC and history; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
- Vitest: frontmatter schema, sidebar ordering, link lint, `FileRef` resolution; Playwright: navigate three pages, search returns a known page, public route hides staff docs.
- axe clean on doc pages.
- `docs/collab/docs-engine.md` explains writing a doc, components and lint; CHANGELOG entry.
- Linear comment with Pages preview and in-app screenshots.

**Edge cases**

- MDX compile error in one file: build reports file and line and renders an error card for that page in dev; CI fails.
- Very long page (10k words): TOC collapses to h2, content virtualisation not needed but images lazy-load.
- File renamed: `git log --follow` keeps history; old slug redirect suggested by lint.
- Same slug in two folders with different audiences: allowed; public and app routes resolve separately.
- Shallow clone in CI: history script detects `--depth` and fetches full history for `docs/` only.
- Mermaid diagram invalid: renders the source in a code block with a warning instead of a blank space.

**Dependencies**

`app-shell/router-layouts` (hard). Soft: `data-layer/search` (index), `design-system/theming` (Shiki theme), `forge/forgejo-deploy` (edit links). Unblocks `collab/decision-log`, `collab/rules-skills-registry`, `collab/knowledge-search`, `data-layer/data-dictionary`, `design-system/guidelines-docs`, `agents/memory`, `libraries/registry`, `migration/notion`, `spec-builder/spec-docs`.

**Agent**

Built by Nova with Quill owning frontmatter and content conventions. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Quill.

**Size**

M: standard MDX tooling, but history, audiences and search integration touch several systems.
