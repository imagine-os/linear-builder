# Round 4 digest: In-App Collaboration & Knowledge (`collab`)

Features: 82 (55 covered, 7 partial, 20 gap). New issues: 14 (1 children, 13 gaps, 4 deferred to v0.2). Amendments: 8. Cross-project suggestions: 5.

Benchmarks: Figma comments and FigJam; Notion docs, comments and suggestions; Linear inbox, subscribers and notifications; Slack notifications; tldraw and Excalidraw; Miro; Google Docs suggesting mode; Loom; Beamer and Headway changelogs; LangSmith prompt traces; Mintlify and Docusaurus (llms.txt, .md mirrors); Intercom articles and Pendo tours; GitHub notifications and CODEOWNERS.

## What was missing and why it matters

1. PAP-136 listed four work packages but only three children existed: the notification core (kinds registry, worker, in-app and email channels) had no issue, although PAP-94, PAP-88 and PAP-89 deliver Justin's decisions and gate results through it. It is now a P0-priority Opus child blocked only by jobs and the event bus.
2. The brief asks for every prompt and response to be logged 'in the documentation system'; the store (PAP-129) and browser (PAP-135) exist but nothing writes a docs page. Build journals turn each finished session into a generated MDX page with decisions, files, cost and replay links.
3. Cold Claude sessions cannot read the docs engine: llms.txt, raw Markdown routes, a `pnpm docs` CLI and a docs MCP tool make the knowledge base readable without a browser and give PAP-109 memory a source.
4. Mentions notify people; nothing lets anyone follow a record, thread or doc, so `comment.replied` and `record.updated` have no recipients. A Linear-style watcher model and a staff triage view for unanswered customer comments close the loop.
5. Six collab DoDs assume seeded data (50 sessions, 2k comments, 50 pins) nobody generates; one Haiku fixtures issue registers deterministic sets with `/__test/seed`. Anchor grammar collision between repo docs and runtime docs (`doc:` vs `tdoc:`) and the `help.*` keys PAP-114 would reject are fixed by amendments.

## New issues

