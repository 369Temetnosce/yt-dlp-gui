# Windsurf Prompts Library - yt-dlp GUI Desktop App

Ready-to-use prompts for each development phase. Copy-paste directly into Windsurf Chat or Write mode.

---

## 🎬 PHASE 1: UI FOUNDATION (Days 1-2)

### Prompt 1.1: Create Application Entry Point

**Mode:** Write  
**File:** `src/main.py`

```
Create @src/main.py as the application entry point for yt-dlp GUI Desktop App.

Requirements:
1. Import necessary PyQt6 modules (QApplication, sys)
2. Import MainWindow from main_window (to be created)
3. Import YTDLPWrapper from ytdlp_wrapper (to check installation)
4. Create QApplication instance
5. Check if yt-dlp binary is installed using YTDLPWrapper.check_yt_dlp_installed()
6. If yt-dlp missing:
   - Show QMessageBox.warning() with message:
     "yt-dlp is not installed. Download from: https://github.com/yt-dlp/yt-dlp/releases"
   - Allow user to dismiss
7. Create MainWindow instance
8. Show window
9. Call sys.exit(app.exec())

Code style:
- Use type hints throughout
- Add docstrings
- Use logging for debug info
- Handle all exceptions gracefully
- Cross-platform compatible

Generate the complete src/main.py file with proper error handling.
```

---

### Prompt 1.2: Design Main Window UI

**Mode:** Write  
**File:** `src/main_window.py`

```
Create @src/main_window.py with PyQt6 MainWindow and complete UI layout.

The window should be titled "yt-dlp GUI Desktop Downloader v0.1.0" and have this layout:

┌─────────────────────────────────────────────────────────┐
│ yt-dlp GUI Desktop Downloader v0.1.0                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Paste Video URL:                                       │
│ ┌───────────────────────────────────────────────────┐ │
│ │ https://www.youtube.com/watch?v=...               │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ Download Format:                                       │
│ ◉ Video (MP4)     ○ Audio (MP3)                       │
│                                                         │
│ Quality: [Best ▼]                                      │
│ (Options: Best, 720p, 480p, 360p)                     │
│                                                         │
│ Save to: /Users/me/Downloads/yt-dlp/  [Browse]        │
│                                                         │
│ ┌────────────────────────────────────────────────────┐ │
│ │            ↓ DOWNLOAD                              │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [Progress Bar - hidden until download starts]         │
│ Downloading... 45% (2.3 MB/s, ~12s remaining)        │
│                                                         │
│ ─────────────────────────────────────────────────────  │
│ Download Log:                                          │
│ ┌───────────────────────────────────────────────────┐ │
│ │ ✓ Download complete: My_Video.mp4 (48.5 MB)      │ │
│ │ ✓ Download complete: Song.mp3 (8.2 MB)           │ │
│ │                                                   │ │
│ │                                                   │ │
│ │                                                   │ │
│ └───────────────────────────────────────────────────┘ │
│                                                         │
│ [Open Folder]  [Clear Log]                            │
│                                                         │
└─────────────────────────────────────────────────────────┘

Requirements:

1. URL Input Field:
   - QLineEdit with placeholder "Paste YouTube URL here"
   - Minimum width: 500px
   - Connect to method that validates and enables/disables Download button

2. Format Selection:
   - Two QRadioButton in a QGroupBox
   - Labels: "Video (MP4)" and "Audio (MP3)"
   - Default: Video selected
   - Group all in QHBoxLayout

3. Quality Dropdown:
   - QComboBox with options: Best, 720p, 480p, 360p
   - Initially empty (populate after metadata fetch)
   - Use placeholder text: "Select quality"

4. Save Location:
   - QLineEdit (read-only) showing current path
   - Default: expanduser("~/Downloads/yt-dlp/")
   - QPushButton labeled "Browse"
   - Connect Browse to QFileDialog.getExistingDirectory()

5. Download Button:
   - QPushButton labeled "↓ DOWNLOAD"
   - Initially disabled (enable only when valid URL entered)
   - Minimum height: 44px (touch-friendly)
   - Connect to download_manager.start_download()

6. Progress Bar:
   - QProgressBar initially hidden
   - Show when download starts
   - Hide when download completes
   - Range: 0-100

7. Progress Label:
   - QLabel for "Downloading... X% (Y MB/s, ~Z remaining)"
   - Initially hidden
   - Update in real-time from progress signals

8. Log Area:
   - QPlainTextEdit (read-only)
   - Scroll bar enabled
   - Max height: 200px
   - Append messages from download_manager signals

9. Control Buttons:
   - "Open Folder" - Open file manager to save location
   - "Clear Log" - Clear log area

Window Properties:
- Minimum size: 800x600
- Icon: (can add later)
- All text fields and buttons clearly labeled
- Use QVBoxLayout and QHBoxLayout for organization

Class Structure:
- Subclass QMainWindow
- Use __init__() to create all widgets
- Create methods: _init_ui(), _create_signals(), _on_[action]()
- Include docstrings

Type hints: Required on all method signatures

Generate complete src/main_window.py with all widgets, layouts, and basic signal/slot connections.
```

