---
identifier: "PAP-363"
title: "Build the default surfaces starter kit: customer portal and staff console page specs, a seeded demo tenant per audience and a first-run checklist for every generated app"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff", "Developer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-55", "PAP-117", "PAP-240", "PAP-361"]
blocks: ["PAP-364"]
key: "gp/app-shell/starter-surfaces"
url: "https://linear.app/paperos/issue/PAP-363/build-the-default-surfaces-starter-kit-customer-portal-and-staff"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:39.724Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-363: Build the default surfaces starter kit: customer portal and staff console page specs, a seeded demo tenant per audience and a first-run checklist for every generated app

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

A generated app must be a product on minute ten, not an empty shell: a landing page, a customer portal, a staff console with dashboard and settings, demo users for each audience, and demo data so the grid, comments and docs have something to show. This issue ships the fixed surfaces that entity-derived page specs do not cover, the deterministic demo tenant, and the first-run checklist that tells the next agent what to do.

**Scope**

In:

* Starter page specs in `packages/cli/templates/starter/specs/pages/`: `public/landing` (name, one sentence from the idea, sign in, sign up, layout `public`), `customer/home` (first verb card, recent records, notifications placeholder), `customer/account` (profile, sessions per PAP-220, export per PAP-221, locale per PAP-27), `staff/dashboard` (`ui.dashboardBlocks` with fallback `ui.responsiveGrid`: counts per entity, last ten audit events from PAP-38), `staff/agents` (agent principals and sessions per PAP-60 and PAP-113), `staff/docs` (in-app docs from PAP-128); settings pages come from the entity-derived generator.
* Copy interpolation: `{{app.name}}`, `{{idea.sentence}}`, `{{audience.label}}` resolved by the driver at creation time from `app.spec.yaml`; no other templating.
* Demo tenant seed `packages/db/seed/demo-tenant.ts` generated per app: tenant `demo`, one user per audience (`customer@demo.<app>.test`, `staff@...`, `owner@...`) with passkey-less magic-link sign-in in preview, 25 records per entity with realistic values by field type (faker seeded with the app id), three comment threads, five audit events; shapes follow the PAP-240 test-mode fixtures so gate 3 and gate 4 reuse them.
* `paperos seed demo [--reset]` command and the `/__test/seed` hook (PAP-240) both call the same function.
* First-run checklist `docs/app/README.mdx` generated from a template: URLs, demo accounts, what was generated, the six interview answers, the next five issues in the Linear project, how to add a page (`author-spec` skill, PAP-118), how to regenerate (`paperos gen`).
* Storybook stories for the six starter pages in the template app so Iris reviews them once.

Out: the entity CRUD pages (entity-derived page specs), notifications inbox (PAP-136), theming beyond `tenant.branding` (PAP-75), marketing site.

**Spec**

* Starter specs validate against PAP-114 with zero warnings and use only PAP-74 registered ids; they reference no entity by name, only `app.entities` iteration in `ui.dashboardBlocks` props.
* Landing page is the only anonymous route; everything else has `access.deny: [anonymous]` and the audience grants from PAP-55.
* Demo users are created with `attributes.demo: true` and cannot be promoted to owner of a non-demo tenant; preview environments only (`PUBLIC_ENV=preview|dev`), the seed refuses to run when `PUBLIC_ENV=production`.
* Records honour field types and constraints (unique fields distinct, relations resolve, dates within the last 90 days); comment bodies are two sentences without lorem ipsum.
* Seed idempotent: rerun without `--reset` upserts; with `--reset` truncates the demo tenant only (RLS scoped, PAP-34).
* README generation is a pure function of `app.spec.yaml`, `.paperos/golden-path.json` and `.paperos/interview.json`.

**Interface contract**

Provides: starter spec templates, `seedDemoTenant(db, app: AppSpec, opts): Promise<{ users, counts }>`, `renderFirstRun(app, goldenPath, interview): string`, and the demo account convention `<audience>@demo.<app>.test`. Consumes: `AppSpec` (PAP-117), fixture shapes and `/__test/seed` (PAP-240), audience ids (PAP-55), entity-derived page specs (routes to link from home and dashboard), auth sign-in flows (PAP-57, soft: magic link only), `ui.dashboardBlocks` (PAP-172, soft: `ui.responsiveGrid` fallback). Consumed by: golden path driver (copies templates, runs seed), golden path acceptance test (signs in as demo users), PAP-29, PAP-82 and PAP-85 (fixtures).

**Test plan**

* Unit: copy interpolation; README rendering snapshot for the clinic fixture; seed value generators per field type honour constraints.
* Integration (PAP-42 stack): seed the clinic app, assert 25 rows per entity, three threads, demo users can sign in via magic link through PAP-57 test mode, `--reset` leaves other tenants untouched.
* Visual: Storybook stories at 375 and 1280 pass gate 3 baselines.
* Safety: seed with `PUBLIC_ENV=production` exits 2 without touching the database.

**Definition of done**

* Six starter specs merged and validating; Storybook stories reviewed by Iris; screenshots at 375 and 1280 attached.
* Seed produces the documented counts for the three canned apps in under 10 s each.
* `docs/app/README.mdx` renders in-app for the clinic fixture with live URLs.
* Template guide (PAP-24) links the starter kit section; CHANGELOG; Linear comment with screenshots and seed timing.

**Edge cases**

* App with no customer audience: landing shows staff sign-in only; `customer/*` specs are skipped, not generated empty.
* Entity with a unique email field: seeded values are unique per row and per audience domain.
* Seed run while Electric shapes (PAP-36) are subscribed: writes go through the API so sync clients see them; direct SQL only for `--reset`.
* Idea sentence longer than 160 characters: truncated at a sentence boundary for the landing hero, full text in README.
* Preview database claimed from the warm pool already has a demo tenant: `--reset` runs automatically at C6.

**Dependencies**

Hard: PAP-117, PAP-240, PAP-55, entity-derived page specs. Soft: PAP-57, PAP-172, PAP-38, PAP-128, PAP-24. Blocks the golden path driver.

**Agent**

Built by Forge (Platform Engineer) with Iris (Interface Designer) for the six starter pages and Quill for the README template; reviewed by Sentinel.

**Size**

M: six specs, one seed module, one renderer, stories.

**Demo**

Preview URL of the clinic app signed in as `customer@demo` and as `staff@demo`, side by side at 1280, plus the rendered first-run README.
