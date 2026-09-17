DOC = "https://linear.app/paperos/document/round-2-pending-issues-libraries-9-63c73eed632d"
DESCRIPTIONS = {}

DESCRIPTIONS["PAP-209"] = """**Goal**

Define the single rubric and ADR table every "should we adopt X" question in PaperOS is answered with, so twenty parallel sessions score libraries the same way and Atlas can compare ADRs from different characters. Six research issues already cite it (PAP-31, PAP-56, PAP-127, PAP-139, PAP-188, PAP-182); this issue makes it real and machine-checkable.

**Scope**

In:

* `docs/libraries/rubric.md`: six criteria (license, maintenance, bundle size, accessibility, TypeScript quality, agent-friendliness), 0-4 anchors, default weights, hard-fail gates, rule for domain extras.
* `packages/spec/libraries/rubric.yaml` with Zod 4 schema `packages/spec/src/libraries/rubric.ts` (`RubricSchema`, `ScorecardSchema`).
* `docs/libraries/scorecard.template.yaml` and CLI `pnpm lib score <scorecard.yaml>`: validate, compute weighted totals, render the Alternatives table ADRs paste in.
* Facts collector `scripts/lib-facts.ts` (npm downloads, last publish, stars, last commit, median issue age, `license`, `types`, gzipped size via esbuild metafile) writing `facts.json`; cache `.cache/lib-facts/`, `GITHUB_TOKEN` support.
* ADR template additions (Alternatives table, Re-open criteria) in `docs/adr/template.md`, created here if PAP-130 has not merged.
* Worked example: TanStack Table v8 versus AG Grid Community under `docs/libraries/examples/`.

Out: the surveys (PAP-212, PAP-213, PAP-214), license mechanics (PAP-211), registry UI (PAP-216).

**Spec**

* Weights (sum 100): license 20, maintenance 20, bundle 15, a11y 15, TS 15, agent-friendliness 15; `n/a` criteria drop and the rest rescale, recorded on the scorecard.
* Anchors, examples: maintenance 4 = release in 90 days, 3+ maintainers or company backing, median first response under 14 days; 0 = archived or 18 months silent. Bundle 4 = under 10 KB gzipped for used imports, 0 = over 250 KB. Agent-friendliness 4 = Markdown docs or `llms.txt`, typed examples, typed errors, small surface, well known to Claude.
* Hard gates (any fail = `reject`): license outside PAP-211 allow tier without waiver; no types; UI library failing in Tauri WebViews; vendor cloud with no self-host path.
* Scorecard `{ candidate, version, evaluatedBy, date, issue, facts, scores: { <id>: { score, evidence } }, extras[], gates, migrationCostHours, verdict: adopt|trial|reject }`; scores of 3 or 4 need a URL or repo path in `evidence` or the CLI fails.
* Ties within 5 points decided by `migrationCostHours` and the owning character's written judgement, never re-scoring.

**Interface contract**

Provides: `RubricSchema`, `ScorecardSchema`, `pnpm lib score` (also `--facts-only` for PAP-218 pre-scores), `scripts/lib-facts.ts` and `facts.json` shape, the ADR sections, `docs/libraries/scorecards/` as the canonical scorecard folder every research issue writes into. Consumes: PAP-211 tiers for the license gate (draft acceptable), PAP-130 ADR frontmatter (soft). Consumers: PAP-211, PAP-212, PAP-213, PAP-214, PAP-215, PAP-216 (facts and scorecard paths), PAP-218, and the six research issues above.

**Definition of done**

* Rubric doc, `rubric.yaml`, schemas, template and CLI merged.
* Worked example committed; rendered table matches its snapshot.
* `docs/adr/template.md` carries both sections consistent with PAP-130 frontmatter.
* Atlas approves weights and gates; Iris confirms a11y anchors; Sentinel passes the CLI.
* CHANGELOG; Linear comment linking rubric and example; one comment on each of the six research issues with final paths.

**Test plan**

* Vitest: schema validation, rescaling on `n/a`, gate logic, evidence rule failure, tie rule, Markdown rendering snapshot, facts collector against recorded npm and GitHub responses.
* CLI smoke in Gate 1: `pnpm lib score docs/libraries/examples/*.yaml` exits 0.
* Docs lint: every anchor cell in `rubric.md` is non-empty (table parser test).

**Demo**

Reviewer runs `pnpm lib score docs/libraries/examples/tanstack-vs-aggrid.yaml`, reads the weighted table, then removes an `evidence` URL and reruns to see the CLI fail with the criterion named. Under one minute.

**Edge cases**

* Monorepo library: score only imported packages, list them in `facts`.
* Non-npm candidate (crate, Docker image, SaaS): crates.io or Docker Hub facts; size `n/a`.
* Open-core (tldraw watermark, AG Grid Enterprise): score the free tier, list excluded features.
* Single maintainer: maintenance capped at 2 unless backed.
* GitHub rate limited in CI: facts older than 7 days warn, not fail.

**Dependencies**

None; ready now. Blocks PAP-211, PAP-212, PAP-213, PAP-214, PAP-215, PAP-216. Soft: PAP-130.

**Agent**

Written by Scout (Library Evaluator). Reviewed by Atlas (weights, gates) and Sentinel (Code Reviewer).

**Size**

S: one document, one small schema and CLI, one fixture; the value is sharp anchors.
"""