---

### Prompt 1.3: Create Config Manager

**Mode:** Write  
**File:** `src/config_manager.py`

```
Create @src/config_manager.py to manage application settings persistence.

ConfigManager should:

1. Store settings in JSON file at ~/.config/yt-dlp-gui/config.json
   - Create ~/.config/yt-dlp-gui/ directory if missing
   - Handle path expansion (~ to user home)

2. Default config structure:
{
  "last_output_path": "~/Downloads/yt-dlp/",
  "last_format": "video",
  "last_quality": "best",
  "download_history": [
    {
      "url": "https://youtube.com/watch?v=xyz",
      "title": "Video Title",
      "date": "2025-12-20T14:23:00Z",
      "file_size_mb": 48.5,
      "duration_seconds": 212
    }
  ]
}

3. Public Methods:

   def load_config() -> dict:
       """Load config from file. Return default if missing."""
       
   def save_config(config: dict) -> None:
       """Save config to file."""
       
   def get_default_config() -> dict:
       """Return default config template."""
       
   def get(key: str, default: Any = None) -> Any:
       """Get config value by key."""
       
   def set(key: str, value: Any) -> None:
       """Set config value and save."""
       
   def add_download_history(title: str, url: str, file_size_mb: float, duration: int) -> None:
       """Add entry to download history. Keep only last 50."""

Requirements:
- Use pathlib.Path for cross-platform paths
- Handle JSON serialization/deserialization
- Create directory with safe permissions
- Handle missing/corrupted JSON gracefully (return defaults)
- Type hints throughout
- Docstrings on all methods
- Log operations (using logging module, not print())

Generate complete src/config_manager.py class.
```

---

## 🔌 PHASE 2: YT-DLP INTEGRATION (Days 2-3)

### Prompt 2.1: Create yt-dlp Wrapper

**Mode:** Write  
**File:** `src/ytdlp_wrapper.py`

