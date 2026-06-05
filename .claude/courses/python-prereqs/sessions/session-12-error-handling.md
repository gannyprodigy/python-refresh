# Session 12 — Error Handling

**Status**: ⬜ Not Started
**Builds On**: Session 06 (decorators — `@retry` is a decorator factory), Session 02 (functions — retry wrappers use `*args/**kwargs`)
**Session goal**: You write `try/except` blocks that catch specific exceptions, define custom domain exception classes, and understand exactly what `@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))` is doing — because you built the manual version first.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-12/01_try_except_depth.ipynb` | Catching specific exceptions, exception hierarchy |
| 2 | `sessions/session-12/02_finally_else.ipynb` | `finally`, `else`, clean resource management |
| 3 | `sessions/session-12/03_custom_exceptions.ipynb` | Domain exception classes |
| 4 | `sessions/session-12/04_retry_pattern.ipynb` | Manual retry → `tenacity` `@retry` |
| — | `sessions/session-12/error_handling.py` | Final: exception hierarchy + tenacity retry |

---

## Segments

### Segment A — try/except at depth: catching the right exception (~35 min)
**Notebook**: `sessions/session-12/01_try_except_depth.ipynb`

**Mental model**: `try/except` intercepts exceptions before they crash the program — but only if you catch the right exception type. Catching too broadly (bare `except:` or `except Exception:`) hides bugs. Catching too narrowly misses real failure modes. The skill is matching the handler to the failure mode.

**Analogy**: Error handling is like a hospital triage system. You don't send every patient to the emergency room — that would overwhelm the system. And you don't treat a broken arm with a bandage. Each condition has the right level of response. Same with exceptions: match the response to the severity.

```python
import httpx

# Too broad — catches everything, including bugs in your own code
try:
    response = httpx.get("https://api.example.com/patients")
    data = response.json()
except Exception as e:
    print("Something went wrong")   # ← hides whether it's a network error or a bug

# Too narrow — misses some real failure modes
try:
    response = httpx.get("https://api.example.com/patients")
except httpx.TimeoutException:
    print("Request timed out")
# ← doesn't handle ConnectionError, HTTPStatusError, etc.

# Correct — catch what you know how to handle; let the rest propagate
try:
    response = httpx.get("https://api.example.com/patients", timeout=10.0)
    response.raise_for_status()   # raises HTTPStatusError for 4xx/5xx
    data = response.json()

except httpx.TimeoutException:
    print("API timed out — will retry later")
    return None

except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        print("Rate limited — backing off")
        return None
    elif e.response.status_code == 404:
        print("Endpoint not found")
        return None
    else:
        raise   # re-raise — you don't know how to handle other status codes

except httpx.NetworkError as e:
    print(f"Network error: {e}")
    return None
```

**The exception hierarchy** — catching a parent class catches all its subclasses:

```python
# Exception hierarchy (simplified):
# BaseException
#   └── Exception
#         ├── ValueError
#         ├── TypeError
#         ├── KeyError
#         ├── RuntimeError
#         └── httpx.HTTPError
#               ├── httpx.HTTPStatusError
#               └── httpx.NetworkError

# Catching the parent catches all children:
except httpx.HTTPError:   # catches HTTPStatusError AND NetworkError
    ...
```

**Multiple except blocks** — ordered most-specific first:

```python
try:
    result = make_api_call()
except httpx.HTTPStatusError as e:   # most specific
    handle_status_error(e)
except httpx.NetworkError:            # less specific
    handle_network_error()
except httpx.HTTPError:               # most general httpx error
    handle_unknown_http_error()
# No bare except: — let unexpected exceptions propagate and crash loudly
```

**`raise` vs `raise e` vs `raise NewException() from e`:**

```python
try:
    result = make_api_call()
except httpx.HTTPStatusError as e:
    raise                           # re-raise original with original traceback ✅
    raise e                         # re-raise but resets traceback location ⚠️
    raise ValueError("Custom") from e  # new exception, chains original as cause ✅
```

**Misconception**: A `except Exception:` block that silently swallows the error (no `raise`) is almost always a bug. A crash with a traceback is 10x easier to debug than a silent wrong result. Only suppress an exception when you have a specific, intentional fallback.

---

### Segment B — finally and else: completing the pattern (~20 min)
**Notebook**: `sessions/session-12/02_finally_else.ipynb`

**Mental model**: `try/except` handles the failure case. `else` handles the success case — code that should only run if no exception was raised. `finally` handles the cleanup case — code that always runs, success or failure. Together they create a complete, readable error-handling block.

```python
def process_payment(payment_id: str) -> dict | None:
    conn = None
    try:
        conn = open_database_connection()
        result = conn.execute("SELECT * FROM payments WHERE id = ?", payment_id)
        data = result.fetchone()

    except DatabaseConnectionError as e:
        print(f"Could not connect to database: {e}")
        return None

    except QueryError as e:
        print(f"Query failed: {e}")
        return None

    else:
        # Only runs if no exception was raised
        print(f"Payment {payment_id} retrieved successfully")
        return data

    finally:
        # ALWAYS runs — even if an exception was raised, even if we return
        if conn:
            conn.close()   # close the connection regardless of what happened
