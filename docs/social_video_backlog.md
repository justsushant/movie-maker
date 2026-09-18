# Social video features, improvements, and bug-fix backlog

Created: 2026-09-18  
Status: Proposed backlog; implementation has not started.

## Objective

Turn existing video footage into useful, engaging social media clips. The primary workflow is a recording → selected moments → edited vertical clips with original audio and readable captions. Narrated image videos remain a supported secondary workflow.

The first target is spoken content such as interviews, podcasts, tutorials, and screen recordings. Gameplay, sports, and other visually driven content will require additional visual analysis. Audience traction is an outcome to measure through experiments, not something the renderer or a clip score can guarantee.

This document captures the repository review and proposed work for a future session. It is a backlog, not an approved implementation design. Priorities and technical choices should be revisited when a representative source video and target platform are selected.

## Current foundation and boundaries

| Component | Available implementation | Boundary relevant to this backlog |
|---|---|---|
| Public Python API | `generate_video_from_text()` and `generate_video_from_file()` | Generates Kokoro narration from text; no footage-editing entry point |
| Lower-level rendering | `create_video()` accepts existing audio, subtitle data, and custom subtitle components | Its scene background is still an image sequence |
| Scene engine | Images, clip durations, motion, effects, transitions, resolution, and frame rate | No video-source clip, source in/out points, or layered video timeline |
| Subtitles | Word timestamps, highlighting, sentence/word/stacking layouts | No transcription of recorded speech; some styling settings are unused |
| Audio analysis | Beat, onset, energy, and spectral analysis | `Scene.audio` is an analysis input, not an exported music track |
| Output | MP4 through MoviePy with H.264/AAC; WAV and subtitle JSON intermediates | Word-level SRT export lives in the CLI; export controls are limited |
| Product surface | Python library, scripts, and examples | No web editor, HTTP service, publishing workflow, or analytics integration |

Useful source entry points:

- [Public API](../api/library.py): `generate_video_from_text`, `generate_video_from_file`.
- [Rendering](../rendering/video.py): `create_video`.
- [Scene model](../engine/scene.py): `Scene`, `ImageClip`, `Transition`.
- [Planning](../engine/planner.py): `ScenePlanner.plan`.
- [Frame rendering](../engine/renderer.py): `FrameRenderer`.
- [Subtitle interfaces](../subtitle/interfaces.py), [configuration](../subtitle/config.py), [layouts](../subtitle/layouts.py), and [renderer](../subtitle/renderer.py).
- [TTS pipeline](../pipeline/orchestrator.py): `TTSPipeline.process`.
- [Existing vertical-video example](../examples/engagement_max_demo.py).

## Priorities and tracking

- **P0 — Foundation:** resolve before calling the first footage workflow reliable. This is a delivery priority, not an incident severity.
- **P1 — Next:** make production, review, and iteration substantially easier.
- **P2 — Later:** extend automation or creative range after the foundation is validated.

All items below are **Open**. IDs are stable references for future issues and implementation plans. Acceptance criteria describe the intended result, not currently passing checks.

## Bug fixes and incomplete behavior

### BUG-01 — Handle scenes shorter than narration explicitly

**Priority:** P0. **Evidence:** source-confirmed behavior; full render reproduction pending.

`create_video()` uses the longest audio, subtitle, or scene duration. When the scene has ended, `FrameRenderer._render_single_clip_frame()` returns black. The [engagement guide](engagement_levers.md) says the last frame is held, which does not match the implementation.

**Work:** introduce an explicit duration/end-of-scene policy, such as hold-last-frame, fit-scene, or reject-mismatch. Document the chosen default. Longer scenes also need a deliberate audio-ending policy.

**Acceptance criteria:**

- A short scene with longer narration has the selected ending behavior rather than an accidental black tail.
- Equal-length and longer-scene cases are covered, including transition overlaps.
- A rendered regression example verifies the final frames and audio ending.

**Sources:** [video exporter](../rendering/video.py), [frame renderer](../engine/renderer.py).

### BUG-02 — Preserve aspect ratio across camera motion

**Priority:** P0. **Evidence:** source-confirmed geometry issue; visual reproduction pending.

Static mode calculates a crop for the output aspect ratio. Zoom presets use viewports based on the source aspect ratio and then resize directly to the output dimensions. Landscape-to-portrait rendering can stretch the image. Pan viewport clamping also needs review when the source is smaller than the requested viewport.

**Work:** share aspect-correct crop/fit calculations across motion presets. Define fit, fill/crop, and optional padded-background modes.

**Acceptance criteria:**

- Circles and faces retain their proportions in portrait, square, and landscape output.
- Motion paths remain within valid source bounds for small and large images.
- Visual checks cover mixed source/output aspect ratios for every motion preset.

