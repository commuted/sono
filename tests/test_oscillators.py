import unittest
import math
import sono as sl


class TestSawtoothElementDefaults(unittest.TestCase):
    """Test SawtoothElement default values and construction."""

    def test_defaults(self):
        saw = sl.SawtoothElement()
        self.assertEqual(saw._frequency, 440.0)
        self.assertEqual(saw._sample_rate, 44100)
        self.assertEqual(saw._phase, 0.0)
        self.assertEqual(saw._scale, 1.0)
        self.assertFalse(saw._on)

    def test_type_and_name(self):
        saw = sl.SawtoothElement()
        self.assertEqual(saw.get_type(), "SawtoothElement")
        self.assertIn("SawtoothElement", saw.get_name())

    def test_custom_name(self):
        saw = sl.SawtoothElement(name="my_saw")
        self.assertEqual(saw.get_name(), "my_saw")

    def test_unique_names(self):
        a = sl.SawtoothElement()
        b = sl.SawtoothElement()
        self.assertNotEqual(a.get_name(), b.get_name())

    def test_invalid_frequency_raises(self):
        with self.assertRaises(ValueError):
            sl.SawtoothElement(frequency=0)
        with self.assertRaises(ValueError):
            sl.SawtoothElement(frequency=-100)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.SawtoothElement(sample_rate=0)


class TestSawtoothElementSampling(unittest.TestCase):
    """Test SawtoothElement waveform generation."""

    def test_sample_off_returns_zero(self):
        saw = sl.SawtoothElement()
        for _ in range(50):
            self.assertEqual(saw.sample(), 0.0)

    def test_first_sample_is_minus_one(self):
        saw = sl.SawtoothElement(frequency=440.0)
        saw.set_on()
        # normalized phase 0 -> 2*0 - 1 = -1
        self.assertAlmostEqual(saw.sample(), -1.0, places=10)

    def test_ramps_upward_within_period(self):
        saw = sl.SawtoothElement(frequency=441.0, sample_rate=44100)
        saw.set_on()
        prev = saw.sample()
        # Sample partway through first cycle; values increase until wrap.
        for _ in range(10):
            cur = saw.sample()
            self.assertGreater(cur, prev)
            prev = cur

    def test_scale_applied(self):
        saw = sl.SawtoothElement(scale=0.5)
        saw.set_on()
        self.assertAlmostEqual(saw.sample(), -0.5, places=10)

    def test_matches_analytic_sawtooth(self):
        freq, sr = 440.0, 44100
        saw = sl.SawtoothElement(frequency=freq, sample_rate=sr)
        saw.set_on()
        inc = (freq / sr) * 2 * math.pi
        phase = 0.0
        for _ in range(200):
            normalized = (phase % (2 * math.pi)) / (2 * math.pi)
            expected = 2 * normalized - 1
            self.assertAlmostEqual(saw.sample(), expected, places=9)
            phase += inc

    def test_set_off_settles_to_zero(self):
        saw = sl.SawtoothElement(frequency=440.0)
        saw.set_on()
        for _ in range(20):
            saw.sample()
        saw.set_off()
        # Within one period it should settle and stay at zero.
        period = int(44100 / 440) + 2
        settled = False
        for _ in range(period):
            if saw.sample() == 0.0:
                settled = True
                break
        self.assertTrue(settled)
        for _ in range(50):
            self.assertEqual(saw.sample(), 0.0)

    def test_sample_pluck_matches_sample(self):
        saw = sl.SawtoothElement()
        saw.set_on()
        self.assertAlmostEqual(saw.sample_pluck(), -1.0, places=10)


class TestSawtoothElementAccessors(unittest.TestCase):
    """Test SawtoothElement getters/setters and phase increment updates."""

    def test_set_frequency_updates_increment(self):
        saw = sl.SawtoothElement(frequency=440.0)
        old = saw._phase_increment
        saw.set_frequency(880.0)
        self.assertEqual(saw.get_frequency(), 880.0)
        self.assertAlmostEqual(saw._phase_increment, old * 2, places=12)

    def test_set_frequency_invalid_raises(self):
        with self.assertRaises(ValueError):
            sl.SawtoothElement().set_frequency(0)

    def test_set_sample_rate_updates_increment(self):
        saw = sl.SawtoothElement(frequency=440.0, sample_rate=44100)
        saw.set_sample_rate(22050)
        self.assertEqual(saw.get_sample_rate(), 22050)

    def test_set_sample_rate_invalid_raises(self):
        with self.assertRaises(ValueError):
            sl.SawtoothElement().set_sample_rate(0)

    def test_scale_accessors(self):
        saw = sl.SawtoothElement()
        saw.set_scale(0.25)
        self.assertEqual(saw.get_scale(), 0.25)

    def test_phase_accessors(self):
        saw = sl.SawtoothElement()
        saw.set_phase(1.5)
        self.assertEqual(saw.get_phase(), 1.5)

    def test_init_phase_affects_set_on(self):
        saw = sl.SawtoothElement()
        saw.set_init_phase(math.pi)  # normalized 0.5 -> value 0
        saw.set_on()
        self.assertAlmostEqual(saw.sample(), 0.0, places=9)


