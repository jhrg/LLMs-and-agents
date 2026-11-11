# Bugfix Plan: "Transcript Status" box is never updated, and fetch errors aren't reported

**Bug:** BUG-005
**Status:** Draft
**Created:** 2026-11-11

## Summary

The UI has a "Transcript Status" box that nothing ever writes to. Separately, an unrecognized URL or a video with no English transcript surfaces as Gradio's generic "Error", because the error-handling paths can't be reached. The fix wires the status box up and makes fetch failures produce clear messages.

## Root cause

- `transcript_status` is created (`ytbot.py:408`), but it isn't in either `.click(..., outputs=...)` (`ytbot.py:411-412`) and no handler returns a value for it.
- `get_video_id` returns `None` for unmatched URLs (`ytbot.py:23`), and `get_transcript` passes that straight into `ytt_api.list(None)` (`ytbot.py:33`) without checking it.
- When no English transcript exists, `get_transcript` returns `None`, and `process(None)` raises `TypeError` on `for i in transcript` (`ytbot.py:56`). Its `except KeyError` (`ytbot.py:61`) couldn't catch attribute errors anyway. As a result, the "No transcript available" branch (`ytbot.py:332`) can't be reached.
- Exceptions from `youtube-transcript-api` (transcripts disabled, video unavailable, network failure) aren't caught anywhere.

## Related requirements

- UC-001 and UC-002 exception flows: an unresolvable reference or a missing transcript must produce a "clear error", and no LLM call should be made. This bug violates both.
- The status box's intended behavior isn't documented anywhere. If the user wants it kept, consider an FR through `/new-requirement`. Otherwise, removing the box is an acceptable fix too (see Fix approach).

## Fix approach

- Define a small `TranscriptError` exception with a user-facing message. Raise it from the fetch path for: unresolvable reference, no usable transcript, and caught `youtube-transcript-api` exceptions (mapped to readable text).
- Add a `None` check for the video ID before the API call.
- Make `process` never receive `None`. Fix or remove its `except KeyError`.
- Add `transcript_status` to both handlers' outputs. On success, show "Transcript loaded: <video id>, <n> segments, <manual|auto-generated>". On failure, show the `TranscriptError` message and leave the summary/answer box empty.
- The CLI front end (FR-007) prints the same message to stderr and exits non-zero. Shared error types make that free.

**Decision for the user:** keep the status box (the default in this plan) or remove it. Removing it would still require the clear-error part, but the error messages would go into the summary or answer box instead.

## Regression risk

- Changes both handlers' outputs. This overlaps with BUG-001, which also changes the handler signatures, so do the two together or one after the other to avoid conflicting wiring edits.
- Broader URL forms (FR-004) change which inputs reach the "unresolvable" path.
- There are no existing tests.

## Verification

- Re-run the BUG-LOG reproduction: step 2 shows a "Transcript loaded…" status. Steps 3 and 4 show specific error messages in the status box, with no generic Gradio "Error" and no LLM call.
- New offline pytests (NFR-001): `get_video_id("not a url")` leads to `TranscriptError`. A stubbed transcript list with no English entries leads to `TranscriptError("no English transcript…")`. A stubbed `TranscriptsDisabled` leads to a readable message. And the LLM factory is never called in these cases (assert on a stub).

## Out of scope

- Accepting more URL forms (FR-004). Until that lands, `youtu.be` links will hit the clear "unrecognized URL" error instead of working.
- Transcript language policy (still TBD in FR-001).

## Work log

### 2026-11-11 15:31 MST — Plan created

**Prompt:**

> Make each of the five problems a bug.
>
> (Follow-up answers: commit pending edits first; log all five on one shared branch,
> `jhrg/ytbot-bug-log`; accept the proposed severities; run the full `/fix-bug` flow,
> including a plan for each bug.)

Logged BUG-005 (Low). Root cause: status box never wired as an output, plus unchecked `None` from `get_video_id` and `get_transcript` making the error branches unreachable. Plan wires the status box and adds `TranscriptError`. Keep-vs-remove decision left to the user.
