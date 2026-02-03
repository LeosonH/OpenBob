"""Windows-specific window tracking implementation."""
import sys
import logging
from typing import List, Optional

from core.window_tracker_base import WindowTrackerBase
from core.data_models import WindowInfo

try:
    import win32gui
    import win32process
    import win32con
    import psutil
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from config import EXCLUDED_WINDOW_CLASSES, EXCLUDED_WINDOW_TITLES, MIN_TITLE_LENGTH

logger = logging.getLogger(__name__)


class WindowsWindowTracker(WindowTrackerBase):
    """Windows-specific window tracking using win32 API."""

    def is_supported(self) -> bool:
        """Check if Windows platform is available."""
        return sys.platform == 'win32' and WINDOWS_AVAILABLE

    def enumerate_windows(self) -> List[WindowInfo]:
        """Enumerate all valid windows on Windows.

        Returns:
            List of WindowInfo objects
        """
        if not WINDOWS_AVAILABLE:
            logger.error("win32gui not available. This requires Windows with pywin32.")
            return []

        windows = []
        active_hwnd = self.get_active_window_handle()

        def callback(hwnd, _):
            """Callback for EnumWindows."""
            if self._is_valid_window(hwnd):
                title = self._get_window_title(hwnd)
                process_name = self._get_process_name(hwnd)
                is_active = (hwnd == active_hwnd)

                window_info = WindowInfo(
                    hwnd=hwnd,
                    title=title,
                    process_name=process_name,
                    is_active=is_active,
                    is_visible=True
                )
                windows.append(window_info)
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            logger.error(f"Error enumerating windows: {e}")

        return windows

    def get_active_window_handle(self) -> Optional[int]:
        """Get the currently active window handle.

        Returns:
            Window handle (hwnd) or None
        """
        if not WINDOWS_AVAILABLE:
            return None

        try:
            hwnd = win32gui.GetForegroundWindow()
            return hwnd if hwnd != 0 else None
        except Exception as e:
            logger.debug(f"Error getting active window: {e}")
            return None

    def _is_valid_window(self, hwnd: int) -> bool:
        """Check if a window is valid for tracking.

        Args:
            hwnd: Window handle

        Returns:
            True if window should be tracked
        """
        try:
            # Window must be visible
            if not win32gui.IsWindowVisible(hwnd):
                return False

            # Get window title
            title = win32gui.GetWindowText(hwnd)
            if len(title) < MIN_TITLE_LENGTH:
                return False

            # Exclude specific titles
            if title in EXCLUDED_WINDOW_TITLES:
                return False

            # Get window class name
            class_name = win32gui.GetClassName(hwnd)
            if class_name in EXCLUDED_WINDOW_CLASSES:
                return False

            # Exclude tool windows (extended style check)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if ex_style & win32con.WS_EX_TOOLWINDOW:
                return False

            # Include only windows with WS_EX_APPWINDOW or no owner
            if not (ex_style & win32con.WS_EX_APPWINDOW):
                # Check if window has an owner (child windows)
                if win32gui.GetWindow(hwnd, win32con.GW_OWNER) != 0:
                    return False

            return True

        except Exception as e:
            logger.debug(f"Error validating window {hwnd}: {e}")
            return False

    def _get_window_title(self, hwnd: int) -> str:
        """Get window title.

        Args:
            hwnd: Window handle

        Returns:
            Window title
        """
        try:
            return win32gui.GetWindowText(hwnd)
        except Exception as e:
            logger.debug(f"Error getting title for window {hwnd}: {e}")
            return ""

    def _get_process_name(self, hwnd: int) -> str:
        """Get process name for a window.

        Args:
            hwnd: Window handle

        Returns:
            Process name
        """
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            logger.debug(f"Error getting process name for window {hwnd}: {e}")
            return "Unknown"
