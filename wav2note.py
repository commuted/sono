#!/usr/bin/env python3
"""
wav2note.py - WAV to Sono Note Converter using MPEG-2 Psychoacoustic Model 2

This utility analyzes a WAV file using the MPEG-2 Psychoacoustic Model 2 reference
implementation to determine perceptually significant frequency components, then
creates a sono Note containing the specified number of sine waves.

The psychoacoustic model implements:
- Critical band analysis (Bark scale)
- Absolute threshold of hearing (ATH)
- Spreading function for simultaneous masking
- Tonality estimation (tonal vs noise-like components)
- Signal-to-mask ratio (SMR) calculation

Usage:
    python wav2note.py input.wav output.json --num-waves 32 --sample-rate 22050
"""

import argparse
import json
import math
import wave
import struct
from typing import List, Tuple, Optional
import numpy as np

from sono import SoundElement, SumElements, FixedAttenuate, Note


# =============================================================================
# MPEG-2 Psychoacoustic Model 2 Constants
# =============================================================================

# Critical band edges in Hz (ISO/IEC 11172-3 Table D.1)
# 25 critical bands for frequencies up to ~20 kHz
CRITICAL_BAND_EDGES = [
    0, 100, 200, 300, 400, 510, 630, 770, 920, 1080,
    1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300,
    6400, 7700, 9500, 12000, 15500, 20500
]

# Absolute threshold of hearing in dB SPL (ISO/IEC 11172-3)
# Approximation of the Fletcher-Munson curve at threshold
def absolute_threshold_of_hearing(f: float) -> float:
    """
    Calculate the absolute threshold of hearing at frequency f (Hz).
    Based on the Terhardt formula used in MPEG audio.

    Returns threshold in dB SPL.
    """
    if f <= 0:
        return 100.0  # Effectively inaudible

    f_khz = f / 1000.0

    # Terhardt's formula (used in MPEG psychoacoustic models)
    ath = 3.64 * (f_khz ** -0.8) - 6.5 * math.exp(-0.6 * (f_khz - 3.3) ** 2) + \
          1e-3 * (f_khz ** 4)

    return ath


def freq_to_bark(f: float) -> float:
    """
    Convert frequency in Hz to critical band rate (Bark scale).
    Using Zwicker's formula.
    """
    if f <= 0:
        return 0.0
    return 13.0 * math.atan(0.00076 * f) + 3.5 * math.atan((f / 7500.0) ** 2)


def bark_to_freq(z: float) -> float:
    """
    Convert critical band rate (Bark) to frequency in Hz.
    Inverse of Zwicker's formula (approximation).
    """
    # Iterative solution since there's no closed form inverse
    f_low, f_high = 0.0, 24000.0
    for _ in range(50):  # Binary search
        f_mid = (f_low + f_high) / 2
        z_mid = freq_to_bark(f_mid)
        if z_mid < z:
            f_low = f_mid
        else:
            f_high = f_mid
    return (f_low + f_high) / 2


def get_critical_band(f: float) -> int:
    """
    Get the critical band index for a frequency.
    """
    for i in range(len(CRITICAL_BAND_EDGES) - 1):
        if CRITICAL_BAND_EDGES[i] <= f < CRITICAL_BAND_EDGES[i + 1]:
            return i
    return len(CRITICAL_BAND_EDGES) - 2


# =============================================================================
# Spreading Function
# =============================================================================

def spreading_function(dz: float) -> float:
    """
    Calculate the spreading function for masking.

    dz: difference in critical band rate (Bark) between masker and maskee

    Returns attenuation in dB.

    Based on ISO/IEC 11172-3 Psychoacoustic Model 2 spreading function.
    """
    if dz < -3:
        # Lower slope (toward lower frequencies)
        return 17 * dz - 0.4 * dz + 17
    elif dz < -1:
        return (0.4 * dz + 6) * dz
    elif dz < 0:
        return -17 * dz
    elif dz < 1:
        return dz * (0.4 * dz - 6)
    elif dz < 8:
        # Upper slope (toward higher frequencies) - asymmetric
        return -17 * dz + 0.15 * 70 * (dz - 1)
    else:
        return -100  # Essentially no masking


def spreading_function_db(dz: float, masker_level: float) -> float:
    """
    Full spreading function including level dependency.

    Higher level maskers have a gentler upper slope (more masking toward
    higher frequencies).
    """
    if dz >= 0:
        # Upper slope becomes gentler with increasing level
        level_factor = max(0, (masker_level - 40) / 80)
        upper_slope = -27 + level_factor * 10  # dB/Bark
        return upper_slope * dz
    else:
        # Lower slope (steeper, ~27 dB/Bark)
        lower_slope = 27
        return lower_slope * dz


