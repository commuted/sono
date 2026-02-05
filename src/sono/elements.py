# elements.py
# Sound element classes for audio synthesis
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

if TYPE_CHECKING:
    SoundElementType = Union[
        "SoundElement",
        "SumElements",
        "MultiplyElements",
        "MixElements",
        "Pluck",
        "FixedAttenuate",
    ]


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
            phase (float): Initial phase in radians (default: 0.0).
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

    def sample_pluck(self) -> float:
        """Alias for sample() to support pluck propagation from parent elements.

        Returns:
            float: The sample value (same as sample()).
        """
        return self.sample()

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
    def midi_note(key_no: int, steps_per_octave: int = 12) -> float:
        """Calculate the frequency for a MIDI note number.

        Args:
            key_no (int): MIDI note number.
            steps_per_octave (int): Number of steps per octave (default: 12 for equal temperament).

        Returns:
            float: The frequency in Hz.
        """
        return 440.0 * 2 ** ((key_no - 69) / steps_per_octave)

    @staticmethod
    def midi_key_from_freq(frequency: float, steps_per_octave: int = 12) -> float:
        """Calculate the MIDI note number from a frequency.

        Args:
            frequency (float): The frequency in Hz.
            steps_per_octave (int): Number of steps per octave (default: 12).

        Returns:
            float: The MIDI note number (fractional).

        Raises:
            ValueError: If frequency is not positive.
        """
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        return steps_per_octave * log2(frequency / 440.0) + 69

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

    def set_init_phase(self, phase: float) -> None:
        """Set the initial phase of the wave (used by set_on).

        Args:
            phase (float): The phase in radians.
        """
        self._init_phase = phase
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
        # Propagate to sub-elements regardless of name match
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

    def sample_pluck(self) -> float:
        """Generate the next sample by multiplying input pluck samples.

        Propagates sample_pluck() to children for embedded Pluck support.

        Returns:
            float: The product of input pluck samples, scaled.
        """
        a_sample = self._a.sample_pluck() if self._a else 0.0
        b_sample = self._b.sample_pluck() if self._b else 0.0
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
        # Propagate to sub-elements regardless of name match
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

    def sample_pluck(self) -> float:
        """Generate the next sample by mixing input pluck samples.

        Propagates sample_pluck() to children for embedded Pluck support.

        Returns:
            float: The mixed pluck sample, scaled.
        """
        sea = self._a.sample_pluck() if self._a else 0.0
        seb = self._b.sample_pluck() if self._b else 0.0
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
        # Propagate to sub-elements regardless of name match
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

    def sample_pluck(self) -> float:
        """Generate the next sample by summing input pluck samples.

        Propagates sample_pluck() to children for embedded Pluck support.

        Returns:
            float: The sum of input pluck samples, scaled.
        """
        sea = self._a.sample_pluck() if self._a else 0.0
        seb = self._b.sample_pluck() if self._b else 0.0
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
        # Propagate to sub-element regardless of name match
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

    def sample_pluck(self) -> float:
        """Generate the next pluck sample with fixed attenuation.

        Propagates sample_pluck() to child for embedded Pluck support.

        Returns:
            float: The attenuated pluck sample.
        """
        return (self._a.sample_pluck() if self._a else 0.0) * self._scale

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
        # Propagate to sub-element regardless of name match
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
            "get_type": self.get_type(),
            "get_name": self.get_name(),
            "a": self._a.dump() if self._a else None,
        }
