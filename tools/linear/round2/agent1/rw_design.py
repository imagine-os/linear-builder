DESCRIPTIONS = {}

DESCRIPTIONS["PAP-66"] = """**Goal**

Create the single source of truth for every visual decision: colour, typography, spacing, radius, motion and elevation tokens in W3C DTCG JSON, compiled by Style Dictionary into CSS custom properties, a Tailwind v4 `@theme` and a typed TypeScript export. Every component and every generated page consumes these variables and nothing else.

**Scope**

* In: `packages/ui/tokens/` (`core.tokens.json`, `semantic.tokens.json`, `themes/{light,dark,hc}.tokens.json`), Style Dictionary 4.x build emitting `tokens.css`, `theme.css` and `tokens.ts`, OKLCH ramps generated with `culori`, contrast check, token lint, the Tokens docs story, ADR.
* Out: components (PAP-67), runtime per-tenant override (PAP-75), Figma export (PAP-77), motion component wrappers (PAP-72; the motion tokens are defined here).

**Spec**

* DTCG: `{"color":{"accent":{"500":{"$type":"color","$value":"oklch(60% 0.18 260)"}}}}`, aliases `{color.accent.500}`; 11-step ramps 50-950 for neutral, accent, success, warning, danger, info.
* Semantic layer: `color.bg.{canvas,surface,raised,overlay}`, `color.fg.{default,muted,subtle,onAccent}`, `color.border.{default,strong,focus}`, `color.accent.{default,hover,active}`, `color.{success,warning,danger,info}.{bg,fg,border}`, `color.focus`.
* Type: `xs` 12 to `4xl` 36 with `clamp()` display sizes; line heights, weights; Inter Variable and JetBrains Mono. Space on 4 px (`0`-`96`), radius `none` to `full`, `shadow.1`-`shadow.5` with dark variants, `duration.{instant,fast,base,slow,deliberate}` = 0/120/200/320/480 ms, `ease.{standard,enter,exit,spring}`.
* Build `pnpm --filter ui tokens:build`: config `style-dictionary.config.ts` with transforms `color/oklch-css`, `size/px-to-rem`, format `css/tailwind-theme`; CSS variables prefixed `--pos-` (`--pos-color-bg-surface`); `:root` and `[data-theme=...]` blocks; sRGB fallbacks under `@supports not (color: oklch(0% 0 0))`; Tailwind default palette disabled with `--color-*: initial`.
* `tokens.ts` exports `tokens.color.bg.surface` as `var(--pos-color-bg-surface)` and `rawTokens` with resolved values per theme; `TokenPath` union.
* `tokens:check` asserts `fg.default` on every `bg.*` at 4.5:1 and `fg.muted` at 3:1 in all three themes; `tokens:lint` enforces kebab names, resolvable aliases, no unused aliases, no cycles.

**Interface contract**

* Provides: `@paperos/ui/styles/tokens.css`, `@paperos/ui/styles/theme.css`, `tokens`, `rawTokens`, `TokenPath`, the semantic token names above (stable API), `data-theme` attribute contract (`light | dark | hc`; attribute wins over `prefers-color-scheme`), `--pos-` prefix, `ops/ci` drift check command.
* Consumers: PAP-67 and all components, PAP-72 motion presets, PAP-75 theming (overrides the same variable names), PAP-18 `theme_color`, PAP-77, PAP-235 print defaults, PAP-89 digest HTML, PAP-82 theme fixture.
* Requires: `packages/ui` folder from PAP-13 (create if absent).

**Definition of done**

* `tokens:build` idempotent; generated files committed; drift check fails on uncommitted output.
* `tokens:check` and `tokens:lint` pass for light, dark and hc.
* Vitest: alias resolution, transforms, `tokens.css` snapshot, cycle detection error names the path.
* Tokens story in Storybook once PAP-69 lands; until then `/tokens` route screenshotted at 375, 1024 and 1920 in all three themes.
* `docs/design/tokens.md`, ADR `docs/adr/0003-design-tokens.md`; changelog entry; Linear comment with the Pages preview.

**Test plan**

* Unit: every transform on fixture tokens; fallback block generation; rem rounding to 4 decimals.
* Contract: `rawTokens` covers every `TokenPath` in every theme (no missing overrides).
* Visual: `/tokens` swatches and type specimens at three widths × three themes.
* Compatibility: `tokens.css` loads in WebKitGTK (Tauri Linux dev) without `color-mix()`.

**Demo**

Run `pnpm --filter ui tokens:build && pnpm tokens:check`, open `/tokens` on the Pages preview, flip `data-theme` in DevTools between `light`, `dark` and `hc` and watch swatches and contrast badges update. Under one minute.

**Edge cases**

* Alias cycle: build fails with the path.
* Fractional rem outputs rounded for stable snapshots.
* Explicit `data-theme` beats system preference; absent attribute follows the system.
* Tailwind palette collisions (`bg-red-500`) impossible after reset.

**Dependencies**

Soft: PAP-13. Consumers listed above.

**Agent**

Iris (Token Keeper). Reviewed by Sentinel (Code Reviewer) and Forge (Tailwind and build).

**Size**

M: small code, permanent naming.
"""

