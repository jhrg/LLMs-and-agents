
# Implementation Constraints

Convention: `IC-###`. Category is one of: Technology/Platform, Infrastructure/
Deployment, Regulatory/Compliance, Organizational/Team, Third-Party/Integration,
Budget/Timeline (add categories as needed).

| ID | Category | Constraint | Rationale | Impact on design |
|---|---|---|---|---|
| IC-001 | Third-Party/Integration | **Status: Superseded by IC-006.** The LLM and the embedding model are served by IBM watsonx, using the user's own IBM Cloud account (API key plus a real project ID) | The user chose to keep the course's provider. The course sandbox's implicit credentials and the `"skills-network"` project ID don't work outside it | No other LLM/embedding providers. Credentials, project ID, region URL and model IDs must be configurable (see IC-002) |
| IC-002 | Security | API keys and other secrets never appear in source code or in files committed to the repo. They come from environment variables or a key file outside the repo | Keeps credentials out of git history | Needs a documented config mechanism. The tool fails with a clear message when credentials are missing |
| IC-003 | Infrastructure/Deployment | The Gradio web UI binds to `127.0.0.1` only, never `0.0.0.0` | The tool is for local use. Binding to all interfaces exposes it, and the user's watsonx quota, to the LAN | The original's `server_name="0.0.0.0"` must change. No remote or shared deployment |
| IC-004 | Technology/Platform | Dependencies are pinned in a `requirements.txt` and installed into a project-local venv. They must install and run on a current Python (minimum version 3.11) | `packages.txt`'s 2024 pins and its gradio/huggingface_hub workarounds aren't reproducible | A pinned `requirements.txt` replaces `packages.txt` as the source of truth |
| IC-005 | Technology/Platform | Only current, non-deprecated LangChain APIs are used. No `LLMChain`, `Chain.run`/`.predict`, `langchain.text_splitter` or `langchain.prompts` imports | Those APIs are deprecated or removed in LangChain 1.x | Chains are built with LCEL (`prompt \| llm \| parser`), importing from `langchain_core`, `langchain_text_splitters`, `langchain_community` and the chosen providers' LangChain integration packages (e.g. `langchain_ibm`, `langchain_anthropic`, `langchain_openai`; see IC-006) |
| IC-006 | Third-Party/Integration | The LLM and the embedding model may come from any provider that has a current, maintained LangChain integration package (for example IBM watsonx, Anthropic, OpenAI), using the user's own account with that provider. The LLM and embedding providers may differ | Supersedes IC-001. On 2026-11-11 the user decided not to lock the tool to watsonx | No hard-coded provider. The provider, model IDs, and provider-specific settings (such as the watsonx URL and project ID) must be configurable, with credentials handled per IC-002. Embeddings may need a separate provider, because Anthropic has no embeddings API. Default provider(s): TBD |