```
Create @src/ytdlp_wrapper.py to wrap yt-dlp subprocess calls.

YTDLPWrapper class with these methods:

1. validate_url(url: str) -> bool:
   - Check if URL contains 'youtube.com' OR 'youtu.be'
   - Use regex if needed
   - Return True if valid, False otherwise
   - Example valid URLs:
     * https://www.youtube.com/watch?v=dQw4w9WgXcQ
     * https://youtu.be/dQw4w9WgXcQ
     * youtube.com/watch?v=xyz

2. check_yt_dlp_installed() -> bool:
   - Run: yt-dlp --version
   - Return True if exit code 0, False otherwise
   - Don't raise exception, log it

3. get_yt_dlp_path() -> str | None:
   - Try: which yt-dlp (Unix) or where yt-dlp (Windows)
   - Return path if found, None otherwise

4. fetch_metadata(url: str) -> dict:
   - Run: yt-dlp --dump-json --no-warnings <URL>
   - Parse JSON response
   - Extract: title, duration, available_formats (best, 720p, 480p, 360p, 480p, audio)
   - Return dict with keys: title, duration, formats, thumbnail_url
   - If error: Return {"error": "Could not fetch video info"}
   - Timeout: 10 seconds max
   - Example response:
     {
       "title": "Never Gonna Give You Up",
       "duration": 212,
       "formats": ["best", "720p", "480p", "360p"],
       "thumbnail_url": "https://..."
     }

5. build_download_command(url: str, format: str, quality: str, output_path: str) -> list:
   - Build yt-dlp command based on format (video/audio) and quality
   - Return list of arguments (no shell required)
   
   Examples:
   - Video best: ["yt-dlp", "-f", "best", "-o", output_path, url]
   - Video 720p: ["yt-dlp", "-f", "best[height<=720]", "-o", output_path, url]
   - Audio MP3: ["yt-dlp", "-f", "best", "-x", "--audio-format", "mp3", "-o", output_path, url]
   
   - output_path should include filename: /path/to/Videos/Title.mp4

Requirements:
- Use subprocess.run() with capture_output=True
- Set timeout=10 for all subprocess calls
- Don't raise exceptions; return error dict instead
- Log all operations (using logging module)
- Type hints on all methods
- Docstrings with examples
- Cross-platform compatible (Windows/macOS/Linux paths)
- Never use shell=True in subprocess

Generate complete src/ytdlp_wrapper.py class.
```

---

### Prompt 2.2: Create Download Manager

**Mode:** Write  
**File:** `src/download_manager.py`

```
Create @src/download_manager.py to orchestrate downloads with threading.

DownloadManager should inherit from QObject and use QThread for long operations.

Signals (use pyqtSignal):
- progress_updated(int percentage, str speed, str eta)  # Emitted during download
- download_finished(str file_path, float file_size_mb)  # Emitted on completion
- error_occurred(str error_message)  # Emitted on error
- log_message(str message)  # Emitted for log updates

Public Methods:

1. start_download(url: str, format: str, quality: str, output_path: str, filename: str) -> None:
   - Build yt-dlp command using YTDLPWrapper.build_download_command()
   - Start download in QThread (don't block main thread)
   - Parse real-time progress from stdout
   - Emit progress_updated signal with percentage, speed, ETA
   - Emit download_finished or error_occurred when done
   - Emit log_message with status updates

2. cancel_download() -> None:
   - Terminate current download thread
   - Emit log_message("Download cancelled")

3. _parse_progress_line(line: str) -> dict | None:
   - Parse yt-dlp progress output line
   - Example line: "[download] 45.2% of ~48MB at 2.3MiB/s ETA 00:12"
   - Return: {"percentage": 45.2, "speed": "2.3 MiB/s", "eta": "00:12"}
   - Return None if not a progress line

4. _run_download(url: str, format: str, quality: str, output_path: str, filename: str) -> None:
   - Internal method run in QThread
   - Execute subprocess with yt-dlp command
   - Read stdout line-by-line (non-blocking)
   - Parse progress and emit signals
   - Handle timeout and other errors gracefully
   - Return exit code and final status

Requirements:
- Use QThread for background execution (not blocking UI)
- Parse progress updates from subprocess stdout in real-time
- Emit signals for UI updates (thread-safe)
- All subprocess calls with timeout=300 (5 minutes max download)
- Log all actions (using logging module)
- Type hints on all methods
- Docstrings with examples
- Handle subprocess errors without crashing

Generate complete src/download_manager.py with QObject/QThread implementation.
```

---

### Prompt 2.3: Create Unit Tests

**Mode:** Write  
**Files:** `tests/test_ytdlp_wrapper.py`, `tests/test_download_manager.py`

