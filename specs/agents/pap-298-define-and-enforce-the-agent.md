---
identifier: "PAP-298"
title: "Define and enforce the agent destructive-action deny list: policy file, PreToolUse hook, MCP destructive-scope interception with Needs Justin escalation, and server-side backstops"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent", "Developer"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-106", "PAP-210"]
blocks: ["PAP-96", "PAP-111", "PAP-280"]
key: "security/agent-deny-list"
url: "https://linear.app/paperos/issue/PAP-298/define-and-enforce-the-agent-destructive-action-deny-list-policy-file"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:08.408Z"
---

# PAP-298: Define and enforce the agent destructive-action deny list: policy file, PreToolUse hook, MCP destructive-scope interception with Needs Justin escalation, and server-side backstops

**Goal**

Turn "agents must never do X" from folklore into one machine-readable policy enforced in three layers: a deny list every session loads, a hook that blocks matching tool calls before they run, and server-side backstops (forge branch protection, Postgres roles, Stripe restricted keys, Linear proxy rules) that hold even if the hook is bypassed. PAP-106 hard-codes five deny patterns; this issue owns the full list and the escalation path when an agent legitimately needs a destructive action.

**Scope**

* In: `ops/security/agent-deny.yaml` (the list), `packages/agent-policy` (loader, matcher, explain), extension of the PAP-106 `enforce-scope.ts` PreToolUse hook to consult it, MCP interception for tools whose catalog scope is `destructive` (PAP-210), a `request-approval` skill that files a Needs Justin decision card (PAP-94) instead of acting, the backstop matrix mapping each rule to the server-side control that enforces it independently, adversarial test suite, `docs/security/agent-deny-list.md`.
* Out: OS sandboxing (PAP-280), least-privilege token minting (PAP-300), forge ruleset JSON itself (PAP-46), budget limits (PAP-111).

**Spec**

* Rule shape: `{ id: DENY-<area>-<nn>, area: git|fs|db|linear|forge|stripe|payroll|infra|secrets|comms|agents, match: { tool: string | glob, input: { <field>: regex } }, action: deny | approve, reason, backstop: [{ control, issue }], severity: S0|S1 }`. `deny` blocks with a message naming the rule; `approve` blocks and offers the approval path.
* Initial list (at least 45 rules), including: git `push --force*`, `push origin :<branch>`, `push origin main|release/*`, `branch -D main`, `tag -d`, `filter-repo`, `reflog expire`; fs `rm -rf` outside the worktree, writes to `ops/secrets/**`, `.claude/settings*.json`, `.claude/hooks/**`, `~/.ssh`, `*.age`, `.env*` in shared paths; db `DROP TABLE|SCHEMA|DATABASE`, `TRUNCATE`, `DELETE|UPDATE` without `WHERE` via psql or Drizzle raw, `ALTER ... DISABLE ROW LEVEL SECURITY`, `ALTER ROLE`, `SET app.bypass`, any statement against `pg-prod` hosts from a build session; linear `issueArchive`, `issueDelete`, `projectArchive|Delete`, `cycleArchive`, `customViewDelete|Update`, `teamUpdate`, `workflowStateArchive`, mutations on PAP-1..PAP-12, `issueUpdate` of `stateId` to `Done` or `Canceled`; forge `DELETE /repos/*`, branch-protection edits, secret or webhook edits, mirror changes, `gh repo delete|archive`, `gh api -X DELETE`; stripe any `sk_live_*` use, refunds, payouts, transfers, `customer.delete`, `subscription.cancel` outside test mode; payroll `run.submit|approve`; infra Coolify production deploy, `docker volume rm|prune`, `docker system prune -a`, `hcloud server delete`, DNS record edits, firewall edits, `sops --decrypt` on any file not in the character's `secretsFor`; secrets `env`, `printenv`, `cat /proc/*/environ`, `curl` with `@`-file bodies or `--data` to non-allowlisted hosts, base64 of secret paths; comms live email or SMS sends outside sandbox mode (PAP-191), social publish (PAP-190) without an approved queue item; agents `pnpm kill --all`, editing `roster.json`, `.claude/agents/**`, `ops/security/**` from a non-Sentinel character.
* Hook: `enforce-scope.ts` (PAP-106) loads the compiled `agent-deny.json` and evaluates rules after the allowlist; `deny` returns `permissionDecision: deny` with `DENY-<id>: <reason>. Use /request-approval if this is required.`; `approve` returns deny plus a hint; every hit is logged as `event: "deny-list-hit"` through PAP-107 with rule id, character, issue.
* MCP interception: the PAP-210 catalog marks tools `scope: destructive`; the bundle generator (PAP-106) wraps those servers so destructive tools are removed from the tool list for every character except Atlas, and for Atlas they route through `approve`.
* Approval path: `/request-approval` skill posts a PAP-94 decision card on the issue (`Decision needed: run <action>`, recommendation, blast radius from the rule, rollback plan), moves nothing, ends the session with footer `status: "approval-requested"`; the orchestrator re-queues the issue with the approved action recorded in the prompt when Justin replies `approve`.
* Backstops: for every rule a `backstop` entry names the independent control (forge ruleset PAP-46, `paperos_app` role `NOBYPASSRLS` PAP-30/PAP-34, Stripe restricted keys PAP-359, credential broker PAP-300 Linear proxy that refuses archive and delete mutations and its egress allowlist); `pnpm policy:backstops` prints rules with no backstop and fails CI if any S0 rule lacks one.
* Explain: `pnpm policy:explain "git push --force origin main"` prints matched rules.

