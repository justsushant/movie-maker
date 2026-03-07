"""Unit tests for I/O implementations.

**Validates: Requirements 6.5**

Tests all concrete implementations of I/O interfaces:
- FileTextReader and StringTextReader
- FileAudioWriter and InMemoryAudioWriter
- JsonMetadataWriter and InMemoryMetadataWriter
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest

from io_adapters.implementations import (
    FileTextReader,
    StringTextReader,
    FileAudioWriter,
    InMemoryAudioWriter,
    JsonMetadataWriter,
    InMemoryMetadataWriter,
)
from processing.models import WordToken, SentenceSegment

if TYPE_CHECKING:
    pass


class TestFileTextReader:
    """Tests for FileTextReader."""
    
    def test_read_simple_text(self, tmp_path: Path):
        """Test reading a simple text file."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_content = "Hello, world!"
        test_file.write_text(test_content, encoding='utf-8')
        
        # Read it back
        reader = FileTextReader(test_file)
        result = reader.read()
        
        assert result == test_content
    
    def test_read_multiline_text(self, tmp_path: Path):
        """Test reading a multiline text file."""
        test_file = tmp_path / "multiline.txt"
        test_content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(test_content, encoding='utf-8')
        
        reader = FileTextReader(test_file)
        result = reader.read()
        
        assert result == test_content
        assert result.count('\n') == 2
    
    def test_read_unicode_text(self, tmp_path: Path):
        """Test reading text with Unicode characters."""
        test_file = tmp_path / "unicode.txt"
        test_content = "Hello 世界! 🎉"
        test_file.write_text(test_content, encoding='utf-8')
        
        reader = FileTextReader(test_file)
        result = reader.read()
        
        assert result == test_content
    
    def test_read_empty_file(self, tmp_path: Path):
        """Test reading an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding='utf-8')
        
        reader = FileTextReader(test_file)
        result = reader.read()
        
        assert result == ""
    
    def test_read_nonexistent_file(self, tmp_path: Path):
        """Test reading a file that doesn't exist."""
        test_file = tmp_path / "nonexistent.txt"
        
        reader = FileTextReader(test_file)
        
        with pytest.raises(FileNotFoundError):
            reader.read()


class TestStringTextReader:
    """Tests for StringTextReader."""
    
    def test_read_simple_string(self):
        """Test reading a simple string."""
        test_text = "Hello, world!"
        reader = StringTextReader(test_text)
        
        result = reader.read()
        
        assert result == test_text
    
    def test_read_multiline_string(self):
        """Test reading a multiline string."""
        test_text = "Line 1\nLine 2\nLine 3"
        reader = StringTextReader(test_text)
        
        result = reader.read()
        
        assert result == test_text
    
    def test_read_empty_string(self):
        """Test reading an empty string."""
        reader = StringTextReader("")
        
        result = reader.read()
        
        assert result == ""
    
    def test_read_unicode_string(self):
        """Test reading a string with Unicode characters."""
        test_text = "Hello 世界! 🎉"
        reader = StringTextReader(test_text)
        
        result = reader.read()
        
        assert result == test_text
    
    def test_read_multiple_times(self):
        """Test that reading multiple times returns the same result."""
        test_text = "Consistent text"
        reader = StringTextReader(test_text)
        
        result1 = reader.read()
        result2 = reader.read()
        
        assert result1 == result2 == test_text


class TestFileAudioWriter:
    """Tests for FileAudioWriter."""
    
    def test_write_simple_audio(self, tmp_path: Path):
        """Test writing simple audio data."""
        output_file = tmp_path / "test.wav"
        
        # Create test audio data
        sample_rate = 24000
        duration = 1.0  # 1 second
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
        
        # Write audio
        writer = FileAudioWriter(output_file)
        writer.write(audio, sample_rate)
        
        # Verify file exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0
    
    def test_write_audio_format(self, tmp_path: Path):
        """Test that written audio can be read back correctly."""
        import soundfile as sf
        
        output_file = tmp_path / "test.wav"
        
        # Create test audio data
        sample_rate = 24000
        audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        
        # Write audio
        writer = FileAudioWriter(output_file)
        writer.write(audio, sample_rate)
        
        # Read back and verify
        read_audio, read_sr = sf.read(str(output_file))
        
        assert read_sr == sample_rate
        # Use decimal=4 for tolerance due to WAV encoding/decoding precision
        np.testing.assert_array_almost_equal(read_audio, audio, decimal=4)
    
    def test_write_empty_audio(self, tmp_path: Path):
        """Test writing empty audio array."""
        output_file = tmp_path / "empty.wav"
        
        audio = np.array([], dtype=np.float32)
        sample_rate = 24000
        
        writer = FileAudioWriter(output_file)
        writer.write(audio, sample_rate)
        
        assert output_file.exists()
    
    def test_write_different_sample_rates(self, tmp_path: Path):
        """Test writing audio with different sample rates."""
        import soundfile as sf
        
        for sample_rate in [16000, 24000, 44100, 48000]:
            output_file = tmp_path / f"test_{sample_rate}.wav"
            audio = np.array([0.1, 0.2, 0.3], dtype=np.float32)
            
            writer = FileAudioWriter(output_file)
            writer.write(audio, sample_rate)
            
            # Verify sample rate
            _, read_sr = sf.read(str(output_file))
            assert read_sr == sample_rate


