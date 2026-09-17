# Rewritten specs for tables PAP-168..PAP-174.
SPECS = {}
def add(k, **s): SPECS[k] = s

add("PAP-168",
Goal="""Add the three time-based views on one `TimeScale` engine: calendar (month, week, day, agenda), a zoomable timeline with lanes, and a Gantt with dependency arrows and critical path. Any dataset with a date field is scheduled by dragging; Gantt additionally reads a self-relation for dependencies. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/time/engine-calendar}} `TimeScale` engine, range compilation, overlap packing and the calendar view (month, week, day, agenda).
* {{tables/time/timeline}} Timeline: two-axis virtualised canvas, lanes, zoom levels, today marker, move and resize.
* {{tables/time/gantt}} Gantt: frozen left grid, dependency arrows, critical path, progress fill, working days.

Out: recurring events, external calendar sync, resource levelling.""",
Spec="""Decisions binding all children:

* `date-fns` 4.x with `@date-fns/tz`; all maths in the actor timezone; all-day values are calendar dates.
* Options `{ startField, endField?, allDay?, dependencyField?, milestoneField?, progressField?, laneField?, colorField?, workingDays, zoom: 'hour'|'day'|'week'|'month'|'quarter' }`.
* Fetch window is the visible range padded one period, compiled as `start <= rangeEnd AND coalesce(end, start) >= rangeStart` through PAP-163; page 500 with "n more" overflow chips.
* Edits write `startField`/`endField` optimistically through `mutate`, snapping to the zoom unit, ghost preview on drag.
* Every bar is a focusable button with `aria-label` "Title, from X to Y, lane Z"; arrows move, Shift+arrows resize; `LiveAnnouncer`; commands `time.*`.
* Under 768 px calendar defaults to agenda; timeline and Gantt hide the left grid.""",
Contract="""Provides: `<CalendarView />`, `<TimelineView />`, `<GanttView />`, `<DateRangeNav />`, `TimeScale` (`toX(date)`, `toDate(x)`, `ticks(zoom)`), `packOverlaps(events)`, `criticalPath(items, deps)`, `onFilter` (click a day or lane) for dashboards, PNG export. Consumes: range query (PAP-163), date, relation and number cells (PAP-164), grid cells for the left pane (PAP-165), drag (PAP-155), pinch zoom (PAP-156). Consumed by PAP-190 social calendar (list fallback until Done), PAP-102 timeline.""",
DoD="""* All three children Done.
* Storybook stories per view; screenshots at 375, 768, 1024, 1440, 1920 in three themes; Gantt drag replay at 1024 and 1920; axe clean; keyboard-only rescheduling works.
* `docs/views/time-views.md` with the options table; CHANGELOG; Linear comment with demo link.""",
Test="""Umbrella `time-views.e2e.spec.ts` on a 2,000-item seed: switch calendar month to week to agenda and assert the same record appears in each; drag an event across a DST boundary in `America/Los_Angeles` and `Europe/Berlin` and assert the stored instant; resize on the timeline at day and week zoom; add a dependency in Gantt, shift the predecessor, accept "shift dependents", assert critical path highlight changes; reject a cycle. Unit fixtures shared by all three children live in `packages/views/test/time/fixtures.ts`.""",
Demo="""Reviewer opens `/demo/calendar`, drags an event to next week, switches to the timeline and zooms with Ctrl+wheel, then opens the Gantt and draws a dependency between two bars, watching the critical path re-colour. Under two minutes.""",
Edge="""* End before start after resize: clamp to zero duration and warn.
* Multi-month events render as spans with continuation arrows.
* Dependency cycles rejected on create; imported cycles render dashed red.
* 10,000 items in one lane keep 60 fps; labels hidden under 40 px bars.
* Missing `endField`: one-unit bars, resize disabled.""",
Deps="""PAP-163 (hard), PAP-164 (hard), PAP-165 (Gantt left grid), PAP-155 (drag), PAP-156 (pinch, soft). Blocks nothing hard; PAP-190 prefers it.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter for date maths, Visual Inspector).""",
Size="""L, split into three M children; land the calendar child first.""")

