# Integration Test Refactor - Design

## Architecture Overview

The refactored integration test suite consists of two independent test modules with separate fixture directories and output locations:

```
tests/
├── integration/
│   ├── __init__.py
│   ├── test_real_world_scenarios.py      # Tier 1: User-facing validation
│   └── test_technical_boundaries.py       # Tier 2: Algorithm correctness
│
├── fixtures/
│   ├── real_world/                        # Realistic content creator scripts
│   │   ├── educational_explainer.txt
│   │   ├── product_demo.txt
│   │   ├── story_narration.txt
│   │   ├── tutorial_walkthrough.txt
│   │   └── news_announcement.txt
│   │
│   └── technical/                         # Minimal edge case inputs
│       ├── extreme_long_word.txt
│       ├── unicode_stress.txt
│       ├── punctuation_heavy.txt
│       ├── multiline_wrap_test.txt
│       └── single_word.txt
│
└── conftest.py                            # Updated fixtures

output/
├── test_real_world_scenarios/             # Manual review outputs
│   ├── educational_explainer/
│   ├── product_demo/
│   └── ...
└── test_technical_boundaries/             # Automated validation outputs
    ├── unicode_stress/
    ├── edge_clipping_portrait/
    └── ...
```

## Component Design

### 1. Real-World Scenario Tests (`test_real_world_scenarios.py`)

**Purpose**: Validate that the tool produces acceptable output for actual content creator use cases.

**Test Structure**:
```python
def test_educational_explainer(real_world_fixture_dir, real_world_output_dir):
    """
    Test educational content with technical terms and moderate pacing.
    
    Validates:
    - Complete pipeline execution
    - Output files created
    - Basic structure correctness
    
    Manual review required for:
    - Subtitle readability
    - Timing accuracy
    - Visual quality
    """
    input_file = real_world_fixture_dir / "educational_explainer.txt"
    output_dir = real_world_output_dir / "educational_explainer"
    
    # Use sensible config for educational content
    config = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "subtitle": {
            "mode": "sentence_with_word_highlight",
            "vertical_align": "bottom",
            "font_size": 48
        }
    }
    
    # Run pipeline
    run_pipeline(config, input_file, output_dir)
    
    # Basic assertions
    assert (output_dir / "output_video.mp4").exists()
    assert (output_dir / "output_moviepy.json").exists()
    assert (output_dir / "output_moviepy.wav").exists()
    
    # Validate JSON structure
    validate_subtitle_json_structure(output_dir / "output_moviepy.json")
```

**Test Cases** (5-8 total):
1. `test_educational_explainer` - Technical terms, moderate pacing, 1080p landscape
2. `test_product_demo` - Marketing language, calls to action, 1080p landscape
3. `test_story_narration` - Dialogue, emotional variation, 1080p landscape
4. `test_tutorial_walkthrough` - Step-by-step instructions, 720p landscape
5. `test_news_announcement` - Formal language, concise, 1080p landscape
6. `test_social_media_short` (optional) - Brief content, portrait 1080x1920
7. `test_podcast_intro` (optional) - Conversational tone, 720p landscape

**Configuration Strategy**:
- Each test uses ONE config appropriate for that content type
- Configs reflect real-world usage patterns
- No combinatorial testing (mode × resolution)

**Validation Strategy**:
- Automated: Files exist, structure valid, no crashes
- Manual: Developer reviews output videos for quality

### 2. Technical Boundary Tests (`test_technical_boundaries.py`)

**Purpose**: Validate algorithm correctness at edge cases and boundary conditions.

**Test Structure**:
```python
def test_multiline_wrapping_narrow_width(technical_fixture_dir, technical_output_dir):
    """
    Test that long text wraps correctly in narrow layouts.
    
    Validates:
    - SentenceLayout creates multiple lines
    - No horizontal edge clipping
    - Text remains readable
    """
    input_file = technical_fixture_dir / "multiline_wrap_test.txt"
    output_dir = technical_output_dir / "multiline_wrapping"
    
    config = {
        "width": 720,
        "height": 1280,  # Portrait
        "subtitle": {
            "mode": "sentence",
            "multiline_enabled": True,
            "vertical_align": "bottom"
        }
    }
    
    run_pipeline(config, input_file, output_dir)
    
    # Automated assertions
    json_path = output_dir / "output_moviepy.json"
    assert_sentence_layout_wraps(config, json_path, visible_time=0.5)
    assert_no_horizontal_edge_clipping(config, json_path, visible_time=0.5)
```

**Test Cases** (10-15 total):

**Text Wrapping & Layout**:
1. `test_multiline_wrapping_narrow_width` - Long text in portrait, multiline enabled
2. `test_single_line_truncation` - Long text in portrait, multiline disabled
3. `test_stacking_overflow` - More lines than max_visible_lines in stacking mode

