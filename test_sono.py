import unittest
import math
import sono as sl


class TestSoundElementDefaults(unittest.TestCase):
    """Test SoundElement default values after instantiation without arguments."""

    def test_frequency_is_float_440(self):
        """Check that frequency is a float set to 440.0."""
        elem = sl.SoundElement()
        self.assertIsInstance(elem._frequency, float)
        self.assertEqual(elem._frequency, 440.0)

    def test_sample_rate_is_int_44100(self):
        """Check that sample_rate is an int set to 44100."""
        elem = sl.SoundElement()
        self.assertIsInstance(elem._sample_rate, int)
        self.assertEqual(elem._sample_rate, 44100)

    def test_name_includes_sound_element_and_unique_id(self):
        """Check that name includes 'SoundElement' and a unique numerical identifier."""
        elem = sl.SoundElement()
        self.assertIsInstance(elem._name, str)
        self.assertIn("SoundElement", elem._name)
        # Name format is "SoundElement_<id>"
        parts = elem._name.split("_")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "SoundElement")
        self.assertTrue(parts[1].isdigit())

    def test_name_is_unique(self):
        """Check that each instance gets a unique name."""
        elem1 = sl.SoundElement()
        elem2 = sl.SoundElement()
        self.assertNotEqual(elem1._name, elem2._name)

    def test_phase_is_float_zero(self):
        """Check that phase is a float set to 0.0."""
        elem = sl.SoundElement()
        self.assertIsInstance(elem._phase, float)
        self.assertEqual(elem._phase, 0.0)

    def test_scale_is_float_one(self):
        """Check that scale is a float set to 1.0."""
        elem = sl.SoundElement()
        self.assertIsInstance(elem._scale, float)
        self.assertEqual(elem._scale, 1.0)

    def test_sample_without_set_on_returns_zero(self):
        """Check that sample() returns 0.0 when set_on() has not been called."""
        elem = sl.SoundElement()
        # Call sample multiple times without set_on()
        for _ in range(100):
            sample = elem.sample()
            self.assertEqual(sample, 0.0)

    def test_sample_with_set_on_returns_sine_wave(self):
        """Check that sample() returns correct sine wave values after set_on()."""
        elem = sl.SoundElement()  # freq=440, sample_rate=44100, phase=0, scale=1
        elem.set_on()

        frequency = 440.0
        sample_rate = 44100
        phase_increment = (frequency / sample_rate) * 2 * math.pi

        # First sample at phase 0 should be sin(0) = 0.0
        phase = 0.0
        for i in range(100):
            expected = math.sin(phase)
            actual = elem.sample()
            self.assertAlmostEqual(actual, expected, places=10,
                msg=f"Sample {i}: expected {expected}, got {actual}")
            phase += phase_increment

    def test_sample_with_phase_offset(self):
        """Check that sample() with a phase offset produces correctly shifted sine wave."""
        initial_phase = math.pi / 4  # 45 degrees
        elem = sl.SoundElement(phase=initial_phase)
        elem.set_on()

        frequency = 440.0
        sample_rate = 44100
        phase_increment = (frequency / sample_rate) * 2 * math.pi

        # First sample should be sin(pi/4) ≈ 0.707
        phase = initial_phase
        for i in range(100):
            expected = math.sin(phase)
            actual = elem.sample()
            self.assertAlmostEqual(actual, expected, places=10,
                msg=f"Sample {i}: expected {expected}, got {actual}")
            phase += phase_increment


class TestSoundElementValidation(unittest.TestCase):
    """Test SoundElement constructor validation."""

    def test_zero_frequency_raises_value_error(self):
        """Check that frequency=0 raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.SoundElement(frequency=0)
        self.assertIn("Frequency must be positive", str(ctx.exception))

    def test_negative_frequency_raises_value_error(self):
        """Check that negative frequency raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.SoundElement(frequency=-100)
        self.assertIn("Frequency must be positive", str(ctx.exception))

    def test_zero_sample_rate_raises_value_error(self):
        """Check that sample_rate=0 raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.SoundElement(sample_rate=0)
        self.assertIn("Sample rate must be positive", str(ctx.exception))

    def test_negative_sample_rate_raises_value_error(self):
        """Check that negative sample_rate raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.SoundElement(sample_rate=-44100)
        self.assertIn("Sample rate must be positive", str(ctx.exception))


class TestSoundElementCustomArgs(unittest.TestCase):
    """Test SoundElement with custom constructor arguments."""

    def test_custom_frequency(self):
        """Check that custom frequency is set correctly."""
        elem = sl.SoundElement(frequency=880.0)
        self.assertEqual(elem.get_frequency(), 880.0)

    def test_custom_sample_rate(self):
        """Check that custom sample_rate is set correctly."""
        elem = sl.SoundElement(sample_rate=48000)
        self.assertEqual(elem.get_sample_rate(), 48000)

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.SoundElement(name="my_oscillator")
        self.assertEqual(elem.get_name(), "my_oscillator")

    def test_custom_phase(self):
        """Check that custom phase is set correctly."""
        elem = sl.SoundElement(phase=math.pi / 2)
        self.assertEqual(elem.get_phase(), math.pi / 2)

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.SoundElement(scale=0.5)
        self.assertEqual(elem.get_scale(), 0.5)

    def test_all_custom_args(self):
        """Check that all custom arguments are set correctly."""
        elem = sl.SoundElement(
            frequency=220.0,
            sample_rate=48000,
            name="test_elem",
            phase=math.pi,
            scale=0.75
        )
        self.assertEqual(elem.get_frequency(), 220.0)
        self.assertEqual(elem.get_sample_rate(), 48000)
        self.assertEqual(elem.get_name(), "test_elem")
        self.assertEqual(elem.get_phase(), math.pi)
        self.assertEqual(elem.get_scale(), 0.75)


class TestSoundElementSetters(unittest.TestCase):
    """Test SoundElement setter methods."""

    def test_set_frequency(self):
        """Check that set_frequency updates the frequency."""
        elem = sl.SoundElement()
        elem.set_frequency(880.0)
        self.assertEqual(elem.get_frequency(), 880.0)

    def test_set_frequency_invalid_raises_error(self):
        """Check that set_frequency with invalid value raises ValueError."""
        elem = sl.SoundElement()
        with self.assertRaises(ValueError):
            elem.set_frequency(0)
        with self.assertRaises(ValueError):
            elem.set_frequency(-100)

    def test_set_sample_rate(self):
        """Check that set_sample_rate updates the sample rate."""
        elem = sl.SoundElement()
        elem.set_sample_rate(48000)
        self.assertEqual(elem.get_sample_rate(), 48000)

    def test_set_sample_rate_invalid_raises_error(self):
        """Check that set_sample_rate with invalid value raises ValueError."""
        elem = sl.SoundElement()
        with self.assertRaises(ValueError):
            elem.set_sample_rate(0)
        with self.assertRaises(ValueError):
            elem.set_sample_rate(-1000)

    def test_set_phase(self):
        """Check that set_phase updates the phase."""
        elem = sl.SoundElement()
        elem.set_phase(math.pi / 2)
        self.assertEqual(elem.get_phase(), math.pi / 2)

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.SoundElement()
        elem.set_scale(0.5)
        self.assertEqual(elem.get_scale(), 0.5)


class TestSoundElementOnOff(unittest.TestCase):
    """Test SoundElement set_on and set_off behavior."""

    def test_set_on_enables_output(self):
        """Check that set_on enables non-zero output."""
        elem = sl.SoundElement(phase=math.pi / 2)  # Start at peak
        elem.set_on()
        sample = elem.sample()
        self.assertNotEqual(sample, 0.0)
        self.assertAlmostEqual(sample, 1.0, places=10)

    def test_set_off_disables_output_after_settling(self):
        """Check that set_off eventually produces zero output after settling."""
        elem = sl.SoundElement()
        elem.set_on()
        # Generate some samples
        for _ in range(10):
            elem.sample()
        elem.set_off()
        # After set_off, it should settle to zero (may take a few samples)
        for _ in range(1000):
            sample = elem.sample()
        self.assertEqual(sample, 0.0)

    def test_set_on_resets_phase_to_initial(self):
        """Check that set_on resets phase to initial phase."""
        initial_phase = math.pi / 4
        elem = sl.SoundElement(phase=initial_phase)
        elem.set_on()
        # Generate many samples to advance phase
        for _ in range(1000):
            elem.sample()
        # Phase should have advanced
        self.assertNotEqual(elem.get_phase(), initial_phase)
        # Call set_on again
        elem.set_on()
        # Phase should reset to initial
        self.assertEqual(elem.get_phase(), initial_phase)


class TestSoundElementScale(unittest.TestCase):
    """Test SoundElement amplitude scaling."""

    def test_scale_affects_amplitude(self):
        """Check that scale factor affects sample amplitude."""
        elem1 = sl.SoundElement(phase=math.pi / 2, scale=1.0)
        elem2 = sl.SoundElement(phase=math.pi / 2, scale=0.5)
        elem1.set_on()
        elem2.set_on()

        sample1 = elem1.sample()
        sample2 = elem2.sample()

        self.assertAlmostEqual(sample1, 1.0, places=10)
        self.assertAlmostEqual(sample2, 0.5, places=10)
        self.assertAlmostEqual(sample2, sample1 * 0.5, places=10)

    def test_scale_zero_produces_zero_output(self):
        """Check that scale=0 produces zero output."""
        elem = sl.SoundElement(scale=0.0)
        elem.set_on()
        for _ in range(100):
            self.assertEqual(elem.sample(), 0.0)


class TestSoundElementFrequencies(unittest.TestCase):
    """Test SoundElement with different frequencies."""

    def test_higher_frequency_shorter_period(self):
        """Check that higher frequency produces shorter period."""
        elem_440 = sl.SoundElement(frequency=440.0)
        elem_880 = sl.SoundElement(frequency=880.0)
        elem_440.set_on()
        elem_880.set_on()

        # Count samples to first positive-to-negative zero crossing
        def samples_to_half_period(elem):
            prev = elem.sample()
            count = 1
            for _ in range(10000):
                curr = elem.sample()
                count += 1
                if prev > 0 and curr <= 0:
                    return count
                prev = curr
            return -1

        period_440 = samples_to_half_period(elem_440)
        period_880 = samples_to_half_period(elem_880)

        # 880 Hz should have half the period of 440 Hz (delta=2 for sampling variation)
        self.assertAlmostEqual(period_440, period_880 * 2, delta=2)

    def test_frequency_change_affects_output(self):
        """Check that changing frequency affects subsequent samples."""
        elem = sl.SoundElement(frequency=440.0)
        elem.set_on()

        # Collect samples at 440 Hz
        samples_440 = [elem.sample() for _ in range(100)]

        # Change to 880 Hz
        elem.set_frequency(880.0)
        elem.set_on()  # Reset phase

        # Collect samples at 880 Hz
        samples_880 = [elem.sample() for _ in range(100)]

        # The patterns should be different (880 Hz oscillates faster)
        # Check that sample 50 is different
        self.assertNotAlmostEqual(samples_440[50], samples_880[50], places=5)


class TestSoundElementTriangle(unittest.TestCase):
    """Test SoundElement triangle wave generation."""

    def test_triangle_without_set_on_returns_zero(self):
        """Check that triangle() returns 0.0 when not activated."""
        elem = sl.SoundElement()
        for _ in range(100):
            self.assertEqual(elem.triangle(), 0.0)

    def test_triangle_with_set_on_produces_output(self):
        """Check that triangle() produces non-zero output after set_on."""
        elem = sl.SoundElement(phase=math.pi / 4)
        elem.set_on()
        sample = elem.triangle()
        self.assertNotEqual(sample, 0.0)

    def test_triangle_range(self):
        """Check that triangle wave stays within [-1, 1] range."""
        elem = sl.SoundElement()
        elem.set_on()
        for _ in range(1000):
            sample = elem.triangle()
            self.assertGreaterEqual(sample, -1.0)
            self.assertLessEqual(sample, 1.0)


class TestSoundElementMIDI(unittest.TestCase):
    """Test SoundElement MIDI-related methods."""

    def test_midi_note_a4_is_440(self):
        """Check that MIDI note 69 (A4) produces 440 Hz."""
        freq = sl.SoundElement.midi_note(69)
        self.assertAlmostEqual(freq, 440.0, places=10)

    def test_midi_note_a5_is_880(self):
        """Check that MIDI note 81 (A5) produces 880 Hz."""
        freq = sl.SoundElement.midi_note(81)
        self.assertAlmostEqual(freq, 880.0, places=10)

    def test_midi_note_a3_is_220(self):
        """Check that MIDI note 57 (A3) produces 220 Hz."""
        freq = sl.SoundElement.midi_note(57)
        self.assertAlmostEqual(freq, 220.0, places=10)

    def test_midi_key_from_freq_440_is_69(self):
        """Check that 440 Hz returns MIDI key 69."""
        key = sl.SoundElement.midi_key_from_freq(440.0)
        self.assertAlmostEqual(key, 69.0, places=10)

    def test_midi_key_from_freq_880_is_81(self):
        """Check that 880 Hz returns MIDI key 81."""
        key = sl.SoundElement.midi_key_from_freq(880.0)
        self.assertAlmostEqual(key, 81.0, places=10)

    def test_midi_key_from_freq_invalid_raises_error(self):
        """Check that invalid frequency raises ValueError."""
        with self.assertRaises(ValueError):
            sl.SoundElement.midi_key_from_freq(0)
        with self.assertRaises(ValueError):
            sl.SoundElement.midi_key_from_freq(-100)

    def test_set_frequency_to_midi_note(self):
        """Check that set_frequency_to_midi_note sets correct frequency."""
        elem = sl.SoundElement()
        result = elem.set_frequency_to_midi_note(69)
        self.assertAlmostEqual(result, 440.0, places=10)
        self.assertAlmostEqual(elem.get_frequency(), 440.0, places=10)

    def test_set_frequency_to_nearest_midi_note(self):
        """Check that set_frequency_to_nearest_midi_note quantizes correctly."""
        elem = sl.SoundElement()
        # 445 Hz is close to A4 (440 Hz)
        result = elem.set_frequency_to_nearest_midi_note(445.0)
        self.assertAlmostEqual(result, 440.0, places=5)

    def test_set_frequency_to_nearest_midi_note_invalid_raises_error(self):
        """Check that invalid frequency raises ValueError."""
        elem = sl.SoundElement()
        with self.assertRaises(ValueError):
            elem.set_frequency_to_nearest_midi_note(0)


class TestSoundElementDump(unittest.TestCase):
    """Test SoundElement dump method."""

    def test_dump_contains_all_properties(self):
        """Check that dump returns all expected properties."""
        elem = sl.SoundElement(
            frequency=880.0,
            sample_rate=48000,
            name="test_dump",
            phase=math.pi / 4,
            scale=0.75
        )
        dump = elem.dump()

        self.assertIn("get_name", dump)
        self.assertIn("get_frequency", dump)
        self.assertIn("get_phase", dump)
        self.assertIn("get_type", dump)
        self.assertIn("get_sample_rate", dump)
        self.assertIn("get_scale", dump)

    def test_dump_values_match(self):
        """Check that dump values match the element's properties."""
        elem = sl.SoundElement(
            frequency=880.0,
            sample_rate=48000,
            name="test_dump",
            phase=math.pi / 4,
            scale=0.75
        )
        dump = elem.dump()

        self.assertEqual(dump["get_name"], "test_dump")
        self.assertEqual(dump["get_frequency"], 880.0)
        self.assertEqual(dump["get_phase"], math.pi / 4)
        self.assertEqual(dump["get_type"], "SoundElement")
        self.assertEqual(dump["get_sample_rate"], 48000)
        self.assertEqual(dump["get_scale"], 0.75)


