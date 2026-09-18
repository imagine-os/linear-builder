---
identifier: "PAP-172"
title: "Add saved views, personal vs shared views, public embeds and per-audience defaults"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: ["PAP-623", "PAP-624"]
blockedBy: ["PAP-59", "PAP-165", "PAP-229", "PAP-304", "PAP-343", "PAP-558", "PAP-614", "PAP-618", "PAP-630"]
blocks: ["PAP-173", "PAP-385", "PAP-839", "PAP-850", "PAP-855", "PAP-857", "PAP-909"]
key: "tables/view-sharing"
url: "https://linear.app/paperos/issue/PAP-172/add-saved-views-personal-vs-shared-views-public-embeds-and-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:37.011Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-172: Add saved views, personal vs shared views, public embeds and per-audience defaults

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make views first-class permissioned objects: personal versus shared views, per-audience defaults per dataset, public read-only links and embeds with expiry and password, view locking, and a switcher listing what the actor may see. This is what lets customers, staff and partners each experience the same dataset differently.

**Scope**

In: tables `view_share`, `view_default`; procedures `views.list|create|update|duplicate|delete|reorder|share|revoke|setDefault|resolveDefault|publicQuery`; `ViewSwitcher`, `ShareViewDialog`, `ViewSettingsSheet`; routes `/v/:token` and `/embed/v/:token`; permission actions `view.read|update|delete|share|lock`.

Out: per-field permissions on entity datasets (PAP-59 and specs), comments on public views.

**Spec**

* `visibility`: `personal` (owner only), `shared` (workspace policies), `public` (token). New views are personal; sharing requires `view.share`.
* `view_default (tenant_id, dataset_ref, audience_id, view_id)`; `resolveDefault(datasetRef, actor)` picks the most specific audience match (PAP-62), else first shared view, else a fresh personal grid; `page.spec.yaml` may pin `views.default`.
* `view_share`: `id, view_id, token (32-byte base64url, indexed), kind: 'link'|'embed', password_hash?, expires_at?, allow_export, allowed_fields jsonb, created_by, revoked_at, view_count, last_viewed_at`; token shown once.
* Public path runs as service principal `public-viewer` with `tenantId` from the share; `views.publicQuery({ token, cursor })` reuses PAP-163 with `allowed_fields` projection and `canEditRecords = []`; 120 per minute per IP and 10k per day per token; `argon2` password sets a signed 24 h cookie; `frame-ancestors` from the tenant allowlist only on `/embed/*`.
* `locked` blocks spec changes except for `view.lock` holders; temporary URL filters still work.
* Switcher groups "Your views / Shared / Public", search, drag reorder, `Ctrl+Shift+V`; commands `view.switch|new|duplicate`.
* Public view count is entitlement `publicViews` (PAP-178); creation goes through `assertWithinLimit`.

**Interface contract**

Provides: the procedures above, `<ViewSwitcher datasetRef />`, `<ShareViewDialog viewId />`, `resolveDefault`, `PublicViewPage`, embed snippet `<iframe src=".../embed/v/{token}?theme=">`, audit events `view.share.created|revoked`, `view.default.changed`, `view.public.password_failed`. Consumes: `can()` and `useCan` (PAP-227, PAP-229), audiences (PAP-62), audit (PAP-38), theming (PAP-74), entitlements (PAP-178), compiler (PAP-163), `GridView` embedded mode (PAP-165), rate limiting (PAP-267). Consumed by PAP-169 public forms, PAP-173 dashboard visibility, PAP-183 saved reports, PAP-189 per-audience CRM defaults.

**Definition of done**

* Vitest and integration below green; permission matrix generated via PAP-63 for the five actions.
* Storybook stories for switcher and dialog; screenshots at 375, 768, 1024, 1440, 1920 in three themes; embed page at 320 and 1024.
* `docs/views/sharing.md` with a security note; CHANGELOG; Linear comment with a live public view link.

**Test plan**

* Unit: default-resolution precedence (specific audience beats general beats first shared); share validation; token generation entropy.
* Integration: valid, expired, revoked, wrong-password and field-stripping cases through `publicQuery`; 121st request in a minute rejected; public view on an RLS entity returns zero rows without an explicit allow policy; entitlement limit enforced under 20 parallel creates.
* E2E: create a share, open `/v/:token` in a fresh context, confirm the hidden field is absent, revoke and see 410; embed in a test page with and without an allowed origin.
* Visual: matrix above.

**Demo**

Reviewer shares the grid demo publicly with a password and a hidden field, opens the link in a private window, enters the password, confirms the field is missing, then revokes and reloads to a 410 page. Under two minutes.

**Edge cases**

* Owner leaves the tenant: personal views deleted, shared views transferred to the workspace owner.
* Public view on an RLS entity: dialog warns "will show 0 records" from a preview count.
* Two audiences match: most specific wins, ties by `position`.
* Embed on a non-allowlisted site: blank via CSP, documented.
* Export on a public view: CSV capped at 10k rows and rate-limited.

**Dependencies**

PAP-165 (hard), PAP-59 children (hard), PAP-62, PAP-38, PAP-74, PAP-178 (soft, limit). Blocks PAP-173 (visibility), feeds PAP-169, PAP-183, PAP-189.

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor primary, Code Reviewer).

**Size**

M: clear data model; the care goes into the public path.
