"""
Pipeline orchestrator for TTS generation and text processing.

This module provides the TTSPipeline class that coordinates the complete
pipeline from text input through TTS generation, text processing, and
output writing using dependency injection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from tts.interfaces import ITTSEngine
    from processing.punctuation import PunctuationMerger
    from processing.grouping import SentenceGrouper
    from io_adapters.interfaces import IAudioWriter, IMetadataWriter
    from processing.models import SentenceSegment


class TTSPipeline:
    """
    Orchestrates the TTS generation and text processing pipeline.
    
    This class coordinates the complete pipeline flow:
    1. Generate TTS audio and tokens from input text
    2. Merge punctuation into adjacent words
    3. Group words into sentence segments
    4. Write audio and metadata outputs
    
    All dependencies are injected through the constructor, following the
    Dependency Inversion Principle. This enables testing with mock
    implementations and allows swapping components without modifying
    the pipeline logic.
    
    Attributes:
        _tts_engine: TTS engine for generating speech and tokens
        _punctuation_merger: Component for merging punctuation tokens
        _sentence_grouper: Component for grouping words into sentences
        _audio_writer: Writer for audio output
        _metadata_writer: Writer for subtitle metadata
    """
    
    def __init__(
        self,
        tts_engine: ITTSEngine,
        punctuation_merger: PunctuationMerger,
        sentence_grouper: SentenceGrouper,
        audio_writer: IAudioWriter,
        metadata_writer: IMetadataWriter
    ):
        """
        Initialize the TTS pipeline with all component dependencies.
        
        Args:
            tts_engine: TTS engine implementing ITTSEngine interface
            punctuation_merger: Component for merging punctuation tokens
            sentence_grouper: Component for grouping words into sentences
            audio_writer: Writer implementing IAudioWriter interface
            metadata_writer: Writer implementing IMetadataWriter interface
        """
        self._tts_engine = tts_engine
        self._punctuation_merger = punctuation_merger
        self._sentence_grouper = sentence_grouper
        self._audio_writer = audio_writer
        self._metadata_writer = metadata_writer
    
    def process(self, text: str) -> List[SentenceSegment]:
        """
        Process text through the complete TTS pipeline.
        
        Executes the full pipeline flow:
        1. Generates TTS audio and word-level tokens
        2. Merges punctuation into adjacent words
        3. Groups words into sentence segments
        4. Writes audio and metadata to configured outputs
        
        Args:
            text: Input text to process
            
        Returns:
            List of sentence segments with word-level timing data
            
        Raises:
            Exception: If any pipeline stage fails (TTS generation,
                      processing, or output writing)
        """
        # Stage 1: Generate TTS audio and tokens
        tts_result = self._tts_engine.generate(text)
        
        # Stage 2: Merge punctuation into adjacent words
        words = self._punctuation_merger.merge(tts_result.tokens)
        
        # Stage 3: Group words into sentence segments
        sentences = self._sentence_grouper.group(words)
        
        # Stage 4: Write outputs
        self._audio_writer.write(tts_result.audio, tts_result.sample_rate)
        self._metadata_writer.write(sentences)
        
        return sentences
