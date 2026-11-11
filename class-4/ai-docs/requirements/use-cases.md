
# Use Cases

Convention: `UC-###`. Each use case follows the template below. Link related `FR-###`
/ `NFR-###` IDs at the bottom so `/trace` can find them in both directions.

---

## UC-001 — Summarize a YouTube video

**Actor(s):** Local user (the tool's only user, running it on their own machine)

**Trigger:** User runs the summarize command in the CLI, or enters a video reference and clicks "Summarize Video" in the web UI

**Preconditions:** watsonx credentials are configured. The machine can reach YouTube and watsonx

**Main flow:**
1. User supplies a video reference (URL or bare ID)
2. Tool resolves the video ID and fetches the transcript
3. Tool generates a summary, splitting the work across chunks when the transcript is longer than the model's context window
4. Tool shows the one-paragraph summary

**Alternate / exception flows:**
- Reference can't be resolved to a video ID → clear error naming the accepted forms
- Video has no usable transcript → clear error saying so (no LLM call is made)
- Credentials missing or rejected → clear error saying which setting is wrong
- Other failures (network, rate limiting): TBD

**Postconditions:** Summary is shown. Whether it is also saved anywhere: TBD

**Related requirements:** FR-001, FR-002, FR-004, FR-005, FR-007, FR-008, IC-001, IC-002

---

## UC-002 — Ask a question about a YouTube video

**Actor(s):** Local user

**Trigger:** User runs the ask command in the CLI with a video reference and a question, or enters both in the web UI and clicks "Ask a Question"

**Preconditions:** As UC-001

**Main flow:**
1. User supplies a video reference and a question
2. Tool resolves the video ID and fetches the transcript, unless it already has the transcript for *that same* video
3. Tool retrieves the transcript segments relevant to the question
4. Tool generates an answer from those segments
5. Tool shows the answer with the timestamp(s) of its supporting segments

**Alternate / exception flows:**
- Same as UC-001 for an invalid reference, a missing transcript, or bad credentials
- Empty question → prompt the user for a question (no LLM call is made)
- Transcript doesn't contain the answer → the tool says so instead of answering from outside the video (behavior: TBD, confirm)

**Postconditions:** Answer is shown with timestamp citations

**Related requirements:** FR-001, FR-003, FR-004, FR-006, FR-007, FR-008, IC-001, IC-002

---
