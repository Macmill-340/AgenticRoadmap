# Status

Last grounded: 2026-08-23

Read order for a new session: `AGENTS.md` → this file → `docs/MAINTENANCE.md` → first unchecked box below.
Before writing any batch: re-fetch that batch's URLs from `docs/MAINTENANCE.md`. Do not skip the fetch list.

## Phase → folder map

| Folder | Phases | Learner files (learner writes) |
|---|---|---|
| `agents/foundation/` | 0–3 | `00_orientation.py`, `02_tool_loop.py`, `03_state.py` |
| `agents/llamaindex/` | 4–6 | `04_rag_fast.py`, `05_rag_decomposed.py`, `06_rag_as_tool.py` |
| `agents/langgraph/` | 7, 7b, 9 | `07_graph.py`, `07b_multi_agent.py`, `09_conventions.py` |
| `agents/smolagents/` | 8 optional | folder created only when Phase 8 is written |

Skeleton folders exist with unpinned `requirements.txt`. Learner writes the `.py` files from the phase docs. Venv per folder: `uv venv` when you reach that group.

## Done (Batch 1 — docs only)

- [x] `AGENTS.md`
- [x] `docs/MAINTENANCE.md`
- [x] `docs/STATUS.md` (this file)
- [x] `docs/00-setup.md`
- [x] `docs/01-phase-0-orientation.md`
- [x] `docs/02-phase-1-decoding.md`
- [x] `docs/03-phase-2-tool-loop.md`
- [x] `agents/foundation/requirements.txt`

Retuned: `uv pip` + `requirements.txt`; LiteLLM → Gemini; MiniLM for later RAG; Ollama optional.

No learner Python files yet. That is intentional.

## Next (Batch 2 — Phases 3–6)

Write in order after fetching the Batch 2 URL list in `docs/MAINTENANCE.md`:

- [x] **`docs/04-phase-3-state-memory.md`** — raw. State = plain dict / TypedDict rendered into the system prompt each turn; not a Memory object. History + facts + tool results. One deepening: cap vs summarize (show the behavior change), plus token budget as a hard constraint. Maps back to Phase 2 loop; foreshadows LangGraph `MessagesState`. File: `agents/foundation/03_state.py`
- [ ] **`docs/05-phase-4-rag-fast.md`** — abstraction. Set `Settings.llm` + `Settings.embed_model` **first**, every script. `SimpleDirectoryReader` → `VectorStoreIndex` → persistent Chroma (`PersistentClient`) → `as_query_engine()`. Chat via LiteLLM Gemini; embeddings via `HuggingFaceEmbedding("all-MiniLM-L6-v2")`. One deepening: rerank (industry default after naive top-k). Not BM25 / graph RAG / LlamaParse / Ollama nomic. File: `agents/llamaindex/04_rag_fast.py`
- [ ] **`docs/06-phase-5-rag-decomposed.md`** — decompose, no LlamaIndex. Hand-roll load → fixed-size chunk → overlap demo (query fails, then succeeds) → MiniLM embed → Chroma client → cosine/top-k → stuff prompt → generate. One deepening: overlap failure + timed `asyncio.gather` vs sequential. Extra: retrieved junk can still produce a fluent wrong answer (groundedness). File: `agents/llamaindex/05_rag_decomposed.py`
- [ ] **`docs/07-phase-6-rag-as-tool.md`** — glue. Phase 4 query engine wrapped as a plain function/tool schema inside the Phase 2 loop; agent chooses retrieve vs answer directly. Almost no new code — keep it short. File: `agents/llamaindex/06_rag_as_tool.py`
- [x] **`agents/llamaindex/requirements.txt`** — `litellm`, `llama-index-core`, `llama-index-llms-litellm`, `llama-index-embeddings-huggingface`, `llama-index-vector-stores-chroma`, `chromadb`, `python-dotenv`; rerank package pinned at write time. Exact pins at write time; freeze if a pin fails.
- [ ] **`data/` sample docs** — a few small local `.txt` files before Phase 4 runs.

Then update this file and stop.

## Later

### Batch 3 — Phases 7 + 7b

Fetch the Batch 3 URL list first.

- [ ] **`docs/08-phase-7-langgraph.md`** — abstraction → short decompose. Segments: `StateGraph` + `MessagesState` + reducers (`add_messages` vs overwrite); agent node + `ToolNode` + `tools_condition`; LlamaIndex retriever wrapped as `@tool` (the hybrid production pattern); `SqliteSaver` + `thread_id` — kill process, resume, contrast `InMemorySaver`; `interrupt()` + `Command(resume=...)` — never `input()`, node restarts from top on resume, side effects must be idempotent, no bare `try/except` around `interrupt`; short hand-rolled dispatcher mapping back to Phases 2–3. Streaming = sidebar only. Never `create_react_agent` (deprecated). One mermaid: START → agent → tools? → ToolNode → agent → END. File: `agents/langgraph/07_graph.py`
- [ ] **`docs/09-phase-7b-multi-agent.md`** — abstraction. Supervisor first: two specialists (`research` = RAG tool from 6/7, `writer` = no tools, markdown out) invoked as `@tool`s by a supervisor; one task needing both. One deepening: handoff as contrast (`Command.goto`; LlamaIndex `AgentWorkflow(can_handoff_to=...)` is a pointer, not a build). Not router / Skills / A2A / Deep Agents. One mermaid: user → supervisor → specialists → supervisor → user. File: `agents/langgraph/07b_multi_agent.py`
- [ ] **`agents/langgraph/requirements.txt`** — skeleton exists (`litellm`, `python-dotenv`, `langgraph`, `langchain`). Extend + pin at write time (LangGraph modular packages: graph engine vs checkpoint extras are separate).

### Batch 4 — Phases 8–9 + parking lot

Fetch the Batch 4 URL list first.

- [ ] **`docs/10-phase-8-smolagents.md`** — optional, half day. `CodeAgent` vs `ToolCallingAgent` on the same task; code-as-action is a different bet, not a framework to master. Sandbox note only. File: `agents/smolagents/08_code_vs_tools.py`
- [ ] **`docs/11-phase-9-modern-conventions.md`** — delta, not rewrite. OpenAI Responses API loop beside the Chat Completions loop they already built; `from langchain.agents import create_agent` as harness on the graph they understand; structured output (`response_format`) vs tools — when to use which; stale-import map ("if you see `create_react_agent` / `AgentWorkflow` for one tool / Chat Completions-only tutorials, here's what replaced them"). File: `agents/langgraph/09_conventions.py`
- [ ] **`docs/appendix-parking-lot.md`** — pointers only, one-liners + official URLs: MCP, LangSmith, evals/guardrails, A2A, Deep Agents, LlamaIndex Workflows. Do not expand without an explicit request.
- [ ] **`agents/smolagents/requirements.txt`** — only if Phase 8 is written (folder is deferred until then).

## Open notes

- Chat Completions via `litellm.completion` for Phases 2–7. Responses API is Phase 9.
- Phase 0 uses `FunctionAgent` + `LiteLLM`, not `AgentWorkflow`, not Ollama.
- If a `requirements.txt` pin fails, freeze after a successful install and write exact versions back.
- Every phase doc gets exactly one mermaid (mental map, not decoration), per the locked template.
- MiniLM `all-MiniLM-L6-v2` truncates at ~256 tokens — this replaces the old Ollama `num_ctx` truncation demo in Phases 4–5.
