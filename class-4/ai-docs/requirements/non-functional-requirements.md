
# Non-Functional Requirements

Convention: `NFR-###`. Category is one of: Performance, Security, Reliability,
Availability, Scalability, Usability, Maintainability, Compliance, Observability
(add categories as needed — keep the list here in sync). Priority: `Must` / `Should`
/ `Could`. Status as in functional-requirements.md.

| ID | Category | Requirement | Measurable Target | Priority | Status |
|---|---|---|---|---|---|
| NFR-001 | Maintainability | The default test suite runs without network access or credentials | `pytest` (no `-m live`) passes on a machine with no network and no watsonx credentials set | Must | Approved |
| NFR-002 | Performance | Asking a further question about a video whose transcript is already loaded doesn't re-embed the transcript | After the first question on a video ID, later questions in the same session make 0 `embed_documents` calls and 1 `embed_query` call each (offline test with a counting fake embedder) | Must | Approved |
