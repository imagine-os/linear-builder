# Rewritten specs for collab issues. Each value: dict of sections (see r3.SECTION_ORDER).
R = {}

R["PAP-127"] = {
"Goal": "Choose the canvas library (tldraw vs React Flow) and the rich-text editor (Tiptap vs BlockNote) in one time-boxed session, prove the choice with two Yjs spikes at our scale, and record it as an ADR. PAP-132 (canvas), PAP-142 (editor) and PAP-131 (comments composer) build on this decision.",
"Scope": """In:

* Rubric scoring per PAP-209 plus collab criteria: Yjs binding maturity, custom node API, programmatic layout, locked elements, touch and pen, PNG/SVG export, theming with tokens.
* Candidates: canvas `tldraw` 3.x (watermark or paid business license, scored against PAP-211) vs `@xyflow/react` 12 (MIT); editor `@tiptap/core` 3.x with `y-prosemirror` (MIT core) vs `@blocknote/core` (MPL-2.0, built on Tiptap).
* Spikes in `spikes/collab-research/` (throwaway): (1) render the `FlowGraph` fixture from PAP-123 with 300 nodes and 600 edges, measure FPS while panning, test locked nodes, groups and custom renderers; (2) two browser contexts editing one document through a local Hocuspocus container, measure time to first collaborative render and gzip bundle size, test mentions, code blocks, tables, image upload hook and read-only rendering.
* ADR `docs/adr/00NN-PAP-127-canvas-and-editor.md` in the PAP-130 format; registry entries in PAP-216 for four libraries.

Out: production integration, whiteboard products (Excalidraw, Miro) beyond a line in alternatives.""",
"Spec": """* Time box: one session, at most 60 turns and 4 hours; if spikes are inconclusive, decide on license and model fit and record the uncertainty.
* Scores 1 to 5 per criterion with one-sentence evidence and a link; totals weighted per rubric weights. Bundle sizes from a production Vite build, gzip. License check with the PAP-211 CI checker on both spike lockfiles.
* Expected outcome unless spikes disagree: React Flow for the canvas (node and edge model matches the spec graph, MIT, ELK-friendly) and Tiptap with `y-prosemirror` for the editor, BlockNote noted as a later document option.
* Linear comment under 300 words with the decision on the first line.""",
"Interface contract": """Exposes: ADR file with frontmatter `status: accepted`, `issue: PAP-127`, `reviewDate: 2027-01-01`; `spikes/collab-research/results.json` `{ canvas: { lib, fps300, gzipKb }, editor: { lib, ttfcrMs, gzipKb } }`; four registry rows (`adopted` or `rejected`). Downstream issues read the ADR's `decision` block: PAP-132 imports the chosen canvas package, PAP-142 the editor package; PAP-127 also fixes the peer-dependency matrix (`yjs`, `y-prosemirror`, `@tiptap/*` versions) that PAP-140 and PAP-142 pin. Consumes: PAP-209 rubric weights, PAP-211 checker, PAP-123 graph fixture shape (use the example JSON in the plan if PAP-123 is unmerged).""",
"Definition of done": """* ADR merged, status `accepted`, scores table, spike links, reopen criteria.
* Two spike folders with README and measured numbers (FPS at 300 nodes, gzip size, time to first collaborative render).
* Registry updated for four libraries; peer-dependency matrix recorded.
* Linear comment with decision, numbers and 1280 px screenshots of both spikes.
* PAP-132 and PAP-142 titles updated to name the chosen libraries.""",
"Test plan": """* Unit: none shipped; each spike has a `pnpm bench` script that reprints the ADR numbers.
* Integration: spike 2 runs against `docker compose up hocuspocus` and asserts two clients converge on the same text (Playwright, two contexts).
* Visual: screenshots of both spikes at 1280 px in light and dark attached to the comment; no baselines kept.
* Review check: Sentinel reruns the license checker on the lockfiles and confirms the ADR quotes the exact tldraw license text and version.""",
"Demo": "Open the ADR, read the first line of the decision. Run `pnpm --filter spike-canvas bench` and see FPS at 300 nodes printed; run `pnpm --filter spike-editor dev`, open two tabs, type in one and watch the other. Under two minutes.",
"Edge cases": """* tldraw license terms changed recently: quote text and version evaluated.
* React Flow lacks freehand drawing: note the plan (sticky notes and shapes as custom nodes, ink via PAP-157).
* BlockNote pins a Tiptap version that conflicts with PAP-142 needs: record the peer matrix.
* Both editors fail screen-reader table navigation: record as a known gap with a mitigation issue.
* Hocuspocus (PAP-140) not deployed: run it locally in Docker and note the difference.""",
"Dependencies": "None hard (Ready). Uses PAP-209 and PAP-211 if merged, else the rubric from the plan. Blocks PAP-132, PAP-142; informs PAP-131.",
"Agent": "Built by Scout (Library Evaluator) with Nova (Canvas Cartographer) running spikes. Reviewed by Atlas (decision) and Sentinel (Security Auditor for license).",
"Size": "S: one session, two spikes, one ADR.",
}

R["PAP-128"] = {
"Goal": "Make documentation part of the product: MDX under `docs/` renders inside PaperOS with navigation, search, git history and audience filtering, so agents write docs beside code and Justin, staff and customers read them in-app. ADRs, changelog, rules, guidelines and the registry all publish through this engine.",
"Scope": """In:

* `packages/collab/docs/`: Vite plugin chain `@mdx-js/rollup` 3, `remark-gfm`, `remark-frontmatter`, `rehype-slug`, `rehype-autolink-headings`, `@shikijs/rehype`; loader `import.meta.glob('/docs/**/*.{md,mdx}')` producing `DocEntry`.
* Frontmatter (Zod 4): `title`, `owner`, `audience: (developer|staff|customer|agent)[]`, `tags[]`, `updated`, `status: draft|published|archived`, `specRef?`, `issue?`, `redirectFrom[]`.
* Sidebar from folder tree plus `_meta.yaml`; breadcrumbs; on-page TOC; previous and next links.
* Routes: `/_app/docs/$` (staff, developer) inside the shell from PAP-16; `/_public/docs/$` for `audience: customer` pages.
* MDX components: `Callout`, `Steps`, `Tabs`, `FileRef` (build-time file or line-range include), `SpecRef`, `Mermaid` (lazy), `IssueRef` (live state via PAP-101 when available).
* Search: `pnpm docs:index` registers docs with PAP-39 `registerSearchable({ entity: 'doc' })`; a client-side Pagefind index in CI until then.
* History: `pnpm docs:history` runs `git log --follow` per file into `docs/.generated/history.json`; footer "Updated by X on Y", History drawer, "Edit this page" to the Forgejo URL (PAP-45).
* Lint `pnpm docs:lint`: frontmatter, broken links, `FileRef` paths, unique headings.

Out: WYSIWYG editing (planned runtime docs store), Notion import (PAP-203), block comments (PAP-131 anchors to heading ids).""",
"Spec": """* Slugs are paths without extension; `index.mdx` maps to its folder.
* Audience enforced at build for `/_public` and at runtime with `useCan('doc.view')`; drafts hidden outside dev.
* Code blocks: copy button, file name, Shiki light and dark themes bound to the `data-theme` attribute from PAP-75.
* Headings expose `data-block-id` for comment anchoring.
* A doc page renders within 100 ms after route load; MDX code-split per file.""",
"Interface contract": """Exposes: `DocEntry { path, slug, frontmatter, headings[], Component, wordCount }`, `useDocs()`, `DocPage`, `renderMdx(source)` (used by PAP-134 and the planned runtime docs store), MDX component set, `docs/.generated/history.json` and `sidebar.json`, search entity `doc` with facets `audience`, `tags`, `owner`, anchor scheme `doc:<path>#<blockId>` consumed by PAP-131, lint `pnpm docs:lint` wired into Gate 1 (PAP-78). Consumes: route layouts and slots from PAP-16, `registerSearchable` from PAP-39, theme attribute from PAP-75, Forgejo base URL env from PAP-17.""",
"Definition of done": """* Twenty existing docs render with sidebar, TOC and history; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Public route hides staff docs; drafts hidden in production build.
* axe clean on doc pages; `docs/collab/docs-engine.md`; CHANGELOG entry; Linear comment with Pages preview and in-app screenshots.""",
"Test plan": """* Vitest: frontmatter schema (valid, missing title, bad audience), `_meta.yaml` ordering, link lint on a fixture tree with one broken link, `FileRef` line-range resolution, redirect map generation.
* Integration: `pnpm docs:history` against a fixture repo with one renamed file keeps history; shallow-clone detection fetches `docs/` history.
* Playwright: navigate three pages via sidebar, search returns a known page, `/_public/docs` as anonymous hides a staff doc (403 and no sidebar entry), History drawer lists commits; run at 375 and 1280.
* Visual: Gate 3 baselines for one long doc and the index at the seven widths, both themes; Mermaid and code block stories in Storybook with axe.""",
"Demo": "Open `/_app/docs`, click the template guide, use the TOC, open History and click the commit, press “Edit this page” and land in Forgejo. Search “quality gates” in the docs search box and open the hit. Under two minutes.",
"Edge cases": """* MDX compile error in one file: dev renders an error card with file and line; CI fails.
* 10k-word page: TOC collapses to h2; images lazy-load.
* Same slug in two folders with different audiences: allowed; routes resolve separately.
* Invalid Mermaid: source shown in a code block with a warning.
* File renamed: `--follow` keeps history; lint suggests a redirect.""",
"Dependencies": "PAP-16 (hard). Soft: PAP-39, PAP-75, PAP-45. Blocks PAP-130, PAP-134, PAP-138, PAP-41, PAP-76, PAP-109, PAP-203, PAP-216 and the planned runtime docs store and in-app help.",
"Agent": "Built by Nova with Quill owning frontmatter and content conventions. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Quill.",
"Size": "M: standard MDX tooling; history, audiences and search touch several systems.",
}

