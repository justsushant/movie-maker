import os
from datetime import datetime


def get_config(run_name=None):
    """
    Returns the single configuration dictionary.
    Each run gets its own timestamped output directory under output/.
    """
    if run_name is None:
        run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    run_dir = os.path.join("output", run_name)

    return {
        # --- Paths ---
        "input_text": os.path.join("files", "input.txt"),
        "run_dir": run_dir,
        "json_file": os.path.join(run_dir, "output_moviepy.json"),
        "audio_file": os.path.join(run_dir, "output_moviepy.wav"),
        "srt_file": os.path.join(run_dir, "output_moviepy_word.srt"),
        "output_video": os.path.join(run_dir, "output_video.mp4"),

        # --- TTS Settings ---
        "lang_code": "a",
        "voice": "af_heart",
        "speed": 1.0,

        # --- Video Settings ---
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "font_size": 40,
        "bg_color": (0, 0, 0),
        "text_color": (255, 255, 255),
        "highlight_color": (255, 255, 0),
    }
