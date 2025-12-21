# Team Standards - yt-dlp GUI Project

## Development Environment

### Required Tools

- Python 3.9+
- yt-dlp (installed globally or bundled)
- ffmpeg (for video/audio merging)
- PyQt6

### Setup Steps

```bash
# Clone and setup
git clone <repo>
cd yt-dlp-gui

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/main.py

# Run tests
pytest tests/ -v
```

## Code Style

### Python Standards

- Follow PEP 8
- Use type hints for function signatures
- Docstrings for all public functions (Google style)
- Max line length: 100 characters

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `DownloadManager` |
| Functions | snake_case | `start_download()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private | _prefix | `_parse_output()` |
| Signals | past_tense | `download_finished` |

### File Organization

```python
# Standard import order
import os
import sys
from typing import Optional

# Third-party imports
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import pyqtSignal

# Local imports
from .ytdlp_wrapper import YTDLPWrapper
```

## Git Workflow

### Branch Naming

- `feature/add-playlist-support`
- `fix/progress-bar-not-updating`
- `refactor/extract-download-logic`

### Commit Messages

Format: `<type>: <description>`

```
feat: add format selection dropdown
fix: resolve UI freeze during metadata fetch
refactor: move progress parsing to separate function
test: add unit tests for URL validation
docs: update README with installation steps
```

## Testing Requirements

### What to Test

- All `ytdlp_wrapper.py` functions
- All `download_manager.py` logic
- Error handling paths
- Signal emissions

### What NOT to Test (MVP)

- PyQt6 widget rendering
- Actual yt-dlp downloads (mock subprocess)

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific file
pytest tests/test_ytdlp_wrapper.py -v
```

## Build & Release

### PyInstaller Build

```bash
# Windows
pyinstaller --onefile --windowed --name yt-dlp-gui src/main.py

# Include yt-dlp binary
pyinstaller --onefile --windowed --add-binary "yt-dlp.exe;." src/main.py
```

### Pre-Release Checklist

- [ ] All tests pass
- [ ] Version number updated
- [ ] README updated
- [ ] Build tested on target OS
- [ ] yt-dlp binary bundled (or documented as requirement)

---

*Last updated: December 2024*
