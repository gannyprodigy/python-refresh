# Session 00 — Setup Notes

**Date**: 2026-06-05  
**Duration**: ~15 min  
**Status**: ✅ Complete

---

## What was set up

| Item | Version |
|------|---------|
| Python | 3.12.13 (installed via `uv python install 3.12`) |
| uv | 0.11.8 |
| pydantic | 2.13.4 |
| httpx | 0.28.1 |
| tenacity | 9.1.4 |
| ipykernel | 7.2.0 |

## Commands that ran

```bash
uv python install 3.12
uv init --python 3.12 --no-workspace .
uv add pydantic pydantic-settings httpx tenacity anyio ipykernel
uv run python -m ipykernel install --user --name python-refresh --display-name "Python Refresh (Python 3.12)"
uv run python sessions/session-00/hello.py
```

## Files created

- `sessions/session-00/hello.py` — environment verification script
- `pyproject.toml` — project config (Python 3.12, all dependencies)
- `uv.lock` — locked dependency versions
- `.venv/` — virtual environment at project root

## Kernel

Registered as **"Python Refresh (Python 3.12)"** in VS Code.  
To select: open any `.ipynb` → click kernel picker top-right → choose "Python Refresh (Python 3.12)".

## One thing to note

`tenacity` has no `__version__` attribute — used `importlib.metadata.version('tenacity')` instead.

## What's next

Session 01 — Python Fluency. Five segments covering the built-in patterns that appear in every production AI file: string/dict/list methods, lambda + sorted, comprehensions, key built-ins, pathlib + datetime + defaultdict.
