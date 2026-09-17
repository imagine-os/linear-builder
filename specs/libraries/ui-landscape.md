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
blocks: ["PAP-236", "PAP-67"]
key: "libraries/ui-landscape"
url: "https://linear.app/paperos/issue/PAP-212/survey-ui-kits-and-headless-libraries-base-ui-radix-react-aria-shadcn"
source: "plan/specs/bucket-8.json (round-1 canonical spec JSON)"
---

# PAP-212: Survey UI kits and headless libraries (Base UI, Radix, React Aria, shadcn, Ark) and recommend

**Goal**

Decide the headless component foundation for `packages/ui` by spiking Base UI, Radix Primitives, React Aria Components, Ark UI and the shadcn/ui distribution against PaperOS's real constraints (Tailwind v4, Tauri WebViews, detached windows, multi-input, WCAG 2.2 AA), and record it as an ADR. `design-system/primitives` proceeds with Base UI by default if this is not merged by 2026-09-19, so the outcome must land before then.

**Scope**

In:
- Spike `spikes/ui-kits/` with the same four components built in each candidate: Select, Dialog, Menu, Combobox (virtualized with 5k options), styled with Tailwind v4 tokens from `design-system/tokens` if merged, otherwise plain CSS variables.
- Scorecards per `libraries/eval-rubric` with extras: Tailwind v4 composability, controlled and uncontrolled APIs, portal behaviour inside Tauri detached windows (`app-shell/breakpoints-windows`), RTL, touch and pen behaviour (`input/input-abstraction`), roving focus and focus trap quality (`input/focus-management`), date and calendar component availability, release stability (Base UI 1.x status, Radix maintenance cadence).
- Measurements: gzipped bundle of the four components, axe results, keyboard-only walkthrough recording, render in webkit2gtk (Linux Tauri) and Chromium.
- Quick rejects with one-paragraph reasons: Headless UI, Mantine, MUI, Chakra, Ant Design.
- ADR `docs/adr/NNNN-PAP-<issue>-ui-primitives.md` and registry entries (adopted, rejected).

Out: building the 20 production components (`design-system/primitives`), icon set (`design-system/icons-illustrations`), form library choice (recorded as a follow-up recommendation only).

**Spec**

- Time-box 1 agent-day; each candidate at most 90 minutes; missing information becomes a rubric penalty, not more research.
- Candidates and versions: `@base-ui-components/react` 1.x, `radix-ui` (unified package) latest, `react-aria-components` 1.x, `@ark-ui/react` 5.x, shadcn/ui CLI (evaluated as a distribution over Radix or Base UI, not as a library).
- Harness: Vite app with a route per candidate and component; Playwright captures screenshots at 375, 768, 1280 in light and dark; axe via `@axe-core/playwright`; bundle via `vite build --mode analyze` per route with `rollup-plugin-visualizer` JSON.
- Tauri check: run the harness inside the `app-shell/tauri-desktop` shell if merged, else in a minimal Tauri 2 scaffold under the spike; open a Dialog and a Menu from a secondary window and confirm portals attach to the correct document.
- Data written to `spikes/ui-kits/results/*.json` and rendered into the ADR table by `pnpm lib score`.
- Recommendation must also state: which primitives are missing in the winner (for example date picker) and where they come from (React Aria date components are the fallback candidate), and the migration cost in hours to the runner-up.

**Definition of done**

- Spike merged under `spikes/` (excluded from `turbo build`), results JSON and generated comparison table committed.
- ADR accepted with scores, gates, rejected options and re-open criteria; Iris and Atlas comment approval on the PR.
- Screenshots at 375, 768, 1280 for the four components per candidate, plus a 30-second keyboard walkthrough video for the winner.
- Registry entries drafted (`libraries/registry`) or a Linear comment for Scout if the registry is not live.
- `design-system/primitives` description updated with the exact package and version.
- CHANGELOG entry; Linear comment linking ADR and results table.

**Edge cases**

- Base UI has not reached a stable 1.0 by evaluation date: score stability down and record the pre-1.0 API-churn risk explicitly.
- Candidate depends on its own styling runtime (Panda, Emotion): penalise under Tailwind composability, do not exclude.
- Portal rendered into the wrong window in Tauri: hard gate failure for detached panels unless a documented container prop exists.
- Combobox cannot virtualize: score a11y and performance separately; note TanStack Virtual integration effort.
- webkit2gtk rendering bugs (backdrop blur, popover positioning): record and check whether they are library or platform bugs.
- License changes (Radix is MIT, Ark MIT, React Aria Apache-2.0): verify at evaluation time via `libraries/license-policy` checker on the spike lockfile.

**Dependencies**

`libraries/eval-rubric` (hard: scoring format; use the draft if unmerged). Soft: `design-system/tokens` (real tokens in the spike), `app-shell/tauri-desktop` (real shell for the WebView test). Blocks `design-system/primitives`; informs `input/focus-management`, `input/input-abstraction`.

**Agent**

Researched by Scout (Library Evaluator) paired with Iris (Component Crafter) for the styling spike. Reviewed by Iris (decision consumer) and Atlas.

**Size**

M: five spikes with measurements is real work, tightly time-boxed to one day.
