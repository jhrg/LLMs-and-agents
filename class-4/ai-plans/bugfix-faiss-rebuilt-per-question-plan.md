# Bugfix Plan: Whole transcript is re-embedded and the FAISS index rebuilt on every question

**Bug:** BUG-002
**Status:** Draft
**Created:** 2026-11-11

## Summary

Each question re-chunks the transcript, re-embeds every chunk through watsonx, and builds a FAISS index that is thrown away afterwards. The fix builds the index once per video and reuses it for later questions.

## Root cause

`answer_question` (`ytbot.py:363-382`) runs `chunk_transcript` → `setup_credentials` → `initialize_watsonx_llm` → `setup_embedding_model` → `create_faiss_index` on every call. `FAISS.from_texts` calls `embed_documents` on all chunks. Nothing keeps the index, the LLM or the embedding client between calls.

## Related requirements

- None documented. No NFR states a latency or watsonx-usage target for Q&A, so "rebuild every time" breaks no written requirement, only the obvious expectation. I suggest adding an NFR through `/new-requirement`, for example: "a follow-up question on an already-loaded video makes no new transcript embedding calls".
- Supports UC-002 indirectly.

## Fix approach

- Build the FAISS index when a video's transcript is first loaded for Q&A, and store it in the same per-video cache entry that BUG-001 introduces (video ID → transcript, processed text, index).
- Create the watsonx LLM and embedding clients once per process (lazily, after credentials are loaded under IC-002), not once per click.
- Keep the index in memory only. Persisting it to disk isn't required by anything written.

This fix stays at "cache what's already computed". Changing the chunk size or overlap (200/20 characters is very small) would affect retrieval quality, and belongs with the FR-006 timestamp work, not here.

## Regression risk

- Depends on BUG-001's per-video cache. Doing BUG-002 first would mean caching onto the buggy global, and a stale index would then make BUG-001 worse.
- Memory grows by one index per video viewed in a session. For a local, single-user tool (IC-003) that's acceptable. A cap could come later.
- There are no existing tests.

## Verification

- Re-run the BUG-LOG reproduction: question 2 on the same video makes zero `embed_documents` calls, and only one `embed_query`.
- New offline pytest (NFR-001): use a fake embeddings class that counts calls, ask two questions on the same video ID, and assert that `embed_documents` ran once. Then switch the video ID and assert that it runs again.

## Out of scope

- Tuning chunk size and overlap.
- Persisting indexes across runs.

## Work log

### 2026-11-11 15:31 MST — Plan created

**Prompt:**

> Make each of the five problems a bug.
>
> (Follow-up answers: commit pending edits first; log all five on one shared branch,
> `jhrg/ytbot-bug-log`; accept the proposed severities; run the full `/fix-bug` flow,
> including a plan for each bug.)

Logged BUG-002 (Medium). Root cause: per-call index construction at `ytbot.py:365-375`. Plan depends on BUG-001's per-video cache. Recommends adding a Q&A efficiency NFR.
