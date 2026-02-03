"""Pygame-based house view for window tracking."""
import pygame
import random
import sys
import time
from typing import Dict, List, Optional
import logging

from core.data_models import WindowInfo
from core.personification import PersonificationManager
from gui.pygame_sprites import Persona, Door, SpeechBubble
from gui.pygame_particles import ParticleSystem
from gui.pygame_sounds import SoundManager
from config import ALWAYS_ON_TOP
from utils.formatters import format_timedelta
from datetime import timedelta
import platform


class Button:
    """Base button class for UI elements."""

    def __init__(self, pos, size=40):
        """Initialize button.

        Args:
            pos: (x, y) position
            size: Button size
        """
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos[0] - size // 2, pos[1] - size // 2, size, size)
        self.hover = False

    def update(self, mouse_pos):
        """Update button state.

        Args:
            mouse_pos: Current mouse position (x, y)
        """
        self.hover = self.rect.collidepoint(mouse_pos)

    def handle_click(self, mouse_pos):
        """Check if button was clicked.

        Args:
            mouse_pos: Mouse click position (x, y)

        Returns:
            bool: True if button was clicked
        """
        return self.rect.collidepoint(mouse_pos)

    def _draw_background(self, screen):
        """Draw button background.

        Args:
            screen: Pygame surface to draw on
        """
        bg_color = (80, 80, 80) if self.hover else (100, 100, 100)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (60, 60, 60), self.rect, 2, border_radius=8)

    def _draw_label(self, screen, text, color=(120, 120, 120)):
        """Draw label below button.

        Args:
            screen: Pygame surface to draw on
            text: Label text
            color: Text color
        """
        label_font = pygame.font.Font(None, 18)
        label_surf = label_font.render(text, True, color)
        label_rect = label_surf.get_rect(center=(self.rect.centerx, self.rect.bottom + 12))
        screen.blit(label_surf, label_rect)

    def draw(self, screen):
        """Draw the button. Override in subclasses.

        Args:
            screen: Pygame surface to draw on
        """
        raise NotImplementedError("Subclasses must implement draw()")


class MuteButton(Button):
    """Mute button UI element."""

    def __init__(self, pos, size=40):
        """Initialize mute button."""
        super().__init__(pos, size)
        self.is_muted = False

    def toggle(self):
        """Toggle mute state."""
        self.is_muted = not self.is_muted

    def draw(self, screen):
        """Draw the mute button."""
        self._draw_background(screen)

        # Label
        label_text = "Mute" if not self.is_muted else "Unmute"
        self._draw_label(screen, label_text)

        # Draw speaker icon
        center_x, center_y = self.rect.center
        icon_color = (240, 240, 240)

        if self.is_muted:
            # Speaker with X
            # Speaker cone
            pygame.draw.polygon(screen, icon_color, [
                (center_x - 8, center_y - 4),
                (center_x - 8, center_y + 4),
                (center_x - 14, center_y + 8),
                (center_x - 14, center_y - 8)
            ])
            # Speaker body
            pygame.draw.rect(screen, icon_color, (center_x - 14, center_y - 3, 4, 6))

            # X symbol
            pygame.draw.line(screen, (255, 60, 60), (center_x - 2, center_y - 6), (center_x + 6, center_y + 2), 3)
            pygame.draw.line(screen, (255, 60, 60), (center_x + 6, center_y - 6), (center_x - 2, center_y + 2), 3)
        else:
            # Speaker with sound waves
            # Speaker cone
            pygame.draw.polygon(screen, icon_color, [
                (center_x - 8, center_y - 4),
                (center_x - 8, center_y + 4),
                (center_x - 14, center_y + 8),
                (center_x - 14, center_y - 8)
            ])
            # Speaker body
            pygame.draw.rect(screen, icon_color, (center_x - 14, center_y - 3, 4, 6))

            # Sound waves as curved brackets - using arcs positioned to look like )
            # Small wave
            pygame.draw.arc(screen, icon_color, (center_x - 4, center_y - 5, 10, 10), -1.57, 1.57, 2)
            # Medium wave
            pygame.draw.arc(screen, icon_color, (center_x - 2, center_y - 8, 14, 16), -1.57, 1.57, 2)
            # Large wave
            pygame.draw.arc(screen, icon_color, (center_x, center_y - 11, 18, 22), -1.57, 1.57, 2)


class StatsButton(Button):
    """Stats button UI element."""

    def draw(self, screen):
        """Draw the stats button."""
        self._draw_background(screen)
        self._draw_label(screen, "Stats")

        # Draw bar chart icon
        center_x, center_y = self.rect.center
        icon_color = (240, 240, 240)

        # Three bars of different heights
        bar_width = 6
        bar_spacing = 3
        bar_heights = [8, 14, 11]

        for i, height in enumerate(bar_heights):
            x = center_x - (len(bar_heights) * (bar_width + bar_spacing)) // 2 + i * (bar_width + bar_spacing)
            y = center_y + 10 - height
            pygame.draw.rect(screen, icon_color, (x, y, bar_width, height))


class AlwaysOnTopButton(Button):
    """Always-on-top toggle button UI element."""

    def __init__(self, pos, size=40):
        """Initialize always-on-top button."""
        super().__init__(pos, size)
        self.is_pinned = ALWAYS_ON_TOP

    def toggle(self):
        """Toggle pinned state."""
        self.is_pinned = not self.is_pinned

    def draw(self, screen):
        """Draw the always-on-top button."""
        self._draw_background(screen)

        # Label (golden when pinned)
        label_color = (255, 215, 0) if self.is_pinned else (120, 120, 120)
        self._draw_label(screen, "Always On Top", label_color)

        # Draw pin icon
        center_x, center_y = self.rect.center
        icon_color = (255, 215, 0) if self.is_pinned else (240, 240, 240)

        if self.is_pinned:
            # Pinned icon (pushpin pushed in)
            # Pin head (circle)
            pygame.draw.circle(screen, icon_color, (center_x, center_y - 6), 5)
            pygame.draw.circle(screen, (200, 180, 0), (center_x, center_y - 6), 5, 2)
            # Pin body (rectangle)
            pygame.draw.rect(screen, icon_color, (center_x - 2, center_y - 1, 4, 10))
            # Pin point
            pygame.draw.polygon(screen, icon_color, [
                (center_x - 2, center_y + 9),
                (center_x + 2, center_y + 9),
                (center_x, center_y + 13)
            ])
        else:
            # Unpinned icon (pushpin at angle)
            # Pin head (circle)
            pygame.draw.circle(screen, icon_color, (center_x - 3, center_y - 4), 5)
            pygame.draw.circle(screen, (180, 180, 180), (center_x - 3, center_y - 4), 5, 2)
            # Pin body (rotated rectangle)
            points = [
                (center_x - 1, center_y + 1),
                (center_x + 1, center_y - 1),
                (center_x + 7, center_y + 5),
                (center_x + 5, center_y + 7)
            ]
            pygame.draw.polygon(screen, icon_color, points)
            # Pin point
            pygame.draw.polygon(screen, icon_color, [
                (center_x + 5, center_y + 7),
                (center_x + 7, center_y + 5),
                (center_x + 10, center_y + 10)
            ])


