---
key: "gap/app-shell/onboarding-wizard"
title: "Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard"
project: "app-shell"
parent: null
phase: "P1"
type: "Build"
priority: 1
size: null
surfaces: []
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/gaps-pending-0.json (agent0/gaps.py)"
linearDocument: null
status: "pending"
---

# Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard

**Goal**

Own the customer-facing half of PAP-5: a new user goes from first sign-in to a useful workspace in under five minutes. PAP-58 redirects new users to `/org/new` and PAP-33 says the UI handles onboarding, but no issue owns the flow; templates (PAP-207) and billing (PAP-177) have no entry point. This wizard is that entry point, with each step optional and resumable.

**Scope**

In:

* Route `/onboarding` with steps: organisation (name, slug, locale, timezone), business template (PAP-207 list with a blank option), invite team (emails and roles, sent through the email package), connect billing (Stripe Checkout via PAP-177, skippable on free plan), finish (seeded dashboard tour).
* Spec `specs/pages/onboarding.spec.yaml` driving the steps; progress persisted in `tenant.settings.onboarding` so refresh resumes.
* Seed application: chosen template imports through PAP-199 in the background with a progress banner.
* Staff view `/admin/onboarding` listing tenants by step reached (funnel), feeding PAP-194.

Out: marketing sign-up pages, plan pricing content, template authoring.

**Spec**

* Slug availability checked live; suggestions on collision.
* Steps are idempotent procedures `onboarding.createOrg|applyTemplate|invite|connectBilling|complete`; each records `completedAt`.
* Skipping billing marks the tenant `plan: free` with entitlements from PAP-178.
* Under 5 minutes measured by the PAP-29 harness as checkpoint C3a.
* Every step has empty, loading, error and success states per PAP-120 codegen.

**Interface contract**

Provides: procedures above, `tenant.settings.onboarding` shape `{ step, completed: string[], templateId?, startedAt }`, route `/onboarding`, funnel query `onboarding.funnel`. Consumes: organisation creation (PAP-58), templates (PAP-207, soft; blank template until then), invites and email (PAP-58 and the email package issue), Stripe Checkout (PAP-177, soft), import runner (PAP-199, soft), `AppShell` and routes (PAP-16), core entities (PAP-33).

**Definition of done**

* New user completes all five steps and lands on a seeded dashboard in under 5 minutes (recording, timed).
* Refresh mid-flow resumes at the same step; skipping billing yields a free-plan tenant.
* Playwright flow at 375 and 1280; screenshots of each step at seven widths; funnel page for staff.
* `docs/product/onboarding.md`; CHANGELOG; Linear comment with recording.

**Test plan**

* Unit: slug validation and suggestion; step state machine resume logic.
* Integration: each procedure via `callAs` twice (idempotent); invite sends one email per address through the email sandbox.
* E2E: Playwright full flow with the blank template; skip billing path; resume after reload.
* Visual: five steps at seven widths, light and dark.
* Timing: PAP-29 harness stamps the duration.

**Demo**

Reviewer signs in with a fresh magic link, names the organisation "Demo Clinic", picks the clinic template, invites one colleague, skips billing and arrives on a dashboard with sample bookings. Under 3 minutes.

**Edge cases**

* Invited user already has an account: membership added, no duplicate user.
* Template import fails midway: banner offers retry; dashboard still usable empty.
* Browser closed after org creation: next login resumes at step two.
* Stripe unavailable: billing step shows retry and can be skipped.

**Dependencies**

PAP-58, PAP-16, PAP-33 (hard). Soft: PAP-207, PAP-177, PAP-199, PAP-178, email package issue. Feeds PAP-29, PAP-194.

**Agent**

Built by Forge with Iris (Component Crafter) and Quill on copy. Reviewed by Sentinel (Visual Inspector).

**Size**

M
