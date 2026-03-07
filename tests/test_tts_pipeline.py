"""
Unit tests for TTSPipeline.

**Validates: Requirements 6.6**

Tests the complete TTS pipeline orchestration using mock implementations
of all dependencies. Verifies correct method calls, data flow, error handling,
and integration between components.
"""

from __future__ import annotations

from typing import List
from unittest.mock import Mock, call

import numpy as np
import pytest

from pipeline.orchestrator import TTSPipeline
from tts.interfaces import ITTSEngine, TTSResult, TTSToken
from processing.punctuation import PunctuationMerger
from processing.grouping import SentenceGrouper
from processing.models import WordToken, SentenceSegment
from io_adapters.interfaces import IAudioWriter, IMetadataWriter


class MockTTSEngine(ITTSEngine):
    """Mock TTS engine for testing."""
    
    def __init__(self):
        self.generate_called = False
        self.last_text = None
        self.result_to_return = None
    
    def generate(self, text: str) -> TTSResult:
        """Mock generate method."""
        self.generate_called = True
        self.last_text = text
        
        if self.result_to_return is None:
            # Default mock result
            return TTSResult(
                audio=np.array([0.1, 0.2, 0.3]),
                sample_rate=24000,
                tokens=[
                    TTSToken(text="Hello", whitespace=" ", start_ts=0.0, end_ts=0.5),
                    TTSToken(text="world", whitespace="", start_ts=0.5, end_ts=1.0),
                    TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.1),
                ]
            )
        
        return self.result_to_return


class MockPunctuationMerger:
    """Mock punctuation merger for testing."""
    
    def __init__(self):
        self.merge_called = False
        self.last_tokens = None
        self.words_to_return = None
    
    def merge(self, tokens: List[TTSToken]) -> List[WordToken]:
        """Mock merge method."""
        self.merge_called = True
        self.last_tokens = tokens
        
        if self.words_to_return is None:
            # Default mock result - merge punctuation
            return [
                WordToken(text="Hello ", clean_word="Hello", start_time=0.0, end_time=0.5),
                WordToken(text="world. ", clean_word="world", start_time=0.5, end_time=1.0),
            ]
        
        return self.words_to_return


class MockSentenceGrouper:
    """Mock sentence grouper for testing."""
    
    def __init__(self):
        self.group_called = False
        self.last_words = None
        self.sentences_to_return = None
    
    def group(self, words: List[WordToken]) -> List[SentenceSegment]:
        """Mock group method."""
        self.group_called = True
        self.last_words = words
        
        if self.sentences_to_return is None:
            # Default mock result - group into one sentence
            return [
                SentenceSegment(
                    sentence_text="Hello world.",
                    start_time=0.0,
                    end_time=1.0,
                    words=words
                )
            ]
        
        return self.sentences_to_return


class MockAudioWriter(IAudioWriter):
    """Mock audio writer for testing."""
    
    def __init__(self):
        self.write_called = False
        self.last_audio = None
        self.last_sample_rate = None
    
    def write(self, audio: np.ndarray, sample_rate: int) -> None:
        """Mock write method."""
        self.write_called = True
        self.last_audio = audio
        self.last_sample_rate = sample_rate


class MockMetadataWriter(IMetadataWriter):
    """Mock metadata writer for testing."""
    
    def __init__(self):
        self.write_called = False
        self.last_segments = None
    
    def write(self, segments: List[SentenceSegment]) -> None:
        """Mock write method."""
        self.write_called = True
        self.last_segments = segments


