import array
import math

import pygame


def _tone(freq_start, freq_end, duration, volume, rate, channels):
    """Build raw 16-bit PCM for a sine sweep with a fade-out (no audio files needed)."""
    n = int(rate * duration)
    samples = array.array("h")
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = freq_start + (freq_end - freq_start) * t
        phase += 2 * math.pi * freq / rate
        envelope = (1.0 - t) ** 1.5
        value = int(32767 * volume * envelope * math.sin(phase))
        for _ in range(channels):
            samples.append(value)
    return samples


class SoundManager:
    """Generates and plays the game's sound effects.

    Falls back to silence if no audio device is available, so the
    game never crashes on machines without sound.
    """

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            rate, fmt, channels = pygame.mixer.get_init()
            if fmt != -16:
                return  # unexpected sample format; stay silent
            self.sounds["whack"] = self._make(_tone(500, 1100, 0.12, 0.6, rate, channels))
            self.sounds["miss"] = self._make(_tone(180, 90, 0.18, 0.6, rate, channels))
            gameover = (
                _tone(660, 660, 0.15, 0.5, rate, channels)
                + _tone(520, 520, 0.15, 0.5, rate, channels)
                + _tone(400, 300, 0.35, 0.5, rate, channels)
            )
            self.sounds["gameover"] = self._make(gameover)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    @staticmethod
    def _make(samples):
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
