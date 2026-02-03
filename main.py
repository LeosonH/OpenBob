"""Main entry point for Window Tracker (Windows & macOS)."""
import sys
import logging

from utils.logger import setup_logging
from core.time_tracker import TimeTracker
from core.personification import PersonificationManager
from core.window_tracker_factory import get_supported_platforms
from gui.pygame_house_view import PygameHouseView


def main():
    """Main entry point."""
    # Setup logging
    setup_logging(log_to_file=True, log_to_console=True)
    logger = logging.getLogger(__name__)

    # Check for pygame (required for all platforms)
    try:
        import pygame
    except ImportError:
        print("ERROR: pygame not found.")
        print("\nPlease install pygame:")
        print("pip install pygame")
        return 1

    # Check platform support
    supported = get_supported_platforms()
    if not supported:
        print(f"ERROR: Unsupported platform: {sys.platform}")
        print("\nThis application requires Windows or macOS.")
        print("\nInstall platform-specific dependencies:")
        print("  Windows: pip install pywin32 psutil")
        print("  macOS:   pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz")
        return 1

    logger.info(f"Starting Window Tracker on {supported[0]}")

    # Create tracker and personification manager
    try:
        tracker = TimeTracker()
        personification_manager = PersonificationManager()
    except RuntimeError as e:
        print(f"ERROR: Failed to initialize tracker: {e}")
        return 1

    # Start tracking
    tracker.start()
    logger.info("Tracking started")

    # Create and run view
    try:
        view = PygameHouseView(tracker, personification_manager)
        view.run()
    except Exception as e:
        logger.error(f"Error running application: {e}", exc_info=True)
        return 1
    finally:
        tracker.stop()
        logger.info("Tracking stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
