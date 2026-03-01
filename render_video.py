import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip

# CONFIGURATION
JSON_FILE = "output_moviepy.json"
AUDIO_FILE = "output_moviepy.wav"
OUTPUT_VIDEO = "output_video.mp4"

# VIDEO SETTINGS
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30
FONT_SIZE = 40 # Adjust based on screen size
BACKGROUND_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow

def load_data():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def make_frame(t, data, font):
    """Generates the frame for a given time `t`."""
    image = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    
    # Find the current sentence
    current_sentence = None
    for sentence in data:
        if sentence["start_time"] <= t <= sentence["end_time"]:
            current_sentence = sentence
            break
            
    if not current_sentence:
        # If no sentence is spoken at time t, just return a blank frame
        return np.array(image)
        
    words = current_sentence["words"]
    
    # Calculate total width to center the text (very basic single-line approach for now)
    # A robust approach would handle text wrapping.
    total_width = 0
    word_widths = []
    
    for word in words:
        # get length of word
        left, top, right, bottom = draw.textbbox((0, 0), word["text"], font=font)
        w = right - left
        word_widths.append(w)
        total_width += w
        
    # Start drawing positions
    x = (VIDEO_WIDTH - total_width) // 2
    y = VIDEO_HEIGHT // 2 - FONT_SIZE // 2
    
    # Draw each word
    for i, word in enumerate(words):
        is_highlighted = word["start_time"] <= t <= word["end_time"]
        color = HIGHLIGHT_COLOR if is_highlighted else TEXT_COLOR
        
        draw.text((x, y), word["text"], font=font, fill=color)
        x += word_widths[i]
        
    return np.array(image)

def create_video():
    print("Loading data and audio...")
    data = load_data()
    audio_clip = AudioFileClip(AUDIO_FILE)
    duration = audio_clip.duration
    
    # Determine the length based on max end_time or audio duration
    max_end_time = data[-1]["end_time"] if data else 0
    final_duration = max(duration, max_end_time)
    
    print(f"Video duration: {final_duration:.2f} seconds")
    
    try:
        # Try a standard macOS font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONT_SIZE)
    except IOError:
        try:
           font = ImageFont.truetype("arial.ttf", FONT_SIZE) 
        except IOError:
           print("Warning: Could not load specific font. Using default.")
           font = ImageFont.load_default()

    print("Generating frames...")
    
    video_clip = VideoClip(lambda t: make_frame(t, data, font), duration=final_duration)
    video_clip = video_clip.with_audio(audio_clip)
    
    print(f"Exporting to {OUTPUT_VIDEO}...")
    video_clip.write_videofile(OUTPUT_VIDEO, fps=FPS, codec="libx264", audio_codec="aac")
    print("Export complete!")

if __name__ == "__main__":
    create_video()
