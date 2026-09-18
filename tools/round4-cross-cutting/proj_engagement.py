from gen_common import trio

K = 'engagement'
MS = ['Engagement contract and booking core', 'Messaging channels, help center and surveys', 'Memberships, loyalty, announcements and swap']

PROJECT = {
    'key': K,
    'name': 'Scheduling, Messaging & Customer Engagement',
    'lead': 'Beacon',
    'phase': 'P2',
    'description': 'The customer-relationship surfaces every service business needs after acquisition: appointments and resource scheduling with calendar sync, two-way conversational messaging over SMS, WhatsApp, email and in-app, a public help center, surveys and NPS, review requests, memberships with check-in, loyalty and gift cards, in-app announcements and a feedback board.',
    'content': """Goal: Growth (PAP-187 to PAP-197) wins the customer; nothing in the plan keeps them. Salons, clinics, gyms, trades, schools, churches and agencies all book time, remind people, answer the same questions, ask for feedback and reward loyalty, and the brief names "customer-facing and staff-facing experiences" and "one-size-fits-all". The libraries project spiked Cal.com and Formbricks (PAP-352) and the support inbox (PAP-197) is deferred, so today the platform has no booking, no two-way texting, no public help center, no surveys, no memberships and no loyalty. This project adds them as one module on the pieces that already exist: a scheduling model (resources, services, availability with the shared recurrence engine, holds, bookings) rendered on the PAP-344 calendar view and exposed as public booking pages and portal flows with reminders through notifications; two-way calendar sync with Google and Microsoft; a `MessagingChannelPort` so the PAP-410 support conversation model carries SMS and WhatsApp threads (Twilio, shared with PAP-404) as well as email and in-app chat; a public help center per tenant on PAP-379 tenant docs with search, feedback and the assistant's unauthenticated mode; surveys, NPS and CSAT on the workflows forms runtime with triggers from bookings and tickets; review requests and a reputation view; memberships (plans on Stripe Connect subscriptions, member cards with QR, check-in kiosk) and a loyalty points sub-ledger with gift cards on the ledger; in-app announcements targeted by segments and flags; and a public feedback board synced to PM entities. Non-goals in v0.2: video visits, a native WhatsApp Business onboarding beyond Twilio, complex class scheduling with waitlist priority rules beyond FIFO, native calendar apps.

## Contract

**Provides**

* `@paperos/contract-engagement`: `SchedulingPort` (`availability`, `hold`, `book`, `reschedule`, `cancel`, `waitlist`) with `Resource`, `Service`, `AvailabilityRule`, `Booking` schemas; `CalendarSyncPort` (`connect`, `pull`, `push`, `feed`); `MessagingChannelPort` (`send`, `receiveWebhook`, `status`, `capabilities`) with `ChannelKind` and `MessageRef`; `HelpCenterPort` (`publish`, `search`, `feedback`); `SurveyPort` (`define`, `trigger`, `responses`, `score`); `ReviewsPort` (`request`, `record`); `MembershipPort` (`plans`, `enrol`, `checkIn`, `status`); `LoyaltyPort` (`earn`, `redeem`, `balance`, `issueGiftCard`, `redeemGiftCard`); `AnnouncementPort` (`publish`, `forPrincipal`, `dismiss`); `FeedbackPort` (`post`, `vote`, `link`); slots `portal.home.cards`, `portal.nav.items`, `record.panel.tabs.bookings`, `dashboard.blocks.engagement`.
* Events: `booking.created|rescheduled|cancelled|no_show|completed`, `calendar.synced`, `message.received|sent|failed`, `survey.responded`, `review.requested|received`, `membership.enrolled|lapsed|checked_in`, `loyalty.earned|redeemed`, `giftcard.issued|redeemed`, `announcement.viewed`, `feedback.posted|voted`.
* Notification kinds: `booking.reminder`, `booking.confirmed`, `booking.changed`, `survey.invite`, `membership.renewal_due`, `loyalty.reward_available`.

**Requires**

* data-layer: recurrence engine (`r4/data-layer/recurrence-engine`), jobs (PAP-43), email (PAP-370), files (PAP-37), search (PAP-39), field encryption for calendar tokens (PAP-353), idempotency and rate limits (PAP-304).
* tables: calendar and timeline views (PAP-344, PAP-345), datasets and views (PAP-161, PAP-172), dashboards (PAP-173).
* identity: audiences and portal shell (PAP-55, PAP-62), OAuth plumbing (PAP-57 children), permission engine (PAP-59).
* collab: notifications with digests and quiet hours (PAP-136, PAP-324), tenant docs (PAP-379), contextual help (PAP-380), changelog feed (PAP-133), comments (PAP-131).
* growth: support conversation model and inbox (PAP-410 to PAP-412), outreach provider and consent (PAP-404, PAP-405, PAP-187 WP0), segments (PAP-195), CRM contacts (PAP-187).
* business-core: Connect and Checkout (PAP-181, PAP-396), Stripe subscriptions (PAP-177 client), ledger posting rules (PAP-394), documents (PAP-395).
* workflows: forms runtime (`r4/workflows/forms-schema-runtime`), approvals for refunds, e-sign for agreements. assistant: portal assistant grounding (optional). app-shell: kiosk mode (PAP-23), custom domains (PAP-431), flags (PAP-366), native barcode scanner (PAP-260).

**Consumed by**

* commerce (HR shift scheduling reuses `SchedulingPort` availability; POS redeems loyalty and gift cards), assistant (Front Desk character books and answers from the help center), workflows (booking and survey triggers), growth (reviews and NPS feed segments), platform-ops (engagement metrics in tenant health), migration packs (salon, clinic, gym packs ship services and booking pages).

**Owner**: Beacon leads; Nova builds scheduling and calendar; Ledger builds memberships and loyalty; Sentinel reviews messaging and money paths. Milestones: Engagement contract and booking core (2026-10-01), Messaging channels, help center and surveys (2026-10-09, deferred v0.2), Memberships, loyalty, announcements and swap (2026-10-16, deferred v0.2).""",
    'milestones': [
        {'name': MS[0], 'targetDate': '2026-10-01', 'description': 'Scheduling model, contract v0.1 and the booking engine with availability, holds and conflict prevention.'},
        {'name': MS[1], 'targetDate': '2026-10-09', 'description': 'Deferred (v0.2). Booking pages and reminders, calendar sync, two-way messaging channels, public help center, surveys and NPS, review requests.'},
        {'name': MS[2], 'targetDate': '2026-10-16', 'description': 'Deferred (v0.2). Memberships and check-in, loyalty and gift cards, announcements, feedback board, conformance suite and kernel wiring.'},
    ],
}

