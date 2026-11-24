"""Vercel Python entry point: serves the Django app (backend/) as one WSGI function.

The root vercel.json routes /api/* here. backend/ is the Python import root, as in pytest.ini.
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application  # noqa: E402  (needs backend/ on the path first)

app = application
