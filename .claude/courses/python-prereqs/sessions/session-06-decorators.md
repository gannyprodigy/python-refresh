# Session 06 — Decorators

**Status**: ⬜ Not Started
**Builds On**: Session 02 (closures — the pattern decorators use), Session 04 (`@classmethod`, `@staticmethod`, `@property` as examples)
**Session goal**: You can write a decorator from scratch with `functools.wraps`, and read any decorator in a production codebase — including `@retry`, `@tool`, `@limiter.limit`, and `@app.get`.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-06/01_decorator_from_scratch.ipynb` | The wrapper pattern → `@` syntax |
| 2 | `sessions/session-06/02_functools_wraps.ipynb` | Why `functools.wraps` is never optional |
| 3 | `sessions/session-06/03_decorator_with_args.ipynb` | `@retry(attempts=3)` — the factory pattern |
| — | `sessions/session-06/decorators.py` | Final: timing, logging, retry decorators |

---

## Segments

### Segment A — The mental model: functions that wrap functions (~30 min)
**Notebook**: `01_decorator_from_scratch.ipynb`

**Mental model**: A decorator is a function that takes a function, wraps it with extra behaviour (before or after), and returns the wrapped version. The `@` symbol is syntactic sugar — it's shorthand for "pass this function to that decorator and replace it with the result."

**Analogy**: A decorator is like a protective phone case. The phone still works the same — it calls, texts, runs apps. The case adds something around it (protection, grip, a card slot). The phone never knows it's in a case. Callers treat the cased phone exactly like the bare phone.

```python
# Step 1: Write the wrapper manually (no @ yet)
def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"→ Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"← Done")
        return result
    return wrapper   # return the wrapper function, not the result

def get_patient(patient_id: str) -> dict:
    return {"id": patient_id, "name": "Riya"}

# Apply the decorator manually:
get_patient = add_logging(get_patient)

# Now calling get_patient:
get_patient("p_001")
# → Calling get_patient
# ← Done
# Returns: {"id": "p_001", "name": "Riya"}
```

```python
# Step 2: The @ syntax — identical to the manual version above
def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"→ Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"← Done")
        return result
    return wrapper

@add_logging          # ← this line means: get_patient = add_logging(get_patient)
def get_patient(patient_id: str) -> dict:
    return {"id": patient_id, "name": "Riya"}

get_patient("p_001")   # same output as before
```

The `@add_logging` line is exactly equivalent to writing `get_patient = add_logging(get_patient)` after the function definition. Nothing more, nothing less.

**Stacking decorators** — decorators apply bottom-up:
```python
@add_logging      # applied second
@add_timing       # applied first (closest to the function)
def get_patient(patient_id: str) -> dict:
    ...

# Equivalent to:
# get_patient = add_logging(add_timing(get_patient))
```

**Misconception**: `@decorator` with no parentheses passes the function directly to the decorator. `@decorator()` with parentheses calls the decorator first (which must return another decorator). `@app.get("/patients")` has parentheses — it calls `app.get("/patients")` which returns a decorator, which then wraps your endpoint function. Getting this wrong gives a cryptic error.

---

### Segment B — `functools.wraps`: the rule that's never optional (~40 min)
**Notebook**: `02_functools_wraps.ipynb`

**Mental model**: When you wrap a function, the wrapper replaces it. The original function's name, docstring, and type hints are hidden inside the closure — from the outside world, the wrapper's name and docstring are what callers see. `functools.wraps` copies the original function's metadata onto the wrapper, so it looks and behaves like the original.

**Why this matters in AI code**: LangChain's `@tool` decorator reads the function's `__name__` and `__doc__` (docstring) to tell the LLM what the tool is called and when to use it. Without `functools.wraps`, a decorated tool function has the wrong name and an empty docstring — the LLM never calls it.

```python
import functools

# Without functools.wraps — BROKEN
def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@add_logging
def get_patient(patient_id: str) -> dict:
    """Look up a patient by ID."""
    return {}

