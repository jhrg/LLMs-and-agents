# Plan: Standalone ytbot v1

**Feature:** FEAT-001
**Status:** Draft
**Created:** 2026-11-11

## Summary

Rebuild the course-only `ytbot.py` as a small Python package that runs on your own machine with your own watsonx account. It has one core shared by a CLI and a local Gradio UI, and adds broad URL support, long-video summaries and timestamped answers. The original script can't run outside the Coursera sandbox, and nearly every function needs changing for IC-005 anyway, so a structured rewrite is cheaper than patching it.

## Requirements traced

- FR-001 — fetch a video's transcript (Phase 2)
- FR-002 — one-paragraph summary (Phase 3)
- FR-003 — question answering over retrieved transcript segments (Phase 4)
- FR-004 — accepted URL forms and bare IDs (Phase 2)
- FR-005 — complete summaries of transcripts longer than the context window (Phase 3)
- FR-006 — timestamp citations in answers (Phase 4)
- FR-007 — CLI (Phase 5)
- FR-008 — local Gradio UI with the same capabilities (Phase 6)
- NFR-001 — the default `pytest` run needs no network or credentials (Phase 1 sets it up, and every phase adds tests to it)
- UC-001 — summarize a video, main and exception flows (Phases 2, 3, 5, 6)
- UC-002 — ask about a video, main and exception flows (Phases 2, 4, 5, 6)

Not cited by FEAT-001 but affected: **NFR-002** (no re-embedding on follow-up questions). You chose to leave it to the BUG-002 fix. The session cache in Phase 4 meets it anyway; see "Relationship to open bugs".

## Constraints considered

- IC-001 (watsonx only, your own account, configurable model IDs). `ChatWatsonx` and `WatsonxEmbeddings` from `langchain_ibm` are the only model clients. The URL, project ID, LLM model ID and embedding model ID all come from config (Phase 1), with today's models as defaults.
- IC-002 (no secrets in the repo). Config reads `WATSONX_APIKEY`, `WATSONX_URL` and `WATSONX_PROJECT_ID` from the environment, which are the names `langchain_ibm` already recognizes, plus an optional env-style key file outside the repo (location: open question 6). Missing values produce a clear error that names the variable, before any network call. `.gitignore` covers `.env*` and `.venv/`.
- IC-003 (bind to `127.0.0.1` only). The `web` command calls `launch(server_name="127.0.0.1", share=False)`. No option exposes it more widely.
- IC-004 (pinned `requirements.txt`, project venv, Python ≥ 3.11). Phase 1 resolves current versions in a fresh 3.11+ venv and pins them exactly. `packages.txt` stays only as a historical reference, and CLAUDE.md already says so.
- IC-005 (non-deprecated LangChain only). Use LCEL chains (`ChatPromptTemplate | ChatWatsonx | StrOutputParser`), `langchain_text_splitters`, and `FAISS` from `langchain_community` (which IC-005 allows). No `LLMChain`, `.run` or `.predict`. A test greps the package for the banned imports.

No constraint conflicts found.

## Relationship to open bugs

All five logged bugs are in code this plan replaces. The rewrite fixes them by design:

| Bug | Fixed in | How |
|---|---|---|
| BUG-001 stale transcript | Phase 4 / 6 | Per-session cache keyed by video ID, no module globals |
| BUG-002 index rebuilt per question | Phase 4 | Index built once per video in the session cache (meets NFR-002) |
| BUG-003 Llama tokens sent to Granite | Phase 3 | `ChatWatsonx` + `ChatPromptTemplate`, so the server applies Granite's own template |
| BUG-004 `Document` reprs in prompt | Phase 4 | `format_context()` renders `[mm:ss] text` |
| BUG-005 status box / unreported errors | Phase 2 / 6 | `TranscriptError` with user-facing messages; status box wired up |

Recommendation: treat the five bugfix plans as superseded by this plan, rather than also applying them to the old `ytbot.py` (open question 1). Each phase's tests include the bug's reproduction as a regression test. Bug statuses stay yours to set.

