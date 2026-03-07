"""
Debug script to investigate timestamp reset issue in subtitle JSON.

This script analyzes the subtitle JSON files from test outputs to identify
where timestamps are resetting and why.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

def analyze_subtitle_json(json_path: Path) -> None:
    """Analyze a subtitle JSON file for timestamp issues."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {json_path}")
    print(f"{'='*80}\n")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    print(f"Total segments: {len(segments)}\n")
    
    prev_end_time = None
    issues_found = []
    
    for i, segment in enumerate(segments):
        start_time = segment['start_time']
        end_time = segment['end_time']
        sentence_text = segment['sentence_text'][:60] + "..." if len(segment['sentence_text']) > 60 else segment['sentence_text']
        
        # Check for timestamp reset
        if prev_end_time is not None:
            gap = start_time - prev_end_time
            
            if start_time < prev_end_time:
                # Timestamp went backwards!
                issues_found.append({
                    'type': 'RESET',
                    'segment_idx': i,
                    'prev_end': prev_end_time,
                    'curr_start': start_time,
                    'text': sentence_text
                })
                print(f"🔴 TIMESTAMP RESET at segment {i}:")
                print(f"   Previous segment ended at: {prev_end_time:.3f}s")
                print(f"   Current segment starts at: {start_time:.3f}s")
                print(f"   Text: {sentence_text}")
                print()
            elif gap > 1.0:
                # Large gap
                issues_found.append({
                    'type': 'LARGE_GAP',
                    'segment_idx': i,
                    'gap': gap,
                    'text': sentence_text
                })
                print(f"⚠️  LARGE GAP ({gap:.3f}s) before segment {i}:")
                print(f"   Text: {sentence_text}")
                print()
        
        prev_end_time = end_time
    
    if not issues_found:
        print("✅ No timestamp issues found!")
    else:
        print(f"\n{'='*80}")
        print(f"Summary: Found {len(issues_found)} issues")
        resets = sum(1 for issue in issues_found if issue['type'] == 'RESET')
        gaps = sum(1 for issue in issues_found if issue['type'] == 'LARGE_GAP')
        print(f"  - Timestamp resets: {resets}")
        print(f"  - Large gaps: {gaps}")
        print(f"{'='*80}")


def main():
    """Analyze all real-world scenario test outputs."""
    test_output_dir = Path("output/test/test_real_world_scenarios")
    
    if not test_output_dir.exists():
        print(f"Error: Test output directory not found: {test_output_dir}")
        sys.exit(1)
    
    # Find all subtitle JSON files
    json_files = list(test_output_dir.glob("*/output_moviepy.json"))
    
    if not json_files:
        print(f"Error: No subtitle JSON files found in {test_output_dir}")
        sys.exit(1)
    
    print(f"Found {len(json_files)} subtitle JSON files to analyze")
    
    for json_file in sorted(json_files):
        analyze_subtitle_json(json_file)


if __name__ == "__main__":
    main()
