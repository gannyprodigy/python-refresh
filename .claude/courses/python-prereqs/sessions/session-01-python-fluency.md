# Session 01 — Python Fluency

**Status**: ⬜ Not Started
**Builds On**: Session 00 (working environment)
**Session goal**: Read any file in a production AI codebase without stopping at unfamiliar syntax.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-01/01_string_dict_list.ipynb` | The methods used in every production file |
| 2 | `sessions/session-01/02_lambda_sorted.ipynb` | Inline functions and key-based sorting |
| 3 | `sessions/session-01/03_comprehensions.ipynb` | List/dict/generator expressions |
| 4 | `sessions/session-01/04_builtins_stdlib.ipynb` | `getattr`, `isinstance`, `Path`, `datetime`, `defaultdict` |
| — | `sessions/session-01/fluency.py` | Final: all fluency patterns in one runnable script |

---

## Segments

### Segment A — String, List, Dict: the methods you'll see in every file (~40 min)
**Notebook**: `01_string_dict_list.ipynb`

**Mental model**: Python's built-in types — strings, lists, dicts — come with methods attached. You call them with dot notation. You'll use a small set of them constantly; the rest rarely. This segment covers exactly the ones that appear in production AI code.

**Analogy**: Like knowing the handful of Excel functions that appear in 90% of spreadsheets. You don't need all 400. You need VLOOKUP, IF, SUM, and a few more — and those you need to know cold.

```python
# --- STRING METHODS ---

name = "  Riya Sharma  "
name.strip()                       # "Riya Sharma" — removes leading/trailing whitespace
name.split(" ")                    # splits into a list on spaces
"2026-06-10".split("-")            # ["2026", "06", "10"]

conditions = ["diabetes", "asthma", "hypertension"]
", ".join(conditions)              # "diabetes, asthma, hypertension"
" | ".join(["80kg×5", "80kg×5"])   # "80kg×5 | 80kg×5"

"bench press".replace(" ", "_")   # "bench_press"
"  hello  ".strip()               # "hello"

# f-strings — the modern way to format strings
patient = "Riya"
age = 34
weight = 85.5
msg = f"Patient: {patient}, age {age}"        # "Patient: Riya, age 34"
msg = f"Weight: {weight:.1f}kg"               # "Weight: 85.5kg" — 1 decimal place
msg = f"Weight: {weight:.2f}kg"               # "Weight: 85.50kg" — 2 decimal places
```

```python
# --- LIST METHODS ---

meds = ["metformin", "lisinopril"]
meds.append("aspirin")             # adds one item to the end
meds.extend(["vitamin D", "B12"]) # adds all items from another list
len(meds)                          # 5

# sorted() — returns a NEW sorted list, doesn't modify the original
scores = [4.2, 4.8, 3.9, 4.5]
sorted(scores)                     # [3.9, 4.2, 4.5, 4.8] — ascending
sorted(scores, reverse=True)       # [4.8, 4.5, 4.2, 3.9] — descending
```

```python
# --- DICT METHODS — the most important ones in production code ---

record = {"name": "Riya", "age": 34, "conditions": ["diabetes"]}

# .get() — safe access with a default (NEVER crashes on missing key)
record.get("name")                  # "Riya"
record.get("weight")                # None — key missing, no crash
record.get("weight", 0)             # 0 — key missing, return default
record.get("conditions", [])        # ["diabetes"] — or [] if missing

# Direct access — crashes if key missing
record["name"]                      # "Riya" ✅
record["weight"]                    # KeyError: 'weight' ❌

# Iterating
for key, value in record.items():
    print(f"{key}: {value}")

list(record.keys())                 # ["name", "age", "conditions"]
list(record.values())               # ["Riya", 34, ["diabetes"]]
```

**Misconception**: `dict["key"]` crashes with a `KeyError` if the key doesn't exist. `dict.get("key", default)` never crashes — it returns the default. In production code, every dict that comes from an external API (JSON responses, webhook payloads, database rows) uses `.get()`. A missing key from an API silently kills the request without it.

---

### Segment B — Lambda and `sorted()` with `key=` (~35 min)
**Notebook**: `02_lambda_sorted.ipynb`

**Mental model**: A lambda is a tiny, inline function written in one expression — no `def`, no name, no `return` statement (the expression result is returned automatically). You'll almost always see it as the `key=` argument inside `sorted()`, telling it *what to sort by*.

**Analogy**: A lambda is like a sticky note with one instruction. You wouldn't frame it — it's used once, right there, and thrown away. For anything more than one expression, write a proper `def` function.

```python
# sorted() with key= — the pattern in production
workouts = [
    {"name": "bench press", "max_weight": 80},
    {"name": "squat",       "max_weight": 120},
    {"name": "deadlift",    "max_weight": 140},
]

