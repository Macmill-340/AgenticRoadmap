from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PHASE_GUIDES = sorted(DOCS.glob("*-phase-*.md"))
LEARNER_DOCS = PHASE_GUIDES + [DOCS / "00-setup.md", ROOT / "README.md"]
LLM_LEAKS = (
    "Last grounded:",
    "Fetch before writing",
    "A new coding session",
    "Prereq files:",
)

BANNED = (
    "packet",
    "cold-start",
    "parking lot",
    "shim",
    "load-bearing",
    "leverage",
    "robust",
    "seamless",
    "delve",
)
BARE_HEADERS = {"what", "why", "concept"}
MILESTONE_NAMES = {
    "03-phase-2-tool-loop.md",
    "04-phase-3-state-memory.md",
    "07-phase-6-rag-as-tool.md",
    "08-phase-7-langgraph.md",
    "09-phase-7b-multi-agent.md",
}
CONCEPT_ONLY = {"02-phase-1-decoding.md"}


def python_fences(text: str) -> list[str]:
    return re.findall(r"```python\n(.*?)```", text, re.DOTALL)


def strip_strings(line: str) -> str:
    return re.sub(r"""("([^"\\]|\\.)*"|'([^'\\]|\\.)*')""", "", line)


def heading_pos(text: str, pattern: str) -> int | None:
    m = re.search(pattern, text, re.MULTILINE)
    return m.start() if m else None


def check(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    name = path.name

    why = heading_pos(text, r"^## Why .+$")
    skeleton = heading_pos(text, r"^## Skeleton$")
    if skeleton is None:
        errors.append("missing ## Skeleton")
    elif why is None:
        errors.append("missing ## Why … before Skeleton")
    elif skeleton < why:
        errors.append("## Skeleton must come after Why")

    mermaids = len(re.findall(r"```mermaid", text))
    if mermaids != 1:
        errors.append(f"expected 1 mermaid, found {mermaids}")

    big = heading_pos(text, r"^## The big picture$")
    if name not in CONCEPT_ONLY and big is None:
        errors.append("missing ## The big picture")

    checkpoint = heading_pos(text, r"^## Checkpoint$")
    if checkpoint is None:
        errors.append("missing ## Checkpoint")

    try_this = heading_pos(text, r"^## Try this$")
    if name in MILESTONE_NAMES:
        if try_this is None:
            errors.append("milestone missing ## Try this")
        elif checkpoint is not None and try_this < checkpoint:
            errors.append("## Try this must come after ## Checkpoint")
    elif try_this is not None:
        errors.append("non-milestone has ## Try this")

    for m in re.finditer(r"^## (.+)$", text, re.MULTILINE):
        title = m.group(1).strip().lower()
        if title in BARE_HEADERS:
            errors.append(f"bare header: ## {m.group(1)}")

    lower = text.lower()
    for word in BANNED:
        if word in lower:
            errors.append(f"banned word: {word!r}")

    for i, block in enumerate(python_fences(text), 1):
        for line_no, line in enumerate(block.splitlines(), 1):
            if "#" in strip_strings(line):
                errors.append(f"python fence {i} line {line_no} has a # comment")

    errors.extend(leak_errors(text))
    return errors


def leak_errors(text: str) -> list[str]:
    errors: list[str] = []
    for phrase in LLM_LEAKS:
        if phrase in text:
            errors.append(f"learner-facing LLM instruction: {phrase!r}")
    return errors


def main() -> int:
    if not PHASE_GUIDES:
        print("no phase guides found", file=sys.stderr)
        return 1
    failed = 0
    for path in PHASE_GUIDES:
        errors = check(path)
        if errors:
            failed += 1
            print(f"{path.relative_to(ROOT)}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok  {path.relative_to(ROOT)}")
    for path in LEARNER_DOCS:
        if path in PHASE_GUIDES:
            continue
        if not path.exists():
            failed += 1
            print(f"{path.relative_to(ROOT)}")
            print("  - missing")
            continue
        errors = leak_errors(path.read_text(encoding="utf-8"))
        if errors:
            failed += 1
            print(f"{path.relative_to(ROOT)}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok  {path.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
