---
identifier: "PAP-172"
title: "Add saved views, personal vs shared views, public embeds and per-audience defaults"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-165", "PAP-229", "PAP-59"]
blocks: ["PAP-173"]
key: "tables/view-sharing"
url: "https://linear.app/paperos/issue/PAP-172/add-saved-views-personal-vs-shared-views-public-embeds-and-per"
source: "plan/specs/bucket-6.json (round-1 canonical spec JSON)"
---

# PAP-172: Add saved views, personal vs shared views, public embeds and per-audience defaults

**Goal**

Make views first-class permissioned objects: personal versus shared views, per-audience default views for each dataset, public read-only links and embeds with expiry and password, view locking, and a views switcher that lists what the actor may see. This is what turns the engine into something customers, staff and partners each experience differently.

**Scope**

In:
- `view_share` table and oRPC procedures `views.list|create|update|duplicate|delete|reorder|share|revoke|setDefault`.
- `<ViewSwitcher />`, `<ShareViewDialog />`, `<ViewSettingsSheet />` in `packages/views/src/sharing/`.
- Public routes `/v/:token` (read-only view) and `/embed/v/:token` (iframe-friendly) in `apps/web`.
- Permission actions `view.read|update|delete|share|lock` wired into `identity/rbac-abac`.

Out: per-field permissions on entity datasets (that lives in the permission engine and specs), comments on public views.

**Spec**

- `view.visibility`: `personal` (only owner; stored per user), `shared` (workspace members per role policies), `public` (via token). Default new views are `personal`; "Share with workspace" flips to `shared` and requires `view.share`.
- Per-audience defaults: `view_default` table `(tenant_id, dataset_ref, audience_id, view_id)`; `views.resolveDefault(datasetRef, actor)` picks the most specific audience match from `identity/audience-model` segments, else the first shared view, else creates a personal grid. Pages declare `views.default` in `page.spec.yaml` for compile-time defaults.
- `view_share`: `id, view_id, token (32-byte base64url, unique, indexed), kind: 'link'|'embed', password_hash?, expires_at?, allow_export, allowed_fields jsonb (hidden fields stripped server-side), created_by, revoked_at, view_count, last_viewed_at`. Tokens are shown once at creation; rotating creates a new row.
- Public request path: `/v/:token` runs as the `service` principal `public-viewer` with `tenantId` from the share; `views.publicQuery({ token, cursor })` reuses the compiler with `allowed_fields` projection and forces `permissions.canEditRecords = []`; rate limit 120/min per IP and 10k/day per token; password via `argon2` check setting a signed cookie for 24 h; `X-Frame-Options` omitted only on `/embed/*` with `frame-ancestors` from the tenant's allowlist.
- Locking: `locked: true` blocks spec changes for everyone but `view.lock` holders; the toolbar shows a lock icon and temporary URL filters still work.
- Switcher: grouped "Your views / Shared / Public"; search; drag reorder (`position`); kind icons; keyboard `Ctrl+Shift+V`; commands `view.switch`, `view.new`, `view.duplicate`.
- Duplicate copies spec and options, not shares; deleting a view with shares revokes them and audits.
- Embed snippet: `<iframe src=".../embed/v/{token}" allow="clipboard-read" loading="lazy">` with a `theme` query param; the embed page hides chrome and uses tenant branding.
- Audit: share create/revoke, public view password failures (rate-limited) and default changes emit `audit_event`.

**Definition of done**

- Vitest for default resolution precedence and share validation; integration tests for token, expiry, password, revoked and field stripping cases.
- Permission matrix tests generated via `identity/permission-tests` for the view actions.
- Playwright: create share, open `/v/:token` in a fresh context, verify hidden field absent, revoke and see 410.
- Storybook stories for switcher and share dialog tagged `visual`; screenshots at 375, 768, 1024, 1440, 1920 in three themes; embed page screenshotted at 320 and 1024.
- `docs/views/sharing.md` including a security note; CHANGELOG entry; Linear comment with a live public view link.

**Edge cases**

- Personal view owner leaves the tenant: personal views are deleted with membership; shared views transfer to the workspace owner.
- Public view on an entity dataset with RLS: `public-viewer` principal has no rows unless an explicit `allow` policy exists; the share dialog warns "This view will show 0 records" using a preview count.
- Token pasted into a browser after expiry: 410 page with tenant branding, no data.
- Two audiences match a user (staff who is also a customer): the more specific segment wins; ties resolve by `position`.
- Embed inside a site not on the allowlist: blank with a CSP violation, documented for tenants.
- Export enabled on a public view: CSV limited to 10k rows and rate-limited.

**Dependencies**

- `tables/grid-view` (first view kind to share), `identity/rbac-abac`, `identity/audience-model`, `data-layer/audit-log`, `design-system/theming` for embed branding, `business-core/entitlements` (public views count as a plan limit).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor primary, Code Reviewer).

**Size**

M: clear data model; the care goes into the public path security.
