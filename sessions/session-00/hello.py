print("ready")

import pydantic
import httpx
import tenacity
from importlib.metadata import version
print(f"pydantic {pydantic.__version__}")
print(f"httpx    {httpx.__version__}")
print(f"tenacity {version('tenacity')}")
print("\nEnvironment confirmed. ✓")