```
Create comprehensive unit tests for YTDLPWrapper.

File: @tests/test_ytdlp_wrapper.py

Use pytest framework. Test cases:

1. test_validate_url_valid():
   - Input: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   - Assert: True

2. test_validate_url_short():
   - Input: "https://youtu.be/dQw4w9WgXcQ"
   - Assert: True

3. test_validate_url_invalid():
   - Input: "https://example.com"
   - Assert: False

4. test_validate_url_empty():
   - Input: ""
   - Assert: False

5. test_check_yt_dlp_installed():
   - Assert: True (assuming yt-dlp is installed in test environment)

6. test_get_yt_dlp_path():
   - Assert: Returns non-empty path string

7. test_build_download_command_video_best():
   - Inputs: url="...", format="video", quality="best", output_path="/tmp/video.mp4"
   - Assert: Command includes ["yt-dlp", "-f", "best", "-o", "/tmp/video.mp4", url]

8. test_build_download_command_audio():
   - Inputs: url="...", format="audio", quality="best", output_path="/tmp/audio.mp3"
   - Assert: Command includes ["-x", "--audio-format", "mp3"]

Requirements:
- Use @pytest.fixture for common setup
- Mock subprocess.run for isolated testing (don't call real yt-dlp)
- Use pytest-mock plugin if needed
- Test both success and failure paths
- Type hints on all test functions

Generate complete tests for YTDLPWrapper.
```

---

## 🎬 PHASE 3: DOWNLOAD LOGIC (Days 3-4)

### Prompt 3.1: Connect UI to Download Manager

**Mode:** Write (Use Cascade for multiple files)  
**Files:** `src/main_window.py` (update), `src/download_manager.py` (update)

```
Update @src/main_window.py to connect signals/slots with download_manager.

Changes needed:

1. Add imports:
   - from src.download_manager import DownloadManager
   - from src.ytdlp_wrapper import YTDLPWrapper

2. In MainWindow.__init__():
   - Create self.download_manager = DownloadManager()
   - Create self.ytdlp_wrapper = YTDLPWrapper()

3. URL Input Field - Add method _on_url_changed(text: str):
   - Validate URL: YTDLPWrapper.validate_url(text)
   - If valid:
     * Enable Download button
     * Fetch metadata in background (use QThread or async)
     * Update Quality dropdown with available options
     * Log: "URL valid, fetching metadata..."
   - If invalid:
     * Disable Download button
     * Clear quality dropdown
     * Log: "Invalid YouTube URL"

4. Format Selection - Add method _on_format_changed(checked: bool):
   - If Video selected: Quality dropdown shows [Best, 720p, 480p, 360p]
   - If Audio selected: Quality dropdown shows [Best Quality] only
   - Remember selection in config

5. Download Button - Add method _on_download_clicked():
   - Disable button, change text to "Downloading..."
   - Get values: url, format, quality, output_path
   - Build filename: sanitize_filename(title) + extension
   - Call: download_manager.start_download(url, format, quality, output_path, filename)
   - Connect signals:
     * download_manager.progress_updated → _on_progress_update()
     * download_manager.download_finished → _on_download_finished()
     * download_manager.error_occurred → _on_download_error()
     * download_manager.log_message → _on_log_message()

6. Progress Update - Add method _on_progress_update(percentage: int, speed: str, eta: str):
   - Update progress bar: self.progress_bar.setValue(percentage)
   - Update label: f"Downloading... {percentage}% ({speed}, ~{eta})"
   - Keep UI responsive (don't block)

7. Download Finished - Add method _on_download_finished(file_path: str, file_size_mb: float):
   - Hide progress bar
   - Enable Download button
   - Restore button text to "↓ DOWNLOAD"
   - Update log: f"✓ Download complete: {file_name} ({file_size_mb} MB)"
   - Save to download history in config
   - Highlight "Open Folder" button for user

8. Download Error - Add method _on_download_error(error_message: str):
   - Show QMessageBox.critical("Download Error", error_message)
   - Log error to file
   - Enable Download button
   - Restore button text
   - Clear URL field for retry

9. Log Message - Add method _on_log_message(message: str):
   - Append to log area: self.log_area.appendPlainText(message)

10. Open Folder Button - Add method _on_open_folder():
    - Call: open_file_manager(output_path) from utils.py
    - Use cross-platform logic (os.startfile, subprocess.run, etc.)

11. Clear Log Button - Add method _on_clear_log():
    - Clear log area text

Requirements:
- Use @pyqtSlot() decorator on slot methods
- All method names follow _on_[action]() pattern
- Type hints on all methods
- Docstrings explaining signal/slot connections
- Thread-safe signal emissions
- No blocking operations on main thread

Generate updated src/main_window.py with complete signal/slot connections.
```

