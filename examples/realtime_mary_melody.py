#!/usr/bin/env python3
"""
Example: Real-time "Mary Had a Little Lamb" - Full Melody

Complete melody with proper notes:
Line 1: A-G-F-G-A-A-A, G-G-G, A-C-C
Line 2: A-G-F-G-A-A-A-A, G-G-A-G-F

Syllable-level synchronization with individual note chords.

Playback uses a blocking-write audio loop plus a "shadow pointer" so lyrics
stay in sync with what is actually audible (see RealtimeLyricPlayer).

Requires: sounddevice (pip install sounddevice)
"""

import sys
sys.path.insert(0, '..')

import sono as sl
import sounddevice as sd
import numpy as np
import time
import threading
from queue import Queue, Empty


class RealtimeLyricPlayer:
    """Play audio with a blocking write loop and display lyrics/controls in
    sync via a "shadow pointer" into the audio stream.

    Why this does not click:

    * The audio path is one thread that only synthesizes and calls
      ``stream.write(...)``. ``write`` blocks until PortAudio has room, so it
      self-throttles to real time, and it does no terminal I/O, so printing can
      never stall it. PortAudio pulls from its own C-level ring buffer, so there
      is no per-block *Python* callback competing for the GIL — which was the
      source of the per-note clicks in the callback design.

    * Lyric/control display runs on a separate thread at a relaxed cadence. It
      never touches the audio path; it only reads a shadow pointer that reports
      how many frames have actually left the DAC, and prints events whose sample
      time has been reached. Lyric-sync tolerance is tens of milliseconds, so
      loose polling is more than adequate.
    """

    def __init__(self, sequencer, total_samples, sample_rate=44100,
                 blocksize=1024, gain=0.9):
        self.sequencer = sequencer
        self.total_samples = total_samples
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.gain = gain
        self.playing = False
        # Events discovered by the writer (which runs ahead of playback),
        # consumed by the display thread once their sample time is *heard*.
        self.events = Queue()
        self._stream = None
        self._t0 = None          # stream time captured at start
        self._latency = 0.0      # output latency (s): write cursor -> DAC

    # --- shadow pointer -----------------------------------------------------
    def _heard_frames(self):
        """Frames that have actually exited the DAC so far.

        The stream clock advances at the sample rate; the first written sample
        is heard one output-latency later. So the audible position in frames is
        ``(now - start - latency) * sample_rate``. This is the "data exiting the
        buffer" cursor the lyrics are aligned to.
        """
        if self._t0 is None:
            return 0
        try:
            elapsed = self._stream.time - self._t0 - self._latency
        except Exception:
            # Stream stopped/closed: flush anything still pending.
            return self.total_samples
        return max(0, int(elapsed * self.sample_rate))

    # --- audio path (no I/O, never stalls) ----------------------------------
    def _writer(self):
        buf = np.empty((self.blocksize, 1), dtype=np.float32)
        i = 0
        while self.sequencer.get_time() < self.total_samples and self.playing:
            result = self.sequencer.sample()[0]        # single channel: "main"
            buf[i, 0] = result["sample"] * self.gain
            i += 1

            # Discover lyric/control events early and tag them with the sample
            # time at which they occur; the display thread shows them later,
            # once that sample is actually heard.
            t = self.sequencer.get_time()
            for syl in result["sync_lyrics"]:
                self.events.put((t, "sync_lyric", syl))
            for ctl in result["controls"]:
                self.events.put((t, "control", ctl))

            if i == self.blocksize:
                np.clip(buf, -1.0, 1.0, out=buf)
                self._stream.write(buf)                # blocks -> real-time throttle
                i = 0

        if i:
            self._stream.write(np.clip(buf[:i], -1.0, 1.0))

    # --- display path (relaxed cadence, off the audio path) -----------------
    def _display(self):
        print("\n" + "=" * 60)
        print("🐑  MARY HAD A LITTLE LAMB  🐑")
        print("=" * 60 + "\n")

        pending = []
        cur_sentence, cur_word = None, -1

        while self.playing or pending or not self.events.empty():
            # Pull everything the writer has discovered into the local buffer.
            try:
                while True:
                    pending.append(self.events.get_nowait())
            except Empty:
                pass

            heard = self._heard_frames()
            still = []
            for ev in pending:
                ptime, kind, payload = ev
                if ptime > heard:
                    still.append(ev)
                    continue
                time_sec = ptime / self.sample_rate
                if kind == "sync_lyric":
                    sentence = payload["sentence"]
                    word_index = payload["word_index"]
                    if sentence != cur_sentence or word_index != cur_word:
                        cur_sentence, cur_word = sentence, word_index
                        words = sentence.split()
                        shown = " ".join(
                            f"\033[1;33m[{w}]\033[0m" if k == word_index else w
                            for k, w in enumerate(words)
                        )
                        print(f"{time_sec:6.2f}s: {shown}")
                elif kind == "control":
                    params = ", ".join(
                        f"{k}={v}" for k, v in payload["parameters"].items()
                    )
                    print(f"\033[0;36m{time_sec:6.2f}s: 🎛️  "
                          f"{payload['device']}.{payload['action']}({params})\033[0m")
            pending = still
            time.sleep(0.02)     # relaxed: well inside lyric-sync tolerance

    def play(self):
        """Start playback; display lyrics/controls synced to the DAC."""
        self.playing = True
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.blocksize,
        )
        self._stream.start()
        self._t0 = self._stream.time
        self._latency = float(self._stream.latency)

        writer = threading.Thread(target=self._writer, daemon=True)
        display = threading.Thread(target=self._display, daemon=True)
        writer.start()
        display.start()

        try:
            writer.join()
            # Let the last buffered audio drain so the final lyrics land in sync.
            time.sleep(self._latency + self.blocksize / self.sample_rate + 0.15)
        except KeyboardInterrupt:
            print("\n\nPlayback interrupted by user")
        finally:
            self.playing = False
            display.join(timeout=1)
            self._stream.stop()
            self._stream.close()
            print("\n" + "=" * 60)
            print("Playback complete!")
            print("=" * 60)


