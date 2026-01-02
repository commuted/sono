# music.py
# Musical abstraction classes for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Union, Any, Dict, List, Tuple, TYPE_CHECKING
from math import log2
from enum import Enum
import re

from .elements import (
    SoundElement,
    SumElements,
    MultiplyElements,
    MixElements,
    Pluck,
    FixedAttenuate,
)

if TYPE_CHECKING:
    SoundElementType = Union[
        SoundElement,
        SumElements,
        MultiplyElements,
        MixElements,
        Pluck,
        FixedAttenuate,
    ]


class Chord:
    """A class to encapsulate sound elements as a musical chord.

    Attributes:
        a (SoundElementType): The underlying sound element.
        name (str): Unique identifier for the chord.
    """

    def __init__(self, note: SoundElementType | None = None, name: str | None = None):
        """Initialize a Chord instance.

        Args:
            note (SoundElementType, optional): The sound element to encapsulate.
            name (str, optional): Unique identifier for the note.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        self._TYPE = "Chord"
        self._a: SoundElementType | None = None
        self._assembly: Dict[Any, Any] = {}
        self._collect: Dict[Any, Any] = {}
        self._done: Dict[Any, Any] = {}
        self.set_note(note)
        self._name = name or f"{self._TYPE}_{id(self)}"

    def get_type(self) -> str:
        """Get the type identifier of the note.

        Returns:
            str: The type string ("Chord").
        """
        return self._TYPE

    def get_name(self) -> str:
        """Get the unique identifier of the note.

        Returns:
            str: The note's name.
        """
        return self._name

    def set_name(self, name: str) -> None:
        """Set the unique identifier of the note.

        Args:
            name (str): The new name.
        """
        self._name = name

    def get_note(self) -> SoundElementType | None:
        """Get the underlying sound element.

        Returns:
            SoundElementType | None: The sound element, or None if not set.
        """
        return self._a

    def set_note(self, note: SoundElementType | None) -> None:
        """Set the underlying sound element.

        Args:
            note (SoundElementType, optional): The sound element to set.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        if note and not isinstance(
            note,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
                Chord,
            ),
        ):
            raise ValueError("object assignment to Chord has no attribute sample()")
        if isinstance(note, Chord):
            self._a = note.get_note()
        else:
            self._a = note

    def set_a(self, note: SoundElementType | None) -> None:
        """Set the underlying sound element (alias for set_note).

        Args:
            note (SoundElementType, optional): The sound element to set.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        self.set_note(note)

    def sample(self) -> float:
        """Generate the next sample from the underlying element.

        Returns:
            float: The sample value, or 0.0 if no element is set.
        """
        return self._a.sample() if self._a else 0.0

    def sample_pluck(self) -> float:
        """Generate the next sample from the underlying element.

        Returns:
            float: The sample value, or 0.0 if no element is set.

            Raises: TypeError when no sample_pluck() method in hierarchy

        """
        if isinstance(self.get_note(), Pluck):
            return self._a.sample_pluck() if self._a else 0.0
        else:
            actual_type = self._a.get_type() if self._a else "None"
            raise TypeError(
               f"Chord top hierarchy is not type Pluck. Is type {actual_type}"
            )

    def set_on(self) -> None:
        """Activate the underlying sound element."""
        if self._a:
            self._a.set_on()

    def set_off(self) -> None:
        """Deactivate the underlying sound element."""
        if self._a:
            self._a.set_off()

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this note.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-element.
        """
        current_name = self._name
        return_val: Dict[str, Any] = {current_name: {}}
        for name in msg:
            if name == current_name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[current_name]["get_name"] = self.get_name()
                    elif cmd == "get_type":
                        return_val[current_name]["get_type"] = self.get_type()
                    elif cmd == "set_name":
                        self.set_name(val[0])
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
        # Propagate to sub-element regardless of name match
        if self._a:
            a_val = self._a.msg(msg)
            if a_val:
                return_val[current_name]["a"] = a_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the chord's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the note's properties and sub-element.
        """
        return {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
        }

    def recursive_walk(self, data: Dict[str, Any]) -> None:
        """Recursively build sound element hierarchy from a data dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing element properties and hierarchy.
        """
        get_type = data["get_type"]
        if get_type == "SoundElement":
            self._done[data["get_name"]] = SoundElement(
                name=data["get_name"],
                frequency=data["get_frequency"],
                sample_rate=data["get_sample_rate"],
                phase=data["get_phase"],
                scale=data["get_scale"],
            )
        elif get_type == "SumElements":
            self._collect[data["get_name"]] = SumElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "Pluck":
            self._collect[data["get_name"]] = Pluck(
                name=data["get_name"],
                sample_rate=data["get_sample_rate"],
                stop=data["get_stop"],
                lambda_dc=data["get_lambda_dc"],
                scale=data["get_scale"],
            )
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])
        elif get_type == "MixElements":
            self._collect[data["get_name"]] = MixElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "MultiplyElements":
            self._collect[data["get_name"]] = MultiplyElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "FixedAttenuate":
            self._collect[data["get_name"]] = FixedAttenuate(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])
        elif get_type == "Chord":
            self._collect[data["get_name"]] = Chord(name=data["get_name"])
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])

    def note_factory_hier_db(self, data: Dict[str, Any]) -> None:
        """Build a note hierarchy from a serialized data dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing the note hierarchy.

        Raises:
            ValueError: If the factory fails to converge or has cyclic dependencies.
        """
        self.recursive_walk(data)
        time_out = int(len(self._assembly) * (log2(len(self._assembly)) + 1))
        cnt = 0
        while self._collect:
            if cnt == time_out:
                raise ValueError(
                    f"Chord factory failed to converge after {cnt} iterations. Check for cyclic dependencies in {self._assembly}"
                )
            cnt += 1
            to_delete = []
            for key, val in self._assembly.items():
                if "a" in val and "b" in val:
                    if val["a"] in self._done and val["b"] in self._done:
                        self._collect[key].set_a(self._done[val["a"]])
                        self._collect[key].set_b(self._done[val["b"]])
                        self._done[key] = self._collect[key]
                        to_delete.append(key)
                        del self._done[val["a"]]
                        del self._done[val["b"]]
                elif "a" in val:
                    if val["a"] in self._done:
                        self._collect[key].set_a(self._done[val["a"]])
                        self._done[key] = self._collect[key]
                        to_delete.append(key)
                        del self._done[val["a"]]
            for key in to_delete:
                del self._collect[key]
        if len(self._done) != 1:
            raise ValueError(
                f"Chord factory failed to converge: {len(self._done)} elements remain"
            )
        for k, v in self._done.items():
            self.set_name(k)
            self.set_note(v)

    class MixType(Enum):
        """Enum for mixing types in chord creation."""

        SUM = "SumElements"
        MIX = "MixElements"

    def make_a_chord(
        self,
        chord: Tuple[int, str, str],
        mix: MixType = MixType.SUM,
        pluck: bool = True,
    ) -> Chord:
        """Create a note from a chord specification.

        Args:
            chord (Tuple[int, str, str]): A tuple of (octave, note, chord_type).
                chord_type can include:
                - Slash bass note: "major/E", "m7/G"
                - Omit notation: "major(omit5)", "9(omit3)"
                - Combined: "maj7(omit5)/E", "9(omit3,5)/G"
                Valid omit values: 1, root, 3, 5, 7, 9, 11, 13
            mix (MixType): The mixing method for combining notes (default: MixType.SUM).
            pluck (bool): If True, apply a Pluck effect to the chord (default: True).

        Returns:
            Chord: A Chord object representing the chord.

        Raises:
            ValueError: If the mix type is invalid.
        """
        note_map = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11,
        }
        chords = {
            "major": {0, 4, 7},
            "maj7": {0, 4, 7, 11},
            "6": {0, 4, 7, 9},
            "6/9": {0, 4, 7, 9, 14},
            "maj9": {0, 4, 7, 11, 14},
            "minor": {0, 3, 7},
            "m7": {0, 3, 7, 10},
            "m6": {0, 3, 7, 9},
            "m6/9": {0, 3, 7, 9, 14},
            "m9": {0, 3, 7, 10, 14},
            "m11": {0, 3, 7, 10, 14, 17},
            "minMaj7": {0, 3, 7, 11},
            "7": {0, 4, 7, 10},
            "9": {0, 4, 7, 10, 14},
            "11": {0, 4, 7, 10, 14, 17},
            "dim": {0, 3, 6},
            "dim7": {0, 3, 6, 9},
            "half-dim": {0, 3, 6, 10},
            "aug": {0, 4, 8},
            "aug7": {0, 4, 8, 10},
            "7-5": {0, 4, 6, 10},
            "7+5": {0, 4, 8, 10},
            "7-9": {0, 4, 7, 10, 13},
            "7+9": {0, 4, 7, 10, 15},
            "7#11": {0, 4, 7, 10, 18},
            "5": {0, 7},
            "add9": {0, 4, 7, 14},
            "add2": {0, 2, 4, 7},
            "add11": {0, 4, 7, 17},
            "add4": {0, 4, 5, 7},
            "sus4": {0, 5, 7},
            "sus2": {0, 2, 7},
        }
        populated: List[SoundElementType] = []
        # Standard MIDI: C4 (middle C) = 60, so octave N maps to (N+1)*12
        base_midi = (chord[0] + 1) * 12 + note_map.get(chord[1], 0)
        chord_type = chord[2]
        slash_bass = None
        omit_intervals: set[int] = set()

        # Map scale degrees to semitone offsets for omit notation
        # Includes both major and minor variants where applicable
        omit_map = {
            "1": {0},
            "root": {0},
            "3": {3, 4},      # minor 3rd and major 3rd
            "5": {7},
            "7": {10, 11},    # minor 7th and major 7th
            "9": {14},
            "11": {17},
            "13": {21},
        }

        # Parse omit notation (e.g., "(omit5)", "(omit3,5)")
        omit_match = re.search(r"\(omit([^)]+)\)", chord_type)
        if omit_match:
            omit_str = omit_match.group(1)
            # Remove the omit notation from chord_type
            chord_type = chord_type[:omit_match.start()] + chord_type[omit_match.end():]
            # Parse comma-separated omit values
            for omit_val in omit_str.split(","):
                omit_val = omit_val.strip().lower()
                if omit_val in omit_map:
                    omit_intervals.update(omit_map[omit_val])

        # Check for slash chord notation (e.g., "major/E", "m7/G#")
        # Exclude chord types that use "/" as part of their name (6/9, m6/9)
        if "/" in chord_type:
            parts = chord_type.rsplit("/", 1)
            # Check if the part after "/" is a valid note name (slash bass)
            # rather than part of the chord name (like "9" in "6/9")
            if parts[1] in note_map:
                chord_type = parts[0]
                slash_bass = parts[1]

        name = f"{chord[0]}{chord[1]}{chord[2]}"
        chord_offsets = chords.get(chord_type, {0})

        # Apply omit intervals
        if omit_intervals:
            chord_offsets = {o for o in chord_offsets if o not in omit_intervals}
        for offset in chord_offsets:
            elem = SoundElement()
            elem.set_frequency_to_midi_note(base_midi + offset)
            populated.append(elem)

        # Add slash bass note (one octave below the chord root)
        if slash_bass is not None:
            bass_offset = note_map[slash_bass]
            # Place bass note one octave below the chord root
            bass_midi = chord[0] * 12 + bass_offset
            bass_elem = SoundElement()
            bass_elem.set_frequency_to_midi_note(bass_midi)
            # Insert bass at the beginning so it's the lowest voice
            populated.insert(0, bass_elem)

        while len(populated) > 1:
            a = populated.pop(0)
            b = populated.pop(0)
            if mix == self.MixType.SUM:
                combined = SumElements(a=a, b=b)
            elif mix == self.MixType.MIX:
                combined = MixElements(a=a, b=b)
            else:
                raise ValueError("Invalid mix type")
            populated.append(combined)
        root = populated[0]
        if pluck:
            root = Pluck(a=root)
        return Chord(note=root, name=name)


class Instrument:
    """A class to manage a collection of notes.

    Attributes:
        instr (Dict[str, Chord]): Dictionary of chords, keyed by name.
        name (str): Unique identifier for the instrument.
    """

    def __init__(
        self, instrument: Dict[str, Chord] | None = None, name: str | None = None
    ):
        """Initialize an Instrument instance.

        Args:
            instrument (Dict[str, Chord], optional): Initial dictionary of chords.
            name (str, optional): Unique identifier for the instrument.
        """
        self._TYPE = "Instrument"
        self._instr = instrument or {}
        self._name = name or f"{self._TYPE}_{id(self)}"

    def get_note_lst(self) -> List[str]:
        """Get the list of note names in the instrument.

        Returns:
            List[str]: List of note names.
        """
        return list(self._instr.keys())

    def add_note(self, note: object, name: str | None = None) -> None:
        """Add a note to the instrument.

        Args:
            note (object): The note to add (must have a sample() method).
            name (str, optional): The name for the note. Uses note's name if None.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        if not isinstance(
            note,
            (
                Chord,
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            raise ValueError("object assignment as Chord has no attribute sample()")
        key = name or note.get_name()
        self._instr[key] = note

    def get_note(self, note: str) -> object:
        """Get a note by its name.

        Args:
            note (str): The name of the note.

        Returns:
            object: The note object, or None if not found.
        """
        return self._instr.get(note)

    def get_type(self) -> str:
        """Get the type identifier of the instrument.

        Returns:
            str: The type string ("Instrument").
        """
        return self._TYPE

    def get_name(self) -> str:
        """Get the unique identifier of the instrument.

        Returns:
            str: The instrument's name.
        """
        return self._name

    def make_from_chords(
        self,
        chords_lst: List[Tuple[int, str, str]],
        mix: Chord.MixType = Chord.MixType.SUM,
        pluck: bool = True,
    ) -> None:
        """Create and add notes from a list of chord specifications.

        Args:
            chords_lst (List[Tuple[int, str, str]]): List of (octave, note, chord_type) tuples.
            mix (Chord.MixType): The mixing method for chords (default: Chord.MixType.SUM).
            pluck (bool): If True, apply a Pluck effect to chords (default: True).
        """
        chord_instance = Chord()
        for chord in chords_lst:
            chord_note = chord_instance.make_a_chord(chord, mix, pluck)
            self.add_note(chord_note)

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this instrument.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including notes.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_note_lst":
                        return_val[self._name]["get_note_lst"] = self.get_note_lst()
                for k, v in self._instr.items():
                    note_val = v.msg(msg)
                    if note_val:
                        return_val[k] = note_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the instrument's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the instrument's properties and notes.
        """
        return_val: Dict[str, Any] = {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
        }
        for k, v in self._instr.items():
            return_val[k] = v.dump()
        return return_val

    def instrument_factory(
        self, instr_dump: Dict[str, Any], force: bool = True
    ) -> None:
        """Build an instrument from a serialized data dictionary.

        Args:
            instr_dump (Dict[str, Any]): A dictionary containing the instrument hierarchy.
            force (bool): If True, overwrite existing notes on name collision (default: True).

        Raises:
            ValueError: If instr_dump is not an Instrument or if note names collide and force is False.
        """
        if instr_dump["get_type"] != "Instrument":
            raise ValueError("instrument_factory requires type 'Instrument' at top")
        results = {}
        for k, v in instr_dump.items():
            if k in ("get_name", "get_type"):
                continue
            if v["get_type"] == "Chord":
                f = Chord()
                f.note_factory_hier_db(v)
                if not force and k in self._instr:
                    raise ValueError(
                        f"instrument_factory Chord collision for '{k}', use force to replace"
                    )
                results[k] = f
        self._instr.update(results)