DESCRIPTIONS["PAP-210"] = """**Goal**

Produce the catalog of every MCP server and connector agents can reach (Linear, GitHub, Forgejo, Stripe, Notion, Google Drive, Webflow, Miro, Gamma, Playwright, Postgres) with each tool's scope class, auth, rate limits and permitted characters, and commit working `.mcp.json` so a fresh Claude Code session has integrations on first boot. PAP-103 validates `mcpServers[]` against it and PAP-121 cross-checks connector files with it.

**Scope**

In:

* `.claude/mcp-catalog.yaml`, Zod 4 schema `packages/agents/src/mcp-catalog.ts`, generated `.claude/mcp-catalog.json` replacing the stub from PAP-103.
* Repo `.mcp.json` with env-var placeholders only; per-character overlays stay with PAP-106.
* Thin Forgejo MCP server `packages/agents/mcp/forgejo/` (stdio, `@modelcontextprotocol/sdk` 1.x): `listRepos`, `getFile`, `listPullRequests`, `createPullRequest`, `commentOnPullRequest`.
* `pnpm mcp check`: starts each stdio server or probes each remote, lists tools, diffs against the catalog, reports missing env vars.
* Weekly `.github/workflows/mcp-check.yml`; `docs/libraries/mcp-servers.md` with table and "adding a server" guide.

Out: enforcing allowlists (PAP-106), page-spec connector registry (PAP-121), end-user OAuth, servers beyond the Forgejo wrapper.

**Spec**

* Entry `{ id, name, kind: remote|stdio, package|url, version, auth: { kind, envVars[], headless, notes }, tools: [{ name, scope: read|write|destructive, description, rateLimitHint }], vendorRateLimit, budgetPerSession, sandbox: { available, how }, owner, allowedCharacters[], docsUrl, healthCheck, aliases[], prefer? }`.
* Owners: Linear and GitHub Atlas; Forgejo and Postgres Forge; Stripe Ledger; Notion and Drive Quill; Webflow, Miro, Gamma Beacon; Playwright Sentinel.
* Scope defaults: `read` to all; `write` to owner and Atlas; `destructive` denied and routed to Needs Justin (PAP-94). Missing class fails the schema.
* Rate limits from vendor docs (Linear about 1500 req/h per key, Stripe 100 req/s test, Notion 3 req/s) with `budgetPerSession` passed by PAP-96 to sessions.
* Sandboxes: Stripe test mode, Linear `PAP-SANDBOX` label, Webflow staging site, Notion `Sandbox` tree, Postgres staging.
* Secrets never committed; env names match PAP-17; interactive-only org connectors report `skipped`.

**Interface contract**

Provides: `McpCatalogSchema`, `mcp-catalog.json` (`{ servers[] }`), tool name grammar `mcp__<server>__<tool>`, `.mcp.json`, Forgejo server package `@paperos/mcp-forgejo`, `pnpm mcp check` exit codes (0 ok or skipped, 1 drift, 2 missing required env), doc page. Consumes: PAP-17 env names (soft), PAP-48 bot tokens for headless remotes (soft), PAP-44 `prefer: forgejo` decision. Consumers: PAP-103 validator, PAP-106 overlays, PAP-121 cross-check, PAP-96 budgets, PAP-217 pins the server versions in a Renovate group.

**Definition of done**

* Catalog with all 11 servers validates; generated JSON committed; comment on PAP-103 to switch the validator.
* `.mcp.json` boots in a fresh session; screenshot of `/mcp` listing Linear, GitHub, Stripe and Playwright attached.
* Forgejo wrapper: five tools tested against a mocked API (msw), README, pinned version.
* `pnpm mcp check` passes locally and weekly; a seeded renamed tool fails it in a test.
* Sentinel Security Auditor signs off every scope class in a PR comment.
* Docs page; CHANGELOG; Linear comment with table and screenshot.

**Test plan**

* Vitest: schema (missing scope rejected, known write verbs never `read`), catalog completeness (11 servers), alias expiry logic, Forgejo tools with msw including auth failure.
* Integration: `pnpm mcp check` against real stdio servers in CI with placeholder env; remote OAuth servers marked skipped.
* Manual: fresh Claude Code session `/mcp` screenshot.

**Demo**

Reviewer runs `pnpm mcp check` and reads the table of 11 servers with tool counts and env status, then opens `mcp-catalog.json` to find Stripe `create_payment_link` classed `write`. Under one minute.

**Edge cases**

* Remote OAuth in headless sessions: `headless: false`, token pre-provisioning per bot documented or API-key fallback.
* Vendor renames a tool: `aliases[]` valid 30 days; drift warns then fails.
* GitHub versus Forgejo PR overlap: `prefer: forgejo`.
* Misclassified mutating tool: review checklist plus verb test.
* Org connectors unavailable in CI: `skipped: interactive-only`, never green-washed.

**Dependencies**

None; ready now. Blocks PAP-121. Soft: PAP-48, PAP-17, PAP-44.

**Agent**

Built by Scout (Library Evaluator) with Atlas on Linear and GitHub specifics. Reviewed by Sentinel (Security Auditor) and Forge for the wrapper.

**Size**

M: cataloging is quick; the Forgejo wrapper and checker are real code with tests.
"""

