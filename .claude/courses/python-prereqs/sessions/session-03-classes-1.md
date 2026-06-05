# Session 03 — Classes Part 1

**Status**: ⬜ Not Started
**Builds On**: Session 02 (functions — especially closures and first-class functions)
**Session goal**: You define a `Patient` class from scratch with typed attributes, multiple methods, and a readable `__repr__` — and understand exactly what `self` means and why every method needs it.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-03/01_blueprint_and_instance.md` | `__init__`, `self`, attributes, creating instances |
| 2 | `sessions/session-03/02_methods.md` | Instance methods, method chaining |
| 3 | `sessions/session-03/03_repr_str.md` | `__repr__`, `__str__`, debuggability |

---

## Segments

### Segment A — Blueprint and Instance: `__init__` and `self` (~35 min)
**File**: `01_blueprint_and_instance.md`

**Mental model**: A class is a blueprint. An instance is one concrete thing built from that blueprint. You can build many instances from one blueprint — each one has its own data, but they all share the same structure and methods. In AI code, almost everything is a class: a database model is a class, a Pydantic schema is a class, an LLM client is a class, an API response is a class.

**Analogy**: A class is like a patient intake form template. The template defines which fields exist — name, date of birth, conditions. Each filled-out form is an instance — same fields, different values. The clinic can have thousands of filled forms, all using the same template.

```python
class Patient:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age  = age

# Create two instances from the same blueprint
p1 = Patient("Riya Sharma", 34)
p2 = Patient("Arjun Mehta", 52)

# Each instance has its own data
print(p1.name)   # "Riya Sharma"
print(p2.age)    # 52
print(p1.age)    # 34 — p1's age is unchanged
```

**What just happened, line by line:**
- `class Patient:` — defines the blueprint
- `def __init__(self, name, age):` — the setup method, runs automatically when you create an instance
- `self` — the instance being created. It's passed automatically by Python as the first argument
- `self.name = name` — stores the `name` argument onto *this specific instance* as an attribute
- `p1 = Patient("Riya Sharma", 34)` — creates an instance; Python calls `__init__` with `self=p1, name="Riya Sharma", age=34`

**Misconception**: Forgetting `self` as the first parameter. Every method on a class must take `self` as its first argument — Python passes the instance automatically. If you write `def __init__(name, age):`, Python passes the instance object as `name` and the string "Riya Sharma" as `age`. The error message will not mention `self` — it'll say something like "takes 2 positional arguments but 3 were given."

```python
# This is wrong — missing self
class Patient:
    def __init__(name, age):   # ❌ Python passes instance as 'name'
        self.name = name       # NameError: 'self' is not defined
```

```python
# This is correct
class Patient:
    def __init__(self, name: str, age: int):  # ✅
        self.name = name
        self.age  = age
```

---

### Segment B — Instance Methods: giving a class behaviour (~40 min)
**File**: `02_methods.md`

**Mental model**: An instance method is a function defined inside a class that operates on that specific instance's data. It always takes `self` as its first argument. Through `self`, it can read and modify the instance's attributes — and call other methods on the same instance.

```python
class Patient:
    def __init__(self, name: str, age: int, conditions: list[str]):
        self.name       = name
        self.age        = age
        self.conditions = conditions

    def is_high_risk(self) -> bool:
        return len(self.conditions) > 2 or self.age > 65

    def add_condition(self, condition: str) -> None:
        self.conditions.append(condition)

    def summary(self) -> str:
        risk = "HIGH RISK" if self.is_high_risk() else "Standard"
        return f"{self.name} ({self.age}) — {risk} — {', '.join(self.conditions)}"

p = Patient("Riya Sharma", 34, ["diabetes", "hypertension", "asthma"])

p.is_high_risk()    # True — has 3 conditions
p.add_condition("depression")
p.summary()
# "Riya Sharma (34) — HIGH RISK — diabetes, hypertension, asthma, depression"
```

Notice: `is_high_risk()` is called inside `summary()` using `self.is_high_risk()`. Methods can call other methods on the same instance through `self`.

**Building up to production-style classes:**

```python
class WorkoutSet:
    def __init__(self, weight_kg: float, reps: int, rpe: float | None = None):
        self.weight_kg = weight_kg
        self.reps      = reps
        self.rpe       = rpe

    def estimated_1rm(self) -> float:
        """Brzycki formula: weight × (36 / (37 - reps))"""
        if self.reps >= 37:
            return self.weight_kg  # formula breaks down at very high reps
        return self.weight_kg * (36 / (37 - self.reps))

    def volume(self) -> float:
        return self.weight_kg * self.reps

s = WorkoutSet(weight_kg=80.0, reps=5)
print(f"Estimated 1RM: {s.estimated_1rm():.1f}kg")  # ~93.3kg
print(f"Volume: {s.volume():.0f}kg")                # 400kg
```

**Misconception**: `self` is not a keyword — it's a convention. You *could* name it `this` or `instance`. But always name it `self`. Any deviation is a red flag in code review and will confuse every reader.

---

### Segment C — `__repr__` and `__str__` (~25 min)
**File**: `03_repr_str.md`

**Mental model**: Python has special "dunder" (double-underscore) methods that control how built-in operations work on your objects. Two of the most important: `__repr__` controls what the Python REPL and debugger show when you inspect an object; `__str__` controls what `print()` shows.

**Why this matters**: Without `__repr__`, every object you inspect in a debugger or log shows `<Patient object at 0x7f4a3b2c1d90>` — completely useless. With `__repr__`, it shows exactly what's in the object.

```python
class Patient:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age  = age

    def __repr__(self) -> str:
        # Used by debugger, REPL, logs, and as fallback for print()
        return f"Patient(name={self.name!r}, age={self.age})"

    def __str__(self) -> str:
        # Used by print() — more human-readable
        return f"{self.name} (age {self.age})"

p = Patient("Riya", 34)
print(p)         # Riya (age 34)        ← uses __str__
repr(p)          # Patient(name='Riya', age=34)  ← uses __repr__
```

The `!r` in `f"{self.name!r}"` applies `repr()` to the value — which adds quotes around strings. This makes the output copy-pasteable as valid Python.

```python
# In real production code — every Pydantic model has this automatically:
class WorkoutSet(BaseModel):   # Pydantic generates __repr__ for you
    weight_kg: float
    reps: int

ws = WorkoutSet(weight_kg=80.0, reps=5)
print(repr(ws))   # WorkoutSet(weight_kg=80.0, reps=5)
```

**Misconception**: If you define only `__repr__` and not `__str__`, Python uses `__repr__` for both `print()` and the REPL. If you define only `__str__`, the REPL falls back to the useless default address. Define `__repr__` at minimum — it's the one that matters for debugging.

---

## Best Practices in This Session

⚡ Always define `__repr__` on any class you'll ever log or debug — `<object at 0x...>` tells you nothing  
⚡ Every method takes `self` as its first parameter — forgetting it gives a confusing "too many arguments" error  
⚡ Store all instance data in `__init__` — don't create new attributes inside other methods (confusing to trace)  
⚡ Use `self.method()` to call other methods on the same instance — don't call them as bare functions  
⚡ One method, one responsibility — a method that books the appointment AND sends the confirmation AND logs the event is three methods

---

## What's Next

Session 04 — Classes Part 2. You can now build a class from scratch. Next: how one class extends another — inheritance — and why `class MyModel(BaseModel)` means "start with everything `BaseModel` does and add my fields." That's the pattern behind Pydantic, SQLModel, and every library class you'll inherit from.
