import unittest
import math
import sono as sl

class TestEventDefaults(unittest.TestCase):
    """Tests for Event default values after instantiation."""

    def test_default_type(self):
        """Check that default _TYPE is 'Event'."""
        event = sl.Event(ptime=0)
        self.assertEqual(event.get_type(), "Event")

    def test_default_name_format(self):
        """Check that default name starts with 'Event_'."""
        event = sl.Event(ptime=0)
        self.assertTrue(event.get_name().startswith("Event_"))

    def test_default_name_is_unique(self):
        """Check that each instance gets a unique name."""
        event1 = sl.Event(ptime=0)
        event2 = sl.Event(ptime=0)
        self.assertNotEqual(event1.get_name(), event2.get_name())

    def test_default_event_is_none(self):
        """Check that default event item is None."""
        event = sl.Event(ptime=0)
        self.assertIsNone(event.get_event())

    def test_ptime_is_set(self):
        """Check that ptime is set correctly."""
        event = sl.Event(ptime=100)
        self.assertEqual(event.get_time(), 100)


class TestEventCustomArgs(unittest.TestCase):
    """Tests for Event initialization with custom arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        event = sl.Event(ptime=0, name="my_event")
        self.assertEqual(event.get_name(), "my_event")

    def test_custom_ptime(self):
        """Check that custom ptime is set correctly."""
        event = sl.Event(ptime=44100)
        self.assertEqual(event.get_time(), 44100)

    def test_custom_event_amchord(self):
        """Check that custom AmChord event is set correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event = sl.Event(ptime=0, event=am_chord)
        self.assertEqual(event.get_event(), am_chord)

    def test_custom_event_amexception(self):
        """Check that custom AmException event is set correctly."""
        am_exc = sl.Event.AmException("test error")
        event = sl.Event(ptime=0, event=am_exc)
        self.assertEqual(event.get_event(), am_exc)

    def test_custom_event_amlyric(self):
        """Check that custom AmLyric event is set correctly."""
        am_lyric = sl.Event.AmLyric("Hello world")
        event = sl.Event(ptime=0, event=am_lyric)
        self.assertEqual(event.get_event(), am_lyric)

    def test_custom_event_ammsg(self):
        """Check that custom AmMSG event is set correctly."""
        am_msg = sl.Event.AmMSG({"test": {"cmd": [1, 2, 3]}})
        event = sl.Event(ptime=0, event=am_msg)
        self.assertEqual(event.get_event(), am_msg)


class TestEventValidation(unittest.TestCase):
    """Tests for Event constructor validation."""

    def test_negative_ptime_raises_error(self):
        """Check that negative ptime raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.Event(ptime=-1)
        self.assertIn("non-negative", str(ctx.exception))

    def test_zero_ptime_is_valid(self):
        """Check that ptime=0 is valid."""
        event = sl.Event(ptime=0)
        self.assertEqual(event.get_time(), 0)


class TestEventSetters(unittest.TestCase):
    """Tests for Event setter methods."""

    def test_set_time(self):
        """Check that set_time updates the time."""
        event = sl.Event(ptime=0)
        event.set_time(44100)
        self.assertEqual(event.get_time(), 44100)

    def test_set_time_to_zero(self):
        """Check that set_time accepts zero."""
        event = sl.Event(ptime=100)
        event.set_time(0)
        self.assertEqual(event.get_time(), 0)

    def test_set_time_negative_raises_error(self):
        """Check that set_time with negative value raises ValueError."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.set_time(-1)

    def test_set_name(self):
        """Check that set_name updates the name."""
        event = sl.Event(ptime=0)
        event.set_name("new_name")
        self.assertEqual(event.get_name(), "new_name")


