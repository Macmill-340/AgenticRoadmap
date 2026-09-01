# Status

Last grounded: 2026-09-01

Read order for a new session: `AGENTS.md` → this file → `docs/MAINTENANCE.md` → first unchecked box below.
Before writing any batch: re-fetch that batch's URLs from `docs/MAINTENANCE.md`. Do not skip the fetch list.

## Phase → folder map

| Folder | Phases | Learner files (learner writes) |
|---|---|---|
| `agents/foundation/` | 0–3 | `00_orientation.py`, `02_tool_loop.py`, `03_state.py` |
| `agents/llamaindex/` | 4–6 | `04_rag_fast.py`, `05_rag_decomposed.py`, `06_rag_as_tool.py` |
| `agents/langgraph/` | 7, 7b, 9 | `07_graph.py`, `07b_multi_agent.py`, `09_conventions.py` |
| `agents/smolagents/` | 8 optional | folder created only when Phase 8 is written |

Skeleton folders exist as uv projects: `pyproject.toml` + committed `uv.lock` per folder (`course-foundation`, `course-llamaindex`, `course-langgraph`). Learner writes the `.py` files from the phase docs. Enter a folder and run the guide's `uv` block (`uv sync` installs the committed pins).

## Done (Batch 1 — docs only)

- [x] `AGENTS.md`
- [x] `docs/MAINTENANCE.md`
- [x] `docs/STATUS.md` (this file)
- [x] `docs/00-setup.md`
- [x] `docs/01-phase-0-orientation.md`
- [x] `docs/02-phase-1-decoding.md`
- [x] `docs/03-phase-2-tool-loop.md`
- [x] `agents/foundation/` uv project manifest (started as requirements.txt, migrated to `pyproject.toml`)
- [x] `README.md` + `.gitignore`