class TestSoundElementMsg(unittest.TestCase):
    """Test SoundElement msg method for control messages."""

    def test_msg_get_frequency(self):
        """Check that msg can get frequency."""
        elem = sl.SoundElement(frequency=880.0, name="test")
        result = elem.msg({"test": {"get_frequency": []}})
        self.assertEqual(result["test"]["get_frequency"], 880.0)

    def test_msg_set_frequency(self):
        """Check that msg can set frequency."""
        elem = sl.SoundElement(name="test")
        elem.msg({"test": {"set_frequency": [880.0]}})
        self.assertEqual(elem.get_frequency(), 880.0)

    def test_msg_get_phase(self):
        """Check that msg can get phase."""
        elem = sl.SoundElement(phase=math.pi / 2, name="test")
        result = elem.msg({"test": {"get_phase": []}})
        self.assertEqual(result["test"]["get_phase"], math.pi / 2)

    def test_msg_set_phase(self):
        """Check that msg can set phase."""
        elem = sl.SoundElement(name="test")
        elem.msg({"test": {"set_phase": [math.pi]}})
        self.assertEqual(elem.get_phase(), math.pi)

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.SoundElement(scale=0.5, name="test")
        result = elem.msg({"test": {"get_scale": []}})
        self.assertEqual(result["test"]["get_scale"], 0.5)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.SoundElement(name="test")
        elem.msg({"test": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_set_on_and_sample(self):
        """Check that msg can activate and sample."""
        elem = sl.SoundElement(phase=math.pi / 2, name="test")
        elem.msg({"test": {"set_on": []}})
        result = elem.msg({"test": {"sample": []}})
        self.assertAlmostEqual(result["test"]["sample"], 1.0, places=10)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.SoundElement(name="test")
        result = elem.msg({"other_name": {"set_frequency": [880.0]}})
        # Frequency should remain unchanged
        self.assertEqual(elem.get_frequency(), 440.0)


class TestSoundElementGetType(unittest.TestCase):
    """Test SoundElement get_type method."""

    def test_get_type_returns_sound_element(self):
        """Check that get_type returns 'SoundElement'."""
        elem = sl.SoundElement()
        self.assertEqual(elem.get_type(), "SoundElement")


# =============================================================================
# MultiplyElements Tests
# =============================================================================

class TestMultiplyElementsDefaults(unittest.TestCase):
    """Test MultiplyElements default values after instantiation without arguments."""

    def test_a_is_none_by_default(self):
        """Check that _a is None when not provided."""
        elem = sl.MultiplyElements()
        self.assertIsNone(elem._a)

    def test_b_is_none_by_default(self):
        """Check that _b is None when not provided."""
        elem = sl.MultiplyElements()
        self.assertIsNone(elem._b)

    def test_scale_is_float_one(self):
        """Check that scale is a float set to 1.0."""
        elem = sl.MultiplyElements()
        self.assertIsInstance(elem._scale, float)
        self.assertEqual(elem._scale, 1.0)

    def test_name_includes_multiply_elements_and_unique_id(self):
        """Check that name includes 'MultiplyElements' and a unique identifier."""
        elem = sl.MultiplyElements()
        self.assertIsInstance(elem._name, str)
        self.assertIn("MultiplyElements", elem._name)
        parts = elem._name.split("_")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "MultiplyElements")
        self.assertTrue(parts[1].isdigit())

    def test_name_is_unique(self):
        """Check that each instance gets a unique name."""
        elem1 = sl.MultiplyElements()
        elem2 = sl.MultiplyElements()
        self.assertNotEqual(elem1._name, elem2._name)

    def test_get_type_returns_multiply_elements(self):
        """Check that get_type returns 'MultiplyElements'."""
        elem = sl.MultiplyElements()
        self.assertEqual(elem.get_type(), "MultiplyElements")


class TestMultiplyElementsCustomArgs(unittest.TestCase):
    """Test MultiplyElements with custom constructor arguments."""

    def test_custom_a_element(self):
        """Check that custom 'a' element is set correctly."""
        sound = sl.SoundElement()
        elem = sl.MultiplyElements(a=sound)
        self.assertIs(elem._a, sound)

    def test_custom_b_element(self):
        """Check that custom 'b' element is set correctly."""
        sound = sl.SoundElement()
        elem = sl.MultiplyElements(b=sound)
        self.assertIs(elem._b, sound)

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.MultiplyElements(name="my_multiplier")
        self.assertEqual(elem.get_name(), "my_multiplier")

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.MultiplyElements(scale=0.5)
        self.assertEqual(elem.get_scale(), 0.5)

    def test_all_custom_args(self):
        """Check that all custom arguments are set correctly."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MultiplyElements(
            a=sound_a,
            b=sound_b,
            name="test_mult",
            scale=0.75
        )
        self.assertIs(elem._a, sound_a)
        self.assertIs(elem._b, sound_b)
        self.assertEqual(elem.get_name(), "test_mult")
        self.assertEqual(elem.get_scale(), 0.75)


class TestMultiplyElementsSetters(unittest.TestCase):
    """Test MultiplyElements setter methods."""

    def test_set_a_with_sound_element(self):
        """Check that set_a accepts SoundElement."""
        elem = sl.MultiplyElements()
        sound = sl.SoundElement()
        elem.set_a(sound)
        self.assertIs(elem._a, sound)

    def test_set_b_with_sound_element(self):
        """Check that set_b accepts SoundElement."""
        elem = sl.MultiplyElements()
        sound = sl.SoundElement()
        elem.set_b(sound)
        self.assertIs(elem._b, sound)

    def test_set_a_with_multiply_elements(self):
        """Check that set_a accepts MultiplyElements (nesting)."""
        inner = sl.MultiplyElements()
        outer = sl.MultiplyElements()
        outer.set_a(inner)
        self.assertIs(outer._a, inner)

    def test_set_b_with_multiply_elements(self):
        """Check that set_b accepts MultiplyElements (nesting)."""
        inner = sl.MultiplyElements()
        outer = sl.MultiplyElements()
        outer.set_b(inner)
        self.assertIs(outer._b, inner)

    def test_set_a_invalid_raises_error(self):
        """Check that set_a with invalid object raises ValueError."""
        elem = sl.MultiplyElements()
        with self.assertRaises(ValueError) as ctx:
            elem.set_a("invalid")
        self.assertIn("no attribute sample()", str(ctx.exception))

    def test_set_b_invalid_raises_error(self):
        """Check that set_b with invalid object raises ValueError."""
        elem = sl.MultiplyElements()
        with self.assertRaises(ValueError) as ctx:
            elem.set_b(12345)
        self.assertIn("no attribute sample()", str(ctx.exception))

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.MultiplyElements()
        elem.set_scale(0.25)
        self.assertEqual(elem.get_scale(), 0.25)


class TestMultiplyElementsGetInstances(unittest.TestCase):
    """Test MultiplyElements get_instances method."""

    def test_get_instances_both_none(self):
        """Check get_instances when both a and b are None."""
        elem = sl.MultiplyElements()
        self.assertEqual(elem.get_instances(), (None, None))

    def test_get_instances_a_only(self):
        """Check get_instances when only a is set."""
        sound = sl.SoundElement(name="sound_a")
        elem = sl.MultiplyElements(a=sound)
        self.assertEqual(elem.get_instances(), ("sound_a", None))

    def test_get_instances_b_only(self):
        """Check get_instances when only b is set."""
        sound = sl.SoundElement(name="sound_b")
        elem = sl.MultiplyElements(b=sound)
        self.assertEqual(elem.get_instances(), (None, "sound_b"))

    def test_get_instances_both_set(self):
        """Check get_instances when both a and b are set."""
        sound_a = sl.SoundElement(name="first")
        sound_b = sl.SoundElement(name="second")
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)
        self.assertEqual(elem.get_instances(), ("first", "second"))


class TestMultiplyElementsSample(unittest.TestCase):
    """Test MultiplyElements sample method."""

    def test_sample_with_no_elements_returns_zero(self):
        """Check that sample() returns 0.0 when no elements are set."""
        elem = sl.MultiplyElements()
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_only_a_returns_zero(self):
        """Check that sample() returns 0.0 when only a is set (b=0)."""
        sound = sl.SoundElement(phase=math.pi / 2)  # Peak = 1.0
        sound.set_on()
        elem = sl.MultiplyElements(a=sound)
        # a * 0 = 0
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_only_b_returns_zero(self):
        """Check that sample() returns 0.0 when only b is set (a=0)."""
        sound = sl.SoundElement(phase=math.pi / 2)  # Peak = 1.0
        sound.set_on()
        elem = sl.MultiplyElements(b=sound)
        # 0 * b = 0
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_multiplies_two_elements(self):
        """Check that sample() correctly multiplies two elements."""
        # Create two elements at peak (sin(pi/2) = 1.0)
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)
        # 1.0 * 1.0 * 1.0 (scale) = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_with_scale(self):
        """Check that sample() applies scale correctly."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, scale=0.5)
        # 1.0 * 1.0 * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_with_different_values(self):
        """Check sample() with elements at different phases."""
        # sin(pi/6) ≈ 0.5, sin(pi/2) = 1.0
        sound_a = sl.SoundElement(phase=math.pi / 6)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)
        expected = math.sin(math.pi / 6) * math.sin(math.pi / 2)
        self.assertAlmostEqual(elem.sample(), expected, places=10)

    def test_sample_produces_ring_modulation(self):
        """Check that multiplying two different frequencies produces ring modulation."""
        # Two different frequencies
        sound_a = sl.SoundElement(frequency=440.0)
        sound_b = sl.SoundElement(frequency=880.0)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)

        # Collect samples and verify they vary (ring modulation effect)
        samples = [elem.sample() for _ in range(100)]
        # Should have both positive and negative values
        has_positive = any(s > 0.1 for s in samples)
        has_negative = any(s < -0.1 for s in samples)
        self.assertTrue(has_positive)
        self.assertTrue(has_negative)


class TestMultiplyElementsOnOff(unittest.TestCase):
    """Test MultiplyElements set_on and set_off behavior."""

    def test_set_on_activates_both_elements(self):
        """Check that set_on activates both child elements."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)

        # Before set_on, children are off
        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

        elem.set_on()

        # After set_on, children should be on
        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

    def test_set_off_deactivates_both_elements(self):
        """Check that set_off deactivates both child elements."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)

        elem.set_on()
        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

        elem.set_off()
        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

    def test_set_on_with_no_elements_does_not_crash(self):
        """Check that set_on with no elements doesn't crash."""
        elem = sl.MultiplyElements()
        elem.set_on()  # Should not raise

    def test_set_off_with_no_elements_does_not_crash(self):
        """Check that set_off with no elements doesn't crash."""
        elem = sl.MultiplyElements()
        elem.set_off()  # Should not raise


class TestMultiplyElementsDump(unittest.TestCase):
    """Test MultiplyElements dump method."""

    def test_dump_contains_all_properties(self):
        """Check that dump returns all expected properties."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="test_mult", scale=0.75)
        dump = elem.dump()

        self.assertIn("get_name", dump)
        self.assertIn("get_type", dump)
        self.assertIn("get_scale", dump)
        self.assertIn("a", dump)
        self.assertIn("b", dump)

    def test_dump_values_match(self):
        """Check that dump values match the element's properties."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="test_mult", scale=0.75)
        dump = elem.dump()

        self.assertEqual(dump["get_name"], "test_mult")
        self.assertEqual(dump["get_type"], "MultiplyElements")
        self.assertEqual(dump["get_scale"], 0.75)
        self.assertIsNotNone(dump["a"])
        self.assertIsNotNone(dump["b"])

    def test_dump_with_no_elements(self):
        """Check dump when no child elements are set."""
        elem = sl.MultiplyElements(name="empty_mult")
        dump = elem.dump()

        self.assertEqual(dump["get_name"], "empty_mult")
        self.assertIsNone(dump["a"])
        self.assertIsNone(dump["b"])

    def test_dump_includes_nested_elements(self):
        """Check that dump includes nested element data."""
        sound_a = sl.SoundElement(name="sound_a", frequency=880.0)
        sound_b = sl.SoundElement(name="sound_b", frequency=440.0)
        elem = sl.MultiplyElements(a=sound_a, b=sound_b)
        dump = elem.dump()

        # Check nested element dump
        self.assertEqual(dump["a"]["get_name"], "sound_a")
        self.assertEqual(dump["a"]["get_frequency"], 880.0)
        self.assertEqual(dump["b"]["get_name"], "sound_b")
        self.assertEqual(dump["b"]["get_frequency"], 440.0)


class TestMultiplyElementsMsg(unittest.TestCase):
    """Test MultiplyElements msg method for control messages."""

    def test_msg_get_name(self):
        """Check that msg can get name."""
        elem = sl.MultiplyElements(name="test")
        result = elem.msg({"test": {"get_name": []}})
        self.assertEqual(result["test"]["get_name"], "test")

    def test_msg_get_type(self):
        """Check that msg can get type."""
        elem = sl.MultiplyElements(name="test")
        result = elem.msg({"test": {"get_type": []}})
        self.assertEqual(result["test"]["get_type"], "MultiplyElements")

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.MultiplyElements(name="test", scale=0.5)
        result = elem.msg({"test": {"get_scale": []}})
        self.assertEqual(result["test"]["get_scale"], 0.5)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.MultiplyElements(name="test")
        elem.msg({"test": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_sample(self):
        """Check that msg can get sample."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="test")
        result = elem.msg({"test": {"sample": []}})
        self.assertAlmostEqual(result["test"]["sample"], 1.0, places=10)

    def test_msg_set_on(self):
        """Check that msg can activate element."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="test")
        elem.msg({"test": {"set_on": []}})
        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

    def test_msg_set_off(self):
        """Check that msg can deactivate element."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="test")
        elem.set_on()
        elem.msg({"test": {"set_off": []}})
        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.MultiplyElements(name="test", scale=1.0)
        elem.msg({"other_name": {"set_scale": [0.5]}})
        self.assertEqual(elem.get_scale(), 1.0)

    def test_msg_propagates_to_children(self):
        """Check that msg propagates to child elements."""
        sound_a = sl.SoundElement(name="child_a")
        sound_b = sl.SoundElement(name="child_b")
        elem = sl.MultiplyElements(a=sound_a, b=sound_b, name="parent")

        # Send message to child through parent
        result = elem.msg({
            "parent": {},
            "child_a": {"get_frequency": []}
        })

        # Child response should be included
        self.assertIn("a", result["parent"])


class TestMultiplyElementsNesting(unittest.TestCase):
    """Test MultiplyElements with nested elements."""

    def test_nested_multiply_elements(self):
        """Check that MultiplyElements can be nested."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_c = sl.SoundElement(phase=math.pi / 2)  # 1.0

        inner = sl.MultiplyElements(a=sound_a, b=sound_b)
        outer = sl.MultiplyElements(a=inner, b=sound_c)

        outer.set_on()
        # (1.0 * 1.0) * 1.0 = 1.0
        self.assertAlmostEqual(outer.sample(), 1.0, places=10)

    def test_deeply_nested_sample(self):
        """Check sample with deeply nested structure."""
        s1 = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5
        s2 = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5
        s3 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s4 = sl.SoundElement(phase=math.pi / 2)  # 1.0

        m1 = sl.MultiplyElements(a=s1, b=s2)  # 0.5 * 0.5 = 0.25
        m2 = sl.MultiplyElements(a=s3, b=s4)  # 1.0 * 1.0 = 1.0
        outer = sl.MultiplyElements(a=m1, b=m2)  # 0.25 * 1.0 = 0.25

        outer.set_on()
        self.assertAlmostEqual(outer.sample(), 0.25, places=10)


# =============================================================================
# MixElements Tests
# =============================================================================

class TestMixElementsDefaults(unittest.TestCase):
    """Test MixElements default values after instantiation without arguments."""

    def test_a_is_none_by_default(self):
        """Check that _a is None when not provided."""
        elem = sl.MixElements()
        self.assertIsNone(elem._a)

    def test_b_is_none_by_default(self):
        """Check that _b is None when not provided."""
        elem = sl.MixElements()
        self.assertIsNone(elem._b)

    def test_scale_is_float_one(self):
        """Check that scale is a float set to 1.0."""
        elem = sl.MixElements()
        self.assertIsInstance(elem._scale, float)
        self.assertEqual(elem._scale, 1.0)

    def test_name_includes_mix_elements_and_unique_id(self):
        """Check that name includes 'MixElements' and a unique identifier."""
        elem = sl.MixElements()
        self.assertIsInstance(elem._name, str)
        self.assertIn("MixElements", elem._name)
        parts = elem._name.split("_")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "MixElements")
        self.assertTrue(parts[1].isdigit())

    def test_name_is_unique(self):
        """Check that each instance gets a unique name."""
        elem1 = sl.MixElements()
        elem2 = sl.MixElements()
        self.assertNotEqual(elem1._name, elem2._name)

    def test_get_type_returns_mix_elements(self):
        """Check that get_type returns 'MixElements'."""
        elem = sl.MixElements()
        self.assertEqual(elem.get_type(), "MixElements")


class TestMixElementsCustomArgs(unittest.TestCase):
    """Test MixElements with custom constructor arguments."""

    def test_custom_a_element(self):
        """Check that custom 'a' element is set correctly."""
        sound = sl.SoundElement()
        elem = sl.MixElements(a=sound)
        self.assertIs(elem._a, sound)

    def test_custom_b_element(self):
        """Check that custom 'b' element is set correctly."""
        sound = sl.SoundElement()
        elem = sl.MixElements(b=sound)
        self.assertIs(elem._b, sound)

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.MixElements(name="my_mixer")
        self.assertEqual(elem.get_name(), "my_mixer")

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.MixElements(scale=0.5)
        self.assertEqual(elem.get_scale(), 0.5)

    def test_all_custom_args(self):
        """Check that all custom arguments are set correctly."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MixElements(
            a=sound_a,
            b=sound_b,
            name="test_mix",
            scale=0.75
        )
        self.assertIs(elem._a, sound_a)
        self.assertIs(elem._b, sound_b)
        self.assertEqual(elem.get_name(), "test_mix")
        self.assertEqual(elem.get_scale(), 0.75)


class TestMixElementsSetters(unittest.TestCase):
    """Test MixElements setter methods."""

    def test_set_a_with_sound_element(self):
        """Check that set_a accepts SoundElement."""
        elem = sl.MixElements()
        sound = sl.SoundElement()
        elem.set_a(sound)
        self.assertIs(elem._a, sound)

    def test_set_b_with_sound_element(self):
        """Check that set_b accepts SoundElement."""
        elem = sl.MixElements()
        sound = sl.SoundElement()
        elem.set_b(sound)
        self.assertIs(elem._b, sound)

    def test_set_a_with_mix_elements(self):
        """Check that set_a accepts MixElements (nesting)."""
        inner = sl.MixElements()
        outer = sl.MixElements()
        outer.set_a(inner)
        self.assertIs(outer._a, inner)

    def test_set_b_with_mix_elements(self):
        """Check that set_b accepts MixElements (nesting)."""
        inner = sl.MixElements()
        outer = sl.MixElements()
        outer.set_b(inner)
        self.assertIs(outer._b, inner)

    def test_set_a_with_multiply_elements(self):
        """Check that set_a accepts MultiplyElements."""
        mult = sl.MultiplyElements()
        mix = sl.MixElements()
        mix.set_a(mult)
        self.assertIs(mix._a, mult)

    def test_set_a_invalid_raises_error(self):
        """Check that set_a with invalid object raises ValueError."""
        elem = sl.MixElements()
        with self.assertRaises(ValueError) as ctx:
            elem.set_a("invalid")
        self.assertIn("no attribute sample()", str(ctx.exception))

    def test_set_b_invalid_raises_error(self):
        """Check that set_b with invalid object raises ValueError."""
        elem = sl.MixElements()
        with self.assertRaises(ValueError) as ctx:
            elem.set_b(12345)
        self.assertIn("no attribute sample()", str(ctx.exception))

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.MixElements()
        elem.set_scale(0.25)
        self.assertEqual(elem.get_scale(), 0.25)


class TestMixElementsGetInstances(unittest.TestCase):
    """Test MixElements get_instances method."""

    def test_get_instances_both_none(self):
        """Check get_instances when both a and b are None."""
        elem = sl.MixElements()
        self.assertEqual(elem.get_instances(), (None, None))

    def test_get_instances_a_only(self):
        """Check get_instances when only a is set."""
        sound = sl.SoundElement(name="sound_a")
        elem = sl.MixElements(a=sound)
        self.assertEqual(elem.get_instances(), ("sound_a", None))

    def test_get_instances_b_only(self):
        """Check get_instances when only b is set."""
        sound = sl.SoundElement(name="sound_b")
        elem = sl.MixElements(b=sound)
        self.assertEqual(elem.get_instances(), (None, "sound_b"))

    def test_get_instances_both_set(self):
        """Check get_instances when both a and b are set."""
        sound_a = sl.SoundElement(name="first")
        sound_b = sl.SoundElement(name="second")
        elem = sl.MixElements(a=sound_a, b=sound_b)
        self.assertEqual(elem.get_instances(), ("first", "second"))


class TestMixElementsSample(unittest.TestCase):
    """Test MixElements sample method (Z = A + B - A*B)."""

    def test_sample_with_no_elements_returns_zero(self):
        """Check that sample() returns 0.0 when no elements are set."""
        elem = sl.MixElements()
        # (0 + 0) - (0 * 0) = 0
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_only_a(self):
        """Check that sample() with only a returns a's value."""
        sound = sl.SoundElement(phase=math.pi / 2)  # Peak = 1.0
        sound.set_on()
        elem = sl.MixElements(a=sound)
        # (1.0 + 0) - (1.0 * 0) = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_with_only_b(self):
        """Check that sample() with only b returns b's value."""
        sound = sl.SoundElement(phase=math.pi / 2)  # Peak = 1.0
        sound.set_on()
        elem = sl.MixElements(b=sound)
        # (0 + 1.0) - (0 * 1.0) = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_mix_formula(self):
        """Check that sample() correctly applies mix formula Z = A + B - A*B."""
        # Use elements with known values
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b)
        # (1.0 + 1.0) - (1.0 * 1.0) = 2.0 - 1.0 = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_mix_with_half_values(self):
        """Check mix formula with 0.5 values."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # sin(pi/6) = 0.5
        sound_b = sl.SoundElement(phase=math.pi / 6)  # sin(pi/6) = 0.5
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b)
        # (0.5 + 0.5) - (0.5 * 0.5) = 1.0 - 0.25 = 0.75
        self.assertAlmostEqual(elem.sample(), 0.75, places=10)

    def test_sample_with_different_values(self):
        """Check mix formula with different values."""
        # sin(pi/6) = 0.5, sin(pi/2) = 1.0
        sound_a = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b)
        a_val = math.sin(math.pi / 6)
        b_val = math.sin(math.pi / 2)
        expected = (a_val + b_val) - (a_val * b_val)
        # (0.5 + 1.0) - (0.5 * 1.0) = 1.5 - 0.5 = 1.0
        self.assertAlmostEqual(elem.sample(), expected, places=10)

    def test_sample_with_scale(self):
        """Check that sample() applies scale correctly."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b, scale=0.5)
        # ((1.0 + 1.0) - (1.0 * 1.0)) * 0.5 = 1.0 * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_with_zero_scale(self):
        """Check that scale=0 produces zero output."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b, scale=0.0)
        self.assertEqual(elem.sample(), 0.0)

    def test_mix_vs_multiply_difference(self):
        """Check that MixElements produces different result than MultiplyElements."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_b = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_a2 = sl.SoundElement(phase=math.pi / 6)
        sound_b2 = sl.SoundElement(phase=math.pi / 6)

        sound_a.set_on()
        sound_b.set_on()
        sound_a2.set_on()
        sound_b2.set_on()

        mix = sl.MixElements(a=sound_a, b=sound_b)
        mult = sl.MultiplyElements(a=sound_a2, b=sound_b2)

        mix_result = mix.sample()  # (0.5 + 0.5) - (0.5 * 0.5) = 0.75
        mult_result = mult.sample()  # 0.5 * 0.5 = 0.25

        self.assertAlmostEqual(mix_result, 0.75, places=10)
        self.assertAlmostEqual(mult_result, 0.25, places=10)
        self.assertNotAlmostEqual(mix_result, mult_result, places=5)