get_patient.__name__   # "wrapper"      ← wrong! ❌
get_patient.__doc__    # None           ← wrong! ❌
```

```python
import functools

# With functools.wraps — CORRECT
def add_logging(func):
    @functools.wraps(func)        # copies __name__, __doc__, __annotations__
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@add_logging
def get_patient(patient_id: str) -> dict:
    """Look up a patient by ID."""
    return {}

get_patient.__name__   # "get_patient"           ← correct ✅
get_patient.__doc__    # "Look up a patient by ID." ← correct ✅
```

**Building a production-grade timing decorator:**

```python
import functools
import time

def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper

@timeit
def process_workouts(workouts: list[dict]) -> list[dict]:
    """Process and score a list of workouts."""
    return [{"id": w["id"], "score": len(w["exercises"])} for w in workouts]
```

**Misconception**: `functools.wraps` is not about correctness of behaviour — the decorated function works either way. It's about metadata. But metadata is what introspection-heavy libraries (LangChain, FastAPI, Pydantic) rely on to register tools, build schemas, and generate documentation. Skip `functools.wraps` and the integration breaks silently.

---

### Segment C — Decorators with arguments: the factory pattern (~30 min)
**Notebook**: `03_decorator_with_args.ipynb`

**Mental model**: Sometimes you want to configure a decorator: `@retry(attempts=3)`, `@limiter.limit("10/minute")`, `@cache(ttl=300)`. This requires one extra layer: the decorator factory — a function that *takes the configuration* and *returns a decorator*. Three levels of nesting instead of two.

**Analogy**: A plain decorator is a ready-made phone case. A decorator factory is a case manufacturer — you give the manufacturer your specifications (colour, model, card slots), and they produce the specific case you need.

```python
import functools

# Plain decorator — no arguments
@add_logging
def get_patient(): ...

# Decorator with arguments — needs a factory
def retry(attempts: int = 3, delay: float = 1.0):
    """Factory: takes config, returns a decorator."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    import time
                    time.sleep(delay)
        return wrapper
    return decorator   # return the decorator, not the wrapper

@retry(attempts=3, delay=0.5)
def call_external_api(url: str) -> dict:
    """Fetch data from an external API."""
    import httpx
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()
```

Three levels:
1. `retry(attempts=3, delay=0.5)` — the factory, called with config, returns `decorator`
2. `decorator(func)` — receives the function, returns `wrapper`
3. `wrapper(*args, **kwargs)` — the actual replacement function, called at runtime

In production, `tenacity`'s `@retry` works exactly this way — you won't write this yourself, but you'll read it constantly:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def get_workouts(page: int) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{HEVY_BASE}/workouts?page={page}")
        response.raise_for_status()
        return response.json()["workouts"]
```

`@retry(...)` is a factory call that returns a decorator. The decorator wraps `get_workouts` with automatic retry on failure.

**Misconception**: `@retry` and `@retry()` are different things. `@retry` (no parentheses) passes the function directly as the first argument — this only works if `retry` is designed as a plain decorator, not a factory. `@retry()` calls `retry()` first to get the decorator. If you use the wrong form, you get a confusing `TypeError`.

---

## Best Practices in This Session

⚡ Always use `functools.wraps` inside every decorator — without it, `__name__` and `__doc__` are wrong, which breaks tool registration and introspection  
⚡ `@decorator` (no parentheses) passes the function; `@decorator()` (with parentheses) calls the factory first — don't mix them up  
⚡ The three-level nesting of a decorator factory (factory → decorator → wrapper) is a fixed pattern — draw it before coding it  
⚡ Decorators stack bottom-up: the closest one to the function runs first  
⚡ Keep decorators single-purpose — a decorator that logs AND retries AND adds timing is three decorators

---

## What's Next

Session 07 — Context Managers. You've seen `with` blocks throughout the examples — `with httpx.AsyncClient() as client:`, `with open("file.txt") as f:`. Now what they actually do: guaranteed cleanup, how to write your own, and the async version that every database session uses.
