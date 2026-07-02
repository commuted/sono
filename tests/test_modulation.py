import unittest
import math
import sono as sl


class ConstantSource:
    """Minimal audio element that always emits a constant value.

    Implements just enough of the element protocol for EnvelopedElement/
    FrequencyModulation tests that need a deterministic input.
    """

    def __init__(self, value=1.0, frequency=440.0, name="const"):
        self._value = value
        self._frequency = frequency
        self._name = name
        self._scale = 1.0
        self._on = False

    def sample(self):
        return self._value if self._on else 0.0

    def sample_pluck(self):
        return self.sample()

    def set_on(self):
        self._on = True

    def set_off(self):
        self._on = False

    def set_frequency(self, f):
        self._frequency = f

    def get_frequency(self):
        return self._frequency

    def set_scale(self, s):
        self._scale = s

    def get_scale(self):
        return self._scale

    def get_type(self):
        return "ConstantSource"

    def get_name(self):
        return self._name

    def msg(self, msg):
        return {self._name: {}}

    def dump(self):
        return {"get_name": self._name, "get_type": "ConstantSource"}


class TestLFODefaults(unittest.TestCase):
    """Test LFO construction and validation."""

    def test_defaults(self):
        lfo = sl.LFO()
        self.assertEqual(lfo.get_type(), "LFO")
        self.assertEqual(lfo.get_rate(), 5.0)
        self.assertEqual(lfo.get_depth(), 1.0)
        self.assertEqual(lfo.get_waveform(), "sine")

    def test_invalid_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.LFO(rate=0)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.LFO(sample_rate=0)

    def test_invalid_waveform_raises(self):
        with self.assertRaises(ValueError):
            sl.LFO(waveform="noise")


class TestLFOSampling(unittest.TestCase):
    """Test LFO waveform generation."""

    def test_sample_off_returns_zero(self):
        lfo = sl.LFO()
        for _ in range(20):
            self.assertEqual(lfo.sample(), 0.0)

    def test_sine_first_sample_zero(self):
        lfo = sl.LFO(rate=5.0, depth=10.0, waveform="sine")
        lfo.set_on()
        self.assertAlmostEqual(lfo.sample(), 0.0, places=9)

    def test_square_first_sample_is_depth(self):
        lfo = sl.LFO(rate=5.0, depth=3.0, waveform="square")
        lfo.set_on()
        self.assertAlmostEqual(lfo.sample(), 3.0, places=9)

    def test_triangle_first_sample_is_depth(self):
        lfo = sl.LFO(rate=5.0, depth=2.0, waveform="triangle")
        lfo.set_on()
        self.assertAlmostEqual(lfo.sample(), 2.0, places=9)

    def test_sawtooth_first_sample_is_negative_depth(self):
        lfo = sl.LFO(rate=5.0, depth=4.0, waveform="sawtooth")
        lfo.set_on()
        self.assertAlmostEqual(lfo.sample(), -4.0, places=9)

    def test_sine_bounded_by_depth(self):
        lfo = sl.LFO(rate=5.0, depth=10.0, waveform="sine")
        lfo.set_on()
        for _ in range(2000):
            v = lfo.sample()
            self.assertLessEqual(abs(v), 10.0 + 1e-9)

    def test_get_modulation_value_advances(self):
        lfo = sl.LFO(rate=5.0, depth=1.0)
        lfo.set_on()
        v1 = lfo.get_modulation_value()
        v2 = lfo.get_modulation_value()
        self.assertNotEqual(v1, v2)


