---
identifier: "PAP-624"
title: "Public view links and embeds: view_share tokens, password and expiry, allowed_fields projection, /v/:token and /embed/v/:token with CSP and rate limits"
project: "tables"
projectName: "Table & Views Engine"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "View sharing, formulas, dashboards"
state: "Backlog"
parent: "PAP-172"
children: []
blockedBy: ["PAP-178", "PAP-304", "PAP-558", "PAP-623"]
blocks: ["PAP-173", "PAP-385", "PAP-625", "PAP-839", "PAP-850", "PAP-855", "PAP-857", "PAP-909"]
key: "r4/tables/public-view-links-and-embeds"
url: "https://linear.app/paperos/issue/PAP-624/public-view-links-and-embeds-view-share-tokens-password-and-expiry"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:18.866Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-624: Public view links and embeds: view_share tokens, password and expiry, allowed_fields projection, /v/:token and /embed/v/:token with CSP and rate limits

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Second half of PAP-172, the anonymous read path: share a view as a link or iframe embed with expiry, password, field projection and export control, executed as the `public-viewer` service principal with strict limits. Public forms (PAP-169 sibling) reuse the same token table.

**Scope**

In: table `view_share`; procedures `views.share|revoke|listShares|publicQuery|publicMeta`; `ShareViewDialog`; routes `/v/:token`, `/embed/v/:token`; `PublicViewPage`; CSP `frame-ancestors` middleware; audit topics; `docs/views/sharing.md` security section.

Out: saved views and defaults (sibling), comments on public views, public export formats beyond CSV (PAP-625).

**Spec**

* `view_share (id, tenant_id, view_id, token, kind: 'link'|'embed'|'form', password_hash?, expires_at?, allow_export, allowed_fields jsonb, allowed_origins text[], created_by, revoked_at, view_count, last_viewed_at)`; token 32 bytes base64url, indexed, shown once; `argon2id` password.
* `views.publicQuery({ token, cursor, tempFilter? })` resolves the share, sets `tenantId` from it, runs PAP-337's query as service principal `public-viewer` with `allowed_fields` projection and `canEditRecords = []`; 120 per minute per IP and 10k per day per token (PAP-304 buckets); password sets a signed 24 h cookie scoped to the token.
* Public views on RLS entity datasets return zero rows unless an explicit `public-viewer` allow policy exists (PAP-228); the dialog previews the count and warns "will show 0 records".
* `/embed/v/:token` sends `Content-Security-Policy: frame-ancestors <allowed_origins>` only; `/v/:token` sends `frame-ancestors 'none'`; both `X-Robots-Tag: noindex` unless `allow_index`; `?theme=light|dark` on embeds.
* Public view count is entitlement `publicViews` (PAP-178) through `assertWithinLimit`; audit `view.share.created|revoked`, `view.public.password_failed` (rate-limited to avoid log floods).
* `ShareViewDialog`: kind, expiry presets, password, export toggle, hidden fields multi-select, origins list for embeds, copy link and iframe snippet `<iframe src=".../embed/v/{token}?theme=" />`.

**Interface contract**

Provides: procedures above, `<ShareViewDialog viewId />`, `PublicViewPage`, `ViewShare` type (reused by the form sibling for `kind: 'form'`), embed snippet, CSP middleware `frameAncestorsFor(share)`, audit topics. Consumes: saved views (sibling), `views.query` (PAP-337), rate limits (PAP-304), entitlements (PAP-178), `toPredicate` policies (PAP-228), theming (PAP-75), audit (PAP-38), `ViewHost` embedded mode. Consumed by the form sibling, the export issue, PAP-193 landing pages.

**Definition of done**

* Vitest, integration and Playwright green; embed page at 320 and 1024 plus dialog at 375, 768, 1280 in three themes; axe clean.
* Security review comment (Sentinel Security Auditor) covering token entropy, password handling, CSP, RLS zero-row rule; `docs/views/sharing.md`; CHANGELOG; Linear comment with a live public link.

**Test plan**

* Unit: token entropy and one-time display; share validation; `allowed_fields` projection; CSP header builder; expiry maths.
* Integration: valid, expired, revoked, wrong-password, field-stripped cases through `publicQuery`; 121st request in a minute rejected; RLS entity view returns zero rows without an allow policy; entitlement limit enforced under 20 parallel creates.
* E2E: share the demo grid with a password and a hidden field, open `/v/:token` in a fresh context, enter the password, confirm the field is absent, embed in a test page with and without an allowed origin (blank via CSP), revoke and reload to 410.

**Demo**

Reviewer shares the demo grid publicly with a password and hidden Budget, opens the link privately, enters the password, confirms Budget is missing, then revokes and sees the 410 page. Under two minutes.

**Edge cases**

* Owner leaves the tenant: shares transferred with the view (sibling rule), tokens unchanged.
* Token pasted into a Slack unfurl: `publicMeta` returns title only, never rows.
* Password brute force: 10 failures per token per hour then 429 with `Retry-After`.
* Export on a public view: CSV capped at 10k rows and rate-limited (format details in the export issue).

**Dependencies**

PAP-623 (hard), PAP-304 (hard, rate limits), PAP-178 (soft, limit). Soft: PAP-228, PAP-75, PAP-38. Blocks the export issue; the form view's public path adopts the token table softly (it ships an internal path first).

**Agent**

Builder: Nova (Views Engineer). Reviewer: Sentinel (Security Auditor, Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/tables/saved-views-switcher-and-audience-defaults` = PAP-623, `r4/tables/view-export-csv-xlsx-ics-print` = PAP-625.
