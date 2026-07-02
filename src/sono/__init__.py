# sono - Audio synthesis library
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

"""
sono - Audio synthesis library

This package provides classes for audio synthesis, including:
- Sound elements: oscillators and signal processors
- Musical abstractions: chords and instruments
- Sequencing: events and playback
- Modulation: LFO, ADSR envelopes, frequency modulation
- Filters: Biquad filters for tone shaping
- I/O: WAV file playback and device input

Example usage:
    import sono as sl

    # Create a simple chord
    chord = sl.Chord().make_a_chord((4, "C", "major"))

    # Create an instrument with multiple chords
    instr = sl.Instrument()
    instr.make_from_chords([
        (4, "C", "major"),
        (4, "G", "major"),
        (4, "A", "minor"),
        (4, "F", "major"),
    ])
    
    # Use new oscillators
    saw = sl.SawtoothElement(frequency=440)
    square = sl.SquareElement(frequency=440, duty_cycle=0.5)
    noise = sl.WhiteNoiseElement()
    
    # Apply ADSR envelope
    osc = sl.SoundElement(frequency=440)
    env = sl.ADSR(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
    enveloped = sl.EnvelopedElement(osc, env)
    
    # Add vibrato with LFO
    carrier = sl.SoundElement(frequency=440)
    lfo = sl.LFO(rate=5.0, depth=10.0)
    vibrato = sl.FrequencyModulation(carrier, lfo)
    
    # Apply filter
    filtered = sl.BiquadFilter(osc, filter_type="lowpass", cutoff=1000, q=0.707)
    
    # Play WAV file
    wav = sl.WAVFileElement(filepath="sound.wav", loop=False)
"""

# Sound elements
from .elements import (
    SoundElement,
    MultiplyElements,
    MixElements,
    SumElements,
    Pluck,
    FixedAttenuate,
)

# New oscillators
from .oscillators import (
    SawtoothElement,
    SquareElement,
    WhiteNoiseElement,
)

# Modulation
from .modulation import (
    LFO,
    FrequencyModulation,
    ADSR,
    EnvelopedElement,
)

# Filters
from .filters import (
    BiquadFilter,
)

# I/O Elements
from .io_elements import (
    WAVFileElement,
    DeviceInputElement,
)

# Protocols
from .protocol import (
    AudioElement,
    ModulationSource,
)

# Musical abstractions
from .music import (
    Chord,
    Instrument,
)

# Sequencing
from .sequencer import (
    DuplicateAmChordError,
    Event,
    Channel,
    Sequencer,
)

# Utilities
from .util import (
    Util,
)

__all__ = [
    # Core Elements
    "SoundElement",
    "MultiplyElements",
    "MixElements",
    "SumElements",
    "Pluck",
    "FixedAttenuate",
    # New Oscillators
    "SawtoothElement",
    "SquareElement",
    "WhiteNoiseElement",
    # Modulation
    "LFO",
    "FrequencyModulation",
    "ADSR",
    "EnvelopedElement",
    # Filters
    "BiquadFilter",
    # I/O Elements
    "WAVFileElement",
    "DeviceInputElement",
    # Protocols
    "AudioElement",
    "ModulationSource",
    # Music
    "Chord",
    "Instrument",
    # Sequencer
    "DuplicateAmChordError",
    "Event",
    "Channel",
    "Sequencer",
    # Utilities
    "Util",
]

__version__ = "0.1.0"