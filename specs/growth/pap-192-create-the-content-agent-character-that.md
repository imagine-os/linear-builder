---
identifier: "PAP-192"
title: "Create the content agent character that drafts posts and emails from changelogs and specs for human approval"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Campaigns and social"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-104", "PAP-287"]
blocks: []
key: "growth/content-agent"
url: "https://linear.app/paperos/issue/PAP-192/create-the-content-agent-character-that-drafts-posts-and-emails-from"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:19.840Z"
---

# PAP-192: Create the content agent character that drafts posts and emails from changelogs and specs for human approval

**Goal**

Turn Beacon's Campaign Composer into a working content agent: a scheduled Claude session that reads merged changelogs, release digests and page specs, drafts social posts, announcement emails and landing copy in the tenant's voice, and files them as `pending_approval` items. It never publishes.

**Scope**

In: character `packages/agents/characters/campaign-composer.yaml` (parent Beacon, `claude-fable-5-1`, effort high, `permissionMode: dontAsk`, tools Read, Grep, WebFetch and `paperos-growth` draft procedures only, Bash and publish procedures denied); prompt `prompts/campaign-composer.md`; skill `.claude/skills/draft-campaign/SKILL.md`; voice guide `docs/growth/voice.md` with `tenant.settings.brand.voice` overrides; Routine after each release candidate (PAP-88) and on the `Campaign` label; eval fixtures for PAP-110.

Out: publishing, image generation, paid ads, A/B testing.

**Spec**

* Grounding: every claim traces to a changelog line, spec field or doc; the agent emits a `sources[]` array; unsupported claims fail self-review and are dropped.
* Output contract `{ channel, variant_body, media_slots[], link_url, sources[], confidence }` validated by Zod before filing.
* Limits from PAP-190 `validatePost` when it exists, otherwise the `platformLimits` constant (see Dependencies); drafts never exceed platform lengths.
* Filing: `social.posts.create({ status: 'pending_approval', source: 'agent' })`, `outreach.templates.create({ approved_by: null })`, `landing.drafts.create`, each stamped with the agent principal (PAP-60) and source references.
* At most 10 items per session; `perSessionUsd` 3 via PAP-111; dedupe on `(source_hash, channel)`.
* Queue UI shows "Drafted by Campaign Composer" with expandable sources; rejection reasons become PAP-109 memory notes.
* Never reads contact PII; the prompt forbids quoting contact data.

**Interface contract**

Provides: character and skill definitions, `CampaignDraft` Zod schema, Routine definition `campaign-after-rc`, eval task `campaign-composer` with three golden fixtures and rubric, `drafted_by` badge component for approval queues. Consumes: roster and schema (PAP-104, PAP-103), skills format (PAP-105), evals (PAP-110), cost controls (PAP-111), memory (PAP-109), agent principals (PAP-60), changelog feed (PAP-133), draft procedures (PAP-190 soft, with the `campaign_draft` fallback in Dependencies; PAP-191 and PAP-193 soft, channel skipped if absent), orchestrator (PAP-96).

**Definition of done**

* Character validates (`pnpm agents validate`) and appears in the org chart; smoke transcript attached.
* Skill run on staging against a real changelog range files at least three X posts, one LinkedIn post, one email template and one landing hero variant in `pending_approval`.
* Eval scores at or above 0.8 on the three fixtures, posted to Linear.
* Screenshots of the queue with agent drafts at 375, 1024, 1920.
* `docs/agents/campaign-composer.md` and voice guide; CHANGELOG; Linear comment with draft links and scores.

**Test plan**

* Unit: output contract validation, length enforcement per channel, source-tracing check rejects a claim without a source, dedupe key.
* Integration: skill run with a fixture changelog through the PAP-110 runner produces drafts through the real procedures on a test tenant; tool scope test asserts a publish call is denied.
* E2E: approval queue shows the agent badge and sources; reject with reason writes a memory note.
* Visual: queue at the three widths in light and dark.

**Demo**

Reviewer triggers the Routine manually with a recent changelog range, waits for the session summary comment, opens the social queue to read three drafts with their sources, and rejects one with a reason. Under two minutes after the session ends.

**Edge cases**

* Internal-only changelog: agent files nothing and says so.
* No voice settings: default guide, flagged in the comment.
* Spec marked `draft: true` excluded unless named.
* Re-run on the same release updates existing drafts.
* Model refusal or partial output: comment posted, nothing filed.

**Dependencies**

PAP-104 (hard), PAP-105, PAP-110, PAP-111, PAP-109, PAP-60, PAP-133, PAP-96. PAP-190 soft (relation `PAP-190 blocks PAP-192` removed on 2026-09-17, FIX-4; PAP-190 is labelled `Deferred`, v0.2): this agent drafts and never publishes, so it does not wait for the scheduler. If `social.posts.create` does not exist when you start, file social drafts through `campaign.drafts.create` into a `campaign_draft (id, tenant_id, channel, variant_body, media_slots jsonb, link_url, sources jsonb, confidence, status: pending_approval|approved|rejected, source: agent, source_hash, created_by_principal)` table owned by this issue, shown in the same approval queue UI, and enforce lengths with a `platformLimits` constant (X 280, LinkedIn 3000, YouTube title under 100) copied from the PAP-190 spec with a `// TODO(PAP-190): replace with validatePost` marker; PAP-190 imports approved rows when it ships. PAP-191 and PAP-193 soft (channel skipped if absent). Justin approves the character once via Needs Justin.

**Agent**

Builder: Beacon (lead) with Quill on prompt and voice guide. Reviewer: Sentinel (Code Reviewer, Security Auditor for tool scope).

**Size**

M: one character, one skill, filing procedures and evals.
