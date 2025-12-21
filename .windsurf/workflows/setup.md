---
description: Set up yt-dlp GUI on a new computer
---

# Setup yt-dlp GUI

This workflow sets up the yt-dlp GUI desktop app on a new computer.

## Steps

1. Check if dependencies are installed by looking for a virtual environment or checking if PyQt6 is importable:
```bash
python -c "import PyQt6" 2>&1
```

2. If dependencies are missing, install them:
// turbo
```bash
pip install -r requirements.txt
```

3. Check if ffmpeg is installed:
```bash
ffmpeg -version 2>&1
```

4. If ffmpeg is not found, install it (Windows):
```bash
winget install ffmpeg
```
Or on macOS:
```bash
brew install ffmpeg
```

5. Run the application:
// turbo
```bash
python run.py
```

6. Remind user to configure Groq API key in Settings if they want transcription features.

## Notes
- The Groq API key is stored locally in `%APPDATA%\yt-dlp-gui\config.json` (Windows) or `~/.config/yt-dlp-gui/config.json` (macOS/Linux)
- ffmpeg is optional but required for transcribing videos larger than 25MB
- Get a free Groq API key at https://console.groq.com/keys