# =============================================================================
# Tonality Estimation
# =============================================================================

def estimate_tonality(spectrum_db: np.ndarray, bin_index: int,
                      window_size: int = 3) -> float:
    """
    Estimate the tonality of a spectral component.

    Returns a value between 0 (noise-like) and 1 (tone-like).

    Based on the spectral flatness measure and local peak detection
    used in MPEG Psychoacoustic Model 2.
    """
    n_bins = len(spectrum_db)

    # Get local window
    start = max(0, bin_index - window_size)
    end = min(n_bins, bin_index + window_size + 1)
    local = spectrum_db[start:end]

    if len(local) < 3:
        return 0.5

    # Check if this is a local maximum (tonal indicator)
    center_idx = bin_index - start
    if center_idx <= 0 or center_idx >= len(local) - 1:
        return 0.5

    is_peak = (local[center_idx] > local[center_idx - 1] and
               local[center_idx] > local[center_idx + 1])

    if not is_peak:
        return 0.0  # Not a tonal component

    # Calculate local spectral flatness (geometric mean / arithmetic mean)
    local_linear = 10 ** (local / 20)
    geo_mean = np.exp(np.mean(np.log(local_linear + 1e-10)))
    arith_mean = np.mean(local_linear)

    sfm = geo_mean / (arith_mean + 1e-10)

    # Convert SFM to tonality index
    # SFM = 1 for flat spectrum (noise), SFM << 1 for tonal
    sfm_db = 10 * np.log10(sfm + 1e-10)

    # Map SFM to tonality: -60 dB -> 1.0 (tonal), 0 dB -> 0.0 (noise)
    tonality = min(1.0, max(0.0, sfm_db / -60.0))

    # Boost tonality for strong peaks
    peak_prominence = local[center_idx] - np.mean([local[center_idx - 1],
                                                    local[center_idx + 1]])
    if peak_prominence > 3:  # More than 3 dB above neighbors
        tonality = min(1.0, tonality + 0.2)

    return tonality


# =============================================================================
# Masking Threshold Calculation
# =============================================================================

def calculate_masking_threshold(frequencies: np.ndarray,
                                spectrum_db: np.ndarray,
                                sample_rate: float) -> np.ndarray:
    """
    Calculate the global masking threshold at each frequency bin.

    Implements the full MPEG-2 Psychoacoustic Model 2 masking calculation:
    1. Calculate absolute threshold of hearing
    2. Identify tonal and noise maskers
    3. Calculate individual masking thresholds from each masker
    4. Combine all thresholds (power summation)

    Returns masking threshold in dB for each frequency bin.
    """
    n_bins = len(frequencies)

    # Initialize with absolute threshold of hearing
    global_threshold = np.array([absolute_threshold_of_hearing(f)
                                  for f in frequencies])

    # Normalize spectrum to dB SPL reference (assuming 96 dB dynamic range)
    max_level = np.max(spectrum_db)
    spectrum_spl = spectrum_db - max_level + 96  # Reference to ~96 dB SPL max

    # Find potential maskers (local maxima above threshold)
    maskers = []
    for i in range(1, n_bins - 1):
        if frequencies[i] <= 0:
            continue

        # Check if local maximum
        if (spectrum_spl[i] > spectrum_spl[i-1] and
            spectrum_spl[i] > spectrum_spl[i+1]):

            # Check if above absolute threshold
            if spectrum_spl[i] > absolute_threshold_of_hearing(frequencies[i]):
                tonality = estimate_tonality(spectrum_spl, i)
                maskers.append({
                    'bin': i,
                    'freq': frequencies[i],
                    'level': spectrum_spl[i],
                    'bark': freq_to_bark(frequencies[i]),
                    'tonality': tonality
                })

    # Calculate masking from each masker
    for masker in maskers:
        masker_bark = masker['bark']
        masker_level = masker['level']
        tonality = masker['tonality']

        # Masking offset depends on tonality
        # Tones mask noise less effectively than noise masks tones
        # Tonal masker: offset = 14.5 + bark
        # Noise masker: offset = 5.5
        masking_offset = tonality * (14.5 + masker_bark) + (1 - tonality) * 5.5

        for i in range(n_bins):
            if frequencies[i] <= 0:
                continue

            maskee_bark = freq_to_bark(frequencies[i])
            dz = maskee_bark - masker_bark

            # Calculate spreading
            spread = spreading_function_db(dz, masker_level)

            # Individual masking threshold from this masker
            mask_threshold = masker_level + spread - masking_offset

            # Combine with global threshold (power summation)
            global_threshold[i] = 10 * np.log10(
                10 ** (global_threshold[i] / 10) +
                10 ** (mask_threshold / 10)
            )

    return global_threshold


