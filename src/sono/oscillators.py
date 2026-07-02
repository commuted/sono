# oscillators.py
# Additional oscillator types for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Dict, Any, List
from math import pi, sin
import random


class SawtoothElement:
    """Sawtooth wave oscillator - rich in harmonics.
    
    Produces a sawtooth waveform with all harmonics present,
    making it ideal for brass, strings, and aggressive sounds.
    
    Attributes:
        frequency (float): The frequency of the wave in Hz.
        sample_rate (int): The sampling rate in Hz.
        name (str): Unique identifier for the element.
        phase (float): Current phase in radians.
        scale (float): Amplitude scaling factor.
    """
    
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 44100,
        name: str | None = None,
        phase: float = 0.0,
        scale: float = 1.0,
    ):
        """Initialize a SawtoothElement.
        
        Args:
            frequency: The frequency of the wave in Hz (default: 440.0).
            sample_rate: The sampling rate in Hz (default: 44100).
            name: Unique identifier for the element. Auto-generated if None.
            phase: Initial phase in radians (default: 0.0).
            scale: Amplitude scaling factor (default: 1.0).
        
        Raises:
            ValueError: If frequency or sample_rate is not positive.
        """
        self._TYPE = "SawtoothElement"
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        self._frequency = frequency
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._phase = phase
        self._init_phase = phase
        self._scale = scale
        self._on = False
        self._settled_off = True
        self._last_sample = 0.0
        self._sample = 0.0
        self._phase_increment = (frequency / sample_rate) * 2 * pi
    
    def set_on(self) -> None:
        """Activate the oscillator."""
        self.set_phase(self._init_phase)
        self._on = True
        self._settled_off = False
    
    def set_off(self) -> None:
        """Deactivate the oscillator."""
        self._on = False
    
    def sample(self) -> float:
        """Generate the next sawtooth wave sample.
        
        Returns:
            float: The sample value in range [-1, 1], or 0.0 if off and settled.
        """
        self._last_sample = self._sample
        if not self._on:
            if self._settled_off:
                return 0.0
            # Sawtooth: 2 * (phase / (2π)) - 1
            normalized_phase = (self._phase % (2 * pi)) / (2 * pi)
            self._sample = self._scale * (2 * normalized_phase - 1)
            self._phase += self._phase_increment
            # Check for zero crossing
            if abs(self._sample) < 1e-10 or (self._last_sample * self._sample) < 0:
                self._settled_off = True
                return 0.0
            return self._sample
        
        normalized_phase = (self._phase % (2 * pi)) / (2 * pi)
        self._sample = self._scale * (2 * normalized_phase - 1)
        self._phase += self._phase_increment
        return self._sample
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def set_phase(self, phase: float) -> None:
        """Set the phase of the wave."""
        self._phase = phase
    
    def set_init_phase(self, phase: float) -> None:
        """Set the initial phase (used by set_on)."""
        self._init_phase = phase
        self._phase = phase
    
    def get_phase(self) -> float:
        """Get the current phase."""
        return self._phase
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_frequency(self) -> float:
        """Get the current frequency."""
        return self._frequency
    
    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the wave."""
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self._frequency = frequency
        self._phase_increment = (frequency / self._sample_rate) * 2 * pi
    
    def get_sample_rate(self) -> int:
        """Get the current sample rate."""
        return self._sample_rate
    
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._phase_increment = (self._frequency / self._sample_rate) * 2 * pi
    
    def get_scale(self) -> float:
        """Get the amplitude scaling factor."""
        return self._scale
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor."""
        self._scale = scale
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_phase":
                        self.set_phase(val[0])
                    elif cmd == "set_init_phase":
                        self.set_init_phase(val[0])
                    elif cmd == "get_phase":
                        return_val[self._name]["get_phase"] = self.get_phase()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_frequency":
                        self.set_frequency(val[0])
                    elif cmd == "get_frequency":
                        return_val[self._name]["get_frequency"] = self.get_frequency()
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
        """Serialize the oscillator's state."""
        return {
            "get_name": self.get_name(),
            "get_frequency": self.get_frequency(),
            "get_phase": self.get_phase(),
            "get_type": self.get_type(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
        }


class SquareElement:
    """Square wave oscillator - odd harmonics only.
    
    Produces a square waveform with only odd harmonics,
    creating a hollow, clarinet-like sound. Supports pulse
    width modulation (PWM) via duty_cycle parameter.
    
    Attributes:
        frequency (float): The frequency of the wave in Hz.
        sample_rate (int): The sampling rate in Hz.
        duty_cycle (float): Pulse width (0.0 to 1.0, default 0.5 for square).
        name (str): Unique identifier for the element.
        phase (float): Current phase in radians.
        scale (float): Amplitude scaling factor.
    """
    
    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 44100,
        duty_cycle: float = 0.5,
        name: str | None = None,
        phase: float = 0.0,
        scale: float = 1.0,
    ):
        """Initialize a SquareElement.
        
        Args:
            frequency: The frequency of the wave in Hz (default: 440.0).
            sample_rate: The sampling rate in Hz (default: 44100).
            duty_cycle: Pulse width ratio 0.0-1.0 (default: 0.5 for square wave).
            name: Unique identifier for the element. Auto-generated if None.
            phase: Initial phase in radians (default: 0.0).
            scale: Amplitude scaling factor (default: 1.0).
        
        Raises:
            ValueError: If frequency or sample_rate is not positive, or duty_cycle out of range.
        """
        self._TYPE = "SquareElement"
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if not 0.0 < duty_cycle < 1.0:
            raise ValueError("Duty cycle must be between 0.0 and 1.0")
        
        self._frequency = frequency
        self._sample_rate = sample_rate
        self._duty_cycle = duty_cycle
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._phase = phase
        self._init_phase = phase
        self._scale = scale
        self._on = False
        self._settled_off = True
        self._last_sample = 0.0
        self._sample = 0.0
        self._phase_increment = (frequency / sample_rate) * 2 * pi
    
    def set_on(self) -> None:
        """Activate the oscillator."""
        self.set_phase(self._init_phase)
        self._on = True
        self._settled_off = False
    
    def set_off(self) -> None:
        """Deactivate the oscillator."""
        self._on = False
    
    def sample(self) -> float:
        """Generate the next square wave sample.
        
        Returns:
            float: The sample value (+1 or -1 scaled), or 0.0 if off and settled.
        """
        self._last_sample = self._sample
        if not self._on:
            if self._settled_off:
                return 0.0
            normalized_phase = (self._phase % (2 * pi)) / (2 * pi)
            self._sample = self._scale * (1.0 if normalized_phase < self._duty_cycle else -1.0)
            self._phase += self._phase_increment
            # Check for zero crossing
            if abs(self._sample) < 1e-10 or (self._last_sample * self._sample) < 0:
                self._settled_off = True
                return 0.0
            return self._sample
        
        normalized_phase = (self._phase % (2 * pi)) / (2 * pi)
        self._sample = self._scale * (1.0 if normalized_phase < self._duty_cycle else -1.0)
        self._phase += self._phase_increment
        return self._sample
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def set_duty_cycle(self, duty_cycle: float) -> None:
        """Set the pulse width (PWM).
        
        Args:
            duty_cycle: Pulse width ratio 0.0-1.0.
        
        Raises:
            ValueError: If duty_cycle is out of range.
        """
        if not 0.0 < duty_cycle < 1.0:
            raise ValueError("Duty cycle must be between 0.0 and 1.0")
        self._duty_cycle = duty_cycle
    
    def get_duty_cycle(self) -> float:
        """Get the current pulse width."""
        return self._duty_cycle
    
    def set_phase(self, phase: float) -> None:
        """Set the phase of the wave."""
        self._phase = phase
    
    def set_init_phase(self, phase: float) -> None:
        """Set the initial phase (used by set_on)."""
        self._init_phase = phase
        self._phase = phase
    
    def get_phase(self) -> float:
        """Get the current phase."""
        return self._phase
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_frequency(self) -> float:
        """Get the current frequency."""
        return self._frequency
    
    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the wave."""
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self._frequency = frequency
        self._phase_increment = (frequency / self._sample_rate) * 2 * pi
    
    def get_sample_rate(self) -> int:
        """Get the current sample rate."""
        return self._sample_rate
    
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._phase_increment = (self._frequency / self._sample_rate) * 2 * pi
    
    def get_scale(self) -> float:
        """Get the amplitude scaling factor."""
        return self._scale
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor."""
        self._scale = scale
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_phase":
                        self.set_phase(val[0])
                    elif cmd == "set_init_phase":
                        self.set_init_phase(val[0])
                    elif cmd == "get_phase":
                        return_val[self._name]["get_phase"] = self.get_phase()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_frequency":
                        self.set_frequency(val[0])
                    elif cmd == "get_frequency":
                        return_val[self._name]["get_frequency"] = self.get_frequency()
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "set_duty_cycle":
                        self.set_duty_cycle(val[0])
                    elif cmd == "get_duty_cycle":
                        return_val[self._name]["get_duty_cycle"] = self.get_duty_cycle()
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the oscillator's state."""
        return {
            "get_name": self.get_name(),
            "get_frequency": self.get_frequency(),
            "get_phase": self.get_phase(),
            "get_type": self.get_type(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
            "get_duty_cycle": self.get_duty_cycle(),
        }


class WhiteNoiseElement:
    """White noise generator - equal energy at all frequencies.
    
    Produces random samples with uniform distribution, useful for
    percussion sounds, wind effects, and as a modulation source.
    
    Attributes:
        sample_rate (int): The sampling rate in Hz.
        name (str): Unique identifier for the element.
        scale (float): Amplitude scaling factor.
        seed (int): Random seed for reproducibility (None for random).
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        name: str | None = None,
        scale: float = 1.0,
        seed: int | None = None,
    ):
        """Initialize a WhiteNoiseElement.
        
        Args:
            sample_rate: The sampling rate in Hz (default: 44100).
            name: Unique identifier for the element. Auto-generated if None.
            scale: Amplitude scaling factor (default: 1.0).
            seed: Random seed for reproducibility (None for random).
        
        Raises:
            ValueError: If sample_rate is not positive.
        """
        self._TYPE = "WhiteNoiseElement"
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale
        self._seed = seed
        self._on = False
        self._rng = random.Random(seed)
    
    def set_on(self) -> None:
        """Activate the noise generator."""
        self._on = True
        if self._seed is not None:
            self._rng = random.Random(self._seed)
    
    def set_off(self) -> None:
        """Deactivate the noise generator."""
        self._on = False
    
    def sample(self) -> float:
        """Generate the next white noise sample.
        
        Returns:
            float: Random sample in range [-scale, +scale], or 0.0 if off.
        """
        if not self._on:
            return 0.0
        return self._scale * (self._rng.random() * 2 - 1)
    
    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation."""
        return self.sample()
    
    def get_name(self) -> str:
        """Get the unique identifier."""
        return self._name
    
    def get_sample_rate(self) -> int:
        """Get the current sample rate."""
        return self._sample_rate
    
    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
    
    def get_scale(self) -> float:
        """Get the amplitude scaling factor."""
        return self._scale
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor."""
        self._scale = scale
    
    def get_type(self) -> str:
        """Get the type identifier."""
        return self._TYPE
    
    def get_seed(self) -> int | None:
        """Get the random seed."""
        return self._seed
    
    def set_seed(self, seed: int | None) -> None:
        """Set the random seed and reset RNG."""
        self._seed = seed
        self._rng = random.Random(seed)
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages."""
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "sample":
                        return_val[self._name]["sample"] = self.sample()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_sample_rate":
                        return_val[self._name]["get_sample_rate"] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "get_seed":
                        return_val[self._name]["get_seed"] = self.get_seed()
                    elif cmd == "set_seed":
                        self.set_seed(val[0])
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the noise generator's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
            "get_seed": self.get_seed(),
        }
