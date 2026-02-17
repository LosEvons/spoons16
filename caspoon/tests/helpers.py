"""Test helpers for Textual TUI tests.

Provides utilities for reliable async testing without timing dependencies.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App
    from textual.pilot import Pilot


async def wait_for_workers(
    app: App,
    pilot: Pilot,
    *,
    timeout: float = 5.0,
    poll_interval: float = 0.05,
) -> None:
    """Wait for all background workers to complete.

    Polls ``app.workers`` until the set is empty, draining the Textual
    message queue between polls so the UI can process completion messages.

    Args:
        app: The Textual application instance.
        pilot: The test pilot (used for ``pause()`` to drain messages).
        timeout: Maximum seconds to wait before raising ``TimeoutError``.
        poll_interval: Seconds between polls.

    Raises:
        TimeoutError: If workers are still running after *timeout* seconds.
    """
    elapsed = 0.0
    while app.workers:
        await pilot.pause()
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
        if elapsed >= timeout:
            raise TimeoutError(
                f"Workers still running after {timeout}s: {app.workers}"
            )
    # One final drain to process any remaining messages
    await pilot.pause()


async def start_analysis_and_wait(
    app: App,
    pilot: Pilot,
    path: str,
    *,
    timeout: float = 10.0,
) -> None:
    """Start an analysis and wait for it to complete.

    Calls ``app.start_analysis(path)`` then waits until the
    ``is_analyzing`` flag is cleared and all workers have finished.

    Args:
        app: A ``CaspoonApp`` instance.
        pilot: The test pilot.
        path: Path to the binary to analyse.
        timeout: Maximum seconds to wait.

    Raises:
        TimeoutError: If the analysis does not complete in time.
    """
    await app.start_analysis(path)
    await pilot.pause()

    elapsed = 0.0
    poll = 0.05
    while getattr(app.state.ui_state, "is_analyzing", False) or app.workers:
        await pilot.pause()
        await asyncio.sleep(poll)
        elapsed += poll
        if elapsed >= timeout:
            raise TimeoutError(
                f"Analysis still running after {timeout}s"
            )
    await pilot.pause()
