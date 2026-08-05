#!/usr/bin/env python3
"""Convert SVG logos to PNG using svglib + reportlab."""
import os
import glob

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
except ImportError:
    print("ERROR: svglib or reportlab not installed")
    print("Run: uv run --with svglib --with reportlab python svg_to_png.py")
    exit(1)

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(BRAND_DIR, "png")
os.makedirs(PNG_DIR, exist_ok=True)

# Sizes for different use cases
SIZES = {
    "dsc-flat-mk-navy": [16, 32, 64, 128, 256, 512, 1024],
    "dsc-flat-mk-white": [16, 32, 64, 128, 256, 512, 1024],
    "dsc-flat-mk-gold": [16, 32, 64, 128, 256, 512, 1024],
    "dsc-hexagon-badge": [128, 256, 512, 1024],
    "dsc-horizontal-lockup": [256, 512, 1024, 2048],
    "dsc-wordmark": [256, 512, 1024, 2048],
    "dsc-social-profile": [400],
    "dsc-social-cover": [1584],
    "dsc-social-post-feasibility": [1080],
    "dsc-social-post-automation": [1080],
    "dsc-social-post-training": [1080],
    "dsc-email-signature": [400],
    "dsc-watermark": [200],
}

count = 0
for svg_name, sizes in SIZES.items():
    svg_path = os.path.join(BRAND_DIR, f"{svg_name}.svg")
    if not os.path.exists(svg_path):
        print(f"  SKIP {svg_name}.svg (not found)")
        continue

    for size in sizes:
        png_name = f"{svg_name}-{size}.png"
        png_path = os.path.join(PNG_DIR, png_name)

        try:
            drawing = svg2rlg(svg_path)
            if drawing is None:
                print(f"  ERROR {svg_name} (svg2rlg returned None)")
                break

            # Scale to target size
            scale = size / max(drawing.width, drawing.height)
            drawing.width = size
            drawing.height = size
            drawing.scale(scale, scale)

            renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=150)
            count += 1
            if size == sizes[0]:
                print(f"  OK {svg_name} -> {size}px")
        except Exception as e:
            print(f"  ERROR {svg_name} {size}px: {e}")
            break

print(f"\n{count} PNG files generated in {PNG_DIR}")
