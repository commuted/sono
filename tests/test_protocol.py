import unittest
import sono as sl


class Incomplete:
    """Object missing most of the AudioElement protocol."""

    def sample(self):
        return 0.0


class FullModulation:
    """Object satisfying the ModulationSource protocol structurally."""

    def get_modulation_value(self):
        return 0.0

    def trigger(self):
        pass

    def release(self):
        pass


class TestAudioElementProtocol(unittest.TestCase):
    """Test the runtime-checkable AudioElement protocol."""

    def test_core_elements_satisfy_protocol(self):
        for elem in (
            sl.SoundElement(),
            sl.SumElements(sl.SoundElement(), sl.SoundElement()),
            sl.MixElements(sl.SoundElement(), sl.SoundElement()),
            sl.MultiplyElements(sl.SoundElement(), sl.SoundElement()),
            sl.Pluck(sl.SoundElement()),
            sl.FixedAttenuate(sl.SoundElement()),
        ):
            self.assertIsInstance(elem, sl.AudioElement)

    def test_new_elements_satisfy_protocol(self):
        for elem in (
            sl.SawtoothElement(),
            sl.SquareElement(),
            sl.WhiteNoiseElement(),
            sl.LFO(),
            sl.ADSR(),
            sl.FrequencyModulation(sl.SoundElement(), sl.LFO()),
            sl.EnvelopedElement(sl.SoundElement(), sl.ADSR()),
            sl.BiquadFilter(sl.SoundElement()),
            sl.DeviceInputElement(),
        ):
            self.assertIsInstance(elem, sl.AudioElement)

    def test_incomplete_object_is_not_audio_element(self):
        self.assertNotIsInstance(Incomplete(), sl.AudioElement)

    def test_plain_object_is_not_audio_element(self):
        self.assertNotIsInstance(object(), sl.AudioElement)


class TestModulationSourceProtocol(unittest.TestCase):
    """Test the runtime-checkable ModulationSource protocol."""

    def test_structural_match_is_instance(self):
        self.assertIsInstance(FullModulation(), sl.ModulationSource)

    def test_plain_object_is_not_modulation_source(self):
        self.assertNotIsInstance(object(), sl.ModulationSource)

    def test_modulation_sources_expose_value(self):
        # LFO and ADSR both offer a modulation value accessor.
        self.assertTrue(hasattr(sl.LFO(), "get_modulation_value"))
        self.assertTrue(hasattr(sl.ADSR(), "get_modulation_value"))


if __name__ == "__main__":
    unittest.main()
