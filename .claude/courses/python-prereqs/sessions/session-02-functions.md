# Session 02 — Functions

**Status**: ⬜ Not Started
**Builds On**: Session 01 (Python fluency — methods, comprehensions, built-ins)
**Session goal**: You can write a function with flexible inputs, pass it to another function, and trace exactly how closures preserve scope — the pattern all decorators are built on.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | `sessions/session-02/01_def_return_params.md` | def, return, parameters, defaults |
| 2 | `sessions/session-02/02_args_kwargs.md` | *args, **kwargs, unpacking |
| 3 | `sessions/session-02/03_first_class_closures.md` | Functions as objects, closures |

---

## Segments

### Segment A — def, return, parameters, default values (~25 min)
**File**: `01_def_return_params.md`

**Mental model**: A function is a named, reusable block of code. It takes inputs (parameters), does work, and gives back an output (the return value). The `return` statement is what sends that output back to whoever called the function — without it, every function silently returns `None`.

**Analogy**: A function is like a vending machine. You put something in (parameters), it processes it, and dispenses something back (the return value). A machine that just makes noise but doesn't dispense anything — that's a function that only prints but doesn't return.

```python
def book_appointment(patient: str, date: str, time: str = "09:00") -> dict:
    return {
        "patient": patient,
        "date": date,
        "time": time,
        "status": "confirmed"
    }

# Three ways to call the same function:
book_appointment("Riya", "2026-06-10")               # time defaults to "09:00"
book_appointment("Riya", "2026-06-10", "14:30")      # positional
book_appointment(date="2026-06-10", patient="Riya")  # keyword — order doesn't matter
```

**Misconception**: `return` and `print` are not the same thing. `print()` shows something on screen — the function still returns `None`. `return` gives a value back to the caller. If you write `result = my_function()` and the function only prints, `result` is `None`. This breaks silently — no error, just wrong behaviour.

```python
# This function looks like it works — but result is None
def get_summary(patient: str) -> str:
    print(f"Summary for {patient}")  # shows on screen
    # no return statement → returns None

result = get_summary("Riya")  # prints to screen
print(result)                 # None — the caller got nothing back
```

---

### Segment B — *args and **kwargs (~35 min)
**File**: `02_args_kwargs.md`

**Mental model**: `*args` collects any number of positional arguments into a tuple. `**kwargs` collects any number of keyword arguments into a dict. Together they make functions that accept flexible, variable inputs — which is exactly how decorator wrappers work (they wrap *any* function, so they need to accept *any* arguments).

**Analogy**: `*args` is like a bag that catches everything you throw positionally. `**kwargs` is a labelled bag that catches everything thrown with a name attached.

```python
def log_call(func_name: str, *args, **kwargs) -> None:
    print(f"Calling: {func_name}")
    print(f"  positional args: {args}")     # tuple
    print(f"  keyword args:    {kwargs}")   # dict

log_call("book_appointment", "Riya", "2026-06-10", time="14:30")
# Calling: book_appointment
#   positional args: ('Riya', '2026-06-10')
#   keyword args:    {'time': '14:30'}
```

The `*` and `**` operators also work in the other direction — *unpacking*:

```python
# ** unpacks a dict into keyword arguments
params = {"patient": "Riya", "date": "2026-06-10", "time": "14:30"}
book_appointment(**params)
# equivalent to: book_appointment(patient="Riya", date="2026-06-10", time="14:30")

# * unpacks a list into positional arguments
args = ["Riya", "2026-06-10"]
book_appointment(*args)
# equivalent to: book_appointment("Riya", "2026-06-10")
```

Why this matters for production code:
```python
# A wrapper that calls any function with any arguments
def retry_call(func, *args, **kwargs):
    for attempt in range(3):
        try:
            return func(*args, **kwargs)    # unpack and forward
        except Exception:
            if attempt == 2:
                raise

# Works for any function signature:
retry_call(book_appointment, "Riya", "2026-06-10", time="14:30")
retry_call(get_patient, patient_id="p_123")
```

**Misconception**: The names `args` and `kwargs` are conventions, not Python keywords. `*data` and `**options` work identically. The `*` and `**` operators are what matter. You'll see both conventions — and sometimes `*a, **kw` — in library code.

---

