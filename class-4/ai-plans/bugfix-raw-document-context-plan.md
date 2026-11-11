# Bugfix Plan: Retrieved context is sent to the LLM as Python `Document` reprs, not text

**Bug:** BUG-004
**Status:** Draft
**Created:** 2026-11-11

## Summary

The Q&A prompt receives `str(list[Document])`, which is a Python repr with IDs, `metadata={}` and escaped newlines, instead of the transcript text. The fix formats the retrieved documents into clean text before filling the prompt.

## Root cause

`retrieve` returns `faiss_index.similarity_search(...)`, a `list[Document]` (`ytbot.py:210`). `generate_answer` passes it directly as `context=relevant_context` (`ytbot.py:285`), so the template formats it with `str()`. No code extracts `page_content`.

## Related requirements

- FR-003: answers are generated "from" the relevant segments, and repr noise dilutes them.
- FR-006: timestamp citations depend on the model reading `Start:` values cleanly. FR-006 isn't implemented yet, but this fix shouldn't get in its way.

## Fix approach

- Add `format_docs(docs) -> str` that joins `d.page_content` with blank lines, ordered by start time so the context reads in video order.
- Use it in the Q&A chain, either inside `generate_answer` or as an LCEL step (`{"context": retriever | format_docs, "question": RunnablePassthrough()}`) if BUG-003's chain change has landed.

This is deliberately narrow. Richer per-chunk metadata, such as storing `start` in `Document.metadata` instead of in the text, belongs with FR-006.

## Regression risk

- Only affects the Q&A path. Answers may change a little because the prompt gets cleaner.
- If BUG-003 lands first, apply this to the new LCEL chain instead of to `generate_answer`.
- There are no existing tests.

## Verification

- Re-run the BUG-LOG reproduction: the printed context contains `Text: … Start: …` lines, and no `Document(`, `page_content=` or `metadata=`.
- New offline pytest (NFR-001): pass hand-made `Document`s through `format_docs` and assert the exact output string. Also run the Q&A chain with a stub LLM and assert that the rendered prompt contains no `Document(`.

## Out of scope

- Timestamp citations (FR-006).
- Chunking strategy.

## Work log

### 2026-11-11 15:31 MST — Plan created

**Prompt:**

> Make each of the five problems a bug.
>
> (Follow-up answers: commit pending edits first; log all five on one shared branch,
> `jhrg/ytbot-bug-log`; accept the proposed severities; run the full `/fix-bug` flow,
> including a plan for each bug.)

Logged BUG-004 (Low). Root cause: `list[Document]` passed raw as `context` at `ytbot.py:285`. Plan: add a `format_docs` step.
