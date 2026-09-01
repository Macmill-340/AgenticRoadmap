# Phase 3 — State and memory by hand

Do first: `docs/00-setup.md`, `docs/02-phase-1-decoding.md`, `docs/03-phase-2-tool-loop.md`  
uv (from `agents/foundation`):

**Windows (PowerShell):**

```powershell
if (Test-Path agents\foundation) { cd agents\foundation }
uv sync
.venv\Scripts\activate
if (-not (Test-Path 03_state.py)) { New-Item -ItemType File 03_state.py }
```

**macOS/Linux:**

```bash
[ -d agents/foundation ] && cd agents/foundation
uv sync
source .venv/bin/activate
touch 03_state.py
```

Open `03_state.py` in your IDE — you will write the segments below there. The last line creates the file only if it does not already exist, so the same block is safe to re-run.

New terminals (VS Code, Cursor) usually open at the repo root; PyCharm sometimes restores already inside the folder. That `if` / `[ -d ... ] &&` does the right thing either way.

No new packages. Same `pyproject.toml` as Phase 2.

Suggested file: `agents/foundation/03_state.py`  
Mode: **raw**. Direct extension of Phase 2. No Memory class, no framework.

## What you'll build

Take Phase 2's `run_agent` and pass it a messages list you keep — so two calls share one conversation. Then add a small `facts` dict rendered into the system prompt. One deepening: **cap** (drop oldest) vs **summarize** (compress oldest).

## Why it matters

Phase 2's `run_agent` built `messages` inside the function. When it returned, everything the agent knew died. Real agents carry context across turns. Every later "memory" feature is the same idea: **data you hold yourself, rendered into the prompt**.

One thing to plant for later: LangGraph's `MessagesState` stores a message list whose reducer decides overwrite-vs-append — the choice you make here when new turns extend `state["messages"]` instead of replacing it. Phase 7 makes that explicit.

## Skeleton

Memory = **a dict you render into the prompt**.

1. Hold a messages list outside `run_agent`
2. Add `facts` and render them into the system string
3. Call the Phase 2 loop on that dict
4. If over budget: cap or summarize

## Official docs

- LiteLLM token usage & helpers: https://docs.litellm.ai/docs/completion/token_usage
- LiteLLM Gemini provider: https://docs.litellm.ai/docs/providers/gemini
- LangGraph Graph API (reducers / `MessagesState`, foreshadow only): https://docs.langchain.com/oss/python/langgraph/graph-api

## The big picture

Start with the Phase 2 list, living outside the function. Then state = `{"messages": [...], "facts": {...}}`.

**Messages outside `run_agent`.** Phase 2's list died when the function returned. Holding it yourself is what "memory" is.

**Facts.** A small dict you render into the system prompt each turn, so notes survive when history is trimmed.

**Render.** The model never sees your Python objects. Every call rebuilds a system string from the dict, then sends that plus the history.

**Budget.** The list cannot grow forever. Cap drops oldest messages; summarize compresses them into `facts`.

```mermaid
flowchart TD
  S["state: {messages, facts}"] --> R["render_system(state) + history"]
  R --> C["completion(...)"]
  C --> A["append assistant / tool msgs, update facts"]
  A --> B{over token budget?}
  B -->|no| S
  B -->|cap| D[drop oldest messages]
  B -->|summarize| E[compress oldest into facts.summary]
  D --> S
  E --> S
```

---

## Segment 1 — The messages list *is* state (and dies easily)

Two turns, one list:

```python
import os

from dotenv import load_dotenv

load_dotenv()

from litellm import completion

MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash-lite")
API_KEY = os.getenv("GEMINI_API_KEY")

messages = [{"role": "system", "content": "You are a concise assistant."}]

messages.append({"role": "user", "content": "My name is Ada."})
resp = completion(
    model=MODEL,
    api_key=API_KEY,
    messages=messages,
)
print(resp.choices[0].message.content)
messages.append(resp.choices[0].message)

messages.append({"role": "user", "content": "What is my name?"})
resp = completion(
    model=MODEL,
    api_key=API_KEY,
    messages=messages,
)
print(resp.choices[0].message.content)
```

```powershell
uv run python 03_state.py
```

**Expected:** the second answer contains `Ada`. Now delete the first three `append`/`completion` lines (keep only the final question) and rerun — the model has no idea. Nothing magical stored anything; **the list was the memory**, and you deleted it.

Keep `MODEL`, `API_KEY`, and the imports. Segment 2 replaces the two-turn script with Phase 2's loop, and the list lives outside it.

---

## Segment 2 — Same loop, list lives outside

