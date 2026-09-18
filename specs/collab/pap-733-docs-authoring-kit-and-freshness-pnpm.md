---
identifier: "PAP-733"
title: "Docs authoring kit and freshness: `pnpm docs new <template>`, Diátaxis templates, owner and review-date lint, stale-page job, was-this-helpful widget"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128"]
blocks: []
key: "r4/collab/docs-authoring-kit"
url: "https://linear.app/paperos/issue/PAP-733/docs-authoring-kit-and-freshness-pnpm-docs-new-template-diataxis"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.021Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-733: Docs authoring kit and freshness: `pnpm docs new <template>`, Diátaxis templates, owner and review-date lint, stale-page job, was-this-helpful widget

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Agents will write hundreds of docs in two weeks. Without templates and a freshness loop the docs engine becomes a landfill, the failure PAP-109 warns about for memory. Give writers `pnpm docs new`, four Diátaxis templates, lint for owners and review dates, a stale-page job that nudges owners, and the one-click feedback widget Mintlify readers expect.

**Scope**

In: `pnpm docs new <how-to|tutorial|reference|explanation|runbook> <slug> --owner <character> --audience <a>` in `packages/collab/docs/cli.ts` writing from `docs/_templates/*.mdx`; `pnpm docs:lint` rules `DOC_OWNER_MISSING`, `DOC_REVIEW_OVERDUE` (warn), `DOC_TEMPLATE_UNFILLED` (placeholder text left); frontmatter `reviewAt` (default `updated` + 90 days); nightly job `docs.freshness` posting one notification (`doc.review_due` kind) per owner per week; `DocFeedback` footer widget (thumbs up or down, optional 200-char note) writing `doc_feedback(tenant_id, path, vote, note, actor)` with a weekly rollup page `/_app/docs/health`. Out: translation, analytics beyond votes, editing UI (PAP-379).

**Spec**

* Templates follow Diátaxis: how-to (goal, steps, verify), tutorial (outcome, prerequisites, steps, next), reference (generated-first, tables), explanation (context, decision, consequences), runbook (symptoms, checks, fix, rollback); each carries `<!-- fill -->` markers the lint catches.
* `reviewAt` overdue pages show a `Review due` badge; `docs.freshness` groups by owner and sends one `doc.review_due` notification through the core; a page older than 180 days without review becomes a warning in the Gate 1 lint summary (never a failure).
* Feedback votes are anonymous for customers (actor null) and attributed for staff; notes pass the PAP-129 redactor before storage; rollup shows votes per page, down-vote notes and stale pages.
* `docs/_templates` are excluded from the sidebar and from `llms.txt`.
* Agent guidance: the `write-docs` note in CLAUDE.md says 'run `pnpm docs new`, never start from a blank file'.

**Interface contract**

Provides: CLI `docs new`, templates, lint rules, `reviewAt` frontmatter, kind `doc.review_due`, `DocFeedback`, table `doc_feedback`, page `/_app/docs/health`. Consumes: docs loader, frontmatter schema and lint (PAP-128), notification core (PAP-725, soft: log only when absent), jobs (PAP-43), redactor (PAP-129), `can()` (PAP-59). Consumed by: PAP-109 memory (templates), PAP-24, PAP-125 (docs pages adopt templates), Quill sessions.

**Definition of done**

* `pnpm docs new how-to add-a-page` creates a lint-clean file; leaving a `<!-- fill -->` marker fails `docs:lint`; a fixture page with `reviewAt` in the past triggers one notification in the job test.
* Widget screenshots at 375 and 1280 in light and dark; axe clean; health page renders votes from seeded feedback.
* `docs/collab/writing-docs.md` (written with the kit); CHANGELOG entry; Linear comment.

**Test plan**

* Unit: template rendering, lint rules, `reviewAt` default computation, weekly grouping by owner.
* Integration: job with `/__test` clock; feedback RLS via `callAs(customer)` (vote allowed, rollup denied).
* E2E (Playwright): vote down with a note, see it in the health page as staff.

**Demo**

Scaffold a runbook, run the lint and watch it fail on the placeholder, fill it, run again clean; vote on a page and open the health page. Under two minutes.

**Edge cases**

* Owner character no longer in the roster (PAP-104): lint warns, job routes to Quill.
* Feedback spam: 10 votes per actor per day; anonymous votes rate-limited per IP (PAP-304).
* Generated reference pages (PAP-732): exempt from `reviewAt`.

**Dependencies**

Hard: PAP-128. Soft: PAP-725, PAP-43, PAP-129, PAP-304, PAP-104.

**Agent**

Builder: Quill (Changelog Scribe). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/docs-reference-hub` = PAP-732, `r4/collab/notification-core` = PAP-725.
