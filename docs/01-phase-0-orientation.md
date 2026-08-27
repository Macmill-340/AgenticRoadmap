# Phase 0 — Orientation

Last grounded: 2026-08-21  
Prereq files: `AGENTS.md`, `docs/00-setup.md`  
Fetch before writing:  
- https://docs.llamaindex.ai/en/stable/understanding/agent/  
- https://docs.llamaindex.ai/en/stable/integrations/llm/litellm/  
- https://docs.litellm.ai/docs/providers/gemini  
uv (from `agents/foundation`):

**Windows (PowerShell):**

```powershell
if (Test-Path agents\foundation) { cd agents\foundation }
uv sync
.venv\Scripts\activate
if (-not (Test-Path 00_orientation.py)) { New-Item -ItemType File 00_orientation.py }
```

**macOS/Linux:**

```bash
[ -d agents/foundation ] && cd agents/foundation
uv sync
source .venv/bin/activate
touch 00_orientation.py
```

Open `00_orientation.py` in your IDE — you will write the segments below there. The last line creates the file only if it does not already exist, so the same block is safe to re-run.

New terminals (VS Code, Cursor) usually open at the repo root; PyCharm sometimes restores already inside the folder. That `if` / `[ -d ... ] &&` does the right thing either way.

Suggested file: `agents/foundation/00_orientation.py`  
Mode: **abstraction**, ~20 lines, not graded.

## What you'll run

A LlamaIndex `FunctionAgent` with **one** tool, through LiteLLM → Gemini. The only thing to notice: the model *chose* to call your function.

## Why it matters

Everything later gets explained against something you've watched run, not a slide. Keep it to ~20 lines: no error handling, no RAG, no second tool.

**Not `AgentWorkflow`.** Official one-tool starter is `FunctionAgent`. `AgentWorkflow` is for multiple agents (Phase 7b).

Chat goes through **LiteLLM**, not the Google SDK. Swap providers later by changing the model string.

## Skeleton

An agent = **model + tools + a loop**.

1. Pick a model
2. Write one tool
3. Hand both to `FunctionAgent`
4. Ask a question
5. Print the answer

## Official docs

- Building an agent: https://docs.llamaindex.ai/en/stable/understanding/agent/
- LlamaIndex LiteLLM: https://docs.llamaindex.ai/en/stable/integrations/llm/litellm/
- LiteLLM Gemini: https://docs.litellm.ai/docs/providers/gemini

## The big picture

An agent is an LLM plus tools plus a loop: the model either answers or emits a structured call; your code runs the function; the result goes back; repeat until it answers. Here the framework owns the loop. Phase 2 will make you own it.

---

## Segment — one tool, live

`.env` must contain `GEMINI_API_KEY`.

### Async in 20 seconds

`FunctionAgent.run` waits on the network, so it is `async`. Three words:

```python
async def main() -> None:            # this function can pause
    response = await agent.run(...)  # pause here until Gemini answers
asyncio.run(main())                  # start the event loop (scripts only)
```

That's all you need here. Phase 5 covers running several waits at once.

A **tool** is a normal Python function you hand to the agent. The model never sees your source code. It sees three things: the function **name**, the **argument types**, and the **docstring** — the `"""..."""` line under `def`. That text is how Gemini decides *when* to call it. Write it like a label on a toolbox, not a note to yourself.

```python
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.litellm import LiteLLM


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    print(f"your process ran multiply({a}, {b})")
    return a * b


agent = FunctionAgent(
    tools=[multiply],
    llm=LiteLLM(
        model=os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash-lite"),
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    system_prompt="You are an assistant that uses tools for arithmetic.",
)


async def main() -> None:
    response = await agent.run(user_msg="What is 1234 * 4567?")
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())
```

```powershell
uv run python 00_orientation.py
```

**Expected:** first a line like `your process ran multiply(1234.0, 4567.0)` — then a sentence containing `5635678` (or the product). You should not see `LiteLLM:WARNING` lines (`LITELLM_LOG=ERROR` in `.env`, and `load_dotenv()` before importing LiteLLM). If you only get the sentence, the model did the math itself; tighten the prompt.

**What just moved:**

1. Question + tool schema (name, docstring, types) went to the model.
2. Model selected `multiply` and filled `a` / `b`.
3. Your function ran.
4. Result went back; model wrote the final sentence.

```mermaid
flowchart LR
  U[User question] --> A[FunctionAgent]
  A --> L[LiteLLM]
  L --> G[Gemini]
  G -->|chooses tool| T[multiply]
  T -->|number| G
  G -->|text| U
```

**Common failures**

| Symptom | Fix |
|---|---|
| `OPENAI_API_KEY` / auth error | You imported a default OpenAI LLM. This script must use `LiteLLM(...)`. |
| Gemini 401 | `.env` missing, `load_dotenv()` not called, or `api_key=` not passed. |
| IDE underlines `run(user_msg=...)` | Ignore it. Official docs use this form; the pin marks a type-overload deprecated. It runs. |
| `str \| None` on `model=` | You dropped the default. Use `os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash-lite")`. |
| Answers without calling the tool | Tighten the prompt: `"Use the multiply tool. What is 1234 * 4567?"` |
| `asyncio` error in notebook vs script | Script needs `asyncio.run`. Notebooks can `await` at top level. |

Do not add chat history, RAG, or a second tool here.

## Checkpoint

1. What three things did the model see besides the user question?
2. Who executed `multiply` — the model or your process?
3. Who owns the loop here — you or `FunctionAgent`?

Answers: (1) tool name, docstring, argument types; (2) your process — the `your process ran multiply(...)` print proves it; (3) `FunctionAgent`. Phase 2 is when you own the loop.