---

### Prompt 3.2: Create Utility Functions

**Mode:** Write  
**File:** `src/utils.py`

```
Create @src/utils.py with file handling and utility functions.

Functions needed:

1. sanitize_filename(filename: str) -> str:
   - Remove illegal characters: < > : " / \ | ? *
   - Replace with underscore: _
   - Limit to 200 characters
   - Example: "My <Awesome> Video!" → "My_Awesome_Video_"
   - Return sanitized filename

2. get_unique_filename(output_dir: str, filename: str) -> str:
   - Check if file exists
   - If yes: Append (1), (2), etc. before extension
   - Example: file.mp4 → file (1).mp4 → file (2).mp4
   - Return unique filename

3. ensure_directory_exists(path: str) -> bool:
   - Create directory and parents if missing
   - Return True on success, False on permission error
   - Log action

4. get_output_filename(metadata: dict, format: str) -> str:
   - Input: metadata dict (from fetch_metadata) with "title" key
   - Input: format ("video" or "audio")
   - Return: "Title.mp4" or "Title.mp3"
   - Use sanitize_filename() on title

5. get_file_size_mb(file_path: str) -> float:
   - Get file size in bytes, convert to MB
   - Return with 1 decimal place
   - Example: 48.5 MB

6. open_file_manager(path: str) -> None:
   - Cross-platform: Open native file manager to path
   - Windows: os.startfile(path)
   - macOS: subprocess.run(['open', path])
   - Linux: subprocess.run(['xdg-open', path])
   - Handle errors gracefully

7. setup_logging(app_name: str = "yt-dlp-gui") -> None:
   - Create log directory: ~/.config/yt-dlp-gui/
   - Setup logger with:
     * File output: app.log (DEBUG level)
     * Console output: INFO level
   - Format: "[YYYY-MM-DD HH:MM:SS] [LEVEL] message"
   - Call this in main.py before creating app

8. get_log_file_path() -> str:
   - Return path to app.log file

Requirements:
- Use pathlib.Path for cross-platform paths
- All functions have type hints
- All functions have docstrings with examples
- Use logging module for debug info
- Handle exceptions gracefully
- Cross-platform compatible

Generate complete src/utils.py with all functions.
```

---

## 🐛 PHASE 4: ERROR HANDLING & POLISH (Days 4-5)

### Prompt 4.1: Add Error Dialogs

**Mode:** Write (Update)  
**File:** `src/main_window.py`

