"""yt-dlp subprocess wrapper for yt-dlp GUI Desktop App.

This module provides a clean interface to yt-dlp command-line functionality:
- URL validation
- Metadata fetching
- Command building for downloads
- Installation checking
"""

import json
import logging
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class YTDLPWrapper:
    """Wrapper class for yt-dlp subprocess operations.
    
    Provides methods to validate URLs, fetch metadata, and build
    download commands without directly exposing subprocess details.
    """
    
    # Timeout for subprocess calls (seconds)
    METADATA_TIMEOUT = 30
    VERSION_TIMEOUT = 10
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
        r'(https?://)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/embed/[\w-]+',
    ]
    
    def __init__(self) -> None:
        """Initialize YTDLPWrapper."""
        self._yt_dlp_path: Optional[str] = None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if URL is a valid YouTube URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is a valid YouTube URL, False otherwise
            
        Example:
            >>> YTDLPWrapper.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            True
            >>> YTDLPWrapper.validate_url("https://example.com")
            False
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        for pattern in YTDLPWrapper.YOUTUBE_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def check_yt_dlp_installed(self) -> bool:
        """Check if yt-dlp is installed and accessible.
        
        Returns:
            True if yt-dlp is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=self.VERSION_TIMEOUT
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"yt-dlp found, version: {version}")
                return True
            else:
                logger.warning("yt-dlp command failed")
                return False
                
        except FileNotFoundError:
            logger.warning("yt-dlp not found in PATH")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("yt-dlp version check timed out")
            return False
        except Exception as e:
            logger.error(f"Error checking yt-dlp: {e}")
            return False
    
    def get_yt_dlp_path(self) -> Optional[str]:
        """Get the path to yt-dlp executable.
        
        Returns:
            Path to yt-dlp if found, None otherwise
        """
        if self._yt_dlp_path:
            return self._yt_dlp_path
        
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["where", "yt-dlp"],
                    capture_output=True,
                    text=True,
                    timeout=self.VERSION_TIMEOUT
                )
            else:
                result = subprocess.run(
                    ["which", "yt-dlp"],
                    capture_output=True,
                    text=True,
                    timeout=self.VERSION_TIMEOUT
                )
            
            if result.returncode == 0:
                self._yt_dlp_path = result.stdout.strip().split('\n')[0]
                logger.debug(f"yt-dlp path: {self._yt_dlp_path}")
                return self._yt_dlp_path
            
        except Exception as e:
            logger.error(f"Error finding yt-dlp path: {e}")
        
        return None
    
    def get_yt_dlp_version(self) -> Optional[str]:
        """Get the installed yt-dlp version.
        
        Returns:
            Version string or None if not installed
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=self.VERSION_TIMEOUT
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
                
        except Exception as e:
            logger.error(f"Error getting yt-dlp version: {e}")
        
        return None
    
    def fetch_metadata(self, url: str) -> dict[str, Any]:
        """Fetch video metadata from YouTube.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with keys:
            - title: Video title
            - duration: Duration in seconds
            - formats: List of available quality options
            - thumbnail_url: URL to thumbnail image
            - uploader: Channel name
            - view_count: Number of views
            - error: Error message if failed (only present on error)
            
        Example:
            >>> wrapper = YTDLPWrapper()
            >>> metadata = wrapper.fetch_metadata("https://youtu.be/dQw4w9WgXcQ")
            >>> print(metadata["title"])
            'Rick Astley - Never Gonna Give You Up'
        """
        if not self.validate_url(url):
            return {"error": "Invalid YouTube URL"}
        
        try:
            logger.info(f"Fetching metadata for: {url}")
            
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-warnings", "--no-playlist", url],
                capture_output=True,
                text=True,
                timeout=self.METADATA_TIMEOUT
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"yt-dlp metadata fetch failed: {error_msg}")
                
                # Parse common errors for user-friendly messages
                if "Video unavailable" in error_msg or "Private video" in error_msg:
                    return {"error": "This video is not available. It may be private or deleted."}
                elif "Sign in" in error_msg or "age" in error_msg.lower():
                    return {"error": "This video requires sign-in or age verification."}
                else:
                    return {"error": "Could not fetch video info. Check your connection."}
            
            # Parse JSON response
            data = json.loads(result.stdout)
            
            # Extract available formats/qualities
            formats = self._extract_available_qualities(data.get("formats", []))
            
            metadata = {
                "title": data.get("title", "Unknown Title"),
                "duration": data.get("duration", 0),
                "formats": formats,
                "thumbnail_url": data.get("thumbnail", ""),
                "uploader": data.get("uploader", "Unknown"),
                "view_count": data.get("view_count", 0),
                "description": data.get("description", "")[:500],  # Truncate
            }
            
            logger.info(f"Metadata fetched: {metadata['title']} ({metadata['duration']}s)")
            return metadata
            
        except subprocess.TimeoutExpired:
            logger.error("Metadata fetch timed out")
            return {"error": "Request timed out. Check your internet connection."}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse yt-dlp JSON: {e}")
            return {"error": "Could not parse video information."}
        except Exception as e:
            logger.error(f"Metadata fetch error: {e}")
            return {"error": "Could not fetch video info. Please try again."}
    
    def _extract_available_qualities(self, formats: list[dict]) -> list[str]:
        """Extract available video qualities from format list.
        
        Args:
            formats: List of format dictionaries from yt-dlp
            
        Returns:
            List of quality strings like ["best", "1080p", "720p", "480p", "360p"]
        """
        available = set()
        
        for fmt in formats:
            height = fmt.get("height")
            if height:
                if height >= 1080:
                    available.add("1080p")
                if height >= 720:
                    available.add("720p")
                if height >= 480:
                    available.add("480p")
                if height >= 360:
                    available.add("360p")
        
        # Always include "best" option
        result = ["best"]
        
        # Add qualities in descending order
        for quality in ["1080p", "720p", "480p", "360p"]:
            if quality in available:
                result.append(quality)
        
        return result
    
    def build_download_command(
        self,
        url: str,
        format_type: str,
        quality: str,
        output_path: str
    ) -> list[str]:
        """Build yt-dlp command for downloading.
        
        Args:
            url: YouTube video URL
            format_type: "video" or "audio"
            quality: Quality string like "best", "720p", etc.
            output_path: Full path including filename for output
            
        Returns:
            List of command arguments for subprocess
            
        Example:
            >>> wrapper = YTDLPWrapper()
            >>> cmd = wrapper.build_download_command(
            ...     "https://youtu.be/xyz",
            ...     "video",
            ...     "720p",
            ...     "/downloads/video.mp4"
            ... )
            >>> print(cmd)
            ['yt-dlp', '-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]', ...]
        """
        cmd = ["yt-dlp"]
        
        # Add format selection
        if format_type == "audio":
            # Audio only - extract and convert to MP3
            cmd.extend([
                "-f", "bestaudio/best",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
            ])
        else:
            # Video - select quality
            format_spec = self._get_format_spec(quality)
            cmd.extend(["-f", format_spec])
            
            # Merge to MP4 container
            cmd.extend(["--merge-output-format", "mp4"])
        
        # Output path
        cmd.extend(["-o", output_path])
        
        # Progress output for parsing
        cmd.extend([
            "--newline",  # Print progress on new lines
            "--no-warnings",
            "--no-playlist",  # Single video only
        ])
        
        # Add URL last
        cmd.append(url)
        
        logger.debug(f"Built command: {' '.join(cmd)}")
        return cmd
    
    def _get_format_spec(self, quality: str) -> str:
        """Get yt-dlp format specification for quality.
        
        Args:
            quality: Quality string like "best", "720p", etc.
            
        Returns:
            yt-dlp format specification string
        """
        quality_map = {
            "best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }
        
        return quality_map.get(quality, quality_map["best"])
    
    def check_ffmpeg_installed(self) -> bool:
        """Check if ffmpeg is installed (needed for audio extraction).
        
        Returns:
            True if ffmpeg is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=self.VERSION_TIMEOUT
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception:
            return False