**Edge Clipping**:
4. `test_no_clipping_portrait_narrow` - Ensure text doesn't touch edges in 720x1280
5. `test_no_clipping_landscape_wide` - Ensure text doesn't touch edges in 1920x1080

**Unicode & Special Characters**:
6. `test_unicode_rendering` - Emoji, accented characters, CJK characters
7. `test_punctuation_heavy` - Multiple punctuation marks, quotes, dashes

**Extreme Aspect Ratios**:
8. `test_ultra_wide_4k` - 3840x2160 landscape
9. `test_portrait_phone` - 720x1280 portrait
10. `test_square_format` - 1080x1080 square

**Subtitle Modes**:
11. `test_word_only_mode` - Single word display
12. `test_stacking_mode_direction_up` - Stacking with upward direction
13. `test_sentence_highlight_mode` - Sentence with word highlighting

**Edge Cases**:
14. `test_single_word_input` - Minimal input
15. `test_very_long_word` - Word longer than typical line width

**Validation Strategy**:
- Automated assertions for all tests
- Pixel-level checks where appropriate
- Layout correctness validation
- No manual review required

### 3. Test Fixtures

#### Real-World Fixtures (`tests/fixtures/real_world/`)

**Content Guidelines**:
- 30-60 seconds of speech when rendered
- Written as if by actual content creator
- Represents realistic use case
- Natural language, proper grammar
- Appropriate complexity for content type

**Example - Educational Explainer**:
```
Welcome to this tutorial on machine learning fundamentals. Today, we'll explore 
how neural networks process information through layers of interconnected nodes. 
Each node applies a mathematical transformation to its inputs, gradually learning 
patterns from the training data. This process, called backpropagation, adjusts 
the network's weights to minimize prediction errors. By the end of this video, 
you'll understand the core concepts behind modern AI systems.
```

**Example - Product Demo**:
```
Introducing the all-new SmartHome Hub - your gateway to effortless home automation. 
Control lights, temperature, and security from a single intuitive interface. 
With voice commands and smartphone integration, managing your home has never been 
easier. Set custom schedules, create automation routines, and monitor everything 
in real-time. Transform your living space into a smart home today. Visit our 
website to learn more and get started with a free trial.
```

#### Technical Fixtures (`tests/fixtures/technical/`)

**Content Guidelines**:
- Minimal text to isolate specific behavior
- Designed to trigger edge cases
- Reproducible and deterministic

**Examples**:

`extreme_long_word.txt`:
```
Pneumonoultramicroscopicsilicovolcanoconiosis
```

`unicode_stress.txt`:
```
Hello 世界 🌍 Café résumé naïve
```

`punctuation_heavy.txt`:
```
"Wait!" she exclaimed—couldn't believe it... Really?!
```

`multiline_wrap_test.txt`:
```
This is an intentionally long sentence designed to test text wrapping behavior when the content exceeds the available width in narrow layouts.
```

### 4. Pytest Fixtures (`conftest.py`)

**New Fixtures**:

```python
@pytest.fixture
def real_world_fixture_dir(project_root: Path) -> Path:
    """Directory containing realistic content creator scripts."""
    return project_root / "tests" / "fixtures" / "real_world"

@pytest.fixture
def technical_fixture_dir(project_root: Path) -> Path:
    """Directory containing minimal edge case test inputs."""
    return project_root / "tests" / "fixtures" / "technical"

@pytest.fixture
def real_world_output_dir(test_output_root: Path) -> Path:
    """Output directory for real-world scenario tests."""
    output_dir = test_output_root / "test_real_world_scenarios"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture
def technical_output_dir(test_output_root: Path) -> Path:
    """Output directory for technical boundary tests."""
    output_dir = test_output_root / "test_technical_boundaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
```

**Preserved Fixtures**:
- `project_root` - Keep as-is
- `test_output_root` - Keep as-is (points to `output/test/`)

**Removed Fixtures**:
- `fixture_text_dir` - No longer needed (replaced by specific fixtures)

### 5. Helper Functions

**Validation Helpers** (preserved from `test_subtitle_stress.py`):

```python
def validate_subtitle_json_structure(json_path: Path) -> None:
    """Validate that subtitle JSON has correct structure."""
    with open(json_path) as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    for segment in data:
        assert "sentence_text" in segment
        assert "start_time" in segment
        assert "end_time" in segment
        assert "words" in segment
        assert isinstance(segment["words"], list)

def assert_frame_has_subtitle_pixels(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """Ensure subtitle is rendered (not blank frame)."""
    # Implementation from test_subtitle_stress.py

def assert_no_horizontal_edge_clipping(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """Ensure subtitle doesn't touch left/right edges."""
    # Implementation from test_subtitle_stress.py

def assert_sentence_layout_wraps(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """Ensure long text creates multiple lines."""
    # Implementation from test_subtitle_stress.py

def assert_single_line_layout(cfg: dict, json_path: Path, subtitle_time: float) -> None:
    """Ensure text stays on single line (no wrapping)."""
    # Implementation from test_subtitle_stress.py
```