class TestSawtoothElementProtocol(unittest.TestCase):
    """Test SawtoothElement msg() and dump()."""

    def test_msg_get_type(self):
        saw = sl.SawtoothElement(name="s")
        out = saw.msg({"s": {"get_type": []}})
        self.assertEqual(out["s"]["get_type"], "SawtoothElement")

    def test_msg_set_frequency(self):
        saw = sl.SawtoothElement(name="s")
        saw.msg({"s": {"set_frequency": [660.0]}})
        self.assertEqual(saw.get_frequency(), 660.0)

    def test_msg_ignores_other_names(self):
        saw = sl.SawtoothElement(name="s")
        out = saw.msg({"other": {"get_type": []}})
        self.assertEqual(out["s"], {})

    def test_dump_structure(self):
        saw = sl.SawtoothElement(name="s", frequency=550.0, scale=0.3)
        d = saw.dump()
        self.assertEqual(d["get_type"], "SawtoothElement")
        self.assertEqual(d["get_name"], "s")
        self.assertEqual(d["get_frequency"], 550.0)
        self.assertEqual(d["get_scale"], 0.3)


class TestSquareElementDefaults(unittest.TestCase):
    """Test SquareElement construction and validation."""

    def test_defaults(self):
        sq = sl.SquareElement()
        self.assertEqual(sq.get_type(), "SquareElement")
        self.assertEqual(sq.get_duty_cycle(), 0.5)

    def test_invalid_duty_cycle_raises(self):
        with self.assertRaises(ValueError):
            sl.SquareElement(duty_cycle=0.0)
        with self.assertRaises(ValueError):
            sl.SquareElement(duty_cycle=1.0)
        with self.assertRaises(ValueError):
            sl.SquareElement(duty_cycle=1.5)

    def test_invalid_frequency_raises(self):
        with self.assertRaises(ValueError):
            sl.SquareElement(frequency=-1)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.SquareElement(sample_rate=0)


class TestSquareElementSampling(unittest.TestCase):
    """Test SquareElement waveform generation."""

    def test_sample_off_returns_zero(self):
        sq = sl.SquareElement()
        for _ in range(50):
            self.assertEqual(sq.sample(), 0.0)

    def test_first_sample_is_high(self):
        sq = sl.SquareElement(duty_cycle=0.5)
        sq.set_on()
        self.assertAlmostEqual(sq.sample(), 1.0, places=10)

    def test_values_are_plus_or_minus_scale(self):
        sq = sl.SquareElement(frequency=440.0, scale=0.8)
        sq.set_on()
        for _ in range(500):
            v = sq.sample()
            self.assertIn(round(v, 6), (0.8, -0.8))

    def test_duty_cycle_changes_high_fraction(self):
        # A high duty cycle should spend most of the period high.
        sq = sl.SquareElement(frequency=440.0, sample_rate=44100, duty_cycle=0.9)
        sq.set_on()
        highs = sum(1 for _ in range(4410) if sq.sample() > 0)
        self.assertGreater(highs, 4410 * 0.8)

    def test_set_duty_cycle_invalid_raises(self):
        with self.assertRaises(ValueError):
            sl.SquareElement().set_duty_cycle(0.0)

    def test_set_duty_cycle_valid(self):
        sq = sl.SquareElement()
        sq.set_duty_cycle(0.25)
        self.assertEqual(sq.get_duty_cycle(), 0.25)

    def test_set_off_settles_to_zero(self):
        sq = sl.SquareElement(frequency=440.0)
        sq.set_on()
        for _ in range(20):
            sq.sample()
        sq.set_off()
        period = int(44100 / 440) + 2
        settled = any(sq.sample() == 0.0 for _ in range(period))
        self.assertTrue(settled)
        for _ in range(50):
            self.assertEqual(sq.sample(), 0.0)


