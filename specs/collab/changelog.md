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
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-133: Auto-generate changelogs from conventional commits and PR summaries, rendered per app and per tenant

**Goal**

Generate changelogs nobody has to write: conventional commits and PR summaries become a repo `CHANGELOG.md`, per-app release notes in the docs engine, and per-tenant, per-audience "What's new" entries in the product, with a Claude pass that rewrites developer language into human language. Staff and customers see what changed the day it ships.

**Scope**

In:
- `packages/collab/changelog/` with `pnpm changelog build [--from <tag>] [--to HEAD]`: parses commits with `conventional-commits-parser` 6 (types, scopes, breaking notes, `Linear:` and `Character:` trailers from `forge/branch-policy`), fetches merged PR bodies through the Forgejo or GitHub API and extracts the `## Summary` and `## Changelog` sections defined in `forge/pr-templates` (`audience: internal|staff|customer`, optional `headline`).
- Classification: scope maps to app and package via `changelog.config.ts` (`scopes: { web: { app: 'paperos-template' }, ui: { package: '@paperos/ui' } }`); type maps to sections Added, Changed, Fixed, Security, Performance, Docs; `feat!` and `BREAKING CHANGE` produce a Breaking section.
- Outputs: `CHANGELOG.md` (Keep a Changelog format, developer audience), `docs/changelog/<version>.mdx` per release rendered by `collab/docs-engine`, and rows in `changelog_entry` (`id`, `tenant_id` nullable for global, `app_id`, `version`, `audience`, `section`, `headline`, `body_md`, `pr_url`, `issue_key`, `published_at`, `hidden`).
- Human rewrite: entries with `audience: staff|customer` are rewritten by a Claude call using the Changelog Scribe prompt (`packages/collab/changelog/prompts/rewrite.md`), stored beside the original, and marked `needsReview` until Quill's review pass or Justin approves in the release digest (`quality/review-report`).
- In-app "What's new": bell-adjacent popover and `/_app/whats-new` page listing entries for the viewer's audience and tenant, unread badge from `user_changelog_seen.last_version`; public `/_public/changelog` for customer entries.
- Trigger: `forge/release-tags` calls `changelog build` on each tag and commits the outputs; nightly job builds an "unreleased" preview into the docs.

Out: marketing posts (Beacon's Campaign Composer reads entries via `growth/content-agent`), email announcements (`collab/notifications` may deliver `changelog.published`), tenant-specific feature flags.

**Spec**

- Deterministic ordering: sections in fixed order, entries by PR merge time; regeneration for a version is idempotent (hash comparison).
- Entries link the PR, the Linear issue and, when the PR touched `specs/pages/*`, the page spec via `SpecRef`.
- Tenant scoping: entries are global unless the PR frontmatter lists `tenants: [slug]` (for tenant-specific work); RLS filters by `tenant_id is null or tenant_id = current`.
- Rewritten copy rules: one sentence headline under 90 characters, body under 60 words, no internal names (character names stripped), present tense.
- Version comes from the tag; unreleased preview uses `next`.

**Definition of done**

- Vitest: parser fixtures (20 commits including breaking, revert and merge), scope mapping, section ordering, idempotent rebuild, rewrite prompt output validation (headline length, forbidden words).
- Running on paperos-template history produces a correct `CHANGELOG.md` for the first tagged release (link).
- What's new popover and page screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark; unread badge clears after viewing; public route shows only customer entries (Playwright).
- Docs page per version renders in the docs engine; `docs/collab/changelog.md` explains PR frontmatter; CHANGELOG entry about the changelog.
- Linear comment with generated files and screenshots.

**Edge cases**

- Commit without a conventional type (merge commit, revert): reverts remove the reverted entry; unknown types go to an Internal section not shown to customers.
- PR body missing the `## Changelog` section: entry defaults to `audience: internal` and the PR gets a bot comment asking for it.
- Squash merge combining ten commits: PR body wins for the summary; individual commits still parsed for scopes.
- Rewrite call fails or exceeds budget: original developer text shown to staff, hidden from customers until reviewed.
- Same feature landed across three PRs: `changelog.group: <key>` frontmatter merges them into one entry.
- Tag on a hotfix branch: entry attached to the patch version and also listed under the next minor's Fixed section.

**Dependencies**

`forge/branch-policy` (hard, trailer and commit format). Soft: `forge/pr-templates` (frontmatter), `forge/release-tags` (trigger, which depends back on this issue for outputs, so agree the CLI name first), `collab/docs-engine`, `quality/review-report`. Consumed by `growth/content-agent`, `collab/notifications`.

**Agent**

Built by Quill (Changelog Scribe) with Forge on the release hook. Reviewed by Sentinel (Code Reviewer) and Beacon for customer-facing copy rules.

**Size**

M: parsing and rendering are standard; the rewrite and review loop needs care.
