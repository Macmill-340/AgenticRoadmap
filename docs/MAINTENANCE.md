# Maintenance — research before you write

Last grounded: 2026-09-01

A new session writing any later phase **must re-fetch official docs**. Do not treat this file, prior chat, or `agentic-frameworks-teaching-roadmap.md` (local only — not in the repo) as API truth.

## Standing rules

1. Fetch the URLs for the batch you are writing. If a URL 404s, open that site's `llms.txt` / section index and find the replacement. Do not invent URLs.
2. Confirm imports against the **installed pin**, not the docs date. Especially LangGraph.
3. Each `agents/*` folder is a uv project: direct deps in `pyproject.toml`, exact pins in the committed `uv.lock`. `[project] name` is `course-<folder>` (`course-foundation`, `course-llamaindex`, `course-langgraph`; Phase 8 = `course-smolagents`) — never the PyPI package name, or uv skips installing it. Set up with one idempotent block: `if (Test-Path agents/<group>) { cd agents/<group> }` + `uv sync` + `activate` + `if (-not (Test-Path <phase_file>.py)) { New-Item -ItemType File <phase_file>.py }` (Windows) / `[ -d agents/<group> ] && cd agents/<group>` + `source .venv/bin/activate` + `touch <phase_file>.py` (macOS/Linux). The last line creates only if missing — safe to re-run. Never `New-Item -Force`. The root `pyproject.toml` exists only so PyCharm shows the repo root (no dependencies) — never `uv add` / `uv sync` there.
4. Check LangGraph + `llama-index-core` + `litellm` changelogs since the last `Last grounded` date.
5. Defaults: LiteLLM → Gemini for chat; HuggingFace `all-MiniLM-L6-v2` for embeddings. Ollama optional.
6. Pedagogy lock: see `AGENTS.md`.
7. Windows: no WSL assumed. `asyncio` HTTP is fine. Subprocess tools: one-line Proactor note.
8. Do not promote a deferred topic (MCP, LangSmith, evals, …) into a new phase without an explicit request.
9. Do not install `litellm[proxy]`.
10. After the batch: set `Last grounded: YYYY-MM-DD` on every file you wrote, and update `docs/STATUS.md`.
11. Style pass before done: every guide follows the writing style in `AGENTS.md` — content-bearing headers, no banned words, expected output after every code block, growing-file keep/replace, field map (not `print(resp)`), What just moved, one new name per segment, process print on the first tool, plain-English tool descriptions, The big picture stage definitions (one sentence per stage this guide builds; Skeleton stays a recipe).
12. Never write or commit session dumps / chat exports (`session-ses_*.md`, transcripts). Delete them if they appear — do not add them to `.gitignore` to hide them.
13. When this session locks a new convention, write it into `AGENTS.md` (and this file if it is a write-time rule) **in the same pass**. A new session must not need prior chat.
14. Checkpoints only quiz what that guide taught. Explain tool docstrings (the model reads them) before the tool snippet. No `#` comments in learner snippets to teach.
15. Before marking a phase guide done, run `python scripts/check_guides.py` from the repo root (stdlib only). It asserts Skeleton-after-Why, The big picture (except concept-only Phase 1), one mermaid, Checkpoint, Try-this placement, banned words, and no `#` comments inside python fences.

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

## Batch 4 — Phases 8–9 + advanced-topics appendix

- https://huggingface.co/docs/smolagents/en/index
- https://huggingface.co/docs/smolagents/en/guided_tour
- https://platform.openai.com/docs/guides/function-calling
- https://docs.langchain.com/oss/python/langchain/structured-output
- Advanced-topics appendix only (fetch these only if writing it): LlamaIndex MCP, LangGraph MCP, LangSmith observability, Ollama OpenAI compat

## Known API drift (as of 2026-09-01)

| Item | Current | Stale |
|---|---|---|
| One-tool LlamaIndex agent | `FunctionAgent` | `AgentWorkflow` for a single tool |
| LangGraph prebuilt ReAct | `from langchain.agents import create_agent` | `from langgraph.prebuilt import create_react_agent` |
| In-memory checkpointer | `InMemorySaver` | older `MemorySaver` name in some posts |
| OpenAI official loop | Responses API | This course uses Chat Completions via LiteLLM until Phase 9 |
| Chat default | LiteLLM `gemini/gemini-3.5-flash-lite` | Ollama as required |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Ollama `nomic-embed-text` |
| Install | `uv sync` / `uv add` per `agents/*` uv project | bare pip; freeze-into-requirements; root uv workspace / shared lock |
| LiteLLM | Python SDK only (`litellm`) | `litellm[proxy]` |
| LlamaIndex defaults | `Settings.llm` / `Settings.embed_model` must be set | relying on defaults |
| HITL | `interrupt()` + `Command(resume=...)` | `input()` inside a node |
| ToolNode routing | `from langgraph.prebuilt import ToolNode, tools_condition`; the node **must** be named `"tools"` | other node names; `create_react_agent` |
| LangGraph messages (current pin: `langchain` 0.3.x) | `from langchain_core.messages import AIMessage, convert_to_openai_messages` | `from langchain.messages import ...` (langchain v1 / Phase 9) |
| Sqlite checkpointer | extra `langgraph-checkpoint-sqlite`; `sqlite3.connect(..., check_same_thread=False)` then `SqliteSaver(conn)` | `SqliteSaver.from_conn_string` as a long-lived graph — it is a context manager and closes the connection |
