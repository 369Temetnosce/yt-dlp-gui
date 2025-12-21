#!/usr/bin/env python3
"""Convenience script to run yt-dlp GUI Desktop App.

Run from project root: python run.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