class TestMixElementsOnOff(unittest.TestCase):
    """Test MixElements set_on and set_off behavior."""

    def test_set_on_activates_both_elements(self):
        """Check that set_on activates both child elements."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MixElements(a=sound_a, b=sound_b)

        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

        elem.set_on()

        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

    def test_set_off_deactivates_both_elements(self):
        """Check that set_off deactivates both child elements."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MixElements(a=sound_a, b=sound_b)

        elem.set_on()
        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

        elem.set_off()
        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

    def test_set_on_with_no_elements_does_not_crash(self):
        """Check that set_on with no elements doesn't crash."""
        elem = sl.MixElements()
        elem.set_on()  # Should not raise

    def test_set_off_with_no_elements_does_not_crash(self):
        """Check that set_off with no elements doesn't crash."""
        elem = sl.MixElements()
        elem.set_off()  # Should not raise

    def test_set_on_with_partial_elements(self):
        """Check that set_on works with only one element set."""
        sound = sl.SoundElement()
        elem = sl.MixElements(a=sound)

        elem.set_on()
        self.assertTrue(sound._on)


class TestMixElementsDump(unittest.TestCase):
    """Test MixElements dump method."""

    def test_dump_contains_all_properties(self):
        """Check that dump returns all expected properties."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MixElements(a=sound_a, b=sound_b, name="test_mix", scale=0.75)
        dump = elem.dump()

        self.assertIn("get_name", dump)
        self.assertIn("get_type", dump)
        self.assertIn("get_scale", dump)
        self.assertIn("a", dump)
        self.assertIn("b", dump)

    def test_dump_values_match(self):
        """Check that dump values match the element's properties."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.MixElements(a=sound_a, b=sound_b, name="test_mix", scale=0.75)
        dump = elem.dump()

        self.assertEqual(dump["get_name"], "test_mix")
        self.assertEqual(dump["get_type"], "MixElements")
        self.assertEqual(dump["get_scale"], 0.75)
        self.assertIsNotNone(dump["a"])
        self.assertIsNotNone(dump["b"])

    def test_dump_with_no_elements(self):
        """Check dump when no child elements are set."""
        elem = sl.MixElements(name="empty_mix")
        dump = elem.dump()

        self.assertEqual(dump["get_name"], "empty_mix")
        self.assertIsNone(dump["a"])
        self.assertIsNone(dump["b"])

    def test_dump_includes_nested_elements(self):
        """Check that dump includes nested element data."""
        sound_a = sl.SoundElement(name="sound_a", frequency=880.0)
        sound_b = sl.SoundElement(name="sound_b", frequency=440.0)
        elem = sl.MixElements(a=sound_a, b=sound_b)
        dump = elem.dump()

        self.assertEqual(dump["a"]["get_name"], "sound_a")
        self.assertEqual(dump["a"]["get_frequency"], 880.0)
        self.assertEqual(dump["b"]["get_name"], "sound_b")
        self.assertEqual(dump["b"]["get_frequency"], 440.0)


class TestMixElementsMsg(unittest.TestCase):
    """Test MixElements msg method for control messages."""

    def test_msg_get_name(self):
        """Check that msg can get name."""
        elem = sl.MixElements(name="test")
        result = elem.msg({"test": {"get_name": []}})
        self.assertEqual(result["test"]["get_name"], "test")

    def test_msg_get_type(self):
        """Check that msg can get type."""
        elem = sl.MixElements(name="test")
        result = elem.msg({"test": {"get_type": []}})
        self.assertEqual(result["test"]["get_type"], "MixElements")

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.MixElements(name="test", scale=0.5)
        result = elem.msg({"test": {"get_scale": []}})
        self.assertEqual(result["test"]["get_scale"], 0.5)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.MixElements(name="test")
        elem.msg({"test": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_sample(self):
        """Check that msg can get sample."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.MixElements(a=sound_a, b=sound_b, name="test")
        result = elem.msg({"test": {"sample": []}})
        # (1.0 + 1.0) - (1.0 * 1.0) = 1.0
        self.assertAlmostEqual(result["test"]["sample"], 1.0, places=10)

    def test_msg_set_on(self):
        """Check that msg can activate element."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MixElements(a=sound_a, b=sound_b, name="test")
        elem.msg({"test": {"set_on": []}})
        self.assertTrue(sound_a._on)
        self.assertTrue(sound_b._on)

    def test_msg_set_off(self):
        """Check that msg can deactivate element."""
        sound_a = sl.SoundElement()
        sound_b = sl.SoundElement()
        elem = sl.MixElements(a=sound_a, b=sound_b, name="test")
        elem.set_on()
        elem.msg({"test": {"set_off": []}})
        self.assertFalse(sound_a._on)
        self.assertFalse(sound_b._on)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.MixElements(name="test", scale=1.0)
        elem.msg({"other_name": {"set_scale": [0.5]}})
        self.assertEqual(elem.get_scale(), 1.0)

    def test_msg_propagates_to_children(self):
        """Check that msg propagates to child elements."""
        sound_a = sl.SoundElement(name="child_a")
        sound_b = sl.SoundElement(name="child_b")
        elem = sl.MixElements(a=sound_a, b=sound_b, name="parent")

        result = elem.msg({
            "parent": {},
            "child_a": {"get_frequency": []}
        })

        self.assertIn("a", result["parent"])


class TestMixElementsNesting(unittest.TestCase):
    """Test MixElements with nested elements."""

    def test_nested_mix_elements(self):
        """Check that MixElements can be nested."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_c = sl.SoundElement(phase=math.pi / 2)  # 1.0

        inner = sl.MixElements(a=sound_a, b=sound_b)
        outer = sl.MixElements(a=inner, b=sound_c)

        outer.set_on()
        # inner: (1.0 + 1.0) - (1.0 * 1.0) = 1.0
        # outer: (1.0 + 1.0) - (1.0 * 1.0) = 1.0
        self.assertAlmostEqual(outer.sample(), 1.0, places=10)

    def test_mix_and_multiply_combined(self):
        """Check combining MixElements and MultiplyElements."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_c = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5

        mult = sl.MultiplyElements(a=sound_a, b=sound_b)  # 1.0 * 1.0 = 1.0
        mix = sl.MixElements(a=mult, b=sound_c)

        mix.set_on()
        # (1.0 + 0.5) - (1.0 * 0.5) = 1.5 - 0.5 = 1.0
        self.assertAlmostEqual(mix.sample(), 1.0, places=10)

    def test_deeply_nested_mix(self):
        """Check sample with deeply nested MixElements."""
        s1 = sl.SoundElement(phase=math.pi / 6)  # 0.5
        s2 = sl.SoundElement(phase=math.pi / 6)  # 0.5
        s3 = sl.SoundElement(phase=math.pi / 6)  # 0.5
        s4 = sl.SoundElement(phase=math.pi / 6)  # 0.5

        # m1: (0.5 + 0.5) - (0.5 * 0.5) = 1.0 - 0.25 = 0.75
        m1 = sl.MixElements(a=s1, b=s2)
        # m2: (0.5 + 0.5) - (0.5 * 0.5) = 1.0 - 0.25 = 0.75
        m2 = sl.MixElements(a=s3, b=s4)
        # outer: (0.75 + 0.75) - (0.75 * 0.75) = 1.5 - 0.5625 = 0.9375
        outer = sl.MixElements(a=m1, b=m2)

        outer.set_on()
        self.assertAlmostEqual(outer.sample(), 0.9375, places=10)


# =============================================================================
# SumElements Tests
# =============================================================================


class TestSumElementsDefaults(unittest.TestCase):
    """Tests for SumElements default values after instantiation without arguments."""

    def test_default_type(self):
        """Check that default _TYPE is 'SumElements'."""
        elem = sl.SumElements()
        self.assertEqual(elem.get_type(), "SumElements")

    def test_default_name_format(self):
        """Check that default name starts with 'SumElements_'."""
        elem = sl.SumElements()
        self.assertTrue(elem.get_name().startswith("SumElements_"))

    def test_default_scale(self):
        """Check that default scale is 0.5."""
        elem = sl.SumElements()
        self.assertEqual(elem.get_scale(), 0.5)

    def test_default_a_is_none(self):
        """Check that default _a is None via get_instances."""
        elem = sl.SumElements()
        a_name, _ = elem.get_instances()
        self.assertIsNone(a_name)

    def test_default_b_is_none(self):
        """Check that default _b is None via get_instances."""
        elem = sl.SumElements()
        _, b_name = elem.get_instances()
        self.assertIsNone(b_name)

    def test_default_sample_returns_zero(self):
        """Check that sample() returns 0.0 with no inputs."""
        elem = sl.SumElements()
        self.assertEqual(elem.sample(), 0.0)


class TestSumElementsCustomArgs(unittest.TestCase):
    """Tests for SumElements initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.SumElements(name="my_sum")
        self.assertEqual(elem.get_name(), "my_sum")

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.SumElements(scale=0.75)
        self.assertEqual(elem.get_scale(), 0.75)

    def test_custom_a_element(self):
        """Check that custom a element is set correctly."""
        sound_a = sl.SoundElement(name="input_a")
        elem = sl.SumElements(a=sound_a)
        a_name, _ = elem.get_instances()
        self.assertEqual(a_name, "input_a")

    def test_custom_b_element(self):
        """Check that custom b element is set correctly."""
        sound_b = sl.SoundElement(name="input_b")
        elem = sl.SumElements(b=sound_b)
        _, b_name = elem.get_instances()
        self.assertEqual(b_name, "input_b")

    def test_custom_both_elements(self):
        """Check that both a and b elements can be set."""
        sound_a = sl.SoundElement(name="input_a")
        sound_b = sl.SoundElement(name="input_b")
        elem = sl.SumElements(a=sound_a, b=sound_b)
        a_name, b_name = elem.get_instances()
        self.assertEqual(a_name, "input_a")
        self.assertEqual(b_name, "input_b")


class TestSumElementsSetters(unittest.TestCase):
    """Tests for SumElements setter methods."""

    def test_set_a(self):
        """Check that set_a updates the a element."""
        elem = sl.SumElements()
        sound_a = sl.SoundElement(name="new_a")
        elem.set_a(sound_a)
        a_name, _ = elem.get_instances()
        self.assertEqual(a_name, "new_a")

    def test_set_b(self):
        """Check that set_b updates the b element."""
        elem = sl.SumElements()
        sound_b = sl.SoundElement(name="new_b")
        elem.set_b(sound_b)
        _, b_name = elem.get_instances()
        self.assertEqual(b_name, "new_b")

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.SumElements()
        elem.set_scale(0.25)
        self.assertEqual(elem.get_scale(), 0.25)

    def test_set_a_invalid_raises_error(self):
        """Check that set_a with invalid object raises ValueError."""
        elem = sl.SumElements()
        with self.assertRaises(ValueError):
            elem.set_a("not a sound element")

    def test_set_b_invalid_raises_error(self):
        """Check that set_b with invalid object raises ValueError."""
        elem = sl.SumElements()
        with self.assertRaises(ValueError):
            elem.set_b(12345)

    def test_set_a_accepts_multiply_elements(self):
        """Check that set_a accepts MultiplyElements."""
        elem = sl.SumElements()
        mult = sl.MultiplyElements(name="mult_elem")
        elem.set_a(mult)
        a_name, _ = elem.get_instances()
        self.assertEqual(a_name, "mult_elem")

    def test_set_b_accepts_mix_elements(self):
        """Check that set_b accepts MixElements."""
        elem = sl.SumElements()
        mix = sl.MixElements(name="mix_elem")
        elem.set_b(mix)
        _, b_name = elem.get_instances()
        self.assertEqual(b_name, "mix_elem")

    def test_set_a_accepts_sum_elements(self):
        """Check that set_a accepts SumElements (nesting)."""
        elem = sl.SumElements()
        inner = sl.SumElements(name="inner_sum")
        elem.set_a(inner)
        a_name, _ = elem.get_instances()
        self.assertEqual(a_name, "inner_sum")


class TestSumElementsGetInstances(unittest.TestCase):
    """Tests for SumElements get_instances method."""

    def test_get_instances_returns_tuple(self):
        """Check that get_instances returns a tuple."""
        elem = sl.SumElements()
        result = elem.get_instances()
        self.assertIsInstance(result, tuple)

    def test_get_instances_tuple_length(self):
        """Check that get_instances returns a tuple of length 2."""
        elem = sl.SumElements()
        result = elem.get_instances()
        self.assertEqual(len(result), 2)

    def test_get_instances_with_elements(self):
        """Check that get_instances returns correct names."""
        sound_a = sl.SoundElement(name="elem_a")
        sound_b = sl.SoundElement(name="elem_b")
        elem = sl.SumElements(a=sound_a, b=sound_b)
        self.assertEqual(elem.get_instances(), ("elem_a", "elem_b"))

    def test_get_instances_partial_a_only(self):
        """Check that get_instances works with only a set."""
        sound_a = sl.SoundElement(name="only_a")
        elem = sl.SumElements(a=sound_a)
        a_name, b_name = elem.get_instances()
        self.assertEqual(a_name, "only_a")
        self.assertIsNone(b_name)


class TestSumElementsSample(unittest.TestCase):
    """Tests for SumElements sample method."""

    def test_sample_with_no_inputs(self):
        """Check that sample returns 0.0 with no inputs."""
        elem = sl.SumElements()
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_only_a(self):
        """Check sample with only a element set."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound_a.set_on()
        elem = sl.SumElements(a=sound_a)
        # (1.0 + 0.0) * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_with_only_b(self):
        """Check sample with only b element set."""
        sound_b = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound_b.set_on()
        elem = sl.SumElements(b=sound_b)
        # (0.0 + 1.0) * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_sum_formula_both_one(self):
        """Check sum formula with both inputs at 1.0."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b)
        # (1.0 + 1.0) * 0.5 = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_sum_formula_with_half_values(self):
        """Check sum formula with 0.5 values."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # sin(pi/6) = 0.5
        sound_b = sl.SoundElement(phase=math.pi / 6)  # sin(pi/6) = 0.5
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b)
        # (0.5 + 0.5) * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_sum_vs_mix_formula(self):
        """Check that sum formula differs from mix formula."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_b = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_a.set_on()
        sound_b.set_on()
        sum_elem = sl.SumElements(a=sound_a, b=sound_b, scale=1.0)

        sound_c = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_d = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_c.set_on()
        sound_d.set_on()
        mix_elem = sl.MixElements(a=sound_c, b=sound_d, scale=1.0)

        # Sum: (0.5 + 0.5) * 1.0 = 1.0
        # Mix: (0.5 + 0.5) - (0.5 * 0.5) = 0.75
        self.assertAlmostEqual(sum_elem.sample(), 1.0, places=10)
        self.assertAlmostEqual(mix_elem.sample(), 0.75, places=10)
        self.assertNotAlmostEqual(sum_elem.sample(), mix_elem.sample(), places=10)

    def test_sample_sum_vs_multiply_formula(self):
        """Check that sum formula differs from multiply formula."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_b = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_a.set_on()
        sound_b.set_on()
        sum_elem = sl.SumElements(a=sound_a, b=sound_b, scale=1.0)

        sound_c = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_d = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_c.set_on()
        sound_d.set_on()
        mult_elem = sl.MultiplyElements(a=sound_c, b=sound_d)

        # Sum: (0.5 + 0.5) * 1.0 = 1.0
        # Multiply: 0.5 * 0.5 * 1.0 = 0.25
        self.assertAlmostEqual(sum_elem.sample(), 1.0, places=10)
        self.assertAlmostEqual(mult_elem.sample(), 0.25, places=10)

    def test_sample_with_custom_scale(self):
        """Check that scale affects sample output."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b, scale=0.25)
        # (1.0 + 1.0) * 0.25 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_with_scale_one(self):
        """Check sample with scale=1.0 (no attenuation)."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_b = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b, scale=1.0)
        # (1.0 + 1.0) * 1.0 = 2.0
        self.assertAlmostEqual(elem.sample(), 2.0, places=10)

    def test_sample_advances_phase(self):
        """Check that sample advances phase of sub-elements."""
        sound_a = sl.SoundElement(phase=0.0, frequency=440)
        sound_b = sl.SoundElement(phase=0.0, frequency=440)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b)
        sample1 = elem.sample()
        sample2 = elem.sample()
        # Samples should differ as phase advances
        self.assertNotEqual(sample1, sample2)


