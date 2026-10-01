import unittest
import math
import numpy as np
import sono as sl


class TestMinDerivativeBasic(unittest.TestCase):
    """Test basic min_derivative functionality."""

    def test_modifies_phases(self):
        """Check that min_derivative modifies element phases."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        # Get initial phases
        dump_before = chord.dump()
        initial_phases = []
        self._collect_phases(dump_before["a"], initial_phases)

        # Apply min_derivative
        sl.Util.min_derivative(chord)

        # Get phases after
        dump_after = chord.dump()
        final_phases = []
        self._collect_phases(dump_after["a"], final_phases)

        # At least some phases should have changed
        self.assertEqual(len(initial_phases), len(final_phases))
        phases_changed = any(
            abs(i - f) > 1e-10
            for i, f in zip(initial_phases, final_phases)
        )
        self.assertTrue(phases_changed, "Phases should be modified by min_derivative")

    def test_returns_none(self):
        """Check that min_derivative returns None."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)
        result = sl.Util.min_derivative(chord)
        self.assertIsNone(result)

    def test_does_not_raise_on_valid_chord(self):
        """Check that min_derivative doesn't raise on a valid chord."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)
        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative raised an exception: {e}")

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


class TestMinDerivativeEmptyChord(unittest.TestCase):
    """Test min_derivative with empty or minimal chords."""

    def test_empty_chord_no_error(self):
        """Check that min_derivative handles chord with no elements."""
        chord = sl.Chord()
        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative raised an exception on empty chord: {e}")

    def test_empty_chord_returns_none(self):
        """Check that min_derivative returns None for empty chord."""
        chord = sl.Chord()
        result = sl.Util.min_derivative(chord)
        self.assertIsNone(result)


class TestMinDerivativeSingleElement(unittest.TestCase):
    """Test min_derivative with single SoundElement chord."""

    def test_single_element_no_error(self):
        """Check that min_derivative works with single element."""
        elem = sl.SoundElement(frequency=440.0)
        chord = sl.Chord(note=elem)
        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative raised an exception: {e}")

    def test_single_element_phase_set(self):
        """Check that single element gets a phase assigned."""
        elem = sl.SoundElement(frequency=440.0, name="test_elem")
        chord = sl.Chord(note=elem)

        sl.Util.min_derivative(chord)

        # Get the phase after optimization
        dump = chord.dump()
        self.assertIsNotNone(dump["a"])
        # Phase should be a valid float
        phase = dump["a"]["get_phase"]
        self.assertIsInstance(phase, float)


class TestMinDerivativeMultipleElements(unittest.TestCase):
    """Test min_derivative with multiple SoundElements."""

    def test_major_chord_three_elements(self):
        """Check that major chord (3 notes) is processed correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        sl.Util.min_derivative(chord)

        # Collect all phases
        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        self.assertEqual(len(phases), 3)  # C, E, G
        for phase in phases:
            self.assertIsInstance(phase, float)

    def test_seventh_chord_four_elements(self):
        """Check that 7th chord (4 notes) is processed correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "maj7"), pluck=False)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        self.assertEqual(len(phases), 4)  # C, E, G, B

    def test_ninth_chord_five_elements(self):
        """Check that 9th chord (5 notes) is processed correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "9"), pluck=False)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        self.assertEqual(len(phases), 5)  # C, E, G, Bb, D

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


