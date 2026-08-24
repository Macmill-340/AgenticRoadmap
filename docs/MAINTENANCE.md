# Maintenance — research before you write

Last grounded: 2026-08-23

A new session writing any later phase **must re-fetch official docs**. Do not treat this file, prior chat, or `agentic-frameworks-teaching-roadmap.md` (local only — not in the repo) as API truth.

## Standing rules

1. Fetch the URLs for the batch you are writing. If a URL 404s, open that site's `llms.txt` / section index and find the replacement. Do not invent URLs.
2. Confirm imports against the **installed pin**, not the docs date. Especially LangGraph.
3. Each `agents/*` folder is a uv project: direct deps in `pyproject.toml`, exact pins in the committed `uv.lock`. Set up with `uv sync`, extend with `uv add`. The root `pyproject.toml` is an IDE shim (no deps) — never `uv add` / `uv sync` there.
4. Check LangGraph + `llama-index-core` + `litellm` changelogs since the last `Last grounded` date.
5. Defaults: LiteLLM → Gemini for chat; HuggingFace `all-MiniLM-L6-v2` for embeddings. Ollama optional.
6. Pedagogy lock: see `AGENTS.md`.
7. Windows: no WSL assumed. `asyncio` HTTP is fine. Subprocess tools: one-line Proactor note.
8. Do not expand the parking lot into new phases without an explicit request.
9. Do not install `litellm[proxy]`.
10. After the batch: set `Last grounded: YYYY-MM-DD` on every file you wrote, and update `docs/STATUS.md`.

## Always fetch (every batch)

- https://docs.langchain.com/oss/python/langgraph/changelog-py
- https://docs.llamaindex.ai/en/stable/changelog/ (fallback: https://docs.llamaindex.ai/en/stable/python/framework/changelog/)
- https://docs.astral.sh/uv/getting-started/installation/
- https://docs.astral.sh/uv/pip/packages/
- https://docs.litellm.ai/docs/

## Batch 1 — setup + Phases 0–2

- https://docs.llamaindex.ai/en/stable/understanding/agent/
- https://docs.llamaindex.ai/en/stable/getting_started/installation/
- https://docs.llamaindex.ai/en/stable/getting_started/async_python/
- https://docs.llamaindex.ai/en/stable/integrations/llm/litellm/
- https://docs.litellm.ai/docs/providers/gemini
- https://platform.openai.com/docs/guides/function-calling
- https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/handle-tool-calls
- https://huggingface.co/learn/agents-course/unit1/what-are-llms
- https://huggingface.co/learn/agents-course/unit1/agent-steps-and-structure
- https://huggingface.co/learn/agents-course/unit1/dummy-agent-library
- https://huggingface.co/spaces/Xenova/the-tokenizer-playground
- https://docs.pydantic.dev/latest/concepts/models/

## Batch 2 — Phases 3–6

- https://docs.llamaindex.ai/en/stable/module_guides/supporting_modules/settings/
- https://docs.llamaindex.ai/en/stable/understanding/rag/
- https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader/
- https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/
- https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores/
- https://docs.llamaindex.ai/en/stable/integrations/vector_stores/chromaindexdemo/
- https://docs.llamaindex.ai/en/stable/integrations/embeddings/huggingface/
- https://docs.llamaindex.ai/en/stable/module_guides/querying/node_postprocessors/
- https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/
- https://docs.trychroma.com/docs/overview/getting-started

## Batch 3 — Phases 7 + 7b

- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.langchain.com/oss/python/langgraph/graph-api
- https://docs.langchain.com/oss/python/langgraph/use-graph-api
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/checkpointers
- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
- https://docs.langchain.com/oss/python/langgraph/agentic-rag
- https://docs.langchain.com/oss/python/langchain/agents
- https://docs.langchain.com/oss/python/langchain/tools
- https://docs.langchain.com/oss/python/langchain/multi-agent
- https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
- https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs
- https://docs.llamaindex.ai/en/stable/understanding/agent/multi_agent/

## Batch 4 — Phases 8–9 + parking lot

- https://huggingface.co/docs/smolagents/en/index
- https://huggingface.co/docs/smolagents/en/guided_tour
- https://platform.openai.com/docs/guides/function-calling
- https://docs.langchain.com/oss/python/langchain/structured-output
- Parking-lot only (fetch if writing the appendix): LlamaIndex MCP, LangGraph MCP, LangSmith observability, Ollama OpenAI compat

## Known API drift (as of 2026-08-21)

| Item | Current | Stale |
|---|---|---|
| One-tool LlamaIndex agent | `FunctionAgent` | `AgentWorkflow` for a single tool |
| LangGraph prebuilt ReAct | `from langchain.agents import create_agent` | `from langgraph.prebuilt import create_react_agent` |
| In-memory checkpointer | `InMemorySaver` | older `MemorySaver` name in some posts |
| OpenAI official loop | Responses API | This course uses Chat Completions via LiteLLM until Phase 9 |
| Chat default | LiteLLM `gemini/gemini-2.5-flash` | Ollama as required |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Ollama `nomic-embed-text` |
| Install | `uv sync` / `uv add` per `agents/*` uv project | bare pip; freeze-into-requirements; root uv workspace / shared lock |
| LiteLLM | Python SDK only (`litellm`) | `litellm[proxy]` |
| LlamaIndex defaults | `Settings.llm` / `Settings.embed_model` must be set | relying on defaults |
| HITL | `interrupt()` + `Command(resume=...)` | `input()` inside a node |