This is the whole feature. Copy `add`, `AddArgs`, `run_add`, and the add JSON as `ADD_TOOL` from your `02_tool_loop.py`. Change `run_agent` so it takes the list you keep:

```python
from pydantic import BaseModel, ValidationError

MAX_STEPS = 8


def add(a: float, b: float) -> float:
    print(f"your process ran add({a}, {b})")
    return a + b


class AddArgs(BaseModel):
    a: float
    b: float


def run_add(raw_json: str) -> str:
    try:
        args = AddArgs.model_validate_json(raw_json)
    except ValidationError as exc:
        return f"Invalid arguments: {exc}"
    return str(add(args.a, args.b))


ADD_TOOL = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Add two numbers and return the sum.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First addend"},
                "b": {"type": "number", "description": "Second addend"},
            },
            "required": ["a", "b"],
        },
    },
}

TOOLS = [ADD_TOOL]


def run_agent(messages: list, user_text: str) -> str:
    messages.append({"role": "user", "content": user_text})
    for _step in range(MAX_STEPS):
        resp = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=messages,
            tools=TOOLS,
        )
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content or ""
        for call in msg.tool_calls:
            if call.function.name == "add":
                content = run_add(call.function.arguments)
            else:
                content = f"Unknown tool: {call.function.name}"
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": content}
            )
    raise RuntimeError(f"Agent exceeded max_steps={MAX_STEPS}")


messages = [
    {"role": "system", "content": "You are a concise assistant. Use add for arithmetic."},
]
print(run_agent(messages, "My name is Ada."))
print(run_agent(messages, "What is my name?"))
print(run_agent(messages, "What is 41 + 1?"))
```

**Expected:** Ada on the second line (from the list, not a Memory object); `your process ran add(...)` then `42` on the third. `run_agent` is called three times and `messages` is the same object — that is the entire feature.

**What just moved:** Phase 2 built `messages` inside the function and threw it away. Now you pass the list in. Two calls share one conversation.

---

## Segment 3 — Facts that survive when history is trimmed

History alone is fragile (Segment 4 proves it). Add a second channel: facts the agent writes with a `remember` tool, rendered into the system prompt every call.

### TypedDict in 20 seconds

`AgentState` looks like a class. At runtime it is still a dict. The names are for you and the type checker.

Same data, two shapes. Read, do not paste.

**Without** — keys are strings you can misspell:

```python
state = {"messages": [], "facts": {}}
state["mesages"] = []
```

**With** — the keys have names:

```python
from typing import TypedDict


class AgentState(TypedDict):
    messages: list
    facts: dict[str, str]


state: AgentState = {"messages": [], "facts": {}}
```

| Change | plain dict | TypedDict |
|---|---|---|
| Runtime | dict | still a dict |
| Keys | any string | `messages` and `facts` |
| Misspell | silent | your editor underlines it |

You need this because state is two channels — history and facts — and you will type those keys a lot.

Replace the bare `messages` list with a dict. Keep `ADD_TOOL` / `add` / `run_add`. Add `remember` beside `add`:

```python
from typing import TypedDict


class AgentState(TypedDict):
    messages: list
    facts: dict[str, str]


class RememberArgs(BaseModel):
    key: str
    value: str


REMEMBER_TOOL = {
    "type": "function",
    "function": {
        "name": "remember",
        "description": "Store a fact that should survive the whole session. Call only when the user says remember, keep, or store.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label, e.g. 'user_name'"},
                "value": {"type": "string", "description": "The fact itself"},
            },
            "required": ["key", "value"],
        },
    },
}

TOOLS = [ADD_TOOL, REMEMBER_TOOL]


def render_system(state: AgentState) -> str:
    base = "You are a concise assistant. Call remember only when the user explicitly says remember, keep, or store a fact. Use add for arithmetic."
    if state["facts"]:
        lines = "\n".join(f"- {k}: {v}" for k, v in sorted(state["facts"].items()))
        base += f"\n\nKnown facts:\n{lines}"
    return base


def build_messages(state: AgentState) -> list:
    return [{"role": "system", "content": render_system(state)}] + state["messages"]
```

`render_system` turns `facts` into text. `build_messages` puts that text on the front of the history. Change `facts`, and the next `completion()` sees different instructions.

Quick check (no model call):

```python
state: AgentState = {"messages": [], "facts": {}}
state["facts"]["user_name"] = "Ada"
for m in build_messages(state):
    print(m)
```

The system message contains `Known facts:` and `user_name: Ada`.

Now point Segment 2's loop at `state`. Two changes: `messages=build_messages(state)`, and a `remember` branch:

```python
def run_agent(state: AgentState, user_text: str) -> str:
    state["messages"].append({"role": "user", "content": user_text})
    for _step in range(MAX_STEPS):
        resp = completion(
            model=MODEL,
            api_key=API_KEY,
            messages=build_messages(state),
            tools=TOOLS,
        )
        msg = resp.choices[0].message
        state["messages"].append(msg)
        if not msg.tool_calls:
            return msg.content or ""
        for call in msg.tool_calls:
            if call.function.name == "remember":
                try:
                    args = RememberArgs.model_validate_json(call.function.arguments)
                    state["facts"][args.key] = args.value
                    content = f"Stored fact '{args.key}'."
                except ValidationError as exc:
                    content = f"Invalid arguments: {exc}"
            elif call.function.name == "add":
                content = run_add(call.function.arguments)
            else:
                content = f"Unknown tool: {call.function.name}"
            state["messages"].append(
                {"role": "tool", "tool_call_id": call.id, "content": content}
            )
    raise RuntimeError(f"Agent exceeded max_steps={MAX_STEPS}")


state: AgentState = {"messages": [], "facts": {}}
print(run_agent(state, "My name is Ada. Please remember it."))
print(run_agent(state, "What is my name?"))
print(run_agent(state, "What is 41 + 1?"))
print(state["facts"])
```

**Expected:** the second answer contains `Ada` *via the fact*, not just via history; the third prints `42`; `state["facts"]` shows the stored entry.

**What just moved:** `remember` writes `facts`. `build_messages` reads `facts` on the next call — including the next loop iteration of the same turn.

**Common failures**

| Symptom | Fix |
|---|---|
| Name answered but `facts` empty | Model answered from history. The user line must say remember/keep/store, or tighten `render_system`. |
| `OPENAI_API_KEY` error | You drifted onto defaults — `model=MODEL` and `GEMINI_API_KEY` only. |
| Tool loop runs away | Same guard as Phase 2: `max_steps` raises; don't soften it. |

---

## Segment 4 — Deepening: token budget, cap vs summarize

Gemini's context window is enormous — you will never overflow it in a demo. So the budget is **artificial on purpose**: `TOKEN_BUDGET = 150` tokens stands in for any hard constraint (a smaller local model, cost caps, latency). Keep the padding loop short — free Gemini allows about 15 requests per minute.

Two helpers, then two strategies. `over_budget` asks LiteLLM how many tokens the next prompt would be. `role_of` reads `role` whether the turn is a dict you appended or a LiteLLM message object.

```python
from litellm import completion, token_counter

TOKEN_BUDGET = 150


def over_budget(state: AgentState) -> bool:
    return token_counter(model=MODEL, messages=build_messages(state)) > TOKEN_BUDGET


def role_of(m) -> str:
    return m["role"] if isinstance(m, dict) else m.role
```

(`resp.usage.prompt_tokens` after a call is the other reading; `token_counter` works before one.)

### Strategy A — cap (drop oldest)

```python
def enforce_cap(state: AgentState) -> None:
    while state["messages"] and over_budget(state):
        state["messages"].pop(0)
        while state["messages"] and role_of(state["messages"][0]) == "tool":
            state["messages"].pop(0)
```

Dropping an assistant message that carried `tool_calls` leaves its `role: "tool"` replies parentless — most providers reject that, so sweep them too.

### Strategy B — summarize (compress oldest into facts)

```python
def enforce_summarize(state: AgentState, keep_last: int = 4) -> None:
    if over_budget(state) is False or len(state["messages"]) <= keep_last:
        return
    old = state["messages"][:-keep_last]
    kept = state["messages"][-keep_last:]
    while kept and role_of(kept[0]) == "tool":
        old.append(kept.pop(0))
    if not kept:
        return
    state["messages"] = kept

    def text_of(m) -> str:
        return (m.get("content") if isinstance(m, dict) else m.content) or ""

    transcript = "\n".join(f"{role_of(m)}: {text_of(m)}" for m in old)
    summary = completion(
        model=MODEL,
        api_key=API_KEY,
        messages=[
            {
                "role": "user",
                "content": f"Summarize in two sentences:\n{transcript}",
            },
        ],
    ).choices[0].message.content
    prev = state["facts"].get("summary", "")
    state["facts"]["summary"] = (prev + " " + summary).strip()
```

Summaries land in `facts`, so they ride along with every rendered system prompt — and facts are never trimmed.

### The experiment

Add an `enforce` argument to `run_agent` and call it **before** appending the new user turn — otherwise the demo below never trims:

```python
def run_agent(state: AgentState, user_text: str, enforce=None) -> str:
    if enforce is not None:
        enforce(state)
    state["messages"].append({"role": "user", "content": user_text})
```