## Phases

### Phase 1 — Project skeleton, dependencies, config

**Goal:** A package layout that installs cleanly from a pinned `requirements.txt`, an offline test harness, and credential loading.
**Satisfies:** NFR-001; groundwork for UC-001/UC-002 ("credentials missing or rejected" exception flow)

Steps:
1. Layout: `ytbot/` (`__init__.py`, `__main__.py`, `config.py`, `video.py`, `transcript.py`, `models.py`, `summarize.py`, `qa.py`, `cli.py`, `web.py`) and `tests/`. Move the course script to `course/ytbot.py`, unchanged, as a reference. A `ytbot.py` next to a `ytbot/` package makes imports ambiguous (open question 8).
2. Create a Python ≥ 3.11 venv, install the current releases of `langchain-core`, `langchain-text-splitters`, `langchain-community`, `langchain-ibm`, `ibm-watsonx-ai`, `faiss-cpu`, `youtube-transcript-api`, `gradio` and `pytest`, check that they import, and pin them with `==` in `requirements.txt`.
3. `pytest.ini` (or `pyproject` `[tool.pytest]`): register a `live` marker, and set `addopts = -m "not live"` so the default run is offline.
4. `config.py`: a `Settings` dataclass (api key, url, project id, llm model id, embedding model id, summary context budget) loaded from the environment and then the optional key file. `ConfigError` names the variable that's missing. Defaults: `ibm/granite-4-h-small` and `ibm/granite-embedding-278m-multilingual` (open question 7).
5. `.gitignore`: `.venv/`, `__pycache__/`, `.env*`.
6. Tests: config loading with `monkeypatch`ed env (present, missing, key file), and a guard test that no module imports `langchain.chains`, `langchain.prompts` or `langchain.text_splitter` (IC-005).

**Risks:** Current `langchain-ibm` / `ibm-watsonx-ai` / `gradio` versions may not resolve together. Find out in step 2, before any code depends on them.

### Phase 2 — Video references and transcript fetching

**Goal:** Turn any accepted reference into a video ID, and fetch a transcript as timestamped segments, with clear errors.
**Satisfies:** FR-004, FR-001, UC-001 / UC-002 exception flows (invalid reference, no usable transcript)

Steps:
1. `video.parse_video_ref(ref) -> str`: parse with `urllib.parse` (not a single regex). Handle `www.`/`m.youtube.com/watch?v=` with any extra query parameters, `youtu.be/<id>`, `youtube.com/shorts/<id>`, and a bare 11-character ID. Raise `TranscriptError("unrecognized video reference…")` listing the accepted forms.
2. `transcript.fetch(video_id) -> Transcript`. `Transcript` holds `video_id`, `language`, `is_generated` and `segments: list[Segment(text, start, duration)]`. Language selection follows the original's policy (English, hand-made over auto-generated) until FR-001's TBD is settled (open question 2), and the policy lives in a single function so it's easy to change.
3. Map `youtube-transcript-api` exceptions (transcripts disabled, no transcript found, video unavailable, request blocked) to `TranscriptError` with readable messages. Never return `None`.
4. Tests (offline, using a stubbed `YouTubeTranscriptApi`): a table of URL forms → IDs, plus rejects; manual preferred over generated; no English → error; each library exception → its message. BUG-005 steps 3 and 4 become regression tests.

**Risks:** YouTube blocks some IPs (cloud and VPN). Live fetch tests may fail for network reasons that have nothing to do with the code. Keep them under `live`.

### Phase 3 — Model clients and summarization (including long videos)

**Goal:** One-paragraph summaries for any transcript length, using properly formatted chat prompts.
**Satisfies:** FR-002, FR-005, UC-001 main flow steps 3–4

