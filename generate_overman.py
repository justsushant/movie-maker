#!/usr/bin/env python3
"""
Generate a video from Nietzsche's Overman text using KokoroMoviePy API.
"""

from pathlib import Path
from api.library import generate_video_from_text

# The text to convert to video
text = """I teach you the Overman. Man is something that shall be overcome. What have you done to overcome him?
All beings hitherto have created something beyond themselves: and do you want to be the ebb of this great tide, and rather go back to the beast than overcome man?
What is the ape to man? A laughingstock, or a painful embarrassment. And just the same shall man be to the Overman: a laughingstock, or a painful embarrassment.
You have made your way from worm to man, and much within you is still worm. Once you were apes, and even now, too, man is more ape than any ape.
The Overman is the meaning of the earth. Let your will say: The Overman shall be the meaning of the earth!
I conjure you, my brothers, remain faithful to the earth, and do not believe those who speak to you of otherworldly hopes! They are poisoners, whether they know it or not.
They are despisers of life, decaying and poisoned themselves, of whom the earth is weary: so let them go."""

if __name__ == "__main__":
    # Output directory for this video
    output_dir = Path("output/overman_video")
    
    print("Starting video generation...")
    print(f"Output directory: {output_dir}")
    
    # Generate the video using default settings
    # - TTS: American English, af_heart voice, 1.0 speed
    # - Video: 1920x1080, 30fps, black background
    # - Subtitles: sentence_with_word_highlight mode, white text with yellow highlights
    video_path = generate_video_from_text(
        text=text,
        output_dir=output_dir
    )
    
    print(f"\n✓ Video generated successfully!")
    print(f"  Location: {video_path}")
    print(f"\nYou can find the following files in {output_dir}:")
    print(f"  - output_video.mp4 (the final video)")
    print(f"  - output_moviepy.wav (the audio)")
    print(f"  - output_moviepy.json (subtitle timing data)")