DESCRIPTIONS["PAP-67"] = """**Goal**

Ship the twenty core interactive components every PaperOS page is built from, on the headless primitive library chosen by PAP-212 (default Base UI, Radix fallback), styled only with Tailwind v4 utilities bound to tokens, each accessible, themable, tested and documented with a story. This issue is the umbrella for three children.

**Children**

1. PAP-236 Component infrastructure and form controls (M): `cn()`, variants, `meta.ts`, Button, IconButton, Input, Textarea, Checkbox, Radio, Switch, Slider, Field - blocks the other two.
2. PAP-237 Overlay components (M): Dialog, AlertDialog, Popover, Tooltip, Menu, Toast.
3. PAP-238 Selection and navigation components (M): Select, Combobox, Tabs, Avatar, Separator, plus the barrel and package `size-limit`.

**Scope**

* In (across children): the twenty components with stories and tests, the `meta.ts` convention PAP-74 fills, portal root resolution for multi-window, focus-ring and touch-target rules, RTL logical properties, bundle budgets.
* Out: layout frames (PAP-70), data display (PAP-71), motion presets (PAP-72), state components (PAP-234), date pickers and form state (PAP-233).

**Spec**

Details live in the children. Cross-child rules:

* Folder shape `components/<name>/{name.tsx, name.stories.tsx, name.test.tsx, meta.ts}`; every component forwards refs, accepts `className`, exposes `data-state`, `data-disabled`, `data-invalid`.
* Sizes `sm|md|lg` = 32/40/48 px; 44 px minimum on coarse pointers; focus ring `2px solid var(--pos-color-focus)` on `:focus-visible` only.
* Library decision: proceed with Base UI if PAP-212 has not merged by 2026-09-19 and note it in the ADR; the public API is ours, so a swap touches imports only.
* Reduced motion: opacity only until PAP-72 presets exist.

**Interface contract**

* Provides (`@paperos/ui`): the twenty components, `cn`, `defineComponentMeta`, `getPortalRoot(doc)`, `ToastProvider` and `useToast`, types `Size`, `Tone`, `Option<T>`; spec IDs `ui.button`, `ui.iconButton`, `ui.input`, `ui.textarea`, `ui.checkbox`, `ui.radio`, `ui.switch`, `ui.slider`, `ui.field`, `ui.dialog`, `ui.alertDialog`, `ui.popover`, `ui.tooltip`, `ui.menu`, `ui.toast`, `ui.select`, `ui.combobox`, `ui.tabs`, `ui.avatar`, `ui.separator`; `can` prop hook point for PAP-229.
* Requires: PAP-66 tokens (hard), PAP-212 decision (soft), PAP-68 `Icon` (soft placeholder).
* Consumers: PAP-69 stories, PAP-70, PAP-71, PAP-74 registry, PAP-151 palette, PAP-224 auth pages, PAP-58 dialogs, PAP-233 pickers, everything else.

**Definition of done**

* All three children Done; twenty components exported from the barrel.
* Integration checks below green; `size-limit` in CI (Button under 6 KB gzipped, package budget documented).
* "All components" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark via PAP-246 (or the local script).
* `docs/design/components.md` lists each component and when to use it; changelog entry; Linear comment with the Storybook link.

**Test plan**

Umbrella checks in `packages/ui/test/umbrella.test.ts` and Storybook:

* Every exported component has `meta.ts` with a valid spec ID and a story; `vitest-axe` zero violations across all stories in `storybook:test`.
* Nested Dialog inside Popover inside Menu dismisses innermost first (PAP-237) and portals resolve per document (PAP-238 Combobox inside a detached window fixture).
* Keyboard traversal story: tab order through one of each component with focus rings visible (video via PAP-83 once available).
* RTL story of the full set at 1280.

**Demo**

Open Storybook "All components", toggle theme and RTL in the toolbar, then tab through the page watching focus rings; open "Overlays/Nested" and press Escape three times. Under one minute.

**Edge cases**

Cross-child: portals inside Tauri multi-window resolve to the trigger's document; long labels truncate with `title`; controlled/uncontrolled switching warns once in dev; the twenty spec IDs are reserved even before PAP-74 fills the schemas.

**Dependencies**

PAP-66 (hard), PAP-212 (soft, dated fallback). Unblocks PAP-69, PAP-70, PAP-71, PAP-73, PAP-74, PAP-151, PAP-233.

**Agent**

Iris (Component Crafter) builds all children. Reviewed by Sentinel (Code Reviewer, Visual Inspector); Scout confirms the primitive library decision.

**Size**

L, split into 3 children (M, M, M).
"""

DESCRIPTIONS["PAP-68"] = """**Goal**

Pick one icon set and one illustration style for all surfaces and ship a tree-shaken `Icon` component plus an `Illustration` component with six starter illustrations, so agents never paste ad-hoc SVGs or mix icon families.

**Scope**

* In: decision between Lucide (`lucide-react` 0.5xx) and Phosphor (`@phosphor-icons/react` 2.x) scored on domain coverage (finance, tables, collaboration), weights, licence, bundle behaviour and agent familiarity (default Lucide); `Icon` wrapper; custom icon pipeline (SVGO plus `@svgr/cli`, 1.5 stroke, 24 px grid); illustration style guide and six illustrations (empty, error, offline, no-permission, success, onboarding); catalogue story with search; ADR.
* Out: logo work, animated icons, emoji policy (PAP-76).

**Spec**

* `Icon` props `{ name: IconName; size?: 'xs'|'sm'|'md'|'lg'|'xl' (12/16/20/24/32); label?: string; flipInRtl?: boolean; className? }`; `aria-hidden` unless `label`, then `role="img" aria-label`.
* `IconName` union generated by `pnpm --filter ui icons:gen` from the library's export list plus `icons/custom/*.svg`; a spec referencing a missing name fails the build (PAP-74 validator).
* Tree-shaking: static imports stay direct; the dynamic-by-name path used by specs goes through a generated lazy map.
* Illustrations use `currentColor` and CSS variables only; `Illustration` sizes `sm|md|lg` (120/200/320 px), always `aria-hidden` with adjacent text required.
* Stroke width from `--pos-icon-stroke` (1.5 default, 2 in hc); `forced-colors: active` uses `CanvasText`.
* ADR `docs/adr/0004-iconography.md`.

**Interface contract**

* Provides: `Icon`, `Illustration`, `IconName`, `IllustrationName` (`empty | error | offline | no-permission | success | onboarding`), `icons:gen` script and the generated `icon-names.json` for the spec validator; spec IDs `ui.icon`, `ui.illustration`; token `--pos-icon-stroke`.
* Requires: PAP-66 sizes and colours. Soft: PAP-209 scoring format.
* Consumers: PAP-236 `IconButton`, PAP-71 `EmptyState`, PAP-234 states, PAP-74 registry, PAP-63 navigation icons (`navigation.console[].icon` is an `IconName`).

**Definition of done**

* ADR merged; both components with stories and Vitest tests.
* Dynamic icon by name renders from a spec fixture; unknown name renders a dev placeholder and logs once.
* `size-limit`: an app importing five icons adds under 3 KB gzipped.
* Six illustrations render in light, dark and hc; screenshots at 375 and 1280.
* Catalogue story searchable; `docs/design/icons.md`; changelog entry.

**Test plan**

* Unit: name union generation from a fixture export list, size token mapping, RTL flip class, `label` to aria attributes.
* Build: `size-limit` scenario file importing five icons.
* Visual: illustration gallery at two widths × three themes; forced-colours emulation in Playwright.
* Interaction: catalogue search filters by name.

**Demo**

Open Storybook "Foundations/Icons", search "invoice", switch to hc and note the thicker stroke; open "Foundations/Illustrations" and toggle dark mode. Under one minute.

**Edge cases**

* Icon-only button without `label`: TypeScript error via `IconButton`.
* Library major version renames icons: the pinned union fails CI on removal.
* Fractional sizes rejected at the type level.
* Print: illustrations hidden, icons keep `currentColor`.

**Dependencies**

PAP-66 (hard). Soft: PAP-209.

**Agent**

Iris (Component Crafter) with Scout (Library Evaluator) supplying the comparison. Reviewed by Sentinel (Code Reviewer); Quill reviews the ADR.

**Size**

S.
"""

