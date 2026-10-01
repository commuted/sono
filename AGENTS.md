# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

**sono** is a procedural audio synthesis library for Python that provides musical abstractions and sequencing capabilities. The library enables real-time audio generation through a composable signal graph architecture.

**Core Technologies:**
- Python 3.10+ (src-layout package)
- NumPy/SciPy (for psychoacoustic analysis only)
- Pure Python synthesis engine (no buffers in sample loop)

**Key Characteristics:**
- Pull-based, one-sample-at-a-time synthesis
- Composite tree architecture for signal processing
- Psychoacoustic WAV-to-chord analysis
- Event-based sequencing with sample-accurate timing

## Architecture

The library is organized in multiple layered modules under `src/sono/`:

```
elements.py  →  music.py  →  sequencer.py
oscillators.py ↗    ↓
modulation.py  →  util.py (cross-cutting)
filters.py     ↗
io_elements.py ↗
protocol.py (type definitions)
```

### Signal Graph Layer (`elements.py`)

The foundation is a **composite tree** where every node implements a uniform protocol:

**Core Protocol (required for all element types):**
- `sample()` - Generate next sample, advance phase
- `sample_pluck()` - Trigger pluck envelopes, propagate through tree
- `set_on()` / `set_off()` - Activate/deactivate element
- `set_scale()` / `get_scale()` - Amplitude control
- `get_type()` / `get_name()` - Type identification
- `msg(dict)` - Control message routing
- `dump()` - Serialization to nested dict

**Element Types:**

**Leaf Oscillators:**
- `SoundElement` - Sine/triangle wave generator (frequency, phase, sample_rate, scale)
- `SawtoothElement` - Sawtooth wave (rich harmonics for brass/strings)
- `SquareElement` - Square wave with PWM (odd harmonics, hollow sound)
- `WhiteNoiseElement` - White noise generator (percussion, wind effects)

**Combinators (wrap 1-2 children):**
- `SumElements` - Z = A + B (default scale=0.5 to avoid clipping)
- `MultiplyElements` - Z = A * B (ring modulation)
- `MixElements` - Z = A + B - A*B (audio mixing formula)
- `Pluck` - Exponential decay envelope (lambda_dc, stop duration)
- `FixedAttenuate` - Simple gain control

**Modulation:**
- `LFO` - Low frequency oscillator for vibrato/tremolo (rate, depth, waveform)
- `FrequencyModulation` - Hierarchical FM synthesis (carrier + modulator)
- `ADSR` - Attack-Decay-Sustain-Release envelope
- `EnvelopedElement` - Apply envelope to any audio element

**Filters:**
- `BiquadFilter` - 2nd-order IIR filter (lowpass, highpass, bandpass, notch, peak, shelving)

**I/O Elements:**
- `WAVFileElement` - WAV file playback with event control
- `DeviceInputElement` - Live audio input (placeholder for PyAudio/sounddevice integration)

**Critical Implementation Rules:**
1. When adding new element types, implement the **entire protocol** or composition breaks
2. All nodes use the same interface - this enables arbitrary nesting
3. Time is measured in **samples** throughout (not seconds)
4. No buffers in the synthesis path - numpy/scipy only in `util.py` analysis

### Pluck Envelope System

`Pluck` requires **two-phase triggering**:

```python
# 1. Build element tree
chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)

# 2. Phase-align to avoid onset click
sl.Util.fix_pop(chord)  # or use Util.min_derivative

# 3. Arm the pluck envelope
chord.set_on()
chord.sample_pluck()  # REQUIRED - arms decay envelope

# 4. Generate samples
samples = [chord.sample() for _ in range(44100)]
```

**Why two phases?** `sample_pluck()` resets the decay timer to 0, so re-triggering a previously-played Pluck starts from full amplitude rather than continuing from where it left off.

### Music Layer (`music.py`)

