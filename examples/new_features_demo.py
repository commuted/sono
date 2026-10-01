#!/usr/bin/env python3
"""
Demo of new sono features: oscillators, ADSR, LFO, filters, WAV playback

This example demonstrates:
1. New oscillator types (Sawtooth, Square, WhiteNoise)
2. ADSR envelope for amplitude control
3. LFO for vibrato (frequency modulation)
4. Biquad filter for tone shaping
5. WAV file playback
6. Combining multiple features

Run: python3 examples/new_features_demo.py
"""

import sys
sys.path.insert(0, '..')

import sono as sl
import wave
import struct


def write_wav(filename: str, samples: list, sample_rate: int = 44100):
    """Write samples to a WAV file."""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Convert float samples to 16-bit integers
        int_samples = [int(max(-1.0, min(1.0, s)) * 32767) for s in samples]
        wav_data = struct.pack(f'{len(int_samples)}h', *int_samples)
        wav_file.writeframes(wav_data)
    print(f"Wrote {len(samples)} samples to {filename}")


def demo_sawtooth():
    """Demo 1: Sawtooth oscillator with ADSR envelope."""
    print("\n=== Demo 1: Sawtooth with ADSR ===")
    
    # Create sawtooth oscillator
    saw = sl.SawtoothElement(frequency=220.0)  # A3
    
    # Create ADSR envelope
    env = sl.ADSR(
        attack=0.05,    # 50ms attack
        decay=0.1,      # 100ms decay
        sustain=0.6,    # 60% sustain level
        release=0.3     # 300ms release
    )
    
    # Combine oscillator with envelope
    enveloped = sl.EnvelopedElement(saw, env)
    
    # Generate 2 seconds of audio
    sample_rate = 44100
    duration = 2.0
    note_duration = 1.0  # Hold note for 1 second
    
    samples = []
    enveloped.set_on()  # Start note
    
    for i in range(int(duration * sample_rate)):
        # Release after 1 second
        if i == int(note_duration * sample_rate):
            enveloped.set_off()
        samples.append(enveloped.sample())
    
    write_wav("demo1_sawtooth_adsr.wav", samples)


def demo_square_pwm():
    """Demo 2: Square wave with pulse width modulation."""
    print("\n=== Demo 2: Square Wave with PWM ===")
    
    # Create square oscillator with 50% duty cycle
    square = sl.SquareElement(frequency=440.0, duty_cycle=0.5)
    
    # Apply envelope
    env = sl.ADSR(attack=0.01, decay=0.05, sustain=0.8, release=0.2)
    enveloped = sl.EnvelopedElement(square, env)
    
    sample_rate = 44100
    duration = 2.0
    samples = []
    
    enveloped.set_on()
    
    for i in range(int(duration * sample_rate)):
        # Modulate duty cycle over time (10% to 90%)
        duty = 0.1 + 0.8 * (i / (duration * sample_rate))
        square.set_duty_cycle(duty)
        
        if i == int(1.5 * sample_rate):
            enveloped.set_off()
        
        samples.append(enveloped.sample())
    
    write_wav("demo2_square_pwm.wav", samples)


def demo_vibrato():
    """Demo 3: Sine wave with LFO vibrato."""
    print("\n=== Demo 3: Vibrato with LFO ===")
    
    # Create carrier oscillator
    carrier = sl.SoundElement(frequency=440.0)  # A4
    
    # Create LFO for vibrato (5 Hz, ±10 Hz depth)
    lfo = sl.LFO(rate=5.0, depth=10.0, waveform="sine")
    
    # Apply frequency modulation
    vibrato = sl.FrequencyModulation(carrier, lfo)
    
    # Add envelope
    env = sl.ADSR(attack=0.1, decay=0.2, sustain=0.7, release=0.4)
    enveloped = sl.EnvelopedElement(vibrato, env)
    
    sample_rate = 44100
    duration = 3.0
    samples = []
    
    enveloped.set_on()
    
    for i in range(int(duration * sample_rate)):
        if i == int(2.5 * sample_rate):
            enveloped.set_off()
        samples.append(enveloped.sample())
    
    write_wav("demo3_vibrato.wav", samples)


def demo_filtered_sawtooth():
    """Demo 4: Filtered sawtooth with resonance."""
    print("\n=== Demo 4: Filtered Sawtooth ===")
    
    # Create sawtooth (rich harmonics)
    saw = sl.SawtoothElement(frequency=110.0)  # A2
    
    # Apply lowpass filter with resonance
    filtered = sl.BiquadFilter(
        source=saw,
        filter_type="lowpass",
        cutoff=1000.0,  # 1 kHz cutoff
        q=5.0           # High resonance
    )
    
    # Add envelope
    env = sl.ADSR(attack=0.02, decay=0.3, sustain=0.4, release=0.5)
    enveloped = sl.EnvelopedElement(filtered, env)
    
    sample_rate = 44100
    duration = 3.0
    samples = []
    
    enveloped.set_on()
    
    for i in range(int(duration * sample_rate)):
        # Sweep filter cutoff from 200 Hz to 4000 Hz
        progress = i / (duration * sample_rate)
        cutoff = 200 + 3800 * progress
        filtered.set_cutoff(cutoff)
        
        if i == int(2.5 * sample_rate):
            enveloped.set_off()
        
        samples.append(enveloped.sample())
    
    write_wav("demo4_filtered_sawtooth.wav", samples)


