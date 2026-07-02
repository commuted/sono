import unittest
import sono as sl


class TestPackageExports(unittest.TestCase):
    """Ensure newly added elements are exported from the top-level package."""

    NEW_SYMBOLS = [
        "SawtoothElement",
        "SquareElement",
        "WhiteNoiseElement",
        "LFO",
        "FrequencyModulation",
        "ADSR",
        "EnvelopedElement",
        "BiquadFilter",
        "WAVFileElement",
        "DeviceInputElement",
        "AudioElement",
        "ModulationSource",
    ]

    def test_symbols_present(self):
        for name in self.NEW_SYMBOLS:
            self.assertTrue(hasattr(sl, name), f"{name} not exported")

    def test_symbols_in_all(self):
        for name in self.NEW_SYMBOLS:
            self.assertIn(name, sl.__all__, f"{name} missing from __all__")

    def test_new_elements_accepted_as_chord_note(self):
        # The Chord constructor must accept each new element type as a note.
        elems = [
            sl.SawtoothElement(),
            sl.SquareElement(),
            sl.WhiteNoiseElement(),
            sl.LFO(),
            sl.ADSR(),
            sl.BiquadFilter(sl.SoundElement()),
        ]
        for e in elems:
            chord = sl.Chord(note=e)
            self.assertIs(chord.get_note(), e)


class TestCombinatorDuckTyping(unittest.TestCase):
    """The combinators now accept any child exposing sample() (hasattr check)."""

    def test_combinators_accept_new_element_children(self):
        # Previously the combinators used isinstance against a fixed list;
        # new element types (e.g. SawtoothElement) must now be accepted.
        for cls in (sl.SumElements, sl.MixElements, sl.MultiplyElements):
            combo = cls(sl.SawtoothElement(), sl.SquareElement())
            self.assertIsInstance(combo.sample(), float)

    def test_single_child_combinators_accept_new_children(self):
        pluck = sl.Pluck(sl.SawtoothElement())
        self.assertIsInstance(pluck.sample(), float)
        atten = sl.FixedAttenuate(sl.WhiteNoiseElement())
        self.assertIsInstance(atten.sample(), float)

    def test_object_without_sample_still_rejected(self):
        with self.assertRaises(ValueError):
            sl.SumElements(object(), sl.SoundElement())
        with self.assertRaises(ValueError):
            sl.Pluck(object())


if __name__ == "__main__":
    unittest.main()