add("PAP-169",
Goal="""Ship the three presentation views: gallery (card grid with covers), list (dense vertical feed for phones and sidebars) and form (a data-entry view that creates records, optionally public). Together they cover directories, feeds and intake without custom pages.""",
Scope="""In: `packages/views/src/views/gallery/`, `views/list/`, `views/form/`; form runtime and builder panel; public route `/f/:token` (tokens from PAP-172; internal-only until then); `forms.submit` procedure.

Out: payments in forms, multi-page forms, file limits beyond PAP-37 defaults.""",
Spec="""* Gallery options `{ coverField?, coverFit, cardSize: 'sm'|'md'|'lg', cardFields, titleField?, showEmptyFields }`; `repeat(auto-fill, minmax(200|280|360px, 1fr))`, virtualised rows, cover from an attachment's `variants.md` or a URL field; click opens `RecordPanel`.
* List options `{ titleField, subtitleField?, metaFields, avatarField?, dense }`; rows 56 or 72 px; grouped headers; two configurable swipe actions (PAP-156); works at 320 px.
* `FormSpec = { fields: { fieldId, label?, help?, required, placeholder?, hiddenWhen?: FilterTree, prefillParam? }[], title, description, submitLabel, successMessage, redirectUrl?, allowMultiple, honeypot: true, captcha?: 'turnstile' }` in `spec.options`.
* Rendering: one editor per row in form mode; validation on blur and submit via `validateRecord`; draft saved per form id in `localStorage`; Markdown via `marked` sanitised.
* `forms.submit({ token, values, honeypot })`: validates token (public, kind form), 30 per minute per IP, strips unknown and hidden fields, honeypot and optional Turnstile, creates as service principal `form-submitter` with `audit_event.reason = 'form:<viewId>'`.
* `hiddenWhen` evaluated client and server side; hidden required fields are not required.
* Public page uses tenant branding (PAP-74); PaperOS footer unless entitlement `whiteLabel` (PAP-178).""",
Contract="""Provides: `<GalleryView />`, `<ListView />`, `<FormView />`, `<FormBuilder />`, `FormSpec`, procedure `forms.submit`, event `form.submitted { viewId, recordId, values }` consumed by PAP-174 triggers and PAP-193, route `/f/:token`. Consumes: query (PAP-163), editors and `validateRecord` (PAP-164), `RecordPanel` (PAP-165), file variants (PAP-37), theming (PAP-74), swipe (PAP-156), drag reorder (PAP-155), share tokens (PAP-172), `FilterTree` in-memory evaluator (PAP-279), rate limiting (PAP-267).""",
DoD="""* Vitest, integration and Playwright below green.
* Storybook stories for three views and the builder; screenshots at 375, 768, 1024, 1440, 1920 in three themes; public form with two tenant brands; axe clean with label and error associations verified.
* `docs/views/gallery-list-form.md`; CHANGELOG; Linear comment with a live public form on the demo tenant.""",
Test="""* Unit: form validation, `hiddenWhen` logic, prefill parsing, honeypot, idempotency key, Markdown sanitisation.
* Integration: `forms.submit` with a valid, expired, revoked and non-form token; hidden-field injection stripped; rate limit trips at 31; record created under `form-submitter` with the audit reason.
* E2E: gallery scroll and open record; list swipe action under touch emulation; form fill with two errors then success; public submission from a fresh browser context; RTL locale layout.
* Visual: matrix above.""",
Demo="""Reviewer opens `/demo/gallery`, switches the same dataset to list, then to a form, fills it with one invalid email, fixes it, submits, and sees the new card appear in the gallery. Under two minutes.""",
Edge="""* Missing or failed cover: placeholder illustration (PAP-72).
* Relation field on a public form: hidden unless the submitter principal may read targets; builder warns.
* Unpublished form: 410 with a friendly page.
* 50 MB upload: rejected by PAP-37 limits with a clear message.
* Double-click submit: idempotency key per draft.""",
Deps="""PAP-163 (hard), PAP-164 (hard), PAP-165 (`RecordPanel`), PAP-37, PAP-74, PAP-156, PAP-155, PAP-172 (public tokens, soft). Feeds PAP-174, PAP-193.""",
Agent="""Builder: Nova (Views Engineer); Iris on card and form styling. Reviewer: Sentinel (Security Auditor for the public endpoint, Visual Inspector).""",
Size="""M: gallery and list are thin over cells; the form runtime is the substance.""")