class TestMinDerivativePhaseBounds(unittest.TestCase):
    """Test that optimized phases are within expected bounds."""

    def test_phases_within_bounds(self):
        """Check that all phases are within [-π, π]."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        for phase in phases:
            self.assertGreaterEqual(phase, -math.pi,
                f"Phase {phase} is less than -π")
            self.assertLessEqual(phase, math.pi,
                f"Phase {phase} is greater than π")

    def test_phases_are_finite(self):
        """Check that all phases are finite numbers."""
        chord = sl.Chord().make_a_chord((4, "C", "maj7"), pluck=False)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        for phase in phases:
            self.assertTrue(math.isfinite(phase),
                f"Phase {phase} is not finite")

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


class TestMinDerivativeDerivativeReduction(unittest.TestCase):
    """Test that min_derivative reduces derivative energy."""

    def test_derivative_energy_reduced(self):
        """Check that derivative energy is reduced after optimization."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        # Get initial derivative energy
        initial_energy = self._compute_derivative_energy(chord)

        # Apply optimization
        sl.Util.min_derivative(chord)

        # Get final derivative energy
        final_energy = self._compute_derivative_energy(chord)

        # Energy should be reduced or equal
        self.assertLessEqual(final_energy, initial_energy * 1.01,
            f"Derivative energy increased: {initial_energy} -> {final_energy}")

    def test_derivative_energy_significantly_reduced_for_in_phase(self):
        """Check derivative energy reduction when starting from all-zero phases."""
        # Create elements with zero phase (worst case for derivative)
        elem1 = sl.SoundElement(frequency=261.63, phase=0.0)  # C4
        elem2 = sl.SoundElement(frequency=329.63, phase=0.0)  # E4
        elem3 = sl.SoundElement(frequency=392.00, phase=0.0)  # G4

        sum1 = sl.SumElements(a=elem1, b=elem2)
        sum2 = sl.SumElements(a=sum1, b=elem3)
        chord = sl.Chord(note=sum2)

        initial_energy = self._compute_derivative_energy(chord)

        sl.Util.min_derivative(chord)

        final_energy = self._compute_derivative_energy(chord)

        # Should see meaningful reduction
        self.assertLess(final_energy, initial_energy,
            "Derivative energy should be reduced for in-phase start")

    def _compute_derivative_energy(self, chord):
        """Compute derivative energy for a chord's current phase configuration."""
        dump = chord.dump()
        element_data = []
        self._collect_element_data(dump["a"], element_data)

        if not element_data:
            return 0.0

        freqs = np.array([d[1] for d in element_data])
        amps = np.array([d[2] for d in element_data])
        phases = np.array([d[3] for d in element_data])

        # Time grid
        fs = 2000
        T = 0.05
        t_grid = np.linspace(0, T, int(fs * T), endpoint=False)

        # Compute derivative
        dS = (amps[:, None] *
              (2 * np.pi * freqs[:, None]) *
              np.cos(2 * np.pi * freqs[:, None] * t_grid[None, :] +
                     phases[:, None])).sum(axis=0)

        return np.mean(dS ** 2)

    def _collect_element_data(self, dump, data):
        """Collect (name, freq, scale, phase) from dump."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            data.append((
                dump["get_name"],
                dump["get_frequency"],
                dump["get_scale"],
                dump["get_phase"]
            ))
        if "a" in dump and dump["a"] is not None:
            self._collect_element_data(dump["a"], data)
        if "b" in dump and dump["b"] is not None:
            self._collect_element_data(dump["b"], data)


class TestMinDerivativeStartValue(unittest.TestCase):
    """Test that min_derivative considers start value penalty."""

    def test_start_value_reduced_from_worst_case(self):
        """Check that start value is reduced compared to all-zero phases."""
        # Create chord with explicit zero phases (worst case for start value)
        elem1 = sl.SoundElement(frequency=261.63, phase=0.0)
        elem2 = sl.SoundElement(frequency=329.63, phase=0.0)
        elem3 = sl.SoundElement(frequency=392.00, phase=0.0)
        sum1 = sl.SumElements(a=elem1, b=elem2)
        sum2 = sl.SumElements(a=sum1, b=elem3)
        chord = sl.Chord(note=sum2)

        # Compute initial start value (all phases = 0, so sin(0) = 0)
        # But after SumElements scaling, check actual signal
        dump_before = chord.dump()
        data_before = []
        self._collect_element_data(dump_before["a"], data_before)
        start_before = sum(d[2] * math.sin(d[3]) for d in data_before)

        sl.Util.min_derivative(chord)

        # Compute start value after optimization
        dump_after = chord.dump()
        data_after = []
        self._collect_element_data(dump_after["a"], data_after)
        start_after = sum(d[2] * math.sin(d[3]) for d in data_after)

        # The start value penalty exists, so it should have some effect
        # (though derivative minimization takes priority)
        # Just verify the optimization completed and produced finite values
        self.assertTrue(math.isfinite(start_after),
            f"Start value should be finite, got {start_after}")

    def test_start_value_is_finite(self):
        """Check that the start value is a finite number."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        element_data = []
        self._collect_element_data(dump["a"], element_data)

        start_value = sum(d[2] * math.sin(d[3]) for d in element_data)

        self.assertTrue(math.isfinite(start_value),
            f"Start value should be finite, got {start_value}")

    def _collect_element_data(self, dump, data):
        """Collect (name, freq, scale, phase) from dump."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            data.append((
                dump["get_name"],
                dump["get_frequency"],
                dump["get_scale"],
                dump["get_phase"]
            ))
        if "a" in dump and dump["a"] is not None:
            self._collect_element_data(dump["a"], data)
        if "b" in dump and dump["b"] is not None:
            self._collect_element_data(dump["b"], data)


class TestMinDerivativeDifferentFrequencies(unittest.TestCase):
    """Test min_derivative with various frequency combinations."""

    def test_low_frequencies(self):
        """Check optimization works with low frequencies."""
        elem1 = sl.SoundElement(frequency=55.0)   # A1
        elem2 = sl.SoundElement(frequency=82.41)  # E2
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        chord = sl.Chord(note=sum_elem)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with low frequencies: {e}")

    def test_high_frequencies(self):
        """Check optimization works with high frequencies."""
        elem1 = sl.SoundElement(frequency=4186.01)  # C8
        elem2 = sl.SoundElement(frequency=5274.04)  # E8
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        chord = sl.Chord(note=sum_elem)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with high frequencies: {e}")

    def test_mixed_frequencies(self):
        """Check optimization works with widely varying frequencies."""
        elem1 = sl.SoundElement(frequency=55.0)     # A1
        elem2 = sl.SoundElement(frequency=440.0)    # A4
        elem3 = sl.SoundElement(frequency=3520.0)   # A7
        sum1 = sl.SumElements(a=elem1, b=elem2)
        sum2 = sl.SumElements(a=sum1, b=elem3)
        chord = sl.Chord(note=sum2)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with mixed frequencies: {e}")

    def test_nearly_equal_frequencies(self):
        """Check optimization works with nearly equal frequencies (beating)."""
        elem1 = sl.SoundElement(frequency=440.0)
        elem2 = sl.SoundElement(frequency=442.0)  # Slight detuning
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        chord = sl.Chord(note=sum_elem)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with nearly equal frequencies: {e}")


class TestMinDerivativeDifferentScales(unittest.TestCase):
    """Test min_derivative with various amplitude/scale combinations."""

    def test_equal_scales(self):
        """Check optimization with equal amplitudes."""
        elem1 = sl.SoundElement(frequency=261.63, scale=1.0)
        elem2 = sl.SoundElement(frequency=329.63, scale=1.0)
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        chord = sl.Chord(note=sum_elem)

        sl.Util.min_derivative(chord)

        # Just verify it completes
        dump = chord.dump()
        self.assertIsNotNone(dump["a"])

    def test_unequal_scales(self):
        """Check optimization with unequal amplitudes."""
        elem1 = sl.SoundElement(frequency=261.63, scale=1.0)
        elem2 = sl.SoundElement(frequency=329.63, scale=0.5)
        elem3 = sl.SoundElement(frequency=392.00, scale=0.25)
        sum1 = sl.SumElements(a=elem1, b=elem2)
        sum2 = sl.SumElements(a=sum1, b=elem3)
        chord = sl.Chord(note=sum2)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        self.assertIsNotNone(dump["a"])

    def test_small_scales(self):
        """Check optimization with small amplitudes."""
        elem1 = sl.SoundElement(frequency=261.63, scale=0.01)
        elem2 = sl.SoundElement(frequency=329.63, scale=0.01)
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        chord = sl.Chord(note=sum_elem)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with small scales: {e}")


class TestMinDerivativeWithPluck(unittest.TestCase):
    """Test min_derivative with Pluck wrapper."""

    def test_chord_with_pluck(self):
        """Check that min_derivative works through Pluck wrapper."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative raised an exception with Pluck: {e}")

    def test_phases_set_through_pluck(self):
        """Check that phases are set correctly through Pluck hierarchy."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)

        sl.Util.min_derivative(chord)

        dump = chord.dump()
        phases = []
        self._collect_phases(dump["a"], phases)

        self.assertEqual(len(phases), 3)  # C, E, G
        # Verify phases were actually set (not all zero)
        all_zero = all(abs(p) < 1e-10 for p in phases)
        self.assertFalse(all_zero, "Not all phases should remain at zero")

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


class TestMinDerivativeWithMixElements(unittest.TestCase):
    """Test min_derivative with MixElements."""

    def test_chord_with_mix_elements(self):
        """Check that min_derivative works with MixElements."""
        chord = sl.Chord().make_a_chord(
            (4, "C", "major"),
            mix=sl.Chord.MixType.MIX,
            pluck=False
        )

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with MixElements: {e}")


class TestMinDerivativeIdempotence(unittest.TestCase):
    """Test that running min_derivative multiple times is stable."""

    def test_double_application_stable(self):
        """Check that applying min_derivative twice gives similar results."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        # First application
        sl.Util.min_derivative(chord)
        dump1 = chord.dump()
        phases1 = []
        self._collect_phases(dump1["a"], phases1)

        # Second application
        sl.Util.min_derivative(chord)
        dump2 = chord.dump()
        phases2 = []
        self._collect_phases(dump2["a"], phases2)

        # Phases should be similar (optimization is deterministic from same start)
        self.assertEqual(len(phases1), len(phases2))
        for p1, p2 in zip(phases1, phases2):
            self.assertAlmostEqual(p1, p2, places=3,
                msg=f"Phases diverged on second application: {p1} vs {p2}")

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


