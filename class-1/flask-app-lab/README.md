
# Generative AI applications using Flask.
Cousera course #1 lab #3. This uses IBM's Watson LLM

## Enviroment
Set up an enviroment for the code.

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install ibm-watsonx-ai==1.3.39
```

This is all you need to run capital.py

For the Flask code, use this:
```bash
pip install Flask langchain-ibm langchain
```

## Different models

| Provider	| Model ID	| Use Cases	| Context Length	| Price USD per million tokens |
| ---- | ---- | ---- | ---- | ---- |
| IBM	| ibm/granite-4-h-small	|Q&A, summarization, classification, generation, extraction, RAG, coding, and multi-tool agentic workflows.	| 128k	| Input: 0.06 / Output: 0.25 |
| Meta	| meta-llama/llama-4-maverick-17b-128e-instruct-fp8	| Multimodal reasoning, long-context processing, code generation and analysis, multilingual operations (200 languages supported), STEM and logical reasoning.	| 1M	| Input: 0.35 / Output: 1.40 |
| Mistral	| mistralai/mistral-small-3-1-24b-instruct-2503	| Instruction following, conversational assistance, image understanding, function calling, multilingual Q&A, summarization, classification, generation, and RAG.	| 128k	| Input: 0.10 / Output: 0.30 |
| Mistral	| mistralai/mistral-medium-2505	| Programming, mathematical reasoning, long document understanding, summarization, dialogue, and multimodal (text + image) tasks.	| 128k	| Input: 0.40 / Output: 2.00 |

## Issue
I think the modification to the AIResponse class in model.py is correct, but it's not the only change to the code
needed to make the 'AI Assistant' work. The new field seems to have not been incorporated into the chain.
