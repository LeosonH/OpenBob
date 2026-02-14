"""Sprite sheet loader for character sprites."""
import pygame
import random
from pathlib import Path


class SpriteSheet:
    """Load and extract sprites from a sprite sheet."""

    def __init__(self, filepath, sprite_width=16, sprite_height=16, margin=0):
        """Initialize sprite sheet loader.

        Args:
            filepath: Path to sprite sheet image
            sprite_width: Width of each sprite in pixels
            sprite_height: Height of each sprite in pixels
            margin: Margin between sprites in pixels
        """
        self.sheet = pygame.image.load(filepath).convert_alpha()
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.margin = margin

        # Calculate grid dimensions accounting for margins
        sheet_width, sheet_height = self.sheet.get_size()
        self.columns = (sheet_width + margin) // (sprite_width + margin)
        self.rows = (sheet_height + margin) // (sprite_height + margin)

    def get_sprite(self, col, row, scale=1.0):
        """Extract a single sprite from the sheet.

        Args:
            col: Column index (0-based)
            row: Row index (0-based)
            scale: Scale factor (1.0 = original size)

        Returns:
            pygame.Surface with the sprite
        """
        # Account for margin between tiles
        x = col * (self.sprite_width + self.margin)
        y = row * (self.sprite_height + self.margin)

        sprite = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, self.sprite_width, self.sprite_height))

        if scale != 1.0:
            new_width = int(self.sprite_width * scale)
            new_height = int(self.sprite_height * scale)
            sprite = pygame.transform.scale(sprite, (new_width, new_height))

        return sprite

    def get_character_set(self, row, scale=1.0):
        """Get all sprites from a row (useful for character variations).

        Args:
            row: Row index (0-based)
            scale: Scale factor

        Returns:
            List of pygame.Surface sprites
        """
        return [self.get_sprite(col, row, scale) for col in range(self.columns)]


class CharacterSpriteManager:
    """Manage character sprites for personas."""

    def __init__(self, sprite_sheet_path, scale=3.0):
        """Initialize character sprite manager.

        Args:
            sprite_sheet_path: Path to Kenney roguelike sprite sheet
            scale: Scale factor for sprites (3.0 = 48x48 pixels)
        """
        self.sprite_sheet = SpriteSheet(
            sprite_sheet_path,
            sprite_width=16,
            sprite_height=16,
            margin=1  # Kenney sprites have 1px margin
        )
        self.scale = scale

        # Pre-load diverse character sprites and validate they're not blank
        self.character_pool = []
        rows_to_use = min(12, self.sprite_sheet.rows)  # Use up to 12 rows

        for row in range(rows_to_use):
            # Each row typically has the same character in different states
            # We'll use the first sprite (idle/standing) from each row
            sprite = self.sprite_sheet.get_sprite(0, row, scale)

            # Validate sprite is not blank (check if it has non-transparent pixels)
            if self._is_valid_sprite(sprite):
                self.character_pool.append({
                    'idle': sprite,
                    'row': row,
                })

        if not self.character_pool:
            raise ValueError("No valid character sprites found in sprite sheet")

        # Shuffle for variety
        random.shuffle(self.character_pool)
        self.next_character_index = 0

    def _is_valid_sprite(self, sprite):
        """Check if sprite has visible pixels.

        Args:
            sprite: pygame.Surface to validate

        Returns:
            bool: True if sprite has non-transparent pixels
        """
        # Check a few sample pixels to see if sprite has content
        w, h = sprite.get_size()
        sample_points = [
            (w // 2, h // 2),  # Center
            (w // 4, h // 2),  # Left-center
            (3 * w // 4, h // 2),  # Right-center
            (w // 2, h // 4),  # Top-center
            (w // 2, 3 * h // 4),  # Bottom-center
        ]

        for x, y in sample_points:
            if 0 <= x < w and 0 <= y < h:
                pixel = sprite.get_at((x, y))
                # Check if pixel has some alpha (not fully transparent)
                if pixel.a > 50:  # Threshold for "visible"
                    return True

        return False

    def get_next_character(self):
        """Get the next character sprite from the pool.

        Returns:
            Dict with 'idle' sprite and 'row' index
        """
        character = self.character_pool[self.next_character_index]
        self.next_character_index = (self.next_character_index + 1) % len(self.character_pool)
        return character

    def get_walking_frames(self, character_row, scale=None):
        """Get walking animation frames for a character.

        Args:
            character_row: Row index from sprite sheet
            scale: Optional scale override

        Returns:
            List of sprites for walking animation (just 2 frames for smooth animation)
        """
        if scale is None:
            scale = self.scale

        # Only use first 2 columns for walking animation to avoid jarring changes
        # Column 0: Idle/base pose
        # Column 1: Walking variation
        frames = []
        for col in range(min(2, self.sprite_sheet.columns)):
            sprite = self.sprite_sheet.get_sprite(col, character_row, scale)
            frames.append(sprite)

        # If we only got 1 frame, duplicate it for smooth animation
        if len(frames) == 1:
            frames.append(frames[0])

        return frames
