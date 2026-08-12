r"""Helper to run pytest with the `src` layout on systems where the package isn't installed.

Usage:
  .venv\Scripts\python.exe run_tests.py -q
"""
import sys
import pytest

# Ensure the src directory is first on sys.path so `import torbot` works
sys.path.insert(0, "src")

if __name__ == "__main__":
    args = sys.argv[1:] or ["-q"]
    raise SystemExit(pytest.main(args))
