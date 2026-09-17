---
identifier: "PAP-370"
title: "Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Developer", "Staff"]
milestone: "Local-first sync working"
state: "Backlog"
parent: null
children: []
blockedBy: []
blocks: []
key: "gap/data-layer/email-package"
url: "https://linear.app/paperos/issue/PAP-370/build-the-transactional-email-package-packagesemail-react-email"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:01:30.840Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-370: Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev

**Goal**

Every sender (magic links, invites, notifications, receipts, digests) calls one `sendEmail()` with the same sandbox, branding and compliance rules. PAP-57, PAP-58, PAP-136, PAP-180 and PAP-191 each wire Resend independently and only PAP-191 defines sandbox mode; PAP-214 picks the provider but ships no package. P0 identity issues call Resend directly at first and migrate here without changing their tests.

**Scope**

In:

* `packages/email`: `defineTemplate(name, schema, Component)` with React Email 4; `sendEmail(template, props, { to, tenantId, tags })` through a `Provider` adapter (`resend` default, `smtp` for Mailpit and self-hosted, `noop` for tests).
* Sandbox mode: outside production every address not on `EMAIL_ALLOWLIST` is rewritten to `sandbox+<hash>@PAPEROS_DOMAIN` and the original recorded.
* Suppression list `email_suppression` (bounces, complaints, unsubscribes) fed by provider webhooks; `sendEmail` refuses suppressed addresses.
* Per-tenant branding (logo, colours, footer) from PAP-72; layout components; plain-text alternative generated.
* `pnpm email:check` verifying SPF, DKIM and DMARC for the sending domain; `pnpm email:preview` dev server.
* Delivery through PAP-43 job `email.send` with retry; `email_log` table.

Out: marketing campaigns and sequences (PAP-191 builds on this), inbound parsing.

**Spec**

* Templates render in under 50 ms; total size under 100 KB; images hosted, not inlined.
* Every message carries `List-Unsubscribe` for non-transactional kinds and a tenant footer.
* Rate: provider limits respected by job concurrency.
* Logs never store bodies, only template name, props hash and status.

**Interface contract**

Provides (from `@paperos/email`): `defineTemplate`, `sendEmail`, `Provider` interface, tables `email_log` and `email_suppression`, job `email.send`, webhook route `POST /api/email/events`, env `EMAIL_PROVIDER`, `RESEND_API_KEY`, `SMTP_URL`, `EMAIL_ALLOWLIST`. Consumes: Resend domain and key (PAP-25), Mailpit (PAP-42), jobs (PAP-43), branding (PAP-72, soft), i18n (PAP-27, soft). Consumed by PAP-57, PAP-58 (migrate after landing), PAP-136, PAP-180, PAP-191, onboarding wizard.

**Definition of done**

* Magic-link and invite templates migrated; `sendEmail` in sandbox delivers to Mailpit locally and to the sandbox address on staging (screenshots).
* Suppression: a bounced address is refused on the next send (test).
* `email:check` passes on the sending domain; previews for every template at 375 and 600 px widths in light and dark.
* Vitest for allowlist rewriting, suppression, template schema; `docs/platform/email.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: sandbox rewrite for allowed, disallowed and mixed recipients; suppression refusal; template props validation.
* Integration (CI compose with Mailpit): send through `smtp`, assert message and plain-text part; provider webhook inserts a suppression row.
* Snapshot: HTML output per template.
* Visual: previews at two widths, light and dark; Gmail and Outlook rendering checked once via Litmus-style screenshots or documented manual check.

**Demo**

Reviewer runs `pnpm email:preview`, opens the invite template with sample props, then triggers an invite from the app and finds it in Mailpit at `localhost:8025` with the tenant footer. Under a minute.

**Edge cases**

* Provider outage: job retries; status `deferred` visible in the log.
* Recipient on suppression list but transactional (password reset): still refused; UI explains to contact support.
* Tenant branding missing: platform default.
* Large recipient list: one job per recipient, not one giant send.

**Dependencies**

PAP-25, PAP-43 (hard). Soft: PAP-42, PAP-72, PAP-27. Consumed by PAP-136, PAP-180, PAP-191, onboarding wizard; PAP-57 and PAP-58 migrate after landing.

**Agent**

Built by Forge with Iris on templates. Reviewed by Sentinel (Security Auditor for webhooks).

**Size**

M
