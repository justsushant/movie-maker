import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip


def load_data(json_file):
    """Loads the hierarchical subtitle JSON from the given path."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def _resolve_font(font_size):
    """Attempts to load a TrueType font, falling back to the default."""
    try:
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            print("Warning: Could not load specific font. Using default.")
            return ImageFont.load_default()


def make_frame(t, data, font, video_settings):
    """
    Generates the frame for a given time `t`.

    Args:
        t: Current time in seconds.
        data: List of sentence dicts (from the subtitle JSON).
        font: PIL ImageFont instance.
        video_settings: Dict with keys: width, height, bg_color, text_color,
                        highlight_color, font_size.
    """
    width = video_settings["width"]
    height = video_settings["height"]
    bg_color = video_settings["bg_color"]
    text_color = video_settings["text_color"]
    highlight_color = video_settings["highlight_color"]
    font_size = video_settings["font_size"]

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Find the current sentence
    current_sentence = None
    for sentence in data:
        if sentence["start_time"] <= t <= sentence["end_time"]:
            current_sentence = sentence
            break

    if not current_sentence:
        return np.array(image)

    words = current_sentence["words"]

    # Calculate total width to center the text
    word_widths = []
    total_width = 0
    for word in words:
        left, top, right, bottom = draw.textbbox((0, 0), word["text"], font=font)
        w = right - left
        word_widths.append(w)
        total_width += w

    # Start drawing positions (centered)
    x = (width - total_width) // 2
    y = height // 2 - font_size // 2

    # Draw each word
    for i, word in enumerate(words):
        is_highlighted = word["start_time"] <= t <= word["end_time"]
        color = highlight_color if is_highlighted else text_color
        draw.text((x, y), word["text"], font=font, fill=color)
        x += word_widths[i]

    return np.array(image)


def create_video(config):
    """
    Renders the final video by compositing subtitle frames over audio.

    Args:
        config: The full configuration dict from config.get_config().
               Required keys: json_file, audio_file, output_video,
               width, height, fps, font_size, bg_color, text_color,
               highlight_color.
    """
    json_file = config["json_file"]
    audio_file = config["audio_file"]
    output_video = config["output_video"]
    fps = config["fps"]

    print("Loading data and audio...")
    data = load_data(json_file)
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration

    max_end_time = data[-1]["end_time"] if data else 0
    final_duration = max(duration, max_end_time)
    print(f"Video duration: {final_duration:.2f} seconds")

    font = _resolve_font(config["font_size"])

    # Build the video-settings subset for make_frame
    video_settings = {
        "width": config["width"],
        "height": config["height"],
        "bg_color": config["bg_color"],
        "text_color": config["text_color"],
        "highlight_color": config["highlight_color"],
        "font_size": config["font_size"],
    }

    print("Generating frames...")
    video_clip = VideoClip(
        lambda t: make_frame(t, data, font, video_settings),
        duration=final_duration,
    )
    video_clip = video_clip.with_audio(audio_clip)

    print(f"Exporting to {output_video}...")
    video_clip.write_videofile(output_video, fps=fps, codec="libx264", audio_codec="aac")
    print("Export complete!")
