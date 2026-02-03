"""Data models for window tracking."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class WindowInfo:
    """Information about a tracked window."""

    hwnd: int
    title: str
    process_name: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    total_open_time: timedelta = field(default_factory=timedelta)
    active_time: timedelta = field(default_factory=timedelta)
    is_active: bool = False
    is_visible: bool = True

    def update_times(self, interval: float, is_currently_active: bool):
        """Update time tracking for this window.

        Args:
            interval: Time interval in seconds since last update
            is_currently_active: Whether this window is currently focused
        """
        self.last_seen = datetime.now()
        self.total_open_time = datetime.now() - self.first_seen

        if is_currently_active:
            self.active_time += timedelta(seconds=interval)
            self.is_active = True
        else:
            self.is_active = False

    def __hash__(self):
        """Make WindowInfo hashable by hwnd."""
        return hash(self.hwnd)

    def __eq__(self, other):
        """Compare WindowInfo objects by hwnd."""
        if isinstance(other, WindowInfo):
            return self.hwnd == other.hwnd
        return False
