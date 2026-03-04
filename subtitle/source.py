"""Subtitle source implementations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from subtitle.interfaces import SubtitleSegment, WordSegment


class JsonSubtitleSource:
    """Reads subtitle segments from the moviepy hierarchical JSON file."""

    def __init__(self, json_path: str | Path) -> None:
        self._path = Path(json_path)
        self._segments: List[SubtitleSegment] | None = None

    def _load(self) -> List[SubtitleSegment]:
        if self._segments is not None:
            return self._segments
        with open(self._path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._segments = []
        for s in data:
            words = [
                WordSegment(
                    text=w["text"],
                    start_time=float(w["start_time"]),
                    end_time=float(w["end_time"]),
                )
                for w in s.get("words", [])
            ]
            self._segments.append(
                SubtitleSegment(
                    sentence_text=s["sentence_text"],
                    start_time=float(s["start_time"]),
                    end_time=float(s["end_time"]),
                    words=words,
                )
            )
        return self._segments

    def get_segments_for_time(self, t: float) -> List[SubtitleSegment]:
        segments = self._load()
        out = []
        for seg in segments:
            if seg.start_time <= t <= seg.end_time:
                out.append(seg)
        return out

    def get_all_segments(self) -> List[SubtitleSegment]:
        return self._load()
