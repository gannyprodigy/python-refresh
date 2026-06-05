# Session 04 — Classes Part 2

**Status**: ⬜ Not Started
**Builds On**: Session 03 (classes — `__init__`, `self`, methods, `__repr__`)
**Session goal**: You build a class hierarchy with inheritance, understand exactly why `super()` is needed, and read `@classmethod` and `@property` without pausing — the patterns Pydantic and SQLModel are built on.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-04/01_inheritance_super.ipynb` | Extending a class, `super()`, method override |
| 2 | `sessions/session-04/02_classmethod_staticmethod.ipynb` | `@classmethod` and `@staticmethod` |
| 3 | `sessions/session-04/03_property_dunders.ipynb` | `@property`, `__eq__`, `__len__`, `__contains__` |
| — | `sessions/session-04/classes_2.py` | Final: inheritance, classmethods, dunders |

---

## Segments

### Segment A — Inheritance and `super()` (~45 min)
**Notebook**: `01_inheritance_super.ipynb`

**Mental model**: Inheritance lets a new class ("child") start with everything an existing class ("parent") already has — all its attributes and methods — and then add or change specific parts. The child doesn't copy the code; it *inherits* it. Any change to the parent is automatically reflected in the child.

This is why `class StrengthProfile(BaseModel)` works: you get all of `BaseModel`'s validation, serialisation, and schema generation without writing a single line of it yourself. You only define your own fields.

**Analogy**: Inheritance is like a job role. A "Senior Doctor" starts with everything in the "Doctor" job description — they can diagnose, prescribe, consult — and the Senior role adds extra responsibilities on top. You don't rewrite the Doctor role from scratch.

```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age  = age

    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

    def __repr__(self) -> str:
        return f"Person(name={self.name!r}, age={self.age})"

class Doctor(Person):
    def __init__(self, name: str, age: int, specialty: str):
        super().__init__(name, age)   # run Person's __init__ first
        self.specialty = specialty    # then add Doctor's own attribute

    def introduce(self) -> str:
        return f"{self.greet()}, specialising in {self.specialty}"

    def __repr__(self) -> str:
        return f"Doctor(name={self.name!r}, specialty={self.specialty!r})"

dr = Doctor("Priya Nair", 41, "dermatology")
dr.greet()       # "Hello, I'm Priya Nair"  ← inherited from Person, unchanged
dr.introduce()   # "Hello, I'm Priya Nair, specialising in dermatology"
dr.name          # "Priya Nair"  ← set by Person.__init__ via super()
```

**What `super()` does**: `super().__init__(name, age)` calls `Person.__init__` with the current instance. Without it, `Person.__init__` never runs, `self.name` and `self.age` are never set, and the first method call that touches them crashes.

**Misconception**: A child class that defines `__init__` *must* call `super().__init__()` if the parent's `__init__` does any setup. Skipping it silently leaves the parent's attributes undefined — no error at construction time, just an `AttributeError` the first time you access `self.name`.

```python
# This is broken — Person.__init__ never runs:
class BrokenDoctor(Person):
    def __init__(self, name: str, age: int, specialty: str):
        self.specialty = specialty   # ← self.name and self.age never set
        # super().__init__() missing!

d = BrokenDoctor("Priya", 41, "dermatology")
d.name        # AttributeError: 'BrokenDoctor' object has no attribute 'name'
```

**Overriding methods**: The child can replace a parent method by defining one with the same name. The child version takes over. The parent version is still accessible via `super()`.

```python
class Patient(Person):
    def greet(self) -> str:
        # Override Person's greet with something more specific
        return f"I'm {self.name}, I have an appointment"
```

---

### Segment B — `@classmethod` and `@staticmethod` (~35 min)
**Notebook**: `02_classmethod_staticmethod.ipynb`

**Mental model**: A regular instance method gets `self` (the instance) as its first argument. `@classmethod` gets `cls` (the class itself) instead — useful for creating instances from different input formats. `@staticmethod` gets neither — it's a utility function that lives in the class for organisation, not because it needs instance or class data.

```python
class Appointment:
    def __init__(self, patient: str, date: str, time: str):
        self.patient = patient
        self.date    = date
        self.time    = time

    @classmethod
    def from_dict(cls, data: dict) -> "Appointment":
        """Alternative constructor — build from a dict."""
        return cls(
            patient=data["patient"],
            date=data["date"],
            time=data.get("time", "09:00")
        )

    @classmethod
    def from_webhook(cls, payload: dict) -> "Appointment":
        """Build from a Twilio webhook payload."""
        return cls(
            patient=payload["From"],
            date=payload["Body"].split()[1],
            time=payload["Body"].split()[2]
        )

    @staticmethod
    def is_valid_time(time: str) -> bool:
        """No instance or class needed — pure validation function."""
        import re
        return bool(re.match(r"^\d{2}:\d{2}$", time))

