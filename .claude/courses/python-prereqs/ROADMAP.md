# Course Roadmap — Python for AI Engineers

**Total sessions**: 13 (Session 00 + Sessions 01–12)
**Total hours**: ~30 hours
**Stack**: Python 3.12+ · uv · Jupyter · Pydantic v2 · pydantic-settings · httpx · tenacity

---

## Session Map

| Session | Title | Hours | Key Deliverable |
|---------|-------|-------|----------------|
| 00 | Setup | 0.5h | Environment confirmed, Jupyter running |
| 01 | Python Fluency | 2.5h | Read real production code without stopping |
| 02 | Functions | 2.5h | Closures understood; functions as first-class values |
| 03 | Classes Part 1 | 2.5h | Working `Patient` class with attributes and methods |
| 04 | Classes Part 2 | 2.5h | Class hierarchy with inheritance; `@classmethod` factory |
| 05 | Type Hints | 2h | Every function and class fully annotated; `TypedDict` clear |
| 06 | Decorators | 2h | Custom decorator from scratch; `functools.wraps` understood |
| 07 | Context Managers | 1.5h | Custom `with` block; `async with` demystified |
| 08 | Pydantic v2 — Models | 3h | Validated nested models; `ValidationError` handled cleanly |
| 09 | Pydantic v2 — Validators + Settings | 2.5h | All config in one `BaseSettings` class from `.env` |
| 10 | Enums + TypedDict | 1.5h | `StrEnum` for all status fields; `TypedDict` for graph state |
| 11 | Async / Await | 3h | Three parallel API calls with `gather`; `async with` session |
| 12 | Error Handling | 2h | Domain exceptions; retry pattern manual → `@retry` |

---

## What You Can Read After Each Session

```
After Session 00:  You have a working Python 3.12 environment.
                   uv, Jupyter, VS Code — all confirmed.

After Session 01:  You can read any Python file and not get stuck on:
                   f-strings, dict.get(), list comprehensions, lambda,
                   sorted(key=), pathlib.Path, datetime, defaultdict.

After Session 02:  You understand why *args/**kwargs exist.
                   You can trace a closure — the pattern decorators use.
                   You understand why functions are "objects" in Python.

After Session 03:  You can write any class from scratch.
                   You understand what self is and why every method needs it.
                   __repr__ no longer looks strange.

After Session 04:  class MyModel(BaseModel) makes sense — it's inheritance.
                   super().__init__() is not magic.
                   @classmethod from_dict() is readable.

After Session 05:  str | None, list[dict], TypedDict, Literal — all readable.
                   You can annotate any function or class you write.

After Session 06:  @retry, @tool, @limiter.limit, @app.get — all demystified.
                   You can write a decorator that wraps a function correctly.
                   functools.wraps is not optional.

After Session 07:  async with AsyncSession() as session: makes sense.
                   with httpx.AsyncClient() as client: is readable.
                   You know why the cleanup always runs, even on exception.

After Session 08:  class StrengthProfile(BaseModel) is completely readable.
                   ValidationError gives you clean, actionable messages.
                   Nested models — list[EstimatedOneRM] inside StrengthProfile — make sense.

After Session 09:  @field_validator and @model_validator are readable.
                   class Settings(BaseSettings) loads from .env automatically.
                   @computed_field vs @property — you know the difference.

After Session 10:  class TaskType(Enum) and class Status(str, Enum) are clear.
                   class AgentState(TypedDict) — the pattern LangGraph uses — makes sense.

After Session 11:  async def / await is not magic anymore.
                   asyncio.gather([call1(), call2(), call3()]) makes 3 calls simultaneously.
                   async with and async for are readable.

After Session 12:  You never write bare except: again.
                   Custom exceptions have a class, not a string message.
                   The @retry decorator replaces a while loop with a one-liner.
```

---

## The Python Patterns Map

Every pattern in this course maps directly to something in production AI code:

| Pattern Learned | Where You'll See It |
|-----------------|---------------------|
| `dict.get("key", default)` | Every API response handler — `w.get("exercises", [])` |
| `sorted(items, key=lambda x: -x[1])` | Cost tracking, PRs, leaderboards |
| `[f"..." for s in sets if s.get("weight")]` | Data transformation in every context builder |
| `def fn(*args, **kwargs)` | Decorator wrappers, library stubs |
| Closures | What every decorator is, under the hood |
| `class Model(BaseModel)` | Every schema in the system — profiles, records, configs |
| `@field_validator` | Input sanitisation — strip whitespace, validate formats |
| `class Settings(BaseSettings)` | The one place all config lives |
| `class Status(str, Enum)` | Every status field in every model |
| `class AgentState(TypedDict)` | LangGraph state — required for every agent graph |
| `async def` + `await` | Every database query, every API call, every tool |
| `async with AsyncClient() as client` | Every HTTP call to an external API |
| `asyncio.gather()` | Parallel API calls, batch processing |
| `@retry(stop=..., wait=...)` | Wrapping every external API call with automatic retry |
| Custom exception classes | Every domain error — `AppointmentNotFoundError`, `RateLimitError` |
