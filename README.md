# Python for AI Engineers

Python prerequisites course — everything you need to read and write production AI code.

## What this covers

13 sessions (~30 hours) taking you from Python basics to the patterns used in every production AI codebase:

| Session | Topic |
|---------|-------|
| 00 | Setup |
| 01 | Python Fluency (methods, comprehensions, lambda, built-ins) |
| 02 | Functions (def, *args/**kwargs, closures, first-class) |
| 03 | Classes Part 1 (\_\_init\_\_, self, methods, \_\_repr\_\_) |
| 04 | Classes Part 2 (inheritance, super(), @classmethod, dunders) |
| 05 | Type Hints (annotations, unions, TypedDict, Literal) |
| 06 | Decorators (@decorator, functools.wraps, factory pattern) |
| 07 | Context Managers (with, \_\_enter\_\_/\_\_exit\_\_, async with) |
| 08 | Pydantic v2 — Models (BaseModel, Field, validation, nesting) |
| 09 | Pydantic v2 — Validators + Settings (@field_validator, BaseSettings) |
| 10 | Enums + TypedDict (StrEnum, TypedDict for agent state) |
| 11 | Async / Await (async def, await, gather, async with) |
| 12 | Error Handling (try/except, custom exceptions, retry) |

## Course notes

Full session guides are in `.claude/courses/python-prereqs/sessions/`.

After each session, Claude writes notes to `.claude/courses/python-prereqs/session-notes/`.

## Setup

```bash
uv init .
uv add pydantic pydantic-settings httpx tenacity anyio
uv run python sessions/session-00/hello.py
```
