---
identifier: "PAP-598"
title: "Partner-managed tenants: partner organisation links, delegated administration across client tenants with scoped roles, a partner switcher and client-visible partner access history"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-227", "PAP-578"]
blocks: []
key: "r4/identity/partner-managed-tenants"
url: "https://linear.app/paperos/issue/PAP-598/partner-managed-tenants-partner-organisation-links-delegated"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:14.738Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 3
dueDate: null
cycle: null
---

# PAP-598: Partner-managed tenants: partner organisation links, delegated administration across client tenants with scoped roles, a partner switcher and client-visible partner access history

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Build M

**Goal**

Deferred to v0.2 (past 2026-10-01): the brief names partners and the audience model (PAP-55) has `partner` with `partnerId`, but nothing lets an agency, bookkeeper or reseller manage several client tenants from one account without being a full member of each. WorkOS, Auth0 and Stripe all model this as an organisation-to-organisation link with scoped delegated admin; PaperOS needs it for the agency and clinic business packs (PAP-427).

**Scope**

In: Table `tenant_link (partner_tenant_id, client_tenant_id, scopes text[], granted_by, accepted_at, revoked_at)`; procedures `partners.invite|accept|revoke|list`; partner principals resolve into a client tenant through `withTenant` with `attributes.partnerId` and a synthetic membership limited by `scopes` (roles from PAP-588); partner switcher (client list) in the console frame; client-side 'Partner access' section on the org settings page with history from audit rows; `partner` audience wiring so page specs can target partners; docs `docs/platform/partners.md`.

Out: Billing between partner and client (business-core), white-label domains (PAP-431), reseller pricing.

**Spec**

* A link is initiated by the client owner or accepted by them; scopes are a subset of the partner's requested roles; either side may revoke; revocation publishes `permission.changed`.
* Partner users act in the client tenant as `Principal { tenantId: client, attributes: { partnerId, role: <scoped role> } }`; RLS sees the client tenant; audit rows carry `partnerId`; impersonation (PAP-61) is not implied.
* Partner switcher lists client tenants with the granted role; switching remounts sync like a tenant switch (PAP-579).
* Clients see every partner access on their settings page and can revoke; a link expires if not accepted within 14 days.

**Interface contract**

Provides: Table `tenant_link`, procedures `partners.*`, partner resolution in `withTenant`, switcher entries, settings section, docs.

Consumes: Tenancy (PAP-578, PAP-579), policy engine (PAP-227), custom roles (PAP-588, soft), console frame (PAP-582, soft), audit (PAP-38), propagation (PAP-591, soft), audiences (PAP-55).

**Definition of done**

* Partner accepted with a `bookkeeper` scoped role can read and post invoices in the client tenant but cannot invite members; revocation ends access on the next request (compose tests).
* Switcher and settings section at 768 and 1280; audit history visible to the client; docs; changelog under Identity.

**Test plan**

* Unit: scope subset validation, expiry, principal resolution for partner users, revocation paths.
* E2E: client owner invites the seeded partner tenant, partner accepts, switches, acts, client revokes.

**Demo**

As the agency owner accept the client link, switch to the client, post an invoice, then as the client revoke and watch the partner lose the tenant from the switcher. Under two minutes.

**Edge cases**

* Partner is also a direct member of the client: direct membership wins; link redundant and shown as such.
* Client deleted: links revoked by the lifecycle job (PAP-432).
* Partner tenant suspended: all links suspended.

**Dependencies**

Blocked by PAP-578 and PAP-227 (hard). Soft: PAP-579, PAP-588, PAP-582, PAP-591, PAP-38, PAP-55, PAP-432. Deferred to v0.2; not claimable before 10-01.

**Agent**

Builder: Forge (Platform Engineer) with Iris on the switcher. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 5 round-4 file keys in this description to Linear identifiers: `r4/identity/console-frame` = PAP-582, `r4/identity/custom-roles` = PAP-588, `r4/identity/permission-propagation` = PAP-591, `r4/identity/tenancy-core` = PAP-578, `r4/identity/tenancy-ui` = PAP-579.
