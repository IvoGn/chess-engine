"""Sound effects for chess engine."""

import sys
import numpy as np
import pygame


class SoundEffects:
    """Manage sound effects for the chess game."""

    def __init__(self):
        """Initialize sound effects."""
        pygame.mixer.init()
        self.move_sound = self._generate_move_sound()
        self.check_sound = self._generate_check_sound()
        self.capture_sound = self._generate_capture_sound()

    def _apply_envelope(self, wave, attack=0.01, decay=0.05, sustain=0.6, release=0.08):
        """Apply ADSR envelope to soften the sound."""
        total_samples = len(wave)
        sample_rate = 22050

        attack_samples = int(attack * sample_rate)
        decay_samples = int(decay * sample_rate)
        sustain_samples = int(sustain * sample_rate)
        release_samples = int(release * sample_rate)

        envelope = np.ones(total_samples)

        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        if decay_end <= total_samples:
            envelope[decay_start:decay_end] = np.linspace(1, sustain, decay_samples)

        # Release
        release_start = max(decay_end, total_samples - release_samples)
        if release_start < total_samples:
            release_length = total_samples - release_start
            envelope[release_start:] = np.linspace(sustain, 0, release_length)

        return (wave * envelope).astype(np.int16)

    def _generate_move_sound(self):
        """Generate a pleasant beep for normal moves."""
        sample_rate = 22050
        duration = 0.15
        frequency = 523  # C5 note

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        wave = (wave * 32767).astype(np.int16)

        wave = self._apply_envelope(wave, attack=0.01, decay=0.05, sustain=0.7, release=0.05)
        stereo_wave = np.array([wave, wave], dtype=np.int16).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def _generate_capture_sound(self):
        """Generate a different pleasant sound for captures."""
        sample_rate = 22050
        duration = 0.2
        frequency = 659  # E5 note

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * frequency * t)
        wave = (wave * 32767).astype(np.int16)

        wave = self._apply_envelope(wave, attack=0.01, decay=0.08, sustain=0.6, release=0.06)
        stereo_wave = np.array([wave, wave], dtype=np.int16).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def _generate_check_sound(self):
        """Generate a warning alert for check."""
        sample_rate = 22050
        duration = 0.3

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a slightly ascending tone
        freq_start = 800
        freq_end = 1000
        frequency = np.linspace(freq_start, freq_end, len(t))
        wave = np.sin(2 * np.pi * frequency * t)
        wave = (wave * 32767).astype(np.int16)

        wave = self._apply_envelope(wave, attack=0.02, decay=0.1, sustain=0.7, release=0.08)
        stereo_wave = np.array([wave, wave], dtype=np.int16).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound

    def play_move(self, is_capture=False):
        """Play sound for a move."""
        try:
            if is_capture:
                self.capture_sound.play()
            else:
                self.move_sound.play()
        except:
            pass  # Silently fail if sound system has issues

    def play_check(self):
        """Play sound for check."""
        try:
            self.check_sound.play()
        except:
            pass