class TestEventAddEvent(unittest.TestCase):
    """Tests for Event add_event method."""

    def test_add_event_amchord(self):
        """Check that add_event accepts AmChord."""
        event = sl.Event(ptime=0)
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event.add_event(am_chord)
        self.assertEqual(event.get_event(), am_chord)

    def test_add_event_amexception(self):
        """Check that add_event accepts AmException."""
        event = sl.Event(ptime=0)
        am_exc = sl.Event.AmException("error message")
        event.add_event(am_exc)
        self.assertEqual(event.get_event(), am_exc)

    def test_add_event_amlyric(self):
        """Check that add_event accepts AmLyric."""
        event = sl.Event(ptime=0)
        am_lyric = sl.Event.AmLyric("lyrics here")
        event.add_event(am_lyric)
        self.assertEqual(event.get_event(), am_lyric)

    def test_add_event_ammsg(self):
        """Check that add_event accepts AmMSG."""
        event = sl.Event(ptime=0)
        am_msg = sl.Event.AmMSG({"key": "value"})
        event.add_event(am_msg)
        self.assertEqual(event.get_event(), am_msg)

    def test_add_event_invalid_string_raises_error(self):
        """Check that add_event rejects string."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError) as ctx:
            event.add_event("invalid")
        self.assertIn("must be one of", str(ctx.exception))

    def test_add_event_invalid_int_raises_error(self):
        """Check that add_event rejects int."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.add_event(42)

    def test_add_event_invalid_dict_raises_error(self):
        """Check that add_event rejects plain dict."""
        event = sl.Event(ptime=0)
        with self.assertRaises(ValueError):
            event.add_event({"not": "AmMSG"})

    def test_add_event_replaces_existing(self):
        """Check that add_event replaces existing event."""
        event = sl.Event(ptime=0)
        lyric1 = sl.Event.AmLyric("first")
        lyric2 = sl.Event.AmLyric("second")
        event.add_event(lyric1)
        event.add_event(lyric2)
        self.assertEqual(event.get_event(), lyric2)


class TestEventAmChord(unittest.TestCase):
    """Tests for Event.AmChord embedded class."""

    def test_amchord_creation(self):
        """Check that AmChord can be created."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertIsNotNone(am_chord)

    def test_amchord_instrument(self):
        """Check that instrument is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("guitar", chord, "add", 44100)
        self.assertEqual(am_chord._instrument, "guitar")

    def test_amchord_chord(self):
        """Check that chord is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertEqual(am_chord._chord, chord)

    def test_amchord_action_add(self):
        """Check that action 'add' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        self.assertEqual(am_chord._action, "add")

    def test_amchord_action_rm(self):
        """Check that action 'rm' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "rm", 44100)
        self.assertEqual(am_chord._action, "rm")

    def test_amchord_action_add_pluck(self):
        """Check that action 'add_pluck' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add_pluck", 44100)
        self.assertEqual(am_chord._action, "add_pluck")

    def test_amchord_action_pluck(self):
        """Check that action 'pluck' is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "pluck", 44100)
        self.assertEqual(am_chord._action, "pluck")

    def test_amchord_action_invalid_raises_error(self):
        """Check that invalid action raises ValueError."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", chord, "invalid", 44100)
        self.assertIn("must be one of", str(ctx.exception))

    def test_amchord_duration(self):
        """Check that duration is stored correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 88200)
        self.assertEqual(am_chord._duration, 88200)

    def test_amchord_duration_zero_is_valid(self):
        """Check that duration=0 is valid."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 0)
        self.assertEqual(am_chord._duration, 0)

    def test_amchord_duration_negative_raises_error(self):
        """Check that negative duration raises ValueError."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", chord, "add", -1)
        self.assertIn("non-negative", str(ctx.exception))

    def test_amchord_invalid_chord_raises_error(self):
        """Check that non-Chord raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            sl.Event.AmChord("piano", "not a chord", "add", 44100)
        self.assertIn("Chord instance", str(ctx.exception))

    def test_amchord_sound_element_raises_error(self):
        """Check that SoundElement (not Chord) raises ValueError."""
        sound = sl.SoundElement()
        with self.assertRaises(ValueError):
            sl.Event.AmChord("piano", sound, "add", 44100)


class TestEventAmException(unittest.TestCase):
    """Tests for Event.AmException embedded class."""

    def test_amexception_creation(self):
        """Check that AmException can be created."""
        am_exc = sl.Event.AmException("test error")
        self.assertIsNotNone(am_exc)

    def test_amexception_message(self):
        """Check that message is stored correctly."""
        am_exc = sl.Event.AmException("error occurred")
        self.assertEqual(am_exc._message, "error occurred")

    def test_amexception_empty_message(self):
        """Check that empty message is allowed."""
        am_exc = sl.Event.AmException("")
        self.assertEqual(am_exc._message, "")


