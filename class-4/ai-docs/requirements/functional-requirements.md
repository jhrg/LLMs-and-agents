
# Functional Requirements

Convention: `FR-###`, zero-padded, assigned sequentially by next-highest-number.
Priority: `Must` / `Should` / `Could` (MoSCoW). Status: `Proposed` / `Approved` /
`Implemented` / `Deprecated` / `Superseded by FR-0XX`. `Proposed` means drafted but
not yet confirmed. It isn't a proposed *feature*; those live outside this repo until
accepted. `Implemented` is normally set by `/features` when a `FEAT` that cites the
FR reaches `Done`.

| ID | Requirement | Priority | Related Use Cases | Status |
|---|---|---|---|---|
| FR-001 | Given a YouTube video, the tool fetches that video's transcript (preferred language and manual vs. auto-generated policy: TBD) | Must | UC-001, UC-002 | Approved |
| FR-002 | The tool produces a concise one-paragraph summary of a video from its transcript | Must | UC-001 | Approved |
| FR-003 | The tool answers a free-text question about a video by retrieving the relevant transcript segments and generating an answer from them | Must | UC-002 | Approved |
| FR-004 | The tool accepts any of these video references: `www.`/`m.youtube.com/watch?v=<id>` (with extra query parameters allowed), `youtu.be/<id>`, `youtube.com/shorts/<id>`, or a bare 11-character video ID | Must | UC-001, UC-002 | Approved |
| FR-005 | The tool summarizes transcripts longer than the LLM's context window completely, without failing and without silently truncating the transcript | Must | UC-001 | Approved |
| FR-006 | Each answer to a question cites the video timestamp(s) where the supporting information appears | Must | UC-002 | Approved |
| FR-007 | The tool offers a command-line interface for summarizing a video and asking a question about it | Must | UC-001, UC-002 | Approved |
| FR-008 | The tool offers a Gradio web UI, run locally, with the same summarize and question capabilities as the CLI | Must | UC-001, UC-002 | Approved |