```
Update @src/main_window.py to add comprehensive error handling.

Add method: show_error_dialog(title: str, message: str) -> None:
- Create QMessageBox.critical() dialog
- Title: Provide clear title (e.g., "Invalid URL")
- Message: Plain English, no jargon, suggest action
- Example:
  * "This URL doesn't look like a YouTube link. Please check and try again."
  * "Could not fetch video info. Check your internet connection and try again."
  * "Cannot save to this location. Check folder permissions or choose another."
- Keep URL field visible for user to retry
- Log error to file

Add method: show_warning_dialog(title: str, message: str) -> bool:
- Create QMessageBox.warning() dialog with Yes/No buttons
- Return True if user clicks Yes, False if No
- Use for non-critical issues:
  * "yt-dlp not found at startup"
  * "Low disk space (XX MB available)"
  * "ffmpeg not installed"

Add method: show_info_dialog(title: str, message: str) -> None:
- Create QMessageBox.information() dialog
- Use for success messages:
  * "Download complete!"

Error Scenarios to Handle:

1. Invalid URL:
   - Show: "This URL doesn't look like a YouTube link. Please check and try again."
   - Disable: Download button
   - Keep: URL field visible

2. yt-dlp Not Installed (at startup):
   - In main.py, check YTDLPWrapper.check_yt_dlp_installed()
   - Show: "yt-dlp is not installed. Download from: https://github.com/yt-dlp/yt-dlp"
   - Allow: User to dismiss and continue (but Download button disabled)

3. Network Timeout (metadata fetch):
   - Show: "Could not fetch video info. Check your internet connection and try again."
   - Suggest: Retry or try different URL

4. Video Unavailable:
   - Show: "This video is not available. Check if it's public or try another."
   - Keep: URL field for user to try another link

5. Format Unavailable:
   - Show: "The selected quality is not available for this video."
   - Suggest: "Available options: Best, 720p"

6. Permission Denied (can't write to folder):
   - Show: "Cannot save to this location. Check folder permissions."
   - Suggest: Click Browse to change folder

7. Disk Space Low (< 100MB):
   - Show: "Low disk space (XX MB available). Download may fail. Continue?"
   - Allow: User to proceed or change location

8. Download Failed:
   - Show: "Download failed. Check your internet or try again."
   - Log: Full error message

Requirements:
- Use QMessageBox from PyQt6
- All messages in plain English
- Include actionable suggestions
- Log all errors to file
- Don't raise exceptions (catch and display)

Update src/main_window.py with error dialogs and error handling methods.
```

---

### Prompt 4.2: Add Logging Setup

**Mode:** Write (Update)  
**File:** `src/utils.py` and `src/main.py`

```
Update @src/utils.py to add complete logging setup.

In utils.py:

1. Add function: setup_logging() -> None:
   - Create ~/.config/yt-dlp-gui/ directory
   - Create logger named "yt-dlp-gui"
   - File handler: ~/.config/yt-dlp-gui/app.log
     * Level: DEBUG
     * Format: "[%(asctime)s] [%(levelname)s] %(message)s"
     * Timestamp format: "%Y-%m-%d %H:%M:%S"
   - Console handler:
     * Level: INFO
     * Same format
   - Set root logger level to DEBUG

2. Add function: get_logger(name: str) -> logging.Logger:
   - Return logger instance
   - Use in all modules: logger = get_logger(__name__)

3. Add function: get_log_file_path() -> str:
   - Return path to app.log

Update src/main.py:

1. At start of main():
   - Call setup_logging() from utils
   - Log: "yt-dlp GUI v0.1.0 started"

2. Log these events throughout app:
   - yt-dlp installation check (info or warning)
   - URL validation (debug)
   - Metadata fetch start/completion (info)
   - Download start/progress/completion (info)
   - All errors (error level)
   - Signal emissions (debug)

Requirements:
- Use logging module (not print())
- All files should have: logger = get_logger(__name__) at top
- Log file rotates after 10MB (optional for MVP)
- Type hints on all functions

Update src/utils.py and src/main.py with logging setup.
```

---

## 🧪 PHASE 5: TESTING & BUNDLING (Days 5-7)

### Prompt 5.1: Create README

**Mode:** Write  
**File:** `README.md`

