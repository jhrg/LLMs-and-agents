<!-- CONTRACT: one entry per ACCEPTED feature — a unit of new capability that groups
     the FR/NFR/UC IDs it delivers and the plan that builds it. Proposed features
     (ideas not yet accepted) do NOT live here; they live wherever this project
     collects ideas (see Conventions in CLAUDE.md), and an entry's Origin field points
     back to one. A FEAT is not a requirement: it never states behavior itself, it
     cites the FR/NFR/UC rows that do. Delete the FEAT-EXAMPLE section once you've
     seen the shape. -->

# Feature Log

Convention: `FEAT-###`, sequential, never renumbered. Status: `Planned` →
`In Progress` → `Done` (or `Won't Do` / `Superseded by FEAT-0XX`). Change status
with `/features FEAT-### <status>`, not by hand, so the Status history line gets
written and, on `Done`, the cited FRs are set to `Implemented`. **Only the user sets
`Done`.** It's a claim about verified, shipped work, not something to infer from a
plan's phases being finished.

Whether a plan exists is shown by the `Plan:` field (`None yet` or a path), not by
the status. A feature's status is its lifecycle; a plan's own `Status` describes only
the plan document.

---

## FEAT-001 — Standalone ytbot v1

**Status:** Planned
**Created:** 2026-11-11
**Requirements:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008, UC-001, UC-002, NFR-001
**Constraints:** IC-002, IC-003, IC-004, IC-005, IC-006
**Plan:** `ai-plans/standalone-ytbot-v1-plan.md`
**Origin:** The 2026-11-11 `/init-planning` interview (no link)

**Summary:** Turns the course-only `ytbot.py` into a tool that runs on your own machine with your own watsonx account: transcript fetch, summaries (including long videos), timestamped Q&A, and broad URL support, through a CLI and a local Gradio UI.

**Status history:**
- 2026-11-11 — logged as `Planned`

---

<!-- Add new features via /new-feature, and change status via /features — keep the
     section format: metadata lines, then Summary, then Status history (append-only,
     oldest first). Requirements must list real FR/NFR/UC IDs; a feature with none
     isn't ready to log — add them with /new-requirement first. -->