class TestEventAmLyric(unittest.TestCase):
    """Tests for Event.AmLyric embedded class."""

    def test_amlyric_creation(self):
        """Check that AmLyric can be created."""
        am_lyric = sl.Event.AmLyric("hello world")
        self.assertIsNotNone(am_lyric)

    def test_amlyric_text(self):
        """Check that text is stored correctly."""
        am_lyric = sl.Event.AmLyric("sing along")
        self.assertEqual(am_lyric._text, "sing along")

    def test_amlyric_empty_text(self):
        """Check that empty text is allowed."""
        am_lyric = sl.Event.AmLyric("")
        self.assertEqual(am_lyric._text, "")

    def test_amlyric_multiline_text(self):
        """Check that multiline text is allowed."""
        am_lyric = sl.Event.AmLyric("line1\nline2\nline3")
        self.assertEqual(am_lyric._text, "line1\nline2\nline3")


class TestEventAmMSG(unittest.TestCase):
    """Tests for Event.AmMSG embedded class."""

    def test_ammsg_creation(self):
        """Check that AmMSG can be created."""
        am_msg = sl.Event.AmMSG({"test": "value"})
        self.assertIsNotNone(am_msg)

    def test_ammsg_msg(self):
        """Check that msg is stored correctly."""
        msg_dict = {"element": {"set_frequency": [440.0]}}
        am_msg = sl.Event.AmMSG(msg_dict)
        self.assertEqual(am_msg._msg, msg_dict)

    def test_ammsg_empty_dict(self):
        """Check that empty dict is allowed."""
        am_msg = sl.Event.AmMSG({})
        self.assertEqual(am_msg._msg, {})

    def test_ammsg_nested_dict(self):
        """Check that nested dict is allowed."""
        msg_dict = {"a": {"b": {"c": [1, 2, 3]}}}
        am_msg = sl.Event.AmMSG(msg_dict)
        self.assertEqual(am_msg._msg, msg_dict)


class TestEventDump(unittest.TestCase):
    """Tests for Event dump method."""

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        event = sl.Event(ptime=100, name="test_event")
        dump = event.dump()
        self.assertIn("get_type", dump)
        self.assertIn("get_time", dump)
        self.assertIn("get_name", dump)
        self.assertIn("event", dump)

    def test_dump_values_match(self):
        """Check that dump values match the event's properties."""
        event = sl.Event(ptime=44100, name="my_event")
        dump = event.dump()
        self.assertEqual(dump["get_type"], "Event")
        self.assertEqual(dump["get_time"], 44100)
        self.assertEqual(dump["get_name"], "my_event")
        self.assertIsNone(dump["event"])

    def test_dump_with_amchord(self):
        """Check that dump serializes AmChord correctly."""
        chord = sl.Chord().make_a_chord((4, "C", "major"))
        am_chord = sl.Event.AmChord("piano", chord, "add", 44100)
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_chord)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmChord")
        self.assertEqual(dump["event"]["instrument"], "piano")
        self.assertEqual(dump["event"]["action"], "add")
        self.assertEqual(dump["event"]["duration"], 44100)
        self.assertIn("chord", dump["event"])
        self.assertEqual(dump["event"]["chord"]["get_type"], "Chord")

    def test_dump_with_amexception(self):
        """Check that dump serializes AmException correctly."""
        am_exc = sl.Event.AmException("error message")
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_exc)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmException")
        self.assertEqual(dump["event"]["message"], "error message")

    def test_dump_with_amlyric(self):
        """Check that dump serializes AmLyric correctly."""
        am_lyric = sl.Event.AmLyric("song lyrics")
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_lyric)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmLyric")
        self.assertEqual(dump["event"]["text"], "song lyrics")

    def test_dump_with_ammsg(self):
        """Check that dump serializes AmMSG correctly."""
        msg_dict = {"elem": {"cmd": [1, 2]}}
        am_msg = sl.Event.AmMSG(msg_dict)
        event = sl.Event(ptime=0, name="test")
        event.add_event(am_msg)
        dump = event.dump()

        self.assertIsNotNone(dump["event"])
        self.assertEqual(dump["event"]["type"], "AmMSG")
        self.assertEqual(dump["event"]["msg"], msg_dict)