logger = logging.getLogger(__name__)


def set_window_always_on_top(enable=True):
    """Set the pygame window to always stay on top (platform-specific).

    Args:
        enable: True to enable always-on-top, False to disable
    """
    system = platform.system()

    try:
        if system == "Windows":
            # Windows implementation
            import win32gui
            import win32con

            # Get pygame window handle
            hwnd = pygame.display.get_wm_info()['window']

            # Set window as topmost or not topmost
            flag = win32con.HWND_TOPMOST if enable else win32con.HWND_NOTOPMOST
            win32gui.SetWindowPos(
                hwnd,
                flag,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
            logger.info(f"Window always-on-top {'enabled' if enable else 'disabled'} (Windows)")

        elif system == "Darwin":  # macOS
            # macOS implementation
            from Cocoa import NSApp, NSFloatingWindowLevel, NSNormalWindowLevel

            # Get the pygame window
            window = NSApp.windows()[0]
            level = NSFloatingWindowLevel if enable else NSNormalWindowLevel
            window.setLevel_(level)
            logger.info(f"Window always-on-top {'enabled' if enable else 'disabled'} (macOS)")

        else:
            logger.warning(f"Always-on-top not supported on platform: {system}")

    except Exception as e:
        logger.warning(f"Failed to set window always on top: {e}")


# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (245, 235, 220)

# House area
HOUSE_RECT = pygame.Rect(50, 50, 800, 450)

# Door position
DOOR_POS = (50, 250)
DOOR_CENTER_OFFSET = (20, 40)

# Speech text options
ENTRY_TEXT_OPTIONS = [
    "Hello everyone!", "I'm here!", "Just arrived!", "Hey there!",
    "What's up?", "Good to be here!", "Hi folks!", "Made it!",
    "Knock knock!", "Coming through!", "Room for one more?",
    "Hope I'm not late!", "I'm back!", "Mind if I join?",
    "Thanks for having me!", "Finally here!", "Let me in!",
    "Honey, I'm home!", "Anybody home?", "Guess who's here!",
    "Did I miss anything?", "Perfect timing!", "Ready when you are!",
    "At your service!", "Couldn't stay away!", "What did I miss?"
]

EXIT_TEXT_OPTIONS = [
    "Goodbye!", "See you later!", "Gotta go!", "Catch you later!",
    "Time to leave!", "Bye everyone!", "Heading out!", "Later!",
    "Peace out!", "Take care!"
]

ACTIVE_TEXT_OPTIONS = [
    "I'm focused right now!", "Check this out!", "Working on something cool",
    "This is interesting...", "Let me show you this", "Almost done here!",
    "Getting things done", "In the zone!", "Making progress", "Hold on a sec...",
    "This is awesome!", "Just a moment...", "Concentrating hard",
    "Got something here", "Pay attention to me!"
]

IDLE_TEXT_OPTIONS = [
    "Just hanging out", "Taking a break", "Hmm...", "Waiting around",
    "Doing my thing", "Chilling here", "La la la...", "What's everyone up to?",
    "Relaxing for a bit", "Just vibing", "Minding my own business", "Anyone there?",
    "Feeling good", "Taking it easy", "Yawn...", "Stretching my legs",
    "Nice day in here", "What should I do next?", "Enjoying the moment",
    "All good over here"
]

# Spawn margins
SPAWN_MARGIN_X = 100
SPAWN_MARGIN_TOP = 120
SPAWN_MARGIN_BOTTOM = 80

# Proximity thresholds
DOOR_PROXIMITY_THRESHOLD = 50

# Display settings
FPS_FONT_SIZE = 24
FPS_DISPLAY_POS = (10, 10)
FPS_TEXT_COLOR = (100, 100, 100)

# Mute button settings
MUTE_BUTTON_SIZE = 40
MUTE_BUTTON_POS = (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60)

# Stats button settings
STATS_BUTTON_SIZE = 40
STATS_BUTTON_POS = (60, SCREEN_HEIGHT - 60)

# Always on top button settings
ALWAYS_ON_TOP_BUTTON_SIZE = 40
ALWAYS_ON_TOP_BUTTON_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)


