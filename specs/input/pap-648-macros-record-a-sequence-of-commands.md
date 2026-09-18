---
identifier: "PAP-648"
title: "Macros: record a sequence of commands into a named macro, bind it to a chord or palette entry, share per workspace and expose it to agents"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-153", "PAP-291"]
blocks: []
key: "r4/input/macros-and-command-chains"
url: "https://linear.app/paperos/issue/PAP-648/macros-record-a-sequence-of-commands-into-a-named-macro-bind-it-to-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:21.142Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-648: Macros: record a sequence of commands into a named macro, bind it to a chord or palette entry, share per workspace and expose it to agents

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Justin's brief lists macros under multi-input control. Excel, VS Code and Keyboard Maestro let a power user record several steps into one shortcut. Because every action is already a command (PAP-151), a macro is a list of command invocations with arguments, recorded from the telemetry stream and replayed through the registry.

**Scope**

In: `packages/input/src/macros/{recorder,player,store,MacroPanel}.ts`; `Macro = { id, name, steps: { commandId, args, waitFor?: 'idle'|'navigation'|ms }[], scope, binding?: Chord[], visibility: 'personal'|'workspace', agentCallable }`; recorder toggled by `macro.record.start|stop`; player with step-by-step progress and abort; `/settings/keyboard` Macros tab; palette entries `macro:<id>`; procedures `macros.*`.

Out: conditional logic and loops (use automations, PAP-174), pointer-coordinate recording, cross-app macros.

**Spec**

* Recording listens to `command.executed` events (PAP-291) for the current window and captures `{ commandId, args }` with argument values serialised through `argsSchema`; commands flagged `macroSafe: false` (destructive without confirm, `agent.*`) are recorded as a confirm step instead of their args.
* Playback runs `registry.execute(step.commandId, step.args, 'macro')` sequentially, awaiting `waitFor` (default `idle` = no pending mutations from PAP-272 and no route transition) with a 10 s per-step timeout; a failing step stops the macro, shows the step index and offers retry or skip; the whole run is one undo entry (PAP-641).
* Bindings resolve through PAP-153's resolver as a `macros` layer between user overrides and page overrides; conflicts surface in the same UI; palette lists macros with a distinct icon and the step count.
* Storage: `user_preferences.macros` for personal, `workspace_macro` table for shared (`macro.share` permission), synced via PAP-143; export and import JSON with the PAP-153 keymap format.
* Agents: `agentCallable: true` macros run through `commands.execute` as a virtual command `macro:<id>` with the same audit rows per step (PAP-291).

**Interface contract**

Provides: `Macro` schema (in `contract-input`), `MacroRecorder`, `MacroPlayer`, `useMacros()`, `MacroPanel`, procedures `macros.list|create|update|delete|share`, commands `macro.record.start|stop`, `macro.run`. Consumes: telemetry and execute endpoint (PAP-291), resolver layer (PAP-153), palette (PAP-290), undo manager (PAP-641), idle detection (PAP-272), preferences sync (PAP-143), workspace permissions (PAP-229). Consumed by PAP-159 voice ("run macro X"), PAP-158 gamepad bindings.

**Definition of done**

* Record a three-step macro on the sample list page, bind it and run it by chord, palette and agent key; recording attached; screenshots of the Macros tab at 768 and 1280 in three themes; axe clean.
* `docs/platform/input/macros.md`; changelog; Linear comment.

**Test plan**

* Unit: recorder filtering and serialisation; `macroSafe` handling; player sequencing, timeouts and abort; binding layer precedence; import validation.
* Integration: `callAs(agent)` runs an `agentCallable` macro producing one audit row per step; a non-callable macro returns `NOT_CALLABLE`.
* E2E: record "filter to my open tasks, group by status, open the first record", stop, bind to `mod+shift+1`, reload, run it; break a step and see the failure UI.

**Demo**

Reviewer records a three-step macro in the demo grid, binds it and replays it with one chord, then runs it through `pnpm agent:cmd macro:<id>`. Under two minutes.

**Edge cases**

* Command removed in a later release: step marked unknown, macro disabled with a fix-it link.
* Recording while another macro plays: refused.
* Step needs an argument prompt (entity picker): recorded value reused; `promptOnRun: true` re-asks.
* Workspace macro edited by two users: last write wins, both notified.

**Dependencies**

PAP-291 (hard, telemetry and execute), PAP-153 (hard, binding layer). Soft: PAP-290, PAP-272, PAP-143, PAP-641.

**Agent**

Builder: Nova (Product Systems Engineer). Reviewer: Sentinel (Security Auditor, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/undo-manager` = PAP-641.