R["PAP-129"] = {
"Goal": "Build the system of record for how agents built PaperOS: Postgres tables and an ingest API storing every session, prompt, response, tool call, token count and cost with redaction and dedupe, queryable by issue, character and PR. Credit metering (PAP-98), evals (PAP-110), memory (PAP-109) and the browser (PAP-135) read from here.",
"Scope": """In:

* Drizzle schema `packages/db/src/schema/prompt-log.ts`: `prompt_session` (`id` text = Claude session id, `tenant_id`, `character`, `sub_agent`, `issue_key`, `linear_issue_id`, `repo`, `branch`, `worktree`, `model`, `launch: hook|sdk`, `parent_session_id`, `started_at`, `ended_at`, `status: running|completed|killed|failed`, token columns, `cost_usd numeric(12,6)`, `pr_url`, `summary`, `redaction_count`, `gaps jsonb`); `prompt_event` (`id uuidv7`, `session_id`, `seq`, `ts`, `event`, `role`, `content`, `content_file_id`, `tool_name`, `tool_input jsonb`, `tool_output`, `usage jsonb`, `cost_usd`, `model`, `redactions jsonb`, `truncated`), unique `(session_id, seq)`, monthly partitions; `prompt_model_price`.
* Ingest `POST /api/v1/prompt-log/events` (NDJSON, 5 MB cap, idempotent on `(session_id, seq)`), bearer token per character from PAP-60, second-pass redaction with `packages/agents/src/redact.ts`, cost recomputed from the price table when absent.
* oRPC `promptLog.sessions.list|get|setSummary`, `promptLog.events.list`, `promptLog.stats({ groupBy })`.
* RLS: platform tenant only; `owner|admin` and agent principals read; ingest tokens write.
* Retention job (PAP-43): events older than 180 days to MinIO NDJSON; sessions and stats kept.

Out: hooks (PAP-107), browser UI (PAP-135), metering reports (PAP-98).""",
"Spec": """* `seq` gaps stored on the session and surfaced by `stats`; a synthetic `session.killed` event closes sessions.
* Cost = sum of tokens times the model price at `ts`; nightly recompute when prices change.
* Ingest p95 under 150 ms for a 1 MB batch via multi-row insert `ON CONFLICT DO NOTHING`.
* Indexes `(issue_key, started_at desc)`, `(character, started_at desc)`, `(session_id, seq)`, GIN on `tool_input`.
* Sessions registered as search entity `prompt_session` (PAP-39) for PAP-138.""",
"Interface contract": """Exposes: tables above; ingest event shape `PromptEventIn { sessionId, seq, ts, character, subAgent?, issueKey?, event, role?, content?, toolName?, toolInput?, toolOutput?, usage?, costUsd?, model?, redactions? }` (Zod in `packages/contracts/prompt-log.ts`, shared with PAP-107); response `{ accepted, duplicates, gaps: [{ from, to }] }`; oRPC procedures above with `PromptSession` and `PromptEvent` types; `promptLog.stats` rows `{ key, inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens, costUsd, sessions }`. Consumes: `tenant`/`user` from PAP-33, migrations from PAP-32, oRPC server and `callAs` from PAP-35, `verifyApiKey` from PAP-60 (static per-character env token until then), blob upload from PAP-37, job runtime from PAP-43.""",
"Definition of done": """* Migration applied on staging; RLS harness (PAP-34) shows a non-platform tenant sees nothing.
* A 20-turn recorded session from PAP-107 fixtures ingests fully; token totals within 1 percent.
* `docs/collab/prompt-log.md` (schema, API, retention, redaction); CHANGELOG entry; Linear comment with test and load results.""",
"Test plan": """* Vitest: dedupe on repeated `seq`, gap detection, cost computation with two price epochs, second-pass redaction over 30 fixtures (keys, tokens, emails), 413 on a 6 MB batch, unknown model leaves cost null and flagged.
* Integration (Postgres in CI): partition routing by month, RLS via `callAs(customerAdmin)` returns zero rows, retention job moves a 200-day-old partition to MinIO and deletes it.
* Load: k6 script `load/prompt-log.js`, 50 concurrent sessions × 200 events, completes under 2 minutes with zero duplicates; result JSON committed.
* Contract: PAP-107 fixture NDJSON validates against `PromptEventIn` in both repos' tests.""",
"Demo": "Run `pnpm prompt-log:replay fixtures/session-20-turns.ndjson` against staging, then call `promptLog.sessions.get` from the API playground and see tokens, cost and the PR URL; run `promptLog.stats({ groupBy: 'character' })` and read the totals. Under two minutes.",
"Edge cases": """* Event arrives before `SessionStart`: session row created from event fields, filled later.
* Same `seq`, different content: first wins, mismatch logged to `ingest_anomaly`.
* Content over 64 KB with MinIO down: truncated with `truncated: true`, never rejected.
* Clock skew: order by `seq`, `ts` for display only.
* Token revoked mid-session: 401; shipper spools until rotation.""",
"Dependencies": "PAP-33, PAP-32, PAP-35 (hard, encoded). Soft: PAP-60, PAP-37, PAP-43. Blocks PAP-107, PAP-135; consumed by PAP-98, PAP-110.",
"Agent": "Built by Forge (Schema Wright) with Quill (Prompt Logger) defining fields. Reviewed by Sentinel (Security Auditor for redaction and RLS) and Atlas.",
"Size": "M: contained schema and ingest; performance, dedupe and redaction must be proven.",
}

