# Architecture Memory - yt-dlp GUI Desktop App

## System Overview

Lightweight PyQt6 wrapper for yt-dlp (YouTube video/audio downloader) targeting casual, non-technical users.

## Layered Architecture

```
┌─────────────────────────────────────────┐
│ UI Layer (main_window.py)               │
│ - PyQt6 widgets, signals/slots          │
│ - Progress bar, log display             │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ Logic Layer (download_manager.py)       │
│ - URL validation, metadata fetching     │
│ - Download orchestration, QThread       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ Wrapper Layer (ytdlp_wrapper.py)        │
│ - Subprocess management                 │
│ - Command building, output parsing      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│ External: yt-dlp Binary + ffmpeg        │
└─────────────────────────────────────────┘
```

## Key Architectural Decisions

### Decision 1: Subprocess over Python Library
- **Date:** Project start
- **Decision:** Use yt-dlp as subprocess, not as Python library
- **Rationale:** Easier updates, same behavior as CLI, simpler error handling
- **Trade-off:** Slightly more complex output parsing

### Decision 2: QThread for Downloads
- **Date:** Project start
- **Decision:** All downloads run on QThread, not main thread
- **Rationale:** Keep UI responsive during long downloads
- **Pattern:** Use signals to communicate progress back to UI

### Decision 3: Single Window UI
- **Date:** Project start
- **Decision:** All functionality in one main window
- **Rationale:** Simple UX for non-technical users, MVP scope

## Technology Stack

- **GUI Framework:** PyQt6 6.6.1+
- **Language:** Python 3.9+
- **Downloader:** yt-dlp (subprocess)
- **Media Processing:** ffmpeg (for merging)
- **Packaging:** PyInstaller
- **Testing:** pytest

## Data Flow

1. User pastes URL → UI validates
2. Metadata fetch → Format dropdowns populated
3. Download start → QThread spawned
4. Progress parsing → Signals emitted → UI updated
5. Completion → File saved, log updated

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point |
| `src/main_window.py` | All UI components |
| `src/download_manager.py` | Threading, orchestration |
| `src/ytdlp_wrapper.py` | yt-dlp subprocess calls |
| `src/config_manager.py` | Settings persistence |

---

*Last updated: December 2024*