class TestSumElementsOnOff(unittest.TestCase):
    """Tests for SumElements set_on and set_off methods."""

    def test_set_on_activates_sub_elements(self):
        """Check that set_on activates sub-elements."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        elem = sl.SumElements(a=sound_a, b=sound_b)
        # Before set_on, sample should be 0
        self.assertEqual(elem.sample(), 0.0)
        # After set_on, should get sum output
        elem.set_on()
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_set_off_deactivates_sub_elements(self):
        """Check that set_off deactivates sub-elements."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(a=sound_a, b=sound_b)
        # Should have output
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)
        # After set_off, should eventually return to 0
        elem.set_off()
        for _ in range(1000):
            elem.sample()
        self.assertAlmostEqual(elem.sample(), 0.0, places=5)

    def test_set_on_with_no_elements(self):
        """Check that set_on doesn't error with no elements."""
        elem = sl.SumElements()
        elem.set_on()  # Should not raise
        self.assertEqual(elem.sample(), 0.0)

    def test_set_off_with_no_elements(self):
        """Check that set_off doesn't error with no elements."""
        elem = sl.SumElements()
        elem.set_off()  # Should not raise
        self.assertEqual(elem.sample(), 0.0)

    def test_set_on_resets_phase(self):
        """Check that set_on resets phase on sub-elements."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_b = sl.SoundElement(phase=math.pi / 2)
        elem = sl.SumElements(a=sound_a, b=sound_b)
        elem.set_on()
        first_sample = elem.sample()
        # Advance phase
        for _ in range(100):
            elem.sample()
        # set_on again should reset phase
        elem.set_on()
        reset_sample = elem.sample()
        self.assertAlmostEqual(first_sample, reset_sample, places=10)


class TestSumElementsDump(unittest.TestCase):
    """Tests for SumElements dump method."""

    def test_dump_returns_dict(self):
        """Check that dump returns a dictionary."""
        elem = sl.SumElements()
        result = elem.dump()
        self.assertIsInstance(result, dict)

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        elem = sl.SumElements()
        result = elem.dump()
        self.assertIn("get_scale", result)
        self.assertIn("get_type", result)
        self.assertIn("get_name", result)
        self.assertIn("a", result)
        self.assertIn("b", result)

    def test_dump_values_match_getters(self):
        """Check that dump values match getter methods."""
        elem = sl.SumElements(name="test_sum", scale=0.75)
        result = elem.dump()
        self.assertEqual(result["get_scale"], elem.get_scale())
        self.assertEqual(result["get_type"], elem.get_type())
        self.assertEqual(result["get_name"], elem.get_name())

    def test_dump_with_sub_elements(self):
        """Check that dump includes sub-element dumps."""
        sound_a = sl.SoundElement(name="sub_a")
        sound_b = sl.SoundElement(name="sub_b")
        elem = sl.SumElements(a=sound_a, b=sound_b)
        result = elem.dump()
        self.assertIsNotNone(result["a"])
        self.assertIsNotNone(result["b"])
        self.assertEqual(result["a"]["get_name"], "sub_a")
        self.assertEqual(result["b"]["get_name"], "sub_b")


class TestSumElementsMsg(unittest.TestCase):
    """Tests for SumElements msg method."""

    def test_msg_returns_dict(self):
        """Check that msg returns a dictionary."""
        elem = sl.SumElements(name="test_sum")
        result = elem.msg({"test_sum": {}})
        self.assertIsInstance(result, dict)

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.SumElements(name="test_sum", scale=0.75)
        result = elem.msg({"test_sum": {"get_scale": []}})
        self.assertEqual(result["test_sum"]["get_scale"], 0.75)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.SumElements(name="test_sum")
        elem.msg({"test_sum": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_get_type(self):
        """Check that msg can get type."""
        elem = sl.SumElements(name="test_sum")
        result = elem.msg({"test_sum": {"get_type": []}})
        self.assertEqual(result["test_sum"]["get_type"], "SumElements")

    def test_msg_get_name(self):
        """Check that msg can get name."""
        elem = sl.SumElements(name="test_sum")
        result = elem.msg({"test_sum": {"get_name": []}})
        self.assertEqual(result["test_sum"]["get_name"], "test_sum")

    def test_msg_sample(self):
        """Check that msg can get sample."""
        sound_a = sl.SoundElement(name="a", phase=math.pi / 2)
        sound_b = sl.SoundElement(name="b", phase=math.pi / 2)
        sound_a.set_on()
        sound_b.set_on()
        elem = sl.SumElements(name="test_sum", a=sound_a, b=sound_b)
        result = elem.msg({"test_sum": {"sample": []}})
        self.assertAlmostEqual(result["test_sum"]["sample"], 1.0, places=10)

    def test_msg_set_on_and_sample(self):
        """Check that msg can activate and sample."""
        sound_a = sl.SoundElement(name="a", phase=math.pi / 2)
        sound_b = sl.SoundElement(name="b", phase=math.pi / 2)
        elem = sl.SumElements(name="test_sum", a=sound_a, b=sound_b)
        elem.msg({"test_sum": {"set_on": []}})
        result = elem.msg({"test_sum": {"sample": []}})
        self.assertAlmostEqual(result["test_sum"]["sample"], 1.0, places=10)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.SumElements(name="test_sum", scale=0.5)
        elem.msg({"other_elem": {"set_scale": [0.9]}})
        self.assertEqual(elem.get_scale(), 0.5)


class TestSumElementsNesting(unittest.TestCase):
    """Tests for SumElements with nested elements."""

    def test_nested_sum_elements(self):
        """Check that SumElements can nest other SumElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        inner = sl.SumElements(a=s1, b=s2, scale=0.5)  # (1+1)*0.5 = 1.0

        s3 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s3.set_on()
        outer = sl.SumElements(a=inner, b=s3, scale=0.5)  # (1+1)*0.5 = 1.0
        self.assertAlmostEqual(outer.sample(), 1.0, places=10)

    def test_sum_with_multiply_elements(self):
        """Check that SumElements can contain MultiplyElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        mult = sl.MultiplyElements(a=s1, b=s2)  # 1.0 * 1.0 = 1.0

        s3 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s3.set_on()
        sum_elem = sl.SumElements(a=mult, b=s3, scale=0.5)  # (1+1)*0.5 = 1.0
        self.assertAlmostEqual(sum_elem.sample(), 1.0, places=10)

    def test_deeply_nested_sum(self):
        """Check deeply nested SumElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s3 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s4 = sl.SoundElement(phase=math.pi / 2)  # 1.0

        # sum1: (1+1)*0.5 = 1.0
        sum1 = sl.SumElements(a=s1, b=s2, scale=0.5)
        # sum2: (1+1)*0.5 = 1.0
        sum2 = sl.SumElements(a=s3, b=s4, scale=0.5)
        # outer: (1+1)*0.5 = 1.0
        outer = sl.SumElements(a=sum1, b=sum2, scale=0.5)

        outer.set_on()
        self.assertAlmostEqual(outer.sample(), 1.0, places=10)


# =============================================================================
# Pluck Tests
# =============================================================================


class TestPluckDefaults(unittest.TestCase):
    """Tests for Pluck default values after instantiation without arguments."""

    def test_default_type(self):
        """Check that default _TYPE is 'Pluck'."""
        elem = sl.Pluck()
        self.assertEqual(elem.get_type(), "Pluck")

    def test_default_name_format(self):
        """Check that default name starts with 'Pluck_'."""
        elem = sl.Pluck()
        self.assertTrue(elem.get_name().startswith("Pluck_"))

    def test_default_scale(self):
        """Check that default scale is 1.0."""
        elem = sl.Pluck()
        self.assertEqual(elem.get_scale(), 1.0)

    def test_default_sample_rate(self):
        """Check that default sample_rate is 44100."""
        elem = sl.Pluck()
        self.assertEqual(elem.get_sample_rate(), 44100)

    def test_default_stop(self):
        """Check that default stop is 2.0."""
        elem = sl.Pluck()
        self.assertEqual(elem.get_stop(), 2.0)

    def test_default_lambda_dc(self):
        """Check that default lambda_dc is 0.03."""
        elem = sl.Pluck()
        self.assertEqual(elem.get_lambda_dc(), 0.03)

    def test_default_sample_returns_zero(self):
        """Check that sample() returns 0.0 when not activated."""
        elem = sl.Pluck()
        self.assertEqual(elem.sample(), 0.0)


class TestPluckCustomArgs(unittest.TestCase):
    """Tests for Pluck initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.Pluck(name="my_pluck")
        self.assertEqual(elem.get_name(), "my_pluck")

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.Pluck(scale=0.5)
        self.assertEqual(elem.get_scale(), 0.5)

    def test_custom_sample_rate(self):
        """Check that custom sample_rate is set correctly."""
        elem = sl.Pluck(sample_rate=48000)
        self.assertEqual(elem.get_sample_rate(), 48000)

    def test_custom_stop(self):
        """Check that custom stop is set correctly."""
        elem = sl.Pluck(stop=1.5)
        self.assertEqual(elem.get_stop(), 1.5)

    def test_custom_lambda_dc(self):
        """Check that custom lambda_dc is set correctly."""
        elem = sl.Pluck(lambda_dc=0.05)
        self.assertEqual(elem.get_lambda_dc(), 0.05)

    def test_custom_a_element(self):
        """Check that custom a element is set correctly."""
        sound_a = sl.SoundElement(name="input_a")
        elem = sl.Pluck(a=sound_a)
        # Verify by checking dump
        result = elem.dump()
        self.assertIsNotNone(result["a"])
        self.assertEqual(result["a"]["get_name"], "input_a")


class TestPluckValidation(unittest.TestCase):
    """Tests for Pluck parameter validation."""

    def test_zero_sample_rate_raises_error(self):
        """Check that sample_rate=0 raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(sample_rate=0)

    def test_negative_sample_rate_raises_error(self):
        """Check that negative sample_rate raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(sample_rate=-44100)

    def test_zero_stop_raises_error(self):
        """Check that stop=0 raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(stop=0)

    def test_negative_stop_raises_error(self):
        """Check that negative stop raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(stop=-1.0)

    def test_zero_lambda_dc_raises_error(self):
        """Check that lambda_dc=0 raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(lambda_dc=0)

    def test_negative_lambda_dc_raises_error(self):
        """Check that negative lambda_dc raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Pluck(lambda_dc=-0.03)

    def test_set_a_invalid_raises_error(self):
        """Check that set_a with invalid object raises ValueError."""
        elem = sl.Pluck()
        with self.assertRaises(ValueError):
            elem.set_a("not a sound element")


class TestPluckSetters(unittest.TestCase):
    """Tests for Pluck setter methods."""

    def test_set_a(self):
        """Check that set_a updates the a element."""
        elem = sl.Pluck()
        sound_a = sl.SoundElement(name="new_a")
        elem.set_a(sound_a)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "new_a")

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.Pluck()
        elem.set_scale(0.25)
        self.assertEqual(elem.get_scale(), 0.25)

    def test_set_sample_rate(self):
        """Check that set_sample_rate updates the sample rate."""
        elem = sl.Pluck()
        elem.set_sample_rate(48000)
        self.assertEqual(elem.get_sample_rate(), 48000)

    def test_set_sample_rate_invalid_raises_error(self):
        """Check that set_sample_rate with invalid value raises ValueError."""
        elem = sl.Pluck()
        with self.assertRaises(ValueError):
            elem.set_sample_rate(0)

    def test_set_stop(self):
        """Check that set_stop updates the stop time."""
        elem = sl.Pluck()
        elem.set_stop(3.0)
        self.assertEqual(elem.get_stop(), 3.0)

    def test_set_stop_invalid_raises_error(self):
        """Check that set_stop with invalid value raises ValueError."""
        elem = sl.Pluck()
        with self.assertRaises(ValueError):
            elem.set_stop(0)

    def test_set_lambda_dc(self):
        """Check that set_lambda_dc updates the decay constant."""
        elem = sl.Pluck()
        elem.set_lambda_dc(0.1)
        self.assertEqual(elem.get_lambda_dc(), 0.1)

    def test_set_lambda_dc_invalid_raises_error(self):
        """Check that set_lambda_dc with invalid value raises ValueError."""
        elem = sl.Pluck()
        with self.assertRaises(ValueError):
            elem.set_lambda_dc(-0.01)

    def test_set_a_accepts_multiply_elements(self):
        """Check that set_a accepts MultiplyElements."""
        elem = sl.Pluck()
        mult = sl.MultiplyElements(name="mult_elem")
        elem.set_a(mult)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "mult_elem")

    def test_set_a_accepts_sum_elements(self):
        """Check that set_a accepts SumElements."""
        elem = sl.Pluck()
        sum_elem = sl.SumElements(name="sum_elem")
        elem.set_a(sum_elem)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "sum_elem")

    def test_set_a_accepts_pluck(self):
        """Check that set_a accepts Pluck (nesting)."""
        elem = sl.Pluck()
        inner = sl.Pluck(name="inner_pluck")
        elem.set_a(inner)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "inner_pluck")


class TestPluckSample(unittest.TestCase):
    """Tests for Pluck sample method."""

    def test_sample_when_off_returns_zero(self):
        """Check that sample returns 0.0 when not activated."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        elem = sl.Pluck(a=sound_a)
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_after_set_on(self):
        """Check that sample returns non-zero after set_on."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        elem = sl.Pluck(a=sound_a)
        elem.set_on()
        # At t=0, e^(-lambda*0) = 1.0, so sample = 1.0 * 1.0 * 1.0 = 1.0
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_decays_over_time(self):
        """Check that samples decay over time."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # constant 1.0
        elem = sl.Pluck(a=sound_a, lambda_dc=0.1)
        elem.set_on()
        first_sample = elem.sample()
        # Advance time
        for _ in range(1000):
            elem.sample()
        later_sample = elem.sample()
        # Later sample should be smaller due to decay
        self.assertLess(abs(later_sample), abs(first_sample))

    def test_sample_with_scale(self):
        """Check that scale affects sample output."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        elem = sl.Pluck(a=sound_a, scale=0.5)
        elem.set_on()
        # At t=0: 1.0 * e^0 * 0.5 = 0.5
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_auto_turns_off_at_stop(self):
        """Check that pluck auto-deactivates at stop time."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a, stop=0.01, sample_rate=44100)  # Very short stop
        elem.set_on()
        # Sample enough times to exceed stop time
        # 0.01 seconds * 44100 samples/second = 441 samples
        for _ in range(500):
            elem.sample()
        # Should be off now
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_without_a_element(self):
        """Check that sample with no a element returns 0.0."""
        elem = sl.Pluck()
        elem.set_on()
        self.assertEqual(elem.sample(), 0.0)

    def test_decay_formula(self):
        """Check the exponential decay formula."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        lambda_dc = 0.5
        sample_rate = 44100
        elem = sl.Pluck(a=sound_a, lambda_dc=lambda_dc, sample_rate=sample_rate)
        elem.set_on()

        # First sample at t=0
        sample0 = elem.sample()
        self.assertAlmostEqual(sample0, 1.0, places=10)

        # Collect many samples to verify decay trend
        samples = [sample0]
        for _ in range(1000):
            samples.append(elem.sample())

        # Verify general decay trend - later absolute values should be smaller
        # (accounting for sine wave oscillation by using running max)
        early_max = max(abs(s) for s in samples[:100])
        late_max = max(abs(s) for s in samples[900:])
        self.assertLess(late_max, early_max)


class TestPluckSamplePluck(unittest.TestCase):
    """Tests for Pluck sample_pluck method."""

    def test_sample_pluck_activates_element(self):
        """Check that sample_pluck activates the element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a)
        # Element is off initially
        self.assertEqual(elem.sample(), 0.0)
        # sample_pluck should activate
        result = elem.sample_pluck()
        self.assertAlmostEqual(result, 1.0, places=10)

    def test_sample_pluck_resets_time(self):
        """Check that sample_pluck resets pluck time."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a, lambda_dc=0.1)
        elem.set_on()
        # Advance time
        for _ in range(1000):
            elem.sample()
        decayed_sample = elem.sample()
        # Reset with sample_pluck
        fresh_sample = elem.sample_pluck()
        # Fresh sample should be larger (less decayed)
        self.assertGreater(abs(fresh_sample), abs(decayed_sample))

    def test_sample_pluck_with_scale(self):
        """Check that sample_pluck respects scale."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        elem = sl.Pluck(a=sound_a, scale=0.5)
        result = elem.sample_pluck()
        self.assertAlmostEqual(result, 0.5, places=10)

    def test_sample_pluck_without_a_element(self):
        """Check that sample_pluck with no a element returns 0.0."""
        elem = sl.Pluck()
        result = elem.sample_pluck()
        self.assertEqual(result, 0.0)


