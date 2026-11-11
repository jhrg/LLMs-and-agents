<!-- CONTRACT: things that constrain HOW the system can be built, independent of
     what it must do. These are boundaries, not preferences — if a plan would cross
     one, that's a flag, not a quiet redesign. Delete the _EXAMPLE_ row once you've
     seen the shape. -->

# Implementation Constraints

Convention: `IC-###`. Category is one of: Technology/Platform, Infrastructure/
Deployment, Regulatory/Compliance, Organizational/Team, Third-Party/Integration,
Budget/Timeline (add categories as needed).

| ID | Category | Constraint | Rationale | Impact on design |
|---|---|---|---|---|
| IC-001 | Third-Party/Integration | The LLM and the embedding model are served by IBM watsonx, using the user's own IBM Cloud account (API key plus a real project ID) | The user chose to keep the course's provider. The course sandbox's implicit credentials and the `"skills-network"` project ID don't work outside it | No other LLM/embedding providers. Credentials, project ID, region URL and model IDs must be configurable (see IC-002) |
| IC-002 | Security | API keys and other secrets never appear in source code or in files committed to the repo. They come from environment variables or a key file outside the repo | Keeps credentials out of git history | Needs a documented config mechanism. The tool fails with a clear message when credentials are missing |
| IC-003 | Infrastructure/Deployment | The Gradio web UI binds to `127.0.0.1` only, never `0.0.0.0` | The tool is for local use. Binding to all interfaces exposes it, and the user's watsonx quota, to the LAN | The original's `server_name="0.0.0.0"` must change. No remote or shared deployment |
| IC-004 | Technology/Platform | Dependencies are pinned in a `requirements.txt` and installed into a project-local venv. They must install and run on a current Python (minimum version TBD) | `packages.txt`'s 2024 pins and its gradio/huggingface_hub workarounds aren't reproducible | A pinned `requirements.txt` replaces `packages.txt` as the source of truth |
| IC-005 | Technology/Platform | Only current, non-deprecated LangChain APIs are used. No `LLMChain`, `Chain.run`/`.predict`, `langchain.text_splitter` or `langchain.prompts` imports | Those APIs are deprecated or removed in LangChain 1.x | Chains are built with LCEL (`prompt \| llm \| parser`), importing from `langchain_core`, `langchain_text_splitters`, `langchain_community` and `langchain_ibm` |

<!-- A constraint is not the same as a non-functional requirement: an NFR describes
     a quality the system should have (and can trade off); a constraint is a boundary
     condition that plans must work within, full stop. If it's negotiable, it's
     probably an NFR with a priority, not a constraint. -->