DESCRIPTIONS["PAP-69"] = """**Goal**

Stand up Storybook 9 for `packages/ui` as the living documentation, the component accessibility gate and the stable screenshot target Gate 3 points Playwright at, deployed to GitHub Pages on every merge and per PR.

**Scope**

* In: Storybook 9.x with `@storybook/react-vite`, addons a11y, vitest (interaction tests through Vitest browser mode), docs, viewport (seven widths from `ops/ci/breakpoints.json`), theme toolbar (`data-theme`), RTL toggle, container-width decorator; scripts `storybook`, `storybook:build`, `storybook:test`; deploy workflow `ops/ci/storybook.yml`; `index.json` export.
* Out: writing component stories (each component issue), guidelines prose (PAP-76), paid visual services.

**Spec**

* Config `packages/ui/.storybook/{main.ts,preview.tsx,manager.ts,vitest.setup.ts}`; stories glob `../src/**/*.stories.@(ts|tsx|mdx)`.
* `preview.tsx`: `globalTypes.theme` toolbar setting `document.documentElement.dataset.theme`; decorators import tokens CSS, `ThemeProvider`, `ToastProvider`, RTL, container width.
* Viewports `xs 320, sm 375, md 768, lg 1024, xl 1280, 2xl 1536, 3xl 1920` generated from `breakpoints.json` at config load.
* a11y addon scoped to `#storybook-root` plus the portal container, WCAG 2.2 AA tags, `test: 'error'` so violations fail `storybook:test`.
* Vitest addon: `packages/ui/vitest.config.ts` adds the storybook project with the Playwright Chromium provider; CI job `storybook-test` in Gate 1.
* Story naming `Category/Component`; ids stable and used as screenshot keys (`ui-button--all-variants`); tags `autodocs`, `visual` (opt-in for PAP-246), `proposal` (PAP-77).
* Pages: build to `storybook-static`, copy into `storybook/` in the same `gh-pages` push as PAP-15, `/pr/<n>/storybook/` per PR, sticky PR comment gains a Storybook link; `viteFinal` sets `base` from `BASE_PATH`.

**Interface contract**

* Provides: Storybook URLs (`https://imagine-os.github.io/<repo>/storybook/`, `/pr/<n>/storybook/`), `storybook-static/index.json` (story ids, titles, tags) consumed by PAP-246 and PAP-73, the `visual` and `proposal` tag conventions, the `storybook-test` Gate 1 job, viewport names matching PAP-82 project names.
* Requires: PAP-236 (at least Button) for stories, PAP-14 `breakpoints.json`, PAP-15 branch strategy, PAP-78 job slot, Chromium in the runner image (PAP-50).
* Consumers: PAP-246, PAP-73, PAP-76 embeds, PAP-84 (story ids in findings), PAP-92 playbook.

**Definition of done**

* `storybook:build` under 2 minutes in CI; site live from `main` and per PR.
* `storybook:test` runs every `play` and axe check and fails on a seeded violation (reverted commit as proof).
* Theme and viewport toolbars work; Button docs page screenshots at 375 and 1280 in three themes.
* `index.json` consumed by a stub script listing all story ids.
* `docs/design/storybook.md` (stories, tags, deploy); changelog entry; Linear comment with both URLs.

**Test plan**

* Unit: viewport generation from `breakpoints.json`; base path resolution.
* CI: `storybook-test` on a PR touching `packages/ui`; fork PR skips deploy with a comment.
* Visual: docs page at two widths × three themes.
* Flake: `play` tests use `waitFor` and `findBy*`; three consecutive green runs.

**Demo**

Open the PR preview `/pr/<n>/storybook/`, switch viewport to `sm 375` and theme to `hc`, run the a11y panel on Button, then open `index.json` in a tab. Under one minute.

**Edge cases**

* Portal stories: a11y scope includes the portal container.
* Missing Chromium on Forgejo runners: `pnpm exec playwright install --with-deps chromium` in the runner image.
* Large story count: lazy compilation and `build.test` mode in CI.
* Fork PRs: Pages deploy skipped with comment.

**Dependencies**

PAP-236 (hard). Soft: PAP-14, PAP-15, PAP-78, PAP-50.

**Agent**

Iris with Forge (Ops Runner) on the workflow. Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
"""

DESCRIPTIONS["PAP-70"] = """**Goal**

Build the structural components page specs place content into: `AppFrame`, `SplitPane`, `Inspector`, `CommandBar` and `ResponsiveGrid`. They replace the plain divs PAP-16 shipped with, respond to container queries rather than the viewport, and give every app the same resizable, collapsible, keyboard-operable frame. Milestone moved to "Tokens and primitives" because PAP-152 and PAP-63 need it by 2026-09-23.

**Scope**

* In: `packages/ui/src/layout/` components, `Drawer` and `Sheet` helpers, pane-size persistence, named containers `shell`, `sidebar`, `main`, `inspector`, `meta.ts` for each, stories with `play` tests, docs.
* Out: window detach (PAP-21), focus-order rules (PAP-152; sane defaults here), command execution (PAP-151), table layouts.

**Spec**

* `AppFrame` props `{ nav?, sidebar?, inspector?, statusbar?, commandbar?, banner?, children, sidebarWidth = 280, inspectorWidth = 360, collapse: { sidebar: 'md', inspector: 'lg' } }`; renders `<header>`, `<nav>`, `<aside>`, `<main id="main">` landmarks; below the collapse width a slot renders in `Drawer`, toggles injected into the top bar; `useAppFrame()` exposes `toggle(slot)`, `isCollapsed(slot)`.
* `SplitPane`: horizontal or vertical, divider `role="separator"` with `aria-valuenow` and `aria-orientation`, arrows move 16 px, Shift 64 px, Home/End collapse, double-click resets, `pointerdown` capture for touch and pen, `touch-action: none` on the handle only.
* `Inspector`: `title`, `onClose`, `tabs?`, `footer?`; Escape closes when focused; open/close announced via `aria-live`; drawer under `lg`.
* `CommandBar`: portal overlay, controlled `open`, `role="combobox"` input with listbox results and managed `aria-activedescendant`, max height 60vh, full screen under `md`; logic injected by PAP-151.
* `ResponsiveGrid`: `grid-template-columns: repeat(auto-fill, minmax(min(100%, var(--min)), 1fr))`.
* Persistence in `localStorage` under `pos.layout.<appId>.<routeId>`; clamp on mount. Styling via tokens and `@container` only.

**Interface contract**

* Provides: components with spec IDs `ui.appFrame`, `ui.splitPane`, `ui.inspector`, `ui.commandBar`, `ui.responsiveGrid`, `ui.drawer`, `ui.sheet`; `useAppFrame()`; slot names `nav`, `sidebar`, `main`, `inspector`, `statusbar`, `commandbar`, `banner` (the contract PAP-16 layouts and PAP-120 codegen `useLayout` use); container names; persistence key format.
* Requires: PAP-236 Button, PAP-238 Tabs, PAP-237 Sheet behaviour, PAP-16 slot contract, PAP-14 breakpoints (soft).
* Consumers: PAP-63 console, PAP-62 portal, PAP-124 spec editor, PAP-152 focus rules, PAP-21 detach buttons, PAP-151 palette, PAP-165 record panel.

**Definition of done**

* `apps/web` `AppShell` switched to `AppFrame`; example routes still pass their Playwright tests.
* Stories for every component including collapsed and RTL; `play` tests for SplitPane keyboard resize and Inspector open/close.
* Screenshots of the frame at all seven widths in light and dark; Inspector drawer proven at 1024 and below.
* Vitest for persistence key and clamping; axe clean.
* `docs/design/layout.md` with slot diagrams; changelog entry; Linear comment with Storybook and Pages links.

**Test plan**

* Unit: persistence key format, clamp to container, collapse threshold resolution at 200 percent zoom (container widths).
* Interaction: divider keyboard steps and Home/End, double-click reset, Inspector Escape, one-drawer-at-a-time at 768.
* Visual: frame at seven widths × two themes; RTL at 1280.
* Touch: drag divider on an emulated touch device does not scroll the page.

**Demo**

Open Storybook "Layout/AppFrame playground", resize the browser from 1920 to 375 watching sidebar then inspector collapse into drawers, drag and keyboard-resize the split, reload and see sizes persist. Under one minute.

**Edge cases**

* Sidebar and inspector both open at 768: one drawer at a time.
* Persisted size larger than container: clamped on mount.
* Nested SplitPane inside Inspector: `id` prop required for a separate key.
* Reduced motion: drawer slides become fades.

**Dependencies**

PAP-67 children (hard), PAP-16 (hard). Soft: PAP-14, PAP-151, PAP-21.

**Agent**

Iris (Component Crafter) with Forge consulting on the router contract. Reviewed by Sentinel (Visual Inspector across the matrix, Code Reviewer).

**Size**

M.
"""

