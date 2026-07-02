# modulation.py
# Modulation sources: LFO, ADSR envelope
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Dict, Any, List, TYPE_CHECKING
from math import pi, sin, exp

if TYPE_CHECKING:
    from .protocol import AudioElement


class LFO:
    """Low Frequency Oscillator for modulation.
    
    Generates slow oscillations (typically 0.1-20 Hz) for vibrato,
    tremolo, filter sweeps, and other time-varying modulation.
    
    Can be used hierarchically to modulate frequency of other oscillators:
    
    Example (vibrato):
        carrier = SoundElement(frequency=440)
        lfo = LFO(rate=5.0, depth=10.0)  # 5 Hz vibrato, ±10 Hz
        vibrato = FrequencyModulation(carrier, lfo)
    
    Attributes:
        rate (float): Oscillation rate in Hz.
        depth (float): Modulation depth (amplitude).
        waveform (str): Waveform type ('sine', 'triangle', 'square', 'sawtooth').
        sample_rate (int): Sampling rate in Hz.
        name (str): Unique identifier.
    """
    
    def __init__(
        self,
        rate: float = 5.0,
        depth: float = 1.0,
        waveform: str = "sine",
        sample_rate: int = 44100,
        name: str | None = None,
        phase: float = 0.0,
    ):
        """Initialize an LFO.
        
        Args:
            rate: Oscillation rate in Hz (default: 5.0).
            depth: Modulation depth/amplitude (default: 1.0).
            waveform: Waveform type - 'sine', 'triangle', 'square', 'sawtooth' (default: 'sine').
            sample_rate: Sampling rate in Hz (default: 44100).
            name: Unique identifier. Auto-generated if None.
            phase: Initial phase in radians (default: 0.0).
        
        Raises:
            ValueError: If rate or sample_rate is not positive, or waveform is invalid.
        """
        self._TYPE = "LFO"
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if waveform not in ("sine", "triangle", "square", "sawtooth"):
            raise ValueError("Waveform must be 'sine', 'triangle', 'square', or 'sawtooth'")
        
        self._rate = rate
        self._depth = depth
        self._waveform = waveform
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._phase = phase
        self._init_phase = phase
        self._phase_increment = (rate / sample_rate) * 2 * pi
        self._on = False
    
    def set_on(self) -> None:
        """Activate the LFO."""
        self._phase = self._init_phase
        self._on = True
    
    def set_off(self) -> None:
        """Deactivate the LFO."""
        self._on = False
    
    def sample(self) -> float:
        """Generate the next LFO sample.
        
        Returns:
            float: Modulation value in range [-depth, +depth], or 0.0 if off.
        """
        if not self._on:
            return 0.0
        
        normalized_phase = (self._phase % (2 * pi)) / (2 * pi)
        
        if self._waveform == "sine":
            value = sin(self._phase)
        elif self._waveform == "triangle":
            # Triangle: -1 to 1 over one cycle
            value = 4 * abs(normalized_phase - 0.5) - 1
        elif self._waveform == "square":
            value = 1.0 if normalized_phase < 0.5 else -1.0
        elif self._waveform == "sawtooth":
            value = 2 * normalized_phase - 1
        else:
            value = 0.0
        
        self._phase += self._phase_increment
        return self._depth * value
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def get_modulation_value(self) -> float:
        """Get current modulation value (alias for sample)."""
        return self.sample()
    
    def set_rate(self, rate: float) -> None:
        """Set the oscillation rate."""
        if rate <= 0:
            raise ValueError("Rate must be positive")
        self._rate = rate
        self._phase_increment = (rate / self._sample_rate) * 2 * pi
    
    def get_rate(self) -> float:
        """Get the oscillation rate."""
        return self._rate
    
    def set_depth(self, depth: float) -> None:
        """Set the modulation depth."""
        self._depth = depth
    
    def get_depth(self) -> float:
        """Get the modulation depth."""
        return self._depth
    
    def set_waveform(self, waveform: str) -> None:
        """Set the waveform type."""
        if waveform not in ("sine", "triangle", "square", "sawtooth"):
            raise ValueError("Waveform must be 'sine', 'triangle', 'square', or 'sawtooth'")
        self._waveform = waveform
    
    def get_waveform(self) -> str:
        """Get the waveform type."""
        return self._waveform
    
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
        """Set the sample rate."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._phase_increment = (self._rate / self._sample_rate) * 2 * pi
    
    def get_scale(self) -> float:
        """Get the depth (for protocol compatibility)."""
        return self._depth
    
    def set_scale(self, scale: float) -> None:
        """Set the depth (for protocol compatibility)."""
        self._depth = scale
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_rate":
                        self.set_rate(val[0])
                    elif cmd == "get_rate":
                        return_val[self._name]["get_rate"] = self.get_rate()
                    elif cmd == "set_depth":
                        self.set_depth(val[0])
                    elif cmd == "get_depth":
                        return_val[self._name]["get_depth"] = self.get_depth()
                    elif cmd == "set_waveform":
                        self.set_waveform(val[0])
                    elif cmd == "get_waveform":
                        return_val[self._name]["get_waveform"] = self.get_waveform()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the LFO's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_rate": self.get_rate(),
            "get_depth": self.get_depth(),
            "get_waveform": self.get_waveform(),
            "get_sample_rate": self.get_sample_rate(),
        }


class FrequencyModulation:
    """Frequency modulation combinator.
    
    Modulates the frequency of a carrier oscillator using a modulator
    (typically an LFO for vibrato, or another oscillator for FM synthesis).
    
    This is a hierarchical implementation where the modulator's output
    is added to the carrier's base frequency each sample.
    
    Example (vibrato):
        carrier = SoundElement(frequency=440)
        lfo = LFO(rate=5.0, depth=10.0)  # 5 Hz, ±10 Hz
        vibrato = FrequencyModulation(carrier, lfo)
        vibrato.set_on()
        sample = vibrato.sample()  # Carrier freq varies 430-450 Hz
    
    Attributes:
        carrier: The oscillator being modulated.
        modulator: The modulation source (LFO or oscillator).
        base_frequency: Original carrier frequency.
    """
    
    def __init__(
        self,
        carrier: AudioElement,
        modulator: AudioElement,
        name: str | None = None,
    ):
        """Initialize a FrequencyModulation combinator.
        
        Args:
            carrier: The oscillator to modulate.
            modulator: The modulation source (LFO or oscillator).
            name: Unique identifier. Auto-generated if None.
        
        Raises:
            ValueError: If carrier doesn't have set_frequency method.
        """
        self._TYPE = "FrequencyModulation"
        # carrier may be None during factory reconstruction; it is wired up later.
        if carrier is not None and (
            not hasattr(carrier, 'set_frequency') or not hasattr(carrier, 'get_frequency')
        ):
            raise ValueError("Carrier must have set_frequency and get_frequency methods")

        self._carrier = carrier
        self._modulator = modulator
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._base_frequency = carrier.get_frequency() if carrier is not None else 0.0
        self._scale = 1.0
    
    def set_on(self) -> None:
        """Activate both carrier and modulator."""
        self._carrier.set_on()
        self._modulator.set_on()
    
    def set_off(self) -> None:
        """Deactivate both carrier and modulator."""
        self._carrier.set_off()
        self._modulator.set_off()
    
    def sample(self) -> float:
        """Generate next sample with frequency modulation.
        
        Returns:
            float: Carrier output with modulated frequency.
        """
        # Get modulation value
        mod_value = self._modulator.sample()
        
        # Modulate carrier frequency
        new_freq = self._base_frequency + mod_value
        self._carrier.set_frequency(max(0.1, new_freq))  # Prevent negative freq
        
        # Get carrier output
        return self._carrier.sample() * self._scale
    
    def sample_pluck(self) -> float:
        """Generate sample with pluck triggering."""
        mod_value = self._modulator.sample_pluck()
        new_freq = self._base_frequency + mod_value
        self._carrier.set_frequency(max(0.1, new_freq))
        return self._carrier.sample_pluck() * self._scale
    
    def set_base_frequency(self, frequency: float) -> None:
        """Set the base (unmodulated) frequency."""
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self._base_frequency = frequency
        self._carrier.set_frequency(frequency)
    
    def get_base_frequency(self) -> float:
        """Get the base frequency."""
        return self._base_frequency
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
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
                    if cmd == "set_base_frequency":
                        self.set_base_frequency(val[0])
                    elif cmd == "get_base_frequency":
                        return_val[self._name]["get_base_frequency"] = self.get_base_frequency()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        
        # Propagate to sub-elements
        if self._carrier:
            carrier_val = self._carrier.msg(msg)
            if carrier_val:
                return_val[self._name]["carrier"] = carrier_val
        if self._modulator:
            mod_val = self._modulator.msg(msg)
            if mod_val:
                return_val[self._name]["modulator"] = mod_val
        
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the FM combinator's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_base_frequency": self.get_base_frequency(),
            "get_scale": self.get_scale(),
            "carrier": self._carrier.dump() if self._carrier else None,
            "modulator": self._modulator.dump() if self._modulator else None,
        }


class ADSR:
    """Attack-Decay-Sustain-Release envelope.
    
    Standard synthesizer envelope with four phases:
    - Attack: 0 → 1 (time to reach peak)
    - Decay: 1 → sustain_level (time to reach sustain)
    - Sustain: holds at sustain_level while gate is on
    - Release: sustain_level → 0 (time after gate off)
    
    Can be used to modulate amplitude, filter cutoff, or any parameter.
    
    Example (amplitude envelope):
        osc = SoundElement(frequency=440)
        env = ADSR(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
        enveloped = EnvelopedElement(osc, env)
        enveloped.set_on()  # Triggers attack
        # ... generate samples ...
        enveloped.set_off()  # Triggers release
    
    Attributes:
        attack (float): Attack time in seconds.
        decay (float): Decay time in seconds.
        sustain (float): Sustain level (0.0 to 1.0).
        release (float): Release time in seconds.
        sample_rate (int): Sampling rate in Hz.
    """
    
    def __init__(
        self,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.3,
        sample_rate: int = 44100,
        name: str | None = None,
    ):
        """Initialize an ADSR envelope.
        
        Args:
            attack: Attack time in seconds (default: 0.01).
            decay: Decay time in seconds (default: 0.1).
            sustain: Sustain level 0.0-1.0 (default: 0.7).
            release: Release time in seconds (default: 0.3).
            sample_rate: Sampling rate in Hz (default: 44100).
            name: Unique identifier. Auto-generated if None.
        
        Raises:
            ValueError: If times are negative, sustain out of range, or sample_rate invalid.
        """
        self._TYPE = "ADSR"
        if attack < 0 or decay < 0 or release < 0:
            raise ValueError("Attack, decay, and release times must be non-negative")
        if not 0.0 <= sustain <= 1.0:
            raise ValueError("Sustain level must be between 0.0 and 1.0")
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        self._attack = attack
        self._decay = decay
        self._sustain = sustain
        self._release = release
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        
        self._attack_samples = max(1, int(attack * sample_rate))
        self._decay_samples = max(1, int(decay * sample_rate))
        self._release_samples = max(1, int(release * sample_rate))
        
        self._state = "idle"  # idle, attack, decay, sustain, release
        self._sample_count = 0
        self._current_level = 0.0
        self._release_start_level = 0.0
    
    def trigger(self) -> None:
        """Start envelope (note on)."""
        self._state = "attack"
        self._sample_count = 0
        self._current_level = 0.0
    
    def set_on(self) -> None:
        """Activate envelope (alias for trigger)."""
        self.trigger()
    
    def release_envelope(self) -> None:
        """Begin release phase (note off)."""
        if self._state != "idle":
            self._state = "release"
            self._sample_count = 0
            self._release_start_level = self._current_level
    
    def set_off(self) -> None:
        """Deactivate envelope (alias for release)."""
        self.release_envelope()
    
    def sample(self) -> float:
        """Generate next envelope value.
        
        Returns:
            float: Envelope value in range [0.0, 1.0].
        """
        if self._state == "idle":
            return 0.0
        
        elif self._state == "attack":
            # Linear ramp 0 → 1
            if self._attack_samples > 0:
                self._current_level = min(1.0, self._sample_count / self._attack_samples)
            else:
                self._current_level = 1.0
            
            if self._sample_count >= self._attack_samples:
                self._state = "decay"
                self._sample_count = 0
        
        elif self._state == "decay":
            # Exponential decay 1 → sustain_level
            if self._decay_samples > 0:
                progress = self._sample_count / self._decay_samples
                # Exponential curve
                self._current_level = self._sustain + (1.0 - self._sustain) * exp(-5 * progress)
            else:
                self._current_level = self._sustain
            
            if self._sample_count >= self._decay_samples:
                self._state = "sustain"
                self._current_level = self._sustain
        
        elif self._state == "sustain":
            # Hold at sustain level
            self._current_level = self._sustain
        
        elif self._state == "release":
            # Exponential decay to 0
            if self._release_samples > 0:
                progress = self._sample_count / self._release_samples
                self._current_level = self._release_start_level * exp(-5 * progress)
            else:
                self._current_level = 0.0
            
            if self._sample_count >= self._release_samples or self._current_level < 0.001:
                self._state = "idle"
                self._current_level = 0.0
        
        self._sample_count += 1
        return self._current_level
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def get_modulation_value(self) -> float:
        """Get current envelope value (alias for sample)."""
        return self.sample()
    
    def get_state(self) -> str:
        """Get current envelope state."""
        return self._state
    
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
        """Set the sample rate and recalculate sample counts."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._attack_samples = max(1, int(self._attack * sample_rate))
        self._decay_samples = max(1, int(self._decay * sample_rate))
        self._release_samples = max(1, int(self._release * sample_rate))
    
    def get_scale(self) -> float:
        """Get scale (always 1.0 for envelopes)."""
        return 1.0
    
    def set_scale(self, scale: float) -> None:
        """Set scale (no-op for envelopes)."""
        pass
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "trigger":
                        self.trigger()
                    elif cmd == "release":
                        self.release_envelope()
                    elif cmd == "get_state":
                        return_val[self._name]["get_state"] = self.get_state()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the ADSR's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "attack": self._attack,
            "decay": self._decay,
            "sustain": self._sustain,
            "release": self._release,
            "get_sample_rate": self.get_sample_rate(),
        }