DESCRIPTIONS["PAP-211"] = """**Goal**

Make license surprises impossible: a written policy (allow permissive, review copyleft and source-available, block SSPL and unlicensed) and a CI job that scans every JavaScript and Rust dependency on every PR, fails on violations and honours a waiver file with expiry. PAP-80 reserved the job slot; PAP-127 (tldraw) and PAP-188 (AGPL products) depend on the tiers.

**Scope**

In:

* `docs/libraries/license-policy.md` and `ops/licenses/policy.yaml` (tiers per context).
* CI job `licenses` in `security.yml` (or `licenses.yml` if PAP-80 is unmerged) producing `reports/licenses.json`, SARIF and a summary; runs on Forgejo Actions.
* `ops/licenses/waivers.yaml` with expiry; fixtures for allow, review, block, waived, expired.
* `THIRD_PARTY_NOTICES.md` generated at build for web and Tauri bundles.
* `deny.toml` for `cargo-deny` mirroring the tiers, skipping cleanly until `Cargo.lock` exists.
* One Needs Justin question: the license of PaperOS's own template code.

Out: scoring (PAP-209), vulnerability scanning (PAP-80), legal advice.

**Spec**

* Contexts derived automatically: `bundled` (deps of `apps/*` and packages they import), `server` (`apps/api`, `ops/`), `dev` (devDependencies), `service` (declared by hand for PAP-215 products).
* Allow everywhere: MIT, Apache-2.0, BSD-2/3-Clause, ISC, 0BSD, Unlicense, CC0-1.0, Zlib, BlueOak-1.0.0, Python-2.0, MPL-2.0 unmodified, OFL-1.1 and CC-BY-4.0 for assets. Review (ADR plus waiver): LGPL and GPL in `dev` and `service` only, AGPL-3.0 `service` only, BUSL-1.1, ELv2, WTFPL, `SEE LICENSE IN` texts such as tldraw's. Block: SSPL-1.0, Commons Clause, JSON, `UNLICENSED` or missing, any copyleft in `bundled`.
* Scanner `ops/licenses/check.ts`: `pnpm licenses list --json --prod` plus `pnpm ls --json` for contexts; SPDX via `spdx-expression-parse` and `spdx-satisfies` (OR passes if any branch allowed, AND needs all); LICENSE file text wins over a disagreeing `license` field and flags `mismatch`. Rust via `cargo deny check licenses`.
* Waiver `{ package, versionRange, license, context, reason, adr, approvedBy: Justin|Atlas, expires }`; Atlas may approve `review`, `block` needs Justin; expired fails.
* Private workspace packages and uninstalled optional peers skipped; budget under 90 s.

**Interface contract**

Provides: `policy.yaml` tiers consumed as data by PAP-209's license gate and PAP-216's `license` field verification, `reports/licenses.json` `{ status, scanned, violations: [{ package, version, license, context, tier, waiver?, reason }], warnings, notices }`, status `licenses`, waivers schema, `pnpm licenses:check` and `pnpm licenses:notices`, `deny.toml`. Consumes: PAP-78 setup action and job slot, PAP-80 SARIF merge (soft), PAP-130 ADR links (soft). Consumers: PAP-217 (report delta on Renovate PRs, required status), PAP-216, PAP-212 to PAP-215 (spike lockfiles), PAP-218 (`block` tier filter).

**Definition of done**

* Policy doc, `policy.yaml`, waivers schema, scanner, `deny.toml`, notices generator merged.
* Real CI run on a seeded fake SSPL package fails with an inline annotation; screenshot attached.
* `THIRD_PARTY_NOTICES.md` produced by `pnpm build` and bundled in Tauri resources.
* Sentinel Security Auditor approves; own-code license question filed to Needs Justin with a default.
* CHANGELOG; Linear comment linking policy and a sample report.

**Test plan**

* Vitest fixtures: allowed, review without waiver (fail), waived (pass), expired waiver (fail), `(MIT OR Apache-2.0)`, `(GPL-3.0 AND MIT)`, field and file mismatch, missing license, GPL dev tool moved to `dependencies` (fail), lockfile out of sync (fast fail).
* CI: seeded violation branch red; clean `main` green under 90 s.
* Notices: snapshot of the generated file for the template.

**Demo**

Reviewer adds a fake SSPL package to a branch, pushes, and watches the `licenses` check fail with the package, tier and context annotated inline; reverts and sees green plus `THIRD_PARTY_NOTICES.md` in the build output. Under two minutes.

**Edge cases**

* tldraw `SEE LICENSE IN LICENSE.md` with watermark clause: review, waiver referencing the PAP-127 ADR.
* Dual license passes; `AND` with copyleft is review.
* GPL CLI in `dev`: allowed with note, blocked if it moves to `dependencies`.
* Fonts and icons (OFL, ISC, MIT): allowed as assets, notices generated.
* Lockfile stale: fail fast rather than scan stale data.

**Dependencies**

PAP-209 (hard: gate references tiers; draft acceptable). Soft: PAP-80, PAP-78, PAP-130. Blocks PAP-216 (license verification) and informs PAP-217.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) for CI. Reviewed by Sentinel (Security Auditor) and Atlas.

**Size**

M: two ecosystems, SPDX parsing and context derivation need care; the policy text is a day.
"""

DESCRIPTIONS["PAP-212"] = """**Goal**

Decide the headless component foundation for `packages/ui` by spiking Base UI, Radix Primitives, React Aria Components, Ark UI and the shadcn/ui distribution against PaperOS's real constraints (Tailwind v4, Tauri WebViews, detached windows, multi-input, WCAG 2.2 AA) and record an ADR. PAP-67 proceeds with Base UI by default if this is not merged by 2026-09-19, so this issue sits in the Evaluation process milestone and must land first.

**Scope**

In:

* `spikes/ui-kits/` with Select, Dialog, Menu and a virtualized 5k-option Combobox built in each candidate, styled with PAP-66 tokens if merged, else CSS variables.
* Scorecards per PAP-209 with extras: Tailwind v4 composability, controlled and uncontrolled APIs, portal behaviour in Tauri detached windows (PAP-24), RTL, touch and pen (PAP-150), roving focus and focus trap (PAP-152), date component availability, release stability.
* Measurements: gzipped bundle of the four components, axe results, keyboard walkthrough recording, render in webkit2gtk and Chromium.
* Quick rejects with one paragraph: Headless UI, Mantine, MUI, Chakra, Ant Design.
* ADR `docs/adr/NNNN-PAP-212-ui-primitives.md`; registry entries drafted.

Out: the 20 production components (PAP-67), icons (PAP-68), form library (follow-up recommendation only).

**Spec**

* Time-box 1 agent-day, 90 minutes per candidate; missing information is a rubric penalty, not more research.
* Versions: `@base-ui-components/react` 1.x, `radix-ui` unified, `react-aria-components` 1.x, `@ark-ui/react` 5.x, shadcn/ui CLI as a distribution.
* Harness: Vite app with a route per candidate and component; Playwright screenshots at 375, 768, 1280 in light and dark; `@axe-core/playwright`; `vite build --mode analyze` with visualizer JSON per route.
* Tauri check inside PAP-19's shell if merged, else a minimal Tauri 2 scaffold: open Dialog and Menu from a secondary window and confirm portals attach to the right document.
* The recommendation states which primitives the winner lacks (date picker) and their source (React Aria date components as fallback), plus migration hours to the runner-up.

**Interface contract**

Provides: ADR naming exact package and version, `spikes/ui-kits/results/*.json` (scorecards, bundle, axe), comparison table via `pnpm lib score`, a `docs/libraries/primitives-gaps.md` listing missing primitives and fallbacks, comments on PAP-67, PAP-152, PAP-150. Consumes: PAP-209 rubric (draft acceptable), PAP-66 tokens (soft), PAP-19 shell (soft), PAP-211 checker on the spike lockfile. Consumers: PAP-67 (hard, with the 09-19 default rule), PAP-233 pickers, PAP-152, PAP-150.

**Definition of done**

* Spike merged under `spikes/` (excluded from `turbo build`); results JSON and table committed.
* ADR accepted with scores, gates, rejects and re-open criteria; Iris and Atlas approval comments.
* Screenshots at 375, 768, 1280 for four components per candidate plus a 30-second keyboard video for the winner.
* PAP-67 description updated with exact package and version; registry entries drafted or a comment for Scout.
* CHANGELOG; Linear comment linking ADR and table.

**Test plan**

* Playwright per candidate route: open, keyboard traverse, close each component; axe zero serious; screenshots at three widths and two themes; Combobox scroll trace at 5k options.
* Tauri: secondary-window portal test recorded.
* Bundle: analyzer JSON per route; `pnpm lib score` validates scorecards.

**Demo**

Reviewer opens the ADR table, then runs `pnpm spike ui-kits --lib base-ui` and tabs through Select, Dialog, Menu and the 5k Combobox by keyboard in dark mode. Under two minutes.

**Edge cases**

* Base UI pre-1.0 at evaluation: stability scored down, API churn risk recorded.
* Candidate needs its own styling runtime: penalised, not excluded.
* Portal into the wrong Tauri window: hard gate unless a container prop exists.
* Combobox cannot virtualize: score a11y and performance separately; note TanStack Virtual effort.
* webkit2gtk rendering bugs: distinguish library from platform.

**Dependencies**

PAP-209 (hard; draft acceptable). Soft: PAP-66, PAP-19. Blocks PAP-67 (default Base UI after 2026-09-19); informs PAP-152, PAP-150, PAP-233.

**Agent**

Researched by Scout (Library Evaluator) paired with Iris (Component Crafter). Reviewed by Iris and Atlas.

**Size**

M: five spikes with measurements, tightly time-boxed to one day.
"""

