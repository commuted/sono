# tests/fixtures/__init__.py
# Test fixture generation for audio tests

import os
import wave
import struct
import numpy as np
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def _ensure_fixtures():
    """Ensure all test fixtures exist, generating them if needed."""
    fixtures = [
        ("sine_440hz_16bit.wav", _generate_sine_440hz_16bit),
        ("sine_440hz_8bit.wav", _generate_sine_440hz_8bit),
        ("chord_major_16bit.wav", _generate_chord_major_16bit),
        ("silence_16bit.wav", _generate_silence_16bit),
        ("stereo_16bit.wav", _generate_stereo_16bit),
        ("complex_tone_16bit.wav", _generate_complex_tone_16bit),
        ("short_click_16bit.wav", _generate_short_click_16bit),
    ]

    for filename, generator in fixtures:
        filepath = FIXTURES_DIR / filename
        if not filepath.exists():
            generator(filepath)


def _generate_sine_440hz_16bit(filepath: Path):
    """Generate a 440 Hz sine wave, 16-bit, 44100 Hz, 1 second."""
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0
    amplitude = 0.8

    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    samples = (amplitude * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    _write_wav(filepath, samples, sample_rate, 1, 2)


def _generate_sine_440hz_8bit(filepath: Path):
    """Generate a 440 Hz sine wave, 8-bit, 44100 Hz, 1 second."""
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0
    amplitude = 0.8

    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    # 8-bit is unsigned, centered at 128
    samples = ((amplitude * np.sin(2 * np.pi * frequency * t) + 1) * 127.5).astype(np.uint8)

    _write_wav(filepath, samples, sample_rate, 1, 1)


def _generate_chord_major_16bit(filepath: Path):
    """Generate a C major chord (C4, E4, G4), 16-bit, 44100 Hz, 1 second."""
    sample_rate = 44100
    duration = 1.0
    frequencies = [261.63, 329.63, 392.00]  # C4, E4, G4
    amplitude = 0.5

    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    samples = np.zeros(n_samples)
    for freq in frequencies:
        samples += amplitude * np.sin(2 * np.pi * freq * t)

    # Normalize and convert
    samples = (samples / len(frequencies) * 32767).astype(np.int16)

    _write_wav(filepath, samples, sample_rate, 1, 2)


def _generate_silence_16bit(filepath: Path):
    """Generate 1 second of silence, 16-bit, 44100 Hz."""
    sample_rate = 44100
    duration = 1.0
    n_samples = int(sample_rate * duration)

    samples = np.zeros(n_samples, dtype=np.int16)
    _write_wav(filepath, samples, sample_rate, 1, 2)


def _generate_stereo_16bit(filepath: Path):
    """Generate stereo audio with different tones in each channel."""
    sample_rate = 44100
    duration = 1.0
    amplitude = 0.8

    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Left channel: 440 Hz, Right channel: 550 Hz
    left = (amplitude * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    right = (amplitude * np.sin(2 * np.pi * 550 * t) * 32767).astype(np.int16)

    # Interleave channels
    stereo = np.empty(n_samples * 2, dtype=np.int16)
    stereo[0::2] = left
    stereo[1::2] = right

    _write_wav(filepath, stereo, sample_rate, 2, 2)


def _generate_complex_tone_16bit(filepath: Path):
    """Generate a complex tone with multiple harmonics."""
    sample_rate = 44100
    duration = 1.0
    fundamental = 220.0  # A3

    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Fundamental + harmonics with decreasing amplitude
    samples = np.zeros(n_samples)
    for harmonic in range(1, 9):
        amplitude = 1.0 / harmonic
        samples += amplitude * np.sin(2 * np.pi * fundamental * harmonic * t)

    # Normalize
    samples = samples / np.max(np.abs(samples)) * 0.8
    samples = (samples * 32767).astype(np.int16)

    _write_wav(filepath, samples, sample_rate, 1, 2)


def _generate_short_click_16bit(filepath: Path):
    """Generate a very short click/impulse for edge case testing."""
    sample_rate = 44100

    # Just 100 samples
    samples = np.zeros(100, dtype=np.int16)
    samples[50] = 32767  # Single impulse

    _write_wav(filepath, samples, sample_rate, 1, 2)


def _write_wav(filepath: Path, samples: np.ndarray, sample_rate: int,
               n_channels: int, sample_width: int):
    """Write samples to a WAV file."""
    with wave.open(str(filepath), 'wb') as wav:
        wav.setnchannels(n_channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(sample_rate)

        if sample_width == 1:
            wav.writeframes(samples.astype(np.uint8).tobytes())
        elif sample_width == 2:
            wav.writeframes(samples.astype(np.int16).tobytes())
        else:
            wav.writeframes(samples.tobytes())


def get_fixture_path(name: str) -> Path:
    """Get path to a fixture file, ensuring it exists."""
    _ensure_fixtures()
    return FIXTURES_DIR / name


def get_sine_440hz_16bit() -> Path:
    """Get path to 440 Hz sine wave fixture."""
    return get_fixture_path("sine_440hz_16bit.wav")


def get_sine_440hz_8bit() -> Path:
    """Get path to 8-bit 440 Hz sine wave fixture."""
    return get_fixture_path("sine_440hz_8bit.wav")


def get_chord_major_16bit() -> Path:
    """Get path to C major chord fixture."""
    return get_fixture_path("chord_major_16bit.wav")


def get_silence_16bit() -> Path:
    """Get path to silence fixture."""
    return get_fixture_path("silence_16bit.wav")


def get_stereo_16bit() -> Path:
    """Get path to stereo fixture."""
    return get_fixture_path("stereo_16bit.wav")


def get_complex_tone_16bit() -> Path:
    """Get path to complex tone fixture."""
    return get_fixture_path("complex_tone_16bit.wav")


def get_short_click_16bit() -> Path:
    """Get path to short click fixture."""
    return get_fixture_path("short_click_16bit.wav")


# Generate fixtures on module import
_ensure_fixtures()
