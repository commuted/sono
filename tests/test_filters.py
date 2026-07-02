import unittest
import sono as sl


class ConstantSource:
    """Constant-output audio element for deterministic filter tests."""

    def __init__(self, value=1.0, name="const"):
        self._value = value
        self._name = name
        self._on = False

    def sample(self):
        return self._value if self._on else 0.0

    def sample_pluck(self):
        return self.sample()

    def set_on(self):
        self._on = True

    def set_off(self):
        self._on = False

    def set_scale(self, s):
        pass

    def get_scale(self):
        return 1.0

    def get_type(self):
        return "ConstantSource"

    def get_name(self):
        return self._name

    def msg(self, msg):
        return {self._name: {}}

    def dump(self):
        return {"get_name": self._name, "get_type": "ConstantSource"}


class TestBiquadFilterConstruction(unittest.TestCase):
    """Test BiquadFilter construction and validation."""

    def test_defaults(self):
        f = sl.BiquadFilter(sl.SoundElement())
        self.assertEqual(f.get_type(), "BiquadFilter")
        self.assertEqual(f.get_filter_type(), "lowpass")
        self.assertEqual(f.get_cutoff(), 1000.0)
        self.assertAlmostEqual(f.get_q(), 0.707)

    def test_invalid_filter_type_raises(self):
        with self.assertRaises(ValueError):
            sl.BiquadFilter(sl.SoundElement(), filter_type="bogus")

    def test_invalid_cutoff_raises(self):
        with self.assertRaises(ValueError):
            sl.BiquadFilter(sl.SoundElement(), cutoff=0)

    def test_invalid_q_raises(self):
        with self.assertRaises(ValueError):
            sl.BiquadFilter(sl.SoundElement(), q=0)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.BiquadFilter(sl.SoundElement(), sample_rate=0)

    def test_all_valid_types_construct(self):
        for ft in ("lowpass", "highpass", "bandpass", "notch",
                   "peak", "lowshelf", "highshelf"):
            f = sl.BiquadFilter(sl.SoundElement(), filter_type=ft)
            self.assertEqual(f.get_filter_type(), ft)


class TestBiquadFilterResponse(unittest.TestCase):
    """Test BiquadFilter frequency response via DC gain."""

    def _dc_steady(self, filter_type):
        src = ConstantSource(1.0)
        f = sl.BiquadFilter(src, filter_type=filter_type, cutoff=1000, q=0.707)
        f.set_on()
        out = 0.0
        for _ in range(5000):
            out = f.sample()
        return out

    def test_lowpass_passes_dc(self):
        self.assertAlmostEqual(self._dc_steady("lowpass"), 1.0, places=4)

    def test_notch_passes_dc(self):
        self.assertAlmostEqual(self._dc_steady("notch"), 1.0, places=4)

    def test_highpass_blocks_dc(self):
        self.assertAlmostEqual(self._dc_steady("highpass"), 0.0, places=4)

    def test_bandpass_blocks_dc(self):
        self.assertAlmostEqual(self._dc_steady("bandpass"), 0.0, places=4)

    def test_scale_applied_to_output(self):
        src = ConstantSource(1.0)
        f = sl.BiquadFilter(src, filter_type="lowpass", cutoff=1000)
        f.set_scale(2.0)
        f.set_on()
        out = 0.0
        for _ in range(5000):
            out = f.sample()
        self.assertAlmostEqual(out, 2.0, places=4)

    def test_output_is_finite(self):
        src = ConstantSource(0.5)
        f = sl.BiquadFilter(src, filter_type="peak", cutoff=1000, q=5, gain=6.0)
        f.set_on()
        for _ in range(1000):
            v = f.sample()
            self.assertFalse(v != v)  # not NaN


class TestBiquadFilterState(unittest.TestCase):
    """Test filter state management."""

    def test_set_on_resets_state(self):
        src = ConstantSource(1.0)
        f = sl.BiquadFilter(src, filter_type="lowpass", cutoff=1000)
        f.set_on()
        for _ in range(100):
            f.sample()
        # Non-zero internal state now.
        self.assertNotEqual((f._x1, f._y1), (0.0, 0.0))
        f.set_on()
        self.assertEqual(f._x1, 0.0)
        self.assertEqual(f._x2, 0.0)
        self.assertEqual(f._y1, 0.0)
        self.assertEqual(f._y2, 0.0)

    def test_set_off_propagates_to_source(self):
        src = ConstantSource(1.0)
        f = sl.BiquadFilter(src)
        f.set_on()
        self.assertTrue(src._on)
        f.set_off()
        self.assertFalse(src._on)