DESCRIPTIONS["PAP-213"] = """**Goal**

Choose the data-heavy foundations: the table library the views engine renders with, the chart and map libraries dashboards and map views use, and a shortlist for canvas and rich text that PAP-127 decides in depth. Each choice is rubric-scored and recorded as an ADR so PAP-165, PAP-170 and PAP-132 build without re-litigating. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Table library** (M, 4 hours): TanStack Table v8 plus Virtual, AG Grid Community, Glide Data Grid, react-data-grid at 100k rows with inline edit, resize, frozen columns, grouping; extras for headless versus rendered, virtualization FPS, editing hooks, pinning, server-side pagination hooks for PAP-163, `role=grid` semantics per PAP-152, dnd-kit compatibility, touch; ADR. PAP-165 proceeds with TanStack Table v8 if this is not merged by 2026-09-21.
* **WP2 Charts and maps** (M, 4.5 hours): ECharts core path, visx, Recharts, Observable Plot, Nivo, Chart.js on a 10k-point line, stacked bar, pie and number tile with token theming; MapLibre GL with Protomaps PMTiles versus OpenFreeMap, Leaflet, on 5k clustered markers; two ADRs.
* **WP3 Canvas and editor shortlist** (S, 2 hours): tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate; facts-only pre-scores and license tiers; two candidates per category commented on PAP-127.

Out: building views (PAP-165, PAP-170), cell renderers (PAP-71), final canvas and editor ADR (PAP-127), sync engine (PAP-31).

**Spec**

* Harness: Vite app with a route per candidate under `spikes/data-libs/`; Playwright traces and screenshots at 375, 1024, 1920; results to `results/*.json`; `pnpm lib score` renders tables.
* Cross-links required to PAP-162 (NocoDB and Baserow features) and PAP-215 (embedding them); never repeat their analysis.
* Every ADR states the fallback candidate and migration hours; ties resolved by the rubric tie rule.
* Order WP1 -> WP2 -> WP3 on `PAP-213/wp<n>-<slug>`; total time-box 1.5 agent-days.

**Interface contract**

Provides: ADRs `table-library`, `chart-library`, `map-library` with exact packages and versions, `results/{tables,charts,maps,shortlist}.json`, registry drafts, comments on PAP-165, PAP-163, PAP-170, PAP-172, PAP-127 with the decisions. Consumes: PAP-209 rubric and `pnpm lib score` (draft acceptable), PAP-66 tokens (soft), PAP-211 tiers, PAP-162 and PAP-188 findings by link, PAP-82 screenshot stability requirements.

**Definition of done**

* Three work packages merged and reported.
* Integration check: grid winner at 55+ FPS scrolling 100k rows in a committed Playwright trace on the CI profile; chart winner renders 10k points under 200 ms; map spike clusters 5k markers with self-hosted tiles offline.
* Three ADRs accepted with Nova and Atlas approval comments; shortlist commented on PAP-127.
* Screenshots at 375, 1024, 1920 in light and dark for grid, charts and map.
* PAP-165 and PAP-170 descriptions updated; registry drafts; CHANGELOG; Linear comment linking ADRs and tables.

**Test plan**

* Playwright per candidate: scroll trace and FPS extraction, inline edit, resize, pin, group; chart render timing and three-run screenshot stability; map cluster and pan; axe with data-table fallback for charts.
* Bundle analysis per route committed.
* `pnpm lib score` validates every scorecard; a Vitest lint asserts the shortlist has two candidates per category.

**Demo**

Reviewer opens the table ADR and its comparison table, runs `pnpm spike tables --lib tanstack` to scroll 100k rows while editing a cell, then toggles dark mode on the chart route and sees the chart re-theme from tokens. Under two minutes.

**Edge cases**

* AG Grid Community lacks row grouping (Enterprise): documented gap, not assumed.
* Canvas-rendered grid defeats screen readers and DOM snapshots: a11y and testability scored down.
* ECharts full bundle: measure `echarts/core` only.
* Paid tile keys: prefer PMTiles; record ops cost.
* TanStack Table v9 alpha: evaluate v8 stable.
* Tie: migration-cost rule, no second spike.

**Dependencies**

PAP-209 (hard; draft acceptable). Soft: PAP-66, PAP-31, PAP-162, PAP-211. Blocks PAP-170 (map and chart views); informs PAP-165 (default TanStack after 2026-09-21), PAP-163, PAP-127, PAP-161.

**Agent**

Researched by Scout (Library Evaluator) paired with Nova (Views Engineer) for the grid and Iris for chart theming. Reviewed by Nova and Atlas.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-214"] = """**Goal**

