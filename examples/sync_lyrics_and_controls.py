#!/usr/bin/env python3
"""
Example: Word-Synchronized Lyrics and Device Controls

Demonstrates the new Event.AmSyncLyric and Event.AmControl event types.
Creates a simple song with:
- Word-by-word lyric synchronization
- Device control events (lights, bells, etc.)
- Musical chord progression

The AmSyncLyric events show how to display a sentence with a pointer
that advances word-by-word in sync with the music. The sentence persists
until replaced by a new one.

The AmControl events demonstrate triggering external devices like lights,
bells, or relays synchronized with the musical timing.
"""

import sys
sys.path.insert(0, '..')

import sono as sl
import wave
import struct


def create_song():
    """Create a song with synchronized lyrics and device controls."""
    
    # Sample rate
    sample_rate = 44100
    
    # Create instruments
    piano = sl.Instrument(name="piano")
    
    # Create chords for a simple progression: C - Am - F - G
    c_major = sl.Chord().make_a_chord((4, "C", "major"), pluck=True)
    a_minor = sl.Chord().make_a_chord((4, "A", "minor"), pluck=True)
    f_major = sl.Chord().make_a_chord((4, "F", "major"), pluck=True)
    g_major = sl.Chord().make_a_chord((4, "G", "major"), pluck=True)
    
    # Fix phase alignment to avoid clicks
    sl.Util.fix_pop(c_major)
    sl.Util.fix_pop(a_minor)
    sl.Util.fix_pop(f_major)
    sl.Util.fix_pop(g_major)
    
    # Add chords to instrument
    piano.add_note(c_major, "C")
    piano.add_note(a_minor, "Am")
    piano.add_note(f_major, "F")
    piano.add_note(g_major, "G")
    
    # Create channel with events
    channel = sl.Channel(name="main")
    
    # Timing constants (in samples)
    beat = sample_rate  # 1 second per beat at 60 BPM
    half_beat = beat // 2
    quarter_beat = beat // 4
    
    # Lyrics for the song
    # Line 1: "Twinkle twinkle little star"
    line1 = "Twinkle twinkle little star"
    line1_words = line1.split()
    
    # Line 2: "How I wonder what you are"
    line2 = "How I wonder what you are"
    line2_words = line2.split()
    
    # === VERSE 1 ===
    
    # Bar 1: "Twinkle twinkle" - C major
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmChord(
        instrument="piano",
        chord=piano.get_note("C"),
        action="add_pluck",
        duration=beat * 2
    ))
    channel.add_event(event)
    
    # Sync lyric: Start of line 1, word 0 ("Twinkle")
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=0))
    channel.add_event(event)
    
    # Device control: Turn on stage light
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="on",
        parameters={"intensity": 0.8, "color": "white"}
    ))
    channel.add_event(event)
    
    # Word 1 ("twinkle" - second occurrence)
    event = sl.Event(ptime=beat)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=1))
    channel.add_event(event)
    
    # Bar 2: "little star" - Am
    event = sl.Event(ptime=beat * 2)
    event.add_event(sl.Event.AmChord(
        instrument="piano",
        chord=piano.get_note("Am"),
        action="add_pluck",
        duration=beat * 2
    ))
    channel.add_event(event)
    
    # Word 2 ("little")
    event = sl.Event(ptime=beat * 2)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=2))
    channel.add_event(event)
    
    # Device control: Pulse light
    event = sl.Event(ptime=beat * 2)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="pulse",
        parameters={"duration": 0.5}
    ))
    channel.add_event(event)
    
    # Word 3 ("star")
    event = sl.Event(ptime=beat * 3)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=3))
    channel.add_event(event)
    
    # Device control: Ring bell
    event = sl.Event(ptime=beat * 3)
    event.add_event(sl.Event.AmControl(
        device="bell",
        action="ring",
        parameters={"volume": 0.7}
    ))
    channel.add_event(event)
    
    # === VERSE 2 ===
    
    # Bar 3: "How I" - F major
    event = sl.Event(ptime=beat * 4)
    event.add_event(sl.Event.AmChord(
        instrument="piano",
        chord=piano.get_note("F"),
        action="add_pluck",
        duration=beat * 2
    ))
    channel.add_event(event)
    
    # Sync lyric: Start of line 2, word 0 ("How")
    event = sl.Event(ptime=beat * 4)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=0))
    channel.add_event(event)
    
    # Device control: Change light color
    event = sl.Event(ptime=beat * 4)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="set_color",
        parameters={"color": "blue", "transition": 0.5}
    ))
    channel.add_event(event)
    
    # Word 1 ("I")
    event = sl.Event(ptime=beat * 5)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=1))
    channel.add_event(event)
    
    # Bar 4: "wonder what" - G major
    event = sl.Event(ptime=beat * 6)
    event.add_event(sl.Event.AmChord(
        instrument="piano",
        chord=piano.get_note("G"),
        action="add_pluck",
        duration=beat * 2
    ))
    channel.add_event(event)
    
    # Word 2 ("wonder")
    event = sl.Event(ptime=beat * 6)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=2))
    channel.add_event(event)
    
    # Word 3 ("what")
    event = sl.Event(ptime=beat * 7)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=3))
    channel.add_event(event)
    
    # Bar 5: "you are" - C major (resolution)
    event = sl.Event(ptime=beat * 8)
    event.add_event(sl.Event.AmChord(
        instrument="piano",
        chord=piano.get_note("C"),
        action="add_pluck",
        duration=beat * 2
    ))
    channel.add_event(event)
    
    # Word 4 ("you")
    event = sl.Event(ptime=beat * 8)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=4))
    channel.add_event(event)
    
    # Device control: Brighten light
    event = sl.Event(ptime=beat * 8)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="set_intensity",
        parameters={"intensity": 1.0, "transition": 0.3}
    ))
    channel.add_event(event)
    
    # Word 5 ("are")
    event = sl.Event(ptime=beat * 9)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=5))
    channel.add_event(event)
    
    # Final bell ring
    event = sl.Event(ptime=beat * 9)
    event.add_event(sl.Event.AmControl(
        device="bell",
        action="ring",
        parameters={"volume": 1.0}
    ))
    channel.add_event(event)
    
    # Fade out light at end
    event = sl.Event(ptime=beat * 10)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="fade_out",
        parameters={"duration": 2.0}
    ))
    channel.add_event(event)
    
    # Create sequencer
    seq = sl.Sequencer(sample_rate=sample_rate)
    seq.add_channel("main", channel, instruments=[piano])
    
    return seq, beat * 12  # Total duration