class TestEventMsg(unittest.TestCase):
    """Tests for Event msg method."""

    def test_msg_get_type(self):
        """Check that msg can get type."""
        event = sl.Event(ptime=0, name="test_event")
        result = event.msg({"test_event": {"get_type": []}})
        self.assertEqual(result["test_event"]["get_type"], "Event")

    def test_msg_get_time(self):
        """Check that msg can get time."""
        event = sl.Event(ptime=44100, name="test_event")
        result = event.msg({"test_event": {"get_time": []}})
        self.assertEqual(result["test_event"]["get_time"], 44100)

    def test_msg_set_time(self):
        """Check that msg can set time."""
        event = sl.Event(ptime=0, name="test_event")
        event.msg({"test_event": {"set_time": [88200]}})
        self.assertEqual(event.get_time(), 88200)

    def test_msg_get_name(self):
        """Check that msg can get name."""
        event = sl.Event(ptime=0, name="test_event")
        result = event.msg({"test_event": {"get_name": []}})
        self.assertEqual(result["test_event"]["get_name"], "test_event")

    def test_msg_set_name(self):
        """Check that msg can set name."""
        event = sl.Event(ptime=0, name="old_name")
        event.msg({"old_name": {"set_name": ["new_name"]}})
        self.assertEqual(event.get_name(), "new_name")

    def test_msg_get_event(self):
        """Check that msg can get event."""
        am_lyric = sl.Event.AmLyric("test")
        event = sl.Event(ptime=0, name="test_event", event=am_lyric)
        result = event.msg({"test_event": {"get_event": []}})
        self.assertEqual(result["test_event"]["get_event"], am_lyric)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        event = sl.Event(ptime=100, name="test_event")
        result = event.msg({"other_name": {"set_time": [0]}})
        # Time should remain unchanged
        self.assertEqual(event.get_time(), 100)

    def test_msg_multiple_commands(self):
        """Check that msg can handle multiple commands."""
        event = sl.Event(ptime=44100, name="test_event")
        result = event.msg({
            "test_event": {
                "get_type": [],
                "get_time": [],
                "get_name": []
            }
        })
        self.assertEqual(result["test_event"]["get_type"], "Event")
        self.assertEqual(result["test_event"]["get_time"], 44100)
        self.assertEqual(result["test_event"]["get_name"], "test_event")

    def test_msg_set_name_uses_current_name_for_return(self):
        """Check that msg uses current name for return value after set_name."""
        event = sl.Event(ptime=0, name="old_name")
        result = event.msg({"old_name": {"set_name": ["new_name"], "get_type": []}})
        # The return should use the original name (captured at start)
        self.assertIn("old_name", result)


class TestChannelDefaults(unittest.TestCase):
    """Tests for Channel default values after instantiation."""

    def test_default_type(self):
        """Check that default _TYPE is 'Channel'."""
        channel = sl.Channel()
        self.assertEqual(channel.get_type(), "Channel")

    def test_default_name_format(self):
        """Check that default name starts with 'Channel_'."""
        channel = sl.Channel()
        self.assertTrue(channel.get_name().startswith("Channel_"))

    def test_default_name_is_unique(self):
        """Check that each instance gets a unique name."""
        channel1 = sl.Channel()
        channel2 = sl.Channel()
        self.assertNotEqual(channel1.get_name(), channel2.get_name())

    def test_default_event_list_is_empty(self):
        """Check that default event list is empty."""
        channel = sl.Channel()
        self.assertEqual(channel.get_event_list(), [])

    def test_default_ptime_list_is_empty(self):
        """Check that default ptime list is empty."""
        channel = sl.Channel()
        self.assertEqual(channel.get_ptime_list(), [])


