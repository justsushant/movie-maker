# Implementation Plan: Video Engine Phase 1

## Overview

This implementation plan breaks down the video engine Phase 1 into discrete coding tasks. The approach follows a bottom-up strategy: build foundational components (easing, camera, data structures) first, then compose them into higher-level systems (planner, renderer), and finally integrate with the existing PRISM pipeline.

Each task builds on previous work, with checkpoints to validate functionality before proceeding. Testing tasks are marked as optional (*) to allow for faster MVP iteration.

## Tasks

- [x] 1. Set up engine module structure and dependencies
  - Create `engine/` directory with `__init__.py`
  - Add opencv-python and scipy to requirements.txt
  - Create empty module files: scene.py, easing.py, camera.py, planner.py, renderer.py, image_loader.py
  - _Requirements: All (foundational)_

- [x] 2. Implement Scene DSL data structures
  - [x] 2.1 Create MotionPreset enum in engine/scene.py
    - Define all motion preset values: STATIC, KEN_BURNS_ZOOM_IN, KEN_BURNS_ZOOM_OUT, PAN_LEFT, PAN_RIGHT, PAN_UP, PAN_DOWN, ZOOM_IN, ZOOM_OUT
    - _Requirements: 1.3_
  
  - [x] 2.2 Create ImageClip dataclass in engine/scene.py
    - Fields: source (Union[str, Path]), duration (float), motion (MotionPreset with default STATIC)
    - _Requirements: 1.2, 1.5_
  
  - [x] 2.3 Create Scene dataclass in engine/scene.py
    - Fields: clips (list[ImageClip]), resolution (tuple[int, int] default 1920x1080), fps (int default 30)
    - _Requirements: 1.1, 1.4_
  
  - [x]* 2.4 Write unit tests for Scene DSL (test_scene_dsl.py)
    - Test Scene creation with defaults
    - Test Scene creation with custom parameters
    - Test ImageClip creation with all motion presets
    - Test ImageClip default motion preset
    - Test MotionPreset enum values
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Implement easing function library
  - [x] 3.1 Create easing functions in engine/easing.py
    - Implement linear(t) -> t
    - Implement ease_in_cubic(t) -> t³
    - Implement ease_out_cubic(t) -> 1 - (1-t)³
    - Implement ease_in_out_cubic(t) -> piecewise cubic
    - Define EasingFunction type alias
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x]* 3.2 Write property test for easing function bounds
    - **Property 1: Easing Function Bounds**
    - **Validates: Requirements 2.5**
  
  - [x]* 3.3 Write property test for easing mathematical correctness
    - **Property 2: Easing Function Mathematical Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
  
  - [x]* 3.4 Write unit tests for easing functions (test_easing.py)
    - Test boundary values (0.0, 1.0) for each function
    - Test midpoint (0.5) for each function
    - Test linear returns input unchanged
    - Test ease-in starts slow
    - Test ease-out ends slow
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 4. Checkpoint - Verify foundational components
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement virtual camera system
  - [x] 5.1 Create Rect dataclass in engine/camera.py
    - Fields: x, y, width, height (all float)
    - Implement clamp_to(image_width, image_height) method
    - _Requirements: 3.1, 10.1_
  
  - [x] 5.2 Create VirtualCamera class in engine/camera.py
    - Constructor accepts viewport Rect
    - Implement apply_transform(source_image, output_size) method using cv2
    - Crop to viewport, resize with cv2.INTER_CUBIC
    - _Requirements: 3.1, 3.2, 3.3, 10.3_
  
  - [x] 5.3 Implement VirtualCamera.interpolate static method
    - Accept rect_start, rect_end, progress, easing_fn
    - Return interpolated Rect using easing function
    - _Requirements: 3.4, 3.5_
  
  - [x]* 5.4 Write property test for rectangle interpolation
    - **Property 3: Rectangle Interpolation Correctness**
    - **Validates: Requirements 3.5**
  
  - [x]* 5.5 Write property test for camera transform dimensions
    - **Property 8: Camera Transform Output Dimensions**
    - **Validates: Requirements 3.2, 3.3, 6.6**
  
  - [x]* 5.6 Write property test for viewport clamping
    - **Property 9: Viewport Clamping Safety**
    - **Validates: Requirements 10.1**
  
  - [x]* 5.7 Write unit tests for virtual camera (test_camera.py)
    - Test VirtualCamera creation
    - Test Rect clamping with various cases
    - Test camera transform with different viewport sizes
    - Test rectangle interpolation at t=0, t=0.5, t=1
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 10.1, 10.2, 10.3_