class TestSquareElementProtocol(unittest.TestCase):
    """Test SquareElement msg() and dump()."""

    def test_msg_duty_cycle(self):
        sq = sl.SquareElement(name="q")
        sq.msg({"q": {"set_duty_cycle": [0.3]}})
        out = sq.msg({"q": {"get_duty_cycle": []}})
        self.assertEqual(out["q"]["get_duty_cycle"], 0.3)

    def test_dump_includes_duty_cycle(self):
        sq = sl.SquareElement(name="q", duty_cycle=0.4)
        d = sq.dump()
        self.assertEqual(d["get_type"], "SquareElement")
        self.assertEqual(d["get_duty_cycle"], 0.4)


class TestWhiteNoiseElement(unittest.TestCase):
    """Test WhiteNoiseElement generation and reproducibility."""

    def test_defaults(self):
        noise = sl.WhiteNoiseElement()
        self.assertEqual(noise.get_type(), "WhiteNoiseElement")
        self.assertEqual(noise.get_sample_rate(), 44100)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            sl.WhiteNoiseElement(sample_rate=0)

    def test_sample_off_returns_zero(self):
        noise = sl.WhiteNoiseElement(seed=1)
        for _ in range(50):
            self.assertEqual(noise.sample(), 0.0)

    def test_samples_within_range(self):
        noise = sl.WhiteNoiseElement(seed=1, scale=0.5)
        noise.set_on()
        for _ in range(1000):
            v = noise.sample()
            self.assertGreaterEqual(v, -0.5)
            self.assertLess(v, 0.5)

    def test_seed_reproducibility(self):
        a = sl.WhiteNoiseElement(seed=42)
        b = sl.WhiteNoiseElement(seed=42)
        a.set_on()
        b.set_on()
        seq_a = [a.sample() for _ in range(100)]
        seq_b = [b.sample() for _ in range(100)]
        self.assertEqual(seq_a, seq_b)

    def test_set_on_reseeds_when_seeded(self):
        noise = sl.WhiteNoiseElement(seed=7)
        noise.set_on()
        first = [noise.sample() for _ in range(20)]
        noise.set_on()  # re-seed
        second = [noise.sample() for _ in range(20)]
        self.assertEqual(first, second)

    def test_different_seeds_differ(self):
        a = sl.WhiteNoiseElement(seed=1)
        b = sl.WhiteNoiseElement(seed=2)
        a.set_on()
        b.set_on()
        self.assertNotEqual([a.sample() for _ in range(50)],
                            [b.sample() for _ in range(50)])

    def test_set_seed_resets_rng(self):
        noise = sl.WhiteNoiseElement(seed=1)
        noise.set_seed(99)
        self.assertEqual(noise.get_seed(), 99)

    def test_dump_structure(self):
        noise = sl.WhiteNoiseElement(name="n", seed=5, scale=0.2)
        d = noise.dump()
        self.assertEqual(d["get_type"], "WhiteNoiseElement")
        self.assertEqual(d["get_seed"], 5)
        self.assertEqual(d["get_scale"], 0.2)


class TestOscillatorSerializationRoundTrip(unittest.TestCase):
    """Round-trip new oscillators through the Chord factory."""

    def test_sawtooth_roundtrip(self):
        saw = sl.SawtoothElement(name="saw", frequency=330.0, scale=0.6, phase=0.2)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=saw, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "SawtoothElement")
        self.assertEqual(n.get_frequency(), 330.0)
        self.assertEqual(n.get_scale(), 0.6)
        self.assertEqual(n.get_phase(), 0.2)

    def test_square_roundtrip(self):
        sq = sl.SquareElement(name="sq", frequency=220.0, duty_cycle=0.3, scale=0.4)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=sq, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "SquareElement")
        self.assertEqual(n.get_duty_cycle(), 0.3)
        self.assertEqual(n.get_scale(), 0.4)

    def test_whitenoise_roundtrip(self):
        noise = sl.WhiteNoiseElement(name="n", seed=13, scale=0.7)
        restored = sl.Chord()
        restored.note_factory_hier_db(sl.Chord(note=noise, name="c").dump())
        n = restored.get_note()
        self.assertEqual(n.get_type(), "WhiteNoiseElement")
        self.assertEqual(n.get_seed(), 13)
        self.assertEqual(n.get_scale(), 0.7)


if __name__ == "__main__":
    unittest.main()