Settle the server-side building blocks the plan has not decided, confirm the ones it has, and record everything as ADRs so Forge, Nova and Ledger stop choosing independently: jobs, email, PDF, search, observability, feature flags, object storage, validation and runtime are open; auth, ORM, sync, realtime and API layer are confirmed by cross-link. Everything must self-host in Docker on the Coolify VPS within a 6 GB service budget. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Jobs, email, PDF** (M, 4.5 hours): Inngest, Trigger.dev, BullMQ, pg-boss (incumbent named by PAP-43), Graphile Worker; Resend, Postmark, SES via Nodemailer, Postal; Playwright print, `@react-pdf/renderer`, Typst. Email ADR covers DKIM, SPF, DMARC and a sandbox mode with allowlist for agent sessions; PDF tested with CJK and RTL.
* **WP2 Search, observability, flags, storage** (M, 4.5 hours): Postgres `tsvector` plus pgvector baseline, ParadeDB, Meilisearch, Typesense; OpenTelemetry with Grafana LGTM, SigNoz, HyperDX; Unleash, Flagsmith, own table plus PAP-59 policies; MinIO, Garage, SeaweedFS; the resource budget table.
* **WP3 Validation, runtime, consolidation** (S, 2 hours): Zod 4 versus Valibot and ArkType; Node 22 versus Bun; cross-links to PAP-56, PAP-32, PAP-31, PAP-139, PAP-35; consolidated decision table, ADR index, registry drafts, license check.

Out: implementing anything (PAP-43, PAP-37, PAP-39, PAP-40, PAP-136, PAP-180), payroll and social APIs (own research).

**Spec**

* Measure with `docker stats` after a 5-minute warm-up under a scripted 50 req/s load where applicable, on the 16 GB profile from PAP-25.
* Rubric extras: self-host maturity, Postgres-native, RAM, TypeScript SDK, `docker compose up` story, tenant isolation, exit cost.
* Constraints: added RAM under 6 GB total; Redis only if two or more chosen services need it; Kubernetes-only rejected; Bun incompatibility with any chosen library defaults runtime to Node 22.
* Each ADR names the consuming issue, exact package or image tag, env vars for PAP-17, fallback and migration hours.
* Order WP1 -> WP2 -> WP3 on `PAP-214/wp<n>-<slug>`; total time-box 1.5 agent-days.

**Interface contract**

Provides: eleven ADRs (jobs, email, pdf, search, observability, flags, storage, validation, runtime, plus confirmation sections), `docs/libraries/backend-decisions.md` decision table, `docs/adr/backend-resource-budget.md` with measured numbers, winner compose files in `ops/compose/`, `results/backend-*.json`, a `@paperos/email` transport interface sketch (`send`, `sandbox`, `allowlist`) handed to data-layer, registry drafts, comments on PAP-43, PAP-37, PAP-39, PAP-40, PAP-57, PAP-136, PAP-180, PAP-191, PAP-17. Consumes: PAP-209 rubric (draft acceptable), PAP-211 tiers, PAP-25 profile, PAP-216 CLI when live.

**Definition of done**

* Three work packages merged and reported.
* Integration check: `compose-smoke` CI job starts every winner with `docker compose up --wait` and a health probe on a Forgejo or GitHub runner; budget table total under 6 GB with headroom stated.
* ADRs accepted with Forge and Atlas approvals; consuming issues commented; license check passes on chosen packages and images.
* Registry drafts exist for every winner; CHANGELOG; Linear comment with the decision table.

**Test plan**

* `compose-smoke` job per winner; losers removed or moved to `spikes/`.
* Budget table generated by script from `docker stats` JSON.
* `pnpm lib score` validates scorecards; Vitest smoke of Zod 4 versus the runner-up on 20 schemas; Bun compatibility script output committed; PDF fixture with CJK and RTL rendered and checked.

**Demo**

Reviewer opens `backend-decisions.md`, sees eleven rows each linking an accepted ADR with RAM and fallback, then runs `docker compose -f ops/compose/jobs.yml up` and enqueues the README sample job to completion. Under two minutes.

**Edge cases**

* License-gated self-hosting (Inngest, Trigger.dev tiers): self-host path only, tier verified.
* Service needs Redis or ClickHouse: counted against budget.
* PDF fonts missing in container: font bundle named.
* Email provider blocks unverified domains: sandbox mode; DNS steps as a Justin task.
* Flags covered by page-spec access rules: "no new service" recorded.
* MinIO is AGPL: `service` tier context recorded.

**Dependencies**

PAP-209 (hard; draft acceptable). Soft: PAP-56, PAP-31, PAP-139 (cross-link only), PAP-211, PAP-25, PAP-216. Blocks PAP-43; informs PAP-37, PAP-39, PAP-40, PAP-136, PAP-180, PAP-191.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) running measurements. Reviewed by Forge and Atlas.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-215"] = """**Goal**

Decide, product by product, whether PaperOS embeds, forks, borrows from or rejects whole open-source products overlapping planned systems: Twenty (CRM), NocoDB and Baserow (tables), Plane (PM), Cal.com (scheduling), Formbricks (forms), Postiz (social), plus Chatwoot (support) and Listmonk (campaigns) for PAP-197 and PAP-191. One ADR records a mode per product and hands it to the owning project. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Tables and PM products** (M, 6 hours): NocoDB, Baserow, Plane; compose spikes, seeded flows (table, relation, filter, kanban, API, webhook; issue, cycle, board, API), metrics, scorecards, provisional modes.
* **WP2 Growth products** (M, 8 hours): Twenty, Chatwoot, Listmonk, Postiz; flows (company, contact, deal, stage, API; inbox, assign, reply; list, campaign, template, bounce; mock provider, schedule, approval).
* **WP3 Cal.com, Formbricks and the ADR** (M, 4 hours plus writing): remaining spikes; ADR with per-product sections and mode matrix; `docs/registry/reference/<id>.md` with Mermaid data model for every `borrow`; embed contracts (SSO, API surface, tenant mapping, theming, export path, owner) for every `embed`; registry entries.

Out: integrating anything (growth, tables, pm-linear own that), library evaluation (siblings), re-deciding Linear as system of record.

**Spec**

