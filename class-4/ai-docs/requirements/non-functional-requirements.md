
# Non-Functional Requirements

Convention: `NFR-###`. Category is one of: Performance, Security, Reliability,
Availability, Scalability, Usability, Maintainability, Compliance, Observability
(add categories as needed — keep the list here in sync). Priority: `Must` / `Should`
/ `Could`. Status as in functional-requirements.md.

| ID | Category | Requirement | Measurable Target | Priority | Status |
|---|---|---|---|---|---|
| NFR-001 | Maintainability | The default test suite runs without network access or credentials | `pytest` (no `-m live`) passes on a machine with no network and no watsonx credentials set | Must | Approved |
