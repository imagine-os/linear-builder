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
blockedBy: ["PAP-104"]
blocks: []
key: "growth/content-agent"
url: "https://linear.app/paperos/issue/PAP-192/create-the-content-agent-character-that-drafts-posts-and-emails-from"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-192: Create the content agent character that drafts posts and emails from changelogs and specs for human approval

**Goal**

Turn Beacon's Campaign Composer sub-character into a working content agent: a scheduled Claude session that reads merged changelogs, release digests and page specs, drafts social posts, announcement emails and landing copy in the tenant's voice, and files them as `pending_approval` items in the social scheduler and outreach templates. It never publishes; humans approve.

**Scope**

In:
- Character definition `packages/agents/characters/campaign-composer.yaml` completed per `agents/character-schema` (parent Beacon, model `claude-fable-5-1`, effort `high`, `permissionMode: dontAsk` with tools limited to Read, Grep, WebFetch and MCP `paperos-growth` write procedures for drafts only; deny Bash and any publish procedure), prompt `packages/agents/prompts/campaign-composer.md` (identity, voice rules, hard limits, output contract).
- Skill `.claude/skills/draft-campaign/SKILL.md`: inputs (changelog range or spec key, audience segment, channels), steps (gather sources, extract customer-facing changes, draft per-channel variants within limits from `growth/social-scheduler` adapters, self-review against the voice guide, file drafts), output (Linear comment with links to drafts).
- Voice guide `docs/growth/voice.md` per tenant override in `tenant.settings.brand.voice` (tone adjectives, banned words, reading level, emoji policy, CTA style).
- Triggers: Routine after each weekly release candidate (`quality/release-train`) and on demand via a Linear issue labelled `Campaign`; orchestrated by `pm-linear/orchestrator` like any character.
- Draft filing via oRPC: `social.posts.create({ status: 'pending_approval', source: 'agent' })`, `outreach.templates.create({ approved_by: null })`, `landing.drafts.create` (`growth/landing-forms`), each stamped with the agent principal (`identity/agent-principals`) and the source references (commit range, spec keys).
- Eval fixtures for `agents/eval-harness`: three changelog samples with golden drafts and a rubric (accuracy to changelog, no invented features, limit compliance, voice match).

Out: publishing, image generation (drafts reference media slots only), paid ads, A/B testing.

**Spec**

- Grounding rule: every claim in a draft must trace to a changelog line, spec field or doc; the agent appends a `sources` array; unsupported claims fail self-review and are dropped.
- Output contract JSON: `{ channel, variant_body, media_slots[], link_url, sources[], confidence }` validated by Zod before filing.
- Limits pulled from the adapter `validate` functions so drafts are never over length.
- One session drafts at most 10 items; cost cap from `agents/cost-controls` (`perSessionUsd` 3).
- Approval UI in the social queue shows "Drafted by Campaign Composer" with sources expandable; reject with reason feeds back as a memory note (`agents/memory`).
- Never reads customer PII beyond segment names; prompt forbids quoting contact data.

**Definition of done**

- Character validates (`pnpm agents validate`) and appears in the org chart; smoke task run transcript attached.
- Skill runs end to end against a real changelog range on staging producing at least: 3 X posts, 1 LinkedIn post, 1 announcement email template, 1 landing hero variant, all in `pending_approval`.
- Eval harness scores the three golden fixtures at or above 0.8 on the rubric; results posted to Linear.
- Vitest: output contract validation, limit enforcement, source tracing check.
- Screenshots of the approval queue showing agent drafts with sources at 375, 1024 and 1920.
- `docs/agents/campaign-composer.md` and voice guide; CHANGELOG entry; Linear comment with draft links and eval scores.

**Edge cases**

- Changelog contains only internal changes: agent files nothing and comments "no customer-facing changes" rather than inventing.
- Tenant has no voice settings: uses the PaperOS default guide and flags it in the comment.
- Spec marked `draft: true`: excluded from sources unless the request names it explicitly.
- Same release drafted twice (re-run): dedupe on `(source_hash, channel)`; existing drafts updated, not duplicated.
- Draft references a feature behind an entitlement: adds an audience note so approvers target the right segment.
- Model refusal or partial output: session ends with a Linear comment and no partial drafts filed.

**Dependencies**

`growth/social-scheduler` and `agents/roster-v1` (hard). `agents/skills-library`, `agents/eval-harness`, `agents/cost-controls`, `identity/agent-principals`, `collab/changelog` (source), `growth/outreach-sequences` and `growth/landing-forms` for the other draft targets (soft; skip channel if absent).

**Agent**

Built by Beacon (lead) with Quill drafting the prompt and voice guide. Reviewed by Sentinel (Code Reviewer, Security Auditor for tool scope) and Justin approving the character via one `Needs Justin` item.

**Size**

M: one character, one skill, filing procedures and evals; no new UI beyond queue badges.
