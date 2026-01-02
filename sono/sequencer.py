# sequencer.py
# Sequencing and event classes for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Any, Dict, List, Tuple

from .music import Chord, Instrument


class DuplicateAmChordError(Exception):
    """Exception raised when attempting to add a second AmChord at the same ptime."""

    def __init__(self, ptime: int):
        self.ptime = ptime
        super().__init__(f"An AmChord already exists at ptime {ptime}")


class Event:
    """A class to represent a timed event in a sequence.

    Attributes:
        time (int): The time of the event in samples.
        items (List[object]): List of event items (e.g., notes, messages).
        name (str): Unique identifier for the event.
    """

    def __init__(
        self, ptime: int, event: object | None = None, name: str | None = None
    ):
        """Initialize an Event instance.

        Args:
            ptime (int): The time of the event in samples.
            event (object, optional): Initial item of event type.
            name (str, optional): Unique identifier for the event.

        Raises:
            ValueError: If ptime is negative.
        """
        self._TYPE = "Event"
        if ptime < 0:
            raise ValueError("Event time must be non-negative")
        self._time = ptime
        self._event = event if event else None
        self._name = name or f"{self._TYPE}_{id(self)}"

    class AmChord:
        """A class to represent a chord action in an event.

        Attributes:
            instrument (str): The instrument name.
            chord (Chord): The chord to play.
            action (str): The action to perform (add, rm, add_pluck, pluck).
            duration (int): Duration of the chord in samples.
        """

        def __init__(self, instrument: str, chord: Chord, action: str, duration: int):
            """Initialize an AmChord instance.

            Args:
                instrument (str): The instrument name.
                chord (Chord): The chord to play.
                action (str): The action to perform (add, rm, add_pluck, pluck).
                duration (int): Duration of the chord in samples.

            Raises:
                ValueError: If action is invalid, duration is negative, or chord is not a Chord.
            """
            if duration < 0:
                raise ValueError("Duration must be non-negative")
            if not isinstance(chord, Chord):
                raise ValueError("chord must be a Chord instance")
            self._instrument = instrument
            self._chord = chord
            self._duration = duration
            if action not in ("add", "rm", "add_pluck", "pluck"):
                raise ValueError(
                    "AmChord action must be one of: add, rm, add_pluck, pluck"
                )
            self._action = action

    class AmException:
        """A class to represent an exception event.

        Attributes:
            message (str): The exception message.
        """

        def __init__(self, message: str):
            """Initialize an AmException instance.

            Args:
                message (str): The exception message.
            """
            self._message = message

    class AmLyric:
        """A class to represent a lyric event.

        Attributes:
            text (str): The lyric text.
        """

        def __init__(self, text: str):
            """Initialize an AmLyric instance.

            Args:
                text (str): The lyric text.
            """
            self._text = text

    class AmMSG:
        """A class to represent a message event.

        Attributes:
            msg (Dict[str, Any]): The message dictionary.
        """

        def __init__(self, msg: Dict[str, Any]):
            """Initialize an AmMSG instance.

            Args:
                msg (Dict[str, Any]): The message dictionary.
            """
            self._msg = msg

    def add_event(self, item: "Event.AmChord | Event.AmException | Event.AmLyric | Event.AmMSG") -> None:
        """Add an item to the event.

        Args:
            item: The item to add (AmChord, AmException, AmLyric, or AmMSG).

        Raises:
            ValueError: If item is not one of the valid event types.
        """
        if not isinstance(item, (Event.AmChord, Event.AmException, Event.AmLyric, Event.AmMSG)):
            raise ValueError(
                "item must be one of: Event.AmChord, Event.AmException, Event.AmLyric, Event.AmMSG"
            )
        self._event = item

    def get_type(self) -> str:
        """Get the type identifier of the event.

        Returns:
            str: The type string ("Event").
        """
        return self._TYPE

    def get_time(self) -> int:
        """Get the time of the event.

        Returns:
            int: The time in samples.
        """
        return self._time

    def set_time(self, ptime: int) -> None:
        """Set the time of the event.

        Args:
            ptime (int): The time in samples.

        Raises:
            ValueError: If ptime is negative.
        """
        if ptime < 0:
            raise ValueError("Event time must be non-negative")
        self._time = ptime

    def get_name(self) -> str:
        """Get the unique identifier of the event.

        Returns:
            str: The event's name.
        """
        return self._name

    def set_name(self, name: str) -> None:
        """Set the unique identifier of the event.

        Args:
            name (str): The new name.
        """
        self._name = name

    def get_event(self) -> object:
        """Get the event item.

        Returns:
            object: The event item (AmChord, AmException, AmLyric, or AmMSG), or None if not set.
        """
        return self._event

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this event.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands.
        """
        current_name = self._name
        return_val: Dict[str, Any] = {current_name: {}}
        for name in msg:
            if name == current_name:
                for cmd, val in msg[name].items():
                    if cmd == "get_time":
                        return_val[current_name]["get_time"] = self.get_time()
                    elif cmd == "set_time":
                        self.set_time(val[0])
                    elif cmd == "get_type":
                        return_val[current_name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[current_name]["get_name"] = self.get_name()
                    elif cmd == "set_name":
                        self.set_name(val[0])
                    elif cmd == "get_event":
                        return_val[current_name]["get_event"] = self.get_event()
        return return_val

    def _dump_event_item(self) -> Dict[str, Any] | None:
        """Serialize the embedded event item.

        Returns:
            Dict[str, Any] | None: Serialized event item, or None if not set.
        """
        if self._event is None:
            return None
        if isinstance(self._event, Event.AmChord):
            return {
                "type": "AmChord",
                "instrument": self._event._instrument,
                "chord": self._event._chord.dump(),
                "action": self._event._action,
                "duration": self._event._duration,
            }
        elif isinstance(self._event, Event.AmException):
            return {
                "type": "AmException",
                "message": self._event._message,
            }
        elif isinstance(self._event, Event.AmLyric):
            return {
                "type": "AmLyric",
                "text": self._event._text,
            }
        elif isinstance(self._event, Event.AmMSG):
            return {
                "type": "AmMSG",
                "msg": self._event._msg,
            }
        return None

    def dump(self) -> Dict[str, Any]:
        """Serialize the event's state for storage and reproduction.

        Returns:
            Dict[str, Any]: A dictionary containing all state needed to reproduce the event.
        """
        return {
            "get_type": self.get_type(),
            "get_time": self.get_time(),
            "get_name": self.get_name(),
            "event": self._dump_event_item(),
        }


class Channel:
    """A class to manage a channel of timed events.

    Attributes:
        event_list (List[Tuple[int, Event]]): List of (ptime, Event) tuples, sorted by time.
        name (str): Unique identifier for the channel.
    """

    def __init__(self, event_list: List[Event] | None = None, name: str | None = None):
        """Initialize a Channel instance.

        Args:
            event_list (List[Event], optional): Initial list of events.
            name (str, optional): Unique identifier for the channel.

        Raises:
            DuplicateAmChordError: If multiple AmChords exist at the same ptime.
        """
        self._TYPE = "Channel"
        self._event_list: List[Tuple[int, Event]] = []
        self._name = name or f"{self._TYPE}_{id(self)}"
        if event_list:
            for event in event_list:
                self.add_event(event)

    def add_event(self, entry: Event) -> None:
        """Add an event to the list and sort by time.

        Args:
            entry (Event): The event to add.

        Raises:
            ValueError: If entry is not an Event instance.
            DuplicateAmChordError: If an AmChord already exists at the same ptime.
        """
        if not isinstance(entry, Event):
            raise ValueError("add_event must be an Event instance")
        # Check for duplicate AmChord at same ptime
        if isinstance(entry.get_event(), Event.AmChord):
            ptime = entry.get_time()
            for pt, event in self._event_list:
                if pt == ptime and isinstance(event.get_event(), Event.AmChord):
                    raise DuplicateAmChordError(ptime)
        self._event_list.append((entry.get_time(), entry))
        self._event_list.sort(key=lambda e: e[0])

    def add_event_list(self, event_list: List[Event], offset: int = 0) -> None:
        """Add a list of events with an optional time offset.

        Args:
            event_list (List[Event]): The list of events to add.
            offset (int): Time offset in samples to apply to each event (default: 0).
        """
        for event in event_list:
            if not isinstance(event, Event):
                continue
            event.set_time(event.get_time() + offset)
            self.add_event(event)

    def get_events(self, ptime: int) -> List[Event]:
        """Get all events at the specified ptime.

        Args:
            ptime (int): The presentation time to search for.

        Returns:
            List[Event]: List of events at the specified ptime.
        """
        return [event for pt, event in self._event_list if pt == ptime]

    def remove_event(self, name: str) -> None:
        """Remove an event from the list by name.

        Args:
            name (str): The name identifier of the event to remove.

        Raises:
            ValueError: If no event with that name is found.
        """
        for i, (pt, event) in enumerate(self._event_list):
            if event.get_name() == name:
                self._event_list.pop(i)
                return
        raise ValueError(f"Event '{name}' not found in list")

    def get_name(self) -> str:
        """Get the unique identifier of the channel.

        Returns:
            str: The channel's name.
        """
        return self._name

    def set_name(self, name: str) -> None:
        """Set the unique identifier of the channel.

        Args:
            name (str): The new name.
        """
        self._name = name

    def get_type(self) -> str:
        """Get the type identifier of the channel.

        Returns:
            str: The type string ("Channel").
        """
        return self._TYPE

    def get_event_list(self) -> List[Event]:
        """Get the list of events.

        Returns:
            List[Event]: The list of events in original format.
        """
        return [event for pt, event in self._event_list]

    def next_event(self, ptime: int) -> int | None:
        """Find the next event time equal to or greater than the given ptime.

        Args:
            ptime (int): The presentation time to search for.

        Returns:
            int | None: The ptime of the first event with time >= ptime, or None if no such event exists.
        """
        for pt, event in self._event_list:
            if pt >= ptime:
                return pt
        return None

    def get_ptime_list(self) -> List[int]:
        """Get a sorted list of unique event times.

        Returns:
            List[int]: Sorted list of unique ptimes, earliest first at index 0.
        """
        seen: set[int] = set()
        result: List[int] = []
        for pt, event in self._event_list:
            if pt not in seen:
                seen.add(pt)
                result.append(pt)
        return result

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Connects canonically to underlying Event msg interfaces, allowing
        messages to be routed through to individual events in the channel.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this
                channel and/or its contained events.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands,
                including results from underlying events.
        """
        current_name = self._name
        return_val: Dict[str, Any] = {current_name: {}}
        for name in msg:
            if name == current_name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[current_name]["get_name"] = self.get_name()
                    elif cmd == "set_name":
                        self.set_name(val[0])
                    elif cmd == "get_type":
                        return_val[current_name]["get_type"] = self.get_type()
                    elif cmd == "get_event_list":
                        return_val[current_name]["get_event_list"] = self.get_event_list()
                    elif cmd == "next_event":
                        return_val[current_name]["next_event"] = self.next_event(val[0])
                    elif cmd == "get_ptime_list":
                        return_val[current_name]["get_ptime_list"] = self.get_ptime_list()
                    elif cmd == "get_events":
                        return_val[current_name]["get_events"] = self.get_events(val[0])
                # Route messages to underlying events
                for pt, event in self._event_list:
                    event_val = event.msg(msg)
                    if event_val:
                        return_val[current_name][event.get_name()] = event_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the channel's state for storage.

        Returns:
            Dict[str, Any]: A dictionary containing the channel's properties
                and all contained events in original format.
        """
        return_val: Dict[str, Any] = {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "events": [event.dump() for pt, event in self._event_list],
        }
        return return_val


class Sequencer:
    """A class to sequence audio events and generate samples.

    Attributes:
        channels (Dict[str, Dict[str, Channel | List[Instrument]]]): Dictionary
            where top-level keys are Channel names, each containing:
            - "event_list": the Channel instance
            - "instruments": list of associated Instrument instances
        name (str): Unique identifier for the sequencer.
        time (int): Current time in samples.
        active_chords (Dict[str, Dict[str, Tuple[Chord, int]]]): Channel-based active chords.
            Outer key is channel name, inner dict maps chord name to (Chord, end_time).
        next_event_time (int): Time of the next event to process.
        event_pointers (Dict[str, int]): Event pointers for each channel.
    """

    def __init__(
        self,
        channels: Dict[str, Dict[str, Channel | List[Instrument]]] | None = None,
        name: str | None = None,
    ):
        """Initialize a Sequencer instance.

        Args:
            channels (Dict[str, Dict[str, Channel | List[Instrument]]], optional):
                Dictionary where top-level keys are Channel names, each containing:
                - "event_list": the Channel instance
                - "instruments": list of associated Instrument instances
            name (str, optional): Unique identifier for the sequencer.
        """
        self._TYPE = "Sequencer"
        self._channels: Dict[str, Dict[str, Channel | List[Instrument]]] = channels or {}
        self._event_q: Dict[str, List[int]] = {}
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._time: int = 0
        self._active_chords: Dict[str, Dict[str, Tuple[Chord, int]]] = {}
        self._next_event_time: int = 0
        self._event_pointers: Dict[str, int] = {k: 0 for k in self._channels}
        self.init()

    def add_channel(
        self,
        name: str,
        event_list: Channel,
        instruments: List[Instrument] | None = None,
    ) -> None:
        """Add a channel to the sequencer.

        Args:
            name (str): The channel name (typically the Channel name).
            event_list (Channel): The channel instance for this channel.
            instruments (List[Instrument], optional): List of instruments for this channel.
        """
        self._channels[name] = {
            "event_list": event_list,
            "instruments": instruments or [],
        }
        self._event_pointers[name] = 0
        self._active_chords[name] = {}
        self.generate_event_queue()

    def get_channel(self, name: str) -> Dict[str, Channel | List[Instrument]]:
        """Get a channel by name.

        Args:
            name (str): The channel name.

        Returns:
            Dict containing 'event_list' and 'instruments'.
        """
        if name in self._channels:
            return self._channels[name]
        raise ValueError(f"{name} channel not found in _channels")

    def get_event_list(self, name: str) -> Channel:
        """Get the Channel from a channel entry.

        Args:
            name (str): The channel name.

        Returns:
            Channel: The channel instance for this channel entry.
        """
        if name in self._channels:
            return self._channels[name]["event_list"]
        raise ValueError(f"{name} channel not found in _channels")

    def get_instruments(self, name: str) -> List[Instrument]:
        """Get the instruments from a channel.

        Args:
            name (str): The channel name.

        Returns:
            List[Instrument]: The instruments for this channel.
        """
        if name in self._channels:
            return self._channels[name]["instruments"]
        raise ValueError(f"{name} channel not found in _channels")

    def remove_channel(self, name: str) -> None:
        """Remove a channel from the sequencer.

        Args:
            name (str): The channel name to remove.
        """
        if name in self._channels:
            del self._channels[name]
            if name in self._event_pointers:
                del self._event_pointers[name]
            self.generate_event_queue()
        else:
            raise ValueError(f"{name} channel not found in _channels")

    def generate_event_queue(self) -> None:
        """Generate the event queue from all channels."""
        self._event_q = {}
        for key, channel in self._channels.items():
            event_list = channel["event_list"]
            self._event_q[key] = []
            f = True
            n = -1
            while f:
                r = event_list.next_event(n)
                if isinstance(r, int):
                    self._event_q[key].append(r)
                    n = r + 1
                else:
                    f = False
        print(self._event_q)

    def add_instrument_to_channel(self, channel_name: str, instrument: Instrument) -> None:
        """Add an instrument to an existing channel.

        Args:
            channel_name (str): The channel name.
            instrument (Instrument): The instrument to add.
        """
        if channel_name in self._channels:
            self._channels[channel_name]["instruments"].append(instrument)
        else:
            raise ValueError(f"{channel_name} channel not found in _channels")

    def init(self) -> None:
        self.generate_event_queue()
        """Initialize or reset the sequencer state."""
        pass

    def sample(self) -> List[Tuple[str, float]]:
        """Generate the next audio sample by polling each channel's active chords.

        Returns:
            List[Tuple[str, float]]: List of (channel_name, sample_value) tuples,
                one entry per channel.
        """
        # Check if we need to process events at current time
        if self._time == self._next_event_time:
            scheduled_events: Dict[str, int] = {}
            next_times: List[int] = []

            for name, channel in self._channels.items():
                event_list = channel["event_list"]
                event_time = event_list.next_event(self._time)
                if event_time is not None and event_time == self._time:
                    scheduled_events[name] = event_time

                next_time = event_list.next_event(self._time + 1)
                if next_time is not None:
                    next_times.append(next_time)

            if scheduled_events:
                self.process_events()

            if next_times:
                self._next_event_time = min(next_times)

        # Poll each channel's active chords and generate samples
        result: List[Tuple[str, float]] = []
        for channel_name in self._channels:
            channel_sample = 0.0
            chords_to_remove: List[str] = []

            # Sum samples from all active chords in this channel
            if channel_name in self._active_chords:
                for chord_name, (chord, end_time) in self._active_chords[channel_name].items():
                    if self._time < end_time:
                        channel_sample += chord.sample()
                    else:
                        chords_to_remove.append(chord_name)

                # Remove expired chords
                for chord_name in chords_to_remove:
                    del self._active_chords[channel_name][chord_name]

            result.append((channel_name, channel_sample))

        self._time += 1
        return result

    def process_events(self) -> List[Tuple[str, float]]:
        """Process events at the current time, updating active chords.

        Returns:
            List[Tuple[str, float]]: List of (channel_name, sample_value) tuples.
        """
        result: List[Tuple[str, float]] = []

        for channel_name, channel in self._channels.items():
            event_list = channel["event_list"]
            events = event_list.get_events(self._time)

            # Initialize channel's active chords dict if needed
            if channel_name not in self._active_chords:
                self._active_chords[channel_name] = {}

            for event in events:
                event_item = event.get_event()
                if isinstance(event_item, Event.AmChord):
                    chord = event_item._chord
                    action = event_item._action
                    duration = event_item._duration
                    chord_name = chord.get_name()

                    if action in ("add", "add_pluck"):
                        # Add chord to active chords with end time
                        end_time = self._time + duration
                        self._active_chords[channel_name][chord_name] = (chord, end_time)
                        chord.set_on()
                        if action == "add_pluck":
                            chord.sample_pluck()
                    elif action == "pluck":
                        # Pluck existing chord if present
                        if chord_name in self._active_chords[channel_name]:
                            self._active_chords[channel_name][chord_name][0].sample_pluck()
                    elif action == "rm":
                        # Remove chord from active chords
                        if chord_name in self._active_chords[channel_name]:
                            self._active_chords[channel_name][chord_name][0].set_off()
                            del self._active_chords[channel_name][chord_name]

            # Generate sample for this channel
            channel_sample = 0.0
            for chord_name, (chord, end_time) in self._active_chords[channel_name].items():
                channel_sample += chord.sample()

            result.append((channel_name, channel_sample))

        return result
