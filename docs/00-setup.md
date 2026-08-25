# Setup

Last grounded: 2026-08-21  
Prereq files: `AGENTS.md`  
Fetch before writing later phases: uv + LiteLLM + Gemini URLs in `docs/MAINTENANCE.md`  
Suggested file: `agents/foundation/pyproject.toml` (already exists; see section 3)  
GitHub-facing overview lives in the root `README.md`; this file is the hands-on install guide.

## What

Install uv, a Gemini API key, and isolated venvs so later phases do not share dependency trees.

## Why

LlamaIndex (Phases 4–6) and LangGraph (Phase 7+) pin different, sometimes conflicting packages. One global venv turns the lesson into an environment-debug session.

Chat goes through **LiteLLM → Gemini** (reliable tool-calling, no multi-GB local model). Embeddings later use HuggingFace MiniLM (~90 MB). Ollama is optional.

## How to read a phase doc

Each phase file is a self-contained guide. Implement **one segment**, run it, match expected output, then the next segment.

A new coding session: read `AGENTS.md` → `docs/STATUS.md` → `docs/MAINTENANCE.md` → the next phase doc.

---

## 1. Install uv (Windows)

Official: https://docs.astral.sh/uv/getting-started/installation/

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alt: `winget install --id=astral-sh.uv -e`

Open a **new** terminal:

```powershell
uv --version
```

## 2. Gemini API key

1. https://aistudio.google.com → Get API key.
2. Put it in `.env` at the repo root (gitignored).

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini/gemini-2.5-flash
```

LiteLLM reads `GEMINI_API_KEY`. Model string is `gemini/<name>`. Swap later: `openai/gpt-4o-mini` or `ollama/qwen3`.

Do **not** install `litellm[proxy]`. That is a gateway server. This path uses the Python SDK only.

## 3. Isolated projects

Each `agents/*` folder is its own uv project: `pyproject.toml` lists direct dependencies, the committed `uv.lock` pins every resolved version, and `.venv/` is created on demand. Set up a folder only when you reach its phase-group.

```powershell
# Phases 0–3 (do this before Phase 0)
cd agents\foundation
uv sync          # resolves, writes/uses uv.lock, creates .venv, installs exactly that
```

Later, same pattern in `agents\llamaindex`, then `agents\langgraph` (`agents\smolagents` is created via `uv init` when Phase 8 is written).

Adding a package mid-course:

```powershell
uv add <package>    # updates pyproject.toml + uv.lock + .venv together
```

Experiment freely with `uv pip install whatever-you-are-testing` — the next `uv sync` removes anything the lock does not know. No wipe-to-refreeze, ever. Commit `uv.lock` changes together with your code/doc changes.

Run without activating:

```powershell
uv run python path\to\file.py
```

Or activate if you prefer: `agents\foundation\.venv\Scripts\activate`.

Never bare `pip install`.

### PyCharm project view

Keep **Settings → Project Structure → Use pyproject.toml-based project model** checked. PyCharm then shows the root module (docs, `data/`, README) plus one module per `agents/*` project.

If the tree ever looks wrong — only subfolders visible, or an empty view: Project Structure → uncheck that box → select the module → **+ Add Content Root** → the repo root → OK → re-check the box. Attach `agents\<group>\.venv\Scripts\python.exe` as a Python SDK when you want per-folder interpreters.

## 4. Smoke-test LiteLLM + Gemini

```python
import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

resp = completion(
    model=os.environ.get("GEMINI_MODEL", "gemini/gemini-2.5-flash"),
    messages=[{"role": "user", "content": "Say hi in five words."}],
)
print(resp.choices[0].message.content)
```

**Expected:** a short greeting. Auth errors → check `.env` and that you ran from a directory that can see it (`load_dotenv()` walks up; or set the env var in the shell).

## 5. Layout after setup

```
AgenticRoadmap/
  README.md
  AGENTS.md
  docs/
  .env
  data/                # sample docs for the RAG phases already included
  agents/foundation/   # uv project (pyproject + lock + venv), phases 0–3
  agents/llamaindex/   # skeleton, phases 4–6 (venv when you get there)
  agents/langgraph/    # skeleton, phases 7, 7b, 9
```

## Optional: Ollama

Not required. To try later, pull a model and set `GEMINI_MODEL` aside:

```python
completion(model="ollama/qwen3", messages=..., api_base="http://localhost:11434")
```

## Common failures

| Symptom | Cause |
|---|---|
| `uv` not found | Old terminal; reopen |
| Gemini 401 / API key | `.env` missing or `load_dotenv()` not called |
| LlamaIndex asks for `OPENAI_API_KEY` | `Settings.llm` / `Settings.embed_model` not set |
| `litellm[proxy]` pulled in | Wrong extra — uninstall; use bare `litellm` |

## Checkpoint

1. Why a separate venv for LangGraph vs LlamaIndex?
2. What do you change to swap Gemini for OpenAI?
3. Why pin both `litellm` and `llama-index-llms-litellm`?

Answers: (1) conflicting pins; (2) the LiteLLM model string (and the other provider’s key); (3) Phase 2 imports `litellm` directly; the wrapper is only for `FunctionAgent`.