class TestInMemoryAudioWriter:
    """Tests for InMemoryAudioWriter."""
    
    def test_write_stores_audio(self):
        """Test that audio is stored in memory."""
        audio = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)
        sample_rate = 24000
        
        writer = InMemoryAudioWriter()
        writer.write(audio, sample_rate)
        
        assert writer.audio is not None
        assert writer.sample_rate == sample_rate
        np.testing.assert_array_equal(writer.audio, audio)
    
    def test_write_empty_audio(self):
        """Test storing empty audio array."""
        audio = np.array([], dtype=np.float32)
        sample_rate = 24000
        
        writer = InMemoryAudioWriter()
        writer.write(audio, sample_rate)
        
        assert writer.audio is not None
        assert writer.sample_rate == sample_rate
        assert len(writer.audio) == 0
    
    def test_initial_state(self):
        """Test that writer starts with None values."""
        writer = InMemoryAudioWriter()
        
        assert writer.audio is None
        assert writer.sample_rate is None
    
    def test_overwrite_audio(self):
        """Test that writing again overwrites previous data."""
        writer = InMemoryAudioWriter()
        
        # Write first audio
        audio1 = np.array([0.1, 0.2], dtype=np.float32)
        writer.write(audio1, 24000)
        
        # Write second audio
        audio2 = np.array([0.5, 0.6, 0.7], dtype=np.float32)
        writer.write(audio2, 48000)
        
        # Verify second audio is stored
        assert writer.sample_rate == 48000
        np.testing.assert_array_equal(writer.audio, audio2)


class TestJsonMetadataWriter:
    """Tests for JsonMetadataWriter."""
    
    def test_write_single_sentence(self, tmp_path: Path):
        """Test writing a single sentence segment."""
        output_file = tmp_path / "test.json"
        
        # Create test data
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
            WordToken(text="world! ", clean_word="world!", start_time=0.5, end_time=1.0),
        ]
        segments = [
            SentenceSegment(
                sentence_text="Hello world!",
                start_time=0.0,
                end_time=1.0,
                words=words
            )
        ]
        
        # Write metadata
        writer = JsonMetadataWriter(output_file)
        writer.write(segments)
        
        # Verify file exists and read back
        assert output_file.exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["sentence_text"] == "Hello world!"
        assert data[0]["start_time"] == 0.0
        assert data[0]["end_time"] == 1.0
        assert len(data[0]["words"]) == 2
    
    def test_write_multiple_sentences(self, tmp_path: Path):
        """Test writing multiple sentence segments."""
        output_file = tmp_path / "multi.json"
        
        # Create test data
        segments = [
            SentenceSegment(
                sentence_text="First sentence.",
                start_time=0.0,
                end_time=1.0,
                words=[
                    WordToken(text="First ", clean_word="First", start_time=0.0, end_time=0.5),
                    WordToken(text="sentence. ", clean_word="sentence.", start_time=0.5, end_time=1.0),
                ]
            ),
            SentenceSegment(
                sentence_text="Second sentence.",
                start_time=1.0,
                end_time=2.0,
                words=[
                    WordToken(text="Second ", clean_word="Second", start_time=1.0, end_time=1.5),
                    WordToken(text="sentence. ", clean_word="sentence.", start_time=1.5, end_time=2.0),
                ]
            ),
        ]
        
        # Write metadata
        writer = JsonMetadataWriter(output_file)
        writer.write(segments)
        
        # Read back and verify
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data) == 2
        assert data[0]["sentence_text"] == "First sentence."
        assert data[1]["sentence_text"] == "Second sentence."
    
    def test_write_json_structure(self, tmp_path: Path):
        """Test that JSON structure matches expected format."""
        output_file = tmp_path / "structure.json"
        
        words = [
            WordToken(text="Test ", clean_word="Test", start_time=0.0, end_time=0.5),
        ]
        segments = [
            SentenceSegment(
                sentence_text="Test",
                start_time=0.0,
                end_time=0.5,
                words=words
            )
        ]
        
        writer = JsonMetadataWriter(output_file)
        writer.write(segments)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify structure
        assert isinstance(data, list)
        assert "sentence_text" in data[0]
        assert "start_time" in data[0]
        assert "end_time" in data[0]
        assert "words" in data[0]
        assert isinstance(data[0]["words"], list)
        assert "text" in data[0]["words"][0]
        assert "clean_word" in data[0]["words"][0]
        assert "start_time" in data[0]["words"][0]
        assert "end_time" in data[0]["words"][0]
    
    def test_write_empty_segments(self, tmp_path: Path):
        """Test writing empty segments list."""
        output_file = tmp_path / "empty.json"
        
        writer = JsonMetadataWriter(output_file)
        writer.write([])
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data == []
    
    def test_write_unicode_content(self, tmp_path: Path):
        """Test writing content with Unicode characters."""
        output_file = tmp_path / "unicode.json"
        
        words = [
            WordToken(text="世界 ", clean_word="世界", start_time=0.0, end_time=0.5),
        ]
        segments = [
            SentenceSegment(
                sentence_text="世界",
                start_time=0.0,
                end_time=0.5,
                words=words
            )
        ]
        
        writer = JsonMetadataWriter(output_file)
        writer.write(segments)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data[0]["sentence_text"] == "世界"
        assert data[0]["words"][0]["text"] == "世界 "


