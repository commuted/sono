# protocol.py
# Protocol definitions for audio elements
# License: BSD 3-Clause License
#
# Copyright (c) 2025, [Your Name or Organization]

from __future__ import annotations
from typing import Protocol, Dict, List, Any, runtime_checkable


@runtime_checkable
class AudioElement(Protocol):
    """Protocol defining the interface for all audio elements.
    
    This protocol ensures all audio elements can be composed uniformly
    in the signal graph, regardless of their specific implementation.
    """
    
    def sample(self) -> float:
        """Generate the next audio sample.
        
        Returns:
            float: Audio sample value, typically in range [-1.0, 1.0]
        """
        ...
    
    def sample_pluck(self) -> float:
        """Generate the next sample with pluck envelope triggering.
        
        This method propagates pluck triggers through the element tree,
        allowing embedded Pluck envelopes to be armed regardless of
        their position in the hierarchy.
        
        Returns:
            float: Audio sample value with pluck triggering
        """
        ...
    
    def set_on(self) -> None:
        """Activate the audio element.
        
        Typically resets phase and prepares the element for sample generation.
        """
        ...
    
    def set_off(self) -> None:
        """Deactivate the audio element.
        
        May trigger release phases in envelopes or graceful shutdown.
        """
        ...
    
    def set_scale(self, scale: float) -> None:
        """Set the amplitude scaling factor.
        
        Args:
            scale: Amplitude multiplier
        """
        ...
    
    def get_scale(self) -> float:
        """Get the current amplitude scaling factor.
        
        Returns:
            float: Current amplitude multiplier
        """
        ...
    
    def get_type(self) -> str:
        """Get the type identifier of the element.
        
        Returns:
            str: Type string (e.g., "SoundElement", "Pluck")
        """
        ...
    
    def get_name(self) -> str:
        """Get the unique identifier of the element.
        
        Returns:
            str: Unique name for this element instance
        """
        ...
    
    def msg(self, msg: Dict[str, Dict[str, List]]) -> Dict[str, Any]:
        """Process control messages to set or get properties.
        
        Args:
            msg: Dictionary of commands keyed by element name
        
        Returns:
            Dict containing command results
        """
        ...
    
    def dump(self) -> Dict[str, Any]:
        """Serialize the element's state for storage or factory use.
        
        Returns:
            Dict containing all state needed to reconstruct the element
        """
        ...


@runtime_checkable
class ModulationSource(Protocol):
    """Protocol for elements that can modulate parameters.
    
    Examples: LFO, ADSR envelope, other control signals
    """
    
    def get_modulation_value(self) -> float:
        """Get the current modulation value.
        
        Returns:
            float: Modulation value (range depends on source type)
        """
        ...
    
    def trigger(self) -> None:
        """Trigger the modulation source (e.g., start envelope).
        
        Optional method - not all modulation sources need triggering.
        """
        ...
    
    def release(self) -> None:
        """Release the modulation source (e.g., envelope release phase).
        
        Optional method - not all modulation sources have release.
        """
        ...
