"""Bridge module — re-exports create_app from the web package."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent so web/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import create_app

__all__ = ["create_app"]
