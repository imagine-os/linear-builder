# Round 4 digest: Design System (`design-system`)

Benchmarks: Radix UI and Base UI; shadcn/ui and Radix Themes; Material 3; Atlassian Design System; Shopify Polaris; IBM Carbon; GitHub Primer; Microsoft Fluent 2; Ant Design; Mantine; W3C DTCG tokens; WCAG 2.2 AA (1.4.4, 1.4.10, 1.4.12).

Feature matrix: 50 rows, 27 covered, 10 partial, 13 gap. New issues: 18 (6 with a parent, 12 standalone gaps, 0 deferred to v0.2). Amendments: 8. Cross-project suggestions: 4.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| DTCG tokens: colour, type, space, radius, motion, elevation | covered | PAP-66 |  |
| z-index scale tokens | partial | PAP-66 | Amendment |
| Component-level tokens (button radius, etc.) | partial | PAP-236 | Amendment |
| Density tokens and runtime density setting | gap | r4/design-system/density-modes | Linear/Gmail/Atlassian |
| Dataviz palettes (categorical, sequential, diverging) with CVD validation | gap | r4/design-system/dataviz-tokens-and-microcharts | PAP-170 assumes them |
| Micro-charts: Sparkline, MiniBar, ProgressRing | gap | r4/design-system/dataviz-tokens-and-microcharts | Stat slot, number blocks |
| Headless primitives + Tailwind v4 conventions | covered | PAP-236 |  |
| Form controls (Button, Input, Checkbox, Radio, Switch, Slider, Field) | covered | PAP-236 |  |
| Overlays (Dialog, AlertDialog, Popover, Tooltip, Menu, Toast) | covered | PAP-237 |  |
| Selection and navigation (Select, Combobox, Tabs, Avatar, Separator) | covered | PAP-238 |  |
| Navigation: NavList, Breadcrumb, Pagination, Link, Stepper, Kbd | gap | r4/design-system/navigation-components | Shells would each invent them |
| Surfaces and feedback: Card, Accordion, InlineAlert, Callout, Progress, Spinner, ScrollArea, Toolbar, SegmentedControl, HoverCard | gap | r4/design-system/surface-and-feedback-components |  |
| Specialised inputs: Number, Password, OTP, Search, ColorPicker, FileUpload, TagInput, Rating | gap | r4/design-system/specialised-inputs | Auth, branding, attachments need them |
| Date, time, range, relative pickers | covered | r4/design-system/date-time-pickers | Split from PAP-233 |
| Form-state adapters (react-hook-form + Zod) | covered | r4/design-system/form-state-adapters | Split from PAP-233 |
| Form layout, sections, sticky actions, unsaved-changes guard | gap | r4/design-system/form-layout-and-unsaved-changes | PAP-333 references FieldGroup |
| Layout: AppFrame, SplitPane, Inspector, CommandBar, ResponsiveGrid | covered | PAP-70 |  |
| Responsive helpers (useContainerSize, Responsive) | partial | PAP-70 | Amendment |
| Cell renderer registry and 20 cells | covered | r4/design-system/cell-renderer-registry-and-cells | Split from PAP-71 |
| Data display: Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime, Money | covered | r4/design-system/data-display-components | Split from PAP-71 |
| Static DataTable (ui.dataTable) | gap | r4/design-system/static-data-table | Codegen emits it; unowned since round 2 |
| State components (Error, Denied, Offline, IntegrationUnavailable, Loading, NotFound) | covered | PAP-234 |  |
| Typography components: Text, Heading, Prose, Code | gap | r4/design-system/typography-components-and-prose | Docs and rich text need Prose |
| Media: Image, FilePreview, Lightbox | gap | r4/design-system/media-preview-and-lightbox | Attachments, screenshots |
| Icons and illustrations | covered | PAP-68 |  |
| Motion system and transitions | covered | PAP-72 |  |
| Reduced motion | covered | PAP-72 |  |
| Storybook with a11y, viewport, interaction tests | covered | PAP-69 |  |
| Storybook density and forced-colors globals | partial | PAP-69 | Amendment |
| Automated axe and ARIA snapshot audit | covered | PAP-73 |  |
| Forced-colors and RTL in the a11y scan matrix | partial | PAP-73 | Amendment |
| Reflow (1.4.10), zoom (1.4.4), text spacing (1.4.12) audit | gap | r4/design-system/reflow-zoom-text-spacing-audit | axe cannot see these |
| Manual screen reader passes | covered | PAP-156 | Input project |
| Component spec IDs and props schemas | covered | PAP-74 |  |
| Component versioning, deprecation, codemods, status page | gap | r4/design-system/ui-package-versioning-and-deprecation |  |
| Design lint (no raw colours, spacing, icons) | gap | r4/design-system/design-lint-rules | Keeps 20 agents on tokens |
| Theme modes light/dark/hc/system with no-flash boot | covered | r4/design-system/theme-provider-and-brand-theme-generator | Split from PAP-75 |
| Per-tenant brand theming and generator | covered | r4/design-system/theme-provider-and-brand-theme-generator |  |
| Branding settings page, Logo, SVG sanitising | covered | r4/design-system/tenant-branding-settings-and-logo | Split from PAP-75 |
| Email and PDF theme kit | covered | PAP-235 | Deferred |
| Guidelines and machine-readable rules | covered | PAP-76 |  |
| Figma/token round-trip decision | covered | PAP-77 |  |
| RTL logical properties in components | covered | PAP-236, PAP-67 |  |
| Component copy i18n hook | partial | PAP-236, PAP-27 | Amendment: useUiStrings |
| Print styles for components | partial | PAP-75, PAP-235 | Light forced; kit deferred |
| Coachmark / product tour components | partial | PAP-380 | Collab builds; cross-project suggestion to use ui.coachmark |
| Notification and inbox UI | partial | PAP-136 | Collab owns |
| Rich text editor chrome | partial | PAP-142 | Realtime owns |
| Charts and maps | covered | r4/tables/chart-view-echarts, r4/tables/map-view-maplibre-and-geo-field | Tables owns views; DS owns palette |
| Module contract, conformance, wiring | covered | PAP-459, PAP-460, PAP-461 |  |