class TestLFOAccessors(unittest.TestCase):
    """Test LFO getters/setters."""

    def test_set_rate_valid_and_invalid(self):
        lfo = sl.LFO()
        lfo.set_rate(2.0)
        self.assertEqual(lfo.get_rate(), 2.0)
        with self.assertRaises(ValueError):
            lfo.set_rate(0)

    def test_set_depth(self):
        lfo = sl.LFO()
        lfo.set_depth(7.5)
        self.assertEqual(lfo.get_depth(), 7.5)

    def test_set_waveform_valid_and_invalid(self):
        lfo = sl.LFO()
        lfo.set_waveform("square")
        self.assertEqual(lfo.get_waveform(), "square")
        with self.assertRaises(ValueError):
            lfo.set_waveform("bogus")

    def test_scale_aliases_depth(self):
        lfo = sl.LFO(depth=1.0)
        lfo.set_scale(5.0)
        self.assertEqual(lfo.get_depth(), 5.0)
        self.assertEqual(lfo.get_scale(), 5.0)

    def test_set_sample_rate_invalid_raises(self):
        with self.assertRaises(ValueError):
            sl.LFO().set_sample_rate(0)

    def test_dump_structure(self):
        lfo = sl.LFO(name="l", rate=3.0, depth=8.0, waveform="triangle")
        d = lfo.dump()
        self.assertEqual(d["get_type"], "LFO")
        self.assertEqual(d["get_rate"], 3.0)
        self.assertEqual(d["get_depth"], 8.0)
        self.assertEqual(d["get_waveform"], "triangle")


class TestFrequencyModulation(unittest.TestCase):
    """Test FrequencyModulation combinator."""

    def test_invalid_carrier_raises(self):
        bad = object()
        with self.assertRaises(ValueError):
            sl.FrequencyModulation(bad, sl.LFO())

    def test_none_carrier_allowed_for_factory(self):
        # Factory reconstruction constructs with carrier/modulator None.
        fm = sl.FrequencyModulation(carrier=None, modulator=None, name="fm")
        self.assertEqual(fm.get_base_frequency(), 0.0)

    def test_base_frequency_from_carrier(self):
        carrier = sl.SoundElement(frequency=440.0)
        fm = sl.FrequencyModulation(carrier, sl.LFO())
        self.assertEqual(fm.get_base_frequency(), 440.0)

    def test_set_on_activates_children(self):
        carrier = ConstantSource(frequency=440.0)
        mod = sl.LFO(rate=5.0, depth=10.0)
        fm = sl.FrequencyModulation(carrier, mod)
        fm.set_on()
        self.assertTrue(carrier._on)
        self.assertTrue(mod._on)

    def test_modulation_changes_carrier_frequency(self):
        carrier = sl.SoundElement(frequency=440.0)
        mod = sl.LFO(rate=5.0, depth=10.0, waveform="square")  # emits +depth first
        fm = sl.FrequencyModulation(carrier, mod)
        fm.set_on()
        fm.sample()
        # base 440 + first modulator value (+10) = 450
        self.assertAlmostEqual(carrier.get_frequency(), 450.0, places=6)

    def test_negative_frequency_clamped(self):
        carrier = sl.SoundElement(frequency=440.0)
        mod = sl.LFO(rate=5.0, depth=1000.0, waveform="sawtooth")  # emits -depth first
        fm = sl.FrequencyModulation(carrier, mod)
        fm.set_on()
        fm.sample()
        self.assertAlmostEqual(carrier.get_frequency(), 0.1, places=6)

    def test_set_base_frequency(self):
        carrier = sl.SoundElement(frequency=440.0)
        fm = sl.FrequencyModulation(carrier, sl.LFO())
        fm.set_base_frequency(220.0)
        self.assertEqual(fm.get_base_frequency(), 220.0)
        self.assertEqual(carrier.get_frequency(), 220.0)
        with self.assertRaises(ValueError):
            fm.set_base_frequency(0)

    def test_scale_accessors(self):
        fm = sl.FrequencyModulation(sl.SoundElement(), sl.LFO())
        fm.set_scale(0.5)
        self.assertEqual(fm.get_scale(), 0.5)

    def test_dump_structure(self):
        carrier = sl.SoundElement(name="car", frequency=440.0)
        lfo = sl.LFO(name="lfo")
        fm = sl.FrequencyModulation(carrier, lfo, name="fm")
        d = fm.dump()
        self.assertEqual(d["get_type"], "FrequencyModulation")
        self.assertEqual(d["get_base_frequency"], 440.0)
        self.assertEqual(d["carrier"]["get_name"], "car")
        self.assertEqual(d["modulator"]["get_name"], "lfo")

    def test_msg_propagates_to_children(self):
        carrier = sl.SoundElement(name="car", frequency=440.0)
        lfo = sl.LFO(name="lfo")
        fm = sl.FrequencyModulation(carrier, lfo, name="fm")
        out = fm.msg({"car": {"get_frequency": []}})
        self.assertEqual(out["fm"]["carrier"]["car"]["get_frequency"], 440.0)


