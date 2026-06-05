# Consultant Playbook — Python for AI Engineers

This playbook connects each session's Python concept to what you'll encounter in real AI consulting engagements. One insight per session — the kind you earn from production code, not tutorials.

---

## Session 00 — Setup

**The insight clients don't expect:**
Every AI project you join will have a Python environment problem waiting for you. Some team member pip-installed into the system Python, some packages conflict, nobody wrote down what version anything is. The consultant who shows up and says "let's standardise on uv — deterministic installs, locked dependencies, same environment on every machine" saves hours of debugging before writing a single line of model code. `pyproject.toml` + `uv.lock` becomes the first deliverable on any new engagement.

---

## Session 01 — Python Fluency

**The insight clients don't expect:**
Data teams spend enormous time transforming structured data — reformatting appointment records, reshaping API responses, normalising workout logs before feeding to a model. A consultant who can write a clean dict comprehension, a well-placed `dict.get()` with a sensible default, and a `sorted(..., key=lambda x: x["date"])` in seconds is visibly different from one who reaches for pandas for a 50-row transformation. Fluency in Python's built-ins is what separates "can write code" from "writes production-quality code."

---

## Session 02 — Functions

**The insight clients don't expect:**
The most reused code in every AI codebase is a small set of functions that format prompts, transform model output, and sanitise external data. Clients often have these written as giant one-off scripts. The consultant's job is to identify these patterns, name them, and extract them into clean functions with clear signatures. `*args` and `**kwargs` appear every time you write a wrapper — which you will, around every LLM call, every API client, every database query.

---

## Session 03 — Classes Part 1

**The insight clients don't expect:**
Every production AI codebase is mostly classes. Every Pydantic model is a class. Every SQLModel table is a class. Every LLM client is a class. When a client shows you their codebase and says "we just have some scripts," what they mean is "we have class definitions we don't know how to read." Understanding `__init__`, `self`, and methods is the prerequisite for reading — and debugging — any AI code you'll encounter in an engagement.

---

## Session 04 — Classes Part 2

**The insight clients don't expect:**
`class MyModel(BaseModel)` — the single most common line in any Pydantic-heavy codebase. Understanding inheritance is understanding why every model you build inherits from BaseModel, why every endpoint handler can call `model.model_dump()`, and why your model automatically validates input without you writing a single if-statement. `@classmethod` appears every time Pydantic uses `model_validate()`. That method comes from the parent. Knowing inheritance means you know why.

---

## Session 05 — Type Hints

**The insight clients don't expect:**
Type hints are the first thing a consultant looks at when entering a new codebase. Unannotated functions are expensive — you have to run code to understand what it expects, trace call sites, read comments that may be wrong. A codebase with clean type hints tells you what every function needs and returns without executing it. When you add type hints to a client's existing codebase, you will find bugs. Real ones. Hidden for months. That is always the deliverable worth mentioning in a project retrospective.

---

## Session 06 — Decorators

**The insight clients don't expect:**
Every AI framework is decorator-heavy. `@tool`, `@retry`, `@app.get`, `@field_validator`, `@limiter.limit` — these are not magic. They are functions that wrap your function. A consultant who understands decorators can read a new framework's API in minutes; one who doesn't spends an hour reading the docs to understand why their `@tool` isn't being called. The moment you write a decorator from scratch is the moment AI library APIs stop being mysterious.

---

## Session 07 — Context Managers

**The insight clients don't expect:**
Resource leaks are the most common non-obvious bug in AI production systems. A database connection not closed, an HTTP client session not cleaned up, a file handle left open. These don't crash immediately — they accumulate until the system degrades or crashes under load. The consultant who reviews production code and converts every manual open/close to a `with` block ships a quiet improvement that prevents a future incident. `async with` appears in every database call. Not understanding it means not reading any database layer.

---

## Session 08 — Pydantic v2 Models

**The insight clients don't expect:**
LLM outputs are unreliable. The model returns `"confirmed"` when you expected `"CONFIRMED"`, or returns a float when you expected a string, or omits a required field entirely. Every production AI system needs a validation layer between the LLM and the application logic. Pydantic is that layer. A consultant who can design a clean Pydantic schema — with appropriate Field descriptions that become part of the LLM's JSON schema — directly improves output quality. The LLM reads your field descriptions to understand what to return.

---

## Session 09 — Pydantic v2 Validators + Settings

**The insight clients don't expect:**
The two most common engagement findings: business logic scattered inside API route handlers, and API keys in source code. `@field_validator` and `@model_validator` centralise business rules in the model — "end_time must be after start_time" is an invariant, not a controller concern. `BaseSettings` solves the secrets problem: one class, all config, loaded from environment — nothing hardcoded. Both patterns are quick wins with visible architecture improvement that any client can point to.

---

## Session 10 — Enums + TypedDict

**The insight clients don't expect:**
Status strings are the most common silent bug in AI systems. `"Confirmed"` and `"confirmed"` and `"CONFIRMED"` all appear in the same database and cause logic failures that take hours to debug. `StrEnum` eliminates the problem: the value is controlled, comparisons are safe, the database stores the right thing. `TypedDict` is what LangGraph uses for agent state — if you're building any multi-step AI workflow, you're writing TypedDicts. The pattern appears on the first page of the LangGraph docs.

---

## Session 11 — Async / Await

**The insight clients don't expect:**
Every production AI endpoint is async — it must be, because every LLM call, every database query, every external API request is a network operation that blocks. A sync endpoint blocks the entire server while waiting for the model. An async endpoint serves other requests while the model thinks. When you show a client the difference between 3 sequential awaits taking 6 seconds and 3 gathered awaits taking 2 seconds, the case for async is obvious. The migration from sync to async is one of the highest-value refactors on a maturing AI project.

---

## Session 12 — Error Handling

**The insight clients don't expect:**
External AI services have intermittent failures by design — rate limits, transient network errors, model capacity issues. A system without retry logic fails on these constantly. A system with `except Exception: pass` hides failures entirely. The consultant's value is designing an error handling strategy: which errors are retriable (rate limit, network timeout), which are not (bad API key, invalid input), and where each category gets logged. The `@retry` decorator from tenacity, combined with a domain exception hierarchy, is the pattern that makes AI systems reliable enough to show to clients.

---

## The Thread Running Through All Sessions

Each session adds a layer. By Session 12 you can write a function that:
- Takes typed, validated input (Pydantic, Session 08–09)
- Calls an async external API (Session 11)
- Retries on transient failure (Session 12)
- Is wrapped in a decorator that logs timing (Session 06)
- Runs inside a context manager that manages the HTTP client (Session 07)
- Returns a typed, validated result (Sessions 05, 08)
- With named status values that won't get mistyped (Session 10)

That's a production-grade function. It's what AI engineers are hired to write. This course is how you get there.