## New issues

| Key | Title | Parent | Milestone | Size | Model / effort | Priority | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/design-system/cell-renderer-registry-and-cells` | Cell renderer registry and the 20 read-only cells with Intl formatting utilities and density support | PAP-71 | Tokens and primitives | M (3) | Sonnet 5 / high | 1 |  |
| `r4/design-system/data-display-components` | Data display components: Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime and Money | PAP-71 | Tokens and primitives | M (3) | Sonnet 5 / high | 2 |  |
| `r4/design-system/theme-provider-and-brand-theme-generator` | ThemeProvider with no-flash boot, light, dark, hc and system modes, and generateBrandTheme producing contrast-validated OKLCH ramps | PAP-75 | Themable per tenant with docs | M (3) | Sonnet 5 / high | 1 |  |
| `r4/design-system/tenant-branding-settings-and-logo` | Tenant branding: tenant.branding schema and procedures, /org/settings/branding page with live preview and contrast report, Logo component and SVG sanitising | PAP-75 | Themable per tenant with docs | M (3) | Sonnet 5 / high | 2 |  |
| `r4/design-system/date-time-pickers` | Date, time, date-range, date-time and relative-date pickers on @internationalized/date with locale, zone and DST correctness | PAP-233 | Component library covers app shell needs | M (3) | Sonnet 5 / high | 1 |  |
| `r4/design-system/form-state-adapters` | Form-state adapters: useAppForm over react-hook-form with Zod, Form and FormField bindings, FieldArray with keyboard reorder, async validation and server error mapping | PAP-233 | Component library covers app shell needs | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/navigation-components` | Navigation components: NavList with nesting and router-aware active state, Breadcrumb, Pagination, Link, Stepper and Kbd | — | Component library covers app shell needs | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/surface-and-feedback-components` | Surface and feedback components: Card, Accordion, InlineAlert, Callout, Progress, Spinner, ScrollArea, Toolbar, SegmentedControl and HoverCard | — | Component library covers app shell needs | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/specialised-inputs` | Specialised inputs: NumberInput, PasswordInput, OTPInput, SearchInput, ColorPicker, FileUpload with progress and crop, TagInput and RatingInput | — | Component library covers app shell needs | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/static-data-table` | Static DataTable (ui.dataTable) for spec pages and settings lists: sortable columns, selection, sticky header, responsive card collapse, no compiler or virtualisation | — | Component library covers app shell needs | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/dataviz-tokens-and-microcharts` | Dataviz tokens and micro-charts: categorical, sequential and diverging palettes validated in three themes, chart theme builder and Sparkline, MiniBar, ProgressRing components | — | Component library covers app shell needs | M (3) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/typography-components-and-prose` | Typography components: Text, Heading with decoupled level and size, Prose for MDX and rich text, Code and inline Kbd styling on the type tokens | — | Component library covers app shell needs | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/form-layout-and-unsaved-changes` | Form layout and unsaved-changes guard: FormLayout, FormSection, FieldGroup, FormActions sticky bar, dirty-state indicator and useUnsavedChangesGuard with router and beforeunload blocking | — | Component library covers app shell needs | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/design-lint-rules` | Design lint rules in Gate 1: no raw colours, no arbitrary spacing, tokens-only utilities, registered icons only, motion and focus rules, with autofix and an allowlist | — | Component library covers app shell needs | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/design-system/density-modes` | Density modes: compact, default and comfortable as a runtime setting with density tokens for control heights, spacing and row heights, applied by every component | — | Themable per tenant with docs | S (2) | Sonnet 5 / medium | 3 |  |
| `r4/design-system/reflow-zoom-text-spacing-audit` | Reflow, zoom and text-spacing audit: 400 percent zoom at 320 CSS px, 200 percent text-only zoom, WCAG 1.4.12 text-spacing injection and 1.4.10 reflow over every story and template page | — | Themable per tenant with docs | S (2) | Opus 5 / high | 2 |  |
| `r4/design-system/media-preview-and-lightbox` | Media components: Image with variants and blur-up, FilePreview for images, PDF, video, audio and office fallbacks, and an accessible Lightbox with zoom and swipe | — | Themable per tenant with docs | S (2) | Sonnet 5 / medium | 3 |  |
| `r4/design-system/ui-package-versioning-and-deprecation` | @paperos/ui versioning and deprecation policy: changesets, since and deprecated metadata, rename codemods, visual baseline update flow and the component status page | — | Themable per tenant with docs | S (2) | Haiku 4.5 / low | 3 |  |

