import json


def export_layered_svg(
    output_path,
    width,
    height,
    centerlines=None,
    contours=None,
    cutline=None,
    tube_diameter_px=6
):
    """
    Exports a structured multi-layer SVG compatible with CorelDRAW, Adobe Illustrator, and Laser/CNC CAD.
    
    Layers:
      1. neon_centerlines: Cyan single-line path representation of the neon LED tube centers.
      2. neon_tube_preview: Semi-transparent glow simulating physical LED tube width.
      3. acrylic_cutline: Red cutting path representing the acrylic backing plate offset.
      4. artwork_contours: Optional outline vectors.
    """
    centerlines = centerlines or []
    contours = contours or []
    cutline = cutline or []

    svg_parts = [
        f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}px" height="{height}px" version="1.1">',
        f'  <defs>',
        f'    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">',
        f'      <feGaussianBlur stdDeviation="3" result="blur" />',
        f'      <feMerge>',
        f'        <feMergeNode in="blur" />',
        f'        <feMergeNode in="SourceGraphic" />',
        f'      </feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <!-- Layer 0: Dark Background for Preview -->',
        f'  <rect width="100%" height="100%" fill="#121216" />'
    ]

    # Layer 1: Acrylic Cutline (Backplate)
    if cutline and len(cutline) >= 3:
        d_path = _points_to_svg_path(cutline, closed=True)
        svg_parts.extend([
            f'  <g id="layer_acrylic_cutline" stroke="#FF2A2A" stroke-width="2" fill="none" stroke-dasharray="4,4">',
            f'    <path d="{d_path}" id="cutline_path" />',
            f'  </g>'
        ])

    # Layer 2: Neon Tube Glow Simulation (Physical Tube Width)
    if centerlines:
        svg_parts.append(f'  <g id="layer_neon_tube_preview" stroke="#00F0FF" stroke-width="{tube_diameter_px}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.45" filter="url(#neon-glow)">')
        for idx, path in enumerate(centerlines):
            d_path = _points_to_svg_path(path, closed=False)
            svg_parts.append(f'    <path d="{d_path}" id="tube_glow_{idx}" />')
        svg_parts.append(f'  </g>')

    # Layer 3: Neon Centerlines (Toolpath for Production)
    if centerlines:
        svg_parts.append(f'  <g id="layer_neon_centerline" stroke="#00FFFF" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round">')
        for idx, path in enumerate(centerlines):
            d_path = _points_to_svg_path(path, closed=False)
            svg_parts.append(f'    <path d="{d_path}" id="centerline_{idx}" />')
        svg_parts.append(f'  </g>')

    # Layer 4: Original Contours (if any)
    if contours:
        svg_parts.append(f'  <g id="layer_artwork_contours" stroke="#39FF14" stroke-width="1" fill="none" stroke-linecap="round" opacity="0.8">')
        for idx, path in enumerate(contours):
            d_path = _points_to_svg_path(path, closed=True)
            svg_parts.append(f'    <path d="{d_path}" id="contour_{idx}" />')
        svg_parts.append(f'  </g>')

    svg_parts.append('</svg>')

    content = "\n".join(svg_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def export_json_paths(output_path, centerlines, cutline, width, height):
    """Exports raw vector path coordinate arrays for API integrations."""
    data = {
        "dimensions": {"width": width, "height": height},
        "centerlines": [
            [{"x": round(float(pt[0]), 2), "y": round(float(pt[1]), 2)} for pt in path]
            for path in centerlines
        ],
        "cutline": [
            {"x": round(float(pt[0]), 2), "y": round(float(pt[1]), 2)} for pt in cutline
        ],
        "stats": {
            "total_paths": len(centerlines),
            "total_tube_length_px": round(sum(_compute_path_length(p) for p in centerlines), 2)
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return output_path


def _points_to_svg_path(points, closed=False):
    """Converts a sequence of (x, y) tuples into an SVG path 'd' string."""
    if not points:
        return ""
    d_parts = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    for pt in points[1:]:
        d_parts.append(f"L {pt[0]:.2f} {pt[1]:.2f}")
    if closed:
        d_parts.append("Z")
    return " ".join(d_parts)


def _compute_path_length(path):
    """Calculates cumulative euclidean length of polyline."""
    length = 0.0
    for i in range(len(path) - 1):
        dx = path[i+1][0] - path[i][0]
        dy = path[i+1][1] - path[i][1]
        length += (dx**2 + dy**2)**0.5
    return length