**`Chord`** - Wraps one element tree as a playable note
- `make_a_chord((octave, root, quality))` - Build from note names
- Supports slash bass: `"major/E"`, `"m7/G"`
- Supports omit notation: `"major(omit5)"`, `"9(omit3,5)"`
- Combined: `"maj7(omit5)/E"`

**`Instrument`** - Named collection of chords
- `make_from_chords(list)` - Batch create from chord specs
- `add_note(chord, name)` - Add individual chord

**`SoundElementType`** - Type alias for accepted element types (Union of all element classes)

### Sequencer Layer (`sequencer.py`)

**`Event`** - Occurs at `ptime` (in samples), contains:
- `AmChord` - Chord action (add, rm, add_pluck, pluck) with duration
- `AmException` - Exception event
- `AmLyric` - Lyric text
- `AmMSG` - Message dictionary

**`Channel`** - Ordered list of Events
- One active chord per channel at a time
- Sorted by ptime automatically
- `DuplicateAmChordError` if multiple AmChords at same ptime

**`Sequencer`** - Multi-channel event processor
- `sample()` returns list of dicts (one per channel) with sample + lyrics + messages
- `generate_event_queue()` / `process_events()` - Event scheduling
- Sample-accurate timing (all times in samples, not seconds)

### Serialization System

**Two serialization modes:**

1. **`dump()`** - Nested dict (entire tree structure)
2. **`msg(registry)`** - Flat dict keyed by unique auto-generated names (e.g., `"SoundElement_<id>"`)

**Factory methods for reconstruction:**
- `Chord.recursive_walk()` / `Chord.note_factory_hier_db()` - Rebuild chord from dump
- `Instrument.instrument_factory()` - Rebuild instrument from dump

**Critical:** When modifying element fields, update **both** `dump()`/`msg()` **and** the matching factory, or round-trip silently breaks.

### Psychoacoustic Analysis (`util.py`)

`Util.wav_to_chord()` and related methods analyze WAV files using:
- FFT for frequency analysis
- MPEG-style psychoacoustic masking model
- Bark scale frequency mapping
- Absolute threshold of hearing
- Spreading function for masking
- Tonality estimation
- Signal-to-mask ratio calculation

Selects perceptually-significant partials and synthesizes a `Chord` of sine waves approximating the input.

**Note:** `wav2note.py` at repo root is a **standalone CLI** implementing the same model. It is **not** part of the installed package. The importable version is `Util.wav_to_chord` in `src/sono/util.py`.

## Building and Running

### Installation

```bash
# Basic installation
pip install -e .

# Development installation (includes pytest, pytest-cov)
pip install -e ".[dev]"
```

**Important:** This is a **src-layout** package. `import sono` only works after `pip install -e .`. The `examples/` scripts work around this with `sys.path.insert(0, '..')`.

### Testing

```bash
# Run all tests (pytest discovers unittest.TestCase classes)
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_elements.py::TestSoundElementDefaults::test_frequency_is_float_440

# Alternative: pure unittest
python -m unittest discover -s tests -v
python -m unittest tests.test_elements.TestSoundElementDefaults.test_frequency_is_float_440
```

**Test Configuration:**
- Tests are `unittest.TestCase` classes discovered by pytest
- Coverage configured for `src/sono/`, branch mode enabled
- Test fixtures in `tests/fixtures/` (WAV files for analysis tests)

### Running Examples

```bash
# Examples require installation first
pip install -e .

# Then run examples
python examples/chord_progression.py
python examples/song.py
python examples/wav_to_chord_example.py
```

## Development Conventions

### Code Organization

1. **Layered architecture** - Respect the elements → music → sequencer dependency flow
2. **Protocol uniformity** - All element types implement the same interface
3. **Sample-based timing** - Use samples, not seconds, for all time measurements
4. **No synthesis buffers** - Keep numpy/scipy in `util.py` analysis code only

### Adding New Element Types

When creating a new element type:

1. **Implement the complete protocol:**
   - `sample()`, `sample_pluck()`, `set_on()`, `set_off()`
   - `set_scale()`, `get_scale()`, `get_type()`, `get_name()`
   - `msg()`, `dump()`

2. **Update type checking:**
   - Add to `SoundElementType` union in `music.py`
   - Add to `isinstance()` checks in setter methods

3. **Update factories:**
   - Add case to `Chord.recursive_walk()`
   - Ensure `dump()` output can be consumed by factory

4. **Test thoroughly:**
   - Unit tests for the element in isolation
   - Integration tests with combinators
   - Serialization round-trip tests

### Serialization Changes

When modifying element properties:

1. Update `dump()` to include new fields
2. Update `msg()` command handling
3. Update factory methods (`recursive_walk`, `note_factory_hier_db`, `instrument_factory`)
4. Add tests for serialization round-trip
5. Check `out.json` (sample dump at repo root) for reference

### Pluck Envelope Guidelines

- Always call `sample_pluck()` after `set_on()` to arm the envelope
- Use `Util.fix_pop()` or `Util.min_derivative()` to phase-align before triggering
- The `stop` parameter is duration in seconds, `lambda_dc` controls decay rate
- Pluck propagates through the tree via `sample_pluck()` method

### Testing Practices

- Tests use `unittest.TestCase` classes (pytest discovers them)
- Use fixtures in `tests/fixtures/` for WAV file tests
- Mock IB API calls if needed (see `conftest.py` pattern from parent repo)
- Test both success and error cases
- Verify serialization round-trips

### Performance Considerations

- The synthesis loop is pure Python - optimize hot paths
- Avoid allocations in `sample()` methods
- Phase increment is pre-calculated in constructors
- Use epsilon comparisons for float zero-crossing detection
- Consider caching frequently-accessed properties

## Common Patterns

### Creating a Simple Chord

```python
import sono as sl

# Create and configure
chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
sl.Util.fix_pop(chord)
chord.set_on()
chord.sample_pluck()

# Generate audio
samples = [chord.sample() for _ in range(44100)]
```

### Building Custom Element Trees

```python
# Create oscillators
se1 = sl.SoundElement(frequency=261.63)  # C4
se2 = sl.SoundElement(frequency=329.63)  # E4

# Apply individual pluck envelopes
p1 = sl.Pluck(a=se1, lambda_dc=5.0)   # fast decay
p2 = sl.Pluck(a=se2, lambda_dc=0.5)   # slow decay

# Combine
combined = sl.SumElements(a=p1, b=p2)
chord = sl.Chord(note=combined)

# Trigger all plucks
chord.sample_pluck()
```

### Using the Sequencer

```python
# Create events
event1 = sl.Event(ptime=0)
event1.add_event(sl.Event.AmChord(
    instrument="piano",
    chord=chord1,
    action="add_pluck",
    duration=44100  # 1 second at 44.1kHz
))

# Create channel
channel = sl.Channel()
channel.add_event(event1)

# Create sequencer
seq = sl.Sequencer()
seq.add_channel("melody", channel, instruments=[instrument])

# Generate samples
while seq.get_time() < total_samples:
    results = seq.sample()  # List of dicts per channel
    for result in results:
        sample = result["sample"]
        lyrics = result["lyrics"]
        messages = result["messages"]
```

### Using New Oscillators

```python
# Sawtooth - rich harmonics
saw = sl.SawtoothElement(frequency=220.0)
saw.set_on()
samples = [saw.sample() for _ in range(44100)]

# Square with PWM
square = sl.SquareElement(frequency=440.0, duty_cycle=0.3)
square.set_on()
samples = [square.sample() for _ in range(44100)]

# White noise
noise = sl.WhiteNoiseElement(seed=42)  # Reproducible
noise.set_on()
samples = [noise.sample() for _ in range(44100)]
```

### Using ADSR Envelopes