class TestPluckOnOff(unittest.TestCase):
    """Tests for Pluck set_on and set_off methods."""

    def test_set_on_activates(self):
        """Check that set_on activates the element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a)
        self.assertEqual(elem.sample(), 0.0)
        elem.set_on()
        self.assertNotEqual(elem.sample(), 0.0)

    def test_set_off_deactivates(self):
        """Check that set_off deactivates the element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a)
        elem.set_on()
        self.assertNotEqual(elem.sample(), 0.0)
        elem.set_off()
        self.assertEqual(elem.sample(), 0.0)

    def test_set_on_activates_sub_element(self):
        """Check that set_on activates the input element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(a=sound_a)
        # sound_a is not on, so even after pluck set_on, it should produce output
        elem.set_on()
        # The pluck's set_on should also call sound_a.set_on()
        self.assertAlmostEqual(elem.sample(), 1.0, places=5)

    def test_set_off_deactivates_sub_element(self):
        """Check that set_off deactivates the input element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        elem = sl.Pluck(a=sound_a)
        elem.set_on()
        elem.set_off()
        # After set_off, sample should be 0
        self.assertEqual(elem.sample(), 0.0)

    def test_set_on_with_no_element(self):
        """Check that set_on doesn't error with no element."""
        elem = sl.Pluck()
        elem.set_on()  # Should not raise
        self.assertEqual(elem.sample(), 0.0)

    def test_set_off_with_no_element(self):
        """Check that set_off doesn't error with no element."""
        elem = sl.Pluck()
        elem.set_off()  # Should not raise


class TestPluckDump(unittest.TestCase):
    """Tests for Pluck dump method."""

    def test_dump_returns_dict(self):
        """Check that dump returns a dictionary."""
        elem = sl.Pluck()
        result = elem.dump()
        self.assertIsInstance(result, dict)

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        elem = sl.Pluck()
        result = elem.dump()
        self.assertIn("get_scale", result)
        self.assertIn("get_lambda_dc", result)
        self.assertIn("get_type", result)
        self.assertIn("get_stop", result)
        self.assertIn("get_name", result)
        self.assertIn("get_sample_rate", result)
        self.assertIn("a", result)

    def test_dump_values_match_getters(self):
        """Check that dump values match getter methods."""
        elem = sl.Pluck(name="test_pluck", scale=0.75, stop=1.5, lambda_dc=0.05)
        result = elem.dump()
        self.assertEqual(result["get_scale"], elem.get_scale())
        self.assertEqual(result["get_lambda_dc"], elem.get_lambda_dc())
        self.assertEqual(result["get_type"], elem.get_type())
        self.assertEqual(result["get_stop"], elem.get_stop())
        self.assertEqual(result["get_name"], elem.get_name())
        self.assertEqual(result["get_sample_rate"], elem.get_sample_rate())

    def test_dump_with_sub_element(self):
        """Check that dump includes sub-element dump."""
        sound_a = sl.SoundElement(name="sub_a")
        elem = sl.Pluck(a=sound_a)
        result = elem.dump()
        self.assertIsNotNone(result["a"])
        self.assertEqual(result["a"]["get_name"], "sub_a")

    def test_dump_without_sub_element(self):
        """Check that dump handles missing sub-element."""
        elem = sl.Pluck()
        result = elem.dump()
        self.assertIsNone(result["a"])


