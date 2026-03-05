from __future__ import annotations

import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def download_video(url: str, output_dir: Path, ffmpeg_location: str | None = None) -> Path:
    """Download a video using yt-dlp and return the path to the downloaded file."""
    output_template = str(output_dir / "%(title).50s.%(ext)s")
    cmd = ["yt-dlp", "-o", output_template, "--no-playlist"]
    if ffmpeg_location:
        cmd.extend(["--ffmpeg-location", ffmpeg_location])
    cmd.append(url)

    log.debug("Running: %s", cmd)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        log.error("yt-dlp stderr: %s", result.stderr)
        raise RuntimeError(f"yt-dlp failed (exit {result.returncode}): {result.stderr.strip()}")

    # Find the downloaded file (most recently modified in output_dir)
    files = sorted(output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    media_files = [f for f in files if f.is_file() and f.suffix != ".wav"]
    if not media_files:
        raise RuntimeError("yt-dlp produced no output file")
    log.debug("Downloaded: %s", media_files[0])
    return media_files[0]
