---
identifier: "PAP-831"
title: "Placeholder users from imports and invite conversion: people matched by email become placeholders, an owner invites them in bulk, and history re-points on acceptance"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-58", "PAP-201", "PAP-579"]
blocks: []
key: "r4/migration/placeholder-users-and-invite-conversion"
url: "https://linear.app/paperos/issue/PAP-831/placeholder-users-from-imports-and-invite-conversion-people-matched-by"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:51.880Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-831: Placeholder users from imports and invite conversion: people matched by email become placeholders, an owner invites them in bulk, and history re-points on acceptance

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Four importers (PAP-204's children, PAP-417 people, PAP-413, the Asana, Trello and Jira issue) create 'placeholder' users for assignees and authors and none defines what a placeholder is or how it becomes a real teammate. One model and one invite flow stop each importer inventing its own.

**Scope**

In: `placeholder_user (tenant_id, email citext, display_name, source, external_ids jsonb, created_by_run_id, converted_user_id?)` referenced by `pm_issue.assignee`, `pm_comment.author`, `crm_activity.created_by` and `import_run_item` through a `principal_ref` that allows `user|placeholder`; wizard step `PeopleMatching` (from the Linear child) writes here; bulk invite page `_app/settings/import/people` sending PAP-58 invitations with role presets; on acceptance a job re-points every reference to the real user and records `converted_user_id`; display components show placeholders with a dashed avatar and 'not yet invited' state; DSAR and purge rules (PAP-355) treat placeholders as PII.

Out: SCIM or directory sync, matching by name only (email or nothing), permissions for placeholders (they are never principals).

**Spec**

* Placeholders can never log in or hold sessions; `can()` treats them as absent; they exist only for attribution.
* Conversion is idempotent and resumable per table; the audit row for each re-point carries `reason: placeholder_convert:<id>`.
* Uninvited placeholders older than 180 days are listed for cleanup, never auto-deleted while referenced.

**Interface contract**

Provides: table and `principal_ref` type, `placeholders.*`, invite page, conversion job, `PlaceholderAvatar` component, wizard step integration. Consumes: mappings (PAP-201), invitations and memberships (PAP-58), PM and CRM tables (PAP-100, growth child), audit (PAP-38), retention (PAP-355), Linear child wizard step.

**Definition of done**

* Import fixture with 12 people creates placeholders; bulk invite sends through the sandboxed email package; acceptance re-points issues and comments in a test; screenshots at 375, 1024, 1920 light and dark; `docs/migration/people.md`; CHANGELOG.

**Test plan**

* Unit: email normalisation, principal ref validation, conversion idempotence, cleanup listing.
* E2E: import the recorded Linear fixture, open People, invite two placeholders, accept one in a second session and see the assignments now show the real user.

**Demo**

Reviewer imports the fixture, invites a placeholder, accepts the sandbox invite link as that user and watches their issues and comments attribute correctly. Under two minutes.

**Edge cases**

* Invitee's email differs from the placeholder's (alias): owner links manually before or after acceptance.
* Placeholder matches an existing member: converted immediately, no invite.
* Two placeholders for one person across sources: merge action combines them.

**Dependencies**

Hard: PAP-201, PAP-58. Soft: PAP-100, PAP-38, PAP-355, PAP-790, PAP-816.

**Agent**

Builder: Scout (Import Mapper) with Forge (Schema Wright). Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790, `r4/migration/linear-connector-and-pm-mapping` = PAP-816.