```
Create @README.md for user documentation and installation instructions.

Content:

# yt-dlp GUI Desktop App

One-click YouTube video/audio downloader with graphical interface.

## Features
- ✅ Paste URL → Select format/quality → Download
- ✅ Download as Video (MP4) or Audio (MP3)
- ✅ Real-time download progress display
- ✅ Smart file organization (auto-rename, prevent duplicates)
- ✅ User-friendly error messages (no technical jargon)
- ✅ Cross-platform (macOS, Windows, Linux)
- ✅ Fast startup (< 2 seconds)
- ✅ Reliable (95%+ download success rate)

## Installation

### Option 1: Download Prebuilt Executable (Recommended)
1. Go to https://github.com/yourusername/yt-dlp-gui/releases
2. Download latest version for your OS:
   - macOS: yt-dlp-GUI-macos.zip
   - Windows: yt-dlp-GUI-windows.zip
   - Linux: yt-dlp-GUI-linux.zip
3. Extract and run

### Option 2: Install from Source
```bash
git clone https://github.com/yourusername/yt-dlp-gui
cd yt-dlp-gui
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python src/main.py
```

### Requirements
- **yt-dlp:** Download from https://github.com/yt-dlp/yt-dlp/releases or install: `pip install yt-dlp`
- **ffmpeg:** (Optional but recommended) Download from https://ffmpeg.org/download.html
  - Without ffmpeg, audio-only downloads may fail

## Usage

1. **Open the app**
   - Run executable or `python src/main.py`

2. **Paste YouTube URL**
   - Copy URL from browser address bar
   - Paste into "Paste Video URL" field

3. **Select Format**
   - Video (MP4): Download full video with audio
   - Audio (MP3): Extract audio only

4. **Choose Quality** (optional)
   - Video: Best, 720p, 480p, 360p
   - Audio: Best Quality (auto-selected)

5. **Download**
   - Click "↓ DOWNLOAD" button
   - Watch progress bar
   - File saves to ~/Downloads/yt-dlp/ (or your chosen folder)

6. **Find File**
   - Click "Open Folder" to jump to file location
   - Or navigate manually to ~/Downloads/yt-dlp/

## Troubleshooting

### "yt-dlp not found" error
```bash
# Install yt-dlp
pip install yt-dlp

# Or download from: https://github.com/yt-dlp/yt-dlp/releases
```

### "Can't download audio" or audio quality poor
```bash
# Install ffmpeg
# macOS (with Homebrew): brew install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
# Linux (Ubuntu): sudo apt-get install ffmpeg
```

### Download fails with "Video unavailable"
- Check: Is the video public? (Private videos can't be downloaded)
- Try: Different video or check if YouTube has blocked the request
- Note: Age-restricted videos require browser cookies (not supported in MVP)

### Can't save to selected folder
- Check: Do you have write permissions to that folder?
- Try: Choose a different folder (Documents, Desktop, etc.)
- Note: Windows 11 may restrict system folders

### App crashes or freezes
- Check: Do you have internet connection?
- Try: Restart the app
- Check: Download log file at ~/.config/yt-dlp-gui/app.log

## Fair Use & Legal Notice

This tool is designed for **personal and educational use only**. 

You are responsible for ensuring your downloads comply with:
- YouTube Terms of Service
- Copyright law in your jurisdiction
- Content creator's licensing requirements

Use responsibly. Respect copyright and creator rights.

## Credits
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)

## License
This software is licensed under the Unlicense (same as yt-dlp).

For more info, visit: http://unlicense.org/

---

**Version:** 0.1.0  
**Last Updated:** December 20, 2025  
**Status:** MVP (Feature-complete, actively maintained)
```

---

### Prompt 5.2: Create PyInstaller Build Scripts

**Mode:** Write  
**Files:** `setup.py`, `build.sh`, `build.bat`

```
Create build scripts to bundle the app into standalone executables.

File: @setup.py
```python
from setuptools import setup, find_packages

setup(
    name='yt-dlp-gui',
    version='0.1.0',
    description='One-click YouTube video/audio downloader with GUI',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/yt-dlp-gui',
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.6.1',
        'yt-dlp>=2024.12.06',
        'requests>=2.31.0',
    ],
    entry_points={
        'console_scripts': [
            'yt-dlp-gui=src.main:main',
        ],
    },
    python_requires='>=3.9',
)
```

File: @build.sh (macOS/Linux)
```bash
#!/bin/bash
# Build PyInstaller executable for macOS/Linux