ISSUES = [
 {
  'key': f'r4/{K}/scheduling-model', 'title': 'Specify the scheduling model: resources, services, availability rules on the recurrence engine, holds, bookings, buffers, time zones and cancellation policies',
  'type': 'Spec', 'tier': 'opus', 'size': 'M', 'priority': 2, 'surfaces': ['Developer', 'Staff', 'Customer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': ['PAP-302', 'PAP-344', 'PAP-352', 'PAP-27', 'PAP-187'], 'blocks': [f'r4/{K}/contract-publish', f'r4/{K}/booking-engine'],
  'goal': "Define scheduling once for salons, clinics, gyms, trades and meeting rooms: resources (people, rooms, equipment) with availability rules expressed as recurrence sets, services with durations, buffers and required resource kinds, holds that expire, bookings with participants and policies, all in the tenant and resource time zones, recording what the Cal.com spike (PAP-352) taught us to borrow.",
  'scope_in': [
    "`docs/engagement/scheduling.md` and Zod schemas: `Resource` (`kind person|room|equipment`, `timezone`, `capacity`, `links: { userId?, fin_employee? }`), `Service` (`duration`, `bufferBefore|After`, `price Money?`, `resourceRequirements[]`, `bookableBy audiences`, `leadTime`, `horizon`, `cancellationPolicy`), `AvailabilityRule` (`rrule` via the recurrence engine, `window`, `kind available|blocked`, source `manual|calendar-sync|shift`), `Hold` (`expiresAt`), `Booking` (`service`, `resources[]`, `participants[] (contacts)`, `start/end`, `status held|confirmed|rescheduled|cancelled|no_show|completed`, `source portal|public|staff|assistant`, `payment?`, `notes`)",
    "Availability algorithm as a written spec: rules ∪ synced busy ∪ existing bookings → free intervals per resource → slot generation per service (step, alignment) → intersection across required resource kinds → lead time and horizon → capacity for group services",
    "Time zones: every rule stores its zone; slots are generated in the resource zone and presented in the viewer zone (PAP-27 helpers); DST transitions handled by the recurrence engine tests",
    "Policies: cancellation windows and fees (Money), no-show handling, reschedule limits, deposit requirement; group services (classes) with capacity and a FIFO waitlist",
  ],
  'scope_out': ['Engine implementation', 'UI', 'Staff shift planning (commerce HR reuses the availability rule shape)'],
  'spec': [
    'Double-booking prevention is a database guarantee: `booking_resource` rows carry a `tstzrange` with an exclusion constraint per resource; holds use the same table with a TTL so the invariant covers both',
    'Bookings link to CRM contacts (PAP-187) as participants; a participant without a contact creates one with consent status `transactional` (PAP-187 WP0) so reminders may be sent',
    'Money on bookings uses the PAP-395 document model: a deposit or fee is an invoice line, never a separate charge path',
    'Every booking status change emits an event carrying `previous`, `by ActorRef` and `reason`, which reminders, surveys and workflows consume',
  ],
  'provides': "`docs/engagement/scheduling.md`, schemas `Resource`, `Service`, `AvailabilityRule`, `Hold`, `Booking`, the availability algorithm spec, exclusion-constraint rule, policy model",
  'consumes': "`Money`/`EntityRef` (PAP-302), calendar view time model (PAP-344), OSS spike findings (PAP-352), Intl and timezone helpers (PAP-27), CRM contacts (PAP-187), recurrence engine (`r4/data-layer/recurrence-engine`)",
  'consumed_by': f"every scheduling issue here; commerce HR shifts; assistant Front Desk tools; migration packs (`services[]`, `resources[]` in `pack.yaml`)",
  'dod': ['Document and schemas merged; migration with exclusion constraint and RLS; three worked examples (salon chair, clinic room plus doctor, gym class of 12) as JSON fixtures that validate'],
  'tests': {
    'Unit': 'schema fixtures; the availability algorithm as a pure function against 25 fixture days including DST forward and back, buffers, capacity and lead time',
    'Review': 'Sentinel checks the consent path for participants and the exclusion constraint against concurrent holds',
  },
  'demo': "Walk the clinic example: a doctor and a room with different rules, a 30-minute service with a 10-minute buffer; show the generated slots for a patient in another time zone.",
  'edge': ['Resource moves time zone (staff relocates): rules keep their original zone; the change is a new rule version', 'Service requiring two resource kinds where only one is free: no slot; the report explains which kind blocked'],
  'deps': 'PAP-302, PAP-344 (hard), `r4/data-layer/recurrence-engine` (hard), PAP-352, PAP-27, PAP-187 (soft).',
  'builder': 'Nova', 'reviewer': 'Sentinel (Edge Case Hunter)', 'tenant_data': False, 'module_edge': False,
 },
 {
  'key': f'r4/{K}/booking-engine', 'title': 'Build the booking engine: availability computation, slot search, holds with TTL, exclusion-constraint conflict prevention, reschedule and cancel policies, group capacity and waitlist',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 2, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/scheduling-model', f'r4/{K}/contract-publish', 'PAP-43', 'PAP-304', 'PAP-303'], 'blocks': [f'r4/{K}/booking-pages', f'r4/{K}/calendar-sync'],
  'goal': "Implement the model as `SchedulingPort`: `availability()` fast enough for a booking page, `hold()` that reserves for 10 minutes, `book()` that converts a hold or books directly under the exclusion constraint, `reschedule()` and `cancel()` that apply policies and fees, capacity and waitlist for group services, and events for everything.",
  'scope_in': [
    "`packages/engagement/src/scheduling/`: tables from the model; `availability({ serviceId, range, viewerTz, resourceIds? })` with a per-resource cached interval set (invalidated by rule, booking and sync events), p95 under 150 ms for a 30-day range; `hold` (`expires_at = now() + 10 min`, sweeper job PAP-43); `book` with `Idempotency-Key` (PAP-304) and the exclusion constraint as the last line of defence",
    "Policies: `reschedule` re-runs availability and keeps the booking id; `cancel` computes the fee from the policy and creates a PAP-395 document line when non-zero; `no_show` and `completed` transitions by staff or by a job after end time (configurable)",
    "Group services: capacity check inside the transaction; `waitlist` FIFO with automatic promotion on cancellation and a 2-hour claim window notification",
    "oRPC `scheduling.*` procedures with audience rules (customers only see their own bookings and public availability), datasets `bookings`, `resources`, `services` registered for views and the PAP-344 calendar",
  ],
  'scope_out': ['Pages and reminders (next issue)', 'Calendar sync (own issue)', 'Payments UI (PAP-396 handles the pay page)'],
  'spec': [
    'Availability never reads other tenants and never exposes other customers\' booking details; public availability returns only free slots, never occupancy reasons',
    'Holds count against capacity; two customers cannot hold the last spot; the sweeper releases expired holds every minute and emits `booking.hold_expired`',
    'Rescheduling within the cancellation window applies the policy fee unless staff override with a reason (audited)',
    'All times stored as `timestamptz`; the API accepts and returns ISO strings with offsets plus the resource zone id',
    'A booking for a resource linked to a staff user writes an `AvailabilityRule(kind blocked)` shadow so shift and calendar views agree',
  ],
  'provides': "`SchedulingPort` default adapter, tables, `scheduling.*` procedures, datasets, hold sweeper and status jobs, `booking.*` events",
  'consumes': "the model and contract, recurrence engine, jobs (PAP-43), idempotency (PAP-304), events (PAP-303), documents for fees (PAP-395), calendar view (PAP-344)",
  'consumed_by': f"`r4/{K}/booking-pages`, `r4/{K}/calendar-sync`, `r4/{K}/memberships-checkin` (class bookings), assistant Front Desk tools, commerce HR shifts, workflows triggers",
  'dod': ['Concurrency test: 200 parallel `book` calls for one slot yield exactly one booking and 199 `SLOT_TAKEN`; availability p95 under 150 ms on the demo tenant; waitlist promotion proven; staff calendar shows bookings live'],
  'tests': {
    'Unit': 'interval math with buffers and capacity; policy fee computation; waitlist ordering',
    'Integration': 'exclusion constraint under concurrency; hold expiry; idempotent book replay; reschedule inside and outside the window',
    'Load': 'k6 (PAP-242) availability at 50 rps for a 30-day range',
  },
  'demo': "Open the staff calendar for the salon demo, book a client into a free slot from the record panel, try to double-book the chair from a second window and get the conflict, then cancel inside the window and see the fee line.",
  'edge': ['Availability rule deleted with future bookings: bookings stay; the calendar shows them as "outside availability" for staff to resolve', 'Clock skew on the client: holds and slot validity are decided by database time and returned to the client'],
  'deps': f"`r4/{K}/scheduling-model` and `r4/{K}/contract-publish` (hard), PAP-43, PAP-304, PAP-303 (hard), PAP-395, PAP-344 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Edge Case Hunter)',
 },
 {
  'key': f'r4/{K}/booking-pages', 'title': 'Build booking pages and reminders: public /book/:slug flow, portal bookings, staff calendar actions, deposits via Checkout, reminders and no-show follow-ups through notifications',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/booking-engine', 'PAP-62', 'PAP-396', 'PAP-136', 'PAP-431', 'PAP-344'], 'blocks': [],
  'goal': "Let customers book without calling: a public booking page per tenant and per service under the tenant brand and domain, a portal flow to view, reschedule and cancel, staff actions on the calendar view, deposits through PAP-396 Checkout, and reminder and follow-up notifications with quiet hours.",
  'scope_in': [
    "Public route `/book/:slug` (spec) on the public layout: service picker, resource picker (optional, \"any available\"), month and day slot picker in the viewer time zone, details form on the forms runtime (`r4/workflows/forms-schema-runtime`) with per-service intake questions, hold on slot select, confirm; deposit step opens Checkout; confirmation page with add-to-calendar (ICS) and manage link",
    "Portal `/portal/bookings` (list, detail, reschedule, cancel with policy explanation); `portal.home.cards` fill for the next booking",
    "Staff: PAP-344 calendar actions (create, drag to reschedule with policy prompt, mark no-show or completed), record panel tab `bookings` (PAP-333) on contacts; bulk reminder resend",
    "Reminders: kinds `booking.confirmed`, `booking.reminder` (24 h and 2 h defaults per service, email and SMS when `r4/collab/sms-notification-channel` exists), `booking.changed`; no-show follow-up template with a rebook link; all through PAP-136 with PAP-324 quiet hours",
  ],
  'scope_out': ['Calendar sync', 'Payments beyond deposits', 'Marketplace-style multi-vendor booking'],
  'spec': [
    'Slot picker shows only slots valid at render time and revalidates on select; a taken slot shows an inline message and refreshes, never a dead end',
    'Public page budget: under 120 KB JS, LCP under 2.5 s on a mid-range phone (PAP-87), no third-party scripts except Turnstile when enabled',
    'Manage links are signed tokens tied to the booking and participant email; they allow reschedule and cancel only within policy',
    'Reminders are idempotent per booking and kind; a rescheduled booking cancels pending reminders and schedules new ones',
    'Every page has portal and public specs with denied and empty states; screenshots at 375, 768, 1024, 1920',
  ],
  'provides': "`/book/:slug`, portal bookings pages, calendar actions, record tab, notification kinds `booking.*`, ICS attachment, manage-link tokens",
  'consumes': "booking engine, portal shell (PAP-62), Checkout (PAP-396), notifications and quiet hours (PAP-136, PAP-324), custom domains and branding (PAP-431, PAP-75), calendar view (PAP-344), record panel (PAP-333), forms runtime, SMS channel (soft)",
  'consumed_by': "migration packs (salon, clinic, gym booking pages), assistant Front Desk (`startBooking` handoff), growth (booking confirmations as sequence triggers)",
  'dod': ['A customer books with a deposit on a phone in test mode, gets a confirmation with ICS, receives the reminder in Mailpit, reschedules from the portal; staff drags a booking on the calendar; Lighthouse budget met'],
  'tests': {
    'Unit': 'slot picker state machine; manage token scope; reminder scheduling on reschedule',
    'E2E': 'public flow at 375 and 1920 with a screen reader script; portal reschedule within and outside policy; no-show follow-up',
  },
  'demo': "Book a haircut on the salon demo's public page from a phone with a $10 deposit, then move it from the portal and show the updated reminder schedule and the staff calendar.",
  'edge': ['Customer books in a zone that skips the slot hour on DST day: the picker shows zone-correct times and the confirmation states both zones', 'Deposit paid but hold expired during Checkout: booking is still created (payment wins) and staff are notified if it now conflicts, with a reschedule action'],
  'deps': f"`r4/{K}/booking-engine` (hard), PAP-62, PAP-396, PAP-136 (hard), PAP-431, PAP-344, PAP-333 (soft), `r4/workflows/forms-schema-runtime` (soft: falls back to a fixed details form).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/calendar-sync', 'title': 'Build calendar sync: ICS feeds, Google Calendar and Microsoft 365 two-way sync with busy-time import, push into external calendars, webhooks and conflict handling',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/booking-engine', 'PAP-57', 'PAP-353', 'PAP-43', 'PAP-121'], 'blocks': [],
  'goal': "Make PaperOS availability agree with the calendars staff already live in: a `CalendarSyncPort` with Google Calendar and Microsoft Graph adapters (OAuth through the PAP-57 plumbing, tokens encrypted with PAP-353), busy-time import into `AvailabilityRule(kind blocked, source calendar-sync)`, bookings pushed as events with updates and cancellations, incremental sync via webhooks with polling fallback, and read-only ICS feeds for everyone else.",
  'scope_in': [
    "`packages/engagement/src/calendar/`: `calendar_connection` (provider, account, encrypted tokens, calendars selected for busy import, target calendar for push, sync cursor, webhook channel); adapters `google` (Calendar API v3 with `syncToken` and push channels) and `microsoft` (Graph delta queries and subscriptions); `ics` feed adapter (signed per-resource URL, PAP-172 token semantics)",
    "Import: busy intervals become blocked rules tagged with the external event id; private details are never stored, only start, end and an opaque id; free/transparent events are ignored by default",
    "Push: booking events create external events with description, location and a manage link; reschedule and cancel update or delete; external edits to a pushed event raise a `calendar.conflict` for staff (PaperOS wins unless staff accept the change)",
    "Settings UI in `/console/settings/calendars` and per-user connection in the profile; connector files for PAP-121 (`google-calendar.connector.yaml`, `microsoft-graph.connector.yaml`)",
  ],
  'scope_out': ['CalDAV (v0.3)', 'Meeting links (Zoom, Meet) beyond a text field', 'Customer calendars (customers get ICS attachments)'],
  'spec': [
    'Sync is incremental and idempotent: cursors persisted per connection; a full resync is an explicit staff action with progress',
    'Token refresh failures pause the connection and notify the owner; nothing books against stale availability for more than the configured staleness (default 15 minutes) without a visible warning on the calendar',
    'Webhook receivers verify provider signatures and are rate-limited (PAP-304); every inbound triggers a job, never inline work',
    'Deleting a connection removes imported blocked rules and leaves pushed events in place with a note (external data is the user\'s)',
  ],
  'provides': "`CalendarSyncPort` with `google`, `microsoft`, `ics` adapters, `calendar_connection`, settings pages, `calendar.synced|conflict` events, connector files",
  'consumes': "booking engine and availability rules, OAuth plumbing (PAP-57), field encryption (PAP-353), jobs (PAP-43), connector registry (PAP-121), tokens (PAP-172), rate limits (PAP-304)",
  'consumed_by': "booking pages (ICS), commerce HR (staff busy time), assistant (\"am I free Thursday?\")",
  'dod': ['Google and Microsoft connections sync a test account both ways on staging with recorded fixtures in CI; ICS feed validates in two clients; conflict path visible; connection removal proven clean'],
  'tests': {
    'Unit': 'delta processing with moved, deleted and recurring events; conflict detection; privacy filter',
    'Integration': 'recorded provider fixtures (msw) for initial, incremental and expired-cursor sync; webhook signature rejection; token refresh failure pause',
  },
  'demo': "Connect a Google calendar for a stylist, add a dentist appointment there, watch the booking page lose that slot within a minute; book a client and see it appear in Google with the manage link.",
  'edge': ['Recurring external event with exceptions: each instance becomes its own blocked interval; the exception is honoured', 'Two staff share one external calendar: each connection imports it; pushes go to the resource owner\'s connection only'],
  'deps': f"`r4/{K}/booking-engine` (hard), PAP-57, PAP-353 (hard), PAP-43 (hard), PAP-121, PAP-172, PAP-304 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/messaging-channels', 'title': 'Build two-way conversational messaging: MessagingChannelPort with SMS and WhatsApp (Twilio), threads unified with support conversations, consent and quiet hours, templates and delivery status',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': ['PAP-410', 'PAP-412', 'PAP-404', 'PAP-405', 'PAP-187', 'PAP-353'], 'blocks': [],
  'goal': "Let staff text customers and customers text back inside the same inbox: a `MessagingChannelPort` whose SMS and WhatsApp adapters share the Twilio client with PAP-404 outreach, inbound webhooks that thread into PAP-410 support conversations by phone number and contact, consent and quiet-hour checks from PAP-405 and PAP-187, WhatsApp template management, delivery status, and per-conversation channel switching.",
  'scope_in': [
    "`packages/engagement/src/messaging/`: `channel_account` (kind sms|whatsapp|email|in-app, provider, number or sender id, encrypted credentials PAP-353, capabilities), `MessagingChannelPort.send(conversationId, body, attachments)` and `receiveWebhook`; adapters `twilio-sms`, `twilio-whatsapp` (reusing PAP-404 provider client), `email` (delegates to PAP-410), `in-app` (delegates to PAP-411)",
    "Threading: inbound by `(channel_account, from)` → existing open conversation within 7 days, else new conversation with contact match by phone (PAP-410 heuristics extended); unknown numbers create a contact with `consent: inbound` (they wrote first)",
    "Compliance: outbound checks `canContact(channel)` (PAP-187 WP0), quiet hours (PAP-405), STOP and START handling, WhatsApp 24-hour session window with template fallback, opt-in capture in booking and forms flows",
    "Inbox: channel badge on conversations (PAP-412), composer channel switcher, delivery receipts (queued, sent, delivered, read, failed with reason), MMS and WhatsApp media into PAP-37 files; console page for channel accounts and WhatsApp templates with approval status",
  ],
  'scope_out': ['Bulk campaigns (PAP-191 and `r4/growth/bulk-campaigns`)', 'Voice calls', 'Native WhatsApp Business onboarding beyond Twilio'],
  'spec': [
    'One Twilio client, two owners: PAP-404 owns sequences, this issue owns conversations; both call `provider.send` and share the suppression list so a STOP anywhere stops everything',
    'Inbound webhooks verify the Twilio signature, are rate-limited (PAP-304) and enqueue a job; the job is idempotent on the provider message id',
    'Templates for WhatsApp are stored with their approval status and language; the composer refuses a non-template outside the session window',
    'Media is scanned (`r4/data-layer/file-scanning-previews` when present) before staff preview; unknown types are downloadable only',
    'Costs: every message records `outreach.messages` usage (PAP-391) with the channel kind',
  ],
  'provides': "`MessagingChannelPort` with four adapters, `channel_account`, inbox channel UI, WhatsApp template management, `message.received|sent|failed` events",
  'consumes': "support conversations and inbox (PAP-410, PAP-412), in-app chat (PAP-411), outreach provider and compliance (PAP-404, PAP-405), consent (PAP-187), encryption (PAP-353), files (PAP-37), rate limits (PAP-304), metering (PAP-391)",
  'consumed_by': "booking reminders with replies (\"reply C to confirm\"), surveys by SMS, assistant escalation, commerce order updates, `r4/collab/sms-notification-channel` (shares adapters)",
  'dod': ['A customer texts the demo number, the conversation appears in the inbox with the contact matched, staff reply over SMS and switch to WhatsApp template when outside the window; STOP suppresses reminders too; recorded fixtures in CI'],
  'tests': {
    'Unit': 'threading rules; session window; consent and quiet hours gates; STOP/START parsing in three languages',
    'Integration': 'Twilio signature verification; duplicate webhook idempotency; media ingestion; delivery status updates',
  },
  'demo': "Text \"can I move my appointment?\" to the salon demo number; watch it land in the inbox threaded to the right contact; reply from the composer; then show the WhatsApp template picker after the session window closes.",
  'edge': ['Two contacts share one phone (family): the inbox shows both candidates and staff pick; the choice is remembered for that number', 'Provider outage: sends queue with backoff (PAP-43) and the composer shows delayed status; nothing is lost or duplicated'],
  'deps': "PAP-410, PAP-412 (hard: conversation model and inbox), PAP-404, PAP-405 (hard: shared client and compliance), PAP-187 (hard), PAP-353 (hard), PAP-37, PAP-304, PAP-391 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/help-center', 'title': 'Build the public help center: articles from tenant docs, categories, search, article feedback, contact and assistant entry points, custom domain and SEO basics',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': ['PAP-379', 'PAP-39', 'PAP-431', 'PAP-380', 'PAP-128'], 'blocks': [],
  'goal': "Give every tenant a help site their customers can find: published pages from the tenant docs store (PAP-379) organised in categories, full-text search (PAP-39), \"was this helpful\" feedback, a contact entry that opens the support widget or a form, the assistant's unauthenticated mode when enabled, under the tenant's custom domain with sitemap and metadata, and deep links from the in-app help panel (PAP-380).",
  'scope_in': [
    "Public routes `/help`, `/help/:category`, `/help/:slug` on the public layout with tenant branding (PAP-75) and domain (PAP-431); `help_category` and a `published` flag plus `audience` on tenant docs (PAP-379) so drafts and staff-only pages never leak; server-rendered HTML for SEO (Vite SSR route or prerender job) with sitemap, canonical and Open Graph tags",
    "Search: PAP-39 registration `help_article` with `audiences: [customer, anonymous]`; instant search box; \"no results\" leads to contact",
    "Feedback: thumbs per article with optional comment stored on the article, aggregated in a staff view; `article.feedback` event; low-rated articles surface in the staff docs list",
    "Entry points: `Contact us` opens PAP-411 widget or a forms-runtime form; assistant launcher when `portalEnabled` and the unauthenticated mode exists; the PAP-380 help panel links to articles tagged with the page spec key",
  ],
  'scope_out': ['Multi-language articles beyond the PAP-27 locale switch (v0.3 with translation skill)', 'Community forums'],
  'spec': [
    'Only pages with `published` and `audience` including `customer` or `anonymous` are served; the query is an RLS-compatible predicate, not an application filter',
    'Rendering budget: help pages are static HTML plus a 15 KB island for search and feedback; Lighthouse ≥ 95 on performance and SEO',
    'Article versions: publishing snapshots the Yjs document to HTML; edits do not change the public page until republished; the snapshot is what search indexes',
    'Accessibility: heading outline, skip links, focus order; axe clean; the help panel deep link opens the article in the inspector without leaving the app',
  ],
  'provides': "`HelpCenterPort.publish|search|feedback`, public help routes, categories, feedback aggregation view, sitemap, `help_article` search registration",
  'consumes': "tenant docs (PAP-379), search (PAP-39), domains and branding (PAP-431, PAP-75), help panel (PAP-380), docs engine rendering (PAP-128), support widget (PAP-411), forms runtime (soft)",
  'consumed_by': "assistant portal grounding, booking pages (policy articles), commerce (return policy), migration packs (starter articles)",
  'dod': ['Demo tenant help center live on staging with 10 starter articles, search, feedback and contact; Lighthouse ≥ 95; a draft article is proven unreachable; in-app help panel deep-links'],
  'tests': {
    'Unit': 'publish snapshot and predicate; sitemap generation; feedback aggregation',
    'E2E': 'search, open, rate, contact on a phone; crawl test for drafts returning 404',
  },
  'demo': "Publish \"How to reschedule\" from tenant docs, search for it on the public help center, rate it, then open the same article from the help panel inside the portal.",
  'edge': ['Article unpublished while indexed: the search row is removed in the same transaction and the URL returns 410 with a search box', 'Custom domain not yet verified: help center serves on the platform subdomain and the settings page shows the DNS steps'],
  'deps': "PAP-379 (hard), PAP-39 (hard), PAP-431, PAP-75 (soft), PAP-380, PAP-128 (soft), PAP-411 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/surveys-nps', 'title': 'Build surveys, NPS and CSAT: templates on the forms runtime, triggers from bookings, tickets and orders through workflows, scoring, response views and Formbricks borrow notes',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': ['PAP-352', 'PAP-136', 'PAP-173', 'PAP-195'], 'blocks': [f'r4/{K}/reviews-requests'],
  'goal': "Ask customers how it went without a third tool: NPS, CSAT and custom survey templates defined on the forms runtime, sent by email, SMS or shown in the portal after a booking completes, a ticket closes or an order ships (workflow triggers), with throttling so nobody is asked twice a month, scoring (NPS formula, CSAT averages), response datasets, dashboard blocks and segment feeds (PAP-195), borrowing the UX patterns the PAP-352 Formbricks spike recorded.",
  'scope_in': [
    "`survey` (template ref → `FormDefinition` with survey block types `nps`, `rating`, `csat`, `openText`; `trigger` config; `throttle`; `channels`), `survey_invite` (contact, token, channel, status), responses stored as form submissions tagged `survey_id` with derived `score` columns",
    "Triggers: workflow step kind `survey.send` and standalone rules (`booking.completed`, `support.conversation.closed`, `order.fulfilled`) with delay; throttle per contact (default 30 days) and per tenant daily cap; consent via `canContact`",
    "Delivery: email (PAP-370) with a one-click NPS row that records the score on click, SMS via messaging channels when present, portal card via `portal.home.cards`; token-authenticated public response page `/s/:token`",
    "Analytics: datasets `survey_responses` with NPS score computed (promoters − detractors), CSAT average, trend chart blocks (PAP-173), verbatims view; low scores raise `survey.low_score` for follow-up workflows; `segments` rules can use last NPS score",
  ],
  'scope_out': ['Product-analytics style in-app micro-surveys targeting by behaviour (platform-ops experiments cover targeting; v0.3)', 'Review sites (next issue)'],
  'spec': [
    'One-click email scoring is idempotent per invite; the follow-up question page loads with the score prefilled',
    'Responses are pseudonymous when the tenant enables `anonymousNps`: contact link dropped at write time, only segment attributes kept',
    'Throttle and consent checks happen at send time, not at trigger time, so a late unsubscribe is honoured',
    'NPS uses the standard 0 to 10 scale and formula; CSAT 1 to 5; both exposed as dataset fields so views and formulas (PAP-171) work',
  ],
  'provides': "`SurveyPort.define|trigger|responses|score`, survey block types, `/s/:token`, datasets and dashboard blocks, `survey.responded|low_score` events, step kind `survey.send`",
  'consumes': "forms runtime (`r4/workflows/forms-schema-runtime`), OSS spike (PAP-352), notifications and email (PAP-136, PAP-370), dashboards (PAP-173), segments (PAP-195), messaging channels (soft), consent (PAP-187)",
  'consumed_by': f"`r4/{K}/reviews-requests`, growth segments and sequences, platform-ops tenant health (NPS as a signal), assistant summaries of verbatims",
  'dod': ['After a demo booking completes, an NPS email arrives, one click records a 9 and opens the follow-up; dashboard shows the trend; a low score triggers a follow-up task; throttle proven'],
  'tests': {
    'Unit': 'NPS and CSAT math; throttle windows; anonymisation',
    'E2E': 'email one-click → follow-up page on a phone; portal card; verbatims view',
  },
  'demo': "Complete a booking in the demo tenant, receive the NPS email in Mailpit, click 9, add a comment, then watch the dashboard update and a detractor fixture open a follow-up task.",
  'edge': ['Contact replies to an expired invite: the page thanks them and records nothing; the invite stays expired', 'Same contact completes two bookings in a day: one invite, throttled correctly'],
  'deps': "`r4/workflows/forms-schema-runtime` (hard), PAP-136, PAP-370 (hard), PAP-352 (soft: borrowed patterns), PAP-173, PAP-195 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/reviews-requests', 'title': 'Build review requests and reputation: Google, Facebook and Yelp review links after positive scores, review capture, display widgets for landing pages and a reputation dashboard',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'S', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/surveys-nps', 'PAP-193', 'PAP-136'], 'blocks': [],
  'goal': "Turn happy customers into public reviews: after a promoter score (or directly after a completed booking or order) send a review request with the tenant's Google, Facebook or Yelp links, capture first-party reviews on a PaperOS page, display approved reviews as a widget on landing pages (PAP-193) and the public site, and show a reputation dashboard with request, click and review counts.",
  'scope_in': [
    "`review_profile` (platform links per location), `review_request` (contact, trigger, sent, clicked platform), `review` (first-party: rating, text, author display consent, status pending|approved|hidden, reply); request flow as a `survey` follow-up (promoters) or standalone trigger with the same throttle and consent",
    "Public page `/reviews/:token` to leave a first-party review; approved reviews dataset; widget `reviews.js` (shares the PAP-193 embed mechanics) and a `portal.home.cards` fill",
    "Reputation dashboard blocks (PAP-173): requests sent, click-through per platform, first-party rating average and volume trend; staff reply to first-party reviews with the reply shown publicly",
  ],
  'scope_out': ['Scraping or importing reviews from platforms (API terms vary; v0.3 ADR)', 'Incentivised reviews (refused by policy text in the flow)'],
  'spec': [
    'Review gating (only asking promoters to post publicly) is off by default and labelled with the platform-policy warning when enabled; the setting is audited',
    'First-party reviews are published only after staff approval; author names use the display consent captured on the page',
    'Widget budget under 8 KB; renders server-provided HTML with structured data (`schema.org/Review`) for SEO',
  ],
  'provides': "`ReviewsPort.request|record`, review tables and pages, `reviews.js`, reputation blocks, `review.requested|received` events",
  'consumes': "surveys (promoter follow-up), landing embeds (PAP-193), notifications (PAP-136), dashboards (PAP-173), consent (PAP-187)",
  'consumed_by': "growth landing pages, migration packs (salon and restaurant packs enable review requests), platform-ops tenant health",
  'dod': ['Promoter fixture receives a review request, clicks Google (tracked), a first-party review is captured, approved and appears in the widget on the demo landing page; dashboard renders'],
  'tests': {
    'Unit': 'gating default and warning; approval state machine; structured data output',
    'E2E': 'review page on a phone; widget embed; reply flow',
  },
  'demo': "Score 10 on the NPS demo, receive the review request, leave a first-party review, approve it in the console and see it appear on the landing page widget.",
  'edge': ['Tenant with multiple locations: profiles per location; the request picks the location from the booking resource'],
  'deps': f"`r4/{K}/surveys-nps` (hard), PAP-193 (soft: embed mechanics), PAP-136, PAP-173 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/memberships-checkin', 'title': 'Build memberships and check-in: membership plans on Stripe Connect subscriptions for the tenant\'s customers, member portal card with QR, check-in kiosk and scanner, attendance and lapse handling',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/booking-engine', 'PAP-181', 'PAP-177', 'PAP-394', 'PAP-23', 'PAP-260'], 'blocks': [f'r4/{K}/loyalty-gift-cards'],
  'goal': "Serve gyms, clubs, coworking spaces, churches and studios: membership plans billed through the tenant's Stripe Connect account (distinct from PAP-177, which bills the tenant), a member portal card with a rotating QR code, a check-in kiosk (PAP-23) and staff scanner (PAP-260 barcode plugin or keyboard wedge), class bookings limited by plan entitlements, attendance datasets, and lapse, pause and cancel flows with ledger postings.",
  'scope_in': [
    "`membership_plan` (price Money, interval, entitlements: class credits per period, booking limits, guest passes, access hours), `membership` (contact, plan, Stripe subscription id on the connected account, status trialing|active|past_due|paused|cancelled|lapsed, period), `checkin` (membership, location, method qr|scan|manual|kiosk, at)",
    "Billing: Stripe Billing on the connected account (PAP-181) with Checkout for enrolment (PAP-396 pattern), webhook state mapping, dunning through the PAP-180 WP4 reminders, proration on plan change; posting rules `membership.invoice.paid|refunded` (PAP-394) to revenue and Connect fees",
    "Portal: `/portal/membership` (plan, status, next charge, pause, cancel per policy, update payment method through the Stripe portal), member card with QR (`r4/design-system/labels-barcodes-qr`) rotating every 60 s and an offline-capable static fallback; class credits shown on booking",
    "Kiosk `/kiosk/checkin` (PAP-23 mode) with camera scan and name search; staff scanner in the console; check-in rules (active status, access hours, credits) with clear denial reasons; attendance dataset and dashboard blocks; lapse job",
  ],
  'scope_out': ['Access-control hardware integration (door locks; v0.3 via webhook)', 'Family and corporate memberships (v0.3)', 'Marketplace memberships'],
  'spec': [
    'Money only moves through Stripe; the membership status is derived from subscription webhooks, never set by hand except `paused` and `cancelled` through Stripe API calls',
    'QR payloads are signed, contain only the membership id and expiry, and are verified server-side; a screenshot older than 60 s fails unless the static fallback (per-tenant setting) is on',
    'Booking engine integration: class bookings consume credits inside the booking transaction; cancellation within policy refunds the credit',
    'Kiosk works offline for check-in by caching the active member list (PAP-148 outbox for the check-in rows) and refuses when the cache is older than 24 h',
    'Every status change emits `membership.*` events for workflows (welcome sequence, lapse win-back) and segments',
  ],
  'provides': "`MembershipPort.plans|enrol|checkIn|status`, tables, portal pages and card, kiosk and scanner, posting rules, `membership.*` events, attendance dataset",
  'consumes': "booking engine (credits), Connect and Stripe client (PAP-181, PAP-177), posting rules (PAP-394), reminders and dunning (PAP-397), kiosk mode (PAP-23), barcode plugin (PAP-260), QR component (`r4/design-system/labels-barcodes-qr`), offline outbox (PAP-148), portal shell (PAP-62)",
  'consumed_by': f"`r4/{K}/loyalty-gift-cards`, commerce POS (member pricing), migration packs (gym, church, coworking), assistant Front Desk (\"is my membership active?\")",
  'dod': ['A member enrols in test mode, sees the card, checks in at the kiosk by QR, books a class with a credit; a past-due fixture is denied with a reason; ledger shows the postings; offline kiosk check-in syncs'],
  'tests': {
    'Unit': 'entitlement math; QR signing and expiry; status mapping from webhook fixtures; access-hours rules across DST',
    'Integration': 'Checkout → webhook → active; proration on plan change; lapse job; credit consumption inside the booking transaction under concurrency',
    'E2E': 'kiosk on a tablet width with camera mock; portal pause and cancel; screenshots',
  },
  'demo': "Enrol in the gym demo's monthly plan in test mode, open the member card on a phone, check in on the kiosk tablet, book a class, then simulate a failed payment and watch the card go past-due with the dunning email.",
  'edge': ['Stripe webhook arrives before the enrolment row commits: the handler retries with backoff (PAP-43) until the row exists, then maps status', 'Member cancels with remaining credits: policy decides whether credits survive to period end; the portal states it plainly before confirming'],
  'deps': f"`r4/{K}/booking-engine` (hard), PAP-181, PAP-177, PAP-394 (hard), PAP-23, PAP-260, PAP-148 (soft), `r4/design-system/labels-barcodes-qr` (soft: inline QR fallback).",
  'builder': 'Ledger', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/loyalty-gift-cards', 'title': 'Build loyalty and gift cards: points sub-ledger with earn and redeem rules, tiers, rewards at checkout, gift cards as liabilities with codes and balances, fraud limits',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/memberships-checkin', 'PAP-179', 'PAP-394', 'PAP-396', 'PAP-408'], 'blocks': [],
  'goal': "Reward repeat business correctly on the books: a points sub-ledger built on PAP-179 (points are a liability with an assumed value), earn rules on bookings, orders and referrals, tiers by rolling points, rewards redeemed at checkout and POS, gift cards as prepaid liabilities with codes, balances and partial redemption, and fraud limits borrowed from PAP-408.",
  'scope_in': [
    "`loyalty_program` (points per Money unit, tiers, expiry policy, assumed value per point), `loyalty_account` (contact, balance cache, tier), `loyalty_entry` (earn|redeem|expire|adjust, points, source EntityRef) posting to ledger accounts `loyalty_liability` and `loyalty_expense` through PAP-394 rules; `gift_card` (code hash, initial and remaining Money, expiry per jurisdiction rules, purchaser, recipient), `gift_card_txn`",
    "Earn triggers: `booking.completed`, `order.paid` (commerce), `referral.qualified` (PAP-407) via rules; redeem as a discount line on PAP-395 documents and a payment method in Checkout (PAP-396 gains `giftCard` and `points` tender types) and POS",
    "Portal: balance, history, rewards catalogue, gift card purchase (Checkout) and send by email with a printable card (print kit); staff: adjust with reason (approval above a threshold via `r4/workflows/approvals-framework`), lookup by code",
    "Fraud: velocity limits per account and IP, redemption caps per day, code entropy and attempt lockouts, adjustments audited (PAP-38) and reviewed weekly",
  ],
  'scope_out': ['Coalition or cross-tenant programs', 'Breakage accounting automation beyond expiry entries (finance decides in PAP-183 reports)'],
  'spec': [
    'Points and gift card balances are never stored as the truth: balances derive from entries and ledger postings; the cache is rebuilt by `rebuildBalances` (PAP-394 pattern) and verified nightly',
    'Gift card codes are stored hashed (like passwords); the plaintext appears once to the purchaser or recipient and in the printable card',
    'Redemptions are idempotent by document line or POS transaction id; a voided document reverses the redemption entry',
    'Expiry follows the program policy but never earlier than the jurisdiction minimum recorded in the PAP-126 compliance profile (many places forbid gift card expiry)',
    'Every entry emits `loyalty.*` or `giftcard.*` events for workflows and segments',
  ],
  'provides': "`LoyaltyPort.earn|redeem|balance|issueGiftCard|redeemGiftCard`, tables and posting rules, portal pages, printable gift card, Checkout tender types, fraud limits",
  'consumes': "ledger and posting rules (PAP-179, PAP-394), documents and Checkout (PAP-395, PAP-396), referral qualification and fraud rules (PAP-407, PAP-408), approvals, print kit (PAP-235), audit (PAP-38), compliance profile (PAP-126)",
  'consumed_by': "commerce POS and orders, booking deposits, migration packs (salon, restaurant, retail), growth segments (tier as attribute)",
  'dod': ['Demo customer earns points on two bookings, reaches a tier, redeems a reward on an invoice; a $50 gift card is bought, emailed, partially redeemed twice; ledger liability accounts reconcile to balances; velocity limit proven'],
  'tests': {
    'Unit': 'earn and tier math; expiry policy floor; code hashing and lockout; idempotent redemption',
    'Integration': 'redeem → document line → posting → void → reversal; nightly balance verification; approval above threshold',
  },
  'demo': "Buy a gift card in the portal, redeem half of it at the demo POS and the rest on an invoice; open the ledger to show the liability shrinking; then earn points and redeem a reward.",
  'edge': ['Gift card purchased on a connected account then refunded by the purchaser: remaining balance is frozen, partial redemptions already made are charged back to the purchaser per policy; the flow needs an approval', 'Points program closed: remaining balances expire on a notified date with `expire` entries and a final liability release'],
  'deps': f"`r4/{K}/memberships-checkin` (soft: shares portal and Connect setup), PAP-179, PAP-394, PAP-396 (hard), PAP-408 (soft: fraud rules), `r4/workflows/approvals-framework` (soft).",
  'builder': 'Ledger', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/announcements', 'title': 'Build in-app announcements and product messaging: banners, modals and a What\'s new feed from the changelog, targeting by segment, audience and flag, scheduling, dismissal and metrics',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'S', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': ['PAP-133', 'PAP-195', 'PAP-366', 'PAP-136'], 'blocks': [],
  'goal': "Let tenants talk to their users inside the app: announcements as banners, modals and a What's new panel fed by the PAP-133 per-tenant changelog, targeted by audience, segment (PAP-195) and flag (PAP-366), scheduled with start and end, dismissible per user, with view and click metrics, so release notes and business notices (holiday hours, price changes) reach the right people without an email blast.",
  'scope_in': [
    "`announcement` (kind banner|modal|feed, body Tiptap JSON, cta, targeting: audiences, segment, flag, routes, start, end, priority, dismissible), `announcement_view` (user, viewed, dismissed, clicked); `AnnouncementPort.forPrincipal(route)` evaluated server-side and streamed via the flag snapshot channel (PAP-366)",
    "Shell fills: `shell.banner` (one banner at a time by priority), modal on first eligible route, What's new bell entry in the PAP-323 inbox area merging changelog entries (PAP-133) and feed announcements",
    "Console page `/console/announcements` with editor, preview per audience, schedule, metrics (views, dismissals, clicks) as dashboard blocks; approval optional via the approvals framework",
  ],
  'scope_out': ['Email or SMS delivery (use notifications or campaigns)', 'Behavioural targeting by product events (platform-ops product analytics; v0.3)'],
  'spec': [
    'Targeting is evaluated with the same evaluator as flags so a segment or flag change applies within the snapshot refresh; the client never decides eligibility',
    'Banners respect reduced motion and the PAP-234 state components; modals never stack with system dialogs and can be deferred once',
    'Dismissal is per user per announcement version; editing the body creates a version and may re-show only when `reshowOnEdit`',
    'Metrics are counts, not per-user tracking beyond dismissal state; no third-party scripts',
  ],
  'provides': "`AnnouncementPort`, tables, shell fills, console page, metrics blocks, `announcement.viewed|dismissed|clicked` events",
  'consumes': "changelog feed (PAP-133), segments (PAP-195), flags and snapshot channel (PAP-366), inbox UI (PAP-323), notifications (PAP-136), state components (PAP-234), approvals (soft)",
  'consumed_by': "platform-ops (platform-wide announcements to all tenants use the same mechanism with `scope: platform`), growth (campaign follow-through in-app), assistant (announcements as grounding for \"what changed?\")",
  'dod': ['Holiday-hours banner targeted at customers in one segment shows only to them, dismisses, and reports metrics; What\'s new merges the last release notes; screenshots at three widths'],
  'tests': {
    'Unit': 'targeting evaluation parity with flags; priority selection; version and dismissal logic',
    'E2E': 'banner and modal on portal and console, keyboard dismissal, reduced motion',
  },
  'demo': "Publish \"Closed Monday\" as a portal banner for the VIP segment starting tomorrow, preview as a VIP and a non-VIP, then show the What's new panel with the latest changelog.",
  'edge': ['Two banners eligible: higher priority wins; the other appears after dismissal; ties break by start date'],
  'deps': "PAP-133 (hard: feed), PAP-195, PAP-366 (hard: targeting), PAP-323, PAP-136 (soft), PAP-234 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/feedback-board', 'title': 'Build the feedback and feature request board: public and portal board, upvotes, statuses synced to PM entities, duplicates merge, changelog linkage and notifications on status change',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'S', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': ['PAP-100', 'PAP-131', 'PAP-133', 'PAP-136'], 'blocks': [],
  'goal': "Close the loop with users: a feedback board where customers post ideas and problems, upvote and comment, staff triage, merge duplicates and link posts to PM issues (PAP-100) whose status flows back, and shipped items link to the changelog entry (PAP-133) with a notification to everyone who voted.",
  'scope_in': [
    "`feedback_post` (title, body, author contact or anonymous email, status open|planned|in_progress|shipped|declined, votes, category, linked pm_issue, merged_into), `feedback_vote`; comments via PAP-131 anchors; public `/feedback` and portal `/portal/feedback` (spec) on the list view with sort by votes and recency; anti-spam via `CaptchaPort` and rate limits",
    "Staff triage view: merge, categorise, link or create a PM issue (PAP-100 entities; Linear sync PAP-101 carries it), set status; status changes notify voters (`feedback.status_changed` kind) with digest batching (PAP-324)",
    "Changelog linkage: when a linked issue ships and PAP-133 publishes the entry, the post moves to `shipped` with the entry link",
  ],
  'scope_out': ['Roadmap page beyond a status-grouped board view', 'Internal-only idea management (use PM)'],
  'spec': [
    'Anonymous posts require email verification (one-time link) before appearing; verified authors can edit for 15 minutes',
    'Votes are one per principal or verified email; merging moves votes without duplicates and redirects the old URL',
    'Board visibility is per tenant setting: public, portal-only or off; RLS predicate matches',
  ],
  'provides': "`FeedbackPort.post|vote|link`, tables, board pages, triage view, `feedback.posted|voted|status_changed` events",
  'consumes': "PM entities and sync (PAP-100, PAP-101), comments (PAP-131), changelog (PAP-133), notifications and digests (PAP-136, PAP-324), list view (PAP-169), `CaptchaPort` (`r4/workflows/forms-publishing`, soft)",
  'consumed_by': "pm-linear (feedback-derived issues), growth (feedback as segment attribute), assistant (summaries of top requests)",
  'dod': ['Demo board with 20 posts; a customer posts and votes on a phone; staff merges two, links one to a PM issue, ships it via changelog and voters are notified'],
  'tests': {
    'Unit': 'vote uniqueness and merge; status flow from PM; visibility predicate',
    'E2E': 'anonymous post with verification; triage actions; digest of status changes',
  },
  'demo': "Post \"Add Apple Pay\" on the demo portal board, upvote from another account, link it to a PM issue in the console, mark shipped through a changelog entry and show the notification.",
  'edge': ['Linked PM issue deleted in Linear: the post keeps its status and shows the link as broken for staff to fix'],
  'deps': "PAP-100, PAP-131, PAP-133, PAP-136 (hard), PAP-101, PAP-324, PAP-169 (soft).",
  'builder': 'Beacon', 'reviewer': 'Sentinel (Code Reviewer)',
 },
]

