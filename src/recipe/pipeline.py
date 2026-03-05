from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.status import Status

from recipe.audio import extract_audio
from recipe.download import download_video
from recipe.llm import create_llm_provider
from recipe.models import SYSTEM_PROMPT, Recipe, recipe_to_markdown
from recipe.stt import create_stt_engine

log = logging.getLogger(__name__)
console = Console()

CACHE_DIR = Path("./cache")


def _is_url(source: str) -> bool:
    try:
        parsed = urlparse(source)
        return parsed.scheme in ("http", "https")
    except Exception:
        return False


def _cache_key(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def _find_media(cache_dir: Path) -> Path | None:
    """Find a cached media file (non-.wav, non-.txt) in the cache dir."""
    for f in cache_dir.iterdir():
        if f.is_file() and f.suffix not in (".wav", ".txt"):
            return f
    return None


def _find_audio(cache_dir: Path) -> Path | None:
    """Find a cached .wav file in the cache dir."""
    wavs = list(cache_dir.glob("*.wav"))
    return wavs[0] if wavs else None


def _find_transcript(cache_dir: Path) -> Path | None:
    """Find a cached transcript .txt file in the cache dir."""
    txts = list(cache_dir.glob("*.txt"))
    return txts[0] if txts else None


def run_pipeline(args: argparse.Namespace) -> None:
    source: str = args.source
    use_cache = not args.no_cache

    # Determine cache directory
    key = _cache_key(source)
    cache_dir = CACHE_DIR / key
    cache_dir.mkdir(parents=True, exist_ok=True)
    log.debug("Cache directory: %s (key=%s)", cache_dir, key)

    # Step 1: Obtain media file
    media_path = _find_media(cache_dir) if use_cache else None
    if media_path:
        console.print(f"[dim]Cached video:[/dim] {media_path.name}")
    elif _is_url(source):
        with Status("[bold cyan]Downloading video...", console=console):
            media_path = download_video(
                source, cache_dir, ffmpeg_location=args.ffmpeg_location
            )
            console.print(f"[green]Downloaded:[/green] {media_path.name}")
    else:
        media_path = Path(source)
        if not media_path.exists():
            raise FileNotFoundError(f"File not found: {source}")

    # Step 2: Extract audio
    audio_path = _find_audio(cache_dir) if use_cache else None
    if audio_path:
        console.print(f"[dim]Cached audio:[/dim] {audio_path.name}")
    else:
        with Status("[bold cyan]Extracting audio...", console=console):
            audio_path = extract_audio(
                media_path, cache_dir, ffmpeg_location=args.ffmpeg_location
            )
            console.print(f"[green]Audio extracted:[/green] {audio_path.name}")

    # Step 3: Transcribe
    transcript_path = _find_transcript(cache_dir) if use_cache else None
    if transcript_path:
        transcript = transcript_path.read_text()
        console.print(f"[dim]Cached transcript:[/dim] {len(transcript)} chars")
    else:
        stt_kwargs = {}
        if args.stt == "whisper-local":
            stt_kwargs["model_size"] = args.whisper_model
        with Status("[bold cyan]Transcribing audio...", console=console):
            engine = create_stt_engine(args.stt, **stt_kwargs)
            transcript = engine.transcribe(audio_path, language=args.language)
            # Save transcript to cache
            transcript_path = cache_dir / f"{audio_path.stem}.txt"
            transcript_path.write_text(transcript)
            console.print(f"[green]Transcription complete:[/green] {len(transcript)} chars")
    log.debug("Transcript: %s", transcript[:500])

    # Step 4: Generate recipe via LLM
    with Status("[bold cyan]Generating recipe...", console=console):
        provider = create_llm_provider(args.llm)
        raw_response = provider.chat(SYSTEM_PROMPT, transcript)
    log.debug("LLM response: %s", raw_response[:500])

    # Step 5: Parse and output
    # Strip markdown code fences if present
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    recipe = Recipe.model_validate_json(cleaned)

    if args.output_format == "json":
        console.print(recipe.model_dump_json(indent=2))
    else:
        console.print(recipe_to_markdown(recipe))
