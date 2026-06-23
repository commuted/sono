# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -e ".[dev]"          # install package + pytest/pytest-cov (Python >= 3.10)
pytest                           # run all tests
python -m unittest discover -s tests -v   # same tests via unittest
pytest --cov                     # coverage (configured for src/sono, branch mode)
```

Run a single test (tests are `unittest.TestCase` classes discovered by pytest):

```bash
pytest tests/test_elements.py::TestSoundElementDefaults::test_frequency_is_float_440
# or, pure unittest:
python -m unittest tests.test_elements.TestSoundElementDefaults.test_frequency_is_float_440
```

This is a **src-layout** package: `import sono` only works after `pip install -e .` (the `examples/` scripts instead hack `sys.path.insert(0, '..')`). README convention is `import sono as sl`.

## Architecture

`sono` is a procedural audio synthesis library. Four modules under `src/sono/`, layered bottom-up: `elements` → `music` → `sequencer`, with `util` as a cross-cutting helper.

### The element signal graph (`elements.py`) — the core abstraction

Synthesis is a **composite tree** of nodes. `SoundElement` is the leaf oscillator (frequency, phase, sample_rate, scale; waveform via `triangle()`/`sample()`). Combinator nodes wrap one or two child nodes (`a`, `b`): `MultiplyElements`, `MixElements`, `SumElements`, plus `Pluck` (per-element exponential decay envelope, `lambda_dc`) and `FixedAttenuate`.

Every node — leaf or combinator — implements the **same protocol**, and that uniformity is what lets them nest arbitrarily, be triggered together, and round-trip through serialization:

`sample()`, `sample_pluck()`, `set_on()`/`set_off()`, `set_scale()`/`get_scale()`, `get_type()`, `get_name()`, `msg()`, `dump()`

When adding a new element type, implement this **entire** protocol or it won't compose, trigger, or serialize.

### Pull-based, one-sample-at-a-time synthesis

`sample()` returns a **single float** and advances the node's internal phase; calling it on a combinator recurses into its children. You render audio by looping it:

```python
samples = [chord.sample() for _ in range(seconds * 44100)]   # default sample_rate = 44100
```

The core synth path uses no buffers/arrays — numpy/scipy appear only in `util`'s analysis code, not the sample loop. Time is measured in **samples** throughout the codebase (including the sequencer).

### Pluck is two-phase; mind onset clicks

`Pluck` envelopes must be **armed by `sample_pluck()`** at note onset before `sample()` produces the decaying tone. The canonical order is: build the element tree → `Util.fix_pop(chord)` (phase-align children to avoid a start "pop"; `Util.min_derivative` is an alternative) → `set_on()` / `sample_pluck()` → loop `sample()`.

### Music layer (`music.py`)

`Chord` wraps one element tree as a playable note; `Chord.make_a_chord((octave, root, quality))` builds chords from note names (e.g. `(4, "C", "major")`). `Instrument` is a named collection of chords. `SoundElementType` (a `Union` defined here) is the accepted-element type alias used across signatures.

### Sequencer layer (`sequencer.py`)

`Event` occurs at a `ptime` (in samples) and carries inner item types `AmChord`/`AmException`/`AmLyric`/`AmMSG`. `Channel` is an ordered list of Events (one chord per channel). `Sequencer` holds named channels plus instruments; `Sequencer.sample()` advances time and returns per-channel output, driven by `generate_event_queue()` / `process_events()`.

### Serialization round-trip (`dump`/`msg` + factories)

Objects serialize two ways: `dump()` → nested dict (whole tree), `msg(registry)` → flat dict keyed by each node's auto-generated unique `name` (e.g. `"SoundElement_<id>"` — names must stay unique because they are the serialization keys). Rebuilding is done by factory methods: `Chord.recursive_walk` / `Chord.note_factory_hier_db`, `Instrument.instrument_factory`. **If you change a node's fields, update both its `dump()`/`msg()` and the matching factory**, or the round-trip silently breaks. `out.json` (repo root) is a sample dump.

### WAV → Chord (`util.py`, psychoacoustic)

`Util.wav_to_chord` / `array_to_chord` / `bytes_to_chord` / `fileobj_to_chord` / `to_chord` analyze a WAV via FFT plus an MPEG-style psychoacoustic masking model (Bark scale, absolute threshold of hearing, spreading function, tonality, signal-to-mask ratio) to select perceptually-significant partials and synthesize a `Chord` of sines that approximates the input. This is the only numpy/scipy-heavy area.

## Note: `wav2note.py` vs `Util.wav_to_chord`

`wav2note.py` at the repo root is a **standalone CLI** (`python wav2note.py input.wav output.json --num-waves N`) implementing the same psychoacoustic model and emitting JSON. It is **not** part of the installed `sono` package and is not imported anywhere; the packaged, importable equivalent is `Util.wav_to_chord` in `src/sono/util.py`. Keep changes to the two in mind — they duplicate the model.
