# Requirements Document: Video Engine Phase 1

## Introduction

PRISM currently generates narrated videos with subtitles over a solid-color background. This feature extends the system with a video generation engine that composites images with motion effects (Ken Burns, pan, zoom) while maintaining full integration with the existing subtitle system. Phase 1 establishes the foundational architecture: Scene DSL, easing functions, virtual camera system, motion presets, and frame-based rendering.

## Glossary

- **Scene**: A declarative description of a video composition containing clips, transitions, and metadata
- **ImageClip**: A single image displayed for a duration with optional motion effects
- **MotionPreset**: A predefined camera movement pattern (Ken Burns, pan, zoom, static)
- **VirtualCamera**: A viewport that defines which portion of a source image is visible in the output frame
- **EasingFunction**: A mathematical function that controls the rate of change for animated parameters
- **FrameRenderer**: The component that generates individual video frames by applying camera transforms to images
- **SubtitleFrameComposer**: The existing component that renders subtitles onto frames
- **BaseImage**: The background image onto which subtitles are composited

## Requirements

### Requirement 1: Scene DSL Data Structures

**User Story:** As a developer, I want to describe video compositions declaratively using Python dataclasses, so that I can easily specify image sequences with motion effects.

#### Acceptance Criteria

1. THE System SHALL provide a Scene dataclass with resolution, fps, and clips list attributes
2. THE System SHALL provide an ImageClip dataclass with source path, duration, and motion preset attributes
3. THE System SHALL provide a MotionPreset enum with values: STATIC, KEN_BURNS_ZOOM_IN, KEN_BURNS_ZOOM_OUT, PAN_LEFT, PAN_RIGHT, PAN_UP, PAN_DOWN, ZOOM_IN, ZOOM_OUT
4. WHEN a Scene is created with default parameters, THE System SHALL use 1920x1080 resolution and 30 fps
5. WHEN an ImageClip is created without a motion preset, THE System SHALL default to STATIC motion

### Requirement 2: Easing Function Library

**User Story:** As a developer, I want smooth animation curves for camera movements, so that motion effects appear natural and professional.

#### Acceptance Criteria

1. THE System SHALL provide a linear easing function that returns the input value unchanged
2. THE System SHALL provide an ease_in_cubic easing function that accelerates from zero velocity
3. THE System SHALL provide an ease_out_cubic easing function that decelerates to zero velocity
4. THE System SHALL provide an ease_in_out_cubic easing function that accelerates then decelerates
5. WHEN an easing function receives a progress value between 0.0 and 1.0, THE System SHALL return a value between 0.0 and 1.0
6. WHEN an easing function receives 0.0, THE System SHALL return 0.0
7. WHEN an easing function receives 1.0, THE System SHALL return 1.0

### Requirement 3: Virtual Camera System

**User Story:** As a developer, I want a virtual camera that defines viewport rectangles, so that I can control which portion of source images appears in output frames.

#### Acceptance Criteria

1. THE System SHALL provide a VirtualCamera class that stores a viewport rectangle (x, y, width, height)
2. WHEN a VirtualCamera applies a transform to a source image, THE System SHALL crop the image to the viewport rectangle
3. WHEN a VirtualCamera applies a transform to a source image, THE System SHALL resize the cropped region to match the output resolution
4. THE System SHALL provide a method to interpolate between two viewport rectangles using an easing function
5. WHEN interpolating between two rectangles, THE System SHALL compute intermediate x, y, width, and height values using the easing function

### Requirement 4: Motion Preset Implementation

**User Story:** As a developer, I want predefined motion patterns, so that I can easily apply common camera movements without manual calculations.

#### Acceptance Criteria

1. WHEN STATIC motion is applied, THE System SHALL use the same viewport rectangle for the entire clip duration
2. WHEN KEN_BURNS_ZOOM_IN motion is applied, THE System SHALL interpolate from a larger viewport to a smaller centered viewport
3. WHEN KEN_BURNS_ZOOM_OUT motion is applied, THE System SHALL interpolate from a smaller centered viewport to a larger viewport
4. WHEN PAN_LEFT motion is applied, THE System SHALL move the viewport horizontally from right to left across the image
5. WHEN PAN_RIGHT motion is applied, THE System SHALL move the viewport horizontally from left to right across the image
6. WHEN PAN_UP motion is applied, THE System SHALL move the viewport vertically from bottom to top across the image
7. WHEN PAN_DOWN motion is applied, THE System SHALL move the viewport vertically from top to bottom across the image
8. WHEN ZOOM_IN motion is applied, THE System SHALL shrink the viewport toward the center over time
9. WHEN ZOOM_OUT motion is applied, THE System SHALL expand the viewport from the center over time
10. THE System SHALL use ease_in_out_cubic easing for all motion presets by default

