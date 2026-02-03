"""Utility functions for formatting data for display."""
from datetime import timedelta


def format_timedelta(td: timedelta) -> str:
    """Format a timedelta object into a human-readable string.

    Args:
        td: Timedelta to format

    Returns:
        Formatted string like "1h 45m 30s" or "30s"
    """
    if not isinstance(td, timedelta):
        return "0s"

    total_seconds = int(td.total_seconds())

    if total_seconds < 0:
        return "0s"

    if total_seconds == 0:
        return "0s"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:  # Always show seconds if nothing else
        parts.append(f"{seconds}s")

    return " ".join(parts)
