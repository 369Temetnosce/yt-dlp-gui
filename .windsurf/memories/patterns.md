# Code Patterns Memory - yt-dlp GUI

## PyQt6 Patterns

### Signal/Slot Connection

```python
# Define custom signal in class
class DownloadWorker(QThread):
    progress_updated = pyqtSignal(int, str)  # percent, message
    download_finished = pyqtSignal(bool, str)  # success, path/error
    
    def run(self):
        # Emit from worker thread
        self.progress_updated.emit(50, "Downloading...")

# Connect in UI
self.worker.progress_updated.connect(self.on_progress_update)

@pyqtSlot(int, str)
def on_progress_update(self, percent: int, message: str):
    self.progress_bar.setValue(percent)
    self.status_label.setText(message)
```

### QThread Worker Pattern

```python
class DownloadWorker(QThread):
    """Worker thread for downloads - never block UI thread."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, url: str, output_path: str):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self._is_cancelled = False
    
    def run(self):
        try:
            # Long-running operation here
            result = self._do_download()
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def cancel(self):
        self._is_cancelled = True
```

## yt-dlp Subprocess Pattern

### Running yt-dlp Commands

```python
import subprocess
import json

def run_ytdlp(args: list[str]) -> subprocess.CompletedProcess:
    """Run yt-dlp with given arguments."""
    cmd = ["yt-dlp"] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )

def get_video_info(url: str) -> dict:
    """Fetch video metadata as JSON."""
    result = run_ytdlp(["-j", "--no-download", url])
    if result.returncode != 0:
        raise ValueError(f"yt-dlp error: {result.stderr}")
    return json.loads(result.stdout)
```

### Progress Parsing

```python
import re

def parse_progress(line: str) -> tuple[int, str] | None:
    """Parse yt-dlp progress output.
    
    Example line: '[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:10'
    """
    match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
    if match:
        percent = int(float(match.group(1)))
        return percent, line.strip()
    return None
```

## Error Handling Pattern

```python
class YTDLPError(Exception):
    """Base exception for yt-dlp errors."""
    pass

class URLValidationError(YTDLPError):
    """Invalid or unsupported URL."""
    pass

class DownloadError(YTDLPError):
    """Download failed."""
    pass

def download_video(url: str, output: str) -> str:
    """Download video with proper error handling."""
    try:
        result = run_ytdlp(["-o", output, url])
        if result.returncode != 0:
            if "is not a valid URL" in result.stderr:
                raise URLValidationError(f"Invalid URL: {url}")
            raise DownloadError(result.stderr)
        return output
    except subprocess.TimeoutExpired:
        raise DownloadError("Download timed out")
```

## Testing Patterns

### Mocking Subprocess

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_ytdlp():
    """Mock yt-dlp subprocess calls."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"title": "Test Video", "duration": 120}',
            stderr=""
        )
        yield mock_run

def test_get_video_info(mock_ytdlp):
    info = get_video_info("https://youtube.com/watch?v=test")
    assert info["title"] == "Test Video"
    mock_ytdlp.assert_called_once()
```

### Testing PyQt6 Signals

```python
from pytestqt.qtbot import QtBot

def test_download_emits_progress(qtbot):
    worker = DownloadWorker(url="test", output_path="/tmp")
    
    with qtbot.waitSignal(worker.progress, timeout=5000) as blocker:
        worker.start()
    
    assert blocker.args[0] >= 0  # Progress percentage
```

## Anti-Patterns to Avoid

### Never Block UI Thread

```python
# BAD - Blocks UI
def on_download_clicked(self):
    result = subprocess.run(["yt-dlp", url])  # UI freezes!
    self.show_result(result)

# GOOD - Use QThread
def on_download_clicked(self):
    self.worker = DownloadWorker(url)
    self.worker.finished.connect(self.show_result)
    self.worker.start()
```

### Never Access UI from Worker Thread

```python
# BAD - Crashes or undefined behavior
class Worker(QThread):
    def run(self):
        self.parent().progress_bar.setValue(50)  # NO!

# GOOD - Use signals
class Worker(QThread):
    progress = pyqtSignal(int)
    
    def run(self):
        self.progress.emit(50)  # UI connects to this signal
```

---

*Last updated: December 2024*
