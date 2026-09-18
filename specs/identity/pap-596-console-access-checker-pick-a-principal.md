---
identifier: "PAP-596"
title: "Console access checker: pick a principal, action and resource, see the decision with matched policies, spec lines, field rules and the SQL predicate, and save the case as a permission-matrix fixture"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-227", "PAP-228", "PAP-582"]
blocks: []
key: "r4/identity/access-checker"
url: "https://linear.app/paperos/issue/PAP-596/console-access-checker-pick-a-principal-action-and-resource-see-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.828Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-596: Console access checker: pick a principal, action and resource, see the decision with matched policies, spec lines, field rules and the SQL predicate, and save the case as a permission-matrix fixture

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-227 ships `explain` as a CLI and PAP-63 renders policies read-only. Justin, staff admins and reviewers need to answer 'why can Ada not see this invoice?' without a terminal, and every answer worth keeping should become a test. Cerbos and Oso ship a playground; this is ours, on the console, wired to the real engine.

**Scope**

In: Page `/console/security/access-checker` with spec, form (principal picker from members and agents or a pasted fixture JSON, action from the registry, resource by dataset and id or a synthetic resource form), result panel (decision, matched policies with `source.specPath:line`, denies that would flip the result, field decisions from PAP-590, `toPredicate` SQL rendered, delegation branch from PAP-594 when `actingFor` is set), 'Save as fixture' writing `specs/fixtures/permissions/<name>.json` through the forge API (PAP-276, soft: download), link from every dev-mode 403 toast (PAP-229 explain) to the checker with the case prefilled; docs section.

Out: Editing policies (PAP-588), the engine itself, matrix generation (PAP-64 consumes the saved fixtures).

**Spec**

* Evaluation runs server-side through `permissions.explain({ principal, action, resource })` (staff only, audited) so results equal production decisions; a synthetic principal is allowed only in non-production.
* Result shows the three layers PAP-59 promises: policy decision, SQL predicate, and (when a page spec declares the action) the UI affordance from `hiddenWhenDenied` or `disabledWhenDenied`.
* Saved fixtures follow PAP-64's fixture schema; PAP-64's generator picks them up as extra cases; duplicates by hash are refused.
* Deep link `?case=<base64>` so a 403 toast in dev opens the exact case.

**Interface contract**

Provides: Page and spec, procedure `permissions.explain` (staff), fixture writer, deep-link format, `ExplainPanel` component reused by the roles page.

Consumes: `explain()` (PAP-227), `toPredicate` (PAP-228), console frame (PAP-582), procedure registry (PAP-268), field rules (PAP-590, soft), delegation (PAP-594, soft), forge API (PAP-276, soft), PAP-64 fixture schema.

**Definition of done**

* Checker reproduces the three worked examples from `docs/platform/permissions.md` with the spec lines shown; saved fixture appears in the PAP-64 run (test).
* Screenshots at 768 and 1280 light and dark; axe clean; dev 403 toast deep link opens the case; docs; changelog under Identity.

**Test plan**

* Unit: case encoding and decoding, fixture schema mapping, duplicate hash refusal, synthetic principal guard.
* E2E: staff opens the checker, evaluates `invoice.update` for a support fixture, reads the deny source, saves the fixture and sees it in the generated matrix.

**Demo**

Open the checker, pick Ada, `invoice.update`, invoice 123, read the denying policy and its spec line, flip to a support agent and read the allow, then save it as a fixture. Under two minutes.

**Edge cases**

* Resource id not found: synthetic resource form with the entity's `permissionColumns`.
* Thousands of policies matched (wildcards): panel groups by source file.
* Agent principal with `actingFor`: both branches shown side by side.

**Dependencies**

Blocked by PAP-227, PAP-228, PAP-582 (hard). Soft: PAP-268, PAP-276, PAP-64, PAP-590, PAP-594.

**Agent**

Builder: Iris (Component Crafter) with Forge on the procedure. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/console-frame` = PAP-582, `r4/identity/custom-roles` = PAP-588, `r4/identity/delegated-authority` = PAP-594, `r4/identity/field-permissions` = PAP-590.
