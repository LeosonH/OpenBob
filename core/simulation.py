"""Simulation mode for testing - simulates people doing activities in a house."""
import random
from datetime import datetime
from typing import List, Tuple

# Family members and friends
PEOPLE = [
    {"name": "Mom", "process": "parent.exe", "personality": "busy"},
    {"name": "Dad", "process": "parent.exe", "personality": "relaxed"},
    {"name": "Sarah", "process": "teenager.exe", "personality": "social"},
    {"name": "Tommy", "process": "kid.exe", "personality": "energetic"},
    {"name": "Grandma", "process": "elder.exe", "personality": "calm"},
    {"name": "Uncle Joe", "process": "visitor.exe", "personality": "chatty"},
    {"name": "Aunt Linda", "process": "visitor.exe", "personality": "helpful"},
    {"name": "Best Friend Alex", "process": "friend.exe", "personality": "fun"},
    {"name": "Neighbor Bob", "process": "neighbor.exe", "personality": "curious"},
]

# Activities people can do in the house
ACTIVITIES = {
    "busy": [
        "Cooking dinner in the kitchen",
        "Doing laundry",
        "Cleaning the living room",
        "Working on laptop in home office",
        "Organizing the garage",
        "Paying bills at desk",
        "Meal prepping",
        "Vacuuming upstairs",
    ],
    "relaxed": [
        "Watching TV in living room",
        "Reading newspaper on couch",
        "Napping on recliner",
        "Listening to music in den",
        "Having coffee in kitchen",
        "Working on puzzle",
        "Browsing phone on patio",
        "Grilling in backyard",
    ],
    "social": [
        "Video chatting with friends",
        "Texting in bedroom",
        "Taking selfies",
        "Posting on social media",
        "Watching TikTok videos",
        "Listening to music and dancing",
        "Video calling boyfriend",
        "Shopping online",
    ],
    "energetic": [
        "Playing video games",
        "Running around backyard",
        "Playing with dog",
        "Building with LEGO",
        "Jumping on trampoline",
        "Riding bike in driveway",
        "Playing basketball",
        "Making a mess in playroom",
    ],
    "calm": [
        "Knitting on couch",
        "Watching cooking show",
        "Reading book in armchair",
        "Doing crossword puzzle",
        "Looking at photo albums",
        "Watering plants",
        "Baking cookies",
        "Having tea in garden",
    ],
    "chatty": [
        "Telling stories in living room",
        "Making phone calls",
        "Chatting at kitchen table",
        "Sharing old photos",
        "Discussing sports",
        "Debating politics",
        "Laughing about old times",
        "Giving unsolicited advice",
    ],
    "helpful": [
        "Helping with dishes",
        "Teaching recipe to Mom",
        "Fixing things around house",
        "Gardening in backyard",
        "Folding laundry",
        "Setting the table",
        "Giving parenting tips",
        "Organizing pantry",
    ],
    "fun": [
        "Playing board games",
        "Telling jokes",
        "Playing cards",
        "Watching comedy show",
        "Planning weekend trip",
        "Playing music together",
        "Having pillow fight",
        "Making funny videos",
    ],
    "curious": [
        "Peeking through window",
        "Asking about new car",
        "Checking out renovations",
        "Discussing neighborhood gossip",
        "Admiring the garden",
        "Asking to borrow tools",
        "Sharing HOA concerns",
        "Talking about weather",
    ],
}


class SimulatedPerson:
    """Represents a simulated person in the house."""

    def __init__(self, person_data: dict):
        """Initialize a simulated person.

        Args:
            person_data: Dictionary with name, process, personality
        """
        self.name = person_data["name"]
        self.process_name = person_data["process"]
        self.personality = person_data["personality"]
        self.hwnd = random.randint(10000, 99999)  # Fake window handle
        self.current_activity = self._get_random_activity()
        self.activity_start_time = datetime.now()
        self.boredom_factor = random.uniform(0.3, 0.7)  # How quickly they change activities

    def _get_random_activity(self) -> str:
        """Get a random activity based on personality."""
        activities = ACTIVITIES.get(self.personality, ACTIVITIES["relaxed"])
        return random.choice(activities)

    def maybe_change_activity(self) -> bool:
        """Randomly decide if person should change activity.

        Returns:
            True if activity changed, False otherwise
        """
        # Random chance based on boredom factor
        if random.random() < self.boredom_factor * 0.1:  # 3-7% chance per update
            self.current_activity = self._get_random_activity()
            self.activity_start_time = datetime.now()
            return True
        return False

    def get_window_info(self) -> Tuple[int, str, str]:
        """Get window information tuple.

        Returns:
            Tuple of (hwnd, title, process_name)
        """
        title = f"{self.name} - {self.current_activity}"
        return (self.hwnd, title, self.process_name)


class HouseSimulation:
    """Manages the house simulation with people doing activities."""

    def __init__(self, num_people: int = None):
        """Initialize the house simulation.

        Args:
            num_people: Number of people to simulate (None for random 4-9)
        """
        if num_people is None:
            num_people = random.randint(4, 9)

        # Randomly select people
        selected_people = random.sample(PEOPLE, min(num_people, len(PEOPLE)))
        self.people = [SimulatedPerson(person) for person in selected_people]

        # Track who is currently the "focus"
        self.current_focus_index = 0
        self.focus_duration = random.uniform(5, 15)  # Seconds before focus changes
        self.last_focus_change = datetime.now()

    def update(self) -> Tuple[List[Tuple[int, str, str]], int]:
        """Update the simulation state.

        Returns:
            Tuple of (list of window info tuples, active hwnd)
        """
        # Maybe change activities for some people
        for person in self.people:
            person.maybe_change_activity()

        # Maybe change focus
        time_since_focus = (datetime.now() - self.last_focus_change).total_seconds()
        if time_since_focus > self.focus_duration:
            self.current_focus_index = random.randint(0, len(self.people) - 1)
            self.focus_duration = random.uniform(3, 20)  # Next focus duration
            self.last_focus_change = datetime.now()

        # Get all window info
        windows = [person.get_window_info() for person in self.people]

        # Get active window handle
        active_hwnd = self.people[self.current_focus_index].hwnd

        return windows, active_hwnd

    def get_people_count(self) -> int:
        """Get the number of people in the simulation."""
        return len(self.people)

    def add_visitor(self):
        """Add a random visitor to the house."""
        # Find people not currently in the simulation
        current_names = {person.name for person in self.people}
        available = [p for p in PEOPLE if p["name"] not in current_names]

        if available:
            new_person_data = random.choice(available)
            new_person = SimulatedPerson(new_person_data)
            self.people.append(new_person)
            return new_person.name
        return None

    def remove_person(self):
        """Remove a random person from the house (they leave)."""
        if len(self.people) > 2:  # Keep at least 2 people
            person = random.choice(self.people)
            self.people.remove(person)
            # Adjust focus index if needed
            if self.current_focus_index >= len(self.people):
                self.current_focus_index = len(self.people) - 1
            return person.name
        return None
