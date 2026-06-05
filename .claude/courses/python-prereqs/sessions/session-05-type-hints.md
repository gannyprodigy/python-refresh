# Session 05 — Type Hints

**Status**: ⬜ Not Started
**Builds On**: Session 04 (classes — including `TypedDict` which is a special class form)
**Session goal**: You can annotate any function or class, and read any typed codebase — including the `str | None`, `TypedDict`, `Literal`, and `Annotated` patterns — without pausing.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-05/01_basic_annotations.ipynb` | Variables, functions, return types |
| 2 | `sessions/session-05/02_union_collections.ipynb` | `str \| None`, `list[T]`, `dict[K,V]`, union types |
| 3 | `sessions/session-05/03_typeddict_literal.ipynb` | `TypedDict`, `Literal`, when to use each |
| 4 | `sessions/session-05/04_annotated_final.ipynb` | `Annotated`, `Final`, `ClassVar` |
| — | `sessions/session-05/type_hints.py` | Final: annotated module with every hint pattern |

---

## Segments

### Segment A — Basic annotations: variables and functions (~30 min)
**Notebook**: `01_basic_annotations.ipynb`

**Mental model**: Type hints are labels you attach to variables and function signatures. They tell readers, editors, and tools what type to expect. Python itself ignores them at runtime — but your editor uses them for autocomplete and error detection, Pydantic uses them for validation, and FastAPI uses them to generate API documentation.

**Analogy**: Type hints are like labels on storage boxes. The box works the same whether it's labelled or not — but without labels, you don't know what's inside until you open it. With labels, your editor catches "you're putting a screwdriver in the 'kitchen utensils' box" before you make the mistake.

```python
# Variable annotations
name: str = "Riya"
age: int  = 34
score: float = 4.8
active: bool = True

# Function annotations — the most important form
def book_appointment(patient: str, date: str, slots: int = 1) -> dict:
    return {"patient": patient, "date": date, "slots": slots}

# Return type None — when a function does work but returns nothing
def send_reminder(patient_id: str, message: str) -> None:
    # ... send the message
    pass   # no return statement needed
```

**Misconception**: Type hints don't raise errors at runtime. `def f(x: int): ...` called with `f("hello")` will not crash Python — it just runs. Only a type checker (mypy, pyright, your IDE) or Pydantic will catch the mismatch. Don't confuse "annotated" with "enforced."

---

### Segment B — Union types, optional fields, and typed collections (~35 min)
**Notebook**: `02_union_collections.ipynb`

**Mental model**: Real data is often "one type *or* another." A field might be a string or `None`. A field might accept a string or a list of strings. Python 3.10+ lets you express this with the `|` operator — clean, readable, and what you'll see in every production codebase.

```python
# str | None — the most common union. Means "string or nothing."
def get_doctor(doctor_id: str) -> str | None:
    # Returns the doctor's name, or None if not found
    ...

# Multiple types
def process_input(data: str | list[str] | None) -> str:
    ...

# Old syntax (Python < 3.10) — you'll see this in older code:
from typing import Optional
def get_doctor(doctor_id: str) -> Optional[str]:  # same as str | None
    ...

# Modern syntax (Python 3.10+) — use this:
def get_doctor(doctor_id: str) -> str | None:     # ✅ cleaner
    ...
```

**Typed collections — always use the lowercase form in Python 3.9+:**

```python
# ✅ Modern (Python 3.9+) — use lowercase built-in types
def get_medications(patient_id: str) -> list[str]: ...
def get_record(record_id: str) -> dict[str, str | int]: ...
def get_ids(user_id: str) -> tuple[str, str, int]: ...
def get_unique_codes(patient_id: str) -> set[str]: ...

# ❌ Old style — avoid:
from typing import List, Dict, Tuple, Set
def get_medications(patient_id: str) -> List[str]: ...
```

Nested types — exactly as they appear in production models:
```python
# A list of dicts
def get_workouts() -> list[dict[str, str | float | int]]: ...

# A dict with string keys mapping to lists
def get_schedule() -> dict[str, list[str]]: ...

# A function that accepts a list of models
def process_patients(patients: list[Patient]) -> list[dict]: ...
```

**Misconception**: `list[str]` not `List[str]` — the uppercase `List` from `typing` is the old way (Python 3.8 and earlier). Since Python 3.9, you can annotate with the actual built-in type directly. Since Python 3.12 is the target for this course, always use lowercase.

---

### Segment C — TypedDict and Literal (~25 min)
**Notebook**: `03_typeddict_literal.ipynb`

**Mental model**: `TypedDict` defines the expected shape of a plain Python dict — with named keys and specific value types. The dict still behaves exactly like a normal dict at runtime; `TypedDict` is purely for the type checker and reader. This is the exact pattern LangGraph uses for agent state — every agent graph starts with a `TypedDict` defining its state schema.

```python
from typing import TypedDict