DESCRIPTIONS["PAP-71"] = """**Goal**

Provide the shared read-only visuals tables, dashboards, feeds and detail pages need: a registry of cell renderers for every field type plus Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime, Money and Truncate, so numbers, dates, users and statuses look identical everywhere. Milestone moved to "Tokens and primitives" because PAP-165 needs it by 2026-09-23.

**Scope**

* In: `packages/ui/src/data/` components, cell renderer registry `data/cells/` for 20 types, `Intl` formatting utilities on `LocaleProvider`, `meta.ts` spec IDs, gallery story.
* Out: editable cells (PAP-165 editors), charts (PAP-170), tables, avatar upload, the other page states (PAP-234 builds ErrorState, DeniedState, OfflineBanner and friends; `EmptyState` stays here).

**Spec**

* Registry: `registerCell(type, renderer)`, `getCell(type)`; types `text, longText, number, currency, percent, date, dateTime, boolean, select, multiSelect, user, relation, url, email, phone, rating, attachment, progress, json, formula` aligned with PAP-164 names (agreed in that issue's thread).
* `Cell` signature `({ value, field, row, density: 'compact'|'default'|'comfortable' }) => ReactNode`; single line at `compact`; overflow via `Truncate` with tooltip; exports `{ Cell, align, defaultWidth }`.
* `Money` takes `{ amountMinor: bigint | number | string, currency }` (the canonical `Money` type lives in `packages/core`; minor units, never floats) with `currencyDisplay: 'narrowSymbol'`; `RelativeTime` on a shared 30 s ticker with absolute time in `title` and `<time dateTime>`.
* `AvatarStack` max 4 visible, `+N` overflow tooltip listing 20 then "and N more"; deterministic fallback colour from PAP-238 Avatar.
* `EmptyState` variants `empty | noResults | success` (illustrations from PAP-68); `error`, `offline`, `noPermission` variants delegate to PAP-234 components.
* `Skeleton` shapes text, avatar, block, table row; shimmer respects reduced motion; `aria-busy` on wrapper. `Timeline` groups `{ id, at, actor, icon?, title, body? }` by local day. `Stat` with label, value, delta and sparkline slot; `KeyValue` definition list with copy buttons.

**Interface contract**

* Provides: components with spec IDs `ui.badge`, `ui.tag`, `ui.avatarStack`, `ui.timeline`, `ui.emptyState`, `ui.skeleton`, `ui.stat`, `ui.keyValue`, `ui.relativeTime`, `ui.money`, `ui.truncate`; `registerCell`, `getCell`, `CellRenderer` type, `CellType` union; `formatMoney`, `formatDate`, `formatNumber` utilities.
* Requires: PAP-238 Avatar, PAP-237 Tooltip, PAP-236 Button; PAP-68 illustrations (soft); PAP-27 `LocaleProvider` (soft: fallback `en-US`); `Money` type from `packages/core` (agree with PAP-175: `amountMinor` bigint at runtime, string on the wire).
* Consumers: PAP-165 grid, PAP-164 field types, PAP-41 data dictionary, PAP-54 in-app git, PAP-62, PAP-183 reports, PAP-234, PAP-186 dashboard.

**Definition of done**

* All components and 20 cell renderers merged with stories at compact, default and comfortable densities.
* Vitest: formatting for en-US, en-GB, de-DE, ja-JP, ar-EG with negative, zero and huge values; registry behaviour.
* axe clean; `play` tests for Tag remove and AvatarStack overflow tooltip.
* "Data display gallery" screenshots at 375, 768, 1280 and 1920 light and dark.
* `docs/design/data-display.md` documents the renderer contract; changelog entry; Linear comment with Storybook link.

**Test plan**

* Unit: every formatter × five locales; bigint-as-string inputs; date-only fields do not shift across zones; null/undefined/empty render an em dash.
* Interaction: Tag remove, AvatarStack overflow tooltip lists 20 then "and N more".
* Visual: gallery at four widths × two themes; RTL (`ar-EG`) story for Money placement.
* Perf: 1 000 `RelativeTime` instances share one interval (single timer assertion).

**Demo**

Open Storybook "Data/Gallery", switch density to compact, then locale to `ar-EG` and watch numerals and currency placement change; hover a 6-person AvatarStack. Under one minute.

**Edge cases**

* Values beyond `MAX_SAFE_INTEGER` arrive as strings and format correctly.
* 500 avatars: slice first `max`, tooltip capped.
* Unbroken URLs wrap with `overflow-wrap: anywhere` inside `Truncate`.
* Unknown cell type: `text` renderer with a dev warning.

**Dependencies**

PAP-67 children (hard). Soft: PAP-68, PAP-27, PAP-175 (`Money` agreement).

**Agent**

Iris (Component Crafter) with Nova (Views Engineer) agreeing the renderer contract. Reviewed by Sentinel (Code Reviewer, Visual Inspector).

**Size**

M.
"""