| Key | Title | Parent | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/collab/notification-core` | Notification core: kinds registry, event-bus subscriber worker, preference resolution, in-app and email channels | PAP-136 | M (3) | Opus 5 / high | 1 | Comments and canvas |  |
| `r4/collab/watchers-subscriptions` | Follow model: watch records, threads and docs with auto-follow rules and watcher fan-out for replies and record changes | - | S (2) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/agent-readable-docs` | Agent-readable docs: `llms.txt`, raw Markdown endpoint per page, `pnpm docs search|get` CLI and a docs MCP tool | - | S (2) | Sonnet 5 / medium | 2 | Knowledge surfaced everywhere |  |
| `r4/collab/build-journals` | Build journals: generate a docs page per issue from the prompt log with summary, decisions, files touched, cost and replay links | - | M (3) | Sonnet 5 / medium | 2 | Knowledge surfaced everywhere |  |
| `r4/collab/collab-demo-seeds` | Collab demo seeds: deterministic fixtures for comments, notifications, prompt sessions, docs and changelog registered with `/__test/seed` | - | S (2) | Haiku 4.5 / low | 2 | Comments and canvas |  |
| `r4/collab/announcements-banners` | In-app announcements and maintenance banners: staff-authored, audience-targeted, scheduled, dismissible, flag-aware | - | S (2) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/canvas-diff-embeds` | Canvas diff mode and embeds: highlight graph changes between two spec hashes, `<FlowGraphEmbed>` for docs and record pages, thumbnail job | - | M (3) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/docs-reference-hub` | Reference hub in the docs engine: one sidebar section for OpenAPI, the data dictionary, module contracts, the component registry and ADRs | - | S (2) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/docs-authoring-kit` | Docs authoring kit and freshness: `pnpm docs new <template>`, Diátaxis templates, owner and review-date lint, stale-page job, was-this-helpful widget | - | S (2) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/customer-comment-triage` | Staff comment triage: unanswered customer threads as a saved view with assignment, age and SLA badges | - | S (2) | Sonnet 5 / medium | 3 | Knowledge surfaced everywhere |  |
| `r4/collab/ask-paperos` | Ask PaperOS: retrieval-augmented answers over docs, ADRs, specs and journals with citations, from the command palette | - | M (3) | Sonnet 5 / medium | 4 | Knowledge surfaced everywhere | yes |
| `r4/collab/comment-email-replies` | Reply to comment and mention emails by email: per-thread reply address, inbound parsing, attribution and loop guards | - | S (2) | Sonnet 5 / medium | 4 | Knowledge surfaced everywhere | yes |
| `r4/collab/docs-suggestion-mode` | Suggestion mode and publish review for runtime docs: tracked changes, accept or reject per change, approval before publish | - | M (3) | Sonnet 5 / medium | 4 | Knowledge surfaced everywhere | yes |
| `r4/collab/docs-i18n` | Docs localisation: `docs/<locale>/` folders with fallback to the default locale, language switcher, translation status page and a translation skill hook | - | M (3) | Sonnet 5 / medium | 4 | Knowledge surfaced everywhere | yes |

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Comments anchored to entity, element, doc block, canvas node, screenshot | covered | PAP-317, PAP-318, PAP-319 | Figma/Notion parity; five anchor kinds. |
| Mentions of users, agents and entities | covered | PAP-317, PAP-318 |  |
| Resolve, reopen, reactions, edit and soft delete | covered | PAP-317 |  |
| Live thread updates and typing indicator | covered | PAP-319 | Electric shape with polling fallback. |
| Deep links to threads | covered | PAP-319 |  |
| Escalate a thread to a Linear issue | covered | PAP-319 |  |
| Attachments in comments | covered | PAP-318 | Through PAP-37 signed uploads. |
| Internal vs customer-visible threads | covered | PAP-317 |  |
| Agent comments with visible attribution | covered | PAP-317 | author_kind plus PAP-60 badge. |
| Follow or watch a record, thread or doc (Linear subscribers) | gap | r4/collab/watchers-subscriptions | comment.replied has no recipients without watchers. |
| Staff triage of unanswered customer comments with assignment and SLA | gap | r4/collab/customer-comment-triage | Intercom-style queue on the views engine. |
| Reply to comment emails by email | gap | r4/collab/comment-email-replies | Deferred v0.2. |
| Suggestion mode / tracked changes on shared docs (Google Docs) | gap | r4/collab/docs-suggestion-mode | Deferred v0.2. |
| Activity timeline per record | covered | PAP-333 | Owned by tables. |
| Comments on PR diffs inside PaperOS | partial | PAP-278 | Forge PR pages are read-only and deferred-risk; PAP-131 anchors not wired to diffs. |
| Comment export in the tenant archive | covered | PAP-420 | Owned by migration. |
| Orphaned and unanchored thread handling | covered | PAP-317, PAP-318 |  |
| UX-flow canvas generated from specs | covered | PAP-320, PAP-123 | React Flow per PAP-127. |
| Collaborative notes, regions, position overrides, undo | covered | PAP-321 |  |
| Filters, search, minimap, deep links, PNG/SVG export | covered | PAP-322 |  |
| Comments on canvas nodes | covered | PAP-322, PAP-317 |  |
| Presence cursors on the canvas | covered | PAP-321, PAP-141 |  |
| Auto layout (ELK) and stale detection | covered | PAP-123, PAP-322 |  |
| Diff mode: what a PR changed in the flow | gap | r4/collab/canvas-diff-embeds | diffGraphs exists in PAP-123; no rendering. |
| Embed a subgraph in docs and record pages; node thumbnails | gap | r4/collab/canvas-diff-embeds |  |
| Entity relation edges (ERD) on the canvas | partial | PAP-123 | Only reads/writes edges; amendment to PAP-123 proposed. |
| Freehand drawing, pen | covered | PAP-157 | Deferred in input. |
| Freeform whiteboard (FigJam/Miro templates) | gap | - | Out of scope by design; canvas is spec-derived. Not issued. |
| Agent org chart on the canvas | covered | PAP-113 | Owned by agents. |
| Repo MDX docs rendered in-app with sidebar, TOC, history | covered | PAP-128 |  |
| Tenant-authored runtime docs (Notion-style) | covered | PAP-379 |  |
| Audience-filtered public docs | covered | PAP-128 |  |
| Docs search and unified search | covered | PAP-138, PAP-39 |  |
| Block-level comments on docs | covered | PAP-128, PAP-317 | Anchor grammar collision between repo and runtime docs; amendments to PAP-379 and PAP-474. |
| Contextual help panel, product tour, shortcut overlay | covered | PAP-380 | Needs spec schema keys; see spec-builder v1.1 issue. |
| Agent-readable docs: llms.txt, raw Markdown, CLI, MCP tool | gap | r4/collab/agent-readable-docs | Mintlify/Docusaurus parity for cold sessions. |
| Reference hub aggregating OpenAPI, data dictionary, contracts, components, ADRs | gap | r4/collab/docs-reference-hub | Sources exist in five projects; no single entry. |
| Doc templates, owner and review-date lint, stale-page nudges | gap | r4/collab/docs-authoring-kit |  |
| Was-this-helpful feedback and docs health | gap | r4/collab/docs-authoring-kit |  |
| Q&A over the knowledge base with citations | gap | r4/collab/ask-paperos | Deferred v0.2. |
| Docs localisation | gap | r4/collab/docs-i18n | Deferred v0.2. |
| Docs lint (links, frontmatter, includes) | covered | PAP-128 |  |
| Mermaid and live refs (IssueRef, SpecRef, FileRef) | covered | PAP-128 |  |
| Print or PDF export of docs | gap | - | Browser print stylesheet from PAP-235 (deferred) suffices; not issued. |
| Public docs SEO (sitemap, meta) | partial | PAP-128 | Handled by spec-builder public metadata issue for spec pages; docs sitemap not issued. |
| Docs available offline in Tauri | covered | PAP-128 | import.meta.glob bundles docs. |
| Version history for runtime docs with restore | covered | PAP-379 |  |
| Notion import into docs | covered | PAP-203, PAP-418 | Deferred in migration. |
| Changelog from conventional commits and PR summaries | covered | PAP-133 |  |
| What's new popover with unread badge; public changelog | covered | PAP-133 |  |
| Per-tenant, per-audience changelog entries | partial | PAP-133 | Not filtered by enabled modules; amendment. |
| Changelog notification and email | covered | PAP-133, r4/collab/notification-core |  |
| In-app announcements and maintenance banners (Beamer/Headway) | gap | r4/collab/announcements-banners |  |
| Public roadmap page | gap | - | Not issued; v0.2 candidate. |
| Content agent drafting posts from changelog | covered | PAP-192 | Growth, deferred. |
| Prompt/response/tool-call store with redaction and cost | covered | PAP-129, PAP-107 |  |
| Session browser, replay, permalinks, golden flags | covered | PAP-135 |  |
| Per-issue build journals in the docs engine | gap | r4/collab/build-journals | The brief's "logged properly in the documentation system". |
| Prompt log search and session summaries | covered | PAP-138 |  |
| Cost metering and daily burn report | covered | PAP-98, PAP-129 | pm-linear. |
| Session observability (heartbeats, OTel) | covered | PAP-288 | agents. |
| Compare two sessions side by side (LangSmith) | gap | - | Not issued; PAP-110 evals cover regressions. |
| Live tail of running sessions | covered | PAP-135 |  |
| Retention and export of prompt events | covered | PAP-129 | 180-day MinIO archive. |
| Rules, skills and agent definitions browsable with history and propose-edit | covered | PAP-134 |  |
| Skill usage analytics from the prompt log | covered | PAP-134 |  |
| Character memory pages | covered | PAP-109 | agents; reads journals. |
| Notification kinds registry, worker, in-app and email channels | gap | r4/collab/notification-core | PAP-136 WP1 had no child; critical path for PAP-94, PAP-88, PAP-89. |
| Inbox, bell badge, preferences matrix | covered | PAP-323 | Snooze proposed as amendment. |
| Digests, quiet hours, burst collapse | covered | PAP-324 |  |
| Slack channel | covered | PAP-325 |  |
| Web and mobile push | covered | PAP-381 | realtime. |
| Tenant outbound webhooks as a channel | partial | PAP-222 | identity issue is deferred; no channel adapter. Not issued. |
| Branded email templates | partial | PAP-235, PAP-370 | PAP-235 deferred; core ships a plain fallback (amendment). |
| Unsubscribe and suppression | covered | r4/collab/notification-core |  |
| Unified search with facets and audience isolation | covered | PAP-138 |  |
| Screenshot and video annotation to Linear issues | covered | PAP-137 | Deferred. |
| Async video walkthroughs (Loom) | partial | PAP-83 | Only CI-recorded flows; user recordings not issued (v0.2). |
| Contract package, conformance suite, kernel wiring | covered | PAP-474, PAP-477, PAP-480 |  |
| Deterministic demo seeds for every collab surface | gap | r4/collab/collab-demo-seeds | Six DoDs assume seeds nobody owns. |
| Library decision for canvas and editor | covered | PAP-127 | Ready for Claude. |
| Decision log with supersession graph | covered | PAP-130 |  |

