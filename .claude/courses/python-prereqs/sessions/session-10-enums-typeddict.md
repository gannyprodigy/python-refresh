# Session 10 — Enums + TypedDict

**Status**: ⬜ Not Started
**Builds On**: Session 05 (type hints — `TypedDict` was introduced there), Session 08–09 (Pydantic models use `Enum` for constrained fields)
**Session goal**: You define an `Enum` and a `StrEnum` for status and task-type fields, and a `TypedDict` for agent state — and know exactly when to use each versus a plain string or a Pydantic model.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-10/01_enum_strenum.ipynb` | `Enum`, `StrEnum`, when each applies |
| 2 | `sessions/session-10/02_typeddict.ipynb` | `TypedDict`, `total=False`, LangGraph state |
| — | `sessions/session-10/enums_typeddict.py` | Final: StrEnum + TypedDict agent state |

---

## Segments

### Segment A — Enum: named constants with type safety (~35 min)
**Notebook**: `sessions/session-10/01_enum_strenum.ipynb`

**Mental model**: An `Enum` is a class whose members are fixed constants. Instead of checking `if status == "confirmed"` — a string that could be misspelled, autocompleted wrong, or changed in one place but not another — you check `if status == AppointmentStatus.CONFIRMED`. The misspelling becomes a `NameError` immediately at development time, not a silent bug at 3am in production.

**Analogy**: Enums are like traffic lights. "Red", "Amber", "Green" are the only valid states. You wouldn't accept a traffic light that shows "redd" or "grreen" — those don't exist. An `Enum` makes invalid states impossible to represent in code.

```python
from enum import Enum

