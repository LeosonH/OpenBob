# OpenBob - Watch Your Apps and Windows Do Things

A cross-platform Python for fun application for tracking open windows (Windows & macOS) with an immersive "House View" visualization that brings your computer usage to life!

- **60 FPS** smooth animations with particle effects and sounds
- **Interactive house** where your apps become characters
- **Visual effects** - sparkles, dust trails, glowing effects
- **Procedural sounds** - no audio files needed
- **Speech bubbles** - see what your apps are "saying"
- **Wandering behavior** - apps move around naturally
- **Usage statistics** - track time spent in each app
- **Always-on-top mode** - keep window visible while working

## Features

### House View
Watch your apps come alive as personas in a cozy house:

- **Open an app** - Sparkles burst as someone enters through the door
- **Close an app** - They say goodbye and exit with a poof
- **Active window** - Golden glow with floating particles
- **Idle time** - Characters wander around the house naturally
- **Speech bubbles** - See what they're saying in real-time

**The Personas:**
Your apps become diverse characters:
- **Known apps**: Chrome (globe), Discord (headphones), Spotify (music note), VS Code (laptop)
- **Unknown apps**: Diverse people (various genders, skin tones, hair, ages)
- Multiple instances get numbers: Chrome #2, Chrome #3

**Speech System:**
- **Entry**: "Hello everyone!", "Just arrived!", "Knock knock!" (when app opens, after initial load)
- **Active**: "Check this out!", "In the zone!", "Pay attention to me!" (when focused)
- **Idle**: "Just hanging out", "What's everyone up to?", "Yawn..." (random, 30-90s intervals)
- **Exit**: "Goodbye!", "See you later!", "Peace out!" (when closing)
- **Staggered timing**: Each persona has independent speech intervals to prevent coordination
- **Grace period**: 3-second delay before new apps can speak

## Installation

### Requirements
- **Windows** or **macOS**
- Python 3.7+

### Setup

```bash
# Install dependencies (automatically installs platform-specific packages)
pip install -r requirements.txt

# Windows only: Post-install for pywin32 (if needed)
python Scripts/pywin32_postinstall.py -install
```

**Platform-Specific Notes:**

- **Windows**: Uses Windows API via `pywin32` and `psutil`
- **macOS**: Uses Quartz and AppKit frameworks via `pyobjc`
  - May require granting accessibility permissions on first run
  - Go to System Preferences → Security & Privacy → Privacy → Accessibility

## Running the Application

```bash
python main.py
```

**Controls:**
- **ESC** - Exit application
- **Stats Button** (bottom-left) - View app usage statistics
- **Always On Top Button** (bottom-center) - Toggle always-on-top mode
- **Mute Button** (bottom-right) - Toggle sound on/off

**Configuration:**
- Edit `config.py` to change default settings
- `ALWAYS_ON_TOP = True/False` - Start with window always on top

## Visual Effects

### Particle Effects
- **Entry Sparkles** - 25 colorful particles burst when apps open (suppressed on initial load)
- **Walking Dust** - Subtle dust puffs appear while moving (reduced frequency and size)
- **Exit Poof** - Gray cloud when apps close
- **Active Glow** - Golden particles float from active window

### Sound Effects
All sounds are **procedurally generated** (no audio files needed):
- Door creak when opening
- Door thump when closing
- Chimes for hello/goodbye
- Quiet ambient background
- **Mute button** to toggle all sounds

### Animations
- **Walking**: Characters tilt side-to-side and bob (natural pace)
- **Direction**: Sprites flip based on movement direction
- **Idle Wandering**: Occasional wandering (12-40s intervals, staggered with per-persona variance)
- **Idle Speech**: Non-active personas chat randomly (30-90s intervals, independent timing)
- **Active**: Pulsing golden glow effect
- **Staggered entry**: On startup, personas enter one at a time (0.5s delays)

### Diversity
- **40+ diverse person emojis** for unknown apps
- Various skin tones, genders, hair colors, and ages
- Inclusive representation

## Usage Statistics

Click the **Stats** button (bottom-left) to view:
- **App names** with emoji icons
- **Total open time** - How long each app has been running
- **Active time** - How long each app has been focused
- **Usage percentage** - Visual progress bar showing active/total ratio
- **Color-coded bars**:
  - Green (>70%) - High focus/usage
  - Orange (30-70%) - Medium usage
  - Gray (<30%) - Low usage
- Shows top 8 apps sorted by total open time
- Golden highlight for currently active app

## Project Structure