class TestADSR(unittest.TestCase):
    """Test ADSR envelope."""

    def test_defaults_and_type(self):
        env = sl.ADSR()
        self.assertEqual(env.get_type(), "ADSR")
        self.assertEqual(env.get_state(), "idle")

    def test_invalid_times_raise(self):
        with self.assertRaises(ValueError):
            sl.ADSR(attack=-1)
        with self.assertRaises(ValueError):
            sl.ADSR(decay=-1)
        with self.assertRaises(ValueError):
            sl.ADSR(release=-1)

    def test_invalid_sustain_raises(self):
        with self.assertRaises(ValueError):
            sl.ADSR(sustain=1.5)
        with self.assertRaises(ValueError):
            sl.ADSR(sustain=-0.1)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.ADSR(sample_rate=0)

    def test_idle_returns_zero(self):
        env = sl.ADSR()
        for _ in range(10):
            self.assertEqual(env.sample(), 0.0)

    def test_trigger_enters_attack(self):
        env = sl.ADSR(attack=0.1)
        env.trigger()
        self.assertEqual(env.get_state(), "attack")

    def test_attack_ramps_to_one(self):
        env = sl.ADSR(attack=0.01, decay=0.5, sustain=0.5, release=0.1,
                      sample_rate=1000)  # attack_samples = 10
        env.trigger()
        peak = max(env.sample() for _ in range(11))
        self.assertAlmostEqual(peak, 1.0, places=6)

    def test_reaches_sustain_level(self):
        env = sl.ADSR(attack=0.001, decay=0.001, sustain=0.6, release=0.1,
                      sample_rate=1000)
        env.trigger()
        for _ in range(50):
            env.sample()
        self.assertEqual(env.get_state(), "sustain")
        self.assertAlmostEqual(env.sample(), 0.6, places=6)

    def test_release_goes_to_idle(self):
        env = sl.ADSR(attack=0.001, decay=0.001, sustain=0.6, release=0.005,
                      sample_rate=1000)
        env.trigger()
        for _ in range(50):
            env.sample()
        env.release_envelope()
        self.assertEqual(env.get_state(), "release")
        for _ in range(500):
            env.sample()
        self.assertEqual(env.get_state(), "idle")
        self.assertEqual(env.sample(), 0.0)

    def test_release_from_idle_is_noop(self):
        env = sl.ADSR()
        env.release_envelope()
        self.assertEqual(env.get_state(), "idle")

    def test_values_bounded(self):
        env = sl.ADSR(attack=0.01, decay=0.02, sustain=0.5, release=0.02,
                      sample_rate=2000)
        env.trigger()
        for i in range(200):
            v = env.sample()
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0 + 1e-9)
            if i == 100:
                env.release_envelope()

    def test_get_scale_is_one_set_scale_noop(self):
        env = sl.ADSR()
        self.assertEqual(env.get_scale(), 1.0)
        env.set_scale(0.5)  # no-op
        self.assertEqual(env.get_scale(), 1.0)

    def test_set_sample_rate_recalculates(self):
        env = sl.ADSR(attack=0.1, sample_rate=1000)
        self.assertEqual(env._attack_samples, 100)
        env.set_sample_rate(2000)
        self.assertEqual(env._attack_samples, 200)
        with self.assertRaises(ValueError):
            env.set_sample_rate(0)

    def test_dump_structure(self):
        env = sl.ADSR(name="e", attack=0.02, decay=0.05, sustain=0.4, release=0.2)
        d = env.dump()
        self.assertEqual(d["get_type"], "ADSR")
        self.assertEqual(d["attack"], 0.02)
        self.assertEqual(d["decay"], 0.05)
        self.assertEqual(d["sustain"], 0.4)
        self.assertEqual(d["release"], 0.2)