DESCRIPTIONS["PAP-72"] = """**Goal**

Define how things move: a small vocabulary of durations and easings as tokens, rules for when motion is allowed, and shared transition components so agents never hand-write animations and every animation disappears cleanly under reduced motion.

**Scope**

* In: finalise motion tokens (PAP-66 defines `duration.*` and `ease.*`; this issue owns their values and presets), `packages/ui/src/motion/` with `Presence`, `Fade`, `SlideIn`, `Collapse`, `Stagger`, `useReducedMotion`, `useMotionSafe`, CSS utilities `animate-in`/`animate-out`, `startViewTransition` helper, a lint rule, motion guidelines page, retrofit of PAP-237 overlays to the presets.
* Out: canvas animations, chart transitions (PAP-170), skeleton shimmer (PAP-71), Lottie or video.

**Spec**

* Tokens: `duration.instant 0, fast 120ms, base 200ms, slow 320ms, deliberate 480ms`; `ease.standard, enter (decelerate), exit (accelerate), spring` as `cubic-bezier` plus a `linear()` spring approximation.
* Runtime: `motion@12` only, imported from `motion/react` and `motion/react-m`; `Presence` API `<Presence present={open} enter="fade-up" exit="fade-down" duration="base">` with presets in `presets.ts` mapped to token variables.
* `Collapse` measures with `ResizeObserver`, animates height and opacity, `overflow: hidden` only during animation, `inert` when collapsed; distance capped at 5 000 px with a fade for the rest.
* `useReducedMotion` combines `prefers-reduced-motion` with the user setting `pos.settings.motion` (`system | always | never`), exposed as a `SettingRow` for PAP-62; under reduced motion durations become `instant`, transforms are removed, 80 ms opacity fades remain.
* Route transitions: `startViewTransition` on TanStack Router `onBeforeNavigate` with `view-transition-name` on `main`; disabled on WebKitGTK until verified.
* Performance rule: animate only `transform` and `opacity`; a Stylelint (or Biome custom) rule fails `transition: all` and animating `width|height|top|left` outside `Collapse`.

**Interface contract**

* Provides: components with spec IDs `ui.presence`, `ui.collapse`, `ui.stagger`; `useReducedMotion()`, `useMotionSafe(value, fallback)`, `startViewTransition(cb)`; preset names `fade`, `fade-up`, `fade-down`, `slide-start`, `slide-end`, `scale`; the lint rule package `ops/lint/motion`; token values consumed by PAP-66's `tokens.css`.
* Requires: PAP-66 tokens (hard). Soft: PAP-237 overlays (retrofit targets), PAP-16 router hook, PAP-75 (themes may override durations).
* Consumers: PAP-154 gestures, PAP-144 conflict banners, PAP-136 toasts and inbox, PAP-70 drawers, PAP-83 (motion evidence videos).

**Definition of done**

* Tokens merged; presets and five components with stories showing each preset and the reduced-motion toggle.
* Vitest: `useReducedMotion` matrix (media × setting); `Collapse` height math with a mocked observer; preset-to-token mapping.
* Playwright videos of Dialog open/close and Drawer slide at 375 and 1280, and the same with `reducedMotion: 'reduce'` proving no transforms (PAP-83 format once available).
* Lint rule fails a seeded `transition: all` commit.
* `docs/design/motion.md` with the duration and distance table; changelog entry; Linear comment with Storybook link.

**Test plan**

* Unit: hook matrix, interrupted exit reverses without flash (fake timers), nested `Presence` waits for children unless `immediate`, low-end device downgrade (`hardwareConcurrency <= 4`).
* Interaction: open/close a preset story ten times without leaked nodes.
* Visual and video: Dialog and Drawer at two widths, normal and reduced.
* Lint: rule fixture with passing and failing CSS.

**Demo**

Open Storybook "Motion/Presets", cycle the preset control, flip the reduced-motion toolbar toggle and watch transforms vanish while fades stay; open a Dialog story to see the retrofit. Under one minute.

**Edge cases**

* Exit interrupted by re-open: cancel and reverse.
* Tab hidden: pause non-essential animations.
* Forced colours: focus rings stay visible mid-animation.
* Very tall `Collapse`: capped distance.

**Dependencies**

PAP-66 (hard). Soft: PAP-237, PAP-16, PAP-75.

**Agent**

Iris (Motion and Input Stylist). Reviewed by Sentinel (Visual Inspector via videos, Edge Case Hunter on reduced-motion paths).

**Size**

S.
"""