**Interface contract**

* Provides: `loadPolicy(): Policy`, `evaluate(toolName, toolInput, ctx: { character, worktree }): { decision: allow|deny|approve, rule?, reason }`, compiled `packages/agent-policy/dist/agent-deny.json`, event `deny-list-hit`, skill `/request-approval`, doc table `docs/security/agent-deny-list.md` generated from YAML.
* Consumers: PAP-106 hook, PAP-96 launcher (refuses to start if `agent-deny.json` is stale), PAP-111 (three S0 hits in one session triggers `kill session`), PAP-81 security reviewer (flags code that adds tool wrappers bypassing the hook), PAP-219 `controls.yaml` (rules referenced as `SEC-AGENT-*`).
* Requires: PAP-106 bundle layout, PAP-210 scope classes, PAP-94 decision card format.

**Definition of done**

* `agent-deny.yaml` has at least 45 rules across all eleven areas, validates against its Zod schema, every S0 rule has a backstop.
* Adversarial suite: 40 prompts (one per rule family plus paraphrases such as `git push -f`, `git push --force-with-lease`, `rm -r -f`, `psql -c "delete from users"`) each produce a denial in the transcript; 10 benign near-misses (`git push origin forge/PAP-42`, `rm -rf node_modules` inside the worktree) are allowed.
* MCP destructive tools absent from a Forge session's tool list; present for Atlas but denied and escalated (recording).
* `/request-approval` produces a valid PAP-94 card on a rehearsal issue; Justin's `approve` reply re-queues the issue with the action authorised (recording).
* Docs; changelog under "Security"; Linear comment with the suite results table.

**Test plan**

* Unit: matcher on 200 fixture commands (glob, regex, path containment relative to worktree), YAML schema, backstop coverage.
* Integration: `claude -p` sessions at low effort with `maxTurns: 3` against the hook (reuses the PAP-106 harness); MCP tool-list diff per character.
* e2e: rehearsal issue on staging with approval round-trip.
* No UI.

**Demo**

In a Forge session ask it to `git push --force origin main`; the hook denies with `DENY-GIT-01` and the reason. Ask it to delete a Linear project; the tool is absent. Run `/request-approval` and watch the decision card appear in Needs Justin. Two minutes.

**Edge cases**

* Command chaining (`cd x && rm -rf /`, `sh -c`, heredocs, `xargs`, `eval`): the matcher tokenises shell with `shell-quote` and evaluates every sub-command; unparseable commands are denied with `DENY-SHELL-00`.
* Rule matches a legitimate migration (`DROP TABLE` inside a Drizzle migration file written by an agent): writing the file is allowed; executing it is `approve` unless the target is a per-worktree dev database (PAP-42 pattern `paperos_dev_*`).
* Justin's own sessions: policy is per character; the `justin` operator profile has `deny` only for secrets exfiltration rules.
* Stale compiled JSON: launcher refuses; `pnpm policy:build` fixes.
* Rule too broad blocks a whole issue: session posts the rule id and returns the issue to Backlog with label `policy-blocked`; Sentinel reviews the rule weekly.

**Dependencies**

Blocked by PAP-106 (hook and bundles), PAP-210 (scope classes). Blocks PAP-96 (launcher staleness check), PAP-111 (S0 hit escalation) and PAP-280 (the sandbox image ships the compiled `agent-deny.json`). Soft: PAP-94, PAP-46.

**Agent**

Built by Sentinel (Security Auditor sub-agent) with Atlas (Dispatcher) for the launcher hook; reviewed by Atlas.

**Size**

M