class PygameHouseView:
    """Pygame-based house visualization."""

    def __init__(self, tracker, personification_manager: PersonificationManager):
        """Initialize pygame house view.

        Args:
            tracker: TimeTracker instance
            personification_manager: PersonificationManager instance
        """
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("OpenBob - Watch Your Apps Live!")
        self.clock = pygame.time.Clock()

        # Set always on top if enabled in config
        if ALWAYS_ON_TOP:
            set_window_always_on_top(True)

        self.tracker = tracker
        self.personification_manager = personification_manager

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.personas = pygame.sprite.Group()
        self.speech_bubbles = pygame.sprite.Group()

        # Door
        self.door = Door(DOOR_POS)
        self.all_sprites.add(self.door)

        # Tracking
        self._persona_map: Dict[int, Persona] = {}  # hwnd -> Persona
        self._exiting_personas = set()
        self._initial_load = True
        self._initial_windows_queue = []  # Queue for staggered initial entry
        self._last_spawn_time = 0.0  # Track when last persona was spawned
        self._spawn_delay = 0.5  # Delay between spawning personas (seconds)

        # Idle wandering
        self._last_wander_time: Dict[int, float] = {}  # hwnd -> last wander time
        self._wander_interval_min = 12.0  # Minimum seconds between wanders
        self._wander_interval_max = 40.0  # Maximum seconds between wanders

        # Idle speech
        self._last_speech_time: Dict[int, float] = {}  # hwnd -> last idle speech time
        self._speech_interval_min = 30.0  # Minimum seconds between idle speech (was 15.0)
        self._speech_interval_max = 90.0  # Maximum seconds between idle speech (was 45.0)
        self._speech_display_time: Dict[int, float] = {}  # hwnd -> when speech was displayed
        self._speech_duration = 5.0  # How long to display speech bubbles (seconds)

        # Persona spawn tracking
        self._persona_spawn_time: Dict[int, float] = {}  # hwnd -> spawn time
        self._speech_grace_period = 3.0  # Seconds before persona can speak after spawning

        # Furniture (static, drawn once)
        self._furniture_surface = self._create_furniture()

        # Particle system
        self.particles = ParticleSystem()

        # Sound system
        self.sounds = SoundManager(enabled=True)
        self.sounds.play_ambient(volume=0.05)

        # Door sound tracking
        self._door_was_open = False

        # FPS display cache
        self._fps_font = pygame.font.Font(None, FPS_FONT_SIZE)

        # Mute button
        self.mute_button = MuteButton(MUTE_BUTTON_POS, MUTE_BUTTON_SIZE)

        # Stats button and overlay
        self.stats_button = StatsButton(STATS_BUTTON_POS, STATS_BUTTON_SIZE)
        self.show_stats = False

        # Always on top button
        self.always_on_top_button = AlwaysOnTopButton(ALWAYS_ON_TOP_BUTTON_POS, ALWAYS_ON_TOP_BUTTON_SIZE)

        logger.info("Pygame house view initialized")

    def _draw_rug(self, surface, x, y, rug_x, rug_y):
        """Draw floor rug with pattern and fringe."""
        RUG_RED = (140, 50, 50)
        RUG_PATTERN = (180, 80, 80)
        WOOD_DARK = (101, 67, 33)

        # Main rug body
        pygame.draw.rect(surface, RUG_RED, (rug_x, rug_y, 200, 140))
        pygame.draw.rect(surface, WOOD_DARK, (rug_x, rug_y, 200, 140), 3)

        # Rug pattern (pixel art diamonds)
        for i in range(4):
            for j in range(3):
                px, py = rug_x + 30 + i * 45, rug_y + 20 + j * 40
                pygame.draw.polygon(surface, RUG_PATTERN, [
                    (px, py - 6), (px + 6, py), (px, py + 6), (px - 6, py)
                ])

        # Rug fringe (tassels)
        for i in range(0, 200, 8):
            pygame.draw.rect(surface, WOOD_DARK, (rug_x + i, rug_y + 140, 4, 6))
            pygame.draw.rect(surface, WOOD_DARK, (rug_x + i, rug_y - 6, 4, 6))

    def _draw_sofa(self, surface, sofa_x, sofa_y):
        """Draw pixel art sofa with cushions."""
        FABRIC_RED = (156, 40, 40)
        FABRIC_RED_DARK = (112, 28, 28)
        WOOD_DARK = (101, 67, 33)
        WOOD_MID = (139, 90, 43)

        # Sofa base
        pygame.draw.rect(surface, FABRIC_RED_DARK, (sofa_x, sofa_y + 15, 90, 35))
        pygame.draw.rect(surface, FABRIC_RED, (sofa_x + 2, sofa_y + 17, 86, 31))

        # Back cushion
        pygame.draw.rect(surface, FABRIC_RED_DARK, (sofa_x, sofa_y, 90, 20))
        pygame.draw.rect(surface, FABRIC_RED, (sofa_x + 2, sofa_y + 2, 86, 16))

        # Seat cushions
        for i in range(3):
            cx = sofa_x + 8 + i * 26
            pygame.draw.rect(surface, FABRIC_RED, (cx, sofa_y + 20, 22, 20))
            pygame.draw.rect(surface, FABRIC_RED_DARK, (cx, sofa_y + 20, 22, 20), 1)
            pygame.draw.line(surface, FABRIC_RED_DARK, (cx + 11, sofa_y + 22), (cx + 11, sofa_y + 38), 1)

        # Armrests
        pygame.draw.rect(surface, FABRIC_RED_DARK, (sofa_x - 2, sofa_y + 10, 8, 30))
        pygame.draw.rect(surface, FABRIC_RED_DARK, (sofa_x + 84, sofa_y + 10, 8, 30))

        # Wooden legs
        for lx in [sofa_x + 5, sofa_x + 35, sofa_x + 65, sofa_x + 80]:
            pygame.draw.rect(surface, WOOD_DARK, (lx, sofa_y + 50, 6, 8))

    def _draw_desk_and_monitor(self, surface, desk_x, desk_y):
        """Draw desk with monitor and lamp."""
        WOOD_DARK = (101, 67, 33)
        WOOD_MID = (139, 90, 43)
        WOOD_LIGHT = (180, 122, 48)
        SCREEN_BLUE = (48, 84, 150)
        SCREEN_CYAN = (88, 140, 190)
        METAL_GRAY = (120, 120, 130)
        METAL_LIGHT = (160, 160, 170)

        # Desk surface
        pygame.draw.rect(surface, WOOD_DARK, (desk_x, desk_y + 35, 120, 8))
        pygame.draw.rect(surface, WOOD_MID, (desk_x + 2, desk_y + 37, 116, 4))

        # Desk front panel with wood grain
        pygame.draw.rect(surface, WOOD_MID, (desk_x + 5, desk_y + 43, 110, 25))
        pygame.draw.rect(surface, WOOD_DARK, (desk_x + 5, desk_y + 43, 110, 25), 1)
        for i in range(desk_y + 45, desk_y + 66, 4):
            pygame.draw.line(surface, WOOD_LIGHT, (desk_x + 8, i), (desk_x + 112, i), 1)

        # Desk legs
        pygame.draw.rect(surface, WOOD_DARK, (desk_x + 10, desk_y + 43, 8, 25))
        pygame.draw.rect(surface, WOOD_DARK, (desk_x + 102, desk_y + 43, 8, 25))

        # Monitor
        monitor_x, monitor_y = desk_x + 35, desk_y
        pygame.draw.rect(surface, METAL_GRAY, (monitor_x + 18, monitor_y + 38, 14, 5))
        pygame.draw.rect(surface, METAL_GRAY, (monitor_x + 22, monitor_y + 30, 6, 8))
        pygame.draw.rect(surface, (20, 20, 22), (monitor_x, monitor_y + 2, 50, 35))
        pygame.draw.rect(surface, METAL_LIGHT, (monitor_x, monitor_y + 2, 50, 2))
        pygame.draw.rect(surface, SCREEN_BLUE, (monitor_x + 4, monitor_y + 6, 42, 26))
        pygame.draw.rect(surface, SCREEN_CYAN, (monitor_x + 6, monitor_y + 8, 38, 3))
        pygame.draw.rect(surface, SCREEN_CYAN, (monitor_x + 8, monitor_y + 14, 15, 2))
        pygame.draw.rect(surface, SCREEN_CYAN, (monitor_x + 8, monitor_y + 18, 22, 2))
        pygame.draw.rect(surface, SCREEN_CYAN, (monitor_x + 8, monitor_y + 22, 18, 2))

        # Desk lamp
        lamp_x, lamp_y = desk_x + 95, desk_y + 25
        pygame.draw.rect(surface, METAL_GRAY, (lamp_x + 6, lamp_y + 10, 3, 12))
        pygame.draw.circle(surface, METAL_GRAY, (lamp_x + 7, lamp_y + 8), 4)
        pygame.draw.polygon(surface, (255, 240, 200), [
            (lamp_x, lamp_y), (lamp_x + 14, lamp_y), (lamp_x + 12, lamp_y + 8), (lamp_x + 2, lamp_y + 8)
        ])
        pygame.draw.polygon(surface, METAL_GRAY, [
            (lamp_x, lamp_y), (lamp_x + 14, lamp_y), (lamp_x + 12, lamp_y + 8), (lamp_x + 2, lamp_y + 8)
        ], 1)
        pygame.draw.ellipse(surface, METAL_GRAY, (lamp_x + 3, lamp_y + 22, 8, 3))

    def _draw_tables_and_shelves(self, surface, x, y, w, h):
        """Draw coffee table, bookshelf, and side table."""
        WOOD_DARK = (101, 67, 33)
        WOOD_MID = (139, 90, 43)
        WOOD_LIGHT = (180, 122, 48)
        SHELF_BEIGE = (200, 180, 140)

        # Bookshelf
        shelf_x, shelf_y = x + 30, y + h - 120
        pygame.draw.rect(surface, WOOD_DARK, (shelf_x, shelf_y, 60, 100))
        pygame.draw.rect(surface, WOOD_MID, (shelf_x + 2, shelf_y + 2, 56, 96))
        for i in range(4):
            sy = shelf_y + 5 + i * 24
            pygame.draw.rect(surface, SHELF_BEIGE, (shelf_x + 4, sy, 52, 3))
            pygame.draw.rect(surface, WOOD_DARK, (shelf_x + 4, sy, 52, 1))

        # Books
        book_colors = [(180, 60, 60), (60, 120, 180), (60, 150, 80),
                      (200, 150, 50), (140, 80, 160), (220, 100, 50)]
        random.seed(42)
        for shelf_idx in range(4):
            sy = shelf_y + 8 + shelf_idx * 24
            bx = shelf_x + 6
            while bx < shelf_x + 50:
                book_color = random.choice(book_colors)
                book_width = random.randint(4, 9)
                book_height = random.randint(16, 20)
                pygame.draw.rect(surface, book_color, (bx, sy, book_width, book_height))
                pygame.draw.rect(surface, tuple(min(c + 40, 255) for c in book_color),
                               (bx + 1, sy + 1, book_width - 2, 2))
                pygame.draw.rect(surface, tuple(max(c - 40, 0) for c in book_color),
                               (bx, sy, book_width, book_height), 1)
                bx += book_width + random.randint(0, 2)
        random.seed()

    def _draw_plants(self, surface, x, y, w, h):
        """Draw pixel art plants in pots."""
        PLANT_GREEN_DARK = (28, 100, 28)
        PLANT_GREEN_LIGHT = (48, 156, 48)

        plant_positions = [
            (x + 200, y + 70),  # Top middle
        ]

        for px, py in plant_positions:
            # Pot
            pygame.draw.polygon(surface, (140, 70, 40), [
                (px + 6, py + 20), (px + 19, py + 20), (px + 17, py + 30), (px + 8, py + 30)
            ])
            pygame.draw.rect(surface, (100, 50, 30), (px + 6, py + 20, 13, 10), 1)
            pygame.draw.rect(surface, (80, 50, 30), (px + 7, py + 20, 11, 3))

            # Leaves
            leaf_positions = [
                (px + 12, py + 8), (px + 8, py + 12), (px + 16, py + 12),
                (px + 10, py + 16), (px + 14, py + 16), (px + 12, py + 18)
            ]
            for lx, ly in leaf_positions:
                pygame.draw.ellipse(surface, PLANT_GREEN_DARK, (lx - 3, ly - 4, 8, 10))
                pygame.draw.ellipse(surface, PLANT_GREEN_LIGHT, (lx - 2, ly - 3, 6, 8))
                pygame.draw.line(surface, PLANT_GREEN_DARK, (lx, ly - 2), (lx, ly + 3), 1)

    def _create_furniture(self):
        """Create static furniture layer with pixel art style.

        Returns:
            Surface with furniture drawn
        """
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        x, y = HOUSE_RECT.x, HOUSE_RECT.y
        w, h = HOUSE_RECT.width, HOUSE_RECT.height

        # Draw furniture using helper methods
        rug_x, rug_y = x + w // 2 - 100, y + h // 2 - 20
        self._draw_rug(surface, x, y, rug_x, rug_y)

        sofa_x, sofa_y = x + 240, y + 70
        self._draw_sofa(surface, sofa_x, sofa_y)

        desk_x, desk_y = x + w - 160, y + 100
        self._draw_desk_and_monitor(surface, desk_x, desk_y)

        self._draw_tables_and_shelves(surface, x, y, w, h)
        self._draw_plants(surface, x, y, w, h)

        return surface

    def _draw_house(self):
        """Draw the house background with pixel art style."""
        # Pixel art color palette for floor
        FLOOR_BASE = (210, 180, 140)
        FLOOR_LIGHT = (230, 200, 160)
        FLOOR_DARK = (180, 150, 110)
        PLANK_LINE = (160, 130, 90)
        WALL_BASE = (200, 190, 170)
        WALL_SHADE = (180, 170, 150)
        SHADOW = (80, 80, 80)

        # Drop shadow
        shadow_rect = HOUSE_RECT.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(self.screen, SHADOW, shadow_rect)

        # Wall background (subtle wallpaper effect)
        wall_rect = pygame.Rect(HOUSE_RECT.x - 10, HOUSE_RECT.y - 40,
                                HOUSE_RECT.width + 20, HOUSE_RECT.height + 50)
        pygame.draw.rect(self.screen, WALL_BASE, wall_rect)
        # Wallpaper pattern (small dots)
        for wx in range(wall_rect.x + 10, wall_rect.right - 10, 20):
            for wy in range(wall_rect.y + 10, wall_rect.bottom - 10, 20):
                pygame.draw.circle(self.screen, WALL_SHADE, (wx, wy), 2)

        # Main floor base
        pygame.draw.rect(self.screen, FLOOR_BASE, HOUSE_RECT)

        # Pixel art wood planks with detail
        plank_height = 40
        plank_y = HOUSE_RECT.y
        plank_offset = 0

        while plank_y < HOUSE_RECT.bottom:
            current_height = min(plank_height, HOUSE_RECT.bottom - plank_y)

            # Alternate plank offset for realistic wood floor pattern
            x_start = HOUSE_RECT.x

            while x_start < HOUSE_RECT.right:
                # Randomize plank width for variety (but keep consistent with seed)
                random.seed(int(plank_y) + int(x_start))
                plank_width = random.randint(80, 140)
                plank_width = min(plank_width, HOUSE_RECT.right - x_start)

                # Plank color variation (some lighter, some darker)
                color_var = random.choice([FLOOR_BASE, FLOOR_LIGHT, FLOOR_DARK])

                # Draw plank
                plank_rect = pygame.Rect(x_start, plank_y, plank_width, current_height)
                pygame.draw.rect(self.screen, color_var, plank_rect)

                # Wood grain lines (2-4 per plank)
                num_grains = random.randint(2, 4)
                for _ in range(num_grains):
                    grain_y = plank_y + random.randint(5, current_height - 5)
                    grain_length = random.randint(plank_width // 3, plank_width - 10)
                    grain_x = x_start + random.randint(5, max(5, plank_width - grain_length - 5))
                    pygame.draw.line(self.screen, PLANK_LINE,
                                   (grain_x, grain_y),
                                   (grain_x + grain_length, grain_y), 1)

                # Plank border (darker outline)
                pygame.draw.rect(self.screen, PLANK_LINE, plank_rect, 1)

                x_start += plank_width

            plank_y += current_height

        random.seed()  # Reset random seed

        # Outer border (house walls)
        pygame.draw.rect(self.screen, (40, 35, 30), HOUSE_RECT, 5)

        # Inner border highlight (pixel art depth)
        inner_border = HOUSE_RECT.copy()
        inner_border.inflate_ip(-10, -10)
        pygame.draw.line(self.screen, FLOOR_LIGHT,
                        (inner_border.left, inner_border.top),
                        (inner_border.right, inner_border.top), 2)
        pygame.draw.line(self.screen, FLOOR_LIGHT,
                        (inner_border.left, inner_border.top),
                        (inner_border.left, inner_border.bottom), 2)

        # Baseboard (trim along bottom)
        baseboard_rect = pygame.Rect(HOUSE_RECT.x, HOUSE_RECT.bottom - 15,
                                     HOUSE_RECT.width, 15)
        pygame.draw.rect(self.screen, (100, 80, 60), baseboard_rect)
        pygame.draw.rect(self.screen, (120, 100, 80),
                        (baseboard_rect.x + 2, baseboard_rect.y + 2,
                         baseboard_rect.width - 4, 8))
        pygame.draw.line(self.screen, (80, 60, 40),
                        (baseboard_rect.x, baseboard_rect.y),
                        (baseboard_rect.right, baseboard_rect.y), 2)

    def _get_door_center(self):
        """Get center position of door.

        Returns:
            Tuple (x, y)
        """
        return (DOOR_POS[0] + DOOR_CENTER_OFFSET[0], DOOR_POS[1] + DOOR_CENTER_OFFSET[1])

    def _get_random_position(self):
        """Get random position inside house.

        Returns:
            Tuple (x, y)
        """
        x = random.randint(HOUSE_RECT.x + SPAWN_MARGIN_X, HOUSE_RECT.right - SPAWN_MARGIN_X)
        y = random.randint(HOUSE_RECT.y + SPAWN_MARGIN_TOP, HOUSE_RECT.bottom - SPAWN_MARGIN_BOTTOM)
        return (x, y)

    def _get_entry_text(self):
        """Get random entry text."""
        return random.choice(ENTRY_TEXT_OPTIONS)

    def _get_exit_text(self):
        """Get random exit text."""
        return random.choice(EXIT_TEXT_OPTIONS)

    def _get_active_text(self):
        """Get random active/talking text."""
        return random.choice(ACTIVE_TEXT_OPTIONS)

    def _get_idle_text(self):
        """Get random idle speech text for non-active personas."""
        return random.choice(IDLE_TEXT_OPTIONS)

    def update(self, windows: List[WindowInfo]):
        """Update view with current windows.

        Args:
            windows: List of WindowInfo objects
        """
        current_hwnds = {w.hwnd for w in windows if w.is_visible}

        # On initial load, queue all windows for staggered entry
        if self._initial_load and len(windows) > 0:
            self._initial_windows_queue = [w for w in windows if w.is_visible]
            self._initial_load = False
            self._last_spawn_time = time.time()
            return

        # If still processing initial queue, only update existing personas
        if self._initial_windows_queue:
            # Only update personas that already exist
            for window in windows:
                if window.is_visible and window.hwnd in self._persona_map:
                    self._update_persona(window)
            return

        # Normal operation: Remove personas for closed windows
        for hwnd in list(self._persona_map.keys()):
            if hwnd not in current_hwnds and hwnd not in self._exiting_personas:
                self._exit_persona(hwnd)

        # Add or update personas
        for window in windows:
            if not window.is_visible:
                continue

            if window.hwnd not in self._persona_map:
                self._add_persona(window)
            else:
                self._update_persona(window)

    def _process_initial_queue(self):
        """Process the initial windows queue, spawning personas gradually."""
        if not self._initial_windows_queue:
            return

        current_time = time.time()
        time_since_last_spawn = current_time - self._last_spawn_time

        # Check if enough time has passed to spawn next persona
        if time_since_last_spawn >= self._spawn_delay:
            # Get next window from queue
            window = self._initial_windows_queue.pop(0)

            # Add persona (will be silent since not during initial_load)
            if window.hwnd not in self._persona_map:
                self._add_persona(window, suppress_effects=True)

            self._last_spawn_time = current_time

    def _add_persona(self, window: WindowInfo, suppress_effects=False):
        """Add a new persona.

        Args:
            window: WindowInfo object
            suppress_effects: Whether to suppress entry effects (sparkles, sounds, speech)
        """
        # Get persona info
        persona_name, activity = self.personification_manager.get_persona_for_window(
            window.hwnd, window.title, window.process_name
        )

        # Extract emoji
        emoji = activity.split()[0] if activity else "🧑"

        # Entry speech (suppressed if requested or initial load)
        speech = None if suppress_effects else self._get_entry_text()

        # Create persona at door
        door_center = self._get_door_center()
        persona = Persona(emoji, persona_name, door_center, speech)

        # Add to groups
        self.personas.add(persona)
        self.all_sprites.add(persona)
        if persona.speech_bubble:
            self.speech_bubbles.add(persona.speech_bubble)
            self.all_sprites.add(persona.speech_bubble)

        # Set target position
        target = self._get_random_position()
        persona.set_target(target)

        # Store mapping
        self._persona_map[window.hwnd] = persona

        # Track spawn time for grace period
        self._persona_spawn_time[window.hwnd] = time.time()

        # Initialize wander timer with highly varied random offset so personas don't all wander simultaneously
        # Use full range and add extra randomness to prevent clustering
        random_offset = random.uniform(self._wander_interval_min, self._wander_interval_max * 1.2)
        self._last_wander_time[window.hwnd] = time.time() - random_offset

        # Initialize idle speech timer with highly varied random offset
        # Use full range and add extra randomness to prevent clustering
        speech_offset = random.uniform(self._speech_interval_min, self._speech_interval_max * 1.2)
        self._last_speech_time[window.hwnd] = time.time() - speech_offset

        # Emit entry sparkles and sound (unless suppressed)
        if not suppress_effects:
            self.particles.emit_sparkles(door_center, count=25)
            self.sounds.play('hello', volume=0.4)

        logger.info(f"Added persona: {persona_name}")

    def _update_persona(self, window: WindowInfo):
        """Update existing persona.

        Args:
            window: WindowInfo object
        """
        if window.hwnd not in self._persona_map:
            return

        persona = self._persona_map[window.hwnd]

        # Update active state and speech
        persona.is_active = window.is_active

        # Check if persona is still in grace period (just spawned)
        spawn_time = self._persona_spawn_time.get(window.hwnd, 0)
        in_grace_period = (time.time() - spawn_time) < self._speech_grace_period

        if window.is_active and not in_grace_period:
            # Set active speech if not already speaking (or if speaking exit text)
            if not persona.speech_text or persona.speech_text in EXIT_TEXT_OPTIONS:
                speech = self._get_active_text()
                persona.set_speech(speech)
                if persona.speech_bubble:
                    # pygame.sprite.Group.add() is idempotent - safe to call multiple times
                    self.speech_bubbles.add(persona.speech_bubble)
                    self.all_sprites.add(persona.speech_bubble)
        else:
            # Only clear ACTIVE speech when window becomes inactive (preserve idle speech and exit speech)
            if persona.speech_text and persona.speech_text in ACTIVE_TEXT_OPTIONS:
                persona.set_speech(None)
                if persona.speech_bubble:
                    persona.speech_bubble.kill()

    def _exit_persona(self, hwnd: int):
        """Start exit animation for persona.

        Args:
            hwnd: Window handle
        """
        if hwnd not in self._persona_map or hwnd in self._exiting_personas:
            return

        self._exiting_personas.add(hwnd)
        persona = self._persona_map[hwnd]

        # Set exit speech
        exit_text = self._get_exit_text()
        persona.set_speech(exit_text)
        if persona.speech_bubble:
            if persona.speech_bubble not in self.all_sprites:
                self.speech_bubbles.add(persona.speech_bubble)
                self.all_sprites.add(persona.speech_bubble)

        # Move to door
        door_center = self._get_door_center()
        persona.set_target(door_center)

        # Play goodbye sound
        self.sounds.play('goodbye', volume=0.4)

        logger.info(f"Persona exiting: {persona.name}")

    def _check_door_proximity(self):
        """Check if any personas are near door and open/close accordingly."""
        door_center = self._get_door_center()
        near_door = False
        distance_threshold_sq = DOOR_PROXIMITY_THRESHOLD ** 2

        for persona in self.personas:
            dx = persona.pos[0] - door_center[0]
            dy = persona.pos[1] - door_center[1]
            distance_sq = dx * dx + dy * dy

            if distance_sq < distance_threshold_sq:
                near_door = True
                break

        # Door logic with sounds
        if near_door and not self._door_was_open:
            self.door.open()
            self.sounds.play('door_open', volume=0.3)
            self._door_was_open = True
        elif not near_door and self._door_was_open:
            self.door.close()
            self.sounds.play('door_close', volume=0.25)
            self._door_was_open = False

    def _remove_exited_personas(self):
        """Remove personas that have completed exit animation."""
        for hwnd in list(self._exiting_personas):
            if hwnd in self._persona_map:
                persona = self._persona_map[hwnd]

                # Check if reached door
                door_center = self._get_door_center()
                dx = persona.pos[0] - door_center[0]
                dy = persona.pos[1] - door_center[1]
                distance_sq = dx * dx + dy * dy  # Skip expensive square root

                if distance_sq < 100 and not persona.is_moving:  # 10 * 10 = 100
                    # Emit exit poof
                    self.particles.emit_exit_poof(persona.pos, count=20)

                    # Remove persona
                    if persona.speech_bubble:
                        persona.speech_bubble.kill()
                    persona.kill()
                    del self._persona_map[hwnd]
                    self._exiting_personas.remove(hwnd)
                    if hwnd in self._last_wander_time:
                        del self._last_wander_time[hwnd]
                    if hwnd in self._last_speech_time:
                        del self._last_speech_time[hwnd]
                    if hwnd in self._speech_display_time:
                        del self._speech_display_time[hwnd]
                    if hwnd in self._persona_spawn_time:
                        del self._persona_spawn_time[hwnd]
                    logger.info("Persona removed after exit")

    def _update_idle_wandering(self):
        """Make personas occasionally wander to random positions."""
        current_time = time.time()

        for hwnd, persona in list(self._persona_map.items()):
            # Skip if exiting or currently moving
            if hwnd in self._exiting_personas or persona.is_moving:
                continue

            # Check if enough time has passed since last wander
            last_wander = self._last_wander_time.get(hwnd, 0)
            time_since_wander = current_time - last_wander

            # Random interval with extra variance to prevent synchronization
            next_wander_time = random.uniform(self._wander_interval_min, self._wander_interval_max)
            # Add unique per-persona variance based on hwnd to further desynchronize
            persona_variance = (hwnd % 10) * 0.5  # 0-4.5 seconds variance
            next_wander_time += persona_variance

            if time_since_wander >= next_wander_time:
                # Time to wander! Pick a random position
                new_pos = self._get_random_position()
                persona.set_target(new_pos)
                self._last_wander_time[hwnd] = current_time
                logger.debug(f"Persona {persona.name} wandering to new position")

    def _update_idle_speech(self):
        """Make non-active personas occasionally say idle things."""
        current_time = time.time()

        for hwnd, persona in list(self._persona_map.items()):
            # Skip if exiting or currently active (active personas have their own speech)
            if hwnd in self._exiting_personas or persona.is_active:
                continue

            # Check if enough time has passed since last idle speech
            last_speech = self._last_speech_time.get(hwnd, 0)
            time_since_speech = current_time - last_speech

            # Random interval with extra variance to prevent synchronization
            next_speech_time = random.uniform(self._speech_interval_min, self._speech_interval_max)
            # Add unique per-persona variance based on hwnd to further desynchronize
            persona_variance = (hwnd % 15) * 2.0  # 0-28 seconds variance
            next_speech_time += persona_variance

            if time_since_speech >= next_speech_time:
                # Time to say something! Get random idle text
                idle_text = self._get_idle_text()
                persona.set_speech(idle_text)
                if persona.speech_bubble:
                    if persona.speech_bubble not in self.all_sprites:
                        self.speech_bubbles.add(persona.speech_bubble)
                        self.all_sprites.add(persona.speech_bubble)
                self._last_speech_time[hwnd] = current_time
                self._speech_display_time[hwnd] = current_time  # Track when speech was displayed
                logger.debug(f"Persona {persona.name} saying: {idle_text}")

    def _clear_expired_speech(self):
        """Clear speech bubbles that have been displayed for too long."""
        current_time = time.time()

        for hwnd, persona in list(self._persona_map.items()):
            # Skip if exiting or active (active personas manage their own speech)
            if hwnd in self._exiting_personas or persona.is_active:
                continue

            # Check if this persona has speech displayed
            if hwnd in self._speech_display_time and persona.speech_text:
                display_time = self._speech_display_time[hwnd]
                time_displayed = current_time - display_time

                # Clear speech if it's been displayed too long
                if time_displayed >= self._speech_duration:
                    persona.set_speech(None)
                    if persona.speech_bubble:
                        persona.speech_bubble.kill()
                    del self._speech_display_time[hwnd]
                    logger.debug(f"Cleared expired speech for {persona.name}")

    def _draw_stats_panel_background(self, panel_x, panel_y, panel_width, panel_height):
        """Draw the stats panel background with shadow and gradient."""
        # Drop shadow
        shadow_offset = 8
        shadow_rect = pygame.Rect(panel_x + shadow_offset, panel_y + shadow_offset, panel_width, panel_height)
        shadow_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=20)
        self.screen.blit(shadow_surf, (panel_x + shadow_offset, panel_y + shadow_offset))

        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, border_radius=20)

        # Gradient header
        header_height = 70
        gradient_surf = pygame.Surface((panel_width, header_height), pygame.SRCALPHA)
        for i in range(header_height):
            alpha = int(20 * (1 - i / header_height))
            color = (180, 200, 220, alpha)
            pygame.draw.rect(gradient_surf, color, (0, i, panel_width, 1))

        # Mask for rounded corners
        mask_surf = pygame.Surface((panel_width, header_height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, panel_width, header_height), border_radius=20)
        gradient_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.screen.blit(gradient_surf, (panel_x, panel_y))

        # Border
        pygame.draw.rect(self.screen, (100, 140, 180), panel_rect, 4, border_radius=20)

    def _draw_stats_header(self, panel_x, panel_y, panel_width, panel_height):
        """Draw stats overlay title and close instruction."""
        # Title
        title_font = pygame.font.Font(None, 52)
        title_surf = title_font.render("App Usage Statistics", True, (40, 60, 80))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 38))
        self.screen.blit(title_surf, title_rect)

        # Close instruction
        close_font = pygame.font.Font(None, 22)
        close_surf = close_font.render("Click anywhere to close", True, (140, 140, 140))
        close_rect = close_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 20))
        self.screen.blit(close_surf, close_rect)

    def _draw_stats_table_header(self, panel_x, panel_y):
        """Draw the stats table column headers."""
        y_offset = panel_y + 95
        header_font = pygame.font.Font(None, 26)
        headers = ["App", "Total Time", "Active Time", "Usage"]
        x_positions = [panel_x + 70, panel_x + 330, panel_x + 490, panel_x + 600]

        for i, header in enumerate(headers):
            header_surf = header_font.render(header, True, (60, 80, 100))
            self.screen.blit(header_surf, (x_positions[i], y_offset))

        # Decorative divider
        gradient_line_y = y_offset + 30
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.line(self.screen, (100, 140, 180, alpha),
                           (panel_x + 25, gradient_line_y + i),
                           (panel_x + 750 - 25, gradient_line_y + i), 1)

        return y_offset + 45, x_positions

    def _draw_stats_overlay(self):
        """Draw the stats overlay showing app usage times."""
        # Semi-transparent background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))

        # Panel dimensions
        panel_width = 750
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        # Draw panel components
        self._draw_stats_panel_background(panel_x, panel_y, panel_width, panel_height)
        self._draw_stats_header(panel_x, panel_y, panel_width, panel_height)
        y_offset, x_positions = self._draw_stats_table_header(panel_x, panel_y)

        # Get sorted windows
        windows = self.tracker.get_all_windows()
        sorted_windows = sorted(windows, key=lambda w: w.total_open_time, reverse=True)

        # Setup fonts and rendering parameters
        stats_font = pygame.font.Font(None, 24)
        emoji_font = pygame.font.SysFont('segoeuiemoji,applesymbolsbook,notocoloremoji', 24)
        line_height = 38
        max_lines = 8

        # Display each window with enhanced visuals
        for idx, window in enumerate(sorted_windows[:max_lines]):
            # Get persona info with emoji
            persona_name, activity = self.personification_manager.get_persona_for_window(
                window.hwnd, window.title, window.process_name
            )
            emoji = activity.split()[0] if activity else "🧑"

            # Format times using utility function
            total_time_str = format_timedelta(window.total_open_time)
            active_time_str = format_timedelta(window.active_time)

            # Get seconds for progress bar calculation
            total_seconds = int(window.total_open_time.total_seconds())
            active_seconds = int(window.active_time.total_seconds())

            # Alternate row colors with gradient
            if idx % 2 == 0:
                row_rect = pygame.Rect(panel_x + 25, y_offset - 6, panel_width - 50, line_height)
                pygame.draw.rect(self.screen, (245, 248, 252), row_rect, border_radius=8)

            # Highlight active window
            if window.is_active:
                row_rect = pygame.Rect(panel_x + 25, y_offset - 6, panel_width - 50, line_height)
                pygame.draw.rect(self.screen, (255, 250, 220), row_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 215, 0), row_rect, 2, border_radius=8)

            # Draw emoji
            emoji_surf = emoji_font.render(emoji, True, (0, 0, 0))
            self.screen.blit(emoji_surf, (panel_x + 40, y_offset))

            # Draw app name (truncate to prevent overflow)
            max_name_length = 20
            display_name = persona_name[:max_name_length]
            if len(persona_name) > max_name_length:
                display_name = display_name[:-1] + "…"
            name_surf = stats_font.render(display_name, True, (40, 40, 40))
            self.screen.blit(name_surf, (x_positions[0], y_offset + 2))

            # Draw times with icons
            total_surf = stats_font.render(total_time_str, True, (60, 90, 120))
            self.screen.blit(total_surf, (x_positions[1], y_offset + 2))

            active_surf = stats_font.render(active_time_str, True, (80, 140, 80))
            self.screen.blit(active_surf, (x_positions[2], y_offset + 2))

            # Progress bar showing active/total ratio
            bar_width = 90
            bar_height = 12
            bar_x = x_positions[3]
            bar_y = y_offset + 6

            # Background bar
            pygame.draw.rect(self.screen, (220, 220, 220),
                           (bar_x, bar_y, bar_width, bar_height), border_radius=6)

            # Active time bar
            if total_seconds > 0:
                ratio = min(active_seconds / total_seconds, 1.0)
                active_bar_width = int(bar_width * ratio)

                # Gradient color based on ratio
                if ratio > 0.7:
                    bar_color = (100, 200, 100)  # Green for high usage
                elif ratio > 0.3:
                    bar_color = (255, 180, 0)    # Orange for medium
                else:
                    bar_color = (180, 180, 200)  # Gray for low

                if active_bar_width > 0:
                    pygame.draw.rect(self.screen, bar_color,
                                   (bar_x, bar_y, active_bar_width, bar_height), border_radius=6)

                # Percentage text (right-aligned within remaining space)
                percent_text = f"{int(ratio * 100)}%"
                percent_font = pygame.font.Font(None, 18)
                percent_surf = percent_font.render(percent_text, True, (100, 100, 100))
                # Position with right margin
                percent_x = min(bar_x + bar_width + 8, panel_x + panel_width - 50)
                self.screen.blit(percent_surf, (percent_x, y_offset + 4))

            y_offset += line_height

    def render(self):
        """Render the scene."""
        # Background
        self.screen.fill(BACKGROUND_COLOR)

        # House
        self._draw_house()

        # Furniture (static layer)
        self.screen.blit(self._furniture_surface, (0, 0))

        # All sprites (door, personas, speech bubbles)
        self.all_sprites.draw(self.screen)

        # Particles (on top)
        self.particles.draw(self.screen)

        # UI elements
        self.mute_button.draw(self.screen)
        self.stats_button.draw(self.screen)
        self.always_on_top_button.draw(self.screen)

        # Stats overlay (if enabled)
        if self.show_stats:
            self._draw_stats_overlay()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()

                        # Check if stats overlay is showing - close it on any click
                        if self.show_stats:
                            self.show_stats = False
                            continue

                        # Check stats button
                        if self.stats_button.handle_click(mouse_pos):
                            self.show_stats = True
                            logger.info("Stats overlay opened")
                            continue

                        # Check mute button
                        if self.mute_button.handle_click(mouse_pos):
                            self.mute_button.toggle()
                            self.sounds.toggle_mute()
                            logger.info(f"Sound {'muted' if self.mute_button.is_muted else 'unmuted'}")
                            continue

                        # Check always-on-top button
                        if self.always_on_top_button.handle_click(mouse_pos):
                            self.always_on_top_button.toggle()
                            set_window_always_on_top(self.always_on_top_button.is_pinned)
                            logger.info(f"Always on top {'enabled' if self.always_on_top_button.is_pinned else 'disabled'}")

            # Update button hover states
            mouse_pos = pygame.mouse.get_pos()
            self.mute_button.update(mouse_pos)
            self.stats_button.update(mouse_pos)
            self.always_on_top_button.update(mouse_pos)

            # Get latest window data
            windows = self.tracker.get_all_windows()
            self.update(windows)

            # Process initial queue for staggered entry
            self._process_initial_queue()

            # Update sprites (pass dust emission callback)
            for sprite in self.all_sprites:
                if isinstance(sprite, Persona):
                    should_emit_glow = sprite.update(dt, emit_dust_callback=self.particles.emit_dust)
                    # Emit active glow based on timer (not random chance)
                    if should_emit_glow:
                        self.particles.emit_active_glow((sprite.pos[0], sprite.pos[1] - 30))
                else:
                    sprite.update(dt)

            # Update particles
            self.particles.update(dt)

            # Door logic
            self._check_door_proximity()

            # Remove exited personas
            self._remove_exited_personas()

            # Update idle wandering
            self._update_idle_wandering()

            # Update idle speech
            self._update_idle_speech()

            # Clear expired speech bubbles
            self._clear_expired_speech()

            # Render
            self.render()

            # Display FPS
            fps_text = f"FPS: {int(self.clock.get_fps())}"
            fps_surf = self._fps_font.render(fps_text, True, FPS_TEXT_COLOR)
            self.screen.blit(fps_surf, FPS_DISPLAY_POS)

            pygame.display.flip()

        pygame.quit()
