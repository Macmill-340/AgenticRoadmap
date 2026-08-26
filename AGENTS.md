# Agentic teaching repo

A phase-by-phase course for becoming an agentic AI engineer. **Docs first.** The learner writes the Python files from the phase docs.

This file is the starting point for any new AI session. A new session must not need prior chat history.

## Read order (every new session)

1. This file (`AGENTS.md`)
2. `docs/STATUS.md` — what is done, what to write next
3. `docs/MAINTENANCE.md` — fetch official docs before writing
4. The next phase doc listed in STATUS

Copy-paste prompt:

```
Read AGENTS.md, docs/STATUS.md, docs/MAINTENANCE.md.
Do the next item in STATUS.md.
Re-fetch that batch's official URLs before writing.
Do not skip the fetch list.
```

## What this is

A phase-by-phase teaching path. Each `docs/*.md` is a **self-contained guide** — what you'll build, why it matters, how to build it, `uv sync` / `uv add` lines, snippets, expected output, suggested filename. Someone should be able to implement from that file alone.

Original handoff (do not treat as current API truth): `agentic-frameworks-teaching-roadmap.md` (local only — not in the repo)

## Frameworks (only these)

| Layer | Tool | Role |
|---|---|---|
| Mechanism | Raw Python + `pydantic.BaseModel` + LiteLLM | Tool-call loop, state, validation, provider swap |
| Retrieval | LlamaIndex (core) | Load → chunk → embed → store → query |
| Orchestration | LangGraph | Graph, checkpointing, HITL |
| Optional | smolagents | Code-as-action (Phase 8 only) |

**Not in the core path:** LangChain-as-orchestration, Pydantic AI as a framework, MCP (deferred), LlamaIndex Workflows as a standalone phase, LiteLLM **proxy** (gateway product). LiteLLM is the **Python SDK** only — one `completion()` call.

**The hybrid that matters:** LlamaIndex retrieves; LangGraph orchestrates. Wrap a query engine as a plain function/`@tool` and call it from a graph node.

## Pedagogy (do not break)

**Simplest working form first. One deepening. Stop.**

- **Raw-first only for Phase 2** (the ~40-line tool loop). That loop is the lesson.
- **Abstraction-first** for RAG, LangGraph, multi-agent, orientation.
- **Concept-only** for decoding (Phase 1). Mermaid + HF Spaces. No neural nets.
- Every phase guide gets a `## Skeleton` after Why: one recitable sentence (e.g. "an agent = model + tools + a loop") + 4–6 numbered ingredient steps. README's `## Spine` collects one line per phase — append when the guide is written.
- Phase 7b (multi-agent) comes **after** a working single-agent graph, not earlier.
- MCP, LangSmith, evals, A2A, Deep Agents stay out of the course until you explicitly ask for them — and then as a short pointers-only appendix, not new phases.

## Writing style (every guide)

Write for one reader: a smart beginner building along in a terminal.

- Headers say what's inside: "What you'll build", "Why it matters", "The big picture", "Don't add yet", "Worth knowing", "Your finished file". Never bare "What" / "Why" / "Concept".
- Short sentences. Second person ("you"). Concrete verbs over abstractions.
- Banned words: packet, cold-start, parking lot, shim, load-bearing, leverage, robust, seamless, delve. "Guide" is the standing noun for a phase doc.
- Every code block is followed by what you should see when you run it.
- Python topics are taught just-in-time: a short box with example code, inside the guide that first needs the topic (async in Phase 5, decorators in Phase 7). setup.md carries the "Coming from pip?" and "Python you should be comfortable with" sections.
- Read the section aloud before marking it done. If it sounds like a changelog or a slide, rewrite it.

## Try this (milestones)

Optional creativity prompts at the end of milestone guides — **not** exercises. No levels, no answer key, no `exercises/` folder, no new packages.

- Milestone guides only: **2, 3, 6, 7/7b**. Never 0, 1, 4, 5, 8, 9.
- Pattern: one situation → build with tools they already know how to write → "Done when …" → close with "skip or invent your own".
- When **planning** a listed phase: draft the full prompt in the plan (detailed, not a stub). When **writing** the guide: include `## Try this` after Checkpoint.
- Foundation gets more room (Phase 2, then Phase 3). Framework side stays thin (Phase 6, then 7/7b).

## Tool-calling API

