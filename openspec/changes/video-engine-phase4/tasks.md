## 1. Setup

- [x] 1.1 Review existing effect system architecture (engine/effects.py)
- [x] 1.2 Review Phase 2 effect patterns for consistency
- [x] 1.3 Review Phase 3 audio-reactive effect patterns for consistency
- [x] 1.4 Set up test fixtures for Phase 4 effects
- [x] 1.5 Create test image fixtures for texture and stylization effects

## 2. Core Implementation - Rich Color Effects (Priority 1)

- [x] 2.1 Implement grayscale effect (simple, 5 lines of code)
- [x] 2.2 Implement invert/negative effect (simple, 1 line of code)
- [x] 2.3 Implement sepia effect (low complexity, 5 lines of code)
- [x] 2.4 Implement hue shift effect (uses OpenCV HSV conversion)
- [x] 2.5 Implement warm color temperature effect (numpy channel manipulation)
- [x] 2.6 Implement cool color temperature effect (numpy channel manipulation)
- [x] 2.7 Implement tint/color overlay effect (numpy alpha blending)
- [x] 2.8 Implement gamma correction effect (numpy power function)
- [x] 2.9 Implement curves/LUT effect (OpenCV LUT or custom lookup)
- [x] 2.10 Implement channel mixer effect (numpy matrix multiplication)
- [x] 2.11 Implement duotone effect (grayscale + linear interpolation)
- [x] 2.12 Implement tricolor/gradient map effect (grayscale + multi-stop colormap)
- [x] 2.13 Implement cinematic teal-orange effect (OpenCV HSV selective color adjustment)
- [x] 2.14 Implement bleach bypass effect (grayscale blend + contrast boost)
- [x] 2.15 Implement cross-process effect (per-channel S-curve adjustments)
- [x] 2.16 Implement auto white balance (gray-world algorithm, channel scaling)
- [x] 2.17 Implement vibrance effect (OpenCV HSV + conditional saturation)
- [x] 2.18 Implement color pulse/flash effect (numpy sine wave envelope)
- [x] 2.19 Implement fade to color effect (numpy linear interpolation)
- [x] 2.20 Implement thermal/infrared effect (OpenCV color map)
- [x] 2.21 Add color effects to engine/effects.py exports
- [x] 2.22 Add property-based tests for color effects
- [x] 2.23 Add unit tests for color effects
- [ ] 2.24 Create examples demonstrating color effects
- [ ] 2.25 Update documentation with color effects

## 3. Core Implementation - Blur Effects (Priority 2)

- [x] 3.1 Implement motion blur effect (OpenCV filter2D with line kernel)
- [x] 3.2 Implement radial blur effect (sample + average along radial lines)
- [x] 3.3 Implement zoom blur effect (blend scaled copies)
- [x] 3.4 Implement tilt-shift/miniature effect (gradient mask + variable blur)
- [x] 3.5 Implement depth-of-field effect (per-pixel blur radius from depth map)
- [x] 3.6 Implement sharpen effect (unsharp mask with Gaussian blur)
- [x] 3.7 Implement pixelate/mosaic effect (downscale + upscale with INTER_NEAREST)
- [x] 3.8 Implement bilateral blur effect (OpenCV bilateralFilter)
- [x] 3.9 Implement box blur effect (OpenCV blur with equal-weight kernel)
- [x] 3.10 Implement animated blur effect (easing-driven kernel size)
- [x] 3.11 Add blur effects to engine/effects.py
- [x] 3.12 Add property-based tests for blur effects
- [x] 3.13 Add unit tests for blur effects
- [ ] 3.14 Create examples demonstrating blur effects
- [ ] 3.15 Update documentation with blur effects

## 4. Core Implementation - Texture Effects (Priority 3)

- [x] 4.1 Implement scan lines effect (numpy row multiplication)
- [x] 4.2 Implement letterbox bars effect (numpy array assignment)
- [x] 4.3 Implement border/frame effect (Pillow rectangle drawing)
- [x] 4.4 Implement gradient overlay effect (numpy gradient + alpha blend)
- [x] 4.5 Implement image watermark effect (Pillow alpha composite)
- [x] 4.6 Implement pattern overlay effect (numpy tiling)
- [x] 4.7 Implement light leak effect (Gaussian blobs at edges)
- [x] 4.8 Implement bokeh overlay effect (Pillow circles + Gaussian blur)
- [x] 4.9 Implement dust and scratches effect (Pillow drawing primitives)
- [x] 4.10 Implement lens flare effect (radial gradient + streak lines)
- [x] 4.11 Implement progress bar overlay (numpy rectangle calculation)
- [x] 4.12 Add texture effects to engine/effects.py
- [x] 4.13 Add property-based tests for texture effects
- [x] 4.14 Add unit tests for texture effects
- [ ] 4.15 Create examples demonstrating texture effects
- [ ] 4.16 Update documentation with texture effects