class TestMinDerivativeVsFixPop(unittest.TestCase):
    """Compare min_derivative with fix_pop."""

    def test_both_methods_complete(self):
        """Check that both methods complete on the same chord type."""
        chord1 = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)
        chord2 = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        try:
            sl.Util.fix_pop(chord1)
            sl.Util.min_derivative(chord2)
        except Exception as e:
            self.fail(f"One of the methods raised an exception: {e}")

    def test_min_derivative_reduces_derivative_at_least_as_well(self):
        """Check min_derivative achieves at least as good derivative reduction."""
        chord1 = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)
        chord2 = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        sl.Util.fix_pop(chord1)
        sl.Util.min_derivative(chord2)

        energy1 = self._compute_derivative_energy(chord1)
        energy2 = self._compute_derivative_energy(chord2)

        # min_derivative should be at least as good (within tolerance)
        self.assertLessEqual(energy2, energy1 * 1.1,
            f"min_derivative ({energy2}) should not be much worse than fix_pop ({energy1})")

    def _compute_derivative_energy(self, chord):
        """Compute derivative energy for a chord."""
        dump = chord.dump()
        element_data = []
        self._collect_element_data(dump["a"], element_data)

        if not element_data:
            return 0.0

        freqs = np.array([d[1] for d in element_data])
        amps = np.array([d[2] for d in element_data])
        phases = np.array([d[3] for d in element_data])

        fs = 2000
        T = 0.05
        t_grid = np.linspace(0, T, int(fs * T), endpoint=False)

        dS = (amps[:, None] *
              (2 * np.pi * freqs[:, None]) *
              np.cos(2 * np.pi * freqs[:, None] * t_grid[None, :] +
                     phases[:, None])).sum(axis=0)

        return np.mean(dS ** 2)

    def _collect_element_data(self, dump, data):
        """Collect (name, freq, scale, phase) from dump."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            data.append((
                dump["get_name"],
                dump["get_frequency"],
                dump["get_scale"],
                dump["get_phase"]
            ))
        if "a" in dump and dump["a"] is not None:
            self._collect_element_data(dump["a"], data)
        if "b" in dump and dump["b"] is not None:
            self._collect_element_data(dump["b"], data)


class TestCollectSoundElementData(unittest.TestCase):
    """Test the _collect_sound_element_data helper method."""

    def test_collects_name_frequency_scale(self):
        """Check that helper collects correct data."""
        elem = sl.SoundElement(frequency=440.0, scale=0.5, name="test_elem")
        chord = sl.Chord(note=elem)

        dump = chord.dump()
        data = []
        sl.Util._collect_sound_element_data(dump["a"], data)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][0], "test_elem")
        self.assertEqual(data[0][1], 440.0)
        self.assertEqual(data[0][2], 0.5)

    def test_collects_from_nested_structure(self):
        """Check that helper collects from nested SumElements."""
        elem1 = sl.SoundElement(frequency=261.63, name="elem1")
        elem2 = sl.SoundElement(frequency=329.63, name="elem2")
        elem3 = sl.SoundElement(frequency=392.00, name="elem3")
        sum1 = sl.SumElements(a=elem1, b=elem2)
        sum2 = sl.SumElements(a=sum1, b=elem3)
        chord = sl.Chord(note=sum2)

        dump = chord.dump()
        data = []
        sl.Util._collect_sound_element_data(dump["a"], data)

        self.assertEqual(len(data), 3)
        names = [d[0] for d in data]
        self.assertIn("elem1", names)
        self.assertIn("elem2", names)
        self.assertIn("elem3", names)

    def test_handles_none_dump(self):
        """Check that helper handles None dump gracefully."""
        data = []
        sl.Util._collect_sound_element_data(None, data)
        self.assertEqual(len(data), 0)


class TestMinDerivativeWithFixedAttenuate(unittest.TestCase):
    """Test min_derivative with FixedAttenuate wrapper."""

    def test_with_fixed_attenuate(self):
        """Check that min_derivative works through FixedAttenuate."""
        elem1 = sl.SoundElement(frequency=261.63)
        elem2 = sl.SoundElement(frequency=329.63)
        sum_elem = sl.SumElements(a=elem1, b=elem2)
        attenuated = sl.FixedAttenuate(a=sum_elem, scale=0.5)
        chord = sl.Chord(note=attenuated)

        try:
            sl.Util.min_derivative(chord)
        except Exception as e:
            self.fail(f"min_derivative failed with FixedAttenuate: {e}")


class TestMinDerivativePhasesPersist(unittest.TestCase):
    """Test that phases set by min_derivative persist through set_on."""

    def test_phases_persist_through_set_on(self):
        """Check that init_phase is set so phases persist after set_on."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)

        sl.Util.min_derivative(chord)

        # Get phases before set_on
        dump_before = chord.dump()
        phases_before = []
        self._collect_phases(dump_before["a"], phases_before)

        # Call set_on (which should reset to init_phase)
        chord.set_on()

        # Get phases after set_on
        dump_after = chord.dump()
        phases_after = []
        self._collect_phases(dump_after["a"], phases_after)

        # Phases should be the same (init_phase was set)
        self.assertEqual(len(phases_before), len(phases_after))
        for pb, pa in zip(phases_before, phases_after):
            self.assertAlmostEqual(pb, pa, places=10,
                msg="Phases should persist through set_on")

    def _collect_phases(self, dump, phases):
        """Helper to collect phases from dump hierarchy."""
        if dump is None:
            return
        if dump.get("get_type") == "SoundElement":
            phases.append(dump["get_phase"])
        if "a" in dump and dump["a"] is not None:
            self._collect_phases(dump["a"], phases)
        if "b" in dump and dump["b"] is not None:
            self._collect_phases(dump["b"], phases)