R["PAP-130"] = {
"Goal": "Give every significant choice a findable, linked record: ADR files with strict frontmatter, a CLI to create and lint them, an in-app index with status and supersession graph, and Linear comments when a decision changes. The plan's fifteen decisions become entries 0001 to 0015.",
"Scope": """In:

* Format `docs/adr/NNNN-PAP-<issue>-<slug>.md`; frontmatter (Zod 4 `AdrFrontmatter`): `id`, `title`, `status: proposed|accepted|rejected|superseded|deprecated`, `date`, `deciders[]`, `issue`, `supersedes[]`, `supersededBy?`, `tags[]`, `reviewDate?`; body headings Context, Decision, Alternatives, Consequences, References.
* CLI `pnpm adr new "<title>" --issue PAP-12 --tags stack`, `pnpm adr lint [--fix]`, `pnpm adr index` writing `docs/.generated/adr-index.json`.
* In-app index `/_app/docs/adr` rendered by PAP-128: filterable table and a small supersession graph (React Flow).
* Status hook: workflow on merge to `main` diffs `adr-index.json`, posts a Linear comment on the linked issue via the `linear-update` skill, and moves the issue to Needs Justin when status becomes `proposed` with Justin among deciders (PAP-94 rules).
* Seed: fifteen plan decisions as accepted ADRs; `docs/adr/README.md` on when an ADR is required.

Out: a decisions table (files are the truth), voting, analytics.""",
"Spec": """* Parallel-branch numbering collisions: keep both files, `adr lint` requires a renumber on the later merge.
* `superseded` requires `supersededBy`; `--fix` adds the reverse link.
* ADRs registered as `doc` search entities with tag `adr`.
* Nightly job comments on the issue when `reviewDate` passes while `accepted`.""",
"Interface contract": """Exposes: `AdrFrontmatter` type and `adr-index.json` `{ generatedAt, adrs: [{ id, title, status, date, deciders, issue, tags, supersedes, supersededBy, path }] }` consumed by PAP-216 (registry links), PAP-138 (search) and PAP-44; CLI commands above, reused by the `write-adr` skill (PAP-105) which imports the numbering function; MDX `AdrRef` component; Linear comment format `ADR 0007 accepted: <title> <link>`. Consumes: `renderMdx` and route from PAP-128, `linear-update` script from PAP-105 (a local copy ships here if unmerged), Needs Justin rules from PAP-94.""",
"Definition of done": """* Fifteen seed ADRs merged, lint clean, index generated.
* In-app index at 375, 1024 and 1920 with filters and graph; axe clean.
* A test ADR status change produces the Linear comment and the Needs Justin move.
* `docs/adr/README.md`; CHANGELOG entry; Linear comment with index link and screenshots.""",
"Test plan": """* Vitest: frontmatter validation (each status, missing `supersededBy`), numbering with a simulated collision, `--fix` reverse links, index generation snapshot, status-diff detection between two index files, `reviewDate` overdue detection.
* Integration: workflow dry-run on a fixture diff posts to a mocked Linear endpoint with the exact comment string; the Needs Justin transition is asserted on a `rehearsal`-labelled issue.
* Playwright: index filters by status and tag; clicking a node in the graph opens the ADR; run at 375 and 1280.
* Visual: index page baselines at 375, 1024 and 1920, both themes.""",
"Demo": "Run `pnpm adr new “Try it” --issue PAP-130`, fill Decision, run `pnpm adr lint && pnpm adr index`, open `/_app/docs/adr` and find it as `proposed`; flip a fixture ADR to `superseded` and watch the graph draw the edge. Under two minutes.",
"Edge cases": """* ADR without an issue: `issue: none` allowed with a lint warning; no comment.
* Two ADRs supersede the same one: fan-out in the graph.
* Issue archived in Linear: comment written to `artifacts/pending-comments/`.
* Status flips back to `proposed`: allowed, logged as a reopen with a References link.
* Long alternatives table: horizontal scroll at 320 and 375.""",
"Dependencies": "PAP-128 (hard, encoded). Soft: PAP-105, PAP-94. Consumed by PAP-44, PAP-127, PAP-139, PAP-216 and every research issue.",
"Agent": "Built by Quill (Changelog Scribe). Reviewed by Atlas (decision policy) and Sentinel (Code Reviewer).",
"Size": "S: files, a small CLI, one docs page and fifteen seeds.",
}

