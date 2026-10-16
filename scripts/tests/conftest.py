import sys
from pathlib import Path

# The checks are standalone stdlib scripts (run with `python -I scripts/<name>.py`), not an
# installed package: make them importable by the tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
