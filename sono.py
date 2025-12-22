# current.py (second half with docstrings)
# Audio synthesis library for generating and manipulating sound elements.
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations
from typing import Union, Any, Dict, List, Tuple, TYPE_CHECKING
from math import sin, asin, pi, e, log2
from enum import Enum
import numpy as np

if TYPE_CHECKING:
    SoundElementType = Union[
        "SoundElement",
        "SumElements",
        "MultiplyElements",
        "MixElements",
        "Pluck",
        "FixedAttenuate",
    ]

# Class registry for type checking
SOUND_ELEMENT_CLASSES = (
    "SoundElement",
    "SumElements",
    "MultiplyElements",
    "MixElements",
    "Pluck",
    "FixedAttenuate",
)


class SoundElement:
    """A class to generate sine or triangle wave audio samples.

    Attributes:
        frequency (float): The frequency of the wave in Hz (default: 440.0).
        sample_rate (int): The sampling rate in Hz (default: 44100).
        name (str): Unique identifier for the element (auto-generated if None).
        phase (float): Initial phase in radians (default: 0.0).
        scale (float): Amplitude scaling factor (default: 1.0).
    """

    def __init__(
        self,
        frequency: float = 440.0,
        sample_rate: int = 44100,
        name: str | None = None,
        phase: float = 0.0,
        scale: float = 1.0,
    ):
        """Initialize a SoundElement with specified parameters.

        Args:
            frequency (float): The frequency of the wave in Hz (default: 440.0).
            sample_rate (int): The sampling rate in Hz (default: 44100).
            name (str, optional): Unique identifier for the element. Auto-generated if None.
            *
+ phase (float): Initial phase in radians (default: 0.0).
            scale (float): Amplitude scaling factor (default: 1.0).

        Raises:
            ValueError: If frequency or sample_rate is not positive.
        """
        self._TYPE = "SoundElement"
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
        self._fade_val: float = 1.0
        self._fade: bool = False
        self._on: bool = False
        self._settled_off: bool = True
        self._last_sample: float = 0.0
        self._sample: float = 0.0
        self._phase_increment = (frequency / sample_rate) * 2 * pi

    def set_on(self) -> None:
        """Activate the sound element, resetting phase and state."""
        self.set_phase(self._init_phase)
        self._on = True
        self._settled_off = False

    def set_off(self) -> None:
        """Deactivate the sound element."""
        self._on = False

    def sample(self) -> float:
        """Generate the next sine wave sample.

        Returns:
            float: The sample value in the range [-1, 1], or 0.0 if off and settled.
        """
        self._last_sample = self._sample
        if not self._on:
            if self._settled_off:
                return 0.0
            self._sample = self._scale * sin(self._phase)
            self._phase += self._phase_increment
            # Use epsilon comparison for float zero-crossing detection
            if abs(self._sample) < 1e-10 or (self._last_sample * self._sample) < 0:
                self._settled_off = True
                return 0.0
            return self._sample
        self._sample = self._scale * sin(self._phase)
        self._phase += self._phase_increment
        return self._sample

    def triangle(self) -> float:
        """Generate the next triangle wave sample.

        Returns:
            float: The triangle wave sample in the range [-1, 1], or 0.0 if off and settled.
        """
        self._last_sample = self._sample
        if not self._on:
            if self._settled_off:
                return 0.0
            self._sample = self._scale * (2 / pi) * asin(sin(self._phase))
            self._phase += self._phase_increment
            # Use epsilon comparison for float zero-crossing detection
            if abs(self._sample) < 1e-10 or (self._last_sample * self._sample) < 0:
                self._settled_off = True
                return 0.0
            return self._sample
        self._sample = self._scale * (2 / pi) * asin(sin(self._phase))
        self._phase += self._phase_increment
        return self._sample

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element, keyed by name.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_phase":
                        self.set_phase(val[0])
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
                    elif cmd == "midi_note":
                        self.midi_note(val[0], val[1])
                    elif cmd == "midi_key_from_freq":
                        return_val[self._name]["midi_key_from_freq"] = (
                            self.midi_key_from_freq(val[0], val[1])
                        )
                    elif cmd == "set_frequency_to_midi_note":
                        self.set_frequency_to_midi_note(val[0])
                    elif cmd == "set_frequency_to_nearest_midi_note":
                        self.set_frequency_to_nearest_midi_note(val[0])
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "set_frequency":
                        self.set_frequency(val[0])
                    elif cmd == "get_frequency":
                        return_val[self._name]["get_frequency"] = self.get_frequency()
                    elif cmd == "get_sample_rate":
                        return_val[self._name][
                            "get_sample_rate"
                        ] = self.get_sample_rate()
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "set_scale":
                        self.set_scale(val[0])
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the sound element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties.
        """
        return {
            "get_name": self.get_name(),
            "get_frequency": self.get_frequency(),
            "get_phase": self.get_phase(),
            "get_type": self.get_type(),
            "get_sample_rate": self.get_sample_rate(),
            "get_scale": self.get_scale(),
        }

    @staticmethod
    def midi_note(key_no: int, div: int = 12) -> float:
        """Calculate the frequency for a MIDI note number.

        Args:
            key_no (int): MIDI note number.
            div (int): Number of divisions per octave (default: 12 for equal temperament).

        Returns:
            float: The frequency in Hz.
        """
        return 440.0 * 2 ** ((key_no - 69) / div)

    @staticmethod
    def midi_key_from_freq(frequency: float, div: int = 12) -> float:
        """Calculate the MIDI note number from a frequency.

        Args:
            frequency (float): The frequency in Hz.
            div (int): Number of divisions per octave (default: 12).

        Returns:
            float: The MIDI note number (fractional).

        Raises:
            ValueError: If frequency is not positive.
        """
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        return div * log2(frequency / 440.0) + 69

    def set_frequency_to_midi_note(self, midi_key_no: int) -> float:
        """Set the frequency to match a MIDI note number.

        Args:
            midi_key_no (int): The MIDI note number.

        Returns:
            float: The set frequency.
        """
        self._frequency = self.midi_note(midi_key_no)
        self._phase_increment = (self._frequency / self._sample_rate) * 2 * pi
        return self._frequency

    def set_frequency_to_nearest_midi_note(self, frequency: float) -> float:
        """Set the frequency to the nearest MIDI note frequency.

        Args:
            frequency (float): The target frequency in Hz.

        Returns:
            float: The quantized frequency.

        Raises:
            ValueError: If frequency is not positive.
        """
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self._frequency = self.midi_note(round(self.midi_key_from_freq(frequency)))
        self._phase_increment = (self._frequency / self._sample_rate) * 2 * pi
        return self._frequency

    def set_phase(self, phase: float) -> None:
        """Set the phase of the wave.

        Args:
            phase (float): The phase in radians.
        """
        self._phase = phase

    def get_phase(self) -> float:
        """Get the current phase of the wave.

        Returns:
            float: The phase in radians.
        """
        return self._phase

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def get_frequency(self) -> float:
        """Get the current frequency.

        Returns:
            float: The frequency in Hz.
        """
        return self._frequency

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the wave.

        Args:
            frequency (float): The frequency in Hz.

        Raises:
            ValueError: If frequency is not positive.
        """
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        self._frequency = frequency
        self._phase_increment = (frequency / self._sample_rate) * 2 * pi

    def get_sample_rate(self) -> int:
        """Get the current sample rate.

        Returns:
            int: The sample rate in Hz.
        """
        return self._sample_rate

    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate.

        Args:
            sample_rate (int): The sample rate in Hz.

        Raises:
            ValueError: If sample_rate is not positive.
        """
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._phase_increment = (self._frequency / self._sample_rate) * 2 * pi

    def get_scale(self) -> float:
        """Get the amplitude scaling factor.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("SoundElement").
        """
        return self._TYPE


class MultiplyElements:
    """A class to multiply two sound elements (Z = A * B).

    Attributes:
        a (SoundElementType): First input sound element.
        b (SoundElementType): Second input sound element.
        name (str): Unique identifier for the element.
        scale (float): Scaling factor for the product (default: 1.0).
    """

    def __init__(
        self,
        a: SoundElementType = None,
        b: SoundElementType = None,
        name: str | None = None,
        scale: float = 1.0,
    ):
        """Initialize a MultiplyElements instance.

        Args:
            a (SoundElementType, optional): First input sound element.
            b (SoundElementType, optional): Second input sound element.
            name (str, optional): Unique identifier for the element.
            scale (float): Scaling factor for the product (default: 1.0).

        Raises:
            ValueError: If a or b does not have a sample() method.
        """
        self._TYPE = "MultiplyElements"
        self._a = None
        self._b = None
        if a:
            self.set_a(a)
        if b:
            self.set_b(b)
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale

    def set_a(self, a: object) -> None:
        """Set the first input sound element.

        Args:
            a (object): The sound element to set.

        Raises:
            ValueError: If a does not have a sample() method.
        """
        if isinstance(
            a,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._a = a
        else:
            raise ValueError(
                "object assignment to MultiplyElements has no attribute sample()"
            )

    def set_b(self, b: object) -> None:
        """Set the second input sound element.

        Args:
            b (object): The sound element to set.

        Raises:
            ValueError: If b does not have a sample() method.
        """
        if isinstance(
            b,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._b = b
        else:
            raise ValueError(
                "object assignment to MultiplyElements has no attribute sample()"
            )

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("MultiplyElements").
        """
        return self._TYPE

    def set_scale(self, scale: float) -> None:
        """Set the scaling factor for the product.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def get_scale(self) -> float:
        """Get the scaling factor for the product.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def get_instances(self) -> Tuple[str | None, str | None]:
        """Get the names of the input sound elements.

        Returns:
            Tuple[str | None, str | None]: Names of the first and second elements, or None if not set.
        """
        return (
            self._a.get_name() if self._a else None,
            self._b.get_name() if self._b else None,
        )

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-elements.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_scale":
                        self.set_scale(val[0])
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
                if self._a:
                    a_val = self._a.msg(msg)
                    if a_val:
                        return_val[self._name]["a"] = a_val
                if self._b:
                    b_val = self._b.msg(msg)
                    if b_val:
                        return_val[self._name]["b"] = b_val
        return return_val

    def set_on(self) -> None:
        """Activate the input sound elements."""
        if self._a:
            self._a.set_on()
        if self._b:
            self._b.set_on()

    def set_off(self) -> None:
        """Deactivate the input sound elements."""
        if self._a:
            self._a.set_off()
        if self._b:
            self._b.set_off()

    def sample(self) -> float:
        """Generate the next sample by multiplying input samples.

        Returns:
            float: The product of input samples, scaled.
        """
        a_sample = self._a.sample() if self._a else 0.0
        b_sample = self._b.sample() if self._b else 0.0
        return a_sample * b_sample * self._scale

    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties and sub-elements.
        """
        return {
            "get_scale": self.get_scale(),
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
            "b": self._b.dump() if self._b else None,
        }


class MixElements:
    """A class to mix two sound elements (Z = A + B - A*B).

    Attributes:
        a (SoundElementType): First input sound element.
        b (SoundElementType): Second input sound element.
        name (str): Unique identifier for the element.
        scale (float): Scaling factor for the mix (default: 1.0).
    """

    def __init__(
        self,
        a: SoundElementType = None,
        b: SoundElementType = None,
        name: str | None = None,
        scale: float = 1.0,
    ):
        """Initialize a MixElements instance.

        Args:
            a (SoundElementType, optional): First input sound element.
            b (SoundElementType, optional): Second input sound element.
            name (str, optional): Unique identifier for the element.
            scale (float): Scaling factor for the mix (default: 1.0).

        Raises:
            ValueError: If a or b does not have a sample() method.
        """
        self._TYPE = "MixElements"
        self._a = None
        self._b = None
        if a:
            self.set_a(a)
        if b:
            self.set_b(b)
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale

    def set_a(self, a: object) -> None:
        """Set the first input sound element.

        Args:
            a (object): The sound element to set.

        Raises:
            ValueError: If a does not have a sample() method.
        """
        if isinstance(
            a,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._a = a
        else:
            raise ValueError(
                "object assignment to MixElements has no attribute sample()"
            )

    def set_b(self, b: object) -> None:
        """Set the second input sound element.

        Args:
            b (object): The sound element to set.

        Raises:
            ValueError: If b does not have a sample() method.
        """
        if isinstance(
            b,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._b = b
        else:
            raise ValueError(
                "object assignment to MixElements has no attribute sample()"
            )

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("MixElements").
        """
        return self._TYPE

    def set_scale(self, scale: float) -> None:
        """Set the scaling factor for the mix.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def get_scale(self) -> float:
        """Get the scaling factor for the mix.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def get_instances(self) -> Tuple[str | None, str | None]:
        """Get the names of the input sound elements.

        Returns:
            Tuple[str | None, str | None]: Names of the first and second elements, or None if not set.
        """
        return (
            self._a.get_name() if self._a else None,
            self._b.get_name() if self._b else None,
        )

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-elements.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
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
                if self._a:
                    a_val = self._a.msg(msg)
                    if a_val:
                        return_val[self._name]["a"] = a_val
                if self._b:
                    b_val = self._b.msg(msg)
                    if b_val:
                        return_val[self._name]["b"] = b_val
        return return_val

    def sample(self) -> float:
        """Generate the next sample by mixing input samples (Z = A + B - A*B).

        Returns:
            float: The mixed sample, scaled.
        """
        sea = self._a.sample() if self._a else 0.0
        seb = self._b.sample() if self._b else 0.0
        return ((sea + seb) - (sea * seb)) * self._scale

    def set_on(self) -> None:
        """Activate the input sound elements."""
        if self._a:
            self._a.set_on()
        if self._b:
            self._b.set_on()

    def set_off(self) -> None:
        """Deactivate the input sound elements."""
        if self._a:
            self._a.set_off()
        if self._b:
            self._b.set_off()

    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties and sub-elements.
        """
        return {
            "get_scale": self.get_scale(),
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
            "b": self._b.dump() if self._b else None,
        }


class SumElements:
    """A class to sum two sound elements (Z = A + B).

    Attributes:
        a (SoundElementType): First input sound element.
        b (SoundElementType): Second input sound element.
        name (str): Unique identifier for the element.
        scale (float): Scaling factor for the sum (default: 0.5 to avoid clipping).
    """

    def __init__(
        self,
        a: SoundElementType = None,
        b: SoundElementType = None,
        name: str | None = None,
        scale: float = 0.5,
    ):
        """Initialize a SumElements instance.

        Args:
            a (SoundElementType, optional): First input sound element.
            b (SoundElementType, optional): Second input sound element.
            name (str, optional): Unique identifier for the element.
            scale (float): Scaling factor for the sum (default: 0.5).

        Raises:
            ValueError: If a or b does not have a sample() method.
        """
        self._TYPE = "SumElements"
        self._a = None
        self._b = None
        if a:
            self.set_a(a)
        if b:
            self.set_b(b)
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._scale = scale

    def set_a(self, a: object) -> None:
        """Set the first input sound element.

        Args:
            a (object): The sound element to set.

        Raises:
            ValueError: If a does not have a sample() method.
        """
        if isinstance(
            a,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._a = a
        else:
            raise ValueError(
                "object assignment to SumElements has no attribute sample()"
            )

    def set_b(self, b: object) -> None:
        """Set the second input sound element.

        Args:
            b (object): The sound element to set.

        Raises:
            ValueError: If b does not have a sample() method.
        """
        if isinstance(
            b,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._b = b
        else:
            raise ValueError(
                "object assignment to SumElements has no attribute sample()"
            )

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("SumElements").
        """
        return self._TYPE

    def set_scale(self, scale: float) -> None:
        """Set the scaling factor for the sum.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def get_scale(self) -> float:
        """Get the scaling factor for the sum.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def get_instances(self) -> Tuple[str | None, str | None]:
        """Get the names of the input sound elements.

        Returns:
            Tuple[str | None, str | None]: Names of the first and second elements, or None if not set.
        """
        return (
            self._a.get_name() if self._a else None,
            self._b.get_name() if self._b else None,
        )

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-elements.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
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
                if self._a:
                    a_val = self._a.msg(msg)
                    if a_val:
                        return_val[self._name]["a"] = a_val
                if self._b:
                    b_val = self._b.msg(msg)
                    if b_val:
                        return_val[self._name]["b"] = b_val
        return return_val

    def sample(self) -> float:
        """Generate the next sample by summing input samples.

        Returns:
            float: The sum of input samples, scaled.
        """
        sea = self._a.sample() if self._a else 0.0
        seb = self._b.sample() if self._b else 0.0
        return (sea + seb) * self._scale

    def set_on(self) -> None:
        """Activate the input sound elements."""
        if self._a:
            self._a.set_on()
        if self._b:
            self._b.set_on()

    def set_off(self) -> None:
        """Deactivate the input sound elements."""
        if self._a:
            self._a.set_off()
        if self._b:
            self._b.set_off()

    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties and sub-elements.
        """
        return {
            "get_scale": self.get_scale(),
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
            "b": self._b.dump() if self._b else None,
        }


class Pluck:
    """A class to apply a plucked string effect (Z = A * e^(-lambda*t)).

    Attributes:
        a (SoundElementType): Input sound element.
        name (str): Unique identifier for the element.
        sample_rate (int): Sampling rate in Hz (default: 44100).
        stop (float): Duration of the pluck effect in seconds (default: 2.0).
        lambda_dc (float): Decay constant for the pluck effect (default: 0.03).
        scale (float): Amplitude scaling factor (default: 1.0).
    """

    def __init__(
        self,
        a: SoundElementType = None,
        name: str | None = None,
        sample_rate: int = 44100,
        stop: float = 2.0,
        lambda_dc: float = 0.03,
        scale: float = 1.0,
    ):
        """Initialize a Pluck instance.

        Args:
            a (SoundElementType, optional): Input sound element.
            name (str, optional): Unique identifier for the element.
            sample_rate (int): Sampling rate in Hz (default: 44100).
            stop (float): Duration of the pluck effect in seconds (default: 2.0).
            lambda_dc (float): Decay constant for the pluck effect (default: 0.03).
            scale (float): Amplitude scaling factor (default: 1.0).

        Raises:
            ValueError: If sample_rate, stop, or lambda_dc is not positive, or if a does not have a sample() method.
        """
        self._TYPE = "Pluck"
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if stop <= 0:
            raise ValueError("Stop time must be positive")
        if lambda_dc <= 0:
            raise ValueError("Lambda decay constant must be positive")
        self._stop = stop
        self._lambda_dc = lambda_dc
        self._scale = scale
        self._a = None
        if a:
            self.set_a(a)
        self._sample_rate = sample_rate
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._pluck_time: float = 0.0
        self._pluck_inc: float = 1 / self._sample_rate
        self._sample: float = 0.0
        self._on: bool = False

    def set_a(self, a: object) -> None:
        """Set the input sound element.

        Args:
            a (object): The sound element to set.

        Raises:
            ValueError: If a does not have a sample() method.
        """
        if isinstance(
            a,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._a = a
        else:
            raise ValueError("object assignment to Pluck has no attribute sample()")

    def sample_pluck(self) -> float:
        """Generate a sample with a new pluck effect, resetting time.

        Returns:
            float: The initial sample value, scaled.
        """
        self.set_on()
        self._pluck_time = 0.0
        val = self._a.sample() if self._a else 0.0
        return val * self._scale

    def sample(self) -> float:
        """Generate the next sample with the pluck effect applied.

        Returns:
            float: The sample value with exponential decay, or 0.0 if off.
        """
        if not self._on:
            return 0.0
        val = (self._a.sample() if self._a else 0.0) * e ** (
            -self._lambda_dc * self._pluck_time
        )
        self._pluck_time += self._pluck_inc
        if self._pluck_time >= self._stop:
            self.set_off()
        return val * self._scale

    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def get_scale(self) -> float:
        """Get the amplitude scaling factor.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def set_lambda_dc(self, lambda_dc: float) -> None:
        """Set the decay constant for the pluck effect.

        Args:
            lambda_dc (float): The decay constant.

        Raises:
            ValueError: If lambda_dc is not positive.
        """
        if lambda_dc <= 0:
            raise ValueError("Lambda decay constant must be positive")
        self._lambda_dc = lambda_dc

    def get_lambda_dc(self) -> float:
        """Get the decay constant for the pluck effect.

        Returns:
            float: The decay constant.
        """
        return self._lambda_dc

    def set_stop(self, stop: float) -> None:
        """Set the duration of the pluck effect.

        Args:
            stop (float): The duration in seconds.

        Raises:
            ValueError: If stop is not positive.
        """
        if stop <= 0:
            raise ValueError("Stop time must be positive")
        self._stop = stop

    def get_stop(self) -> float:
        """Get the duration of the pluck effect.

        Returns:
            float: The duration in seconds.
        """
        return self._stop

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def set_sample_rate(self, sample_rate: int) -> None:
        """Set the sample rate and update pluck increment.

        Args:
            sample_rate (int): The sample rate in Hz.

        Raises:
            ValueError: If sample_rate is not positive.
        """
        if sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        self._sample_rate = sample_rate
        self._pluck_inc = 1 / self._sample_rate

    def get_sample_rate(self) -> int:
        """Get the current sample rate.

        Returns:
            int: The sample rate in Hz.
        """
        return self._sample_rate

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("Pluck").
        """
        return self._TYPE

    def set_off(self) -> None:
        """Deactivate the pluck effect and input element."""
        self._on = False
        if self._a:
            self._a.set_off()

    def set_on(self) -> None:
        """Activate the pluck effect and input element."""
        self._on = True
        if self._a:
            self._a.set_on()

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-element.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "set_lambda_dc":
                        self.set_lambda_dc(val[0])
                    elif cmd == "set_stop":
                        self.set_stop(val[0])
                    elif cmd == "set_sample_rate":
                        self.set_sample_rate(val[0])
                    elif cmd == "set_on":
                        self.set_on()
                    elif cmd == "set_off":
                        self.set_off()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_sample_rate":
                        return_val[self._name][
                            "get_sample_rate"
                        ] = self.get_sample_rate()
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "get_lambda_dc":
                        return_val[self._name]["get_lambda_dc"] = self.get_lambda_dc()
                    elif cmd == "get_stop":
                        return_val[self._name]["get_stop"] = self.get_stop()
                if self._a:
                    a_val = self._a.msg(msg)
                    if a_val:
                        return_val[self._name]["a"] = a_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties and sub-element.
        """
        return {
            "get_scale": self.get_scale(),
            "get_lambda_dc": self.get_lambda_dc(),
            "get_type": self.get_type(),
            "get_stop": self.get_stop(),
            "get_name": self.get_name(),
            "get_sample_rate": self.get_sample_rate(),
            "a": self._a.dump() if self._a else None,
        }


