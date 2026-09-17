import os
"""Milestone date fix, project Contract sections, umbrella comments, PAP-136 re-push."""
import sys, json
sys.path.insert(0, os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2/agent3")
import r3, rw_collab
DRY = "--dry" in sys.argv
ch = r3.load_changes()
cur = json.load(open(r3.A3 + "/project_current.json"))
CUR = {v["id"]: v for v in cur.values()}

CONTRACTS = {
"collab": """

## Contract

**Provides**

* Docs engine (PAP-128): `DocEntry`, `renderMdx()`, MDX components (`Callout`, `Steps`, `Tabs`, `FileRef`, `SpecRef`, `Mermaid`, `IssueRef`), routes `/_app/docs/$` and `/_public/docs/$`, `docs/.generated/history.json`, `pnpm docs:lint` in Gate 1, block anchors `data-block-id`.
* Prompt log (PAP-129, PAP-135): tables `prompt_session`, `prompt_event`, `prompt_model_price`; ingest `POST /api/v1/prompt-log/events` with `PromptEventIn` in `packages/contracts`; oRPC `promptLog.*`; permalink `/_app/dev/prompt-log/<sessionId>?seq=`.
* Decision log (PAP-130): `AdrFrontmatter`, `adr-index.json`, `pnpm adr new|lint|index`, Linear comment format for status changes.
* Comments (PAP-131): `comment_thread`, `comment`, `CommentAnchor` union and `anchorKey()`, oRPC `comments.*`, `CommentableRoot`, `useThreads()`, events `comment.created|mentioned`, `thread.resolved`, deep link `?thread=`.
* Canvas (PAP-132): `PaperCanvas`, `registerNodeType()`, `CanvasOverlayDoc` Yjs schema, `canvas.graph.get`, `packages/collab/canvas/types.ts` shared with PAP-123.
* Changelog (PAP-133): `changelog build` CLI and JSON feed, `changelog_entry`, `changelog.list|markSeen`, event `changelog.published`.
* Rules registry (PAP-134): `RuleObject`, `rules-index.json`, oRPC `rules.*`, search kind `rule_skill`.
* Notifications (PAP-136, now P1): `defineKind()`, `registerChannel()`, `Channel`, `notify()`, `resolvePreferences()`, tables `notification*`, `NotificationBell`, inbox and preference routes, unsubscribe route.
* QA viewer (PAP-137): `AnnotationViewer`, screenshot anchors, `buildVisualIssue()`. Search (PAP-138): `search.query`, `SearchProvider`, seven kind registrations, health page.
* Planned once the Linear issue limit is lifted (specs in `round2/agent3/pending-issues.json`): runtime docs store (`doc_page`, `docs.pages.*`), in-app help (`HelpPanel`, spec `help.*` fields), and child issues for PAP-131, PAP-132, PAP-136.

**Requires**

* data-layer: core entities and migrations (PAP-33, PAP-32), oRPC server, contract package and `callAs` (PAP-267, PAP-268), RLS helpers (PAP-34, PAP-228), search registry (PAP-39), file storage (PAP-37), jobs (PAP-43), observability (PAP-40), shape proxy and read hooks (PAP-270, PAP-271), planned event bus and email package.
* realtime: Hocuspocus provider and rooms (PAP-140), presence payload (PAP-141), `RichTextEditor`, `renderRichText`, `richTextToPlain` (PAP-142), `subscribeShape` (PAP-143).
* identity: `can()` and policies (PAP-59, PAP-227), sessions (PAP-223), agent principals and `ActorBadge` (PAP-60), audiences (PAP-55).
* app-shell: routes and slots (PAP-16), env (PAP-17); design-system: primitives, layout, data display, tokens, email kit (PAP-67, PAP-70, PAP-71, PAP-66, PAP-235); spec-builder: schema and `FlowGraph` (PAP-114, PAP-123); forge: trailers, PR template, tags, Forgejo API (PAP-46, PAP-49, PAP-52, PAP-45); pm-linear: Linear client and webhooks (PAP-101, PAP-97), Justin queue rules (PAP-94); quality: media manifests and video (PAP-82, PAP-83, PAP-84, PAP-239), test mode (PAP-240); agents: skills and roster (PAP-105, PAP-104); libraries: rubric and license policy (PAP-209, PAP-211).

**Milestone exit criteria**

* Docs and prompt log stores (2026-09-20, moved from 09-21 so PAP-129 precedes PAP-107): PAP-127 ADR accepted; PAP-128 renders twenty docs at seven widths with history; PAP-129 ingests the 20-turn fixture on staging under RLS; PAP-130 fifteen seed ADRs indexed in-app; PAP-133 `changelog build` produces the first tagged release file (moved here so PAP-52 can consume its CLI).
* Comments and canvas (2026-09-26): PAP-131 two-context comment test green with a Linear issue created; PAP-132 canvas at 55 fps on 300 nodes with collaborative moves; PAP-134 rules browsable with history and a PR proposed; PAP-135 Justin replays a real session; PAP-136 work package 1 delivers `issue.needs_justin` and `review.gate_failed` in-app and by email.
* Knowledge surfaced everywhere (2026-09-30): PAP-136 inbox, digests and Slack merged; PAP-137 one real visual finding confirmed through the viewer; PAP-138 palette search over the seeded corpus with p95 under 300 ms and audience isolation proven.
""",
"realtime": """

## Contract

**Provides**

* CRDT decision (PAP-139): ADR with library, encoding `updateV2`, snapshot cadence and pinned versions; `CrdtAdapter` bench harness.
* Collab server (PAP-140): `createDocProvider({ room, token, ephemeral? })`, room grammar `doc:|page:|canvas:<tenant>:...`, close codes `4401|4403|4413`, tables `yjs_documents`, `yjs_updates`, metrics `collab_*`, `wss://collab.<domain>`.
* Presence (PAP-141, PAP-146): `PresenceState` schema (with `agent?` extension), `PresenceProvider`, `usePresence()`, `useViewers()`, `PresenceAvatars`, `LiveCursor`, `AgentAvatar`, `ActivityChip`, DOM attribute `data-presence-surface`, `createAgentPresenceClient()` for PAP-107.
* Editor (PAP-142): `RichTextEditor` (`full|comment|inline`), `richTextSchema`, `renderRichText()`, `richTextToPlain()`, `MentionSource`, markdown converters, command ids `editor.*`.
* Record sync (PAP-143): `useRecord()`, `useRecordChanges()`, `subscribeShape()`, `registerShape()`, `mutate(..., { expect })`, events `sync.conflict`, `sync.remoteChange`, inspector `window.__paperosSync`, compose test stack with Electric.
* Conflict UX spec (PAP-144): five component interfaces and spec IDs, `resolutionPolicy(fieldType)`, approved Storybook reference. Offline queue (PAP-148): `enqueue()`, `flush()`, `useSyncStatus()`, `SyncStatusIndicator`, `Idempotency-Key` header and `/api/rpc/batch` contract.
* Multi-window (PAP-145): `WindowBus`, `useIsLeader()`, message types `selection|navigation|presence|auth|theme|keymap|dnd.transfer`, `WindowChip`. Follow mode (PAP-149): `useFollow()`, `FollowBar`, awareness messages `presence.request|accept|decline|ping`, table `follow_sessions`.
* Capacity (PAP-147): `load/baseline.json`, scaling formula, nightly load job. Planned once the issue limit is lifted: push transport (`publishLiveEvent()`, `useLiveEvents()`, `PushProvider`) and child issues for PAP-143.

**Requires**

* identity: `verifySessionToken()`, `verifyApiKey()` (PAP-223, PAP-60), `can()` and predicate compiler (PAP-227, PAP-228), impersonation boundary (PAP-61), display names (PAP-55).
* data-layer: migrations and RLS (PAP-32, PAP-34), oRPC middleware chain for `mutation_id` stamping (PAP-267), Electric proxy, PGlite hooks and outbox (PAP-270, PAP-271, PAP-272), audit log (PAP-38), observability (PAP-40), jobs (PAP-43), test mode (PAP-240).
* app-shell: VPS, Caddy and Coolify (PAP-25), env schema (PAP-17), PWA (PAP-18), WindowManager (PAP-262), mobile shims (PAP-259, PAP-260); design-system: `AvatarStack`, `Badge`, tokens, primitives (PAP-71, PAP-66, PAP-236 to PAP-238); input: `defineCommand`, roving tabindex (PAP-151, PAP-152); spec-builder: page flags `realtime.*` (PAP-114), route index (PAP-115); collab: library choice (PAP-127); agents: character glyphs and hooks (PAP-103, PAP-104, PAP-107); tables: field types and view model (PAP-164, PAP-161); forge: second runner host for load generation (PAP-50).

**Milestone exit criteria**

* Yjs server and presence (2026-09-22): PAP-139 ADR accepted; PAP-140 deployed at `wss://collab.<domain>` with the RLS forged-room test and reconnect test green; PAP-141 two-browser presence under 1 s; PAP-142 two-cursor editing with offline merge and the palette-integrated toolbar.
* Record sync and conflict UX (2026-09-26): PAP-143 lag p95 under 500 ms with Electric in CI and permission resubscribe proven; PAP-144 five component definitions with approved Storybook reference; PAP-145 one WebSocket across three windows with re-election under 2 s.
* Scale and offline tested (2026-09-30): PAP-146 agent avatar within 2 s of a tool call; PAP-147 five scenarios run with baseline committed and nightly job green three nights; PAP-148 offline 20-edit replay in order with captive-portal handling; PAP-149 consent-gated follow session mirrored within 300 ms.
""",
"input": """

## Contract

**Provides**

* Input core (PAP-150, package `@paperos/input`): `InputEvent`, `Pointer`, `Key`, `Chord` with `parseChord()`, `formatChord()`, `matchChord()`, `usePointerSurface()`, `useInputCapabilities()`, `useLastInputModality()`, `THRESHOLDS`, `data-input-*` attributes, Biome rule `no-raw-touch-handlers`.
* Commands (PAP-151): `defineCommand()`, `CommandRegistry` with `setBindingsResolver()`, `useCommand()`, `useShortcut()`, `CommandPalette`, `CommandButton`, `commands.manifest.json`, oRPC `commands.execute`, telemetry `command.executed`, default `nav.*`, `ui.*`, `edit.*`, `help.*`, `search.open`.
* Focus (PAP-152): `FocusRegion`, `useRovingTabIndex()`, `FocusScope`, `useFocusRestore()`, `useGridFocus()`, shared `LiveAnnouncer`, attributes `data-focus-entry|key|region`, commands `focus.*`, CLI `a11y:focus-order`.
* Keymaps (PAP-153): `Keymap` schema, presets `default|vim|linear`, `resolveBindings()`, `useEffectiveChord()`, `preferences.keymap.*`, window message `keymap.changed`.
* Gestures (PAP-154): `useTap|useLongPress|useSwipe|usePinch|usePan|usePullToRefresh|useEdgeSwipe`, `GestureArena`, `SwipeableRow`, `PinchZoomView`, `PullToRefresh`, `BottomSheet`, `haptic()`, touch-target fixture.
* Drag-and-drop (PAP-155): `SortableList`, `SortableGrid`, `KanbanDnd`, `DropZone`, `DragHandle`, `between()`, `CanDropResult`, commands `dnd.*`, message `dnd.transfer`.
* Screen reader (PAP-156): protocol, `sr-results.json` (tiered), guidepup helper, `a11y` label convention. Pen (PAP-157): `usePenStroke()`, `InkStroke` codec, `InkAnnotationLayer`, canvas node `ink`. Spatial (PAP-158): `SpatialNavigationProvider`, `useFocusable()`, `FocusGroup`, `scoreCandidates()`, `SpatialKeyboard`. Voice (PAP-159): `SpeechBackend` seam (Web Speech only in this build), `matchCommand()`, `DictationTarget`, command option `voice`. Statement (PAP-160): `report.json`, `criteria-map.json`, `/accessibility`, `a11y:report` CLI.
* Planned once the issue limit is lifted: child issues for PAP-151 and PAP-155 (specs in `round2/agent3/pending-issues.json`).

**Requires**

* design-system: primitives incl. focus-scope, `Dialog`, `Menu`, `Combobox` (PAP-236 to PAP-238), `AppFrame` and `CommandBar` slots (PAP-70), tokens and TV theme (PAP-66, PAP-75), `a11y-report.json` (PAP-73).
* identity: `can()` (PAP-227), agent scopes (PAP-60); data-layer: oRPC and `callAs` (PAP-267, PAP-268), `user_preferences` (PAP-33), audit (PAP-38), observability (PAP-40), test mode (PAP-240).
* app-shell: `breakpoints.json` and TV breakpoint (PAP-14), Tauri mobile haptics and mic entitlements (PAP-258 to PAP-260), kiosk (PAP-23), WindowManager (PAP-262); realtime: `WindowBus` (PAP-145), record sync (PAP-143), `RichTextEditor` (PAP-142), presence surfaces (PAP-141); spec-builder: `commands:` and `help.*` sections (PAP-114), app-level spec (PAP-117), codegen attributes (PAP-120); collab: canvas tool host (PAP-132), QA viewer (PAP-137), docs engine (PAP-128); quality: e2e flows (PAP-86), Gate 3 (PAP-82), rubric (PAP-79), quarantine (PAP-90), release train and digest (PAP-88, PAP-89); pm-linear: Linear read API and webhooks (PAP-101, PAP-97), `publicSummary` (PAP-93); forge: non-Linux runners (planned) for PAP-156 Tier 2; tables: grid selection (PAP-165), form view (PAP-169).

**Milestone exit criteria**

* Keyboard and command system (2026-09-23): PAP-150 spec merged, playground story live, Biome rule at zero violations; PAP-151 palette on every page with manifest committed and agent endpoint audited; PAP-152 skip links, `F6` and route-change focus with focus-order strips at 375 and 1280.
* Touch, pen, gamepad (2026-09-27): PAP-153 three presets with cross-device sync under 2 s; PAP-154 device video with haptics and touch-target audit green; PAP-155 pointer, touch and keyboard paths with announcement snapshots and a cross-window drag; PAP-156 protocol merged, Tier 1 nightly green, zero open Sev-1 and Sev-2 on Tier 1 (Tier 2 depends on runners and may report `partial`).
* Voice and accessibility certification (2026-09-30): PAP-157 pressure strokes synced between two browsers; PAP-158 kiosk build driven end to end by controller; PAP-159 four spoken commands and dictation in Chrome with the Whisper reopen criteria recorded; PAP-160 all 55 criteria reported, `/accessibility` live, wording approved by Justin.
""",
}

UMBRELLA_COMMENT = """**Work packages pending child issues.** This issue is split into the work packages listed in its Scope. The child issues could not be created: Linear returned `USAGE_LIMIT_EXCEEDED` (free-plan issue cap) for every `issueCreate` on 2026-09-17. Full specs for each child (all sections, labels, milestone, size) are saved in `round2/agent3/pending-issues.json` and will be created as sub-issues once the workspace plan is upgraded or the cap is lifted. Until then, build the work packages in the listed order on branches named `<issue>/wp<n>-<slug>` and report each in a comment here."""
UMBRELLAS = ["PAP-131", "PAP-132", "PAP-136", "PAP-143", "PAP-151", "PAP-155"]

if "--projects" in sys.argv or not DRY:
    for key, pid in r3.PROJECTS.items():
        if pid in ch["projectsUpdated"]: print("skip project", key); continue
        content = (CUR[pid]["content"] or "").rstrip()
        if "## Contract" in content: print("already has contract", key); continue
        new = content + CONTRACTS[key]
        print(key, "content words", r3.words(new))
        if DRY: continue
        d = r3.gql("mutation($id: String!, $i: ProjectUpdateInput!) { p: projectUpdate(id: $id, input: $i) { success } }", {"id": pid, "i": {"content": new}})
        if d["p"]["success"]: ch["projectsUpdated"].append(pid); r3.save_changes(ch); print("updated project", key)

# milestone date: collab first milestone 09-21 -> 09-20
mid = r3.MILESTONES[(r3.PROJECTS["collab"], "Docs and prompt log stores")]
if not any(m.get("milestoneId") == mid for m in ch["milestoneChanges"]):
    print("milestone date fix", mid)
    if not DRY:
        d = r3.gql("mutation($id: String!, $i: ProjectMilestoneUpdateInput!) { m: projectMilestoneUpdate(id: $id, input: $i) { success projectMilestone { targetDate } } }", {"id": mid, "i": {"targetDate": "2026-09-20"}})
        if d["m"]["success"]: ch["milestoneChanges"].append({"milestoneId": mid, "name": "Docs and prompt log stores", "targetDate": "2026-09-20", "was": "2026-09-21"}); r3.save_changes(ch); print("milestone updated", d["m"])

# umbrella comments
done = set(c.get("issue") for c in ch.get("comments", []))
todo = [u for u in UMBRELLAS if u not in done]
print("comments to post", todo)
if not DRY and todo:
    vardefs=[]; parts=[]; variables={}
    for j,u in enumerate(todo):
        vardefs.append(f"$i{j}: CommentCreateInput!"); parts.append(f"c{j}: commentCreate(input: $i{j}) {{ success comment {{ id }} }}")
        variables[f"i{j}"] = {"issueId": r3.BY_ID[u]["id"], "body": UMBRELLA_COMMENT}
    d = r3.gql("mutation(" + ", ".join(vardefs) + ") { " + " ".join(parts) + " }", variables)
    ch.setdefault("comments", [])
    for j,u in enumerate(todo):
        if d[f"c{j}"]["success"]: ch["comments"].append({"issue": u, "id": d[f"c{j}"]["comment"]["id"]})
    r3.save_changes(ch); print("comments posted", len(todo))

# PAP-136 trimmed description re-push
if "--repush136" in sys.argv and not DRY:
    iss = r3.BY_ID["PAP-136"]
    d = r3.gql('mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success issue { identifier labels { nodes { name } } priority projectMilestone { name } } } }', {"id": iss["id"], "i": {"description": r3.render(rw_collab.R["PAP-136"])}})
    print("PAP-136 repush", d)
