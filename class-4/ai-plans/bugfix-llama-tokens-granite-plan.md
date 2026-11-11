# Bugfix Plan: Prompts use Llama 3 chat-template tokens but are sent to an IBM Granite model

**Bug:** BUG-003
**Status:** Draft
**Created:** 2026-11-11

## Summary

The summary and Q&A prompts hard-code Llama 3 chat markers (`<|begin_of_text|>`, `<|start_header_id|>`, `<|eot_id|>`), but the model is `ibm/granite-4-h-small`. The fix stops hand-writing model-specific tokens. Prompts go through watsonx's chat API, which applies the model's own template.

## Root cause

`create_summary_prompt` (`ytbot.py:162-175`) and `create_qa_prompt_template` (`ytbot.py:221-235`) embed Llama 3 special tokens in plain `PromptTemplate` strings. `WatsonxLLM` uses the text-generation endpoint, which passes the string through verbatim and applies no chat template, so Granite receives Llama's markers as ordinary text. The templates also carry 4 spaces of indentation on each line. This is very likely left over from when the course used a Llama model. How much output quality suffers hasn't been measured.

## Related requirements

- FR-002 and FR-003: summary and answer quality depend on a correctly formatted prompt. The correct prompt format was never written down as a requirement; it was an unwritten assumption.
- IC-001: the model is served by watsonx, and model IDs must be configurable. Hard-coded tokens tie the prompts to one model family, which conflicts with a configurable model ID.
- IC-005: the replacement uses current LangChain APIs (`ChatPromptTemplate`, LCEL).

## Fix approach

- Replace `WatsonxLLM` with `ChatWatsonx` (from `langchain_ibm`), and both `PromptTemplate`s with `ChatPromptTemplate.from_messages([("system", ...), ("human", ...)])`, with no special tokens and no stray indentation.
- Build the chains as `prompt | chat_model | StrOutputParser()` (IC-005), replacing `LLMChain` and `.run`/`.predict` for these two chains.
- Move the greedy decoding and max-token settings over to `ChatWatsonx`'s parameters.

The alternative of hand-writing Granite's own tokens (`<|start_of_role|>…<|end_of_role|>`) would fix today's mismatch but break again whenever the model ID changes. The chat API removes that whole class of bug.

## Regression risk

- This changes the LLM class and the chain style together, which overlaps with the IC-005 LangChain modernization. If that is planned as a separate task, coordinate so the two don't conflict. This fix could become the first slice of it.
- Output wording will change, and there are no baseline tests for it.
- `ChatWatsonx` must be available in whatever `langchain_ibm` version gets pinned (IC-004).

## Verification

- Re-run the BUG-LOG reproduction: the logged prompts contain no `<|begin_of_text|>`, `<|start_header_id|>` or `<|eot_id|>`.
- New offline pytest (NFR-001): render both prompt templates and assert that none of those tokens appear, that the system and human messages are separate, and that no line starts with 4 spaces.
- `live` test: summarize one short known video and check that the output is a single paragraph (FR-002). This is a manual or eyeball check of quality, not an automated assertion.

## Out of scope

- Prompt wording changes beyond removing the tokens and indentation.
- Timestamp citations in answers (FR-006).
- Splitting long transcripts for summaries (FR-005).

## Work log

### 2026-11-11 15:31 MST — Plan created

**Prompt:**

> Make each of the five problems a bug.
>
> (Follow-up answers: commit pending edits first; log all five on one shared branch,
> `jhrg/ytbot-bug-log`; accept the proposed severities; run the full `/fix-bug` flow,
> including a plan for each bug.)

Logged BUG-003 (Medium). Root cause: Llama 3 tokens hard-coded in both templates, sent verbatim through the completion endpoint. Plan: switch to `ChatWatsonx` + `ChatPromptTemplate` (aligns with IC-005).
