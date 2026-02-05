import unittest
import math
import sono as sl

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

    def test_sample_pluck_without_pluck_propagates(self):
        """Check that sample_pluck propagates through non-Pluck elements."""
        sound = sl.SoundElement(phase=math.pi / 2)
        chord = sl.Chord(note=sound)
        # Should return sample value, not raise error
        sample = chord.sample_pluck()
        self.assertIsInstance(sample, float)

    def test_sample_pluck_with_no_note_returns_zero(self):
        """Check that sample_pluck with no element returns 0.0."""
        chord = sl.Chord()
        self.assertEqual(chord.sample_pluck(), 0.0)


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



if __name__ == "__main__":
    unittest.main()
