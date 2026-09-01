# Setup

Suggested file: `agents/foundation/pyproject.toml` (already exists; see section 3)  
GitHub-facing overview lives in the root `README.md`; this file is the hands-on install guide.

## What this sets up

uv installed, a free Gemini key in `.env`, and one isolated environment per phase group — so a broken dependency in one layer of the course can never take down another.

## Why separate environments

LlamaIndex (phases 4–6) and LangGraph (phase 7+) pin different, sometimes conflicting packages. One shared environment turns every crash into a dependency hunt instead of a lesson.

Chat goes through **LiteLLM → Gemini** (reliable tool-calling, no multi-GB local model). Embeddings later use HuggingFace MiniLM (~90 MB). Ollama is optional.

## How to read a phase doc

Each phase file is a self-contained guide. Implement **one segment** in the same `.py` the guide named: keep what it says to keep, add or replace the rest, run, match expected output, then the next segment. Print the field path the guide names (`resp.choices[0].message.content`), not the whole object.

---

## Editor (mermaid)

Each phase guide has one mermaid diagram. Pick an editor that can preview it — or skip this and read the diagram on GitHub / [mermaid.live](https://mermaid.live).

| Editor | Mermaid |
|---|---|
| PyCharm / IntelliJ | plugin [Mermaid](https://plugins.jetbrains.com/plugin/20146-mermaid) |
| VS Code / Cursor | plugin [Markdown Preview Mermaid Support](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) |
| Neither | open the guide on GitHub, or paste the fence into [mermaid.live](https://mermaid.live) |

No editor is required. The course is a terminal plus whatever you already use.

## What you need

- **Python 3.13+** — `uv sync` downloads it if missing. You do not install Python by hand.
- **Git** — you already have this repo.
- **A Google account** — free Gemini key in the next section.
- **Disk later** — Phase 4 downloads MiniLM plus a large CPU torch stack (hundreds of MB, one time).

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

1. https://aistudio.google.com → Get API key (Bottom Left Key Icon) → Create API Key (Top Right Button).
2. From the **repo root**, copy the example (PowerShell and macOS/Linux):

```
cp .env.example .env
```

3. Open `.env` and set `GEMINI_API_KEY` to your key. Leave `GEMINI_MODEL` and `LITELLM_LOG=ERROR` as is (`LITELLM_LOG` quiets LiteLLM's Gemini 3 sampling notice; real errors still raise).

One `.env` at the repo root only (gitignored). `load_dotenv()` walks up from `agents/*`. Call it **before** importing LiteLLM — LiteLLM reads `LITELLM_LOG` at import time. Never commit `.env`.

Pass `api_key=os.getenv("GEMINI_API_KEY")` into every `completion` / `LiteLLM` call. Model string is `gemini/<name>`. Swap later: `openai/gpt-4o-mini` or `ollama/qwen3`.

Do **not** install `litellm[proxy]`. That is a gateway server. This path uses the Python SDK only.

## 3. Isolated projects

Each `agents/*` folder is its own uv project: `pyproject.toml` lists direct dependencies, the committed `uv.lock` pins every resolved version, and `.venv/` is created on demand. Set up a folder only when you reach its phase-group.

**Windows (PowerShell):**

```powershell
# Phases 0–3 (do this before Phase 0)
if (Test-Path agents\foundation) { cd agents\foundation }
uv sync                # resolves, writes/uses uv.lock, creates .venv, installs exactly that
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
[ -d agents/foundation ] && cd agents/foundation
uv sync
source .venv/bin/activate
```

You should see `(.venv)` at the start of the prompt. `uv` also supports `uv run` without activating — both work; activation just lets the IDE see the same interpreter.

New terminals (VS Code, Cursor) usually open at the repo root; PyCharm sometimes restores already inside the folder. That `if` / `[ -d ... ] &&` does the right thing either way.

Later, same pattern in `agents\llamaindex`, then `agents\langgraph` (`agents\smolagents` is created via `uv init` when Phase 8 is written).

`agents/foundation/pyproject.toml` lists **two** LiteLLM-related packages on purpose: `llama-index-llms-litellm` is the wrapper Phase 0 imports as `LiteLLM(...)`; `litellm` is the SDK you will `import` yourself in Phase 2. Same provider, two import paths.

Adding a package mid-course:

```powershell
uv add <package>    # updates pyproject.toml + uv.lock + .venv together
```

Experiment freely with `uv pip install whatever-you-are-testing` — the next `uv sync` removes anything the lock does not know. No wipe-to-refreeze, ever. Commit `uv.lock` changes together with your code/doc changes.

Run (either way works; `activate` is optional for `uv run`):

```powershell
uv run python path\to\file.py
```

Never bare `pip install`.

### PyCharm project view

Keep **Settings → Project Structure → Use pyproject.toml-based project model** checked. PyCharm then shows the root module (docs, `data/`, README) plus one module per `agents/*` project.

If the tree ever looks wrong — only subfolders visible, or an empty view: Project Structure → uncheck that box → select the module → **+ Add Content Root** → the repo root → OK → re-check the box. Attach `agents\<group>\.venv\Scripts\python.exe` as a Python SDK when you want per-folder interpreters.

### Coming from pip?

Three ideas cover everything this course does with uv:

- A **virtual environment** (`.venv/`) is a private sandbox for one project's packages — same idea as `python -m venv`, just faster.
- `pyproject.toml` says what you *want* (direct dependencies, loose names). `uv.lock` records what you *got* (every package resolved to an exact version, committed to git).
- `uv sync` makes reality match the lock: installs what's missing, removes what's extra. `uv add <pkg>` updates the want-file and the lock in one step.

That's the whole vocabulary. You'll never ask "should I freeze?" — the lock *is* the freeze.

### Python you should be comfortable with

The course assumes everyday Python: functions, dicts, lists, f-strings, `if __name__ == "__main__"`. Five things get a short refresher exactly where they first appear:

| Topic | First used | The 10-second version |
|---|---|---|
| Type hints + `TypedDict` | Phase 3 | a dict at runtime; named keys for the type checker |
| `pydantic.BaseModel` | Phase 2 | typed fields; a bad payload becomes an error string, not a crash |
| `pathlib.Path` | Phase 4 | paths from this file, not from the shell's cwd |
| `async` / `await` | Phase 0 | one wait for `FunctionAgent.run`; gather / overlap is Phase 5 |
| Decorators (`@name`) | Phase 7 | `@mark` means `greet = mark(greet)`; then `@tool` |

Nothing deeper is assumed.

## 4. Smoke-test LiteLLM + Gemini

```python
import os
from dotenv import load_dotenv

load_dotenv()

from litellm import completion

resp = completion(
    model=os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash-lite"),
    api_key=os.getenv("GEMINI_API_KEY"),
    messages=[{"role": "user", "content": "Say hi in five words."}],
)
print(resp.choices[0].message.content)
```

**Expected:** a short greeting. Auth errors → check `.env` and that you ran from a directory that can see it (`load_dotenv()` walks up; or set the env var in the shell).

## 5. Layout after setup

```
AgenticRoadmap/
  README.md
  AGENTS.md            # for people extending the course, not for following it
  docs/
  .env.example         # copy to .env; never commit .env
  .env                 # your key (gitignored)
  data/                # sample docs for the RAG phases already included
  agents/foundation/   # uv project (pyproject + lock + venv), phases 0–3
  agents/llamaindex/   # skeleton, phases 4–6 (venv when you get there)
  agents/langgraph/    # skeleton, phases 7, 7b, 9
```

## Optional: Ollama

Not required. To try later, pull a model and set `GEMINI_MODEL` aside:

```python
completion(
    model="ollama/qwen3",
    messages=...,
    api_base="http://localhost:11434",
)
```

## Common failures

| Symptom | Cause |
|---|---|
| `uv` not found | Old terminal; reopen |
| Gemini 401 / API key | `.env` missing (`cp .env.example .env` from the repo root), empty key, or `load_dotenv()` not called |
| LlamaIndex asks for `OPENAI_API_KEY` | `Settings.llm` / `Settings.embed_model` not set |
| `litellm[proxy]` pulled in | Wrong extra — uninstall; use bare `litellm` |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy. Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again — or just use `uv run python path\to\file.py` and skip activation. |

## Checkpoint

1. Why a separate venv for LangGraph vs LlamaIndex?
2. What do you change to swap Gemini for OpenAI?
3. Why does `foundation` pin both `litellm` and `llama-index-llms-litellm`?

Answers: (1) conflicting pins; (2) the LiteLLM model string (and the other provider’s key); (3) the wrapper is `LiteLLM(...)` in Phase 0; `import litellm` is the raw SDK you use from Phase 2.