### Segment C — First-class functions: passing functions as values (~40 min)
**File**: `03_first_class_closures.md` (first half)

**Mental model**: In Python, a function is an object — just like a string, a number, or a list. You can assign it to a variable, store it in a dict, pass it as an argument to another function, and return it from a function. This is called "first-class functions" and it's the foundation of decorators, callbacks, and tool registries.

**Analogy**: Like a phone number. You can write it down, give it to someone, and they can call that number later. You're not making the call yourself — you're handing over the *ability* to make the call. Functions work the same way.

```python
def square(x: int) -> int:
    return x * x

def cube(x: int) -> int:
    return x * x * x

def apply(func, value: int) -> int:
    return func(value)   # call whichever function was passed in

apply(square, 5)    # 25  — passes the square function
apply(cube, 5)      # 125 — passes the cube function

# Store functions in a dict — a "registry"
transforms = {
    "square": square,
    "cube":   cube,
}
transforms["square"](4)  # 16
```

In production AI code, tool registries look exactly like this:
```python
TOOLS = {
    "get_patient":    get_patient,
    "check_schedule": check_schedule,
    "book_slot":      book_slot,
}

# When the LLM requests a tool by name:
tool_name = "book_slot"
result = TOOLS[tool_name](**tool_args)  # calls the function by name
```

---

### Segment D — Closures: functions that remember their scope (~30 min)
**File**: `03_first_class_closures.md` (second half)

**Mental model**: A closure is a function defined inside another function that "closes over" — remembers — variables from the outer function, even after the outer function has finished running. This is exactly what a decorator does: it wraps a function and the wrapper remembers the original function as a closure variable.

**Analogy**: A closure is like a backpack. When the inner function is created, it packs the variables from its surrounding scope into a backpack. It carries that backpack wherever it goes, long after the surrounding function is gone.

```python
def make_greeter(greeting: str):
    # greeting is a variable in the outer function's scope

    def greet(name: str) -> str:
        return f"{greeting}, {name}!"  # 'greeting' is remembered here
    
    return greet  # return the inner function

say_hello   = make_greeter("Hello")
say_namaste = make_greeter("Namaste")

say_hello("Riya")     # "Hello, Riya!" — greeting is "Hello" in this closure
say_namaste("Riya")   # "Namaste, Riya!" — greeting is "Namaste" in this closure
```

`greeting` no longer exists in `make_greeter`'s scope (the function finished), but `greet` still has it in its backpack.

Now see this pattern applied to wrapping a function:
```python
def add_logging(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")   # func is closed over
        result = func(*args, **kwargs)       # func is closed over
        print(f"Done. Result: {result}")
        return result
    return wrapper  # return the wrapper function

def add(a, b):
    return a + b

logged_add = add_logging(add)
logged_add(3, 4)
# Calling add
# Done. Result: 7
```

This is exactly what a decorator does — Session 06 will just show you the `@` syntax that makes this pattern cleaner. The closure behaviour is identical.

**Misconception**: Variables in closures are looked up at call time, not at definition time. This matters in loops:

```python
# Common mistake — all functions share the same `i`
funcs = []
for i in range(3):
    funcs.append(lambda: i)   # all three lambdas close over the SAME i

[f() for f in funcs]   # [2, 2, 2] — not [0, 1, 2]

# Fix: capture the value with a default argument
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)   # each lambda gets its own copy of i

[f() for f in funcs]   # [0, 1, 2] ✅
```

---

## Best Practices in This Session

⚡ Every function that produces a value must `return` it — a function that only `print()`s is a dead end  
⚡ Use keyword arguments at call sites when a function has 3+ parameters — `book_appointment(patient="Riya", date="2026-06-10")` is readable; `book_appointment("Riya", "2026-06-10")` is not  
⚡ Never use a mutable default argument: `def f(items=[])` is a bug — all calls share the same list object  
⚡ The names `args` and `kwargs` are conventions — the `*` and `**` are what matter  
⚡ Type-annotate every function signature — it's required by Pydantic's tool registration and improves every editor and type checker

---

## What's Next

Session 03 — Classes. Functions are the foundation; classes are what holds everything together. Every Pydantic model, every database record, every LLM client — they're all classes. You'll build them from scratch, starting with `__init__` and `self`.
