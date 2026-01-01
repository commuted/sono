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

__all__ = [
    # Elements
    "SoundElement",
    "MultiplyElements",
    "MixElements",
    "SumElements",
    "Pluck",
    "FixedAttenuate",
    # Music
    "Chord",
    "Instrument",
    # Sequencer
    "DuplicateAmChordError",
    "Event",
    "Channel",
    "Sequencer",
]

__version__ = "0.1.0"