class TestChannelCustomArgs(unittest.TestCase):
    """Tests for Channel with custom constructor arguments."""

    def test_custom_name(self):
        """Check that custom name is set correctly."""
        channel = sl.Channel(name="my_channel")
        self.assertEqual(channel.get_name(), "my_channel")

    def test_custom_event_list(self):
        """Check that custom event_list is set correctly."""
        events = [
            sl.Event(ptime=100, name="event1"),
            sl.Event(ptime=200, name="event2"),
        ]
        channel = sl.Channel(event_list=events)
        self.assertEqual(len(channel.get_event_list()), 2)

    def test_event_list_is_sorted_by_ptime(self):
        """Check that events are sorted by ptime."""
        events = [
            sl.Event(ptime=300, name="event3"),
            sl.Event(ptime=100, name="event1"),
            sl.Event(ptime=200, name="event2"),
        ]
        channel = sl.Channel(event_list=events)
        event_list = channel.get_event_list()
        self.assertEqual(event_list[0].get_name(), "event1")
        self.assertEqual(event_list[1].get_name(), "event2")
        self.assertEqual(event_list[2].get_name(), "event3")

    def test_both_name_and_event_list(self):
        """Check that both name and event_list can be set."""
        events = [sl.Event(ptime=100, name="event1")]
        channel = sl.Channel(event_list=events, name="test_channel")
        self.assertEqual(channel.get_name(), "test_channel")
        self.assertEqual(len(channel.get_event_list()), 1)


class TestChannelValidation(unittest.TestCase):
    """Tests for Channel validation."""

    def test_duplicate_amchord_in_init_raises_error(self):
        """Check that duplicate AmChord at same ptime in init raises error."""
        chord = sl.Chord()
        chord.make_a_chord((4, "C", "major"))

        event1 = sl.Event(ptime=100, name="event1")
        event1.add_event(sl.Event.AmChord("instr1", chord, "add", 100))

        event2 = sl.Event(ptime=100, name="event2")
        event2.add_event(sl.Event.AmChord("instr2", chord, "add", 100))

        with self.assertRaises(sl.DuplicateAmChordError) as ctx:
            sl.Channel(event_list=[event1, event2])
        self.assertEqual(ctx.exception.ptime, 100)

    def test_duplicate_amchord_in_add_event_raises_error(self):
        """Check that duplicate AmChord at same ptime in add_event raises error."""
        chord = sl.Chord()
        chord.make_a_chord((4, "C", "major"))

        event1 = sl.Event(ptime=100, name="event1")
        event1.add_event(sl.Event.AmChord("instr1", chord, "add", 100))

        event2 = sl.Event(ptime=100, name="event2")
        event2.add_event(sl.Event.AmChord("instr2", chord, "add", 100))

        channel = sl.Channel()
        channel.add_event(event1)

        with self.assertRaises(sl.DuplicateAmChordError) as ctx:
            channel.add_event(event2)
        self.assertEqual(ctx.exception.ptime, 100)

    def test_amchord_at_different_ptimes_is_allowed(self):
        """Check that AmChords at different ptimes are allowed."""
        chord = sl.Chord()
        chord.make_a_chord((4, "C", "major"))

        event1 = sl.Event(ptime=100, name="event1")
        event1.add_event(sl.Event.AmChord("instr1", chord, "add", 100))

        event2 = sl.Event(ptime=200, name="event2")
        event2.add_event(sl.Event.AmChord("instr2", chord, "add", 100))

        channel = sl.Channel()
        channel.add_event(event1)
        channel.add_event(event2)  # Should not raise
        self.assertEqual(len(channel.get_event_list()), 2)

    def test_non_amchord_events_at_same_ptime_allowed(self):
        """Check that non-AmChord events at same ptime are allowed."""
        event1 = sl.Event(ptime=100, name="event1")
        event1.add_event(sl.Event.AmLyric("lyrics"))

        event2 = sl.Event(ptime=100, name="event2")
        event2.add_event(sl.Event.AmLyric("more lyrics"))

        channel = sl.Channel()
        channel.add_event(event1)
        channel.add_event(event2)  # Should not raise
        self.assertEqual(len(channel.get_event_list()), 2)

    def test_add_event_with_non_event_raises_error(self):
        """Check that add_event with non-Event raises ValueError."""
        channel = sl.Channel()
        with self.assertRaises(ValueError):
            channel.add_event("not an event")


