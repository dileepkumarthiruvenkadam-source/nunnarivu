# tests/conftest.py
import sys
from pathlib import Path

# Ensure project root (the folder that contains `backend/` and `cli/`) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