add("PAP-170",
Goal="""Add the two analytic views: a map plotting records with coordinates on vector tiles and a chart view (bar, stacked bar, line, area, pie, donut, number) bound to compiler groups and aggregates. Both are the blocks PAP-173 arranges and must be data-driven and cross-filter aware from day one.""",
Scope="""In: `packages/views/src/views/map/`, `views/chart/`, the `geo` field type `{ lat, lng, label? }` registered in PAP-164, chart and map options, `onFilter` emission, PNG and CSV export.

Out: geocoding, choropleths, custom tile hosting, drill-through beyond one level.""",
Spec="""* Chart options `{ chartType, xField, seriesField?, yAggregate: { fieldId?, fn }, bucket?: 'day'|'week'|'month'|'quarter'|'year', sortBy, limit (default 20, remainder "Other"), colorScheme, showLegend, showDataLabels, goal? }`; map options `{ geoField, labelField?, colorField?, cluster, fitToData, basemap: 'light'|'dark'|'auto' }`.
* ECharts 5.x via `echarts/core` with only the needed renderers; chart chunk under 250 KB gzip; theme built at runtime from tokens using the dataviz palette mapped onto `--pos-color-*`, regenerated on theme change.
* Data from `views.groups` (one or two levels); number chart from `views.query` aggregates with previous-period comparison when `xField` is a date bucket; axes and tooltips format through the field type `format`.
* Click emits `onFilter({ fieldId: xField, op: 'is', value })`; active element highlighted; legend toggles series; keyboard: Tab to chart, arrows across categories, Enter filters; "View as table" fallback.
* MapLibre GL JS 4.x, OpenFreeMap `liberty` style with a hook for self-hosted PMTiles; bounding-box filter compiled on `geo` casts with btree indexes; `cluster: true`; Shift+drag rectangle emits `isWithin` bounds.
* Export: `getDataURL` and MapLibre canvas PNG; CSV of aggregated rows.""",
Contract="""Provides: `<ChartView spec datasetRef onFilter activeFilter? />`, `<MapView />`, `buildSeries(groups, options)`, `buildEchartsTheme(tokens)`, `geo` field type, `FilterCondition` emission contract shared with PAP-173 and PAP-186. Consumes: groups and aggregates (PAP-163), `format` and field registry (PAP-164), tokens and theming (PAP-66, PAP-74), `EmptyState` (PAP-71), ECharts choice confirmed by PAP-213 ADR.""",
DoD="""* Vitest, Playwright and bundle check below green; WebGL enabled in the Playwright image.
* Storybook stories per chart type and the map; screenshots at 375, 768, 1024, 1440, 1920 in light, dark and high-contrast; palette contrast validated with the dataviz checker.
* `docs/views/map-chart.md`; CHANGELOG; Linear comment with demo link.""",
Test="""* Unit: series shaping for one and two levels, "Other" bucketing, zero-fill of date gaps, period comparison, bounds-filter compilation, per-currency series split.
* Integration: chart bound to a 50k-row seed renders from `views.groups` within 500 ms server time; map bounds query uses the btree index (`EXPLAIN`).
* E2E: click a bar and assert the emitted condition; legend toggle; cluster click zoom; rectangle select; keyboard category navigation; "View as table" shows identical totals.
* Bundle: `size-limit` chart chunk under 250 KB gzip; map chunk lazy.
* Visual: matrix above.""",
Demo="""Reviewer opens `/demo/chart`, switches bar to stacked bar by owner, clicks a bar and sees the emitted filter chip, toggles "View as table", then opens `/demo/map`, clicks a cluster and Shift-drags a rectangle. Under two minutes.""",
Edge="""* 10,000 points cluster; above 50,000 the view asks for a filter first.
* Negative values in a pie: refused with a bar suggestion.
* Mixed currencies: one series per currency.
* No WebGL (kiosks): static coordinate list with explanation.
* Colour-blind users: patterns in high-contrast, legend always textual.""",
Deps="""PAP-163 (hard), PAP-164 (hard for `geo`), PAP-66, PAP-74, PAP-213 (ADR, soft). Blocks PAP-173, and through it PAP-186.""",
Agent="""Builder: Nova (Views Engineer) with Iris (dataviz plugin) on palette. Reviewer: Sentinel (Visual Inspector, Code Reviewer).""",
Size="""M: mature libraries; the work is binding, theming and interaction.""")

