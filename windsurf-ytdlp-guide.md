# Windsurf Step-by-Step Guide: yt-dlp GUI Desktop App
## Complete Implementation Roadmap

**Document Date:** December 20, 2025  
**Target Completion:** 1 week  
**Framework:** PyQt6 (Python)  
**Bundler:** PyInstaller

---

## 🎯 Project Overview

Build a lightweight **desktop GUI application** that wraps yt-dlp's command-line functionality into a user-friendly interface. Users can:
- Paste YouTube URL → Select Format (Video/Audio) → Choose Quality → Click Download
- See real-time progress, file organization, and error handling
- No terminal knowledge required

---

## 📋 Table of Contents

1. [Development Environment Setup](#1-development-environment-setup)
2. [Project Structure](#2-project-structure)
3. [Phase 1: UI Foundation (Days 1-2)](#3-phase-1-ui-foundation-days-1-2)
4. [Phase 2: yt-dlp Integration (Days 2-3)](#4-phase-2-yt-dlp-integration-days-2-3)
5. [Phase 3: Download Logic (Days 3-4)](#5-phase-3-download-logic-days-3-4)
6. [Phase 4: Error Handling & Polish (Days 4-5)](#6-phase-4-error-handling--polish-days-4-5)
7. [Testing & Bundling (Days 5-7)](#7-testing--bundling-days-5-7)
8. [Windsurf-Specific Prompts](#8-windsurf-specific-prompts)

---

## 1. Development Environment Setup

### Step 1.1: Initialize Project

```bash
# Create project directory
mkdir yt-dlp-gui
cd yt-dlp-gui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Create project structure
mkdir src
mkdir tests
mkdir resources
mkdir build
touch requirements.txt
touch setup.py
```

### Step 1.2: Install Core Dependencies

**File: `requirements.txt`**

```txt
PyQt6==6.6.1
PyQt6-sip==13.6.0
yt-dlp==2024.12.06
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
pyinstaller==6.1.0
```

```bash
pip install -r requirements.txt
```

### Step 1.3: Verify yt-dlp Installation

```bash
# Check yt-dlp is available
yt-dlp --version

# If missing, install separately:
pip install yt-dlp

# Test basic functionality
yt-dlp --help | head -20
```

### Step 1.4: Create .windsurfrules.md (Windsurf Context File)

**File: `.windsurfrules.md`**

```markdown
# yt-dlp GUI Desktop App - Windsurf Development Rules

## Project Context
- **Framework:** PyQt6 (Python GUI)
- **Goal:** Lightweight desktop app wrapping yt-dlp CLI
- **Timeline:** 1 week MVP
- **Target Users:** Casual YouTube downloaders (non-technical)

## Architecture
- **UI Layer:** PyQt6 (main_window.py)
- **Logic Layer:** DownloadManager (download_manager.py)
- **yt-dlp Wrapper:** YTDLPWrapper (ytdlp_wrapper.py)
- **Config:** State persistence (config.json)

## Key Files Structure
```
src/
  ├── main.py                 # Application entry point
  ├── main_window.py          # UI components (PyQt6)
  ├── download_manager.py     # Download orchestration
  ├── ytdlp_wrapper.py        # yt-dlp subprocess wrapper
  ├── config_manager.py       # Settings/state persistence
  └── utils.py                # Helper functions

resources/
  ├── styles.qss              # Qt stylesheets
  └── icons/                  # Button/app icons (future)

tests/
  ├── test_ytdlp_wrapper.py
  ├── test_download_manager.py
  └── test_ui.py

requirements.txt
setup.py
```

## Code Style & Conventions
- **Language:** Python 3.9+
- **Type Hints:** Use throughout (def func(param: str) -> bool:)
- **Error Handling:** Try/except with user-friendly messages
- **Threading:** Use QThread for long operations (no UI freezing)
- **Logging:** Use logging module; save to ~/.config/yt-dlp-gui/app.log

## Must-Have Features (MVP)
1. ✅ URL input + validation (YouTube only)
2. ✅ Format selection (Video/Audio toggle)
3. ✅ Quality dropdown (Best, 720p, 480p, 360p)
4. ✅ Save location picker (default: ~/Downloads/yt-dlp/)
5. ✅ Download button → progress bar
6. ✅ Error handling with plain-English messages
7. ✅ File organization (auto-rename, prevent duplicates)
8. ✅ Open Folder button

## Windsurf-Specific Tips
- Use `@` mentions to reference files (e.g., @main_window.py)
- Use Chat mode for architecture discussions, Write mode for code generation
- Leverage Cascade for multi-file edits (e.g., simultaneous updates to UI + logic)
- Create Rules in .windsurfrules.md for persistent context
- Test with `@tests/` to validate implementations

## No-Go Areas (Won't-Have for MVP)
- ❌ Playlist support
- ❌ Subtitle downloads
- ❌ Multi-threaded downloads
- ❌ Advanced format customization
- ❌ Authentication/cookie storage
- ❌ Cloud sync / telemetry

## Release Checklist
- [ ] All MVP features functional
- [ ] Error messages user-friendly
- [ ] Cross-platform tested (macOS, Windows, Linux)
- [ ] Executable bundled (PyInstaller)
- [ ] GitHub release published
- [ ] README with setup instructions
```

---

## 2. Project Structure

Create this structure **in Windsurf** (you can use the file explorer or create files via prompts):

```
yt-dlp-gui/
├── src/
│   ├── __init__.py
│   ├── main.py                    # App entry point
│   ├── main_window.py             # PyQt6 UI
│   ├── download_manager.py        # Download orchestration
│   ├── ytdlp_wrapper.py           # yt-dlp subprocess wrapper
│   ├── config_manager.py          # State persistence
│   └── utils.py                   # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_ytdlp_wrapper.py
│   ├── test_download_manager.py
│   └── test_ui.py
├── resources/
│   └── styles.qss                 # Qt stylesheet
├── .windsurfrules.md              # Context for Windsurf
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

---

## 3. Phase 1: UI Foundation (Days 1-2)

### Step 3.1: Create Application Entry Point

**File: `src/main.py`**

Windsurf Prompt:
```
@main.py Create a PyQt6 application entry point for yt-dlp GUI Desktop App.
Use QApplication, import main_window.py, and handle startup:
- QApplication initialization
- MainWindow instantiation
- Check yt-dlp binary availability
- Show error dialog if yt-dlp missing
- sys.exit() on application close
```

### Step 3.2: Design Main Window UI

**File: `src/main_window.py`**

Windsurf Prompt:
```
@main_window.py Create PyQt6 MainWindow with the following layout:

Left Panel:
- URL Input field (QLineEdit) with placeholder "Paste YouTube URL here"
- Format Selection (QRadioButton group: Video/Audio)
- Quality Dropdown (QComboBox with options: Best, 720p, 480p, 360p)
- Save Location (QLineEdit + Browse button)

Center:
- Download Button (QPushButton, initially disabled until URL entered)
- Progress Bar (QProgressBar, hidden until download starts)
- Progress Text (QLabel showing "45% (2.3 MB/s, ~12s remaining)")

Bottom:
- Log/Status Area (QPlainTextEdit, read-only, displays download history)
- Open Folder button
- Clear Log button

Requirements:
- Use QHBoxLayout/QVBoxLayout for organization
- Set reasonable window size (800x600 minimum)
- All buttons/inputs labeled clearly
- Download button disabled by default (enable on valid URL)
- Connect signals/slots for basic interactivity
```

### Step 3.3: Create Config Manager

**File: `src/config_manager.py`**

Windsurf Prompt:
```
@config_manager.py Create ConfigManager class to persist user settings:

Methods:
- load_config() -> dict: Load from ~/.config/yt-dlp-gui/config.json
- save_config(data: dict) -> None: Save to same location
- get_default_config() -> dict: Return default settings:
  {
    "last_output_path": "~/Downloads/yt-dlp/",
    "last_format": "video",
    "last_quality": "best",
    "download_history": []
  }

Handle:
- Create config directory if missing
- JSON serialization/deserialization
- Path expansion (~/ to user home)
```

---

## 4. Phase 2: yt-dlp Integration (Days 2-3)

### Step 4.1: Create yt-dlp Wrapper

**File: `src/ytdlp_wrapper.py`**

Windsurf Prompt:
```
@ytdlp_wrapper.py Create YTDLPWrapper class to handle yt-dlp subprocess calls:

Methods:
1. validate_url(url: str) -> bool:
   - Regex check: Must contain youtube.com or youtu.be
   - Return True if valid, False otherwise

2. fetch_metadata(url: str) -> dict:
   - Run: yt-dlp --dump-json --no-warnings <URL>
   - Parse JSON response
   - Extract: title, duration, available_formats
   - Return: {
       "title": "Video Title",
       "duration": 212,  # seconds
       "formats": ["best", "720p", "480p", "360p"],
       "thumbnail_url": "https://..."
     }
   - On error: Return empty dict with error flag

3. check_yt_dlp_installed() -> bool:
   - Run: yt-dlp --version
   - Return True if exit code 0, False otherwise

4. get_yt_dlp_path() -> str:
   - Try: which yt-dlp (Unix) or where yt-dlp (Windows)
   - Return path if found, None otherwise

Requirements:
- Use subprocess.run() with capture_output=True
- Handle TimeoutError (set timeout=10 seconds)
- Don't raise exceptions; return error in response dict
- Log all calls to ~/yt-dlp-gui/debug.log
```

### Step 4.2: Create Download Manager

**File: `src/download_manager.py`**

Windsurf Prompt:
```
@download_manager.py Create DownloadManager class to orchestrate downloads:

Methods:
1. start_download(url: str, format: str, quality: str, output_path: str) -> Thread:
   - format: "video" or "audio"
   - quality: "best", "720p", "480p", "360p"
   - Build yt-dlp command based on format/quality
   - Run in QThread (return Thread object)
   - Emit progress signals (percentage, speed, eta, log_message)

2. get_yt_dlp_command(format: str, quality: str, output_path: str) -> list:
   - Video (best): ["yt-dlp", "-f", "best", "-o", output_path, url]
   - Video (720p): ["yt-dlp", "-f", "best[height<=720]", ...]
   - Audio (mp3): ["yt-dlp", "-f", "best", "-x", "--audio-format", "mp3", ...]
   - Return list of command arguments

3. parse_progress(line: str) -> dict:
   - Parse yt-dlp progress line:
     "[download] 45.2% of ~48MB at 2.3MiB/s ETA 00:12"
   - Return: {
       "percentage": 45.2,
       "speed": "2.3 MiB/s",
       "eta": "00:12"
     }

4. cancel_download() -> None:
   - Terminate current download thread

Signals (use PyQt6 signals):
- progress_updated: Emit (percentage, speed, eta)
- download_finished: Emit (file_path, file_size_mb)
- error_occurred: Emit (error_message)
- log_message: Emit (message_text)

Requirements:
- Use QThread for background execution
- Capture subprocess stdout in real-time
- Parse progress updates line-by-line
- Emit signals for UI updates (don't block main thread)
```

---

## 5. Phase 3: Download Logic (Days 3-4)

### Step 5.1: Connect UI to Download Manager

**File: `src/main_window.py` (Update)**

Windsurf Prompt:
```
@main_window.py Update MainWindow to connect signals/slots:

1. URL Input (QLineEdit):
   - On text changed: Validate URL via YTDLPWrapper
   - Enable/disable Download button based on validity
   - If valid: Fetch metadata (title, duration, formats)
   - Display metadata in window title or status bar

2. Format Selection (Video/Audio radio buttons):
   - On selection: Update Quality dropdown options
   - Video: Show [Best, 720p, 480p, 360p]
   - Audio: Show [Best Quality] only

3. Quality Dropdown:
   - Populate based on available formats from metadata
   - Gray out unavailable options

4. Browse Button (Save Location):
   - Open QFileDialog
   - Let user select folder
   - Save selected path to config

5. Download Button:
   - On click: Disable button, show spinner
   - Call download_manager.start_download()
   - Connect progress_updated signal → Update progress bar + label
   - Connect download_finished signal → Enable button, show success message
   - Connect error_occurred signal → Show error dialog, enable button

6. Log Area:
   - Append all log_message signals from download_manager
   - Show formatted: "✓ Download complete: filename.mp4 (48MB)"
   - Or: "✗ Error: Invalid URL format"

7. Open Folder Button:
   - On click: Open system file manager to output_path
   - Use: os.startfile() (Windows), subprocess.run(['open', path]) (macOS), subprocess.run(['xdg-open', path]) (Linux)

Requirements:
- Use Qt signals/slots (connect with .connect())
- Thread-safe updates (emit signals from download thread)
- Disable/enable buttons appropriately during operations
```

### Step 5.2: Implement File Organization

**File: `src/utils.py`**

Windsurf Prompt:
```
@utils.py Create utility functions for file handling:

1. sanitize_filename(title: str) -> str:
   - Remove illegal characters: < > : " / \ | ? *
   - Replace with underscore: __
   - Limit to 200 characters
   - Example: "My <Awesome> Video" → "My_Awesome_Video"

2. get_unique_filename(output_path: str, filename: str) -> str:
   - If file exists: Append (1), (2), etc.
   - Example: file.mp4 → file (1).mp4 → file (2).mp4

3. ensure_directory_exists(path: str) -> bool:
   - Create directory if missing
   - Return True on success, False on permission error

4. get_output_filename(metadata: dict, format: str) -> str:
   - Input: metadata (from fetch_metadata), format ("video"/"audio")
   - Return: "Video_Title.mp4" or "Video_Title.mp3"
   - Use sanitize_filename()

5. open_file_manager(path: str) -> None:
   - Cross-platform: Open native file manager to path
   - Windows: os.startfile(path)
   - macOS: subprocess.run(['open', path])
   - Linux: subprocess.run(['xdg-open', path])

6. get_file_size_mb(file_path: str) -> float:
   - Return file size in MB (with 1 decimal place)
   - Example: 48.5 MB
```

---

## 6. Phase 4: Error Handling & Polish (Days 4-5)

### Step 6.1: Create Error Handler

**File: `src/main_window.py` (Update)**

Windsurf Prompt:
```
@main_window.py Add error handling for common scenarios:

1. Invalid URL:
   - Message: "This URL doesn't look like a YouTube link. Please check and try again."
   - Show in red alert box

2. yt-dlp Not Installed:
   - At startup: Check if yt-dlp available
   - If missing: Show dialog with install link
   - Message: "yt-dlp is not installed. Download from: https://github.com/yt-dlp/yt-dlp/releases"
   - Allow user to proceed without download button enabled

3. Network Timeout:
   - Timeout during metadata fetch
   - Message: "Could not fetch video info. Check your internet connection and try again."
   - Retry button?

4. Format Unavailable:
   - Selected quality doesn't exist
   - Message: "The selected quality is not available for this video. Choose another."
   - Suggest available options

5. File System Error:
   - Can't write to output path (permission denied)
   - Message: "Cannot save to this location. Check folder permissions."

6. Disk Space:
   - Check free space before download
   - If < 100MB: Warn user

All errors should:
- Use QMessageBox (critical/warning based on severity)
- Display in plain English (no technical jargon)
- Suggest actionable solution
- Log to file for debugging
```

### Step 6.2: Create Logging Module

**File: `src/utils.py` (Update)**

Windsurf Prompt:
```
@utils.py Add logging setup:

1. setup_logging() -> None:
   - Create log directory: ~/.config/yt-dlp-gui/
   - Setup logger to write to: app.log
   - Log format: "[YYYY-MM-DD HH:MM:SS] [LEVEL] message"
   - Console output: INFO level
   - File output: DEBUG level

2. Log all:
   - yt-dlp command execution
   - Network requests (URL validation, metadata fetch)
   - Download start/progress/completion
   - Errors and exceptions
   - UI events (button clicks, etc.)

3. Provide log file path to user:
   - Settings menu (future feature)
   - Or: Display path in "About" dialog
```

### Step 6.3: Add Metadata Preview (Optional)

**File: `src/main_window.py` (Update)**

Windsurf Prompt (Optional for MVP):
```
@main_window.py Add metadata preview display (optional):

After URL validation + metadata fetch:
- Show video title in a label
- Show duration (HH:MM:SS format)
- Show thumbnail preview (if available)

This helps user confirm they're downloading the right video.

Can skip for MVP if time is tight.
```

---

## 7. Testing & Bundling (Days 5-7)

### Step 7.1: Create Unit Tests

**File: `tests/test_ytdlp_wrapper.py`**

Windsurf Prompt:
```
@tests/test_ytdlp_wrapper.py Create unit tests for YTDLPWrapper:

Test cases:
1. test_validate_url_valid():
   - Input: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   - Expected: True

2. test_validate_url_invalid():
   - Input: "https://example.com"
   - Expected: False

3. test_check_yt_dlp_installed():
   - Expected: True (assuming yt-dlp is installed)

4. test_fetch_metadata_valid_url():
   - Mock subprocess.run() to return valid JSON
   - Verify dict contains: title, duration, formats

5. test_fetch_metadata_invalid_url():
   - Mock subprocess.run() to return error
   - Verify error handling

Run with: pytest tests/
```

### Step 7.2: Manual Testing Checklist

Create `TESTING.md`:

```markdown
# Manual Testing Checklist

## Core Workflow
- [ ] Launch app → Main window appears
- [ ] Paste valid YouTube URL → Download button enabled
- [ ] Paste invalid URL → Download button disabled, error shown
- [ ] Select Video format → Quality dropdown shows video options
- [ ] Select Audio format → Quality dropdown shows "Best Quality" only
- [ ] Browse button → Opens file manager, saves selected path
- [ ] Click Download → Progress bar shows, button disabled
- [ ] Progress updates → Bar fills, percentage updates
- [ ] Download completes → Success message, file visible in folder
- [ ] Open Folder button → Opens system file manager to download location

## Error Cases
- [ ] No internet → Timeout error shown
- [ ] Video unavailable → Clear error message
- [ ] yt-dlp missing → Startup dialog with install link
- [ ] Disk full → Warning before download
- [ ] Can't write to path → Error message with permission tip

## Edge Cases
- [ ] Long video title → Filename truncated/sanitized
- [ ] Duplicate filename → Handled with (1), (2) suffix
- [ ] Special characters in title → Removed/replaced
- [ ] Resume partial download → Handled gracefully

## Performance
- [ ] App startup < 2 seconds
- [ ] Metadata fetch < 3 seconds
- [ ] UI responsive during download (no freezing)
- [ ] Progress bar updates smoothly

## Cross-Platform
- [ ] macOS: Test on recent macOS (10.14+)
- [ ] Windows: Test on Win10+
- [ ] Linux: Test on Ubuntu 20.04+
```

### Step 7.3: Bundle with PyInstaller

Windsurf Prompt:
```
Create setup.py and build script:

File: setup.py
- Use setuptools
- Define entry point: yt_dlp_gui = src.main:main
- Include package data (styles, icons)
- Set version: 0.1.0

File: build.sh (macOS/Linux):
#!/bin/bash
pyinstaller --onefile --windowed --name "yt-dlp-GUI" \
  --icon=resources/icon.icns \
  --add-data "resources:resources" \
  src/main.py

File: build.bat (Windows):
pyinstaller --onefile --windowed --name "yt-dlp-GUI" ^
  --icon=resources/icon.ico ^
  --add-data "resources;resources" ^
  src/main.py

Run build script:
macOS/Linux: bash build.sh
Windows: build.bat

Output: dist/yt-dlp-GUI (executable)
```

### Step 7.4: Create GitHub Release

**File: `README.md`**

Windsurf Prompt:
```
Create README.md with:

# yt-dlp GUI Desktop App

One-click YouTube video/audio downloader with graphical interface.

## Features
- ✅ Paste URL → Select format/quality → Download
- ✅ Video (MP4) or Audio (MP3)
- ✅ Real-time progress display
- ✅ Smart file organization
- ✅ User-friendly error messages
- ✅ Cross-platform (macOS, Windows, Linux)

## Installation

### Requirements
- Python 3.9+ (if running from source)
- yt-dlp (installed separately or via pip)
- ffmpeg (strongly recommended for audio encoding)

### Download Prebuilt Executable
1. Go to Releases: https://github.com/yourusername/yt-dlp-gui/releases
2. Download latest version for your OS
3. Run executable
4. Done!

### Install from Source
```bash
git clone https://github.com/yourusername/yt-dlp-gui
cd yt-dlp-gui
pip install -r requirements.txt
python src/main.py
```

## Usage
1. Open app
2. Paste YouTube URL
3. Select Video or Audio
4. Choose quality (if available)
5. Click Download
6. File appears in ~/Downloads/yt-dlp/ (or folder you chose)

## Troubleshooting

**"yt-dlp not found"**
- Install: pip install yt-dlp
- Or: Download from https://github.com/yt-dlp/yt-dlp

**"Can't download audio"**
- Install ffmpeg: https://ffmpeg.org/download.html
- Without ffmpeg, audio-only downloads may fail

**"Video unavailable"**
- Check: Is video public? (Livestreams, age-restricted may not work)
- Try: Different quality

## License
Licensed under Unlicense (same as yt-dlp)

## Attribution
Powered by yt-dlp (https://github.com/yt-dlp/yt-dlp)

## Fair Use Disclaimer
This tool is designed for personal/educational use. 
You are responsible for ensuring your downloads comply with copyright law.
```

---

## 8. Windsurf-Specific Prompts

### Prompt Template 1: Create File with Context

**Use this when starting a new module:**

```
Create @src/filename.py for the yt-dlp GUI Desktop App project.

Context:
- Project: Lightweight PyQt6 desktop downloader wrapper
- Audience: Non-technical YouTube downloaders
- Timeline: MVP in 1 week
- Framework: Python 3.9+, PyQt6

Purpose: [Your description]

Requirements:
- [Requirement 1]
- [Requirement 2]
- ...

Type hints: Required
Error handling: Use try/except, return friendly messages
Logging: Use logging module, don't print()
Threading: Use QThread for long operations
```

### Prompt Template 2: Update Existing File

```
Update @src/main_window.py to add [feature]:

Current state: [Brief description of what's already there]

Changes needed:
1. [Change 1]
2. [Change 2]
...

Requirements:
- Don't break existing code
- Keep signal/slot architecture
- Add comments for new methods
```

### Prompt Template 3: Debug Issue

```
@src/download_manager.py has an issue: [Description]

Context:
- What you expected: [Expected behavior]
- What happened: [Actual behavior]
- When: [Under what conditions]

Steps to reproduce:
1. [Step 1]
2. [Step 2]

Possible cause: [Your hypothesis]

Please review and fix.
```

### Prompt Template 4: Code Review

```
Review @src/ytdlp_wrapper.py for:
- Type safety (are all type hints correct?)
- Error handling (are all exceptions caught?)
- Performance (any blocking operations?)
- Cross-platform compatibility (Windows/macOS/Linux paths?)

Suggest improvements if needed.
```

### Prompt Template 5: Multi-File Refactor

```
I need to refactor URL validation across the codebase.

Current: URL validation happens in @main_window.py in the URL input handler.

Goal: Move to @src/ytdlp_wrapper.py as validate_url() method.

Files to update:
- @src/main_window.py: Import from ytdlp_wrapper, use in URL input slot
- @src/ytdlp_wrapper.py: Add validate_url() method
- @tests/test_ytdlp_wrapper.py: Add test_validate_url cases

Please update all three files consistently.
```

---

## 9. Daily Breakdown (Week 1 MVP)

### Day 1-2: UI Foundation
- [ ] `src/main.py` - App entry point (Windsurf Chat)
- [ ] `src/main_window.py` - UI layout (Windsurf Write)
- [ ] `src/config_manager.py` - Settings persistence (Windsurf Write)
- [ ] `resources/styles.qss` - Basic styling (Optional)

**Daily Goal:** App launches, main window visible, buttons clickable (no functionality yet)

### Day 2-3: yt-dlp Integration
- [ ] `src/ytdlp_wrapper.py` - Subprocess wrapper (Windsurf Write)
- [ ] `src/download_manager.py` - Download orchestration (Windsurf Write)
- [ ] `tests/test_ytdlp_wrapper.py` - Unit tests (Windsurf Write)

**Daily Goal:** Can validate URL, fetch metadata, identify available formats

### Day 3-4: Download Logic
- [ ] Update `src/main_window.py` - Connect signals/slots (Windsurf Write)
- [ ] `src/utils.py` - File handling utilities (Windsurf Write)
- [ ] Implement progress bar updates (Windsurf Turbo)

**Daily Goal:** Can select format/quality, start download, see progress

### Day 4-5: Error Handling & Polish
- [ ] Update `src/main_window.py` - Error dialogs (Windsurf Write)
- [ ] Update `src/utils.py` - Logging setup (Windsurf Write)
- [ ] Test error scenarios (Windsurf Chat)

**Daily Goal:** All error cases handled gracefully with user-friendly messages

### Day 5-7: Testing & Release
- [ ] `tests/` - Full test coverage (Windsurf Write)
- [ ] `README.md` - Documentation (Windsurf Write)
- [ ] `setup.py` + `build.sh/bat` - Bundling (Windsurf Write)
- [ ] Manual testing on macOS/Windows/Linux (Local)
- [ ] GitHub release (Local)

**Daily Goal:** Executable released, working on all platforms

---

## 10. Key Windsurf Features to Leverage

### Feature 1: @-Mentions for Context
```
@src/main_window.py @src/download_manager.py
I need to ensure these two files work together correctly.
[Your question or request]
```

### Feature 2: Cascade for Multi-File Edits
Use Cascade (Write Mode) when updating multiple files that depend on each other:
- Add method to `ytdlp_wrapper.py`
- Update signal connection in `main_window.py`
- Add test in `test_ytdlp_wrapper.py`
→ All in one Cascade operation

### Feature 3: Rules for Persistent Context
Create `.windsurfrules.md` (already done above) to give Windsurf project context across sessions.

### Feature 4: Chat Mode for Architecture
Use Chat mode for:
- "Should I use QThread or threading.Thread?"
- "What's the best way to handle progress updates?"
- "How do I structure error handling?"

### Feature 5: Write Mode for Implementation
Use Write mode for:
- Generate complete class definitions
- Multi-file updates (Cascade)
- Bug fixes with code changes

### Feature 6: Turbo for Quick Iterations
Use Turbo mode for:
- Small UI tweaks
- Single-method implementations
- Test generation

---

## 11. Debugging Tips in Windsurf

### When Code Breaks:

1. **Identify issue:**
   ```
   App crashes when downloading. Error:
   AttributeError: 'YTDLPWrapper' object has no attribute 'get_yt_dlp_command'
   ```

2. **Share context with Windsurf:**
   ```
   @src/main_window.py @src/download_manager.py @src/ytdlp_wrapper.py
   
   When I click Download, the app crashes with:
   [Error message and traceback]
   
   The issue is that download_manager is calling a method that doesn't exist.
   ```

3. **Windsurf will:**
   - Review referenced files
   - Identify the missing method
   - Suggest fix (add method or update call)
   - Provide corrected code

### Common Issues & Solutions:

| Issue | Solution |
|-------|----------|
| App freezes during download | Add QThread to `download_manager.py` |
| Progress bar doesn't update | Verify signals are connected in `main_window.py` |
| Config not persisting | Check `config_manager.py` save path and JSON format |
| yt-dlp command fails | Log full command in `ytdlp_wrapper.py`, test in terminal |
| File not found after download | Verify output path is correct in `utils.py` |

---

## 12. Ready to Start?

### Next Steps:

1. **Set up environment locally:**
   ```bash
   mkdir yt-dlp-gui && cd yt-dlp-gui
   python3 -m venv venv
   source venv/bin/activate
   pip install PyQt6 yt-dlp requests pytest pyinstaller
   ```

2. **Open Windsurf with this project:**
   ```bash
   windsurf yt-dlp-gui
   ```

3. **Create `.windsurfrules.md`** in project root (copy from Section 1.4)

4. **Start with Phase 1, Step 1:**
   Open Windsurf Chat and ask:
   ```
   I'm building a PyQt6 GUI wrapper for yt-dlp.
   
   First, I need @src/main.py - the application entry point.
   
   The app should:
   1. Initialize QApplication
   2. Create MainWindow
   3. Check if yt-dlp is installed
   4. Show error if missing, warn user
   5. Show main window
   
   Requirements:
   - Type hints throughout
   - Error handling
   - Logging for debugging
   - Cross-platform (macOS/Windows/Linux)
   
   Generate the complete src/main.py file.
   ```

5. **Continue through phases**, updating prompts as you go.

6. **Use Cascade** for multi-file operations (Phase 2, 3, 4).

7. **Test frequently** with `python src/main.py`.

---

## 📚 Reference Links

- **yt-dlp GitHub:** https://github.com/yt-dlp/yt-dlp
- **PyQt6 Docs:** https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **PyInstaller Docs:** https://pyinstaller.org/
- **Python Logging:** https://docs.python.org/3/library/logging.html

---

## 🎉 Success Criteria

You're done when:
- ✅ App launches in < 2 seconds
- ✅ Paste URL → Download button enabled
- ✅ Select format/quality → Works correctly
- ✅ Click Download → Progress bar shows, file downloaded
- ✅ All errors display user-friendly messages
- ✅ Works on macOS, Windows, Linux
- ✅ Executable bundled and released
- ✅ README explains how to use and install

---

**Happy coding! Use Windsurf to your advantage—leverage Cascade, Turbo, and Chat modes strategically. Good luck! 🚀**
