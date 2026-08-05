#!/usr/bin/env python3
"""Convert social media SVGs to PNG using svglib + reportlab."""
import os
import glob

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
except ImportError:
    print("ERROR: svglib or reportlab not installed")
    exit(1)

SVG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-kit")
PNG_DIR = os.path.join(SVG_DIR, "png")
os.makedirs(PNG_DIR, exist_ok=True)

svg_files = glob.glob(os.path.join(SVG_DIR, "*.svg"))
count = 0

for svg_path in svg_files:
    name = os.path.splitext(os.path.basename(svg_path))[0]
    png_path = os.path.join(PNG_DIR, f"{name}.png")
    
    try:
        drawing = svg2rlg(svg_path)
        if drawing is None:
            print(f"  ERROR {name} (svg2rlg returned None)")
            continue
        
        renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=150)
        count += 1
        print(f"  OK {name}.png")
    except Exception as e:
        print(f"  ERROR {name}: {e}")

print(f"\n{count} PNG files generated in {PNG_DIR}")
