# filters.py
# Digital filters for audio processing
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Dict, Any, List, TYPE_CHECKING
from math import pi, sin, cos, sqrt

if TYPE_CHECKING:
    from .protocol import AudioElement


class BiquadFilter:
    """Biquad (2nd-order IIR) filter for audio processing.
    
    Industry-standard digital filter supporting multiple types:
    - lowpass: Attenuates frequencies above cutoff
    - highpass: Attenuates frequencies below cutoff
    - bandpass: Passes frequencies near cutoff, attenuates others
    - notch: Attenuates frequencies near cutoff
    - peak: Boosts/cuts frequencies near cutoff
    - lowshelf: Boosts/cuts frequencies below cutoff
    - highshelf: Boosts/cuts frequencies above cutoff
    
    Uses Direct Form I implementation with coefficient caching.
    
    Example:
        osc = SoundElement(frequency=440)
        lpf = BiquadFilter(source=osc, filter_type="lowpass", cutoff=1000, q=0.707)
        lpf.set_on()
        samples = [lpf.sample() for _ in range(44100)]
    
    Attributes:
        source: The audio element to filter.
        filter_type: Type of filter (see above).
        cutoff: Cutoff frequency in Hz.
        q: Quality factor (resonance, typically 0.5-10).
        gain: Gain in dB for peak/shelf filters.
        sample_rate: Sampling rate in Hz.
    """
    
    def __init__(
        self,
        source: AudioElement,
        filter_type: str = "lowpass",
        cutoff: float = 1000.0,
        q: float = 0.707,
        gain: float = 0.0,
        sample_rate: int = 44100,
        name: str | None = None,
    ):
        """Initialize a BiquadFilter.
        
        Args:
            source: The audio element to filter.
            filter_type: Filter type - 'lowpass', 'highpass', 'bandpass', 'notch',
                        'peak', 'lowshelf', 'highshelf' (default: 'lowpass').
            cutoff: Cutoff frequency in Hz (default: 1000.0).
            q: Quality factor/resonance (default: 0.707 for Butterworth).
            gain: Gain in dB for peak/shelf filters (default: 0.0).
            sample_rate: Sampling rate in Hz (default: 44100).
            name: Unique identifier. Auto-generated if None.
        
        Raises:
            ValueError: If parameters are out of valid ranges.
        """
        self._TYPE = "BiquadFilter"
        valid_types = ("lowpass", "highpass", "bandpass", "notch", "peak", "lowshelf", "highshelf")
        if filter_type not in valid_types:
            raise ValueError(f"Filter type must be one of {valid_types}")
        if cutoff <= 0:
            raise ValueError("Cutoff frequency must be positive")
        if q <= 0:
            raise ValueError("Q must be positive")
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        self._source = source
        self._filter_type = filter_type
        self._cutoff = cutoff
        self._q = q
        self._gain = gain
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = 1.0
        
        # Filter state (Direct Form I)
        self._x1 = 0.0  # x[n-1]
        self._x2 = 0.0  # x[n-2]
        self._y1 = 0.0  # y[n-1]
        self._y2 = 0.0  # y[n-2]
        
        # Biquad coefficients
        self._b0 = 1.0
        self._b1 = 0.0
        self._b2 = 0.0
        self._a1 = 0.0
        self._a2 = 0.0
        
        self._calculate_coefficients()
    
    def _calculate_coefficients(self) -> None:
        """Calculate biquad coefficients based on filter parameters."""
        w0 = 2 * pi * self._cutoff / self._sample_rate
        cos_w0 = cos(w0)
        sin_w0 = sin(w0)
        alpha = sin_w0 / (2 * self._q)
        A = 10 ** (self._gain / 40)  # Convert dB to linear
        
        if self._filter_type == "lowpass":
            b0 = (1 - cos_w0) / 2
            b1 = 1 - cos_w0
            b2 = (1 - cos_w0) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        
        elif self._filter_type == "highpass":
            b0 = (1 + cos_w0) / 2
            b1 = -(1 + cos_w0)
            b2 = (1 + cos_w0) / 2
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        
        elif self._filter_type == "bandpass":
            b0 = alpha
            b1 = 0
            b2 = -alpha
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        
        elif self._filter_type == "notch":
            b0 = 1
            b1 = -2 * cos_w0
            b2 = 1
            a0 = 1 + alpha
            a1 = -2 * cos_w0
            a2 = 1 - alpha
        
        elif self._filter_type == "peak":
            b0 = 1 + alpha * A
            b1 = -2 * cos_w0
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_w0
            a2 = 1 - alpha / A
        
        elif self._filter_type == "lowshelf":
            sqrt_A = sqrt(A)
            b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * sqrt_A * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
            b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * sqrt_A * alpha)
            a0 = (A + 1) + (A - 1) * cos_w0 + 2 * sqrt_A * alpha
            a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
            a2 = (A + 1) + (A - 1) * cos_w0 - 2 * sqrt_A * alpha
        
        elif self._filter_type == "highshelf":
            sqrt_A = sqrt(A)
            b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * sqrt_A * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
            b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * sqrt_A * alpha)
            a0 = (A + 1) - (A - 1) * cos_w0 + 2 * sqrt_A * alpha
            a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
            a2 = (A + 1) - (A - 1) * cos_w0 - 2 * sqrt_A * alpha
        
        else:
            # Default to passthrough
            b0, b1, b2 = 1.0, 0.0, 0.0
            a0, a1, a2 = 1.0, 0.0, 0.0
        
        # Normalize by a0
        self._b0 = b0 / a0
        self._b1 = b1 / a0
        self._b2 = b2 / a0
        self._a1 = a1 / a0
        self._a2 = a2 / a0
    
    def set_on(self) -> None:
        """Activate the filter and source."""
        self._source.set_on()
        # Reset filter state
        self._x1 = 0.0
        self._x2 = 0.0
        self._y1 = 0.0
        self._y2 = 0.0
    
    def set_off(self) -> None:
        """Deactivate the filter and source."""
        self._source.set_off()
    
    def sample(self) -> float:
        """Generate next filtered sample.
        
        Returns:
            float: Filtered audio sample.
        """
        # Get input sample
        x0 = self._source.sample()
        
        # Direct Form I biquad
        y0 = (self._b0 * x0 + self._b1 * self._x1 + self._b2 * self._x2
              - self._a1 * self._y1 - self._a2 * self._y2)
        
        # Update state
        self._x2 = self._x1
        self._x1 = x0
        self._y2 = self._y1
        self._y1 = y0
        
        return y0 * self._scale
    
    def sample_pluck(self) -> float:
        """Generate filtered sample with pluck triggering."""
        x0 = self._source.sample_pluck()
        y0 = (self._b0 * x0 + self._b1 * self._x1 + self._b2 * self._x2
              - self._a1 * self._y1 - self._a2 * self._y2)
        self._x2 = self._x1
        self._x1 = x0
        self._y2 = self._y1
        self._y1 = y0
        return y0 * self._scale
    
    def set_cutoff(self, cutoff: float) -> None:
        """Set cutoff frequency and recalculate coefficients."""
        if cutoff <= 0:
            raise ValueError("Cutoff frequency must be positive")
        self._cutoff = cutoff
        self._calculate_coefficients()
    
    def get_cutoff(self) -> float:
        """Get cutoff frequency."""
        return self._cutoff
    
    def set_q(self, q: float) -> None:
        """Set Q factor and recalculate coefficients."""
        if q <= 0:
            raise ValueError("Q must be positive")
        self._q = q
        self._calculate_coefficients()
    
    def get_q(self) -> float:
        """Get Q factor."""
        return self._q
    
    def set_gain(self, gain: float) -> None:
        """Set gain (for peak/shelf filters) and recalculate coefficients."""
        self._gain = gain
        self._calculate_coefficients()
    
    def get_gain(self) -> float:
        """Get gain."""
        return self._gain
    
    def set_filter_type(self, filter_type: str) -> None:
        """Set filter type and recalculate coefficients."""
        valid_types = ("lowpass", "highpass", "bandpass", "notch", "peak", "lowshelf", "highshelf")
        if filter_type not in valid_types:
            raise ValueError(f"Filter type must be one of {valid_types}")
        self._filter_type = filter_type
        self._calculate_coefficients()
    
    def get_filter_type(self) -> str:
        """Get filter type."""
        return self._filter_type
    
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
        """Set sample rate and recalculate coefficients."""
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._calculate_coefficients()
    
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
                    if cmd == "set_cutoff":
                        self.set_cutoff(val[0])
                    elif cmd == "get_cutoff":
                        return_val[self._name]["get_cutoff"] = self.get_cutoff()
                    elif cmd == "set_q":
                        self.set_q(val[0])
                    elif cmd == "get_q":
                        return_val[self._name]["get_q"] = self.get_q()
                    elif cmd == "set_gain":
                        self.set_gain(val[0])
                    elif cmd == "get_gain":
                        return_val[self._name]["get_gain"] = self.get_gain()
                    elif cmd == "set_filter_type":
                        self.set_filter_type(val[0])
                    elif cmd == "get_filter_type":
                        return_val[self._name]["get_filter_type"] = self.get_filter_type()
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
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        
        # Propagate to source
        if self._source:
            source_val = self._source.msg(msg)
            if source_val:
                return_val[self._name]["source"] = source_val
        
        return return_val
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the filter's state."""
        return {
            "get_name": self.get_name(),
            "get_type": self.get_type(),
            "get_filter_type": self.get_filter_type(),
            "get_cutoff": self.get_cutoff(),
            "get_q": self.get_q(),
            "get_gain": self.get_gain(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
            "source": self._source.dump() if self._source else None,
        }
