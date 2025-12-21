---
description: Auto-setup when starting work on this project (run on new computer)
---

# Start Working - yt-dlp GUI

When the user says "start working" or opens this project on a new computer, follow these steps:

## 1. Check if this is a new computer setup

Check if dependencies are installed:
```bash
python -c "import PyQt6; print('Dependencies OK')"
```

## 2. If dependencies are missing, install them

// turbo
```bash
pip install -r requirements.txt
```

## 3. Check ffmpeg availability

```bash
ffmpeg -version
```

If ffmpeg is not found, inform the user:
- **Windows:** `winget install ffmpeg`
- **macOS:** `brew install ffmpeg`
- ffmpeg is optional but required for transcribing videos >25MB

## 4. Pull latest changes

// turbo
```bash
git pull
```

## 5. Run the application

// turbo
```bash
python run.py
```

## 6. Check Groq API key

Remind user: If transcription doesn't work, click **⚙ Settings** and enter your Groq API key.
Get a free key at: https://console.groq.com/keys

## Quick Reference

| Feature | Requirement |
|---------|-------------|
| Video Download | yt-dlp (bundled) |
| Audio Download | yt-dlp (bundled) |
| Transcription | Groq API key |
| Large File Transcription | ffmpeg + Groq API key |
