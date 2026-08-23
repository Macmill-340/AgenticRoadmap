# Agentic Frameworks Teaching Roadmap
*Research-backed, as of August 2026. Handoff document — structure and reasoning are final; code, exercises, and prose are for opencode to draft per phase.*

## Framework decision (why these three, and only these three)

| Layer | Framework | Role | Why |
|---|---|---|---|
| Fundamentals | Raw Python (+ `pydantic.BaseModel`) | Tool-call loop, state, validation | Small enough to build by hand; it's the atomic unit everything else reduces to |
| Retrieval | LlamaIndex (core only) | Load → chunk → embed → store → query | Best-in-class RAG ergonomics; official 2026 tutorial sequence maps directly onto this teaching order |
| Orchestration | LangGraph | Stateful graph, branching, checkpointing, HITL | Dominant production framework (~41–45% of enterprise agent deployments in 2026); this is the one that transfers to a job |
| Optional aside | smolagents | Code-as-action paradigm | Actively maintained, teaches a genuinely different mental model LlamaIndex/LangGraph don't cover |

**Explicitly excluded from the core path:** LangChain (superseded by LangGraph for orchestration, its remaining niche is integration breadth you don't need for teaching), Pydantic AI as a full framework (its core teaching value — typed validation — is folded into the raw fundamentals phase via bare `pydantic.BaseModel` instead of adopting a second agent framework), MCP (explicitly deferred by request), LlamaIndex Workflows as a standalone phase (redundant with LangGraph for the same underlying concept — stateful branching — and LangGraph is the one worth the switching cost).

**The one hybrid pattern used, and it's load-bearing, not incidental:** LlamaIndex handles retrieval; LangGraph handles the agent loop, durable state, and human-in-the-loop gates. A LlamaIndex query engine gets wrapped in a plain function/`@tool` and called from inside a LangGraph node. This is the standard 2026 production pattern, not a workaround — so the capstone project doubles as "how it's actually done," not a toy example.

## Cross-cutting setup notes (apply to every phase, stated once here)
- **Fresh virtual environment per major phase-group**, not one shared environment for the whole roadmap. Phases 4–6 (LlamaIndex) and Phase 7 (LangGraph) pin different, occasionally conflicting dependency trees — isolating them avoids a debugging session about environments instead of concepts.
- **Local-first defaults throughout, matching the existing Ollama-based setup:** `nomic-embed-text` for embeddings (Phase 4–6), the already-configured local Qwen3 model for chat/tool-calling where the exercise doesn't specifically require a hosted model's tool-calling reliability. Note explicitly where a hosted model (OpenAI/Anthropic) is worth the cost for a given phase — tool-calling reliability on small local models can be noticeably worse than on hosted frontier models, and Phase 2 in particular depends on the model reliably emitting well-formed tool calls, so it's worth flagging as the one phase where a hosted model may be worth it even under a cost-conscious default.
- **Pin exact versions in every requirements file opencode generates**, not just package names — this entire ecosystem (LangGraph especially) has had breaking changes multiple times within 2026 alone. A roadmap meant to be taught more than once needs to survive package updates between runs.

## Pedagogical rule applied throughout

For each phase, a deliberate call is made: **raw-first** when the concept is small and central enough that abstracting it away first would remove the entire lesson (the tool-call loop, state management). **Abstraction-first, then decomposed** when the pipeline has enough real engineering surface area that seeing it work end-to-end first gives a mental map worth having before opening the hood (RAG, LangGraph orchestration). **Concept-only, not built** where the value is intuition, not implementation (decoding/token prediction).

Every phase states which mode it uses and why — this isn't a stylistic footnote, it's the organizing principle opencode should preserve when drafting exercises.

---

## Phase 0 — Orientation
**Mode:** abstraction, ~30 minutes, not graded/tested.

**Goal:** give a working mental model of "what an agent even is" before any theory, so later explanations land against a real reference point instead of an abstraction.

**What to build:** run a LlamaIndex `AgentWorkflow` (or equivalent minimal prebuilt agent) with exactly one tool, live. Don't explain the internals yet — just point at the moving pieces: model, tool, the fact that it decided to call the tool at all.

**Notes for opencode:** keep this to the smallest possible working snippet (~15–20 lines). No error handling, no edge cases. The point is a five-minute "oh, that's what we're building toward," not a tutorial.

---

## Phase 1 — How decoding actually works (concept layer)
**Mode:** concept-only. Nothing is built by the learner in this phase.

**Goal:** demystify what's happening inside the model when Phase 0's agent "decided" to call a tool — next-token prediction, not reasoning in the human sense.

**Content to cover:**
- Logits → softmax → a probability distribution over the next token
- Sampling strategies: greedy, temperature, top-k, top-p, and how each changes output character
- The reframe that matters for everything downstream: tool-calling is the same token-prediction process, just steered toward emitting structured (JSON or code) output instead of prose

**Resources to use:** the Hugging Face AI Agents Course decoding/tokenization visualizer spaces — confirmed actively maintained (course maintainers active, content structure unchanged through 2026). Use these as interactive demos rather than building anything from scratch here; the payoff-to-effort ratio of hand-rolling a decoding visualizer is poor for a teaching context.

**Notes for opencode:** this phase should produce zero code deliverables. If a "project" feels necessary for momentum, a single throwaway script that prints logits/probabilities for the top-5 next tokens of a small local model is enough — but don't over-invest here.

---

## Phase 2 — The raw tool-calling loop (build it)
**Mode:** raw, fully hand-built. This is the load-bearing phase of the entire roadmap.

**Goal:** understand, at the level of raw messages and JSON, what every agent framework is doing under the hood: `messages + tool schemas → model proposes a call → your code executes it → the result goes back into messages → repeat`.

**What to build:**
1. A minimal chat loop against a provider SDK (OpenAI-compatible or Anthropic), no framework.
2. Define 1–2 simple tools (e.g. a calculator, a weather stub) as plain Python functions.
3. Hand-write the JSON tool schema for each — by hand first, so the shape of a tool schema is felt, not just generated.
4. Validate tool arguments with `pydantic.BaseModel` — this is where Pydantic's core teaching value (typed, validated inputs) gets folded in, without adopting a second agent framework.
5. Add a `max_steps` safety guard so the loop can't run away.

**Why raw and not abstraction-first here specifically:** this loop is small, concrete, and recurs identically inside every framework covered later (LlamaIndex's agent layer, LangGraph's `ToolNode`). Abstracting it away first would mean the *only* lesson in the whole roadmap about how tool-calling actually works gets skipped. Everything downstream is judged by how well it maps back onto this loop.

**Notes for opencode:** resist adding retries, streaming, or multi-tool orchestration here — those belong later. Keep this phase's code small enough that a learner can hold the whole loop in their head at once.

**Fine-tuned details easy to miss:**
- **OpenAI's and Anthropic's tool-calling message formats are not interchangeable**, and this is exactly the kind of detail that's invisible if a framework is used first. OpenAI expects a `tool_calls` array on the assistant message and a separate `role: "tool"` message keyed by `tool_call_id` for the result; Anthropic expects a `tool_use` content block on the assistant turn and a `tool_result` content block (keyed by the same `id`) inside the next `user` turn, not a distinct role. Picking one provider and being explicit about this shape — rather than hand-waving "and then you send the result back" — is the actual point of this phase.
- Write the JSON schema by hand once, on paper or in a comment, before ever calling `model.model_json_schema()` on the Pydantic model. Generating it automatically from the start skips the exact "oh, that's what a tool schema *is*" moment this phase exists to produce.
- `max_steps` should fail loudly (raise, don't silently return) — a silent cutoff teaches the wrong lesson about runaway loops being a minor inconvenience rather than a real failure mode to design around.

---

## Phase 3 — Manual state and memory (build it)
**Mode:** raw, direct extension of Phase 2.

**Goal:** understand what "memory" actually is before any framework's `Context` or `MemorySaver` object does it automatically — it's just data, rendered into the prompt.

**What to build:**
- Extend Phase 2's loop with a plain `dict` (or a `TypedDict`/Pydantic model) that accumulates: conversation history, any facts learned, tool results.
- Manually render that state into the system prompt on each turn — no pre-built memory module.
- Optional stretch: cap history length and show what happens to model behavior when older context is dropped vs. summarized.

**Why raw:** same reasoning as Phase 2 — this directly foreshadows LangGraph's `MessagesState`/checkpointer later, and having built it by hand makes that later abstraction legible instead of magic.

---

## Phase 4 — RAG fundamentals, abstraction-first (build it fast)
**Mode:** abstraction-first.

**Goal:** see a complete RAG pipeline work end-to-end before decomposing it, because RAG has enough real engineering surface (chunk size, embedding choice, top-k, vector store setup) that a working mental map is worth having before manual decomposition.

**What to build:**
- `pip install llama-index llama-index-vector-stores-chroma llama-index-embeddings-ollama` — given the existing local Ollama setup, pull `nomic-embed-text` (274 MB, 137M params) as the embedding model rather than defaulting to an OpenAI embedding call. It's small enough to load into VRAM instantly on an RTX 3050 and leaves headroom for the Qwen3 chat model to stay resident too.
- Load a small local document set with `SimpleDirectoryReader`.
- Build a `VectorStoreIndex` backed by a persistent Chroma client (not the in-memory default — persistence is the more realistic habit to build).
- Query it via `as_query_engine()`.

**Notes for opencode:** keep this to the "starter tutorial" scope — a handful of documents, default chunking settings, no reranking or hybrid search yet. The goal is "it works and I can see the shape," not production tuning.

**Fine-tuned details easy to miss:**
- **LlamaIndex's global `Settings` object is the single most common beginner trap.** If `Settings.embed_model` and `Settings.llm` aren't explicitly set before building the index, LlamaIndex silently defaults to OpenAI for both and throws an opaque `AuthenticationError`/`OPENAI_API_KEY not set` error that looks unrelated to what was actually misconfigured. Set both explicitly at the top of the script, every time — don't rely on defaults even "just for the demo."
- `nomic-embed-text` supports an 8,192-token context window, but Ollama **serves it with a 2,048-token default window** unless `num_ctx` is raised explicitly. Long chunks get silently truncated with no error — worth a deliberate demonstration of this failure mode rather than just a warning in prose.
- `chromadb.PersistentClient(path=...)` is the current API (the old `chromadb.Client(Settings(...))` pattern from 2023-era tutorials is deprecated) — LlamaIndex's `ChromaVectorStore` wraps a collection from this client, it doesn't create the client itself.

---

## Phase 5 — RAG decomposed (build it manually)
**Mode:** raw, immediately follows Phase 4.

**Goal:** open the hood on what Phase 4 did automatically.

**What to build, by hand, no LlamaIndex:**
1. Load raw text files.
2. Chunk manually (fixed-size, then sentence/paragraph-aware — show both, discuss the tradeoff).
3. Call an embedding model directly (same one Phase 4 used, for a fair comparison) to embed each chunk.
4. Store vectors directly via the `chromadb` Python client (not through LlamaIndex).
5. Embed a query, run a manual cosine-similarity or Chroma's own nearest-neighbor query, retrieve top-k chunks.
6. Stuff retrieved chunks into a prompt manually and generate an answer.

**Async, introduced here specifically:** embedding calls are the first genuinely I/O-bound operation in the roadmap. Use `asyncio.gather` to embed multiple chunks concurrently, and time it against a sequential loop so the payoff of async is visible, not asserted. This is the natural, motivated first appearance of async in the roadmap — not bolted on earlier for its own sake.

**Notes for opencode:** this is the single most valuable "internals" phase after Phase 2 — don't compress it. The comparison back to Phase 4's one-liner (`index.as_query_engine()`) is the actual lesson.

**Fine-tuned details easy to miss:**
- Chunking has two axes that get conflated if not called out separately: **splitting strategy** (fixed-character-count vs. sentence/paragraph-boundary-aware) and **overlap** (chunks sharing a tail/head window so an idea split across a boundary isn't lost entirely). Demonstrate a query that fails with naive fixed-size, no-overlap chunking and succeeds once overlap is added — a concrete failure is a better teaching moment than the parameter explained abstractly.
- Token-based vs. character-based chunk sizing matters concretely here: `nomic-embed-text`'s window is *token*-based, so a "500 character" chunk isn't a reliable proxy for "fits in the embedding window" across documents with different content density.
- Since this runs on a Windows machine natively (no WSL): `asyncio.gather` with Ollama's local HTTP embedding calls is fine as-is on modern Python's default event loop, but if any subprocess-based tool gets added later, flag that Windows' `ProactorEventLoop` and `asyncio` subprocess handling behave differently from the Linux/Mac defaults most tutorials are written against — worth a one-line callout, not a deep dive, so it isn't a silent debugging trap later.

---

## Phase 6 — RAG as a tool inside the agent
**Mode:** integration, reusing Phases 2–5 directly.

**Goal:** merge the two tracks built so far — the raw tool-calling loop now gets a real, non-trivial tool.

**What to build:** wrap Phase 4's (or Phase 5's, learner's choice) query engine in a plain function, register it as a tool schema in Phase 2's loop, and confirm the agent decides on its own when to call it vs. answer directly.

**Notes for opencode:** this phase should require almost no new code — its value is entirely in seeing two previously separate builds click together. Keep it short.

---

## Phase 7 — LangGraph capstone (abstraction-first, mirrors real production pattern)
**Mode:** abstraction-first, with a hand-rolled comparison afterward.

**Goal:** land on the framework that's actually dominant in production (~41–45% of enterprise agent deployments in 2026), and do it via the same hybrid pattern real teams use — LlamaIndex for retrieval, LangGraph for orchestration — rather than a disconnected toy example.

**What to build:**
1. `StateGraph` + `MessagesState` basics: nodes, edges, conditional routing (`tools_condition` or hand-written equivalent).
2. Take Phase 4's LlamaIndex query engine, wrap it as a `@tool`-decorated function (same shape as Phase 6, different framework).
3. Build a small graph: an agent node that can call the wrapped RAG tool, with `ToolNode` handling execution and looping back to the agent node.
4. Add a checkpointer (`MemorySaver` or similar) and show a conversation surviving a restart — this is the concrete payoff of "durable state" that raw Python in Phase 3 didn't give you.
5. Add one human-in-the-loop interrupt point (e.g. require approval before a specific tool call) — this is LangGraph's clearest differentiator from everything built so far.

**Why abstraction-first here:** hand-rolling a general event/step dispatcher with checkpointing and interrupts is mostly plumbing with low conceptual payoff relative to effort. Show the working graph first.

**Hand-rolled comparison, afterward (short, not a full rebuild):** a tiny hand-written step dispatcher — a dict of step functions plus a control loop, reusing the exact pattern from Phase 2/3 — to demystify that a "graph" here is fundamentally the same loop-plus-state shape already built by hand, with nicer syntax, persistence, and interrupts layered on top.

**Notes for opencode:** this is the second-most-important phase after Phase 2 (Phase 2 teaches the atomic mechanism; this phase teaches the industry-standard way of scaling it). Include enough on checkpointing and HITL that the learner understands *why* LangGraph, specifically, is the production answer — not just how to write the graph syntax.

**Fine-tuned details easy to miss — this phase has the most version-churn risk of the whole roadmap:**
- **`from langgraph.prebuilt import create_react_agent` is deprecated as of LangGraph 1.0 (October 2025).** That functionality moved to `from langchain.agents import create_agent`. A large fraction of tutorials, blog posts, and even some cached course material still reference the old import path and will fail with an unhelpful error, or silently pull in a shadow/legacy package. Confirm the current import path against the installed version before writing any exercise around it, and flag this explicitly to the learner as "if you see this elsewhere, it's outdated."
- Checkpointer imports live under `langgraph.checkpoint.memory` (`MemorySaver` / `InMemorySaver`) for local dev, and `langgraph.checkpoint.postgres` (`PostgresSaver` / `AsyncPostgresSaver`) for anything beyond a single teaching session. **`InMemorySaver` is explicitly documented as debugging/testing-only** — fine for this roadmap's purposes, but say so out loud so the learner doesn't carry it into a real project unmodified. `SqliteSaver` is a reasonable middle ground for "survives a restart, still zero extra infrastructure" given the local-first, cost-conscious tooling preference already in use for everything else in this setup.
- LangGraph pins specific `langchain-core` versions internally; installing it into an existing global/shared Python environment (rather than a fresh per-project virtual environment) is a common source of silent dependency conflicts. Given the existing dev setup runs multiple AI tools locally already, a dedicated venv for this phase specifically — not reused from earlier phases — is worth calling out as a default, not an afterthought.
- The package is modular: `langgraph` (graph engine) is separate from `langgraph-checkpoint`, `langgraph-checkpoint-postgres`, and the CLI. Installing just `langgraph` and expecting `PostgresSaver` to be available is a common early confusion.
- For the human-in-the-loop interrupt point specifically: `interrupt()` pauses the graph and requires the invoking code to resume with a `Command(resume=...)` on the next call using the same `thread_id` — it is not a blocking `input()` call inside the node. Worth a explicit before/after trace of the state to make the pause-and-resume mechanic concrete rather than assumed.

---

## Phase 8 — Optional: smolagents (code-as-action paradigm)
**Mode:** abstraction-first, self-contained side quest — not required for the core path.

**Goal:** expose a genuinely different paradigm — the model writes and executes Python code as its action, instead of emitting JSON tool calls.

**What to build:** a small `CodeAgent` example, contrasted directly against a `ToolCallingAgent` on the same task, to make the difference concrete rather than asserted.

**Notes for opencode:** frame this explicitly as "a different bet on how agents should act," not a framework to master. Half a day, max.

---

## Parking lot — know it exists, don't build it yet
Explicitly deferred by request, but worth a one-line forward pointer when relevant so it doesn't feel hidden:
- **MCP** — both LlamaIndex and LangGraph/LangChain ecosystems have native support when ready.
- **LangSmith / observability** — the standard tracing layer paired with LangGraph in production; natural next step once Phase 7 is comfortable.
- **Structured-output retries, evals, guardrails** — production hardening, not core concepts.
- **Multi-agent patterns (subgraphs, agent handoff, A2A protocol)** — natural extension of Phase 7 once single-agent LangGraph is solid.
- **LangGraph Deep Agents / long-horizon planning agents** — the frontier end of what LangGraph now supports; worth a mention only.

---

## Summary of what changed from the original Qwen/Grok drafts
- LangChain dropped entirely as a teaching target (both drafts had it as an open question — resolved: skip it, LangGraph is the answer for orchestration and LlamaIndex the answer for retrieval).
- LlamaIndex Workflows considered and then cut as a standalone phase — redundant with LangGraph for the same concept, and LangGraph is the one with real production adoption and mature middleware (checkpointing, HITL, observability) that LlamaIndex's orchestration layer doesn't yet match.
- Pydantic AI evaluated as a full framework and folded down to "bare `pydantic.BaseModel` inside the raw loop" instead — keeps the framework count minimal without losing the typed-validation lesson.
- Async placement moved to be motivated by the first genuinely I/O-bound step (manual embedding calls in Phase 5) rather than introduced early for its own sake.
- Final structure lands on exactly three frameworks, each doing only the job it's actually best at: raw Python (mechanism), LlamaIndex (retrieval), LangGraph (orchestration) — plus one optional aside (smolagents).