add("PAP-171",
Goal="""Build the formula engine so `formula` fields compute values users already know how to write: Airtable and Notion compatible syntax, static type checking, a TypeScript evaluator for editors and previews, and SQL compilation for the subset that can run inside PAP-163 so formulas filter, sort and aggregate server-side. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/formula/parser-typecheck}} Lexer, Pratt parser, AST, type checker, `defineFunction` metadata and the function catalogue from `formula-functions.csv`.
* {{tables/formula/evaluator-editor}} TypeScript evaluator with all function implementations, CodeMirror 6 editor with autocomplete, signature help and live preview.
* {{tables/formula/sql-cache}} SQL compiler, `formula_cache` fallback job, dependency graph and cycle detection.

Out: cell-level spreadsheet formulas, user-defined functions, cross-dataset references except through relations.""",
Spec="""Decisions binding all children:

* Grammar: `IF({Status} = "Done", 1, 0)`, `{Field}` references, `&`, arithmetic, comparisons, `AND/OR/NOT` and `&&/||/!`, string escapes, `//` comments; references rewritten to `@fld_<id>` at save so renames are safe.
* Types `text | number | boolean | date | array<T> | null | error`; coercions only number to text in `&` and parseable text to number in arithmetic; diagnostics carry positions.
* `defineFunction({ name, aliases, params, returns, ts, sql?, pure, volatile? })`; `NOW()` and `TODAY()` volatile, excluded from indexes; date functions take the actor timezone from context.
* `compile(ast) => SQL | Unsupported`; unsupported formulas materialise into `record.formula_cache jsonb` refreshed in batches of 500 by a PAP-43 job when dependencies change.
* Errors render `#ERROR` with hover detail; division by zero is an error; `IFERROR` supported.""",
Contract="""Provides: `parse(src) => AST`, `checkType(ast, fields) => { resultType, diagnostics }`, `evaluate(ast, record, ctx)`, `compile(ast) => SQL | Unsupported`, `functions` metadata, `<FormulaEditor field fields sampleRecord />`, `dependencyGraph(dataset)`. Consumes: field types and `formula` storage type (PAP-164), compiler integration point `compiler/ops/formula.ts` (PAP-163), function inventory (PAP-162), jobs (PAP-43), CodeMirror from the libraries registry. Consumed by PAP-169 conditional logic and PAP-174 template expressions (shared expression subset).""",
DoD="""* All three children Done.
* Function coverage: at least 80 functions; every SQL-capable function has a TS versus SQL parity test on a 1,000-record fixture.
* Storybook editor story; screenshots at 375, 1024, 1920 in three themes.
* `docs/views/formulas.md` generated from metadata; parity CSV row updated; CHANGELOG; Linear comment with coverage count and the unsupported-in-SQL list.""",
Test="""Umbrella `formula.e2e.test.ts`: 200-expression golden corpus parsed, type-checked and evaluated against Airtable-documented answers; for each SQL-capable function run the formula through `views.query` filter and sort and compare with `evaluate`; edit a formula that depends on a lookup and assert `formula_cache` refresh within one job cycle; `fast-check` fuzz for parser crash-freedom (10k cases); Playwright: type a formula with autocomplete, see a diagnostic, fix it, see the preview.""",
Demo="""Reviewer adds a formula field `IF({Amount} > 1000, "Big", "Small") & " deal"` in the editor with autocomplete, sees the live preview on a sample row, saves, and filters the grid by the formula result server-side. Under two minutes.""",
Edge="""* Deleted field reference: `#REF` with a fix-it action.
* `LEN` and `MID` count code points, matching Airtable.
* Date arithmetic across DST uses timezone-aware functions.
* Nesting depth limited to 200 with a clear error.
* `TODAY()` in a public view uses the tenant timezone.""",
Deps="""PAP-164 (hard), PAP-163 (hard), PAP-162 (hard, inventory), PAP-43 (cache job). Soft consumer: PAP-174.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Edge Case Hunter with adversarial expressions, Security Auditor on SQL compilation).""",
Size="""L, split into three M children; ship the TS evaluator behind a flag first.""")

