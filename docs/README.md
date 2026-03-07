# PRISM Documentation

Complete documentation for the PRISM video generation system.

## 📚 Documentation Index

### Getting Started
- **[Getting Started Guide](getting_started.md)** - Installation, first video, basic usage
- **[Quick Reference](quick_reference.md)** - 30-second cheat sheet for common tasks
- **[Requirements](requirements.md)** - What you need to create videos

### Core Features
- **[Video Engine](video_engine.md)** - Motion effects, transitions, and visual effects (Phase 1 & 2)
- **[Subtitles](subtitles.md)** - Subtitle modes, styling, and configuration
- **[How It Works](how_it_works.md)** - Technical pipeline walkthrough

### Architecture & Design
- **[Architecture](architecture.md)** - System design, patterns, and component overview
- **[Video Engine Plan](video_engine_plan.md)** - Roadmap and implementation phases

### Performance
- **[Performance Benchmarks](performance_benchmarks.md)** - Rendering performance data
- **[Profiling Analysis](profiling_analysis.md)** - Performance optimization insights

## 🎯 Quick Navigation

### I want to...

**Create my first video**
→ Start with [Getting Started Guide](getting_started.md)

**Use images with motion and transitions**
→ Read [Video Engine](video_engine.md)

**Customize subtitle appearance**
→ See [Subtitles](subtitles.md)

**Understand the system architecture**
→ Check [Architecture](architecture.md)

**Optimize performance**
→ Review [Performance Benchmarks](performance_benchmarks.md)

**See working examples**
→ Browse `../examples/` directory

## 📖 Documentation by User Type

### Content Creators
1. [Getting Started Guide](getting_started.md) - Learn the basics
2. [Video Engine](video_engine.md) - Add motion and effects
3. [Subtitles](subtitles.md) - Customize subtitle appearance
4. [Quick Reference](quick_reference.md) - Common tasks

### Developers
1. [Architecture](architecture.md) - Understand the system
2. [How It Works](how_it_works.md) - Technical details
3. [Getting Started Guide](getting_started.md#python-api-programmatic) - API usage
4. [Video Engine](video_engine.md) - Scene DSL and effects API

### Video Producers
1. [Video Engine](video_engine.md) - Professional effects
2. [Performance Benchmarks](performance_benchmarks.md) - Production considerations
3. [Subtitles](subtitles.md) - Subtitle styling options
4. [Quick Reference](quick_reference.md) - Workflow shortcuts

## 🚀 Quick Start

```bash
# Install
make setup

# Create video
source .venv/bin/activate
python -c "
from pathlib import Path
from api.library import generate_video_from_text

text = 'Hello world! This is PRISM.'
video_path = generate_video_from_text(text, Path('output/hello'))
print(f'Video: {video_path}')
"
```

## 📂 Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── getting_started.md           # Installation and first steps
├── quick_reference.md           # Quick cheat sheet
├── requirements.md              # What you need
├── video_engine.md              # Motion, transitions, effects
├── subtitles.md                 # Subtitle configuration
├── how_it_works.md              # Technical pipeline
├── architecture.md              # System design
├── video_engine_plan.md         # Roadmap
├── performance_benchmarks.md    # Performance data
└── profiling_analysis.md        # Optimization insights
```

## 🎬 Examples

Complete working examples are in the `examples/` directory:

```
examples/
├── demo_phase2_showcase.py      # Full feature showcase
├── demo_phase2_simple.py        # Quick visual demo
└── dragon/                      # Dragon legends example
    ├── README.md
    ├── create_dragon_video.py
    └── create_dragon_video_simple.py
```

## 🔧 API Reference

### Main API Functions

```python
from api.library import generate_video_from_text, generate_video_from_file

# Generate from text string
video_path = generate_video_from_text(text, output_dir)

# Generate from text file
video_path = generate_video_from_file(input_file, output_dir)
```

See [Getting Started Guide](getting_started.md#python-api-programmatic) for detailed API documentation.

## 🎨 Feature Overview

### Phase 1 (Complete)
- ✅ Image-based video composition
- ✅ 9 motion presets (Ken Burns, pan, zoom)
- ✅ Virtual camera system
- ✅ Smooth easing functions
- ✅ Image caching

### Phase 2 (Complete)
- ✅ 24 transition types
  - Blend (crossfade, fade through colors)
  - Geometric (slides, pushes, wipes)
  - Shapes (iris, clock, diamond, blinds)
  - Animated (zoom through, whip pan, pixelate, glitch)
- ✅ Visual effects
  - Color grading (brightness, contrast, saturation)
  - Vignette
  - Film grain
  - Fade in/out
  - Pulse effect
- ✅ Effect chaining
- ✅ Full backward compatibility

## 📊 Test Coverage

- **278 tests passing** (62 Phase 2 + 216 Phase 1)
- Unit tests for all components
- Integration tests for complete pipeline
- Property-based tests for correctness
- Visual regression tests
- Performance benchmarks

## 🤝 Contributing

When contributing documentation:

1. Keep examples simple and focused
2. Use code blocks with syntax highlighting
3. Include expected output when relevant
4. Cross-reference related documentation
5. Test all code examples before committing

## 📝 Documentation Standards

- **Markdown format** - All docs use GitHub-flavored Markdown
- **Code examples** - Include working, tested examples
- **Cross-references** - Link to related documentation
- **Clear structure** - Use headings, lists, and formatting
- **Up-to-date** - Keep docs synchronized with code changes

## 🔗 External Resources

- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Text-to-speech engine
- [MoviePy](https://zulko.github.io/moviepy/) - Video composition library
- [Pillow](https://pillow.readthedocs.io/) - Image processing
- [OpenCV](https://opencv.org/) - Computer vision library

## 📮 Getting Help

1. **Check documentation** - Browse this directory
2. **Run examples** - See `examples/` for working code
3. **Run tests** - `make test` to verify installation
4. **Read source** - Code has extensive docstrings

---

**Ready to get started?** → [Getting Started Guide](getting_started.md)

**Need a quick reference?** → [Quick Reference](quick_reference.md)

**Want to see examples?** → `../examples/` directory