- **Phases 2–7:** OpenAI **Chat Completions** shape via `litellm.completion` (`tool_calls`, `role: "tool"`).
- **Default model:** `gemini/gemini-2.5-flash` + `GEMINI_API_KEY`. Swap later by changing the model string (`openai/gpt-4o-mini`, `ollama/qwen3`).
- **Phase 9:** OpenAI **Responses API** as a delta, not a rewrite.

## Models (ease, not local-first)

- Chat: Gemini through LiteLLM. No Ollama required.
- Embeddings (Phases 4–6): HuggingFace `all-MiniLM-L6-v2` (~90 MB, one download, CPU). Not Ollama.
- Ollama is optional (change the LiteLLM model string). Do not install `litellm[proxy]`.

## uv (always)

Windows install:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Each `agents/*` folder is a real uv project: `pyproject.toml` (direct deps) + committed `uv.lock` (exact pins) + `.venv/`.

**Windows (PowerShell):**

```powershell
if (Test-Path agents\foundation) { cd agents\foundation }   # or llamaindex / langgraph
uv sync                # first run: resolves, writes lock, creates .venv, installs
.venv\Scripts\activate
if (-not (Test-Path <phase_file>.py)) { New-Item -ItemType File <phase_file>.py }  # e.g. 00_orientation.py — creates only if missing
```

**macOS/Linux:**

```bash
[ -d agents/foundation ] && cd agents/foundation
uv sync
source .venv/bin/activate
touch <phase_file>.py   # creates only if missing
```

The last line is idempotent — safe to re-run on later sessions. New terminals (VS Code, Cursor) usually open at the repo root; PyCharm sometimes restores already inside the folder. That `if` / `[ -d ... ] &&` does the right thing either way.

```powershell
uv run python path\to\file.py  # works with or without activate; open the .py in your IDE
uv add <package>       # mid-course: updates pyproject + lock + venv together
```

Never bare `pip install`. The root `pyproject.toml` exists only so PyCharm shows the repo root — no dependencies, no `[tool.uv.workspace]`; never `uv add` / `uv sync` at the repo root. Real projects live in `agents/*`. Commit `uv.lock` changes alongside doc changes.

Isolated projects (skeletons exist; learner writes the `.py` files):

| Folder | Phases | Learner files |
|---|---|---|
| `agents/foundation/` | 0–3 | `00_orientation.py`, `02_tool_loop.py`, `03_state.py` |
| `agents/llamaindex/` | 4–6 | `04_rag_fast.py`, `05_rag_decomposed.py`, `06_rag_as_tool.py` |
| `agents/langgraph/` | 7, 7b, 9 | `07_graph.py`, `07b_multi_agent.py`, `09_conventions.py` |
| `agents/smolagents/` | 8 optional | folder created only when Phase 8 is written |

Each folder: `uv sync` when you reach its group, then `uv run python path\to\file.py` (activate first if you want the IDE to see the venv: `.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on macOS/Linux).

## Layout

```
docs/            teaching guides + MAINTENANCE + STATUS
agents/          uv project skeletons; learner writes the .py files
data/            small local docs for RAG
README.md        GitHub overview; learner entry point (links to 00-setup.md)
AGENTS.md        starting point for AI sessions extending the course
```

## Do not

- Promote a deferred topic (MCP, LangSmith, evals, …) into a new phase only on an explicit request.
- Use `from langgraph.prebuilt import create_react_agent` (deprecated). Production shortcut is `from langchain.agents import create_agent` — Phase 9 only.
- Use `AgentWorkflow` for the Phase 0 one-tool demo. Use `FunctionAgent`.
- Default LlamaIndex `Settings` to OpenAI. Set `Settings.llm` and `Settings.embed_model` every time.
- Wrap `interrupt()` in bare `try/except`. HITL is `interrupt()` + `Command(resume=...)`, not `input()`.
- Commit secrets. Use `.env`.
- Do not write the learner's `.py` files — every guide tells the learner which file to create. STATUS tracks docs; learners track code.
- Never write or commit session dumps / chat exports (`session-ses_*.md`, transcripts). Delete them if they appear — do not add them to `.gitignore` to hide them.

## Batches

1. Session files + setup + Phases 0–2
2. Phases 3–6
3. Phases 7 + 7b
4. Phases 8–9 + advanced-topics appendix

End of every batch: update `docs/STATUS.md`, then stop.