class AppointmentStatus(Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

# Creating and comparing
status = AppointmentStatus.CONFIRMED

status == AppointmentStatus.CONFIRMED   # True
status == AppointmentStatus.CANCELLED   # False
status == "confirmed"                   # False — Enum != plain string (without StrEnum)

# Accessing the value
status.value   # "confirmed"
status.name    # "CONFIRMED"

# Iterating all members
for s in AppointmentStatus:
    print(s.name, "→", s.value)

# From a string (e.g., from a database or API)
AppointmentStatus("confirmed")   # → AppointmentStatus.CONFIRMED
AppointmentStatus("invalid")     # ValueError: 'invalid' is not a valid AppointmentStatus
```

**StrEnum — when you need string-compatible enums:**

Plain `Enum` members are not equal to strings. If you're storing enum values in a database or JSON (where they become strings) and comparing them back, you need `StrEnum` — whose members *are* strings.

```python
from enum import StrEnum   # Python 3.11+

class TaskType(StrEnum):
    ROUTING  = "routing"
    ANALYSIS = "analysis"
    SUMMARY  = "summary"
    REPORT   = "report"

# StrEnum members ARE strings
TaskType.ROUTING == "routing"   # True ✅ (plain Enum would be False)
TaskType.ROUTING.upper()        # "ROUTING" — string methods work

# Works directly in dict keys without .value
MODEL_MAP = {
    TaskType.ROUTING:  "claude-haiku-4-5-20251001",
    TaskType.ANALYSIS: "claude-sonnet-4-6",
    TaskType.SUMMARY:  "claude-sonnet-4-6",
    TaskType.REPORT:   "claude-opus-4-8",
}
MODEL_MAP[TaskType.ANALYSIS]   # "claude-sonnet-4-6"
MODEL_MAP["analysis"]          # "claude-sonnet-4-6" — also works with StrEnum
```

How this looks in a config module:

```python
class TaskType(StrEnum):
    ROUTING  = "routing"
    ANALYSIS = "analysis"
    SUMMARY  = "summary"
    REPORT   = "report"

def model_for(task: TaskType) -> str:
    return MODEL_MAP[task]

def max_tokens_for(task: TaskType) -> int:
    return MAX_TOKENS_MAP[task]

# Usage — clean, readable, typo-proof
model = model_for(TaskType.ANALYSIS)   # "claude-sonnet-4-6"
```

**The `class StrengthTier(str, Enum)` pattern** — an older equivalent of `StrEnum`:

```python
# Before Python 3.11, StrEnum didn't exist. This was the pattern:
class StrengthTier(str, Enum):
    BEGINNER     = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED     = "advanced"
    ELITE        = "elite"

# Members are strings (inheriting from str)
StrengthTier.INTERMEDIATE == "intermediate"   # True ✅
```

You'll see both in production codebases. `StrEnum` (Python 3.11+) is cleaner; `(str, Enum)` is the pre-3.11 equivalent.

**Misconception**: Plain `Enum` members are NOT strings. `AppointmentStatus.CONFIRMED != "confirmed"` — they're different types. If you store `AppointmentStatus.CONFIRMED` to a JSON field and read it back as the string `"confirmed"`, you must reconstruct with `AppointmentStatus("confirmed")`. Use `StrEnum` (or `str, Enum`) when the value lives in a database, JSON, or API response.

---

### Segment B — TypedDict: typed shape for plain dicts (~30 min)
**Notebook**: `sessions/session-10/02_typeddict.ipynb`

**Mental model**: `TypedDict` describes the expected keys and value types of a plain Python dict. The dict behaves exactly like a normal dict at runtime — no validation, no extra methods. `TypedDict` exists purely for the type checker and for readers — it makes the structure of complex dicts explicit and documentable.

This is the exact pattern LangGraph uses for agent state: every graph has a `TypedDict` defining what fields flow through it, and every node reads from and writes to that state dict.

```python
from typing import TypedDict

class AgentState(TypedDict):
    messages:      list[str]
    current_agent: str
    patient_id:    str | None
    done:          bool

# Usage — it's just a dict
state: AgentState = {
    "messages":      ["Hello, I need to book an appointment"],
    "current_agent": "receptionist",
    "patient_id":    None,
    "done":          False,
}

# Access like any dict
state["messages"].append("Do you have slots tomorrow?")
state["done"] = True
state["current_agent"]   # "receptionist"
```

**`total=False` — making all fields optional:**

```python
from typing import TypedDict

class WorkflowState(TypedDict, total=False):
    raw_input:   str         # optional — may not be set yet
    parsed_data: dict        # optional — set after extraction
    warnings:    list[str]   # optional — set after validation

# Only set what you have:
state: WorkflowState = {"raw_input": "some input text"}
# 'parsed_data' and 'warnings' not set — no error
```

**When to use `TypedDict` vs Pydantic `BaseModel`:**

| Situation | Use |
|-----------|-----|
| LangGraph agent state | `TypedDict` — LangGraph requires a plain dict |
| Validated API request/response | `BaseModel` — Pydantic validates at runtime |
| Internal function return type hint | `TypedDict` — lightweight, type-checker only |
| Config loaded from `.env` | `BaseSettings` (Session 09) |
| Any data that must be validated | `BaseModel` |

```python
# Real LangGraph pattern — the state flowing through an agent graph
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages:   Annotated[list, add_messages]  # special reducer
    session_id: str
    user_id:    str | None
    intent:     str | None
    done:       bool
```

**Misconception**: `TypedDict` does NOT validate at runtime. You can put the wrong type in a `TypedDict` field — Python won't complain. The type checker (your IDE, mypy) will flag it. If you need runtime validation, use Pydantic `BaseModel`. The choice between `TypedDict` and `BaseModel` is always: "do I need runtime enforcement?" If yes → `BaseModel`. If it's just for readability and IDE help → `TypedDict`.

---

## Best Practices in This Session

⚡ Use `StrEnum` (Python 3.11+) or `class Status(str, Enum)` for any field stored in a database or API response — plain `Enum` members are not strings  
⚡ `TypedDict` for LangGraph state — it must be a plain dict, `BaseModel` won't work  
⚡ `AppointmentStatus("confirmed")` to reconstruct an Enum from a database string — not `AppointmentStatus.CONFIRMED` which creates a new member  
⚡ `total=False` on a `TypedDict` when not all fields are always present — e.g., state that's built up incrementally across agent nodes  
⚡ Use `Enum` members (not `.value`) in code — `TaskType.ANALYSIS` not `"analysis"` — the type checker can catch `TaskType.ANALYSISS` but not `"analysiss"`

---

## What's Next

Session 11 — Async / Await. Every database call, every API call, every tool execution in an AI system is async. This session makes `async def`, `await`, `asyncio.gather()`, and `async with` fully readable and writable — the foundation that every AI library sits on.