class FixedAttenuate:
    """A class to apply fixed attenuation to a sound element.

    Attributes:
        a (SoundElementType): Input sound element.
        name (str): Unique identifier for the element.
        scale (float): Attenuation factor (default: 1.0).
    """

    def __init__(
        self, a: SoundElementType = None, name: str | None = None, scale: float = 1.0
    ):
        """Initialize a FixedAttenuate instance.

        Args:
            a (SoundElementType, optional): Input sound element.
            name (str, optional): Unique identifier for the element.
            scale (float): Attenuation factor (default: 1.0).

        Raises:
            ValueError: If a does not have a sample() method.
        """
        self._TYPE = "FixedAttenuate"
        self._scale = scale
        self._a = None
        if a:
            self.set_a(a)
        self._name = name or f"{self._TYPE}_{id(self)}"

    def set_scale(self, scale: float) -> None:
        """Set the attenuation factor.

        Args:
            scale (float): The scale factor.
        """
        self._scale = scale

    def set_off(self) -> None:
        """Deactivate the input sound element."""
        if self._a:
            self._a.set_off()

    def set_on(self) -> None:
        """Activate the input sound element."""
        if self._a:
            self._a.set_on()

    def set_a(self, a: object) -> None:
        """Set the input sound element.

        Args:
            a (object): The sound element to set.

        Raises:
            ValueError: If a does not have a sample() method.
        """
        if isinstance(
            a,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            self._a = a
        else:
            raise ValueError(
                "object assignment to FixedAttenuate has no attribute sample()"
            )

    def get_scale(self) -> float:
        """Get the attenuation factor.

        Returns:
            float: The scale factor.
        """
        return self._scale

    def get_type(self) -> str:
        """Get the type identifier of the element.

        Returns:
            str: The type string ("FixedAttenuate").
        """
        return self._TYPE

    def get_name(self) -> str:
        """Get the unique identifier of the element.

        Returns:
            str: The element's name.
        """
        return self._name

    def sample(self) -> float:
        """Generate the next sample with fixed attenuation.

        Returns:
            float: The attenuated sample.
        """
        return (self._a.sample() if self._a else 0.0) * self._scale

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this element.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "set_scale":
                        self.set_scale(val[0])
                    elif cmd == "get_scale":
                        return_val[self._name]["get_scale"] = self.get_scale()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                if self._a:
                    self._a.msg(msg)
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the element's properties and sub-element.
        """
        return {
            "get_scale": self.get_scale(),
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
        }


class Note:
    """A class to encapsulate a sound element as a musical note.

    Attributes:
        a (SoundElementType): The underlying sound element.
        name (str): Unique identifier for the note.
    """

    def __init__(self, note: SoundElementType | None = None, name: str | None = None):
        """Initialize a Note instance.

        Args:
            note (SoundElementType, optional): The sound element to encapsulate.
            name (str, optional): Unique identifier for the note.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        self._TYPE = "Note"
        self._a: SoundElementType | None = None
        self._assembly: Dict[Any, Any] = {}
        self._collect: Dict[Any, Any] = {}
        self._done: Dict[Any, Any] = {}
        self.set_note(note)
        self._name = name or f"{self._TYPE}_{id(self)}"

    def get_type(self) -> str:
        """Get the type identifier of the note.

        Returns:
            str: The type string ("Note").
        """
        return self._TYPE

    def get_name(self) -> str:
        """Get the unique identifier of the note.

        Returns:
            str: The note's name.
        """
        return self._name

    def set_name(self, name: str) -> None:
        """Set the unique identifier of the note.

        Args:
            name (str): The new name.
        """
        self._name = name

    def get_note(self) -> SoundElementType | None:
        """Get the underlying sound element.

        Returns:
            SoundElementType | None: The sound element, or None if not set.
        """
        return self._a

    def set_note(self, note: SoundElementType | None) -> None:
        """Set the underlying sound element.

        Args:
            note (SoundElementType, optional): The sound element to set.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        if note and not isinstance(
            note,
            (
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
                Note,
            ),
        ):
            raise ValueError("object assignment to Note has no attribute sample()")
        if isinstance(note, Note):
            self._a = note.get_note()
        else:
            self._a = note

    def set_a(self, note: SoundElementType | None) -> None:
        """Set the underlying sound element (alias for set_note).

        Args:
            note (SoundElementType, optional): The sound element to set.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        self.set_note(note)

    def sample(self) -> float:
        """Generate the next sample from the underlying element.

        Returns:
            float: The sample value, or 0.0 if no element is set.
        """
        return self._a.sample() if self._a else 0.0

    def sample_pluck(self) -> float:
        """Generate the next sample from the underlying element.

        Returns:
            float: The sample value, or 0.0 if no element is set.

            Raises: TypeError when no sample_pluck() method in hierarchy

        """
        if isinstance(self.get_note(), Pluck):
            return self._a.sample_pluck() if self._a else 0.0
        else:
            actual_type = self._a.get_type() if self._a else "None"
            raise TypeError(
               f"Note top hierarchy is not type Pluck. Is type {actual_type}"
            )
 
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this note.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including sub-element.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                if self._a:
                    a_val = self._a.msg(msg)
                    if a_val:
                        return_val[self._name]["a"] = a_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the note's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the note's properties and sub-element.
        """
        return {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
        }

    def recursive_walk(self, data: Dict[str, Any]) -> None:
        """Recursively build sound element hierarchy from a data dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing element properties and hierarchy.
        """
        get_type = data["get_type"]
        if get_type == "SoundElement":
            self._done[data["get_name"]] = SoundElement(
                name=data["get_name"],
                frequency=data["get_frequency"],
                sample_rate=data["get_sample_rate"],
                phase=data["get_phase"],
                scale=data["get_scale"],
            )
        elif get_type == "SumElements":
            self._collect[data["get_name"]] = SumElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "Pluck":
            self._collect[data["get_name"]] = Pluck(
                name=data["get_name"],
                sample_rate=data["get_sample_rate"],
                stop=data["get_stop"],
                lambda_dc=data["get_lambda_dc"],
                scale=data["get_scale"],
            )
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])
        elif get_type == "MixElements":
            self._collect[data["get_name"]] = MixElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "MultiplyElements":
            self._collect[data["get_name"]] = MultiplyElements(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {
                "a": data["a"]["get_name"],
                "b": data["b"]["get_name"],
            }
            self.recursive_walk(data["a"])
            self.recursive_walk(data["b"])
        elif get_type == "FixedAttenuate":
            self._collect[data["get_name"]] = FixedAttenuate(
                name=data["get_name"], scale=data["get_scale"]
            )
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])
        elif get_type == "Note":
            self._collect[data["get_name"]] = Note(name=data["get_name"])
            self._assembly[data["get_name"]] = {"a": data["a"]["get_name"]}
            self.recursive_walk(data["a"])

    def note_factory_hier_db(self, data: Dict[str, Any]) -> None:
        """Build a note hierarchy from a serialized data dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing the note hierarchy.

        Raises:
            ValueError: If the factory fails to converge or has cyclic dependencies.
        """
        self.recursive_walk(data)
        time_out = int(len(self._assembly) * (log2(len(self._assembly)) + 1))
        cnt = 0
        while self._collect:
            if cnt == time_out:
                raise ValueError(
                    f"Note factory failed to converge after {cnt} iterations. Check for cyclic dependencies in {self._assembly}"
                )
            cnt += 1
            to_delete = []
            for key, val in self._assembly.items():
                if "a" in val and "b" in val:
                    if val["a"] in self._done and val["b"] in self._done:
                        self._collect[key].set_a(self._done[val["a"]])
                        self._collect[key].set_b(self._done[val["b"]])
                        self._done[key] = self._collect[key]
                        to_delete.append(key)
                        del self._done[val["a"]]
                        del self._done[val["b"]]
                elif "a" in val:
                    if val["a"] in self._done:
                        self._collect[key].set_a(self._done[val["a"]])
                        self._done[key] = self._collect[key]
                        to_delete.append(key)
                        del self._done[val["a"]]
            for key in to_delete:
                del self._collect[key]
        if len(self._done) != 1:
            raise ValueError(
                f"Note factory failed to converge: {len(self._done)} elements remain"
            )
        for k, v in self._done.items():
            self.set_name(k)
            self.set_note(v)

    class MixType(Enum):
        """Enum for mixing types in chord creation."""

        SUM = "SumElements"
        MIX = "MixElements"

    def make_a_chord(
        self,
        chord: Tuple[int, str, str],
        mix: MixType = MixType.SUM,
        pluck: bool = True,
    ) -> Note:
        """Create a note from a chord specification.

        Args:
            chord (Tuple[int, str, str]): A tuple of (octave, note, chord_type).
            mix (MixType): The mixing method for combining notes (default: MixType.SUM).
            pluck (bool): If True, apply a Pluck effect to the chord (default: True).

        Returns:
            Note: A Note object representing the chord.

        Raises:
            ValueError: If the mix type is invalid.
        """
        note_map = {
            "C": 0,
            "C#": 1,
            "Db": 1,
            "D": 2,
            "D#": 3,
            "Eb": 3,
            "E": 4,
            "F": 5,
            "F#": 6,
            "Gb": 6,
            "G": 7,
            "G#": 8,
            "Ab": 8,
            "A": 9,
            "A#": 10,
            "Bb": 10,
            "B": 11,
        }
        chords = {
            "major": {0, 4, 7},
            "maj7": {0, 4, 7, 11},
            "6": {0, 4, 7, 9},
            "6/9": {0, 4, 7, 9, 14},
            "maj9": {0, 4, 7, 11, 14},
            "minor": {0, 3, 7},
            "m7": {0, 3, 7, 10},
            "m6": {0, 3, 7, 9},
            "m6/9": {0, 3, 7, 9, 14},
            "m9": {0, 3, 7, 10, 14},
            "m11": {0, 3, 7, 10, 14, 17},
            "minMaj7": {0, 3, 7, 11},
            "7": {0, 4, 7, 10},
            "9": {0, 4, 7, 10, 14},
            "11": {0, 4, 7, 10, 14, 17},
            "dim": {0, 3, 6},
            "dim7": {0, 3, 6, 9},
            "half-dim": {0, 3, 6, 10},
            "aug": {0, 4, 8},
            "aug7": {0, 4, 8, 10},
            "7-5": {0, 4, 6, 10},
            "7+5": {0, 4, 8, 10},
            "7-9": {0, 4, 7, 10, 13},
            "7+9": {0, 4, 7, 10, 15},
            "7#11": {0, 4, 7, 10, 18},
            "5": {0, 7},
            "add9": {0, 4, 7, 14},
            "add2": {0, 2, 4, 7},
            "add11": {0, 4, 7, 17},
            "add4": {0, 4, 5, 7},
            "sus4": {0, 5, 7},
            "sus2": {0, 2, 7},
        }
        populated: List[SoundElementType] = []
        base_midi = chord[0] * 12 + note_map.get(chord[1], 0)
        name = f"{chord[0]}{chord[1]}{chord[2]}"
        chord_offsets = chords.get(chord[2], {0})
        for offset in chord_offsets:
            elem = SoundElement()
            elem.set_frequency_to_midi_note(base_midi + offset)
            populated.append(elem)
        while len(populated) > 1:
            a = populated.pop(0)
            b = populated.pop(0)
            if mix == self.MixType.SUM:
                combined = SumElements(a=a, b=b)
            elif mix == self.MixType.MIX:
                combined = MixElements(a=a, b=b)
            else:
                raise ValueError("Invalid mix type")
            populated.append(combined)
        root = populated[0]
        if pluck:
            root = Pluck(a=root)
        return Note(note=root, name=name)


class Instrument:
    """A class to manage a collection of notes.

    Attributes:
        instr (Dict[str, Note]): Dictionary of notes, keyed by name.
        name (str): Unique identifier for the instrument.
    """

    def __init__(
        self, instrument: Dict[str, Note] | None = None, name: str | None = None
    ):
        """Initialize an Instrument instance.

        Args:
            instrument (Dict[str, Note], optional): Initial dictionary of notes.
            name (str, optional): Unique identifier for the instrument.
        """
        self._TYPE = "Instrument"
        self._instr = instrument or {}
        self._name = name or f"{self._TYPE}_{id(self)}"

    def get_note_lst(self) -> List[str]:
        """Get the list of note names in the instrument.

        Returns:
            List[str]: List of note names.
        """
        return list(self._instr.keys())

    def add_note(self, note: object, name: str | None = None) -> None:
        """Add a note to the instrument.

        Args:
            note (object): The note to add (must have a sample() method).
            name (str, optional): The name for the note. Uses note's name if None.

        Raises:
            ValueError: If note does not have a sample() method.
        """
        if not isinstance(
            note,
            (
                Note,
                SoundElement,
                SumElements,
                MultiplyElements,
                MixElements,
                Pluck,
                FixedAttenuate,
            ),
        ):
            raise ValueError("object assignment as Note has no attribute sample()")
        key = name or note.get_name()
        self._instr[key] = note

    def get_note(self, note: str) -> object:
        """Get a note by its name.

        Args:
            note (str): The name of the note.

        Returns:
            object: The note object, or None if not found.
        """
        return self._instr.get(note)

    def get_type(self) -> str:
        """Get the type identifier of the instrument.

        Returns:
            str: The type string ("Instrument").
        """
        return self._TYPE

    def get_name(self) -> str:
        """Get the unique identifier of the instrument.

        Returns:
            str: The instrument's name.
        """
        return self._name

    def make_from_chords(
        self,
        chords_lst: List[Tuple[int, str, str]],
        mix: Note.MixType = Note.MixType.SUM,
        pluck: bool = True,
    ) -> None:
        """Create and add notes from a list of chord specifications.

        Args:
            chords_lst (List[Tuple[int, str, str]]): List of (octave, note, chord_type) tuples.
            mix (Note.MixType): The mixing method for chords (default: Note.MixType.SUM).
            pluck (bool): If True, apply a Pluck effect to chords (default: True).
        """
        note_instance = Note()
        for chord in chords_lst:
            chord_note = note_instance.make_a_chord(chord, mix, pluck)
            self.add_note(chord_note)

    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.

        Args:
            msg (Dict[str, Dict[str, List]]): A dictionary of commands for this instrument.

        Returns:
            Dict[str, Any]: A dictionary with the results of the commands, including notes.
        """
        return_val: Dict[str, Any] = {self._name: {}}
        for name in msg:
            if name == self._name:
                for cmd, val in msg[name].items():
                    if cmd == "get_name":
                        return_val[self._name]["get_name"] = self.get_name()
                    elif cmd == "get_type":
                        return_val[self._name]["get_type"] = self.get_type()
                    elif cmd == "get_note_lst":
                        return_val[self._name]["get_note_lst"] = self.get_note_lst()
                for k, v in self._instr.items():
                    note_val = v.msg(msg)
                    if note_val:
                        return_val[k] = note_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the instrument's state for storage or factory use.

        Returns:
            Dict[str, Any]: A dictionary containing the instrument's properties and notes.
        """
        return_val: Dict[str, Any] = {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
        }
        for k, v in self._instr.items():
            return_val[k] = v.dump()
        return return_val

    def instrument_factory(
        self, instr_dump: Dict[str, Any], force: bool = True
    ) -> None:
        """Build an instrument from a serialized data dictionary.

        Args:
            instr_dump (Dict[str, Any]): A dictionary containing the instrument hierarchy.
            force (bool): If True, overwrite existing notes on name collision (default: True).

        Raises:
            ValueError: If instr_dump is not an Instrument or if note names collide and force is False.
        """
        if instr_dump["get_type"] != "Instrument":
            raise ValueError("instrument_factory requires type 'Instrument' at top")
        results = {}
        for k, v in instr_dump.items():
            if k in ("get_name", "get_type"):
                continue
            if v["get_type"] == "Note":
                f = Note()
                f.note_factory_hier_db(v)
                if not force and k in self._instr:
                    raise ValueError(
                        f"instrument_factory Note collision for '{k}', use force to replace"
                    )
                results[k] = f
        self._instr.update(results)


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
        event_list (List[Event]): List of events, sorted by time.
        name (str): Unique identifier for the event list.
    """

    def __init__(self, event_list: List[Event] | None = None, name: str | None = None):
        """Initialize an EventList instance.

        Args:
            event_list (List[Event], optional): Initial list of events.
            name (str, optional): Unique identifier for the event list.
        """
        self._TYPE = "EventList"
        self._event_list = event_list or []
        if self._event_list:
            self._event_list.sort(key=lambda e: e.get_time())
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
        self._event_list.append(entry)
        self._event_list.sort(key=lambda e: e.get_time())

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

    def get_event(self, item: int) -> Event:
        """Get an event by its index.

        Args:
            item (int): The index of the event.

        Returns:
            Event: The event at the specified index.

        Raises:
            IndexError: If item is out of range.
        """
        if not 0 <= item < len(self._event_list):
            raise IndexError("Event index out of range")
        return self._event_list[item]

    def remove_event(self, entry: Event) -> None:
        """Remove an event from the list.

        Args:
            entry (Event): The event to remove.

        Raises:
            ValueError: If entry is not in the list.
        """
        if entry not in self._event_list:
            raise ValueError("Event not found in list")
        self._event_list.remove(entry)

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
            List[Event]: The list of events.
        """
        return self._event_list

    def next_event(self, ptime: int) -> int | None:
        """Find the next event time equal to or greater than the given ptime.

        Args:
            ptime (int): The presentation time to search for.

        Returns:
            int | None: The ptime of the first event with time >= ptime, or None if no such event exists.
        """
        for event in self._event_list:
            if event.get_time() >= ptime:
                return event.get_time()
        return None

    def get_ptime_list(self) -> List[int]:
        """Get a sorted list of unique event times.

        Returns:
            List[int]: Sorted list of unique ptimes, earliest first at index 0.
        """
        seen: set[int] = set()
        result: List[int] = []
        for event in self._event_list:
            ptime = event.get_time()
            if ptime not in seen:
                seen.add(ptime)
                result.append(ptime)
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
                # Route messages to underlying events
                for event in self._event_list:
                    event_val = event.msg(msg)
                    if event_val:
                        return_val[self._name][event.get_name()] = event_val
        return return_val

    def dump(self) -> Dict[str, Any]:
        """Serialize the event list's state for storage.

        Returns:
            Dict[str, Any]: A dictionary containing the event list's properties
                and all contained events.
        """
        return_val: Dict[str, Any] = {
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "events": [event.dump() for event in self._event_list],
        }
        return return_val


class Sequencer:
    """A class to sequence audio events and generate samples.

    Attributes:
        instrument_lib (Dict[str, Instrument]): Dictionary of instruments, keyed by name.
        event_lib (Dict[str, EventList]): Dictionary of event lists, keyed by name.
        name (str): Unique identifier for the sequencer.
        time (int): Current time in samples.
        active_notes (Dict[str, Tuple[Note, int]]): Active notes with their end times.
        next_event_time (int): Time of the next event to process.
        event_pointers (Dict[str, int]): Event pointers for each event list.
    """

    def __init__(
        self,
        instrument_lib: Dict[str, Instrument] | None = None,
        event_lib: Dict[str, EventList] | None = None,
        name: str | None = None,
    ):
        """Initialize a Sequencer instance.

        Args:
            instrument_lib (Dict[str, Instrument], optional): Initial dictionary of instruments.
            event_lib (Dict[str, EventList], optional): Initial dictionary of event lists.
            name (str, optional): Unique identifier for the sequencer.
        """
        self._TYPE = "Sequencer"
        self._instrument_lib = instrument_lib or {}
        self._event_lib = event_lib or {}
        self._name = name or f"{self._TYPE}_{id(self)}"
        self._time: int = 0
        self._active_notes: Dict[str, Tuple[Note, int]] = {}
        self._next_event_time: int = 0
        self._event_pointers = {k: 0 for k in self._event_lib}
        self.init()

    def add_event_list(self, events: EventList) -> None:
        """Add an event list to the sequencer.

        Args:
            events (EventList): The event list to add.
        """
        self._event_lib[events.get_name()] = events

    def generate_event_queue(self) -> None:
        pass # TODO

    def add_instrument(self, instrument: Instrument) -> None:
        """Add an instrument to the sequencer.

        Args:
            instrument (Instrument): The instrument to add.
        """
        self._instrument_lib[instrument.get_name()] = instrument

    def add_instrument_lib(self, instrument_lib: Dict[str, Instrument]) -> None:
        """Add a dictionary of instruments to the sequencer.

        Args:
            instrument_lib (Dict[str, Instrument]): Dictionary of instruments to add.
        """
        self._instrument_lib.update(instrument_lib)

    def add_event_lib(self, event_lib: Dict[str, EventList]) -> None:
        """Add a dictionary of event lists to the sequencer.

        Args:
            event_lib (Dict[str, EventList]): Dictionary of event lists to add.
        """
        self._event_lib.update(event_lib)

    def init(self) -> None:
        """Initialize or reset the sequencer state."""
        self._time = 0
        self._active_notes = {}
        self._event_pointers = {k: 0 for k in self._event_lib}
        if self._event_lib:
            self._next_event_time = min(
                el.get_event(0).get_time()
                for el in self._event_lib.values()
                if el._event_list
            )
        else:
            self._next_event_time = float("inf")

    def sample(self) -> float:
        """Generate the next audio sample by processing active notes.

        Returns:
            float: The sum of samples from active notes.
        """
        if self._time >= self._next_event_time:
            self.process_events()
        samples = np.array([note.sample() for note, _ in self._active_notes.values()])
        to_remove = [
            key
            for key, (_, end_time) in self._active_notes.items()
            if self._time >= end_time
        ]
        for key in to_remove:
            note, _ = self._active_notes.pop(key)
            note.set_off()
        self._time += 1
        return float(np.sum(samples))

    def process_events(self) -> None:
        """Process events at the current time, updating active notes."""
        for list_name, el in self._event_lib.items():
            pointer = self._event_pointers[list_name]
            while (
                pointer < len(el._event_list)
                and el._event_list[pointer].get_time() <= self._time
            ):
                event = el.get_event(pointer)
                for item in event.get_items():
                    if isinstance(item, Event.AmNote):
                        instr = self._instrument_lib.get(item._instrument)
                        if not instr:
                            continue
                        note_obj = instr.get_note(item._note)
                        if not note_obj:
                            continue
                        if item._action in ("add", "add_pluck"):
                            note_obj.set_on()
                            if item._action == "add_pluck" and hasattr(
                                note_obj.get_note(), "sample_pluck"
                            ):
                                note_obj.get_note().sample_pluck()
                            end_time = self._time + item._duration
                            key = f"{item._instrument}_{item._note}_{self._time}"
                            self._active_notes[key] = (note_obj, end_time)
                        elif item._action == "rm":
                            for k, (n, _) in list(self._active_notes.items()):
                                if n == note_obj:
                                    n.set_off()
                                    del self._active_notes[k]
                        elif item._action == "pluck" and hasattr(
                            note_obj.get_note(), "sample_pluck"
                        ):
                            note_obj.get_note().sample_pluck()
                    elif isinstance(item, Event.AmMSG):
                        for instr in self._instrument_lib.values():
                            instr.msg(item._msg)
                pointer += 1
            self._event_pointers[list_name] = pointer
        next_times = [
            el._event_list[pointer].get_time()
            for list_name, pointer in self._event_pointers.items()
            if pointer < len(self._event_lib[list_name]._event_list)
        ]
        self._next_event_time = min(next_times) if next_times else float("inf")
