import os
import unittest
import sono as sl
from tests.fixtures import (
    get_sine_440hz_16bit,
    get_sine_440hz_8bit,
    get_stereo_16bit,
    get_silence_16bit,
    get_short_click_16bit,
)


class TestWAVFileElementLoading(unittest.TestCase):
    """Test WAVFileElement metadata loading and validation."""

    def test_type_and_defaults(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        self.assertEqual(wav.get_type(), "WAVFileElement")
        self.assertFalse(wav.get_loop())
        self.assertEqual(wav.get_sample_rate(), 44100)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            sl.WAVFileElement("/nonexistent/path/does_not_exist.wav")

    def test_invalid_wav_raises(self, ):
        # Point at a non-WAV file to trigger the invalid-format path.
        not_wav = os.path.join(os.path.dirname(__file__), "test_io_elements.py")
        with self.assertRaises(ValueError):
            sl.WAVFileElement(not_wav)

    def test_loads_8bit(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_8bit()))
        wav.set_on()
        self.assertTrue(any(wav.sample() != 0.0 for _ in range(2000)))

    def test_loads_stereo_as_mono(self):
        wav = sl.WAVFileElement(str(get_stereo_16bit()))
        wav.set_on()
        # Mono conversion: one value per frame, in range.
        for _ in range(2000):
            v = wav.sample()
            self.assertGreaterEqual(v, -1.0)
            self.assertLessEqual(v, 1.0)


class TestWAVFileElementPlayback(unittest.TestCase):
    """Test WAVFileElement playback behavior."""

    def test_sample_off_returns_zero(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        for _ in range(50):
            self.assertEqual(wav.sample(), 0.0)

    def test_set_on_starts_at_zero_position(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_on()
        self.assertEqual(wav.get_position(), 0)
        wav.sample()
        self.assertEqual(wav.get_position(), 1)

    def test_sine_produces_signal(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_on()
        samples = [wav.sample() for _ in range(4410)]
        self.assertTrue(any(abs(s) > 0.1 for s in samples))

    def test_silence_is_zero(self):
        wav = sl.WAVFileElement(str(get_silence_16bit()))
        wav.set_on()
        for _ in range(1000):
            self.assertAlmostEqual(wav.sample(), 0.0, places=6)

    def test_scale_applied(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()), scale=0.0)
        wav.set_on()
        for _ in range(1000):
            self.assertEqual(wav.sample(), 0.0)

    def test_non_looping_stops_at_end(self):
        wav = sl.WAVFileElement(str(get_short_click_16bit()), loop=False)
        wav.set_on()
        # click fixture is 100 samples long
        for _ in range(100):
            wav.sample()
        self.assertTrue(wav.is_finished())
        self.assertEqual(wav.sample(), 0.0)
        self.assertFalse(wav._on)

    def test_looping_wraps_around(self):
        wav = sl.WAVFileElement(str(get_short_click_16bit()), loop=True)
        wav.set_on()
        for _ in range(250):  # more than 2x the 100-sample fixture
            wav.sample()
        self.assertFalse(wav.is_finished())
        self.assertTrue(wav._on)

    def test_reset(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_on()
        for _ in range(100):
            wav.sample()
        wav.reset()
        self.assertEqual(wav.get_position(), 0)

    def test_get_duration(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        # 1 second fixture at 44100 Hz
        self.assertAlmostEqual(wav.get_duration(), 44100, delta=10)

    def test_resample_ratio_changes_duration(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()), sample_rate=22050)
        # target rate is half the file rate -> ratio 2 -> duration halved
        self.assertAlmostEqual(wav.get_duration(), 22050, delta=10)


class TestWAVFileElementAccessors(unittest.TestCase):
    """Test WAVFileElement getters/setters."""

    def test_loop_accessors(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_loop(True)
        self.assertTrue(wav.get_loop())

    def test_filepath_accessor(self):
        path = str(get_sine_440hz_16bit())
        wav = sl.WAVFileElement(path)
        self.assertEqual(wav.get_filepath(), path)

    def test_set_sample_rate_updates_ratio(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_sample_rate(22050)
        self.assertEqual(wav.get_sample_rate(), 22050)
        self.assertAlmostEqual(wav._resample_ratio, 2.0, places=6)
        with self.assertRaises(ValueError):
            wav.set_sample_rate(0)

    def test_scale_accessors(self):
        wav = sl.WAVFileElement(str(get_sine_440hz_16bit()))
        wav.set_scale(0.5)
        self.assertEqual(wav.get_scale(), 0.5)

    def test_dump_structure(self):
        path = str(get_sine_440hz_16bit())
        wav = sl.WAVFileElement(path, loop=True, name="w", scale=0.3)
        d = wav.dump()
        self.assertEqual(d["get_type"], "WAVFileElement")
        self.assertEqual(d["get_filepath"], path)
        self.assertTrue(d["get_loop"])
        self.assertEqual(d["get_scale"], 0.3)

    def test_roundtrip(self):
        path = str(get_sine_440hz_16bit())
        wav = sl.WAVFileElement(path, loop=True, name="w", scale=0.3)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=wav, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "WAVFileElement")
        self.assertEqual(n.get_filepath(), path)
        self.assertTrue(n.get_loop())
        self.assertEqual(n.get_scale(), 0.3)


class TestDeviceInputElement(unittest.TestCase):
    """Test DeviceInputElement (placeholder audio input)."""

    def test_type_and_defaults(self):
        dev = sl.DeviceInputElement()
        self.assertEqual(dev.get_type(), "DeviceInputElement")
        self.assertEqual(dev.get_device_id(), 0)
        self.assertEqual(dev.get_channels(), 1)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.DeviceInputElement(sample_rate=0)

    def test_invalid_channels_raises(self):
        with self.assertRaises(ValueError):
            sl.DeviceInputElement(channels=3)

    def test_sample_off_returns_zero(self):
        dev = sl.DeviceInputElement()
        for _ in range(20):
            self.assertEqual(dev.sample(), 0.0)

    def test_sample_on_returns_silence_placeholder(self):
        dev = sl.DeviceInputElement()
        dev.set_on()
        self.assertTrue(dev._on)
        for _ in range(20):
            self.assertEqual(dev.sample(), 0.0)

    def test_set_off(self):
        dev = sl.DeviceInputElement()
        dev.set_on()
        dev.set_off()
        self.assertFalse(dev._on)

    def test_set_sample_rate(self):
        dev = sl.DeviceInputElement()
        dev.set_sample_rate(22050)
        self.assertEqual(dev.get_sample_rate(), 22050)
        with self.assertRaises(ValueError):
            dev.set_sample_rate(0)

    def test_scale_accessors(self):
        dev = sl.DeviceInputElement()
        dev.set_scale(0.5)
        self.assertEqual(dev.get_scale(), 0.5)

    def test_dump_structure(self):
        dev = sl.DeviceInputElement(device_id=2, channels=2, name="d", scale=0.7)
        d = dev.dump()
        self.assertEqual(d["get_type"], "DeviceInputElement")
        self.assertEqual(d["get_device_id"], 2)
        self.assertEqual(d["get_channels"], 2)
        self.assertEqual(d["get_scale"], 0.7)

    def test_roundtrip(self):
        dev = sl.DeviceInputElement(device_id=1, channels=2, name="d", scale=0.7)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=dev, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "DeviceInputElement")
        self.assertEqual(n.get_device_id(), 1)
        self.assertEqual(n.get_channels(), 2)
        self.assertEqual(n.get_scale(), 0.7)


if __name__ == "__main__":
    unittest.main()