echo "Building yt-dlp GUI for macOS/Linux..."

# Create venv if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Build lazy extractors for faster startup (optional but recommended)
python -c "from yt_dlp import YoutubeDL; YoutubeDL({'quiet': True}).extract_info('https://youtu.be/test', download=False)" 2>/dev/null || true

# Build executable
pyinstaller \\
    --onefile \\
    --windowed \\
    --name "yt-dlp-GUI" \\
    --add-data "resources:resources" \\
    --collect-all "PyQt6" \\
    --hidden-import="PyQt6.QtCore" \\
    --hidden-import="PyQt6.QtGui" \\
    --hidden-import="PyQt6.QtWidgets" \\
    src/main.py

echo "Build complete! Executable at: dist/yt-dlp-GUI"
echo "Run: ./dist/yt-dlp-GUI"
```

File: @build.bat (Windows)
```batch
@echo off
REM Build PyInstaller executable for Windows

echo Building yt-dlp GUI for Windows...

REM Create venv if missing
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

REM Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Build executable
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "yt-dlp-GUI" ^
    --add-data "resources;resources" ^
    --collect-all "PyQt6" ^
    --hidden-import="PyQt6.QtCore" ^
    --hidden-import="PyQt6.QtGui" ^
    --hidden-import="PyQt6.QtWidgets" ^
    src/main.py

echo Build complete! Executable at: dist\yt-dlp-GUI.exe
echo Run: dist\yt-dlp-GUI.exe
```

Requirements:
- Both scripts activate venv
- Install all dependencies
- Run PyInstaller with optimized flags
- Output: dist/yt-dlp-GUI (executable)
- Executable size: ~100-200 MB (acceptable for MVP)

Generate setup.py, build.sh, and build.bat files.
```

---

## 🎯 Quick Start Checklist

Use this to track your progress through the 1-week MVP:

### Day 1-2: UI Foundation
- [ ] Run: `mkdir yt-dlp-gui && cd yt-dlp-gui`
- [ ] Create virtual environment
- [ ] Install dependencies from requirements.txt
- [ ] Create `.windsurfrules.md` (copy from provided)
- [ ] Use Prompt 1.1 to create `src/main.py`
- [ ] Use Prompt 1.2 to create `src/main_window.py`
- [ ] Use Prompt 1.3 to create `src/config_manager.py`
- [ ] Test: `python src/main.py` → Main window should appear

### Day 2-3: yt-dlp Integration
- [ ] Use Prompt 2.1 to create `src/ytdlp_wrapper.py`
- [ ] Use Prompt 2.2 to create `src/download_manager.py`
- [ ] Use Prompt 2.3 to create `tests/test_ytdlp_wrapper.py`
- [ ] Run: `pytest tests/ -v` → All tests pass
- [ ] Test: Validate URL in app manually

### Day 3-4: Download Logic
- [ ] Use Prompt 3.1 to update main_window.py (Cascade)
- [ ] Use Prompt 3.2 to create `src/utils.py`
- [ ] Test: Download a real YouTube video
- [ ] Check: File appears in ~/Downloads/yt-dlp/

### Day 4-5: Error Handling
- [ ] Use Prompt 4.1 to add error dialogs
- [ ] Use Prompt 4.2 to add logging
- [ ] Test all error scenarios from checklist
- [ ] Verify log file at ~/.config/yt-dlp-gui/app.log

### Day 5-7: Testing & Release
- [ ] Use Prompt 5.1 to create README.md
- [ ] Use Prompt 5.2 to create build scripts
- [ ] Test on macOS/Windows/Linux (or primary OS)
- [ ] Run: `bash build.sh` (or build.bat)
- [ ] Test executable: `./dist/yt-dlp-GUI`
- [ ] Create GitHub release with download links

---

**Happy building! 🚀**
