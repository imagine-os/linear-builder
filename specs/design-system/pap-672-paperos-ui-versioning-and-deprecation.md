---
identifier: "PAP-672"
title: "@paperos/ui versioning and deprecation policy: changesets, since and deprecated metadata, rename codemods, visual baseline update flow and the component status page"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Docs"
priority: 3
surfaces: ["Developer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-52", "PAP-74", "PAP-459", "PAP-522"]
blocks: ["PAP-461"]
key: "r4/design-system/ui-package-versioning-and-deprecation"
url: "https://linear.app/paperos/issue/PAP-672/paperosui-versioning-and-deprecation-policy-changesets-since-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:28.027Z"
model: "claude-haiku-4-5"
effort: "low"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-672: @paperos/ui versioning and deprecation policy: changesets, since and deprecated metadata, rename codemods, visual baseline update flow and the component status page

**Model / Effort:** Haiku 4.5 (`claude-haiku-4-5-20251001`) / low — Docs S

**Goal**

Sixty components will change under twenty agents. Without a written policy, a renamed prop breaks codegen output silently. Define how `@paperos/ui` versions, deprecates and removes, generate a component status page from `meta.ts`, and give agents a codemod path so a rename is one command.

**Scope**

In: `docs/design/versioning.md`; `.changeset` config for `packages/ui` and `packages/tokens` (independent semver in the workspace, `0.x` until RC per `docs/module-system.md` 2.1); `meta.ts` fields `since`, `deprecated: { since, replaceWith, removeIn }` enforced by a test; `pnpm ui:codemod <from> <to>` (jscodeshift transform for component and prop renames, driven by `deprecated.replaceWith`); generated `docs/design/status.md` (component, spec id, since, status `alpha|stable|deprecated`, a11y audited, reflow audited); Gate 3 baseline update rule for intentional visual changes.

Out: the contract package versioning itself (PAP-459 and the module system), release tagging (PAP-52), Storybook deploy (PAP-69).

**Spec**

* Policy: additive props and new components are minor; prop removal or rename is a deprecation for at least one minor with a console warning in dev and a codemod entry, then removal in the next minor; `0.x` semantics per the module system document; the `contract-design-system` version bumps only when a spec id or props schema changes.
* `meta.ts` test: every component has `since`; `deprecated` entries need `replaceWith` and `removeIn`; `registry.json` (PAP-74) carries both so PAP-115's validator warns on deprecated ids and PAP-120 codegen never emits them.
* Codemod: `pnpm ui:codemod ui.button:variant=ghost ui.button:variant=subtle` and `pnpm ui:codemod ui.oldCard ui.card` rewrite TSX imports and JSX props across `apps/**` and `packages/**`, and page specs (`specs/**/*.yaml`) through a YAML-aware pass; dry run by default.
* Visual baselines: an intentional change adds the `visual-change` label and the PR body lists affected story ids; PAP-246's update flow accepts new baselines only with that label; documented as the one way to change what a component looks like.
* Status page regenerated in CI from `registry.json` and `meta.a11y`; linked from Storybook's docs landing and PAP-76 guidelines.

**Interface contract**

Provides: `docs/design/versioning.md`, changeset config, `meta.ts` schema additions, `pnpm ui:codemod`, `docs/design/status.md` generator, the `visual-change` label convention. Consumes: `meta.ts` and `registry.json` (PAP-74), contract versioning rules (PAP-459, module system doc), release automation (PAP-52), baseline flow (PAP-246, soft), validator and codegen (PAP-115, PAP-120, soft). Consumed by PAP-461 wire (deprecation window), PAP-92 playbook, every component PR.

**Definition of done**

* Policy doc merged and linked from `docs/design/components.md`; `meta.ts` test enforces `since`; codemod renames a seeded component across a fixture app and a page spec; status page generated in CI.
* Changeset config produces a version bump PR on a seeded change; changelog; Linear comment on PAP-74 and PAP-461.

**Test plan**

* Unit: meta schema test; codemod transforms on TSX and YAML fixtures (import, JSX, prop rename, dry run); status page generation determinism.
* CI: changeset bump on a seeded change; status page diff fails when `registry.json` changed without regeneration.
* E2E: none.

**Demo**

Reviewer deprecates a prop in a fixture component's `meta.ts`, runs the codemod over the fixture app in dry-run and then for real, and opens the regenerated status page showing the deprecation. Under one minute.

**Edge cases**

* Codemod hits a spread props usage: reports as manual, never rewrites blindly.
* Component deprecated but still emitted by an old page spec: validator warning with the replacement.
* Version bump of tokens without ui: independent changesets, both documented.

**Dependencies**

PAP-74 (hard, `meta.ts` and registry), PAP-459 (hard, versioning rules), PAP-52 (hard, release automation). Soft: PAP-246, PAP-115, PAP-120. Blocks PAP-461's deprecation-window step.

**Agent**

Builder: Quill (Changelog Scribe) with Iris. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
