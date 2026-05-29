import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_DIR / "src"

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