**Source:** [camera implementation](../engine/camera.py), especially `compute_motion_path` and `VirtualCamera.apply_transform`.

### BUG-03 — Make exposed subtitle styling controls effective

**Priority:** P0 for outlines/shadows; P1 for stacking controls. **Evidence:** source-confirmed unused settings.

`shadow_color` and `outline_color` are accepted by `SubtitleConfig`, but the default renderer draws only filled text. Stacking speed, direction, and old-line fading are configured but unused by `StackingLayout`.

**Work:** implement these settings or explicitly deprecate unsupported options. Specify units and behavior for animation controls before implementing them.

**Acceptance criteria:**

- Outlines and shadows visibly improve caption contrast on bright and dark footage.
- Supported stacking settings produce observable, documented changes.
- Visual regression checks exercise settings through the public configuration path.

**Sources:** [subtitle configuration](../subtitle/config.py), [subtitle renderer](../subtitle/renderer.py), [stacking layout](../subtitle/layouts.py).

### BUG-04 — Repair stale test and benchmark entry points

**Priority:** P0. **Evidence:** missing paths confirmed during the review.

`make test-stress` references the absent `tests/test_subtitle_stress.py`. The benchmark suite references absent files under `tests/fixtures/text/` and skips missing inputs, potentially leaving no useful measurements.

**Acceptance criteria:**

- Every documented Make test target resolves to existing tests.
- Benchmark cases use maintained fixtures and report how many cases actually ran.
- A benchmark with no valid cases exits unsuccessfully rather than producing a misleading result.

**Sources:** [Makefile](../Makefile), [benchmark script](../tests/benchmark_performance.py), [current fixtures](../tests/fixtures/).

## New features

### FEAT-01 — Edit clips from existing footage

**Priority:** P0. **Depends on:** IMP-01; coordinate framing behavior with BUG-02.

Add a video-source clip abstraction with source path, in/out points, timeline placement, original-audio selection, and crop/fit settings. Support consecutive excerpts from one or more files. Keep existing image scenes working.

**Acceptance criteria:**

- A user can select three source intervals and export three separate vertical MP4s with original speech.
- Trim boundaries are frame-accurate under the selected export strategy, without audible or visible synchronization drift.
- Unsupported files, invalid intervals, missing audio, rotation metadata, and variable-frame-rate inputs have defined handling.
- Mixed image/video compositions can reuse compatible existing effects and captions.

**Starting points:** [scene model](../engine/scene.py), [planner](../engine/planner.py), [renderer](../engine/renderer.py), [exporter](../rendering/video.py).

### FEAT-02 — Transcribe recorded speech and edit captions

**Priority:** P0. **Depends on:** IMP-01; integrates with FEAT-01.

Introduce a transcription adapter that returns text and word timestamps compatible with the subtitle system. Support corrections and transcript reuse. Select the transcription backend after comparing language support, timing quality, runtime, and cost on representative footage.

**Acceptance criteria:**

- Original speech can be captioned without generating TTS narration.
- Corrections persist and can be rendered without repeating transcription.
- Captions stay synchronized after trimming and combining intervals.
- Transcript data records language, source identity, and available timing/confidence information.

**Reuse:** [subtitle source](../subtitle/source.py), [subtitle interfaces](../subtitle/interfaces.py), [processing models](../processing/models.py).

### FEAT-03 — Suggest self-contained excerpts

**Priority:** P1. **Depends on:** FEAT-01, FEAT-02.

Analyze transcripts to propose excerpts with a clear opening, sufficient context, and a payoff. Return source timestamps, an editable title, and an explanation of the selection. Combine semantic analysis with sentence boundaries and duration constraints.

**Acceptance criteria:**

- Suggestions reference actual source intervals and can be previewed.
- Users can adjust boundaries before rendering; suggestions do not automatically publish.
- Selection favors complete thoughts and avoids cutting off setup or conclusions.
- Rankings are labeled as editorial heuristics, not validated predictions of virality.

### FEAT-04 — Reframe for vertical and square output

**Priority:** P1. **Depends on:** FEAT-01, BUG-02.

Start with an editable crop and consistent output presets. Add face/speaker tracking with smooth crop movement, manual overrides, and split-screen layouts for interviews. Preserve readable screen content in tutorial layouts.

**Acceptance criteria:**

- One excerpt can produce 9:16, 1:1, and 16:9 variants without stretching.
- Automatic framing has a stable fallback when tracking fails.
- Crop paths can be inspected and adjusted; multiple speakers do not cause rapid framing oscillation.
- Caption and title placement account for configurable platform overlay safe areas.

### FEAT-05 — Mix and normalize audio

**Priority:** P1. **Depends on:** FEAT-01, IMP-01.

