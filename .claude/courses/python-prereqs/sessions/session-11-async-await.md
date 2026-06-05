# Session 11 — Async / Await

**Status**: ⬜ Not Started
**Builds On**: Session 07 (context managers — `async with`), Session 06 (decorators — `@retry` is async in practice)
**Session goal**: You write async functions from scratch, use `await` correctly, run three API calls in parallel with `asyncio.gather()`, and use `async with` for an HTTP client — the exact patterns every database and LLM call uses in production.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-11/01_mental_model.ipynb` | The cooperative waiting model — why async exists |
| 2 | `sessions/session-11/02_async_def_await.ipynb` | `async def`, `await`, the viral rule, `asyncio.run()` |
| 3 | `sessions/session-11/03_gather_parallel.ipynb` | `asyncio.gather()` — concurrent coroutines |
| 4 | `sessions/session-11/04_async_context_iterators.ipynb` | `async with`, `async for`, async generators |
| — | `sessions/session-11/async_patterns.py` | Final: async fetch, gather, streaming |

---

## Segments

### Segment A — The mental model: cooperative waiting (~35 min)
**Notebook**: `sessions/session-11/01_mental_model.ipynb`

**Mental model**: Async lets Python *pause* a function while it's waiting for something slow — a network request, a database query, a file read — and run other work in the meantime. Without async, one slow API call blocks everything. With async, hundreds of API calls can be "in flight" simultaneously, all using a single thread.

**Analogy**: A synchronous chef cooks one dish at a time: starts the pasta, stands over it for 12 minutes, serves it, then starts the risotto. An async chef starts the pasta, sets a timer, starts the risotto while the pasta cooks, then comes back to the pasta when the timer fires. Same one person, much more output — because waiting is the bottleneck, not cooking.

```python
import asyncio
import time

# Sync — each call waits for the previous one to complete
def get_patient_sync(patient_id: str) -> dict:
    time.sleep(1)   # simulate a database query taking 1 second
    return {"id": patient_id, "name": "Riya"}

start = time.perf_counter()
p1 = get_patient_sync("p_001")
p2 = get_patient_sync("p_002")
p3 = get_patient_sync("p_003")
print(f"Sync: {time.perf_counter() - start:.1f}s")   # ~3.0s

# Async — all three wait simultaneously
async def get_patient_async(patient_id: str) -> dict:
    await asyncio.sleep(1)   # simulate async database query
    return {"id": patient_id, "name": "Riya"}

async def main():
    start = time.perf_counter()
    p1, p2, p3 = await asyncio.gather(
        get_patient_async("p_001"),
        get_patient_async("p_002"),
        get_patient_async("p_003"),
    )
    print(f"Async: {time.perf_counter() - start:.1f}s")   # ~1.0s — all three ran concurrently

asyncio.run(main())
```

Three database calls that each take 1 second: sync = 3 seconds; async = 1 second. The speedup is the difference between your product feeling responsive or sluggish.

**What async does NOT speed up**: CPU-heavy work — sorting a million records, parsing a large file, doing matrix multiplication. Async only helps when Python is *waiting* on external things (network, disk, database). If Python is actively computing, async doesn't help.

**Misconception**: Async is not parallel and not multi-threaded. It's cooperative and single-threaded. While one coroutine is *waiting*, another runs. But two coroutines cannot run at the exact same time — there's no second CPU being used. The speedup comes from eliminating *idle waiting*, not from parallelism.

---

### Segment B — async def, await, and the viral rule (~40 min)
**Notebook**: `sessions/session-11/02_async_def_await.ipynb`

**Mental model**: `async def` marks a function as a *coroutine* — it can be paused. `await` is the pause point — "wait here until this async thing finishes, and let other coroutines run while we wait." The viral rule: if you call an async function, *your* function must also be async. Async spreads upward through the call chain.

```python
import asyncio
import httpx