## Data Flow

### Real-World Scenario Test Flow:
```
1. Load realistic script from fixtures/real_world/
2. Configure pipeline with appropriate settings
3. Run complete TTS → video pipeline
4. Assert output files exist
5. Validate JSON structure
6. Developer manually reviews video output
```

### Technical Boundary Test Flow:
```
1. Load minimal test input from fixtures/technical/
2. Configure pipeline to trigger edge case
3. Run complete TTS → video pipeline
4. Assert output files exist
5. Run automated pixel/layout assertions
6. Test passes/fails based on assertions
```

## Configuration Strategy

### Real-World Tests
- Use realistic configs that content creators would use
- One config per test (no permutations)
- Configs stored inline in test functions for clarity

### Technical Tests
- Use configs designed to trigger edge cases
- May test multiple configs for same input (e.g., multiline on/off)
- Configs stored inline in test functions

### Config Helper
```python
def get_integration_test_config(
    case_id: str,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    subtitle_config: dict = None
) -> dict:
    """
    Create test configuration for integration tests.
    
    Uses existing config.py infrastructure but with test-specific defaults.
    """
    from config import get_test_config
    
    overrides = {
        "width": width,
        "height": height,
        "fps": fps,
        "bg_color": (0, 0, 0),
        "text_color": (255, 255, 255),
        "highlight_color": (255, 255, 0),
    }
    
    if subtitle_config:
        overrides["subtitle"] = subtitle_config
    
    return get_test_config(case_id=case_id, overrides=overrides)
```

## Migration Plan

### Phase 1: Setup Structure
1. Create `tests/integration/` directory
2. Create `tests/fixtures/real_world/` directory
3. Create `tests/fixtures/technical/` directory
4. Create `tests/integration/__init__.py`

### Phase 2: Write Fixtures
1. Write 5-8 realistic scripts for real-world scenarios
2. Write 5-10 minimal inputs for technical edge cases
3. Review fixture content for quality and coverage

### Phase 3: Implement Real-World Tests
1. Create `test_real_world_scenarios.py`
2. Implement 5-8 test functions
3. Add helper function for JSON validation
4. Run tests and verify output

### Phase 4: Implement Technical Tests
1. Create `test_technical_boundaries.py`
2. Copy assertion helpers from `test_subtitle_stress.py`
3. Implement 10-15 test functions
4. Run tests and verify assertions pass

### Phase 5: Update Fixtures
1. Update `conftest.py` with new fixtures
2. Remove old `fixture_text_dir` fixture
3. Add new fixture functions

### Phase 6: Cleanup
1. Verify all new tests pass
2. Delete `test_subtitle_stress.py`
3. Delete `tests/fixtures/text/` directory
4. Update Makefile if needed
5. Update documentation

## Testing Strategy

### Running Tests

**Run all integration tests**:
```bash
pytest tests/integration/
```

**Run only real-world scenarios**:
```bash
pytest tests/integration/test_real_world_scenarios.py
```

**Run only technical boundaries**:
```bash
pytest tests/integration/test_technical_boundaries.py
```

**Run specific test**:
```bash
pytest tests/integration/test_real_world_scenarios.py::test_educational_explainer
```

### Manual Review Process

After running real-world scenario tests:
1. Navigate to `output/test_real_world_scenarios/`
2. Review each scenario's output video
3. Check for:
   - Subtitle readability
   - Timing accuracy
   - Visual quality
   - Appropriate layout for content type
4. If issues found, file bug or adjust config

### Automated Validation

Technical boundary tests should pass/fail automatically:
- Green: Algorithm behaves correctly at boundary
- Red: Edge case not handled properly, needs fix

## Success Criteria

1. ✅ Total integration test count: 15-25 (down from 48)
2. ✅ Real-world tests: 5-8 with realistic scripts
3. ✅ Technical tests: 10-15 with automated assertions
4. ✅ Clear separation: Two test files, two fixture dirs, two output dirs
5. ✅ Independent execution: Each test file can run standalone
6. ✅ Reasonable execution time: Under 5 minutes total
7. ✅ Easy manual review: 5-8 videos to check, not 48
8. ✅ Clean migration: Old test file and fixtures removed

## Risks & Mitigations

**Risk**: Real-world scripts may not cover all edge cases
**Mitigation**: Technical boundary tests explicitly cover edge cases

**Risk**: Manual review is subjective
**Mitigation**: Real-world tests have clear automated assertions for basic correctness

**Risk**: Test execution time may exceed 5 minutes
**Mitigation**: Use shorter scripts if needed, parallelize tests

**Risk**: Fixture content may become stale
**Mitigation**: Document fixture purpose and update as product evolves

## Future Enhancements

- Add visual regression testing (screenshot comparison)
- Add performance benchmarks for integration tests
- Add CI/CD integration with artifact upload
- Add test report generation with embedded videos
