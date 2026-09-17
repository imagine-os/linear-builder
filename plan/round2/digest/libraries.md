# libraries — Library Discovery & Integration
PHASE P0 prio 2 dependsOn []
SUMMARY: A governed borrow-before-build process: evaluation rubric, landscape surveys, OSS product evaluation, a registry with ADRs, license policy in CI, MCP connector catalog and a Scout routine.
DESC: Goal: the platform is assembled from the best existing libraries and products, chosen deliberately and recorded. A rubric (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness) and ADR template govern every adoption. Landscape surveys cover UI kits, data/canvas/editor/chart libraries and backend building blocks; whole OSS products (Twenty, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz) are evaluated for embedding or forking. A registry in the docs system tracks adopted, trialing and rejected libraries; a license policy is enforced in CI; MCP servers and connectors are cataloged for agents; Renovate keeps dependencies fresh; a weekly Scout routine scans for new options. Non-goal: adopting anything without an ADR.
MILESTONES: ['Evaluation process 2026-09-19: Rubric, license policy, MCP catalog', 'Core adoptions decided 2026-09-24: UI, data and backend landscape ADRs, OSS product evaluation', 'Registry live 2026-09-30: Registry, Renovate, Scout routine']


## PAP-209 [P0 Spec S prio1 Ready for Claude] Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template
key=libraries/eval-rubric milestone=Evaluation process agent=Written by Scout (Library Evaluator). Reviewed by Atlas (wei
blockedBy=[] blocks=['PAP-216', 'PAP-215', 'PAP-214', 'PAP-213', 'PAP-212', 'PAP-211']
GOAL: Define the single rubric and ADR table format every "should we adopt X" question in PaperOS is answered with, so that twenty parallel sessions score libraries the same way and Atlas can compare ADRs written by different characters. Six research issues already cite this rubric (`data-layer/sync-research`, `identity/auth-research`, `collab/collab-research`, `realtime/realtime-research`, `growth/growth-research`, `business-core/payroll-research`); this issue makes it real and machine-checkable.
SCOPE: In:

* `docs/libraries/rubric.md`: six core criteria (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness), 0-4 scale with written anchors per score, default weights, hard-fail gates, and the rule for adding domain-specific extra criteria.
* Machine-readable rubric `packages/spec/libraries/rubric.yaml` with Zod 4 schema `packages/spec/src/libraries/rubric.ts` (`RubricSchema`, `ScorecardSchema`).
* Scorecard template `docs/libraries/scorecard.template.yaml` and CLI `pnpm lib score <scorecard.yaml>` that validates, computes weighted totals and renders the Alternatives Markdown table ADRs paste in.
* Facts collector `scripts/lib-facts.ts` (npm downloads, last publish, GitHub stars/last commit/open-issue median age, `license` field, `types` field, gzipped size of the imported entry points via a local esbuild `--metafile` run) writing `facts.json` so score
SPEC(first 1200): * Default weights (sum 100): license 20, maintenance 20, bundle size 15, accessibility 15, TypeScript quality 15, agent-friendliness 15. A criterion marked `n/a` (a11y for a server library, bundle size for a Docker image) is dropped and remaining weights rescale proportionally; the scorecard records the rescaled weights.
* Anchors, examples: maintenance 4 = release in the last 90 days, 3+ active maintainers or company backing, median issue first-response under 14 days; 0 = archived or no release in 18 months. Bundle size 4 = under 10 KB gzipped for the imports used, 0 = over 250 KB. Agent-friendliness 4 = plain-Markdown docs or `llms.txt`, TypeScript examples, stable API with typed errors, small surface, widely known so Claude writes it correctly without docs.
* Hard gates (any failure = verdict `reject` regardless of score): license outside `libraries/license-policy` allow tier with no approved waiver; no types for a runtime JS library; UI library that does not run in Tauri WebViews (WebView2, WKWebView, webkit2gtk); requires a vendor cloud with no self-host path.
* Scorecard YAML: `{ candidate, version, evaluatedBy, date, issue, facts, scores: { <criterionId>: { score, evidence }
DOD:
* Rubric doc, `rubric.yaml`, Zod schemas, scorecard template and `pnpm lib score` merged in paperos-template.
* Vitest: schema validation, weight rescaling on `n/a`, gate logic, evidence rule, Markdown table rendering snapshot.
* Worked example committed and rendered table matches the snapshot.
* `docs/adr/template.md` contains Alternatives table and Re-open criteria sections consistent with `collab/decision-log` frontmatter.
* Atlas approves weights and gates; Iris confirms the a11y anchors; Sentinel Code Reviewer passes the CLI.
* CHANGELOG entry; Linear comment linking rubric and example; one comment on each of the six research issues pointing at the final paths.
EDGE:
* Monorepo library with many entry points: score only the packages imported and list them in `facts`.
* Non-npm candidate (Rust crate, Docker image, SaaS API): collector pulls [crates.io](<http://crates.io>) or Docker Hub facts; size `n/a`.
* Dual-licensed or open-core (tldraw watermark, AG Grid Enterprise): score the free tier only and list excluded paid features.
* Single-maintainer project: maintenance capped at 2 unless foundation or company backed.
* Whole product rather than library: rubric applies with the extras defined in `libraries/oss-products`.
* GitHub API rate limited in CI: cached facts older than 7 days produce a warning, not a failure.
DEPS: None; ready now. Consumed by every research issue, `libraries/license-policy`, `libraries/registry`, `libraries/scout-agent`. Soft: `collab/decision-log` (adopts the template sections if it merges later).


## PAP-210 [P0 Infra M prio1 Ready for Claude] Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents
key=libraries/mcp-servers milestone=Evaluation process agent=Built by Scout (Library Evaluator) with Atlas supplying Line
blockedBy=[] blocks=['PAP-121']
GOAL: Produce the catalog of every MCP server and connector agents can reach (Linear, GitHub, Forgejo, Stripe, Notion, Google Drive, Webflow, Miro, Gamma, Playwright, Postgres), with each tool's scope class, auth, rate limits and permitted characters, and commit working `.mcp.json` configs so a fresh Claude Code session in paperos-template has integrations on first boot. This is the catalog `agents/character-schema` validates `mcpServers[]` against and `spec-builder/integrations-section` cross-checks its connector files with.
SCOPE: In:

* Source `.claude/mcp-catalog.yaml`, Zod 4 schema `packages/agents/src/mcp-catalog.ts`, generated `.claude/mcp-catalog.json` (replaces the `mcp-catalog.stub.json` from `agents/character-schema`).
* Repo-level `.mcp.json` with env-var placeholders only; per-character overlay generation is left to `agents/tool-scopes` but the catalog carries the data it needs.
* Thin Forgejo MCP server `packages/agents/mcp/forgejo/` (stdio, TypeScript, `@modelcontextprotocol/sdk` 1.x) because no official one exists: tools `listRepos`, `getFile`, `listPullRequests`, `createPullRequest`, `commentOnPullRequest`.
* Smoke checker `pnpm mcp check`: starts each stdio server or probes each remote, lists tools, diffs against the catalog, reports missing env vars.
* Weekly workflow `.github/workflows/mcp-check.yml` and doc `docs/libraries/mcp-servers.md` with the catalog table and "adding a server" guide.

Out:
SPEC(first 1200): * Catalog entry: `{ id, name, kind: remote|stdio, package|url, version, auth: { kind: oauth|apiKey|none, envVars[], headless: true|false, notes }, tools: [{ name (mcp__<server>__<tool>), scope: read|write|destructive, description, rateLimitHint }], vendorRateLimit, sandbox: { available, how }, owner (character), allowedCharacters[], docsUrl, healthCheck, aliases[] }`.
* Servers to catalog: Linear (official remote `https://mcp.linear.app/mcp`, OAuth; owner Atlas), GitHub (official remote or `@modelcontextprotocol/server-github`; owner Atlas), Forgejo (wrapper above; owner Forge), Stripe (`@stripe/mcp`, test-mode keys; owner Ledger), Notion (official remote; owner Quill), Google Drive (org connector, read scopes recorded; owner Quill), Webflow (org connector; note `webflow_guide_tool` once per session; owner Beacon), Miro and Gamma (org connectors; Gamma is generate-only, cannot edit; owner Beacon), Playwright (`@playwright/mcp`; owner Sentinel), Postgres (`@modelcontextprotocol/server-postgres` read-only against staging; owner Forge).
* Scope classes drive defaults: `read` allowed to all characters; `write` allowed to owner and Atlas; `destructive` (delete issue, refund, drop table,
DOD:
* Catalog with all 11 servers validated in Vitest; generated JSON committed and `agents/character-schema` validator switched to it (comment on that issue).
* `.mcp.json` boots in a fresh session; screenshot of `/mcp` tool listing for Linear, GitHub, Stripe, Playwright attached to the PR.
* Forgejo wrapper: five tools with tests against a mocked API (msw), README, pinned version.
* `pnpm mcp check` passes locally and in the weekly workflow; a seeded drift (renamed tool) fails it in a test.
* Sentinel Security Auditor signs off on every scope class in a PR comment.
* Docs page rendered, CHANGELOG entry, Linear comment with the table and screenshot.
EDGE:
* Remote OAuth servers in headless orchestrator sessions: mark `headless: false`, document token pre-provisioning per bot account (`forge/bot-accounts`) or fall back to API-key servers.
* Vendor renames a tool: `aliases[]` keeps old names valid for 30 days; drift check warns then fails.
* Overlapping capability (GitHub vs Forgejo PRs): `prefer: forgejo` field per the `forge/vcs-decision-adr` decision.
* Unpinned server packages drift: exact pins; grouped by `libraries/upgrade-bot`.
* Tool misclassified as `read` but mutates (Stripe `create_payment_link`): checklist in the review; test asserts known write verbs are not `read`.
* Org connectors unavailable in CI: reported `skipped: interactive-only`, never green-washed.
DEPS: None; ready now. Consumed by `agents/character-schema`, `agents/tool-scopes`, `spec-builder/integrations-section`, `pm-linear/orchestrator`. Soft: `forge/bot-accounts`, `app-shell/env-config`.


## PAP-211 [P0 Infra M prio2 Backlog] Set the license policy (allow MIT/Apache/BSD, review AGPL, block SSPL) enforced by a CI license check
key=libraries/license-policy milestone=Evaluation process agent=Built by Scout (Library Evaluator) with Forge (Ops Runner) f
blockedBy=['PAP-209'] blocks=[]
GOAL: Make license surprises impossible: a written policy (allow permissive, review copyleft and source-available, block SSPL and unlicensed) and a CI job that scans every JavaScript and Rust dependency on every PR, fails on violations, and honours a waiver file for approved exceptions. `quality/security-scans` reserved a job slot for this; `collab/collab-research` (tldraw) and `growth/growth-research` (AGPL products) already depend on the tiers.
SCOPE: In:

* Policy doc `docs/libraries/license-policy.md` and machine config `ops/licenses/policy.yaml` (tiers per usage context).
* CI job `licenses` in `.github/workflows/security.yml` (or `licenses.yml` if that file is not merged) producing `reports/licenses.json`, SARIF and a job summary, runnable on Forgejo Actions.
* Waivers `ops/licenses/waivers.yaml` with expiry, plus Vitest fixtures for allow, review, block, waived and expired cases.
* `THIRD_PARTY_NOTICES.md` generation for shipped bundles (Tauri and web) at build time.
* `deny.toml` for `cargo-deny` mirroring the tiers, skipping cleanly until `Cargo.lock` exists (`app-shell/tauri-desktop`).
* One Needs Justin question: the license of PaperOS's own template code (currently the placeholder from `app-shell/monorepo-scaffold`).

Out: scoring libraries (`libraries/eval-rubric`), vulnerability scanning (`quality/security-scans`), legal a
SPEC(first 1200): * Contexts: `bundled` (shipped in web or native bundles, strictest), `server` (runs in our containers), `dev` (build and test tooling only), `service` (separately deployed OSS product). Derived automatically: `dependencies` of `apps/*` and `packages/*` imported by apps are `bundled`; `apps/api` and `ops/` are `server`; `devDependencies` are `dev`; `service` entries are declared by hand for products from `libraries/oss-products`.
* Tiers (SPDX ids). Allow in all contexts: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, Unlicense, CC0-1.0, Zlib, BlueOak-1.0.0, Python-2.0, MPL-2.0 (unmodified), OFL-1.1 and CC-BY-4.0 (assets only). Review (requires ADR plus waiver): LGPL-2.1/3.0 and GPL-2.0/3.0 (allowed in `dev` and `service` only, never `bundled`), AGPL-3.0 (`service` only, unmodified or with published fork), BUSL-1.1, ELv2, WTFPL, `SEE LICENSE IN` custom texts such as tldraw's. Block: SSPL-1.0, Commons Clause, JSON, `UNLICENSED` or missing license from third parties, any license in `bundled` that is copyleft.
* Scanner `ops/licenses/check.ts`: reads `pnpm licenses list --json --prod` plus `pnpm ls --json` for context derivation; parses SPDX expressions with `spdx-expression-p
DOD:
* Policy doc, `policy.yaml`, waivers schema, scanner, `deny.toml` and notices generator merged.
* Vitest fixtures: allowed, review without waiver (fails), waived (passes), expired waiver (fails), SPDX OR and AND expressions, field/file mismatch, missing license.
* One real CI run on a seeded fake SSPL package fails with an inline annotation; screenshot in the PR.
* `THIRD_PARTY_NOTICES.md` produced by `pnpm build` and included in the Tauri bundle resources.
* Sentinel Security Auditor approves; Justin answered (or was asked, with a default) the own-code license question via Needs Justin.
* CHANGELOG entry; Linear comment linking the policy and a sample report.
EDGE:
* tldraw `SEE LICENSE IN LICENSE.md` with watermark clause: review tier, waiver referencing the `collab/collab-research` ADR.
* Dual license `(MIT OR Apache-2.0)`: passes; `(GPL-3.0 AND MIT)`: review.
* GPL-licensed dev tool (for example a CLI) in `dev` context: allowed with a note, blocked if it ever moves to `dependencies`.
* License field says MIT, LICENSE file is proprietary: violation with `mismatch` reason.
* Fonts and icon sets (OFL, ISC, MIT): allowed as assets, notices generated.
* Lockfile out of sync with `package.json`: job fails fast with a clear message rather than scanning stale data.
DEPS: `libraries/eval-rubric` (hard: license gate references these tiers). Soft: `quality/security-scans` (job slot and SARIF merge), `quality/ci-gate1` (setup job), `collab/decision-log` (waiver ADR links). Consumed by `libraries/upgrade-bot`, `libraries/registry`, every research issue.


## PAP-212 [P0 Research M prio2 Backlog] Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend
key=libraries/ui-landscape milestone=Core adoptions decided agent=Researched by Scout (Library Evaluator) paired with Iris (Co
blockedBy=['PAP-209'] blocks=['PAP-67']
GOAL: Decide the headless component foundation for `packages/ui` by spiking Base UI, Radix Primitives, React Aria Components, Ark UI and the shadcn/ui distribution against PaperOS's real constraints (Tailwind v4, Tauri WebViews, detached windows, multi-input, WCAG 2.2 AA), and record it as an ADR. `design-system/primitives` proceeds with Base UI by default if this is not merged by 2026-09-19, so the outcome must land before then.
SCOPE: In:

* Spike `spikes/ui-kits/` with the same four components built in each candidate: Select, Dialog, Menu, Combobox (virtualized with 5k options), styled with Tailwind v4 tokens from `design-system/tokens` if merged, otherwise plain CSS variables.
* Scorecards per `libraries/eval-rubric` with extras: Tailwind v4 composability, controlled and uncontrolled APIs, portal behaviour inside Tauri detached windows (`app-shell/breakpoints-windows`), RTL, touch and pen behaviour (`input/input-abstraction`), roving focus and focus trap quality (`input/focus-management`), date and calendar component availability, release stability (Base UI 1.x status, Radix maintenance cadence).
* Measurements: gzipped bundle of the four components, axe results, keyboard-only walkthrough recording, render in webkit2gtk (Linux Tauri) and Chromium.
* Quick rejects with one-paragraph reasons: Headless UI, Mantine, MUI
SPEC(first 1200): * Time-box 1 agent-day; each candidate at most 90 minutes; missing information becomes a rubric penalty, not more research.
* Candidates and versions: `@base-ui-components/react` 1.x, `radix-ui` (unified package) latest, `react-aria-components` 1.x, `@ark-ui/react` 5.x, shadcn/ui CLI (evaluated as a distribution over Radix or Base UI, not as a library).
* Harness: Vite app with a route per candidate and component; Playwright captures screenshots at 375, 768, 1280 in light and dark; axe via `@axe-core/playwright`; bundle via `vite build --mode analyze` per route with `rollup-plugin-visualizer` JSON.
* Tauri check: run the harness inside the `app-shell/tauri-desktop` shell if merged, else in a minimal Tauri 2 scaffold under the spike; open a Dialog and a Menu from a secondary window and confirm portals attach to the correct document.
* Data written to `spikes/ui-kits/results/*.json` and rendered into the ADR table by `pnpm lib score`.
* Recommendation must also state: which primitives are missing in the winner (for example date picker) and where they come from (React Aria date components are the fallback candidate), and the migration cost in hours to the runner-up.
DOD:
* Spike merged under `spikes/` (excluded from `turbo build`), results JSON and generated comparison table committed.
* ADR accepted with scores, gates, rejected options and re-open criteria; Iris and Atlas comment approval on the PR.
* Screenshots at 375, 768, 1280 for the four components per candidate, plus a 30-second keyboard walkthrough video for the winner.
* Registry entries drafted (`libraries/registry`) or a Linear comment for Scout if the registry is not live.
* `design-system/primitives` description updated with the exact package and version.
* CHANGELOG entry; Linear comment linking ADR and results table.
EDGE:
* Base UI has not reached a stable 1.0 by evaluation date: score stability down and record the pre-1.0 API-churn risk explicitly.
* Candidate depends on its own styling runtime (Panda, Emotion): penalise under Tailwind composability, do not exclude.
* Portal rendered into the wrong window in Tauri: hard gate failure for detached panels unless a documented container prop exists.
* Combobox cannot virtualize: score a11y and performance separately; note TanStack Virtual integration effort.
* webkit2gtk rendering bugs (backdrop blur, popover positioning): record and check whether they are library or platform bugs.
* License changes (Radix is MIT, Ark MIT, React Aria Apache-2.0): verify at evaluation time via `libraries/license-policy` checker on the spike lockfile.
DEPS: `libraries/eval-rubric` (hard: scoring format; use the draft if unmerged). Soft: `design-system/tokens` (real tokens in the spike), `app-shell/tauri-desktop` (real shell for the WebView test). Blocks `design-system/primitives`; informs `input/focus-management`, `input/input-abstraction`.


## PAP-213 [P0 Research L prio2 Backlog] Survey table, canvas, editor and chart libraries (TanStack, AG Grid, tldraw, Tiptap, ECharts, visx) and recommend
key=libraries/data-landscape milestone=Core adoptions decided agent=Researched by Scout (Library Evaluator) paired with Nova (Vi
blockedBy=['PAP-209'] blocks=[]
GOAL: Choose the data-heavy foundations of the platform: the table library the views engine renders with, the chart library dashboards use, the map library, and a shortlist for canvas and rich text that `collab/collab-research` decides in depth. Each choice is scored with the shared rubric and recorded as an ADR so `tables/grid-view`, `tables/map-chart-views` and `collab/canvas-view` build without re-litigating.
SCOPE: In:

* Tables: TanStack Table v8 + TanStack Virtual, AG Grid Community (MIT), Glide Data Grid (canvas-rendered), react-data-grid; Handsontable rejected on license.
* Charts: Apache ECharts 5/6, visx, Recharts, Observable Plot, Nivo, Chart.js; measured with the dataviz guidance Iris owns.
* Maps: MapLibre GL JS, Leaflet; tile source options (self-hosted Protomaps PMTiles vs OpenFreeMap).
* Canvas and editor breadth pass only: tldraw, React Flow (`@xyflow/react`), Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate. Output is a two-candidate shortlist per category handed to `collab/collab-research`, not a decision.
* Spikes under `spikes/data-libs/`: 100k-row virtualized grid with inline edit, column resize, frozen columns and grouping; 10k-point line chart plus a stacked bar with theme switching; a 5k-marker map.
* Three ADRs (table, charts, maps) and registry entries.

Out: building the
SPEC(first 1200): * Time-box 1.5 agent-days: tables 4 hours, charts 3 hours, maps 1.5 hours, canvas and editor shortlist 2 hours.
* Rubric extras for tables: headless vs rendered, virtualization quality at 100k rows (scroll FPS in Playwright trace), inline editing hooks, column pinning, grouping and aggregation primitives, server-side pagination hooks (`tables/query-compiler`), accessibility of grid semantics (`role=grid`, roving cell focus per `input/focus-management`), keyboard drag-and-drop compatibility with dnd-kit (`input/drag-drop`), touch behaviour.
* Rubric extras for charts: tree-shaken size for bar, line, pie, number; theming via CSS variables or theme object driven by `design-system/tokens`; SVG vs canvas (screenshot stability for `quality/playwright-matrix`); accessible descriptions and data tables fallback; large-data performance; dark mode.
* Rubric extras for maps: vector tiles, clustering, offline tiles in Tauri, license of tiles and styles, bundle size.
* Harness: Vite app with a route per candidate; Playwright records traces and screenshots at 375, 1024, 1920; results to `spikes/data-libs/results/*.json`; `pnpm lib score` renders tables.
* Cross-links required: `tables/feature-par
DOD:
* Spikes merged under `spikes/` with results JSON and generated comparison tables.
* Three ADRs accepted (table, charts, maps) with Nova and Atlas approval comments; the canvas and editor shortlist posted as a comment on `collab/collab-research`.
* Grid spike shows 100k rows at 55+ FPS scroll in a Playwright trace on the reference laptop profile; chart spike renders 10k points under 200 ms; screenshots at the three widths in light and dark attached.
* Registry entries for adopted and rejected libraries drafted.
* `tables/grid-view` and `tables/map-chart-views` descriptions updated with exact packages and versions.
* CHANGELOG entry; Linear comment linking ADRs and result tables.
EDGE:
* AG Grid Community lacks a feature the parity audit needs (row grouping is Enterprise): document the gap explicitly rather than assuming.
* Canvas-rendered grid (Glide) defeats screen readers and Playwright DOM snapshots: score a11y and testability down and note the vision-agent dependency.
* ECharts full bundle is large: measure the tree-shaken `echarts/core` path only.
* Map tiles require a paid key: prefer self-hosted PMTiles; record ops cost.
* Library upgrade in flight (TanStack Table v9 alpha): evaluate the stable major and note the timeline.
* Two candidates tie: apply the rubric tie rule using migration cost, not another spike.
DEPS: `libraries/eval-rubric` (hard; use the draft if unmerged). Soft: `design-system/tokens` for theming tests, `data-layer/sync-research` for the sync engine the grid will bind to. Blocks `tables/grid-view`, `tables/map-chart-views`; informs `collab/collab-research`, `tables/view-model-spec`.


## PAP-214 [P0 Research L prio2 Backlog] Survey backend building blocks (Better Auth, Drizzle, Electric, Hocuspocus, Inngest, Resend) and recommend
key=libraries/backend-landscape milestone=Core adoptions decided agent=Researched by Scout (Library Evaluator) with Forge (Ops Runn
blockedBy=['PAP-209'] blocks=['PAP-43']
GOAL: Settle the server-side building blocks the plan has not yet decided, confirm the ones it has, and record everything as ADRs so Forge, Nova and Ledger stop making independent choices: job queue, transactional email, PDF generation, search engine, observability stack, feature flags and object storage are open; auth, ORM, sync, realtime and API layer have owning research issues and are confirmed here by cross-link only. Every choice must self-host in Docker on the Coolify VPS.
SCOPE: In:

* Open decisions with candidates: jobs and workflows (Inngest self-hosted, [Trigger.dev](<http://Trigger.dev>) self-hosted, BullMQ with Redis, pg-boss, Graphile Worker); email (Resend, Postmark, Amazon SES via Nodemailer, self-hosted Postal); PDF (Playwright print to PDF, `@react-pdf/renderer`, Typst); search (Postgres `tsvector` + pgvector, ParadeDB `pg_search`, Meilisearch, Typesense); observability (OpenTelemetry collector with Grafana LGTM, SigNoz, HyperDX); feature flags (Unleash, Flagsmith, own table plus `identity/rbac-abac` policies); storage (MinIO, Garage, SeaweedFS); validation (Zod 4 confirmed vs Valibot, ArkType); runtime (Node 22 LTS vs Bun for the API).
* Confirmations by cross-link: Better Auth (`identity/auth-research`), Drizzle (`data-layer/drizzle-schema`), ElectricSQL (`data-layer/sync-research`), Hocuspocus (`realtime/realtime-research`), oRPC (`data-layer/api-l
SPEC(first 1200): * Time-box 1.5 agent-days; each decision at most 90 minutes; measure with `docker stats` after a 5-minute warm-up under a scripted load of 50 req/s where applicable.
* Rubric extras: self-host maturity and docs, Postgres-native (fewer moving parts wins), memory footprint, TypeScript SDK quality, local dev story (`docker compose up` in `ops/compose/`), multi-tenant isolation, exit cost.
* Constraints: total added RAM for chosen services under 6 GB; Redis is acceptable only if two or more chosen services need it; anything requiring Kubernetes is rejected.
* Deliverable `ops/compose/candidates/` with one compose file per candidate used for measurement, deleted or moved to `spikes/` on merge.
* Each ADR names the consuming issue, the exact package or image tag, env vars to add to `app-shell/env-config`, and the fallback candidate with migration hours.
* Email ADR must cover deliverability (DKIM, SPF, DMARC setup) and sandbox mode for agent sessions (`email:send (sandbox until approved)` per Beacon's access scope).
* Search ADR must consider `data-layer/search`'s plan for `tsvector` + pgvector as the baseline and justify any extra service.
DOD:
* ADRs accepted for jobs, email, PDF, search, observability, feature flags, storage, validation and runtime; Forge and Atlas approval comments.
* Resource budget table committed with measured numbers and the total under budget.
* Compose files for the winners merged into `ops/compose/` (others removed), each starting cleanly with `docker compose up` in CI on a Forgejo runner (`forge/actions-runner`) or GitHub.
* Registry entries drafted; license check from `libraries/license-policy` passes on all chosen images and packages.
* Consuming issue descriptions updated with the decisions (comments on each).
* CHANGELOG entry; Linear comment with the summary table.
EDGE:
* Candidate is open source but self-hosting is undocumented or license-gated ([Trigger.dev](<http://Trigger.dev>), Inngest tiers): score self-host path only and verify the license tier.
* Service needs Redis or ClickHouse (SigNoz): count the extra footprint against the 6 GB budget.
* Bun incompatibility with a chosen library (Tauri sidecars, native modules): runtime decision defaults to Node 22.
* PDF rendering needs fonts and CJK support: test with a sample invoice containing CJK and RTL text.
* Email provider blocks sending from unverified domains in test: use sandbox mode and document the verification steps as a Justin task.
* Feature flag needs are covered by page-spec access rules: record "no new service" as a valid decision.
DEPS: `libraries/eval-rubric` (hard; use the draft if unmerged). Soft: `identity/auth-research`, `data-layer/sync-research`, `realtime/realtime-research` (link both ways, do not duplicate). Informs `data-layer/search`, `data-layer/observability`, `data-layer/file-storage`, `collab/notifications`, `business-core/invoicing`, `growth/outreach-sequences`.


## PAP-215 [P1 Research L prio2 Backlog] Evaluate whole OSS products to embed or fork (Twenty CRM, NocoDB, Baserow, Plane, Cal.com, Formbricks, Postiz)
key=libraries/oss-products milestone=Core adoptions decided agent=Researched by Scout (Library Evaluator) with Forge (Ops Runn
blockedBy=['PAP-209'] blocks=[]
GOAL: Decide, product by product, whether PaperOS embeds, forks, borrows from or rejects whole open-source products that overlap with planned systems: Twenty (CRM), NocoDB and Baserow (tables), Plane (project management), [Cal.com](<http://Cal.com>) (scheduling), Formbricks (forms and surveys), Postiz (social scheduling), plus Chatwoot (support inbox) and Listmonk (email campaigns) because `growth/support-inbox` and `growth/outreach-sequences` need the same answer. Each decision is recorded in one ADR with a mode and handed to the owning project.
SCOPE: In:

* Four modes with definitions: `embed` (run as a separate service, integrate via API, SSO from Better Auth and theming; `service` license context), `fork` (vendor code into the monorepo; almost never, requires Justin), `borrow` (study data model and UX, reimplement on the tables and views engine), `reject`.
* Spike: run each product with `docker compose` from `spikes/oss-products/<id>/`, seed one tenant with sample data, exercise the core flow, capture screenshots at 375 and 1280, record RAM, startup time, and export completeness.
* Scorecards per `libraries/eval-rubric` with extras: license and tenancy (`libraries/license-policy` service tier), API completeness for the flows we need, SSO and embedding (iframe, theming, deep links), data ownership and export formats, ops footprint, UX distance from what `tables/view-model-spec` will offer, upstream velocity and fork risk.
* One ADR 
SPEC(first 1200): * Time-box 2 agent-days; each product at most 2 hours including compose start-up; if a product does not start within 20 minutes on the reference VPS profile, score ops down and move on.
* Expected licenses to verify at evaluation time: Twenty AGPL-3.0, NocoDB AGPL-3.0, Baserow MIT core with premium modules, Plane AGPL-3.0, [Cal.com](<http://Cal.com>) AGPL-3.0 plus commercial `ee`, Formbricks AGPL-3.0 plus `ee`, Postiz AGPL-3.0, Chatwoot MIT, Listmonk AGPL-3.0. AGPL forces `embed` or `borrow`, never `fork` into shipped code, per policy.
* Required flows per product: Twenty (create company, contact, deal, move stage, API read), NocoDB and Baserow (create table, relation, filter, kanban, API and webhook), Plane (issue, cycle, board, API), [Cal.com](<http://Cal.com>) (event type, booking, webhook), Formbricks (survey, embed, response webhook), Postiz (connect a mock provider, schedule a post, approval), Chatwoot (inbox, assign, reply, contact link), Listmonk (list, campaign, template, bounce handling).
* Compose files use pinned image tags; secrets via `.env.example`; measurements from `docker stats` after five minutes idle and after the flow.
* Borrow deliverable: for each `borrow` ve
DOD:
* Nine compose spikes committed under `spikes/oss-products/`, each with `README.md`, screenshots at 375 and 1280, and `metrics.json`.
* ADR accepted with the mode matrix and per-product rationale; Atlas, Nova (tables), Beacon (growth) approvals in PR comments.
* Registry entries created or drafted for all nine; license checker passes with `service` context recorded.
* Borrow reference docs written for every `borrow` verdict; embed contracts for every `embed` verdict.
* Comments posted on `growth/growth-research`, `tables/feature-parity-audit`, `growth/support-inbox`, `pm-linear/pm-data-model` with the relevant verdicts.
* CHANGELOG entry; Linear comment with the matrix and screenshot gallery.
EDGE:
* Product requires a paid tier for SSO or API (common in `ee` folders): score embed down and record the exact gate.
* Product ships its own auth and cannot trust an external session: embed requires a proxy or is downgraded to borrow.
* Multi-tenancy is per-instance only (one deployment per tenant): ops cost multiplies; usually reject for embed.
* Export is UI-only with no API: fail data-ownership gate.
* Upstream is a single-company project with recent license changes: raise fork risk, prefer borrow.
* Docker images need more than 2 GB RAM ([Cal.com](<http://Cal.com>), Twenty): record and weigh against the VPS budget from `libraries/backend-landscape`.
DEPS: `libraries/eval-rubric` (hard). Soft: `libraries/license-policy` (service tier), `tables/feature-parity-audit` (shares NocoDB and Baserow findings, cross-link only). Informs `growth/growth-research`, `growth/crm-model`, `growth/support-inbox`, `growth/social-scheduler`, `pm-linear/pm-data-model`, `tables/view-model-spec`.


## PAP-216 [P1 Build M prio2 Backlog] Build the library registry in the docs system: adopted, trialing, rejected with reasons and owners
key=libraries/registry milestone=Registry live agent=Built by Scout (Library Evaluator) with Quill for the docs p
blockedBy=['PAP-128', 'PAP-209'] blocks=['PAP-218']
GOAL: Give PaperOS one place that says what third-party code we use, why, who owns it and where the decision lives: a file-based registry rendered in-app through the docs engine, with a drift check so a dependency cannot appear in a lockfile without a registry entry and a rejected library cannot creep back in. This is the memory the Scout routine, Renovate summaries and every research ADR write into.
SCOPE: In:

* Registry entries `docs/registry/entries/<id>.yaml`, Zod 4 schema `packages/spec/src/libraries/registry.ts`, generated `docs/.generated/registry.json`.
* CLI `pnpm lib add <npm-name|crate:<name>|image:<ref>> --status trialing --owner scout --adr 0012 --category ui` scaffolding an entry with facts from `scripts/lib-facts.ts` (`libraries/eval-rubric`); `pnpm lib registry build`; `pnpm lib registry check`.
* In-app page `/_app/docs/registry` rendered by `collab/docs-engine` (MDX page plus a small React table component) with filters by status, category and owner, status badges, ADR and scorecard links, and a "review due" indicator.
* Drift check job in Gate 1 (`quality/ci-gate1` `generated-drift` pattern).
* Seed: every current production dependency of paperos-template imported with `status: adopted` and `adr: pending` where no ADR exists, plus one Linear issue listing the pending ADRs
SPEC(first 1200): * Entry schema: `{ id, name, source: { kind: npm|crate|image|service, ref }, version (derived from lockfile at build, not hand-edited), status: candidate|trialing|adopted|reference|deprecated|replaced|rejected, category (ui|data|canvas|editor|charts|maps|auth|db|sync|realtime|jobs|email|pdf|storage|search|observability|testing|build|agent-tooling|product), owner (character id), adr (NNNN or `pending`), scorecard (path), license (SPDX, verified by `libraries/license-policy`), context: bundled|server|dev|service, usedBy: [package names], alternativesConsidered: [ids], reasons, addedAt, reviewAt, replacedBy?, notes }`.
* Build: reads `pnpm-lock.yaml` and `Cargo.lock` to fill `version` and `usedBy`; resolves `adr` against `docs/.generated/adr-index.json` from `collab/decision-log` and fails on a dangling id; writes `registry.json` `{ generatedAt, entries[], stats: { byStatus, byCategory } }`.
* Check rules: every production dependency of any non-private package has an entry with status `adopted` or `trialing` (error); entry with status `rejected`, `replaced` or `deprecated` present in a lockfile (error); entry with no `usedBy` and status `adopted` (warning, "unused"); `reviewAt` in the
DOD:
* Schema, CLI, build and check merged; Vitest covers schema, lockfile parsing for pnpm and Cargo, ADR resolution, every check rule with fixtures, and status transitions.
* Seed entries for all current production dependencies committed; check passes on `main`; the pending-ADR Linear issue exists.
* Drift check runs in Gate 1 and a seeded unregistered dependency fails it (screenshot of the red status).
* In-app page screenshots at 375, 1024 and 1920 in light and dark; axe clean; Playwright test filters by status and opens an entry.
* README and `docs/libraries/registry.md` written; CHANGELOG entry; Linear comment with page link and screenshots.
* Research issues' ADR outputs (`libraries/*-landscape`, `libraries/oss-products`) have entries, added by this issue if their drafts exist.
EDGE:
* Same library used in `bundled` and `dev` contexts: one entry, `context` becomes an array, strictest license rule applies.
* Dependency renamed or scoped (`radix-ui` unified package replacing `@radix-ui/*`): `aliases[]` on the entry so check passes during migration.
* Lockfile has multiple versions of one package: `version` lists all; warning if more than two.
* Entry references an ADR still `proposed`: allowed for `trialing`, error for `adopted`.
* `adr-index.json` missing because decision-log has not merged: build warns and skips ADR resolution, does not fail.
* Cargo.lock absent before Tauri lands: Rust checks skipped with a notice.
DEPS: `libraries/eval-rubric` (hard: facts collector and scorecard paths), `collab/docs-engine` (hard: in-app rendering). Soft: `collab/decision-log` (ADR index), `quality/ci-gate1` (job slot), `libraries/license-policy` (license field verification). Consumed by `libraries/upgrade-bot`, `libraries/scout-agent`, `quality/review-rubrics` (third-party findings pointer).


## PAP-217 [P1 Infra M prio3 Backlog] Set up Renovate with grouped upgrades and agent-reviewed changelog summaries
key=libraries/upgrade-bot milestone=Registry live agent=Built by Scout (Library Evaluator) with Forge (Ops Runner) f
blockedBy=['PAP-78'] blocks=[]
GOAL: Keep dependencies current without burning Justin's or the agents' attention: self-hosted Renovate opens grouped upgrade PRs on a schedule, every PR gets an agent-written summary of what changed and what it means for our code, safe upgrades merge themselves once the gates pass, and risky ones become Linear work. Runs on both forges because it is a workflow, not the Mend app.
SCOPE: In:

* `renovate.json` at the paperos-template root plus a shared preset `ops/renovate/default.json` other imagine-os repos extend.
* Scheduled workflow `.github/workflows/renovate.yml` running `renovate` CLI (Docker image `renovate/renovate` pinned) against the repo with a bot token from `forge/bot-accounts` (Scout bot); runnable on Forgejo Actions via the Forgejo platform setting.
* Summary workflow `.github/workflows/upgrade-summary.yml` triggered when a Renovate PR opens or updates: spawns a Scout (Library Evaluator) Claude Code session through the orchestrator's headless entry point to post the summary comment.
* Automerge rules tied to Gate 1 and Gate 3 statuses from `quality/ci-gate1` and `quality/playwright-matrix`, executed by Atlas's Merger sub-agent so `forge/branch-policy` review rules hold.
* Dependency dashboard issue mirrored to Linear.

Out: security vulnerability alerts 
SPEC(first 1200): * Renovate config: `extends: ["config:recommended", ":semanticCommits", ":pinAllExceptPeerDependencies"]`; `schedule: ["before 6am on monday"]` for non-security; `vulnerabilityAlerts.enabled: true` with `schedule: at any time`; `lockFileMaintenance` weekly; `rangeStrategy: pin`; `commitBodyTable: true`; `commitBody: "Linear: PAP-<upgrades-epic>\nCharacter: scout"` to satisfy the trailer rule from `forge/branch-policy`; `labels: ["upgrade", "upgrade:{{updateType}}"]`.
* Groups (`packageRules`): `@tanstack/*`; UI primitives (`@base-ui-components/*`, `radix-ui`, `react-aria-components`); editor and CRDT (`@tiptap/*`, `yjs`, `@hocuspocus/*`); `drizzle-orm` + `drizzle-kit`; test tooling (`vitest`, `@playwright/*`, `@axe-core/*`); `@biomejs/biome`; MCP servers from `libraries/mcp-servers`; Tauri (`@tauri-apps/*` npm and `tauri*` cargo in one group); GitHub Actions; Docker image tags in `ops/compose/`. Majors are never grouped with minors.
* Automerge: `devDependencies` patch and minor, and `dependencies` patch, with `automergeType: pr` and required statuses `gate/1-static`, `gate/3-visual`, `licenses`; Merger performs the merge when statuses are green and the summary verdict is `merge`. 
DOD:
* `renovate.json`, preset, both workflows merged; first scheduled run opens grouped PRs (screenshot of the PR list).
* One patch PR automerges end to end with green statuses and a summary comment; one seeded major (pin an old version in a fixture branch) gets a `hold` or `needs-work` summary and a Linear issue.
* Summary workflow tests: prompt fixture and a mocked Claude response asserting the comment schema and the branch push path.
* Workflow verified on a Forgejo runner (`forge/actions-runner`) with the Forgejo platform setting; link in the PR.
* Docs `docs/libraries/upgrades.md` covering groups, automerge rules and how to pause Renovate; CHANGELOG entry; Linear comment with links.
* Sentinel Security Auditor confirms the bot token scopes are least privilege.
EDGE:
* Renovate PR conflicts with an agent's open PR touching the lockfile: `rebaseWhen: conflicted`, and `pm-linear/concurrency` file-lock hints treat `pnpm-lock.yaml` as shared.
* Release notes missing or huge: summary falls back to the diff of `package.json` and changelog headings; truncate to 2k tokens per package.
* Upgrade breaks Gate 3 visuals only: verdict `needs-work`, comment includes the screenshot diff links.
* Same package updated by a human agent mid-week: Renovate rebases or closes as superseded.
* Bot token expires: workflow fails loudly and posts to the Linear dashboard issue.
* Renovate schedule collides with the release train (`quality/release-train`): schedule Monday morning, release candidate Friday.
DEPS: `quality/ci-gate1` (hard: required statuses). Soft: `quality/playwright-matrix`, `quality/perf-budgets`, `quality/security-scans`, `libraries/license-policy` (report inputs), `forge/bot-accounts` (token), `forge/actions-runner`, `pm-linear/orchestrator` (headless session entry), `agents/cost-controls`, `libraries/registry`.


## PAP-218 [P2 Build M prio3 Backlog] Create the Scout character routine: weekly scan for new libraries relevant to open issues
key=libraries/scout-agent milestone=Registry live agent=Built by Scout (Library Evaluator) with Atlas (Dispatcher) f
blockedBy=['PAP-104', 'PAP-216'] blocks=[]
GOAL: Make discovery continuous: every Monday the Scout character scans for libraries and products relevant to the issues currently open in Linear, pre-scores them with the rubric and license policy, records candidates in the registry and tells the owning issues, without creating noise or spending more than its budget. Discovery becomes a routine the org runs, not a thing someone remembers to do.
SCOPE: In:

* Skill `.claude/skills/scout-scan/SKILL.md` with `scripts/` (query builder, facts collector reuse, dedupe, report renderer) in the `agents/skills-library` format.
* Scheduled workflow `.github/workflows/scout-scan.yml` (Monday 06:00 UTC, also `workflow_dispatch`) that asks the orchestrator (`pm-linear/orchestrator`) to spawn Scout (Library Evaluator) with the skill.
* Scan report `docs/registry/scans/YYYY-MM-DD.md` rendered by the docs engine, and `docs/registry/scans/seen.json` as dedupe memory.
* Linear actions: comments on relevant issues, up to three new Research issues per scan in Backlog, and a pinned "Scout scans" issue updated with each summary.
* Watch list: adopted registry entries checked for license changes, archival, or deprecation notices.
* Golden task for `agents/eval-harness`.

Out: making adoption decisions (research issues and ADRs do that), upgrading versions (`
SPEC(first 1200): * Inputs each run: open Linear issues in Backlog and Ready for Claude with labels Build or Research (Linear API via the `linear-update` skill script), `registry.json`, `adr-index.json`, previous three scan reports and `seen.json`.
* Query building: per project with open issues, derive three to five queries from issue titles and the project's category list (for example `tables` -> "react virtualized grid", "formula engine typescript"); sources are npm search, GitHub search (stars over 300, pushed within 12 months), and WebSearch limited to 10 results per query; total candidates capped at 60 per run.
* Filtering: drop anything already in the registry unless a new major version or a status-relevant change appeared; drop license-policy `block` tier; run `scripts/lib-facts.ts` for the rest and compute a facts-only pre-score (maintenance, license, bundle size, TypeScript quality; a11y and agent-friendliness left `unknown`).
* Relevance: each surviving candidate is linked to specific issue keys with a one-sentence rationale; candidates without a linked issue are dropped.
* Report sections: summary line, new candidates per project (name, version, license, pre-score, linked issues, recommen
DOD:
* Skill, scripts, workflow, report template and golden task merged; `pnpm agents build` lists the skill for Scout only.
* Vitest: query builder from fixture issues, dedupe against `seen.json`, pre-score computation, report rendering snapshot, action limits (three research issues, one comment per issue).
* Golden task in `agents/eval-harness`: frozen issue list and mocked search results produce a report matching the expected shape and actions; scored nightly.
* One real dispatch run against Linear team PAP with a `PAP-SANDBOX` label produced a report, a candidate entry and a comment; links in the PR.
* Scan report page screenshot at 375 and 1280 in the docs engine; CHANGELOG entry; Linear comment on the pinned "Scout scans" issue.
* Atlas approves the action limits; Sentinel confirms Linear scopes are comment and create-in-Backlog only.
EDGE:
* No open issues in a project: skip it; report says so.
* Search API rate-limited or down: partial report, `deferred` list, no failure email storms.
* Candidate is a fork of an adopted library: mark `related` to the adopted entry rather than a new candidate.
* Adopted library changes license (watch list): create a Research issue with priority 1 regardless of the three-issue cap and mention `libraries/license-policy`.
* Duplicate candidates across projects: one registry entry, multiple linked issues.
* Orchestrator unavailable: workflow fails visibly and retries next week; no direct Claude call bypassing logging (`agents/prompt-logging-hook`).
DEPS: `libraries/registry` (hard: candidate entries), `agents/roster-v1` (hard: Scout character definition). Soft: `agents/skills-library` (skill format, `linear-update`), `pm-linear/orchestrator` (spawn path), `agents/cost-controls`, `agents/eval-harness`, `pm-linear/issue-contract`, `libraries/license-policy`, `libraries/eval-rubric`.
