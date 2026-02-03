"""macOS-specific window tracking implementation."""
import sys
import logging
from typing import List, Optional

from core.window_tracker_base import WindowTrackerBase
from core.data_models import WindowInfo

try:
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
        kCGNullWindowID
    )
    from AppKit import NSWorkspace
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False

from config import MIN_TITLE_LENGTH

logger = logging.getLogger(__name__)


class MacOSWindowTracker(WindowTrackerBase):
    """macOS-specific window tracking using Quartz and AppKit."""

    def __init__(self):
        """Initialize macOS window tracker."""
        self._workspace = None
        if MACOS_AVAILABLE:
            self._workspace = NSWorkspace.sharedWorkspace()

    def is_supported(self) -> bool:
        """Check if macOS platform is available."""
        return sys.platform == 'darwin' and MACOS_AVAILABLE

    def enumerate_windows(self) -> List[WindowInfo]:
        """Enumerate all valid windows on macOS.

        Returns:
            List of WindowInfo objects
        """
        if not MACOS_AVAILABLE:
            logger.error("Quartz/AppKit not available. Install pyobjc-framework-Quartz and pyobjc-framework-Cocoa.")
            return []

        windows = []
        active_app_name = self._get_active_app_name()

        try:
            # Get all on-screen windows
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
                kCGNullWindowID
            )

            for window in window_list:
                # Filter system windows (only show layer 0 = normal windows)
                layer = window.get('kCGWindowLayer', 0)
                if layer != 0:
                    continue

                # Get window info
                title = window.get('kCGWindowName', '')
                owner = window.get('kCGWindowOwnerName', '')
                window_id = window.get('kCGWindowNumber', 0)

                # Skip windows without titles or from system processes
                if not title or len(title) < MIN_TITLE_LENGTH:
                    continue

                # Skip certain system applications
                if self._should_exclude_app(owner):
                    continue

                # Check if this window belongs to the active application
                is_active = (owner == active_app_name)

                window_info = WindowInfo(
                    hwnd=window_id,
                    title=title,
                    process_name=owner,
                    is_active=is_active,
                    is_visible=True
                )
                windows.append(window_info)

        except Exception as e:
            logger.error(f"Error enumerating windows on macOS: {e}")

        return windows

    def get_active_window_handle(self) -> Optional[int]:
        """Get the currently active window handle.

        Note: On macOS, we can only reliably get the active application,
        not the specific window. Returns a synthetic ID based on app name.

        Returns:
            Synthetic window ID or None
        """
        if not MACOS_AVAILABLE:
            return None

        try:
            active_app = self._workspace.activeApplication()
            app_name = active_app.get('NSApplicationName', '')
            # Return hash of app name as synthetic window ID
            return hash(app_name) if app_name else None
        except Exception as e:
            logger.debug(f"Error getting active window: {e}")
            return None

    def _get_active_app_name(self) -> str:
        """Get the name of the currently active application.

        Returns:
            Active application name
        """
        try:
            active_app = self._workspace.activeApplication()
            return active_app.get('NSApplicationName', '')
        except Exception as e:
            logger.debug(f"Error getting active app: {e}")
            return ""

    def _should_exclude_app(self, app_name: str) -> bool:
        """Check if an application should be excluded from tracking.

        Args:
            app_name: Application name

        Returns:
            True if app should be excluded
        """
        # Exclude common system applications
        excluded_apps = {
            'Dock',
            'Spotlight',
            'SystemUIServer',
            'ControlCenter',
            'NotificationCenter',
            'WindowServer',
            'loginwindow',
            'Finder',  # Optional - you may want to track Finder windows
        }

        return app_name in excluded_apps
