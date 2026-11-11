<!-- CONTRACT: deviations from intended behavior, tracked from report through root
     cause to fix. Not a duplicate of ai-docs/requirements/ — a bug means something
     already documented (or implicitly assumed) isn't holding true in practice.
     Delete the BUG-EXAMPLE section once you've seen the shape. -->

# Bug Log

Convention: `BUG-###`, sequential, never renumbered. Status: `Open` → `Investigating`
→ `Fix Planned` → `Fixed` → (or `Won't Fix` / `Duplicate of BUG-0XX`). `Open` means
logged with reproduction steps but root cause not yet looked at (`/fix-bug` sets it
at step 4 and moves to `Investigating` at step 5; an entry logged by hand starts here
too). **Only the user sets a bug to `Fixed`** — that's a claim about verified
deployed behavior, not something to self-report from having written a fix plan.

---

## BUG-001 — Q&A answers from the previous video's transcript after the URL changes

**Severity:** High
**Status:** Fix Planned
**Reported:** 2026-11-11
**Related requirements:** UC-002 main flow step 2 ("unless it already has the transcript for *that same* video"), FR-003
**Fix plan:** `ai-plans/bugfix-stale-transcript-plan.md`

**Reproduction steps:**
1. Start `ytbot.py` with working watsonx credentials and open the UI at port 7860
2. Enter the URL of video A (any English-captioned video), type a question about video A, and click "Ask a Question"
3. Replace the URL with video B (a different English-captioned video on an unrelated topic), and don't click "Summarize Video"
4. Ask a question that only video B can answer, and click "Ask a Question"

**Expected behavior:** The answer comes from video B's transcript.

**Actual behavior:** The answer comes from video A's transcript. Video B is never fetched, and nothing tells the user.

**Root cause:** `processed_transcript` is a single module-level global (`ytbot.py:291`). `answer_question` fetches only when it is empty (`ytbot.py:355`) and never checks which URL produced it. Only `summarize_video` refreshes it (`ytbot.py:310-313`), so after the first fetch every question uses whatever video was loaded last. Because the global is module-level, it is also shared across every browser session connected to the Gradio server.

---

## BUG-002 — Whole transcript is re-embedded and the FAISS index rebuilt on every question

**Severity:** Medium
**Status:** Fix Planned
**Reported:** 2026-11-11
**Related requirements:** None documented. No NFR covers Q&A latency or watsonx usage, and that gap is worth filling with `/new-requirement`.
**Fix plan:** `ai-plans/bugfix-faiss-rebuilt-per-question-plan.md`

**Reproduction steps:**
1. Start `ytbot.py` with working watsonx credentials, and wrap or log `WatsonxEmbeddings.embed_documents` so you can count its calls and inputs
2. Enter the URL of a video at least 10 minutes long and ask question 1
3. Without changing the URL, ask question 2

**Expected behavior:** The transcript chunks are embedded once per video. Question 2 only embeds the question text, and reuses the index built for question 1.

**Actual behavior:** Both questions call `embed_documents` on every chunk of the transcript. Question 2 takes about as long as question 1 and uses the same embedding quota.

**Root cause:** Every call to `answer_question` re-runs `chunk_transcript`, `setup_credentials`, `initialize_watsonx_llm`, `setup_embedding_model` and `create_faiss_index` (`ytbot.py:365-379`). It builds a new `FAISS.from_texts` index and throws it away afterwards. Nothing caches the index per video. With `chunk_size=200` (`ytbot.py:68`), a 10-minute transcript is on the order of 100 chunks per question.

---

## BUG-003 — Prompts use Llama 3 chat-template tokens but are sent to an IBM Granite model

**Severity:** Medium
**Status:** Fix Planned
**Reported:** 2026-11-11
**Related requirements:** FR-002, FR-003 (the quality of the summary and the answers), IC-001 (watsonx-served model). Using the correct prompt format for the model was an unwritten assumption.
**Fix plan:** `ai-plans/bugfix-llama-tokens-granite-plan.md`

**Reproduction steps:**
1. Start `ytbot.py` with working watsonx credentials. `verbose=True` is already the default, so the chains print the prompt they send
2. Summarize any video, then ask any question
3. Read the prompt text printed to the console

