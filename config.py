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

    cfg = {
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

        # --- Subtitle Settings (optional, used by SubtitleConfig) ---
        # These keep the existing defaults but allow overriding via the
        # nested `subtitle` section if desired.
        "subtitle": {
            # one of: "sentence", "word", "sentence_with_word_highlight", "stacking"
            "mode": "sentence_with_word_highlight",
            # If omitted, base/highlight colors fall back to text_color / highlight_color.
            # "base_color": (255, 255, 255),
            # "highlight_color": (255, 255, 0),
            # "vertical_align": "bottom",
            # "x_margin": 0.05,
            # "y_margin": 0.05,
            # "max_width_ratio": 0.9,
            # "font_size_strategy": "scale_with_height",
            # "font_size": 40,
            "multiline_enabled": False,
            "overflow_strategy": "chunk_single_line",
            # "min_words_per_chunk": 1,
            # "max_words_per_chunk": None,
            # "prefer_break_on_punctuation": True,
        },
    }

    return cfg


def get_test_config(case_id=None, overrides=None):
    """
    Returns config for stress/integration tests.

    All test runs are scoped under output/test:
    - case_id is None    -> output/test
    - case_id is "foo"   -> output/test/foo
    """
    run_name = "test" if not case_id else os.path.join("test", case_id)
    cfg = get_config(run_name=run_name)

    if overrides:
        _deep_update(cfg, overrides)

    return cfg


def _deep_update(target, updates):
    """Recursively updates nested dictionaries in-place."""
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