def main():
    """Generate the song and display synchronized events."""
    
    print("Creating song with synchronized lyrics and device controls...")
    seq, total_samples = create_song()
    
    # Generate samples and display events
    print("\n=== Song Playback ===\n")
    
    samples = []
    current_sentence = None
    current_word_index = -1
    
    while seq.get_time() < total_samples:
        results = seq.sample()
        
        for result in results:
            # Collect audio sample
            samples.append(result["sample"])
            
            # Display synchronized lyrics
            if result["sync_lyrics"]:
                for sync_lyric in result["sync_lyrics"]:
                    sentence = sync_lyric["sentence"]
                    word_index = sync_lyric["word_index"]
                    
                    # New sentence or word update
                    if sentence != current_sentence or word_index != current_word_index:
                        current_sentence = sentence
                        current_word_index = word_index
                        
                        # Display sentence with pointer
                        words = sentence.split()
                        display = []
                        for i, word in enumerate(words):
                            if i == word_index:
                                display.append(f"[{word}]")  # Current word in brackets
                            else:
                                display.append(word)
                        
                        time_sec = seq.get_time() / 44100
                        print(f"{time_sec:6.2f}s: {' '.join(display)}")
            
            # Display device control events
            if result["controls"]:
                for control in result["controls"]:
                    time_sec = seq.get_time() / 44100
                    device = control["device"]
                    action = control["action"]
                    params = control["parameters"]
                    
                    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                    print(f"{time_sec:6.2f}s: CONTROL {device}.{action}({param_str})")
            
            # Display regular lyrics (if any)
            if result["lyrics"]:
                for lyric in result["lyrics"]:
                    time_sec = seq.get_time() / 44100
                    print(f"{time_sec:6.2f}s: {lyric}")
    
    # Write to WAV file
    print("\n=== Writing to WAV file ===")
    output_file = "sync_lyrics_demo.wav"
    
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(44100)
        
        # Convert samples to 16-bit integers
        for sample in samples:
            # Clamp to [-1, 1] and convert to 16-bit
            clamped = max(-1.0, min(1.0, sample))
            int_sample = int(clamped * 32767)
            wav_file.writeframes(struct.pack('<h', int_sample))
    
    print(f"Wrote {len(samples)} samples to {output_file}")
    print(f"Duration: {len(samples) / 44100:.2f} seconds")
    print("\nThe output demonstrates:")
    print("- Word-by-word lyric synchronization with [brackets] around current word")
    print("- Device control events (lights, bells) synchronized with music")
    print("- Musical chord progression (C - Am - F - G - C)")


if __name__ == "__main__":
    main()
