"""
Debug script to check audio file durations and compare with subtitle timestamps.
"""

from __future__ import annotations

import json
import soundfile as sf
from pathlib import Path


def analyze_audio_and_subtitles(test_dir: Path) -> None:
    """Analyze audio duration vs subtitle timestamps."""
    json_file = test_dir / "output_moviepy.json"
    audio_file = test_dir / "output_moviepy.wav"
    
    if not json_file.exists() or not audio_file.exists():
        print(f"Skipping {test_dir.name}: missing files")
        return
    
    # Read audio duration
    audio_data, sample_rate = sf.read(audio_file)
    audio_duration = len(audio_data) / sample_rate
    
    # Read subtitle data
    with open(json_file, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    # Find max timestamp in subtitles
    max_subtitle_time = max(seg['end_time'] for seg in segments)
    
    # Find where reset happens
    reset_at = None
    for i in range(1, len(segments)):
        if segments[i]['start_time'] < segments[i-1]['end_time']:
            reset_at = i
            break
    
    print(f"\n{test_dir.name}:")
    print(f"  Audio duration: {audio_duration:.2f}s")
    print(f"  Max subtitle timestamp: {max_subtitle_time:.2f}s")
    print(f"  Timestamp reset at segment: {reset_at}")
    print(f"  Last segment before reset ends at: {segments[reset_at-1]['end_time']:.2f}s" if reset_at else "  No reset")


def main():
    """Analyze all test outputs."""
    test_output_dir = Path("output/test/test_real_world_scenarios")
    
    for test_dir in sorted(test_output_dir.iterdir()):
        if test_dir.is_dir():
            analyze_audio_and_subtitles(test_dir)


if __name__ == "__main__":
    main()
