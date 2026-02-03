"""Personification layer - maps real windows to people and activities in a house."""
import random
from typing import Dict, Tuple

# Titles/prefixes to personify app names
TITLES = [
    "Mr.", "Ms.", "Sir", "Lady", "Captain", "Dr.", "Professor",
    "Chief", "Master", "Madam", "Lord", "Dame"
]

# Emojis to assign to different app types
EMOJI_MAP = {
    "chrome": "🌐", "firefox": "🦊", "edge": "🌊", "safari": "🧭",
    "discord": "🎧", "slack": "💼", "teams": "👔", "zoom": "📹",
    "spotify": "🎵", "music": "🎵", "netflix": "🎬", "vlc": "📺",
    "word": "📝", "excel": "📊", "powerpoint": "📊", "outlook": "📧",
    "code": "💻", "vscode": "💻", "terminal": "⌨️", "cmd": "⌨️",
    "calculator": "🔢", "notepad": "📄", "photos": "📷", "files": "📁",
    "steam": "🎮", "minecraft": "⛏️", "roblox": "🎮", "game": "🎮",
    "default": "🧑"
}

# Diverse human emojis for apps without specific icons
DIVERSE_PEOPLE = [
    # Various skin tones and genders
    "👨", "👩", "🧑",  # Light skin tone
    "👨🏻", "👩🏻", "🧑🏻",  # Light
    "👨🏼", "👩🏼", "🧑🏼",  # Medium-light
    "👨🏽", "👩🏽", "🧑🏽",  # Medium
    "👨🏾", "👩🏾", "🧑🏾",  # Medium-dark
    "👨🏿", "👩🏿", "🧑🏿",  # Dark
    # Different hair colors
    "👱", "👱‍♀️", "👱‍♂️",  # Blond
    "👨‍🦰", "👩‍🦰",  # Red hair
    "👨‍🦱", "👩‍🦱",  # Curly hair
    "👨‍🦳", "👩‍🦳",  # White hair
    "👨‍🦲", "👩‍🦲",  # Bald
    # Age diversity
    "🧒", "🧒🏻", "🧒🏼", "🧒🏽", "🧒🏾", "🧒🏿",  # Child
    "🧓", "🧓🏻", "🧓🏼", "🧓🏽", "🧓🏾", "🧓🏿",  # Older person
]

# Map app types to house activities (generic, don't mention app names)
ACTIVITY_MAPPINGS = {
    # Browsers
    "chrome": ["reading on the couch", "relaxing in living room", "looking something up at kitchen table", "browsing on tablet in den"],
    "firefox": ["reading in the den", "sitting at the desk", "looking at something on laptop"],
    "edge": ["working in home office", "researching at desk", "reading at computer"],
    "safari": ["browsing on laptop in bedroom", "looking at screen on couch"],

    # Social & Communication
    "discord": ["chatting in bedroom", "talking on phone", "laughing at something funny"],
    "slack": ["working quietly in home office", "typing messages at desk"],
    "teams": ["on a call in study", "having a meeting in office"],
    "zoom": ["on a video call", "meeting in home office"],
    "skype": ["video calling relatives", "talking to friends"],
    "messenger": ["texting in bedroom", "sending messages"],

    # Entertainment
    "spotify": ["listening to music in bedroom", "humming along to music", "enjoying tunes in living room"],
    "netflix": ["watching TV in living room", "relaxing with entertainment", "enjoying a show"],
    "youtube": ["watching something on couch", "entertained in den"],
    "vlc": ["watching something in living room", "enjoying media"],
    "steam": ["playing games in bedroom", "having fun at computer", "gaming in den"],
    "minecraft": ["playing in playroom", "building something creative", "having fun at desk"],
    "roblox": ["playing in playroom", "creating in bedroom", "having fun"],

    # Productivity
    "word": ["writing at desk", "working on project in study", "typing in office"],
    "excel": ["working with numbers at desk", "organizing at computer", "calculating in office"],
    "powerpoint": ["preparing something in office", "working on project at desk"],
    "outlook": ["checking messages at desk", "organizing in office", "planning at computer"],
    "notepad": ["jotting notes at desk", "writing ideas down", "making a list"],
    "code": ["working in home office", "concentrating at computer", "focused at desk"],
    "vscode": ["working at desk", "typing away in office", "focused on project"],
    "terminal": ["working at computer", "doing technical work at desk"],

    # Utilities
    "calculator": ["doing math at desk", "calculating in office", "working on numbers"],
    "calendar": ["planning at desk", "organizing schedule", "checking dates"],
    "photos": ["looking at photo albums", "organizing pictures", "browsing photos"],
    "files": ["organizing in office", "looking for something", "tidying up files"],
    "explorer": ["organizing in office", "searching for something"],

    # Default
    "default": ["busy at desk", "working on something", "focused at computer", "doing something at laptop"]
}

# Rooms in the house
ROOMS = [
    "living room", "kitchen", "bedroom", "home office", "den",
    "playroom", "study", "dining room", "backyard patio", "garage workshop"
]