class TestPluckMsg(unittest.TestCase):
    """Tests for Pluck msg method."""

    def test_msg_returns_dict(self):
        """Check that msg returns a dictionary."""
        elem = sl.Pluck(name="test_pluck")
        result = elem.msg({"test_pluck": {}})
        self.assertIsInstance(result, dict)

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.Pluck(name="test_pluck", scale=0.75)
        result = elem.msg({"test_pluck": {"get_scale": []}})
        self.assertEqual(result["test_pluck"]["get_scale"], 0.75)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.Pluck(name="test_pluck")
        elem.msg({"test_pluck": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_get_lambda_dc(self):
        """Check that msg can get lambda_dc."""
        elem = sl.Pluck(name="test_pluck", lambda_dc=0.1)
        result = elem.msg({"test_pluck": {"get_lambda_dc": []}})
        self.assertEqual(result["test_pluck"]["get_lambda_dc"], 0.1)

    def test_msg_set_lambda_dc(self):
        """Check that msg can set lambda_dc."""
        elem = sl.Pluck(name="test_pluck")
        elem.msg({"test_pluck": {"set_lambda_dc": [0.2]}})
        self.assertEqual(elem.get_lambda_dc(), 0.2)

    def test_msg_get_stop(self):
        """Check that msg can get stop."""
        elem = sl.Pluck(name="test_pluck", stop=3.0)
        result = elem.msg({"test_pluck": {"get_stop": []}})
        self.assertEqual(result["test_pluck"]["get_stop"], 3.0)

    def test_msg_set_stop(self):
        """Check that msg can set stop."""
        elem = sl.Pluck(name="test_pluck")
        elem.msg({"test_pluck": {"set_stop": [4.0]}})
        self.assertEqual(elem.get_stop(), 4.0)

    def test_msg_get_sample_rate(self):
        """Check that msg can get sample_rate."""
        elem = sl.Pluck(name="test_pluck", sample_rate=48000)
        result = elem.msg({"test_pluck": {"get_sample_rate": []}})
        self.assertEqual(result["test_pluck"]["get_sample_rate"], 48000)

    def test_msg_set_sample_rate(self):
        """Check that msg can set sample_rate."""
        elem = sl.Pluck(name="test_pluck")
        elem.msg({"test_pluck": {"set_sample_rate": [96000]}})
        self.assertEqual(elem.get_sample_rate(), 96000)

    def test_msg_get_type(self):
        """Check that msg can get type."""
        elem = sl.Pluck(name="test_pluck")
        result = elem.msg({"test_pluck": {"get_type": []}})
        self.assertEqual(result["test_pluck"]["get_type"], "Pluck")

    def test_msg_set_on(self):
        """Check that msg can activate element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(name="test_pluck", a=sound_a)
        self.assertEqual(elem.sample(), 0.0)
        elem.msg({"test_pluck": {"set_on": []}})
        self.assertNotEqual(elem.sample(), 0.0)

    def test_msg_set_off(self):
        """Check that msg can deactivate element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.Pluck(name="test_pluck", a=sound_a)
        elem.set_on()
        elem.msg({"test_pluck": {"set_off": []}})
        self.assertEqual(elem.sample(), 0.0)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.Pluck(name="test_pluck", scale=1.0)
        elem.msg({"other_elem": {"set_scale": [0.5]}})
        self.assertEqual(elem.get_scale(), 1.0)


class TestPluckNesting(unittest.TestCase):
    """Tests for Pluck with nested elements."""

    def test_pluck_with_sound_element(self):
        """Check basic Pluck with SoundElement."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        pluck = sl.Pluck(a=sound)
        pluck.set_on()
        self.assertAlmostEqual(pluck.sample(), 1.0, places=10)

    def test_pluck_with_multiply_elements(self):
        """Check Pluck with MultiplyElements input."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        mult = sl.MultiplyElements(a=s1, b=s2)  # 1.0 * 1.0 = 1.0
        pluck = sl.Pluck(a=mult)
        pluck.set_on()
        self.assertAlmostEqual(pluck.sample(), 1.0, places=10)

    def test_nested_pluck(self):
        """Check nested Pluck elements."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        inner_pluck = sl.Pluck(a=sound)
        outer_pluck = sl.Pluck(a=inner_pluck)
        outer_pluck.set_on()
        # Both plucks apply decay, but at t=0, both have factor 1.0
        self.assertAlmostEqual(outer_pluck.sample(), 1.0, places=10)

    def test_pluck_with_sum_elements(self):
        """Check Pluck with SumElements input."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        sum_elem = sl.SumElements(a=s1, b=s2, scale=0.5)  # (1+1)*0.5 = 1.0
        pluck = sl.Pluck(a=sum_elem)
        pluck.set_on()
        self.assertAlmostEqual(pluck.sample(), 1.0, places=10)


# =============================================================================
# FixedAttenuate Tests
# =============================================================================


class TestFixedAttenuateDefaults(unittest.TestCase):
    """Tests for FixedAttenuate default values after instantiation without arguments."""

    def test_default_type(self):
        """Check that default _TYPE is 'FixedAttenuate'."""
        elem = sl.FixedAttenuate()
        self.assertEqual(elem.get_type(), "FixedAttenuate")

    def test_default_name_format(self):
        """Check that default name starts with 'FixedAttenuate_'."""
        elem = sl.FixedAttenuate()
        self.assertTrue(elem.get_name().startswith("FixedAttenuate_"))

    def test_default_scale(self):
        """Check that default scale is 1.0."""
        elem = sl.FixedAttenuate()
        self.assertEqual(elem.get_scale(), 1.0)

    def test_default_sample_returns_zero(self):
        """Check that sample() returns 0.0 with no input."""
        elem = sl.FixedAttenuate()
        self.assertEqual(elem.sample(), 0.0)


class TestFixedAttenuateCustomArgs(unittest.TestCase):
    """Tests for FixedAttenuate initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        elem = sl.FixedAttenuate(name="my_attenuate")
        self.assertEqual(elem.get_name(), "my_attenuate")

    def test_custom_scale(self):
        """Check that custom scale is set correctly."""
        elem = sl.FixedAttenuate(scale=0.5)
        self.assertEqual(elem.get_scale(), 0.5)

    def test_custom_a_element(self):
        """Check that custom a element is set correctly."""
        sound_a = sl.SoundElement(name="input_a")
        elem = sl.FixedAttenuate(a=sound_a)
        result = elem.dump()
        self.assertIsNotNone(result["a"])
        self.assertEqual(result["a"]["get_name"], "input_a")

    def test_custom_scale_zero(self):
        """Check that scale=0 is allowed."""
        elem = sl.FixedAttenuate(scale=0.0)
        self.assertEqual(elem.get_scale(), 0.0)

    def test_custom_scale_negative(self):
        """Check that negative scale is allowed (phase inversion)."""
        elem = sl.FixedAttenuate(scale=-1.0)
        self.assertEqual(elem.get_scale(), -1.0)

    def test_custom_scale_greater_than_one(self):
        """Check that scale > 1.0 is allowed (amplification)."""
        elem = sl.FixedAttenuate(scale=2.0)
        self.assertEqual(elem.get_scale(), 2.0)


class TestFixedAttenuateSetters(unittest.TestCase):
    """Tests for FixedAttenuate setter methods."""

    def test_set_a(self):
        """Check that set_a updates the a element."""
        elem = sl.FixedAttenuate()
        sound_a = sl.SoundElement(name="new_a")
        elem.set_a(sound_a)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "new_a")

    def test_set_scale(self):
        """Check that set_scale updates the scale."""
        elem = sl.FixedAttenuate()
        elem.set_scale(0.25)
        self.assertEqual(elem.get_scale(), 0.25)

    def test_set_scale_zero(self):
        """Check that set_scale accepts zero."""
        elem = sl.FixedAttenuate()
        elem.set_scale(0.0)
        self.assertEqual(elem.get_scale(), 0.0)

    def test_set_scale_negative(self):
        """Check that set_scale accepts negative values."""
        elem = sl.FixedAttenuate()
        elem.set_scale(-0.5)
        self.assertEqual(elem.get_scale(), -0.5)

    def test_set_a_invalid_raises_error(self):
        """Check that set_a with invalid object raises ValueError."""
        elem = sl.FixedAttenuate()
        with self.assertRaises(ValueError):
            elem.set_a("not a sound element")

    def test_set_a_accepts_sound_element(self):
        """Check that set_a accepts SoundElement."""
        elem = sl.FixedAttenuate()
        sound = sl.SoundElement(name="sound_elem")
        elem.set_a(sound)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "sound_elem")

    def test_set_a_accepts_multiply_elements(self):
        """Check that set_a accepts MultiplyElements."""
        elem = sl.FixedAttenuate()
        mult = sl.MultiplyElements(name="mult_elem")
        elem.set_a(mult)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "mult_elem")

    def test_set_a_accepts_sum_elements(self):
        """Check that set_a accepts SumElements."""
        elem = sl.FixedAttenuate()
        sum_elem = sl.SumElements(name="sum_elem")
        elem.set_a(sum_elem)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "sum_elem")

    def test_set_a_accepts_mix_elements(self):
        """Check that set_a accepts MixElements."""
        elem = sl.FixedAttenuate()
        mix = sl.MixElements(name="mix_elem")
        elem.set_a(mix)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "mix_elem")

    def test_set_a_accepts_pluck(self):
        """Check that set_a accepts Pluck."""
        elem = sl.FixedAttenuate()
        pluck = sl.Pluck(name="pluck_elem")
        elem.set_a(pluck)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "pluck_elem")

    def test_set_a_accepts_fixed_attenuate(self):
        """Check that set_a accepts FixedAttenuate (nesting)."""
        elem = sl.FixedAttenuate()
        inner = sl.FixedAttenuate(name="inner_atten")
        elem.set_a(inner)
        result = elem.dump()
        self.assertEqual(result["a"]["get_name"], "inner_atten")


class TestFixedAttenuateSample(unittest.TestCase):
    """Tests for FixedAttenuate sample method."""

    def test_sample_with_no_input(self):
        """Check that sample returns 0.0 with no input."""
        elem = sl.FixedAttenuate()
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_scale_one(self):
        """Check that scale=1.0 passes signal unchanged."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=1.0)
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_with_scale_half(self):
        """Check that scale=0.5 halves the signal."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=0.5)
        self.assertAlmostEqual(elem.sample(), 0.5, places=10)

    def test_sample_with_scale_zero(self):
        """Check that scale=0 produces zero output."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=0.0)
        self.assertEqual(elem.sample(), 0.0)

    def test_sample_with_scale_negative(self):
        """Check that negative scale inverts phase."""
        sound_a = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=-1.0)
        self.assertAlmostEqual(elem.sample(), -1.0, places=10)

    def test_sample_with_scale_amplify(self):
        """Check that scale > 1.0 amplifies signal."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # sin(pi/6) = 0.5
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=2.0)
        self.assertAlmostEqual(elem.sample(), 1.0, places=10)

    def test_sample_advances_phase(self):
        """Check that sample advances phase of sub-element."""
        sound_a = sl.SoundElement(phase=0.0, frequency=440)
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a)
        sample1 = elem.sample()
        sample2 = elem.sample()
        # Samples should differ as phase advances
        self.assertNotEqual(sample1, sample2)

    def test_sample_formula(self):
        """Check the attenuation formula A * scale."""
        sound_a = sl.SoundElement(phase=math.pi / 6)  # 0.5
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a, scale=0.6)
        # 0.5 * 0.6 = 0.3
        self.assertAlmostEqual(elem.sample(), 0.3, places=10)


class TestFixedAttenuateOnOff(unittest.TestCase):
    """Tests for FixedAttenuate set_on and set_off methods."""

    def test_set_on_activates_sub_element(self):
        """Check that set_on activates the input element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        elem = sl.FixedAttenuate(a=sound_a)
        # Before set_on, sub-element is off, so sample should be 0
        self.assertEqual(elem.sample(), 0.0)
        # After set_on
        elem.set_on()
        self.assertAlmostEqual(elem.sample(), 1.0, places=5)

    def test_set_off_deactivates_sub_element(self):
        """Check that set_off deactivates the input element."""
        sound_a = sl.SoundElement(phase=math.pi / 2)
        sound_a.set_on()
        elem = sl.FixedAttenuate(a=sound_a)
        # Should have output
        self.assertAlmostEqual(elem.sample(), 1.0, places=5)
        # After set_off, should eventually return to 0
        elem.set_off()
        for _ in range(1000):
            elem.sample()
        self.assertAlmostEqual(elem.sample(), 0.0, places=5)

    def test_set_on_with_no_element(self):
        """Check that set_on doesn't error with no element."""
        elem = sl.FixedAttenuate()
        elem.set_on()  # Should not raise
        self.assertEqual(elem.sample(), 0.0)

    def test_set_off_with_no_element(self):
        """Check that set_off doesn't error with no element."""
        elem = sl.FixedAttenuate()
        elem.set_off()  # Should not raise


class TestFixedAttenuateDump(unittest.TestCase):
    """Tests for FixedAttenuate dump method."""

    def test_dump_returns_dict(self):
        """Check that dump returns a dictionary."""
        elem = sl.FixedAttenuate()
        result = elem.dump()
        self.assertIsInstance(result, dict)

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        elem = sl.FixedAttenuate()
        result = elem.dump()
        self.assertIn("get_scale", result)
        self.assertIn("get_type", result)
        self.assertIn("get_name", result)
        self.assertIn("a", result)

    def test_dump_values_match_getters(self):
        """Check that dump values match getter methods."""
        elem = sl.FixedAttenuate(name="test_atten", scale=0.75)
        result = elem.dump()
        self.assertEqual(result["get_scale"], elem.get_scale())
        self.assertEqual(result["get_type"], elem.get_type())
        self.assertEqual(result["get_name"], elem.get_name())

    def test_dump_with_sub_element(self):
        """Check that dump includes sub-element dump."""
        sound_a = sl.SoundElement(name="sub_a")
        elem = sl.FixedAttenuate(a=sound_a)
        result = elem.dump()
        self.assertIsNotNone(result["a"])
        self.assertEqual(result["a"]["get_name"], "sub_a")

    def test_dump_without_sub_element(self):
        """Check that dump handles missing sub-element."""
        elem = sl.FixedAttenuate()
        result = elem.dump()
        self.assertIsNone(result["a"])


class TestFixedAttenuateMsg(unittest.TestCase):
    """Tests for FixedAttenuate msg method."""

    def test_msg_returns_dict(self):
        """Check that msg returns a dictionary."""
        elem = sl.FixedAttenuate(name="test_atten")
        result = elem.msg({"test_atten": {}})
        self.assertIsInstance(result, dict)

    def test_msg_get_scale(self):
        """Check that msg can get scale."""
        elem = sl.FixedAttenuate(name="test_atten", scale=0.75)
        result = elem.msg({"test_atten": {"get_scale": []}})
        self.assertEqual(result["test_atten"]["get_scale"], 0.75)

    def test_msg_set_scale(self):
        """Check that msg can set scale."""
        elem = sl.FixedAttenuate(name="test_atten")
        elem.msg({"test_atten": {"set_scale": [0.25]}})
        self.assertEqual(elem.get_scale(), 0.25)

    def test_msg_get_type(self):
        """Check that msg can get type."""
        elem = sl.FixedAttenuate(name="test_atten")
        result = elem.msg({"test_atten": {"get_type": []}})
        self.assertEqual(result["test_atten"]["get_type"], "FixedAttenuate")

    def test_msg_get_name(self):
        """Check that msg can get name."""
        elem = sl.FixedAttenuate(name="test_atten")
        result = elem.msg({"test_atten": {"get_name": []}})
        self.assertEqual(result["test_atten"]["get_name"], "test_atten")

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        elem = sl.FixedAttenuate(name="test_atten", scale=1.0)
        elem.msg({"other_elem": {"set_scale": [0.5]}})
        self.assertEqual(elem.get_scale(), 1.0)

    def test_msg_propagates_to_sub_element(self):
        """Check that msg propagates to sub-element."""
        sound_a = sl.SoundElement(name="sub_sound", frequency=440)
        elem = sl.FixedAttenuate(name="test_atten", a=sound_a)
        # Set frequency via msg on the sub-element
        elem.msg({"sub_sound": {"set_frequency": [880]}})
        # Verify the sub-element was updated
        self.assertEqual(sound_a._frequency, 880)


class TestFixedAttenuateNesting(unittest.TestCase):
    """Tests for FixedAttenuate with nested elements."""

    def test_attenuate_with_sound_element(self):
        """Check basic FixedAttenuate with SoundElement."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        atten = sl.FixedAttenuate(a=sound, scale=0.5)
        self.assertAlmostEqual(atten.sample(), 0.5, places=10)

    def test_nested_attenuate(self):
        """Check nested FixedAttenuate elements."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        inner = sl.FixedAttenuate(a=sound, scale=0.5)  # 1.0 * 0.5 = 0.5
        outer = sl.FixedAttenuate(a=inner, scale=0.5)  # 0.5 * 0.5 = 0.25
        self.assertAlmostEqual(outer.sample(), 0.25, places=10)

    def test_attenuate_with_multiply_elements(self):
        """Check FixedAttenuate with MultiplyElements input."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        mult = sl.MultiplyElements(a=s1, b=s2)  # 1.0 * 1.0 = 1.0
        atten = sl.FixedAttenuate(a=mult, scale=0.5)
        self.assertAlmostEqual(atten.sample(), 0.5, places=10)

    def test_attenuate_with_sum_elements(self):
        """Check FixedAttenuate with SumElements input."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        sum_elem = sl.SumElements(a=s1, b=s2, scale=0.5)  # (1+1)*0.5 = 1.0
        atten = sl.FixedAttenuate(a=sum_elem, scale=0.5)
        self.assertAlmostEqual(atten.sample(), 0.5, places=10)

    def test_attenuate_chain(self):
        """Check chain of FixedAttenuate elements."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        a1 = sl.FixedAttenuate(a=sound, scale=0.8)    # 0.8
        a2 = sl.FixedAttenuate(a=a1, scale=0.5)       # 0.4
        a3 = sl.FixedAttenuate(a=a2, scale=0.5)       # 0.2
        self.assertAlmostEqual(a3.sample(), 0.2, places=10)


# =============================================================================
# Chord Tests
# =============================================================================


class TestChordDefaults(unittest.TestCase):
    """Tests for Chord default values after instantiation without arguments."""

    def test_default_type(self):
        """Check that default _TYPE is 'Chord'."""
        chord = sl.Chord()
        self.assertEqual(chord.get_type(), "Chord")

    def test_default_name_format(self):
        """Check that default name starts with 'Chord_'."""
        chord = sl.Chord()
        self.assertTrue(chord.get_name().startswith("Chord_"))

    def test_default_name_is_unique(self):
        """Check that each instance gets a unique name."""
        chord1 = sl.Chord()
        chord2 = sl.Chord()
        self.assertNotEqual(chord1.get_name(), chord2.get_name())

    def test_default_note_is_none(self):
        """Check that default underlying element is None."""
        chord = sl.Chord()
        self.assertIsNone(chord.get_note())

    def test_default_sample_returns_zero(self):
        """Check that sample() returns 0.0 with no underlying element."""
        chord = sl.Chord()
        self.assertEqual(chord.sample(), 0.0)


class TestChordCustomArgs(unittest.TestCase):
    """Tests for Chord initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        chord = sl.Chord(name="my_chord")
        self.assertEqual(chord.get_name(), "my_chord")

    def test_custom_note_sound_element(self):
        """Check that custom SoundElement note is set correctly."""
        sound = sl.SoundElement(name="my_sound")
        chord = sl.Chord(note=sound, name="test_chord")
        self.assertEqual(chord.get_note(), sound)

    def test_custom_note_pluck(self):
        """Check that custom Pluck note is set correctly."""
        pluck = sl.Pluck(name="my_pluck")
        chord = sl.Chord(note=pluck, name="test_chord")
        self.assertEqual(chord.get_note(), pluck)

    def test_custom_note_sum_elements(self):
        """Check that custom SumElements note is set correctly."""
        sum_elem = sl.SumElements(name="my_sum")
        chord = sl.Chord(note=sum_elem, name="test_chord")
        self.assertEqual(chord.get_note(), sum_elem)

    def test_custom_note_mix_elements(self):
        """Check that custom MixElements note is set correctly."""
        mix = sl.MixElements(name="my_mix")
        chord = sl.Chord(note=mix, name="test_chord")
        self.assertEqual(chord.get_note(), mix)

    def test_custom_note_multiply_elements(self):
        """Check that custom MultiplyElements note is set correctly."""
        mult = sl.MultiplyElements(name="my_mult")
        chord = sl.Chord(note=mult, name="test_chord")
        self.assertEqual(chord.get_note(), mult)

    def test_custom_note_fixed_attenuate(self):
        """Check that custom FixedAttenuate note is set correctly."""
        atten = sl.FixedAttenuate(name="my_atten")
        chord = sl.Chord(note=atten, name="test_chord")
        self.assertEqual(chord.get_note(), atten)

    def test_custom_note_chord_unwraps(self):
        """Check that passing a Chord extracts its underlying element."""
        sound = sl.SoundElement(name="inner_sound")
        inner_chord = sl.Chord(note=sound, name="inner_chord")
        outer_chord = sl.Chord(note=inner_chord, name="outer_chord")
        # The outer chord should have the sound element, not the inner chord
        self.assertEqual(outer_chord.get_note(), sound)


class TestChordValidation(unittest.TestCase):
    """Tests for Chord constructor validation."""

    def test_invalid_note_raises_error(self):
        """Check that invalid note type raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Chord(note="not a sound element")

    def test_invalid_note_object_raises_error(self):
        """Check that non-sound object raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Chord(note={"invalid": "dict"})

    def test_invalid_note_number_raises_error(self):
        """Check that number raises ValueError."""
        with self.assertRaises(ValueError):
            sl.Chord(note=42)


class TestChordSetters(unittest.TestCase):
    """Tests for Chord setter methods."""

    def test_set_name(self):
        """Check that set_name updates the name."""
        chord = sl.Chord()
        chord.set_name("new_name")
        self.assertEqual(chord.get_name(), "new_name")

    def test_set_note(self):
        """Check that set_note updates the underlying element."""
        chord = sl.Chord()
        sound = sl.SoundElement(name="new_sound")
        chord.set_note(sound)
        self.assertEqual(chord.get_note(), sound)

    def test_set_note_replaces_existing(self):
        """Check that set_note replaces existing element."""
        sound1 = sl.SoundElement(name="sound1")
        sound2 = sl.SoundElement(name="sound2")
        chord = sl.Chord(note=sound1)
        chord.set_note(sound2)
        self.assertEqual(chord.get_note(), sound2)

    def test_set_note_none(self):
        """Check that set_note accepts None."""
        sound = sl.SoundElement(name="sound")
        chord = sl.Chord(note=sound)
        chord.set_note(None)
        self.assertIsNone(chord.get_note())

    def test_set_note_invalid_raises_error(self):
        """Check that set_note with invalid type raises ValueError."""
        chord = sl.Chord()
        with self.assertRaises(ValueError):
            chord.set_note("invalid")

    def test_set_a_alias(self):
        """Check that set_a is an alias for set_note."""
        chord = sl.Chord()
        sound = sl.SoundElement(name="via_set_a")
        chord.set_a(sound)
        self.assertEqual(chord.get_note(), sound)

    def test_set_a_accepts_all_valid_types(self):
        """Check that set_a accepts all valid sound element types."""
        chord = sl.Chord()

        types_to_test = [
            sl.SoundElement(name="sound"),
            sl.SumElements(name="sum"),
            sl.MixElements(name="mix"),
            sl.MultiplyElements(name="mult"),
            sl.Pluck(name="pluck"),
            sl.FixedAttenuate(name="atten"),
        ]

        for elem in types_to_test:
            chord.set_a(elem)
            self.assertEqual(chord.get_note(), elem)


class TestChordSample(unittest.TestCase):
    """Tests for Chord sample method."""

    def test_sample_with_no_note(self):
        """Check that sample returns 0.0 with no underlying element."""
        chord = sl.Chord()
        self.assertEqual(chord.sample(), 0.0)

    def test_sample_with_sound_element(self):
        """Check that sample delegates to underlying SoundElement."""
        sound = sl.SoundElement(phase=math.pi / 2)  # sin(pi/2) = 1.0
        sound.set_on()
        chord = sl.Chord(note=sound)
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_sample_with_scaled_element(self):
        """Check that sample returns scaled value from underlying element."""
        sound = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5 * sin(pi/2) = 0.5
        sound.set_on()
        chord = sl.Chord(note=sound)
        self.assertAlmostEqual(chord.sample(), 0.5, places=10)

    def test_sample_with_pluck(self):
        """Check that sample works with Pluck element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound)
        pluck.set_on()
        chord = sl.Chord(note=pluck)
        # At t=0, decay factor is e^0 = 1.0
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_sample_with_sum_elements(self):
        """Check that sample works with SumElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        sum_elem = sl.SumElements(a=s1, b=s2, scale=0.5)  # (1+1)*0.5 = 1.0
        chord = sl.Chord(note=sum_elem)
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_sample_multiple_calls(self):
        """Check that multiple sample calls advance the underlying element."""
        sound = sl.SoundElement(phase=0.0)
        sound.set_on()
        chord = sl.Chord(note=sound)

        samples = [chord.sample() for _ in range(10)]
        # Samples should change as sine wave advances
        self.assertNotEqual(samples[0], samples[5])


class TestChordSamplePluck(unittest.TestCase):
    """Tests for Chord sample_pluck method."""

    def test_sample_pluck_with_pluck_element(self):
        """Check that sample_pluck works with Pluck element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound)
        chord = sl.Chord(note=pluck)
        # sample_pluck should activate and return sample
        sample = chord.sample_pluck()
        self.assertAlmostEqual(sample, 1.0, places=10)

    def test_sample_pluck_resets_pluck_time(self):
        """Check that sample_pluck resets the pluck time."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound, lambda_dc=0.1)
        chord = sl.Chord(note=pluck)

        # First pluck
        chord.sample_pluck()
        # Advance several samples (decay should happen)
        for _ in range(100):
            chord.sample()
        decayed_sample = chord.sample()

        # Second pluck should reset
        fresh_sample = chord.sample_pluck()
        self.assertGreater(fresh_sample, decayed_sample)

    def test_sample_pluck_without_pluck_raises_error(self):
        """Check that sample_pluck with non-Pluck element raises TypeError."""
        sound = sl.SoundElement(phase=math.pi / 2)
        chord = sl.Chord(note=sound)
        with self.assertRaises(TypeError):
            chord.sample_pluck()

    def test_sample_pluck_with_no_note_raises_error(self):
        """Check that sample_pluck with no element raises TypeError."""
        chord = sl.Chord()
        with self.assertRaises(TypeError):
            chord.sample_pluck()


class TestChordOnOff(unittest.TestCase):
    """Tests for Chord set_on and set_off methods."""

    def test_set_on_activates_underlying_element(self):
        """Check that set_on activates the underlying element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        chord = sl.Chord(note=sound)
        chord.set_on()
        # After set_on, sample should return non-zero
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_set_off_deactivates_underlying_element(self):
        """Check that set_off deactivates the underlying element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        chord = sl.Chord(note=sound)
        chord.set_on()
        # Verify it's on
        self.assertNotEqual(chord.sample(), 0.0)
        chord.set_off()
        # After set_off and settling, should return zero
        for _ in range(1000):
            chord.sample()
        self.assertEqual(chord.sample(), 0.0)

    def test_set_on_with_no_note(self):
        """Check that set_on with no element doesn't raise error."""
        chord = sl.Chord()
        chord.set_on()  # Should not raise

    def test_set_off_with_no_note(self):
        """Check that set_off with no element doesn't raise error."""
        chord = sl.Chord()
        chord.set_off()  # Should not raise

    def test_set_on_propagates_to_pluck(self):
        """Check that set_on propagates to Pluck element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound)
        chord = sl.Chord(note=pluck)
        chord.set_on()
        # Pluck should be on and return a value
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_set_off_propagates_to_pluck(self):
        """Check that set_off propagates to Pluck element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound)
        chord = sl.Chord(note=pluck)
        chord.set_on()
        chord.sample()  # Get one sample
        chord.set_off()
        # After set_off, Pluck should return 0
        self.assertEqual(chord.sample(), 0.0)


