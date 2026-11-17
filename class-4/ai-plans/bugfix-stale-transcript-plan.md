# Bugfix Plan: Q&A answers from the previous video's transcript after the URL changes

**Bug:** BUG-001
**Status:** Draft
**Created:** 2026-11-11

## Summary

`answer_question` reuses a single global transcript no matter which URL is in the box. Once anything has been fetched, questions about a different video are answered from the old one. The fix keys the cached transcript to its video ID, and keeps that cache per user session instead of per process.

## Root cause

`processed_transcript` is a module-level global (`ytbot.py:291`). `answer_question` fetches only `if not processed_transcript` (`ytbot.py:355`) and never records or compares the URL or video ID that produced it. `summarize_video` always refetches (`ytbot.py:310-313`), which hides the problem if the user summarizes before asking. Because the global lives in the module, every browser session on the Gradio server shares it.

## Related requirements

- UC-002 main flow step 2: the tool fetches the transcript "unless it already has the transcript for *that same* video". This bug is the "same video" check missing.
- FR-003: answers must come from *the* video in question.

## Fix approach

- Cache the transcript keyed by **video ID** (from `get_video_id`), not by raw URL, so different URL forms of the same video (FR-004) hit the same entry.
- Hold that cache in Gradio per-session state (`gr.State`), passed in and out of both handlers, instead of in module globals. The core functions then take the transcript as an argument and stop reading `global`. This also prepares for the shared core module the CLI front end needs (FR-007), since the CLI has no Gradio session.
- `summarize_video` and `answer_question` both call one helper: `get_or_fetch(video_id, state)`.

A narrower fix, storing `last_url` next to the global, would fix the symptom but keep the shared cross-session state and leave the CLI split harder. The state change is small, so the broader fix is worth doing now.

## Regression risk

- Both click handlers change signature (they gain a state input and output). Any wiring in the `gr.Blocks` section (`ytbot.py:411-412`) must be updated together.
- There are no existing tests.
- Interacts with BUG-002, which caches the FAISS index per video. The two should share the same per-video cache entry; plan them together, or do this one first.

## Verification

- Re-run the BUG-LOG reproduction steps: the answer to step 4 must come from video B.
- New offline pytest (NFR-001): stub `get_transcript` to return different fake transcripts for IDs A and B. Call the Q&A path with A and then B, and assert that the context passed to the LLM stub contains B's text.
- Same-video check: `www.youtube.com/watch?v=ID` followed by `youtu.be/ID` fetches only once (once FR-004 URL handling exists).

## Out of scope

- Caching the FAISS index (BUG-002).
- Broader URL forms (FR-004). This plan only depends on `get_video_id` returning a stable ID.

## Work log

### 2026-11-11 15:31 MST — Plan created

**Prompt:**

> Make each of the five problems a bug.
>
> (Follow-up answers: commit pending edits first; log all five on one shared branch,
> `jhrg/ytbot-bug-log`; accept the proposed severities; run the full `/fix-bug` flow,
> including a plan for each bug.)

Logged BUG-001 (High). Root cause traced to the module-global `processed_transcript` and the unconditional reuse check at `ytbot.py:355`. Drafted a fix that caches transcripts per session, keyed by video ID.
