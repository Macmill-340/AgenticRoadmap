# AgenticRoadmap

Phase-by-phase path to becoming an agentic AI engineer. **Docs first — you write the Python.**

Each phase is a closed packet in [`docs/`](docs/): what, why, how, exact install commands, snippets, expected output, and the filename you create. No framework hopping, no black boxes: every framework abstraction later in the path maps back to a loop you built by hand early.

## The path

Packets marked *pending* are written batch by batch, each grounded against current official docs first (see [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)).

| # | Topic | Mode | You write | Packet |
|---|---|---|---|---|
| — | Setup (uv, Gemini key, isolated venvs) | — | `requirements.txt` per folder | [`docs/00-setup.md`](docs/00-setup.md) — done |
| 0 | Orientation: your first agent | guided demo | `00_orientation.py` | [`docs/01-phase-0-orientation.md`](docs/01-phase-0-orientation.md) — done |
| 1 | How decoding actually works | concept only | — (HF Spaces demos) | [`docs/02-phase-1-decoding.md`](docs/02-phase-1-decoding.md) — done |
| 2 | The raw tool-calling loop | raw, by hand | `02_tool_loop.py` | [`docs/03-phase-2-tool-loop.md`](docs/03-phase-2-tool-loop.md) — done |
| 3 | State & memory by hand | raw, by hand | `03_state.py` | [`docs/04-phase-3-state-memory.md`](docs/04-phase-3-state-memory.md) — done |
| 4 | RAG fast (LlamaIndex + Chroma) | abstraction-first | `04_rag_fast.py` | *pending* |
| 5 | RAG decomposed | open the hood | `05_rag_decomposed.py` | *pending* |
| 6 | RAG as a tool | glue | `06_rag_as_tool.py` | *pending* |
| 7 | LangGraph single-agent graph | abstraction, then peek | `07_graph.py` | *pending* |
| 7b | Multi-agent (supervisor, then handoff contrast) | abstraction | `07b_multi_agent.py` | *pending* |
| 8 | smolagents: code-as-action | optional side quest | `08_code_vs_tools.py` | *pending* |
| 9 | Modern conventions (Responses API, `create_agent`) | delta | `09_conventions.py` | *pending* |

## How to follow

1. Do [`docs/00-setup.md`](docs/00-setup.md) end to end (~10 min): install uv, set a free Gemini key in `.env`.
2. Open the next packet, create its file in the right folder, and work **one segment at a time**: implement → run → match the expected output → next segment.
3. Every packet ends with checkpoint questions (answers included) — if you cannot answer them, rerun the segment.

## Stack defaults

| Role | Choice | Why |
|---|---|---|
| Install | [uv](https://docs.astral.sh/uv/) — `uv venv` + `uv pip install -r requirements.txt` | fast, pip-style habits, pins live in `requirements.txt` |
| Chat + tools | LiteLLM → Gemini (`gemini/gemini-2.5-flash`) | reliable tool-calling; hot-swap providers by editing one model string |
| Embeddings (phases 4–6) | HuggingFace `all-MiniLM-L6-v2` (~90 MB, CPU) | no Ollama required |
| Tool validation | `pydantic.BaseModel` | typed arguments; errors go back to the model as observations |
| Retrieval | LlamaIndex core | load → chunk → embed → store → query |
| Orchestration | LangGraph | explicit graph state, checkpointing, human-in-the-loop |

Ollama stays optional (one model-string change). Never used: `litellm[proxy]` (that is a gateway product).

## Isolation model

One uv project per layer so dependency trees never fight:

| Folder | Phases |
|---|---|
| `agents/foundation/` | 0–3 |
| `agents/llamaindex/` | 4–6 |
| `agents/langgraph/` | 7, 7b, 9 |
| `agents/smolagents/` | created only if Phase 8 is written |

Skeletons ship with unpinned `requirements.txt`; you run `uv venv` in a folder only when you reach its phase group.

## Repo layout

```
docs/      teaching packets + STATUS.md (progress cursor) + MAINTENANCE.md (research rules)
agents/    uv skeletons — the .py files are yours to write
data/      small local documents for the RAG phases
AGENTS.md  cold-start packet for AI coding sessions that extend this corpus
```

This corpus is built to grow through AI-assisted sessions: any new session starts from `AGENTS.md` → `docs/STATUS.md` → `docs/MAINTENANCE.md` and continues the next unchecked item, re-fetching official docs before writing.

## Deliberately not covered (parking lot)

MCP, LangSmith/observability, evals/guardrails, A2A, Deep Agents, LlamaIndex Workflows — pointer-only appendix when it lands. Also out of the core path: LangChain-as-orchestration, Pydantic AI as a framework, and neural-network internals.