Steps:
1. `models.py`: `chat_model(settings)` → `ChatWatsonx` with greedy decoding and a max-tokens setting; `embeddings(settings)` → `WatsonxEmbeddings`. Both are created lazily, once per process.
2. Prompts as `ChatPromptTemplate.from_messages([("system", …), ("human", …)])`, with no special tokens and no stray indentation (BUG-003). The summary input is the plain transcript text without timestamps, so the model doesn't need to be told to ignore `Start:` values.
3. `summarize(transcript, llm, settings)`: estimate the prompt size (method: open question 3). If it fits within `settings.summary_context_budget`, make one call. Otherwise **map-reduce**: split the segment text into budget-sized pieces with `RecursiveCharacterTextSplitter`, summarize each piece into notes (map), then combine the notes into the final paragraph (reduce). Reduce recursively if the combined notes still exceed the budget. Every segment ends up in exactly one map input, with no truncation (FR-005).
4. Tests with a fake chat model (LangChain's `FakeListChatModel` or a stub runnable): a short transcript makes a single call; a long transcript (with a deliberately tiny budget) goes through map-reduce; the map inputs together cover every segment's text; rendered prompts contain no `<|…|>` tokens.

**Risks:** The right budget depends on Granite's real context limit on watsonx and on the input-token limits of your plan. A conservative default plus config avoids hard failures. Map-reduce raises cost and latency for long videos, which is accepted under FR-005.

### Phase 4 — Q&A with timestamp citations, and the session cache

**Goal:** Answers grounded in the retrieved segments that cite where in the video they come from, and a per-video cache so transcripts and indexes aren't rebuilt.
**Satisfies:** FR-003, FR-006, UC-002 main flow steps 2–5 and the "empty question" exception flow

Steps:
1. Chunking keyed by time: group consecutive segments into chunks of about N characters (configurable). Each chunk is a `Document` with `page_content` = joined text and `metadata = {"start": first_segment.start, "end": …}`. This replaces character-splitting the `Text: … Start: …` string, so every chunk carries an exact start time.
2. `VideoSession` (a per-video cache entry): `transcript`, a lazily built `FAISS` index, and a lazily built summary. `SessionCache` is a dict from `video_id` to `VideoSession`. There are no module globals (BUG-001). The index is built once per video (BUG-002, meets NFR-002).
3. `format_context(docs)`: retrieved chunks sorted by start time and rendered as `[mm:ss] text` (BUG-004).
4. A QA chain (LCEL) whose system prompt says to answer only from the context and cite `[mm:ss]` markers. Citation post-processing follows open question 4: either check the model's citations against the retrieved chunks, or append a deterministic "Sources" list. Each source links as `https://youtu.be/<id>?t=<seconds>`.
5. An empty question returns a prompt to ask something, with no LLM or embedding call. The "answer not in the video" behavior follows open question 5.
6. Tests: a fake embedder that counts calls (two questions on one video → one `embed_documents`; switching video → a new index; BUG-001 and BUG-002 reproductions); the `format_context` output; citation formatting and links; an empty question makes no model calls.

**Risks:** Instruction-following for citations is model-dependent. That's why the deterministic fallback is in the open questions.

### Phase 5 — CLI

**Goal:** Scriptable access to both capabilities.
**Satisfies:** FR-007, UC-001, UC-002 (CLI triggers)

Steps:
1. `python -m ytbot summarize <ref>`, `python -m ytbot ask <ref> "<question>" [--question …]` (repeatable `--question` reuses one `VideoSession`, so follow-up questions don't re-embed), and `python -m ytbot web` (Phase 6). Built with `argparse`.
2. Output: the summary or answer on stdout. `TranscriptError` / `ConfigError` messages go to stderr, and the process exits with a non-zero code (distinct codes for config, transcript and model errors).
3. Tests: run `cli.main([...])` with the core functions stubbed, and check output, stderr and exit codes for success, a bad reference and missing credentials.

**Risks:** None notable.

### Phase 6 — Local Gradio UI

**Goal:** Browser access to the same core, bound to localhost.
**Satisfies:** FR-008, UC-001, UC-002 (web triggers and exception flows)

Steps:
1. `web.build_app(settings) -> gr.Blocks`: a URL box, "Summarize Video", a question box, "Ask a Question", summary and answer outputs, and a **Transcript Status** box that both handlers update (BUG-005). The `SessionCache` is held in `gr.State`, so each browser session gets its own (BUG-001).
2. Handlers call the same core functions as the CLI, catch `TranscriptError` / `ConfigError` and show the message in the status box. No Python tracebacks reach the UI.
3. `launch(server_name="127.0.0.1", server_port=7860, share=False)` (IC-003). The port can be changed with `--port`.
4. Tests: call the handler functions directly with stubs (no browser), including the BUG-001 URL-switch sequence, and assert that the launch settings use `127.0.0.1`.

**Risks:** Gradio's API changes between major versions. Pin it in Phase 1 and write against that version.

### Phase 7 — Live verification and usage docs

**Goal:** Confirm the whole flow against real YouTube and watsonx, and document how to set it up.
**Satisfies:** UC-001, UC-002 (end to end); keeps NFR-001 intact by marking these tests `live`

Steps:
1. `tests/test_live.py` (`@pytest.mark.live`): fetch a short, stable, captioned video, summarize it, and ask one question. Assert that the summary is non-empty and that the answer has a valid timestamp link. Quality is judged by eye.
2. Run the original reproduction steps of BUG-001 to BUG-005 against the web UI by hand, and record the results in this plan's work log.
3. A short `README.md` in `class-4/`: venv setup, credential variables and key file, the CLI commands, and `python -m ytbot web`.

**Risks:** Needs a working IBM Cloud account with access to the default models (open question 7).

## Open questions

1. **Bug plans superseded?** Recommendation: this plan fixes BUG-001 to BUG-005 and the five bugfix plans are not carried out separately. This only affects whether those plans are worked on their own. It doesn't block a phase.
2. **FR-001 language policy (TBD).** Which transcript languages, and whether hand-made beats auto-generated. Blocks *finalizing* Phase 2. The interim default is English, hand-made first.
3. **Context budget for summaries.** Granite 4 H Small's usable input size on your watsonx plan, and how to count tokens: the watsonx tokenize endpoint (exact, but one extra call per summary) or a character heuristic (free, approximate). Blocks the Phase 3 default.
4. **How FR-006 citations are produced.** Trust the model's `[mm:ss]` citations (checked against the retrieved chunks), or always append a deterministic "Sources" list of the retrieved chunks' times, or both. Blocks Phase 4 step 4.
5. **UC-002 "answer not in the video."** It's marked "behavior: TBD, confirm". The proposed behavior is to say the video doesn't cover it. Blocks the Phase 4 prompt wording.
6. **Key file location (IC-002).** For example `~/.config/ytbot/env`, or a path from `YTBOT_ENV_FILE`. Doesn't block, because environment variables work first.
7. **Model IDs and access.** Are `ibm/granite-4-h-small` and `ibm/granite-embedding-278m-multilingual` available in your account and region? Blocks Phase 7, and possibly the Phase 1 defaults.
8. **Where the original script goes.** The proposal is `course/ytbot.py`, kept unchanged. Blocks Phase 1 step 1.

## Out of scope

- LLM or embedding providers other than watsonx (IC-001).
- Saving indexes, summaries or answers to disk between runs (UC-001 postcondition is TBD).
- Remote or multi-user deployment (IC-003).
- An interactive REPL-style CLI chat. Repeated `--question` covers follow-up questions in one run.
- Retries and rate-limit handling beyond clear error messages (UC-001 "other failures: TBD").
- Tuning prompt wording for quality, beyond what the requirements specify.

## Work log

### 2026-11-11 16:24 MST — Plan created

**Prompt:**

> /plan-feature FEAT-001

Re-read the requirement and constraint docs (no ADRs exist), confirmed that FEAT-001's requirement list matches, and reviewed `ytbot.py`. Drafted a 7-phase plan to rebuild it as a package, which absorbs the fixes for BUG-001 to BUG-005. Eight open questions are recorded, and four of them block parts of specific phases.
