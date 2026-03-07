"""
Configuration for TTS engines.

This module provides configuration dataclasses for TTS engines,
with support for backward compatibility with legacy config dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TTSConfig:
    """
    Configuration for TTS engine.
    
    Attributes:
        lang_code: Language code for TTS (default: "a" for American English)
        voice: Voice identifier (default: "af_heart")
        speed: Speech speed multiplier (default: 1.0)
    """
    lang_code: str = "a"
    voice: str = "af_heart"
    speed: float = 1.0
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> TTSConfig:
        """
        Create TTSConfig from legacy config dictionary.
        
        This method provides backward compatibility with the existing
        configuration system that uses a single dictionary for all settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            TTSConfig instance with values from the dictionary
        """
        return cls(
            lang_code=config.get("lang_code", "a"),
            voice=config.get("voice", "af_heart"),
            speed=config.get("speed", 1.0)
        )
