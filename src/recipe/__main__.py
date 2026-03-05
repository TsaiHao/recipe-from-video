from __future__ import annotations

import logging
import sys

from recipe.cli import build_parser
from recipe.config import load_dotenv
from recipe.pipeline import run_pipeline
from recipe.stt import STT_BACKENDS
from recipe.llm import LLM_BACKENDS


def main() -> None:
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if args.list_stt:
        from rich.console import Console
        from rich.table import Table

        table = Table(title="Available STT Backends")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        for name, cls in STT_BACKENDS.items():
            table.add_row(name, cls.__doc__ or "")
        Console().print(table)
        return

    if args.list_llm:
        from rich.console import Console
        from rich.table import Table

        table = Table(title="Available LLM Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        for name, cls in LLM_BACKENDS.items():
            table.add_row(name, cls.__doc__ or "")
        Console().print(table)
        return

    if args.source is None:
        parser.error("source is required (unless using --list-stt or --list-llm)")

    run_pipeline(args)


if __name__ == "__main__":
    main()