class TestChordDump(unittest.TestCase):
    """Tests for Chord dump method."""

    def test_dump_contains_all_properties(self):
        """Check that dump returns all expected properties."""
        chord = sl.Chord(name="test_chord")
        dump = chord.dump()

        self.assertIn("get_type", dump)
        self.assertIn("get_name", dump)
        self.assertIn("a", dump)

    def test_dump_values_match(self):
        """Check that dump values match the chord's properties."""
        chord = sl.Chord(name="test_chord")
        dump = chord.dump()

        self.assertEqual(dump["get_type"], "Chord")
        self.assertEqual(dump["get_name"], "test_chord")
        self.assertIsNone(dump["a"])

    def test_dump_with_sound_element(self):
        """Check that dump includes underlying SoundElement."""
        sound = sl.SoundElement(name="inner_sound", frequency=880.0)
        chord = sl.Chord(note=sound, name="test_chord")
        dump = chord.dump()

        self.assertIsNotNone(dump["a"])
        self.assertEqual(dump["a"]["get_name"], "inner_sound")
        self.assertEqual(dump["a"]["get_frequency"], 880.0)
        self.assertEqual(dump["a"]["get_type"], "SoundElement")

    def test_dump_with_pluck(self):
        """Check that dump includes Pluck element and its hierarchy."""
        sound = sl.SoundElement(name="inner_sound")
        pluck = sl.Pluck(a=sound, name="inner_pluck", lambda_dc=0.05)
        chord = sl.Chord(note=pluck, name="test_chord")
        dump = chord.dump()

        self.assertIsNotNone(dump["a"])
        self.assertEqual(dump["a"]["get_name"], "inner_pluck")
        self.assertEqual(dump["a"]["get_type"], "Pluck")
        self.assertEqual(dump["a"]["get_lambda_dc"], 0.05)
        self.assertIsNotNone(dump["a"]["a"])
        self.assertEqual(dump["a"]["a"]["get_name"], "inner_sound")

    def test_dump_with_nested_hierarchy(self):
        """Check that dump captures full nested hierarchy."""
        s1 = sl.SoundElement(name="s1")
        s2 = sl.SoundElement(name="s2")
        sum_elem = sl.SumElements(a=s1, b=s2, name="sum")
        pluck = sl.Pluck(a=sum_elem, name="pluck")
        chord = sl.Chord(note=pluck, name="chord")
        dump = chord.dump()

        self.assertEqual(dump["get_name"], "chord")
        self.assertEqual(dump["a"]["get_name"], "pluck")
        self.assertEqual(dump["a"]["a"]["get_name"], "sum")
        self.assertEqual(dump["a"]["a"]["a"]["get_name"], "s1")
        self.assertEqual(dump["a"]["a"]["b"]["get_name"], "s2")


class TestChordMsg(unittest.TestCase):
    """Tests for Chord msg method."""

    def test_msg_get_name(self):
        """Check that msg can get name."""
        chord = sl.Chord(name="test_chord")
        result = chord.msg({"test_chord": {"get_name": []}})
        self.assertEqual(result["test_chord"]["get_name"], "test_chord")

    def test_msg_get_type(self):
        """Check that msg can get type."""
        chord = sl.Chord(name="test_chord")
        result = chord.msg({"test_chord": {"get_type": []}})
        self.assertEqual(result["test_chord"]["get_type"], "Chord")

    def test_msg_set_name(self):
        """Check that msg can set name."""
        chord = sl.Chord(name="old_name")
        chord.msg({"old_name": {"set_name": ["new_name"]}})
        self.assertEqual(chord.get_name(), "new_name")

    def test_msg_set_on(self):
        """Check that msg can activate chord."""
        sound = sl.SoundElement(phase=math.pi / 2, name="sound")
        chord = sl.Chord(note=sound, name="test_chord")
        chord.msg({"test_chord": {"set_on": []}})
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_msg_set_off(self):
        """Check that msg can deactivate chord."""
        sound = sl.SoundElement(phase=math.pi / 2, name="sound")
        chord = sl.Chord(note=sound, name="test_chord")
        chord.set_on()
        chord.sample()
        chord.msg({"test_chord": {"set_off": []}})
        # After settling
        for _ in range(1000):
            chord.sample()
        self.assertEqual(chord.sample(), 0.0)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        chord = sl.Chord(name="test_chord")
        result = chord.msg({"other_name": {"get_type": []}})
        # Result should have chord's name but no data from other_name
        self.assertIn("test_chord", result)
        self.assertNotIn("get_type", result["test_chord"])

    def test_msg_propagates_to_subelement(self):
        """Check that msg propagates to underlying element."""
        sound = sl.SoundElement(name="inner_sound", frequency=440.0)
        chord = sl.Chord(note=sound, name="test_chord")

        # Send message to the inner sound
        result = chord.msg({"inner_sound": {"get_frequency": []}})

        # The result should contain the nested response
        self.assertIn("a", result["test_chord"])
        self.assertEqual(
            result["test_chord"]["a"]["inner_sound"]["get_frequency"], 440.0
        )

    def test_msg_propagates_set_frequency_to_subelement(self):
        """Check that msg can set properties on underlying element."""
        sound = sl.SoundElement(name="inner_sound", frequency=440.0)
        chord = sl.Chord(note=sound, name="test_chord")

        # Set frequency on inner sound
        chord.msg({"inner_sound": {"set_frequency": [880.0]}})

        self.assertEqual(sound.get_frequency(), 880.0)

    def test_msg_propagates_regardless_of_name_match(self):
        """Check that msg propagates to subelement even if chord name doesn't match."""
        sound = sl.SoundElement(name="inner_sound", phase=math.pi / 2)
        chord = sl.Chord(note=sound, name="test_chord")

        # Message doesn't match chord name, but should still propagate
        result = chord.msg({"inner_sound": {"set_on": []}})

        # Sound should be activated
        sample = sound.sample()
        self.assertAlmostEqual(sample, 1.0, places=10)

    def test_msg_multiple_commands(self):
        """Check that msg can handle multiple commands."""
        chord = sl.Chord(name="test_chord")
        result = chord.msg({
            "test_chord": {
                "get_name": [],
                "get_type": []
            }
        })
        self.assertEqual(result["test_chord"]["get_name"], "test_chord")
        self.assertEqual(result["test_chord"]["get_type"], "Chord")

    def test_msg_set_name_uses_current_name_for_return(self):
        """Check that msg uses current name for return value after set_name."""
        chord = sl.Chord(name="old_name")
        result = chord.msg({"old_name": {"set_name": ["new_name"], "get_type": []}})
        # The return should use the original name (captured at start)
        self.assertIn("old_name", result)


class TestChordMakeAChord(unittest.TestCase):
    """Tests for Chord make_a_chord factory method."""

    def test_make_major_chord(self):
        """Check that make_a_chord creates a major chord."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        self.assertIsNotNone(chord)
        self.assertEqual(chord.get_type(), "Chord")
        self.assertEqual(chord.get_name(), "4Cmajor")

    def test_make_minor_chord(self):
        """Check that make_a_chord creates a minor chord."""
        chord = sl.Chord().make_a_chord((4, "A", "minor"))
        self.assertEqual(chord.get_name(), "4Aminor")

    def test_make_7th_chord(self):
        """Check that make_a_chord creates a dominant 7th chord."""
        chord = sl.Chord().make_a_chord((4, "G", "7"))
        self.assertEqual(chord.get_name(), "4G7")

    def test_make_maj7_chord(self):
        """Check that make_a_chord creates a major 7th chord."""
        chord = sl.Chord().make_a_chord((5, "C", "maj7"))
        self.assertEqual(chord.get_name(), "5Cmaj7")

    def test_make_dim_chord(self):
        """Check that make_a_chord creates a diminished chord."""
        chord = sl.Chord().make_a_chord((4, "B", "dim"))
        self.assertEqual(chord.get_name(), "4Bdim")

    def test_make_aug_chord(self):
        """Check that make_a_chord creates an augmented chord."""
        chord = sl.Chord().make_a_chord((4, "C", "aug"))
        self.assertEqual(chord.get_name(), "4Caug")

    def test_make_sus4_chord(self):
        """Check that make_a_chord creates a sus4 chord."""
        chord = sl.Chord().make_a_chord((4, "D", "sus4"))
        self.assertEqual(chord.get_name(), "4Dsus4")

    def test_make_add9_chord(self):
        """Check that make_a_chord creates an add9 chord."""
        chord = sl.Chord().make_a_chord((4, "C", "add9"))
        self.assertEqual(chord.get_name(), "4Cadd9")

    def test_make_power_chord(self):
        """Check that make_a_chord creates a power chord (5)."""
        chord = sl.Chord().make_a_chord((4, "E", "5"))
        self.assertEqual(chord.get_name(), "4E5")

    def test_make_6_9_chord(self):
        """Check that 6/9 chord is not confused with slash chord."""
        chord = sl.Chord().make_a_chord((4, "C", "6/9"))
        self.assertEqual(chord.get_name(), "4C6/9")

    def test_make_chord_with_sharp(self):
        """Check that sharp notes work correctly."""
        chord = sl.Chord().make_a_chord((4, "C#", "major"))
        self.assertEqual(chord.get_name(), "4C#major")

    def test_make_chord_with_flat(self):
        """Check that flat notes work correctly."""
        chord = sl.Chord().make_a_chord((4, "Bb", "minor"))
        self.assertEqual(chord.get_name(), "4Bbminor")

    def test_make_chord_different_octaves(self):
        """Check that different octaves produce different pitches."""
        chord_low = sl.Chord().make_a_chord((3, "C", "major"))
        chord_high = sl.Chord().make_a_chord((5, "C", "major"))
        # Names should reflect different octaves
        self.assertEqual(chord_low.get_name(), "3Cmajor")
        self.assertEqual(chord_high.get_name(), "5Cmajor")

    def test_make_chord_with_pluck_true(self):
        """Check that pluck=True wraps chord in Pluck."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
        # The underlying note should be a Pluck
        self.assertIsInstance(chord.get_note(), sl.Pluck)

    def test_make_chord_with_pluck_false(self):
        """Check that pluck=False does not wrap in Pluck."""
        chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=False)
        # The underlying note should not be a Pluck (should be SumElements or similar)
        self.assertNotIsInstance(chord.get_note(), sl.Pluck)

    def test_make_chord_with_sum_mix(self):
        """Check that SUM mix type uses SumElements."""
        chord = sl.Chord().make_a_chord(
            (4, "C", "major"),
            mix=sl.Chord.MixType.SUM,
            pluck=False
        )
        # Should produce SumElements hierarchy
        self.assertEqual(chord.get_note().get_type(), "SumElements")

    def test_make_chord_with_mix_mix(self):
        """Check that MIX mix type uses MixElements."""
        chord = sl.Chord().make_a_chord(
            (4, "C", "major"),
            mix=sl.Chord.MixType.MIX,
            pluck=False
        )
        self.assertEqual(chord.get_note().get_type(), "MixElements")

    def test_make_chord_produces_sound(self):
        """Check that created chord produces sound samples."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        chord.get_note().set_on()
        sample = chord.sample()
        self.assertIsInstance(sample, float)


class TestChordMakeAChordSlash(unittest.TestCase):
    """Tests for Chord make_a_chord with slash chord notation."""

    def test_slash_chord_major_over_e(self):
        """Check that C/E creates a C major with E bass."""
        chord = sl.Chord().make_a_chord((4, "C", "major/E"))
        self.assertEqual(chord.get_name(), "4Cmajor/E")

    def test_slash_chord_minor_over_g(self):
        """Check that Am/G creates an A minor with G bass."""
        chord = sl.Chord().make_a_chord((4, "A", "minor/G"))
        self.assertEqual(chord.get_name(), "4Aminor/G")

    def test_slash_chord_7th_over_sharp(self):
        """Check that G7/F# creates a G7 with F# bass."""
        chord = sl.Chord().make_a_chord((4, "G", "7/F#"))
        self.assertEqual(chord.get_name(), "4G7/F#")

    def test_slash_chord_with_flat_bass(self):
        """Check that chord with flat bass note works."""
        chord = sl.Chord().make_a_chord((4, "C", "major/Bb"))
        self.assertEqual(chord.get_name(), "4Cmajor/Bb")

    def test_slash_chord_produces_sound(self):
        """Check that slash chord produces sound."""
        chord = sl.Chord().make_a_chord((4, "C", "major/E"))
        chord.get_note().set_on()
        sample = chord.sample()
        self.assertIsInstance(sample, float)

    def test_6_9_not_confused_with_slash(self):
        """Check that 6/9 chord type is not parsed as slash chord."""
        chord = sl.Chord().make_a_chord((4, "C", "6/9"))
        # Should be 6/9 chord type, not C6 with a 9 bass
        self.assertEqual(chord.get_name(), "4C6/9")


class TestChordMakeAChordOmit(unittest.TestCase):
    """Tests for Chord make_a_chord with omit notation."""

    def test_omit5(self):
        """Check that (omit5) creates chord without 5th."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit5)"))
        self.assertEqual(chord.get_name(), "4Cmajor(omit5)")

    def test_omit3(self):
        """Check that (omit3) creates chord without 3rd."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit3)"))
        self.assertEqual(chord.get_name(), "4Cmajor(omit3)")

    def test_omit_root(self):
        """Check that (omit1) or (omitroot) creates chord without root."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit1)"))
        self.assertEqual(chord.get_name(), "4Cmajor(omit1)")

    def test_omit_multiple(self):
        """Check that (omit3,5) creates chord without 3rd and 5th."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit3,5)"))
        self.assertEqual(chord.get_name(), "4Cmajor(omit3,5)")

    def test_omit_with_7th_chord(self):
        """Check that omit works with 7th chords."""
        chord = sl.Chord().make_a_chord((4, "C", "maj7(omit5)"))
        self.assertEqual(chord.get_name(), "4Cmaj7(omit5)")

    def test_omit_with_slash(self):
        """Check that omit works with slash notation."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit5)/E"))
        self.assertEqual(chord.get_name(), "4Cmajor(omit5)/E")

    def test_omit_produces_sound(self):
        """Check that omit chord produces sound."""
        chord = sl.Chord().make_a_chord((4, "C", "major(omit5)"))
        chord.get_note().set_on()
        sample = chord.sample()
        self.assertIsInstance(sample, float)


class TestChordFactory(unittest.TestCase):
    """Tests for Chord factory methods (recursive_walk, note_factory_hier_db)."""

    def test_factory_simple_sound_element(self):
        """Check that factory can recreate a simple SoundElement hierarchy."""
        original = sl.SoundElement(name="test_sound", frequency=880.0, scale=0.75)
        sound_chord = sl.Chord(note=original, name="original_chord")
        dump = sound_chord.dump()

        # Create new chord from dump
        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "original_chord")
        restored_note = restored.get_note()
        self.assertEqual(restored_note.get_name(), "test_sound")
        self.assertEqual(restored_note.get_frequency(), 880.0)
        self.assertEqual(restored_note.get_scale(), 0.75)

    def test_factory_pluck_hierarchy(self):
        """Check that factory can recreate Pluck hierarchy."""
        sound = sl.SoundElement(name="inner_sound", frequency=440.0)
        pluck = sl.Pluck(a=sound, name="test_pluck", lambda_dc=0.05, stop=1.5)
        original = sl.Chord(note=pluck, name="pluck_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "pluck_chord")
        restored_pluck = restored.get_note()
        self.assertEqual(restored_pluck.get_name(), "test_pluck")
        self.assertEqual(restored_pluck.get_lambda_dc(), 0.05)
        self.assertEqual(restored_pluck.get_stop(), 1.5)

    def test_factory_sum_elements_hierarchy(self):
        """Check that factory can recreate SumElements hierarchy."""
        s1 = sl.SoundElement(name="s1", frequency=440.0)
        s2 = sl.SoundElement(name="s2", frequency=880.0)
        sum_elem = sl.SumElements(a=s1, b=s2, name="test_sum", scale=0.4)
        original = sl.Chord(note=sum_elem, name="sum_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "sum_chord")
        restored_sum = restored.get_note()
        self.assertEqual(restored_sum.get_name(), "test_sum")
        self.assertEqual(restored_sum.get_scale(), 0.4)

    def test_factory_mix_elements_hierarchy(self):
        """Check that factory can recreate MixElements hierarchy."""
        s1 = sl.SoundElement(name="s1")
        s2 = sl.SoundElement(name="s2")
        mix = sl.MixElements(a=s1, b=s2, name="test_mix", scale=0.8)
        original = sl.Chord(note=mix, name="mix_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "mix_chord")
        restored_mix = restored.get_note()
        self.assertEqual(restored_mix.get_name(), "test_mix")
        self.assertEqual(restored_mix.get_scale(), 0.8)

    def test_factory_multiply_elements_hierarchy(self):
        """Check that factory can recreate MultiplyElements hierarchy."""
        s1 = sl.SoundElement(name="s1")
        s2 = sl.SoundElement(name="s2")
        mult = sl.MultiplyElements(a=s1, b=s2, name="test_mult", scale=0.9)
        original = sl.Chord(note=mult, name="mult_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "mult_chord")
        restored_mult = restored.get_note()
        self.assertEqual(restored_mult.get_name(), "test_mult")
        self.assertEqual(restored_mult.get_scale(), 0.9)

    def test_factory_fixed_attenuate_hierarchy(self):
        """Check that factory can recreate FixedAttenuate hierarchy."""
        sound = sl.SoundElement(name="inner_sound")
        atten = sl.FixedAttenuate(a=sound, name="test_atten", scale=0.3)
        original = sl.Chord(note=atten, name="atten_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "atten_chord")
        restored_atten = restored.get_note()
        self.assertEqual(restored_atten.get_name(), "test_atten")
        self.assertEqual(restored_atten.get_scale(), 0.3)

    def test_factory_complex_hierarchy(self):
        """Check that factory can recreate complex nested hierarchy."""
        s1 = sl.SoundElement(name="s1", frequency=440.0)
        s2 = sl.SoundElement(name="s2", frequency=554.37)
        s3 = sl.SoundElement(name="s3", frequency=659.25)

        sum1 = sl.SumElements(a=s1, b=s2, name="sum1")
        sum2 = sl.SumElements(a=sum1, b=s3, name="sum2")
        pluck = sl.Pluck(a=sum2, name="pluck_top")

        original = sl.Chord(note=pluck, name="complex_chord")
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), "complex_chord")
        self.assertEqual(restored.get_note().get_name(), "pluck_top")
        self.assertEqual(restored.get_note().get_type(), "Pluck")

    def test_factory_make_a_chord_roundtrip(self):
        """Check that make_a_chord output can be serialized and restored."""
        original = sl.Chord().make_a_chord((4, "C", "major"))
        dump = original.dump()

        restored = sl.Chord()
        restored.note_factory_hier_db(dump)

        self.assertEqual(restored.get_name(), original.get_name())
        self.assertEqual(restored.get_type(), "Chord")


class TestChordNesting(unittest.TestCase):
    """Tests for Chord with nested elements."""

    def test_chord_with_sound_element(self):
        """Check basic Chord with SoundElement."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        chord = sl.Chord(note=sound)
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_chord_with_pluck(self):
        """Check Chord with Pluck element."""
        sound = sl.SoundElement(phase=math.pi / 2)
        pluck = sl.Pluck(a=sound)
        chord = sl.Chord(note=pluck)
        chord.set_on()
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_chord_with_sum_elements(self):
        """Check Chord with SumElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s1.set_on()
        s2.set_on()
        sum_elem = sl.SumElements(a=s1, b=s2, scale=0.5)  # (1+1)*0.5 = 1.0
        chord = sl.Chord(note=sum_elem)
        self.assertAlmostEqual(chord.sample(), 1.0, places=10)

    def test_chord_with_multiply_elements(self):
        """Check Chord with MultiplyElements."""
        s1 = sl.SoundElement(phase=math.pi / 2)  # 1.0
        s2 = sl.SoundElement(phase=math.pi / 6)  # 0.5
        s1.set_on()
        s2.set_on()
        mult = sl.MultiplyElements(a=s1, b=s2)  # 1.0 * 0.5 = 0.5
        chord = sl.Chord(note=mult)
        self.assertAlmostEqual(chord.sample(), 0.5, places=10)

    def test_chord_with_mix_elements(self):
        """Check Chord with MixElements."""
        s1 = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5
        s2 = sl.SoundElement(phase=math.pi / 2, scale=0.5)  # 0.5
        s1.set_on()
        s2.set_on()
        # Mix formula: (A + B) - (A * B) = (0.5 + 0.5) - (0.5 * 0.5) = 1.0 - 0.25 = 0.75
        mix = sl.MixElements(a=s1, b=s2)
        chord = sl.Chord(note=mix)
        self.assertAlmostEqual(chord.sample(), 0.75, places=10)

    def test_chord_with_fixed_attenuate(self):
        """Check Chord with FixedAttenuate."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        atten = sl.FixedAttenuate(a=sound, scale=0.25)  # 0.25
        chord = sl.Chord(note=atten)
        self.assertAlmostEqual(chord.sample(), 0.25, places=10)

    def test_deeply_nested_chord(self):
        """Check deeply nested element hierarchy."""
        sound = sl.SoundElement(phase=math.pi / 2)  # 1.0
        sound.set_on()
        atten1 = sl.FixedAttenuate(a=sound, scale=0.8)    # 0.8
        atten2 = sl.FixedAttenuate(a=atten1, scale=0.5)   # 0.4
        pluck = sl.Pluck(a=atten2)
        pluck.set_on()
        chord = sl.Chord(note=pluck)
        # At t=0, decay = 1.0, so output = 0.4
        self.assertAlmostEqual(chord.sample(), 0.4, places=10)


