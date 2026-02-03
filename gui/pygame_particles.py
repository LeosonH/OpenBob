"""Particle system for visual effects."""
import pygame
import random
import math


class Particle:
    """A single particle."""

    def __init__(self, pos, velocity, color, lifetime, size=3, fade=True):
        """Initialize particle.

        Args:
            pos: Starting position (x, y)
            velocity: Velocity vector (vx, vy)
            color: RGB color tuple
            lifetime: Lifetime in seconds
            size: Particle size
            fade: Whether to fade out
        """
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.fade = fade

    def update(self, dt):
        """Update particle.

        Args:
            dt: Delta time in seconds
        """
        # Move
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        # Gravity (for some particle types)
        self.velocity[1] += 200 * dt  # Gravity

        # Age
        self.lifetime -= dt

    def is_dead(self):
        """Check if particle is dead."""
        return self.lifetime <= 0

    def draw(self, screen):
        """Draw particle to screen.

        Args:
            screen: Pygame surface
        """
        if self.is_dead():
            return

        # Calculate alpha based on lifetime if fading
        alpha = 255
        if self.fade:
            alpha = int(255 * (self.lifetime / self.max_lifetime))

        # Draw directly to screen (more efficient than creating surface)
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(screen, color_with_alpha, (int(self.pos[0]), int(self.pos[1])), size)


class ParticleSystem:
    """Manages particle effects."""

    def __init__(self):
        """Initialize particle system."""
        self.particles = []

    def emit_sparkles(self, pos, count=20):
        """Emit sparkle particles (for entry).

        Args:
            pos: Center position (x, y)
            count: Number of particles
        """
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(50, 150)
            velocity = (
                math.cos(angle) * speed,
                math.sin(angle) * speed - 100  # Upward bias
            )
            color = random.choice([
                (255, 215, 0),   # Gold
                (255, 255, 255), # White
                (255, 182, 193), # Pink
                (135, 206, 250), # Sky blue
            ])
            particle = Particle(
                pos=pos,
                velocity=velocity,
                color=color,
                lifetime=random.uniform(0.5, 1.0),
                size=random.randint(2, 4),
                fade=True
            )
            self.particles.append(particle)

    def emit_dust(self, pos):
        """Emit dust puff (for walking).

        Args:
            pos: Position (x, y)
        """
        for _ in range(2):  # Reduced from 3 to 2 particles
            velocity = (
                random.uniform(-15, 15),  # Reduced velocity
                random.uniform(-5, 5)
            )
            particle = Particle(
                pos=pos,
                velocity=velocity,
                color=(220, 220, 220),  # Lighter gray for more subtlety
                lifetime=random.uniform(0.15, 0.25),  # Shorter lifetime
                size=random.randint(2, 3),  # Smaller size (was 3-6)
                fade=True
            )
            self.particles.append(particle)

    def emit_exit_poof(self, pos, count=15):
        """Emit poof effect (for exit).

        Args:
            pos: Center position (x, y)
            count: Number of particles
        """
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(30, 80)
            velocity = (
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            particle = Particle(
                pos=pos,
                velocity=velocity,
                color=(180, 180, 180),
                lifetime=random.uniform(0.3, 0.6),
                size=random.randint(2, 5),
                fade=True
            )
            self.particles.append(particle)

    def emit_active_glow(self, pos):
        """Emit subtle glow particles (for active window).

        Args:
            pos: Position above character (x, y)
        """
        angle = random.random() * math.pi * 2
        distance = random.uniform(10, 20)
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance

        particle = Particle(
            pos=(pos[0] + offset_x, pos[1] + offset_y),
            velocity=(0, -20),  # Float upward
            color=(255, 215, 0),  # Gold
            lifetime=random.uniform(0.3, 0.5),
            size=2,
            fade=True
        )
        self.particles.append(particle)

    def update(self, dt):
        """Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Filter alive particles instead of removing dead ones (O(n) instead of O(n²))
        alive_particles = []
        for particle in self.particles:
            particle.update(dt)
            if not particle.is_dead():
                alive_particles.append(particle)
        self.particles = alive_particles

    def draw(self, screen):
        """Draw all particles.

        Args:
            screen: Pygame surface
        """
        for particle in self.particles:
            particle.draw(screen)

    def clear(self):
        """Clear all particles."""
        self.particles.clear()