Separate source audio, optional narration, music, sound effects, and analysis inputs. Add gain, fades, speech-aware music ducking, and export loudness controls.

**Acceptance criteria:**

- Music selected for output is audible in the exported file; analysis-only inputs remain separate.
- Original speech remains intelligible with music enabled.
- The mixer handles source offsets and edits consistently, with defined clipping and end-of-track behavior.

**Current boundary:** `Scene.audio` only drives analysis in [the planner](../engine/planner.py); [the exporter](../rendering/video.py) attaches a separate audio file.

### FEAT-06 — Add reusable caption and branding templates

**Priority:** P1. **Depends on:** BUG-03, FEAT-01, FEAT-02.

Provide a small set of configurable styles: caption font and emphasis, title hook, logo, colors, outro, and optional progress indicator. Keep captions readable and effects restrained by default.

**Acceptance criteria:**

- A saved template can be reused across recordings and aspect ratios.
- Users can generate variants without editing Python scripts.
- Titles and captions do not overlap each other or configured safe areas.
- Real font measurements guide wrapping; chosen fonts support the target language.

**Reuse:** [subtitle layouts](../subtitle/layouts.py) and compatible [text/watermark effects](../engine/effects.py).

### FEAT-07 — Review, save, and resume projects

**Priority:** P1. **Depends on:** FEAT-01, FEAT-02, IMP-01, IMP-02.

Provide a lightweight review interface for previewing excerpts, editing timestamps/transcripts, adjusting framing, selecting a style, and rendering selected clips. Start with local project files; add a service only if needed.

**Acceptance criteria:**

- A saved project reopens with source references, edits, captions, and settings intact.
- Cheap previews are available before full-resolution rendering.
- Render progress and failures are visible; independent failed clips can be retried.

### FEAT-08 — Compare variants and record audience results

**Priority:** P2. **Depends on:** FEAT-06, FEAT-07.

Associate exported variants with changes to opening, duration, framing, and caption style. Begin with manual metrics entry; consider platform analytics connectors later.

**Acceptance criteria:**

- Each variant records its source excerpt and exact editing recipe.
- Metrics include platform, observation window, and available retention/watch metrics.
- Comparisons distinguish changes to content from changes to presentation.
- Results are treated as observations with audience and distribution differences, not proof of causation.

### FEAT-09 — Optional production extensions

**Priority:** P2. **Depends on:** a reliable core editing workflow.

Candidates: subtitle translation, optional TTS introductions, supplemental image/video inserts, export of caption sidecars, upload preparation, scheduling/publishing integrations, and visual-event selection for non-spoken footage.

**Acceptance criteria:** split each selected extension into its own scoped issue with a representative input, expected output, dependencies, and measurable success criteria before implementation.

## Engineering and workflow improvements

### IMP-01 — Introduce one edit timeline and timestamp mapping

**Priority:** P0.

Represent source time and output time explicitly. Every retained interval should map source video, source audio, captions, and framing to the same output interval. This is especially important when removing pauses or joining nonadjacent excerpts.

**Acceptance criteria:** one shared mapping drives all timed components; boundary checks cover joins, trimmed words, transitions, and any future speed changes. Save edit decisions in a versioned, serializable project format. Existing image scenes remain usable.

### IMP-02 — Separate generation, planning, preview, and export APIs

**Priority:** P1; expose the minimal footage entry point during P0.

The current convenience API constructs Kokoro for every call. Add independent stages so imported footage, existing narration, and corrected subtitles do not trigger unwanted regeneration. Expose reusable results and let audio-reactive effects access analysis without duplicating planning.

**Acceptance criteria:** callers can render without importing/initializing TTS; reuse narration and transcription; preview selected frames; export captions; and inspect planned durations. Existing convenience functions keep their documented behavior.

### IMP-03 — Make installation and test execution reproducible

**Priority:** P0 for environment setup; P1 for packaging and CI.

Declare a supported Python/dependency combination, reproducible dependency resolution, and FFmpeg/model/font setup. Separate lightweight rendering dependencies from optional TTS and transcription dependencies where practical.

**Acceptance criteria:** a clean environment can run a small render smoke test; fast tests do not unexpectedly load or download models; CI separates unit checks from expensive media/model integration checks. Run commands reflect actual files and test selection.

**Sources:** [requirements](../requirements.txt), [Makefile](../Makefile), [API tests](../tests/test_library_api_scene.py).

### IMP-04 — Consolidate documentation around the current public API

**Priority:** P1.

Replace stale `api.generate_video()` examples and outdated module paths. Document image versus footage capabilities, analysis audio versus output audio, configuration precedence, output files, and end-of-scene behavior. Audit public settings against their consumers rather than documenting fields as working features automatically.