class TestChannelSetters(unittest.TestCase):
    """Tests for Channel getter and setter methods."""

    def test_get_name(self):
        """Check that get_name returns the name."""
        channel = sl.Channel(name="test_channel")
        self.assertEqual(channel.get_name(), "test_channel")

    def test_set_name(self):
        """Check that set_name updates the name."""
        channel = sl.Channel(name="old_name")
        channel.set_name("new_name")
        self.assertEqual(channel.get_name(), "new_name")

    def test_get_type(self):
        """Check that get_type returns 'Channel'."""
        channel = sl.Channel()
        self.assertEqual(channel.get_type(), "Channel")


class TestChannelAddEvent(unittest.TestCase):
    """Tests for Channel add_event method."""

    def test_add_event_increases_count(self):
        """Check that add_event increases event count."""
        channel = sl.Channel()
        self.assertEqual(len(channel.get_event_list()), 0)
        channel.add_event(sl.Event(ptime=100))
        self.assertEqual(len(channel.get_event_list()), 1)
        channel.add_event(sl.Event(ptime=200))
        self.assertEqual(len(channel.get_event_list()), 2)

    def test_add_event_maintains_sort_order(self):
        """Check that events are kept sorted by ptime."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=300, name="event3"))
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        events = channel.get_event_list()
        self.assertEqual(events[0].get_time(), 100)
        self.assertEqual(events[1].get_time(), 200)
        self.assertEqual(events[2].get_time(), 300)

    def test_add_event_with_same_ptime(self):
        """Check that multiple events at same ptime are allowed."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=100, name="event2"))
        self.assertEqual(len(channel.get_event_list()), 2)


class TestChannelAddEventList(unittest.TestCase):
    """Tests for Channel add_event_list method."""

    def test_add_event_list_adds_all_events(self):
        """Check that add_event_list adds all events."""
        channel = sl.Channel()
        events = [
            sl.Event(ptime=100, name="event1"),
            sl.Event(ptime=200, name="event2"),
            sl.Event(ptime=300, name="event3"),
        ]
        channel.add_event_list(events)
        self.assertEqual(len(channel.get_event_list()), 3)

    def test_add_event_list_with_offset(self):
        """Check that add_event_list applies offset correctly."""
        channel = sl.Channel()
        events = [
            sl.Event(ptime=100, name="event1"),
            sl.Event(ptime=200, name="event2"),
        ]
        channel.add_event_list(events, offset=1000)

        event_list = channel.get_event_list()
        self.assertEqual(event_list[0].get_time(), 1100)
        self.assertEqual(event_list[1].get_time(), 1200)

    def test_add_event_list_skips_non_events(self):
        """Check that add_event_list skips non-Event items."""
        channel = sl.Channel()
        events = [
            sl.Event(ptime=100, name="event1"),
            "not an event",
            sl.Event(ptime=200, name="event2"),
        ]
        channel.add_event_list(events)
        self.assertEqual(len(channel.get_event_list()), 2)


class TestChannelGetEvents(unittest.TestCase):
    """Tests for Channel get_events method."""

    def test_get_events_returns_events_at_ptime(self):
        """Check that get_events returns all events at specified ptime."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=100, name="event2"))
        channel.add_event(sl.Event(ptime=200, name="event3"))

        events = channel.get_events(100)
        self.assertEqual(len(events), 2)
        names = [e.get_name() for e in events]
        self.assertIn("event1", names)
        self.assertIn("event2", names)

    def test_get_events_returns_empty_for_no_match(self):
        """Check that get_events returns empty list when no events at ptime."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        events = channel.get_events(200)
        self.assertEqual(events, [])

    def test_get_events_on_empty_channel(self):
        """Check that get_events returns empty list on empty channel."""
        channel = sl.Channel()
        events = channel.get_events(100)
        self.assertEqual(events, [])


class TestChannelRemoveEvent(unittest.TestCase):
    """Tests for Channel remove_event method."""

    def test_remove_event_by_name(self):
        """Check that remove_event removes event by name."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        channel.remove_event("event1")
        events = channel.get_event_list()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].get_name(), "event2")

    def test_remove_event_not_found_raises_error(self):
        """Check that remove_event raises ValueError for unknown name."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))

        with self.assertRaises(ValueError) as ctx:
            channel.remove_event("unknown")
        self.assertIn("unknown", str(ctx.exception))

    def test_remove_event_from_empty_channel_raises_error(self):
        """Check that remove_event raises ValueError on empty channel."""
        channel = sl.Channel()
        with self.assertRaises(ValueError):
            channel.remove_event("event1")


