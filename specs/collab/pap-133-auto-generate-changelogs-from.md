---
identifier: "PAP-133"
title: "Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Docs and prompt log stores"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-46"]
blocks: ["PAP-52"]
key: "collab/changelog"
url: "https://linear.app/paperos/issue/PAP-133/auto-generate-changelogs-from-conventional-commits-and-pr-summaries"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:53:28.970Z"
---

# PAP-133: Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant

**Goal**

Generate changelogs nobody writes by hand: conventional commits and PR summaries become `CHANGELOG.md`, per-release notes in the docs engine and per-tenant, per-audience “What's new” entries in the product, with a Claude rewrite from developer to human language. Moved to the first collab milestone because PAP-52 (release tags) consumes its CLI.

**Scope**

In:

* `packages/collab/changelog/` with `pnpm changelog build [--from <tag>] [--to HEAD]`: `conventional-commits-parser` 6 over commits with `Linear:` and `Character:` trailers (PAP-46); merged PR bodies fetched from Forgejo or GitHub, `## Summary` and `## Changelog` sections parsed per PAP-49 (`audience: internal|staff|customer`, `headline`, `group`, `tenants[]`).
* Classification via `changelog.config.ts`: scope → app or package; type → Added, Changed, Fixed, Security, Performance, Docs; `feat!` → Breaking.
* Outputs: `CHANGELOG.md` (Keep a Changelog), `docs/changelog/<version>.mdx` rendered by PAP-128, rows in `changelog_entry` (`id`, `tenant_id?`, `app_id`, `version`, `audience`, `section`, `headline`, `body_md`, `pr_url`, `issue_key`, `published_at`, `hidden`, `needs_review`).
* Rewrite: staff and customer entries rewritten by a Claude call with the Changelog Scribe prompt, stored beside the original, `needs_review` until Quill's pass or Justin's approval in the release digest (PAP-89).
* In-app "What's new": popover and `/_app/whats-new`, unread badge from `user_changelog_seen.last_version`; public `/_public/changelog`.
* Trigger: PAP-52 runs `changelog build` per tag; nightly "unreleased" preview.

Out: marketing posts (PAP-192), email announcements (notifications), feature flags.

**Spec**

* Deterministic ordering; regeneration per version is idempotent by hash.
* Entries link PR, issue and page spec via `SpecRef` when `specs/pages/*` changed.
* RLS `tenant_id is null or tenant_id = current`.
* Rewritten copy: headline under 90 characters, body under 60 words, no character names, present tense.
* Version from the tag; preview uses `next`.

**Interface contract**

Exposes: CLI `changelog build` and its JSON feed `docs/.generated/changelog/<version>.json` `{ version, date, entries: [{ id, audience, section, headline, body, prUrl, issueKey, specRef? }] }` (agreed first so PAP-52 can call it), table `changelog_entry`, oRPC `changelog.list({ audience, since })`, `changelog.markSeen(version)`, event `changelog.published { version, audiences[] }` for PAP-136, MDX pages under `docs/changelog/`. Consumes: commit trailer grammar from PAP-46, PR template sections from PAP-49, tag hook from PAP-52, `renderMdx` from PAP-128, digest approval flow from PAP-89.

**Definition of done**

* Running on paperos-template history produces a correct `CHANGELOG.md` for the first tagged release (link).
* Popover and page screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; public route shows only customer entries.
* `docs/collab/changelog.md` explains PR frontmatter; CHANGELOG entry about the changelog; Linear comment with generated files and screenshots.

**Test plan**

* Vitest: parser fixtures (20 commits incl. breaking, revert, merge, squash), scope mapping, section ordering, idempotent rebuild hash, rewrite output validation (headline length, forbidden words), `group` merging.
* Integration: build against a fixture git repo with two tags and mocked Forgejo PR API; the JSON feed matches a snapshot; a PR without `## Changelog` triggers the bot-comment call.
* Playwright: unread badge appears after seeding a new version and clears after viewing; anonymous `/_public/changelog` lists no `internal` or `staff` entries; run at 375 and 1280.
* Visual: Gate 3 baselines for popover and page at the seven widths, both themes.

**Demo**

Run `pnpm changelog build --from v0.1.0` on the template, open the generated `CHANGELOG.md`, then open `/_app/whats-new` to see the rewritten entries with the unread badge; open `/_public/changelog` in a private window and confirm only customer entries. Under two minutes.

**Edge cases**

* Non-conventional commit: goes to Internal, hidden from customers; reverts remove the reverted entry.
* Squash of ten commits: PR body wins for the summary.
* Rewrite fails or exceeds budget: original shown to staff, hidden from customers until reviewed.
* Hotfix tag: entry under the patch version and the next minor's Fixed.

**Dependencies**

PAP-46 (hard, encoded). Soft: PAP-49, PAP-52 (mutual; feed JSON agreed here first), PAP-128, PAP-89. Blocks PAP-52; consumed by PAP-192 and PAP-136.

**Agent**

Built by Quill (Changelog Scribe) with Forge on the release hook. Reviewed by Sentinel (Code Reviewer) and Beacon for customer copy rules.

**Size**

M: parsing and rendering are standard; the rewrite and review loop needs care.