def calculate_smr(frequencies: np.ndarray, spectrum_db: np.ndarray,
                  sample_rate: float) -> np.ndarray:
    """
    Calculate Signal-to-Mask Ratio for each frequency component.

    SMR = signal level - masking threshold

    Higher SMR means the component is more audible.
    """
    threshold = calculate_masking_threshold(frequencies, spectrum_db, sample_rate)

    # Normalize spectrum
    max_level = np.max(spectrum_db)
    spectrum_spl = spectrum_db - max_level + 96

    smr = spectrum_spl - threshold
    return smr


# =============================================================================
# WAV File Processing
# =============================================================================

def read_wav_file(filepath: str) -> Tuple[np.ndarray, int, int]:
    """
    Read a WAV file and return audio data, sample rate, and channels.

    Returns:
        audio: numpy array of samples (float, normalized to -1..1)
        sample_rate: sample rate in Hz
        n_channels: number of channels
    """
    with wave.open(filepath, 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        n_frames = wav.getnframes()

        raw_data = wav.readframes(n_frames)

    # Convert to numpy array based on sample width
    if sample_width == 1:
        # 8-bit unsigned
        audio = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float64)
        audio = (audio - 128) / 128.0
    elif sample_width == 2:
        # 16-bit signed
        audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float64)
        audio = audio / 32768.0
    elif sample_width == 3:
        # 24-bit signed (need manual unpacking)
        n_samples = len(raw_data) // 3
        audio = np.zeros(n_samples, dtype=np.float64)
        for i in range(n_samples):
            sample_bytes = raw_data[i*3:(i+1)*3] + (b'\x00' if raw_data[i*3+2] < 128 else b'\xff')
            audio[i] = struct.unpack('<i', sample_bytes)[0] / 8388608.0
    elif sample_width == 4:
        # 32-bit signed or float
        try:
            audio = np.frombuffer(raw_data, dtype=np.int32).astype(np.float64)
            audio = audio / 2147483648.0
        except:
            audio = np.frombuffer(raw_data, dtype=np.float32).astype(np.float64)
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    # Reshape for multi-channel
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels)
        # Mix down to mono
        audio = np.mean(audio, axis=1)

    return audio, sample_rate, n_channels


