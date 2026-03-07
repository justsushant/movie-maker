"""
DEPRECATED MODULE - This module is deprecated and will be removed in a future version.

This module contains the legacy MoviePySubtitleExtractor class which has been
replaced by a modular architecture with better separation of concerns.

MIGRATION GUIDE:
===============

The old MoviePySubtitleExtractor has been replaced by the new modular pipeline.
Please migrate to the new API as follows:

OLD CODE (DEPRECATED):
----------------------
from tts_pipeline import MoviePySubtitleExtractor

extractor = MoviePySubtitleExtractor(
    text="Hello world!",
    lang_code='a',
    voice='af_heart',
    speed=1.0
)
extractor.export_moviepy_json("output.json")
extractor.get_audio("output.wav")

NEW CODE (RECOMMENDED):
-----------------------
from pathlib import Path
from api.library import generate_video_from_text

# Generate complete video from text
video_path = generate_video_from_text(
    text="Hello world!",
    output_dir=Path("output")
)

# Or if you need more control over configuration:
from tts.config import TTSConfig
from config.video_config import VideoConfig

tts_config = TTSConfig(lang_code='a', voice='af_heart', speed=1.0)
video_config = VideoConfig(width=1920, height=1080, fps=30)

video_path = generate_video_from_text(
    text="Hello world!",
    output_dir=Path("output"),
    tts_config=tts_config,
    video_config=video_config
)

BENEFITS OF NEW API:
--------------------
- Cleaner separation of concerns (TTS, processing, rendering)
- Dependency injection for better testability
- Type-safe configuration classes
- Easier to swap TTS engines
- Better error handling and documentation

For more information, see:
- api/library.py - Main library API
- docs/architecture.md - Architecture documentation
- docs/how_it_works.md - Pipeline walkthrough
"""

import json
import re
import warnings
import numpy as np
import soundfile as sf
from kokoro import KPipeline