class PersonificationManager:
    """Manages the personification of windows as people in a house."""

    def __init__(self):
        """Initialize the personification manager."""
        self._window_to_persona: Dict[int, Dict] = {}  # hwnd -> persona info
        self._used_names: Dict[str, int] = {}  # Track name usage for uniqueness
        self._person_emoji_pool = list(DIVERSE_PEOPLE)  # Copy of diverse people pool
        random.shuffle(self._person_emoji_pool)  # Shuffle for variety
        self._person_emoji_index = 0  # Current index in pool

    def get_persona_for_window(self, hwnd: int, title: str, process_name: str) -> Tuple[str, str]:
        """Get or create a persona for a window.

        Args:
            hwnd: Window handle
            title: Window title
            process_name: Process name

        Returns:
            Tuple of (persona_name, activity_description)
        """
        # Check if we already have a persona for this window
        if hwnd in self._window_to_persona:
            persona_info = self._window_to_persona[hwnd]
            activity = self._generate_activity(title, process_name, persona_info)
            return persona_info['name'], activity

        # Assign a new persona
        persona = self._assign_persona(process_name)
        self._window_to_persona[hwnd] = persona
        activity = self._generate_activity(title, process_name, persona)

        return persona['name'], activity

    def _assign_persona(self, process_name: str) -> Dict:
        """Assign a persona to a new window based on process name.

        Args:
            process_name: Name of the process

        Returns:
            Persona dictionary with name and emoji
        """
        # Clean up process name (remove .exe, etc.)
        clean_name = process_name.replace('.exe', '').replace('.app', '')
        clean_name = clean_name.strip()

        # Capitalize first letter
        if clean_name:
            base_name = clean_name[0].upper() + clean_name[1:]
        else:
            base_name = "Unknown"

        # Generate a unique personified name
        persona_name = self._generate_unique_name(base_name, process_name.lower())

        # Get appropriate emoji
        emoji = self._get_emoji_for_app(process_name.lower())

        return {
            'name': persona_name,
            'emoji': emoji
        }

    def _generate_unique_name(self, base_name: str, process_lower: str) -> str:
        """Generate a unique personified name.

        Args:
            base_name: Cleaned up base name
            process_lower: Lowercase process name for checking

        Returns:
            Unique personified name
        """
        # Check if this base name already exists
        if base_name not in self._used_names:
            self._used_names[base_name] = 0
            # First instance - just use the name
            return base_name
        else:
            # Multiple instances - add a number
            self._used_names[base_name] += 1
            count = self._used_names[base_name]
            return f"{base_name} #{count + 1}"

    def _get_emoji_for_app(self, process_lower: str) -> str:
        """Get an appropriate emoji for an app.

        Args:
            process_lower: Lowercase process name

        Returns:
            Emoji string
        """
        # Check for matches in emoji map
        for key, emoji in EMOJI_MAP.items():
            if key in process_lower:
                return emoji

        # For apps without specific emoji, use diverse person
        # Get next person from pool (cycling through)
        emoji = self._person_emoji_pool[self._person_emoji_index]
        self._person_emoji_index = (self._person_emoji_index + 1) % len(self._person_emoji_pool)

        return emoji

    def _generate_activity(self, title: str, process_name: str, persona: Dict) -> str:
        """Generate an activity description for a persona.

        Args:
            title: Window title
            process_name: Process name
            persona: Persona dictionary

        Returns:
            Activity description
        """
        process_lower = process_name.lower()

        # Try to find matching activity mapping
        activities = None
        for app_key, app_activities in ACTIVITY_MAPPINGS.items():
            if app_key in process_lower:
                activities = app_activities
                break

        # Use default if no match
        if not activities:
            activities = ACTIVITY_MAPPINGS["default"]

        # Pick a random activity
        activity = random.choice(activities)

        # Add emoji to make it more fun
        return f"{persona['emoji']} {activity}"

    def remove_window(self, hwnd: int):
        """Remove a window's persona mapping.

        Args:
            hwnd: Window handle
        """
        if hwnd in self._window_to_persona:
            del self._window_to_persona[hwnd]

    def clear_all(self):
        """Clear all persona mappings."""
        self._window_to_persona.clear()
        self._used_names.clear()

    def get_persona_count(self) -> int:
        """Get the number of active personas (people in the house).

        Returns:
            Number of active personas
        """
        return len(self._window_to_persona)

    def format_window_for_display(self, hwnd: int, title: str, process_name: str,
                                   is_active: bool) -> Tuple[str, str]:
        """Format a window for personified display.

        Args:
            hwnd: Window handle
            title: Window title
            process_name: Process name
            is_active: Whether window is currently active

        Returns:
            Tuple of (display_title, display_process)
        """
        persona_name, activity = self.get_persona_for_window(hwnd, title, process_name)

        # Format the display
        status_indicator = "🗣️ " if is_active else ""
        display_title = f"{status_indicator}{persona_name} - {activity}"
        display_process = f"in the house"

        return display_title, display_process