class TestChannelGetEventList(unittest.TestCase):
    """Tests for Channel get_event_list method."""

    def test_get_event_list_returns_all_events(self):
        """Check that get_event_list returns all events."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        events = channel.get_event_list()
        self.assertEqual(len(events), 2)

    def test_get_event_list_returns_events_in_order(self):
        """Check that get_event_list returns events sorted by ptime."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=300, name="event3"))
        channel.add_event(sl.Event(ptime=100, name="event1"))

        events = channel.get_event_list()
        self.assertEqual(events[0].get_time(), 100)
        self.assertEqual(events[1].get_time(), 300)


class TestChannelNextEvent(unittest.TestCase):
    """Tests for Channel next_event method."""

    def test_next_event_with_mixed_order_events(self):
        """Check that next_event works correctly when events are added in mixed order."""
        channel = sl.Channel()

        # Add events in mixed (non-sorted) order: 500, 100, 300, 200, 400
        channel.add_event(sl.Event(ptime=500, name="event_500"))
        channel.add_event(sl.Event(ptime=100, name="event_100"))
        channel.add_event(sl.Event(ptime=300, name="event_300"))
        channel.add_event(sl.Event(ptime=200, name="event_200"))
        channel.add_event(sl.Event(ptime=400, name="event_400"))

        # Test when ptime matches an event time exactly - should return that time
        self.assertEqual(channel.next_event(100), 100)
        self.assertEqual(channel.next_event(200), 200)
        self.assertEqual(channel.next_event(300), 300)
        self.assertEqual(channel.next_event(400), 400)
        self.assertEqual(channel.next_event(500), 500)

        # Test when ptime is before an event - should return the next event time
        self.assertEqual(channel.next_event(0), 100)
        self.assertEqual(channel.next_event(50), 100)
        self.assertEqual(channel.next_event(99), 100)
        self.assertEqual(channel.next_event(101), 200)
        self.assertEqual(channel.next_event(150), 200)
        self.assertEqual(channel.next_event(250), 300)
        self.assertEqual(channel.next_event(350), 400)
        self.assertEqual(channel.next_event(450), 500)

        # Test when ptime is after all events - should return None
        self.assertIsNone(channel.next_event(501))
        self.assertIsNone(channel.next_event(1000))

    def test_next_event_on_empty_channel(self):
        """Check that next_event returns None on empty channel."""
        channel = sl.Channel()
        self.assertIsNone(channel.next_event(0))


class TestChannelGetPtimeList(unittest.TestCase):
    """Tests for Channel get_ptime_list method."""

    def test_get_ptime_list_returns_unique_ptimes(self):
        """Check that get_ptime_list returns unique ptimes."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=100, name="event2"))
        channel.add_event(sl.Event(ptime=200, name="event3"))

        ptimes = channel.get_ptime_list()
        self.assertEqual(ptimes, [100, 200])

    def test_get_ptime_list_is_sorted(self):
        """Check that get_ptime_list returns sorted ptimes."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=300, name="event3"))
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        ptimes = channel.get_ptime_list()
        self.assertEqual(ptimes, [100, 200, 300])

    def test_get_ptime_list_on_empty_channel(self):
        """Check that get_ptime_list returns empty list on empty channel."""
        channel = sl.Channel()
        self.assertEqual(channel.get_ptime_list(), [])