R["PAP-131"] = {
"Goal": "Umbrella: let people and agents discuss anything where it lives. Comments anchor to an entity, page element, doc block, canvas node or screenshot, support mentions and resolve state, update live for everyone on the same anchor, and escalate to a Linear issue in one click. Work is planned as three work packages; this issue owns the integration test and the docs.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Comment schema, anchors, RLS and oRPC procedures** — `comment_thread` and `comment` tables, five anchor kinds and `anchor_key` grammar, visibility policies, `comments.*` procedures, event emission.
2. **Comment panel, pins and composer UI** — `CommentableRoot`, pin overlay with clustering, `CommentsPanel`, `ThreadView`, composer on `RichTextEditor` (PAP-142) in local mode with mentions.
3. **Live updates, deep links and Linear escalation** — Electric shape subscription with polling fallback, `?thread=` deep links, `threads.createIssue` through PAP-101 or the Linear SDK.

Parent owns: `docs/collab/comments.md`, the two-context Playwright integration test, Gate 3 baselines, and the `c` keyboard command registration (PAP-151).

Out: notification delivery (PAP-136), screenshot viewer (PAP-137), email replies.""",
"Spec": """* `anchor_key`: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`; index `(tenant_id, anchor_key, status)`.
* `visibility: internal` hidden from `customer.*` audiences via PAP-59 policies `comment.read|create|update|delete|resolve`; agents may comment, never resolve customer threads.
* Body limit 10k characters; attachments through PAP-37 signed uploads.
* Live: shape on both tables scoped by tenant and anchor prefix (PAP-143) or TanStack Query polling every 5 s.""",
"Interface contract": """Exposes (owned by the work packages, listed here as the umbrella contract): tables `comment_thread`, `comment`; types `CommentAnchor` (discriminated union) and `anchorKey(anchor)` in `packages/collab/comments/anchors.ts`; oRPC `comments.threads.list|create|resolve|reopen|createIssue`, `comments.create|update|delete|react`; React `CommentableRoot`, `useThreads(anchor)`, `CommentsPanel`, `CommentPin`; DOM contract `data-comment-anchor` (codegen's `data-spec-key` doubles as element anchor); events `comment.created`, `comment.mentioned`, `thread.resolved` on `packages/core/events` (payload `{ threadId, commentId, anchor, actorId, mentions[] }`) consumed by PAP-136; deep link `?thread=<id>`. Consumes: `RichTextEditor` local mode (PAP-142), `can()` (PAP-59), awareness room `thread:<id>` (PAP-140, PAP-141), shape proxy (PAP-143), file uploads (PAP-37), issue creation (PAP-101).""",
"Definition of done": """* All three work packages merged; integration test below green in CI.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark showing pins and panel (drawer under `lg`).
* axe clean; composer usable keyboard-only; `docs/collab/comments.md` including how a page becomes commentable; CHANGELOG entry; Linear comment with screenshots and the created test issue link.""",
"Test plan": """* Integration (parent): Playwright with two contexts: staff A pins an element on the sample page and posts a mention of B; B sees the pin and thread within 1 s, replies, resolves; A reopens; A creates a Linear issue (mocked PAP-101) and the thread shows the issue key; a customer context cannot see the `internal` thread. Runs at 375 and 1280.
* Unit and component tests per work package (anchor derivation, `callAs` visibility matrix, mention parsing, pin clustering, composer keyboard).
* Visual: Gate 3 baselines for pins, panel and drawer at the seven widths, both themes.
* Contract: event payload snapshot validated against `packages/contracts/events.ts`.""",
"Demo": "Open the sample records page, press `c`, click a field, type “@Bo looks wrong”, send. In a second browser as Bo, watch the pin appear, reply, resolve. Back as A, click “Create issue” and open the Linear link. Under two minutes.",
"Edge cases": """* Anchored element removed by a deploy: thread listed under "Unanchored", pin hidden.
* Row in a virtualised grid: anchor is `entity`, not `element`.
* Mention of a user without access: stored, notification suppressed, hint shown.
* Offline: composer queues via PAP-148; append-only so no conflict.
* Fifty pins on one page: cluster with a count above 12 per viewport.""",
"Dependencies": "PAP-140, PAP-59, PAP-142 (hard). Soft: PAP-143, PAP-37, PAP-101, PAP-141, PAP-151. Blocks PAP-136, PAP-137, PAP-197.",
"Agent": "Built by Nova (CRDT Engineer) with Iris on the panel components. Reviewed by Sentinel (Security Auditor for visibility, Visual Inspector) and Quill.",
"Size": "L, planned as three M/S work packages (child issues pending the issue limit).",
}

R["PAP-132"] = {
"Goal": "Umbrella: show the whole app as a live map. Pages, transitions, entities and external systems come from specs, lay out automatically, filter by audience, and can be annotated and rearranged collaboratively with comments on any node. This is the canvas view Justin asked for and the base PAP-113 (agent org chart) reuses. Planned as three work packages; the umbrella owns the integration test and performance evidence.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Canvas node and edge types with graph loader** — `@xyflow/react` 12 (per PAP-127) custom nodes `PageNode`, `EntityNode`, `ExternalNode`, `StartNode`, `GroupNode`, `NoteNode`, `RegionNode`; edges `navigate`, `mutation`, `integration`, `reads`, `writes`; oRPC `canvas.graph.get(appId)` serving `FlowGraph` from PAP-123 with `specHash`; locked spec-derived elements.
2. **Collaborative overlay: notes, regions, overrides in Yjs** — room `canvas:<appId>` on PAP-140 holding `positions`, `notes`, `regions`, `hidden`, `viewportBookmarks`; presence cursors from PAP-141; undo via `y-undomanager`; reset layout for selected nodes.
3. **Filters, deep links, export and 300-node performance run** — audience and surface filters, edge-kind toggles, search and focus, minimap, `?node=&audience=` deep links, PNG/SVG export (`html-to-image`), stale banner on `specHash` change, fps evidence.

Parent owns route `/_app/dev/canvas`, comment anchors on nodes (`canvas_node`, PAP-131), `docs/collab/canvas.md`, integration test.

Out: editing specs on the canvas (PAP-124), freehand drawing (PAP-157), the org chart itself.""",
"Spec": """* Budget: 300 nodes and 600 edges at 60 fps while panning on a 2020 laptop; `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4.
* Merge rule: generated positions apply unless an override exists.
* Colours and type from PAP-66 tokens; dark theme; minimum readable label at zoom 0.6.
* Room authorised for tenant staff via the PAP-140 auth hook.""",
"Interface contract": """Exposes: package `packages/collab/canvas` with `<PaperCanvas graph overlayRoom filters onNodeOpen />`, node type registry `registerNodeType(kind, component)` (PAP-113 registers `CharacterNode`), `CanvasOverlayDoc` Yjs schema (`Y.Map` keys above), `useCanvasOverlay(room)`, `exportCanvas({ format, region })`; oRPC `canvas.graph.get(appId) -> { graph: FlowGraph, specHash, generatedAt }`; comment anchor `canvas:<canvasId>:<nodeId>`; deep-link params. Consumes: `FlowGraph { nodes[{ id, kind, label, route?, surface?, audiences[], status }], edges[{ id, from, to, kind, on?, guard? }] }` from PAP-123, provider from PAP-140, awareness payload from PAP-141, `useThreads` from PAP-131, thumbnails from PAP-82 when present.""",
"Definition of done": """* All three work packages merged; integration test green; performance run shows 55 fps or more on a generated 300-node graph (numbers in the comment).
* Screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 render read-only with a "larger screen recommended" notice.
* axe clean for toolbar and node focus order; `docs/collab/canvas.md`; CHANGELOG entry; Linear comment with screenshots, PAP-83 video and demo link; PAP-113 owner confirms the node API is reusable.""",
"Test plan": """* Integration (parent): Playwright, two contexts on the example graph: filter by audience `customer`, drag `PageNode` "Inbox" in context A and assert its position in B within 1 s, add a note, comment on a node, export PNG and assert file size > 0, change `specHash` on the mock and assert the stale banner. Runs at 1280 and 1920.
* Performance: Playwright CDP trace while panning a generated 300/600 graph for 5 s; assert mean fps ≥ 55; result JSON committed.
* Unit tests per work package (loader mapping, override merge, filter logic, stale detection, export bounds).
* Visual: Gate 3 baselines at five widths, both themes; Storybook stories per node type with axe.""",
"Demo": "Open `/_app/dev/canvas`, filter to the customer audience, drag a page node, add a sticky note, open a second tab and see both changes; click a node, press `Enter` to open its spec; export PNG. Under two minutes.",
"Edge cases": """* Renamed page id: orphaned override listed by a cleanup action.
* Two users drag one node: Yjs last writer wins with a brief cursor highlight.
* Hocuspocus down: read-only from JSON with a banner.
* Over 500 `reads` edges: hidden by default, toggle shows them.
* 20k-pixel export: viewport or selection only, capped at 8k pixels.""",
"Dependencies": "PAP-114, PAP-123, PAP-127, PAP-140 (hard). Soft: PAP-131, PAP-141, PAP-82. Blocks PAP-113, PAP-157; shares overlay code with PAP-137.",
"Agent": "Built by Nova (Canvas Cartographer, CRDT Engineer). Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Iris for visual consistency.",
"Size": "L, planned as three M work packages (child issues pending the issue limit).",
}

R["PAP-133"] = {
"Goal": "Generate changelogs nobody writes by hand: conventional commits and PR summaries become `CHANGELOG.md`, per-release notes in the docs engine and per-tenant, per-audience “What's new” entries in the product, with a Claude rewrite from developer to human language. Moved to the first collab milestone because PAP-52 (release tags) consumes its CLI.",
"Scope": """In:

* `packages/collab/changelog/` with `pnpm changelog build [--from <tag>] [--to HEAD]`: `conventional-commits-parser` 6 over commits with `Linear:` and `Character:` trailers (PAP-46); merged PR bodies fetched from Forgejo or GitHub, `## Summary` and `## Changelog` sections parsed per PAP-49 (`audience: internal|staff|customer`, `headline`, `group`, `tenants[]`).
* Classification via `changelog.config.ts`: scope → app or package; type → Added, Changed, Fixed, Security, Performance, Docs; `feat!` → Breaking.
* Outputs: `CHANGELOG.md` (Keep a Changelog), `docs/changelog/<version>.mdx` rendered by PAP-128, rows in `changelog_entry` (`id`, `tenant_id?`, `app_id`, `version`, `audience`, `section`, `headline`, `body_md`, `pr_url`, `issue_key`, `published_at`, `hidden`, `needs_review`).
* Rewrite: staff and customer entries rewritten by a Claude call with the Changelog Scribe prompt, stored beside the original, `needs_review` until Quill's pass or Justin's approval in the release digest (PAP-89).
* In-app "What's new": popover and `/_app/whats-new`, unread badge from `user_changelog_seen.last_version`; public `/_public/changelog`.
* Trigger: PAP-52 runs `changelog build` per tag; nightly "unreleased" preview.

Out: marketing posts (PAP-192), email announcements (notifications), feature flags.""",
"Spec": """* Deterministic ordering; regeneration per version is idempotent by hash.
* Entries link PR, issue and page spec via `SpecRef` when `specs/pages/*` changed.
* RLS `tenant_id is null or tenant_id = current`.
* Rewritten copy: headline under 90 characters, body under 60 words, no character names, present tense.
* Version from the tag; preview uses `next`.""",
"Interface contract": """Exposes: CLI `changelog build` and its JSON feed `docs/.generated/changelog/<version>.json` `{ version, date, entries: [{ id, audience, section, headline, body, prUrl, issueKey, specRef? }] }` (agreed first so PAP-52 can call it), table `changelog_entry`, oRPC `changelog.list({ audience, since })`, `changelog.markSeen(version)`, event `changelog.published { version, audiences[] }` for PAP-136, MDX pages under `docs/changelog/`. Consumes: commit trailer grammar from PAP-46, PR template sections from PAP-49, tag hook from PAP-52, `renderMdx` from PAP-128, digest approval flow from PAP-89.""",
"Definition of done": """* Running on paperos-template history produces a correct `CHANGELOG.md` for the first tagged release (link).
* Popover and page screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; public route shows only customer entries.
* `docs/collab/changelog.md` explains PR frontmatter; CHANGELOG entry about the changelog; Linear comment with generated files and screenshots.""",
"Test plan": """* Vitest: parser fixtures (20 commits incl. breaking, revert, merge, squash), scope mapping, section ordering, idempotent rebuild hash, rewrite output validation (headline length, forbidden words), `group` merging.
* Integration: build against a fixture git repo with two tags and mocked Forgejo PR API; the JSON feed matches a snapshot; a PR without `## Changelog` triggers the bot-comment call.
* Playwright: unread badge appears after seeding a new version and clears after viewing; anonymous `/_public/changelog` lists no `internal` or `staff` entries; run at 375 and 1280.
* Visual: Gate 3 baselines for popover and page at the seven widths, both themes.""",
"Demo": "Run `pnpm changelog build --from v0.1.0` on the template, open the generated `CHANGELOG.md`, then open `/_app/whats-new` to see the rewritten entries with the unread badge; open `/_public/changelog` in a private window and confirm only customer entries. Under two minutes.",
"Edge cases": """* Non-conventional commit: goes to Internal, hidden from customers; reverts remove the reverted entry.
* Squash of ten commits: PR body wins for the summary.
* Rewrite fails or exceeds budget: original shown to staff, hidden from customers until reviewed.
* Hotfix tag: entry under the patch version and the next minor's Fixed.""",
"Dependencies": "PAP-46 (hard, encoded). Soft: PAP-49, PAP-52 (mutual; feed JSON agreed here first), PAP-128, PAP-89. Blocks PAP-52; consumed by PAP-192 and PAP-136.",
"Agent": "Built by Quill (Changelog Scribe) with Forge on the release hook. Reviewed by Sentinel (Code Reviewer) and Beacon for customer copy rules.",
"Size": "M: parsing and rendering are standard; the rewrite and review loop needs care.",
}

