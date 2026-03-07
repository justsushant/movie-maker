"""Script to create test images for video engine testing."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_test_images():
    """Create test images in various formats and sizes."""
    fixtures_dir = Path("tests/fixtures/images")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    # Landscape images
    create_solid_color_image(fixtures_dir / "landscape_1920x1080.png", (1920, 1080), (100, 150, 200))
    create_solid_color_image(fixtures_dir / "landscape_1280x720.jpg", (1280, 720), (200, 100, 150))
    create_gradient_image(fixtures_dir / "landscape_gradient_1920x1080.png", (1920, 1080))
    
    # Portrait images
    create_solid_color_image(fixtures_dir / "portrait_1080x1920.png", (1080, 1920), (150, 200, 100))
    create_solid_color_image(fixtures_dir / "portrait_720x1280.jpg", (720, 1280), (200, 150, 100))
    
    # Square images
    create_solid_color_image(fixtures_dir / "square_1080x1080.png", (1080, 1080), (180, 180, 100))
    create_solid_color_image(fixtures_dir / "square_2048x2048.jpg", (2048, 2048), (100, 180, 180))
    
    # Small and large images
    create_solid_color_image(fixtures_dir / "small_100x100.png", (100, 100), (255, 200, 100))
    create_solid_color_image(fixtures_dir / "large_3840x2160.jpg", (3840, 2160), (120, 140, 160))
    
    # Images with text overlays
    create_text_image(fixtures_dir / "text_overlay_1920x1080.png", (1920, 1080), "TEST IMAGE")
    
    # Complex scene (checkerboard pattern)
    create_checkerboard_image(fixtures_dir / "checkerboard_1920x1080.png", (1920, 1080))
    
    print(f"Created test images in {fixtures_dir}")


def create_solid_color_image(path: Path, size: tuple[int, int], color: tuple[int, int, int]):
    """Create a solid color image."""
    img = Image.new('RGB', size, color)
    img.save(path)
    print(f"Created {path.name}")


def create_gradient_image(path: Path, size: tuple[int, int]):
    """Create a gradient image."""
    width, height = size
    
    # Create horizontal gradient
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for x in range(width):
        r = int(255 * x / width)
        g = int(128 * (1 - x / width))
        b = int(200 * x / width)
        gradient[:, x] = [r, g, b]
    
    img = Image.fromarray(gradient)
    img.save(path)
    print(f"Created {path.name}")


def create_text_image(path: Path, size: tuple[int, int], text: str):
    """Create an image with text overlay."""
    img = Image.new('RGB', size, (50, 50, 50))
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to default if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
    except:
        font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    img.save(path)
    print(f"Created {path.name}")


def create_checkerboard_image(path: Path, size: tuple[int, int], square_size: int = 100):
    """Create a checkerboard pattern image."""
    width, height = size
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            # Alternate colors
            if ((x // square_size) + (y // square_size)) % 2 == 0:
                color = (200, 200, 200)
            else:
                color = (80, 80, 80)
            
            draw.rectangle([x, y, x + square_size, y + square_size], fill=color)
    
    img.save(path)
    print(f"Created {path.name}")


if __name__ == "__main__":
    create_test_images()
