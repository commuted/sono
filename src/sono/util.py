# util.py
# Utility functions for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional
from math import pi, sin, asin, exp, log, atan

import wave
import struct

import numpy as np
from scipy.optimize import minimize

from .music import Chord
from .elements import SoundElement, SumElements, Pluck


# =============================================================================
# MPEG-2 Psychoacoustic Model 2 Constants
# =============================================================================

# Critical band edges in Hz (ISO/IEC 11172-3 Table D.1)
CRITICAL_BAND_EDGES = [
    0, 100, 200, 300, 400, 510, 630, 770, 920, 1080,
    1270, 1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300,
    6400, 7700, 9500, 12000, 15500, 20500
]


class Util:
    """Utility class for audio synthesis operations.

    Provides helper methods for common audio processing tasks such as
    eliminating pops at chord start by phase alignment.
    """

    @staticmethod
    def _collect_sound_element_names(dump: Dict[str, Any], names: List[str]) -> None:
        """Recursively collect all SoundElement names from a dump hierarchy.

        Args:
            dump: A dump dictionary from an element's dump() method.
            names: List to append found SoundElement names to.
        """
        if dump is None:
            return

        if dump.get("get_type") == "SoundElement":
            names.append(dump["get_name"])

        # Recurse into sub-elements
        if "a" in dump and dump["a"] is not None:
            Util._collect_sound_element_names(dump["a"], names)
        if "b" in dump and dump["b"] is not None:
            Util._collect_sound_element_names(dump["b"], names)

    @staticmethod
    def _collect_sound_element_data(
        dump: Dict[str, Any],
        data: List[Tuple[str, float, float]]
    ) -> None:
        """Recursively collect SoundElement data from a dump hierarchy.

        Args:
            dump: A dump dictionary from an element's dump() method.
            data: List to append (name, frequency, scale) tuples to.
        """
        if dump is None:
            return

        if dump.get("get_type") == "SoundElement":
            data.append((
                dump["get_name"],
                dump["get_frequency"],
                dump["get_scale"]
            ))

        # Recurse into sub-elements
        if "a" in dump and dump["a"] is not None:
            Util._collect_sound_element_data(dump["a"], data)
        if "b" in dump and dump["b"] is not None:
            Util._collect_sound_element_data(dump["b"], data)

    @staticmethod
    def fix_pop(chord: Chord) -> None:
        """Fix the pop/click at chord start by spreading and adjusting phases.

        The pop is caused by oscillators starting in phase, creating a large
        initial derivative (rapid amplitude change) and potentially a non-zero
        starting value. This method:
        1. Spreads oscillator phases evenly to reduce peak derivative
        2. Adjusts individual phase(s) so the combined signal starts at zero

        Args:
            chord: The Chord to fix.
        """
        # Get the chord's element hierarchy
        dump = chord.dump()

        # Collect all SoundElement names
        element_names: List[str] = []
        if dump.get("a") is not None:
            Util._collect_sound_element_names(dump["a"], element_names)

        n = len(element_names)
        if n == 0:
            return

        # Step 1: Spread phases evenly across 2π to reduce derivative
        phases = [(2 * pi * i) / n for i in range(n)]

        # Step 2: Calculate current sum of initial values
        current_sum = sum(sin(p) for p in phases)

        # Step 3: Adjust phase(s) to bring sum to zero
        # Try adjusting the last phase first
        if abs(current_sum) > 1e-10:
            # Sum of first n-1 phases
            partial_sum = sum(sin(p) for p in phases[:-1])

            # Need sin(new_phase) = -partial_sum to make total = 0
            target_sin = -partial_sum

            if abs(target_sin) <= 1.0:
                # Can solve with single phase adjustment
                phases[-1] = asin(target_sin)
            else:
                # Need to adjust multiple phases
                # Distribute the adjustment across phases
                adjustment_per_phase = current_sum / n
                for i in range(n):
                    # Iteratively adjust each phase to reduce its contribution
                    current_val = sin(phases[i])
                    new_val = current_val - adjustment_per_phase
                    if abs(new_val) <= 1.0:
                        phases[i] = asin(new_val)

        # Build msg to set init_phase for all SoundElements
        # Using set_init_phase ensures the phase persists through set_on()
        msg: Dict[str, Dict[str, List]] = {}
        for i, name in enumerate(element_names):
            msg[name] = {"set_init_phase": [phases[i]]}

        # Send the message through the chord's msg interface
        chord.msg(msg)

    @staticmethod
    def min_derivative(chord: Chord) -> None:
        """Fix the pop/click at chord start using derivative minimization.

        Uses scipy optimization to find phases that minimize the derivative
        energy of the summed signal, with a small penalty for non-zero start
        values. This produces smoother chord onsets than simple phase spreading.

        Args:
            chord: The Chord to fix.
        """
        # Get the chord's element hierarchy
        dump = chord.dump()

        # Collect all SoundElement data (name, frequency, scale)
        element_data: List[Tuple[str, float, float]] = []
        if dump.get("a") is not None:
            Util._collect_sound_element_data(dump["a"], element_data)

        n = len(element_data)
        if n == 0:
            return

        # Extract arrays for optimization
        names = [d[0] for d in element_data]
        freqs = np.array([d[1] for d in element_data])
        amps = np.array([d[2] for d in element_data])

        # Time grid for evaluation (short duration sufficient for optimization)
        fs = 2000  # sampling frequency
        T = 0.05   # evaluation duration
        t_grid = np.linspace(0, T, int(fs * T), endpoint=False)

        def objective(phases: np.ndarray) -> float:
            """Minimize derivative energy with start-value penalty."""
            # Derivative analytically: d/dt sin(2π f t + φ) = 2π f cos(...)
            dS = (amps[:, None] *
                  (2 * np.pi * freqs[:, None]) *
                  np.cos(2 * np.pi * freqs[:, None] * t_grid[None, :] +
                         phases[:, None])).sum(axis=0)

            # Energy of the derivative
            cost_derivative = np.mean(dS ** 2)

            # Start-value penalty
            S0 = (amps * np.sin(phases)).sum()
            lam = 1e-3
            cost_start = S0 ** 2

            return cost_derivative + lam * cost_start

        # Initial guess and bounds
        x0 = np.zeros(n)
        bounds = [(-np.pi, np.pi) for _ in range(n)]

        # Optimize
        result = minimize(
            fun=objective,
            x0=x0,
            bounds=bounds,
            method='L-BFGS-B',
            options=dict(maxiter=500, ftol=1e-8)
        )

        opt_phases = result.x

        # Build msg to set init_phase for all SoundElements
        msg: Dict[str, Dict[str, List]] = {}
        for i, name in enumerate(names):
            msg[name] = {"set_init_phase": [float(opt_phases[i])]}

        # Send the message through the chord's msg interface
        chord.msg(msg)

    # =========================================================================
    # MPEG-2 Psychoacoustic Model 2 Methods
    # =========================================================================

    @staticmethod
    def _absolute_threshold_of_hearing(f: float) -> float:
        """Calculate the absolute threshold of hearing at frequency f (Hz).

        Based on the Terhardt formula used in MPEG audio.

        Args:
            f: Frequency in Hz.

        Returns:
            Threshold in dB SPL.
        """
        if f <= 0:
            return 100.0  # Effectively inaudible

        f_khz = f / 1000.0

        # Terhardt's formula (used in MPEG psychoacoustic models)
        ath = (3.64 * (f_khz ** -0.8) -
               6.5 * exp(-0.6 * (f_khz - 3.3) ** 2) +
               1e-3 * (f_khz ** 4))

        return ath

    @staticmethod
    def _freq_to_bark(f: float) -> float:
        """Convert frequency in Hz to critical band rate (Bark scale).

        Using Zwicker's formula.

        Args:
            f: Frequency in Hz.

        Returns:
            Critical band rate in Bark.
        """
        if f <= 0:
            return 0.0
        return 13.0 * atan(0.00076 * f) + 3.5 * atan((f / 7500.0) ** 2)

    @staticmethod
    def _bark_to_freq(z: float) -> float:
        """Convert critical band rate (Bark) to frequency in Hz.

        Inverse of Zwicker's formula (approximation via binary search).

        Args:
            z: Critical band rate in Bark.

        Returns:
            Frequency in Hz.
        """
        f_low, f_high = 0.0, 24000.0
        for _ in range(50):  # Binary search
            f_mid = (f_low + f_high) / 2
            z_mid = Util._freq_to_bark(f_mid)
            if z_mid < z:
                f_low = f_mid
            else:
                f_high = f_mid
        return (f_low + f_high) / 2

    @staticmethod
    def _get_critical_band(f: float) -> int:
        """Get the critical band index for a frequency.

        Args:
            f: Frequency in Hz.

        Returns:
            Critical band index (0-24).
        """
        for i in range(len(CRITICAL_BAND_EDGES) - 1):
            if CRITICAL_BAND_EDGES[i] <= f < CRITICAL_BAND_EDGES[i + 1]:
                return i
        return len(CRITICAL_BAND_EDGES) - 2

    @staticmethod
    def _spreading_function_db(dz: float, masker_level: float) -> float:
        """Full spreading function including level dependency.

        Higher level maskers have a gentler upper slope (more masking toward
        higher frequencies).

        Args:
            dz: Difference in critical band rate (Bark) between masker and maskee.
            masker_level: Level of the masker in dB.

        Returns:
            Attenuation in dB.
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

    @staticmethod
    def _estimate_tonality(spectrum_db: np.ndarray, bin_index: int,
                           window_size: int = 3) -> float:
        """Estimate the tonality of a spectral component.

        Returns a value between 0 (noise-like) and 1 (tone-like).
        Based on spectral flatness and local peak detection.

        Args:
            spectrum_db: Spectrum in dB.
            bin_index: Index of the bin to analyze.
            window_size: Size of the analysis window.

        Returns:
            Tonality index (0 to 1).
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
        sfm_db = 10 * np.log10(sfm + 1e-10)

        # Map SFM to tonality: -60 dB -> 1.0 (tonal), 0 dB -> 0.0 (noise)
        tonality = min(1.0, max(0.0, sfm_db / -60.0))

        # Boost tonality for strong peaks
        peak_prominence = local[center_idx] - np.mean([local[center_idx - 1],
                                                        local[center_idx + 1]])
        if peak_prominence > 3:  # More than 3 dB above neighbors
            tonality = min(1.0, tonality + 0.2)

        return tonality

    @staticmethod
    def _calculate_masking_threshold(frequencies: np.ndarray,
                                     spectrum_db: np.ndarray,
                                     sample_rate: float) -> np.ndarray:
        """Calculate the global masking threshold at each frequency bin.

        Implements MPEG-2 Psychoacoustic Model 2 masking calculation.

        Args:
            frequencies: Array of frequency bins.
            spectrum_db: Magnitude spectrum in dB.
            sample_rate: Sample rate in Hz.

        Returns:
            Masking threshold in dB for each frequency bin.
        """
        n_bins = len(frequencies)

        # Initialize with absolute threshold of hearing
        global_threshold = np.array([Util._absolute_threshold_of_hearing(f)
                                     for f in frequencies])

        # Normalize spectrum to dB SPL reference (assuming 96 dB dynamic range)
        max_level = np.max(spectrum_db)
        spectrum_spl = spectrum_db - max_level + 96

        # Find potential maskers (local maxima above threshold)
        maskers = []
        for i in range(1, n_bins - 1):
            if frequencies[i] <= 0:
                continue

            # Check if local maximum
            if (spectrum_spl[i] > spectrum_spl[i-1] and
                spectrum_spl[i] > spectrum_spl[i+1]):

                # Check if above absolute threshold
                if spectrum_spl[i] > Util._absolute_threshold_of_hearing(frequencies[i]):
                    tonality = Util._estimate_tonality(spectrum_spl, i)
                    maskers.append({
                        'bin': i,
                        'freq': frequencies[i],
                        'level': spectrum_spl[i],
                        'bark': Util._freq_to_bark(frequencies[i]),
                        'tonality': tonality
                    })

        # Calculate masking from each masker
        for masker in maskers:
            masker_bark = masker['bark']
            masker_level = masker['level']
            tonality = masker['tonality']

            # Masking offset depends on tonality
            masking_offset = tonality * (14.5 + masker_bark) + (1 - tonality) * 5.5

            for i in range(n_bins):
                if frequencies[i] <= 0:
                    continue

                maskee_bark = Util._freq_to_bark(frequencies[i])
                dz = maskee_bark - masker_bark

                # Calculate spreading
                spread = Util._spreading_function_db(dz, masker_level)

                # Individual masking threshold from this masker
                mask_threshold = masker_level + spread - masking_offset

                # Combine with global threshold (power summation)
                global_threshold[i] = 10 * np.log10(
                    10 ** (global_threshold[i] / 10) +
                    10 ** (mask_threshold / 10)
                )

        return global_threshold

    @staticmethod
    def _calculate_smr(frequencies: np.ndarray, spectrum_db: np.ndarray,
                       sample_rate: float) -> np.ndarray:
        """Calculate Signal-to-Mask Ratio for each frequency component.

        SMR = signal level - masking threshold

        Args:
            frequencies: Array of frequency bins.
            spectrum_db: Magnitude spectrum in dB.
            sample_rate: Sample rate in Hz.

        Returns:
            SMR in dB for each frequency bin.
        """
        threshold = Util._calculate_masking_threshold(frequencies, spectrum_db, sample_rate)

        max_level = np.max(spectrum_db)
        spectrum_spl = spectrum_db - max_level + 96

        smr = spectrum_spl - threshold
        return smr

    # =========================================================================
    # WAV File Processing Methods
    # =========================================================================

    @staticmethod
    def _read_wav_file(filepath: str) -> Tuple[np.ndarray, int, int]:
        """Read a WAV file and return audio data, sample rate, and channels.

        Args:
            filepath: Path to the WAV file.

        Returns:
            Tuple of (audio array normalized to -1..1, sample_rate, n_channels).

        Raises:
            ValueError: If sample width is unsupported.
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
                sample_bytes = raw_data[i*3:(i+1)*3]
                sample_bytes += (b'\x00' if raw_data[i*3+2] < 128 else b'\xff')
                audio[i] = struct.unpack('<i', sample_bytes)[0] / 8388608.0
        elif sample_width == 4:
            # 32-bit signed or float
            try:
                audio = np.frombuffer(raw_data, dtype=np.int32).astype(np.float64)
                audio = audio / 2147483648.0
            except Exception:
                audio = np.frombuffer(raw_data, dtype=np.float32).astype(np.float64)
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        # Reshape for multi-channel and mix to mono
        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)
            audio = np.mean(audio, axis=1)

        return audio, sample_rate, n_channels

    @staticmethod
    def _analyze_spectrum(audio: np.ndarray, sample_rate: int,
                          fft_size: int = 4096) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Analyze the spectrum of audio using FFT with Hann windowing.

        For longer audio, uses Welch's method (averaged periodogram).

        Args:
            audio: Audio samples.
            sample_rate: Sample rate in Hz.
            fft_size: FFT window size.

        Returns:
            Tuple of (frequencies, magnitude_db, phases).
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

    @staticmethod
    def _select_frequencies_psychoacoustic(
        frequencies: np.ndarray,
        magnitude_db: np.ndarray,
        phases: np.ndarray,
        sample_rate: int,
        num_waves: int
    ) -> List[Tuple[float, float, float]]:
        """Select the most perceptually significant frequency components.

        Uses MPEG-2 Psychoacoustic Model 2 to rank frequencies by their
        Signal-to-Mask Ratio (SMR).

        Args:
            frequencies: Array of frequency bins.
            magnitude_db: Magnitude spectrum in dB.
            phases: Phase angles.
            sample_rate: Sample rate in Hz.
            num_waves: Number of components to select.

        Returns:
            List of (frequency, amplitude, phase) tuples.
        """
        # Calculate SMR for all frequency bins
        smr = Util._calculate_smr(frequencies, magnitude_db, sample_rate)

        # Convert magnitude from dB to linear amplitude
        max_db = np.max(magnitude_db)
        amplitude_linear = 10 ** ((magnitude_db - max_db) / 20)

        # Create list of candidates
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

        # Select top frequencies, avoiding bins too close together
        selected: List[Tuple[float, float, float]] = []

        for candidate in candidates:
            if len(selected) >= num_waves:
                break

            freq = candidate['freq']
            bark = Util._freq_to_bark(freq)

            # Check if too close to already selected
            too_close = False
            for sel in selected:
                sel_bark = Util._freq_to_bark(sel[0])
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
                if not any(abs(freq - s[0]) < 1 for s in selected):
                    entry = (candidate['freq'], candidate['amp'], candidate['phase'])
                    if entry not in selected:
                        selected.append(entry)

        return selected[:num_waves]

    @staticmethod
    def _create_sound_from_components(
        components: List[Tuple[float, float, float]],
        sample_rate: int,
        name: str = "wav_sound",
        pluck: bool = True
    ) -> Chord:
        """Create a Chord from frequency components.

        Args:
            components: List of (frequency, amplitude, phase) tuples.
            sample_rate: Target sample rate.
            name: Name for the generated Chord.
            pluck: If True, wrap with Pluck for envelope decay (default: True).

        Returns:
            A Chord containing all frequency components summed together.

        Raises:
            ValueError: If no components provided.
        """
        if not components:
            raise ValueError("No components provided")

        # Create individual SoundElements for each component
        # Amplitude is set directly in SoundElement.scale
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
        # Use scale=1.0 to preserve amplitudes (no attenuation)
        if len(elements) == 1:
            combined = elements[0]
        else:
            sum_counter = [0]

            def make_unique_sum(a, b):
                sum_elem = SumElements(
                    a=a,
                    b=b,
                    name=f"{name}_sum_{sum_counter[0]}",
                    scale=1.0  # No attenuation, amplitudes in SoundElement
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

        # Apply Pluck envelope for natural decay
        if pluck:
            root = Pluck(
                a=combined,
                sample_rate=sample_rate,
                name=f"{name}_pluck"
            )
        else:
            root = combined

        # Wrap in a Chord
        return Chord(note=root, name=name)

    # =========================================================================
    # Public WAV to Chord Method
    # =========================================================================

    @staticmethod
    def wav_to_chord(
        input_path: str,
        num_waves: int = 32,
        target_sample_rate: Optional[int] = None,
        fft_size: int = 4096,
        name: str = "wav_chord",
        pluck: bool = True
    ) -> Tuple[Chord, Dict[str, Any]]:
        """Convert a WAV file to a Chord using psychoacoustic analysis.

        Uses MPEG-2 Psychoacoustic Model 2 to identify perceptually significant
        frequency components and creates a Chord containing sine wave partials.

        Args:
            input_path: Path to input WAV file.
            num_waves: Number of sine wave components to extract (default: 32).
            target_sample_rate: Output sample rate (None = use WAV's rate).
            fft_size: FFT window size for analysis (default: 4096).
            name: Name for the generated Chord (default: "wav_chord").
            pluck: If True, wrap with Pluck for envelope decay (default: True).

        Returns:
            Tuple of (Chord object, metadata dict).

        Raises:
            ValueError: If num_waves < 1 or fft_size < 256.
        """
        if num_waves < 1:
            raise ValueError("Number of waves must be at least 1")
        if fft_size < 256:
            raise ValueError("FFT size must be at least 256")

        # Read WAV file
        audio, wav_sample_rate, n_channels = Util._read_wav_file(input_path)

        # Determine output sample rate
        if target_sample_rate is None:
            output_sample_rate = wav_sample_rate
        else:
            output_sample_rate = min(target_sample_rate, wav_sample_rate)

        # Analyze spectrum
        frequencies, magnitude_db, phases = Util._analyze_spectrum(
            audio, wav_sample_rate, fft_size
        )

        # Select frequencies using psychoacoustic model
        components = Util._select_frequencies_psychoacoustic(
            frequencies, magnitude_db, phases, wav_sample_rate, num_waves
        )

        # Create Chord
        chord = Util._create_sound_from_components(
            components, output_sample_rate, name, pluck
        )

        # Build metadata
        metadata = {
            "source_file": input_path,
            "source_sample_rate": wav_sample_rate,
            "source_channels": n_channels,
            "source_duration_samples": len(audio),
            "output_sample_rate": output_sample_rate,
            "num_components": len(components),
            "fft_size": fft_size,
            "pluck": pluck,
            "components": [
                {"frequency": f, "amplitude": a, "phase": p}
                for f, a, p in components
            ]
        }

        return chord, metadata

    @staticmethod
    def array_to_chord(
        audio: np.ndarray,
        sample_rate: int,
        num_waves: int = 32,
        fft_size: int = 4096,
        name: str = "array_chord",
        pluck: bool = True
    ) -> Tuple[Chord, Dict[str, Any]]:
        """Convert a numpy audio array to a Chord using psychoacoustic analysis.

        This is useful when working with audio libraries like scipy, librosa,
        soundfile, or pydub that provide audio as numpy arrays.

        Args:
            audio: Audio samples as numpy array. Can be:
                   - 1D array for mono
                   - 2D array with shape (n_samples, n_channels) for multi-channel
                   Values should be in range [-1.0, 1.0] or will be normalized.
            sample_rate: Sample rate in Hz.
            num_waves: Number of sine wave components to extract (default: 32).
            fft_size: FFT window size for analysis (default: 4096).
            name: Name for the generated Chord (default: "array_chord").
            pluck: If True, wrap with Pluck for envelope decay (default: True).

        Returns:
            Tuple of (Chord object, metadata dict).

        Raises:
            ValueError: If audio array is empty, num_waves < 1, or fft_size < 256.
        """
        if audio.size == 0:
            raise ValueError("Audio array is empty")
        if num_waves < 1:
            raise ValueError("Number of waves must be at least 1")
        if fft_size < 256:
            raise ValueError("FFT size must be at least 256")

        # Convert to float64 if needed
        audio = np.asarray(audio, dtype=np.float64)

        # Handle multi-channel by mixing to mono
        if audio.ndim == 2:
            n_channels = audio.shape[1]
            audio = np.mean(audio, axis=1)
        else:
            n_channels = 1

        # Normalize if values are outside [-1, 1]
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val

        # Analyze spectrum
        frequencies, magnitude_db, phases = Util._analyze_spectrum(
            audio, sample_rate, fft_size
        )

        # Select frequencies using psychoacoustic model
        components = Util._select_frequencies_psychoacoustic(
            frequencies, magnitude_db, phases, sample_rate, num_waves
        )

        # Create Chord
        chord = Util._create_sound_from_components(
            components, sample_rate, name, pluck
        )

        # Build metadata
        metadata = {
            "source_type": "numpy_array",
            "source_sample_rate": sample_rate,
            "source_channels": n_channels,
            "source_duration_samples": len(audio),
            "output_sample_rate": sample_rate,
            "num_components": len(components),
            "fft_size": fft_size,
            "pluck": pluck,
            "components": [
                {"frequency": f, "amplitude": a, "phase": p}
                for f, a, p in components
            ]
        }

        return chord, metadata

    @staticmethod
    def bytes_to_chord(
        audio_bytes: bytes,
        sample_rate: int,
        sample_width: int = 2,
        n_channels: int = 1,
        num_waves: int = 32,
        fft_size: int = 4096,
        name: str = "bytes_chord",
        pluck: bool = True
    ) -> Tuple[Chord, Dict[str, Any]]:
        """Convert raw PCM audio bytes to a Chord using psychoacoustic analysis.

        Args:
            audio_bytes: Raw PCM audio data.
            sample_rate: Sample rate in Hz.
            sample_width: Bytes per sample (1=8-bit, 2=16-bit, 4=32-bit).
            n_channels: Number of audio channels (default: 1).
            num_waves: Number of sine wave components to extract (default: 32).
            fft_size: FFT window size for analysis (default: 4096).
            name: Name for the generated Chord (default: "bytes_chord").
            pluck: If True, wrap with Pluck for envelope decay (default: True).

        Returns:
            Tuple of (Chord object, metadata dict).

        Raises:
            ValueError: If sample_width is unsupported or audio is empty.
        """
        if len(audio_bytes) == 0:
            raise ValueError("Audio bytes are empty")

        # Convert bytes to numpy array
        if sample_width == 1:
            # 8-bit unsigned
            audio = np.frombuffer(audio_bytes, dtype=np.uint8).astype(np.float64)
            audio = (audio - 128) / 128.0
        elif sample_width == 2:
            # 16-bit signed
            audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float64)
            audio = audio / 32768.0
        elif sample_width == 4:
            # 32-bit signed
            audio = np.frombuffer(audio_bytes, dtype=np.int32).astype(np.float64)
            audio = audio / 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        # Handle multi-channel
        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)

        return Util.array_to_chord(audio, sample_rate, num_waves, fft_size, name, pluck)

    @staticmethod
    def fileobj_to_chord(
        fileobj,
        num_waves: int = 32,
        fft_size: int = 4096,
        name: str = "fileobj_chord",
        pluck: bool = True
    ) -> Tuple[Chord, Dict[str, Any]]:
        """Convert a file-like object containing WAV data to a Chord.

        Useful for reading from io.BytesIO or other file-like objects.

        Args:
            fileobj: File-like object with WAV data (must support read/seek).
            num_waves: Number of sine wave components to extract (default: 32).
            fft_size: FFT window size for analysis (default: 4096).
            name: Name for the generated Chord (default: "fileobj_chord").
            pluck: If True, wrap with Pluck for envelope decay (default: True).

        Returns:
            Tuple of (Chord object, metadata dict).

        Raises:
            ValueError: If the file object doesn't contain valid WAV data.
        """
        with wave.open(fileobj, 'rb') as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            n_frames = wav.getnframes()
            raw_data = wav.readframes(n_frames)

        # Convert using bytes_to_chord logic
        if sample_width == 1:
            audio = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float64)
            audio = (audio - 128) / 128.0
        elif sample_width == 2:
            audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float64)
            audio = audio / 32768.0
        elif sample_width == 4:
            audio = np.frombuffer(raw_data, dtype=np.int32).astype(np.float64)
            audio = audio / 2147483648.0
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        if n_channels > 1:
            audio = audio.reshape(-1, n_channels)

        chord, metadata = Util.array_to_chord(
            audio, sample_rate, num_waves, fft_size, name, pluck
        )

        # Update metadata to reflect file source
        metadata["source_type"] = "file_object"
        metadata["source_channels"] = n_channels

        return chord, metadata

    @staticmethod
    def to_chord(
        source,
        sample_rate: Optional[int] = None,
        num_waves: int = 32,
        fft_size: int = 4096,
        name: str = "audio_chord",
        pluck: bool = True,
        **kwargs
    ) -> Tuple[Chord, Dict[str, Any]]:
        """Convert various audio sources to a Chord (auto-detecting format).

        This is a unified method that accepts multiple input types:
        - str or Path: Treated as a file path to a WAV file
        - numpy.ndarray: Treated as audio samples (requires sample_rate)
        - bytes: Treated as raw PCM data (requires sample_rate, sample_width, n_channels)
        - file-like object: Treated as WAV file data

        Args:
            source: Audio source (path, array, bytes, or file object).
            sample_rate: Sample rate in Hz (required for array/bytes input).
            num_waves: Number of sine wave components to extract (default: 32).
            fft_size: FFT window size for analysis (default: 4096).
            name: Name for the generated Chord (default: "audio_chord").
            pluck: If True, wrap with Pluck for envelope decay (default: True).
            **kwargs: Additional arguments passed to format-specific methods:
                      - sample_width: For bytes input (default: 2)
                      - n_channels: For bytes input (default: 1)
                      - target_sample_rate: For WAV file input

        Returns:
            Tuple of (Chord object, metadata dict).

        Raises:
            ValueError: If source type is unsupported or required args are missing.
            TypeError: If source type cannot be determined.
        """
        from pathlib import Path
        import io

        # String or Path -> WAV file
        if isinstance(source, (str, Path)):
            target_sr = kwargs.get('target_sample_rate', None)
            return Util.wav_to_chord(str(source), num_waves, target_sr, fft_size, name, pluck)

        # NumPy array
        if isinstance(source, np.ndarray):
            if sample_rate is None:
                raise ValueError("sample_rate is required for numpy array input")
            return Util.array_to_chord(source, sample_rate, num_waves, fft_size, name, pluck)

        # Bytes -> raw PCM
        if isinstance(source, bytes):
            if sample_rate is None:
                raise ValueError("sample_rate is required for bytes input")
            sample_width = kwargs.get('sample_width', 2)
            n_channels = kwargs.get('n_channels', 1)
            return Util.bytes_to_chord(
                source, sample_rate, sample_width, n_channels,
                num_waves, fft_size, name, pluck
            )

        # File-like object (has read method)
        if hasattr(source, 'read'):
            return Util.fileobj_to_chord(source, num_waves, fft_size, name, pluck)

        raise TypeError(f"Unsupported source type: {type(source).__name__}")