### Requirement 5: Scene Timeline Planning

**User Story:** As a developer, I want the system to resolve clip timings automatically, so that I can specify durations without manually calculating start times.

#### Acceptance Criteria

1. WHEN a Scene contains multiple clips, THE System SHALL compute start_time for each clip by summing previous clip durations
2. WHEN a Scene contains multiple clips, THE System SHALL compute end_time for each clip as start_time plus duration
3. THE System SHALL provide a ScenePlanner class that converts a Scene into a ResolvedTimeline
4. THE System SHALL provide a ResolvedTimeline class that contains a list of ResolvedClip objects
5. THE System SHALL provide a ResolvedClip class with source path, start_time, end_time, and camera_path attributes
6. WHEN planning a scene, THE System SHALL compute camera paths for each clip based on its motion preset

### Requirement 6: Frame-Based Renderer

**User Story:** As a developer, I want a frame renderer that generates video frames from a timeline, so that I can produce the visual content for videos.

#### Acceptance Criteria

1. THE System SHALL provide a FrameRenderer class that accepts a ResolvedTimeline and output resolution
2. WHEN rendering a frame at time t, THE System SHALL identify which clip is active at that time
3. WHEN rendering a frame at time t, THE System SHALL load the source image for the active clip
4. WHEN rendering a frame at time t, THE System SHALL compute the camera viewport for that time using the clip's camera path
5. WHEN rendering a frame at time t, THE System SHALL apply the camera transform to the source image
6. WHEN rendering a frame at time t, THE System SHALL return the transformed image as a numpy array
7. WHEN no clip is active at time t, THE System SHALL return a black frame

### Requirement 7: Integration with Subtitle System

**User Story:** As a developer, I want subtitles to render over engine-generated frames, so that narrated videos can have both visual content and text overlays.

#### Acceptance Criteria

1. WHEN SubtitleFrameComposer is initialized with a base_image parameter, THE System SHALL composite subtitles onto that image instead of creating a blank background
2. WHEN create_video receives a Scene parameter, THE System SHALL use FrameRenderer to generate base frames
3. WHEN create_video receives a Scene parameter, THE System SHALL pass each base frame to SubtitleFrameComposer for subtitle overlay
4. WHEN create_video does not receive a Scene parameter, THE System SHALL use the current solid-color background behavior
5. THE System SHALL maintain backward compatibility with existing video generation when no Scene is provided

### Requirement 8: Library API Extension

**User Story:** As a developer, I want to pass Scene objects through the library API, so that I can generate videos with image sequences programmatically.

#### Acceptance Criteria

1. WHEN generate_video_from_text receives a scene parameter, THE System SHALL pass it to create_video
2. WHEN generate_video_from_text receives a scene parameter, THE System SHALL use the scene's resolution and fps
3. WHEN generate_video_from_text does not receive a scene parameter, THE System SHALL use the current default behavior
4. THE System SHALL pass subtitle_config from generate_video_from_text to create_video correctly

### Requirement 9: Image Loading and Validation

**User Story:** As a developer, I want robust image loading with error handling, so that the system gracefully handles missing or invalid image files.

#### Acceptance Criteria

1. WHEN loading an image file, THE System SHALL support PNG, JPEG, and common image formats
2. WHEN an image file does not exist, THE System SHALL raise a FileNotFoundError with a descriptive message
3. WHEN an image file is corrupted or invalid, THE System SHALL raise an appropriate exception with a descriptive message
4. WHEN loading an image, THE System SHALL convert it to RGB color mode
5. WHEN loading an image, THE System SHALL cache loaded images to avoid redundant disk reads

### Requirement 10: Camera Transform Mathematics

**User Story:** As a developer, I want accurate camera transforms, so that motion effects produce correct visual results without distortion.

#### Acceptance Criteria

1. WHEN a viewport rectangle extends beyond the source image boundaries, THE System SHALL clamp the rectangle to valid coordinates
2. WHEN resizing a cropped region, THE System SHALL maintain aspect ratio if the viewport and output resolutions differ
3. WHEN resizing a cropped region, THE System SHALL use high-quality interpolation (bicubic or better)
4. THE System SHALL handle source images with different aspect ratios than the output resolution
5. WHEN computing Ken Burns zoom, THE System SHALL center the smaller viewport on the image center or a specified focal point