# =============================================================================
# Event Tests
# =============================================================================


class TestEventDefaults(unittest.TestCase):
    """Tests for Event default values after instantiation."""

    def test_default_type(self):
        """Check that default _TYPE is 'Event'."""
        event = sl.Event(ptime=0)
        self.assertEqual(event.get_type(), "Event")

    def test_default_name_format(self):
        """Check that default name starts with 'Event_'."""
        event = sl.Event(ptime=0)
        self.assertTrue(event.get_name().startswith("Event_"))

    def test_default_name_is_unique(self):
        """Check that each instance gets a unique name."""
        event1 = sl.Event(ptime=0)
        event2 = sl.Event(ptime=0)
        self.assertNotEqual(event1.get_name(), event2.get_name())

    def test_default_event_is_none(self):
        """Check that default event item is None."""
        event = sl.Event(ptime=0)
        self.assertIsNone(event.get_event())

    def test_ptime_is_set(self):
        """Check that ptime is set correctly."""
        event = sl.Event(ptime=100)
        self.assertEqual(event.get_time(), 100)


class TestEventCustomArgs(unittest.TestCase):
    """Tests for Event initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        event = sl.Event(ptime=0, name="my_event")
        self.assertEqual(event.get_name(), "my_event")

    def test_custom_ptime(self):
        """Check that custom ptime is set correctly."""
        event = sl.Event(ptime=44100)
        self.assertEqual(event.get_time(), 44100)

    def test_custom_event_amchord(self):
        """Check that custom AmChord event is set correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event = sl.Event(ptime=0, event=am_chord)
        self.assertEqual(event.get_event(), am_chord)

    def test_custom_event_amexception(self):
        """Check that custom AmException event is set correctly."""
        am_exc = sl.Event.AmException("test error")
        event = sl.Event(ptime=0, event=am_exc)
        self.assertEqual(event.get_event(), am_exc)

    def test_custom_event_amlyric(self):
        """Check that custom AmLyric event is set correctly."""
        am_lyric = sl.Event.AmLyric("Hello world")
        event = sl.Event(ptime=0, event=am_lyric)
        self.assertEqual(event.get_event(), am_lyric)

    def test_custom_event_ammsg(self):
        """Check that custom AmMSG event is set correctly."""
        am_msg = sl.Event.AmMSG({"test": {"cmd": [1, 2, 3]}})
        event = sl.Event(ptime=0, event=am_msg)
        self.assertEqual(event.get_event(), am_msg)


class TestEventValidation(unittest.TestCase):
    """Tests for Event constructor validation."""

    def test_negative_ptime_raises_error(self):
        """Check that negative ptime raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.Event(ptime=-1)
        self.assertIn("non-negative", str(ctx.exception))

    def test_zero_ptime_is_valid(self):
        """Check that ptime=0 is valid."""
        event = sl.Event(ptime=0)
        self.assertEqual(event.get_time(), 0)


class TestEventSetters(unittest.TestCase):
    """Tests for Event setter methods."""

    def test_set_time(self):
        """Check that set_time updates the time."""
        event = sl.Event(ptime=0)
        event.set_time(44100)
        self.assertEqual(event.get_time(), 44100)

    def test_set_time_to_zero(self):
        """Check that set_time accepts zero."""
        event = sl.Event(ptime=100)
        event.set_time(0)
        self.assertEqual(event.get_time(), 0)

    def test_set_time_negative_raises_error(self):
        """Check that set_time with negative value raises ValueError."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.set_time(-1)

    def test_set_name(self):
        """Check that set_name updates the name."""
        event = sl.Event(ptime=0)
        event.set_name("new_name")
        self.assertEqual(event.get_name(), "new_name")


class TestEventAddEvent(unittest.TestCase):
    """Tests for Event add_event method."""

    def test_add_event_amchord(self):
        """Check that add_event accepts AmChord."""
        event = sl.Event(ptime=0)
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event.add_event(am_chord)
        self.assertEqual(event.get_event(), am_chord)

    def test_add_event_amexception(self):
        """Check that add_event accepts AmException."""
        event = sl.Event(ptime=0)
        am_exc = sl.Event.AmException("error message")
        event.add_event(am_exc)
        self.assertEqual(event.get_event(), am_exc)

    def test_add_event_amlyric(self):
        """Check that add_event accepts AmLyric."""
        event = sl.Event(ptime=0)
        am_lyric = sl.Event.AmLyric("lyrics here")
        event.add_event(am_lyric)
        self.assertEqual(event.get_event(), am_lyric)

    def test_add_event_ammsg(self):
        """Check that add_event accepts AmMSG."""
        event = sl.Event(ptime=0)
        am_msg = sl.Event.AmMSG({"key": "value"})
        event.add_event(am_msg)
        self.assertEqual(event.get_event(), am_msg)

    def test_add_event_invalid_string_raises_error(self):
        """Check that add_event rejects string."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError) as ctx:
            event.add_event("invalid")
        self.assertIn("must be one of", str(ctx.exception))

    def test_add_event_invalid_int_raises_error(self):
        """Check that add_event rejects int."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.add_event(42)

    def test_add_event_invalid_dict_raises_error(self):
        """Check that add_event rejects plain dict."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.add_event({"not": "AmMSG"})

    def test_add_event_replaces_existing(self):
        """Check that add_event replaces existing event."""
        event = sl.Event(ptime=0)
        lyric1 = sl.Event.AmLyric("first")
        lyric2 = sl.Event.AmLyric("second")
        event.add_event(lyric1)
        event.add_event(lyric2)
        self.assertEqual(event.get_event(), lyric2)


class TestEventAmChord(unittest.TestCase):
    """Tests for Event.AmChord embedded class."""

    def test_amchord_creation(self):
        """Check that AmChord can be created."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertIsNotNone(am_chord)

    def test_amchord_instrument(self):
        """Check that instrument is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("guitar", chord, "add", 44100)
        self.assertEqual(am_chord._instrument, "guitar")

    def test_amchord_chord(self):
        """Check that chord is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertEqual(am_chord._chord, chord)

    def test_amchord_action_add(self):
        """Check that action 'add' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertEqual(am_chord._action, "add")

    def test_amchord_action_rm(self):
        """Check that action 'rm' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "rm", 44100)
        self.assertEqual(am_chord._action, "rm")

    def test_amchord_action_add_pluck(self):
        """Check that action 'add_pluck' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add_pluck", 44100)
        self.assertEqual(am_chord._action, "add_pluck")

    def test_amchord_action_pluck(self):
        """Check that action 'pluck' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "pluck", 44100)
        self.assertEqual(am_chord._action, "pluck")

    def test_amchord_action_invalid_raises_error(self):
        """Check that invalid action raises ValueError."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", chord, "invalid", 44100)
        self.assertIn("must be one of", str(ctx.exception))

    def test_amchord_duration(self):
        """Check that duration is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 88200)
        self.assertEqual(am_chord._duration, 88200)

    def test_amchord_duration_zero_is_valid(self):
        """Check that duration=0 is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 0)
        self.assertEqual(am_chord._duration, 0)

    def test_amchord_duration_negative_raises_error(self):
        """Check that negative duration raises ValueError."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", chord, "add", -1)
        self.assertIn("non-negative", str(ctx.exception))

    def test_amchord_invalid_chord_raises_error(self):
        """Check that non-Chord raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", "not a chord", "add", 44100)
        self.assertIn("Chord instance", str(ctx.exception))

    def test_amchord_sound_element_raises_error(self):
        """Check that SoundElement (not Chord) raises ValueError."""
        sound = sl.SoundElement()
        with self.assertRaises(ValueError):
            sl.Event.AmChord("piano", sound, "add", 44100)


class TestEventAmException(unittest.TestCase):
    """Tests for Event.AmException embedded class."""

    def test_amexception_creation(self):
        """Check that AmException can be created."""
        am_exc = sl.Event.AmException("test error")
        self.assertIsNotNone(am_exc)

    def test_amexception_message(self):
        """Check that message is stored correctly."""
        am_exc = sl.Event.AmException("error occurred")
        self.assertEqual(am_exc._message, "error occurred")

    def test_amexception_empty_message(self):
        """Check that empty message is allowed."""
        am_exc = sl.Event.AmException("")
        self.assertEqual(am_exc._message, "")


class TestEventAmLyric(unittest.TestCase):
    """Tests for Event.AmLyric embedded class."""

    def test_amlyric_creation(self):
        """Check that AmLyric can be created."""
        am_lyric = sl.Event.AmLyric("hello world")
        self.assertIsNotNone(am_lyric)

    def test_amlyric_text(self):
        """Check that text is stored correctly."""
        am_lyric = sl.Event.AmLyric("sing along")
        self.assertEqual(am_lyric._text, "sing along")

    def test_amlyric_empty_text(self):
        """Check that empty text is allowed."""
        am_lyric = sl.Event.AmLyric("")
        self.assertEqual(am_lyric._text, "")

    def test_amlyric_multiline_text(self):
        """Check that multiline text is allowed."""
        am_lyric = sl.Event.AmLyric("line1\nline2\nline3")
        self.assertEqual(am_lyric._text, "line1\nline2\nline3")


class TestEventAmMSG(unittest.TestCase):
    """Tests for Event.AmMSG embedded class."""

    def test_ammsg_creation(self):
        """Check that AmMSG can be created."""
        am_msg = sl.Event.AmMSG({"test": "value"})
        self.assertIsNotNone(am_msg)

    def test_ammsg_msg(self):
        """Check that msg is stored correctly."""
        msg_dict = {"element": {"set_frequency": [440.0]}}
        am_msg = sl.Event.AmMSG(msg_dict)
        self.assertEqual(am_msg._msg, msg_dict)

    def test_ammsg_empty_dict(self):
        """Check that empty dict is allowed."""
        am_msg = sl.Event.AmMSG({})
        self.assertEqual(am_msg._msg, {})

    def test_ammsg_nested_dict(self):
        """Check that nested dict is allowed."""
        msg_dict = {"a": {"b": {"c": [1, 2, 3]}}}
        am_msg = sl.Event.AmMSG(msg_dict)
        self.assertEqual(am_msg._msg, msg_dict)


class TestEventDump(unittest.TestCase):
    """Tests for Event dump method."""

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        event = sl.Event(ptime=100, name="test_event")
        dump = event.dump()
        self.assertIn("get_type", dump)
        self.assertIn("get_time", dump)
        self.assertIn("get_name", dump)
        self.assertIn("event", dump)

    def test_dump_values_match(self):
        """Check that dump values match the event's properties."""
        event = sl.Event(ptime=44100, name="my_event")
        dump = event.dump()
        self.assertEqual(dump["get_type"], "Event")
        self.assertEqual(dump["get_time"], 44100)
        self.assertEqual(dump["get_name"], "my_event")
        self.assertIsNone(dump["event"])

    def test_dump_with_amchord(self):
        """Check that dump serializes AmChord correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_chord)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmChord")
        self.assertEqual(dump["event"]["instrument"], "piano")
        self.assertEqual(dump["event"]["action"], "add")
        self.assertEqual(dump["event"]["duration"], 44100)
        self.assertIn("chord", dump["event"])
        self.assertEqual(dump["event"]["chord"]["get_type"], "Chord")

    def test_dump_with_amexception(self):
        """Check that dump serializes AmException correctly."""
        am_exc = sl.Event.AmException("error message")
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_exc)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmException")
        self.assertEqual(dump["event"]["message"], "error message")

    def test_dump_with_amlyric(self):
        """Check that dump serializes AmLyric correctly."""
        am_lyric = sl.Event.AmLyric("song lyrics")
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_lyric)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmLyric")
        self.assertEqual(dump["event"]["text"], "song lyrics")

    def test_dump_with_ammsg(self):
        """Check that dump serializes AmMSG correctly."""
        msg_dict = {"elem": {"cmd": [1, 2]}}
        am_msg = sl.Event.AmMSG(msg_dict)
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_msg)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmMSG")
        self.assertEqual(dump["event"]["msg"], msg_dict)


class TestEventMsg(unittest.TestCase):
    """Tests for Event msg method."""

    def test_msg_get_type(self):
        """Check that msg can get type."""
        event = sl.Event(ptime=0, name="test_event")
        result = event.msg({"test_event": {"get_type": []}})
        self.assertEqual(result["test_event"]["get_type"], "Event")

    def test_msg_get_time(self):
        """Check that msg can get time."""
        event = sl.Event(ptime=44100, name="test_event")
        result = event.msg({"test_event": {"get_time": []}})
        self.assertEqual(result["test_event"]["get_time"], 44100)

    def test_msg_set_time(self):
        """Check that msg can set time."""
        event = sl.Event(ptime=0, name="test_event")
        event.msg({"test_event": {"set_time": [88200]}})
        self.assertEqual(event.get_time(), 88200)

    def test_msg_get_name(self):
        """Check that msg can get name."""
        event = sl.Event(ptime=0, name="test_event")
        result = event.msg({"test_event": {"get_name": []}})
        self.assertEqual(result["test_event"]["get_name"], "test_event")

    def test_msg_set_name(self):
        """Check that msg can set name."""
        event = sl.Event(ptime=0, name="old_name")
        event.msg({"old_name": {"set_name": ["new_name"]}})
        self.assertEqual(event.get_name(), "new_name")

    def test_msg_get_event(self):
        """Check that msg can get event."""
        am_lyric = sl.Event.AmLyric("test")
        event = sl.Event(ptime=0, name="test_event", event=am_lyric)
        result = event.msg({"test_event": {"get_event": []}})
        self.assertEqual(result["test_event"]["get_event"], am_lyric)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        event = sl.Event(ptime=100, name="test_event")
        result = event.msg({"other_name": {"set_time": [0]}})
        # Time should remain unchanged
        self.assertEqual(event.get_time(), 100)

    def test_msg_multiple_commands(self):
        """Check that msg can handle multiple commands."""
        event = sl.Event(ptime=44100, name="test_event")
        result = event.msg({
            "test_event": {
                "get_type": [],
                "get_time": [],
                "get_name": []
            }
        })
        self.assertEqual(result["test_event"]["get_type"], "Event")
        self.assertEqual(result["test_event"]["get_time"], 44100)
        self.assertEqual(result["test_event"]["get_name"], "test_event")

    def test_msg_set_name_uses_current_name_for_return(self):
        """Check that msg uses current name for return value after set_name."""
        event = sl.Event(ptime=0, name="old_name")
        result = event.msg({"old_name": {"set_name": ["new_name"], "get_type": []}})
        # The return should use the original name (captured at start)
        self.assertIn("old_name", result)


if __name__ == "__main__":
    unittest.main()