TRIO = trio({
    'key': K, 'lead': 'Beacon', 'owner': 'Beacon', 'kind': 'runtime', 'swapRisk': 'medium', 'impl': 'packages/engagement, apps/web/src/engagement',
    'milestones': MS, 'impl_keys': [f'r4/{K}/booking-engine', f'r4/{K}/booking-pages', f'r4/{K}/messaging-channels', f'r4/{K}/help-center'],
    'publish_blockedBy': [f'r4/{K}/scheduling-model'],
    'ports': ['`SchedulingPort` (`availability`, `hold`, `book`, `reschedule`, `cancel`, `waitlist`) with `Resource`, `Service`, `AvailabilityRule`, `Hold`, `Booking`', '`CalendarSyncPort` (`connect`, `pull`, `push`, `feed`) with `CalendarConnection`', '`MessagingChannelPort` (`send`, `receiveWebhook`, `status`, `capabilities`) with `ChannelKind`, `ChannelAccount`, `MessageRef`', '`HelpCenterPort` (`publish`, `search`, `feedback`) and `SurveyPort` (`define`, `trigger`, `responses`, `score`)', '`ReviewsPort` (`request`, `record`) and `FeedbackPort` (`post`, `vote`, `link`)', '`MembershipPort` (`plans`, `enrol`, `checkIn`, `status`) and `LoyaltyPort` (`earn`, `redeem`, `balance`, `issueGiftCard`, `redeemGiftCard`)', '`AnnouncementPort` (`publish`, `forPrincipal`, `dismiss`)', 'slots `portal.home.cards`, `portal.nav.items`, `record.panel.tabs.bookings`, `dashboard.blocks.engagement`, `shell.banner`'],
    'events': ['booking.created', 'booking.rescheduled', 'booking.cancelled', 'booking.no_show', 'booking.completed', 'calendar.synced', 'message.received', 'message.sent', 'message.failed', 'survey.responded', 'review.received', 'membership.enrolled', 'membership.lapsed', 'membership.checked_in', 'loyalty.earned', 'loyalty.redeemed', 'giftcard.issued', 'giftcard.redeemed', 'announcement.viewed', 'feedback.posted'],
    'requires': ['`@paperos/contract-data-layer` ^0.1 (jobs, email, files, search, idempotency, recurrence)', '`@paperos/contract-tables` ^0.1 (calendar view time model, datasets, views)', '`@paperos/contract-identity` ^0.1 (`Principal`, audiences, OAuth plumbing)', '`@paperos/contract-collab` ^0.1 (notification kinds, tenant docs, changelog)', '`@paperos/contract-growth` ^0.1 (support conversations, outreach provider, consent, segments, CRM contacts)', '`@paperos/contract-business-core` ^0.1 (Connect, Checkout, posting rules, documents)', '`@paperos/contract-workflows` ^0.1 (forms runtime, approvals; optional)', '`@paperos/contract-app-shell` ^0.1 (kiosk mode, domains, flags, native scanner)'],
    'fixtures': 'three scheduling scenarios (salon chair, clinic room plus doctor, gym class) with 25 availability days including DST, six bookings across the status machine, two calendar connections with delta fixtures, four channel accounts and eight inbound messages, two surveys with responses, one membership plan with webhook fixtures, a loyalty program with twenty entries and two gift cards, three announcements with targeting',
    'consumers': 'commerce (shift availability, POS loyalty and gift cards, member pricing), assistant (Front Desk booking and help-center answers), workflows (booking and survey triggers), growth (reviews and NPS into segments), platform-ops (engagement metrics), migration (salon, clinic, gym packs)',
})

ISSUES = [TRIO[0]] + ISSUES + TRIO[1:]
