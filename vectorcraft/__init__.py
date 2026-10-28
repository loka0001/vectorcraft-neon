"""
VectorCraft-Neon: Automated Logo Centerline & Cut-Path Vectorizer
Designed for neon sign makers, CNC routing, and laser fabrication.
"""

__version__ = "1.0.0"
__author__ = "Malek Mesbah"

from .core.binarizer import binarize_image
from .core.skeleton import zhang_suen_thinning
from .core.tracer import trace_skeleton_paths, simplify_path
from .core.cutline import compute_cutline_contour
from .core.exporter import export_layered_svg, export_json_paths

__all__ = [
    "binarize_image",
    "zhang_suen_thinning",
    "trace_skeleton_paths",
    "simplify_path",
    "compute_cutline_contour",
    "export_layered_svg",
    "export_json_paths",
]