```python
# Create oscillator
osc = sl.SoundElement(frequency=440.0)

# Create ADSR envelope
env = sl.ADSR(
    attack=0.01,    # 10ms attack
    decay=0.1,      # 100ms decay
    sustain=0.7,    # 70% sustain level
    release=0.3     # 300ms release
)

# Combine with EnvelopedElement
enveloped = sl.EnvelopedElement(osc, env)

# Trigger note
enveloped.set_on()  # Starts attack phase
samples = [enveloped.sample() for _ in range(44100)]
enveloped.set_off()  # Starts release phase
samples.extend([enveloped.sample() for _ in range(22050)])
```

### Using LFO for Vibrato

```python
# Create carrier oscillator
carrier = sl.SoundElement(frequency=440.0)

# Create LFO (5 Hz vibrato, ±10 Hz depth)
lfo = sl.LFO(rate=5.0, depth=10.0, waveform="sine")

# Apply frequency modulation
vibrato = sl.FrequencyModulation(carrier, lfo)

# Activate and generate
vibrato.set_on()
samples = [vibrato.sample() for _ in range(44100)]
```

### Using Filters

```python
# Create oscillator with rich harmonics
saw = sl.SawtoothElement(frequency=110.0)

# Apply lowpass filter
filtered = sl.BiquadFilter(
    source=saw,
    filter_type="lowpass",
    cutoff=1000.0,  # 1 kHz cutoff
    q=0.707         # Butterworth response
)

# Activate and generate
filtered.set_on()

# Sweep filter cutoff
for i in range(44100):
    cutoff = 200 + 3800 * (i / 44100)  # 200 Hz to 4 kHz
    filtered.set_cutoff(cutoff)
    sample = filtered.sample()
```

### Using WAV File Playback

```python
# Load and play WAV file
wav = sl.WAVFileElement(filepath="sound.wav", loop=False)
wav.set_on()

samples = []
while not wav.is_finished():
    samples.append(wav.sample())

# Or with looping
wav_loop = sl.WAVFileElement(filepath="loop.wav", loop=True)
wav_loop.set_on()
samples = [wav_loop.sample() for _ in range(44100 * 5)]  # 5 seconds
```

### WAV Analysis

```python
# Analyze WAV file
chord = sl.Util.wav_to_chord("input.wav", num_waves=10)

# Or from array
import numpy as np
audio_array = np.array([...])
chord = sl.Util.array_to_chord(audio_array, sample_rate=44100)
```

## Key Files Reference

- `src/sono/__init__.py` - Package exports and version
- `src/sono/protocol.py` - Protocol definitions for AudioElement and ModulationSource
- `src/sono/elements.py` - Core signal graph elements (1000+ lines)
- `src/sono/oscillators.py` - Additional oscillators (Sawtooth, Square, WhiteNoise)
- `src/sono/modulation.py` - Modulation sources (LFO, ADSR, FrequencyModulation, EnvelopedElement)
- `src/sono/filters.py` - Digital filters (BiquadFilter)
- `src/sono/io_elements.py` - I/O elements (WAVFileElement, DeviceInputElement)
- `src/sono/music.py` - Musical abstractions (500+ lines)
- `src/sono/sequencer.py` - Event sequencing (600+ lines)
- `src/sono/util.py` - Psychoacoustic analysis utilities
- `tests/` - Test suite (unittest.TestCase classes)
- `examples/` - Usage examples (require installation)
- `examples/new_features_demo.py` - Demo of new oscillators, ADSR, LFO, filters, WAV playback
- `wav2note.py` - Standalone CLI (not part of package)
- `out.json` - Sample serialization output
- `CLAUDE.md` - Detailed development guide (read this for deep dives)

## Related Documentation

For more detailed information:
- See `CLAUDE.md` for in-depth architecture discussion
- See `README.md` for quick start and basic usage
- See docstrings in source files for API details
- See `tests/` for usage examples and edge cases

## Version Information

- Package version: 0.1.0 (Alpha)
- Python requirement: >=3.10
- License: BSD 3-Clause
