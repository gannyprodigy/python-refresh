# Session 09 — Pydantic v2: Validators + Settings

**Status**: ⬜ Not Started
**Builds On**: Session 08 (Pydantic models — `BaseModel`, `Field()`, `ValidationError`)
**Session goal**: You write a `@field_validator`, a `@model_validator`, a `@computed_field`, and a `BaseSettings` class that loads all config from `.env` — the exact patterns in every production AI codebase.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-09/01_field_validator.ipynb` | Custom single-field validation |
| 2 | `sessions/session-09/02_model_validator.ipynb` | Cross-field validation rules |
| 3 | `sessions/session-09/03_computed_field.ipynb` | Derived values that appear in serialised output |
| 4 | `sessions/session-09/04_base_settings.ipynb` | All config from `.env` in one class |
| — | `sessions/session-09/pydantic_validators.py` | Final: validators + BaseSettings config |

---

## Segments

### Segment A — @field_validator: single-field custom rules (~35 min)
**Notebook**: `sessions/session-09/01_field_validator.ipynb`

**Mental model**: `Field(gt=0)` handles numeric constraints. `@field_validator` handles everything else — business rules that require logic, string format checks, cleaning and normalising incoming data. It runs after Pydantic's built-in type check, so the value is already the right type when your validator receives it.

**Analogy**: A `@field_validator` is like a receptionist double-checking a form after the clerk has confirmed all the fields are filled in. The clerk checked "is there something in the Date box?" — the receptionist checks "is the date actually in the future?"

```python
from pydantic import BaseModel, field_validator
import re

class Patient(BaseModel):
    name:      str
    phone:     str
    weight_kg: float

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace")
        return v   # return the (possibly cleaned) value

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)  # remove spaces, dashes, brackets
        if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
            raise ValueError(f"Invalid phone number format: {v!r}")
        return cleaned   # return the cleaned value

    @field_validator("weight_kg")
    @classmethod
    def weight_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Weight must be positive")
        if v > 500:
            raise ValueError("Weight value seems incorrect (>500kg)")
        return v

# Valid:
p = Patient(name="  Riya Sharma  ", phone="+91 98765 43210", weight_kg=62.5)
p.name   # "Riya Sharma" — stripped of whitespace by the validator
p.phone  # "+919876543210" — cleaned by the validator

# Invalid:
Patient(name="", phone="abc", weight_kg=-5)
# ValidationError: 3 validation errors
```

**Key details:**
- `@field_validator` must be a `@classmethod`
- The validator receives the value after type conversion — `v` is already a `str` (not raw input)
- `raise ValueError("message")` → becomes a Pydantic validation error
- Return the value (possibly modified) — returning `None` makes the field `None`

**Misconception**: `@field_validator` runs *after* the type check — if the field type is `int` and you pass `"abc"`, the type check fails first and your validator never runs. Don't use `@field_validator` as a type check replacement.

---

### Segment B — @model_validator: cross-field rules (~30 min)
**Notebook**: `sessions/session-09/02_model_validator.ipynb`

**Mental model**: `@field_validator` validates one field at a time. `@model_validator(mode="after")` runs once the entire model is constructed and gets access to all fields simultaneously. Use it for rules that involve multiple fields — "end time must be after start time", "if payment method is UPI, UPI ID is required."

```python
from pydantic import BaseModel, model_validator
from datetime import datetime

class Appointment(BaseModel):
    patient:    str
    start_time: datetime
    end_time:   datetime
    duration_min: int | None = None

    @model_validator(mode="after")
    def end_after_start(self) -> "Appointment":
        if self.end_time <= self.start_time:
            raise ValueError(
                f"end_time ({self.end_time}) must be after start_time ({self.start_time})"
            )
        return self   # must return self

class PaymentRecord(BaseModel):
    method:    str   # "cash", "card", "upi"
    amount:    float
    upi_id:    str | None = None

    @model_validator(mode="after")
    def upi_id_required_for_upi(self) -> "PaymentRecord":
        if self.method == "upi" and not self.upi_id:
            raise ValueError("upi_id is required when payment method is 'upi'")
        return self

# Works:
PaymentRecord(method="upi", amount=500.0, upi_id="riya@upi")

# Fails:
PaymentRecord(method="upi", amount=500.0)
# ValidationError: upi_id is required when payment method is 'upi'

