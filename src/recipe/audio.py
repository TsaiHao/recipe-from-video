from __future__ import annotations

import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def extract_audio(
    input_path: Path,
    output_dir: Path,
    ffmpeg_location: str | None = None,
) -> Path:
    """Extract audio from a media file as 16kHz mono WAV."""
    output_path = output_dir / f"{input_path.stem}.wav"
    ffmpeg = ffmpeg_location or "ffmpeg"
    cmd = [
        ffmpeg, "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        str(output_path),
    ]

    log.debug("Running: %s", cmd)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        log.error("ffmpeg stderr: %s", result.stderr)
        raise RuntimeError(f"ffmpeg failed (exit {result.returncode}): {result.stderr.strip()}")

    log.debug("Extracted audio: %s", output_path)
    return output_path