Retuned: uv projects (pyproject + lock) per agents/* folder; LiteLLM → Gemini; MiniLM for later RAG; Ollama optional.

No learner Python files yet. That is intentional.

## Done (Batch 2 — Phases 3–6)

- [x] **`docs/04-phase-3-state-memory.md`** — raw. State = plain dict / TypedDict rendered into the system prompt each turn; not a Memory object. History + facts + tool results. One deepening: cap vs summarize (show the behavior change), plus token budget as a hard constraint. Maps back to Phase 2 loop; foreshadows LangGraph `MessagesState`. File: `agents/foundation/03_state.py`
- [x] **`docs/05-phase-4-rag-fast.md`** — abstraction. Set `Settings.llm` + `Settings.embed_model` **first**, every script. `SimpleDirectoryReader` → `VectorStoreIndex` → persistent Chroma (`PersistentClient`) → `as_query_engine()`. Chat via LiteLLM Gemini; embeddings via `HuggingFaceEmbedding("all-MiniLM-L6-v2")`. One deepening: rerank (industry default after naive top-k). Not BM25 / graph RAG / LlamaParse / Ollama nomic. File: `agents/llamaindex/04_rag_fast.py`
- [x] **`docs/06-phase-5-rag-decomposed.md`** — decompose, no LlamaIndex. Hand-roll load → fixed-size chunk → overlap demo (query fails, then succeeds) → MiniLM embed (`sentence_transformers` directly) → raw Chroma client with own embeddings → cosine/top-k → stuff prompt → generate. One deepening: overlap failure + honest async timing (sequential vs batch vs `gather`+threads; batch wins on CPU). Extra: retrieved junk produces a fluent wrong answer (groundedness). New data: `overlap-demo.txt`. File: `agents/llamaindex/05_rag_decomposed.py`
- [x] **`docs/07-phase-6-rag-as-tool.md`** — glue. Phase 4 query engine wrapped as `search_notes(query)` + hand-written schema inside a copy of the Phase 2 loop beside `add`; model chooses retrieve / arithmetic / direct answer. Try this: three of your own files, known + unknown questions. File: `agents/llamaindex/06_rag_as_tool.py`
- [x] **`agents/llamaindex/pyproject.toml`** — `course-llamaindex`. `litellm`, `python-dotenv`, `llama-index-core`, `llama-index-llms-litellm`, `llama-index-embeddings-huggingface`, `llama-index-vector-stores-chroma`, `chromadb`, `sentence-transformers`. Reranker (`SentenceTransformerRerank`) ships in core — no extra package. Exact pins live in the committed `uv.lock`.
- [x] **`data/` sample docs** — `agent-loop.txt` (real answer source), `rag.txt` (real), `decoy-tools.txt` (keyword bait that rerank should demote), `overlap-demo.txt` (Nightjar memo for the chunk-overlap failure). Sized under MiniLM's ~256-token truncation.

## Done (Batch 3 — Phases 7 + 7b)

- [x] **`docs/08-phase-7-langgraph.md`** — abstraction → short decompose. Growing file: graph + `MessagesState` → agent node (`litellm.completion`) + `ToolNode` + `tools_condition` → LlamaIndex retriever as `@tool` → `SqliteSaver` + `thread_id` (kill, resume, contrast `InMemorySaver`) → `interrupt()` + `Command(resume=...)`. Hand-rolled dispatcher is read-only (`tools_condition` = Phase 2's `if tool_calls`). Streaming = sidebar. Never `create_react_agent`. File: `agents/langgraph/07_graph.py`
- [x] **`docs/09-phase-7b-multi-agent.md`** — abstraction. Supervisor graph; `research` + `writer` as `@tool`s; one task needing both. Handoff (`Command.goto`; LlamaIndex `AgentWorkflow(can_handoff_to=...)`) is contrast, not a build. File: `agents/langgraph/07b_multi_agent.py`
- [x] **`agents/langgraph/pyproject.toml`** — `course-langgraph` plus `langgraph-checkpoint-sqlite`, LlamaIndex wrap deps, `chromadb`. Exact pins in the committed `uv.lock`.

## Next (Batch 4 — Phases 8–9 + advanced-topics appendix)

Fetch the Batch 4 URL list from `docs/MAINTENANCE.md` before writing. Then:

- [ ] **`docs/10-phase-8-smolagents.md`** — optional, half day. `CodeAgent` vs `ToolCallingAgent` on the same task; code-as-action is a different bet, not a framework to master. Sandbox note only. File: `agents/smolagents/08_code_vs_tools.py`
- [ ] **`docs/11-phase-9-modern-conventions.md`** — delta + **translation map** (approved expansion; no second implementation anywhere). Part A: Responses API loop beside the Chat Completions loop they built; structured output vs tools; stale-import map ("if you see `create_react_agent` / one-tool `AgentWorkflow` / Chat-Completions-only tutorials, here's what replaced them"). Part B — each row gets what-it-is, when-you'd-switch, ≤5-line snippet: Phase 2 loop → LangGraph `create_agent` harness (LlamaIndex `FunctionAgent` = pointer back to Phase 0); Phase 3 dict → LlamaIndex ChatEngine/memory as *pointer* + LangGraph `MessagesState`/Store; Phases 4–6 engine-as-tool → already the hybrid pattern; `max_steps` → `recursion_limit`; LlamaIndex Workflows / subgraphs → pointers only. File: `agents/langgraph/09_conventions.py`
- [ ] **`docs/appendix-advanced-topics.md`** — short pointers + official URLs, nothing more: MCP, LangSmith, evals/guardrails, A2A, Deep Agents, LlamaIndex Workflows. Never grows into new phases without an explicit request.
- [ ] **`agents/smolagents/pyproject.toml`** — only if Phase 8 is written (folder via `uv init`, `[project] name` = `course-smolagents`, deferred until then).

Then update this file and stop.

## Later

### Optional fluency tours — write only when explicitly asked

Same rule as smolagents (Phase 8): no folder, no doc, no code until requested. Purpose: framework fluency on tasks already built raw — zero new concepts.

- **LlamaIndex-native agent tour** — `FunctionAgent` + LlamaIndex memory + the Phase 6 RAG tool, same task. Shows the native stack end to end.
- **LangGraph harness tour** — `create_agent` + checkpointer rebuilding the Phase 7 task on top of the Phase 9 map.

## Open notes

- Chat Completions via `litellm.completion` for Phases 2–7 (Phase 7 agent node included). Responses API is Phase 9.
- Phase 0 uses `FunctionAgent` + `LiteLLM`, not `AgentWorkflow`, not Ollama.
- uv projects per folder: `[project] name` is `course-<folder>` (never the PyPI package name). Direct deps in each `agents/*` `pyproject.toml`, exact pins in the committed `uv.lock`. `uv sync` heals a venv to those pins; `uv add` extends manifest + lock + venv together. The root `pyproject.toml` exists only so PyCharm shows the repo root (no dependencies) — never `uv add` / `uv sync` at the repo root.
- Every phase doc gets exactly one mermaid (mental map, not decoration), per the locked template. If it maps the snippet they just ran, it sits after Expected / What just moved.
- Checkpoints only quiz what that guide taught. Tool docstrings are explained before the snippet (the model reads them).
- Every phase guide gets `## Skeleton` after Why: one recitable sentence + 4–6 ingredient steps. Append that phase's line to README's `## Spine` in the same pass.
- Every build guide (not Phase 1) gets `## The big picture`: one sentence per stage this guide builds (what it is, why it exists). Only names that guide uses. Skeleton stays a recipe. No unused-term glossary. Phase 2's mermaid stays after the loop.
- `## Try this` rule (see AGENTS.md): optional milestone prompts only — Phases 2, 3, 6, 7/7b. One situation + "Done when …" + "skip or invent your own". Draft the prompt during planning; place the section after Checkpoint when writing. Locked prompts: P2 = keep `add`, add one invented tool, one user line needing both; P3 = preference told on turn 1 must survive capping by turn 4; P6 = agent answers from your own three files in `data/` or chats, retrieval never hard-coded; P7/7b = one real approval via `interrupt()` before a write tool, or two specialists on a task you actually care about.
- MiniLM `all-MiniLM-L6-v2` truncates at ~256 tokens — this replaces the old Ollama `num_ctx` truncation demo in Phases 4–5.
- Writing style is locked in `AGENTS.md`: content-bearing headers, banned-words list, growing-file keep/replace, field map not `print(resp)`, What just moved, one new name per segment, The big picture stage definitions, style pass before a guide counts as done (MAINTENANCE rule 11). Python topics are just-in-time boxes with example code — async `run`/`await` in Phase 0, pydantic in Phase 2, TypedDict in Phase 3, pathlib in Phase 4, gather / concurrency in Phase 5, decorator box in Phase 7; each box is before/after + table + why this guide; runnable boxes have prints and Expected (`read, do not paste` means not in the growing `.py`). setup.md carries "Coming from pip?" and the Python checklist. Learner-facing files must not contain session instructions (`Last grounded`, `Fetch before writing`, `Prereq files:`, "A new coding session").
- Learner `.py` files are gitignored. Before marking a guide done: `python scripts/check_guides.py` from the repo root.
