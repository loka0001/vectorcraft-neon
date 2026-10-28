import os
import sys

# Ensure vectorcraft can be imported without pip install -e .
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from vectorcraft.core.binarizer import binarize_image
from vectorcraft.core.skeleton import zhang_suen_thinning
from vectorcraft.core.tracer import trace_skeleton_paths
from vectorcraft.core.cutline import compute_cutline_contour
from vectorcraft.core.exporter import export_layered_svg, export_json_paths


def generate_synthetic_logo(output_path, text="NEON", width=400, height=200):
    """Draws a clean raster sign logo for testing and demonstration."""
    # Create white canvas
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle border
    draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=15, outline=(0, 0, 0), width=6)

    # Draw geometric icon (lightning bolt / star)
    cx, cy = 80, height // 2
    bolt_pts = [
        (cx, cy - 40), (cx - 20, cy + 5), (cx - 5, cy + 5),
        (cx - 15, cy + 40), (cx + 25, cy - 5), (cx + 5, cy - 5)
    ]
    draw.polygon(bolt_pts, fill=(0, 0, 0))

    # Draw sample text stroke simulation
    draw.line([(140, cy - 35), (140, cy + 35)], fill=(0, 0, 0), width=6) # N leg
    draw.line([(140, cy - 35), (175, cy + 35)], fill=(0, 0, 0), width=6) # N diag
    draw.line([(175, cy - 35), (175, cy + 35)], fill=(0, 0, 0), width=6) # N leg

    # Letter O (ellipse)
    draw.ellipse([200, cy - 35, 260, cy + 35], outline=(0, 0, 0), width=6)

    # Letter W / V
    draw.line([(280, cy - 35), (300, cy + 35)], fill=(0, 0, 0), width=6)
    draw.line([(300, cy + 35), (320, cy - 35)], fill=(0, 0, 0), width=6)
    draw.line([(320, cy - 35), (340, cy + 35)], fill=(0, 0, 0), width=6)
    draw.line([(340, cy + 35), (360, cy - 35)], fill=(0, 0, 0), width=6)

    img.save(output_path)
    return output_path


def run_demo():
    demo_dir = os.path.dirname(os.path.abspath(__file__))
    sample_logo_path = os.path.join(demo_dir, "sample_logo.png")
    output_svg_path = os.path.join(demo_dir, "sample_neon_output.svg")
    output_json_path = os.path.join(demo_dir, "sample_toolpath.json")

    print(f"1. Generating synthetic sign logo: {sample_logo_path}")
    generate_synthetic_logo(sample_logo_path, text="NOW", width=420, height=200)

    print("2. Running VectorCraft-Neon pipeline...")
    img = Image.open(sample_logo_path)
    w, h = img.size

    binary = binarize_image(img)
    skeleton = zhang_suen_thinning(binary)
    centerlines = trace_skeleton_paths(skeleton, min_length=4, epsilon=1.5)
    cutline = compute_cutline_contour(binary, offset_pixels=20, epsilon=1.5)

    export_layered_svg(output_svg_path, w, h, centerlines, cutline=cutline, tube_diameter_px=6)
    export_json_paths(output_json_path, centerlines, cutline, w, h)

    print(f"3. Layered SVG saved: {output_svg_path}")
    print(f"4. Toolpath JSON saved: {output_json_path}")
    print(f"   -> Extracted Centerline Segments: {len(centerlines)}")
    print(f"   -> Acrylic Cutline Vertices: {len(cutline)}")
    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