class EnvelopedElement:
    """Apply an envelope to any audio element.
    
    Multiplies the audio signal by the envelope value each sample,
    creating amplitude modulation controlled by the envelope.
    
    Example:
        osc = SoundElement(frequency=440)
        env = ADSR(attack=0.01, decay=0.1, sustain=0.7, release=0.3)
        enveloped = EnvelopedElement(osc, env)
        enveloped.set_on()  # Triggers both oscillator and envelope
        samples = [enveloped.sample() for _ in range(44100)]
        enveloped.set_off()  # Triggers release phase
    
    Attributes:
        source: The audio element to envelope.
        envelope: The envelope (ADSR or other modulation source).
    """
    
    def __init__(
        self,
        source: AudioElement,
        envelope: ADSR,
        name: str | None = None,
    ):
        """Initialize an EnvelopedElement.
        
        Args:
            source: The audio element to envelope.
            envelope: The envelope to apply.
            name: Unique identifier. Auto-generated if None.
        """
        self._TYPE = "EnvelopedElement"
        self._source = source
        self._envelope = envelope
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = 1.0
    
    def set_on(self) -> None:
        """Activate source and trigger envelope."""
        self._source.set_on()
        self._envelope.trigger()
    
    def set_off(self) -> None:
        """Trigger envelope release (source stays on during release)."""
        self._envelope.release_envelope()
    
    def sample(self) -> float:
        """Generate next sample with envelope applied.
        
        Returns:
            float: Source output multiplied by envelope value.
        """
        source_sample = self._source.sample()
        envelope_value = self._envelope.sample()
        return source_sample * envelope_value * self._scale
    
    def sample_pluck(self) -> float:
        """Generate sample with pluck triggering."""
        source_sample = self._source.sample_pluck()
        envelope_value = self._envelope.sample()
        return source_sample * envelope_value * self._scale
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
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
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        
        # Propagate to sub-elements
        if self._source:
            source_val = self._source.msg(msg)
            if source_val:
                return_val[self._name]["source"] = source_val
        if self._envelope:
            env_val = self._envelope.msg(msg)
            if env_val:
                return_val[self._name]["envelope"] = env_val
        
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the enveloped element's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_scale": self.get_scale(),
            "source": self._source.dump() if self._source else None,
            "envelope": self._envelope.dump() if self._envelope else None,
        }
