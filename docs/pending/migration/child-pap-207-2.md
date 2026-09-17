---
key: "child/PAP-207/2"
title: "Template gallery in onboarding and settings: cards with previews, dry-run diff, apply with or without sample data, remove sample data"
project: "migration"
parent: "PAP-207"
phase: "P2"
type: "Build"
priority: 3
size: "S"
surfaces: ["Customer", "Staff"]
milestone: "Business migrations"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
identifier: "PAP-428"
status: "created"
createdAt: "2026-09-17"
---

# Template gallery in onboarding and settings: cards with previews, dry-run diff, apply with or without sample data, remove sample data

**Goal**

Surface templates where a new business meets PaperOS: a gallery in the `paperos create` onboarding flow and in settings, with preview cards, included-items list, a diff preview from dry run, an "apply with sample data" toggle and a one-click sample-data removal.

**Scope**

In: route `_app/settings/templates` and an onboarding step in PAP-22's flow; components `TemplateCard`, `PackDiff`, `SampleDataBanner`; upgrade prompt when a newer pack version exists.

Out: pack content and applier.

**Spec**

* Diff preview reuses `RunReport` from PAP-199 child 3 with a templates section (tables added, fields merged, accounts skipped).
* Banner shows on every page containing demo rows until removal.

**Interface contract**

Provides: components above, route, onboarding step export `TemplateStep` for PAP-22. Consumes: child 1 applier and `planUpgrade`, child 2 previews and metadata, PAP-199 child 3 `RunReport`. PAP-208 links to this route when recommending templates.

**Definition of done**

* Gallery renders five cards with previews; apply and remove sample data work on staging.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for gallery and one applied dashboard; axe clean.

**Test plan**

* Vitest: card metadata rendering, upgrade prompt logic.
* Playwright: gallery, diff, apply with sample data, browse a page, remove sample data; visual baselines at seven widths, both themes.
* axe on gallery and diff.

**Demo**

Reviewer opens Settings > Templates, picks Agency, reads the diff, applies with sample data and lands on the agency dashboard; clicks "Remove sample data" in the banner. Under two minutes.

**Edge cases**

* Same pack already applied: card shows "Applied" and an Upgrade button when relevant.
* Apply fails at dry run (RLS): error shown inline with the offending table.
* 320 width: cards stack, previews hidden behind a tap.

**Dependencies**

Children 1 and 2 (hard), PAP-22 (soft: settings route works alone), PAP-199 child 3.

**Agent**

Built by Scout (Template Packager) with Iris. Reviewed by Sentinel (Visual Inspector).

**Size**

S