class TestBiquadFilterAccessors(unittest.TestCase):
    """Test BiquadFilter getters/setters recompute coefficients."""

    def test_set_cutoff_changes_coefficients(self):
        f = sl.BiquadFilter(sl.SoundElement(), cutoff=1000)
        b0_old = f._b0
        f.set_cutoff(5000)
        self.assertEqual(f.get_cutoff(), 5000)
        self.assertNotEqual(f._b0, b0_old)
        with self.assertRaises(ValueError):
            f.set_cutoff(0)

    def test_set_q(self):
        f = sl.BiquadFilter(sl.SoundElement())
        f.set_q(2.0)
        self.assertEqual(f.get_q(), 2.0)
        with self.assertRaises(ValueError):
            f.set_q(0)

    def test_set_gain(self):
        f = sl.BiquadFilter(sl.SoundElement(), filter_type="peak")
        f.set_gain(6.0)
        self.assertEqual(f.get_gain(), 6.0)

    def test_set_filter_type(self):
        f = sl.BiquadFilter(sl.SoundElement())
        f.set_filter_type("highpass")
        self.assertEqual(f.get_filter_type(), "highpass")
        with self.assertRaises(ValueError):
            f.set_filter_type("nope")

    def test_set_sample_rate(self):
        f = sl.BiquadFilter(sl.SoundElement(), sample_rate=44100)
        f.set_sample_rate(22050)
        self.assertEqual(f.get_sample_rate(), 22050)
        with self.assertRaises(ValueError):
            f.set_sample_rate(0)

    def test_scale_accessors(self):
        f = sl.BiquadFilter(sl.SoundElement())
        f.set_scale(0.4)
        self.assertEqual(f.get_scale(), 0.4)


class TestBiquadFilterProtocol(unittest.TestCase):
    """Test BiquadFilter msg() and dump()."""

    def test_msg_set_cutoff(self):
        f = sl.BiquadFilter(sl.SoundElement(name="s"), name="f")
        f.msg({"f": {"set_cutoff": [2000.0]}})
        self.assertEqual(f.get_cutoff(), 2000.0)

    def test_msg_propagates_to_source(self):
        src = sl.SoundElement(name="s", frequency=440.0)
        f = sl.BiquadFilter(src, name="f")
        out = f.msg({"s": {"get_frequency": []}})
        self.assertEqual(out["f"]["source"]["s"]["get_frequency"], 440.0)

    def test_dump_structure(self):
        src = sl.SoundElement(name="s")
        f = sl.BiquadFilter(src, filter_type="highpass", cutoff=800, q=1.5,
                            gain=3.0, name="f")
        d = f.dump()
        self.assertEqual(d["get_type"], "BiquadFilter")
        self.assertEqual(d["get_filter_type"], "highpass")
        self.assertEqual(d["get_cutoff"], 800)
        self.assertEqual(d["get_q"], 1.5)
        self.assertEqual(d["get_gain"], 3.0)
        self.assertEqual(d["source"]["get_name"], "s")


class TestBiquadFilterRoundTrip(unittest.TestCase):
    """Round-trip BiquadFilter through the Chord factory."""

    def test_roundtrip(self):
        src = sl.SoundElement(name="s", frequency=440.0)
        f = sl.BiquadFilter(src, filter_type="bandpass", cutoff=1500, q=2.0,
                            gain=0.0, name="f")
        f.set_scale(0.4)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=f, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "BiquadFilter")
        self.assertEqual(n.get_filter_type(), "bandpass")
        self.assertEqual(n.get_cutoff(), 1500)
        self.assertEqual(n.get_q(), 2.0)
        self.assertEqual(n.get_scale(), 0.4)
        self.assertEqual(n._source.get_name(), "s")


if __name__ == "__main__":
    unittest.main()
