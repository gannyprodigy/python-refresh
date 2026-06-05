# Python for AI Engineers — Course Design

## Overview

**Goal**: Master every Python pattern used in production AI codebases. By the end, you can read any file in a production AI project without pausing, and write the patterns from scratch.
**Timeline**: At your pace — 10+ hours/week puts you done in ~3 weeks
**Sessions**: 13 total (~30 hours of content)

---

## Teaching Philosophy

Three principles:

1. **Understand the mental model first, then build it** — before every code block, you get a clear explanation of *why this exists and what problem it solves*. No surprises in the code.

2. **Every example looks like real AI code** — no toy examples with fruits or animal classes. Every pattern is shown in a context you'll recognise the moment you open a real production file.

3. **One misconception per segment, then move on** — the single thing that trips most people up, stated once clearly. Not a lecture. One line, then back to building.

---

## Session Template

Every session, every segment:

```
Segment title
├── Mental model        ← 3–4 sentences: what this is, the problem it solves
├── Analogy             ← one comparison to something already known
├── Code — run it
├── What just happened  ← line by line, no assumptions
└── When this breaks    ← the one misconception that trips everyone up
```

No quizzes. No exercises. No comprehension checks. The session ends when the milestone runs.

Progress is tracked in `PROGRESS.md` — segments marked complete when the code works.

---

## Course Structure

| Session | Title | Hours | What Clicks |
|---------|-------|-------|-------------|
| 00 | Setup | 0.5h | Python 3.12+, uv, VS Code, Jupyter — all running |
| 01 | Python Fluency | 2.5h | Read any real production Python file without stopping |
| 02 | Functions | 2.5h | def/return/params → *args/**kwargs → closures → first-class |
| 03 | Classes Part 1 | 2.5h | `__init__`, `self`, attributes, methods, `__repr__` |
| 04 | Classes Part 2 | 2.5h | Inheritance, `super()`, `@classmethod`, dunder methods |
| 05 | Type Hints | 2h | Annotate any code; read any typed codebase instantly |
| 06 | Decorators | 2h | Read and write `@decorators`; understand `@retry`, `@tool` |
| 07 | Context Managers | 1.5h | `with` blocks, write your own, async versions |
| 08 | Pydantic v2 — Models | 3h | `BaseModel`, `Field()`, validation, nested models |
| 09 | Pydantic v2 — Validators + Settings | 2.5h | Custom validators, computed fields, `.env` config |
| 10 | Enums + TypedDict | 1.5h | `Enum`/`StrEnum` for state, `TypedDict` for graph state |
| 11 | Async / Await | 3h | `async def`, `await`, `gather`, `async with` |
| 12 | Error Handling | 2h | `try/except` depth, custom exceptions, retry pattern |

---

## What "Completion" Means

After Session 12, open any production AI codebase and read it without pausing. Every pattern — the `@retry` decorator, the `async with session:` block, the `class Config(BaseModel):` schema, the `TypedDict` state, the `StrEnum` — is familiar. You built each one from scratch.

That's the test. No quiz needed.

---

## What Comes After

This course is the prerequisite layer. The next courses build on it directly:
- LLM APIs (Anthropic SDK) — Sessions 00–03 of the AI product courses
- FastAPI + PostgreSQL — web and database layer
- LangGraph + multi-agent systems — the orchestration layer
- Production hardening — retry, logging, observability, deployment

Every concept in those courses assumes everything in this one.