# Usage:
a1 = Appointment("Riya", "2026-06-10", "14:30")                      # regular
a2 = Appointment.from_dict({"patient": "Riya", "date": "2026-06-10"}) # classmethod
Appointment.is_valid_time("14:30")  # True — staticmethod
Appointment.is_valid_time("2pm")    # False
```

This pattern is used throughout production code — Pydantic's `model_validate()` and `model_validate_json()` are both classmethods that provide alternative ways to construct models.

**Misconception**: `@classmethod` is not a factory for the specific child class — `cls` always refers to whichever class the method was called on. If a subclass inherits a `@classmethod`, calling `SubClass.from_dict(...)` creates a `SubClass` instance, not a parent class instance. This is the correct, expected behaviour.

---

### Segment C — `@property` (~20 min)
**Notebook**: `03_property_dunders.ipynb` (first half)

**Mental model**: `@property` makes a method look like an attribute — you access it without calling it (no parentheses). Use it for values that are computed from existing attributes but should feel like simple data access. In Pydantic v2, `@computed_field` (Session 09) builds on this pattern.

```python
class WorkoutSet:
    def __init__(self, weight_kg: float, reps: int):
        self.weight_kg = weight_kg
        self.reps      = reps

    @property
    def estimated_1rm(self) -> float:
        if self.reps >= 37:
            return self.weight_kg
        return self.weight_kg * (36 / (37 - self.reps))

    @property
    def volume(self) -> float:
        return self.weight_kg * self.reps

s = WorkoutSet(80.0, 5)
s.estimated_1rm   # 93.3 — no parentheses, reads like an attribute
s.volume          # 400.0 — same pattern
```

**Misconception**: `@property` values are *not* included in `model_dump()` or JSON serialisation in Pydantic v2. For that, you need `@computed_field` (Session 09). A regular `@property` is invisible to Pydantic's serialiser.

---

### Segment D — Key Dunder Methods: `__eq__`, `__len__`, `__contains__` (~25 min)
**Notebook**: `03_property_dunders.ipynb` (second half)

**Mental model**: Dunder methods (double-underscore on both sides) are Python's hooks into built-in operations. `==` calls `__eq__`. `len()` calls `__len__`. `in` calls `__contains__`. By defining these, your class works naturally with Python's operators and built-in functions.

```python
class MedicationList:
    def __init__(self, medications: list[str]):
        self._meds = [m.lower().strip() for m in medications]

    def __len__(self) -> int:
        return len(self._meds)

    def __contains__(self, item: str) -> bool:
        return item.lower().strip() in self._meds

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MedicationList):
            return False
        return sorted(self._meds) == sorted(other._meds)

    def __repr__(self) -> str:
        return f"MedicationList({self._meds!r})"

meds = MedicationList(["Metformin", "Lisinopril", "Aspirin"])

len(meds)               # 3 ← calls __len__
"metformin" in meds     # True ← calls __contains__ (case-insensitive)
"Ibuprofen" in meds     # False

other = MedicationList(["Lisinopril", "Metformin", "Aspirin"])
meds == other           # True ← calls __eq__ (order-independent)
```

The `__eq__` pattern is how you make two instances of the same class compare as "equal" based on their data — not their memory address (which is Python's default).

**Misconception**: Without defining `__eq__`, two objects with identical data are *not* equal:

```python
class Simple:
    def __init__(self, x: int):
        self.x = x

a = Simple(5)
b = Simple(5)
a == b   # False — different objects in memory, default __eq__ compares identity
```

---

## Best Practices in This Session

⚡ Always call `super().__init__()` in a child's `__init__` unless you're certain the parent has no setup — missing it is a silent bug  
⚡ `@classmethod` for alternative constructors (`from_dict`, `from_json`, `from_webhook`); `@staticmethod` for pure utilities  
⚡ Don't overuse class attributes — they're shared across ALL instances, which creates subtle bugs when mutated  
⚡ Define `__eq__` whenever you need to compare instances by their data, not their identity  
⚡ Use `@property` for read-only computed values; never use it for heavy computation (it runs every access)

---

## What's Next

Session 05 — Type Hints. You've been writing `name: str` in function signatures and class attributes. Now the full picture: union types, generics, `TypedDict`, `Literal`, and `Annotated` — the type system that Pydantic, FastAPI, and LangGraph are all built on.
