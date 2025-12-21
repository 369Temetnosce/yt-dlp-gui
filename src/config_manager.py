"""Configuration manager for yt-dlp GUI Desktop App.

This module handles persistent storage of user settings and download history
using JSON files stored in the user's config directory.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .utils import get_config_dir, get_default_download_path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration and state persistence.
    
    Stores settings in ~/.config/yt-dlp-gui/config.json (Unix)
    or %APPDATA%/yt-dlp-gui/config.json (Windows).
    
    Attributes:
        config_path: Path to the config.json file
        _config: Cached configuration dictionary
    """
    
    MAX_HISTORY_ENTRIES = 50
    
    def __init__(self) -> None:
        """Initialize ConfigManager and load existing config."""
        self.config_dir = get_config_dir()
        self.config_path = self.config_dir / "config.json"
        self._config: dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or create default."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.debug(f"Config loaded from {self.config_path}")
            else:
                self._config = self.get_default_config()
                self._save_config()
                logger.info(f"Created default config at {self.config_path}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"Corrupted config file, using defaults: {e}")
            self._config = self.get_default_config()
            self._save_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._config = self.get_default_config()
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.debug("Config saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    @staticmethod
    def get_default_config() -> dict[str, Any]:
        """Get default configuration template.
        
        Returns:
            Dictionary with default settings
        """
        return {
            "last_output_path": str(get_default_download_path()),
            "last_format": "video",
            "last_quality": "best",
            "window_geometry": None,
            "download_history": [],
            "groq_api_key": ""
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self._save_config()
        logger.debug(f"Config updated: {key}")
    
    def load_config(self) -> dict[str, Any]:
        """Load and return the current configuration.
        
        Returns:
            Configuration dictionary
        """
        self._load_config()
        return self._config.copy()
    
    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration dictionary to file.
        
        Args:
            config: Configuration dictionary to save
        """
        self._config = config
        self._save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self._save_config()
        logger.debug(f"Config updated: {key} = {value}")
    
    def get_output_path(self) -> Path:
        """Get the configured output directory path.
        
        Returns:
            Path object for output directory
        """
        path_str = self.get("last_output_path", str(get_default_download_path()))
        return Path(path_str).expanduser()
    
    def set_output_path(self, path: str | Path) -> None:
        """Set the output directory path.
        
        Args:
            path: New output directory path
        """
        self.set("last_output_path", str(path))
    
    def get_last_format(self) -> str:
        """Get the last used format (video/audio).
        
        Returns:
            'video' or 'audio'
        """
        return self.get("last_format", "video")
    
    def set_last_format(self, format_type: str) -> None:
        """Set the last used format.
        
        Args:
            format_type: 'video' or 'audio'
        """
        if format_type in ("video", "audio"):
            self.set("last_format", format_type)
    
    def get_last_quality(self) -> str:
        """Get the last used quality setting.
        
        Returns:
            Quality string like 'best', '720p', etc.
        """
        return self.get("last_quality", "best")
    
    def set_last_quality(self, quality: str) -> None:
        """Set the last used quality.
        
        Args:
            quality: Quality string
        """
        self.set("last_quality", quality)
    
    def add_download_history(
        self,
        title: str,
        url: str,
        file_path: str,
        file_size_mb: float,
        duration_seconds: int = 0
    ) -> None:
        """Add an entry to download history.
        
        Keeps only the last MAX_HISTORY_ENTRIES entries.
        
        Args:
            title: Video title
            url: YouTube URL
            file_path: Path to downloaded file
            file_size_mb: File size in megabytes
            duration_seconds: Video duration in seconds
        """
        history = self._config.get("download_history", [])
        
        entry = {
            "title": title,
            "url": url,
            "file_path": file_path,
            "file_size_mb": file_size_mb,
            "duration_seconds": duration_seconds,
            "date": datetime.now().isoformat()
        }
        
        history.insert(0, entry)
        
        # Keep only last N entries
        if len(history) > self.MAX_HISTORY_ENTRIES:
            history = history[:self.MAX_HISTORY_ENTRIES]
        
        self._config["download_history"] = history
        self._save_config()
        logger.info(f"Added to download history: {title}")
    
    def get_download_history(self) -> list[dict[str, Any]]:
        """Get download history.
        
        Returns:
            List of download history entries (newest first)
        """
        return self._config.get("download_history", [])
    
    def clear_download_history(self) -> None:
        """Clear all download history."""
        self._config["download_history"] = []
        self._save_config()
        logger.info("Download history cleared")
    
    def save_window_geometry(self, geometry: bytes) -> None:
        """Save window geometry for restoration.
        
        Args:
            geometry: QByteArray from saveGeometry() as bytes
        """
        import base64
        encoded = base64.b64encode(geometry).decode("ascii")
        self.set("window_geometry", encoded)
    
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry.
        
        Returns:
            Geometry bytes or None if not saved
        """
        import base64
        encoded = self.get("window_geometry")
        if encoded:
            try:
                return base64.b64decode(encoded)
            except Exception:
                return None
        return None
