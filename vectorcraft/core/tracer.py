import math
import numpy as np


def trace_skeleton_paths(skeleton_mask, min_length=4, epsilon=1.5):
    """
    Traces 1-pixel skeleton into discrete polyline paths [(x, y), ...].
    Filters out noise segments shorter than `min_length` and applies Douglas-Peucker simplification.
    """
    # Find all skeleton pixel coordinates (y, x)
    points_y, points_x = np.where(skeleton_mask)
    if len(points_y) == 0:
        return []

    # Map of remaining coordinates
    active_points = set(zip(points_x, points_y))
    paths = []

    # 8-connectivity neighborhood offsets (dx, dy)
    neighbors = [
        (1, 0), (1, 1), (0, 1), (-1, 1),
        (-1, 0), (-1, -1), (0, -1), (1, -1)
    ]

    # Find endpoints (degree == 1) to start tracing from tips
    endpoints = []
    for px, py in active_points:
        count = sum(1 for dx, dy in neighbors if (px + dx, py + dy) in active_points)
        if count == 1:
            endpoints.append((px, py))

    # Trace starting from endpoints first
    start_candidates = endpoints + list(active_points)

    for start in start_candidates:
        if start not in active_points:
            continue

        current_path = [start]
        active_points.remove(start)
        curr = start

        while True:
            # Look for adjacent remaining pixel
            next_pt = None
            cx, cy = curr
            for dx, dy in neighbors:
                cand = (cx + dx, cy + dy)
                if cand in active_points:
                    next_pt = cand
                    break

            if next_pt:
                current_path.append(next_pt)
                active_points.remove(next_pt)
                curr = next_pt
            else:
                break

        if len(current_path) >= min_length:
            # Simplify path
            simplified = simplify_path(current_path, epsilon=epsilon)
            paths.append(simplified)

    return paths


def simplify_path(points, epsilon=1.5):
    """
    Douglas-Peucker polyline simplification algorithm.
    Reduces redundant collinear points within epsilon distance.
    """
    if len(points) <= 2:
        return points

    # Find point with max perpendicular distance from line segment (start -> end)
    start = np.array(points[0], dtype=float)
    end = np.array(points[-1], dtype=float)
    
    line_vec = end - start
    line_len = np.linalg.norm(line_vec)

    max_dist = 0.0
    index = 0

    if line_len == 0:
        # Start and end are identical point
        dists = [np.linalg.norm(np.array(p) - start) for p in points[1:-1]]
        if dists:
            max_dist = max(dists)
            index = dists.index(max_dist) + 1
    else:
        line_unit = line_vec / line_len
        normal = np.array([-line_unit[1], line_unit[0]])

        for i in range(1, len(points) - 1):
            pt = np.array(points[i], dtype=float)
            dist = abs(np.dot(pt - start, normal))
            if dist > max_dist:
                max_dist = dist
                index = i

    if max_dist > epsilon:
        left = simplify_path(points[:index + 1], epsilon)
        right = simplify_path(points[index:], epsilon)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]
