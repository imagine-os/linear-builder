---
identifier: "PAP-894"
title: "Build the platform super-admin console at /admin: tenant list and detail, entitlement overrides, flag rules, module toggles, jobs and dead-letter queue, usage and health, every action audited and MFA-gated"
project: "platform-ops"
projectName: "Platform Operations, Analytics & Compliance"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "Ops contract, super-admin console and status page"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-43", "PAP-55", "PAP-61", "PAP-63", "PAP-178", "PAP-220", "PAP-266", "PAP-366", "PAP-565", "PAP-581", "PAP-583", "PAP-893"]
blocks: ["PAP-900", "PAP-901", "PAP-907"]
key: "r4/platform-ops/superadmin-console"
url: "https://linear.app/paperos/issue/PAP-894/build-the-platform-super-admin-console-at-admin-tenant-list-and-detail"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:48.843Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-894: Build the platform super-admin console at /admin: tenant list and detail, entitlement overrides, flag rules, module toggles, jobs and dead-letter queue, usage and health, every action audited and MFA-gated

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

Give Justin and platform staff the console PaperOS itself has been missing: a `/admin` surface for the `platform` audience, separate from the tenant console (PAP-63), listing every tenant with plan, usage, health and lifecycle state, with tabs to override entitlements, set per-tenant flag rules, toggle modules, inspect jobs and drain the dead-letter queue, start an audited impersonation, and see errors and sync lag, where every action requires a fresh MFA step-up and writes an audit row with a reason.

**Scope**

In: `apps/web/src/admin/` routes under `/admin` (specs per page) on the PAP-70 `AppFrame` with `admin.nav` slot: Tenants (grid over a `platform_tenants` dataset: name, plan, state PAP-432, seats, storage, MRR, health score, last active), Tenant detail tabs via `admin.tenant.tabs`: Overview, Entitlements (PAP-178 overrides as a JSON-with-form editor), Flags (PAP-366 rule editor scoped to the tenant), Modules (PAP-266 toggles with dependency warnings), Jobs (PAP-43 queue and DLQ filtered by tenant, retry and discard), Usage (PAP-391), Errors (PAP-368 reports), Sync (PAP-328 lag), Audit (PAP-38 for the tenant), Impersonate (PAP-61 handoff). Platform-wide pages: Flags (all rules), Jobs (global DLQ), Releases (PAP-254 RC state), Announcements (`scope: platform` when engagement exists), Platform audit. `PlatformAdminPort` adapter: procedures under `admin.*` requiring `audience: platform`, `mfaAge < 10 min` (PAP-220 step-up), and a `reason` string on every mutation; audit rows carry `actor_kind: platform`. Security: `/admin` served only on the platform host (never tenant domains, PAP-431), CSP and headers per PAP-219, IP allow-list optional, session idle timeout 15 minutes, every page in the PAP-64 permission matrix tests.

Out: Tenant-facing settings (PAP-63 and PAP-912). Billing operations beyond overrides (Stripe dashboard is the tool). Metrics dashboards beyond links into Grafana (PAP-40).

**Spec**

* Overrides are typed and time-boxed by default (expiry required, max 90 days without a Needs Justin note); expiry job reverts and notifies
* Flag rule edits from the console go through the same PAP-366 procedures and appear in the flag audit; a kill switch is one click with confirmation
* DLQ actions: retry with the original payload, discard with reason, or open a Linear issue prefilled (PAP-97 pattern); bulk limited to 50
* Impersonation entry shows the PAP-61 consent and banner rules; exit returns to the tenant detail
* The console is itself a module (`platform-ops`), so a tenant without the `platform` audience never loads its routes or bundle chunk

**Interface contract**

Provides: `/admin` routes and pages, `PlatformAdminPort` default adapter, `admin.*` procedures, `platform_tenants` dataset, slots `admin.nav` and `admin.tenant.tabs`, `platform.tenant.overridden` and `platform.flag.changed` events. Consumes: tenant console patterns (PAP-63), platform audience (PAP-55), MFA step-up and sessions (PAP-220), flags (PAP-366), module toggles (PAP-266), entitlements (PAP-178), jobs and DLQ (PAP-43), impersonation (PAP-61), audit (PAP-38), usage (PAP-391), error reports (PAP-368), sync lag (PAP-328), RC state (PAP-254). Consumed by: PAP-901 (renders scores), PAP-900 (quarantine actions), PAP-902 (profile view), every module needing a per-tenant admin action, PAP-89 digest links.

**Definition of done**

* Console live on staging behind the platform audience; override, flag rule, module toggle, DLQ retry and impersonation each produce an audit row with reason and require step-up; permission matrix tests prove non-platform principals get `DeniedState`; screenshots at 1024 and 1920
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: override expiry logic; reason validation; bulk limits.
* Integration: step-up enforcement (stale MFA rejected); tenant-host request to `/admin` returns 404; DLQ retry replays the original payload once.
* E2E: tenant search, open detail, set an expiring override, flip a flag, retry a DLQ job, start and exit impersonation; keyboard navigation.
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

Search the demo tenant in `/admin`, grant a 7-day `assistant` entitlement override with a reason after an MFA prompt, flip its `module.tables.impl` flag to `next`, retry a dead-lettered job and show all three in the platform audit.

**Edge cases**

* Two platform admins edit the same override: last write wins with the audit showing both; the UI warns on stale data (PAP-144 banner)
* Platform admin who is also a tenant member: the audiences are separate sessions contexts; `/admin` never inherits tenant scope and impersonation is explicit
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-893 (hard), PAP-63, PAP-55, PAP-220 (hard), PAP-366, PAP-266, PAP-178, PAP-43, PAP-61, PAP-38 (hard), PAP-391, PAP-368, PAP-328, PAP-254 (soft).

**Agent**

Builder: Forge. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/app-shell/settings-registry` = PAP-912, `r4/platform-ops/abuse-controls` = PAP-900, `r4/platform-ops/compliance-profiles` = PAP-902, `r4/platform-ops/contract-publish` = PAP-893, `r4/platform-ops/tenant-health-scores` = PAP-901.