# Sort by max_weight, highest first
sorted(workouts, key=lambda w: w["max_weight"], reverse=True)
# → [{deadlift: 140}, {squat: 120}, {bench press: 80}]

# The lambda is equivalent to writing this function:
def by_weight(w):
    return w["max_weight"]

sorted(workouts, key=by_weight, reverse=True)   # identical result
```

From real production code:
```python
# personal records dict: {"bench press": 80.0, "squat": 120.0, ...}
# Sort by weight (value), take top 10
for lift, weight in sorted(prs.items(), key=lambda x: -x[1])[:10]:
    print(f"{lift}: {weight}kg")
```

`prs.items()` produces pairs like `("bench press", 80.0)`. The lambda `lambda x: -x[1]` sorts by the second element (the weight) as a negative number — which gives descending order without `reverse=True`. `[:10]` takes the first 10 results.

```python
# Sorting a list of tuples (user_id, spend)
top_spenders = sorted(daily_spend.items(), key=lambda x: -x[1])[:5]

# Sorting strings alphabetically
sorted(["banana", "apple", "cherry"], key=lambda s: s.lower())

# Sorting by multiple criteria: first by age, then alphabetically by name
people = [{"name": "Riya", "age": 34}, {"name": "Arjun", "age": 34}]
sorted(people, key=lambda p: (p["age"], p["name"]))
```

**Misconception**: Lambda can only contain one expression — no `if/else` blocks, no multiple lines, no assignments. For anything more complex, write a regular `def` function. Lambda is not "more powerful" than def — it's just shorter for simple cases.

---

### Segment C — List, Dict, and Generator Comprehensions (~40 min)
**Notebook**: `03_comprehensions.ipynb`

**Mental model**: A comprehension builds a new list (or dict, or set) by applying an expression to every item in an iterable — in one line. It replaces the three-line for-loop-plus-append pattern with a single readable expression. Generator expressions do the same thing but produce values lazily, one at a time, instead of building the whole list in memory first.

**Analogy**: A list comprehension is like a filtering and transforming pipeline on a conveyor belt — items come in, you apply a rule and a transformation, only the ones that pass come out the other end, and the result is a new list.

```python
# --- LIST COMPREHENSION ---

# The for-loop way (3 lines):
weights = []
for s in exercise_sets:
    weights.append(s["weight_kg"])

# List comprehension — exactly the same result (1 line):
weights = [s["weight_kg"] for s in exercise_sets]

# With a filter (only include sets where weight > 0):
weights = [s["weight_kg"] for s in exercise_sets if s.get("weight_kg")]

# Transformation:
names_upper = [name.upper() for name in ["riya", "arjun", "priya"]]
# ["RIYA", "ARJUN", "PRIYA"]
```

```python
# --- DICT COMPREHENSION ---

# Build a dict from two lists
lifts = ["bench", "squat", "deadlift"]
weights = [80, 120, 140]
pr_map = {lift: weight for lift, weight in zip(lifts, weights)}
# {"bench": 80, "squat": 120, "deadlift": 140}

# Build a dict with transformation
pr_map_kg = {lift: f"{weight}kg" for lift, weight in pr_map.items()}
# {"bench": "80kg", "squat": "120kg", "deadlift": "140kg"}
```

```python
# --- GENERATOR EXPRESSION (no square brackets) ---
# Same syntax as list comprehension but with () or used directly inside a function.
# Produces values one at a time — doesn't build the full list in memory.

# Used inside join():
sets_str = " | ".join(
    f"{s['weight_kg']}kg×{s['reps']}"   # what to produce
    for s in exercise_sets               # iterate
    if s.get("weight_kg")               # filter: skip sets with no weight
)
# → "80kg×5 | 80kg×5 | 82.5kg×3"

# Used inside sum():
total_volume = sum(s["weight_kg"] * s["reps"] for s in exercise_sets)

# Used inside any():
has_heavy_set = any(s["weight_kg"] > 100 for s in exercise_sets)
```

This is real production code — from the context builder that processes workout data for the AI coach:
```python
lines = ["# Recent Workouts\n"]
for w in workouts:
    date = w.get("start_time", "")[:10]
    lines.append(f"\n[{date}] {w.get('title', 'Workout')}")
    for ex in w.get("exercises", []):
        sets_str = " | ".join(
            f"{s['weight_kg']}kg×{s['reps']}"
            for s in ex.get("sets", [])
            if s.get("weight_kg")
        )
        if sets_str:
            lines.append(f"  {ex['title']}: {sets_str}")
