#!/usr/bin/env python3
"""
Test: Verify that Util.fix_pop() prevents onset pops/clicks

Generates two versions of the same chord:
1. Without fix_pop - phases aligned, causes pop
2. With fix_pop - phases spread, no pop

Measures and compares:
- Initial amplitude (should be near zero)
- Initial derivative (rate of change, should be minimized)
- Audible difference in WAV files
"""

import sys
sys.path.insert(0, '..')

import sono as sl
import wave
import struct
import numpy as np


def measure_onset_characteristics(samples, sample_rate=44100):
    """Measure onset characteristics of audio samples.
    
    Returns:
        dict with 'initial_amplitude', 'initial_derivative', 'max_derivative'
    """
    if len(samples) < 10:
        return None
    
    # Initial amplitude (first sample)
    initial_amp = abs(samples[0])
    
    # Initial derivative (difference between first two samples)
    initial_deriv = abs(samples[1] - samples[0]) * sample_rate
    
    # Maximum derivative in first 100 samples
    derivatives = np.diff(samples[:100]) * sample_rate
    max_deriv = np.max(np.abs(derivatives))
    
    return {
        'initial_amplitude': initial_amp,
        'initial_derivative': initial_deriv,
        'max_derivative': max_deriv
    }


def create_chord_without_fix():
    """Create a chord without fix_pop - will have aligned phases."""
    chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
    # Do NOT call fix_pop
    chord.set_on()
    chord.sample_pluck()
    return chord


def create_chord_with_fix():
    """Create a chord with fix_pop - phases will be spread."""
    chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
    sl.Util.fix_pop(chord)  # Apply fix
    chord.set_on()
    chord.sample_pluck()
    return chord


def generate_samples(chord, num_samples=44100):
    """Generate audio samples from a chord."""
    samples = []
    for _ in range(num_samples):
        samples.append(chord.sample())
    return np.array(samples)


def write_wav(filename, samples, sample_rate=44100):
    """Write samples to WAV file."""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            int_sample = int(clamped * 32767)
            wav_file.writeframes(struct.pack('<h', int_sample))


def main():
    print("="*60)
    print("Testing Util.fix_pop() Effectiveness")
    print("="*60)
    print()
    
    sample_rate = 44100
    duration = 1.0  # 1 second
    num_samples = int(sample_rate * duration)
    
    # Test 1: Without fix_pop
    print("1. Generating chord WITHOUT fix_pop...")
    chord_no_fix = create_chord_without_fix()
    samples_no_fix = generate_samples(chord_no_fix, num_samples)
    metrics_no_fix = measure_onset_characteristics(samples_no_fix, sample_rate)
    
    print(f"   Initial amplitude: {metrics_no_fix['initial_amplitude']:.6f}")
    print(f"   Initial derivative: {metrics_no_fix['initial_derivative']:.2f}")
    print(f"   Max derivative (first 100 samples): {metrics_no_fix['max_derivative']:.2f}")
    print()
    
    # Test 2: With fix_pop
    print("2. Generating chord WITH fix_pop...")
    chord_with_fix = create_chord_with_fix()
    samples_with_fix = generate_samples(chord_with_fix, num_samples)
    metrics_with_fix = measure_onset_characteristics(samples_with_fix, sample_rate)
    
    print(f"   Initial amplitude: {metrics_with_fix['initial_amplitude']:.6f}")
    print(f"   Initial derivative: {metrics_with_fix['initial_derivative']:.2f}")
    print(f"   Max derivative (first 100 samples): {metrics_with_fix['max_derivative']:.2f}")
    print()
    
    # Calculate improvements
    print("3. Improvement Analysis:")
    print()
    
    amp_improvement = (1 - metrics_with_fix['initial_amplitude'] / 
                       max(metrics_no_fix['initial_amplitude'], 1e-10)) * 100
    deriv_improvement = (1 - metrics_with_fix['initial_derivative'] / 
                         max(metrics_no_fix['initial_derivative'], 1e-10)) * 100
    max_deriv_improvement = (1 - metrics_with_fix['max_derivative'] / 
                             max(metrics_no_fix['max_derivative'], 1e-10)) * 100
    
    print(f"   Initial amplitude reduction: {amp_improvement:.1f}%")
    print(f"   Initial derivative reduction: {deriv_improvement:.1f}%")
    print(f"   Max derivative reduction: {max_deriv_improvement:.1f}%")
    print()
    
    # Write WAV files for audible comparison
    print("4. Writing WAV files for audible comparison...")
    write_wav("test_no_fix_pop.wav", samples_no_fix, sample_rate)
    write_wav("test_with_fix_pop.wav", samples_with_fix, sample_rate)
    print("   - test_no_fix_pop.wav (should have audible click)")
    print("   - test_with_fix_pop.wav (should be smooth)")
    print()
    
    # Verdict
    print("="*60)
    print("VERDICT:")
    print("="*60)
    
    if metrics_with_fix['initial_amplitude'] < metrics_no_fix['initial_amplitude'] * 0.5:
        print("✓ Initial amplitude significantly reduced")
    else:
        print("✗ Initial amplitude not significantly reduced")
    
    if metrics_with_fix['initial_derivative'] < metrics_no_fix['initial_derivative'] * 0.5:
        print("✓ Initial derivative significantly reduced")
    else:
        print("✗ Initial derivative not significantly reduced")
    
    if metrics_with_fix['max_derivative'] < metrics_no_fix['max_derivative'] * 0.8:
        print("✓ Maximum derivative reduced")
    else:
        print("✗ Maximum derivative not significantly reduced")
    
    print()
    print("Listen to the WAV files to hear the difference:")
    print("- test_no_fix_pop.wav should have a noticeable click at start")
    print("- test_with_fix_pop.wav should start smoothly without click")
    print()


if __name__ == "__main__":
    main()
