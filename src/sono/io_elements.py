# io_elements.py
# Audio I/O elements: WAV file playback and device input
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Dict, Any, List
import wave
import struct


class WAVFileElement:
    """WAV file playback element with event control.
    
    Reads and plays back WAV files sample-by-sample. Supports:
    - Start/stop control via set_on/set_off
    - Looping playback
    - Automatic resampling (if needed)
    - Mono conversion (if stereo)
    
    Designed for use with sequencer events:
    - Event opens file and starts playback
    - Event can specify duration or play until end
    - Multiple instances can play different files simultaneously
    
    Example:
        wav = WAVFileElement(filepath="sound.wav", loop=False)
        wav.set_on()  # Start playback
        samples = [wav.sample() for _ in range(44100)]
        wav.set_off()  # Stop playback
    
    Attributes:
        filepath (str): Path to WAV file.
        loop (bool): Whether to loop playback.
        sample_rate (int): Target sample rate (resamples if needed).
        name (str): Unique identifier.
    """
    
    def __init__(
        self,
        filepath: str,
        loop: bool = False,
        sample_rate: int = 44100,
        name: str | None = None,
        scale: float = 1.0,
    ):
        """Initialize a WAVFileElement.
        
        Args:
            filepath: Path to WAV file to play.
            loop: Whether to loop playback (default: False).
            sample_rate: Target sample rate (default: 44100).
            name: Unique identifier. Auto-generated if None.
            scale: Amplitude scaling factor (default: 1.0).
        
        Raises:
            FileNotFoundError: If WAV file doesn't exist.
            ValueError: If WAV file is invalid or unsupported.
        """
        self._TYPE = "WAVFileElement"
        self._filepath = filepath
        self._loop = loop
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale
        self._on = False
        
        # WAV file state
        self._wav_file = None
        self._wav_params = None
        self._samples = []
        self._position = 0
        self._file_sample_rate = sample_rate
        self._resample_ratio = 1.0
        
        # Load WAV file metadata (but don't read samples yet)
        self._load_wav_metadata()
    
    def _load_wav_metadata(self) -> None:
        """Load WAV file metadata without reading all samples."""
        try:
            with wave.open(self._filepath, 'rb') as wav:
                self._wav_params = wav.getparams()
                self._file_sample_rate = wav.getframerate()
                self._resample_ratio = self._file_sample_rate / self._sample_rate
                
                # Validate format
                if self._wav_params.sampwidth not in (1, 2, 3, 4):
                    raise ValueError(f"Unsupported sample width: {self._wav_params.sampwidth}")
                if self._wav_params.nchannels > 2:
                    raise ValueError(f"Unsupported channel count: {self._wav_params.nchannels}")
        except FileNotFoundError:
            raise FileNotFoundError(f"WAV file not found: {self._filepath}")
        except Exception as e:
            raise ValueError(f"Invalid WAV file: {e}")
    
    def _load_samples(self) -> None:
        """Load all samples from WAV file into memory."""
        if self._samples:
            return  # Already loaded
        
        with wave.open(self._filepath, 'rb') as wav:
            n_frames = wav.getnframes()
            raw_data = wav.readframes(n_frames)
            
            # Parse samples based on bit depth
            if self._wav_params.sampwidth == 1:
                # 8-bit unsigned
                samples = struct.unpack(f'{n_frames * self._wav_params.nchannels}B', raw_data)
                samples = [(s - 128) / 128.0 for s in samples]
            elif self._wav_params.sampwidth == 2:
                # 16-bit signed
                samples = struct.unpack(f'{n_frames * self._wav_params.nchannels}h', raw_data)
                samples = [s / 32768.0 for s in samples]
            elif self._wav_params.sampwidth == 3:
                # 24-bit signed (convert to 32-bit)
                samples = []
                for i in range(0, len(raw_data), 3):
                    # Little-endian 24-bit to 32-bit
                    val = int.from_bytes(raw_data[i:i+3], byteorder='little', signed=True)
                    samples.append(val / 8388608.0)  # 2^23
            elif self._wav_params.sampwidth == 4:
                # 32-bit signed
                samples = struct.unpack(f'{n_frames * self._wav_params.nchannels}i', raw_data)
                samples = [s / 2147483648.0 for s in samples]
            
            # Convert stereo to mono if needed
            if self._wav_params.nchannels == 2:
                mono_samples = []
                for i in range(0, len(samples), 2):
                    mono_samples.append((samples[i] + samples[i+1]) / 2.0)
                self._samples = mono_samples
            else:
                self._samples = samples
    
    def set_on(self) -> None:
        """Start playback from beginning."""
        self._load_samples()
        self._position = 0
        self._on = True
    
    def set_off(self) -> None:
        """Stop playback."""
        self._on = False
    
    def sample(self) -> float:
        """Generate next sample from WAV file.
        
        Returns:
            float: Audio sample, or 0.0 if stopped or at end (non-looping).
        """
        if not self._on or not self._samples:
            return 0.0
        
        if self._position >= len(self._samples):
            if self._loop:
                self._position = 0
            else:
                self._on = False
                return 0.0
        
        # Simple nearest-neighbor resampling
        # For production, use linear interpolation or better
        file_position = int(self._position * self._resample_ratio)
        if file_position >= len(self._samples):
            if self._loop:
                file_position = 0
                self._position = 0
            else:
                self._on = False
                return 0.0
        
        sample_value = self._samples[file_position] * self._scale
        self._position += 1
        
        return sample_value
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def reset(self) -> None:
        """Reset playback to beginning."""
        self._position = 0
    
    def get_position(self) -> int:
        """Get current playback position in samples."""
        return self._position
    
    def get_duration(self) -> int:
        """Get total duration in samples (at target sample rate)."""
        if not self._samples:
            self._load_samples()
        return int(len(self._samples) / self._resample_ratio)
    
    def is_finished(self) -> bool:
        """Check if playback has finished (non-looping only)."""
        return not self._loop and self._position >= len(self._samples)
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
    def get_filepath(self) -> str:
        """Get the WAV file path."""
        return self._filepath
    
    def get_loop(self) -> bool:
        """Get loop setting."""
        return self._loop
    
    def set_loop(self, loop: bool) -> None:
        """Set loop setting."""
        self._loop = loop
    
    def get_sample_rate(self) -> int:
        """Get the target sample rate."""
        return self._sample_rate
    
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the target sample rate."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._resample_ratio = self._file_sample_rate / self._sample_rate
    
    def get_scale(self) -> float:
        """Get the amplitude scaling factor."""
        return self._scale
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor."""
        self._scale = scale
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "reset":
                        self.reset()
                    elif cmd == "get_position":
                        return_val[self._name]["get_position"] = self.get_position()
                    elif cmd == "get_duration":
                        return_val[self._name]["get_duration"] = self.get_duration()
                    elif cmd == "is_finished":
                        return_val[self._name]["is_finished"] = self.is_finished()
                    elif cmd == "get_filepath":
                        return_val[self._name]["get_filepath"] = self.get_filepath()
                    elif cmd == "get_loop":
                        return_val[self._name]["get_loop"] = self.get_loop()
                    elif cmd == "set_loop":
                        self.set_loop(val[0])
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the WAV element's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_filepath": self.get_filepath(),
            "get_loop": self.get_loop(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
        }


class DeviceInputElement:
    """Live audio input from device (microphone, line-in, etc.).
    
    Placeholder for live audio input functionality. In a production system,
    this would interface with PyAudio, sounddevice, or similar library to
    capture real-time audio from input devices.
    
    Current implementation returns silence (0.0) but provides the interface
    for future integration with audio input libraries.
    
    Example:
        mic = DeviceInputElement(device_id=0, sample_rate=44100)
        mic.set_on()  # Start capturing
        samples = [mic.sample() for _ in range(44100)]
        mic.set_off()  # Stop capturing
    
    Attributes:
        device_id (int): Audio device ID (platform-specific).
        sample_rate (int): Sampling rate in Hz.
        channels (int): Number of input channels (1=mono, 2=stereo).
        name (str): Unique identifier.
    
    Note:
        To enable actual audio input, integrate with:
        - PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
        - sounddevice: https://python-sounddevice.readthedocs.io/
        - python-rtmidi: For MIDI input
    """
    
    def __init__(
        self,
        device_id: int = 0,
        sample_rate: int = 44100,
        channels: int = 1,
        name: str | None = None,
        scale: float = 1.0,
    ):
        """Initialize a DeviceInputElement.
        
        Args:
            device_id: Audio device ID (default: 0 for default device).
            sample_rate: Sampling rate in Hz (default: 44100).
            channels: Number of input channels, 1=mono, 2=stereo (default: 1).
            name: Unique identifier. Auto-generated if None.
            scale: Amplitude scaling factor (default: 1.0).
        
        Raises:
            ValueError: If parameters are invalid.
        """
        self._TYPE = "DeviceInputElement"
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if channels not in (1, 2):
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        
        self._device_id = device_id
        self._sample_rate = sample_rate
        self._channels = channels
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale
        self._on = False
        
        # Placeholder for audio input stream
        # In production, initialize PyAudio/sounddevice stream here
        self._stream = None
        self._buffer = []
    
    def set_on(self) -> None:
        """Start audio capture.
        
        In production, this would open the audio input stream.
        """
        self._on = True
        # TODO: Open audio input stream
        # Example with sounddevice:
        # import sounddevice as sd
        # self._stream = sd.InputStream(
        #     device=self._device_id,
        #     channels=self._channels,
        #     samplerate=self._sample_rate,
        #     callback=self._audio_callback
        # )
        # self._stream.start()
    
    def set_off(self) -> None:
        """Stop audio capture.
        
        In production, this would close the audio input stream.
        """
        self._on = False
        # TODO: Close audio input stream
        # if self._stream:
        #     self._stream.stop()
        #     self._stream.close()
        #     self._stream = None
    
    def sample(self) -> float:
        """Get next sample from audio input.
        
        Returns:
            float: Audio sample from input device, or 0.0 if not implemented.
        
        Note:
            Current implementation returns 0.0 (silence).
            In production, this would return samples from the input buffer.
        """
        if not self._on:
            return 0.0
        
        # TODO: Return sample from input buffer
        # if self._buffer:
        #     return self._buffer.pop(0) * self._scale
        # else:
        #     return 0.0
        
        # Placeholder: return silence
        return 0.0
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def get_device_id(self) -> int:
        """Get the audio device ID."""
        return self._device_id
    
    def get_channels(self) -> int:
        """Get the number of input channels."""
        return self._channels
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
    def get_sample_rate(self) -> int:
        """Get the sample rate."""
        return self._sample_rate
    
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate.
        
        Note: Changing sample rate while stream is active requires restart.
        """
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        was_on = self._on
        if was_on:
            self.set_off()
        self._sample_rate = sample_rate
        if was_on:
            self.set_on()
    
    def get_scale(self) -> float:
        """Get the amplitude scaling factor."""
        return self._scale
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor."""
        self._scale = scale
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_device_id":
                        return_val[self._name]["get_device_id"] = self.get_device_id()
                    elif cmd == "get_channels":
                        return_val[self._name]["get_channels"] = self.get_channels()
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the device input element's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_device_id": self.get_device_id(),
            "get_channels": self.get_channels(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
        }
