---
identifier: "PAP-501"
title: "Flags settings page `/settings/flags`: kill switches, per-tenant and per-audience overrides, rule editor with priority, audit trail and `flags.yaml` declaration status"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-17", "PAP-33", "PAP-35", "PAP-59", "PAP-229", "PAP-236", "PAP-269", "PAP-366"]
blocks: ["PAP-453"]
key: "r4/app-shell/flags-settings-page"
url: "https://linear.app/paperos/issue/PAP-501/flags-settings-page-settingsflags-kill-switches-per-tenant-and-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:51.012Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-29"
cycle: null
---

# PAP-501: Flags settings page `/settings/flags`: kill switches, per-tenant and per-audience overrides, rule editor with priority, audit trail and `flags.yaml` declaration status

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-366 ships the flag tables, evaluator and hooks; the staff page that operates them is a separate half-session so the evaluator can merge first and the module swap page (PAP-538) can reuse the same components. This is the surface Justin and Atlas use to turn risky work on for one tenant and off for everyone in five seconds.

**Scope**

In:

* Spec `specs/pages/staff/settings-flags.spec.yaml` with `access: { audiences: [staff.owner, agent.atlas] }` and route `/settings/flags` in the `shell.settings.sections` slot.
* Components in `apps/web/src/pages/settings/flags/`: `FlagTable` (key, kind, default, declared-in-repo badge, rule count, kill state), `RuleEditor` (tenant, audience, segment, value, priority), `KillSwitch` with confirm and reason, `FlagHistory` reading PAP-38 audit events.
* Procedures used: `flags.list|update|kill` (PAP-366); a `flags.declared` procedure returning the generated `FlagKey` union so undeclared database keys show a warning badge.
* Storybook stories for the four states (empty, populated, killed, undeclared) at 375 and 1280.

Out: the evaluator, tables and hooks (PAP-366), segment authoring (PAP-195), experimentation statistics.

**Spec**

* Every mutation requires `can(actor, "flags.manage")` and writes an audit event with `reason`; the page shows the last ten events per flag.
* Kill switch confirm shows the affected tenant count and the propagation target (5 s).
* Rule conflicts (same tenant, two values) are prevented in the editor and rejected by the API with `FLAG_RULE_CONFLICT`.
* Reading works offline from the last `FlagSnapshot`; editing requires online and shows the PAP-234 `OfflineBanner`.

**Interface contract**

Provides: route `/settings/flags`, `FlagTable`, `RuleEditor`, `KillSwitch` components reused by PAP-538; consumed by PAP-88 (release train toggles), PAP-435, Atlas.

Consumes: `flags.*` procedures and `FlagKey` (PAP-366), `can` (PAP-59), form and table primitives (PAP-236, PAP-238), audit events (PAP-38), `OfflineBanner` (PAP-234).

**Definition of done**

* Playwright: staff toggles a flag for one tenant and the customer tab changes without reload; kill switch measured under 5 s; customer principal gets `DeniedState`.
* Screenshots at 375, 768, 1280, 1920 light and dark; a11y (axe) clean; CHANGELOG; Linear comment.

**Test plan**

* Unit: rule conflict detection in the editor reducer.
* Unit: undeclared-key badge from `flags.declared` diff.
* E2E: toggle, kill, history visible; `callAs(customer)` forbidden on `flags.update`.

**Demo**

Reviewer opens `/settings/flags`, adds a tenant rule for `dashboard.newChart`, sees the audit row appear, hits Kill with a reason and watches the rule table grey out. Under 90 seconds.

**Edge cases**

* Flag deleted from `flags.yaml` but rows remain: shown with an `undeclared` badge and a one-click archive.
* Thousands of rules: table virtualised, filter by tenant.
* Two staff edit the same rule: last write wins, both audit events shown (PAP-366 rule).

**Dependencies**

Hard: PAP-59, PAP-236; the evaluator and procedures half of PAP-366 (sibling work). Soft: PAP-38, PAP-234, PAP-195.

**Agent**

Builder: Iris (Component Crafter) with Forge on procedures. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/modules-settings-page` = PAP-538.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-366 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-366 blocks this issue (`blocks` relation).