R["PAP-134"] = {
"Goal": "Make the rules and skills that govern agents visible and governable in the product: every `CLAUDE.md`, rules file, skill, agent definition and policy is a browsable object with owners, version history, usage from the prompt log and a propose-edit flow that opens a PR. Justin sees what agents are told without opening the repo.",
"Scope": """In:

* Indexer `pnpm rules:index` in `packages/collab/rules/` over `.claude/CLAUDE.md`, `.claude/rules/**/*.md`, `.claude/skills/*/SKILL.md` (plus `skills.json` from PAP-105), `.claude/agents/*.md` (PAP-104), `docs/policies/**/*.md` → `docs/.generated/rules-index.json`; frontmatter validated with PAP-103 and PAP-105 schemas.
* oRPC `rules.list`, `rules.get(id)`, `rules.history(id)` (commits via the Forgejo API), `rules.diff(id, from, to)`, `rules.usage(id)` (sessions from PAP-129 where `tool_name = 'Skill'` or `SessionStart` with character), `rules.proposeEdit({ id, content, message })`.
* UI `/_app/dev/rules` (developer, `staff.admin`): list grouped by kind with search and filters; detail with markdown via the PAP-128 renderer, metadata sidebar, History tab with diffs (`react-diff-viewer-continued`), Usage tab (30-day sessions, sparkline, links to PAP-135), Propose edit (CodeMirror 6, branch `rules/<id>`, PR link).
* Cross-links skill ↔ agent ↔ referenced rules; registered as `rule_skill` search entity for PAP-138.

Out: executing skills, editing `main` directly, per-tenant rules.""",
"Spec": """* Content read from the built git ref (`import.meta.glob`) and refreshed from Forgejo for other org repos; ids `repo:kind:name`.
* 1500-word skill limit from PAP-105 shown as a warning badge.
* `rules.propose` permission (staff.admin, Atlas, Quill); agent proposals carry attribution.
* Index rebuilt per deploy; history and usage cached 5 minutes.""",
"Interface contract": """Exposes: `RuleObject { id, kind: rule|skill|agent|policy, path, title, description, version, owners[], allowedCharacters[], wordCount, updatedAt, lastCommit, tags[] }` and `rules-index.json`; oRPC procedures above; search entity `rule_skill`; comment anchor `entity:rule_skill:<id>` (PAP-131); page consumed by PAP-112 (character docs link here). Consumes: `skills.json` and SKILL frontmatter from PAP-105, character frontmatter from PAP-103/PAP-104, `renderMdx` from PAP-128, Forgejo client from PAP-54's first child when merged (else a 40-line fetch wrapper here), `promptLog.events.list` from PAP-129.""",
"Definition of done": """* Index covers all objects in paperos-template; a missing frontmatter field fails `docs:lint`.
* Usage tab shows real sessions from a seeded prompt log.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; axe clean; `docs/collab/rules-registry.md`; CHANGELOG entry; Linear comment with screenshots.
* Justin reviews one rule in-app and comments on it.""",
"Test plan": """* Vitest: indexer over a fixture `.claude/` tree (valid, missing SKILL.md, oversized skill), frontmatter validation, id derivation across two repos, usage aggregation from fixture events.
* Integration: `rules.history` and `rules.diff` against a mocked Forgejo API; `rules.proposeEdit` creates a branch and PR on a scratch Forgejo repo in CI (PAP-273 stack) and returns the URL; `callAs(customer)` gets 403.
* Playwright: browse to `review-pr`, open History, open a diff, propose an edit and see the PR link; run at 375 and 1280.
* Visual: Gate 3 baselines for list and detail at the seven widths, both themes.""",
"Demo": "Open `/_app/dev/rules`, filter to skills, open `review-pr`, read the word-count badge, open Usage to see last week's sessions, open History and a diff, click Propose edit, change one line, submit and open the PR. Under two minutes.",
"Edge cases": """* Skill folder without SKILL.md: listed as invalid with a fix link.
* Forgejo unreachable: content from the build; history shows retry.
* 20k-word CLAUDE.md: TOC, no word-limit badge.
* Proposed edit conflicts with a merge: PR shows conflict; no auto-resolve.
* Older sessions lack Skill events: "no data before <date>".""",
"Dependencies": "PAP-128, PAP-105 (hard, encoded). Soft: PAP-104, PAP-276 (Forgejo client), PAP-129, PAP-131. Consumed by PAP-112.",
"Agent": "Built by Quill (Prompt Logger) with Nova on UI. Reviewed by Atlas (governance) and Sentinel (Code Reviewer).",
"Size": "M: indexer plus a CRUD-like UI with git history and a PR flow.",
}

