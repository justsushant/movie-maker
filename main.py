import os
import shutil
import json
import importlib.util
from pathlib import Path

# Import from config.py file (not config/ package) to avoid naming conflict
_config_spec = importlib.util.spec_from_file_location("config_module", "config.py")
config_py = importlib.util.module_from_spec(_config_spec)
_config_spec.loader.exec_module(config_py)

from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle_config import SubtitleConfig
from api.library import generate_video_from_file


def _generate_srt_from_json(json_file: Path, srt_file: Path) -> None:
    """
    Generate SRT subtitle file from JSON metadata.
    
    This is a CLI-specific feature that creates standard SRT subtitles
    for compatibility with external video players and editors.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    def _format_timestamp(seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
    
    with open(srt_file, 'w', encoding='utf-8') as f:
        idx = 1
        for segment in segments:
            for word in segment.get('words', []):
                start_time = word['start_time']
                end_time = word['end_time']
                text = word['text'].strip()
                
                if text:
                    f.write(f"{idx}\n")
                    f.write(f"{_format_timestamp(start_time)} --> {_format_timestamp(end_time)}\n")
                    f.write(f"{text}\n\n")
                    idx += 1


def run_pipeline(cfg):
    """
    Runs the full pipeline with an injected config:
      1. Read input text from files/input.txt
      2. Create a timestamped run directory under output/
      3. Generate TTS audio + subtitle metadata
      4. Render the final video with highlighted subtitles
    """
    # Create the run directory
    os.makedirs(cfg["run_dir"], exist_ok=True)
    print(f"Run directory: {cfg['run_dir']}")

    # 1. Check input text exists and is not empty
    input_path = cfg["input_text"]
    print(f"Reading input text from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: input.txt is empty. Add some text and try again.")
        return

    # Copy input.txt into the run directory for reproducibility
    shutil.copy2(input_path, os.path.join(cfg["run_dir"], "input.txt"))

    # 2. Build configuration objects from legacy config dict
    tts_config = TTSConfig.from_dict(cfg)
    video_config = VideoConfig.from_dict(cfg)
    subtitle_config = SubtitleConfig.from_dict(cfg)

    # 3. Use new library API to generate video
    print("Generating video using library API...")
    video_path = generate_video_from_file(
        input_file=Path(input_path),
        output_dir=Path(cfg["run_dir"]),
        tts_config=tts_config,
        video_config=video_config,
        subtitle_config=subtitle_config
    )

    # 4. Generate SRT file for compatibility (CLI-specific feature)
    print("Generating SRT subtitles...")
    json_file = Path(cfg["run_dir"]) / "output_moviepy.json"
    srt_file = Path(cfg["srt_file"])
    _generate_srt_from_json(json_file, srt_file)

    print(f"\nDone! All outputs saved to {cfg['run_dir']}/")
    print(f"Video file: {video_path}")


def main():
    """Entry point for normal CLI usage with default config."""
    cfg = config_py.get_config()
    run_pipeline(cfg)


if __name__ == "__main__":
    main()
