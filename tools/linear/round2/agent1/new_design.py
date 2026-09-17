# New issues for the design-system project: gaps and children of PAP-67.
P = "design-system"
MS1 = "Tokens and primitives"
MS2 = "Component library covers app shell needs"
MS3 = "Themable per tenant with docs"

GAPS = [
{
 "key": "design-system/date-pickers-forms", "project": P, "milestone": MS2, "phase": "P1", "type": "Build",
 "surfaces": ["Developer"], "priority": 1, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-67"], "blocks": ["PAP-164", "PAP-166"],
 "title": "Build date, time, date-range and calendar pickers plus form-state adapters (react-hook-form Field, arrays, async validation)",
 "description": """**Goal**

Fill the two holes every data-entry page hits first: date and time pickers (single, range, time, relative presets) that the field types, filter builder and finance pages need, and the form-state adapters that connect `Field` to `react-hook-form` with Zod, arrays and async validation. PAP-67 excluded both deliberately; PAP-164 and PAP-166 require them.

**Scope**

* In: `Calendar`, `DatePicker`, `DateRangePicker`, `TimeField`, `DateTimeField`, `RelativeDatePicker` (presets like "last 30 days", "this quarter") on the chosen primitive library's date components or React Aria (`react-aria-components` `DateField`, `Calendar`, `RangeCalendar`) as fallback; `Form`, `FormField`, `FieldArray`, `useAppForm` adapters over `react-hook-form` 7.x with `@hookform/resolvers/zod`; async validators with debounce; `meta.ts` spec IDs.
* Out: recurring-schedule editors, natural-language date parsing, form layout guidelines (PAP-76).

**Spec**

* Values are `Temporal`-like plain objects via `@internationalized/date` (`CalendarDate`, `Time`, `ZonedDateTime`); never JS `Date` at the API boundary; serialised as ISO strings; date-only fields never shift across zones.
* `DatePicker` props: `{ value, onChange, min, max, granularity: 'day' | 'minute', locale?, timeZone?, presets?, isDateUnavailable? }`; keyboard grid per ARIA APG; typed input with segment editing; `Popover` from PAP-67.
* `RelativeDatePicker` emits `{ kind: 'relative', unit, amount, anchor }` or absolute ranges, matching the shared filter grammar (data-layer spec) so PAP-166 filters and PAP-195 segments store the same shape.
* Forms: `useAppForm(schema, { defaultValues, mode: 'onBlur' })` returns typed `register`, `Field` binding, `errors` mapped to `Field.error`; `FieldArray` with add, remove, reorder (keyboard) rows; async rule helper `asyncRule(fn, { debounceMs: 400 })` sets `validating` state on the Field.
* Validation timing follows guideline `DS-FORM-03`: on blur, then on submit; server errors mapped by path via `setServerErrors(errorMap)`.

**Interface contract**

* Provides: components above with spec IDs `ui.datePicker`, `ui.dateRangePicker`, `ui.timeField`, `ui.dateTimeField`, `ui.relativeDatePicker`, `ui.form`, `ui.fieldArray`; types `DateValue`, `RelativeRange`; `useAppForm`, `setServerErrors`.
* Requires: PAP-67 Popover, Field, Input; PAP-66 tokens; PAP-27 `LocaleProvider`; shared filter grammar types (data-layer) for `RelativeRange`.
* Consumers: PAP-164 date fields, PAP-166 filter builder, PAP-168 calendar view, PAP-180 invoices, PAP-58 invitation expiry.

**Definition of done**

* Six components and the form adapters merged with stories for every state and RTL; `vitest-axe` zero violations.
* Formatting and parsing tests for en-US, en-GB, de-DE, ja-JP, ar-EG with DST boundaries and leap day.
* `RelativeRange` round-trips through the filter grammar fixture from data-layer.
* Screenshots of the "Pickers" and "Forms" stories at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* Docs `docs/design/forms-and-dates.md`; changelog under "Design system".

**Test plan**

* Unit: segment editing, min/max clamping, unavailable dates, preset resolution at quarter boundaries, `FieldArray` reorder.
* Interaction (`play`): open picker, arrow to a date, Enter selects, Escape closes returning focus; range selection with keyboard; async validator shows `validating` then error.
* Visual: seven widths, mobile picker as full-screen sheet under 768.

**Demo**

Open Storybook "Forms/Invoice example": fill a due date with the keyboard only, pick "last quarter" in the range filter, add two line items with FieldArray, submit with an invalid email and watch the on-blur error. Under two minutes.

**Edge cases**

* Time zone differs between user and tenant: `DateTimeField` shows the zone badge; storage in UTC with zone recorded.
* Locale with non-Gregorian calendar (`fa-IR`): Calendar follows `Intl` calendar; documented limits.
* 10 000-row `FieldArray`: virtualised rows over 200.
* Paste of `2026-13-01`: rejected segment, field stays invalid with message.
* Reduced motion: no popover transitions.

**Dependencies**

PAP-67 (hard). Soft: PAP-27, PAP-212 (library choice), data-layer filter grammar spec.

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Nova (field-type contract).

**Size**

M: pickers are mostly library wiring; locale and zone correctness is the risk.
"""},
{
 "key": "design-system/state-components", "project": P, "milestone": MS2, "phase": "P1", "type": "Build",
 "surfaces": ["Developer", "Agent"], "priority": 1, "size": "S", "state": "Backlog",
 "blockedBy": ["PAP-71", "PAP-68"], "blocks": ["PAP-120"],
 "title": "Build the state components codegen emits: ErrorState, DeniedState, OfflineBanner, IntegrationUnavailable, LoadingPage as spec-mapped `ui.*` components",
 "description": """**Goal**

Give every declared page state a real component so codegen (PAP-120) emits `ui.errorState`, `ui.deniedState`, `ui.offlineBanner`, `ui.integrationUnavailable` and `ui.loadingPage` instead of plain fallbacks, and every generated page shows the same loading, error, denied and offline experience.

**Scope**

* In: `packages/ui/src/states/` with `ErrorState` (error boundary aware, retry, report id), `DeniedState` (403 with explain in dev and a return link), `OfflineBanner` (moved from `packages/core/pwa` shell into the design system, with a thin re-export kept for PAP-18), `IntegrationUnavailable` (connector name, status, reconnect action), `LoadingPage` (skeleton composition per layout slot), `NotFoundState`; `meta.ts` for each; copy in one file for i18n.
* Out: `EmptyState` (PAP-71), error reporting transport (app-shell error handling issue), notifications.

**Spec**

* Common props: `{ title?, body?, illustration?, actions?: { primary?, secondary? }, testId? }` with sensible defaults per state; illustrations from PAP-68 (`error`, `no-permission`, `offline`).
* `ErrorState` accepts `error` and `resetErrorBoundary` (compatible with `react-error-boundary` 4.x); shows `errorId` from `reportError()` when available; in dev shows the stack in a `<details>`.
* `DeniedState` reads `useCan` explain text (PAP-59) in dev; production copy is generic.
* `OfflineBanner` subscribes to `navigator.onLine` plus the sync status from PAP-36 `useSyncStatus()`; renders in the layout `banner` slot; announces via `aria-live="polite"` once.
* `IntegrationUnavailable` takes `{ connector, reason: 'disconnected' | 'rate_limited' | 'error', retryAt? }` from PAP-121 status shape.
* `LoadingPage` composes `Skeleton` variants from PAP-71 by `layout` name (`list`, `detail`, `dashboard`, `form`).

**Interface contract**

* Provides: spec IDs `ui.errorState`, `ui.deniedState`, `ui.offlineBanner`, `ui.integrationUnavailable`, `ui.loadingPage`, `ui.notFoundState`; `StateProps` type; the `states` map `stateComponents: Record<PageState, ComponentType>` consumed by codegen.
* Requires: PAP-71 Skeleton, EmptyState; PAP-68 illustrations; soft PAP-59 `useCan`, PAP-36 `useSyncStatus`, PAP-121 connector status.
* Consumers: PAP-120 codegen states switch, PAP-122 conformance tests (declared states must render these ids), PAP-62 and PAP-63 shells.

**Definition of done**

* Six components with stories in light, dark and high-contrast; `vitest-axe` clean; `play` test for `ErrorState` retry.
* `stateComponents` map exported and consumed by PAP-120's template (PR or comment agreeing the import path).
* `OfflineBanner` toggles within one frame of the `offline` event in a Playwright test using `context.setOffline(true)`.
* Screenshots of the "States gallery" at 320, 375, 768, 1280, 1920.
* Docs section in `docs/design/data-display.md` "States"; changelog under "Design system".

**Test plan**

* Unit: default copy per state, dev-only details hidden in production build.
* Integration: error boundary catches a thrown render and shows `ErrorState`; retry re-renders.
* E2E: offline toggle; denied route renders `DeniedState` for a customer principal.
* Visual: gallery at five widths.

**Demo**

Open Storybook "States/Gallery", flip the theme toolbar through light, dark and hc; then in the example app open DevTools, set Offline, and watch the banner appear and announce. Under two minutes.

**Edge cases**

* Error inside `ErrorState` itself: minimal unstyled fallback text, never a blank screen.
* Offline flaps every second: banner debounced 2 s.
* Denied on the root route: `DeniedState` offers sign-out and tenant switch.
* Very small viewport (320): illustrations hidden, text remains.

**Dependencies**

PAP-71, PAP-68 (hard). Soft: PAP-59, PAP-36, PAP-121, PAP-18 (re-export).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector) and Quill (codegen contract).

**Size**

S: six small compositions; the contract with codegen is the point.
"""},
{
 "key": "design-system/email-pdf-theme", "project": P, "milestone": MS3, "phase": "P2", "type": "Build",
 "surfaces": ["Customer", "Staff"], "priority": 3, "size": "M", "state": "Backlog",
 "blockedBy": ["PAP-75"], "blocks": ["PAP-180"],
 "title": "Build the email and PDF rendering theme: `brandingToInlineCss`, print stylesheet and a template kit shared by invoices, receipts, digests and the ACR export",
 "description": """**Goal**

Make everything the product sends or prints look like the product: one branded layout kit for HTML email and HTML-to-PDF, driven by the same tenant branding JSON as the app, used by invoices and receipts (PAP-180), the release digest (PAP-89), notification emails and the accessibility conformance report (PAP-160).

**Scope**

* In: `packages/ui-print/` with `brandingToInlineCss(branding)`, `EmailLayout`, `PdfLayout`, blocks (`Header`, `Footer`, `Table`, `Totals`, `Callout`, `Signature`, `PageBreak`), React Email components for mail, a print stylesheet for PDF, `renderPdf(element, options)` using headless Chromium (Playwright already in the toolchain), `renderEmail(element)` producing inlined HTML plus text, previews in Storybook and a `/__preview/print` dev route.
* Out: template content (each consumer), sending (Resend transport), PDF signing, multi-language copy (consumers pass strings).

**Spec**

* `brandingToInlineCss` maps `tenant.branding` (PAP-75) to a fixed set of inline-safe values: accent, accent contrast, neutral text, border, logo URL (absolute, light variant), font stack (system fallback for email); OKLCH converted to hex with `culori`.
* Email: React Email 3.x components, table-based layout, 600 px column, dark-mode meta with safe colours, plain-text alternative generated with `html-to-text`; tested in Litmus-like snapshot set via `@react-email/render` and a visual check in Mailpit.
* PDF: A4 and Letter, margins 18 mm, running header with logo and document title, footer with page x of y (Chromium `headerTemplate`), `@page` rules, fonts embedded from the Google fonts allowlist or system; `renderPdf` returns a Buffer and a stable text layer.
* Kit contract: consumers build a React tree from blocks and call render; no consumer writes CSS.

**Interface contract**

* Provides: `brandingToInlineCss()`, `renderEmail()`, `renderPdf()`, layout and block components, spec IDs `print.*` in the registry, `PrintBranding` type.
* Requires: PAP-75 branding JSON and font allowlist, PAP-66 tokens (default values), PAP-37 for logo URLs, Playwright Chromium on runners (PAP-50 image).
* Consumers: PAP-180 invoices and receipts, PAP-89 digest HTML, PAP-136 emails, PAP-160 ACR PDF, PAP-191 outreach.

**Definition of done**

* Sample invoice, receipt, digest and ACR render to PDF and email with the seeded tenant's branding; PDFs under 300 KB; text selectable.
* Email renders acceptably in Gmail web, Apple Mail and Outlook web (manual screenshots once, snapshot tests thereafter).
* `brandingToInlineCss` contrast test: accent-on-white text passes 4.5:1 or is nudged (reuses PAP-75 validator).
* Storybook previews at 375 and 1280; print preview route screenshots for A4 and Letter.
* Docs `docs/design/print-and-email.md`; changelog under "Design system".

**Test plan**

* Unit: branding mapping for 20 random accents, hex conversion, plain-text generation.
* Integration: `renderPdf` page count and header text via `pdf-parse`; `renderEmail` snapshot of inlined HTML.
* Visual: PDF first page rasterised and compared at 1240 px width; email preview stories.

**Demo**

Run `pnpm print:preview invoice --tenant acme` to open the preview route, toggle Letter and A4, click Download PDF, then open Mailpit after `pnpm print:send-sample` to see the branded email. Under two minutes.

**Edge cases**

* Tenant without a logo: text wordmark in the accent colour.
* Very long tables spanning pages: repeating table header, no orphaned totals.
* RTL locale: `dir="rtl"` on both layouts; numerals per locale.
* Dark-mode email clients inverting colours: forced light background with `color-scheme: light only`.
* Chromium unavailable at runtime: `renderPdf` throws a typed error the job retries; never a blank PDF.

**Dependencies**

PAP-75 (hard). Soft: PAP-37, PAP-27, PAP-50.

**Agent**

Built by Iris (Token Keeper) with Ledger consulted on invoice layout needs. Reviewed by Sentinel (Visual Inspector) and Quill (digest fit).

**Size**

M: two renderers and a block kit; email client quirks take the time.
"""},
]