DESCRIPTIONS["PAP-73"] = """**Goal**

Audit every component in `packages/ui` against WCAG 2.2 AA with automated axe scans and ARIA snapshot checks across all seven widths and three themes, fix every finding, and leave behind a per-component accessibility record and a CI job so the library cannot regress below AA. Recast per the round-2 audit: manual NVDA, VoiceOver and TalkBack passes move to PAP-156, which owns the assistive-technology drivers and device runners; this issue is fully automatable on a Linux runner.

**Scope**

* In: `pnpm --filter ui a11y:scan` (Storybook static build, every story × 7 widths × 3 themes with `@axe-core/playwright`), `locator.ariaSnapshot()` per story committed as name/role regression baselines, contrast verification of every token pair components use (extends `tokens:check`), fix PRs grouped by severity, `meta.ts` `a11y` record, allowlist with expiry, Gate 1 job, checklist template, docs.
* Out: manual screen-reader passes (PAP-156), page-level audits of real apps (PAP-156), accessibility statement (PAP-160), AAA.

**Spec**

* Scan iterates `storybook-static/index.json` (PAP-69), opens each story at each width and theme, runs axe with tags `wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice` scoped to `#storybook-root` plus the portal container, writes `packages/ui/a11y-report.json` and a Markdown summary grouped by rule and component.
* Severity mapping to PAP-79: axe `critical` and `serious` fail CI (S1); `moderate` creates a Linear issue via PAP-97; `minor` logged.
* ARIA snapshots: `__aria__/<storyId>.yml` committed; CI fails on a diff; updates through the same label flow as PAP-247.
* Checklist `docs/design/a11y-checklist.md` per component: name, role, value, keyboard operability, focus visible, announcements, target size (2.5.8), dragging alternatives (2.5.7), focus not obscured (2.4.11), consistent help (3.2.6), redundant entry (3.3.7), accessible authentication (3.3.8); the keyboard and focus rows are verified by `play` tests, the AT rows are marked "see PAP-156".
* `meta.a11y = { auditedAt, wcag: 'AA', notes, atVerified?: ['nvda' | 'voiceover' | 'talkback'] }`; `atVerified` filled by PAP-156.
* CI job `a11y` in Gate 1 on `packages/ui` changes, cached by story hash, under 4 minutes.

**Interface contract**

* Provides: `a11y-report.json` (contracts kind `a11y`: `{ violations: [{ ruleId, impact, storyId, width, theme, nodes }], summary }`), ARIA snapshot baselines, `a11y.allow.json` with expiry, `meta.a11y` shape, the checklist template PAP-156 completes.
* Requires: PAP-67 children and PAP-69 (hard), PAP-70, PAP-71 (audit whatever exists at start, re-run at end), PAP-79 severity names, PAP-78 job slot, PAP-239 artifact kind, PAP-97 (soft) for moderate issues.
* Consumers: PAP-156 (AT rows), PAP-160 (conformance report data), PAP-84 (a11y rubric items), PAP-76 (accessibility page).

**Definition of done**

* Scan reports zero `critical` or `serious` across all stories, widths and themes.
* Every exported component has `meta.a11y.auditedAt` set and a checklist entry with keyboard and focus rows verified by a `play` test.
* ARIA snapshots committed; CI fails on a seeded role change.
* Contrast check covers every token pair used by components in all themes.
* Focus-state screenshots at 375 and 1280 for Dialog, Menu, Select, Tabs, SplitPane; `docs/design/accessibility.md`; changelog entry; Linear comment with the report link and fix count.

**Test plan**

* Automated: the scan itself (21 combinations × all stories); ARIA snapshot diff; contrast assertions; allowlist expiry test.
* Interaction: keyboard operability `play` tests for every interactive component (tab, arrows, Escape, Enter/Space).
* Visual: focus-state screenshots.
* Seeded regressions: a removed `aria-label` and a 3:1 text pair each fail the job.

**Demo**

Run `pnpm --filter ui a11y:scan --story ui-select--default` and open the Markdown summary; then edit Select to drop its label, rerun and read the `serious` violation with the story id, width and theme. Under two minutes.

**Edge cases**

* Portal or hidden-story false positives: allowlist by rule and story id with justification and expiry.
* hc theme changes contrast math: scan runs per theme.
* 44 px targets at 320 px: 24 px minimum with spacing per the 2.5.8 exception, documented.
* Toast disappearing during announcement: `useToast` pauses while the live region is being read.
* Storybook chrome violations: scope excludes it.

**Dependencies**

PAP-67 children, PAP-69 (hard). Soft: PAP-70, PAP-71, PAP-79, PAP-78, PAP-239, PAP-97.

**Agent**

Sentinel (Visual Inspector and Edge Case Hunter) audits; Iris (Component Crafter) fixes. Reviewed by Iris for fixes and Atlas for sign-off.

**Size**

M.
"""

DESCRIPTIONS["PAP-74"] = """**Goal**

Give every design-system component a stable spec ID and a machine-readable props schema so `page.spec.yaml` files reference real components, the validator rejects unknown components or bad props, and codegen emits correct JSX. This is the bridge between the design system and the spec builder.

**Scope**

* In: `defineComponentMeta` convention finalised, `pnpm --filter ui registry:build` producing `registry.json` and `packages/spec/src/generated/components.ts`, `resolveComponent(specId)`, validator rules for PAP-115, auto-generated `docs/spec/components.md`, coverage of primitives, layout, data display, states, pickers, Icon and Illustration.
* Out: the spec schema itself (PAP-114), codegen (PAP-120), non-UI packages.

**Spec**

* `meta.ts` exports `defineComponentMeta({ specId, displayName, category, props: z.object(...), slots, events, a11y, examples, since, deprecated? })`; ID grammar `^(ui|app|print)\\.[a-z][A-Za-z0-9]*$` (`app.` for app-local components registered through the same API, `print.` for PAP-235).
* `props` is Zod 4 and JSON-serialisable only; event handlers live in `events: ['onClick', 'onChange']` and are bound by codegen to spec `logic` actions; unions emit JSON Schema enums; defaults included.
* `slots: { [name]: { multiple: boolean, accepts?: specId[] } }` so `ui.appFrame.sidebar` can restrict content; circular acceptance depth-limited to 10.
* `examples: [{ title, yaml }]` validated at build time.
* `registry.json`: `{ version, generatedAt, components: { [specId]: { displayName, category, schema, slots, events, a11y, deprecated?, since } } }`, committed and drift-checked in Gate 1.
* Resolver: `import.meta.glob('../../ui/src/**/meta.ts')` in dev, generated static map in prod to preserve tree-shaking.
* Interim YAML usage until PAP-114 fixes key names: `components: - id: ui.button  props: { variant: primary, size: md }  slot: main  events: { onClick: actions.save }`.

**Interface contract**

* Provides: `registry.json`, `components.ts` (`SpecComponentId` union and `SpecComponentProps<Id>`), `resolveComponent()`, `validateComponentUsage(spec) => ValidationError[]` (error kinds `unknown-component`, `unknown-prop`, `wrong-type`, `missing-required`, `deprecated`), `defineComponentMeta`, `docs/spec/components.md`.
* Requires: PAP-67 children and every component issue supplying `meta.ts` (PAP-70, PAP-71, PAP-72, PAP-233, PAP-234, PAP-68); PAP-114 final key names (soft, interim shape).
* Consumers: PAP-115 validator, PAP-120 codegen, PAP-124 editor autocompletion, PAP-16 slot registry, PAP-85 planner (component types), PAP-76 related-component lists, PAP-244 spec-conformance reviewer.

**Definition of done**

* Every exported component has `meta.ts`; a Vitest test fails when one is missing or its ID is invalid.
* `registry.json` and `components.ts` generated, committed, drift-checked in Gate 1.
* Validator rules delivered as a PAP-115 plugin (or standalone `validateComponentUsage`) with tests for the five error kinds.
* Three example specs in `specs/pages/examples/` validate and resolve to real components; rendered screenshots at 375 and 1280.
* `docs/spec/components.md` generated; changelog entry; Linear comment with doc and registry links.

**Test plan**

* Unit: ID regex, duplicate ID build failure naming both files, JSON Schema emission for unions and defaults, slot acceptance and depth limit, deprecation warning with `replaceWith`.
* Integration: the three example specs through `validateComponentUsage`; resolver returns lazy components in dev and static in prod build.
* Contract: PAP-120 fixture renders `ui.button` from YAML; PAP-124 autocompletion reads enums.
* Meta: registry build determinism.

**Demo**

Edit `specs/pages/examples/customer-list.page.spec.yaml` to use `ui.buton` and `size: huge`, run `pnpm spec validate` and read the two errors with suggestions; fix and open the generated `docs/spec/components.md` entry for `ui.button`. Under one minute.

**Edge cases**

* `render`/`asChild` polymorphism not spec-exposed; codegen uses named alternatives (`href` produces a link).
* Renamed component: old ID deprecated one minor version with `replaceWith`.
* App-local component collides with a `ui.` ID: build fails.

**Dependencies**

PAP-67 children (hard), PAP-114 (hard for final names; start interim). Soft: PAP-70, PAP-71, PAP-72, PAP-68, PAP-233, PAP-234.

**Agent**

Iris (Component Crafter) with Quill (Page Spec Writer) owning the YAML shape. Reviewed by Sentinel (Code Reviewer) and Atlas for the contract.

**Size**

M.
"""

