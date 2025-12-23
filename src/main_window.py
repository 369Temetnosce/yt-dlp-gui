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
from .transcriber import Transcriber
from .proofreader import Proofreader
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
        self.transcriber = Transcriber(self.config.get("groq_api_key"))
        self.proofreader = Proofreader(
            api_key=self.config.get("openrouter_api_key"),
            model=self.config.get("proofreader_model", "claude-3.5-sonnet"),
            system_prompt_path=Path(__file__).parent.parent / "proofreader.txt"
        )
        
        # State
        self._current_metadata: Optional[dict] = None
        self._metadata_fetch_timer: Optional[QTimer] = None
        self._last_downloaded_file: Optional[str] = None
        
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
        """Create control buttons (Open Folder, Transcribe, Clear Log, Settings)."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_folder_button = QPushButton("📂 Open Folder")
        self.open_folder_button.setMinimumHeight(36)
        layout.addWidget(self.open_folder_button)
        
        self.transcribe_button = QPushButton("🎤 Transcribe")
        self.transcribe_button.setMinimumHeight(36)
        self.transcribe_button.setToolTip("Transcribe a video/audio file to text")
        layout.addWidget(self.transcribe_button)
        
        self.proofread_button = QPushButton("📝 Proofread")
        self.proofread_button.setMinimumHeight(36)
        self.proofread_button.setToolTip("Proofread and edit transcript files using AI")
        layout.addWidget(self.proofread_button)
        
        self.clear_log_button = QPushButton("🗑 Clear Log")
        self.clear_log_button.setMinimumHeight(36)
        layout.addWidget(self.clear_log_button)
        
        layout.addStretch()
        
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setMinimumHeight(36)
        layout.addWidget(self.settings_button)
        
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
        self.transcribe_button.clicked.connect(self._on_transcribe_clicked)
        self.proofread_button.clicked.connect(self._on_proofread_clicked)
        self.clear_log_button.clicked.connect(self._on_clear_log)
        self.settings_button.clicked.connect(self._on_settings_clicked)
        
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
        else:
            # Log yt-dlp version
            version = self.ytdlp_wrapper.get_yt_dlp_version()
            self._log(f"yt-dlp version: {version}")
        
        if not self.ytdlp_wrapper.check_ffmpeg_installed():
            self._log("ℹ ffmpeg not found - audio downloads may have issues")
        
        # Log browser cookies status
        browser = self.ytdlp_wrapper.get_browser()
        if browser:
            self._log(f"🍪 Using {browser} cookies for age-restricted videos")
        else:
            self._log("ℹ No browser cookies - some videos may be restricted")
    
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
        
        # Store last downloaded file for transcription
        self._last_downloaded_file = file_path
        
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
        
        # Show success message with transcribe option
        reply = QMessageBox.question(
            self,
            "Download Complete",
            f"File saved successfully!\n\n{Path(file_path).name}\nSize: {file_size} MB\n\nWould you like to transcribe this video?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._on_transcribe_clicked()
    
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
    
    @pyqtSlot()
    def _on_transcribe_clicked(self) -> None:
        """Handle Transcribe button click."""
        # If no recent download, prompt to select a file
        if not self._last_downloaded_file or not Path(self._last_downloaded_file).exists():
            file_path = self._select_video_for_transcription()
            if not file_path:
                return
        else:
            # Ask user: transcribe last download or browse for file?
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Transcribe Video")
            msg_box.setText(f"Transcribe the last downloaded video?\n\n{Path(self._last_downloaded_file).name}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            browse_button = msg_box.addButton("Browse...", QMessageBox.ButtonRole.ActionRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == browse_button:
                file_path = self._select_video_for_transcription()
                if not file_path:
                    return
            elif msg_box.result() == QMessageBox.StandardButton.Yes:
                file_path = Path(self._last_downloaded_file)
            else:
                return
        
        self._transcribe_file(file_path)
    
    def _select_video_for_transcription(self) -> Optional[Path]:
        """Open file dialog to select a video/audio file for transcription."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video/Audio to Transcribe",
            self.save_path_input.text(),
            "Media Files (*.mp4 *.mkv *.webm *.avi *.mov *.mp3 *.m4a *.wav *.flac);;All Files (*.*)"
        )
        if file_path:
            return Path(file_path)
        return None
    
    def _transcribe_file(self, file_path: Path) -> None:
        """Transcribe the specified file."""
        if not file_path.exists():
            self._show_error_dialog("File Not Found", f"The file no longer exists:\n{file_path}")
            return
        
        # Check if API key is configured
        if not self.transcriber.has_groq_api_key():
            reply = QMessageBox.question(
                self,
                "Groq API Key Required",
                "Transcription requires a Groq API key.\n\n"
                "Would you like to configure it now?\n\n"
                "(Get a free key at groq.com)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._on_settings_clicked()
            return
        
        # Check for resumable transcription
        resume_info = self.transcriber.check_resume_available(str(file_path))
        if resume_info:
            reply = QMessageBox.question(
                self,
                "Resume Transcription?",
                f"Found incomplete transcription for this file.\n\n"
                f"Progress: {resume_info['completed_chunks']}/{resume_info['total_chunks']} chunks completed\n\n"
                f"Would you like to resume from chunk {resume_info['completed_chunks'] + 1}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                # Resume transcription
                self._log(f"🎤 Resuming transcription: {file_path.name} (chunk {resume_info['completed_chunks'] + 1}/{resume_info['total_chunks']})")
                self.transcribe_button.setEnabled(False)
                self.transcribe_button.setText("Transcribing...")
                
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                
                result = self.transcriber.resume_transcription(
                    str(file_path),
                    progress_callback=lambda msg: (self._log(f"  {msg}"), QCoreApplication.processEvents())
                )
                
                self.transcribe_button.setText("🎤 Transcribe")
                self.transcribe_button.setEnabled(True)
                
                if "error" in result:
                    self._log(f"✗ Transcription failed: {result['error']}")
                    self._show_error_dialog("Transcription Failed", result["error"])
                    return
                
                # Use the timestamps setting from the saved progress
                include_timestamps = resume_info.get('include_timestamps', False)
                if include_timestamps and "timestamped_text" in result:
                    save_text = result["timestamped_text"]
                    display_text = result["timestamped_text"]
                else:
                    save_text = result["text"]
                    display_text = result["text"]
                
                # Save and show result (same as normal flow below)
                transcript_path = file_path.with_suffix(".txt")
                if self.transcriber.save_transcript(save_text, str(file_path.with_suffix(""))):
                    chunks_info = f"\nChunks processed: {result.get('chunks', 1)}" if result.get('chunks', 1) > 1 else ""
                    self._log(f"✓ Transcript saved: {transcript_path.name}{chunks_info}")
                    
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Transcription Complete")
                    msg_box.setText(f"Transcript saved to:\n{transcript_path.name}\n\nLanguage: {result.get('language', 'unknown')}{chunks_info}")
                    msg_box.setDetailedText(display_text)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    
                    copy_button = msg_box.addButton("Copy to Clipboard", QMessageBox.ButtonRole.ActionRole)
                    msg_box.exec()
                    
                    if msg_box.clickedButton() == copy_button:
                        from PyQt6.QtWidgets import QApplication
                        QApplication.clipboard().setText(display_text)
                        self._log("📋 Transcript copied to clipboard")
                else:
                    self._log(f"✗ Failed to save transcript")
                return
            # If No, continue with fresh transcription (fall through)
        
        # Ask about timestamps
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
        
        options_dialog = QDialog(self)
        options_dialog.setWindowTitle("Transcription Options")
        options_dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(options_dialog)
        layout.addWidget(QLabel(f"<b>File:</b> {file_path.name}"))
        
        timestamps_checkbox = QCheckBox("Include timestamps (e.g., [00:01:23] text)")
        timestamps_checkbox.setChecked(self.config.get("include_timestamps", False))
        layout.addWidget(timestamps_checkbox)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(options_dialog.accept)
        buttons.rejected.connect(options_dialog.reject)
        layout.addWidget(buttons)
        
        if options_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        include_timestamps = timestamps_checkbox.isChecked()
        self.config.set("include_timestamps", include_timestamps)
        
        # Start transcription
        self._log(f"🎤 Starting transcription: {file_path.name}" + (" (with timestamps)" if include_timestamps else ""))
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setText("Transcribing...")
        
        # Run transcription (this blocks UI - could be improved with QThread)
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        result = self.transcriber.transcribe(
            str(file_path),
            progress_callback=lambda msg: (self._log(f"  {msg}"), QCoreApplication.processEvents()),
            include_timestamps=include_timestamps
        )
        
        self.transcribe_button.setText("🎤 Transcribe")
        self.transcribe_button.setEnabled(True)
        
        if "error" in result:
            self._log(f"✗ Transcription failed: {result['error']}")
            self._show_error_dialog("Transcription Failed", result["error"])
            return
        
        # Determine which text to save (timestamped or plain)
        if include_timestamps and "timestamped_text" in result:
            save_text = result["timestamped_text"]
            display_text = result["timestamped_text"]
        else:
            save_text = result["text"]
            display_text = result["text"]
        
        # Save transcript
        transcript_path = file_path.with_suffix(".txt")
        if self.transcriber.save_transcript(save_text, str(file_path.with_suffix(""))):
            chunks_info = f"\nChunks processed: {result.get('chunks', 1)}" if result.get('chunks', 1) > 1 else ""
            self._log(f"✓ Transcript saved: {transcript_path.name}{chunks_info}")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Transcription Complete")
            msg_box.setText(f"Transcript saved to:\n{transcript_path.name}\n\nLanguage: {result.get('language', 'unknown')}{chunks_info}")
            msg_box.setDetailedText(display_text)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            
            # Add copy button
            copy_button = msg_box.addButton("Copy to Clipboard", QMessageBox.ButtonRole.ActionRole)
            
            msg_box.exec()
            
            if msg_box.clickedButton() == copy_button:
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(display_text)
                self._log("📋 Transcript copied to clipboard")
        else:
            self._log(f"✗ Failed to save transcript")
    
    @pyqtSlot()
    def _on_proofread_clicked(self) -> None:
        """Handle proofread button click - select and proofread transcript files."""
        # Check if API key is configured
        if not self.proofreader.has_api_key():
            reply = QMessageBox.question(
                self,
                "OpenRouter API Key Required",
                "Proofreading requires an OpenRouter API key.\n\n"
                "Would you like to configure it now?\n\n"
                "(Get a key at openrouter.ai)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._on_settings_clicked()
            return
        
        # Open file dialog for transcript selection (multi-select)
        start_dir = str(self.config.get_output_path())
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Transcript Files to Proofread",
            start_dir,
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_paths:
            return
        
        # Confirm with user
        file_count = len(file_paths)
        if file_count > 1:
            reply = QMessageBox.question(
                self,
                "Confirm Bulk Proofreading",
                f"You selected {file_count} files to proofread.\n\n"
                f"Model: {self.proofreader.get_model()}\n\n"
                "This may take a while and incur API costs. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Start proofreading
        self._log(f"📝 Starting proofreading: {file_count} file(s)")
        self.proofread_button.setEnabled(False)
        self.proofread_button.setText("Proofreading...")
        
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        # Process files
        success_count = 0
        fail_count = 0
        
        for i, file_path in enumerate(file_paths, 1):
            file_name = Path(file_path).name
            self._log(f"  Processing {i}/{file_count}: {file_name}")
            QCoreApplication.processEvents()
            
            result = self.proofreader.proofread_file(
                file_path,
                progress_callback=lambda msg: (self._log(f"    {msg}"), QCoreApplication.processEvents())
            )
            
            if "error" in result:
                self._log(f"  ✗ Failed: {result['error']}")
                fail_count += 1
            else:
                output_path = Path(result.get("output_path", ""))
                self._log(f"  ✓ Saved: {output_path.name}")
                if result.get("summary"):
                    # Log summary briefly
                    summary_lines = result["summary"].strip().split("\n")
                    for line in summary_lines[:4]:  # First 4 lines of summary
                        self._log(f"    {line.strip()}")
                success_count += 1
        
        # Re-enable button
        self.proofread_button.setText("📝 Proofread")
        self.proofread_button.setEnabled(True)
        
        # Show summary
        if file_count == 1:
            if success_count == 1:
                # Show detailed result for single file
                result = self.proofreader.proofread_file(file_paths[0])  # Already processed, just get result
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Proofreading Complete")
                msg_box.setText(f"Edited transcript saved!\n\nModel: {self.proofreader.get_model()}")
                if result.get("summary"):
                    msg_box.setDetailedText(result["summary"])
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
        else:
            # Bulk summary
            self._log(f"📝 Proofreading complete: {success_count} succeeded, {fail_count} failed")
            QMessageBox.information(
                self,
                "Bulk Proofreading Complete",
                f"Processed {file_count} files:\n\n"
                f"✓ Succeeded: {success_count}\n"
                f"✗ Failed: {fail_count}\n\n"
                f"Edited files saved with '-Edited.md' suffix."
            )
    
    @pyqtSlot()
    def _on_settings_clicked(self) -> None:
        """Show settings dialog."""
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(450)
        
        layout = QFormLayout(dialog)
        
        # === Groq API Key (Transcription) ===
        layout.addRow(QLabel("<b>Transcription (Groq Whisper)</b>"))
        
        groq_key_input = QLineEdit()
        groq_key_input.setPlaceholderText("Enter your Groq API key")
        groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        current_groq_key = self.config.get("groq_api_key", "")
        if current_groq_key:
            groq_key_input.setText(current_groq_key)
        layout.addRow("Groq API Key:", groq_key_input)
        
        groq_help = QLabel('<a href="https://console.groq.com/keys">Get free Groq API key</a>')
        groq_help.setOpenExternalLinks(True)
        layout.addRow("", groq_help)
        
        # === OpenRouter API Key (Proofreading) ===
        layout.addRow(QLabel(""))  # Spacer
        layout.addRow(QLabel("<b>Proofreading (OpenRouter)</b>"))
        
        openrouter_key_input = QLineEdit()
        openrouter_key_input.setPlaceholderText("Enter your OpenRouter API key")
        openrouter_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        current_openrouter_key = self.config.get("openrouter_api_key", "")
        if current_openrouter_key:
            openrouter_key_input.setText(current_openrouter_key)
        layout.addRow("OpenRouter Key:", openrouter_key_input)
        
        # Model selection
        model_combo = QComboBox()
        model_combo.addItems(self.proofreader.get_available_models())
        current_model = self.config.get("proofreader_model", "claude-3.5-sonnet")
        index = model_combo.findText(current_model)
        if index >= 0:
            model_combo.setCurrentIndex(index)
        layout.addRow("Proofreader Model:", model_combo)
        
        openrouter_help = QLabel('<a href="https://openrouter.ai/keys">Get OpenRouter API key</a>')
        openrouter_help.setOpenExternalLinks(True)
        layout.addRow("", openrouter_help)
        
        # Show/hide keys button
        show_keys_btn = QPushButton("Show Keys")
        show_keys_btn.setCheckable(True)
        def toggle_key_visibility(checked):
            mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            groq_key_input.setEchoMode(mode)
            openrouter_key_input.setEchoMode(mode)
            show_keys_btn.setText("Hide Keys" if checked else "Show Keys")
        show_keys_btn.toggled.connect(toggle_key_visibility)
        layout.addRow("", show_keys_btn)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save Groq key
            groq_key = groq_key_input.text().strip()
            if groq_key != current_groq_key:
                self.config.set("groq_api_key", groq_key)
                self.transcriber.set_groq_api_key(groq_key)
                if groq_key:
                    self._log("✓ Groq API key saved")
                else:
                    self._log("ℹ Groq API key removed")
            
            # Save OpenRouter key
            openrouter_key = openrouter_key_input.text().strip()
            if openrouter_key != current_openrouter_key:
                self.config.set("openrouter_api_key", openrouter_key)
                self.proofreader.set_api_key(openrouter_key)
                if openrouter_key:
                    self._log("✓ OpenRouter API key saved")
                else:
                    self._log("ℹ OpenRouter API key removed")
            
            # Save model selection
            selected_model = model_combo.currentText()
            if selected_model != current_model:
                self.config.set("proofreader_model", selected_model)
                self.proofreader.set_model(selected_model)
                self._log(f"✓ Proofreader model set to {selected_model}")
    
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
