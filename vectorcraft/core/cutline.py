import numpy as np
from PIL import Image, ImageFilter
from .tracer import simplify_path


def compute_cutline_contour(binary_mask, offset_pixels=25, epsilon=2.0):
    """
    Computes an outer acrylic backing cut-line contour with an offset margin around the logo.
    
    Args:
        binary_mask: 2D boolean numpy array (foreground = True).
        offset_pixels: Radius of the offset padding around the logo artwork.
        epsilon: Polyline simplification tolerance.
        
    Returns:
        List of (x, y) points representing the closed outer cut-line polygon.
    """
    if not np.any(binary_mask):
        return []

    # Pad image to allow outward offset
    pad = int(offset_pixels * 1.5) + 10
    padded = np.pad(binary_mask.astype(np.uint8) * 255, pad, mode='constant', constant_values=0)

    # Use Pillow's MaxFilter (morphological dilation) to expand boundary smoothly
    pil_img = Image.fromarray(padded)
    # Filter size must be odd
    filter_size = max(3, int(offset_pixels * 2) | 1)
    dilated = pil_img.filter(ImageFilter.MaxFilter(size=filter_size))

    # Apply slight Gaussian blur and threshold to round sharp inner vertices
    smoothed = dilated.filter(ImageFilter.GaussianBlur(radius=max(1.0, offset_pixels * 0.15)))
    dilated_mask = np.array(smoothed) > 120

    # Extract outer boundary contour using Moore-Neighbor boundary tracing
    contour = trace_outer_boundary(dilated_mask)

    if not contour:
        return []

    # Shift coordinates back by padding amount
    adjusted_contour = [(x - pad, y - pad) for (x, y) in contour]
    
    # Simplify to smooth curves
    simplified = simplify_path(adjusted_contour, epsilon=epsilon)
    # Ensure closed loop
    if simplified[0] != simplified[-1]:
        simplified.append(simplified[0])

    return simplified


def trace_outer_boundary(binary_mask):
    """Traces the outer boundary pixels of the primary connected shape using Moore neighborhood."""
    # Find first top-most, left-most pixel
    ys, xs = np.where(binary_mask)
    if len(ys) == 0:
        return []

    # Start at the top-left foreground pixel
    start_idx = np.lexsort((xs, ys))[0]
    start_pt = (int(xs[start_idx]), int(ys[start_idx]))

    # Moore neighborhood 8 directions starting North
    dirs = [
        (0, -1), (1, -1), (1, 0), (1, 1),
        (0, 1), (-1, 1), (-1, 0), (-1, -1)
    ]

    boundary = [start_pt]
    curr = start_pt
    back_dir = 6 # West

    max_steps = binary_mask.size
    steps = 0

    while steps < max_steps:
        steps += 1
        found_next = False
        # Search clockwise starting from the direction we came from + 1
        start_dir_idx = (back_dir + 1) % 8
        for i in range(8):
            d_idx = (start_dir_idx + i) % 8
            dx, dy = dirs[d_idx]
            nx, ny = curr[0] + dx, curr[1] + dy
            if 0 <= ny < binary_mask.shape[0] and 0 <= nx < binary_mask.shape[1]:
                if binary_mask[ny, nx]:
                    curr = (nx, ny)
                    boundary.append(curr)
                    back_dir = (d_idx + 4) % 8
                    found_next = True
                    break

        if not found_next or curr == start_pt:
            break

    return boundary