## Amendments to existing specs

- **PAP-136** (Spec): Work package 1 is the child issue `r4/collab/notification-core` (Opus 5 / high, blocked by PAP-43 and PAP-303 only). Because PAP-235 is Deferred, the `EmailChannel` ships a plain-HTML fallback template and switches to the PAP-235 kit when it lands. The `notification` row stores `ActorRef` (PAP-302) for the actor and `EntityRef` for the source, per Contracts §2.
- **PAP-133** (Spec): Per-tenant "What's new" filters entries by the tenant's enabled modules (PAP-266 `tenant_module`): an entry whose PR touched only `packages/<module>` files of a disabled module is hidden for that tenant. The Claude rewrite is capped at 40 entries per build and $2 per version; beyond the cap, remaining entries stay `needs_review` with the original text.
- **PAP-323** (Spec): Rows support snooze (`snoozed_until`, presets 1 h, tomorrow 09:00, next Monday) and "mark all read" for the current filter; a snoozed row returns to unread at the time and is exempt from PAP-324 quiet hours. Add an "unfollow source" action once `r4/collab/watchers-subscriptions` lands.
- **PAP-379** (Spec): Anchor grammar: runtime doc blocks use `tdoc:<pageId>#<blockId>`, not `doc:<path>#<blockId>`, so repo MDX and tenant pages cannot collide on a path-like id; `CommentAnchor` in `@paperos/contract-collab` (PAP-474) gains the `tdoc:` form as a patch bump. `doc_page.slug` may not start with `t/` (reserved by the route).
- **PAP-474** (Spec): `CommentAnchor` grammar includes six forms: `entity:`, `element:`, `doc:` (repo MDX path), `tdoc:` (runtime `doc_page` id, PAP-379), `canvas:`, `shot:`. Fixtures: three per form. `NotificationPort` exports `defineKind`, `notify`, `resolvePreferences` and the `Channel` interface as specified by `r4/collab/notification-core`.
- **PAP-380** (Dependencies): The spec fields `help.docs[]` and `help.tour[]` are not in PAP-114 v1, whose unknown-key rule rejects them. Until `r4/spec-builder/schema-v1-1-extensions` lands, write them as `x-help: { docs, tour }` (passes through untouched) and read both spellings; the validator rule for doc paths registers against `x-help` first.
- **PAP-134** (Definition of done): "Justin reviews one rule in-app" is evidence, not a gate: if no review has happened by RC2 (09-28), attach a Quill review comment on a real rule instead and do not hold the issue in In Review for it.
- **PAP-129** (Spec): `prompt_session` gains `journal_path text` (written by `r4/collab/build-journals`) and `summary_source: search|journal|manual`. Blob contents uploaded through `content_file_id` pass the second-pass redactor before upload, never after. `promptLog.sessions.list` accepts `filter: FilterTree` (PAP-279) so PAP-135's saved views compile server-side.

## Cross-project suggestions

- **spec-builder**: Reserve `help`, `comments`, `flags`, `modules`, `seo`, `budgets` keys in page.spec.yaml v1.1. PAP-380 (help panel) and PAP-361 (comments anchor per detail page) write keys PAP-114 rejects; filed as r4/spec-builder/schema-v1-1-extensions.
- **growth**: Expose PAP-410 inbound email parsing (quote stripping, HTML sanitising) as a shared helper in `packages/email`. r4/collab/comment-email-replies and PAP-197 both parse inbound replies; one parser avoids two threading heuristics.
- **realtime**: PAP-142 editor: block ids on every node for `tdoc:` comment anchors and suggestion marks. PAP-379 anchors comments to Tiptap block ids and the deferred suggestion mode needs stable node ids; PAP-142 should emit `data-block-id` via a UniqueID extension.
- **design-system**: Ship a plain-HTML email base template before PAP-235. PAP-235 is deferred but the notification core and auth emails need a branded-enough base; a 100-line fallback in packages/email unblocks three projects.
- **agents**: PAP-109 memory loader reads build journals and docs via the docs MCP tool. r4/collab/build-journals and r4/collab/agent-readable-docs give memory a source; PAP-109 should consume them instead of a separate notes store.
