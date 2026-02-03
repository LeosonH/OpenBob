"""Sound manager for audio effects."""
import pygame
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SoundManager:
    """Manages sound effects."""

    def __init__(self, enabled=True):
        """Initialize sound manager.

        Args:
            enabled: Whether sounds are enabled
        """
        self.enabled = enabled
        self.sounds = {}

        if not enabled:
            logger.info("Sound disabled")
            return

        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._generate_sounds()
            logger.info("Sound system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sound: {e}")
            self.enabled = False

    def _generate_sounds(self):
        """Generate procedural sound effects."""
        try:
            # Door creak (descending tone with noise)
            self.sounds['door_open'] = self._generate_creak()

            # Door close (thump)
            self.sounds['door_close'] = self._generate_thump()

            # Footstep (short click)
            self.sounds['footstep'] = self._generate_footstep()

            # Hello (ascending chime)
            self.sounds['hello'] = self._generate_chime(ascending=True)

            # Goodbye (descending chime)
            self.sounds['goodbye'] = self._generate_chime(ascending=False)

            # Ambient (very quiet white noise)
            self.sounds['ambient'] = self._generate_ambient()

            logger.info("Generated procedural sounds")
        except Exception as e:
            logger.error(f"Failed to generate sounds: {e}")

    def _generate_creak(self):
        """Generate door creak sound."""
        sample_rate = 22050
        duration = 0.3
        samples = int(sample_rate * duration)

        # Generate descending frequency with noise
        t = np.linspace(0, duration, samples)
        freq_start = 400
        freq_end = 200
        frequency = np.linspace(freq_start, freq_end, samples)

        # Sine wave with envelope
        wave = np.sin(2 * np.pi * frequency * t)
        envelope = np.exp(-3 * t)
        wave *= envelope

        # Add noise
        noise = np.random.uniform(-0.1, 0.1, samples)
        wave += noise

        # Convert to int16
        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)

        # Stereo
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    def _generate_thump(self):
        """Generate door close thump sound."""
        sample_rate = 22050
        duration = 0.15
        samples = int(sample_rate * duration)

        # Low frequency pulse
        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * 100 * t)
        envelope = np.exp(-10 * t)
        wave *= envelope

        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    def _generate_footstep(self):
        """Generate footstep sound."""
        sample_rate = 22050
        duration = 0.05
        samples = int(sample_rate * duration)

        # Short noise burst
        wave = np.random.uniform(-0.5, 0.5, samples)
        t = np.linspace(0, duration, samples)
        envelope = np.exp(-20 * t)
        wave *= envelope

        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    def _generate_chime(self, ascending=True):
        """Generate chime sound.

        Args:
            ascending: True for ascending, False for descending
        """
        sample_rate = 22050
        duration = 0.4
        samples = int(sample_rate * duration)

        t = np.linspace(0, duration, samples)

        # Multiple frequencies for harmony
        if ascending:
            freqs = [440, 554, 659]  # A, C#, E (major chord)
        else:
            freqs = [659, 554, 440]

        wave = np.zeros(samples)
        for i, freq in enumerate(freqs):
            start = int(samples * i / len(freqs))
            segment_t = t[start:]
            tone = np.sin(2 * np.pi * freq * segment_t[:len(wave) - start])
            envelope = np.exp(-5 * segment_t[:len(wave) - start])
            wave[start:] += tone * envelope * 0.3

        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    def _generate_ambient(self):
        """Generate ambient background sound."""
        sample_rate = 22050
        duration = 2.0  # Loop this
        samples = int(sample_rate * duration)

        # Very quiet pink noise
        wave = np.random.uniform(-0.05, 0.05, samples)

        wave = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo)

    def play(self, sound_name, volume=0.3):
        """Play a sound effect.

        Args:
            sound_name: Name of sound to play
            volume: Volume (0.0 to 1.0)
        """
        if not self.enabled or sound_name not in self.sounds:
            return

        try:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            logger.error(f"Failed to play sound {sound_name}: {e}")

    def play_ambient(self, volume=0.1):
        """Start playing ambient sound in loop.

        Args:
            volume: Volume (0.0 to 1.0)
        """
        if not self.enabled or 'ambient' not in self.sounds:
            return

        try:
            sound = self.sounds['ambient']
            sound.set_volume(volume)
            sound.play(loops=-1, fade_ms=1000)
        except Exception as e:
            logger.error(f"Failed to play ambient: {e}")

    def stop_ambient(self):
        """Stop ambient sound."""
        if not self.enabled or 'ambient' not in self.sounds:
            return

        try:
            self.sounds['ambient'].fadeout(1000)
        except Exception as e:
            logger.error(f"Failed to stop ambient: {e}")

    def toggle_mute(self):
        """Toggle sound on/off.

        Returns:
            bool: New enabled state
        """
        if 'ambient' in self.sounds:
            if self.enabled:
                self.stop_ambient()
            else:
                self.play_ambient(volume=0.05)

        self.enabled = not self.enabled
        logger.info(f"Sound {'enabled' if self.enabled else 'muted'}")
        return self.enabled
