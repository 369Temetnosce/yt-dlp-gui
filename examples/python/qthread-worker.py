"""
QThread Worker Pattern for yt-dlp GUI

This pattern ensures downloads run on a background thread,
keeping the UI responsive.
"""

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
import subprocess
import re


class DownloadWorker(QThread):
    """Background worker for downloading videos.
    
    Signals:
        progress_updated(int, str): Emits download percentage and status message
        download_finished(bool, str): Emits success status and file path or error
        log_message(str): Emits log messages for display
    """
    
    progress_updated = pyqtSignal(int, str)
    download_finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, url: str, output_path: str, format_id: str = "best"):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.format_id = format_id
        self._is_cancelled = False
        self._process = None
    
    def run(self):
        """Execute download in background thread."""
        try:
            cmd = [
                "yt-dlp",
                "-f", self.format_id,
                "-o", self.output_path,
                "--newline",  # Important: one progress line per update
                self.url
            ]
            
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in self._process.stdout:
                if self._is_cancelled:
                    self._process.terminate()
                    self.download_finished.emit(False, "Cancelled by user")
                    return
                
                # Parse progress
                progress = self._parse_progress(line)
                if progress:
                    percent, message = progress
                    self.progress_updated.emit(percent, message)
                
                # Log all output
                self.log_message.emit(line.strip())
            
            self._process.wait()
            
            if self._process.returncode == 0:
                self.download_finished.emit(True, self.output_path)
            else:
                self.download_finished.emit(False, f"Exit code: {self._process.returncode}")
                
        except Exception as e:
            self.download_finished.emit(False, str(e))
    
    def cancel(self):
        """Request cancellation of the download."""
        self._is_cancelled = True
        if self._process:
            self._process.terminate()
    
    def _parse_progress(self, line: str) -> tuple[int, str] | None:
        """Parse yt-dlp progress output.
        
        Example: '[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:10'
        """
        match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
        if match:
            percent = int(float(match.group(1)))
            return percent, line.strip()
        return None


# ============================================
# Usage in MainWindow
# ============================================

"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
    
    def start_download(self):
        url = self.url_input.text()
        output = self.get_output_path()
        
        self.worker = DownloadWorker(url, output)
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.download_finished.connect(self.on_finished)
        self.worker.log_message.connect(self.on_log)
        self.worker.start()
        
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
    
    def cancel_download(self):
        if self.worker:
            self.worker.cancel()
    
    @pyqtSlot(int, str)
    def on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
    
    @pyqtSlot(bool, str)
    def on_finished(self, success: bool, result: str):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            self.status_label.setText(f"Downloaded: {result}")
        else:
            self.status_label.setText(f"Error: {result}")
    
    @pyqtSlot(str)
    def on_log(self, message: str):
        self.log_text.append(message)
"""
