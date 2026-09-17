---
identifier: "PAP-94"
title: "Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Staff"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: ["PAP-108", "PAP-252", "PAP-254", "PAP-88"]
key: "pm-linear/justin-queue"
url: "https://linear.app/paperos/issue/PAP-94/design-the-needs-justin-queue-batched-decisions-one-click"
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-94: Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule

**Goal**

Design and implement the rules that keep the single human reviewer's queue small and fast: `Needs Justin` holds at most five open items, every item is a batched, pre-digested decision with one-click approve/reject via comment keywords, and anything that does not need a human is refused entry. This is what makes the rest of the plan's autonomy safe.

**Scope**

In:
- `docs/pm/justin-queue.md`: what qualifies for `Needs Justin` (release-candidate approval, irreversible actions such as production deploys, spend above a threshold, external-facing communication, credential grants, hiring a new character), what does not (code review, test failures, library choices under the rubric).
- Decision card format for the issue description or comment: `Decision needed`, `Recommendation` (one sentence), `Options` (max 3, each with cost and risk), `Deadline` and `Default if no answer` (auto-applies after 48 hours unless marked `hard-block`), `Context links`.
- Reply grammar parsed by the webhook handler: a comment starting with `approve`, `reject`, `option 2`, `defer 3d`, or `ask: <question>`; the handler moves the issue (`Done`, `Backlog`, or back to `In Progress` with the chosen option recorded) and posts an acknowledgement.
- Queue governor in the orchestrator: a transition into `Needs Justin` is refused (bounced to `In Review` with label `queued-for-justin`) when five items are already open; items are admitted FIFO by priority when a slot frees.
- Batching: a daily digest comment on a pinned issue `PAP-JUSTIN-DIGEST` (created once) listing open decisions, their defaults and deadlines, plus a Slack/email hook stub for later (`collab/notifications`).
- Weekly release candidate is one item, not many: `quality/release-train` posts a single issue per RC.

Out: the review digest content (`quality/review-report`), notification delivery channels, any UI beyond Linear.

**Spec**

- Module `src/justin/` in `imagine-os/paperos-orchestrator`: `governor.ts` (slot accounting, uses Linear `issues(filter: {state: {name: {eq: "Needs Justin"}}})`), `replies.ts` (grammar parser, regex plus fallback to an LLM classification only when the regex fails), `digest.ts` (cron 14:00 UTC daily).
- Defaults execute through the same state transitions the orchestrator uses; every auto-applied default is logged with `appliedBy: "default"` and posted as a comment.
- Priority order for admission: Linear priority (Urgent first), then age.
- All comments carry the `paperos-session` footer JSON with `status: "decision-requested" | "decision-applied"`.
- Configuration in `orchestrator.config.yaml`: `justinQueue.maxOpen: 5`, `defaultTimeoutHours: 48`, `digestCronUtc: "0 14 * * *"`.

**Definition of done**

- Doc published and linked from the session playbook.
- Governor tested: sixth item bounces with label; freeing a slot admits the highest-priority waiting item within one poll cycle (integration test against a Linear sandbox team or mocked SDK).
- Reply grammar has a fixture suite of 30 real-looking replies including typos (`aprove`) with expected outcomes.
- Default application after timeout tested with a fake clock.
- Digest posted to `PAP-JUSTIN-DIGEST` for three consecutive days in staging; screenshot at 375 px (Linear mobile) and 1280 px attached because Justin will read this on his phone.
- Changelog entry; Linear comment with screenshots.

**Edge cases**

- Justin replies with prose that matches none of the grammar: handler asks one clarifying question using the `ask:` template, does not guess.
- Two decisions batched in one comment (`approve PAP-40, reject PAP-41`): support multiple `key: verb` pairs.
- An `Urgent` item arrives when the queue is full: bump the oldest non-urgent item back to `queued-for-justin` and comment why.
- Default timeout passes on a `hard-block` item: never auto-apply; re-post reminder daily and escalate priority.
- Justin edits the issue instead of commenting: treat a state change by Justin as approval of the recommendation.
- Clock skew between orchestrator and Linear timestamps: compute deadlines from Linear `createdAt` of the decision comment.

**Dependencies**

- `pm-linear/configure-workspace` (states and labels).
- Works with `pm-linear/webhooks` for comment events; can be built against the mock receiver first.

**Agent**

Built by Atlas (lead), reviewed by Sentinel (Code Reviewer) and by Justin himself via a single approval comment on this issue, which doubles as the first live test.

**Size**

M: small code, but the grammar and governor need real fixtures and a staging soak.
