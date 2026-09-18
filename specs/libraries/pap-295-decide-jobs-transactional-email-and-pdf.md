---
identifier: "PAP-295"
title: "Decide jobs, transactional email and PDF generation with Docker measurements: Inngest, Trigger.dev, BullMQ, pg-boss, Graphile Worker; Resend, Postmark, SES, Postal; Playwright PDF, react-pdf, Typst"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: "PAP-214"
children: []
blockedBy: ["PAP-209"]
blocks: ["PAP-296"]
key: "child/PAP-214/0"
url: "https://linear.app/paperos/issue/PAP-295/decide-jobs-transactional-email-and-pdf-generation-with-docker"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:09.338Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-295: Decide jobs, transactional email and PDF generation with Docker measurements: Inngest, Trigger.dev, BullMQ, pg-boss, Graphile Worker; Resend, Postmark, SES, Postal; Playwright PDF, react-pdf, Typst

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Research M

**Goal**

Settle the three server building blocks other projects are waiting on most: the job queue PAP-43 builds, the email transport PAP-57, PAP-136 and PAP-191 send through, and the PDF renderer PAP-180 uses, each measured in Docker on the shared VPS profile and recorded as ADRs. Time-box 4.5 hours.

**Scope**

In: `ops/compose/candidates/{jobs,email,pdf}/` compose files; `docker stats` after 5-minute warm-up under 50 req/s where applicable; scorecards with extras (self-host maturity, Postgres-native, RAM, TypeScript SDK, `docker compose up` story, tenant isolation, exit cost); email ADR covering DKIM, SPF, DMARC and a sandbox mode with allowlist for agent sessions; PDF ADR tested with an invoice containing CJK and RTL text; three ADRs; registry drafts.

Out: search, observability, flags, storage (sibling 2); validation and runtime (sibling 3); implementing anything.

**Spec**

* Redis acceptable only if two or more chosen services need it; Kubernetes-only candidates rejected.
* pg-boss is the incumbent (PAP-43 already names it); the ADR must confirm or reverse with numbers.
* Each ADR names consuming issue, exact package or image tag, env vars for PAP-17, fallback and migration hours.

**Interface contract**

Provides: ADRs `jobs`, `email`, `pdf` with the fields above, `results/backend-1.json`, compose files for winners under `ops/compose/`, a `@paperos/email` transport interface sketch (`send`, `sandbox`, `allowlist`) handed to data-layer, comments on PAP-43, PAP-57, PAP-136, PAP-180, PAP-191. Consumes: PAP-209 rubric, PAP-211 tiers, PAP-25 VPS profile numbers.

**Definition of done**

* Three ADRs accepted with Forge and Atlas approval; measured RAM table committed.
* Winner compose files start cleanly in CI on a Forgejo or GitHub runner.
* Consuming issues commented with the decision.

**Test plan**

* CI job `compose-smoke` runs `docker compose up --wait` for each winner and a health probe.
* `pnpm lib score` validates scorecards; evidence URLs required.
* PDF fixture rendered and visually checked at A4 with CJK and RTL text.

**Demo**

Reviewer reads the jobs ADR, runs `docker compose -f ops/compose/jobs.yml up`, enqueues a sample job from the README and sees it complete; opens the rendered CJK invoice PDF. Under two minutes.

**Edge cases**

* Candidate self-hosting is license-gated (Inngest, [Trigger.dev](<http://Trigger.dev>) tiers): score the self-host path only and verify the tier.
* Email provider blocks unverified domains: sandbox mode documented; DNS setup becomes a Justin task.
* PDF fonts missing in the container: font bundle listed in the ADR.

**Dependencies**

PAP-209 (hard; draft acceptable), PAP-211 (soft), PAP-25 (soft). Blocks PAP-43 (via parent relation). Informs PAP-57, PAP-136, PAP-180, PAP-191.

**Agent**

Researched by Scout (Library Evaluator) with Forge (Ops Runner) for measurements. Reviewed by Forge and Atlas.

**Size**

M
