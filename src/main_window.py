"""Main window UI for yt-dlp GUI Desktop App.

This module contains the PyQt6 MainWindow class with all UI components:
- URL input and validation
- Format and quality selection
- Download progress display
- Log area
- Error dialogs
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QProgressBar,
    QPlainTextEdit,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFrame,
    QSizePolicy,
)

from .config_manager import ConfigManager
from .download_manager import DownloadManager
from .ytdlp_wrapper import YTDLPWrapper
from .utils import (
    get_output_filename,
    get_unique_filename,
    format_duration,
    open_file_manager,
    check_disk_space,
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for yt-dlp GUI.
    
    Provides the complete user interface for downloading YouTube videos
    and audio with real-time progress feedback.
    """
    
    APP_TITLE = "yt-dlp GUI Desktop Downloader v0.1.0"
    MIN_WIDTH = 700
    MIN_HEIGHT = 550
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        # Initialize managers
        self.config = ConfigManager()
        self.download_manager = DownloadManager(self)
        self.ytdlp_wrapper = YTDLPWrapper()
        
        # State
        self._current_metadata: Optional[dict] = None
        self._metadata_fetch_timer: Optional[QTimer] = None
        
        # Setup UI
        self._init_ui()
        self._connect_signals()
        self._load_settings()
        
        # Check yt-dlp installation
        self._check_dependencies()
        
        logger.info("MainWindow initialized")
    
    def _init_ui(self) -> None:
        """Initialize all UI components."""
        self.setWindowTitle(self.APP_TITLE)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # URL Input Section
        main_layout.addWidget(self._create_url_section())
        
        # Format and Quality Section
        main_layout.addWidget(self._create_format_section())
        
        # Save Location Section
        main_layout.addWidget(self._create_save_section())
        
        # Download Button
        main_layout.addWidget(self._create_download_button())
        
        # Progress Section
        main_layout.addWidget(self._create_progress_section())
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Log Section
        main_layout.addWidget(self._create_log_section())
        
        # Control Buttons
        main_layout.addWidget(self._create_control_buttons())
    
    def _create_url_section(self) -> QWidget:
        """Create URL input section."""
        group = QGroupBox("Video URL")
        layout = QVBoxLayout(group)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here (e.g., https://www.youtube.com/watch?v=...)")
        self.url_input.setMinimumHeight(36)
        font = self.url_input.font()
        font.setPointSize(11)
        self.url_input.setFont(font)
        layout.addWidget(self.url_input)
        
        # Video info label (shows title after metadata fetch)
        self.video_info_label = QLabel("")
        self.video_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.video_info_label.setWordWrap(True)
        self.video_info_label.hide()
        layout.addWidget(self.video_info_label)
        
        return group
    
    def _create_format_section(self) -> QWidget:
        """Create format and quality selection section."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Format selection
        format_group = QGroupBox("Download Format")
        format_layout = QHBoxLayout(format_group)
        
        self.format_button_group = QButtonGroup(self)
        
        self.video_radio = QRadioButton("Video (MP4)")
        self.video_radio.setChecked(True)
        self.format_button_group.addButton(self.video_radio)
        format_layout.addWidget(self.video_radio)
        
        self.audio_radio = QRadioButton("Audio (MP3)")
        self.format_button_group.addButton(self.audio_radio)
        format_layout.addWidget(self.audio_radio)
        
        format_layout.addStretch()
        layout.addWidget(format_group)
        
        # Quality selection
        quality_group = QGroupBox("Quality")
        quality_layout = QHBoxLayout(quality_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setMinimumWidth(120)
        self.quality_combo.addItems(["Best", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        
        layout.addWidget(quality_group)
        
        return container
    
    def _create_save_section(self) -> QWidget:
        """Create save location section."""
        group = QGroupBox("Save Location")
        layout = QHBoxLayout(group)
        
        self.save_path_input = QLineEdit()
        self.save_path_input.setReadOnly(True)
        self.save_path_input.setMinimumHeight(32)
        layout.addWidget(self.save_path_input)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setMinimumHeight(32)
        self.browse_button.setMinimumWidth(100)
        layout.addWidget(self.browse_button)
        
        return group
    
    def _create_download_button(self) -> QPushButton:
        """Create the main download button."""
        self.download_button = QPushButton("↓ DOWNLOAD")
        self.download_button.setMinimumHeight(50)
        self.download_button.setEnabled(False)
        
        # Style the button
        font = self.download_button.font()
        font.setPointSize(14)
        font.setBold(True)
        self.download_button.setFont(font)
        
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        return self.download_button
    
    def _create_progress_section(self) -> QWidget:
        """Create progress bar and label section."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.hide()
        layout.addWidget(self.progress_label)
        
        return container
    
    def _create_log_section(self) -> QWidget:
        """Create log/status area section."""
        group = QGroupBox("Download Log")
        layout = QVBoxLayout(group)
        
        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setPlaceholderText("Download history will appear here...")
        
        # Monospace font for log
        font = QFont("Consolas", 9)
        self.log_area.setFont(font)
        
        layout.addWidget(self.log_area)
        
        return group
    
    def _create_control_buttons(self) -> QWidget:
        """Create control buttons (Open Folder, Clear Log)."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_folder_button = QPushButton("📂 Open Folder")
        self.open_folder_button.setMinimumHeight(36)
        layout.addWidget(self.open_folder_button)
        
        self.clear_log_button = QPushButton("🗑 Clear Log")
        self.clear_log_button.setMinimumHeight(36)
        layout.addWidget(self.clear_log_button)
        
        layout.addStretch()
        
        return container
    
    def _connect_signals(self) -> None:
        """Connect all signal/slot connections."""
        # URL input
        self.url_input.textChanged.connect(self._on_url_changed)
        
        # Format selection
        self.video_radio.toggled.connect(self._on_format_changed)
        
        # Browse button
        self.browse_button.clicked.connect(self._on_browse_clicked)
        
        # Download button
        self.download_button.clicked.connect(self._on_download_clicked)
        
        # Control buttons
        self.open_folder_button.clicked.connect(self._on_open_folder)
        self.clear_log_button.clicked.connect(self._on_clear_log)
        
        # Download manager signals
        self.download_manager.progress_updated.connect(self._on_progress_update)
        self.download_manager.download_finished.connect(self._on_download_finished)
        self.download_manager.error_occurred.connect(self._on_download_error)
        self.download_manager.log_message.connect(self._on_log_message)
    
    def _load_settings(self) -> None:
        """Load saved settings from config."""
        # Output path
        output_path = self.config.get_output_path()
        self.save_path_input.setText(str(output_path))
        
        # Format
        last_format = self.config.get_last_format()
        if last_format == "audio":
            self.audio_radio.setChecked(True)
        else:
            self.video_radio.setChecked(True)
        
        # Quality
        last_quality = self.config.get_last_quality()
        index = self.quality_combo.findText(last_quality, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)
        
        # Window geometry
        geometry = self.config.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        logger.debug("Settings loaded")
    
    def _check_dependencies(self) -> None:
        """Check if yt-dlp and ffmpeg are installed."""
        if not self.ytdlp_wrapper.check_yt_dlp_installed():
            self._show_warning_dialog(
                "yt-dlp Not Found",
                "yt-dlp is not installed or not in PATH.\n\n"
                "Please install it from:\n"
                "https://github.com/yt-dlp/yt-dlp/releases\n\n"
                "Or run: pip install yt-dlp"
            )
            self.download_button.setEnabled(False)
            self._log("⚠ yt-dlp not found - downloads disabled")
        
        if not self.ytdlp_wrapper.check_ffmpeg_installed():
            self._log("ℹ ffmpeg not found - audio downloads may have issues")
    
    @pyqtSlot(str)
    def _on_url_changed(self, text: str) -> None:
        """Handle URL input changes."""
        text = text.strip()
        
        # Reset state
        self._current_metadata = None
        self.video_info_label.hide()
        
        if not text:
            self.download_button.setEnabled(False)
            return
        
        # Validate URL
        if self.ytdlp_wrapper.validate_url(text):
            self.download_button.setEnabled(True)
            self._fetch_metadata_delayed(text)
        else:
            self.download_button.setEnabled(False)
            if len(text) > 10:  # Only show error for substantial input
                self.video_info_label.setText("⚠ Not a valid YouTube URL")
                self.video_info_label.setStyleSheet("color: #c00; font-style: italic;")
                self.video_info_label.show()
    
    def _fetch_metadata_delayed(self, url: str) -> None:
        """Fetch metadata after a short delay (debounce)."""
        # Cancel previous timer
        if self._metadata_fetch_timer:
            self._metadata_fetch_timer.stop()
        
        # Start new timer
        self._metadata_fetch_timer = QTimer()
        self._metadata_fetch_timer.setSingleShot(True)
        self._metadata_fetch_timer.timeout.connect(lambda: self._fetch_metadata(url))
        self._metadata_fetch_timer.start(500)  # 500ms delay
    
    def _fetch_metadata(self, url: str) -> None:
        """Fetch video metadata."""
        self.video_info_label.setText("Fetching video info...")
        self.video_info_label.setStyleSheet("color: #666; font-style: italic;")
        self.video_info_label.show()
        
        # Fetch in main thread for now (could move to worker thread)
        metadata = self.ytdlp_wrapper.fetch_metadata(url)
        
        if "error" in metadata:
            self.video_info_label.setText(f"⚠ {metadata['error']}")
            self.video_info_label.setStyleSheet("color: #c00; font-style: italic;")
            self._current_metadata = None
        else:
            self._current_metadata = metadata
            title = metadata.get("title", "Unknown")
            duration = format_duration(metadata.get("duration", 0))
            self.video_info_label.setText(f"📺 {title} ({duration})")
            self.video_info_label.setStyleSheet("color: #060; font-style: normal;")
            
            # Update quality options
            formats = metadata.get("formats", ["Best"])
            self._update_quality_options(formats)
    
    def _update_quality_options(self, formats: list[str]) -> None:
        """Update quality dropdown with available formats."""
        current = self.quality_combo.currentText()
        self.quality_combo.clear()
        
        # Capitalize for display
        display_formats = [f.capitalize() if f != "best" else "Best" for f in formats]
        self.quality_combo.addItems(display_formats)
        
        # Restore previous selection if available
        index = self.quality_combo.findText(current, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)
    
    @pyqtSlot(bool)
    def _on_format_changed(self, checked: bool) -> None:
        """Handle format radio button changes."""
        if self.video_radio.isChecked():
            # Video format - show all quality options
            self.quality_combo.setEnabled(True)
            if self._current_metadata:
                self._update_quality_options(self._current_metadata.get("formats", ["Best"]))
            else:
                self.quality_combo.clear()
                self.quality_combo.addItems(["Best", "720p", "480p", "360p"])
        else:
            # Audio format - only "Best Quality"
            self.quality_combo.clear()
            self.quality_combo.addItems(["Best Quality"])
            self.quality_combo.setEnabled(False)
        
        # Save preference
        format_type = "video" if self.video_radio.isChecked() else "audio"
        self.config.set_last_format(format_type)
    
    @pyqtSlot()
    def _on_browse_clicked(self) -> None:
        """Handle Browse button click."""
        current_path = self.save_path_input.text()
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.save_path_input.setText(folder)
            self.config.set_output_path(folder)
            self._log(f"Save location: {folder}")
    
    @pyqtSlot()
    def _on_download_clicked(self) -> None:
        """Handle Download button click."""
        url = self.url_input.text().strip()
        
        if not url:
            return
        
        # Get settings
        format_type = "video" if self.video_radio.isChecked() else "audio"
        quality = self.quality_combo.currentText().lower()
        output_path = self.save_path_input.text()
        
        # Check disk space
        has_space, available_mb = check_disk_space(output_path)
        if not has_space:
            reply = QMessageBox.warning(
                self,
                "Low Disk Space",
                f"Only {available_mb} MB available. Download may fail.\n\nContinue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Generate filename
        if self._current_metadata:
            title = self._current_metadata.get("title", "video")
        else:
            title = "video"
        
        filename = get_output_filename(title, format_type)
        filename = get_unique_filename(output_path, filename)
        
        # Update UI for downloading state
        self._set_downloading_state(True)
        
        # Save quality preference
        self.config.set_last_quality(quality)
        
        # Start download
        success = self.download_manager.start_download(
            url, format_type, quality, output_path, filename
        )
        
        if not success:
            self._set_downloading_state(False)
            self._show_error_dialog("Download Error", "A download is already in progress.")
    
    def _set_downloading_state(self, downloading: bool) -> None:
        """Update UI for downloading/idle state."""
        self.download_button.setEnabled(not downloading)
        self.url_input.setEnabled(not downloading)
        self.video_radio.setEnabled(not downloading)
        self.audio_radio.setEnabled(not downloading)
        self.quality_combo.setEnabled(not downloading)
        self.browse_button.setEnabled(not downloading)
        
        if downloading:
            self.download_button.setText("Downloading...")
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.progress_label.show()
        else:
            self.download_button.setText("↓ DOWNLOAD")
            self.progress_bar.hide()
            self.progress_label.hide()
    
    @pyqtSlot(int, str, str)
    def _on_progress_update(self, percentage: int, speed: str, eta: str) -> None:
        """Handle download progress updates."""
        self.progress_bar.setValue(percentage)
        
        if speed and eta:
            self.progress_label.setText(f"Downloading... {percentage}% ({speed}, ~{eta} remaining)")
        else:
            self.progress_label.setText(f"Downloading... {percentage}%")
    
    @pyqtSlot(str, float)
    def _on_download_finished(self, file_path: str, file_size: float) -> None:
        """Handle download completion."""
        self._set_downloading_state(False)
        self.progress_bar.setValue(100)
        
        # Add to history
        if self._current_metadata:
            self.config.add_download_history(
                title=self._current_metadata.get("title", "Unknown"),
                url=self.url_input.text(),
                file_path=file_path,
                file_size_mb=file_size,
                duration_seconds=self._current_metadata.get("duration", 0)
            )
        
        # Clear URL for next download
        self.url_input.clear()
        self._current_metadata = None
        self.video_info_label.hide()
        
        # Show success message
        self._show_info_dialog(
            "Download Complete",
            f"File saved successfully!\n\n{Path(file_path).name}\nSize: {file_size} MB"
        )
    
    @pyqtSlot(str)
    def _on_download_error(self, message: str) -> None:
        """Handle download errors."""
        self._set_downloading_state(False)
        self._log(f"✗ Error: {message}")
        self._show_error_dialog("Download Failed", message)
    
    @pyqtSlot(str)
    def _on_log_message(self, message: str) -> None:
        """Handle log messages from download manager."""
        self._log(message)
    
    @pyqtSlot()
    def _on_open_folder(self) -> None:
        """Open the download folder in file manager."""
        path = self.save_path_input.text()
        if path:
            open_file_manager(path)
    
    @pyqtSlot()
    def _on_clear_log(self) -> None:
        """Clear the log area."""
        self.log_area.clear()
    
    def _log(self, message: str) -> None:
        """Add a message to the log area."""
        self.log_area.appendPlainText(message)
        # Scroll to bottom
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        QMessageBox.critical(self, title, message)
        logger.error(f"{title}: {message}")
    
    def _show_warning_dialog(self, title: str, message: str) -> bool:
        """Show a warning dialog. Returns True if user clicks OK."""
        result = QMessageBox.warning(
            self, title, message,
            QMessageBox.StandardButton.Ok
        )
        logger.warning(f"{title}: {message}")
        return result == QMessageBox.StandardButton.Ok
    
    def _show_info_dialog(self, title: str, message: str) -> None:
        """Show an info dialog."""
        QMessageBox.information(self, title, message)
    
    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Save window geometry
        self.config.save_window_geometry(self.saveGeometry())
        
        # Cancel any ongoing download
        if self.download_manager.is_downloading:
            reply = QMessageBox.question(
                self,
                "Download in Progress",
                "A download is in progress. Cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.download_manager.cancel_download()
        
        logger.info("Application closing")
        event.accept()