def create_song():
    """Create Mary Had a Little Lamb with full melody."""

    sample_rate = 44100

    piano = sl.Instrument(name="piano")

    # The tune sits in octave 4, but its high "sol" (C) belongs an octave up:
    # in this tuning C4 (392 Hz) is *below* F4/A4, which would collapse the
    # "little lamb" leap (mi -> sol) into a downward drop. C5 (784 Hz) sits
    # above A4 (659 Hz), giving the correct ascending interval. Every other
    # note stays in octave 4.
    def octave_for(note_name):
        return 5 if note_name == "C" else 4

    # Build a *fresh* chord instance for every note event. Reusing one shared
    # object per note name makes repeated notes (A-A-A, G-G-G, C-C) click on
    # retrigger, because a chord can't crossfade against itself; with distinct
    # instances the sequencer fades each outgoing note out cleanly instead.
    note_counter = [0]

    def make_note(note_name):
        chord = sl.Chord().make_a_chord(
            (octave_for(note_name), note_name, "major"), pluck=True
        )
        sl.Util.fix_pop(chord)
        piano.add_note(chord, f"{note_name}_{note_counter[0]}")
        note_counter[0] += 1
        return chord

    # Create channel
    channel = sl.Channel(name="main")

    # Timing: quarter note = 0.5 seconds (120 BPM)
    quarter = int(sample_rate * 0.5)
    half = quarter * 2

    # Lyrics with syllables as separate words
    line1 = "Ma ry had a lit tle lamb lit tle lamb lit tle lamb"
    line2 = "Ma ry had a lit tle lamb its fleece was white as snow"

    # Melody for line 1: A-G-F-G-A-A-A, G-G-G, A-C-C
    melody_line1 = [
        ("A", 0, quarter, line1, 0),           # Ma
        ("G", quarter, quarter, line1, 1),     # ry
        ("F", quarter*2, quarter, line1, 2),   # had
        ("G", quarter*3, quarter, line1, 3),   # a
        ("A", quarter*4, quarter, line1, 4),   # lit
        ("A", quarter*5, quarter, line1, 5),   # tle
        ("A", quarter*6, half, line1, 6),      # lamb

        ("G", quarter*8, quarter, line1, 7),   # lit
        ("G", quarter*9, quarter, line1, 8),   # tle
        ("G", quarter*10, half, line1, 9),     # lamb

        ("A", quarter*12, quarter, line1, 10), # lit
        ("C", quarter*13, quarter, line1, 11), # tle
        ("C", quarter*14, half, line1, 12),    # lamb
    ]

    # Melody for line 2: A-G-F-G-A-A-A-A, G-G-A-G-F
    offset = quarter * 16
    melody_line2 = [
        ("A", offset + 0, quarter, line2, 0),           # Ma
        ("G", offset + quarter, quarter, line2, 1),     # ry
        ("F", offset + quarter*2, quarter, line2, 2),   # had
        ("G", offset + quarter*3, quarter, line2, 3),   # a
        ("A", offset + quarter*4, quarter, line2, 4),   # lit
        ("A", offset + quarter*5, quarter, line2, 5),   # tle
        ("A", offset + quarter*6, quarter, line2, 6),   # lamb
        ("A", offset + quarter*7, quarter, line2, 7),   # its

        ("G", offset + quarter*8, quarter, line2, 8),   # fleece
        ("G", offset + quarter*9, quarter, line2, 9),   # was
        ("A", offset + quarter*10, quarter, line2, 10), # white
        ("G", offset + quarter*11, quarter, line2, 11), # as
        ("F", offset + quarter*12, half*2, line2, 12),  # snow
    ]

    melody = melody_line1 + melody_line2

    # Add events
    prev_word_idx = -1
    prev_sentence = None

    for note_name, ptime, duration, sentence, word_idx in melody:
        # Add chord event (fresh chord instance per note -> click-free retrigger)
        event = sl.Event(ptime=ptime)
        event.add_event(sl.Event.AmChord(
            instrument="piano",
            chord=make_note(note_name),
            action="add_pluck",
            duration=duration
        ))
        channel.add_event(event)

        # Add synchronized lyric
        if sentence != prev_sentence or word_idx != prev_word_idx:
            event = sl.Event(ptime=ptime)
            event.add_event(sl.Event.AmSyncLyric(
                sentence=sentence,
                word_index=word_idx
            ))
            channel.add_event(event)
            prev_word_idx = word_idx
            prev_sentence = sentence

    # Add device controls
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="on",
        parameters={"intensity": 0.7, "color": "warm"}
    ))
    channel.add_event(event)

    event = sl.Event(ptime=quarter*6)
    event.add_event(sl.Event.AmControl(
        device="bell",
        action="ring",
        parameters={"volume": 0.5}
    ))
    channel.add_event(event)

    event = sl.Event(ptime=offset + quarter*12)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="fade_out",
        parameters={"duration": 2.0}
    ))
    channel.add_event(event)

    # Create sequencer
    seq = sl.Sequencer(sample_rate=sample_rate)
    seq.add_channel("main", channel, instruments=[piano])

    return seq, offset + quarter * 16


def main():
    """Run real-time playback with full melody."""

    print("Creating 'Mary Had a Little Lamb' with full melody...")
    print("Line 1: A-G-F-G-A-A-A, G-G-G, A-C-C")
    print("Line 2: A-G-F-G-A-A-A-A, G-G-A-G-F")
    seq, total_samples = create_song()

    print("\nStarting real-time playback...")
    print("Press Ctrl+C to stop\n")

    player = RealtimeLyricPlayer(seq, total_samples)
    player.play()


if __name__ == "__main__":
    main()
