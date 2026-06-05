# Session 07 — Context Managers

**Status**: ⬜ Not Started
**Builds On**: Session 06 (decorators), Session 02 (closures — `contextlib` uses generators)
**Session goal**: You understand why cleanup always runs in a `with` block even when an exception fires, can write your own context manager, and read `async with AsyncSession() as session:` without pausing.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-07/01_with_and_why.md` | The `with` contract and what it guarantees |
| 2 | `sessions/session-07/02_write_your_own.md` | `__enter__`/`__exit__` and `contextlib.contextmanager` |
| 3 | `sessions/session-07/03_async_context_managers.md` | `async with` — the version every DB call uses |

---

## Segments

### Segment A — What `with` does and the cleanup guarantee (~25 min)
**File**: `01_with_and_why.md`

**Mental model**: A context manager guarantees that cleanup code runs — whether the block inside succeeds, fails with an exception, or is interrupted. Any resource that needs to be "opened then closed" — a file, a database connection, an HTTP client — should live inside a `with` block.

**Analogy**: A `with` block is like a hotel key card. When you check in, the hotel activates your key (`__enter__`). When you check out — or if you get kicked out — the hotel deactivates it (`__exit__`). You can't forget to check out; the hotel handles it regardless.

```python
# Without with — resource leak on exception
f = open("data.txt", "w")
f.write("hello")            # if this raises an exception...
f.close()                   # ...this never runs. File stays open.

# With with — cleanup guaranteed
with open("data.txt", "w") as f:
    f.write("hello")        # if this raises...
                            # ...f.close() still runs. Always.
```

The same guarantee applies to database connections and HTTP clients:

```python
# HTTP client — closed after the block, even on exception
import httpx

with httpx.Client() as client:
    response = client.get("https://api.example.com/workouts")
    data = response.json()   # if this fails, client is still closed

# Database session — committed/rolled back and closed after the block
from sqlmodel import Session, create_engine

engine = create_engine("postgresql://...")
with Session(engine) as session:
    session.add(new_record)
    session.commit()   # if this fails, session is still closed
```

**Misconception**: The cleanup (`__exit__`) runs even when an exception is raised inside the block. That's the entire point. Without `with`, an exception between "open" and "close" leaks the resource permanently. At scale, leaked database connections will exhaust the connection pool and bring down the application.

---

### Segment B — Writing your own context manager (~35 min)
**File**: `02_write_your_own.md`

**Mental model**: Any class with `__enter__` and `__exit__` methods is a context manager. `__enter__` runs at the start of the `with` block and returns the value that goes into `as result:`. `__exit__` runs at the end — whether the block succeeded or raised an exception — and receives exception information if one occurred.

```python
class DatabaseTransaction:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        print("Transaction started")
        return self.session        # this is what 'as session:' receives

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()  # no exception → commit
            print("Transaction committed")
        else:
            self.session.rollback()  # exception → rollback
            print(f"Transaction rolled back: {exc_val}")
        return False  # False = don't suppress the exception

# Usage:
with DatabaseTransaction(session) as sess:
    sess.add(record)   # on success: commits. On exception: rolls back.
```

`__exit__` receives three arguments:
- `exc_type` — the exception class (`ValueError`, `KeyError`, etc.), or `None` if no exception
- `exc_val` — the exception instance, or `None`
- `exc_tb` — the traceback object, or `None`

Return `False` (or `None`) to let the exception propagate. Return `True` to suppress it (rarely correct).

**The `contextlib.contextmanager` shortcut** — same result, half the code:

```python
from contextlib import contextmanager

@contextmanager
def database_transaction(session):
    try:
        yield session          # yield = the 'as session:' value
        session.commit()       # runs after the with block if no exception
    except Exception:
        session.rollback()
        raise                  # re-raise so the caller knows something failed

with database_transaction(session) as sess:
    sess.add(record)
```

The pattern: set up → `yield` → teardown. Code before `yield` is `__enter__`. Code after (in `finally` or after the `yield`) is `__exit__`.

**Misconception**: In `contextlib.contextmanager`, there must be *exactly one* `yield`. The generator must yield exactly once. A context manager that yields twice, or not at all, raises a `RuntimeError`.

---

### Segment C — `async with`: the async version (~25 min)
**File**: `03_async_context_managers.md`

**Mental model**: `async with` is the async version of `with`. Instead of `__enter__` and `__exit__`, async context managers define `__aenter__` and `__aexit__`. You must use `async with` for any async resource — using regular `with` on an async context manager raises a `TypeError`.

This is the pattern every database query and every HTTP call uses in production AI code:

```python
import httpx

# Async HTTP client — must use 'async with'
async def fetch_workouts(api_key: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.hevyapp.com/v1/workouts",
            headers={"api-key": api_key}
        )
        response.raise_for_status()
        return response.json()["workouts"]
```

```python
from sqlmodel.ext.asyncio.session import AsyncSession

# Async database session — must use 'async with'
async def get_patient(session: AsyncSession, patient_id: str) -> Patient | None:
    async with session.begin():
        result = await session.get(Patient, patient_id)
        return result
```

**Writing an async context manager with `contextlib`:**

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_connection(url: str):
    conn = await create_connection(url)
    try:
        yield conn
    finally:
        await conn.close()   # always closes, even on exception

async with managed_connection("redis://localhost") as conn:
    await conn.set("key", "value")
```

**Misconception**: You cannot use `async with` outside of an `async def` function. And you cannot use `with` (synchronous) on an async context manager — it won't call `__aenter__`, it'll try to call `__enter__`, which doesn't exist, and raise a `TypeError`. Always match: `async with` for async resources, `with` for sync resources.

---

## Best Practices in This Session

⚡ Never manually close a resource that has a context manager — always use `with`; manual close is never reached on exception  
⚡ `async with` for async resources — using `with` on an `AsyncClient` silently fails  
⚡ Return `False` from `__exit__` to let exceptions propagate — returning `True` silently swallows them  
⚡ Use `contextlib.contextmanager` for simple cases; `__enter__`/`__exit__` only when you need class-level state  
⚡ The `yield` in `contextlib.contextmanager` is the boundary between setup and teardown — always exactly one `yield`

---

## What's Next

Session 08 — Pydantic v2: Models. You've seen `class Patient(BaseModel)` and `class StrengthProfile(BaseModel)` throughout the examples. Now the full picture: how Pydantic builds on everything you know — type hints, classes, `Field()` — to create validated, serialisable data models that are the foundation of every AI pipeline.
