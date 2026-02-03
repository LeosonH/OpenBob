"""Pygame sprite classes for the house view."""
import pygame
import random
import math


class Persona(pygame.sprite.Sprite):
    """A persona sprite representing an app/window."""

    def __init__(self, emoji, name, pos, speech_text=None):
        """Initialize persona sprite.

        Args:
            emoji: Emoji character to display
            name: Persona name
            pos: Starting position (x, y)
            speech_text: Optional speech bubble text
        """
        super().__init__()
        self.emoji = emoji
        self.name = name
        self.pos = list(pos)
        self.target_pos = list(pos)

        # Animation state
        self.bob_time = random.random() * math.pi * 2  # Random start phase
        self.scale_pulse = 0
        self.is_moving = False
        self.walk_frame = 0
        self.walk_speed = 0
        self.last_step_time = 0

        # Direction for walking animation
        self.facing_right = True

        # Speech bubble
        self.speech_text = speech_text
        self.speech_bubble = None

        # Movement animation
        self.move_progress = 1.0  # 0.0 to 1.0
        self.start_pos = list(pos)

        # Active glow effect
        self.is_active = False
        self.glow_time = 0
        self.glow_emission_timer = 0  # Timer for controlled glow particle emission
        self.glow_emission_interval = 0.2  # Emit every 0.2 seconds (~5 particles/sec)

        # Font caching for performance
        self._emoji_font_cache = {}  # Cache emoji fonts by size
        self._name_surface_cache = None  # Cache rendered name (doesn't change)

        self.render()

    def render(self):
        """Render the sprite."""
        # Create surface with transparency
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)

        # Active glow effect
        if self.is_active:
            glow_radius = 45 + int(math.sin(self.glow_time) * 5)
            glow_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            for i in range(3):
                alpha = 30 - i * 10
                radius = glow_radius + i * 5
                pygame.draw.circle(glow_surf, (255, 215, 0, alpha), (50, 40), radius)
            self.image.blit(glow_surf, (0, 0))

        # Bob animation offset (more pronounced when walking)
        if self.is_moving and self.walk_speed > 0.5:
            bob_offset = math.sin(self.walk_frame * 4) * 5
        else:
            bob_offset = math.sin(self.bob_time) * 2

        # Draw shadow (ellipse at bottom)
        shadow_alpha = max(0, 100 - int(abs(bob_offset) * 10))
        shadow_surf = pygame.Surface((60, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect())
        self.image.blit(shadow_surf, (20, 75))

        # Draw emoji (with walking tilt)
        scale = 1.0 + math.sin(self.scale_pulse) * 0.05
        font_size = int(48 * scale)

        # Use cached font or create new one
        if font_size not in self._emoji_font_cache:
            try:
                self._emoji_font_cache[font_size] = pygame.font.SysFont('segoeuiemoji,applesymbolsbook,notocoloremoji', font_size)
            except:
                self._emoji_font_cache[font_size] = pygame.font.Font(None, font_size)

        font = self._emoji_font_cache[font_size]
        emoji_surf = font.render(self.emoji, True, (0, 0, 0))

        # Flip if facing left
        if not self.facing_right and self.is_moving:
            emoji_surf = pygame.transform.flip(emoji_surf, True, False)

        # Apply walking tilt
        if self.is_moving and self.walk_speed > 0.5:
            tilt = math.sin(self.walk_frame * 4) * 5
            emoji_surf = pygame.transform.rotate(emoji_surf, tilt)

        emoji_rect = emoji_surf.get_rect(center=(50, 35 + bob_offset))
        self.image.blit(emoji_surf, emoji_rect)

        # Draw name (cached since it never changes)
        if self._name_surface_cache is None:
            font_name = pygame.font.Font(None, 16)
            self._name_surface_cache = font_name.render(self.name, True, (50, 50, 50))
        name_surf = self._name_surface_cache
        name_rect = name_surf.get_rect(center=(50, 65))
        self.image.blit(name_surf, name_rect)

        self.rect = self.image.get_rect(center=self.pos)

    def set_target(self, target_pos):
        """Set movement target with animation.

        Args:
            target_pos: Target position (x, y)
        """
        self.target_pos = list(target_pos)
        self.start_pos = list(self.pos)
        self.move_progress = 0.0
        self.is_moving = True

    def set_speech(self, text):
        """Set speech bubble text.

        Args:
            text: Speech text or None to remove
        """
        self.speech_text = text
        if text and not self.speech_bubble:
            self.speech_bubble = SpeechBubble(text, self.pos)
        elif not text and self.speech_bubble:
            self.speech_bubble.kill()
            self.speech_bubble = None
        elif text and self.speech_bubble:
            self.speech_bubble.set_text(text)

    def update(self, dt, emit_dust_callback=None):
        """Update sprite animation.

        Args:
            dt: Delta time in seconds
            emit_dust_callback: Optional callback to emit dust particles

        Returns:
            bool: True if active glow particle should be emitted this frame
        """
        # Bob animation
        self.bob_time += dt * 3

        # Scale pulse (subtle breathing effect)
        self.scale_pulse += dt * 2

        # Glow animation and emission timer for active personas
        should_emit_glow = False
        if self.is_active:
            self.glow_time += dt * 4
            self.glow_emission_timer += dt
            if self.glow_emission_timer >= self.glow_emission_interval:
                should_emit_glow = True
                self.glow_emission_timer = 0

        # Movement animation with easing
        if self.is_moving:
            old_pos = list(self.pos)

            self.move_progress += dt * 0.3  # Much slower walking speed
            if self.move_progress >= 1.0:
                self.move_progress = 1.0
                self.is_moving = False
                self.walk_speed = 0

            # Ease in-out
            t = self.move_progress
            eased_t = t * t * (3.0 - 2.0 * t)

            # Interpolate position
            self.pos[0] = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * eased_t
            self.pos[1] = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * eased_t

            # Calculate walk speed and direction
            dx = self.pos[0] - old_pos[0]
            dy = self.pos[1] - old_pos[1]
            self.walk_speed = (dx * dx + dy * dy) ** 0.5

            # Update facing direction
            if abs(dx) > 0.1:
                self.facing_right = dx > 0

            # Walk animation
            if self.walk_speed > 0.5:
                self.walk_frame += dt * 8

                # Emit dust particles occasionally while walking (much less frequent)
                if emit_dust_callback and int(self.walk_frame * 0.3) != int(self.last_step_time * 0.3):
                    emit_dust_callback((self.pos[0], self.pos[1] + 30))
                    self.last_step_time = self.walk_frame

        # Update speech bubble position
        if self.speech_bubble:
            self.speech_bubble.update_position((self.pos[0], self.pos[1] - 50))

        self.render()
        return should_emit_glow


class SpeechBubble(pygame.sprite.Sprite):
    """A speech bubble for personas."""

    def __init__(self, text, pos):
        """Initialize speech bubble.

        Args:
            text: Text to display
            pos: Position (x, y) above persona
        """
        super().__init__()
        self.text = text
        self.pos = list(pos)
        self.render()

    def set_text(self, text):
        """Change bubble text.

        Args:
            text: New text
        """
        self.text = text
        self.render()

    def update_position(self, pos):
        """Update bubble position.

        Args:
            pos: New position (x, y)
        """
        self.pos = list(pos)
        self.rect.center = self.pos

    def render(self):
        """Render the speech bubble."""
        # Create text surface
        font = pygame.font.Font(None, 20)
        text_surf = font.render(self.text, True, (0, 0, 0))

        # Calculate bubble size
        padding = 15
        width = min(200, text_surf.get_width() + padding * 2)
        height = 45

        # Create bubble surface with alpha
        self.image = pygame.Surface((width, height + 15), pygame.SRCALPHA)

        # Draw shadow
        shadow_rect = pygame.Rect(3, 3, width, height)
        pygame.draw.ellipse(self.image, (0, 0, 0, 80), shadow_rect)

        # Draw white bubble
        bubble_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.ellipse(self.image, (255, 255, 255, 255), bubble_rect)
        pygame.draw.ellipse(self.image, (100, 100, 100, 255), bubble_rect, 2)

        # Draw pointer (triangle)
        pointer = [
            (width // 2 - 8, height),
            (width // 2 + 8, height),
            (width // 2, height + 12)
        ]
        pygame.draw.polygon(self.image, (255, 255, 255, 255), pointer)
        pygame.draw.lines(self.image, (100, 100, 100, 255), False,
                         [pointer[0], pointer[2], pointer[1]], 2)

        # Draw text (wrap if needed)
        words = self.text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = font.render(test_line, True, (0, 0, 0))
            if test_surf.get_width() <= width - padding * 2:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Blit text lines
        y_offset = (height - len(lines) * 20) // 2
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, (0, 0, 0))
            line_rect = line_surf.get_rect(center=(width // 2, y_offset + i * 20 + 10))
            self.image.blit(line_surf, line_rect)

        self.rect = self.image.get_rect(center=self.pos)


class Door(pygame.sprite.Sprite):
    """An animated door sprite."""

    def __init__(self, pos):
        """Initialize door.

        Args:
            pos: Position (x, y) of door top-left
        """
        super().__init__()
        self.pos = pos
        self.width = 40
        self.height = 80

        self.is_open = False
        self.open_progress = 0.0  # 0.0 = closed, 1.0 = open
        self.target_progress = 0.0

        self.render()

    def open(self):
        """Start opening animation."""
        self.target_progress = 1.0

    def close(self):
        """Start closing animation."""
        self.target_progress = 0.0

    def render(self):
        """Render the door."""
        self.image = pygame.Surface((self.width + 50, self.height + 10), pygame.SRCALPHA)

        x_base = 5
        y_base = 5

        # Draw door frame
        frame_rect = pygame.Rect(x_base - 5, y_base - 5,
                                self.width + 10, self.height + 10)
        pygame.draw.rect(self.image, (101, 67, 33), frame_rect, 3)

        if self.open_progress < 0.1:
            # Door closed
            door_rect = pygame.Rect(x_base, y_base, self.width, self.height)
            pygame.draw.rect(self.image, (139, 90, 43), door_rect)
            pygame.draw.rect(self.image, (101, 67, 33), door_rect, 2)

            # Door panels
            panel1 = pygame.Rect(x_base + 5, y_base + 10,
                               self.width - 10, self.height // 2 - 15)
            panel2 = pygame.Rect(x_base + 5, y_base + self.height // 2 + 5,
                               self.width - 10, self.height // 2 - 15)
            pygame.draw.rect(self.image, (101, 67, 33), panel1, 2)
            pygame.draw.rect(self.image, (101, 67, 33), panel2, 2)

            # Door knob
            knob_pos = (x_base + self.width - 8, y_base + self.height // 2)
            pygame.draw.circle(self.image, (255, 215, 0), knob_pos, 4)
        else:
            # Door opening/open
            # Show dark interior
            interior_rect = pygame.Rect(x_base, y_base, self.width, self.height)
            pygame.draw.rect(self.image, (30, 30, 30), interior_rect)

            # Door panel sliding to the side
            door_offset = int(self.open_progress * 35)
            door_rect = pygame.Rect(x_base - door_offset, y_base,
                                   self.width, self.height)
            pygame.draw.rect(self.image, (139, 90, 43), door_rect)
            pygame.draw.rect(self.image, (101, 67, 33), door_rect, 2)

            # Knob on open door
            knob_pos = (x_base - door_offset + 5, y_base + self.height // 2)
            pygame.draw.circle(self.image, (255, 215, 0), knob_pos, 4)

        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, dt):
        """Update door animation.

        Args:
            dt: Delta time in seconds
        """
        # Animate toward target
        if abs(self.open_progress - self.target_progress) > 0.01:
            direction = 1 if self.target_progress > self.open_progress else -1
            self.open_progress += direction * dt * 3  # Speed
            self.open_progress = max(0.0, min(1.0, self.open_progress))
            self.render()

        self.is_open = self.open_progress > 0.5
