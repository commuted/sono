#!/usr/bin/env python3
"""
Chord Progression Demo

This example demonstrates how to use the sono library to create a chord
progression and write it out to a WAV file using Python's built-in wave module.

The progression is I-V-vi-IV in C major (C - G - Am - F), a classic pop
chord progression used in countless songs.

Usage:
    python chord_progression.py [output_file]

    output_file: Optional path for the output WAV file (default: progression.wav)
"""

import sys
import wave
import struct

# Add parent directory to path for imports when running from examples/
sys.path.insert(0, '..')
import sono as sl


def create_chord_progression():
    """Create a I-V-vi-IV chord progression in C major."""

    # Define the chord progression: C - G - Am - F
    # Each tuple is (octave, root_note, chord_type)
    progression = [
        (4, "C", "major"),   # I   - C major
        (4, "G", "major"),   # V   - G major
        (4, "A", "minor"),   # vi  - A minor
        (4, "F", "major"),   # IV  - F major
    ]

    # Create Chord objects for each chord in the progression
    chords = []
    for chord_spec in progression:
        chord = sl.Chord()
        chord = chord.make_a_chord(chord_spec, pluck=True)
        # Fix pop by spreading phases and adjusting for zero start
        sl.Util.fix_pop(chord)
        chords.append(chord)

    return chords


def generate_samples(chords, sample_rate=44100, chord_duration_sec=1.0):
    """Generate audio samples for the chord progression.

    Args:
        chords: List of Chord objects to play
        sample_rate: Audio sample rate in Hz
        chord_duration_sec: Duration of each chord in seconds

    Returns:
        List of float samples normalized to [-1.0, 1.0]
    """
    samples_per_chord = int(sample_rate * chord_duration_sec)
    all_samples = []

    for chord in chords:
        # Activate the chord (triggers the pluck)
        chord.set_on()

        # Generate samples for this chord
        for _ in range(samples_per_chord):
            sample = chord.sample()
            all_samples.append(sample)

        # Deactivate chord
        chord.set_off()

    return all_samples


def normalize_samples(samples):
    """Normalize samples to use full dynamic range.

    Args:
        samples: List of float samples

    Returns:
        List of normalized float samples in range [-1.0, 1.0]
    """
    if not samples:
        return samples

    max_val = max(abs(s) for s in samples)
    if max_val == 0:
        return samples

    # Leave some headroom (normalize to 90% of max)
    scale = 0.9 / max_val
    return [s * scale for s in samples]


def write_wav(filename, samples, sample_rate=44100, bits_per_sample=16):
    """Write samples to a WAV file.

    Args:
        filename: Output WAV file path
        samples: List of float samples in range [-1.0, 1.0]
        sample_rate: Audio sample rate in Hz
        bits_per_sample: Bit depth (16 or 24)
    """
    n_channels = 1  # Mono

    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(bits_per_sample // 8)
        wav_file.setframerate(sample_rate)

        # Convert float samples to integers
        if bits_per_sample == 16:
            max_int = 32767
            packed_samples = b''.join(
                struct.pack('<h', int(s * max_int))
                for s in samples
            )
        elif bits_per_sample == 24:
            max_int = 8388607
            packed_samples = b''.join(
                struct.pack('<i', int(s * max_int))[:3]
                for s in samples
            )
        else:
            raise ValueError(f"Unsupported bit depth: {bits_per_sample}")

        wav_file.writeframes(packed_samples)


def main():
    # Configuration
    sample_rate = 44100
    chord_duration = 1.5  # seconds per chord
    output_file = sys.argv[1] if len(sys.argv) > 1 else "progression.wav"

    print("Chord Progression Demo")
    print("=" * 40)
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Chord duration: {chord_duration} seconds")
    print(f"Output file: {output_file}")
    print()

    # Create the chord progression
    print("Creating chord progression (C - G - Am - F)...")
    chords = create_chord_progression()

    # Generate audio samples
    print("Generating audio samples...")
    samples = generate_samples(chords, sample_rate, chord_duration)
    print(f"  Generated {len(samples)} samples ({len(samples)/sample_rate:.1f} seconds)")

    # Normalize
    print("Normalizing audio...")
    samples = normalize_samples(samples)

    # Write WAV file
    print(f"Writing WAV file: {output_file}")
    write_wav(output_file, samples, sample_rate)

    print()
    print(f"Done! Play the file with: aplay {output_file}")
    print("Or open it in any audio player.")


if __name__ == "__main__":
    main()