R["PAP-135"] = {
"Goal": "Let Justin audit any agent decision in minutes: a browser over the prompt-log store that filters sessions by issue, character, status and cost, replays a session turn by turn with tool calls expanded, and jumps to the PR, Linear issue and worktree. Reviewers flag sessions as golden or failure for evals.",
"Scope": """In:

* Route `/_app/dev/prompt-log` (platform tenant; `staff.admin` and agent principals) with a sessions grid on PAP-165 using a PAP-161 view model: character, sub-agent, issue, status, model, duration, tokens, cache, cost, PR, started; saved views "Today", "Failed", "Over $5".
* Detail `/_app/dev/prompt-log/$sessionId`: metadata header with cost and token gauges, links (PR, issue, branch, worktree, parent), virtualised timeline (`@tanstack/react-virtual` 3) coloured by role, collapsible tool calls with pretty JSON and on-demand blobs, `[REDACTED:kind]` markers, `PreCompact` markers, nested sub-agent sessions.
* Replay: `j`/`k`, space to autoplay 1x to 8x, running cost bar, "jump to first tool error", "jump to final message".
* Actions: Flag as golden or failure → PAP-110 `evals.flag`; Open issue via PAP-131 escalation; Copy permalink `?seq=`.
* Stats `/_app/dev/prompt-log/stats` from `promptLog.stats`, charts per the dataviz palette (PAP-170 or Recharts fallback).

Out: ingestion (PAP-129), budgets (PAP-111), daily reports (PAP-98).""",
"Spec": """* Cursor pagination; grid pages of 100; events in 500-event chunks by `seq` with prefetch.
* In-session search: client-side over loaded chunks plus `events.list({ q })`.
* Grid becomes a card list under `md`; gauges stack at 320 and 375.
* Timestamps in viewer timezone, UTC on hover.""",
"Interface contract": """Exposes: routes above; permalink grammar `/_app/dev/prompt-log/<sessionId>?seq=<n>` used by PAP-98 metering comments, PAP-134 usage links and PAP-144 agent attribution; `SessionLink({ sessionId, seq? })` component in `packages/collab`; view model `prompt-sessions.view.json`. Consumes: `promptLog.sessions.list|get`, `promptLog.events.list`, `promptLog.stats` (PAP-129); `GridView` and `ViewModel` (PAP-165, PAP-161) with a plain TanStack Table fallback; `evals.flag({ sessionId, verdict, note })` (PAP-110); `threads.createIssue` (PAP-131); Electric shape on `prompt_session` for live tailing (PAP-143) else 5 s polling.""",
"Definition of done": """* Seeded store of 50 sessions browsable; a 10k-event session scrolls at 60 fps (measurement in comment).
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; replay video from PAP-83.
* axe clean; `docs/collab/prompt-log-ui.md`; CHANGELOG entry; Linear comment with screenshots and video.
* Justin replays one real session and confirms PR link and cost match the metering comment.""",
"Test plan": """* Vitest: chunk loader (boundaries, prefetch), permalink resolution to a virtual index, gauge math, sub-agent nesting from `parent_session_id`, redaction marker rendering.
* Integration: oRPC calls through `callAs(staffAdmin)` succeed and `callAs(customerAdmin)` 403 on both list and events.
* Playwright (seeded 50 sessions): filter by character, open a session, expand a tool call, replay with keyboard to `seq` 42, flag as golden against a mocked eval endpoint, open permalink `?seq=42` and assert the row is in view; run at 375 and 1280.
* Performance: CDP trace scrolling a 10k-event session; assert ≥ 55 fps.
* Visual: Gate 3 baselines for grid, detail and stats at the seven widths, both themes.""",
"Demo": "Open `/_app/dev/prompt-log`, pick “Over $5”, open the top session, press space to autoplay, hit “jump to first tool error”, expand the call, click the PR link, copy the permalink and paste it in a new tab. Under two minutes.",
"Edge cases": """* Running session: live status, timeline tails new events.
* Gaps: warning rows with the missing range.
* Fully redacted message: row shows kind counts.
* Expired blob: "content expired" with size.
* Grid engine unmerged: TanStack Table fallback with a documented TODO.""",
"Dependencies": "PAP-129, PAP-165 (hard, encoded; fallback for the grid). Soft: PAP-110, PAP-161, PAP-170, PAP-101, PAP-143, PAP-131. Consumed by PAP-134, PAP-98, PAP-144.",
"Agent": "Built by Nova (Views Engineer) with Quill (Prompt Logger) defining reviewer needs. Reviewed by Sentinel (Visual Inspector, Code Reviewer) and Atlas.",
"Size": "M: two screens over an existing API; virtualisation and replay are the work.",
}

R["PAP-136"] = {
"Goal": "Umbrella for the user-facing half of notifications: the inbox with a live badge, preference matrix with quiet hours and digests, and the Slack channel. Delivery itself (kinds registry, worker, in-app rows and email) moves to the P1 notification core issue so Justin's queue and gate results do not wait for comments. Planned as three work packages.",
"Scope": """Work packages (child issues pending the Linear issue limit):

1. **Inbox UI, bell badge and preferences page** — bell popover (latest 10, mark read, archive), `/_app/inbox` with filters and day grouping, `/_app/settings/notifications` matrix of kinds by channel with test send; live badge from an Electric shape on `notification` (PAP-143) with polling fallback.
2. **Digests, quiet hours and burst collapse** — `notification_preference.digest` and `quiet_hours`, hourly and daily digest jobs, same-kind-same-source collapse within 10 minutes, per-tenant preference rows with a global fallback.
3. **Slack channel and tenant Slack configuration** — `tenant_slack_config` (encrypted webhook), Block Kit templates per kind, revoked-webhook banner, per-kind channel routing.

Parent owns `docs/collab/notifications.md` end-user section, integration test and Gate 3 baselines.

Out: kinds registry, worker, email channel (notification core), push (realtime push transport gap), SMS, marketing email (PAP-191).""",
"Spec": """* Preferences are per tenant with a global fallback row; unsubscribed kinds are `suppressed`, not failed.
* Quiet hours computed with `@date-fns/tz`, DST-safe; digests cap at 50 items with a link to the inbox.
* Slack deliveries go through the core's `notification_delivery` rows with `channel: 'slack'`.
* Inbox rows follow the `Notification` type from the core; no second schema.""",
"Interface contract": """Exposes: routes `/_app/inbox`, `/_app/settings/notifications`; components `NotificationBell`, `InboxList`, `PreferenceMatrix`; oRPC `notifications.list({ unread?, kind?, cursor })`, `notifications.markRead(ids)`, `notifications.archive(ids)`, `preferences.get|set`, `slack.configure({ webhookUrl, defaultChannel })`, `slack.test()`; channel adapter `SlackChannel implements Channel` registered with the core. Consumes: `Notification`, `NotificationKind`, `Channel` interface, `registerChannel()` and `resolvePreferences()` from the notification core; shape proxy (PAP-143); `renderEmail` (PAP-235) for digest emails; secret encryption helper (data-layer gap) for the webhook.""",
"Definition of done": """* All three work packages merged; integration test green.
* Inbox and preferences at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* axe clean; docs; CHANGELOG entry; Linear comment with screenshots and delivery logs.
* `issue.needs_justin` reaches Justin's configured channels with the PAP-94 batching rule.""",
"Test plan": """* Integration (parent): Playwright, two contexts: A mentions B in a comment; B's bell badge increments within 2 s, popover shows the item, inbox marks it read; B sets `comment.mentioned` to digest-only and a second mention produces no badge but appears in the next digest run (job triggered via `/__test` clock, PAP-240); a Slack test webhook receives a Block Kit payload (mock server asserts schema).
* Unit tests per work package (preference resolution matrix, quiet hours across DST, collapse and digest grouping, Block Kit snapshots).
* Visual: Gate 3 baselines at the seven widths, both themes.""",
"Demo": "Mention yourself from a second account, watch the bell badge, open the popover and mark read, open settings, switch mentions to daily digest, click “Test send” for Slack and see the message land in the test channel. Under two minutes.",
"Edge cases": """* User in two tenants: separate preference rows.
* Slack webhook revoked: delivery fails; admin banner.
* Digest with 300 items: truncated to 50.
* Deleted source: notification kept with "no longer available".""",
"Dependencies": "Notification core (hard, new issue), PAP-43, PAP-131 (first producer; relation kept), PAP-143 (soft). Consumed by PAP-94, PAP-88, PAP-133, PAP-199.",
"Agent": "Built by Nova with Forge (Ops Runner) on Slack delivery. Reviewed by Sentinel (Security Auditor for the webhook secret, Visual Inspector) and Beacon.",
"Size": "L, planned as three S/M work packages (child issues pending the issue limit).",
}

