---
identifier: "PAP-712"
title: "Deny list: the `/request-approval` skill filing a Needs Justin card, MCP destructive-scope interception per character and the backstop matrix with `pnpm policy:backstops`"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: "PAP-298"
children: []
blockedBy: ["PAP-94", "PAP-106", "PAP-210", "PAP-710", "PAP-711"]
blocks: ["PAP-111", "PAP-280", "PAP-903"]
key: "r4/agents/request-approval-mcp-interception-and-backstops"
url: "https://linear.app/paperos/issue/PAP-712/deny-list-the-request-approval-skill-filing-a-needs-justin-card-mcp"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:39.238Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-712: Deny list: the `/request-approval` skill filing a Needs Justin card, MCP destructive-scope interception per character and the backstop matrix with `pnpm policy:backstops`

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build S

**Goal**

Second half of PAP-298: what happens when a blocked action is genuinely needed, how destructive MCP tools disappear from every character except Atlas, and the proof that every S0 rule is also enforced server-side so a bypassed hook still fails. Without the backstop matrix the deny list is advice; with it, it is a control Sentinel can audit.

**Scope**

* In: `.claude/skills/request-approval/` (SKILL.md, `scripts/file-card.ts`) producing a PAP-94 decision card and ending the session with footer `status: "approval-requested"`; orchestrator handling of the approved re-queue (`APPROVED_ACTION` in the prompt); bundle generator extension (PAP-106 sibling) removing `scope: destructive` MCP tools for all but Atlas and routing Atlas's through `approve`; `ops/security/backstops.yaml` mapping each rule to its independent control and owning issue; `pnpm policy:backstops` CI check; docs sections.
* Out: the rules and matcher (sibling), the controls themselves (forge rulesets PAP-46, Postgres roles PAP-30 and PAP-34, restricted Stripe keys PAP-359, Linear write proxy PAP-300).

**Spec**

* `/request-approval <action>`: validates the action against the policy (it must match an `approve` or `deny` rule), files a card `Decision needed: run <action>` with recommendation, blast radius from the rule's `reason`, rollback plan, options `approve | reject`, deadline 48 h, `hard-block: true` for S0; moves nothing; ends the session with the footer; the orchestrator re-queues the issue when Justin replies `approve`, injecting `APPROVED_ACTION: <id> <action> approved <at>` into the prompt so the hook allows exactly that command once (matched by hash) and logs `approved-action-used`.
* MCP interception: the PAP-210 catalog marks tools `scope: destructive`; the bundle generator wraps those servers with a tool filter so destructive tools are absent from every character's tool list except Atlas, whose calls hit `approve`; a probe in the PAP-106 probe suite asserts the tool list per character.
* Backstops: `backstops.yaml` `{ ruleId, control, issue, verify: test|manual }`; initial matrix: git rules to forge rulesets (PAP-46), db rules to `paperos_app` `NOBYPASSRLS` and tailnet-only Postgres (PAP-30, PAP-34), Linear rules to the write proxy allowlist (PAP-300), forge rules to bot token scopes (PAP-48), Stripe to restricted test keys (PAP-359), infra and secrets to credentials absent from sessions (PAP-300, PAP-280), comms to sandbox mode (PAP-190, PAP-191), agents to CODEOWNERS (PAP-305).
* `pnpm policy:backstops` fails CI when any S0 rule lacks a backstop or names an issue that is Canceled; PAP-219 `controls.yaml` gains `SEC-AGENT-*` entries generated from the matrix.

**Interface contract**

* Provides: skill `/request-approval`, footer status `approval-requested`, prompt variable `APPROVED_ACTION`, event `approved-action-used`, `backstops.yaml` schema, `pnpm policy:backstops`, MCP tool filter in bundles.
* Consumes: sibling policy and hook, PAP-94 `requestDecision()` and grammar, PAP-96 re-queue, PAP-106 bundles, PAP-210 scope classes, PAP-219 controls.

**Definition of done**

* `/request-approval` on a rehearsal issue produces a valid card; Justin's `approve` re-queues the issue and the approved command runs once and is logged (recording).
* MCP destructive tools absent from a Forge session's tool list, present for Atlas but denied and escalated (recording).
* `pnpm policy:backstops` passes with every S0 rule mapped; a seeded rule without a backstop fails CI (test).
* Docs; changelog under "Security"; Linear comment with recordings.

**Test plan**

* Unit: card rendering from a rule, approved-action hash match and single use, tool filter per character, backstop coverage check.
* E2E: rehearsal approval round trip on staging.

**Demo**

In a Forge session run `/request-approval 'docker volume rm paperos_staging'`; watch the card appear in Needs Justin; reply `approve`; watch the re-queued session run exactly that command and the hook log `approved-action-used`. Two minutes.

**Edge cases**

* Approved action drifts (different flags): hash mismatch denies; the session must request again with the exact command.
* Justin approves after the deadline: card expired; a new request is needed (no stale approvals).
* Backstop control is itself down (Forgejo offline): the hook still denies; the matrix documents which layer held.
* Atlas needs a destructive Linear action during planning: the write proxy (PAP-300) is the backstop and refuses regardless of the hook.

**Dependencies**

Hard: PAP-711, PAP-94. Soft: PAP-96, PAP-106, PAP-210, PAP-219, PAP-300, PAP-46, PAP-48, PAP-359, PAP-305.

* Soft dependency (round 4): PAP-96 is a soft dependency, not a `blocks` relation, because this issue's milestone (2026-09-24) is later than PAP-96's (2026-09-22); build against its interface and reconcile when it lands.
  **Agent**

Builder: Sentinel (Security Auditor) with Atlas (Dispatcher) for the re-queue. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/agents/deny-list-policy-file-and-hook` = PAP-711.