* Modes: `embed` (separate service via API, SSO from Better Auth, theming; `service` license context), `fork` (vendor into monorepo; requires Justin, expected zero), `borrow` (study model and UX, reimplement on PAP-161), `reject`.
* Spikes under `spikes/oss-products/<id>/` with pinned images, `.env.example`, `README.md`, `metrics.json` (RAM idle and after flow, startup, export completeness), screenshots at 375 and 1280; a product not starting within 20 minutes on the reference profile is scored down and skipped.
* Expected licenses to verify: Twenty, NocoDB, Plane, Cal.com, Formbricks, Postiz, Listmonk AGPL-3.0 (some with `ee`); Baserow MIT core; Chatwoot MIT. AGPL forces `embed` or `borrow`.
* Rubric extras: license and tenancy tier, API completeness for our flows, SSO and embedding, data ownership and export, ops footprint, UX distance, upstream velocity and fork risk.
* Order WP1 and WP2 in parallel, then WP3, on `PAP-215/wp<n>-<slug>`; total time-box 2 agent-days.

**Interface contract**

Provides: ADR `docs/adr/NNNN-PAP-215-oss-products.md` with the nine-row matrix (product, license, tier, mode, RAM, owner, consuming issue), nine scorecards and `metrics.json`, borrow reference docs, embed contracts, registry entries (`adopted` for embed, `reference` for borrow, `rejected`), comments on PAP-188, PAP-187, PAP-197, PAP-190, PAP-162, PAP-100, PAP-161. Consumes: PAP-209 rubric, PAP-211 `service` tier, PAP-162 and PAP-188 findings by link, PAP-25 profile, PAP-216 CLI when live.

**Definition of done**

* Three work packages merged and reported.
* Integration check: all nine compose spikes start in the `compose-smoke` CI job; every product has a scorecard, metrics, screenshots and a mode in the matrix (Vitest lint).
* ADR accepted with Atlas, Nova and Beacon approvals; reference docs for every borrow; contracts for every embed; registry entries or drafts for all nine.
* Comments posted on the consuming issues; CHANGELOG; Linear comment with matrix and screenshot gallery.

**Test plan**

* `compose-smoke` per product with health probe.
* Playwright flow scripts per product saving screenshots at 375 and 1280.
* `pnpm lib score` validation; Vitest lint over the matrix; Mermaid diagrams render in the docs engine (screenshot).

**Demo**

Reviewer opens the ADR matrix, starts the NocoDB compose and opens the seeded kanban, then reads one borrow reference doc's data model diagram and one embed contract's SSO section. Under two minutes after images pull.

**Edge cases**

* Paid tier for SSO or API (`ee` folders): embed scored down with the exact gate.
* Product cannot trust an external session: proxy or downgrade to borrow.
* Per-instance tenancy: ops cost multiplies; usually reject for embed.
* UI-only export: data-ownership gate fails.
* Single-company upstream with license changes: fork risk raised.
* Images over 2 GB RAM (Cal.com, Twenty): weighed against the PAP-214 budget.

**Dependencies**

PAP-209 (hard). Soft: PAP-211, PAP-162, PAP-188 (cross-link), PAP-216. Informs PAP-188, PAP-187, PAP-197, PAP-190, PAP-100, PAP-161.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) for compose and metrics. Reviewed by Atlas, with Nova and Beacon as consumers.

**Size**

L umbrella; three M work packages. Pending sub-issue specs: {DOC}
"""

DESCRIPTIONS["PAP-216"] = """**Goal**

Give PaperOS one place that says what third-party code we use, why, who owns it and where the decision lives: a file-based registry rendered in-app through the docs engine, with a drift check so no dependency appears in a lockfile without an entry and no rejected library creeps back. This is the memory PAP-218, PAP-217 and every research ADR write into.

**Scope**

In:

* Entries `docs/registry/entries/<id>.yaml`, Zod 4 schema `packages/spec/src/libraries/registry.ts`, generated `docs/.generated/registry.json`.
* CLI `pnpm lib add <npm|crate:|image:> --status --owner --adr --category` scaffolding with facts from PAP-209's collector; `pnpm lib registry build|check`.
* Page `/_app/docs/registry` via PAP-128 (MDX plus a small React table): filters by status, category, owner; badges; ADR and scorecard links; "review due".
* Drift check job in Gate 1 (`generated-drift` pattern, PAP-78).
* Seed: every current production dependency as `adopted` with `adr: pending`, plus one Linear issue listing pending ADRs for Atlas.

Out: the ADR system (PAP-130), upgrades (PAP-217), scanning (PAP-218), rendering with the views engine (plain table; swap to PAP-165 later).

**Spec**

* Entry `{ id, name, source: { kind: npm|crate|image|service, ref }, version (from lockfile), status: candidate|trialing|adopted|reference|deprecated|replaced|rejected, category, owner, adr, scorecard, license (verified against PAP-211), context: bundled|server|dev|service (array allowed), usedBy[], alternativesConsidered[], reasons, addedAt, reviewAt, replacedBy?, aliases[], notes }`.
* Build reads `pnpm-lock.yaml` and `Cargo.lock` for `version` and `usedBy`; resolves `adr` against PAP-130's `adr-index.json`, failing on a dangling id, warning and skipping when the index is absent.
* Check rules: production dependency without `adopted` or `trialing` entry (error); `rejected|replaced|deprecated` present in a lockfile (error); `adopted` with no `usedBy` (warning); `reviewAt` past (warning); trivial helpers allowlisted in `docs/registry/trivial.yaml`.
* Transitions enforced by the CLI: `candidate` -> `trialing` -> `adopted` (needs accepted ADR) or `rejected`; `adopted` -> `deprecated` -> `replaced` with `replacedBy`.
* `reviewAt` defaults to `addedAt` plus 180 days; README documents statuses and cadence.

**Interface contract**

Provides: `RegistryEntrySchema`, `registry.json` `{ generatedAt, entries[], stats: { byStatus, byCategory } }`, CLI commands above, page route, Gate 1 job `registry-drift`, `trivial.yaml`. Consumes: PAP-209 `lib-facts` and scorecard paths, PAP-128 rendering, PAP-130 `adr-index.json` (soft), PAP-78 job slot, PAP-211 `policy.yaml` for license verification. Consumers: PAP-217 (`registry build` post-merge), PAP-218 (`lib add --status candidate`), PAP-79 third-party findings pointer, PAP-212 to PAP-215 entries.

