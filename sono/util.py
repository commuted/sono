# util.py
# Utility functions for audio synthesis
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Any, Dict, List
from math import pi, sin, asin

from .music import Chord


class Util:
    """Utility class for audio synthesis operations.

    Provides helper methods for common audio processing tasks such as
    eliminating pops at chord start by phase alignment.
    """

    @staticmethod
    def _collect_sound_element_names(dump: Dict[str, Any], names: List[str]) -> None:
        """Recursively collect all SoundElement names from a dump hierarchy.

        Args:
            dump: A dump dictionary from an element's dump() method.
            names: List to append found SoundElement names to.
        """
        if dump is None:
            return

        if dump.get("get_type") == "SoundElement":
            names.append(dump["get_name"])

        # Recurse into sub-elements
        if "a" in dump and dump["a"] is not None:
            Util._collect_sound_element_names(dump["a"], names)
        if "b" in dump and dump["b"] is not None:
            Util._collect_sound_element_names(dump["b"], names)

    @staticmethod
    def fix_pop(chord: Chord) -> None:
        """Fix the pop/click at chord start by spreading and adjusting phases.

        The pop is caused by oscillators starting in phase, creating a large
        initial derivative (rapid amplitude change) and potentially a non-zero
        starting value. This method:
        1. Spreads oscillator phases evenly to reduce peak derivative
        2. Adjusts individual phase(s) so the combined signal starts at zero

        Args:
            chord: The Chord to fix.
        """
        # Get the chord's element hierarchy
        dump = chord.dump()

        # Collect all SoundElement names
        element_names: List[str] = []
        if dump.get("a") is not None:
            Util._collect_sound_element_names(dump["a"], element_names)

        n = len(element_names)
        if n == 0:
            return

        # Step 1: Spread phases evenly across 2π to reduce derivative
        phases = [(2 * pi * i) / n for i in range(n)]

        # Step 2: Calculate current sum of initial values
        current_sum = sum(sin(p) for p in phases)

        # Step 3: Adjust phase(s) to bring sum to zero
        # Try adjusting the last phase first
        if abs(current_sum) > 1e-10:
            # Sum of first n-1 phases
            partial_sum = sum(sin(p) for p in phases[:-1])

            # Need sin(new_phase) = -partial_sum to make total = 0
            target_sin = -partial_sum

            if abs(target_sin) <= 1.0:
                # Can solve with single phase adjustment
                phases[-1] = asin(target_sin)
            else:
                # Need to adjust multiple phases
                # Distribute the adjustment across phases
                adjustment_per_phase = current_sum / n
                for i in range(n):
                    # Iteratively adjust each phase to reduce its contribution
                    current_val = sin(phases[i])
                    new_val = current_val - adjustment_per_phase
                    if abs(new_val) <= 1.0:
                        phases[i] = asin(new_val)

        # Build msg to set init_phase for all SoundElements
        # Using set_init_phase ensures the phase persists through set_on()
        msg: Dict[str, Dict[str, List]] = {}
        for i, name in enumerate(element_names):
            msg[name] = {"set_init_phase": [phases[i]]}

        # Send the message through the chord's msg interface
        chord.msg(msg)