**Acceptance criteria:** examples use actual symbols; runnable examples receive smoke checks; planned features and historical benchmark/test results are clearly labeled. This backlog complements the [existing engine roadmap](video_engine_plan.md), with footage support prioritized ahead of depth/parallax and elaborate typography.

### IMP-05 — Add representative output-quality checks

**Priority:** P0 for milestone checks; expand in P1.

Use short maintained media fixtures to verify exported files, not only API calls and file existence. Include mixed aspect ratios, original speech, long captions, portrait output, source cuts, and multiple excerpts.

**Acceptance criteria:** check decoded dimensions, duration, audio presence/synchronization, caption boundaries, and unintended black tails. Add targeted visual regressions for BUG-02 and BUG-03. Record actual command output before declaring a milestone complete.

### IMP-06 — Measure performance and improve repeated rendering

**Priority:** P1.

Benchmark realistic footage at draft and final resolutions. Measure transcription, planning, frame processing, encoding, and total process memory separately. Reuse loaded models, cache expensive analysis, cache fonts/layout where useful, and release media readers/writers reliably.

**Acceptance criteria:** benchmarks identify hardware, dependency versions, source duration, output settings, effect count, and cold/warm runs. Report peak process memory rather than treating Python allocation tracking as total memory. Re-rendering visual variants reuses unchanged audio/transcripts.

### IMP-07 — Add preflight validation and structured render results

**Priority:** P1.

Validate files, intervals, dimensions, durations, fonts, and required capabilities before expensive work. Return output paths, warnings, timing summaries, and errors in a structured result. Use isolated output directories for concurrent jobs.

**Acceptance criteria:** invalid requests fail with actionable errors; incomplete outputs are identifiable; repeated jobs do not accidentally overwrite each other; batch callers can tell which clips succeeded. Add cancellation and retry behavior when the review interface or service needs it.

## Recommended delivery milestones

| Milestone | Scope | Exit condition |
|---|---|---|
| 0. Establish a trustworthy baseline | BUG-01–04, IMP-03 setup, IMP-05 baseline | Dependencies installed; findings reproduced or revised; targeted checks and a real image-video render reviewed |
| 1. Produce clips from one recording | FEAT-01–02, IMP-01, minimal IMP-02 | Three manually selected excerpts become vertical MP4s with original audio, corrected captions, editable crops, and verified synchronization |
| 2. Improve editing and presentation | FEAT-04–07, IMP-02, IMP-04–07 | Projects can be saved, previewed, styled, mixed, rendered, and retried with consistent results |
| 3. Assist selection and learn from results | FEAT-03, FEAT-08 | Suggested excerpts are reviewed by a user; exported variants can be linked to observed audience metrics |
| 4. Extend where evidence supports it | Selected FEAT-09 items | Each extension has its own validated scope and representative quality checks |

Do not make a browser editor, publishing service, or automatic clip ranking a prerequisite for the first usable export. A script or CLI with a saved edit file is sufficient for milestone 1.

## Architecture direction to evaluate

Reuse the subtitle interfaces, image effects, and existing image-scene workflow. Introduce media sources, an explicit editing timeline, transcription adapters, and audio composition around them.

Evaluate FFmpeg for standard decode/trim/crop/mix/encode operations while retaining Python frame rendering for custom visuals. FFmpeg provides relevant filters for trimming, cropping, mixing, silence detection, and loudness normalization; exact backend choices need a representative quality/performance comparison. See the [official filter documentation](https://ffmpeg.org/ffmpeg-filters.html).

For audience feedback, YouTube exposes measures including stayed-to-watch, average view duration, and average percentage viewed. These are possible inputs to FEAT-08, not universal success thresholds. See [YouTube's content-performance documentation](https://support.google.com/youtube/answer/12220281?hl=en).

## Decisions to make when work resumes

1. Choose one representative recording and initial content category.
2. Choose the first publishing platform, desired clip lengths, and required languages.
3. Decide whether transcription must run locally or may use an external service.
4. Choose the smallest useful editing surface: Python, CLI/project file, or browser interface.
5. Decide the default crop/fit and duration policies, including manual override behavior.
6. Set quality and runtime targets using actual footage; no delivery estimates are committed here.

## Review evidence and limits

The 2026-09-18 review inspected implementations, documentation, examples, and tests. All 129 tracked Python files parsed successfully at that point. The checkout had no project virtual environment, and the checked Python interpreter lacked the project dependencies. The test suite and full rendering pipeline were not executed.

Bug descriptions above distinguish source findings from runtime reproduction. Existing test counts and performance claims in other documents were not revalidated. Recheck the current source and establish the baseline in milestone 0 before treating any item as resolved or assuming historical measurements still apply.
