"""Transcription module for yt-dlp GUI Desktop App.

Supports:
1. Groq Whisper API (primary, fast, free tier)
2. Local Whisper (fallback, offline)
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# Groq API endpoint for Whisper
GROQ_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class Transcriber:
    """Handles audio/video transcription using Groq API or local Whisper."""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize transcriber.
        
        Args:
            groq_api_key: Groq API key. If None, will try env var GROQ_API_KEY.
        """
        self._groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        self._local_whisper_available: Optional[bool] = None
    
    def set_groq_api_key(self, api_key: str) -> None:
        """Set Groq API key."""
        self._groq_api_key = api_key
        logger.info("Groq API key configured")
    
    def has_groq_api_key(self) -> bool:
        """Check if Groq API key is configured."""
        return bool(self._groq_api_key)
    
    def check_local_whisper(self) -> bool:
        """Check if local Whisper is available."""
        if self._local_whisper_available is not None:
            return self._local_whisper_available
        
        try:
            import whisper
            self._local_whisper_available = True
            logger.info("Local Whisper available")
        except ImportError:
            self._local_whisper_available = False
            logger.info("Local Whisper not installed")
        
        return self._local_whisper_available
    
    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Transcribe audio/video file.
        
        Args:
            file_path: Path to audio/video file
            language: Optional language code (e.g., 'en', 'es')
            progress_callback: Optional callback for progress updates
            
        Returns:
            dict with keys:
            - text: Transcribed text
            - language: Detected language
            - duration: Audio duration in seconds
            - error: Error message (only if failed)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # Extract audio if video file
        audio_path = self._extract_audio(file_path, progress_callback)
        if audio_path is None:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 25:
                return {"error": f"File too large ({file_size_mb:.1f}MB). Groq limit is 25MB.\n\nInstall ffmpeg to extract audio from large videos:\n  winget install ffmpeg"}
            return {"error": "Failed to extract audio from video"}
        
        try:
            # Try Groq API first (faster)
            if self._groq_api_key:
                if progress_callback:
                    progress_callback("Transcribing with Groq API...")
                result = self._transcribe_groq(audio_path, language)
                if "error" not in result:
                    return result
                logger.warning(f"Groq API failed: {result['error']}, trying local Whisper")
            
            # Fallback to local Whisper
            if self.check_local_whisper():
                if progress_callback:
                    progress_callback("Transcribing with local Whisper...")
                return self._transcribe_local(audio_path, language, progress_callback)
            
            # No transcription method available
            if not self._groq_api_key:
                return {"error": "No Groq API key configured. Please add your API key in Settings."}
            return {"error": "Transcription failed. Please check your API key."}
            
        finally:
            # Clean up temp audio file if we created one
            if audio_path != file_path and audio_path.exists():
                try:
                    audio_path.unlink()
                except Exception:
                    pass
    
    def _extract_audio(
        self,
        file_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Path]:
        """Extract audio from video file using ffmpeg or fallback methods.
        
        Returns path to audio file (may be same as input if already audio).
        """
        # Check if already an audio file
        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
        if file_path.suffix.lower() in audio_extensions:
            return file_path
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # If file is small enough, use it directly (Groq accepts video up to 25MB)
        if file_size_mb <= 25:
            logger.info(f"Using video file directly ({file_size_mb:.1f}MB <= 25MB limit)")
            return file_path
        
        if progress_callback:
            progress_callback("Extracting audio (file > 25MB)...")
        
        # Create temp file for audio
        temp_audio = Path(tempfile.gettempdir()) / f"yt-dlp-audio-{file_path.stem}.mp3"
        
        # Try ffmpeg first (most reliable for local files)
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-i", str(file_path),
                    "-vn",  # No video
                    "-acodec", "libmp3lame",
                    "-ab", "64k",  # Lower bitrate to reduce file size
                    "-ar", "16000",  # 16kHz sample rate (good for speech)
                    "-ac", "1",  # Mono
                    "-y",  # Overwrite
                    str(temp_audio)
                ],
                capture_output=True,
                text=True,
                timeout=600  # 10 min timeout for large files
            )
            if result.returncode == 0 and temp_audio.exists():
                audio_size_mb = temp_audio.stat().st_size / (1024 * 1024)
                logger.info(f"Audio extracted with ffmpeg: {temp_audio} ({audio_size_mb:.1f}MB)")
                if audio_size_mb <= 25:
                    return temp_audio
                else:
                    logger.warning(f"Extracted audio still too large: {audio_size_mb:.1f}MB")
                    temp_audio.unlink()
        except FileNotFoundError:
            logger.warning("ffmpeg not found - cannot extract audio from large video")
        except subprocess.TimeoutExpired:
            logger.warning("ffmpeg audio extraction timed out")
        except Exception as e:
            logger.error(f"ffmpeg error: {e}")
        
        # No ffmpeg available - provide helpful error
        logger.error(f"Cannot transcribe: file is {file_size_mb:.1f}MB (limit 25MB) and ffmpeg not installed")
        return None
    
    def _transcribe_groq(
        self,
        audio_path: Path,
        language: Optional[str] = None
    ) -> dict:
        """Transcribe using Groq Whisper API."""
        import requests
        
        try:
            # Check file size (Groq limit is 25MB)
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 25:
                return {"error": f"File too large for Groq API ({file_size_mb:.1f}MB > 25MB limit)"}
            
            headers = {
                "Authorization": f"Bearer {self._groq_api_key}"
            }
            
            data = {
                "model": "whisper-large-v3",
                "response_format": "verbose_json"
            }
            
            if language:
                data["language"] = language
            
            with open(audio_path, "rb") as f:
                files = {"file": (audio_path.name, f, "audio/mpeg")}
                
                response = requests.post(
                    GROQ_API_URL,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "text": result.get("text", ""),
                    "language": result.get("language", "unknown"),
                    "duration": result.get("duration", 0)
                }
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                logger.error(f"Groq API error: {error_msg}")
                return {"error": f"Groq API error: {error_msg}"}
                
        except requests.exceptions.Timeout:
            return {"error": "Groq API request timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.exception(f"Groq transcription error: {e}")
            return {"error": str(e)}
    
    def _transcribe_local(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Transcribe using local Whisper model."""
        try:
            import whisper
            
            if progress_callback:
                progress_callback("Loading Whisper model...")
            
            # Use base model for balance of speed/accuracy
            model = whisper.load_model("base")
            
            if progress_callback:
                progress_callback("Transcribing audio...")
            
            result = model.transcribe(
                str(audio_path),
                language=language,
                fp16=False  # CPU compatibility
            )
            
            return {
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "duration": 0  # Local whisper doesn't return duration easily
            }
            
        except Exception as e:
            logger.exception(f"Local Whisper error: {e}")
            return {"error": str(e)}
    
    def save_transcript(
        self,
        text: str,
        output_path: str,
        format: str = "txt"
    ) -> bool:
        """Save transcript to file.
        
        Args:
            text: Transcript text
            output_path: Path to save (without extension)
            format: Output format ('txt', 'srt', 'json')
            
        Returns:
            True if saved successfully
        """
        output_path = Path(output_path)
        
        try:
            if format == "txt":
                file_path = output_path.with_suffix(".txt")
                file_path.write_text(text, encoding="utf-8")
            elif format == "json":
                file_path = output_path.with_suffix(".json")
                file_path.write_text(
                    json.dumps({"transcript": text}, indent=2),
                    encoding="utf-8"
                )
            else:
                file_path = output_path.with_suffix(f".{format}")
                file_path.write_text(text, encoding="utf-8")
            
            logger.info(f"Transcript saved: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            return False
