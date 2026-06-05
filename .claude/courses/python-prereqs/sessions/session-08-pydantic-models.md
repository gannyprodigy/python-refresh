# Session 08 — Pydantic v2: Models

**Status**: ⬜ Not Started
**Builds On**: Session 03–04 (classes, inheritance), Session 05 (type hints — Pydantic reads these)
**Session goal**: You define a nested, validated Pydantic model from scratch, create instances, catch `ValidationError` cleanly, and serialise to dict and JSON — the exact pattern used for every schema in an AI pipeline.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-08/01_basemodel_fields.md` | `BaseModel`, required vs optional, `Field()` |
| 2 | `sessions/session-08/02_validation_error.md` | `ValidationError`, error messages, safe parsing |
| 3 | `sessions/session-08/03_serialisation.md` | `model_dump()`, `model_validate()`, `model_json_schema()` |
| 4 | `sessions/session-08/04_nested_models.md` | Nested models, `list[Model]`, real production schema |

---

## Segments

### Segment A — BaseModel and Field() (~35 min)
**File**: `01_basemodel_fields.md`

**Mental model**: Pydantic's `BaseModel` turns type hints into runtime enforcement. You define a class with typed attributes — Pydantic validates that every value matches its declared type when an instance is created. If something doesn't match, you get a clear, structured error instead of a silent wrong value or a cryptic crash three functions later.

**Analogy**: A Pydantic model is like a bank form. The form has boxes for specific types of information — Account Number must be digits, Date must be in DD/MM/YYYY format. If you fill it wrong, it's rejected immediately at the counter with a specific reason, not 3 days later when someone tries to process it.

```python
from pydantic import BaseModel, Field

class Patient(BaseModel):
    name:       str                # required — must be provided
    age:        int                # required — must be a valid integer
    weight_kg:  float | None = None  # optional — None if not provided
    conditions: list[str] = []    # optional with default empty list
    
    # Field() adds constraints and documentation
    rating: float = Field(default=5.0, ge=1.0, le=5.0, 
                          description="Patient satisfaction score")

# Creating an instance — validation happens here
p = Patient(name="Riya Sharma", age=34, weight_kg=62.5, conditions=["diabetes"])
print(p.name)       # "Riya Sharma"
print(p.weight_kg)  # 62.5
print(p.rating)     # 5.0 (default)
```

**Field constraints** — `ge` (greater than or equal), `le` (less than or equal), `gt`, `lt`, `min_length`, `max_length`:

```python
class WorkoutSet(BaseModel):
    weight_kg: float = Field(gt=0, description="Weight in kilograms — must be positive")
    reps:      int   = Field(ge=1, le=50, description="Rep count between 1 and 50")
    rpe:       float | None = Field(default=None, ge=1.0, le=10.0,
                                    description="Rate of Perceived Exertion — 1 to 10")
```

**Two ways to create a Pydantic instance:**

```python
# 1. From keyword arguments (most common)
ws = WorkoutSet(weight_kg=80.0, reps=5)

# 2. From a dict — e.g., from a parsed API response or JSON
data = {"weight_kg": 80.0, "reps": 5}
ws = WorkoutSet(**data)             # unpack dict into keyword args
ws = WorkoutSet.model_validate(data) # explicit Pydantic method — same result
```

**Misconception**: In Pydantic v2, `.dict()` and `.json()` still exist but are deprecated from v1 — they work but will be removed eventually. Always use `model_dump()` and `model_dump_json()`. Old tutorials still use v1 syntax; always check which version they're targeting.

---

### Segment B — ValidationError: when validation fails (~30 min)
**File**: `02_validation_error.md`

**Mental model**: When you pass invalid data to a Pydantic model, it raises a `ValidationError` — not a generic `TypeError` or `ValueError`, but a structured error with a list of exactly which fields failed and why. Catching this specifically lets you return clean, actionable error messages.

```python
from pydantic import BaseModel, ValidationError

class WorkoutSet(BaseModel):
    weight_kg: float
    reps:      int

# This raises ValidationError — not ValueError or TypeError
try:
    ws = WorkoutSet(weight_kg="very heavy", reps=-5)
except ValidationError as e:
    print(e)
    # 2 validation errors for WorkoutSet
    # weight_kg
    #   Input should be a valid number [type=float_parsing, ...]
    # reps
    #   Input should be greater than or equal to 1 [type=greater_than_equal, ...]
    
    # The .errors() method gives a list of dicts — machine-readable
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

**Using `model_validate` for safe parsing** — when you don't want to crash:

```python
def parse_workout_set(data: dict) -> WorkoutSet | None:
    try:
        return WorkoutSet.model_validate(data)
    except ValidationError as e:
        print(f"Invalid workout set data: {e.error_count()} errors")
        return None

# Works:
parse_workout_set({"weight_kg": 80.0, "reps": 5})   # WorkoutSet(...)
# Returns None with error printed:
parse_workout_set({"weight_kg": "heavy", "reps": 0}) # None
```

**Pydantic's type coercion** — Pydantic is lenient about some conversions:

```python
class Patient(BaseModel):
    age: int

# These all work — Pydantic coerces:
Patient(age="34")     # "34" (string) → 34 (int) ✅
Patient(age=34.0)     # 34.0 (float) → 34 (int) ✅
Patient(age="abc")    # ValidationError — can't parse "abc" as int ❌
```