```

`finally` is the right place for cleanup that must happen — closing connections, releasing locks, cleaning up temp files. Without `finally`, an exception between "open resource" and "close resource" leaks the resource.

**Misconception**: `finally` runs even when there's a `return` statement in the `try` or `except` block. The function doesn't return until `finally` completes. This is intentional — it guarantees cleanup.

---

### Segment C — Custom exceptions: domain error classes (~25 min)
**Notebook**: `sessions/session-12/03_custom_exceptions.ipynb`

**Mental model**: Python's built-in exceptions (`ValueError`, `KeyError`, `RuntimeError`) describe *how* something went wrong — not *what* in your domain failed. Custom exceptions describe the domain failure specifically. `AppointmentNotFoundError` is clearer than `ValueError: appointment not found`. It's also catchable by type — callers can handle `AppointmentNotFoundError` specifically without catching all `ValueError`s.

```python
# Base exception for your entire application
class AppError(Exception):
    """Base class for all application exceptions."""
    pass

# Domain-specific exceptions inherit from the base
class AppointmentNotFoundError(AppError):
    def __init__(self, appointment_id: str):
        self.appointment_id = appointment_id
        super().__init__(f"Appointment not found: {appointment_id!r}")

class SlotUnavailableError(AppError):
    def __init__(self, date: str, time: str):
        self.date = date
        self.time = time
        super().__init__(f"No slot available on {date} at {time}")

class PatientAlreadyExistsError(AppError):
    def __init__(self, phone: str):
        self.phone = phone
        super().__init__(f"Patient with phone {phone!r} already registered")

class RateLimitError(AppError):
    def __init__(self, service: str, retry_after: int | None = None):
        self.service = service
        self.retry_after = retry_after
        msg = f"Rate limited by {service}"
        if retry_after:
            msg += f" — retry after {retry_after}s"
        super().__init__(msg)
```

**Using custom exceptions:**

```python
async def get_appointment(appointment_id: str) -> Appointment:
    result = await db.get(Appointment, appointment_id)
    if result is None:
        raise AppointmentNotFoundError(appointment_id)
    return result

async def book_slot(date: str, time: str, patient_id: str) -> Appointment:
    if not await is_slot_available(date, time):
        raise SlotUnavailableError(date, time)
    return await create_appointment(date, time, patient_id)

# Catching specifically at the API layer:
async def handle_booking_request(date: str, time: str, patient_id: str) -> dict:
    try:
        appt = await book_slot(date, time, patient_id)
        return {"status": "confirmed", "appointment_id": appt.id}
    except SlotUnavailableError as e:
        return {"status": "unavailable", "date": e.date, "time": e.time}
    except PatientAlreadyExistsError as e:
        return {"status": "duplicate", "phone": e.phone}
    # AppointmentNotFoundError and others propagate to the framework error handler
```

**Misconception**: Adding custom attributes to a custom exception (`self.appointment_id`, `self.retry_after`) is not extra complexity — it's essential. Without them, the handler has to parse the string message to extract information. With them, the handler reads `e.appointment_id` directly.

---

### Segment D — The retry pattern: manual to tenacity (~30 min)
**Notebook**: `sessions/session-12/04_retry_pattern.ipynb`

**Mental model**: External APIs fail occasionally — network blips, temporary rate limits, momentary service outages. The correct response is to wait briefly and try again, with increasing delay between attempts. This is the retry pattern. You'll build it manually first to understand it, then see how `tenacity`'s `@retry` decorator replaces it in one line.

**The manual version:**

```python
import asyncio

async def call_with_retry(func, *args, max_attempts: int = 3, **kwargs):
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except (httpx.NetworkError, httpx.TimeoutException) as e:
            if attempt == max_attempts:
                raise   # give up after max attempts
            wait = 2 ** (attempt - 1)   # 1s, 2s, 4s
            print(f"Attempt {attempt} failed: {e}. Waiting {wait}s...")
            await asyncio.sleep(wait)

# Usage:
workouts = await call_with_retry(fetch_workouts, api_key="my-key", max_attempts=3)
```

**The tenacity version — a decorator:**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException))
)
async def fetch_workouts(api_key: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.example.com/workouts",
            headers={"api-key": api_key}
        )
        response.raise_for_status()
        return response.json()["workouts"]
```

What each argument does:
- `stop_after_attempt(3)` — give up after 3 failures
- `wait_exponential(multiplier=1, min=1, max=10)` — wait 1s, 2s, 4s, 8s... up to 10s max
- `retry_if_exception_type(...)` — only retry on these specific exceptions; let others propagate immediately

**Why only retry transient errors:**

```python
# ✅ Retry these — they're temporary:
retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException, RateLimitError))

# ❌ Never retry these — they won't fix themselves:
# - 401 Unauthorized (bad API key)
# - 400 Bad Request (malformed input)
# - ValidationError (your code passed wrong data)
```

**Misconception**: Don't wrap `@retry` around the entire application. Wrap it around specific external API calls — `fetch_workouts`, `send_whatsapp_message`, `create_payment_link`. Internal functions don't need retry; they fail fast and loudly so you fix the bug.

---

## Best Practices in This Session

⚡ Catch specific exception types — never bare `except:` or `except Exception:` as a catch-all  
⚡ Always log the exception before swallowing it — a `print(f"Error: {e}")` is the minimum  
⚡ Custom exception classes for domain errors — one class per category of failure, with relevant attributes  
⚡ Only retry transient errors (network, rate limit) — never retry on auth failure or bad input  
⚡ `raise` (not `raise e`) to re-raise with the original traceback intact

---

## Course Complete

After this session, open any production AI codebase and read it without stopping.

Every pattern — the `@retry` decorator, the `async with session:` block, the `class Config(BaseModel):` schema, the `TypedDict` state, the `StrEnum` status, the `@field_validator` business rule — is no longer unfamiliar. You built each one from scratch, understood exactly why it exists, and know what breaks when it's missing.

That's the prerequisite. The next layer is the product.