add("PAP-172",
Goal="""Make views first-class permissioned objects: personal versus shared views, per-audience defaults per dataset, public read-only links and embeds with expiry and password, view locking, and a switcher listing what the actor may see. This is what lets customers, staff and partners each experience the same dataset differently.""",
Scope="""In: tables `view_share`, `view_default`; procedures `views.list|create|update|duplicate|delete|reorder|share|revoke|setDefault|resolveDefault|publicQuery`; `ViewSwitcher`, `ShareViewDialog`, `ViewSettingsSheet`; routes `/v/:token` and `/embed/v/:token`; permission actions `view.read|update|delete|share|lock`.

Out: per-field permissions on entity datasets (PAP-59 and specs), comments on public views.""",
Spec="""* `visibility`: `personal` (owner only), `shared` (workspace policies), `public` (token). New views are personal; sharing requires `view.share`.
* `view_default (tenant_id, dataset_ref, audience_id, view_id)`; `resolveDefault(datasetRef, actor)` picks the most specific audience match (PAP-62), else first shared view, else a fresh personal grid; `page.spec.yaml` may pin `views.default`.
* `view_share`: `id, view_id, token (32-byte base64url, indexed), kind: 'link'|'embed', password_hash?, expires_at?, allow_export, allowed_fields jsonb, created_by, revoked_at, view_count, last_viewed_at`; token shown once.
* Public path runs as service principal `public-viewer` with `tenantId` from the share; `views.publicQuery({ token, cursor })` reuses PAP-163 with `allowed_fields` projection and `canEditRecords = []`; 120 per minute per IP and 10k per day per token; `argon2` password sets a signed 24 h cookie; `frame-ancestors` from the tenant allowlist only on `/embed/*`.
* `locked` blocks spec changes except for `view.lock` holders; temporary URL filters still work.
* Switcher groups "Your views / Shared / Public", search, drag reorder, `Ctrl+Shift+V`; commands `view.switch|new|duplicate`.
* Public view count is entitlement `publicViews` (PAP-178); creation goes through `assertWithinLimit`.""",
Contract="""Provides: the procedures above, `<ViewSwitcher datasetRef />`, `<ShareViewDialog viewId />`, `resolveDefault`, `PublicViewPage`, embed snippet `<iframe src=".../embed/v/{token}?theme=">`, audit events `view.share.created|revoked`, `view.default.changed`, `view.public.password_failed`. Consumes: `can()` and `useCan` (PAP-227, PAP-229), audiences (PAP-62), audit (PAP-38), theming (PAP-74), entitlements (PAP-178), compiler (PAP-163), `GridView` embedded mode (PAP-165), rate limiting (PAP-267). Consumed by PAP-169 public forms, PAP-173 dashboard visibility, PAP-183 saved reports, PAP-189 per-audience CRM defaults.""",
DoD="""* Vitest and integration below green; permission matrix generated via PAP-63 for the five actions.
* Storybook stories for switcher and dialog; screenshots at 375, 768, 1024, 1440, 1920 in three themes; embed page at 320 and 1024.
* `docs/views/sharing.md` with a security note; CHANGELOG; Linear comment with a live public view link.""",
Test="""* Unit: default-resolution precedence (specific audience beats general beats first shared); share validation; token generation entropy.
* Integration: valid, expired, revoked, wrong-password and field-stripping cases through `publicQuery`; 121st request in a minute rejected; public view on an RLS entity returns zero rows without an explicit allow policy; entitlement limit enforced under 20 parallel creates.
* E2E: create a share, open `/v/:token` in a fresh context, confirm the hidden field is absent, revoke and see 410; embed in a test page with and without an allowed origin.
* Visual: matrix above.""",
Demo="""Reviewer shares the grid demo publicly with a password and a hidden field, opens the link in a private window, enters the password, confirms the field is missing, then revokes and reloads to a 410 page. Under two minutes.""",
Edge="""* Owner leaves the tenant: personal views deleted, shared views transferred to the workspace owner.
* Public view on an RLS entity: dialog warns "will show 0 records" from a preview count.
* Two audiences match: most specific wins, ties by `position`.
* Embed on a non-allowlisted site: blank via CSP, documented.
* Export on a public view: CSV capped at 10k rows and rate-limited.""",
Deps="""PAP-165 (hard), PAP-59 children (hard), PAP-62, PAP-38, PAP-74, PAP-178 (soft, limit). Blocks PAP-173 (visibility), feeds PAP-169, PAP-183, PAP-189.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor primary, Code Reviewer).""",
Size="""M: clear data model; the care goes into the public path.""")

