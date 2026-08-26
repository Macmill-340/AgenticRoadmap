# AgenticRoadmap

Phase-by-phase path to becoming an agentic AI engineer. **Docs first — you write the Python.**

Each phase is a self-contained guide in [`docs/`](docs/): what, why, how, exact install commands, snippets, expected output, and the filename you create. No framework hopping, no black boxes: every framework abstraction later in the path maps back to a loop you built by hand early.

## The path

Guides marked *pending* are written batch by batch, each grounded against current official docs first (see [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md)).

| # | Topic | Mode | You write | Guide |
|---|---|---|---|---|
| — | Setup (uv, Gemini key, isolated uv projects) | — | `pyproject.toml` per folder (provided) | [`docs/00-setup.md`](docs/00-setup.md) — done |
| 0 | Orientation: your first agent | guided demo | `00_orientation.py` | [`docs/01-phase-0-orientation.md`](docs/01-phase-0-orientation.md) — done |
| 1 | How decoding actually works | concept only | — (HF Spaces demos) | [`docs/02-phase-1-decoding.md`](docs/02-phase-1-decoding.md) — done |
| 2 | The raw tool-calling loop | raw, by hand | `02_tool_loop.py` | [`docs/03-phase-2-tool-loop.md`](docs/03-phase-2-tool-loop.md) — done |
| 3 | State & memory by hand | raw, by hand | `03_state.py` | [`docs/04-phase-3-state-memory.md`](docs/04-phase-3-state-memory.md) — done |
| 4 | RAG fast (LlamaIndex + Chroma) | abstraction-first | `04_rag_fast.py` | [`docs/05-phase-4-rag-fast.md`](docs/05-phase-4-rag-fast.md) — done |
| 5 | RAG decomposed | open the hood | `05_rag_decomposed.py` | [`docs/06-phase-5-rag-decomposed.md`](docs/06-phase-5-rag-decomposed.md) — done |
| 6 | RAG as a tool | glue | `06_rag_as_tool.py` | [`docs/07-phase-6-rag-as-tool.md`](docs/07-phase-6-rag-as-tool.md) — done |
| 7 | LangGraph single-agent graph | abstraction, then peek | `07_graph.py` | *pending* |
| 7b | Multi-agent (supervisor, then handoff contrast) | abstraction | `07b_multi_agent.py` | *pending* |
| 8 | smolagents: code-as-action | optional side quest | `08_code_vs_tools.py` | *pending* |
| 9 | Modern conventions (Responses API, `create_agent`) | delta | `09_conventions.py` | *pending* |

## Spine

Recite this after any break: one sentence per layer, then the recipe.

- **Agent** — model + tools + a loop. Pick a model, write tools, hand both over, ask, print.
- **Decoding** — the model only picks the next token. Score, pick, append, repeat, stop.
- **The loop** — messages + schemas → call → run → append → repeat (`max_steps` raises).
- **Memory** — a dict you render into the prompt. History for continuity, facts for durability.
- **RAG** — load → embed → store → retrieve → generate (+ optional rerank).
- **RAG internals** — Phase 4's one-liners are just load / chunk / embed / query functions.
- **RAG as a tool** — the engine becomes one more tool inside your Phase 2 loop.

Later phases (LangGraph, multi-agent, conventions) append their line here as each guide is written.

## How to follow

1. Do [`docs/00-setup.md`](docs/00-setup.md) end to end (~10 min): install uv, set a free Gemini key in `.env`.
2. Open the next guide, run its `uv` block (creates the file only if missing — safe to re-run), and work **one segment at a time**: implement → run → match the expected output → next segment.
3. Every guide ends with checkpoint questions (answers included) — if you cannot answer them, rerun the segment.
4. Milestone guides (2, 3, 6, 7/7b) end with an optional **Try this**: one small build of your own using what you just wrote. Skip it or invent something else — both are fine.

## Stack defaults

| Role | Choice | Why |
|---|---|---|
| Install | [uv](https://docs.astral.sh/uv/) — `uv sync` inside each project folder | fast; exact versions pinned in each committed `uv.lock` |
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

Each folder is its own uv project: `pyproject.toml` lists direct deps, the committed `uv.lock` pins every resolved version. Run the guide's `uv` block — `if (Test-Path agents/<group>) { cd agents/<group> }` + `uv sync` + `activate` + `if (-not (Test-Path <phase_file>.py)) { New-Item ... }` (Windows) or `[ -d agents/<group> ] && cd ...` + `source .venv/bin/activate` + `touch` (macOS/Linux) — the last line is idempotent, safe to re-run. Extend later with `uv add`. Experiments installed ad hoc are cleaned by the next `uv sync`.

## Repo layout

```
docs/      teaching guides + STATUS.md (tracks where you are) + MAINTENANCE.md (research rules)
agents/    uv skeletons — the .py files are yours to write
data/      small local documents for the RAG phases
AGENTS.md  starting point for AI coding sessions that extend the course
README.md  this file — learner entry point
```

This repo is built to grow through AI-assisted sessions: any new session starts from `AGENTS.md` → `docs/STATUS.md` → `docs/MAINTENANCE.md` and continues the next unchecked item, re-fetching official docs before writing.

## What this course leaves out

Some things are worth knowing about but don't belong in the core path: MCP, LangSmith/observability, evals/guardrails, A2A, Deep Agents, and LlamaIndex Workflows. They'll get a short pointers-only appendix at the end — a place to start when you're curious, not extra phases to build. Also skipped on purpose: LangChain-as-orchestration, Pydantic AI as a framework, and neural-network internals.
