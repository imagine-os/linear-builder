# Decisions

Architecture Decision Records (Nygard style: Status, Context, Decision, Consequences, Alternatives rejected) for the build loop itself — process and infrastructure choices the coordinating session made while running the PaperOS plan on autopilot. These are separate from the plan's own pre-assigned ADR register (`docs/module-system.md` and the builder brief list ADR 0001..0025, which live in the product repositories under `docs/adr/`); this folder's numbering is its own sequence, starting at 0001.

| # | Title | Date | File |
|---|---|---|---|
| 0001 | Build pilot operating mode | 2026-09-19 | [`0001-build-pilot-operating-mode.md`](0001-build-pilot-operating-mode.md) |
| 0002 | Integrator merge queue | 2026-09-19 | [`0002-integrator-merge-queue.md`](0002-integrator-merge-queue.md) |
| 0003 | Integrator owns Linear state moves and lands non-clean branches by rebase | 2026-09-19 | [`0003-integrator-owns-state-moves-and-rebase-landing.md`](0003-integrator-owns-state-moves-and-rebase-landing.md) |
