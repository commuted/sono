#!/usr/bin/env python3
"""
Example: Convert a WAV file to a Chord using psychoacoustic analysis.

This demonstrates:
1. Loading a WAV file and extracting perceptually significant frequencies
2. Creating a Chord with SoundElements for each frequency component
3. Applying Pluck envelope for natural decay
4. Using min_derivative() to optimize phases
5. Generating and comparing audio output
"""

import numpy as np
from sono.util import Util


def main():
    # Path to WAV file (adjust as needed)
    wav_path = "tests/fixtures/piano_3_Bf_d_m_74.wav"

    # Read original WAV for comparison
    audio_orig, sample_rate, n_channels = Util._read_wav_file(wav_path)
    print("=== ORIGINAL WAV FILE ===")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Channels: {n_channels}")
    print(f"Duration: {len(audio_orig)/sample_rate:.2f} sec")
    print(f"Peak amplitude: {np.max(np.abs(audio_orig)):.4f}")

    # Convert WAV to Chord
    # - num_waves: number of frequency components to extract
    # - pluck: wrap with Pluck envelope for decay
    chord, metadata = Util.wav_to_chord(
        wav_path,
        num_waves=15,
        pluck=True,
        name="piano_chord"
    )

    print(f"\n=== DETECTED COMPONENTS ({metadata['num_components']}) ===")
    # Sort by amplitude (strongest first)
    components = sorted(metadata['components'], key=lambda x: -x['amplitude'])
    for i, c in enumerate(components[:5]):
        print(f"  {i+1}. {c['frequency']:7.2f} Hz, amplitude={c['amplitude']:.4f}")
    if len(components) > 5:
        print(f"  ... and {len(components)-5} more")

    # Configure the Pluck envelope
    # lambda_dc controls decay rate: higher = faster decay
    # Default is 0.03 (decays to 1/e in ~33 sec)
    # Setting to 5.0 gives decay to 1/e in 0.2 sec (200ms)
    chord.msg({'piano_chord_pluck': {'set_lambda_dc': [5.0]}})

    # Apply min_derivative() to optimize phases
    # This minimizes derivative energy to reduce pops/clicks at chord start
    print("\n=== APPLYING min_derivative() ===")
    Util.min_derivative(chord)

    # Generate audio samples
    duration_sec = 3.0
    n_samples = int(sample_rate * duration_sec)

    chord.set_on()
    samples = np.array([chord.sample() for _ in range(n_samples)])

    print(f"\n=== GENERATED AUDIO ({duration_sec} sec) ===")
    print(f"Peak amplitude: {np.max(np.abs(samples)):.4f}")
    print(f"RMS amplitude: {np.sqrt(np.mean(samples**2)):.4f}")

    # Analyze frequencies in generated audio
    fft_result = np.fft.rfft(samples)
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)
    magnitudes = np.abs(fft_result)

    # Find dominant frequencies
    top_indices = np.argsort(magnitudes)[-5:][::-1]
    print("\nTop frequencies in generated audio:")
    for idx in top_indices:
        print(f"  {freqs[idx]:7.2f} Hz (magnitude: {magnitudes[idx]:.2f})")

    # Compare with original
    print("\n=== COMPARISON ===")
    fft_orig = np.fft.rfft(audio_orig)
    freqs_orig = np.fft.rfftfreq(len(audio_orig), 1.0 / sample_rate)
    mags_orig = np.abs(fft_orig)

    orig_dominant = freqs_orig[np.argmax(mags_orig)]
    gen_dominant = freqs[np.argmax(magnitudes)]

    print(f"Dominant frequency - Original: {orig_dominant:.2f} Hz")
    print(f"Dominant frequency - Generated: {gen_dominant:.2f} Hz")
    print(f"Frequency match: {abs(orig_dominant - gen_dominant):.2f} Hz difference")


def example_numpy_array():
    """Example: Create Chord from numpy array (e.g., from scipy, librosa)."""
    print("\n=== NUMPY ARRAY EXAMPLE ===")

    # Simulate audio from scipy/librosa (440 Hz + 880 Hz)
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)

    # Convert to Chord
    chord, metadata = Util.array_to_chord(
        audio,
        sample_rate=sample_rate,
        num_waves=4,
        pluck=False
    )

    print(f"Detected {metadata['num_components']} components:")
    for c in metadata['components']:
        print(f"  {c['frequency']:.2f} Hz, amplitude={c['amplitude']:.4f}")


def example_unified_api():
    """Example: Use unified to_chord() API with different input types."""
    print("\n=== UNIFIED API EXAMPLE ===")

    # From file path
    chord1, _ = Util.to_chord("tests/fixtures/piano_3_Bf_d_m_74.wav", num_waves=5)
    print(f"From file: {chord1.get_name()}")

    # From numpy array
    audio = np.sin(np.linspace(0, 20 * np.pi, 4410))
    chord2, _ = Util.to_chord(audio, sample_rate=44100, num_waves=2)
    print(f"From array: {chord2.get_name()}")

    # From bytes (16-bit PCM)
    audio_int16 = (audio * 32767).astype(np.int16)
    chord3, _ = Util.to_chord(
        audio_int16.tobytes(),
        sample_rate=44100,
        sample_width=2,
        num_waves=2
    )
    print(f"From bytes: {chord3.get_name()}")


if __name__ == "__main__":
    main()
    example_numpy_array()
    example_unified_api()