return "\n".join(lines)
```

Every pattern in Session 01 appears in those 10 lines: `.get()` with defaults, f-strings, generator expression inside `join()`, list filtering.

**Misconception**: A list comprehension always builds the complete list in memory before returning. A generator expression produces values one at a time — use it inside `join()`, `sum()`, `any()`, `all()` when you only need to iterate once. For large datasets (80 workouts, 1000 sets), the difference matters.

---

### Segment D — Key Built-in Functions (~25 min)
**Notebook**: `04_builtins_stdlib.ipynb` (first half)

Six built-in functions that appear in production AI code, each doing something you'd otherwise write 5 lines for:

```python
# getattr(obj, name, default) — get an attribute by its name as a string
# Used when you don't know the attribute name at write time
cache_read = getattr(usage, "cache_read_input_tokens", 0)
# If usage has .cache_read_input_tokens → returns it
# If not → returns 0. Never crashes.

# isinstance(obj, Type) — check if an object is an instance of a type
def process(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [str(v) for v in value]

# any() — True if at least one item is truthy
has_data = any(s.get("weight_kg") for s in sets)

# all() — True if ALL items are truthy
all_complete = all(step["done"] for step in workflow_steps)

# sum() — sum any iterable of numbers
total_spend = sum(user_spend.values())
total_volume = sum(s["weight_kg"] * s["reps"] for s in sets)

# zip() — pair up two lists element by element
lifts = ["bench", "squat"]
weights = [80, 120]
for lift, weight in zip(lifts, weights):
    print(f"{lift}: {weight}kg")
```

---

### Segment E — Standard Library: pathlib, datetime, defaultdict (~20 min)
**Notebook**: `04_builtins_stdlib.ipynb` (second half)

Three standard library modules used directly in production code — no installation needed.

```python
# --- pathlib.Path — object-oriented file paths ---
from pathlib import Path

# Path(__file__) is the current file's absolute path
# .parent goes up one directory, / joins paths
prompts_dir = Path(__file__).parent.parent / "prompts"
system_prompt = (prompts_dir / "coach_system.txt").read_text()

# Why not strings?
# Strings: "prompts/coach_system.txt" breaks on Windows (uses backslash)
# Path: always correct on every OS; .read_text() reads in one line

# Check existence before reading
config_file = Path(".env")
if config_file.exists():
    content = config_file.read_text()
```

```python
# --- datetime: timestamps and time arithmetic ---
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)        # current UTC time (always use UTC)
four_weeks_ago = now - timedelta(weeks=4)
yesterday = now - timedelta(days=1)
in_two_hours = now + timedelta(hours=2)

# Parse an ISO timestamp string (what APIs return)
dt = datetime.fromisoformat("2026-01-15T10:30:00+00:00")

# Format a datetime back to string
dt.isoformat()                          # "2026-01-15T10:30:00+00:00"
dt.strftime("%Y-%m-%d")                 # "2026-01-15"

# Compare
if dt >= four_weeks_ago:
    print("within last 4 weeks")
```

```python
# --- collections.defaultdict — a dict with automatic defaults ---
from collections import defaultdict

# A regular dict crashes on missing keys:
spend = {}
spend["user_123"] += 0.003   # KeyError: 'user_123'

# defaultdict provides a default value for any missing key:
spend = defaultdict(float)   # missing keys → 0.0 (float's zero value)
spend["user_123"] += 0.003   # works — creates the key with 0.0, then adds 0.003
spend["user_456"] += 0.001   # also works

# Other defaultdict types:
from collections import defaultdict
messages = defaultdict(list)    # missing keys → []
messages["user_123"].append("hello")  # no KeyError
```

**Misconception**: `datetime.now()` without `timezone.utc` returns local time — which differs by machine and location. Always use `datetime.now(timezone.utc)` for anything stored in a database or compared across systems.

---

## Best Practices in This Session

⚡ Always use `.get("key", default)` on any dict from an external source — never `dict["key"]` on untrusted data  
⚡ Use generator expressions inside `join()`, `sum()`, `any()`, `all()` — no intermediate list in memory  
⚡ `Path` over string paths — one line to read a file, works on every OS  
⚡ Always `timezone.utc` on `datetime.now()` — never store local time in a database  
⚡ `defaultdict` when you're counting or grouping — eliminates the "check if key exists, then update" pattern

---

## What's Next

Session 02 — Functions. You've seen `lambda` as an inline function. Now the full picture: how functions receive arguments flexibly with `*args` and `**kwargs`, how closures work (the pattern decorators are built on), and why functions are "objects" in Python.