**Expected behavior:** The prompt sent to `ibm/granite-4-h-small` uses Granite's own chat format, or goes through the chat API so watsonx applies the format on the server.

**Actual behavior:** Both prompts start with `<|begin_of_text|><|start_header_id|>system<|end_header_id|>` and use `<|eot_id|>`, which is Llama 3's chat template. Granite receives these markers as plain text. How much this hurts output quality hasn't been measured.

**Root cause:** The templates in `create_summary_prompt` (`ytbot.py:162-175`) and `create_qa_prompt_template` (`ytbot.py:221-235`) hard-code Llama 3 special tokens, presumably left over from when the course used a Llama model. `WatsonxLLM` calls the text-generation (completion) endpoint, which sends the string to the model as-is and applies no chat template. `model_id` is now `ibm/granite-4-h-small` (`ytbot.py:82`). Each line of the template also carries 4 spaces of indentation from the triple-quoted string.

---

## BUG-004 — Retrieved context is sent to the LLM as Python `Document` reprs, not text

**Severity:** Low
**Status:** Fix Planned
**Reported:** 2026-11-11
**Related requirements:** FR-003 (answer from the relevant segments), FR-006 (timestamps must be easy to find in the context)
**Fix plan:** `ai-plans/bugfix-raw-document-context-plan.md`

**Reproduction steps:**
1. Start `ytbot.py` with working watsonx credentials (`verbose=True` is the default)
2. Enter a video URL and ask any question
3. Read the printed prompt after `Relevant Video Context:`

**Expected behavior:** The context is the retrieved transcript text, one segment per line or block, for example `Text: ... Start: 12.3`.

**Actual behavior:** The context is a stringified Python list, such as `[Document(id='…uuid…', metadata={}, page_content='Text: … Start: 12.3\nText: …'), Document(…), …]`. It contains UUIDs, escaped newlines and repr syntax.

**Root cause:** `retrieve` returns `list[Document]` (`ytbot.py:210`), and `generate_answer` passes that list straight in as `context=` (`ytbot.py:285`). The prompt template formats it with `str()`, so it ends up as a repr. Nothing extracts `page_content`.

---

## BUG-005 — "Transcript Status" box is never updated, and fetch errors aren't reported

**Severity:** Low
**Status:** Fix Planned
**Reported:** 2026-11-11
**Related requirements:** UC-001 and UC-002 exception flows (an invalid reference or a missing transcript should produce a "clear error"). The status box's own purpose isn't documented anywhere.
**Fix plan:** `ai-plans/bugfix-transcript-status-unused-plan.md`

**Reproduction steps:**
1. Start `ytbot.py` and open the UI
2. Enter a valid video URL and click "Summarize Video". The Transcript Status box stays empty
3. Enter `https://youtu.be/<any id>` (or any non-`www.youtube.com/watch` URL) and click "Summarize Video"
4. Enter the URL of a video that has no English transcript and click "Summarize Video"

**Expected behavior:** The status box shows whether a transcript was fetched, for which video, and why not if it failed. Steps 3 and 4 show a clear error message.

**Actual behavior:** The status box is always empty. Step 3 makes Gradio show a generic "Error": `get_video_id` returns `None`, and the call to `ytt_api.list(None)` then fails (the exact exception has not been checked). Step 4 also shows a generic "Error": `get_transcript` returns `None`, and then `process(None)` raises `TypeError` while iterating.

**Root cause:** `transcript_status` is created (`ytbot.py:408`) but isn't an output of either `.click` handler (`ytbot.py:411-412`), and no function returns a value for it. `get_video_id` returns `None` for unmatched URLs (`ytbot.py:23`), and nothing checks for that before the call to `ytt_api.list` (`ytbot.py:33`). `process` iterates its argument without a `None` check (`ytbot.py:56`). Its `except KeyError` (`ytbot.py:61`) can't catch the errors that attribute access actually raises, which are `AttributeError` and `TypeError`. So the "No transcript available" branch (`ytbot.py:332`) can't be reached.

---

<!-- Add new bugs via /fix-bug, or by hand — keep the section format: metadata lines,
     then Reproduction / Expected / Actual / Root Cause. A bug with no reproduction
     steps yet is a symptom report, not a bug entry — get concrete steps before
     assigning an ID if at all possible. -->
