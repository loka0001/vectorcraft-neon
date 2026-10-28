import argparse
import sys
import os
from PIL import Image

from .core.binarizer import binarize_image
from .core.skeleton import zhang_suen_thinning
from .core.tracer import trace_skeleton_paths
from .core.cutline import compute_cutline_contour
from .core.exporter import export_layered_svg, export_json_paths


def main():
    parser = argparse.ArgumentParser(
        description="VectorCraft-Neon: Automated Logo Centerline & Cutline Generator for Neon Signs & CNC"
    )
    parser.add_argument("input", help="Path to input logo image (PNG, JPG, BMP)")
    parser.add_argument("-o", "--output", default="output_neon.svg", help="Output SVG path (default: output_neon.svg)")
    parser.add_argument("--json", dest="json_out", default=None, help="Optional output JSON path for toolpath coordinates")
    parser.add_argument("--offset", type=int, default=25, help="Acrylic backplate offset in pixels (default: 25)")
    parser.add_argument("--tube-width", type=int, default=6, help="Simulated neon tube diameter in pixels (default: 6)")
    parser.add_argument("--min-length", type=int, default=5, help="Minimum segment pixel length to eliminate noise (default: 5)")
    parser.add_argument("--epsilon", type=float, default=1.5, help="Douglas-Peucker simplification tolerance (default: 1.5)")
    parser.add_argument("--invert", action="store_true", help="Invert foreground/background selection")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing logo: {args.input}")
    pil_img = Image.open(args.input)
    width, height = pil_img.size

    print("  [1/4] Binarizing image and calculating Otsu threshold...")
    binary_mask = binarize_image(pil_img, invert=args.invert)

    print("  [2/4] Applying Zhang-Suen morphological thinning for medial axis centerlines...")
    skeleton_mask = zhang_suen_thinning(binary_mask)

    print(f"  [3/4] Tracing vector paths (epsilon={args.epsilon})...")
    centerlines = trace_skeleton_paths(skeleton_mask, min_length=args.min_length, epsilon=args.epsilon)

    print(f"  [4/4] Computing acrylic backing cut-line offset ({args.offset}px)...")
    cutline = compute_cutline_contour(binary_mask, offset_pixels=args.offset, epsilon=args.epsilon)

    # Export SVG
    export_layered_svg(
        output_path=args.output,
        width=width,
        height=height,
        centerlines=centerlines,
        cutline=cutline,
        tube_diameter_px=args.tube_width
    )
    print(f"\n[OK] Layered SVG exported to: {args.output}")

    # Optional JSON
    if args.json_out:
        export_json_paths(args.json_out, centerlines, cutline, width, height)
        print(f"[OK] Toolpath JSON exported to: {args.json_out}")

    # Print summary metrics
    total_length = sum(
        sum(((p[i+1][0]-p[i][0])**2 + (p[i+1][1]-p[i][1])**2)**0.5 for i in range(len(p)-1))
        for p in centerlines
    )
    print("\n--- Summary Metrics ---")
    print(f"  - Extracted neon paths: {len(centerlines)}")
    print(f"  - Total neon tube length: {total_length:.1f} px")
    print(f"  - Acrylic cut-line perimeter: {len(cutline)} vertices")


if __name__ == "__main__":
    main()