## 5. Core Implementation - Stylization Effects (Priority 4)

- [x] 5.1 Implement edge detection effect (OpenCV Canny)
- [x] 5.2 Implement sketch/pencil effect (OpenCV pencilSketch)
- [x] 5.3 Implement oil painting effect (OpenCV stylization)
- [x] 5.4 Implement emboss effect (convolution with emboss kernel)
- [x] 5.5 Implement halftone effect (luminance to dot radius mapping)
- [x] 5.6 Implement chromatic aberration effect (channel offset)
- [x] 5.7 Implement glitch RGB split effect (numpy roll)
- [x] 5.8 Implement glitch block displacement effect (random row-slice offsets)
- [x] 5.9 Implement glitch scan line shift effect (per-row random offsets)
- [x] 5.10 Implement glitch color corruption effect (random channel swaps in rects)
- [x] 5.11 Implement CRT/retro effect (scan lines + barrel + channel blur)
- [x] 5.12 Implement VHS/tape distortion effect (row shifts + per-channel blur + noise)
- [x] 5.13 Implement threshold/high contrast B&W effect (numpy where)
- [x] 5.14 Implement dithering effect (Floyd-Steinberg algorithm)
- [x] 5.15 Add stylization effects to engine/effects.py
- [x] 5.16 Add property-based tests for stylization effects
- [x] 5.17 Add unit tests for stylization effects
- [ ] 5.18 Create examples demonstrating stylization effects
- [ ] 5.19 Update documentation with stylization effects

## 6. Core Implementation - Rich Transitions (Priority 5)

- [x] 6.1 Implement push left transition (both clips move left)
- [x] 6.2 Implement push right transition (both clips move right)
- [x] 6.3 Implement push up transition (both clips move up)
- [x] 6.4 Implement push down transition (both clips move down)
- [x] 6.5 Implement blinds horizontal transition (horizontal strips)
- [x] 6.6 Implement blinds vertical transition (vertical strips)
- [x] 6.7 Implement diamond wipe transition (Manhattan distance mask)
- [x] 6.8 Implement zoom through transition (scale + fade)
- [x] 6.9 Implement whip pan transition (motion blur + crossfade)
- [x] 6.10 Implement pixelate transition (downscale-upscale + crossfade)
- [x] 6.11 Implement glitch transition (RGB split + block displacement + crossfade)
- [x] 6.12 Add transitions to engine/transitions.py
- [x] 6.13 Add property-based tests for transitions
- [x] 6.14 Add unit tests for transitions
- [ ] 6.15 Create examples demonstrating transitions
- [ ] 6.16 Update documentation with transitions

## 7. Testing

- [x] 7.1 Run property-based tests for all Phase 4 effects
- [x] 7.2 Run unit tests for all Phase 4 effects
- [x] 7.3 Run integration tests with effect chains
- [x] 7.4 Run integration tests with transitions
- [ ] 7.5 Generate visual regression references for all effects
- [ ] 7.6 Verify test coverage >90%
- [ ] 7.7 Run stress tests across resolutions (640p, 1080p, 4K)
- [ ] 7.8 Run performance benchmarks for all effects
- [x] 7.9 Fix any failing tests

## 8. Documentation and Examples

- [ ] 8.1 Create Phase 4 showcase demo (examples/demo_phase4_rich_effects.py)
- [ ] 8.2 Add docstrings to all Phase 4 effects
- [ ] 8.3 Update docs/video_engine_plan.md with Phase 4 effects
- [ ] 8.4 Update docs/subtitles.md (if changes needed)
- [ ] 8.5 Update docs/architecture.md (if changes needed)
- [ ] 8.6 Create usage examples in documentation
- [ ] 8.7 Verify all examples run successfully

## 9. Integration and Validation

- [ ] 9.1 Verify all Phase 4 effects work with existing effect chain
- [ ] 9.2 Verify effects integrate with Scene DSL
- [ ] 9.3 Verify effects work with FrameRenderer
- [ ] 9.4 Verify backward compatibility with Phase 2/3 effects
- [ ] 9.5 Run full test suite and verify all pass
- [ ] 9.6 Run integration tests end-to-end
- [ ] 9.7 Create sample videos for manual QA
- [ ] 9.8 Verify performance targets met (5-100ms per effect at 1080p)
- [ ] 9.9 Verify no breaking changes to existing functionality
