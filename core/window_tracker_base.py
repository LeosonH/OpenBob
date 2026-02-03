"""Abstract base class for platform-specific window tracking."""
from abc import ABC, abstractmethod
from typing import List
from core.data_models import WindowInfo


class WindowTrackerBase(ABC):
    """Abstract base class for window tracking across platforms."""

    @abstractmethod
    def enumerate_windows(self) -> List[WindowInfo]:
        """Enumerate all visible windows.

        Returns:
            List of WindowInfo objects for all visible windows
        """
        pass

    @abstractmethod
    def get_active_window_handle(self):
        """Get the handle/ID of the currently active window.

        Returns:
            Window handle/ID (type varies by platform)
        """
        pass

    @abstractmethod
    def is_supported(self) -> bool:
        """Check if this platform is supported.

        Returns:
            True if the current platform is supported by this implementation
        """
        pass
