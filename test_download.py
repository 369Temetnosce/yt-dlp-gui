#!/usr/bin/env python3
"""Quick test script to verify download functionality."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ytdlp_wrapper import YTDLPWrapper
from src.download_manager import DownloadManager
from src.utils import setup_logging, get_file_size_mb

# Setup
setup_logging()
url = "https://youtu.be/-Tgc_9uYJLI"
output_path = Path.home() / "Downloads" / "yt-dlp"
output_path.mkdir(parents=True, exist_ok=True)

# Clean up any existing files
for f in output_path.glob("*"):
    f.unlink()

print("=" * 50)
print("yt-dlp GUI Download Test")
print("=" * 50)

# Test 1: YTDLPWrapper
print("\n[1] Testing YTDLPWrapper...")
wrapper = YTDLPWrapper()

print(f"  - yt-dlp installed: {wrapper.check_yt_dlp_installed()}")
print(f"  - yt-dlp version: {wrapper.get_yt_dlp_version()}")
print(f"  - ffmpeg installed: {wrapper.check_ffmpeg_installed()}")
print(f"  - Browser for cookies: {wrapper.get_browser()}")
print(f"  - URL valid: {wrapper.validate_url(url)}")

# Test 2: Metadata fetch
print("\n[2] Fetching metadata...")
metadata = wrapper.fetch_metadata(url)
if "error" in metadata:
    print(f"  ERROR: {metadata['error']}")
else:
    print(f"  - Title: {metadata.get('title', 'N/A')}")
    print(f"  - Duration: {metadata.get('duration', 0)}s")
    print(f"  - Formats: {metadata.get('formats', [])}")

# Test 3: Build command
print("\n[3] Building download command...")
filename = "test_video.mp4"
cmd = wrapper.build_download_command(url, "video", "best", str(output_path / filename))
print(f"  Command: {' '.join(cmd[:6])}...")

# Test 4: Direct download test
print("\n[4] Testing direct download...")
import subprocess

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=120
)

if result.returncode == 0:
    file_path = output_path / filename
    if file_path.exists():
        size = get_file_size_mb(file_path)
        print(f"  ✓ SUCCESS! Downloaded: {filename} ({size} MB)")
    else:
        # Check for any mp4 files
        mp4_files = list(output_path.glob("*.mp4"))
        if mp4_files:
            size = get_file_size_mb(mp4_files[0])
            print(f"  ✓ SUCCESS! Downloaded: {mp4_files[0].name} ({size} MB)")
        else:
            print(f"  ✗ File not found at expected location")
else:
    print(f"  ✗ FAILED with code {result.returncode}")
    if result.stderr:
        print(f"  Error: {result.stderr[:200]}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)
