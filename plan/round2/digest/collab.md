# collab — In-App Collaboration & Knowledge
PHASE P1 prio 1 dependsOn ['realtime', 'data-layer']
SUMMARY: Comments anchored anywhere, a canvas UX-flow view, an in-app docs engine, changelogs, a prompt/response log and browsable rules and skills.
DESC: Goal: the product contains its own documentation, discussion and memory. A docs engine renders repo-stored MDX in-app with search and git versioning. A prompt-log store records every agent session (prompts, responses, tool calls, tokens, cost) with redaction, and a browser lets Justin replay any session and jump to its PR. Comments anchor to entities, page elements, doc blocks and screenshots and can spawn Linear issues. The canvas view shows the UX flow of the whole app generated from specs and editable in realtime. Changelogs are generated per app and per tenant; rules and skills are browsable and versioned objects. A decision log holds ADRs. Non-goal: replacing Notion for external documents; the docs engine can import from it.
MILESTONES: ['Docs and prompt log stores 2026-09-21: Docs engine, prompt-log store, decision log, canvas/editor research', 'Comments and canvas 2026-09-26: Comments, canvas view, changelog, rules/skills registry, prompt log UI', 'Knowledge surfaced everywhere 2026-09-30: Notifications, screenshot annotations, unified search']


## PAP-127 [P0 Research S prio2 Ready for Claude] Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR
key=collab/collab-research milestone=Docs and prompt log stores agent=Built by Scout (Library Evaluator) with Nova (Canvas Cartogr
blockedBy=[] blocks=['PAP-142', 'PAP-132']
GOAL: Choose the canvas library (tldraw vs React Flow) and the rich-text editor (Tiptap vs BlockNote) for PaperOS in one time-boxed session, with spikes that prove Yjs collaboration and our scale, and record the decision as an ADR. Everything in the collab project and the realtime text editor builds on this choice.
SCOPE: In:

* Rubric scoring per `libraries/eval-rubric` (license, maintenance, bundle size, a11y, TypeScript quality, agent-friendliness) plus collab-specific criteria: Yjs binding maturity, custom node/element API, programmatic layout, read-only and locked elements, touch and pen support, export to PNG/SVG, theming with our tokens.
* Candidates: canvas `tldraw` 3.x (note: the tldraw SDK license requires the "Made with tldraw" watermark or a paid business license, which must be scored against `libraries/license-policy`) vs `@xyflow/react` 12 (MIT); editor `@tiptap/core` 2.x or 3.x with `y-prosemirror` (MIT core, some Pro extensions paid) vs `@blocknote/core` (MPL-2.0, built on Tiptap and ProseMirror, ships Yjs collaboration and block UI).
* Spikes in `spikes/collab-research/` (throwaway, not shipped): (1) render the example flow graph shape from `spec-builder/spec-to-canvas` with 300 nodes and
SPEC(first 1200): * Time box: one session, at most 60 turns and 4 hours wall clock; if spikes are inconclusive, decide on license and model fit and record the uncertainty.
* Scores 1 to 5 per criterion with one-sentence evidence and a link; totals weighted per the rubric weights.
* Bundle measurements taken from a production Vite build of each spike, gzip sizes recorded.
* Licence check run with the CI license checker from `libraries/license-policy` on both spike lockfiles.
* Findings summarised in the Linear comment in under 300 words with the decision on the first line.
DOD:
* ADR merged with status `accepted`, scores table, spike links and a review date of 2027-01-01.
* Two spike repos or folders with README and measured numbers (FPS at 300 nodes, gzip size, time to first collaborative render).
* Registry updated for four libraries.
* Linear comment with decision, numbers and screenshots of both spikes at 1280.
* Follow-up issues adjusted: `collab/canvas-view` and `realtime/collab-text` titles reference the chosen libraries.
EDGE:
* tldraw license terms changed recently: quote the exact license text and version evaluated in the ADR.
* React Flow lacks freeform drawing for annotations: note the plan (sticky notes and shapes as custom nodes, pen via `input/pen` later).
* BlockNote pins a Tiptap version that conflicts with `realtime/collab-text` needs: record the peer dependency matrix.
* Both editors fail the a11y criterion on screen-reader navigation of tables: record as a known gap with a mitigation issue.
* Spike Hocuspocus not yet deployed (`realtime/yjs-server`): run it locally in Docker; note the difference.
* Team disagreement after the ADR: the ADR lists the criteria that would reopen it (license change, unmaintained for 6 months, blocking a11y bug).
DEPS: None hard. Uses `libraries/eval-rubric` and `libraries/license-policy` if merged, otherwise the rubric from the plan. Unblocks `collab/canvas-view`, `realtime/collab-text`, `collab/comments` editor choice.


## PAP-128 [P0 Build M prio1 Backlog] Build the docs engine: MDX docs stored in the repo, rendered in-app, searchable and versioned with git
key=collab/docs-engine milestone=Docs and prompt log stores agent=Built by Nova with Quill owning frontmatter and content conv
blockedBy=['PAP-16'] blocks=['PAP-216', 'PAP-203', 'PAP-138', 'PAP-134', 'PAP-130', 'PAP-109', 'PAP-76', 'PAP-41']
GOAL: Make documentation part of the product: MDX files stored in the repo under `docs/` render inside PaperOS with navigation, search, version history from git and audience filtering, so agents write docs next to code and Justin, staff and customers read them in-app. Every other knowledge feature (ADRs, changelog, rules, guidelines, registry) publishes through this engine.
SCOPE: In:

* `packages/collab/docs/`: Vite plugin setup with `@mdx-js/rollup` 3, `remark-gfm`, `remark-frontmatter`, `rehype-slug`, `rehype-autolink-headings`, `@shikijs/rehype` for code; loader `import.meta.glob('/docs/**/*.{md,mdx}')` producing `DocEntry { path, slug, frontmatter, headings[], Component, wordCount }`.
* Frontmatter Zod 4 schema: `title`, `owner` (character or person), `audience: developer|staff|customer|agent` (array), `tags[]`, `updated`, `status: draft|published|archived`, `specRef?`, `issue?`.
* Sidebar from folder tree plus `_meta.yaml` ordering and labels; breadcrumbs; on-page table of contents; previous and next links.
* Routes: `/_app/docs/$` splat for staff and developer audiences inside the shell (`app-shell/router-layouts`), `/_public/docs/$` for `audience: customer` pages with the public layout.
* MDX components: `Callout`, `Steps`, `Tabs`, `FileRef` (includes a fi
SPEC(first 1200): * Slugs are file paths without extension; `index.mdx` maps to the folder; redirects via `redirectFrom[]` frontmatter.
* Audience filter is enforced at build for `/_public` and at runtime with `useCan('doc.view')` in the shell; drafts hidden outside dev.
* Code blocks have copy buttons and file names; dark and light Shiki themes bound to the theme attribute from `design-system/theming`.
* Heading anchors expose `data-block-id` for comment anchoring.
* Each doc page renders within 100 ms after route load; MDX is code-split per file.
DOD:
* Twenty existing docs (template guide, ADRs, quality gates) render with sidebar, TOC and history; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Vitest: frontmatter schema, sidebar ordering, link lint, `FileRef` resolution; Playwright: navigate three pages, search returns a known page, public route hides staff docs.
* axe clean on doc pages.
* `docs/collab/docs-engine.md` explains writing a doc, components and lint; CHANGELOG entry.
* Linear comment with Pages preview and in-app screenshots.
EDGE:
* MDX compile error in one file: build reports file and line and renders an error card for that page in dev; CI fails.
* Very long page (10k words): TOC collapses to h2, content virtualisation not needed but images lazy-load.
* File renamed: `git log --follow` keeps history; old slug redirect suggested by lint.
* Same slug in two folders with different audiences: allowed; public and app routes resolve separately.
* Shallow clone in CI: history script detects `--depth` and fetches full history for `docs/` only.
* Mermaid diagram invalid: renders the source in a code block with a warning instead of a blank space.
DEPS: `app-shell/router-layouts` (hard). Soft: `data-layer/search` (index), `design-system/theming` (Shiki theme), `forge/forgejo-deploy` (edit links). Unblocks `collab/decision-log`, `collab/rules-skills-registry`, `collab/knowledge-search`, `data-layer/data-dictionary`, `design-system/guidelines-docs`, `agents/memory`, `libraries/registry`, `migration/notion`, `spec-builder/spec-docs`.


## PAP-129 [P0 Build M prio1 Backlog] Create the prompt/response log store (session, character, issue, tokens, cost, tool calls) with redaction
key=collab/prompt-log-store milestone=Docs and prompt log stores agent=Built by Forge (Schema Wright) with Quill (Prompt Logger) de
blockedBy=['PAP-33'] blocks=['PAP-135', 'PAP-107']
GOAL: Build the system of record for how agents built PaperOS: Postgres tables and an ingest API that store every session, prompt, response, tool call, token count and cost with redaction and dedupe, queryable by issue, character and PR. Credit metering, evals, memory curation and the prompt-log browser all read from here.
SCOPE: In:

* Drizzle schema in `packages/db/src/schema/prompt-log.ts`: `prompt_session` (`id` text from Claude session id, `tenant_id` platform tenant, `character`, `sub_agent`, `issue_key`, `linear_issue_id`, `repo`, `branch`, `worktree`, `model`, `launch: hook|sdk`, `parent_session_id`, `started_at`, `ended_at`, `status: running|completed|killed|failed`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cost_usd numeric(12,6)`, `pr_url`, `summary`, `redaction_count`); `prompt_event` (`id uuidv7`, `session_id`, `seq int`, `ts`, `event`, `role`, `content text`, `content_file_id` for blobs over 64 KB in `data-layer/file-storage`, `tool_name`, `tool_input jsonb`, `tool_output text`, `usage jsonb`, `cost_usd`, `model`, `redactions jsonb`, `truncated bool`), unique `(session_id, seq)`, partitioned monthly by `ts`; `prompt_model_price` (`model`, `input_per_mtok`, `output_
SPEC(first 1200): * `seq` gaps are stored on the session as `gaps jsonb` and surfaced by `stats`; a `session.killed` synthetic event from the orchestrator closes sessions.
* Cost formula: sum over events of tokens times price for the event's model at `ts`; nightly job recomputes sessions whose prices changed.
* Ingest p95 under 150 ms for a 1 MB batch; `COPY`-style multi-row insert with `ON CONFLICT DO NOTHING`.
* Indexes: `(issue_key, started_at desc)`, `(character, started_at desc)`, `(session_id, seq)`, GIN on `tool_input` for tool-name and path searches.
* Full-text: sessions registered with `data-layer/search` (`title` from issue and summary, `body` from summary) for `collab/knowledge-search`; events are not indexed.
DOD:
* Drizzle migration applied on staging; RLS tests from `data-layer/rls-tenancy` harness show a non-platform tenant sees nothing.
* Vitest: ingest dedupe, gap detection, cost computation, second-pass redaction (30 fixtures), batch cap rejection with `413`.
* Integration: a 20-turn recorded session from `agents/prompt-logging-hook` fixtures ingests fully; token totals match within 1 percent.
* Load: 50 concurrent sessions shipping 200 events each ingest under 2 minutes with no duplicates (k6 script committed).
* `docs/collab/prompt-log.md` (schema, API, retention, redaction); CHANGELOG entry; Linear comment with test and load results.
EDGE:
* Event arrives before its session's first event: session row created from the event's fields; later `SessionStart` fills details.
* Same `seq` with different content (hook retried after edit): first wins, mismatch logged to `ingest_anomaly` table.
* Model unknown in the price table: cost stored null and flagged; `stats` reports uncosted tokens separately.
* Content over 64 KB and MinIO unavailable: truncated with `truncated: true`, never rejected.
* Clock skew across hosts: ordering uses `seq`, `ts` only for display.
* Token revoked mid-session: ingest returns 401; shipper spools until the orchestrator rotates the token.
DEPS: `data-layer/core-entities` (hard, tenant and user), `data-layer/drizzle-schema`, `data-layer/api-layer`. Soft: `identity/agent-principals` (tokens; use a static per-character token from env until then), `data-layer/file-storage`. Unblocks `agents/prompt-logging-hook`, `collab/prompt-log-ui`, `pm-linear/credit-metering`, `agents/eval-harness`.


## PAP-130 [P0 Build S prio2 Backlog] Add an ADR/decision log with status, alternatives and links to issues
key=collab/decision-log milestone=Docs and prompt log stores agent=Built by Quill (Changelog Scribe). Reviewed by Atlas (decisi
blockedBy=['PAP-128'] blocks=[]
GOAL: Give every significant choice a findable, linked record: ADR files in the repo with a strict frontmatter, a CLI to create and lint them, an in-app index with status and supersession graph, and automatic Linear comments when a decision changes. The plan's fifteen decisions become the first entries.
SCOPE: In:

* Format `docs/adr/NNNN-PAP-<issue>-<slug>.md` with frontmatter (Zod 4 `AdrFrontmatter`): `id` (NNNN), `title`, `status: proposed|accepted|rejected|superseded|deprecated`, `date`, `deciders[]` (characters or Justin), `issue` (PAP key), `supersedes[]`, `supersededBy?`, `tags[]`, `reviewDate?`; body headings in order: Context, Decision, Alternatives (table with score columns when a rubric applies), Consequences, References.
* CLI `pnpm adr new "<title>" --issue PAP-12 --tags stack` (numbering per the `write-adr` skill rule: next number plus issue suffix, reconciled on merge), `pnpm adr lint` (frontmatter, headings, unique ids, supersession links resolve, `reviewDate` past due warns), `pnpm adr index` writing `docs/.generated/adr-index.json`.
* In-app index `/_app/docs/adr` rendered by `collab/docs-engine`: table (id, title, status, date, deciders, tags) with filters, and a supersessio
SPEC(first 1200): * Numbering collisions from parallel branches resolve by keeping both files and letting `adr lint` require a renumber on the later merge; the index uses `id` from the filename.
* `superseded` requires `supersededBy`; setting it also adds the reverse `supersedes` entry via `adr lint --fix`.
* Index JSON shape: `{ generatedAt, adrs: [{ id, title, status, date, deciders, issue, tags, supersedes, supersededBy, path }] }`; consumed by `libraries/registry` and `collab/knowledge-search`.
* ADRs are registered as `doc` search entities with tag `adr` so one search covers them.
* Review dates: nightly job comments on the issue when `reviewDate` passes and status is still `accepted`.
DOD:
* Fifteen seed ADRs merged, lint clean, index generated.
* Vitest: frontmatter validation, numbering script, supersession fix, index generation, status-diff detection.
* In-app index screenshot at 375, 1024 and 1920 with filters and graph; axe clean.
* Seeded status change on a test ADR produces the Linear comment (link) and the Needs Justin move.
* `docs/adr/README.md`; CHANGELOG entry; Linear comment with index link and screenshots.
EDGE:
* ADR without an issue (pre-existing decision): `issue: none` allowed with a lint warning; no Linear comment.
* Two ADRs supersede the same one: allowed; graph shows a fan-out.
* Frontmatter edited manually with invalid status: lint fails in gate 1 via `docs:lint`.
* Issue key archived or deleted in Linear: comment fails gracefully and is written to `artifacts/pending-comments/`.
* Very long alternatives table: rendered with horizontal scroll at 320 and 375.
* Status flips back from `accepted` to `proposed`: allowed, logged as a reopen with a required `References` link.
DEPS: `collab/docs-engine` (hard for the index page). Uses `agents/skills-library` `write-adr` and `linear-update` scripts (soft; ship the numbering script here if the skill is not merged and the skill imports it). Consumed by `forge/vcs-decision-adr`, `collab/collab-research`, `libraries/registry`, every research issue.


## PAP-131 [P1 Build L prio1 Backlog] Implement in-app comments anchored to any entity, page element or doc block with mentions and resolve
key=collab/comments milestone=Comments and canvas agent=Built by Nova (CRDT Engineer) with Iris on the panel compone
blockedBy=['PAP-59', 'PAP-140'] blocks=['PAP-197', 'PAP-137', 'PAP-136']
GOAL: Let people and agents discuss anything where it lives: comments anchored to an entity, a page element, a doc block, a canvas node or a screenshot, with mentions, resolve state and one-click escalation to a Linear issue. Threads update live for everyone viewing the same anchor.
SCOPE: In:

* Drizzle schema `packages/db/src/schema/comments.ts`: `comment_thread` (`id`, `tenant_id`, `workspace_id`, `anchor_type: entity|element|doc_block|canvas_node|screenshot`, `anchor jsonb` (`{ entityType, entityId }` | `{ route, specKey, selector?, rect? }` | `{ docPath, blockId }` | `{ canvasId, nodeId }` | `{ fileId, frame?, rect }`), `anchor_key text` generated for indexing, `status: open|resolved`, `visibility: internal|shared`, `created_by`, `resolved_by`, `resolved_at`, `linear_issue_id`, `last_activity_at`); `comment` (`id`, `thread_id`, `body_json jsonb` Tiptap document, `body_text`, `author_id`, `author_kind: human|agent`, `mentions uuid[]`, `reactions jsonb`, `edited_at`, `deleted_at`). RLS by tenant; `visibility: internal` hidden from `customer.*` audiences via `identity/rbac-abac` policies `comment.read|create|update|delete|resolve`.
* oRPC `comments.threads.list({ anchorK
SPEC(first 1200): * `anchor_key` format: `entity:<type>:<id>`, `element:<route>:<specKey>`, `doc:<path>#<blockId>`, `canvas:<canvasId>:<nodeId>`, `shot:<fileId>:<frame>`; indexed with `(tenant_id, anchor_key, status)`.
* Deep link `?thread=<id>` opens the panel and scrolls to the anchor; missing anchor shows the thread with an "element moved" note.
* Agents may comment (author_kind `agent`) with visible attribution from `identity/agent-principals`; agents may not resolve customer threads.
* Body limit 10k characters; attachments via `data-layer/file-storage` signed uploads, images inline.
* Keyboard: `c` to comment on focused element when `input/command-registry` is present; composer `Cmd+Enter` to send.
DOD:
* Vitest: anchor key derivation, RLS and visibility tests through `callAs(actor)` for customer, staff and agent, mention parsing.
* Playwright: two contexts, one posts a comment on an element, the other sees it within 1 s; resolve and reopen; create Linear issue (mocked); screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark showing pins and panel (drawer under `lg`).
* axe clean; composer usable with keyboard only.
* `docs/collab/comments.md` including how a page becomes commentable; CHANGELOG entry; Linear comment with screenshots and the created test issue link.
EDGE:
* Anchored element removed by a later deploy: thread remains listed under "Unanchored" for the page; pin hidden.
* Comment on a row inside a virtualised grid: anchor is `entity` (row id), not `element`, so scrolling does not lose it.
* Mention of a user without access to the anchor: mention stored but notification suppressed with a hint to the author.
* Offline: composer queues via `realtime/offline-queue`, shows pending state; conflict impossible (append-only).
* Deleted comment with replies: body replaced by "deleted", thread kept.
* Fifty pins on one page: pins cluster with a count badge above 12 per viewport.
DEPS: `realtime/yjs-server` (presence transport) and `identity/rbac-abac` (hard). `realtime/record-sync` for live updates (fallback: TanStack Query polling every 5 s), `data-layer/file-storage`, `pm-linear/linear-sync`. Unblocks `collab/notifications`, `collab/screenshot-annotations`, `growth/support-inbox`, canvas node comments.


## PAP-132 [P1 Build L prio1 Backlog] Build the canvas view (tldraw or React Flow) showing the UX flow of the whole app, generated from specs and editable
key=collab/canvas-view milestone=Comments and canvas agent=Built by Nova (Canvas Cartographer, CRDT Engineer). Reviewed
blockedBy=['PAP-127', 'PAP-140', 'PAP-114'] blocks=['PAP-157', 'PAP-123', 'PAP-113']
GOAL: Show the whole app as a live map: pages, transitions, entities and external systems generated from specs, laid out automatically, filterable by audience, annotated and rearranged collaboratively in real time, with comments on any node. This is the "canvas view of the UX flow" Justin asked for, and the base other graph views (agent org chart) reuse.
SCOPE: In:

* `packages/collab/canvas/` on `@xyflow/react` 12 (per `collab/collab-research` ADR; if tldraw wins, the node model below still applies) with custom node types `PageNode` (title, route, surface colour from tokens, audience chips, status badge, thumbnail when available, open-spec and open-page actions), `EntityNode`, `ExternalNode` (connector icon), `StartNode`, `GroupNode` (surface and nav-section compounds), `NoteNode` (sticky note, markdown), `RegionNode` (labelled rectangle); edge types `navigate`, `mutation`, `integration`, `reads`, `writes` with distinct styles and labels (`on`, `guard`).
* Loader from `spec-builder/spec-to-canvas` `FlowGraph` (`specs/.generated/flow-graph.json` served by oRPC `canvas.graph.get(appId)` with `specHash`); spec-derived nodes and edges are locked (not deletable, positions overridable).
* Collaborative overlay in a Yjs document `canvas:<appId>` on `
SPEC(first 1200): * Rendering budget: 300 nodes and 600 edges at 60 fps while panning on a 2020 laptop; use `onlyRenderVisibleElements`, memoised nodes, edge simplification below zoom 0.4.
* Merge rule: generated positions apply unless an override exists; "reset layout" clears overrides for selected nodes only.
* Node colours and typography from `design-system/tokens`; dark theme supported; minimum readable label at zoom 0.6.
* Yjs doc persisted by Hocuspocus to Postgres; document name authorised for the tenant's staff via the auth hook.
* Deep link `?node=<id>&audience=<id>` restores filter and focus.
DOD:
* Vitest: loader mapping, override merge, filter logic, stale detection; Playwright: load the example graph, filter by audience, move a node in one context and see it move in another within 1 s, add a note, comment on a node, export PNG; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 render read-only with a "larger screen recommended" notice.
* Performance run with a generated 300-node graph shows 55 fps or more (numbers in comment).
* axe clean for toolbar and node focus order.
* `docs/collab/canvas.md`; CHANGELOG entry; Linear comment with screenshots, video from `quality/video-replays` and the demo link.
* `agents/org-chart-ui` owner confirms the node API is reusable (comment).
EDGE:
* Graph regenerated with a renamed page id: override orphaned; a cleanup action lists orphans.
* Two users drag the same node: Yjs last-writer wins; a brief highlight shows the other cursor.
* Hocuspocus down: canvas loads read-only from the JSON with a banner; notes disabled.
* Thousands of `reads` edges: hidden by default above 500 edges, toggle shows them.
* Node thumbnail 404: placeholder with surface icon.
* Export of a 20k-pixel canvas: export the current viewport or a selected region, capped at 8k pixels.
DEPS: `spec-builder/schema` and `spec-builder/spec-to-canvas` (graph), `realtime/yjs-server` (hard for collaboration), `collab/collab-research` (library). Soft: `collab/comments`, `realtime/presence`, `quality/playwright-matrix` thumbnails. Unblocks `agents/org-chart-ui`, `input/pen`, `collab/screenshot-annotations` shares the overlay code.


## PAP-133 [P1 Build M prio2 Backlog] Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant
key=collab/changelog milestone=Comments and canvas agent=Built by Quill (Changelog Scribe) with Forge on the release 
blockedBy=['PAP-46'] blocks=['PAP-52']
GOAL: Generate changelogs nobody has to write: conventional commits and PR summaries become a repo `CHANGELOG.md`, per-app release notes in the docs engine, and per-tenant, per-audience "What's new" entries in the product, with a Claude pass that rewrites developer language into human language. Staff and customers see what changed the day it ships.
SCOPE: In:

* `packages/collab/changelog/` with `pnpm changelog build [--from <tag>] [--to HEAD]`: parses commits with `conventional-commits-parser` 6 (types, scopes, breaking notes, `Linear:` and `Character:` trailers from `forge/branch-policy`), fetches merged PR bodies through the Forgejo or GitHub API and extracts the `## Summary` and `## Changelog` sections defined in `forge/pr-templates` (`audience: internal|staff|customer`, optional `headline`).
* Classification: scope maps to app and package via `changelog.config.ts` (`scopes: { web: { app: 'paperos-template' }, ui: { package: '@paperos/ui' } }`); type maps to sections Added, Changed, Fixed, Security, Performance, Docs; `feat!` and `BREAKING CHANGE` produce a Breaking section.
* Outputs: `CHANGELOG.md` (Keep a Changelog format, developer audience), `docs/changelog/<version>.mdx` per release rendered by `collab/docs-engine`, and rows in 
SPEC(first 1200): * Deterministic ordering: sections in fixed order, entries by PR merge time; regeneration for a version is idempotent (hash comparison).
* Entries link the PR, the Linear issue and, when the PR touched `specs/pages/*`, the page spec via `SpecRef`.
* Tenant scoping: entries are global unless the PR frontmatter lists `tenants: [slug]` (for tenant-specific work); RLS filters by `tenant_id is null or tenant_id = current`.
* Rewritten copy rules: one sentence headline under 90 characters, body under 60 words, no internal names (character names stripped), present tense.
* Version comes from the tag; unreleased preview uses `next`.
DOD:
* Vitest: parser fixtures (20 commits including breaking, revert and merge), scope mapping, section ordering, idempotent rebuild, rewrite prompt output validation (headline length, forbidden words).
* Running on paperos-template history produces a correct `CHANGELOG.md` for the first tagged release (link).
* What's new popover and page screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; unread badge clears after viewing; public route shows only customer entries (Playwright).
* Docs page per version renders in the docs engine; `docs/collab/changelog.md` explains PR frontmatter; CHANGELOG entry about the changelog.
* Linear comment with generated files and screenshots.
EDGE:
* Commit without a conventional type (merge commit, revert): reverts remove the reverted entry; unknown types go to an Internal section not shown to customers.
* PR body missing the `## Changelog` section: entry defaults to `audience: internal` and the PR gets a bot comment asking for it.
* Squash merge combining ten commits: PR body wins for the summary; individual commits still parsed for scopes.
* Rewrite call fails or exceeds budget: original developer text shown to staff, hidden from customers until reviewed.
* Same feature landed across three PRs: `changelog.group: <key>` frontmatter merges them into one entry.
* Tag on a hotfix branch: entry attached to the patch version and also listed under the next minor's Fixed section.
DEPS: `forge/branch-policy` (hard, trailer and commit format). Soft: `forge/pr-templates` (frontmatter), `forge/release-tags` (trigger, which depends back on this issue for outputs, so agree the CLI name first), `collab/docs-engine`, `quality/review-report`. Consumed by `growth/content-agent`, `collab/notifications`.


## PAP-134 [P1 Build M prio2 Backlog] Surface rules (CLAUDE.md, policies) and skills as browsable, editable objects in-app with version history
key=collab/rules-skills-registry milestone=Comments and canvas agent=Built by Quill (Prompt Logger) with Nova on UI. Reviewed by 
blockedBy=['PAP-105', 'PAP-128'] blocks=[]
GOAL: Make the rules and skills that govern agents visible and governable inside the product: every `CLAUDE.md`, rules file, skill, agent definition and policy appears as a browsable object with owners, version history, usage statistics from the prompt log and a propose-edit flow that opens a PR. Justin can see what agents are told to do without opening the repo.
SCOPE: In:

* Indexer `pnpm rules:index` in `packages/collab/rules/` scanning `.claude/CLAUDE.md`, `.claude/rules/**/*.md`, `.claude/skills/*/SKILL.md` (plus `skills.json` from `agents/skills-library`), `.claude/agents/*.md` (from `agents/roster-v1`), `docs/policies/**/*.md`, producing `docs/.generated/rules-index.json`: `[{ id, kind: rule|skill|agent|policy, path, title, description, version, owners[], allowedCharacters[], wordCount, updatedAt, lastCommit, tags[] }]`; frontmatter validated with the schemas from `agents/character-schema` and `agents/skills-library`.
* oRPC `rules.list`, `rules.get(id)` (content rendered from the repo at the deployed SHA), `rules.history(id)` (commits touching the path via the Forgejo API, `forge/in-app-git` client), `rules.diff(id, fromSha, toSha)`, `rules.usage(id)` (sessions that loaded the skill or agent, from `collab/prompt-log-store` events where `tool_nam
SPEC(first 1200): * Content is read from the git ref the app was built from (embedded via `import.meta.glob` for the template) and refreshed from Forgejo for other repos of the org; source repo is part of the object id (`paperos-template:skill:review-pr`).
* Word count and the 1500-word skill limit from `agents/skills-library` are shown with a warning badge when exceeded.
* Propose edit requires `rules.propose` permission (staff.admin, Atlas, Quill); agents' proposals carry attribution.
* Version is frontmatter `version` when present, else short SHA.
* Index rebuild on every deploy; history and usage fetched on demand with 5-minute cache.
DOD:
* Index covers all objects in paperos-template; Vitest for the indexer and frontmatter validation; a missing frontmatter field fails `docs:lint`.
* Playwright: browse to a skill, view history, open a diff, propose an edit (mocked Forgejo) and see the PR link; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Usage tab shows real sessions from a seeded prompt log.
* axe clean; `docs/collab/rules-registry.md`; CHANGELOG entry; Linear comment with screenshots.
* Justin reviews one rule in-app and comments (via `collab/comments` on the object, anchor `entity:rule_skill:<id>`).
EDGE:
* Skill folder without SKILL.md: listed as invalid with a fix link.
* Same skill name in two repos: distinct ids by repo prefix.
* Forgejo unreachable: content still shown from the build; history tab shows a retry notice.
* Huge CLAUDE.md (20k words): rendered with a TOC; word-limit badge applies only to skills.
* Proposed edit conflicts with a concurrent merge: PR shows conflict; UI links to it, no auto-resolve.
* Prompt log lacks Skill events (older sessions): usage shows "no data before" with the first logged date.
DEPS: `collab/docs-engine` (renderer) and `agents/skills-library` (`skills.json`, frontmatter) (hard). Soft: `agents/roster-v1`, `forge/in-app-git`, `collab/prompt-log-store`, `collab/comments`. Consumed by `agents/character-docs`.


## PAP-135 [P1 Build M prio2 Backlog] Build the prompt log browser: filter by issue or character, replay a session, link to the PR
key=collab/prompt-log-ui milestone=Comments and canvas agent=Built by Nova (Views Engineer) with Quill (Prompt Logger) de
blockedBy=['PAP-165', 'PAP-129'] blocks=[]
GOAL: Let Justin audit any agent decision in minutes: a browser over the prompt-log store that filters sessions by issue, character, status and cost, replays a session turn by turn with tool calls expanded, and jumps to the PR, Linear issue and worktree. It also feeds evals by letting a reviewer flag a session as a golden or a failure.
SCOPE: In:

* Route `/_app/dev/prompt-log` (platform tenant, `staff.admin` and agent principals read) with a sessions grid built on `tables/grid-view` using a view model from `tables/view-model-spec`: columns character, sub-agent, issue (link), status, model, duration, input and output tokens, cache tokens, cost, PR (link), started; default sort started desc; filters and grouping by character or issue; saved views ("Today", "Failed", "Over $5").
* Session detail `/_app/dev/prompt-log/$sessionId`: header with metadata, cost and token gauges, links (PR, Linear issue via `pm-linear/linear-sync` or direct URL, branch, worktree path, parent session); timeline of events virtualised with `@tanstack/react-virtual` 3, colour by role, tool calls collapsible with input and output (JSON pretty-printed, large outputs loaded from blob on demand), redaction markers shown inline as `[REDACTED:kind]`, `PreCompa
SPEC(first 1200): * Data via oRPC `promptLog.*` with cursor pagination; grid pages of 100; detail loads events in 500-event chunks by `seq` with prefetch of the next chunk.
* Search within a session: client-side over loaded chunks plus server `events.list({ q })` using `ILIKE` on `content` for the rest.
* Permalinks resolve `seq` and scroll the virtual list to it.
* Responsive: grid becomes a card list under `md`; detail timeline is single-column at every width; gauges stack at 320 and 375.
* All timestamps in the viewer's timezone with UTC on hover.
DOD:
* Playwright with a seeded store of 50 sessions: filter by character, open a session, expand a tool call, replay with keyboard, flag as golden (mocked eval endpoint), open permalink; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; video of a replay from `quality/video-replays`.
* Vitest: chunk loading, permalink resolution, gauge math, nesting of sub-agent sessions.
* 10k-event session scrolls at 60 fps (measurement in comment).
* axe clean; `docs/collab/prompt-log-ui.md`; CHANGELOG entry; Linear comment with screenshots and video.
* Justin replays one real session and confirms the PR link and cost match Linear's metering comment.
EDGE:
* Session still running: header shows live status, timeline tails new events via polling every 5 s (or Electric shape when available).
* Session with gaps (`gaps jsonb`): gap rows rendered with a warning and the missing seq range.
* Redacted content that hides the whole message: show a "fully redacted" row with the kind counts.
* Tool output blob missing (retention): "content expired" placeholder with the size.
* Killed session: red status, final synthetic `session.killed` event with the reason.
* Grid view engine not merged: fall back to a plain TanStack Table with the same columns; documented TODO.
DEPS: `collab/prompt-log-store` (hard), `tables/grid-view` (hard, with fallback). Soft: `agents/eval-harness`, `tables/view-model-spec`, `tables/map-chart-views`, `pm-linear/linear-sync`, `realtime/record-sync`. Consumed by `collab/rules-skills-registry` (usage links), `pm-linear/credit-metering` (deep links).


## PAP-136 [P2 Build L prio2 Backlog] Build a notification center (in-app, email, Slack) with per-audience preferences
key=collab/notifications milestone=Knowledge surfaced everywhere agent=Built by Nova with Forge (Ops Runner) on the worker and prov
blockedBy=['PAP-43', 'PAP-131'] blocks=[]
GOAL: Deliver mentions, replies, resolutions, review results and release news to people where they are: an in-app inbox with a live badge, email through Resend and Slack messages, governed by per-user and per-audience preferences with digests and quiet hours. Justin's Needs Justin queue and comment mentions both flow through this one system.
SCOPE: In:

* Drizzle schema `packages/db/src/schema/notifications.ts`: `notification` (`id uuidv7`, `tenant_id`, `user_id`, `kind`, `title`, `body_md`, `link`, `source jsonb { type, id }`, `actor_id`, `actor_kind`, `seen_at`, `read_at`, `archived_at`, `created_at`); `notification_preference` (`user_id`, `tenant_id`, `kind`, `channels jsonb { inApp, email, slack }`, `digest: none|hourly|daily`, `quiet_hours jsonb { start, end, tz }`); `notification_delivery` (`notification_id`, `channel`, `status: queued|sent|failed|suppressed`, `attempts`, `provider_id`, `error`, `sent_at`); `tenant_slack_config` (`tenant_id`, `webhook_url` encrypted, `default_channel`).
* Kinds registry `packages/collab/notifications/kinds.ts`: `comment.mentioned`, `comment.replied`, `thread.resolved`, `issue.needs_justin`, `review.gate_failed`, `review.ready`, `release.candidate`, `changelog.published`, `agent.blocked`, `imp
SPEC(first 1200): * Recipient expansion for `audience` uses `identity/audience-model` segments; capped at 500 recipients per event, above that a digest-only mode.
* Suppression rules: actor never notified of own action; mention of a user without access to the source is suppressed with `status: suppressed`; unsubscribed kind is suppressed, not failed.
* Idempotency key `(kind, source, recipient, bucket)` prevents duplicates on retries.
* Email templates render with tokens from `design-system/tokens` inlined; plain-text alternative generated.
* Latency target: in-app under 2 s from emit; email under 60 s outside digests.
DOD:
* Vitest: preference resolution, quiet hours across timezones, collapse and digest grouping, idempotency, template rendering snapshots (email HTML and Slack JSON).
* Integration: a comment mention produces an in-app notification in a second browser context within 2 s, an email captured by a Resend test key (or Mailpit in CI) and a Slack message to a test webhook (link or screenshot).
* Playwright: inbox and preferences at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; unsubscribe link works.
* axe clean; `docs/collab/notifications.md` including how to add a kind; CHANGELOG entry; Linear comment with screenshots and delivery logs.
* `issue.needs_justin` delivers to Justin's configured channels with the batching rule from `pm-linear/justin-queue`.
EDGE:
* User in two tenants with different preferences: preferences are per tenant; global fallback row when unset.
* Resend rate limit or outage: deliveries stay queued up to 24 h, then fail with alert to Ops (`data-layer/observability`).
* Quiet hours spanning midnight and DST changes: computed with `@date-fns/tz`; test cases included.
* Slack webhook revoked: delivery fails; tenant admin sees a banner in settings.
* Digest with 300 items: truncated to 50 with a link to the inbox.
* Deleted source (thread removed): notification stays with "no longer available" on click.
DEPS: `collab/comments` (hard, first producer). `data-layer/api-layer`, `realtime/record-sync` (fallback polling), `identity/audience-model`, `app-shell/env-config` for provider keys. Consumed by `pm-linear/justin-queue`, `quality/release-train`, `collab/changelog`, `migration/import-framework`.


## PAP-137 [P2 Build M prio3 Backlog] Allow annotating screenshots and video frames with comments that create Linear issues
key=collab/screenshot-annotations milestone=Knowledge surfaced everywhere agent=Built by Nova (Canvas Cartographer) with Sentinel (Visual In
blockedBy=['PAP-83', 'PAP-131'] blocks=[]
GOAL: Close the loop from picture to ticket: a viewer for the Playwright screenshots and video replays of every PR run where anyone can draw a box or pin on an image or a paused video frame, comment, see the vision agent's findings overlaid, and create a Linear issue with the cropped evidence in one click. Visual bugs stop needing a written reproduction.
SCOPE: In:

* Route `/_app/dev/qa/$runId` (staff, developer) reading the run manifest published by `quality/playwright-matrix` and `quality/video-replays` (`reports/gate3.json` uploaded to MinIO via `data-layer/file-storage` with entries `{ page, width, theme, kind: screenshot|video|contactSheet, fileId, flowId?, durationMs? }`), grouped by page with a width by theme matrix; a runs list `/_app/dev/qa` by PR and date from `pm-linear/webhooks` records.
* Viewer in `packages/collab/annotations/`: image viewer with zoom and pan, video player (`<video>` with frame stepping via `requestVideoFrameCallback`, time code display, flow step captions from the contact sheet data), annotation layer reusing the overlay code from `collab/canvas-view` (`RegionNode`-like rectangles and pins) drawn with pointer events (mouse, touch; pen refinements come from `input/pen`), keyboard alternative (arrow keys to positi
SPEC(first 1200): * Image coordinates stored as percentages so annotations survive resizing; render uses the natural size for crops.
* Video frame anchor uses milliseconds; the viewer seeks and pauses on open; contact sheet thumbnails link to the nearest step.
* Manifest access requires `qa.view` (staff.\*); issue creation requires `qa.report`.
* Deep link `?file=<id>&t=<ms>&thread=<id>`.
* Loading budget: first image visible under 1 s on a 1920 grid; thumbnails via MinIO image variants (`data-layer/file-storage`).
DOD:
* Playwright with a seeded run manifest: open run, draw a rectangle on a screenshot, comment, create a Linear issue (mocked) and verify the crop uploaded; pause a video, pin at a frame, permalink reopens at the frame; screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 support viewing and pinning, not compare mode.
* Vitest: percent coordinate math, crop generation, title and description builders, vision finding mapping.
* Keyboard-only annotation recorded as a video flow; axe clean.
* `docs/collab/qa-viewer.md`; CHANGELOG entry; Linear comment with screenshots, the test issue created and the video.
* Sentinel's Visual Inspector posts one real finding that a human confirms through the viewer.
EDGE:
* Run manifest partially uploaded (shard still running): viewer shows available items and a live "3 of 4 shards" indicator.
* Screenshot regenerated for the same PR (new commit): old annotations stay attached to the old file id and are listed under "previous run".
* Video codec unsupported in Safari or WebKitGTK: fall back to the contact sheet with a notice.
* Very tall full-page screenshot (12k px): tiled rendering, zoom limited to keep memory under 300 MB.
* Rect smaller than 8 px: converted to a pin.
* Linear project inference fails (page without spec): issue lands in the default project with a note.
DEPS: `collab/comments` (hard) and `quality/video-replays` (hard, manifest and MP4s). `quality/playwright-matrix`, `quality/screenshot-annotation` (finding JSON), `data-layer/file-storage`, `pm-linear/webhooks`, `collab/canvas-view` overlay code (soft, can be copied). Consumed by `quality/review-report` (links to the viewer).


## PAP-138 [P2 Build M prio2 Backlog] Unify search across docs, comments, specs, prompt logs and issues
key=collab/knowledge-search milestone=Knowledge surfaced everywhere agent=Built by Nova (Views Engineer) with Forge (Schema Wright) on
blockedBy=['PAP-128', 'PAP-39'] blocks=[]
GOAL: One search box over everything the organisation knows: docs, ADRs, page specs, comments, prompt sessions, rules and skills, and Linear-mirrored issues, with hybrid keyword and vector ranking, facets by kind, audience-safe results and actions on each hit. Reachable from the command palette on every page.
SCOPE: In:

* Registrations through `data-layer/search` `registerSearchable(...)` in `packages/collab/search/registrations.ts`: `doc` (title, body from MDX text, facets `audience`, `tags`, `owner`; route `/_app/docs/<slug>`), `adr` (from `collab/decision-log` index; facets `status`, `tags`), `page_spec` (title, purpose, route, edge-case text; facets `surface`, `status`, `owner`; route to `spec-builder/spec-editor-ui`), `comment` (body_text with thread anchor label; facets `status`, `anchorType`; route deep link with `?thread=`), `prompt_session` (issue key, character, summary; facets `character`, `status`; route to `collab/prompt-log-ui`), `rule_skill` (from `collab/rules-skills-registry`), `issue` (from `pm-linear/pm-data-model` mirror; facets `state`, `project`, `labels`; route to the issue page and Linear URL).
* Indexers: build-time script `pnpm search:index-static` for docs, ADRs, specs an
SPEC(first 1200): * Snippets from `ts_headline` with 160-character windows; vector results fall back to the first matching sentence.
* Ranking: registry hybrid score plus recency boost for comments and issues (half-life 30 days) and a kind weight (`doc` 1.0, `page_spec` 0.9, `issue` 0.9, `comment` 0.7, `prompt_session` 0.6).
* Queries under 2 characters return recents; operators `kind:doc`, `owner:Quill`, `is:open` parsed client-side into facets.
* Latency: p95 under 300 ms for hybrid on 100k documents; palette shows results after 150 ms debounce.
* Audit: searches are not logged with text, only counts per kind (privacy).
DOD:
* Vitest: registrations validate at boot, operator parsing, kind allowlist per audience, ranking weights.
* Seeded corpus (500 docs, 50 specs, 2k comments, 300 sessions, 1k issues): Playwright searches from the palette and the page, filters by facet, opens a result of each kind; customer actor sees only allowed kinds; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Benchmark committed showing p95 under 300 ms.
* axe clean for palette and results; `docs/collab/search.md` including how to register a new kind; CHANGELOG entry; Linear comment with screenshots and benchmark.
* Justin finds a prompt session by issue key from the palette (video).
EDGE:
* Same document indexed twice after a rename: static indexer deletes by vanished path before upsert.
* Comment visibility `internal` and a customer search: RLS excludes it even if the kind were allowed.
* Prompt summary generation fails: session indexed with issue key and character only.
* Very long query (2k characters): truncated to 500 with a notice.
* Vector model changed: registry marks rows stale; health page shows the count; keyword still works.
* Command registry not merged: a temporary global `Cmd/Ctrl+K` handler is installed with a TODO.
DEPS: `data-layer/search` and `collab/docs-engine` (hard). Soft: `collab/decision-log`, `collab/comments`, `collab/prompt-log-store`, `collab/rules-skills-registry`, `pm-linear/pm-data-model`, `input/command-registry`. Consumed by `agents/memory` (characters query it at session start).
