# Session 00 — Setup

**Status**: ⬜ Not Started
**Session goal**: `uv run python sessions/session-00/hello.py` prints "ready", all packages are installed, and the Jupyter kernel is registered in VS Code.

---

## What You Open

| Order | File | What it builds |
|-------|------|---------------|
| 1 | Terminal | Install Python 3.12+, uv, VS Code |
| 2 | `sessions/session-00/hello.py` | First script — confirms environment and packages |

---

## Segments

### Segment A — Install Python 3.12+ and uv (~15 min)

`uv` is the modern Python package manager — it replaces `pip`, `venv`, and `pip-compile` in one tool. Faster, deterministic, and what the industry is moving to. One command creates an isolated Python environment with locked dependencies.

Check Python first:
```bash
python3 --version   # must show 3.12.x or higher
```

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal, then verify:
```bash
uv --version   # should print something like "uv 0.5.x"
```

**Misconception**: `uv` is not a Python version manager — it's a package manager. If you don't have Python 3.12+, install it from [python.org](https://python.org) first.

---

### Segment B — Create the project environment (~10 min)

```bash
cd /Users/ganesh/Documents/GaneshFiles/Python_Refresh
uv init .
uv add pydantic pydantic-settings httpx tenacity anyio ipykernel
```

This creates a `.venv/` folder and a `pyproject.toml`. Every package the course uses is now installed.

Now register the kernel so VS Code can find it for notebooks:
```bash
uv run python -m ipykernel install --user --name python-refresh --display-name "Python Refresh (Python 3.12)"
```

Open any `.ipynb` notebook in VS Code → select kernel → pick **"Python Refresh (Python 3.12)"**.

**Misconception**: You never need to "activate" the virtual environment when using `uv`. Just prefix commands with `uv run`. uv handles the rest automatically.

---

### Segment C — Run the first script (~5 min)

Create `sessions/session-00/hello.py`:

```python
print("ready")

import pydantic
import httpx
import tenacity
print(f"pydantic {pydantic.__version__}")
print(f"httpx    {httpx.__version__}")
print(f"tenacity {tenacity.__version__}")
print("\nEnvironment confirmed. ✓")
```

Run it:
```bash
uv run python sessions/session-00/hello.py
```

All lines print without errors. That's the environment confirmed. Every session from here runs code with `uv run python <file.py>` or by copying snippets directly into the Python REPL (`uv run python`).

---

## What's Next

Session 01 — Python Fluency. Before writing any class or async function, you need the layer underneath: the string/dict/list methods, comprehensions, and built-ins that appear in every single production Python file. That's Session 01.