class MoviePySubtitleExtractor:
    """
    DEPRECATED: Use api.library.generate_video_from_text() instead.
    
    This class is deprecated and will be removed in a future version.
    It has been replaced by a modular architecture with better separation
    of concerns and improved testability.
    
    Legacy class that extracts high-quality audio and a hierarchical JSON
    subtitle structure from Kokoro TTS for use with subtitle effects in MoviePy.
    
    See module docstring for migration guide.
    """
    def __init__(self, text, lang_code='a', voice='af_heart', speed=1.0):
        warnings.warn(
            "MoviePySubtitleExtractor is deprecated and will be removed in a future version. "
            "Please use api.library.generate_video_from_text() instead. "
            "See the module docstring for a complete migration guide.",
            DeprecationWarning,
            stacklevel=2
        )
        self.pipeline = KPipeline(lang_code=lang_code)
        
        # Split text into paragraphs
        paragraphs = re.split(r'\n+', text.strip())
        
        audio_segments = []
        self.moviepy_data = [] # Stores hierarchical subtitle data
        self.paragraph_segments = [] # Legacy format for SRT export if needed
        
        for paragraph_idx, paragraph in enumerate(paragraphs):
            generator = self.pipeline(
                paragraph, voice=voice, speed=speed
            )
            
            paragraph_audio = []
            raw_tokens = []
            
            for i, result in enumerate(generator):
                paragraph_audio.append(result.audio.cpu().numpy())
                raw_tokens.extend(result.tokens)
                
            time_offset = sum(len(seg) for seg in audio_segments) / 24000 if audio_segments else 0
            
            # 1. Merge Punctuation Tokens
            merged_words = self._merge_punctuation(raw_tokens, time_offset)
            
            # 2. Group into Sentences
            sentences = self._group_into_sentences(merged_words)
            self.moviepy_data.extend(sentences)
            
            # 3. Store for legacy SRT formats
            self.paragraph_segments.append({
                "paragraph_idx": paragraph_idx,
                "text": paragraph,
                "word_segments": merged_words,
                "time_offset": 0 # Offset already applied in merged_words
            })
            
            if paragraph_audio:
                audio_segments.append(np.concatenate(paragraph_audio))
        
        if audio_segments:
            self.audio = np.concatenate(audio_segments)
        else:
            self.audio = np.array([])
            
    def _merge_punctuation(self, tokens, time_offset):
        """
        Merges standalone punctuation and tiny whitespace tokens into the 
        preceding valid word token so MoviePy doesn't highlight them separately.
        """
        merged_words = []
        
        for t in tokens:
            text_content = t.text.strip()
            # Check if token is just punctuation or extremely short without alphanumeric characters
            is_punctuation = not bool(re.search(r'[a-zA-Z0-9]', text_content))
            
            # If it's the very first token, we can't merge it backwards, so just keep it.
            if is_punctuation and merged_words:
                # Append to the previous word
                merged_words[-1]["text"] += t.text + t.whitespace
            else:
                # It's a valid word (or the first token)
                merged_words.append({
                    "text": t.text + t.whitespace,
                    "clean_word": text_content, # Useful for processing without spaces
                    "start_time": t.start_ts + time_offset,
                    "end_time": t.end_ts + time_offset
                })
                
        return merged_words

    def _group_into_sentences(self, merged_words, max_duration=5.0):
        """Groups merged words into a hierarchical sentence structure."""
        sentences = []
        
        if not merged_words:
            return sentences
            
        current_sentence_words = []
        start_time = merged_words[0]["start_time"]
        
        for i, word in enumerate(merged_words):
            current_sentence_words.append(word)
            current_end_time = word["end_time"]
            
            # Check if sentence ends (., ?, !) or duration limit reached
            is_sentence_end = re.search(r'[.!?](\s+)?$', word["text"])
            is_duration_exceeded = (current_end_time - start_time) >= max_duration
            is_last_word = (i == len(merged_words) - 1)
            
            if is_sentence_end or is_duration_exceeded or is_last_word:
                # Compile full sentence text
                full_text = "".join(w["text"] for w in current_sentence_words).strip()
                
                if full_text: # Only add if we actually have text
                    sentences.append({
                        "sentence_text": full_text,
                        "start_time": start_time,
                        "end_time": current_end_time,
                        "words": current_sentence_words
                    })
                
                # Reset for next sentence
                current_sentence_words = []
                if not is_last_word:
                    start_time = merged_words[i+1]["start_time"]
                    
        return sentences

    def export_moviepy_json(self, json_file):
        """
        DEPRECATED: Use api.library.generate_video_from_text() instead.
        
        Exports the hierarchical subtitle data to a JSON file.
        """
        warnings.warn(
            "export_moviepy_json() is deprecated. Use api.library.generate_video_from_text() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.moviepy_data, f, indent=4, ensure_ascii=False)
        print(f"Exported JSON metadata for MoviePy to {json_file}")

    def get_audio(self, audio_file):
        """
        DEPRECATED: Use api.library.generate_video_from_text() instead.
        
        Saves the generated audio.
        """
        warnings.warn(
            "get_audio() is deprecated. Use api.library.generate_video_from_text() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        sf.write(audio_file, self.audio, 24000)
        print(f"Exported audio to {audio_file}")

    # --- Legacy Methods below for completeness ---
    
    def convert_to_subtitle_timestamp(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

    def get_word_level_subtitles(self, subtitle_file):
        idx_counter = 1
        with open(subtitle_file, "w", encoding="utf-8") as f:
            for paragraph in self.paragraph_segments:
                for word in paragraph["word_segments"]:
                    f.write(f"{idx_counter}\n")
                    f.write(f"{self.convert_to_subtitle_timestamp(word['start_time'])} --> {self.convert_to_subtitle_timestamp(word['end_time'])}\n")
                    f.write(f"{word['text'].strip()}\n\n")
                    idx_counter += 1
        print(f"Exported legacy word-level SRT to {subtitle_file}")


