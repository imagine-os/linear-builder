---
identifier: "PAP-431"
title: "Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-35", "PAP-178", "PAP-269"]
blocks: ["PAP-865", "PAP-868", "PAP-905", "PAP-909"]
key: "gap/app-shell/custom-domains"
url: "https://linear.app/paperos/issue/PAP-431/add-per-tenant-custom-domains-on-demand-tls-in-caddy-host-based-tenant"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:51.012Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-431: Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let a tenant serve PaperOS at `app.acme.com` with its own branding: Caddy issues certificates on demand for verified hosts, the API resolves the tenant by host, and a settings UI walks the tenant through CNAME plus TXT verification. PAP-178 sells a `whiteLabel` entitlement and PAP-35 resolves by subdomain, but nothing provisions domains today.

**Scope**

In:

* Table `tenant_domain` (`tenant_id`, `host`, `status pending|verified|active|failed`, `verification_token`, `verified_at`).
* Caddy on-demand TLS with an `ask` endpoint `GET /api/domains/allow?host=` that answers only for `active` hosts.
* Tenant resolution middleware in PAP-35 extended: header, subdomain, then `tenant_domain` lookup with a 60 s cache.
* Settings page `/settings/domains` with instructions, verification button and status; PAP-72 branding applied per host.
* Job `domains.verify` re-checking DNS hourly; entitlement check `whiteLabel` (PAP-178).

Out: email sending domains, apex domains without CNAME flattening (documented), custom domains for the marketing site.

**Spec**

* Verification: CNAME `app.acme.com -> tenants.PAPEROS_DOMAIN` and TXT `_paperos.acme.com = <token>`; both required.
* `ask` endpoint responds in under 50 ms from cache; certificates issued at first request.
* Removing a domain revokes routing immediately and lets the certificate expire.
* Auth cookies scoped per host; PAP-57 session works across the custom host through the same-origin API path.

**Interface contract**

Provides: table, oRPC `domains.add|verify|remove|list`, `GET /api/domains/allow`, host resolution in the tenant middleware, `useTenantHost()`. Consumes: Caddy on the host (PAP-25), tenant middleware (PAP-35), jobs (PAP-43), entitlements (PAP-178), branding (PAP-72), sessions (PAP-57).

**Definition of done**

* A test domain pointed at staging verifies, gets a certificate and serves the tenant with its branding (recording).
* Unverified host returns 404 from Caddy `ask`; removal stops routing within 60 s.
* Vitest for verification logic and resolution order; `docs/platform/domains.md`; settings page at 375, 768, 1280, 1920; CHANGELOG; Linear comment.

**Test plan**

* Unit: DNS answer parsing with fixtures (missing TXT, wrong CNAME target, both correct); resolution order with header, subdomain and host conflicts.
* Integration: `ask` endpoint against `active`, `pending` and unknown hosts; cache expiry.
* E2E: staging with a real test domain; Playwright asserts branding and sign-in on the custom host.
* Visual: settings page states at four widths.

**Demo**

Reviewer adds `demo.paperos-test.dev` in settings, sets the two DNS records shown, clicks Verify, then opens the domain in a new tab and lands on the tenant's branded sign-in page over HTTPS. Under 2 minutes once DNS propagates.

**Edge cases**

* Apex domain: instruct ALIAS or CNAME flattening; otherwise unsupported.
* Domain moved between tenants: old mapping removed first; unique `host`.
* Cloudflare proxied CNAME: works but documented certificate mode.
* Rate limits from Let's Encrypt: on-demand TLS limited to verified hosts only.

**Dependencies**

PAP-25, PAP-35, PAP-178 (hard). Soft: PAP-43, PAP-57, PAP-72.

**Agent**

Built by Forge (Ops Runner and Platform Engineer). Reviewed by Sentinel (Security Auditor).

**Size**

M
