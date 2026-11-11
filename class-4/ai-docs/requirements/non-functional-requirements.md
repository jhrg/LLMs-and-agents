<!-- CONTRACT: quality attributes the system must meet, with a measurable target where
     possible. "Fast" and "user-friendly" are not requirements — a number or a
     testable condition is. Delete the _EXAMPLE_ row once you've seen the shape. -->

# Non-Functional Requirements

Convention: `NFR-###`. Category is one of: Performance, Security, Reliability,
Availability, Scalability, Usability, Maintainability, Compliance, Observability
(add categories as needed — keep the list here in sync). Priority: `Must` / `Should`
/ `Could`. Status as in functional-requirements.md.

| ID | Category | Requirement | Measurable Target | Priority | Status |
|---|---|---|---|---|---|
| NFR-001 | Maintainability | The default test suite runs without network access or credentials | `pytest` (no `-m live`) passes on a machine with no network and no watsonx credentials set | Must | Approved |

<!-- If you genuinely can't state a measurable target yet, write TBD in that column
     rather than a vague phrase — TBD is honest and searchable; "reasonably fast"
     just looks finished. -->
