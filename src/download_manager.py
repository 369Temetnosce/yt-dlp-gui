"""Download manager for yt-dlp GUI Desktop App.

This module handles download orchestration with threading support:
- QThread-based background downloads
- Real-time progress parsing
- Signal-based UI updates
- Download cancellation
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from .ytdlp_wrapper import YTDLPWrapper
from .utils import get_file_size_mb, ensure_directory_exists

logger = logging.getLogger(__name__)


class DownloadWorker(QObject):
    """Worker class that runs download in a separate thread.
    
    Signals:
        progress_updated: Emitted with (percentage, speed, eta) during download
        download_finished: Emitted with (file_path, file_size_mb) on completion
        error_occurred: Emitted with (error_message) on failure
        log_message: Emitted with (message) for status updates
    """
    
    progress_updated = pyqtSignal(int, str, str)  # percentage, speed, eta
    download_finished = pyqtSignal(str, float)     # file_path, file_size_mb
    error_occurred = pyqtSignal(str)               # error_message
    log_message = pyqtSignal(str)                  # message
    
    def __init__(
        self,
        url: str,
        format_type: str,
        quality: str,
        output_path: str,
        filename: str
    ) -> None:
        """Initialize download worker.
        
        Args:
            url: YouTube video URL
            format_type: "video" or "audio"
            quality: Quality string like "best", "720p"
            output_path: Directory to save file
            filename: Output filename
        """
        super().__init__()
        self.url = url
        self.format_type = format_type
        self.quality = quality
        self.output_path = output_path
        self.filename = filename
        self._cancelled = False
        self._process: Optional[subprocess.Popen] = None
        self._wrapper = YTDLPWrapper()
    
    def run(self) -> None:
        """Execute the download. Called when thread starts."""
        try:
            # Ensure output directory exists
            if not ensure_directory_exists(self.output_path):
                self.error_occurred.emit(
                    "Cannot create download folder. Check permissions."
                )
                return
            
            # Build full output path
            full_path = str(Path(self.output_path) / self.filename)
            
            # Build command
            cmd = self._wrapper.build_download_command(
                self.url,
                self.format_type,
                self.quality,
                full_path
            )
            
            self.log_message.emit(f"Starting download: {self.filename}")
            logger.info(f"Download started: {self.url} -> {full_path}")
            
            # Start subprocess
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            last_percentage = 0
            error_lines = []  # Capture error output
            for line in iter(self._process.stdout.readline, ''):
                if self._cancelled:
                    self._process.terminate()
                    self.log_message.emit("Download cancelled")
                    logger.info("Download cancelled by user")
                    return
                
                line = line.strip()
                if not line:
                    continue
                
                # Capture error lines
                if "ERROR" in line or "error" in line.lower():
                    error_lines.append(line)
                    logger.error(f"yt-dlp error: {line}")
                
                # Parse progress
                progress = self._parse_progress_line(line)
                if progress:
                    percentage = progress["percentage"]
                    # Only emit if percentage changed (reduce signal spam)
                    if percentage != last_percentage:
                        self.progress_updated.emit(
                            percentage,
                            progress["speed"],
                            progress["eta"]
                        )
                        last_percentage = percentage
                
                # Log other important messages
                elif "[download]" in line.lower() or "[info]" in line.lower():
                    logger.debug(line)
            
            # Wait for process to complete
            self._process.wait()
            
            if self._cancelled:
                return
            
            if self._process.returncode == 0:
                # Success - get file size
                file_size = get_file_size_mb(full_path)
                self.progress_updated.emit(100, "", "")
                self.download_finished.emit(full_path, file_size)
                self.log_message.emit(
                    f"✓ Download complete: {self.filename} ({file_size} MB)"
                )
                logger.info(f"Download complete: {full_path} ({file_size} MB)")
            else:
                # Build error message from captured errors
                if error_lines:
                    error_msg = error_lines[-1]  # Use last error
                    # Clean up error message for user
                    if "Sign in" in error_msg or "bot" in error_msg.lower():
                        error_msg = "YouTube requires sign-in. Please sign in to YouTube in your browser and try again."
                    elif "unavailable" in error_msg.lower():
                        error_msg = "This video is unavailable or private."
                    elif "age" in error_msg.lower():
                        error_msg = "This video is age-restricted. Please sign in to YouTube in your browser."
                else:
                    error_msg = "Download failed. Please check your connection and try again."
                
                self.error_occurred.emit(error_msg)
                logger.error(f"Download failed with code {self._process.returncode}: {error_lines}")
                
        except FileNotFoundError:
            self.error_occurred.emit(
                "yt-dlp not found. Please install it first."
            )
            logger.error("yt-dlp not found during download")
        except Exception as e:
            self.error_occurred.emit(f"Download error: {str(e)}")
            logger.exception(f"Download exception: {e}")
    
    def _parse_progress_line(self, line: str) -> Optional[dict]:
        """Parse yt-dlp progress output line.
        
        Args:
            line: Output line from yt-dlp
            
        Returns:
            Dict with percentage, speed, eta or None if not a progress line
            
        Example:
            Input: "[download]  45.2% of ~48.00MiB at  2.30MiB/s ETA 00:12"
            Output: {"percentage": 45, "speed": "2.30 MiB/s", "eta": "00:12"}
        """
        if "[download]" not in line:
            return None
        
        # Pattern for progress line
        # [download]  45.2% of ~48.00MiB at  2.30MiB/s ETA 00:12
        progress_pattern = r'\[download\]\s+(\d+\.?\d*)%.*?at\s+([\d.]+\s*\w+/s).*?ETA\s+(\d+:\d+)'
        
        match = re.search(progress_pattern, line)
        if match:
            return {
                "percentage": int(float(match.group(1))),
                "speed": match.group(2),
                "eta": match.group(3)
            }
        
        # Simpler pattern for percentage only
        simple_pattern = r'\[download\]\s+(\d+\.?\d*)%'
        match = re.search(simple_pattern, line)
        if match:
            return {
                "percentage": int(float(match.group(1))),
                "speed": "",
                "eta": ""
            }
        
        return None
    
    def cancel(self) -> None:
        """Cancel the current download."""
        self._cancelled = True
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass


class DownloadManager(QObject):
    """Manages download operations with threading support.
    
    Provides a high-level interface for starting, monitoring, and
    cancelling downloads without blocking the UI.
    
    Signals:
        progress_updated: Forwarded from worker (percentage, speed, eta)
        download_finished: Forwarded from worker (file_path, file_size_mb)
        error_occurred: Forwarded from worker (error_message)
        log_message: Forwarded from worker (message)
    """
    
    progress_updated = pyqtSignal(int, str, str)
    download_finished = pyqtSignal(str, float)
    error_occurred = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QObject] = None) -> None:
        """Initialize DownloadManager."""
        super().__init__(parent)
        self._thread: Optional[QThread] = None
        self._worker: Optional[DownloadWorker] = None
        self._is_downloading = False
    
    @property
    def is_downloading(self) -> bool:
        """Check if a download is currently in progress."""
        return self._is_downloading
    
    def start_download(
        self,
        url: str,
        format_type: str,
        quality: str,
        output_path: str,
        filename: str
    ) -> bool:
        """Start a download in a background thread.
        
        Args:
            url: YouTube video URL
            format_type: "video" or "audio"
            quality: Quality string like "best", "720p"
            output_path: Directory to save file
            filename: Output filename
            
        Returns:
            True if download started, False if already downloading
        """
        if self._is_downloading:
            logger.warning("Download already in progress")
            return False
        
        self._is_downloading = True
        
        # Create thread and worker
        self._thread = QThread()
        self._worker = DownloadWorker(
            url, format_type, quality, output_path, filename
        )
        
        # Move worker to thread
        self._worker.moveToThread(self._thread)
        
        # Connect signals
        self._thread.started.connect(self._worker.run)
        
        self._worker.progress_updated.connect(self._on_progress)
        self._worker.download_finished.connect(self._on_finished)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.log_message.connect(self._on_log)
        
        # Cleanup connections
        self._worker.download_finished.connect(self._cleanup)
        self._worker.error_occurred.connect(self._cleanup)
        
        # Start thread
        self._thread.start()
        logger.info(f"Download thread started for: {url}")
        
        return True
    
    def cancel_download(self) -> None:
        """Cancel the current download."""
        if self._worker:
            self._worker.cancel()
            self.log_message.emit("Cancelling download...")
    
    def _on_progress(self, percentage: int, speed: str, eta: str) -> None:
        """Forward progress signal."""
        self.progress_updated.emit(percentage, speed, eta)
    
    def _on_finished(self, file_path: str, file_size: float) -> None:
        """Forward finished signal."""
        self.download_finished.emit(file_path, file_size)
    
    def _on_error(self, message: str) -> None:
        """Forward error signal."""
        self.error_occurred.emit(message)
    
    def _on_log(self, message: str) -> None:
        """Forward log signal."""
        self.log_message.emit(message)
    
    def _cleanup(self) -> None:
        """Clean up thread and worker after download."""
        self._is_downloading = False
        
        if self._thread:
            self._thread.quit()
            self._thread.wait(5000)  # Wait up to 5 seconds
            self._thread.deleteLater()
            self._thread = None
        
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        
        logger.debug("Download thread cleaned up")