**Definition of done**

* Schema, CLI, build and check merged; seed entries for all production dependencies committed; check passes on `main`; pending-ADR Linear issue exists.
* Drift check runs in Gate 1; a seeded unregistered dependency fails it (screenshot of the red status).
* Page screenshots at 375, 1024 and 1920 in light and dark; axe clean.
* `docs/registry/README.md` and `docs/libraries/registry.md`; CHANGELOG; Linear comment with page link.
* Entries exist for the ADR outputs of PAP-212 to PAP-215 where drafts exist.

**Test plan**

* Vitest: schema, pnpm and Cargo lockfile parsing fixtures, ADR resolution with and without index, every check rule with fixtures, transition enforcement, alias handling, multiple versions warning.
* CI: seeded violation branch fails `registry-drift`; clean `main` passes.
* Playwright: filter by status, open an entry, stacked cards at 375; visual baselines at 375, 1024, 1920 in both themes; axe.

**Demo**

Reviewer runs `pnpm lib add left-pad --status trialing --owner scout --category ui` and sees the scaffolded entry with facts filled, then `pnpm lib registry check` and opens `/_app/docs/registry` filtered to `trialing`. Under two minutes.

**Edge cases**

* Same library in `bundled` and `dev`: one entry, `context` array, strictest rule.
* Renamed or scoped package (`radix-ui` unifying `@radix-ui/*`): `aliases[]`.
* Multiple versions in lockfile: all listed; warning over two.
* `proposed` ADR: fine for `trialing`, error for `adopted`.
* `Cargo.lock` absent before Tauri: Rust checks skipped with notice.

**Dependencies**

PAP-209 and PAP-128 (hard). PAP-211 (license verification). Soft: PAP-130, PAP-78. Blocks PAP-218.

**Agent**

Built by Scout (Library Evaluator) with Quill for the docs page. Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Atlas.

**Size**

M: small schema and page; lockfile parsing, check rules and seeding touch every package.
"""

DESCRIPTIONS["PAP-217"] = """**Goal**

Keep dependencies current without burning attention: self-hosted Renovate opens grouped upgrade PRs on a schedule, every PR gets an agent-written summary of what changed and what it means for our code, safe upgrades merge themselves once gates pass, and risky ones become Linear work. Runs on both forges as a workflow, not the Mend app.

**Scope**

In:

* `renovate.json` at the template root plus shared preset `ops/renovate/default.json` other repos extend.
* `.github/workflows/renovate.yml` running the pinned `renovate/renovate` image with the Scout bot token from PAP-48; Forgejo platform setting for Forgejo Actions.
* `.github/workflows/upgrade-summary.yml` on Renovate PR open or update: spawns a Scout (Library Evaluator) session through PAP-96's headless entry to post the summary comment.
* Automerge tied to statuses `gate/1-static`, `gate/3-visual`, `licenses`, executed by Atlas's Merger sub-agent so PAP-46 rules hold.
* Dependency dashboard mirrored to a pinned Linear issue with a weekly burn line.

Out: vulnerability detection (PAP-80; consumed here), major framework migrations (normal issues), registry schema (PAP-216).

**Spec**

* Config: `extends: ["config:recommended", ":semanticCommits", ":pinAllExceptPeerDependencies"]`, `schedule: ["before 6am on monday"]`, `vulnerabilityAlerts` at any time, weekly `lockFileMaintenance`, `rangeStrategy: pin`, `commitBody: "Linear: PAP-<upgrades-epic>\\nCharacter: scout"`, labels `upgrade`, `upgrade:{{updateType}}`.
* Groups: `@tanstack/*`; UI primitives; editor and CRDT (`@tiptap/*`, `yjs`, `@hocuspocus/*`); Drizzle; test tooling; Biome; MCP servers from PAP-210; Tauri npm and cargo together; GitHub Actions; Docker tags in `ops/compose/`. Majors never grouped with minors.
* Automerge: devDependency patch and minor, dependency patch, with `automergeType: pr`, required statuses above and summary verdict `merge`. Minor dependencies and all majors need the verdict plus a Sentinel Code Reviewer pass (PAP-81).
* Summary comment (posted once, edited on update): packages and versions, release-note highlights, breaking changes found by grepping our code for removed APIs, bundle delta from PAP-87, license delta from `reports/licenses.json`, risk `low|medium|high`, verdict `merge|needs-work|hold`. `needs-work` on minors pushes a fix commit to the branch (`rebaseWhen: conflicted`); majors open a Backlog issue.
* Cost guard: 40 turns and the PAP-111 per-PR budget (default $3); over budget posts `hold`.
* Post-merge `pnpm lib registry build` updates versions.

**Interface contract**

Provides: preset `ops/renovate/default.json`, both workflows, `UpgradeSummary` schema `{ packages[], breaking[], bundleDelta, licenseDelta, risk, verdict }` posted as a sticky comment via PAP-78's action, labels `upgrade:*`, pinned Linear "Dependency dashboard" issue. Consumes: PAP-78 statuses and sticky-comment action, PAP-82 `gate/3-visual`, PAP-211 `licenses` status and report, PAP-87 perf report (soft), PAP-80 alerts (soft), PAP-48 bot token, PAP-50 runner, PAP-96 headless entry, PAP-111 budget, PAP-216 build, PAP-97 concurrency file-lock hints for `pnpm-lock.yaml`.

**Definition of done**

* Config, preset and both workflows merged; first scheduled run opens grouped PRs (screenshot).
* One patch PR automerges end to end with green statuses and a summary; one seeded major (old pin on a fixture branch) gets `hold` or `needs-work` and a Linear issue.
* Workflow verified on a Forgejo runner with the platform setting; link in the PR.
* `docs/libraries/upgrades.md` (groups, automerge rules, pausing); CHANGELOG; Linear comment.
* Sentinel Security Auditor confirms least-privilege token scopes.

**Test plan**

* Vitest: summary prompt fixture and mocked Claude response asserting the comment schema, verdict routing, branch push path, budget guard producing `hold`.
* Config: `renovate-config-validator` in Gate 1.
* Integration: seeded fixture branch with an old patch and an old major; observe automerge and hold paths on both forges.

**Demo**