# Works:
PaymentRecord(method="cash", amount=500.0)  # upi_id not needed for cash
```

**`mode="before"` vs `mode="after"`:**
- `mode="after"` — runs after all fields are constructed and validated. `self` is a fully-formed model instance. Use this for cross-field checks.
- `mode="before"` — runs before Pydantic processes anything. Receives the raw input dict. Use this to pre-process or reshape incoming data before validation.

**Misconception**: `@model_validator(mode="after")` must `return self`. Returning `None` or forgetting the return creates a `None` model — the calling code gets `None` instead of your model with no error message.

---

### Segment C — @computed_field: derived values in output (~20 min)
**Notebook**: `sessions/session-09/03_computed_field.ipynb`

**Mental model**: `@property` creates a computed attribute — but `@property` is invisible to Pydantic's serialiser. `@computed_field` is Pydantic's equivalent: a computed value that *does* appear in `model_dump()`, `model_dump_json()`, and the JSON Schema.

```python
from pydantic import BaseModel, computed_field

class WorkoutSet(BaseModel):
    weight_kg: float
    reps:      int

    @computed_field
    @property
    def estimated_1rm(self) -> float:
        """Brzycki formula."""
        if self.reps >= 37:
            return self.weight_kg
        return round(self.weight_kg * (36 / (37 - self.reps)), 1)

    @computed_field
    @property
    def volume(self) -> float:
        return self.weight_kg * self.reps

ws = WorkoutSet(weight_kg=80.0, reps=5)
ws.estimated_1rm   # 93.3

# The computed field appears in serialised output:
ws.model_dump()
# {"weight_kg": 80.0, "reps": 5, "estimated_1rm": 93.3, "volume": 400.0}
```

**Misconception**: `@computed_field` requires `@property` stacked underneath it — both decorators are needed. `@computed_field` alone won't work. And a plain `@property` without `@computed_field` is silently excluded from `model_dump()` — no error, just absent from the output.

---

### Segment D — BaseSettings: all config from .env (~35 min)
**Notebook**: `sessions/session-09/04_base_settings.ipynb`

**Mental model**: `BaseSettings` is a Pydantic model where field values come from environment variables (or a `.env` file) instead of function arguments. One class holds all your config. Every field is typed, has a default, and is validated on load. If a required env var is missing, you get a clear `ValidationError` at startup — not a `KeyError` three calls deep when a user triggers a feature.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Required — must be in .env; startup fails if missing
    anthropic_api_key: str
    database_url:      str

    # Optional — have sensible defaults
    app_env:      str = "development"
    debug:        bool = False
    max_retries:  int = 3
    log_level:    str = "INFO"
    redis_url:    str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

# Create one instance at module level — loaded once on import
settings = Settings()

# Use anywhere in the codebase:
print(settings.anthropic_api_key)  # from .env
print(settings.max_retries)        # 3 (default, or from .env if set)
```

Your `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
APP_ENV=production
MAX_RETRIES=5
```

**Env var names**: Pydantic matches field names case-insensitively to env var names. `anthropic_api_key` in the model matches `ANTHROPIC_API_KEY` in `.env`. No special mapping needed.

**The singleton pattern** — create settings once and import everywhere:

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str
    model_config = {"env_file": ".env"}

settings = Settings()   # created once when config.py is imported

# In any other file:
from .config import settings

async def call_llm(prompt: str) -> str:
    client = Anthropic(api_key=settings.anthropic_api_key)
    ...
```

**Misconception**: `BaseSettings` reads the `.env` file at instantiation time — when `Settings()` is called. If you create the instance at module import time (the recommended pattern), changing `.env` after the process starts has no effect until the process restarts. This is intentional — config should be stable, not dynamic.

---

## Best Practices in This Session

⚡ All config in one `BaseSettings` class — never `os.getenv()` scattered across files  
⚡ `@field_validator` must be a `@classmethod` — forgetting this gives a confusing error  
⚡ `@model_validator(mode="after")` must `return self` — returning `None` silently breaks the caller  
⚡ `@computed_field` + `@property` are both required — one without the other doesn't work as expected  
⚡ Create `settings = Settings()` at module level — import the instance, don't recreate it per function call

---

## What's Next

Session 10 — Enums + TypedDict. Two patterns you'll see in every agent codebase: `Enum` (or `StrEnum`) for status fields and task types, and `TypedDict` for agent state. Both are lightweight, both are required to read LangGraph code fluently.
