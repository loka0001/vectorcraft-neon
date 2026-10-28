import numpy as np
from vectorcraft.core.skeleton import zhang_suen_thinning


def test_zhang_suen_thinning_bar():
    # Create a thick vertical bar (width = 10, height = 30)
    mask = np.zeros((50, 50), dtype=bool)
    mask[10:40, 20:30] = True

    skeleton = zhang_suen_thinning(mask)

    # Skeleton must have reduced pixel count dramatically
    orig_count = np.sum(mask)
    skel_count = np.sum(skeleton)
    assert skel_count < orig_count
    # Width of skeleton along interior rows should be 1 or 2 pixels
    for row in range(16, 34):
        row_pixels = np.sum(skeleton[row, :])
        assert 1 <= row_pixels <= 2