class TestInMemoryMetadataWriter:
    """Tests for InMemoryMetadataWriter."""
    
    def test_write_stores_segments(self):
        """Test that segments are stored in memory."""
        words = [
            WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
        ]
        segments = [
            SentenceSegment(
                sentence_text="Hello",
                start_time=0.0,
                end_time=0.5,
                words=words
            )
        ]
        
        writer = InMemoryMetadataWriter()
        writer.write(segments)
        
        assert len(writer.segments) == 1
        assert writer.segments[0].sentence_text == "Hello"
        assert writer.segments[0].start_time == 0.0
        assert writer.segments[0].end_time == 0.5
        assert len(writer.segments[0].words) == 1
    
    def test_write_multiple_segments(self):
        """Test storing multiple segments."""
        segments = [
            SentenceSegment(
                sentence_text="First",
                start_time=0.0,
                end_time=1.0,
                words=[WordToken(text="First ", clean_word="First", start_time=0.0, end_time=1.0)]
            ),
            SentenceSegment(
                sentence_text="Second",
                start_time=1.0,
                end_time=2.0,
                words=[WordToken(text="Second ", clean_word="Second", start_time=1.0, end_time=2.0)]
            ),
        ]
        
        writer = InMemoryMetadataWriter()
        writer.write(segments)
        
        assert len(writer.segments) == 2
        assert writer.segments[0].sentence_text == "First"
        assert writer.segments[1].sentence_text == "Second"
    
    def test_initial_state(self):
        """Test that writer starts with empty list."""
        writer = InMemoryMetadataWriter()
        
        assert writer.segments == []
    
    def test_overwrite_segments(self):
        """Test that writing again overwrites previous data."""
        writer = InMemoryMetadataWriter()
        
        # Write first segments
        segments1 = [
            SentenceSegment(
                sentence_text="First",
                start_time=0.0,
                end_time=1.0,
                words=[]
            )
        ]
        writer.write(segments1)
        
        # Write second segments
        segments2 = [
            SentenceSegment(
                sentence_text="Second",
                start_time=1.0,
                end_time=2.0,
                words=[]
            ),
            SentenceSegment(
                sentence_text="Third",
                start_time=2.0,
                end_time=3.0,
                words=[]
            ),
        ]
        writer.write(segments2)
        
        # Verify second segments are stored
        assert len(writer.segments) == 2
        assert writer.segments[0].sentence_text == "Second"
        assert writer.segments[1].sentence_text == "Third"
    
    def test_write_empty_segments(self):
        """Test storing empty segments list."""
        writer = InMemoryMetadataWriter()
        writer.write([])
        
        assert writer.segments == []