def demo_noise_percussion():
    """Demo 5: White noise percussion with filter."""
    print("\n=== Demo 5: Noise Percussion ===")
    
    # Create white noise
    noise = sl.WhiteNoiseElement(seed=42)  # Reproducible
    
    # Apply bandpass filter (snare-like)
    filtered = sl.BiquadFilter(
        source=noise,
        filter_type="bandpass",
        cutoff=2000.0,
        q=2.0
    )
    
    # Short, punchy envelope
    env = sl.ADSR(attack=0.001, decay=0.05, sustain=0.0, release=0.1)
    enveloped = sl.EnvelopedElement(filtered, env)
    
    sample_rate = 44100
    duration = 2.0
    samples = []
    
    # Create 4 hits
    hit_times = [0.0, 0.5, 1.0, 1.5]
    current_hit = 0
    
    for i in range(int(duration * sample_rate)):
        time = i / sample_rate
        
        # Trigger next hit
        if current_hit < len(hit_times) and time >= hit_times[current_hit]:
            enveloped.set_on()
            current_hit += 1
        
        samples.append(enveloped.sample())
    
    write_wav("demo5_noise_percussion.wav", samples)


def demo_complex_patch():
    """Demo 6: Complex patch combining multiple features."""
    print("\n=== Demo 6: Complex Patch ===")
    
    # Layer 1: Filtered sawtooth bass
    bass = sl.SawtoothElement(frequency=55.0)  # A1
    bass_filter = sl.BiquadFilter(bass, "lowpass", cutoff=300.0, q=1.0)
    bass_env = sl.ADSR(attack=0.01, decay=0.1, sustain=0.8, release=0.3)
    bass_final = sl.EnvelopedElement(bass_filter, bass_env)
    
    # Layer 2: Square lead with vibrato
    lead = sl.SquareElement(frequency=440.0, duty_cycle=0.3)
    lead_lfo = sl.LFO(rate=6.0, depth=8.0, waveform="sine")
    lead_vibrato = sl.FrequencyModulation(lead, lead_lfo)
    lead_env = sl.ADSR(attack=0.05, decay=0.2, sustain=0.6, release=0.4)
    lead_final = sl.EnvelopedElement(lead_vibrato, lead_env)
    
    # Mix layers
    mixed = sl.MixElements(a=bass_final, b=lead_final)
    
    sample_rate = 44100
    duration = 3.0
    samples = []
    
    # Start bass
    bass_final.set_on()
    
    for i in range(int(duration * sample_rate)):
        time = i / sample_rate
        
        # Start lead at 0.5s
        if i == int(0.5 * sample_rate):
            lead_final.set_on()
        
        # Release bass at 2.5s
        if i == int(2.5 * sample_rate):
            bass_final.set_off()
        
        # Release lead at 2.7s
        if i == int(2.7 * sample_rate):
            lead_final.set_off()
        
        samples.append(mixed.sample())
    
    write_wav("demo6_complex_patch.wav", samples)


def demo_wav_playback():
    """Demo 7: WAV file playback (if demo1 exists)."""
    print("\n=== Demo 7: WAV File Playback ===")
    
    try:
        # Try to play back the first demo file
        wav = sl.WAVFileElement(filepath="demo1_sawtooth_adsr.wav", loop=False)
        
        sample_rate = 44100
        duration = 2.0
        samples = []
        
        wav.set_on()
        
        for i in range(int(duration * sample_rate)):
            sample = wav.sample()
            if wav.is_finished():
                break
            samples.append(sample)
        
        write_wav("demo7_wav_playback.wav", samples)
        print(f"Played back {len(samples)} samples from demo1_sawtooth_adsr.wav")
    except FileNotFoundError:
        print("Skipping WAV playback demo (demo1 file not found)")


def main():
    """Run all demos."""
    print("=" * 60)
    print("sono New Features Demo")
    print("=" * 60)
    print("\nThis will generate several WAV files demonstrating:")
    print("- New oscillators (Sawtooth, Square, WhiteNoise)")
    print("- ADSR envelopes")
    print("- LFO vibrato")
    print("- Biquad filters")
    print("- WAV file playback")
    print("- Complex patches")
    
    demo_sawtooth()
    demo_square_pwm()
    demo_vibrato()
    demo_filtered_sawtooth()
    demo_noise_percussion()
    demo_complex_patch()
    demo_wav_playback()
    
    print("\n" + "=" * 60)
    print("All demos complete! Check the generated WAV files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