- [x] 6. Implement motion preset computation
  - [x] 6.1 Create compute_motion_path function in engine/camera.py
    - Accept preset, image_size, output_size, duration
    - Return Callable[[float], Rect] that maps time to viewport
    - Implement STATIC motion (centered crop)
    - _Requirements: 4.1, 4.10_
  
  - [x] 6.2 Implement zoom motion presets
    - Implement KEN_BURNS_ZOOM_IN (full to 50% centered)
    - Implement KEN_BURNS_ZOOM_OUT (50% centered to full)
    - Implement ZOOM_IN (shrink toward center)
    - Implement ZOOM_OUT (expand from center)
    - _Requirements: 4.2, 4.3, 4.8, 4.9, 10.5_
  
  - [x] 6.3 Implement pan motion presets
    - Implement PAN_LEFT (viewport moves right)
    - Implement PAN_RIGHT (viewport moves left)
    - Implement PAN_UP (viewport moves down)
    - Implement PAN_DOWN (viewport moves up)
    - _Requirements: 4.4, 4.5, 4.6, 4.7_
  
  - [x]* 6.4 Write property test for static motion invariance
    - **Property 5: Static Motion Invariance**
    - **Validates: Requirements 4.1**
  
  - [x]* 6.5 Write property test for pan motion monotonicity
    - **Property 6: Pan Motion Monotonicity**
    - **Validates: Requirements 4.4, 4.5, 4.6, 4.7**
  
  - [x]* 6.6 Write property test for zoom motion monotonicity
    - **Property 7: Zoom Motion Monotonicity**
    - **Validates: Requirements 4.2, 4.3, 4.8, 4.9**
  
  - [x]* 6.7 Write unit tests for motion presets (test_motion_presets.py)
    - Test STATIC returns same viewport at different times
    - Test Ken Burns zoom directions
    - Test pan directions
    - Test zoom directions
    - Test with landscape, portrait, and square images
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