def analyze_spectrum(audio: np.ndarray, sample_rate: int,
                     fft_size: int = 4096) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Analyze the spectrum of audio using FFT with Hann windowing.

    For longer audio, uses Welch's method (averaged periodogram).

    Returns:
        frequencies: array of frequency bins
        magnitude_db: magnitude spectrum in dB
        phases: phase angle for each bin
    """
    # Use Hann window
    window = np.hanning(fft_size)

    # If audio is longer than FFT size, average multiple windows
    n_samples = len(audio)
    hop_size = fft_size // 2

    if n_samples < fft_size:
        # Pad with zeros
        padded = np.zeros(fft_size)
        padded[:n_samples] = audio
        audio = padded
        n_windows = 1
    else:
        n_windows = (n_samples - fft_size) // hop_size + 1

    # Accumulate power spectrum
    power_sum = np.zeros(fft_size // 2 + 1)
    phase_sum = np.zeros(fft_size // 2 + 1, dtype=complex)

    for i in range(n_windows):
        start = i * hop_size
        segment = audio[start:start + fft_size] * window

        fft_result = np.fft.rfft(segment)
        power_sum += np.abs(fft_result) ** 2
        phase_sum += fft_result

    # Average
    power_avg = power_sum / n_windows
    phase_avg = phase_sum / n_windows

    # Convert to dB (with floor to avoid log(0))
    magnitude_db = 10 * np.log10(power_avg + 1e-10)

    # Get phases from averaged complex spectrum
    phases = np.angle(phase_avg)

    # Frequency bins
    frequencies = np.fft.rfftfreq(fft_size, 1.0 / sample_rate)

    return frequencies, magnitude_db, phases


# =============================================================================
# Perceptual Frequency Selection
# =============================================================================

def select_frequencies_psychoacoustic(frequencies: np.ndarray,
                                       magnitude_db: np.ndarray,
                                       phases: np.ndarray,
                                       sample_rate: int,
                                       num_waves: int) -> List[Tuple[float, float, float]]:
    """
    Select the most perceptually significant frequency components.

    Uses MPEG-2 Psychoacoustic Model 2 to rank frequencies by their
    Signal-to-Mask Ratio (SMR).

    Returns:
        List of (frequency, amplitude, phase) tuples, sorted by perceptual importance
    """
    # Calculate SMR for all frequency bins
    smr = calculate_smr(frequencies, magnitude_db, sample_rate)

    # Convert magnitude from dB to linear amplitude
    # Normalize so max is 1.0
    max_db = np.max(magnitude_db)
    amplitude_linear = 10 ** ((magnitude_db - max_db) / 20)

    # Create list of (smr, freq, amplitude, phase) for all bins
    candidates = []
    for i in range(len(frequencies)):
        if frequencies[i] <= 0 or frequencies[i] > sample_rate / 2:
            continue
        if amplitude_linear[i] < 1e-6:  # Skip very quiet bins
            continue

        candidates.append({
            'smr': smr[i],
            'freq': frequencies[i],
            'amp': amplitude_linear[i],
            'phase': phases[i],
            'bin': i
        })

    # Sort by SMR (most perceptually significant first)
    candidates.sort(key=lambda x: x['smr'], reverse=True)

    # Select top frequencies, but avoid picking bins too close together
    # (within the same critical band, prefer the strongest one)
    selected = []
    used_bands = set()

    for candidate in candidates:
        if len(selected) >= num_waves:
            break

        freq = candidate['freq']
        band = get_critical_band(freq)

        # Allow multiple selections per band, but limit density
        bark = freq_to_bark(freq)
        too_close = False
        for sel in selected:
            sel_bark = freq_to_bark(sel[0])
            if abs(bark - sel_bark) < 0.5:  # Within 0.5 Bark
                too_close = True
                break

        if not too_close:
            selected.append((candidate['freq'], candidate['amp'], candidate['phase']))

    # If we don't have enough, relax the spacing constraint
    if len(selected) < num_waves:
        for candidate in candidates:
            if len(selected) >= num_waves:
                break

            freq = candidate['freq']
            if not any(abs(freq - s[0]) < 1 for s in selected):  # Not exact duplicate
                if (freq, candidate['amp'], candidate['phase']) not in selected:
                    selected.append((candidate['freq'], candidate['amp'], candidate['phase']))

    return selected[:num_waves]


# =============================================================================
# Sono Note Creation
# =============================================================================

def create_sono_note(components: List[Tuple[float, float, float]],
                     sample_rate: int,
                     name: str = "wav_note") -> Note:
    """
    Create a sono Note from frequency components.

    Args:
        components: List of (frequency, amplitude, phase) tuples
        sample_rate: Target sample rate
        name: Name for the note

    Returns:
        A sono Note containing all the frequency components summed together
    """
    if not components:
        raise ValueError("No components provided")

    # Create individual SoundElements for each component
    elements = []
    for i, (freq, amp, phase) in enumerate(components):
        elem = SoundElement(
            frequency=freq,
            sample_rate=sample_rate,
            name=f"{name}_partial_{i}",
            phase=phase,
            scale=amp
        )
        elements.append(elem)

    # Build a tree of SumElements to combine all partials
    if len(elements) == 1:
        combined = elements[0]
    else:
        # Build binary tree of sums for efficiency
        # Use a counter to ensure unique names across all tree levels
        sum_counter = [0]  # Use list for mutation in nested scope

        def make_unique_sum(a, b):
            sum_elem = SumElements(
                a=a,
                b=b,
                name=f"{name}_sum_{sum_counter[0]}"
            )
            sum_counter[0] += 1
            return sum_elem

        while len(elements) > 1:
            new_elements = []
            for i in range(0, len(elements), 2):
                if i + 1 < len(elements):
                    new_elements.append(make_unique_sum(elements[i], elements[i + 1]))
                else:
                    new_elements.append(elements[i])
            elements = new_elements
        combined = elements[0]

    # Normalize amplitude (divide by number of components to prevent clipping)
    normalized = FixedAttenuate(
        a=combined,
        scale=1.0 / len(components),
        name=f"{name}_normalized"
    )

    # Wrap in a Note
    note = Note(note=normalized, name=name)

    return note


# =============================================================================
# Main Program
# =============================================================================

def wav_to_note(input_path: str,
                num_waves: int = 32,
                target_sample_rate: Optional[int] = None,
                fft_size: int = 4096,
                note_name: str = "wav_note") -> Tuple[Note, dict]:
    """
    Convert a WAV file to a sono Note using psychoacoustic analysis.

    Args:
        input_path: Path to input WAV file
        num_waves: Number of sine wave components to extract
        target_sample_rate: Output sample rate (None = use WAV's rate)
        fft_size: FFT window size for analysis
        note_name: Name for the generated Note

    Returns:
        Tuple of (Note object, metadata dict)
    """
    # Read WAV file
    print(f"Reading {input_path}...")
    audio, wav_sample_rate, n_channels = read_wav_file(input_path)
    print(f"  Sample rate: {wav_sample_rate} Hz")
    print(f"  Channels: {n_channels}")
    print(f"  Duration: {len(audio) / wav_sample_rate:.2f} seconds")

    # Determine output sample rate
    if target_sample_rate is None:
        output_sample_rate = wav_sample_rate
    else:
        output_sample_rate = min(target_sample_rate, wav_sample_rate)
    print(f"  Output sample rate: {output_sample_rate} Hz")

    # Analyze spectrum
    print("Analyzing spectrum...")
    frequencies, magnitude_db, phases = analyze_spectrum(audio, wav_sample_rate, fft_size)
    print(f"  FFT size: {fft_size}")
    print(f"  Frequency resolution: {wav_sample_rate / fft_size:.2f} Hz")

    # Select frequencies using psychoacoustic model
    print(f"Selecting {num_waves} perceptually significant components...")
    components = select_frequencies_psychoacoustic(
        frequencies, magnitude_db, phases, wav_sample_rate, num_waves
    )
    print(f"  Selected {len(components)} components")

    # Print component info
    print("\nSelected frequency components (sorted by perceptual importance):")
    print("  {:>10}  {:>10}  {:>10}".format("Freq (Hz)", "Amplitude", "Phase"))
    print("  " + "-" * 34)
    for freq, amp, phase in sorted(components, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {freq:>10.2f}  {amp:>10.6f}  {phase:>10.4f}")
    if len(components) > 10:
        print(f"  ... and {len(components) - 10} more")

    # Create Note
    print("\nCreating sono Note...")
    note = create_sono_note(components, output_sample_rate, note_name)

    # Build metadata
    metadata = {
        "source_file": input_path,
        "source_sample_rate": wav_sample_rate,
        "source_channels": n_channels,
        "source_duration_samples": len(audio),
        "output_sample_rate": output_sample_rate,
        "num_components": len(components),
        "fft_size": fft_size,
        "components": [
            {"frequency": f, "amplitude": a, "phase": p}
            for f, a, p in components
        ]
    }

    return note, metadata


def save_note(note: Note, metadata: dict, output_path: str):
    """
    Save a Note and its metadata to a JSON file.
    """
    output = {
        "metadata": metadata,
        "note": note.dump()
    }

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert WAV file to sono Note using MPEG-2 Psychoacoustic Model 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.wav
  %(prog)s input.wav -o output.json --num-waves 64
  %(prog)s input.wav --sample-rate 22050 --num-waves 32
  %(prog)s input.wav --fft-size 8192 --name my_sound
        """
    )

    parser.add_argument("input", help="Input WAV file path")
    parser.add_argument("-o", "--output", default="out.json",
                        help="Output JSON file path (default: out.json)")
    parser.add_argument("-n", "--num-waves", type=int, default=32,
                        help="Number of sine wave components (default: 32)")
    parser.add_argument("-s", "--sample-rate", type=int, default=None,
                        help="Output sample rate (default: same as input)")
    parser.add_argument("-f", "--fft-size", type=int, default=4096,
                        help="FFT window size (default: 4096)")
    parser.add_argument("--name", type=str, default="wav_note",
                        help="Name for the generated Note (default: wav_note)")

    args = parser.parse_args()

    # Ensure output has .json extension
    output_path = args.output
    if not output_path.lower().endswith('.json'):
        output_path = output_path + '.json'

    # Validate arguments
    if args.num_waves < 1:
        parser.error("Number of waves must be at least 1")
    if args.fft_size < 256:
        parser.error("FFT size must be at least 256")
    if args.fft_size & (args.fft_size - 1):
        parser.error("FFT size must be a power of 2")

    # Process
    note, metadata = wav_to_note(
        input_path=args.input,
        num_waves=args.num_waves,
        target_sample_rate=args.sample_rate,
        fft_size=args.fft_size,
        note_name=args.name
    )

    # Save
    save_note(note, metadata, output_path)

    print("\nDone!")


if __name__ == "__main__":
    main()
