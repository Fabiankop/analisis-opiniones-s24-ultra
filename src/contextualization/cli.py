"""Command-line interface for the contextualization pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from contextualization import (
    extraction_scraping,
    sentiment_analysis,
    statistical_analysis,
    word_frequency,
)

STEPS: dict[str, Callable[[], None]] = {
    "extraction": extraction_scraping.main,
    "statistics": statistical_analysis.main,
    "sentiment": sentiment_analysis.main,
    "frequency": word_frequency.main,
}

ALL_STEPS = "all"


def _run_step(name: str) -> None:
    print("\n" + "=" * 70)
    print(f"RUNNING STEP: {name}")
    print("=" * 70)
    STEPS[name]()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the contextualization analysis pipeline by step.",
    )
    parser.add_argument(
        "step",
        choices=[*STEPS.keys(), ALL_STEPS],
        help=f"Step to run: {', '.join(STEPS)}, or {ALL_STEPS}.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    if args.step == ALL_STEPS:
        for name in STEPS:
            _run_step(name)
        return

    _run_step(args.step)


if __name__ == "__main__":
    main()
