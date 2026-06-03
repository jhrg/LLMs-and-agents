# LLMs-and-agents

## Labs

### Lab 1

- **Title:** Build an AI Math Assistant with LangChain Tool Calling
- **Filename:** `Lab-1-Hello-World-v1.ipynb`
- **Summary:** Introduces LangChain tool calling by building a math assistant
  that can add, subtract, multiply, and divide through natural-language prompts.
  The lab compares `Tool(...)` and `@tool`, explains how agent/tool
  compatibility depends on input and return schemas, shows how to debug broken
  tool behavior, and finishes by extending the agent with a Wikipedia lookup
  tool plus an exercise to add exponent support.

### Lab 2

- **Title:** DataWizard: AI-Powered Data Analysis
- **Filename:** `Lab-2-LLM-Powered-Data-Science-v1.ipynb`
- **Summary:** Builds a data-analysis agent that helps users explore CSV
  datasets with natural language. It creates tools for listing files, caching
  DataFrames, generating dataset summaries, running selected pandas methods, and
  evaluating classification or regression datasets with scikit-learn, then wraps
  them in an OpenAI tools agent and `AgentExecutor` to support multi-step
  dataset analysis workflows.

### Lab 3

- **Title:** Build Interactive LLM Agents with Tools
- **Filename:** `Lab-3-Interactive-Tool-Calling-Agent-v1.ipynb`
- **Summary:** Walks through the mechanics of direct tool calling with LangChain
  and OpenAI models using simple arithmetic tools. The lab shows how to define
  tools, bind them to a model, inspect `tool_calls`, execute the requested
  function, return `ToolMessage` results, and then package the whole loop into a
  small reusable agent class, with exercises based on a tip calculator.

### Lab 4

- **Title:** Build a Tool Calling Agent
- **Filename:** `Lab-4-Tool-Calling-v1.ipynb`
- **Summary:** Develops a richer tool-calling agent around YouTube workflows. It
  defines tools for extracting video IDs, fetching transcripts, searching
  YouTube, retrieving metadata, listing trending videos, and collecting
  thumbnails, then demonstrates manual multi-step tool orchestration, fixed
  LangChain runnable chains, and a recursive chain that keeps calling tools
  until the model reaches a final answer such as a video summary or
  trending-video report.