class AgentState(TypedDict):
    messages:      list[str]
    current_agent: str
    patient_id:    str | None
    done:          bool

# Usage — it's just a plain dict with declared structure
state: AgentState = {
    "messages":      [],
    "current_agent": "receptionist",
    "patient_id":    None,
    "done":          False,
}

# You can add/access keys like a normal dict
state["messages"].append("Hello")
state["done"] = True
```

`Literal` — a string (or int, bool) constrained to a specific set of values:

```python
from typing import Literal

# Status can ONLY be one of these four strings
AppointmentStatus = Literal["pending", "confirmed", "cancelled", "completed"]

def update_status(appt_id: str, status: AppointmentStatus) -> None: ...

# The type checker will flag this:
update_status("a123", "rescheduled")  # ❌ type error — "rescheduled" not in Literal
update_status("a123", "confirmed")    # ✅
```

**When to use `TypedDict` vs Pydantic `BaseModel`:**

| Use case | Use |
|----------|-----|
| LangGraph agent state | `TypedDict` — must be a plain dict |
| Validated input/output | `BaseModel` — Pydantic validates at runtime |
| Internal function return types | `TypedDict` — lightweight, no validation overhead |
| API request/response schemas | `BaseModel` — FastAPI reads these |

**Misconception**: `TypedDict` does NOT validate at runtime. Passing `"rescheduled"` as a `Literal["pending", "confirmed"]` won't raise an error in Python — only in the type checker. For runtime validation, use Pydantic's `BaseModel` (Session 08).

---

### Segment D — Annotated, Final, ClassVar (~25 min)
**Notebook**: `04_annotated_final.ipynb`

**Mental model**: `Annotated` lets you attach extra metadata to a type hint — not just the type, but additional constraints or documentation that Pydantic and FastAPI can read. `Final` marks a variable that should never be reassigned. `ClassVar` marks a class attribute (shared across all instances, not per-instance).

`Annotated` — the pattern Pydantic v2 uses for field constraints:

```python
from typing import Annotated
from pydantic import Field

# Instead of:
class WorkoutSet(BaseModel):
    weight_kg: float = Field(gt=0, description="Weight in kilograms")
    reps: int        = Field(ge=1, le=50, description="Number of reps")

# You can also write:
Weight = Annotated[float, Field(gt=0, description="Weight in kilograms")]
Reps   = Annotated[int,   Field(ge=1, le=50)]

class WorkoutSet(BaseModel):
    weight_kg: Weight
    reps:      Reps
```

`Final` — a constant that should never be reassigned:

```python
from typing import Final

MAX_RETRIES: Final = 3
API_VERSION: Final[str] = "v1"

MAX_RETRIES = 5   # type checker flags this — but Python doesn't enforce it at runtime
```

`ClassVar` — a class-level attribute shared across all instances, not stored per-instance:

```python
from typing import ClassVar

class Appointment:
    clinic_timezone: ClassVar[str] = "Asia/Kolkata"  # shared by all appointments
    
    def __init__(self, patient: str):
        self.patient = patient   # per-instance, stored on each object

a1 = Appointment("Riya")
a2 = Appointment("Arjun")

Appointment.clinic_timezone    # "Asia/Kolkata"
a1.clinic_timezone             # "Asia/Kolkata" — same value
Appointment.clinic_timezone = "UTC"
a1.clinic_timezone             # "UTC" — shared, both instances see the change
```

**Misconception**: `Final` doesn't raise a runtime error on reassignment in Python — it's a signal to the type checker only. If you need true runtime enforcement, use a property with no setter, or a frozen Pydantic model.

---

## Best Practices in This Session

⚡ Use `str | None` not `Optional[str]` — cleaner, Python 3.10+ syntax  
⚡ Use `list[str]`, `dict[str, int]` not `List[str]`, `Dict[str, int]` — lowercase form since Python 3.9  
⚡ Annotate every function signature; skip annotations on local variables (too noisy)  
⚡ Use `TypedDict` for LangGraph state and internal dicts; use `BaseModel` when you need validation  
⚡ `Literal` for strings that should be one of a fixed set — catches typos at type-check time, not at runtime

---

## What's Next

Session 06 — Decorators. You've seen `@classmethod`, `@staticmethod`, and `@property` — all decorators. Now the full picture: what a decorator actually *is* under the hood, how to write one from scratch, and the `functools.wraps` rule that prevents a class of silent bugs. After this session, `@retry`, `@tool`, and `@app.get` are completely readable.
