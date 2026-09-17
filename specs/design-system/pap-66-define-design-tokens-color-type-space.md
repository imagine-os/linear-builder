---
identifier: "PAP-66"
title: "Define design tokens (color, type, space, radius, motion, elevation) in DTCG JSON compiled to CSS variables"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-27", "PAP-67", "PAP-68", "PAP-72", "PAP-75", "PAP-77", "PAP-236"]
key: "design-system/tokens"
url: "https://linear.app/paperos/issue/PAP-66/define-design-tokens-color-type-space-radius-motion-elevation-in-dtcg"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:10.797Z"
---

# PAP-66: Define design tokens (color, type, space, radius, motion, elevation) in DTCG JSON compiled to CSS variables

**Goal**

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