add("PAP-173",
Goal="""Compose views into dashboard pages: a responsive 12-column grid of drag-arranged blocks (any view kind, KPI numbers, text, filter controls) with cross-filtering, so a click on a chart bar filters the grid beside it. PAP-186 and PAP-102 build on it. Umbrella for three children.""",
Scope="""Children (same milestone, Backlog):

* {{tables/dashboard/model-grid}} (M) Tables, layout engine, breakpoint layouts, drag and resize with keyboard moves.
* {{tables/dashboard/blocks-crossfilter}} (M) Block kinds (`view`, `number`, `text`, `filter`, `divider`), cross-filter bus, filter bar, params and deep links.
* {{tables/dashboard/print-perf-spec}} (S) Lazy loading and error boundaries, print route `/print/d/:id`, `layout.dashboard` page-spec hook, permission tiles.

Out: scheduled email snapshots, per-block permissions beyond view inheritance, templates marketplace.""",
Spec="""Decisions binding all children:

* `dashboard (id, tenant_id, workspace_id, name, description, layout jsonb per breakpoint, params jsonb, visibility, owner_user_id, refresh_seconds?, position)`; `dashboard_block (id, dashboard_id, kind, view_id?, spec_override jsonb, title, config jsonb, x, y, w, h, min_w, min_h)`.
* Grid: 12 columns at `lg >= 1280`, 8 at `md >= 768`, 1 at `sm`; row height 40 px; `sm` auto-derived from `y` unless customised; collisions push down.
* Blocks render views in `embedded` mode with `spec_override` merged over the saved spec.
* `DashboardFilterContext = { global: FilterTree, byBlock: Record<blockId, FilterCondition[]> }`; blocks merge conditions whose field key exists or is mapped in `config.fieldMap`; `config.ignoreCrossFilter` opts out; chips in the header bar.
* Params typed (date range, tenant-scoped picker) and mirrored in `?p.<name>=`.
* Budget: 12-block dashboard settles under 2 s on the seed tenant; each block has its own error boundary and skeleton.""",
Contract="""Provides: `<Dashboard id />`, `<DashboardEditor />`, `<Block />`, `<NumberBlock />`, `<TextBlock />`, `<FilterBarBlock />`, `defineNumberBlock({ key, query, format })` registry used by PAP-183 and PAP-186, `useDashboardFilters()`, procedures `dashboards.*`, `dashboardBlocks.*`, print route, `layout.dashboard` in `page.spec.yaml` (PAP-120). Consumes: `onFilter` from charts, map, kanban and grid group headers (PAP-170, PAP-167, PAP-165), `FilterTree` (PAP-279), drag (PAP-155), visibility (PAP-172), ECharts sparkline (PAP-170), Playwright print (PAP-82 image).""",
DoD="""* All three children Done.
* Permission tests: a viewer without access to one view sees a "No access" tile, others render.
* Screenshots of a six-block demo at 375, 768, 1024, 1440, 1920 in three themes; cross-filter replay; performance trace under 2 s.
* `docs/views/dashboards.md`; CHANGELOG; Linear comment with the demo dashboard link.""",
Test="""Umbrella `dashboard.e2e.spec.ts`: build a six-block dashboard (chart, grid, number, filter bar, text, map) via the editor; click a chart bar and assert the grid's row count and the header chip; clear the chip; set the global date range and assert both charts refetch; move a block with keyboard and assert `layout.lg`; resize the viewport to 700 px and assert single-column order; print `/print/d/:id` to PDF and assert page count; measure settle time on the seed tenant.""",
Demo="""Reviewer opens `/demo/dashboard`, clicks a bar in the chart, watches the grid filter and a chip appear, drags the chart wider, opens fullscreen on the number block, then prints to PDF. Under two minutes.""",
Edge="""* Referenced view deleted: "View removed" tile with replace action.
* Cross-filter type mismatch across datasets: ignored with a tooltip.
* 40 blocks: lazy loading and a warning at 30.
* Two filter blocks on one field: last change wins, both display it.
* Print with a map block: static image, list fallback without WebGL.""",
Deps="""PAP-170 (hard), PAP-165 (hard), PAP-155 (hard), PAP-172 (hard, visibility), PAP-120 (page-spec hook, soft), PAP-279. Blocks PAP-186.""",
Agent="""Builder: Nova (Views Engineer). Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris on block chrome.""",
Size="""L, split into two M children and one S child.""")

