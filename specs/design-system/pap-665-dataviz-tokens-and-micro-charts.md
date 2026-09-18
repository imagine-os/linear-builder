---
identifier: "PAP-665"
title: "Dataviz tokens and micro-charts: categorical, sequential and diverging palettes validated in three themes, chart theme builder and Sparkline, MiniBar, ProgressRing components"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66", "PAP-293"]
blocks: ["PAP-386", "PAP-621"]
key: "r4/design-system/dataviz-tokens-and-microcharts"
url: "https://linear.app/paperos/issue/PAP-665/dataviz-tokens-and-micro-charts-categorical-sequential-and-diverging"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:25.309Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-665: Dataviz tokens and micro-charts: categorical, sequential and diverging palettes validated in three themes, chart theme builder and Sparkline, MiniBar, ProgressRing components

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

PAP-170 says "the dataviz palette mapped onto `--pos-color-*`" and PAP-71's `Stat` has a sparkline slot, but no issue defines the palette tokens, validates them for contrast and colour-vision deficiency, or ships the tiny inline charts that stats, cells and dashboard number blocks need without loading ECharts. Own that here so every chart in the platform reads as one system.

**Scope**

In: `packages/ui/tokens/dataviz.tokens.json` (DTCG) with `color.dataviz.categorical.1-12`, `sequential.{accent,neutral}.1-9`, `diverging.1-11`, `semantic.{positive,negative,neutral}`; `pnpm tokens:check-dataviz` (contrast against `bg.surface` and pairwise distinguishability with a CVD simulation via `culori`); `buildChartTheme(tokens)` (library-agnostic object plus an ECharts adapter); `packages/ui/src/dataviz/{Sparkline,MiniBar,ProgressRing,Legend}.tsx` in inline SVG.

Out: full chart views (PAP-621), map styles, print palettes (PAP-235).

**Spec**

* Categorical palette: 12 OKLCH hues at matched lightness per theme, ordered so the first six are maximally distinguishable under deuteranopia and protanopia simulation (pairwise ΔE > 20 in the simulated space); dark and hc variants; hc doubles as patterns (`fill` hatch ids) exported alongside colours.
* Sequential ramps derive from the accent and neutral ramps of PAP-66; diverging joins `danger` and `success` through neutral; every step passes 3:1 against `bg.surface` for large marks and the checker reports failures per theme.
* `buildChartTheme(tokens)` returns `{ palette, grid, axis, tooltip, font, radius }` from resolved tokens and an `echartsTheme(theme)` adapter; regenerated on `theme.changed`; the dataviz skill's validator rules (form, colour, mark) are encoded as tests where checkable.
* `Sparkline { data, width, height, tone, showLast }` inline SVG with `<title>` summary, no axes, under 1 KB DOM; `MiniBar { value, max, tone }` for cells and conditional formatting bars; `ProgressRing { value, max, size, label }` with `role="progressbar"`; `Legend { items, onToggle }` textual legend with patterns in hc; all respect reduced motion (no draw animation).
* Tokens compile through PAP-66's Style Dictionary build into `--pos-color-dataviz-*`; TypeScript export `dataviz` in `tokens.ts`.

**Interface contract**

Provides: dataviz DTCG tokens and CSS variables, `tokens:check-dataviz`, `buildChartTheme`, `echartsTheme`, components with spec ids `ui.sparkline`, `ui.miniBar`, `ui.progressRing`, `ui.chartLegend`, pattern ids for hc. Consumes: token build and contrast maths (PAP-66), chart library ADR (PAP-293), theme change (theme provider issue, soft). Consumed by PAP-621, PAP-386 `NumberBlock`, `Stat` (data-display issue), PAP-626 (`MiniBar`), PAP-186.

**Definition of done**

* Tokens merged and compiled; checker green in light, dark and hc with the CVD report attached; four components with stories; `vitest-axe` clean.
* Screenshots of the palette swatches and micro-charts at 375 and 1280 in three themes; `docs/design/dataviz.md` (palette usage rules, when to use which ramp); changelog; Linear comment on PAP-170 and PAP-386.

**Test plan**

* Unit: palette ordering under CVD simulation; contrast per step per theme; `buildChartTheme` token resolution; sparkline path generation with nulls; progress ring arc maths.
* Snapshot: `echartsTheme(light)` JSON committed and diffed.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Foundations/Dataviz`, toggles the deuteranopia simulation decorator and confirms the first six categories stay distinct, switches to hc and sees patterns, then reads a Sparkline's title. Under one minute.

**Edge cases**

* More than 12 series: colours cycle with a lighter tint and the legend warns.
* Sparkline with a single point: renders a dot.
* Tenant accent close to a categorical hue: sequential ramp still derives; categorical stays fixed (documented).
* Forced colours: SVG uses `CanvasText` and patterns.

**Dependencies**

PAP-66 (hard), PAP-293 (soft, adapter target; ECharts assumed). Blocks the chart view and PAP-386; the data-display `Stat` slot consumes `Sparkline` softly.

**Agent**

Builder: Iris (Token Keeper) with the dataviz plugin. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/chart-view-echarts` = PAP-621, `r4/tables/conditional-formatting` = PAP-626.