R["PAP-137"] = {
"Goal": "Close the loop from picture to ticket: a viewer for every PR run's screenshots and video replays where anyone draws a box or pin on an image or paused frame, comments, sees the vision agent's findings overlaid and creates a Linear issue with cropped evidence in one click.",
"Scope": """In:

* Routes `/_app/dev/qa` (runs by PR and date from PAP-97 records) and `/_app/dev/qa/$runId` reading the manifest `visual.json` and `videos.json` (PAP-239 contract) from MinIO (PAP-37), grouped by page with a width by theme matrix.
* Viewer in `packages/collab/annotations/`: image zoom and pan, video with frame stepping (`requestVideoFrameCallback`), flow captions from the contact sheet, annotation layer reusing the PAP-132 `RegionNode` overlay for rectangles and pins with mouse, touch and keyboard (arrows position, `Shift` plus arrows size).
* Annotations are PAP-131 threads with `anchor_type: screenshot`; PAP-84 findings rendered read-only with confirm and dismiss posting back to the run comment.
* Create issue: `threads.createIssue` with title `[visual] <page> @<width> <theme>: <first line>`, description with the padded crop uploaded via signed URL, image, run and PR links, flow step and time code; labels `Bug` plus the page's Surface; project from spec `meta.owner`; PR back-link via PAP-97.
* Compare mode: side by side or onion-skin against the `main` baseline.

Out: producing media (quality), pixel-diff gating, freehand tools (PAP-157), customer access.""",
"Spec": """* Rects stored as image percentages; crops use natural size.
* Video anchors in milliseconds; open seeks and pauses.
* `qa.view` for manifests, `qa.report` for issue creation.
* Deep link `?file=<id>&t=<ms>&thread=<id>`; first image under 1 s on a 1920 grid via MinIO variants.""",
"Interface contract": """Exposes: `AnnotationViewer`, `useRunManifest(runId)`, screenshot anchor `{ fileId, frame?: ms, rect: { x, y, w, h } }` (percent) registered in PAP-131's `CommentAnchor` union, finding overlay adapter `VisionFinding -> Overlay`, issue builder `buildVisualIssue(annotation)`, `InkAnnotationLayer` slot for PAP-157. Consumes: `visual.json` `{ screenshots: [{ id, page, width, theme, path }] }` and `videos.json` `{ videos: [{ id, flowId, width, path, steps: [{ t, label }] }] }` from PAP-239; `vision.json` findings `{ fileId, severity, kind, rect, message }` from PAP-84; `threads.createIssue` from PAP-131; run records and PR comment API from PAP-97; signed uploads and variants from PAP-37.""",
"Definition of done": """* Seeded run browsable; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 support viewing and pinning, not compare.
* Keyboard-only annotation recorded as a PAP-83 flow; axe clean.
* `docs/collab/qa-viewer.md`; CHANGELOG entry; Linear comment with screenshots, the test issue and the video.
* Sentinel's Visual Inspector posts one real finding a human confirms in the viewer.""",
"Test plan": """* Vitest: percent to pixel math at three image sizes, crop generation with padding and clamping, title and description builders, finding mapping, rect under 8 px becomes a pin.
* Integration: manifest loader against a fixture MinIO bucket with a partial shard; `callAs(customer)` denied on `qa.view`.
* Playwright (seeded run): draw a rectangle, comment, create issue against mocked PAP-101 and assert the crop upload; pause a video at 3200 ms, pin, copy permalink, reopen at the frame; compare mode toggles onion-skin; run at 1280 and 1920, plus pin-only at 375.
* Visual: Gate 3 baselines for viewer and compare at five widths, both themes.""",
"Demo": "Open the latest run, click the 1280 dark screenshot of Inbox, drag a box over the misaligned button, type “off by 4 px”, click Create issue and open the Linear link with the crop embedded; scrub the sign-in video, pin a frame and copy the permalink. Under two minutes.",
"Edge cases": """* Shard still running: "3 of 4 shards" live indicator.
* New commit regenerates screenshots: old annotations under "previous run".
* Unsupported video codec: contact sheet fallback.
* 12k-pixel screenshot: tiled rendering, memory under 300 MB.
* No spec owner: default project with a note.""",
"Dependencies": "PAP-131, PAP-83 (hard, encoded). Soft: PAP-82, PAP-84, PAP-239, PAP-37, PAP-97, PAP-132. Consumed by PAP-89.",
"Agent": "Built by Nova (Canvas Cartographer) with Sentinel (Visual Inspector) defining the finding overlay. Reviewed by Sentinel (Code Reviewer) and Iris.",
"Size": "M: viewer and overlay build on comments and canvas code; video frames are the tricky part.",
}

