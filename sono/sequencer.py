# sequencer.py
# Sequencing and event classes for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Any, Dict, List, Tuple

from .music import Chord, Instrument


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

    class AmNote:
        """A class to represent a note action in an event.

        Attributes:
            instrument (str): The instrument name.
            note (str): The note name.
            action (str): The action to perform (add, rm, add_pluck, pluck).
            duration (int): Duration of the note in samples.
        """

        def __init__(self, instrument: str, note: str, action: str, duration: int):
            """Initialize an AmNote instance.

            Args:
                instrument (str): The instrument name.
                note (str): The note name.
                action (str): The action to perform (add, rm, add_pluck, pluck).
                duration (int): Duration of the note in samples.

            Raises:
                ValueError: If action is invalid or duration is negative.
            """
            if duration < 0:
                raise ValueError("Duration must be non-negative")
            self._instrument = instrument
            self._note = note
            self._duration = duration
            if action not in ("add", "rm", "add_pluck", "pluck"):
                raise ValueError(
                    "AmNote action must be one of: add, rm, add_pluck, pluck"
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

    def add(self, item: object) -> None:
        """Add an item to the event.

        Args:
            item (object): The item to add (e.g., AmNote, AmMSG).
        """
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
        """Get the list of event items.

        Returns:
            object: The item (e.g., AmNote, AmMSG).
        """
        return self._event

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this event.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_time":
                        return_val[self._name]["get_time"] = self.get_time()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_event":
                        return_val[self._name]["get_event"] = self.get_event()
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the event's state for storage.

        Returns:
            Dict[str, Any]: A dictionary containing the event's properties and items.
        """
        return {
            "get_type": self.get_type(),
            "get_time": self.get_time(),
            "get_name": self.get_name(),
            "get_event": self.get_event()
        }


class EventList:
    """A class to manage a list of timed events.

    Attributes:
        event_list (List[Tuple[int, Event]]): List of (ptime, Event) tuples, sorted by time.
        name (str): Unique identifier for the event list.
    """

    def __init__(self, event_list: List[Event] | None = None, name: str | None = None):
        """Initialize an EventList instance.

        Args:
            event_list (List[Event], optional): Initial list of events.
            name (str, optional): Unique identifier for the event list.
        """
        self._TYPE = "EventList"
        self._event_list: List[Tuple[int, Event]] = []
        if event_list:
            for event in event_list:
                self._event_list.append((event.get_time(), event))
            self._event_list.sort(key=lambda e: e[0])
        self._name = name or f"{self._TYPE}_{id(self)}"

    def add_event(self, entry: Event) -> None:
        """Add an event to the list and sort by time.

        Args:
            entry (Event): The event to add.

        Raises:
            ValueError: If entry is not an Event instance.
        """
        if not isinstance(entry, Event):
            raise ValueError("add_event must be an Event instance")
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

    def remove_event(self, entry: Event) -> None:
        """Remove an event from the list.

        Args:
            entry (Event): The event to remove.

        Raises:
            ValueError: If entry is not in the list.
        """
        for i, (pt, event) in enumerate(self._event_list):
            if event is entry:
                self._event_list.pop(i)
                return
        raise ValueError("Event not found in list")

    def get_name(self) -> str:
        """Get the unique identifier of the event list.

        Returns:
            str: The event list's name.
        """
        return self._name

    def set_name(self, name: str) -> None:
        """Set the unique identifier of the event list.

        Args:
            name (str): The new name.
        """
        self._name = name

    def get_type(self) -> str:
        """Get the type identifier of the event list.

        Returns:
            str: The type string ("EventList").
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
        messages to be routed through to individual events in the list.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this
                event list and/or its contained events.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands,
                including results from underlying events.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_event_list":
                        return_val[self._name]["get_event_list"] = self.get_event_list()
                    elif cmd == "next_event":
                        return_val[self._name]["next_event"] = self.next_event(val[0])
                    elif cmd == "get_ptime_list":
                        return_val[self._name]["get_ptime_list"] = self.get_ptime_list()
                    elif cmd == "get_events":
                        return_val[self._name]["get_events"] = self.get_events(val[0])
                # Route messages to underlying events
                for pt, event in self._event_list:
                    event_val = event.msg(msg)
                    if event_val:
                        return_val[self._name][event.get_name()] = event_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the event list's state for storage.

        Returns:
            Dict[str, Any]: A dictionary containing the event list's properties
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
        channels (Dict[str, Dict[str, EventList | List[Instrument]]]): Dictionary
            where top-level keys are EventList names, each containing:
            - "event_list": the EventList instance
            - "instruments": list of associated Instrument instances
        name (str): Unique identifier for the sequencer.
        time (int): Current time in samples.
        active_notes (Dict[str, Tuple[Chord, int]]): Active chords with their end times.
        next_event_time (int): Time of the next event to process.
        event_pointers (Dict[str, int]): Event pointers for each event list.
    """

    def __init__(
        self,
        channels: Dict[str, Dict[str, EventList | List[Instrument]]] | None = None,
        name: str | None = None,
    ):
        """Initialize a Sequencer instance.

        Args:
            channels (Dict[str, Dict[str, EventList | List[Instrument]]], optional):
                Dictionary where top-level keys are EventList names, each containing:
                - "event_list": the EventList instance
                - "instruments": list of associated Instrument instances
            name (str, optional): Unique identifier for the sequencer.
        """
        self._TYPE = "Sequencer"
        self._channels: Dict[str, Dict[str, EventList | List[Instrument]]] = channels or {}
        self._event_q: Dict[str, List[int]] = {}
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._time: int = 0
        self._active_notes: Dict[str, Tuple[Chord, int]] = {}
        self._next_event_time: int = 0
        self._event_pointers: Dict[str, int] = {k: 0 for k in self._channels}
        self._start: bool = True
        self._next_event: int = 0
        self.init()

    def add_channel(
        self,
        name: str,
        event_list: EventList,
        instruments: List[Instrument] | None = None,
    ) -> None:
        """Add a channel to the sequencer.

        Args:
            name (str): The channel name (typically the EventList name).
            event_list (EventList): The event list for this channel.
            instruments (List[Instrument], optional): List of instruments for this channel.
        """
        self._channels[name] = {
            "event_list": event_list,
            "instruments": instruments or [],
        }
        self._event_pointers[name] = 0
        self.generate_event_queue()

    def get_channel(self, name: str) -> Dict[str, EventList | List[Instrument]]:
        """Get a channel by name.

        Args:
            name (str): The channel name.

        Returns:
            Dict containing 'event_list' and 'instruments'.
        """
        if name in self._channels:
            return self._channels[name]
        raise ValueError(f"{name} channel not found in _channels")

    def get_event_list(self, name: str) -> EventList:
        """Get the EventList from a channel.

        Args:
            name (str): The channel name.

        Returns:
            EventList: The event list for this channel.
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

    def sample(self) -> Tuple[float, ...]:
        """Generate the next audio sample by processing active notes.

        Returns:
            Tuple[float, ...]: The samples from active notes.
        """
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
                return self.process_events()

            if next_times:
                self._next_event_time = min(next_times)

            self._time += 1
        else:
            pass

    def process_events(self) -> Tuple[float, ...]:
        """Process events at the current time, updating active notes.

        Returns:
            Tuple[float, ...]: The samples from active notes.
        """
        return ()