class TestEnvelopedElement(unittest.TestCase):
    """Test EnvelopedElement applies an envelope to a source."""

    def test_type(self):
        ee = sl.EnvelopedElement(sl.SoundElement(), sl.ADSR())
        self.assertEqual(ee.get_type(), "EnvelopedElement")

    def test_set_on_triggers_both(self):
        src = ConstantSource()
        env = sl.ADSR(attack=0.1)
        ee = sl.EnvelopedElement(src, env)
        ee.set_on()
        self.assertTrue(src._on)
        self.assertEqual(env.get_state(), "attack")

    def test_set_off_releases_envelope(self):
        src = ConstantSource()
        env = sl.ADSR(attack=0.001, decay=0.001, sustain=0.5, release=0.1,
                      sample_rate=1000)
        ee = sl.EnvelopedElement(src, env)
        ee.set_on()
        for _ in range(20):
            ee.sample()
        ee.set_off()
        self.assertEqual(env.get_state(), "release")

    def test_output_is_source_times_envelope(self):
        src = ConstantSource(value=1.0)
        env = sl.ADSR(attack=0.01, decay=0.02, sustain=0.5, release=0.02,
                      sample_rate=1000)
        ee = sl.EnvelopedElement(src, env)
        ee.set_scale(0.5)

        # Twin envelope stepped in lockstep to predict the envelope value.
        ref = sl.ADSR(attack=0.01, decay=0.02, sustain=0.5, release=0.02,
                      sample_rate=1000)
        ee.set_on()
        ref.trigger()
        for _ in range(100):
            expected = 1.0 * ref.sample() * 0.5
            self.assertAlmostEqual(ee.sample(), expected, places=9)

    def test_scale_accessors(self):
        ee = sl.EnvelopedElement(sl.SoundElement(), sl.ADSR())
        ee.set_scale(0.3)
        self.assertEqual(ee.get_scale(), 0.3)

    def test_dump_structure(self):
        osc = sl.SoundElement(name="osc")
        env = sl.ADSR(name="env")
        ee = sl.EnvelopedElement(osc, env, name="ee")
        d = ee.dump()
        self.assertEqual(d["get_type"], "EnvelopedElement")
        self.assertEqual(d["source"]["get_name"], "osc")
        self.assertEqual(d["envelope"]["get_name"], "env")


class TestModulationSerializationRoundTrip(unittest.TestCase):
    """Round-trip modulation elements through the Chord factory."""

    def test_lfo_roundtrip(self):
        lfo = sl.LFO(name="lfo", rate=3.0, depth=8.0, waveform="triangle")
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=lfo, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "LFO")
        self.assertEqual(n.get_rate(), 3.0)
        self.assertEqual(n.get_depth(), 8.0)
        self.assertEqual(n.get_waveform(), "triangle")

    def test_adsr_roundtrip(self):
        env = sl.ADSR(name="env", attack=0.02, decay=0.05, sustain=0.4, release=0.2)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=env, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "ADSR")
        self.assertEqual(n._attack, 0.02)
        self.assertEqual(n._sustain, 0.4)

    def test_frequency_modulation_roundtrip(self):
        carrier = sl.SoundElement(name="car", frequency=440.0)
        lfo = sl.LFO(name="lfo", rate=5.0, depth=10.0)
        fm = sl.FrequencyModulation(carrier, lfo, name="fm")
        fm.set_scale(0.5)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=fm, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "FrequencyModulation")
        self.assertEqual(n.get_base_frequency(), 440.0)
        self.assertEqual(n.get_scale(), 0.5)
        self.assertEqual(n._carrier.get_name(), "car")
        self.assertEqual(n._modulator.get_name(), "lfo")

    def test_enveloped_element_roundtrip(self):
        osc = sl.SoundElement(name="osc", frequency=440.0)
        env = sl.ADSR(name="env", attack=0.01, sustain=0.7)
        ee = sl.EnvelopedElement(osc, env, name="ee")
        ee.set_scale(0.6)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=ee, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "EnvelopedElement")
        self.assertEqual(n.get_scale(), 0.6)
        self.assertEqual(n._source.get_name(), "osc")
        self.assertEqual(n._envelope.get_name(), "env")


if __name__ == "__main__":
    unittest.main()