Reviewer triggers `renovate.yml` by `workflow_dispatch` on a fixture branch pinning an old `vitest`, watches the grouped PR open, reads the summary comment with a `merge` verdict, and sees it automerge once statuses are green. Under two minutes after CI.

**Edge cases**

* Conflict with an agent PR on the lockfile: `rebaseWhen: conflicted`; lockfile shared in PAP-97.
* Missing or huge release notes: `package.json` diff and changelog headings, 2k tokens per package.
* Only Gate 3 visuals break: `needs-work` with diff links.
* Same package upgraded mid-week: Renovate rebases or closes as superseded.
* Bot token expires: loud failure on the dashboard issue.
* Release train (PAP-88): Monday upgrades, Friday RC.

**Dependencies**

PAP-78 (hard: required statuses), PAP-48 (hard: bot token). Soft: PAP-82, PAP-87, PAP-80, PAP-211, PAP-50, PAP-96, PAP-111, PAP-216, PAP-210 group.

**Agent**

Built by Scout (Library Evaluator) with Forge (Ops Runner) and Atlas (Merger). Reviewed by Sentinel (Security Auditor, Code Reviewer).

**Size**

M: config is quick; the summary workflow and automerge plumbing are the work.
"""

DESCRIPTIONS["PAP-218"] = """**Goal**

Make discovery continuous: every Monday the Scout character scans for libraries and products relevant to the issues open in Linear, pre-scores them with the rubric and license policy, records candidates in the registry and tells the owning issues, without noise or overspend. Discovery becomes a routine the org runs.

**Scope**

In:

* Skill `.claude/skills/scout-scan/SKILL.md` with `scripts/` (query builder, facts collector reuse, dedupe, report renderer) in the PAP-105 format.
* Workflow `.github/workflows/scout-scan.yml` (Monday 06:00 UTC, plus `workflow_dispatch`) asking PAP-96 to spawn Scout (Library Evaluator) with the skill.
* Report `docs/registry/scans/YYYY-MM-DD.md` rendered by PAP-128; `docs/registry/scans/seen.json` as dedupe memory.
* Linear actions: comments on relevant issues, up to three new Research issues per scan in Backlog, a pinned "Scout scans" issue updated each run.
* Watch list: adopted entries checked for license changes, archival or deprecation.
* Golden task for PAP-110.

Out: adoption decisions (research issues and ADRs), upgrades (PAP-217), the registry itself (PAP-216).

**Spec**

* Inputs: open Backlog and Ready for Claude issues labelled Build or Research (via `linear-update`), `registry.json`, `adr-index.json`, last three reports, `seen.json`.
* Queries: three to five per project, derived from titles and the project's category list; sources npm search, GitHub search (300+ stars, pushed within 12 months), WebSearch at 10 results per query; 60 candidates per run.
* Filtering: drop registry members unless a new major or status change; drop PAP-211 `block` tier; run `lib-facts` for a facts-only pre-score.
* Relevance: each candidate linked to issue keys with a one-sentence rationale, else dropped.
* Actions: `candidate` writes a registry entry via `pnpm lib add --status candidate`; `research` also creates a Backlog Research issue per PAP-93 with a scorecard stub; at most three per run; one comment per issue per run, none within 30 days of a prior mention; format from PAP-108.
* Budget: PAP-111 cap of $15 and 60 turns; on cap the report gets `partial: true` and leftovers become `deferred` in `seen.json`.
* Kill switch: `docs/registry/scout.paused` or the character budget switch.

**Interface contract**

Provides: skill and scripts (`buildQueries(issues, categories)`, `dedupe(candidates, seen)`, `preScore(facts)`, `renderReport(run)`), `ScanReport` schema `{ date, summary, byProject: [{ project, candidates: [{ name, version, license, preScore, linkedIssues, action }] }], watchAlerts, budget, partial }`, `seen.json` schema, the pinned issue, golden task. Consumes: PAP-216 `lib add` and `registry.json`, PAP-104 Scout definition, PAP-105 skill format and `linear-update`, PAP-96 spawn path, PAP-111 budgets, PAP-110 harness, PAP-93 issue template, PAP-211 tiers, PAP-209 `--facts-only`, PAP-108 comment format, PAP-129 logging.

**Definition of done**

* Skill, scripts, workflow, report template and golden task merged; `pnpm agents build` lists the skill for Scout only.
* One real `workflow_dispatch` run against team PAP with a `PAP-SANDBOX` label produced a report, a candidate entry and a comment; links in the PR.
* Golden task scored nightly at or above threshold; no fixture exceeds the action limits.
* Report page screenshots at 375 and 1280 in light and dark; CHANGELOG; comment on the pinned issue.
* Atlas approves action limits; Sentinel confirms Linear scopes are comment and create-in-Backlog only.

**Test plan**

* Vitest: query builder from fixture issues, dedupe against `seen.json` including the 30-day rule, pre-score computation, report rendering snapshot, action limits (three research issues, one comment per issue), partial-run carry-over, kill switch.
* Eval: frozen issue list and mocked search results produce the expected report shape and actions.
* Playwright: report page at 375 and 1280, both themes.

**Demo**

Reviewer dispatches `scout-scan.yml` with the sandbox label, opens the new `docs/registry/scans/<date>.md` page, then finds the registry entry it created and the comment on the linked issue. Under two minutes after the run.

**Edge cases**

* Project without open issues: skipped, noted.
* Search rate-limited or down: partial report, `deferred` list.
* Fork of an adopted library: marked `related`.
* Adopted library changes license: priority 1 Research issue regardless of the cap.
* Duplicate across projects: one entry, multiple linked issues.
* Orchestrator unavailable: visible failure, retry next week; no direct Claude call bypassing PAP-129.

**Dependencies**

PAP-216 and PAP-104 (hard). Soft: PAP-105, PAP-96, PAP-111, PAP-110, PAP-93, PAP-211, PAP-209, PAP-108.

**Agent**

Built by Scout (Library Evaluator) with Atlas (Dispatcher) for the orchestrator hook. Reviewed by Atlas and Sentinel (Security Auditor, Code Reviewer).

**Size**

M: a skill and scripts; the Linear action rules and eval fixture need care.
"""

for _k in list(DESCRIPTIONS):
    DESCRIPTIONS[_k] = DESCRIPTIONS[_k].replace("{DOC}", DOC)
