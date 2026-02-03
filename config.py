"""Configuration constants for the Window Tracker application."""

# Polling intervals (seconds)
WINDOW_ENUMERATION_INTERVAL = 1.0

# Window filtering settings
EXCLUDED_WINDOW_CLASSES = [
    'Shell_TrayWnd',
    'DV2ControlHost',
    'MsgrIMEWindowClass',
    'SysShadow',
    'Button',
    'Windows.UI.Core.CoreWindow'
]

EXCLUDED_WINDOW_TITLES = [
    'Program Manager',
    'Default IME',
    'MSCTFIME UI',
    'OpenBob - Watch Your Apps Live!',  # Exclude the tracker itself
    ''
]

# Minimum window title length
MIN_TITLE_LENGTH = 1

# Logging settings
LOG_FILE = 'window_tracker.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Threading
TRACKING_THREAD_NAME = 'WindowTrackerThread'
DAEMON_THREAD = True

# Window behavior
ALWAYS_ON_TOP = False  # Set to True to keep window always on top