add("PAP-174",
Goal="""Give every table Airtable, Notion and ClickUp class automations without code: triggers (record change, enters view, schedule, form, webhook, button), conditions from the shared filter builder, and actions (update or create records, notify, outbound webhook, connector call, scoped agent task, delay, branch) with a run log. This is how business templates encode their own workflows. Umbrella for three children.""",
Scope="""Children (M each, same milestone, Backlog):

* {{tables/automations/model-triggers}} Schema, trigger sources, run runtime on PAP-43 jobs with idempotency, loop guard, daily limits and circuit breaker.
* {{tables/automations/actions}} Action catalogue with scope classes, template expressions, `connector.call`, `agent.run`, `delay`, `branch`, signed `webhook.send`.
* {{tables/automations/builder-log-templates}} Builder page from `automations.page.spec.yaml`, test run, run log grid with replay, five starter templates, import hooks.

Out: workflow canvas editing, arbitrary code actions, cross-tenant automations.""",
Spec="""Decisions binding all children:

* `automation (tenant_id, name, enabled, trigger jsonb, conditions jsonb: FilterTree, actions jsonb[], owner_id, run_limit_per_day)`; `automation_run (status, trigger_payload, steps jsonb, error, duration_ms, cost_units)`.
* Record triggers come from `LISTEN/NOTIFY` emitted by PAP-38 audit triggers, debounced 500 ms per record; `record.entersView` diffs membership through PAP-163; schedules run in the tenant timezone; webhook URLs carry an HMAC secret with replay protection.
* Runs are `automations.run` jobs idempotent per `(automation_id, trigger_event_id)`; loop guard allows one self-retrigger then stops (`loop_guard`), chaining depth opt-in up to 3; circuit breaker after 20 consecutive failures.
* Every action declares `read|write|destructive`; destructive actions need admin enablement and are excluded from templates.
* Template expressions `{{record.field}}`, `{{trigger.*}}`, `{{now}}` share the PAP-171 expression subset.
* Run log retained 90 days and mirrored to audit with `actor_kind = 'automation'`.""",
Contract="""Provides: `defineTrigger`, `defineAction({ key, scope, schema, run })`, procedures `automations.*`, `automationRuns.*`, event `automation.run.finished`, `button` field type (registered into PAP-164), webhook route `/api/automations/:id/webhook`, starter templates JSON consumed by PAP-208. Consumes: `FilterBuilder` and `FilterTree` (PAP-166, PAP-279), jobs (PAP-43), audit NOTIFY (PAP-38), connector registry (PAP-121), notifications (PAP-136 or its core), handoffs (PAP-108), `form.submitted` (PAP-169), signed outbound webhooks helper (PAP-222).""",
DoD="""* All three children Done.
* Parity matrix in `docs/tables/automations.md` against the PAP-162 trigger and action lists.
* Builder keyboard-operable (PAP-158 checklist); screenshots at 375 and 1280 in three themes; page spec merged.
* CHANGELOG; Linear comment with demo video.""",
Test="""Umbrella `automations.e2e.spec.ts`: create "when Status becomes Done, notify owner and POST webhook" in the builder; test-run with a sample record; edit a grid cell and assert one run with two successful steps within 5 s; replay a webhook payload and assert rejection; fire a schedule across a DST boundary with a fixed clock; create a self-updating automation and assert `loop_guard`; fail a webhook 20 times and assert the breaker; import 1,000 rows with automations paused and assert zero runs.""",
Demo="""Reviewer opens the automation builder, picks a trigger, adds a condition with the filter builder and two actions, presses "Test run" on a sample record, then edits that record in the grid and watches the run log fill in. Under two minutes.""",
Edge="""* Trigger table deleted: automation disabled with a visible reason.
* Notify target removed from tenant: step skipped with warning, run continues.
* Webhook target 5xx for an hour: job retry schedule, then failed step with resend.
* Missing tenant timezone: UTC with a banner.
* Offline edits synced later: triggers fire at server apply time; log shows both timestamps.""",
Deps="""PAP-166 (hard), PAP-43 (hard), PAP-38 (hard, NOTIFY source), PAP-121 (hard, connectors), PAP-279. Soft: PAP-136, PAP-171, PAP-169, PAP-155, PAP-108, PAP-222. Consumed by PAP-208, PAP-195, PAP-180 and {{gap/business-core/recurring-dunning}}.""",
Agent="""Builder: Nova (Views Engineer) with Forge on LISTEN/NOTIFY. Reviewer: Sentinel (Security Auditor for webhooks and scopes, Edge Case Hunter for loops and limits).""",
Size="""L, split into three M children; start after the grid and filter builder are stable.""")