**Misconception**: Pydantic v2 coerces types by default — passing `"34"` where `int` is expected produces `34`, not a `ValidationError`. This is "lax mode." If you need strict mode (no coercion), use `model_config = ConfigDict(strict=True)`. Most production code uses the default lax mode.

---

### Segment C — Serialisation: getting data out of models (~25 min)
**File**: `03_serialisation.md`

**Mental model**: Pydantic models are Python objects — you can't store them directly in a database or send them over HTTP. `model_dump()` converts to a plain Python dict. `model_dump_json()` converts to a JSON string. `model_json_schema()` gives you the JSON Schema — which is what the LLM uses for structured output.

```python
from pydantic import BaseModel

class Patient(BaseModel):
    name:       str
    age:        int
    conditions: list[str] = []

p = Patient(name="Riya", age=34, conditions=["diabetes"])

# → dict
p.model_dump()
# {"name": "Riya", "age": 34, "conditions": ["diabetes"]}

# → JSON string
p.model_dump_json()
# '{"name":"Riya","age":34,"conditions":["diabetes"]}'

# → JSON Schema (what the LLM uses to fill in the model)
Patient.model_json_schema()
# {"properties": {"name": {"title": "Name", "type": "string"}, ...}, ...}

# Exclude certain fields from the output
p.model_dump(exclude={"age"})
# {"name": "Riya", "conditions": ["diabetes"]}

# Include only certain fields
p.model_dump(include={"name", "conditions"})
# {"name": "Riya", "conditions": ["diabetes"]}
```

**From dict back to model:**

```python
data = {"name": "Riya", "age": 34}
p = Patient.model_validate(data)

# From JSON string:
json_str = '{"name": "Riya", "age": 34}'
p = Patient.model_validate_json(json_str)
```

**Misconception**: `model_dump()` returns Python types — `datetime` stays as a `datetime` object. `model_dump(mode="json")` converts everything to JSON-serialisable types (`datetime` becomes an ISO string, `UUID` becomes a string). Use `mode="json"` when you're about to pass the result to `json.dumps()` or store in a JSON column.

---

### Segment D — Nested models and list[Model] fields (~30 min)
**File**: `04_nested_models.md`

**Mental model**: Pydantic models can contain other Pydantic models as fields. A `StrengthProfile` contains a list of `EstimatedOneRM` models and a `MuscleBalance` model. Pydantic validates the entire nested structure — if any nested field is wrong, you get a `ValidationError` with the full path to the problem.

```python
from pydantic import BaseModel, Field

class EstimatedOneRM(BaseModel):
    lift_name:    str
    estimated_kg: float
    confidence:   str = Field(description="low | medium | high")

class MuscleBalance(BaseModel):
    push_pull_ratio:         float
    dominant_pattern:        str
    underdeveloped_patterns: list[str]
    recommendation:          str

class StrengthProfile(BaseModel):
    user_id:        str
    bodyweight_kg:  float | None = None
    estimated_1rms: list[EstimatedOneRM]   # list of nested models
    muscle_balance: MuscleBalance          # single nested model
    top_weaknesses: list[str]
    program_focus:  str

# Creating with nested data — all validated recursively
profile = StrengthProfile(
    user_id="ganesh",
    bodyweight_kg=80.0,
    estimated_1rms=[
        {"lift_name": "bench press", "estimated_kg": 95.0, "confidence": "high"},
        {"lift_name": "squat",       "estimated_kg": 130.0, "confidence": "medium"},
    ],
    muscle_balance={
        "push_pull_ratio": 1.3,
        "dominant_pattern": "push",
        "underdeveloped_patterns": ["rear delts", "face pulls"],
        "recommendation": "Add 2 sets of face pulls per session"
    },
    top_weaknesses=["rear delts", "hamstrings"],
    program_focus="posterior chain development"
)

# Access nested data
profile.estimated_1rms[0].lift_name    # "bench press"
profile.muscle_balance.push_pull_ratio  # 1.3

# Serialise the whole thing (recursively)
profile.model_dump()   # all nested objects become dicts
```

**Misconception**: When building a nested model from a dict (e.g., from an API response), you don't need to manually convert nested dicts to their model types. Pass the dict to `model_validate()` and Pydantic handles the conversion recursively. Manually doing `EstimatedOneRM(**item)` for each nested item is redundant.

---

## Best Practices in This Session

⚡ `model_dump()` not `.dict()` — Pydantic v2; v1 method still works but is deprecated  
⚡ Use `Field(description="...")` on every field — Pydantic includes this in `model_json_schema()`, which shapes what the LLM puts in each field during structured output  
⚡ Required fields have no default; optional fields use `field: Type | None = None`  
⚡ Catch `ValidationError` specifically — never `except Exception:` — and use `.errors()` for structured error data  
⚡ Use `model_dump(mode="json")` when the result will be JSON-serialised — keeps `datetime`, `UUID`, `Enum` as serialisable types

---

## What's Next

Session 09 — Pydantic v2: Validators + Settings. The models so far do type checking and constraint checking. Next: custom validators for business rules ("the end time must be after the start time"), computed fields (derived values that appear in serialised output), and `BaseSettings` — the single class that loads all config from `.env`.
