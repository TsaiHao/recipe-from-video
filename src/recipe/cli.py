from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recipe",
        description="Extract structured recipes from cooking videos.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="URL (Bilibili/YouTube/Douyin) or local file path",
    )
    parser.add_argument(
        "-s", "--stt",
        default="whisper-local",
        help="STT backend (default: whisper-local)",
    )
    parser.add_argument(
        "-l", "--llm",
        default="deepseek",
        help="LLM provider (default: deepseek)",
    )
    parser.add_argument(
        "--language",
        default="zh",
        help="Audio language hint (default: zh)",
    )
    parser.add_argument(
        "--whisper-model",
        default="large-v3",
        help="Whisper model size (default: large-v3)",
    )
    parser.add_argument(
        "--output-format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--ffmpeg-location",
        default=None,
        help="Path to ffmpeg binary",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore cached files and re-run all steps",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--list-stt",
        action="store_true",
        help="List available STT backends and exit",
    )
    parser.add_argument(
        "--list-llm",
        action="store_true",
        help="List available LLM providers and exit",
    )
    return parser
