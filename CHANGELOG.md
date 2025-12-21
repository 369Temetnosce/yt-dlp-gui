# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-12-21

### Added
- **Core Features**
  - YouTube video/audio download with quality selection
  - Real-time progress display (percentage, speed, ETA)
  - Format selection (Video MP4 / Audio MP3)
  - Quality presets (Best, 1080p, 720p, 480p, 360p)

- **Browser Cookie Support**
  - Auto-detection of available browsers (Chrome, Firefox, Edge, Brave)
  - DPAPI encryption detection for Chrome on Windows
  - Automatic fallback to working browser

- **Transcription (Groq Whisper)**
  - Integration with Groq's Whisper API
  - Chunked processing for videos of any length
  - Optional timestamps in output (`[HH:MM:SS] text`)
  - Browse and transcribe any existing video/audio file
  - Optimal audio extraction settings (32kbps, 16kHz, mono)

- **UI/UX**
  - Modern PyQt6 interface
  - Settings dialog for API key configuration
  - Open Folder button for quick access
  - Transcribe button with options dialog
  - Download history logging

- **Smart Defaults**
  - Works without ffmpeg (uses pre-muxed formats)
  - Remembers user preferences
  - Automatic output filename generation

### Technical
- yt-dlp wrapper with subprocess management
- QThread-based download manager
- JSON-based configuration persistence
- Comprehensive logging to app.log

## Upcoming
- Web version for Railway deployment
- Batch download support
- Playlist support