class TestTTSPipelineInitialization:
    """Test TTSPipeline initialization."""
    
    def test_initialization_with_all_dependencies(self):
        """Test that TTSPipeline initializes with all required dependencies."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        assert pipeline._tts_engine is tts_engine
        assert pipeline._punctuation_merger is punctuation_merger
        assert pipeline._sentence_grouper is sentence_grouper
        assert pipeline._audio_writer is audio_writer
        assert pipeline._metadata_writer is metadata_writer


class TestTTSPipelineCompleteFlow:
    """Test complete pipeline flow from text to output."""
    
    def test_process_calls_all_components_in_order(self):
        """Test that process() calls all components in the correct order."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        text = "Hello world."
        result = pipeline.process(text)
        
        # Verify all components were called
        assert tts_engine.generate_called
        assert punctuation_merger.merge_called
        assert sentence_grouper.group_called
        assert audio_writer.write_called
        assert metadata_writer.write_called
        
        # Verify correct input was passed to TTS engine
        assert tts_engine.last_text == text
        
        # Verify result is returned
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], SentenceSegment)
    
    def test_process_passes_data_between_components(self):
        """Test that data flows correctly between pipeline components."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("Test text.")
        
        # Verify TTS tokens were passed to punctuation merger
        assert punctuation_merger.last_tokens is not None
        assert len(punctuation_merger.last_tokens) == 3
        assert punctuation_merger.last_tokens[0].text == "Hello"
        
        # Verify words were passed to sentence grouper
        assert sentence_grouper.last_words is not None
        assert len(sentence_grouper.last_words) == 2
        assert sentence_grouper.last_words[0].text == "Hello "
        
        # Verify audio was written
        assert audio_writer.last_audio is not None
        assert np.array_equal(audio_writer.last_audio, np.array([0.1, 0.2, 0.3]))
        assert audio_writer.last_sample_rate == 24000
        
        # Verify metadata was written
        assert metadata_writer.last_segments is not None
        assert len(metadata_writer.last_segments) == 1
        assert metadata_writer.last_segments[0].sentence_text == "Hello world."
    
    def test_process_returns_sentence_segments(self):
        """Test that process() returns the sentence segments from grouper."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        # Set up custom return value
        expected_segments = [
            SentenceSegment(
                sentence_text="First sentence.",
                start_time=0.0,
                end_time=1.0,
                words=[]
            ),
            SentenceSegment(
                sentence_text="Second sentence.",
                start_time=1.0,
                end_time=2.0,
                words=[]
            )
        ]
        sentence_grouper.sentences_to_return = expected_segments
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("Test text.")
        
        assert result == expected_segments
        assert len(result) == 2
        assert result[0].sentence_text == "First sentence."
        assert result[1].sentence_text == "Second sentence."


