import os
import shutil
import json
from pathlib import Path
from datetime import datetime

from tts.config import TTSConfig
from config.video_config import VideoConfig
from subtitle.config import SubtitleConfig, SubtitleMode
from api.library import generate_video_from_file


def get_default_tts_config() -> TTSConfig:
    """Return default TTS configuration for CLI."""
    return TTSConfig(
        lang_code="a",
        voice="af_heart",
        speed=1.0
    )


def get_default_video_config() -> VideoConfig:
    """Return default video configuration for CLI."""
    return VideoConfig(
        width=1920,
        height=1080,
        fps=30,
        bg_color=(0, 0, 0)
    )


def get_default_subtitle_config() -> SubtitleConfig:
    """Return default subtitle configuration for CLI."""
    return SubtitleConfig(
        mode=SubtitleMode.SENTENCE_WITH_WORD_HIGHLIGHT,
        base_color=(255, 255, 255),
        highlight_color=(255, 255, 0),
        font_size=40,
        multiline_enabled=False,
        overflow_strategy="chunk_single_line"
    )


def create_run_directory() -> Path:
    """Create timestamped output directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("output") / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


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


def run_pipeline():
    """
    Runs the full pipeline:
      1. Read input text from files/input.txt
      2. Create a timestamped run directory under output/
      3. Generate TTS audio + subtitle metadata
      4. Render the final video with highlighted subtitles
    """
    # Configuration
    input_file = Path("files/input.txt")
    run_dir = create_run_directory()
    
    print(f"Run directory: {run_dir}")
    
    # 1. Check input text exists and is not empty
    print(f"Reading input text from {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: input.txt is empty. Add some text and try again.")
        return

    # Copy input.txt into the run directory for reproducibility
    shutil.copy2(input_file, run_dir / "input.txt")

    # 2. Build configuration objects
    tts_config = get_default_tts_config()
    video_config = get_default_video_config()
    subtitle_config = get_default_subtitle_config()

    # 3. Use library API to generate video
    print("Generating video using library API...")
    video_path = generate_video_from_file(
        input_file=input_file,
        output_dir=run_dir,
        tts_config=tts_config,
        video_config=video_config,
        subtitle_config=subtitle_config
    )

    # 4. Generate SRT file for compatibility (CLI-specific feature)
    print("Generating SRT subtitles...")
    json_file = run_dir / "output_moviepy.json"
    srt_file = run_dir / "output_moviepy_word.srt"
    _generate_srt_from_json(json_file, srt_file)

    print(f"\nDone! All outputs saved to {run_dir}/")
    print(f"Video file: {video_path}")


def main():
    """Entry point for normal CLI usage with default config."""
    run_pipeline()


if __name__ == "__main__":
    main()