```
window-tracker/
├── main.py                         # Application entry point
├── config.py                       # Configuration constants
├── requirements.txt                # Platform-specific dependencies
├── core/
│   ├── data_models.py             # WindowInfo dataclass
│   ├── window_tracker_base.py     # Abstract tracker interface
│   ├── window_tracker_windows.py  # Windows implementation (win32gui)
│   ├── window_tracker_macos.py    # macOS implementation (Quartz/AppKit)
│   ├── window_tracker_factory.py  # Platform detection & creation
│   ├── time_tracker.py            # Background thread tracking
│   ├── personification.py         # Persona generation & mapping
│   └── simulation.py              # Test simulation mode
├── gui/
│   ├── pygame_house_view.py       # Main house visualization (60 FPS)
│   ├── pygame_sprites.py          # Sprite classes (Persona, Door, Speech)
│   ├── pygame_particles.py        # Particle system (optimized)
│   └── pygame_sounds.py           # Procedural sound generation
└── utils/
    ├── formatters.py              # Time formatting helpers
    └── logger.py                  # Logging setup
```

## How It Works

### Window Tracking
- **Platform abstraction layer** - factory creates appropriate tracker for OS
- **Windows**: Uses `win32gui` to enumerate windows, `GetForegroundWindow()` for active window
- **macOS**: Uses `CGWindowListCopyWindowInfo` (Quartz) and `NSWorkspace` (AppKit)
- Polls every 1 second for updates
- Filters out system windows, toolbars, and the tracker itself
- **Self-exclusion**: App doesn't track its own window

### Time Tracking
- **Total Open Time**: Wall clock time since window appeared
- **Active Time**: Cumulative focus time
- Background thread with thread-safe dict
- Mutex locks prevent race conditions

### Personification
- Maps `hwnd → persona` consistently per session
- Generates unique names with numbers (Chrome #2, Chrome #3)
- Diverse emoji pool for inclusive representation
- Activities randomly selected from app-specific pools
- Generic activities preserve privacy

### Architecture
```
60 FPS Game Loop
    ↓
Windows → TimeTracker → View
    ↓
Sprite Groups → Update (particles, animations)
    ↓
Render Layers (background → furniture → sprites → particles → UI buttons)
    ↓
Display
```

## Customization

### Toggle Sound
Click the **Mute** button (bottom-right) or edit config:
```python
# In gui/pygame_house_view.py
self.sounds = SoundManager(enabled=False)
```

### Adjust Volumes
```python
self.sounds.play('hello', volume=0.8)      # Louder
self.sounds.play_ambient(volume=0.02)      # Quieter
```

### Change Movement Speed
In `gui/pygame_sprites.py`:
```python
self.move_progress += dt * 1.2  # Faster (default: 0.3)
```

### Adjust Wandering Frequency
In `gui/pygame_house_view.py` (`__init__`):
```python
self._wander_interval_min = 5.0   # More frequent (default: 12.0)
self._wander_interval_max = 15.0  # (default: 40.0)
```

### Adjust Idle Speech Frequency
In `gui/pygame_house_view.py` (`__init__`):
```python
self._speech_interval_min = 10.0  # More frequent (default: 30.0)
self._speech_interval_max = 30.0  # (default: 90.0)
self._speech_duration = 8.0       # Longer display (default: 5.0)
```

### Add Custom Speech Lines
At the top of `gui/pygame_house_view.py` (module-level constants):
```python
ENTRY_TEXT_OPTIONS = [
    "Hello everyone!",
    "Custom entry message!",
    # Add your own messages
]

IDLE_TEXT_OPTIONS = [
    "Just hanging out",
    "Custom idle message!",
    # Add your own messages
]
```

### Always On Top
- Click the **Pin** button (bottom-center) to toggle at runtime
- Or set default in `config.py`: `ALWAYS_ON_TOP = True`

## Performance

- **CPU**: <1% (60 FPS constant)
- **Memory**: 80-120 MB
- **GPU**: Minimal (2D only)
- **FPS**: Locked at 60

**Optimizations:**
- Font caching (emoji & FPS display)
- O(n) particle list filtering
- Timer-based glow emission (not random)
- Direct particle rendering (no surface creation)
- Squared distance checks (no sqrt)
- Module-level constants (no repeated list creation)
- Reduced particle emission frequency for dust trails

## Logging

Logs written to `window_tracker.log`:
- Window tracking events
- Persona creation/removal
- Animation states
- Button interactions
- Errors and warnings

## Fun Ideas

- Watch your workflow patterns emerge
- See which apps dominate your "house"
- Use as a productivity awareness tool
- Show it off to colleagues
- Make it a game to minimize house population
- Notice how apps naturally spread out over time
- Track your most-used apps with the stats overlay

## Notes

- **Windows & macOS supported**
- Windows: Tested on Windows 10/11
- macOS: Requires accessibility permissions for window tracking
- Some security software may need to whitelist the app
- Does **not** capture window content, only titles
- Safe and privacy-focused
- **Self-exclusion**: The tracker doesn't track itself
- Linux: Not currently supported (PRs welcome!)

## License

Free to use and modify!

## Credits

- Built with Python and pygame
- Procedural sound generation using numpy
- Emoji-based character visualization
- Diverse and inclusive representation
