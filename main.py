import os
import shutil

from config import get_config
from tts_pipeline import MoviePySubtitleExtractor
from renderer import create_video


def main():
    """
    Orchestrates the full pipeline:
      1. Read input text from files/input.txt
      2. Create a timestamped run directory under output/
      3. Generate TTS audio + subtitle metadata
      4. Render the final video with highlighted subtitles
    """
    cfg = get_config()

    # Create the run directory
    os.makedirs(cfg["run_dir"], exist_ok=True)
    print(f"Run directory: {cfg['run_dir']}")

    # 1. Read input text
    input_path = cfg["input_text"]
    print(f"Reading input text from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("Error: input.txt is empty. Add some text and try again.")
        return

    # Copy input.txt into the run directory for reproducibility
    shutil.copy2(input_path, os.path.join(cfg["run_dir"], "input.txt"))

    # 2. Run TTS pipeline — inject voice/speed/lang settings
    print("Generating TTS and extracting timing metadata...")
    extractor = MoviePySubtitleExtractor(
        text,
        lang_code=cfg["lang_code"],
        voice=cfg["voice"],
        speed=cfg["speed"],
    )

    extractor.export_moviepy_json(cfg["json_file"])
    extractor.get_audio(cfg["audio_file"])
    extractor.get_word_level_subtitles(cfg["srt_file"])

    # 3. Render video — inject all video/path settings
    print("Rendering video...")
    create_video(cfg)

    print(f"\nDone! All outputs saved to {cfg['run_dir']}/")


if __name__ == "__main__":
    main()
