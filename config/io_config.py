"""I/O configuration for input/output paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class IOConfig:
    """Configuration for input/output paths.
    
    Attributes:
        input_text: Path to input text file
        output_dir: Base output directory for the run
        json_file: Path to output JSON metadata file
        audio_file: Path to output audio WAV file
        srt_file: Path to output SRT subtitle file
        video_file: Path to output video MP4 file
    """
    input_text: Path
    output_dir: Path
    json_file: Path
    audio_file: Path
    srt_file: Path
    video_file: Path
    
    @classmethod
    def from_dict(cls, config: dict) -> IOConfig:
        """Create IOConfig from legacy config dictionary.
        
        Args:
            config: Configuration dictionary containing I/O paths
            
        Returns:
            IOConfig instance with paths from the dictionary
        """
        run_dir = Path(config["run_dir"])
        return cls(
            input_text=Path(config["input_text"]),
            output_dir=run_dir,
            json_file=run_dir / "output_moviepy.json",
            audio_file=run_dir / "output_moviepy.wav",
            srt_file=run_dir / "output_moviepy_word.srt",
            video_file=Path(config.get("output_video", run_dir / "output_video.mp4"))
        )