CHILDREN = {
"PAP-67": [
{
 "key": "design-system/primitives/infra-form-controls", "type": "Build", "size": "M",
 "title": "Component infrastructure and form controls",
 "description": """**Goal**

Lay down the conventions every component follows and ship the form controls: `cn()`, the variant API, the `meta.ts` convention, and Button, IconButton, Input, Textarea, Checkbox, Radio, Switch, Slider and Field on the chosen headless primitives with Tailwind v4 bound to tokens.

**Scope**

* In: `packages/ui` package setup (`sideEffects: false`, barrel, `size-limit`), `cn()` (`clsx` + `tailwind-merge`), `class-variance-authority` variants (`variant`, `size`, `tone`), `meta.ts` convention with `defineComponentMeta` placeholder, the nine form controls with stories and tests, focus-ring and touch-target rules, RTL logical properties.
* Out: overlays and selection components (siblings), date pickers, form state.

**Spec**

* Folder `packages/ui/src/components/<name>/{name.tsx, name.stories.tsx, name.test.tsx, meta.ts}`; every component forwards refs, accepts `className`, exposes `data-state`, `data-disabled`, `data-invalid`.
* Sizes `sm|md|lg` = 32/40/48 px; `@media (pointer: coarse)` enforces 44 px minimum hit area; focus ring `outline: 2px solid var(--pos-color-focus)` offset 2 px on `:focus-visible` only.
* `Field` wraps label, description, error with `aria-describedby` wiring; `Input` supports `startAdornment`, `endAdornment`, `loading` (Button only); `Slider` supports range and keyboard steps.
* Base UI `@base-ui-components/react` 1.x by default; if PAP-212 recommends Radix by 2026-09-19 switch imports (the API surface here is ours, not the library's).

**Interface contract**

* Provides: `cn`, `cva` presets, `defineComponentMeta`, components and their `meta.ts` with spec IDs `ui.button`, `ui.iconButton`, `ui.input`, `ui.textarea`, `ui.checkbox`, `ui.radio`, `ui.switch`, `ui.slider`, `ui.field`; `Size`, `Tone` types.
* Requires: PAP-66 tokens and `theme.css`; PAP-68 `Icon` for `IconButton` (soft, placeholder glyph until merged).

**Definition of done**

* Nine components merged with stories for every variant and state; `vitest-axe` zero violations each.
* `size-limit`: Button alone under 6 KB gzipped, checked in CI.
* Storybook "All form controls" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* `docs/design/components.md` started with conventions and the nine entries.

**Test plan**

* Unit: variant class output snapshots, controlled and uncontrolled behaviour, `Field` aria wiring.
* Interaction: keyboard toggles for Checkbox, Radio group arrows, Slider arrows and Home/End.
* Visual: seven widths; RTL story for Input adornments.

**Demo**

Open Storybook "Forms/All controls", tab through every control with the keyboard watching focus rings, switch to RTL and dark in the toolbar. Under one minute.

**Edge cases**

* Long Button labels: truncate with `title` unless `wrap`.
* `IconButton` without `label`: TypeScript error.
* Switching controlled to uncontrolled: one dev warning.

**Dependencies**

PAP-66 (hard). Blocks the two sibling children.

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer).

**Size**

M.
"""},
{
 "key": "design-system/primitives/overlays", "type": "Build", "size": "M",
 "title": "Overlay components: Dialog, AlertDialog, Popover, Tooltip, Menu, Toast",
 "description": """**Goal**

Ship the layered components with correct focus, dismiss and stacking behaviour: Dialog, AlertDialog, Popover, Tooltip, Menu (dropdown and context) and Toast with its provider.

**Scope**

* In: six components on the headless primitives, `ToastProvider` and `useToast`, portal root resolution per document (Tauri multi-window), dismiss layers that do not close parents, full-screen sheet mode under `md`, stories and interaction tests.
* Out: Drawer and Sheet layout helpers (PAP-70), motion presets (PAP-72; use opacity only here).

**Spec**

* Dialog: focus trap, `Escape` closes unless `preventClose`, scroll lock, returns focus to trigger, `role="dialog"` with `aria-labelledby`; sheet mode under 768 px via container query.
* AlertDialog: destructive tone, initial focus on cancel, `confirmLabel` required.
* Popover: anchored with collision handling, `modal` option, arrow optional.
* Tooltip: 500 ms delay, instant on group, never for essential content; `IconButton` gets Tooltip automatically from `label`.
* Menu: keyboard navigation, typeahead, submenus, checkbox and radio items, `shortcut` slot, context-menu trigger.
* Toast: queue of max 3, `push({ title, body?, tone, action?, durationMs = 6000 })`, pause on hover and focus, `role="status"`, bottom-right on desktop and top on mobile.

**Interface contract**

* Provides: components with spec IDs `ui.dialog`, `ui.alertDialog`, `ui.popover`, `ui.tooltip`, `ui.menu`, `ui.toast`; `ToastProvider`, `useToast()`; `getPortalRoot(doc)` used by PAP-70 and PAP-21 windows.
* Requires: sibling infrastructure child (`cn`, variants, Button); PAP-66 tokens.

**Definition of done**

* Six components merged; `play` tests for Dialog, Menu and Toast pass in `storybook:test`.
* Nested Dialog inside Popover inside Menu closes only the innermost on Escape (test).
* Screenshots of each overlay at 375 and 1280 light and dark; sheet mode at 375.
* `vitest-axe` clean including portal content.

**Test plan**

* Interaction: focus trap cycle, focus return, Escape and outside-click rules, Toast pause on hover.
* Unit: queue overflow, duration, `preventClose`.
* Visual: overlays at two widths; high-contrast borders.

**Demo**

Open Storybook "Overlays/Nested": open a Menu, then a Popover, then a Dialog, press Escape three times and watch each close in order; push four toasts and see the queue cap at three. Under one minute.

**Edge cases**

* Portal target in a detached Tauri window: resolved via the trigger's `ownerDocument`.
* Tooltip on touch: long-press shows, tap outside hides.
* Toast while a Dialog is open: rendered above the dialog, still announced.

**Dependencies**

Sibling infrastructure child (hard).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
"""},
{
 "key": "design-system/primitives/selection-navigation", "type": "Build", "size": "M",
 "title": "Selection and navigation components: Select, Combobox, Tabs, Avatar, Separator",
 "description": """**Goal**

Complete the twenty-component set with Select, Combobox (virtualised, async), Tabs, Avatar and Separator, and close PAP-67 with the bundle check, the barrel and the "All components" screenshot story.

**Scope**

* In: five components, `@tanstack/react-virtual` list over 200 items, async `loadOptions` with loading and empty states, Tabs with automatic and manual activation, Avatar with fallback initials and deterministic colour, final `index.ts` barrel, `size-limit` config for the whole package, "All components" story.
* Out: Combobox multi-select chips (PAP-164 `multiSelect` editor), data cells (PAP-71).

**Spec**

* Select: native-like keyboard model, typeahead, groups, `placeholder`, `invalid`; renders in a Popover; mobile uses a sheet under 768 px.
* Combobox: `options | loadOptions(query)`, debounce 250 ms, virtualised beyond 200 items, `allowCustomValue`, `aria-activedescendant` managed, `role="combobox"`.
* Tabs: `orientation`, `activation: 'automatic' | 'manual'`, overflow scroll with fade, `value` controlled or not, `lazy` panels.
* Avatar: `src`, `name`, `size`, deterministic fallback colour from a name hash over the accent ramp; `AvatarStack` lives in PAP-71.
* Separator: horizontal and vertical, `decorative` default.

**Interface contract**

* Provides: spec IDs `ui.select`, `ui.combobox`, `ui.tabs`, `ui.avatar`, `ui.separator`; `Option<T>` type shared with PAP-164 select fields and PAP-166 filter values; complete `@paperos/ui` barrel.
* Requires: sibling children (Popover, Field, `cn`); PAP-66 tokens.

**Definition of done**

* Five components merged; `play` tests for Select, Combobox and Tabs.
* Combobox with 10 000 options scrolls at 60 fps (Playwright trace) and reports under 40 DOM rows.
* "All components" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* `size-limit` passes for the package; `docs/design/components.md` completed for all twenty.

**Test plan**

* Interaction: typeahead, async load with loading state, Tabs arrow keys and Home/End, manual activation with Enter.
* Unit: option filtering, custom value, avatar colour determinism.
* Visual: seven widths; Select sheet mode at 375.

**Demo**

Open Storybook "Selection/Combobox async": type "inv", watch loading then results, arrow down and Enter; then open "All components" and flip themes. Under one minute.

**Edge cases**

* Options with duplicate labels: keys by value, labels disambiguated by `description`.
* Tabs with 30 items at 320 px: horizontal scroll with visible affordance.
* Avatar image fails to load: initials fallback without layout shift.

**Dependencies**

Both sibling children (hard).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer) and Nova (Option contract).

**Size**

M.
"""},
],
}

SIBLING_BLOCKS = {
 "design-system/primitives/infra-form-controls": ["design-system/primitives/overlays", "design-system/primitives/selection-navigation"],
 "design-system/primitives/overlays": ["design-system/primitives/selection-navigation"],
}