R["PAP-138"] = {
"Goal": "One search box over everything the organisation knows: docs, ADRs, page specs, comments, prompt sessions, rules and skills and mirrored issues, with hybrid ranking, facets, audience-safe results and actions per hit, reachable from the command palette on every page.",
"Scope": """In:

* Registrations in `packages/collab/search/registrations.ts` through PAP-39 `registerSearchable`: `doc`, `adr`, `page_spec`, `comment`, `prompt_session`, `rule_skill`, `issue`, each with title, body, facets and route builder.
* Indexers: `pnpm search:index-static` for docs, ADRs, specs and rules (hash upserts, delete vanished paths); registry triggers for comments and issues; prompt sessions on `ended_at` with a one-time 200-word Claude summary stored in `prompt_session.summary`.
* oRPC `search.query({ q, kinds?, facets?, cursor, mode })` wrapping the registry with an audience allowlist (customers: `doc`, `changelog`; staff: all but `prompt_session` and `rule_skill` unless `staff.admin`).
* UI: PAP-151 palette provider (`mod+k` "Search everything" with grouped top results) and `/_app/search` with facets, keyboard navigation, highlighted snippets and per-result actions; recents in `localStorage`.
* Admin `search:reindex --kind` and `/_app/dev/search-health`.

Out: the engine (PAP-39), external sources, Q&A chat.""",
"Spec": """* Snippets via `ts_headline`, 160 characters; vector hits fall back to the first matching sentence.
* Ranking: registry hybrid score, recency half-life 30 days for comments and issues, kind weights `doc` 1.0, `page_spec` 0.9, `issue` 0.9, `comment` 0.7, `prompt_session` 0.6.
* Operators `kind:`, `owner:`, `is:open` parsed client-side.
* p95 under 300 ms hybrid on 100k documents; 150 ms debounce.
* Only counts per kind are logged, never query text.""",
"Interface contract": """Exposes: `search.query` result `{ hits: [{ kind, id, title, snippet, route, facets, score }], facets: { kind: [{ value, count }], ... }, cursor }`; `SearchProvider` and `useSearch()`; palette command `search.open`; `registerSearchKind()` docs for module authors (PAP-28 modules register their own kinds); health page JSON. Consumes: `registerSearchable`, `search()` and `ts_headline` helpers from PAP-39; `renderMdx` text extraction from PAP-128; `adr-index.json` (PAP-130); `rules-index.json` (PAP-134); `comment` tables (PAP-131); `prompt_session` (PAP-129); PM mirror tables (PAP-100); `CommandPalette` provider slot (PAP-151).""",
"Definition of done": """* Seeded corpus (500 docs, 50 specs, 2k comments, 300 sessions, 1k issues) searchable from palette and page; customer actor sees only allowed kinds.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; benchmark committed with p95 under 300 ms.
* axe clean; `docs/collab/search.md` including how to register a kind; CHANGELOG entry; Linear comment with screenshots and benchmark; video of Justin finding a session by issue key.""",
"Test plan": """* Vitest: registrations validate at boot, operator parsing, allowlist per audience, ranking weights and recency boost, static indexer deletes vanished paths.
* Integration (Postgres with pgvector in CI): seeded corpus; `callAs(customer)` never returns `internal` comments even with `kinds: ['comment']`; reindex of one kind leaves others untouched.
* Benchmark: k6 or Vitest bench, 200 hybrid queries on the 100k corpus, p95 asserted under 300 ms; JSON committed.
* Playwright: `mod+k`, type "PAP-129", open the prompt session hit; on `/_app/search` filter by facet and open one result of each kind; run at 375 and 1280.
* Visual: Gate 3 baselines for palette and results page at the seven widths, both themes.""",
"Demo": "Press `mod+k`, type “Hocuspocus”, see grouped hits across docs, ADRs and comments, press `Enter` on the ADR; open `/_app/search?q=PAP-140`, filter to prompt sessions, open one and land in the replay. Under two minutes.",
"Edge cases": """* Renamed doc: deleted by vanished path before upsert.
* Summary generation fails: session indexed by issue and character only.
* 2k-character query: truncated to 500 with a notice.
* Vector model changed: rows marked stale on the health page; keyword still works.
* Registry unmerged: temporary global `mod+k` handler with a TODO.""",
"Dependencies": "PAP-39, PAP-128 (hard, encoded). Soft: PAP-130, PAP-131, PAP-129, PAP-134, PAP-100, PAP-151. Consumed by PAP-109.",
"Agent": "Built by Nova (Views Engineer) with Forge (Schema Wright) on indexers. Reviewed by Sentinel (Security Auditor for audience leakage, Visual Inspector) and Quill.",
"Size": "M: the registry does the heavy lifting; seven registrations, indexers and the palette UI remain.",
}

# PAP-136 re-phased to P1 (audit): the core cannot be a separate issue while the workspace is at the Linear issue limit,
# so it is work package 1 here and independent of comments.
R["PAP-136"] = {
"Goal": "Deliver mentions, review results, release news and Justin's decisions where people are: a kinds registry and worker that turn domain events into notification rows, in-app and email channels, then an inbox, preferences with digests and quiet hours, and Slack. Re-phased to P1 because PAP-94, PAP-88 and PAP-89 deliver through it; work package 1 must not depend on comments.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Notification core** — schema `notification`, `notification_preference`, `notification_delivery`; kinds registry (`issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `import.finished`, `comment.mentioned`, `comment.replied`, `thread.resolved`) with default channels per audience and templates; pg-boss worker (PAP-43) expanding recipients, applying preferences, writing rows and enqueuing deliveries with 3 retries; `InAppChannel` and `EmailChannel` (React Email via PAP-235, per-kind one-click unsubscribe JWT). Depends only on PAP-43 and the event bus.
2. **Inbox UI, bell badge and preferences page** — bell popover (latest 10), `/_app/inbox`, `/_app/settings/notifications` matrix; live badge via Electric shape (PAP-143) with polling fallback.
3. **Digests, quiet hours and burst collapse** — hourly and daily digest jobs, `quiet_hours` with `@date-fns/tz`, same-kind-same-source collapse within 10 minutes, per-tenant preference rows with a global fallback.
4. **Slack channel and tenant configuration** — `tenant_slack_config` with encrypted webhook, Block Kit templates, revoked-webhook banner.

Out: push (planned realtime push transport), SMS, marketing email (PAP-191), Linear-side notifications.""",
"Spec": """* Actor never notified of own action; recipients without access to the source are `suppressed`; idempotency key `(kind, source, recipient, bucket)`.
* In-app row within 2 s of emit; email within 60 s outside digests; `issue.needs_justin` applies the PAP-94 batching rule.
* Digests cap at 50 items; recipient expansion capped at 500.""",
"Interface contract": """Exposes: `Notification`, `NotificationKind`, `defineKind({ id, audiences, defaultChannels, template })`, `registerChannel(name, impl)`, `Channel { send(n, recipient) -> DeliveryResult }`, `notify(kind, { recipients, payload })`, `resolvePreferences(userId, tenantId, kind)`; oRPC `notifications.list|markRead|archive`, `preferences.get|set`, `slack.configure|test`; components `NotificationBell`, `InboxList`, `PreferenceMatrix`; unsubscribe route `/n/unsubscribe/:token`; tables above. Consumes: `emit()`/`subscribe()` from `packages/core/events` (planned; until then an in-process emitter with the same signature in `packages/collab/notifications/bus.ts`), `defineJob` (PAP-43), audience segments (PAP-55), `renderEmail` (PAP-235), email adapter (planned `packages/email`, else Resend with allowlist and Mailpit), shape subscriptions (PAP-143), producers PAP-131, PAP-97, PAP-88, PAP-133, PAP-199, `SecretStore` (PAP-17) for the webhook.""",
"Definition of done": """* Work package 1 alone: a `review.gate_failed` event produces an in-app row and a Mailpit email in CI; `issue.needs_justin` reaches Justin with batching.
* All four merged: inbox and preferences screenshots at the seven widths in light and dark; a Slack test message delivered.
* axe clean; `docs/collab/notifications.md` including how to add a kind; CHANGELOG entry; Linear comment with screenshots and delivery logs.""",
"Test plan": """* Vitest: kind registry validation, recipient expansion cap, suppression rules, idempotency on retry, preference resolution matrix, quiet hours across midnight and DST, collapse and digest grouping, template snapshots (email HTML, in-app markdown, Block Kit).
* Integration (Postgres, pg-boss, Mailpit, mock Slack): emit each kind, assert row within 2 s and email within 60 s; provider failure retries three times then `failed`; `callAs(userB)` cannot read userA's rows; Slack 410 marks the webhook broken.
* Playwright, two contexts: mention → badge within 2 s, mark read; switch a kind to daily digest and run the job through the `/__test` clock (PAP-240); unsubscribe link suppresses the next email; run at 375 and 1280.
* Visual: Gate 3 baselines for inbox and settings at the seven widths.""",
"Demo": "Run `pnpm notify:demo review.gate_failed --to justin`, watch the bell badge and the Mailpit email; open settings, move mentions to a daily digest, click Slack “Test send” and see the message land. Under two minutes.",
"Edge cases": """* Provider outage: queued up to 24 h, then failed with an ops alert (PAP-40).
* Deleted source: kept with "no longer available"; digest of 300: truncated to 50.""",
"Dependencies": "PAP-43 (hard) for work package 1; PAP-131 (relation kept; first comment producer, needed only for work package 2's mention flows). Soft: PAP-55, PAP-235, PAP-143, PAP-240, PAP-17, planned event bus and email package (data-layer). Consumed by PAP-94, PAP-88, PAP-89, PAP-133, PAP-199, PAP-97.",
"Agent": "Built by Forge (Ops Runner) for the core and Slack with Nova on inbox and preferences. Reviewed by Sentinel (Security Auditor for unsubscribe tokens and the webhook secret, Visual Inspector) and Beacon for deliverability.",
"Size": "L, planned as four work packages (M, M, S, S) that become child issues once the issue limit is lifted.",
}
