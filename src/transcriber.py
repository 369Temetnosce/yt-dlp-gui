"""Transcription module for yt-dlp GUI Desktop App.

Supports:
1. Groq Whisper API (primary, fast, free tier)
2. Local Whisper (fallback, offline)

Optimal audio settings for Whisper (based on research):
- Bitrate: 32 kbps (no quality loss, Whisper downsamples internally)
- Sample Rate: 16 kHz (Whisper's native rate)
- Channels: Mono
- Format: MP3

For long files, audio is split into chunks and transcribed separately.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Callable, List

logger = logging.getLogger(__name__)

# Optimal settings for Whisper transcription
WHISPER_BITRATE = "32k"  # 32 kbps - optimal for speech, no quality loss
WHISPER_SAMPLE_RATE = "16000"  # 16 kHz - Whisper's native sample rate
WHISPER_CHANNELS = "1"  # Mono
CHUNK_DURATION_SECONDS = 600  # 10 minutes per chunk (~2.4MB at 32kbps)

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
        self._audio_chunks: List[Path] = []  # For chunked processing
    
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
        progress_callback: Optional[Callable[[str], None]] = None,
        include_timestamps: bool = False
    ) -> dict:
        """Transcribe audio/video file.
        
        Args:
            file_path: Path to audio/video file
            language: Optional language code (e.g., 'en', 'es')
            progress_callback: Optional callback for progress updates
            include_timestamps: If True, include timestamps in output
            
        Returns:
            dict with keys:
            - text: Transcribed text (plain)
            - timestamped_text: Text with timestamps (if include_timestamps=True)
            - language: Detected language
            - duration: Audio duration in seconds
            - error: Error message (only if failed)
        """
        self._include_timestamps = include_timestamps
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        # Extract audio if video file
        audio_path = self._extract_audio(file_path, progress_callback)
        
        # Check if we have chunks for long files
        if self._audio_chunks:
            return self._transcribe_chunks(language, progress_callback)
        
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
                result = self._transcribe_groq(audio_path, language, include_timestamps)
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
    
    def _transcribe_chunks(
        self,
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Transcribe multiple audio chunks and combine results."""
        if not self._groq_api_key:
            return {"error": "No Groq API key configured. Please add your API key in Settings."}
        
        all_text = []
        all_timestamped_text = []
        detected_language = None
        total_chunks = len(self._audio_chunks)
        include_timestamps = getattr(self, '_include_timestamps', False)
        
        try:
            for i, chunk_path in enumerate(self._audio_chunks):
                if progress_callback:
                    progress_callback(f"Transcribing chunk {i+1}/{total_chunks}...")
                
                # Calculate time offset for this chunk
                time_offset = i * CHUNK_DURATION_SECONDS
                
                result = self._transcribe_groq(chunk_path, language, include_timestamps, time_offset)
                
                if "error" in result:
                    logger.error(f"Chunk {i+1} failed: {result['error']}")
                    return {"error": f"Failed on chunk {i+1}/{total_chunks}: {result['error']}"}
                
                all_text.append(result.get("text", ""))
                if include_timestamps and "timestamped_text" in result:
                    all_timestamped_text.append(result["timestamped_text"])
                
                if not detected_language:
                    detected_language = result.get("language")
                
                logger.info(f"Chunk {i+1}/{total_chunks} transcribed successfully")
            
            # Combine all transcripts
            combined_text = "\n\n".join(all_text)
            logger.info(f"Combined {total_chunks} chunks into {len(combined_text)} characters")
            
            response = {
                "text": combined_text,
                "language": detected_language or "unknown",
                "duration": 0,
                "chunks": total_chunks
            }
            
            if include_timestamps and all_timestamped_text:
                response["timestamped_text"] = "\n".join(all_timestamped_text)
            
            return response
            
        finally:
            # Clean up chunk files
            for chunk_path in self._audio_chunks:
                try:
                    chunk_path.unlink()
                except Exception:
                    pass
            # Try to remove the temp directory
            if self._audio_chunks:
                try:
                    self._audio_chunks[0].parent.rmdir()
                except Exception:
                    pass
            self._audio_chunks = []
    
    def _extract_audio(
        self,
        file_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Path]:
        """Extract audio from video file using ffmpeg.
        
        For short files (<25MB), returns single audio file.
        For long files, returns None and sets self._audio_chunks for chunked processing.
        
        Returns path to audio file (may be same as input if already audio).
        """
        self._audio_chunks = []  # Reset chunks
        
        # Check if already an audio file
        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
        if file_path.suffix.lower() in audio_extensions:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb <= 25:
                return file_path
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # If file is small enough, use it directly (Groq accepts video up to 25MB)
        if file_size_mb <= 25:
            logger.info(f"Using video file directly ({file_size_mb:.1f}MB <= 25MB limit)")
            return file_path
        
        # Get duration to determine if we need chunking
        duration_seconds = self._get_duration(file_path)
        if not duration_seconds:
            logger.error("Could not determine file duration")
            return None
        
        # Calculate if single file extraction would work
        # At 32kbps mono, 1 minute ≈ 0.24MB, so 25MB ≈ 104 minutes
        max_duration_for_single = 100 * 60  # 100 minutes to be safe
        
        if duration_seconds <= max_duration_for_single:
            # Single file extraction
            if progress_callback:
                progress_callback("Extracting audio...")
            return self._extract_single_audio(file_path, progress_callback)
        else:
            # Need chunked extraction for very long files
            if progress_callback:
                progress_callback(f"Long video ({duration_seconds/60:.0f} min), extracting in chunks...")
            return self._extract_chunked_audio(file_path, duration_seconds, progress_callback)
    
    def _extract_single_audio(
        self,
        file_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Path]:
        """Extract audio as a single file using optimal Whisper settings."""
        temp_audio = Path(tempfile.gettempdir()) / f"yt-dlp-audio-{file_path.stem}.mp3"
        
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-i", str(file_path),
                    "-vn",  # No video
                    "-acodec", "libmp3lame",
                    "-ab", WHISPER_BITRATE,
                    "-ar", WHISPER_SAMPLE_RATE,
                    "-ac", WHISPER_CHANNELS,
                    "-y",  # Overwrite
                    str(temp_audio)
                ],
                capture_output=True,
                text=True,
                timeout=1200
            )
            if result.returncode == 0 and temp_audio.exists():
                audio_size_mb = temp_audio.stat().st_size / (1024 * 1024)
                logger.info(f"Audio extracted: {temp_audio} ({audio_size_mb:.1f}MB)")
                if audio_size_mb <= 25:
                    return temp_audio
                else:
                    logger.warning(f"Audio too large ({audio_size_mb:.1f}MB), will use chunked processing")
                    temp_audio.unlink()
                    return None
        except FileNotFoundError:
            logger.error("ffmpeg not found")
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg timed out")
        except Exception as e:
            logger.error(f"ffmpeg error: {e}")
        return None
    
    def _extract_chunked_audio(
        self,
        file_path: Path,
        duration_seconds: float,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[Path]:
        """Extract audio in chunks for very long files.
        
        Creates multiple audio files and stores paths in self._audio_chunks.
        Returns None to signal chunked processing is needed.
        """
        num_chunks = int(duration_seconds / CHUNK_DURATION_SECONDS) + 1
        logger.info(f"Splitting {duration_seconds/60:.1f} min audio into {num_chunks} chunks")
        
        self._audio_chunks = []
        temp_dir = Path(tempfile.gettempdir()) / f"yt-dlp-chunks-{file_path.stem}"
        temp_dir.mkdir(exist_ok=True)
        
        for i in range(num_chunks):
            start_time = i * CHUNK_DURATION_SECONDS
            chunk_path = temp_dir / f"chunk_{i:03d}.mp3"
            
            if progress_callback:
                progress_callback(f"Extracting chunk {i+1}/{num_chunks}...")
            
            try:
                result = subprocess.run(
                    [
                        "ffmpeg", "-i", str(file_path),
                        "-ss", str(start_time),
                        "-t", str(CHUNK_DURATION_SECONDS),
                        "-vn",
                        "-acodec", "libmp3lame",
                        "-ab", WHISPER_BITRATE,
                        "-ar", WHISPER_SAMPLE_RATE,
                        "-ac", WHISPER_CHANNELS,
                        "-y",
                        str(chunk_path)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0 and chunk_path.exists():
                    chunk_size_mb = chunk_path.stat().st_size / (1024 * 1024)
                    logger.info(f"Chunk {i+1}: {chunk_size_mb:.1f}MB")
                    self._audio_chunks.append(chunk_path)
                else:
                    logger.error(f"Failed to extract chunk {i+1}")
                    break
            except Exception as e:
                logger.error(f"Error extracting chunk {i+1}: {e}")
                break
        
        if len(self._audio_chunks) == num_chunks:
            logger.info(f"Successfully extracted {num_chunks} audio chunks")
            return None  # Signal to use chunked transcription
        else:
            # Cleanup on failure
            for chunk in self._audio_chunks:
                try:
                    chunk.unlink()
                except:
                    pass
            self._audio_chunks = []
            return None
    
    def _get_duration(self, file_path: Path) -> Optional[float]:
        """Get duration of media file in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(file_path)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
        return None
    
    def _transcribe_groq(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        include_timestamps: bool = False,
        time_offset: float = 0.0
    ) -> dict:
        """Transcribe using Groq Whisper API.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code
            include_timestamps: If True, include segment timestamps in output
            time_offset: Offset to add to timestamps (for chunked transcription)
        """
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
                
                # Build response
                response_data = {
                    "text": result.get("text", ""),
                    "language": result.get("language", "unknown"),
                    "duration": result.get("duration", 0)
                }
                
                # Include timestamps if requested
                if include_timestamps and "segments" in result:
                    segments = result["segments"]
                    timestamped_text = self._format_timestamps(segments, time_offset)
                    response_data["timestamped_text"] = timestamped_text
                    response_data["segments"] = segments
                
                return response_data
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
    
    def _format_timestamps(self, segments: list, time_offset: float = 0.0) -> str:
        """Format segments with timestamps.
        
        Args:
            segments: List of segment dicts with 'start', 'end', 'text'
            time_offset: Offset to add to all timestamps (for chunked files)
            
        Returns:
            Formatted string with timestamps like "[00:01:23] Text here"
        """
        lines = []
        for segment in segments:
            start = segment.get("start", 0) + time_offset
            text = segment.get("text", "").strip()
            if text:
                timestamp = self._format_time(start)
                lines.append(f"[{timestamp}] {text}")
        return "\n".join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS or MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
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
