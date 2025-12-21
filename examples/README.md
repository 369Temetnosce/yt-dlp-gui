# Examples Library - yt-dlp GUI

This directory contains code examples demonstrating approved patterns for the yt-dlp GUI project.

## Directory Structure

```
examples/
├── python/        # Python/PyQt6 patterns
├── testing/       # pytest patterns
└── cli/           # yt-dlp command patterns
```

## How to Use

### In Cascade

Reference examples using @ mentions:
- `@examples/python/qthread-worker.py`
- `@examples/testing/mock-subprocess.py`

### When Implementing Features

1. Find the relevant example
2. Follow the pattern structure
3. Adapt to your specific use case

## Example Categories

### Python (`examples/python/`)
- QThread worker pattern
- Signal/slot connections
- Subprocess handling
- Error handling

### Testing (`examples/testing/`)
- Mocking subprocess
- Testing PyQt6 signals
- Fixtures for yt-dlp

### CLI (`examples/cli/`)
- Common yt-dlp commands
- Output format examples
