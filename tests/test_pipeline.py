import os
import tempfile
from PIL import Image, ImageDraw
from vectorcraft import (
    binarize_image,
    zhang_suen_thinning,
    trace_skeleton_paths,
    compute_cutline_contour,
    export_layered_svg,
    export_json_paths
)


def test_full_vectorcraft_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Generate test image
        img = Image.new("RGB", (150, 150), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([40, 40, 110, 110], outline=(0, 0, 0), width=6)
        
        img_path = os.path.join(tmpdir, "circle.png")
        svg_path = os.path.join(tmpdir, "circle.svg")
        json_path = os.path.join(tmpdir, "circle.json")
        img.save(img_path)

        # 2. Run steps
        binary = binarize_image(img_path)
        assert np_any_check(binary)

        skeleton = zhang_suen_thinning(binary)
        assert np_any_check(skeleton)

        centerlines = trace_skeleton_paths(skeleton, min_length=3, epsilon=1.0)
        assert len(centerlines) > 0

        cutline = compute_cutline_contour(binary, offset_pixels=10, epsilon=1.0)
        assert len(cutline) >= 4

        # 3. Export
        export_layered_svg(svg_path, 150, 150, centerlines, cutline=cutline)
        export_json_paths(json_path, centerlines, cutline, 150, 150)

        assert os.path.exists(svg_path)
        assert os.path.exists(json_path)

        with open(svg_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "layer_neon_centerline" in content
            assert "layer_acrylic_cutline" in content


def np_any_check(arr):
    return bool(arr.any())
