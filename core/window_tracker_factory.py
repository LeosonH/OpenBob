"""Factory for creating platform-specific window trackers."""
import sys
import logging

from core.window_tracker_base import WindowTrackerBase
from core.window_tracker_windows import WindowsWindowTracker
from core.window_tracker_macos import MacOSWindowTracker

logger = logging.getLogger(__name__)


def create_window_tracker() -> WindowTrackerBase:
    """Create a window tracker for the current platform.

    Returns:
        Platform-specific WindowTracker instance

    Raises:
        RuntimeError: If no supported platform is detected
    """
    # Try Windows first
    windows_tracker = WindowsWindowTracker()
    if windows_tracker.is_supported():
        logger.info("Using Windows window tracker")
        return windows_tracker

    # Try macOS
    macos_tracker = MacOSWindowTracker()
    if macos_tracker.is_supported():
        logger.info("Using macOS window tracker")
        return macos_tracker

    # No supported platform found
    platform = sys.platform
    error_msg = f"Unsupported platform: {platform}. This application requires Windows or macOS."

    if platform == 'win32':
        error_msg += "\n\nWindows detected but pywin32 is not installed. Install with:\n  pip install pywin32"
    elif platform == 'darwin':
        error_msg += "\n\nmacOS detected but PyObjC is not installed. Install with:\n  pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz"

    logger.error(error_msg)
    raise RuntimeError(error_msg)


def get_supported_platforms() -> list:
    """Get list of supported platforms.

    Returns:
        List of platform names that are supported
    """
    supported = []

    windows_tracker = WindowsWindowTracker()
    if windows_tracker.is_supported():
        supported.append("Windows")

    macos_tracker = MacOSWindowTracker()
    if macos_tracker.is_supported():
        supported.append("macOS")

    return supported
