# yt-dlp GUI Desktop App

A modern, user-friendly desktop application for downloading YouTube videos and audio with built-in transcription support.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### 🎬 Video/Audio Download
- Download videos in multiple quality options (Best, 1080p, 720p, 480p, 360p)
- Extract audio-only (MP3)
- Real-time progress display with speed and ETA
- Automatic browser cookie support for age-restricted videos
- Smart format selection (works with or without ffmpeg)

### 🎤 Transcription (NEW!)
- **Groq Whisper API** integration for fast, accurate transcription
- **Chunked processing** for long videos (any length supported!)
- **Optional timestamps** in output (e.g., `[00:01:23] text`)
- Transcribe downloaded videos or browse for any existing file
- Automatic audio extraction at optimal settings (32kbps, 16kHz mono)

### 🔧 Smart Features
- Auto-detects Chrome DPAPI encryption issues and falls back to Firefox
- Works without ffmpeg (uses pre-muxed formats)
- Remembers your preferences (quality, output folder, timestamps)
- Download history tracking

## Installation

### Prerequisites
- Python 3.9 or higher
- Windows/macOS/Linux

### Quick Start

```bash
# Clone the repository
git clone https://github.com/369Temetnosce/yt-dlp-gui.git
cd yt-dlp-gui

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

### Optional: Install ffmpeg (recommended)
ffmpeg enables:
- Best quality downloads (separate video+audio streams merged)
- Transcription of large video files (>25MB)

```bash
# Windows
winget install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## Usage

### Downloading Videos
1. Paste a YouTube URL
2. Select format (Video/Audio) and quality
3. Click **Download**

### Transcribing Videos
1. Click **🎤 Transcribe**
2. Select a file (or use last downloaded)
3. Check "Include timestamps" if desired
4. Click **OK** to start

### Settings
Click **⚙ Settings** to configure:
- **Groq API Key** - Required for transcription ([Get free key](https://console.groq.com/keys))

## Configuration

Settings are stored in:
- **Windows:** `%APPDATA%\yt-dlp-gui\config.json`
- **macOS/Linux:** `~/.config/yt-dlp-gui/config.json`

## Project Structure

```
yt-dlp-gui/
├── src/
│   ├── main.py              # Application entry point
│   ├── main_window.py       # PyQt6 UI
│   ├── download_manager.py  # Download threading
│   ├── ytdlp_wrapper.py     # yt-dlp subprocess wrapper
│   ├── transcriber.py       # Groq Whisper transcription
│   ├── config_manager.py    # Settings persistence
│   └── utils.py             # Helper functions
├── resources/
│   └── styles.qss           # Qt stylesheet
├── requirements.txt
├── run.py                   # Convenience launcher
└── README.md
```

## Technical Details

### Transcription Settings (Optimized for Whisper)
Based on research, these settings provide optimal quality with minimal file size:
- **Bitrate:** 32 kbps (no quality loss for speech)
- **Sample Rate:** 16 kHz (Whisper's native rate)
- **Channels:** Mono
- **Chunk Duration:** 10 minutes (~2.4MB per chunk)

### Browser Cookie Support
The app automatically detects available browsers for cookie extraction:
1. Checks Chrome (skips if DPAPI encrypted on Windows)
2. Falls back to Firefox, Edge, Brave

## Roadmap

- [x] Basic video/audio download
- [x] Browser cookie support
- [x] Groq Whisper transcription
- [x] Chunked transcription for long videos
- [x] Timestamp support
- [ ] Web version (Railway deployment)
- [ ] Batch downloads
- [ ] Playlist support

## License

MIT License - see LICENSE file for details.

## Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video download engine
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Groq](https://groq.com) - Whisper API for transcription
- [ffmpeg](https://ffmpeg.org) - Audio/video processing