Keep the rest of `run_agent` as in Segment 3. Pad the conversation so the budget bites, then interrogate. Do **not** ask the model to remember — history is the only carrier:

```python
def demo(enforce) -> None:
    state: AgentState = {"messages": [], "facts": {}}
    run_agent(state, "My name is Ada.", enforce=enforce)
    for i in range(5):
        run_agent(state, f"One sentence about the number {i}, please.", enforce=enforce)
    answer = run_agent(state, "What is my name?", enforce=enforce)
    print(enforce.__name__, "->", answer)
    print("facts:", state["facts"], "| turns:", len(state["messages"]))


demo(enforce_cap)
demo(enforce_summarize)
```

**Expected:**
- `enforce_cap` → the name is **forgotten** (history dropped, nothing else knew it).
- `enforce_summarize` → the name **survives** inside `facts["summary"]`.
- Bonus check: rerun the cap demo but say *"My name is Ada. Please remember it."* — with Segment 3's `remember` tool the model stores the fact, and **even the cap demo recalls it**. Durable memory is something the agent must choose to write; history is disposable.

Print `len(state["messages"])` before/after trimming so the mechanism is visible, not asserted.

| Symptom | Fix |
|---|---|
| 429 / rate limit | Free Gemini is ~15 requests/minute. Wait a minute, then rerun. Run `demo(enforce_cap)` and `demo(enforce_summarize)` as two separate passes if needed. |
| Cap demo still knows Ada | The model called `remember` without being asked. Tighten `render_system` so remember fires only on an explicit ask. |
| Missing corresponding tool call | Cap/summarize left a `role: tool` message without its parent. Sweep leading tool messages after the trim, same as `enforce_cap`. |

---

## Worth knowing

- **Render every call.** `build_messages(state)` recomputes the system prompt each `completion()` — never cache it. Facts change mid-loop.
- **Overwrite vs append is yours.** Here you always append to `messages` (that is `add_messages` behavior in Phase 7). If you ever assign instead of append, you have implemented the default-overwrite reducer — feel the difference once.
- **Rough vs exact counts.** `token_counter` uses a tokenizer approximation for Gemini; exact billing numbers come from `usage` on the response. Budget checks want approximations; bills want `usage`.
- **Windows note:** none yet. No async, no subprocess in this file.

## Don't add yet

- No Memory/chat-buffer classes, no LlamaIndex, no LangGraph import.
- No vector memory or embeddings — retrieval is Phases 4–6.
- No tiktoken install — `litellm.token_counter` is enough.
- No streaming, retries, or persistence-to-disk.
- Do not claim a real Gemini overflow; the budget is synthetic.

## Your finished file

`agents/foundation/03_state.py` — `MODEL`, `TOKEN_BUDGET`, `AgentState`, `RememberArgs`/`AddArgs`, `TOOLS` (add + remember), `render_system`, `build_messages`, `over_budget`, `role_of`, `enforce_cap`, `enforce_summarize`, `run_agent` (with `enforce=`), `demo`, `__main__`. Roughly 90–120 lines.

Segment 2's `run_agent(messages, ...)` is replaced by Segment 3's `run_agent(state, ...)`. Keep one.

## Checkpoint

1. In Segment 1, what exactly "remembered" Ada — and where did it go when you deleted it?
2. In Segment 2, why does the second `run_agent` call know Ada?
3. Why does the summarized name survive `enforce_summarize` but not `enforce_cap`?
4. If the model calls `remember` mid-loop, when does the new fact reach the model?
5. `TOKEN_BUDGET = 150` is fake. In production, where do the two real numbers come from?

Answers: (1) the `messages` list — it was the only carrier; deleting it deleted the memory. (2) you passed the same list in; Phase 2 used to throw it away. (3) summarize moves old content into `facts`, which is rendered into the system prompt and never trimmed; cap deletes outright. (4) on the *next* `build_messages()` — i.e., the next `completion()` call, possibly the same turn's next loop iteration. (5) the model's context window (provider spec / `litellm.model_cost`) and your own cost/latency ceiling; measured against `usage.prompt_tokens` or `token_counter`.

---

## Try this

Four turns, played with a friend (or yourself): turn 1 they tell the agent their name **and one preference** ("I'm Sam and I hate spoilers"). Turn 2–3, chat about something else so history grows. Turn 4, ask *"what does Sam hate?"* — with `enforce_cap` active so old turns drop.

Done when the answer comes from `facts`, not leftover history: the preference survives even though the early turns were trimmed. If it fails, check whether turn 1 actually called `remember`. Skip it or invent your own scenario — that is the point.
