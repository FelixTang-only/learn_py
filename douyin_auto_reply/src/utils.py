"""Shared helpers: logging and human-like delays."""

from __future__ import annotations

import logging
import random
import time
from typing import Sequence


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def human_delay(delay_ms: Sequence[int] | None = None) -> None:
    """Sleep a random interval to mimic human pacing."""
    if not delay_ms or len(delay_ms) < 2:
        low, high = 800, 2000
    else:
        low, high = int(delay_ms[0]), int(delay_ms[1])
    if high < low:
        low, high = high, low
    seconds = random.randint(low, high) / 1000.0
    time.sleep(seconds)


def pick_one(items: Sequence[str]) -> str:
    if not items:
        return ""
    return random.choice(list(items))
