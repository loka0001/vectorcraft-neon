import numpy as np
from vectorcraft.core.cutline import compute_cutline_contour


def test_compute_cutline_contour():
    # Square in center
    mask = np.zeros((100, 100), dtype=bool)
    mask[30:70, 30:70] = True

    cutline = compute_cutline_contour(mask, offset_pixels=15, epsilon=2.0)
    assert len(cutline) >= 4
    # Cutline should enclose area larger than 30:70
    min_x = min(pt[0] for pt in cutline)
    max_x = max(pt[0] for pt in cutline)
    min_y = min(pt[1] for pt in cutline)
    max_y = max(pt[1] for pt in cutline)

    assert min_x < 30
    assert max_x > 70
    assert min_y < 30
    assert max_y > 70