# An async function — defined with 'async def'
async def fetch_workouts(api_key: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(       # 'await' pauses here while network waits
            "https://api.example.com/workouts",
            headers={"api-key": api_key},
        )
        response.raise_for_status()
        return response.json()["workouts"]

# Another async function — calls the above, so must also be async
async def get_top_lifts(api_key: str) -> list[str]:
    workouts = await fetch_workouts(api_key)   # 'await' — get the result
    return [w["exercises"][0]["title"] for w in workouts if w.get("exercises")]

# Entry point — asyncio.run() starts the event loop
asyncio.run(get_top_lifts("my-api-key"))
```

**The viral rule in action:**

```python
# ❌ WRONG — calling an async function without await
def process_data(api_key: str):
    workouts = fetch_workouts(api_key)   # returns a coroutine object, NOT the result
    print(workouts)   # <coroutine object fetch_workouts at 0x7f...> — not what you wanted

# ✅ CORRECT — must be async, must await
async def process_data(api_key: str):
    workouts = await fetch_workouts(api_key)   # actually runs the function
    print(workouts)   # [{"id": ..., "exercises": [...]}, ...]
```

**`asyncio.run()`** — the bridge between sync and async. You call it once, at the top level, to start the async world:

```python
# In a script (not a library):
if __name__ == "__main__":
    asyncio.run(main())

# In FastAPI, the framework calls your async functions — you never call asyncio.run() yourself
```

**`await` is only valid inside `async def`:**

```python
async def good():
    result = await some_async_function()   # ✅

def bad():
    result = await some_async_function()   # SyntaxError: 'await' outside async function
```

**Misconception**: You cannot use `await` inside a regular `def` function. If you need to call an async function from a sync function, you must either make the sync function async, or use `asyncio.run()` (which creates a new event loop — only safe at the top level of a script, never inside an already-running async context).

---

### Segment C — asyncio.gather(): parallel coroutines (~30 min)
**Notebook**: `sessions/session-11/03_gather_parallel.ipynb`

**Mental model**: `asyncio.gather()` starts multiple coroutines simultaneously and waits for all of them to finish. It returns a list of results in the same order as the inputs — regardless of which finished first. This is how you make 10 database calls in parallel instead of sequentially.

```python
import asyncio

async def get_patient(patient_id: str) -> dict:
    await asyncio.sleep(0.5)   # simulate DB query
    return {"id": patient_id, "name": f"Patient {patient_id}"}

# Sequential — 1.5 seconds
async def sequential():
    p1 = await get_patient("p_001")
    p2 = await get_patient("p_002")
    p3 = await get_patient("p_003")
    return [p1, p2, p3]

# Parallel with gather — 0.5 seconds
async def parallel():
    results = await asyncio.gather(
        get_patient("p_001"),
        get_patient("p_002"),
        get_patient("p_003"),
    )
    return results   # [{"id": "p_001", ...}, {"id": "p_002", ...}, {"id": "p_003", ...}]
```

**Passing a list to gather:**

```python
patient_ids = ["p_001", "p_002", "p_003", "p_004", "p_005"]

# Build the list of coroutines first, then pass with *
coroutines = [get_patient(pid) for pid in patient_ids]
results = await asyncio.gather(*coroutines)
```

**Handling individual failures with `return_exceptions=True`:**

```python
results = await asyncio.gather(
    get_patient("p_001"),
    get_patient("invalid"),    # this one might fail
    get_patient("p_003"),
    return_exceptions=True     # instead of crashing, exceptions are returned as values
)

for result in results:
    if isinstance(result, Exception):
        print(f"Failed: {result}")
    else:
        print(f"OK: {result}")
```

**Misconception**: `asyncio.gather()` is not threads. If any one coroutine does CPU-heavy work without yielding (without `await`), it blocks the event loop and prevents the others from running. `gather` only helps when coroutines spend time *waiting* on I/O — which is exactly what database queries and API calls do.

---

### Segment D — async for, async with, and async generators (~25 min)
**Notebook**: `sessions/session-11/04_async_context_iterators.ipynb`

**Mental model**: Just as `async def` and `await` are the async versions of `def` and a function call, `async with` is the async version of `with`, and `async for` is the async version of `for`. They're needed when the resource or iterator itself is async — meaning it yields control back to the event loop between operations.

**`async with` — you've seen this throughout the course:**

```python
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

# Every HTTP call in production uses this
async def call_api(url: str) -> dict:
    async with httpx.AsyncClient() as client:  # client opened and closed asynchronously
        response = await client.get(url)
        return response.json()

# Every database call in production uses this
async def get_records(session: AsyncSession) -> list:
    async with session.begin():                # transaction opened and closed async
        result = await session.exec(select(Patient))
        return result.all()
```

**`async for` — iterating an async source:**

```python
# Streaming LLM response — tokens arrive over time
async def stream_coaching_response(message: str):
    client = anthropic.AsyncAnthropic()
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": message}],
    ) as stream:
        async for text in stream.text_stream:   # each token arrives async
            print(text, end="", flush=True)
```

**Async generators — `yield` inside `async def`:**

```python
# An async generator: produces values one at a time, asynchronously
async def paginated_workouts(api_key: str, pages: int = 5):
    async with httpx.AsyncClient() as client:
        for page in range(1, pages + 1):
            response = await client.get(
                f"https://api.example.com/workouts?page={page}",
                headers={"api-key": api_key}
            )
            workouts = response.json()["workouts"]
            for workout in workouts:
                yield workout   # yields one workout at a time

# Consuming an async generator:
async def process_all_workouts(api_key: str):
    async for workout in paginated_workouts(api_key):
        process(workout)   # called for each workout as it arrives
```

**Misconception**: You cannot use `async with` outside of `async def` — same viral rule as `await`. And you cannot use regular `with` on an async context manager — it won't call `__aenter__`, it'll raise a `TypeError`. Match: `async with` for async resources, `with` for sync resources.

---

## Best Practices in This Session

⚡ Always `await` async function calls — forgetting gives you a coroutine object, not the result (no error message, just wrong behaviour)  
⚡ Never `time.sleep()` in async code — use `await asyncio.sleep()` or you block the entire event loop  
⚡ `asyncio.gather()` for parallel I/O-bound calls; sequential `await` for calls that depend on each other  
⚡ One `asyncio.run()` per program at the top level — never call it inside an already-running async context (FastAPI manages the loop for you)  
⚡ Use `httpx.AsyncClient`, not `requests` — `requests` is synchronous and will block the event loop in an async context

---

## What's Next

Session 12 — Error Handling. The final session. How to catch the right exceptions specifically (not everything), write custom exception classes for domain errors, and understand the retry pattern that `tenacity` implements — which is also the last library decorator you'll see in production AI code.