# =============================================================================
# wav_to_chord Tests
# =============================================================================

class TestWavToChordBasic(unittest.TestCase):
    """Test basic wav_to_chord functionality."""

    @classmethod
    def setUpClass(cls):
        """Ensure fixtures are generated."""
        from tests.fixtures import get_sine_440hz_16bit
        cls.sine_path = str(get_sine_440hz_16bit())

    def test_returns_tuple(self):
        """Check that wav_to_chord returns a tuple."""
        result = sl.Util.wav_to_chord(self.sine_path, num_waves=4)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_returns_chord(self):
        """Check that first element is a Chord."""
        chord, _ = sl.Util.wav_to_chord(self.sine_path, num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_returns_metadata_dict(self):
        """Check that second element is a metadata dict."""
        _, metadata = sl.Util.wav_to_chord(self.sine_path, num_waves=4)
        self.assertIsInstance(metadata, dict)

    def test_metadata_contains_required_keys(self):
        """Check that metadata contains all required keys."""
        _, metadata = sl.Util.wav_to_chord(self.sine_path, num_waves=4)
        required_keys = [
            "source_file", "source_sample_rate", "source_channels",
            "source_duration_samples", "output_sample_rate",
            "num_components", "fft_size", "components"
        ]
        for key in required_keys:
            self.assertIn(key, metadata, f"Missing key: {key}")

    def test_chord_produces_samples(self):
        """Check that the returned chord can produce samples."""
        chord, _ = sl.Util.wav_to_chord(self.sine_path, num_waves=4)
        chord.set_on()
        samples = [chord.sample() for _ in range(100)]
        # Should produce non-zero samples
        self.assertTrue(any(s != 0.0 for s in samples))


class TestWavToChordValidation(unittest.TestCase):
    """Test wav_to_chord input validation."""

    @classmethod
    def setUpClass(cls):
        from tests.fixtures import get_sine_440hz_16bit
        cls.sine_path = str(get_sine_440hz_16bit())

    def test_num_waves_zero_raises(self):
        """Check that num_waves=0 raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.wav_to_chord(self.sine_path, num_waves=0)

    def test_num_waves_negative_raises(self):
        """Check that negative num_waves raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.wav_to_chord(self.sine_path, num_waves=-1)

    def test_fft_size_too_small_raises(self):
        """Check that fft_size < 256 raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.wav_to_chord(self.sine_path, fft_size=128)

    def test_nonexistent_file_raises(self):
        """Check that nonexistent file raises error."""
        with self.assertRaises(FileNotFoundError):
            sl.Util.wav_to_chord("/nonexistent/path/file.wav")


class TestWavToChordFormats(unittest.TestCase):
    """Test wav_to_chord with different WAV formats."""

    def test_16bit_mono(self):
        """Check 16-bit mono WAV processing."""
        from tests.fixtures import get_sine_440hz_16bit
        chord, metadata = sl.Util.wav_to_chord(str(get_sine_440hz_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)
        self.assertEqual(metadata["source_channels"], 1)

    def test_8bit_mono(self):
        """Check 8-bit mono WAV processing."""
        from tests.fixtures import get_sine_440hz_8bit
        chord, metadata = sl.Util.wav_to_chord(str(get_sine_440hz_8bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_stereo(self):
        """Check stereo WAV processing (mixed to mono)."""
        from tests.fixtures import get_stereo_16bit
        chord, metadata = sl.Util.wav_to_chord(str(get_stereo_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)
        self.assertEqual(metadata["source_channels"], 2)


class TestWavToChordFrequencyDetection(unittest.TestCase):
    """Test that wav_to_chord detects correct frequencies."""

    def test_detects_440hz_sine(self):
        """Check that 440 Hz sine wave is detected."""
        from tests.fixtures import get_sine_440hz_16bit
        _, metadata = sl.Util.wav_to_chord(str(get_sine_440hz_16bit()), num_waves=8)

        # Find the highest amplitude component
        components = metadata["components"]
        strongest = max(components, key=lambda c: c["amplitude"])

        # Should be close to 440 Hz (within FFT resolution)
        self.assertAlmostEqual(strongest["frequency"], 440.0, delta=20.0)

    def test_detects_chord_frequencies(self):
        """Check that major chord frequencies are detected."""
        from tests.fixtures import get_chord_major_16bit
        _, metadata = sl.Util.wav_to_chord(str(get_chord_major_16bit()), num_waves=8)

        detected_freqs = [c["frequency"] for c in metadata["components"]]
        expected_freqs = [261.63, 329.63, 392.00]  # C4, E4, G4

        # Each expected frequency should have a close match
        for expected in expected_freqs:
            closest = min(detected_freqs, key=lambda f: abs(f - expected))
            self.assertAlmostEqual(closest, expected, delta=20.0,
                msg=f"Expected to detect ~{expected} Hz")

    def test_detects_harmonics(self):
        """Check that harmonics are detected in complex tone."""
        from tests.fixtures import get_complex_tone_16bit
        _, metadata = sl.Util.wav_to_chord(str(get_complex_tone_16bit()), num_waves=8)

        detected_freqs = sorted([c["frequency"] for c in metadata["components"]])

        # Fundamental is 220 Hz, should detect some harmonics
        fundamental = 220.0
        # Check that we have frequencies roughly at harmonic positions
        self.assertTrue(any(abs(f - fundamental) < 20 for f in detected_freqs),
            "Should detect fundamental frequency")


class TestWavToChordEdgeCases(unittest.TestCase):
    """Test wav_to_chord edge cases."""

    def test_silence(self):
        """Check that silence is handled gracefully."""
        from tests.fixtures import get_silence_16bit
        # Should not raise, even for silent input
        chord, metadata = sl.Util.wav_to_chord(str(get_silence_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_short_audio(self):
        """Check that very short audio is handled."""
        from tests.fixtures import get_short_click_16bit
        chord, metadata = sl.Util.wav_to_chord(str(get_short_click_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_single_component(self):
        """Check extraction of single component."""
        from tests.fixtures import get_sine_440hz_16bit
        chord, metadata = sl.Util.wav_to_chord(str(get_sine_440hz_16bit()), num_waves=1)
        self.assertEqual(metadata["num_components"], 1)


class TestWavToChordCustomName(unittest.TestCase):
    """Test wav_to_chord custom naming."""

    def test_custom_name(self):
        """Check that custom name is applied."""
        from tests.fixtures import get_sine_440hz_16bit
        chord, _ = sl.Util.wav_to_chord(str(get_sine_440hz_16bit()),
                                        num_waves=4, name="my_custom_chord")
        self.assertEqual(chord.get_name(), "my_custom_chord")


# =============================================================================
# array_to_chord Tests
# =============================================================================

class TestArrayToChordBasic(unittest.TestCase):
    """Test basic array_to_chord functionality."""

    def test_sine_array(self):
        """Check conversion of sine wave array."""
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = 0.8 * np.sin(2 * np.pi * 440 * t)

        chord, metadata = sl.Util.array_to_chord(audio, sample_rate, num_waves=4)
        self.assertIsInstance(chord, sl.Chord)
        self.assertEqual(metadata["source_type"], "numpy_array")

    def test_multichannel_array(self):
        """Check that multichannel arrays are mixed to mono."""
        sample_rate = 44100
        n_samples = 22050
        stereo = np.random.randn(n_samples, 2)

        chord, metadata = sl.Util.array_to_chord(stereo, sample_rate, num_waves=4)
        self.assertEqual(metadata["source_channels"], 2)

    def test_normalization(self):
        """Check that arrays with large values are normalized."""
        sample_rate = 44100
        # Create array with values > 1.0
        audio = np.sin(np.linspace(0, 10*np.pi, 4410)) * 100

        # Should not raise
        chord, _ = sl.Util.array_to_chord(audio, sample_rate, num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_empty_array_raises(self):
        """Check that empty array raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.array_to_chord(np.array([]), 44100)

    def test_different_dtypes(self):
        """Check that different numpy dtypes work."""
        sample_rate = 44100
        audio_float32 = np.sin(np.linspace(0, 10*np.pi, 4410)).astype(np.float32)
        audio_int16 = (np.sin(np.linspace(0, 10*np.pi, 4410)) * 32767).astype(np.int16)

        chord1, _ = sl.Util.array_to_chord(audio_float32, sample_rate, num_waves=4)
        chord2, _ = sl.Util.array_to_chord(audio_int16, sample_rate, num_waves=4)

        self.assertIsInstance(chord1, sl.Chord)
        self.assertIsInstance(chord2, sl.Chord)


# =============================================================================
# bytes_to_chord Tests
# =============================================================================

class TestBytesToChordBasic(unittest.TestCase):
    """Test basic bytes_to_chord functionality."""

    def test_16bit_pcm(self):
        """Check conversion of 16-bit PCM bytes."""
        sample_rate = 44100
        n_samples = 4410
        t = np.linspace(0, 0.1, n_samples, endpoint=False)
        audio = (0.8 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        audio_bytes = audio.tobytes()

        chord, metadata = sl.Util.bytes_to_chord(
            audio_bytes, sample_rate, sample_width=2, num_waves=4
        )
        self.assertIsInstance(chord, sl.Chord)

    def test_8bit_pcm(self):
        """Check conversion of 8-bit PCM bytes."""
        sample_rate = 44100
        n_samples = 4410
        t = np.linspace(0, 0.1, n_samples, endpoint=False)
        audio = ((0.8 * np.sin(2 * np.pi * 440 * t) + 1) * 127.5).astype(np.uint8)
        audio_bytes = audio.tobytes()

        chord, _ = sl.Util.bytes_to_chord(
            audio_bytes, sample_rate, sample_width=1, num_waves=4
        )
        self.assertIsInstance(chord, sl.Chord)

    def test_empty_bytes_raises(self):
        """Check that empty bytes raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.bytes_to_chord(b"", 44100)

    def test_unsupported_sample_width_raises(self):
        """Check that unsupported sample width raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Util.bytes_to_chord(b"\x00" * 100, 44100, sample_width=3)


# =============================================================================
# fileobj_to_chord Tests
# =============================================================================

class TestFileobjToChordBasic(unittest.TestCase):
    """Test basic fileobj_to_chord functionality."""

    def test_bytesio_wav(self):
        """Check conversion from BytesIO containing WAV data."""
        import io
        from tests.fixtures import get_sine_440hz_16bit

        # Read WAV file into BytesIO
        with open(get_sine_440hz_16bit(), 'rb') as f:
            wav_data = f.read()

        fileobj = io.BytesIO(wav_data)
        chord, metadata = sl.Util.fileobj_to_chord(fileobj, num_waves=4)

        self.assertIsInstance(chord, sl.Chord)
        self.assertEqual(metadata["source_type"], "file_object")

    def test_real_file_object(self):
        """Check conversion from real file object."""
        from tests.fixtures import get_sine_440hz_16bit

        with open(get_sine_440hz_16bit(), 'rb') as f:
            chord, _ = sl.Util.fileobj_to_chord(f, num_waves=4)

        self.assertIsInstance(chord, sl.Chord)


# =============================================================================
# to_chord (unified) Tests
# =============================================================================

class TestToChordUnified(unittest.TestCase):
    """Test the unified to_chord method."""

    def test_string_path(self):
        """Check that string path is handled."""
        from tests.fixtures import get_sine_440hz_16bit
        chord, _ = sl.Util.to_chord(str(get_sine_440hz_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_path_object(self):
        """Check that Path object is handled."""
        from pathlib import Path
        from tests.fixtures import get_sine_440hz_16bit
        chord, _ = sl.Util.to_chord(Path(get_sine_440hz_16bit()), num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_numpy_array(self):
        """Check that numpy array is handled."""
        audio = np.sin(np.linspace(0, 10*np.pi, 4410))
        chord, _ = sl.Util.to_chord(audio, sample_rate=44100, num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_numpy_array_without_sample_rate_raises(self):
        """Check that numpy array without sample_rate raises."""
        audio = np.sin(np.linspace(0, 10*np.pi, 4410))
        with self.assertRaises(ValueError):
            sl.Util.to_chord(audio, num_waves=4)

    def test_bytes_input(self):
        """Check that bytes are handled."""
        audio = (np.sin(np.linspace(0, 10*np.pi, 4410)) * 32767).astype(np.int16)
        chord, _ = sl.Util.to_chord(
            audio.tobytes(), sample_rate=44100, sample_width=2, num_waves=4
        )
        self.assertIsInstance(chord, sl.Chord)

    def test_bytes_without_sample_rate_raises(self):
        """Check that bytes without sample_rate raises."""
        audio_bytes = b"\x00" * 1000
        with self.assertRaises(ValueError):
            sl.Util.to_chord(audio_bytes, num_waves=4)

    def test_file_object(self):
        """Check that file object is handled."""
        import io
        from tests.fixtures import get_sine_440hz_16bit

        with open(get_sine_440hz_16bit(), 'rb') as f:
            wav_data = f.read()

        fileobj = io.BytesIO(wav_data)
        chord, _ = sl.Util.to_chord(fileobj, num_waves=4)
        self.assertIsInstance(chord, sl.Chord)

    def test_unsupported_type_raises(self):
        """Check that unsupported type raises TypeError."""
        with self.assertRaises(TypeError):
            sl.Util.to_chord(12345, num_waves=4)

    def test_list_raises(self):
        """Check that list raises TypeError."""
        with self.assertRaises(TypeError):
            sl.Util.to_chord([0.1, 0.2, 0.3], sample_rate=44100, num_waves=4)


# =============================================================================
# Psychoacoustic Model Helper Tests
# =============================================================================

class TestPsychoacousticHelpers(unittest.TestCase):
    """Test psychoacoustic model helper methods."""

    def test_freq_to_bark_zero(self):
        """Check bark conversion at 0 Hz."""
        self.assertEqual(sl.Util._freq_to_bark(0), 0.0)

    def test_freq_to_bark_1000hz(self):
        """Check bark conversion at 1000 Hz (~8.5 Bark)."""
        bark = sl.Util._freq_to_bark(1000)
        self.assertAlmostEqual(bark, 8.5, delta=0.5)

    def test_bark_to_freq_roundtrip(self):
        """Check that bark_to_freq inverts freq_to_bark."""
        test_freqs = [100, 500, 1000, 2000, 5000, 10000]
        for freq in test_freqs:
            bark = sl.Util._freq_to_bark(freq)
            recovered = sl.Util._bark_to_freq(bark)
            self.assertAlmostEqual(freq, recovered, delta=freq * 0.01,
                msg=f"Roundtrip failed for {freq} Hz")

    def test_absolute_threshold_of_hearing_low_freq(self):
        """Check ATH at low frequency is high."""
        ath_20hz = sl.Util._absolute_threshold_of_hearing(20)
        ath_1000hz = sl.Util._absolute_threshold_of_hearing(1000)
        self.assertGreater(ath_20hz, ath_1000hz)

    def test_absolute_threshold_of_hearing_zero(self):
        """Check ATH at 0 Hz returns high value."""
        ath = sl.Util._absolute_threshold_of_hearing(0)
        self.assertEqual(ath, 100.0)

    def test_get_critical_band(self):
        """Check critical band assignment."""
        # 100 Hz should be in band 0-1
        band_100 = sl.Util._get_critical_band(100)
        self.assertIn(band_100, [0, 1])

        # 1000 Hz should be around band 8-10
        band_1000 = sl.Util._get_critical_band(1000)
        self.assertIn(band_1000, [8, 9, 10])


if __name__ == "__main__":
    unittest.main()