DESCRIPTIONS["PAP-75"] = """**Goal**

Let any app switch between light, dark and high-contrast at runtime and let each tenant upload a logo and a few brand colours that re-theme the whole product without a rebuild, while every generated palette still passes contrast checks.

**Scope**

* In: `ThemeProvider` with `mode: 'light' | 'dark' | 'hc' | 'system'` persisted per user and applied as `data-theme` with a no-flash boot script; `generateBrandTheme()` producing OKLCH ramps with contrast validation and nudging; `tenant.branding jsonb` and `branding.get/update` procedures gated by `can('tenant.branding.update')`; `/org/settings/branding` page and spec with live preview; `Logo` component with SVG sanitising; hc token finalisation; Storybook toolbar hook.
* Out: custom CSS injection, per-page themes, marketing site theming, font uploads (allowlist only), email and PDF rendering (PAP-235 consumes `brandingToInlineCss`, which this issue provides).

**Spec**

* Boot script in `apps/web/index.html` reads `localStorage` `pos.settings.theme` and `matchMedia` and sets `data-theme` before first paint; `ThemeProvider` hydrates from it; Tauri also calls `window.setTheme`.
* `generateBrandTheme({ accent, neutral?, radius?, font? })` fixes hue and a chroma curve from the accent and derives 11 steps at lightness `97, 93, 85, 75, 65, 55, 47, 39, 31, 23, 15`; dark maps inverted; hc clamps `fg` to L 10 or 98 and doubles border widths; returns `{ css, failures: [{ token, ratio, required }] }` after nudging lightness until every PAP-66 semantic pair passes.
* Injection: one `<style id="pos-tenant-theme">` replaced atomically, scoped to `[data-tenant="<id>"]` or `:root`, under 6 KB.
* `tenant.branding = { logoFileId, logoDarkFileId?, accent, neutral?, radius?, fontFamily?, defaultMode }`; fonts from an allowlist of 12 Google fonts plus system stacks with `font-display: swap`.
* `Logo` picks light or dark variant, falls back to the tenant name; SVG max 512 KB sanitised with `dompurify` on upload; PNG accepted.
* Settings page: colour pickers, logo upload (PAP-37), live component preview, contrast failure list with the adjusted colour shown, reset.
* `brandingToInlineCss(branding)` returns inline-safe hex values for PAP-235.

**Interface contract**

* Provides: `ThemeProvider`, `useTheme()` (`{ mode, setMode, resolved }`), `generateBrandTheme()`, `brandingToInlineCss()`, `Logo`, `TenantBranding` Zod schema, procedures `branding.get`, `branding.update`, the `data-theme` and `data-tenant` attribute contracts, `pos.settings.theme` storage key; the same CSS variable names as PAP-66 (overrides only, no new names).
* Requires: PAP-66 tokens (hard); PAP-33 `tenant.branding` column, PAP-35 procedures, PAP-37 file storage, PAP-59 permission, PAP-63 settings route, PAP-36 cache (all soft).
* Consumers: PAP-62 portal, PAP-63 console, PAP-235, PAP-180 PDFs, PAP-193 landing pages, PAP-69 toolbar, PAP-82 theme fixture.

**Definition of done**

* No flash on first paint for light, dark, hc and system (Playwright screenshot at first paint).
* `generateBrandTheme` for 20 random accents: all contrast pairs pass after nudging (Vitest).
* Settings page screenshots at 375, 768, 1280 and 1920; live preview updates within one frame of a picker change (video).
* Tenant switch re-themes without reload (e2e with two tenants).
* Security review of SVG sanitising; `docs/design/theming.md`; changelog entry; Linear comment with before/after screenshots.

**Test plan**

* Unit: ramp generation, nudge convergence, near-white and near-black accents fall back with a warning, CSS size cap, `brandingToInlineCss` hex output.
* Integration: `branding.update` denied for `member`; sanitiser strips `<script>` and external references from a fixture SVG.
* E2E: mode switch persists across reload; system mode follows a `matchMedia` change; two windows with different tenants do not bleed.
* Visual: settings page at four widths; print media forces light.

**Demo**

Open `/org/settings/branding` as the seeded owner, pick a purple accent and upload the sample logo, watch the preview and the console re-theme live, then switch to the second tenant and back. Under two minutes.

**Edge cases**

* Accent nearly white or black: neutral-tinted fallback with a warning.
* Malicious SVG: stripped; raster fallback offered.
* Offline first load: branding cached in PGlite (PAP-36).
* Printing: light theme forced.

**Dependencies**

PAP-66 (hard). Soft: PAP-33, PAP-35, PAP-37, PAP-59, PAP-63, PAP-36.

**Agent**

Iris (Token Keeper). Reviewed by Sentinel (Security Auditor for uploads, Visual Inspector for themes); Ledger consulted on branding needs for PAP-235.

**Size**

M.
"""

