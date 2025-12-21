# yt-dlp Command Reference

Common yt-dlp commands used in this project.

## Get Video Info (JSON)

```bash
# Full metadata as JSON
yt-dlp -j --no-download "URL"

# Just format list
yt-dlp -F "URL"
```

## Download Commands

```bash
# Best quality (video + audio merged)
yt-dlp -f "bestvideo+bestaudio/best" -o "%(title)s.%(ext)s" "URL"

# Specific format by ID
yt-dlp -f 22 -o "output.mp4" "URL"

# Audio only (best quality)
yt-dlp -f "bestaudio" -x --audio-format mp3 -o "%(title)s.%(ext)s" "URL"

# 720p max
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" "URL"
```

## Progress Output

Use `--newline` for parseable progress:

```bash
yt-dlp --newline -o "video.mp4" "URL"
```

Output format:
```
[download] Destination: video.mp4
[download]  10.0% of 50.00MiB at 2.00MiB/s ETA 00:20
[download]  50.0% of 50.00MiB at 2.50MiB/s ETA 00:10
[download] 100.0% of 50.00MiB at 3.00MiB/s ETA 00:00
[download] 100% of 50.00MiB in 00:16
```

## Useful Flags

| Flag | Purpose |
|------|---------|
| `--no-download` | Don't download, just get info |
| `-j` | Output info as JSON |
| `-F` | List available formats |
| `-f FORMAT` | Select format |
| `-o TEMPLATE` | Output filename template |
| `--newline` | Progress on separate lines |
| `-x` | Extract audio |
| `--audio-format FORMAT` | Convert audio to format |
| `--embed-thumbnail` | Embed thumbnail in file |
| `--add-metadata` | Add metadata to file |

## Output Templates

```bash
# Title with extension
"%(title)s.%(ext)s"

# Custom folder
"downloads/%(title)s.%(ext)s"

# With uploader
"%(uploader)s - %(title)s.%(ext)s"

# Sanitized title (safe for filenames)
"%(title).100s.%(ext)s"
```

## Error Handling

Common exit codes:
- `0` - Success
- `1` - General error
- `2` - Error in options

Common errors in stderr:
- `ERROR: Video unavailable`
- `ERROR: is not a valid URL`
- `ERROR: Unable to extract`
