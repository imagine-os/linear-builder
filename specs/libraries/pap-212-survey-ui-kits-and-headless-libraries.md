---
identifier: "PAP-212"
title: "Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Evaluation process"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-67", "PAP-236"]
key: "libraries/ui-landscape"
url: "https://linear.app/paperos/issue/PAP-212/survey-ui-kits-and-headless-libraries-base-ui-radix-react-aria-shadcn"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:57.033Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-212: Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

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