class TestTTSPipelineWithRealComponents:
    """Test pipeline with real component implementations."""
    
    def test_process_with_real_punctuation_merger(self):
        """Test pipeline with real PunctuationMerger."""
        tts_engine = MockTTSEngine()
        punctuation_merger = PunctuationMerger()  # Real implementation
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("Test text.")
        
        # Verify punctuation was merged correctly
        assert sentence_grouper.last_words is not None
        assert len(sentence_grouper.last_words) == 2
        assert sentence_grouper.last_words[0].text == "Hello "
        assert sentence_grouper.last_words[1].text == "world. "
    
    def test_process_with_real_sentence_grouper(self):
        """Test pipeline with real SentenceGrouper."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = SentenceGrouper()  # Real implementation
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("Test text.")
        
        # Verify sentence was grouped correctly
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world."
        assert len(result[0].words) == 2


class TestTTSPipelineEmptyInput:
    """Test pipeline behavior with empty input."""
    
    def test_process_empty_text(self):
        """Test processing empty text."""
        tts_engine = MockTTSEngine()
        tts_engine.result_to_return = TTSResult(
            audio=np.array([]),
            sample_rate=24000,
            tokens=[]
        )
        
        punctuation_merger = MockPunctuationMerger()
        punctuation_merger.words_to_return = []
        
        sentence_grouper = MockSentenceGrouper()
        sentence_grouper.sentences_to_return = []
        
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("")
        
        # Verify all components were still called
        assert tts_engine.generate_called
        assert punctuation_merger.merge_called
        assert sentence_grouper.group_called
        assert audio_writer.write_called
        assert metadata_writer.write_called
        
        # Verify empty result
        assert result == []
        assert len(result) == 0


class TestTTSPipelineMultipleSentences:
    """Test pipeline with multiple sentences."""
    
    def test_process_multiple_sentences(self):
        """Test processing text with multiple sentences."""
        tts_engine = MockTTSEngine()
        tts_engine.result_to_return = TTSResult(
            audio=np.array([0.1, 0.2, 0.3, 0.4, 0.5]),
            sample_rate=24000,
            tokens=[
                TTSToken(text="First", whitespace=" ", start_ts=0.0, end_ts=0.5),
                TTSToken(text="sentence", whitespace="", start_ts=0.5, end_ts=1.0),
                TTSToken(text=".", whitespace=" ", start_ts=1.0, end_ts=1.1),
                TTSToken(text="Second", whitespace=" ", start_ts=1.1, end_ts=1.6),
                TTSToken(text="one", whitespace="", start_ts=1.6, end_ts=2.0),
                TTSToken(text=".", whitespace=" ", start_ts=2.0, end_ts=2.1),
            ]
        )
        
        punctuation_merger = MockPunctuationMerger()
        punctuation_merger.words_to_return = [
            WordToken(text="First ", clean_word="First", start_time=0.0, end_time=0.5),
            WordToken(text="sentence. ", clean_word="sentence", start_time=0.5, end_time=1.0),
            WordToken(text="Second ", clean_word="Second", start_time=1.1, end_time=1.6),
            WordToken(text="one. ", clean_word="one", start_time=1.6, end_time=2.0),
        ]
        
        sentence_grouper = MockSentenceGrouper()
        sentence_grouper.sentences_to_return = [
            SentenceSegment(
                sentence_text="First sentence.",
                start_time=0.0,
                end_time=1.0,
                words=punctuation_merger.words_to_return[:2]
            ),
            SentenceSegment(
                sentence_text="Second one.",
                start_time=1.1,
                end_time=2.0,
                words=punctuation_merger.words_to_return[2:]
            )
        ]
        
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("First sentence. Second one.")
        
        # Verify multiple sentences were processed
        assert len(result) == 2
        assert result[0].sentence_text == "First sentence."
        assert result[1].sentence_text == "Second one."
        
        # Verify metadata writer received both sentences
        assert len(metadata_writer.last_segments) == 2


class TestTTSPipelineErrorHandling:
    """Test pipeline error handling."""
    
    def test_process_handles_tts_engine_error(self):
        """Test that TTS engine errors propagate correctly."""
        tts_engine = Mock(spec=ITTSEngine)
        tts_engine.generate.side_effect = RuntimeError("TTS generation failed")
        
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        with pytest.raises(RuntimeError, match="TTS generation failed"):
            pipeline.process("Test text.")
        
        # Verify downstream components were not called
        assert not punctuation_merger.merge_called
        assert not sentence_grouper.group_called
        assert not audio_writer.write_called
        assert not metadata_writer.write_called
    
    def test_process_handles_audio_writer_error(self):
        """Test that audio writer errors propagate correctly."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        
        audio_writer = Mock(spec=IAudioWriter)
        audio_writer.write.side_effect = IOError("Failed to write audio")
        
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        with pytest.raises(IOError, match="Failed to write audio"):
            pipeline.process("Test text.")
        
        # Verify processing happened before the error
        assert tts_engine.generate_called
        assert punctuation_merger.merge_called
        assert sentence_grouper.group_called
        
        # Verify metadata writer was not called (error occurred before)
        assert not metadata_writer.write_called
    
    def test_process_handles_metadata_writer_error(self):
        """Test that metadata writer errors propagate correctly."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        sentence_grouper = MockSentenceGrouper()
        audio_writer = MockAudioWriter()
        
        metadata_writer = Mock(spec=IMetadataWriter)
        metadata_writer.write.side_effect = IOError("Failed to write metadata")
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        with pytest.raises(IOError, match="Failed to write metadata"):
            pipeline.process("Test text.")
        
        # Verify all processing happened before the error
        assert tts_engine.generate_called
        assert punctuation_merger.merge_called
        assert sentence_grouper.group_called
        assert audio_writer.write_called


class TestTTSPipelineMethodCalls:
    """Test that pipeline makes correct method calls on dependencies."""
    
    def test_process_calls_tts_engine_generate_once(self):
        """Test that TTS engine generate() is called exactly once."""
        tts_engine = Mock(spec=ITTSEngine)
        tts_engine.generate.return_value = TTSResult(
            audio=np.array([0.1]),
            sample_rate=24000,
            tokens=[]
        )
        
        punctuation_merger = MockPunctuationMerger()
        punctuation_merger.words_to_return = []
        sentence_grouper = MockSentenceGrouper()
        sentence_grouper.sentences_to_return = []
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        pipeline.process("Test text.")
        
        # Verify generate was called exactly once with correct argument
        tts_engine.generate.assert_called_once_with("Test text.")
    
    def test_process_calls_audio_writer_with_correct_data(self):
        """Test that audio writer is called with correct audio data."""
        tts_engine = MockTTSEngine()
        expected_audio = np.array([0.1, 0.2, 0.3])
        expected_sample_rate = 24000
        tts_engine.result_to_return = TTSResult(
            audio=expected_audio,
            sample_rate=expected_sample_rate,
            tokens=[]
        )
        
        punctuation_merger = MockPunctuationMerger()
        punctuation_merger.words_to_return = []
        sentence_grouper = MockSentenceGrouper()
        sentence_grouper.sentences_to_return = []
        audio_writer = Mock(spec=IAudioWriter)
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        pipeline.process("Test text.")
        
        # Verify audio writer was called with correct data
        audio_writer.write.assert_called_once()
        call_args = audio_writer.write.call_args
        assert np.array_equal(call_args[0][0], expected_audio)
        assert call_args[0][1] == expected_sample_rate
    
    def test_process_calls_metadata_writer_with_correct_segments(self):
        """Test that metadata writer is called with correct segments."""
        tts_engine = MockTTSEngine()
        punctuation_merger = MockPunctuationMerger()
        
        expected_segments = [
            SentenceSegment(
                sentence_text="Test sentence.",
                start_time=0.0,
                end_time=1.0,
                words=[]
            )
        ]
        sentence_grouper = MockSentenceGrouper()
        sentence_grouper.sentences_to_return = expected_segments
        
        audio_writer = MockAudioWriter()
        metadata_writer = Mock(spec=IMetadataWriter)
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        pipeline.process("Test text.")
        
        # Verify metadata writer was called with correct segments
        metadata_writer.write.assert_called_once_with(expected_segments)


class TestTTSPipelineIntegration:
    """Integration tests with real components."""
    
    def test_process_with_all_real_components_except_tts(self):
        """Test pipeline with real processing components and mock TTS."""
        tts_engine = MockTTSEngine()
        tts_engine.result_to_return = TTSResult(
            audio=np.array([0.1, 0.2, 0.3]),
            sample_rate=24000,
            tokens=[
                TTSToken(text="Hello", whitespace=" ", start_ts=0.0, end_ts=0.5),
                TTSToken(text="world", whitespace="", start_ts=0.5, end_ts=1.0),
                TTSToken(text="!", whitespace=" ", start_ts=1.0, end_ts=1.1),
            ]
        )
        
        punctuation_merger = PunctuationMerger()  # Real
        sentence_grouper = SentenceGrouper()  # Real
        audio_writer = MockAudioWriter()
        metadata_writer = MockMetadataWriter()
        
        pipeline = TTSPipeline(
            tts_engine=tts_engine,
            punctuation_merger=punctuation_merger,
            sentence_grouper=sentence_grouper,
            audio_writer=audio_writer,
            metadata_writer=metadata_writer
        )
        
        result = pipeline.process("Hello world!")
        
        # Verify complete processing
        assert len(result) == 1
        assert result[0].sentence_text == "Hello world!"
        assert len(result[0].words) == 2
        assert result[0].words[0].text == "Hello "
        assert result[0].words[1].text == "world! "
        
        # Verify outputs were written
        assert audio_writer.write_called
        assert np.array_equal(audio_writer.last_audio, np.array([0.1, 0.2, 0.3]))
        assert metadata_writer.write_called
        assert len(metadata_writer.last_segments) == 1
