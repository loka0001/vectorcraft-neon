import numpy as np
from vectorcraft.core.tracer import trace_skeleton_paths, simplify_path


def test_simplify_path_straight_line():
    # Straight line with 10 collinear points
    points = [(i, i * 2) for i in range(10)]
    simplified = simplify_path(points, epsilon=0.5)
    # Collinear points should simplify to just start and end
    assert len(simplified) == 2
    assert simplified[0] == points[0]
    assert simplified[-1] == points[-1]


def test_trace_skeleton_paths():
    mask = np.zeros((40, 40), dtype=bool)
    # Draw simple vertical line
    mask[5:35, 20] = True

    paths = trace_skeleton_paths(mask, min_length=5, epsilon=1.0)
    assert len(paths) >= 1
    # Check bounds of path
    p = paths[0]
    assert len(p) >= 2
