#!/usr/bin/env python3
"""
Example: Real-time Word-Synchronized Lyrics with Audio Playback

Demonstrates real-time audio playback using sounddevice while displaying
word-synchronized lyrics in the terminal. The lyrics update in real-time
as the song plays, with the current word highlighted.

Requires: sounddevice (pip install sounddevice)
"""

import sys
sys.path.insert(0, '..')

import sono as sl
import sounddevice as sd
import numpy as np
import time
import threading
from queue import Queue


class RealtimeLyricPlayer:
    """Plays audio in real-time while displaying synchronized lyrics."""
    
    def __init__(self, sequencer, total_samples, sample_rate=44100):
        self.sequencer = sequencer
        self.total_samples = total_samples
        self.sample_rate = sample_rate
        self.audio_queue = Queue(maxsize=10)
        self.lyric_queue = Queue()
        self.playing = False
        self.current_sentence = None
        self.current_word_index = -1
        
    def audio_callback(self, outdata, frames, time_info, status):
        """Callback for sounddevice to fill audio buffer."""
        if status:
            print(f"Audio status: {status}")
        
        # Get audio data from queue
        try:
            data = self.audio_queue.get_nowait()
            if len(data) < frames:
                # Pad with zeros if not enough data
                outdata[:len(data)] = data.reshape(-1, 1)
                outdata[len(data):] = 0
            else:
                outdata[:] = data[:frames].reshape(-1, 1)
        except:
            # No data available, output silence
            outdata[:] = 0
    
    def generate_audio(self):
        """Generate audio samples and lyrics in a separate thread."""
        buffer_size = 2048
        buffer = []
        
        while self.sequencer.get_time() < self.total_samples and self.playing:
            results = self.sequencer.sample()
            
            for result in results:
                # Collect audio sample
                buffer.append(result["sample"])
                
                # Check for synchronized lyrics
                if result["sync_lyrics"]:
                    for sync_lyric in result["sync_lyrics"]:
                        self.lyric_queue.put({
                            'type': 'sync_lyric',
                            'sentence': sync_lyric["sentence"],
                            'word_index': sync_lyric["word_index"],
                            'time': self.sequencer.get_time() / self.sample_rate
                        })
                
                # Check for device controls
                if result["controls"]:
                    for control in result["controls"]:
                        self.lyric_queue.put({
                            'type': 'control',
                            'device': control["device"],
                            'action': control["action"],
                            'parameters': control["parameters"],
                            'time': self.sequencer.get_time() / self.sample_rate
                        })
                
                # When buffer is full, send to audio queue
                if len(buffer) >= buffer_size:
                    audio_data = np.array(buffer, dtype=np.float32)
                    self.audio_queue.put(audio_data)
                    buffer = []
        
        # Send remaining buffer
        if buffer:
            audio_data = np.array(buffer, dtype=np.float32)
            self.audio_queue.put(audio_data)
    
    def display_lyrics(self):
        """Display lyrics in real-time in a separate thread."""
        print("\n" + "="*60)
        print("REAL-TIME SYNCHRONIZED LYRICS")
        print("="*60 + "\n")
        
        while self.playing:
            try:
                event = self.lyric_queue.get(timeout=0.1)
                
                if event['type'] == 'sync_lyric':
                    sentence = event['sentence']
                    word_index = event['word_index']
                    time_sec = event['time']
                    
                    # Update display if sentence or word changed
                    if sentence != self.current_sentence or word_index != self.current_word_index:
                        self.current_sentence = sentence
                        self.current_word_index = word_index
                        
                        # Clear previous line and display new one
                        words = sentence.split()
                        display = []
                        for i, word in enumerate(words):
                            if i == word_index:
                                display.append(f"\033[1;33m[{word}]\033[0m")  # Yellow bold
                            else:
                                display.append(word)
                        
                        # Clear line and print
                        print(f"\r{time_sec:6.2f}s: {' '.join(display)}", end='', flush=True)
                        print()  # New line after each word change
                
                elif event['type'] == 'control':
                    time_sec = event['time']
                    device = event['device']
                    action = event['action']
                    params = event['parameters']
                    
                    param_str = ", ".join(f"{k}={v}" for k, v in params.items())
                    print(f"\033[0;36m{time_sec:6.2f}s: 🎛️  {device}.{action}({param_str})\033[0m")
            
            except:
                continue
    
    def play(self):
        """Start real-time playback with synchronized lyrics."""
        self.playing = True
        
        # Start audio generation thread
        audio_thread = threading.Thread(target=self.generate_audio, daemon=True)
        audio_thread.start()
        
        # Start lyric display thread
        lyric_thread = threading.Thread(target=self.display_lyrics, daemon=True)
        lyric_thread.start()
        
        # Start audio stream
        try:
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=2048
            ):
                # Wait for audio generation to complete
                audio_thread.join()
                
                # Wait a bit for audio buffer to drain
                time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\nPlayback interrupted by user")
        
        finally:
            self.playing = False
            lyric_thread.join(timeout=1)
            print("\n\n" + "="*60)
            print("Playback complete!")
            print("="*60)


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
    
    # Lyrics for the song
    line1 = "Twinkle twinkle little star"
    line2 = "How I wonder what you are"
    
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
    
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=0))
    channel.add_event(event)
    
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="on",
        parameters={"intensity": 0.8, "color": "white"}
    ))
    channel.add_event(event)
    
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
    
    event = sl.Event(ptime=beat * 2)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=2))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 2)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="pulse",
        parameters={"duration": 0.5}
    ))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 3)
    event.add_event(sl.Event.AmSyncLyric(sentence=line1, word_index=3))
    channel.add_event(event)
    
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
    
    event = sl.Event(ptime=beat * 4)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=0))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 4)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="set_color",
        parameters={"color": "blue", "transition": 0.5}
    ))
    channel.add_event(event)
    
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
    
    event = sl.Event(ptime=beat * 6)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=2))
    channel.add_event(event)
    
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
    
    event = sl.Event(ptime=beat * 8)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=4))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 8)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="set_intensity",
        parameters={"intensity": 1.0, "transition": 0.3}
    ))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 9)
    event.add_event(sl.Event.AmSyncLyric(sentence=line2, word_index=5))
    channel.add_event(event)
    
    event = sl.Event(ptime=beat * 9)
    event.add_event(sl.Event.AmControl(
        device="bell",
        action="ring",
        parameters={"volume": 1.0}
    ))
    channel.add_event(event)
    
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
    """Run real-time playback with synchronized lyrics."""
    
    print("Creating song with real-time synchronized lyrics...")
    seq, total_samples = create_song()
    
    print("Starting real-time playback...")
    print("Press Ctrl+C to stop\n")
    
    # Create and start player
    player = RealtimeLyricPlayer(seq, total_samples)
    player.play()


if __name__ == "__main__":
    main()