DESCRIPTIONS["PAP-76"] = """**Goal**

Write the design-system guidelines agents consult when a spec leaves room for judgement: voice and tone, density, spacing rhythm, hierarchy, component choice, forms, feedback and states, responsive behaviour. Published in the docs engine, linked from every story, and partly machine-readable so review agents can check them.

**Scope**

* In: twelve MDX pages under `docs/design/guidelines/`, Do and Don't examples rendered from live components, `rules.json` (60 or more rules, 20 checkable by lint or vision), a glossary, 30 before/after copy rewrites, an agent checklist.
* Out: brand marketing guidelines, illustration tutorials, component API docs (autodocs), motion and accessibility content beyond links (PAP-72, PAP-73).

**Spec**

* Pages: `principles`, `voice-and-tone` (sentence case, plain verbs, error formula: what happened, why, what to do), `layout-and-spacing` (4 px grid, 8/16/24 rhythm, 1200 max content width, 65ch measure), `density`, `typography`, `color-usage` (semantic tokens only, one accent per view), `components-when-to-use` (decision tables: Dialog vs Sheet vs Popover, Select vs Combobox vs Radio, Toast vs inline alert vs banner), `forms` (labels above, validation on blur then submit, destructive confirmations), `feedback-and-states` (loading, empty, error, offline, permission, success mapped to PAP-71 and PAP-234 components), `responsive`, `agent-checklist` (10 questions before a PR), `glossary`.
* Frontmatter `title, summary, owner: Iris, lastReviewed, appliesTo: [web, desktop, mobile]`; rule IDs `DS-<AREA>-<nn>` cited by every Do/Don't; each page under 1 200 words with a summary box; "Related components" and "Related specs" resolved from `registry.json`.
* `rules.json` schema `{ id, area, rule, rationale, severity: 'blocker' | 'major' | 'minor', checkable: 'lint' | 'vision' | 'agent' | 'manual', appliesTo?, when?, locale?, examples: { do, dont } }`; severities follow PAP-79.
* Rendering: PAP-128 docs engine at `/docs/design/...`; Storybook MDX under `Guidelines/` until it merges; embeds via `@storybook/blocks`.

**Interface contract**

* Provides: `docs/design/guidelines/rules.json` (validated by a Zod schema exported from `packages/contracts` as kind `design-rules`), rule ID namespace `DS-*`, the glossary terms file `glossary.json` for the spec editor, page slugs.
* Requires: PAP-69 embeds (hard), PAP-128 (hard for final home; Storybook fallback allowed), PAP-74 `registry.json` (soft), PAP-79 severity names.
* Consumers: PAP-244 spec-conformance reviewer (loads `rules.json`), PAP-84 vision inspector (`checkable: vision` items), PAP-118 spec-authoring skill, PAP-105 page-from-spec skill, PAP-124 editor hints.

**Definition of done**

* Twelve pages merged and rendering with working component embeds (docs engine or Storybook fallback).
* `rules.json` validates and contains at least 60 rules, 20 marked `vision` or `lint`; every rule cited by at least one Do/Don't.
* PAP-244 prompt references `rules.json` (PR or comment agreeing the hook); PAP-84 lists the vision rules it checks.
* Screenshots of two guideline pages at 375 and 1280 light and dark.
* Reviewed by Quill (prose) and Iris (correctness); changelog entry; Linear comment with the docs link.

**Test plan**

* Unit: `rules.json` schema validation, unique IDs, every cited ID exists, `appliesTo` values valid.
* Docs: link checker over the twelve pages; every "Related components" entry resolves in `registry.json`.
* Dry run: Sentinel runs the spec-conformance reviewer over one seeded PR that violates `DS-FORM-03` and confirms the finding cites the rule.
* Visual: two pages at two widths × two themes.

**Demo**

Open `/docs/design/components-when-to-use`, read the Dialog vs Sheet table with live embeds, then open `rules.json` and filter for `checkable: vision`; finally open a seeded PR review citing `DS-FORM-03`. Under two minutes.

**Edge cases**

* Guideline contradicts a story: the story is wrong; open a fix task rather than soften the rule.
* Touch-only or desktop-only rules: `appliesTo` and `when` so reviewers skip irrelevant ones.
* Locale-specific copy rules: `locale: en`.
* Removed rule: deprecate, never renumber.

**Dependencies**

PAP-69, PAP-128 (hard; fallback allowed). Soft: PAP-74, PAP-79.

**Agent**

Iris writes; Quill (Changelog Scribe and Page Spec Writer) edits. Reviewed by Sentinel (reviewer dry run) and Atlas.

**Size**

M.
"""

DESCRIPTIONS["PAP-77"] = """**Goal**

Decide before 2026-10-01 whether a design tool belongs in the loop: either wire a token round-trip between the DTCG JSON and Figma variables and document it, or record an ADR to skip Figma in favour of Storybook and code-first design with the criteria that would reopen the question.

**Scope**

* In: one-session research (Figma Variables REST API write access and plan requirements, Tokens Studio plugin with GitHub sync, `@tokens-studio/sd-transforms`, Code Connect and the Figma MCP server, cost, Justin's current workflow via one Needs Justin question defaulting to "no Figma"); the go path converter and Action; the no-go path `design/README.md`, Storybook `proposal` tag and PR template checkbox; `docs/design/design-tooling.md` either way.
* Out: a Figma plugin, redrawing components in Figma, Penpot beyond a paragraph.

**Spec**

* `docs/research/figma-sync.md` (800-1 500 words): options table with cost, write access, automation, maintenance burden, agent usability; recommendation.
* ADR `docs/adr/0007-design-tooling.md` with `status`, `alternatives`, `reopenWhen` (a human designer joins; variables write API reaches the Professional plan).
* Go path: `pnpm --filter ui tokens:figma` converts DTCG `$value/$type` to Tokens Studio sets (`{ "global": { "color": { "accent": { "500": { "value": "#…", "type": "color" } } } } }`), OKLCH to hex via `culori` with `clampChroma`, themes as `$themes.json` with `selectedTokenSets`; protected `figma-tokens` branch; Action `ops/ci/figma-tokens.yml` reverse-converts and opens a PR labelled `tokens` for Iris; code is the source of truth.
* No-go path: `design/README.md` for reference images, Storybook `proposal` tag documented, PR template checkbox "visual proposal attached" (PAP-49).
* Needs Justin comment with options A skip, B Tokens Studio manual sync, C Enterprise API; default A after 48 hours.

**Interface contract**

* Provides: the ADR, `docs/design/design-tooling.md` (how visual proposals are made and reviewed), and on the go path `tokens:figma` plus the `figma-tokens` branch convention; on the no-go path the `proposal` story tag (already reserved by PAP-69) and the PR template line.
* Requires: PAP-66 tokens (hard). Soft: PAP-49 template, PAP-94 question format, PAP-209 scoring.
* Consumers: PAP-92 playbook (how to propose visual changes), PAP-76 (links the tooling page).

**Definition of done**

* Research doc and ADR merged with Justin's answer or the default recorded.
* Go: converter round-trip Vitest on all token files; screenshot of a Figma file with imported variables; Action runs on a test push.
* No-go: `design/README.md`, `proposal` tag documented, PR template updated.
* `docs/design/design-tooling.md` published; changelog entry; Linear comment summarising the decision; Needs Justin item closed.

**Test plan**

* Go: round-trip test DTCG to Tokens Studio to DTCG equals input for every token file; gamut clamping test on an out-of-sRGB OKLCH; composite tokens split correctly.
* No-go: PR template lint (PAP-49) passes with the new checkbox; a `proposal` story renders in Storybook.
* Either: link check on the two docs.

**Demo**

Open the ADR and read the decision and `reopenWhen`; on the go path run `pnpm --filter ui tokens:figma` and open the generated `$themes.json`; on the no-go path open a `proposal`-tagged story. Under one minute.

**Edge cases**

* Out-of-gamut OKLCH: clamped with a noted loss.
* Figma modes limited to 4: light, dark, hc fit; tenant themes never exported.
* Reverse sync renames a token: treated as delete plus add, manual review.
* No Figma seat: research from documentation; limitation recorded.
* No answer in 48 hours: default A applies and the ADR says so.

**Dependencies**

PAP-66 (hard). Soft: PAP-49, PAP-94, PAP-209. Nothing blocks on this issue.

**Agent**

Scout (Library Evaluator) researches; Iris (Token Keeper) builds any converter. Reviewed by Quill (ADR) and Atlas (decision).

**Size**

S.
"""
