# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run

This project uses `uv` (located at `~/.local/bin/uv`).

```bash
uv sync                          # Install dependencies
uv run recipe --help             # Run the CLI
uv run recipe --list-stt         # List STT backends
uv run recipe --list-llm         # List LLM providers
uv run recipe <URL_or_file>      # Full pipeline
uv run recipe --debug <source>   # With debug logging
```

Optional dependency groups: `uv sync --extra aws`, `uv sync --extra google`.

External tools required at runtime: `yt-dlp`, `ffmpeg`.

## Architecture

The tool converts cooking videos into structured 1-person recipes in Chinese. The pipeline flows: **download → extract audio → transcribe → LLM summarize → parse → output**.

### Plugin registries

Both STT and LLM use a registry pattern with `@register("name")` decorators. Adding a new backend means:
1. Create a file in `stt/` or `llm/`
2. Subclass `SttEngine` or `LlmProvider`
3. Decorate with `@register("backend-name")`
4. Import in the package `__init__.py`

The registries (`STT_BACKENDS`, `LLM_BACKENDS`) are populated at import time and used by `--list-stt`/`--list-llm` and the factory functions.

### Config resolution

API keys resolve in order: environment variable → `~/.config/recipe/config.toml` under `[keys]`. Use `config.get_api_key("ENV_VAR_NAME")`.

### Output

`models.py` contains the Pydantic `Recipe` model, the Chinese system prompt for the LLM, and the `recipe_to_markdown()` formatter. The pipeline handles stripping markdown code fences from LLM responses before parsing.
