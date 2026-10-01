#!/usr/bin/env python3
"""
Example: Real-time "Twinkle Twinkle Little Star" with Correct Melody

Plays the actual melody of "Twinkle Twinkle Little Star" with word-synchronized
lyrics in real-time using sounddevice.

Melody pattern:
C C G G | A A G - | F F E E | D D C -
Twinkle twinkle little star, how I wonder what you are

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
        
        try:
            data = self.audio_queue.get_nowait()
            if len(data) < frames:
                outdata[:len(data)] = data.reshape(-1, 1)
                outdata[len(data):] = 0
            else:
                outdata[:] = data[:frames].reshape(-1, 1)
        except:
            outdata[:] = 0
    
    def generate_audio(self):
        """Generate audio samples and lyrics in a separate thread."""
        buffer_size = 2048
        buffer = []
        
        while self.sequencer.get_time() < self.total_samples and self.playing:
            results = self.sequencer.sample()
            
            for result in results:
                buffer.append(result["sample"])
                
                if result["sync_lyrics"]:
                    for sync_lyric in result["sync_lyrics"]:
                        self.lyric_queue.put({
                            'type': 'sync_lyric',
                            'sentence': sync_lyric["sentence"],
                            'word_index': sync_lyric["word_index"],
                            'time': self.sequencer.get_time() / self.sample_rate
                        })
                
                if result["controls"]:
                    for control in result["controls"]:
                        self.lyric_queue.put({
                            'type': 'control',
                            'device': control["device"],
                            'action': control["action"],
                            'parameters': control["parameters"],
                            'time': self.sequencer.get_time() / self.sample_rate
                        })
                
                if len(buffer) >= buffer_size:
                    audio_data = np.array(buffer, dtype=np.float32)
                    self.audio_queue.put(audio_data)
                    buffer = []
        
        if buffer:
            audio_data = np.array(buffer, dtype=np.float32)
            self.audio_queue.put(audio_data)
    
    def display_lyrics(self):
        """Display lyrics in real-time in a separate thread."""
        print("\n" + "="*60)
        print("🎵  TWINKLE TWINKLE LITTLE STAR  🎵")
        print("="*60 + "\n")
        
        while self.playing:
            try:
                event = self.lyric_queue.get(timeout=0.1)
                
                if event['type'] == 'sync_lyric':
                    sentence = event['sentence']
                    word_index = event['word_index']
                    time_sec = event['time']
                    
                    if sentence != self.current_sentence or word_index != self.current_word_index:
                        self.current_sentence = sentence
                        self.current_word_index = word_index
                        
                        words = sentence.split()
                        display = []
                        for i, word in enumerate(words):
                            if i == word_index:
                                display.append(f"\033[1;33m[{word}]\033[0m")
                            else:
                                display.append(word)
                        
                        print(f"\r{time_sec:6.2f}s: {' '.join(display)}", end='', flush=True)
                        print()
                
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
        
        audio_thread = threading.Thread(target=self.generate_audio, daemon=True)
        audio_thread.start()
        
        lyric_thread = threading.Thread(target=self.display_lyrics, daemon=True)
        lyric_thread.start()
        
        try:
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=2048
            ):
                audio_thread.join()
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
    """Create Twinkle Twinkle Little Star with correct melody."""
    
    sample_rate = 44100
    
    # Create instrument with individual notes
    piano = sl.Instrument(name="piano")
    
    # Create notes for the melody (octave 4)
    notes = {}
    for note_name in ["C", "D", "E", "F", "G", "A"]:
        chord = sl.Chord().make_a_chord((4, note_name, "major"), pluck=True)
        sl.Util.fix_pop(chord)
        piano.add_note(chord, note_name)
        notes[note_name] = chord
    
    # Create channel
    channel = sl.Channel(name="main")
    
    # Timing: quarter note = 0.5 seconds (120 BPM)
    quarter = sample_rate // 2  # 0.5 seconds
    half = quarter * 2          # 1.0 seconds
    
    # Lyrics
    line1 = "Twinkle twinkle little star"
    line2 = "How I wonder what you are"
    
    # Melody: C C G G | A A G - | F F E E | D D C -
    melody = [
        ("C", 0, quarter, line1, 0),      # Twinkle
        ("C", quarter, quarter, line1, 1), # twinkle
        ("G", quarter*2, quarter, line1, 2), # little
        ("G", quarter*3, quarter, line1, 3), # star
        
        ("A", quarter*4, quarter, line2, 0), # How
        ("A", quarter*5, quarter, line2, 1), # I
        ("G", quarter*6, half, line2, 2),    # wonder
        
        ("F", quarter*8, quarter, line2, 3), # what
        ("F", quarter*9, quarter, line2, 4), # you
        ("E", quarter*10, quarter, line2, 5), # are
        ("E", quarter*11, quarter, line2, 5), # (hold "are")
        
        ("D", quarter*12, quarter, line2, 5), # (ending)
        ("D", quarter*13, quarter, line2, 5),
        ("C", quarter*14, half, line2, 5),
    ]
    
    # Add events for each note
    for note_name, ptime, duration, sentence, word_idx in melody:
        # Add chord event
        event = sl.Event(ptime=ptime)
        event.add_event(sl.Event.AmChord(
            instrument="piano",
            chord=piano.get_note(note_name),
            action="add_pluck",
            duration=duration
        ))
        channel.add_event(event)
        
        # Add synchronized lyric (only on note changes, not holds)
        if ptime == 0 or melody[melody.index((note_name, ptime, duration, sentence, word_idx)) - 1][4] != word_idx:
            event = sl.Event(ptime=ptime)
            event.add_event(sl.Event.AmSyncLyric(
                sentence=sentence,
                word_index=word_idx
            ))
            channel.add_event(event)
    
    # Add device controls at key moments
    # Light on at start
    event = sl.Event(ptime=0)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="on",
        parameters={"intensity": 0.7, "color": "warm_white"}
    ))
    channel.add_event(event)
    
    # Pulse on "star"
    event = sl.Event(ptime=quarter*3)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="pulse",
        parameters={"duration": 0.3}
    ))
    channel.add_event(event)
    
    # Bell on "wonder"
    event = sl.Event(ptime=quarter*6)
    event.add_event(sl.Event.AmControl(
        device="bell",
        action="ring",
        parameters={"volume": 0.5}
    ))
    channel.add_event(event)
    
    # Brighten on final "are"
    event = sl.Event(ptime=quarter*10)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="set_intensity",
        parameters={"intensity": 1.0, "transition": 0.5}
    ))
    channel.add_event(event)
    
    # Fade out at end
    event = sl.Event(ptime=quarter*16)
    event.add_event(sl.Event.AmControl(
        device="stage_light",
        action="fade_out",
        parameters={"duration": 1.5}
    ))
    channel.add_event(event)
    
    # Create sequencer
    seq = sl.Sequencer(sample_rate=sample_rate)
    seq.add_channel("main", channel, instruments=[piano])
    
    return seq, quarter * 18  # Total duration


def main():
    """Run real-time playback with synchronized lyrics."""
    
    print("Creating 'Twinkle Twinkle Little Star' with correct melody...")
    seq, total_samples = create_song()
    
    print("Starting real-time playback...")
    print("Press Ctrl+C to stop\n")
    
    player = RealtimeLyricPlayer(seq, total_samples)
    player.play()


if __name__ == "__main__":
    main()
