# Cross-Platform Implementation Guide

This document describes the cross-platform architecture for Window Tracker.

## Overview

Window Tracker supports **Windows** and **macOS** through a platform abstraction layer.

## Architecture

### Platform Abstraction Layer

```
┌─────────────────────────────────────────┐
│         WindowTrackerBase (ABC)         │
│  - enumerate_windows()                  │
│  - get_active_window_handle()           │
│  - is_supported()                       │
└─────────────────────────────────────────┘
           ▲                  ▲
           │                  │
┌──────────┴──────────┐  ┌───┴─────────────────┐
│ WindowsWindowTracker│  │MacOSWindowTracker   │
│ (win32gui/psutil)   │  │(Quartz/AppKit)      │
└─────────────────────┘  └─────────────────────┘
           │                  │
           └─────────┬────────┘
                     │
         ┌───────────▼──────────────┐
         │ window_tracker_factory   │
         │  create_window_tracker() │
         └──────────────────────────┘
                     │
                     ▼
              ┌────────────┐
              │TimeTracker │
              └────────────┘
```

## Platform Differences

### Windows

**APIs Used:**
- `win32gui.EnumWindows()` - enumerate windows
- `win32gui.GetForegroundWindow()` - active window
- `win32process.GetWindowThreadProcessId()` - process info
- `psutil.Process()` - process name
- `win32gui.SetWindowPos()` - always-on-top functionality

**Filtering:**
- Excludes tool windows (`WS_EX_TOOLWINDOW`)
- Checks for app window flag (`WS_EX_APPWINDOW`)
- Filters by window class and title
- Excludes Window Tracker's own window

### macOS

**APIs Used:**
- `CGWindowListCopyWindowInfo()` - enumerate windows
- `NSWorkspace.activeApplication()` - active app
- Window properties: `kCGWindowName`, `kCGWindowOwnerName`, `kCGWindowLayer`
- `NSWindow.setLevel_()` - always-on-top functionality

**Filtering:**
- Only includes layer 0 windows (normal app windows)
- Excludes system apps: Dock, Spotlight, WindowServer, etc.
- Filters by window title length
- Excludes Window Tracker's own window

**Limitations:**
- Can only detect active *application*, not specific window
- Window IDs are CGWindowNumber (not persistent across restarts)
- Requires accessibility permissions

## Installation

### Windows
```bash
pip install -r requirements.txt
# Optional: pywin32 post-install
python Scripts/pywin32_postinstall.py -install
```

### macOS
```bash
pip install -r requirements.txt
# Accessibility permissions required on first run
# System Preferences → Security & Privacy → Privacy → Accessibility
```

## Testing on macOS

Since this was developed on Windows/WSL, testing on macOS is needed:

1. **Basic Functionality:**
   - Does the app start without errors?
   - Are windows detected and displayed?
   - Does the active window detection work?

2. **Persona Creation:**
   - Do known apps get correct emojis?
   - Do unknown apps get diverse person emojis?
   - Are multiple instances numbered correctly?

3. **Animations & Effects:**
   - Entry/exit animations work?
   - Door opens/closes correctly?
   - Particles render properly?
   - Staggered entry working?

4. **UI Buttons:**
   - Stats overlay displays correctly?
   - Always-on-top toggle works?
   - Mute button toggles sound?
   - Labels visible and readable?

5. **Edge Cases:**
   - Multiple monitors?
   - Fullscreen apps?
   - Apps with long titles?
   - Self-exclusion working?

## Known macOS Limitations

1. **Active Window Detection:**
   - Can only detect active *application*, not specific window
   - If an app has multiple windows, all will show as active when app is active

2. **Window IDs:**
   - CGWindowNumber changes between launches
   - Persona mappings won't persist across app restarts (same on Windows)

3. **Permissions:**
   - User must grant accessibility permissions
   - May need to restart app after granting permissions

4. **System Apps:**
   - Some system apps may not be trackable
   - Finder windows are currently excluded (can be changed)

## Future Enhancements

- **Linux Support:** Use X11 or Wayland APIs
- **Per-Window Detection on macOS:** Use Accessibility API (`AXUIElement`)
- **Better macOS Integration:** Use `NSAccessibilityElement` for window titles
- **Window Screenshots:** Capture thumbnails (privacy toggle)
- **Persistence:** Save persona mappings across sessions
- **Keyboard shortcuts:** For buttons and controls
- **Customizable themes:** Change house colors/style

## Troubleshooting

### Windows
- **ImportError: pywin32**: Run `pip install pywin32`
- **No windows detected**: Check if running with sufficient permissions
- **Missing process names**: Ensure psutil is installed
- **Always-on-top not working**: Check Windows permissions

### macOS
- **ImportError: No module named 'Quartz'**: Run `pip install pyobjc-framework-Quartz`
- **Empty window list**: Grant accessibility permissions
- **Permission denied**: Go to System Preferences → Security & Privacy → Accessibility
- **Always-on-top not working**: Check macOS window management permissions

## Development Notes

### Adding a New Platform

1. Create `core/window_tracker_<platform>.py`
2. Extend `WindowTrackerBase`
3. Implement required methods
4. Add platform detection to factory
5. Add dependencies to `requirements.txt` with markers
6. Update documentation
7. Implement always-on-top functionality

### Platform-Specific Testing

Use simulation mode for cross-platform development:
```python
tracker = TimeTracker(simulation_mode=True)
```

This allows testing the visualization without platform APIs.