## Amendments to existing specs

| Issue | Section | Summary |
|---|---|---|
| PAP-66 | Spec | * Round 4: add `zIndex.{base 0, raised 10, sticky 100, dropdown 1000, overlay 1100, modal 1200, popover 1300, toast 1400, tooltip 1500}` tokens (`--pos-z-*`) so… |
| PAP-236 | Spec | * Round 4: a component token layer `--pos-<component>-<prop>` (for example `--pos-button-radius`, `--pos-control-height-md`) defined in `packages/ui/tokens/comp… |
| PAP-73 | Spec | * Round 4: the scan matrix adds `forced-colors: active` emulation (Windows High Contrast; asserts focus rings, borders and icons remain visible via `CanvasText`… |
| PAP-70 | Interface contract | * Round 4: also provides `useContainerSize(ref)` (named container query results as `{ width, name, matches: { sm, md, lg } }`), `<Responsive above="md" / below=… |
| PAP-71 | Scope | Round 4: this issue is an umbrella for `r4/design-system/cell-renderer-registry-and-cells` (registry, twenty cells, formatters, `Truncate`) and `r4/design-syste… |
| PAP-74 | Spec | * Round 4: `defineComponentMeta` gains `a11y` (already planned) plus `density: ('compact'/'default'/'comfortable')[]` support flags, `since` and `deprecated: { … |
| PAP-69 | Spec | * Round 4: `globalTypes` also expose `density` (`compact/default/comfortable`, sets `data-density` via `r4/design-system/density-modes`), `forcedColors` (emulat… |
| PAP-76 | Spec | * Round 4: a thirteenth page `navigation-patterns` (sidebar vs tabs vs breadcrumb, pagination vs infinite scroll, when a Stepper) referencing `r4/design-system/… |

## Cross-project suggestions

| Target | Title | Why |
|---|---|---|
| collab | PAP-380 product tour uses design-system `ui.coachmark` and `ui.spotlight` components rather than its own overlay | A coachmark is a Popover variant with a step counter; if collab builds it privately it will not follow tokens, density or reduced motion. Iris can add the two components to `r4/design-system/surface-and-feedback-components` if collab agrees. |
| quality | PAP-246 story baselines add `forced-colors`, RTL and `density: compact` projects for the component gallery | PAP-73 and the reflow audit emulate them; baselines that ignore them let regressions through. |
| app-shell | PAP-27 i18n provides the catalog hook behind `useUiStrings()` and pseudo-locale testing of component copy | Component strings (Close, Clear, Loading) must be translatable; the design system exposes the hook, app-shell owns catalogs. |
| identity | PAP-224 auth pages consume `ui.otpInput`, `ui.passwordInput` and `ui.stepper` from `r4/design-system/specialised-inputs` and navigation components | Avoids a second OTP field and keeps sign-in visually identical to the rest of the app. |

## What was missing and why it matters

1. Codegen emits `ui.dataTable` (PAP-120, PAP-125) and the round-2 audit noted nobody owns it; a light static `DataTable` with an explicit boundary against the views grid now exists so agents pick the right table.
2. Whole component families every benchmark system ships were absent: navigation (NavList, Breadcrumb, Pagination, Stepper, Kbd), surfaces and feedback (Card, Accordion, InlineAlert, Progress, Toolbar, SegmentedControl), specialised inputs (Number, OTP, ColorPicker, FileUpload, TagInput) and typography (Text, Heading, Prose). Without them the console, portal, auth pages and docs engine would each invent their own.
3. PAP-170 assumed a dataviz palette and PAP-71's `Stat` a sparkline slot with no owner; dataviz tokens validated for contrast and colour-vision deficiency plus inline micro-charts now sit in the design system so every chart reads as one system.
4. Two audits axe cannot perform (reflow at 320 CSS px, 200 percent zoom, WCAG 1.4.12 text spacing) and the density system (compact, default, comfortable as tokens and a user setting) were missing; both feed PAP-160's conformance report and PAP-76's guidelines.
5. Governance for twenty agents editing sixty components was missing: design lint rules (no raw colours, spacing or unregistered icons) in Gate 1 and a versioning, deprecation and codemod policy with a status page. PAP-71, PAP-75 and PAP-233 were split into six children so the cells and pickers on the grid critical path land first; the branding page is mounted by identity's console (`r4/identity/console-admin-pages`).