class TestChannelDump(unittest.TestCase):
    """Tests for Channel dump method."""

    def test_dump_contains_required_keys(self):
        """Check that dump contains all required keys."""
        channel = sl.Channel(name="test_channel")
        dump = channel.dump()

        self.assertIn("get_type", dump)
        self.assertIn("get_name", dump)
        self.assertIn("events", dump)

    def test_dump_values_match_getters(self):
        """Check that dump values match getter methods."""
        channel = sl.Channel(name="test_channel")
        dump = channel.dump()

        self.assertEqual(dump["get_type"], "Channel")
        self.assertEqual(dump["get_name"], "test_channel")
        self.assertEqual(dump["events"], [])

    def test_dump_includes_events(self):
        """Check that dump includes event dumps."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        dump = channel.dump()
        self.assertEqual(len(dump["events"]), 2)
        self.assertEqual(dump["events"][0]["get_name"], "event1")
        self.assertEqual(dump["events"][0]["get_time"], 100)
        self.assertEqual(dump["events"][1]["get_name"], "event2")
        self.assertEqual(dump["events"][1]["get_time"], 200)

    def test_dump_events_are_sorted(self):
        """Check that dump events are sorted by ptime."""
        channel = sl.Channel()
        channel.add_event(sl.Event(ptime=300, name="event3"))
        channel.add_event(sl.Event(ptime=100, name="event1"))

        dump = channel.dump()
        self.assertEqual(dump["events"][0]["get_time"], 100)
        self.assertEqual(dump["events"][1]["get_time"], 300)


class TestChannelMsg(unittest.TestCase):
    """Tests for Channel msg method."""

    def test_msg_get_name(self):
        """Check that msg can get name."""
        channel = sl.Channel(name="test_channel")
        result = channel.msg({"test_channel": {"get_name": []}})
        self.assertEqual(result["test_channel"]["get_name"], "test_channel")

    def test_msg_set_name(self):
        """Check that msg can set name."""
        channel = sl.Channel(name="old_name")
        channel.msg({"old_name": {"set_name": ["new_name"]}})
        self.assertEqual(channel.get_name(), "new_name")

    def test_msg_get_type(self):
        """Check that msg can get type."""
        channel = sl.Channel(name="test_channel")
        result = channel.msg({"test_channel": {"get_type": []}})
        self.assertEqual(result["test_channel"]["get_type"], "Channel")

    def test_msg_get_event_list(self):
        """Check that msg can get event list."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))
        result = channel.msg({"test_channel": {"get_event_list": []}})
        self.assertEqual(len(result["test_channel"]["get_event_list"]), 1)

    def test_msg_next_event(self):
        """Check that msg can call next_event."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        result = channel.msg({"test_channel": {"next_event": [50]}})
        self.assertEqual(result["test_channel"]["next_event"], 100)

        result = channel.msg({"test_channel": {"next_event": [150]}})
        self.assertEqual(result["test_channel"]["next_event"], 200)

    def test_msg_get_ptime_list(self):
        """Check that msg can get ptime list."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=200, name="event2"))

        result = channel.msg({"test_channel": {"get_ptime_list": []}})
        self.assertEqual(result["test_channel"]["get_ptime_list"], [100, 200])

    def test_msg_get_events(self):
        """Check that msg can get events at ptime."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))
        channel.add_event(sl.Event(ptime=100, name="event2"))

        result = channel.msg({"test_channel": {"get_events": [100]}})
        self.assertEqual(len(result["test_channel"]["get_events"]), 2)

    def test_msg_ignores_other_names(self):
        """Check that msg ignores messages for other names."""
        channel = sl.Channel(name="test_channel")
        result = channel.msg({"other_name": {"set_name": ["new_name"]}})
        # Name should remain unchanged
        self.assertEqual(channel.get_name(), "test_channel")

    def test_msg_multiple_commands(self):
        """Check that msg can handle multiple commands."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))

        result = channel.msg({
            "test_channel": {
                "get_type": [],
                "get_name": [],
                "get_ptime_list": []
            }
        })
        self.assertEqual(result["test_channel"]["get_type"], "Channel")
        self.assertEqual(result["test_channel"]["get_name"], "test_channel")
        self.assertEqual(result["test_channel"]["get_ptime_list"], [100])

    def test_msg_set_name_uses_current_name_for_return(self):
        """Check that msg uses current name for return value after set_name."""
        channel = sl.Channel(name="old_name")
        result = channel.msg({"old_name": {"set_name": ["new_name"], "get_type": []}})
        # The return should use the original name (captured at start)
        self.assertIn("old_name", result)

    def test_msg_routes_to_events(self):
        """Check that msg routes messages to contained events."""
        channel = sl.Channel(name="test_channel")
        channel.add_event(sl.Event(ptime=100, name="event1"))

        result = channel.msg({
            "test_channel": {"get_name": []},
            "event1": {"get_time": []}
        })
        # Channel should have routed the message to event1
        self.assertIn("event1", result["test_channel"])


if __name__ == "__main__":
    unittest.main()
