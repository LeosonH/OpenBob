"""Time tracking logic with background thread."""
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from config import WINDOW_ENUMERATION_INTERVAL, TRACKING_THREAD_NAME, DAEMON_THREAD
from core.data_models import WindowInfo
from core.window_tracker_factory import create_window_tracker

logger = logging.getLogger(__name__)


class TimeTracker:
    """Central tracking class for managing window time tracking."""

    def __init__(self, simulation_mode: bool = False):
        """Initialize the TimeTracker.

        Args:
            simulation_mode: If True, use simulation instead of real window tracking
        """
        self._windows: Dict[int, WindowInfo] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_update_time = None
        self._simulation_mode = simulation_mode
        self._simulation = None
        self._window_tracker = None

        if simulation_mode:
            from core.simulation import HouseSimulation
            self._simulation = HouseSimulation()
            logger.info("TimeTracker initialized in SIMULATION mode")
        else:
            # Create platform-specific window tracker
            try:
                self._window_tracker = create_window_tracker()
            except RuntimeError as e:
                logger.error(f"Failed to create window tracker: {e}")
                raise

    def start(self):
        """Start the background tracking thread."""
        if self._running:
            logger.warning("TimeTracker already running")
            return

        self._running = True
        self._last_update_time = time.time()
        self._thread = threading.Thread(
            target=self._tracking_loop,
            name=TRACKING_THREAD_NAME,
            daemon=DAEMON_THREAD
        )
        self._thread.start()
        logger.info("TimeTracker started")

    def stop(self):
        """Stop the background tracking thread."""
        if not self._running:
            logger.warning("TimeTracker not running")
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("TimeTracker stopped")

    def clear(self):
        """Clear all tracked window data."""
        with self._lock:
            self._windows.clear()
        logger.info("TimeTracker data cleared")

    def get_all_windows(self) -> List[WindowInfo]:
        """Get a copy of all tracked windows.

        Returns:
            List of WindowInfo objects
        """
        with self._lock:
            return list(self._windows.values())

    def get_window(self, hwnd: int) -> Optional[WindowInfo]:
        """Get information about a specific window.

        Args:
            hwnd: Window handle

        Returns:
            WindowInfo object or None if not found
        """
        with self._lock:
            return self._windows.get(hwnd)

    def is_running(self) -> bool:
        """Check if the tracker is currently running.

        Returns:
            True if running, False otherwise
        """
        return self._running

    def _tracking_loop(self):
        """Main tracking loop running in background thread."""
        logger.info("Tracking loop started")

        while self._running:
            try:
                # Calculate time since last update
                current_time = time.time()
                interval = current_time - self._last_update_time
                self._last_update_time = current_time

                # Update window tracking
                self._update_windows(interval)

                # Sleep until next cycle
                time.sleep(WINDOW_ENUMERATION_INTERVAL)

            except Exception as e:
                logger.error(f"Error in tracking loop: {e}", exc_info=True)
                time.sleep(WINDOW_ENUMERATION_INTERVAL)

        logger.info("Tracking loop ended")

    def _update_windows(self, interval: float):
        """Update all window information.

        Args:
            interval: Time interval in seconds since last update
        """
        # Get current windows from platform-specific tracker or simulation
        if self._simulation_mode and self._simulation:
            current_windows, active_hwnd = self._simulation.update()
            # Convert to list of tuples for backward compatibility
            current_windows_list = [(hwnd, title, process) for hwnd, title, process in current_windows]
        else:
            # Use platform-specific window tracker
            windows = self._window_tracker.enumerate_windows()
            current_windows_list = windows
            active_hwnd = self._window_tracker.get_active_window_handle()

        # Get set of current window handles
        if self._simulation_mode:
            current_hwnds = {hwnd for hwnd, _, _ in current_windows_list}
        else:
            current_hwnds = {w.hwnd for w in current_windows_list}

        with self._lock:
            # Update existing windows and add new ones
            if self._simulation_mode:
                # Simulation mode: old tuple format
                for hwnd, title, process_name in current_windows_list:
                    is_currently_active = (hwnd == active_hwnd)

                    if hwnd in self._windows:
                        # Update existing window
                        window_info = self._windows[hwnd]
                        window_info.update_times(interval, is_currently_active)
                        window_info.title = title
                        window_info.is_visible = True
                    else:
                        # Add new window
                        window_info = WindowInfo(
                            hwnd=hwnd,
                            title=title,
                            process_name=process_name,
                            first_seen=datetime.now(),
                            last_seen=datetime.now(),
                            is_active=is_currently_active,
                            is_visible=True
                        )
                        self._windows[hwnd] = window_info
                        logger.info(f"New window tracked: {title} ({process_name})")
            else:
                # Platform-specific tracker: WindowInfo objects
                for window_info in current_windows_list:
                    hwnd = window_info.hwnd
                    is_currently_active = window_info.is_active

                    if hwnd in self._windows:
                        # Update existing window
                        existing = self._windows[hwnd]
                        existing.update_times(interval, is_currently_active)
                        existing.title = window_info.title
                        existing.is_visible = window_info.is_visible
                        existing.is_active = is_currently_active
                    else:
                        # Add new window
                        window_info.first_seen = datetime.now()
                        window_info.last_seen = datetime.now()
                        self._windows[hwnd] = window_info
                        logger.info(f"New window tracked: {window_info.title} ({window_info.process_name})")

            # Mark windows that are no longer visible
            for hwnd in list(self._windows.keys()):
                if hwnd not in current_hwnds:
                    if hwnd in self._windows:
                        self._windows[hwnd].is_visible = False
                        logger.debug(f"Window no longer visible: {hwnd}")

    def get_stats(self) -> Dict[str, any]:
        """Get tracking statistics.

        Returns:
            Dictionary with tracking stats
        """
        with self._lock:
            total_windows = len(self._windows)
            visible_windows = sum(1 for w in self._windows.values() if w.is_visible)
            active_window = next((w for w in self._windows.values() if w.is_active), None)

            return {
                'total_windows': total_windows,
                'visible_windows': visible_windows,
                'active_window': active_window.title if active_window else None,
                'is_running': self._running,
                'simulation_mode': self._simulation_mode
            }

    def add_simulation_visitor(self) -> Optional[str]:
        """Add a visitor to the simulation (simulation mode only).

        Returns:
            Name of the visitor added, or None if not in simulation mode
        """
        if self._simulation_mode and self._simulation:
            return self._simulation.add_visitor()
        return None

    def remove_simulation_person(self) -> Optional[str]:
        """Remove a person from the simulation (simulation mode only).

        Returns:
            Name of the person who left, or None if not in simulation mode
        """
        if self._simulation_mode and self._simulation:
            return self._simulation.remove_person()
        return None
