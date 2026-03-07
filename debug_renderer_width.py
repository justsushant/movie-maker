"""Test actual renderer width calculation."""

from PIL import ImageFont, ImageDraw, Image

# Test different font sizes and character width ratios
test_strings = [
    "This is a longer paragraph that intentionally contains several clauses and transitions,",
    "what?! \"No way,\" she said; then paused and smiled",
    "WWWWWWWWWW",  # Wide characters
    "iiiiiiiiii",  # Narrow characters
    "Hello World",
]

for font_size in [40, 60, 80]:
    print(f"\nFont size: {font_size}px")
    print("="*80)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    img = Image.new('RGB', (1920, 1080))
    draw = ImageDraw.Draw(img)
    
    for text in test_strings:
        bbox = draw.textbbox((0, 0), text, font=font)
        actual_width = bbox[2] - bbox[0]
        
        # Test different estimation ratios
        for ratio in [0.5, 0.55, 0.6, 0.65, 0.7]:
            avg_char_px = int(font_size * ratio)
            estimated_width = len(text) * avg_char_px
            error_pct = abs(estimated_width - actual_width) / actual_width * 100
            
            if ratio == 0.55:  # Current ratio
                marker = " <-- CURRENT"
            else:
                marker = ""
            
            if ratio == 0.5:
                print(f"\n  Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                print(f"  Length: {len(text)} chars, Actual width: {actual_width}px")
            
            print(f"    Ratio {ratio}: est={estimated_width}px, error={error_pct:.1f}%{marker}")
