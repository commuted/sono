# sono

Audio synthesis library for procedural audio generation, musical abstractions, and sequencing. The architecture looks like an ASIC. I plan a front end that looks like a object based schematic. It's more competent than the documentation. 

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

```python
import sono as sl

# Create a chord
chord = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
sl.Util.fix_pop(chord)
chord.set_on()

# Generate samples
samples = [chord.sample() for _ in range(44100)]
```

### Embedded Pluck (Individual Decay)

```python
# Create elements with individual decay envelopes
se1 = sl.SoundElement(frequency=261.63)  # C4
se2 = sl.SoundElement(frequency=329.63)  # E4

p1 = sl.Pluck(a=se1, lambda_dc=5.0)   # fast decay
p2 = sl.Pluck(a=se2, lambda_dc=0.5)   # slow decay

combined = sl.SumElements(a=p1, b=p2)
chord = sl.Chord(note=combined)

# Trigger all plucks
chord.sample_pluck()

# Continue sampling
for _ in range(44100):
    sample = chord.sample()
```

## Testing

```bash
pytest
```

Or with unittest:
```bash
python -m unittest discover -s tests -v
```

## License

BSD 3-Clause License
