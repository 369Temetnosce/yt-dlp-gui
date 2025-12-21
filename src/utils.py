"""Utility functions for yt-dlp GUI Desktop App.

This module provides helper functions for:
- Filename sanitization
- Directory management
- Cross-platform file manager opening
- Logging setup
- File size formatting
"""

import logging
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the application config directory path.
    
    Returns:
        Path to ~/.config/yt-dlp-gui/ (Unix) or %APPDATA%/yt-dlp-gui/ (Windows)
    """
    if platform.system() == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    
    return base / "yt-dlp-gui"


def setup_logging(app_name: str = "yt-dlp-gui") -> None:
    """Setup application logging with file and console handlers.
    
    Creates log directory and configures:
    - File handler: DEBUG level, writes to app.log
    - Console handler: INFO level
    
    Args:
        app_name: Name of the application for logger
    """
    log_dir = get_config_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "app.log"
    
    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler (DEBUG level)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialized. Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_log_file_path() -> Path:
    """Get the path to the application log file.
    
    Returns:
        Path to app.log
    """
    return get_config_dir() / "app.log"


def sanitize_filename(filename: str) -> str:
    """Remove illegal characters from filename for cross-platform compatibility.
    
    Removes: < > : " / \\ | ? *
    Replaces with underscore.
    Limits to 200 characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for all platforms
        
    Example:
        >>> sanitize_filename("My <Awesome> Video!")
        'My _Awesome_ Video!'
    """
    # Characters illegal on Windows and/or other platforms
    illegal_chars = r'[<>:"/\\|?*]'
    
    # Replace illegal characters with underscore
    sanitized = re.sub(illegal_chars, '_', filename)
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)
    
    # Remove leading/trailing spaces and dots (Windows issue)
    sanitized = sanitized.strip(' .')
    
    # Limit length (leave room for extension)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # Ensure not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized


def get_unique_filename(output_dir: str | Path, filename: str) -> str:
    """Get a unique filename by appending (1), (2), etc. if file exists.
    
    Args:
        output_dir: Directory where file will be saved
        filename: Desired filename (with extension)
        
    Returns:
        Unique filename (just the name, not full path)
        
    Example:
        >>> get_unique_filename("/downloads", "video.mp4")
        'video.mp4'  # if doesn't exist
        >>> get_unique_filename("/downloads", "video.mp4")
        'video (1).mp4'  # if video.mp4 exists
    """
    output_path = Path(output_dir)
    full_path = output_path / filename
    
    if not full_path.exists():
        return filename
    
    # Split name and extension
    stem = full_path.stem
    suffix = full_path.suffix
    
    counter = 1
    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        new_path = output_path / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1
        
        # Safety limit
        if counter > 1000:
            # Use timestamp as fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{stem}_{timestamp}{suffix}"


def ensure_directory_exists(path: str | Path) -> bool:
    """Create directory and parents if they don't exist.
    
    Args:
        path: Directory path to create
        
    Returns:
        True if directory exists or was created, False on permission error
    """
    logger = get_logger(__name__)
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
        return True
    except PermissionError:
        logger.error(f"Permission denied creating directory: {path}")
        return False
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def get_output_filename(title: str, format_type: str) -> str:
    """Generate output filename from video title and format.
    
    Args:
        title: Video title (will be sanitized)
        format_type: "video" or "audio"
        
    Returns:
        Sanitized filename with appropriate extension
        
    Example:
        >>> get_output_filename("My Video", "video")
        'My Video.mp4'
        >>> get_output_filename("My Song", "audio")
        'My Song.mp3'
    """
    sanitized_title = sanitize_filename(title)
    extension = ".mp4" if format_type == "video" else ".mp3"
    return f"{sanitized_title}{extension}"


def get_file_size_mb(file_path: str | Path) -> float:
    """Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB with 1 decimal place, or 0.0 if file doesn't exist
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 1)
    except (FileNotFoundError, OSError):
        return 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string like "48.5 MB" or "1.2 GB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: int) -> str:
    """Format duration in HH:MM:SS or MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def open_file_manager(path: str | Path) -> bool:
    """Open the native file manager to the specified path.
    
    Cross-platform support for Windows, macOS, and Linux.
    
    Args:
        path: Directory or file path to open
        
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger(__name__)
    path = Path(path)
    
    # If path is a file, open its parent directory
    if path.is_file():
        path = path.parent
    
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(str(path))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(path)], check=True)
        else:  # Linux and others
            subprocess.run(["xdg-open", str(path)], check=True)
        
        logger.info(f"Opened file manager to: {path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to open file manager: {e}")
        return False


def get_default_download_path() -> Path:
    """Get the default download directory path.
    
    Returns:
        Path to ~/Downloads/yt-dlp/ (or equivalent on Windows)
    """
    downloads = Path.home() / "Downloads" / "yt-dlp"
    return downloads


def get_free_disk_space(path: str | Path) -> int:
    """Get free disk space at the specified path in bytes.
    
    Args:
        path: Path to check (uses the drive/mount point)
        
    Returns:
        Free space in bytes, or 0 if cannot determine
    """
    try:
        usage = shutil.disk_usage(path)
        return usage.free
    except (FileNotFoundError, OSError):
        return 0


def check_disk_space(path: str | Path, required_mb: float = 100) -> tuple[bool, float]:
    """Check if there's enough disk space.
    
    Args:
        path: Path to check
        required_mb: Minimum required space in MB
        
    Returns:
        Tuple of (has_enough_space, available_mb)
    """
    free_bytes = get_free_disk_space(path)
    free_mb = free_bytes / (1024 * 1024)
    return (free_mb >= required_mb, round(free_mb, 1))