- [x] 7. Checkpoint - Verify camera and motion systems
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement image loader with caching
  - [x] 8.1 Create ImageLoader class in engine/image_loader.py
    - Initialize with empty cache dictionary
    - Implement load(path) method
    - Check cache first, load from disk if not cached
    - Use PIL to load and convert to RGB
    - Convert to numpy array and cache
    - Handle FileNotFoundError and corrupted images
    - Implement clear_cache() method
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x]* 8.2 Write property test for image loader caching
    - **Property 11: Image Loader Caching**
    - **Validates: Requirements 9.5**
  
  - [x]* 8.3 Write property test for RGB conversion
    - **Property 12: Image Loader RGB Conversion**
    - **Validates: Requirements 9.4**
  
  - [x]* 8.4 Write unit tests for image loader (test_image_loader.py)
    - Test loading PNG, JPEG, WebP
    - Test loading image with alpha channel
    - Test loading grayscale image
    - Test caching behavior (mock file I/O)
    - Test FileNotFoundError for missing file
    - Test exception for corrupted file
    - Test clear_cache
    - Test output is numpy array with correct shape and dtype
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 9. Implement scene planner
  - [x] 9.1 Create ResolvedClip dataclass in engine/planner.py
    - Fields: source (Path), start_time (float), end_time (float), camera_path (Callable[[float], Rect])
    - _Requirements: 5.5_
  
  - [x] 9.2 Create ResolvedTimeline dataclass in engine/planner.py
    - Fields: clips (list[ResolvedClip]), resolution (tuple[int, int]), fps (int), duration (float)
    - _Requirements: 5.4_
  
  - [x] 9.3 Create ScenePlanner class in engine/planner.py
    - Implement plan(scene, image_loader) method
    - Iterate through clips, compute start/end times
    - Load images to get dimensions
    - Compute camera paths using compute_motion_path
    - Create ResolvedClip objects with absolute timing
    - Return ResolvedTimeline
    - _Requirements: 5.1, 5.2, 5.3, 5.6_
  
  - [x]* 9.4 Write property test for timeline clip timing
    - **Property 4: Timeline Clip Timing Consistency**
    - **Validates: Requirements 5.1, 5.2**
  
  - [x]* 9.5 Write property test for scene planning completeness
    - **Property 13: Scene Planning Completeness**
    - **Validates: Requirements 5.6**
  
  - [x]* 9.6 Write unit tests for scene planner (test_planner.py)
    - Test planning empty scene
    - Test planning single-clip scene
    - Test planning multi-clip scene
    - Test planning with mixed motion presets
    - Test timeline duration calculation
    - Test ResolvedClip attributes
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 10. Implement frame renderer
  - [x] 10.1 Create FrameRenderer class in engine/renderer.py
    - Constructor accepts ResolvedTimeline and ImageLoader
    - Store output resolution from timeline
    - _Requirements: 6.1_
  
  - [x] 10.2 Implement render_frame(t) method
    - Find active clip using _find_active_clip helper
    - Return black frame if no clip active
    - Load source image using image loader
    - Get viewport from clip's camera_path(t)
    - Create VirtualCamera and apply transform
    - Return transformed frame as numpy array
    - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [x] 10.3 Implement _find_active_clip(t) helper method
    - Iterate through clips, find where start_time <= t < end_time
    - Return clip or None
    - _Requirements: 6.2_
  
  - [x]* 10.4 Write property test for frame renderer clip selection
    - **Property 10: Frame Renderer Clip Selection**
    - **Validates: Requirements 6.2**
  
  - [x]* 10.5 Write unit tests for frame renderer (test_renderer.py)
    - Test render frame at t=0, t=middle, t=end
    - Test render frame between clips (black frame)
    - Test render frame before/after timeline (black frame)
    - Test with different motion presets
    - Test output dimensions
    - Test output dtype
    - Test image loader cache usage
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 11. Checkpoint - Verify complete engine pipeline
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Create test fixtures for real image testing
  - [x] 12.1 Create tests/fixtures/images/ directory structure
    - Add landscape images (1920x1080, 1280x720)
    - Add portrait images (1080x1920, 720x1280)
    - Add square images (1080x1080)
    - Add images in PNG, JPEG formats
    - Add small (100x100) and large (4K) test images
    - _Requirements: All (testing infrastructure)_
  
  - [x]* 12.2 Write integration test for complete pipeline
    - Test Scene → Planner → Renderer → Frames
    - Test rendering all frames for a 2-second scene
    - Test with real images from fixtures
    - Test with each motion preset
    - _Requirements: All_
  
  - [x]* 12.3 Write visual regression tests (test_visual_regression.py)
    - Generate reference frames for each motion preset
    - Compare rendered frames against references
    - Allow small tolerance for floating-point differences
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [x] 13. Integrate engine with existing rendering system
  - [x] 13.1 Modify rendering/video.py create_video function
    - Add optional scene parameter
    - When scene provided, create ImageLoader, ScenePlanner, FrameRenderer
    - Override resolution and fps from scene
    - Create make_frame_with_engine function that:
      - Gets base frame from engine renderer
      - Converts to PIL Image
      - Gets subtitle segments
      - Layouts and renders subtitles
      - Returns final frame as numpy array
    - When scene not provided, use existing SubtitleFrameComposer (backward compatibility)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x]* 13.2 Write integration test for subtitle overlay on engine frames
    - Test that subtitles render correctly over engine-generated frames
    - Test with different motion presets
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 14. Extend library API with Scene support
  - [x] 14.1 Modify api/library.py generate_video_from_text function
    - Add optional scene parameter
    - When scene provided, use scene's resolution and fps in renderer_config
    - Pass scene through to create_video
    - Fix bug: add subtitle_config to renderer_config dict
    - When scene not provided, use existing defaults (backward compatibility)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x]* 14.2 Write integration test for library API with Scene
    - Test generate_video_from_text with scene parameter
    - Test that scene resolution/fps override defaults
    - Test that subtitle_config is properly passed
    - Test backward compatibility without scene parameter
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 15. Checkpoint - Verify complete integration
  - Ensure all tests pass, ask the user if questions arise.

- [x]* 16. Write end-to-end integration test
  - Create complete test that:
    - Defines a Scene with multiple ImageClips
    - Uses different motion presets
    - Generates video with TTS audio and subtitles
    - Verifies output MP4 file exists and has correct duration
    - Verifies backward compatibility (video without Scene)
  - _Requirements: All_

- [x]* 17. Write error handling tests (test_error_handling.py)
  - Test image loader with missing file
  - Test image loader with corrupted file
  - Test motion preset with invalid enum value
  - Test scene with negative clip duration
  - Test viewport clamping with extreme values
  - Test renderer with empty timeline
  - _Requirements: 9.2, 9.3, 10.1_

- [x]* 18. Write performance tests
  - Measure frame render time with 1080p images
  - Measure frame render time with 4K images
  - Measure memory usage with cached images
  - Verify cache hit rate
  - Verify no memory leaks over 100 frames
  - _Requirements: 9.5_

- [x] 19. Final checkpoint - Complete Phase 1
  - Ensure all tests pass, ask the user if questions arise.
  - Verify backward compatibility with existing tests
  - Verify new functionality works with real images

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end functionality
- Real image fixtures enable visual regression testing
- Backward compatibility is maintained throughout
