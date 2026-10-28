"""
VectorCraft-Neon Interactive Studio
Streamlit application for interactive logo vectorization and CNC cutline preview.
"""

import io
import streamlit as st
import numpy as np
from PIL import Image

from vectorcraft.core.binarizer import binarize_image
from vectorcraft.core.skeleton import zhang_suen_thinning
from vectorcraft.core.tracer import trace_skeleton_paths
from vectorcraft.core.cutline import compute_cutline_contour
from vectorcraft.core.exporter import export_layered_svg

st.set_page_config(page_title="VectorCraft-Neon Studio", page_icon="⚡", layout="wide")

st.title("⚡ VectorCraft-Neon: Automated Logo Centerline & Cutline Studio")
st.markdown(
    "Automates single-stroke neon tube centerlines and acrylic backing cutlines from raster logos. "
    "Built for neon sign manufacturing, CNC routing, and laser fabrication."
)

col_controls, col_preview = st.columns([1, 2])

with col_controls:
    st.subheader("1. Configuration")
    uploaded_file = st.file_uploader("Upload Logo (PNG, JPG)", type=["png", "jpg", "jpeg"])
    
    offset_px = st.slider("Acrylic Cutline Offset (px)", min_value=10, max_value=60, value=25, step=5)
    tube_width = st.slider("Neon Tube Diameter (px)", min_value=2, max_value=16, value=6, step=2)
    epsilon = st.slider("Vector Smoothing / Simplification", min_value=0.5, max_value=5.0, value=1.5, step=0.5)
    invert = st.checkbox("Invert Foreground / Background", value=False)
    
    st.info("💡 Generates 3 synchronized layers: Centerline toolpath, Neon tube glow preview, and Acrylic backing contour.")

with col_preview:
    st.subheader("2. Visual Transformation & SVG Preview")
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        w, h = img.size
        
        st.image(img, caption=f"Original Raster Input ({w}x{h} px)", use_container_width=True)
        
        with st.spinner("Processing morphological skeleton and vector layers..."):
            binary = binarize_image(img, invert=invert)
            skeleton = zhang_suen_thinning(binary)
            centerlines = trace_skeleton_paths(skeleton, min_length=4, epsilon=epsilon)
            cutline = compute_cutline_contour(binary, offset_pixels=offset_px, epsilon=epsilon)
            
            temp_svg_path = "temp_studio_output.svg"
            export_layered_svg(temp_svg_path, w, h, centerlines, cutline=cutline, tube_diameter_px=tube_width)
            
            with open(temp_svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
                
            st.markdown("### Output Vector Visualization")
            st.image(temp_svg_path, caption="Layered Vector Output (Cyan: Tube Centerline, Red: Acrylic Cutline)", use_container_width=True)
            
            st.download_button(
                label="📥 Download Production-Ready Layered SVG",
                data=svg_content,
                file_name="neon_production_layers.svg",
                mime="image/svg+xml"
            )
            
            # Metrics
            total_len = sum(
                sum(((p[i+1][0]-p[i][0])**2 + (p[i+1][1]-p[i][1])**2)**0.5 for i in range(len(p)-1))
                for p in centerlines
            )
            m1, m2, m3 = st.columns(3)
            m1.metric("Toolpath Segments", len(centerlines))
            m2.metric("Estimated Tube Length", f"{total_len:.0f} px")
            m3.metric("Cut-line Perimeter Vertices", len(cutline))
    else:
        st.info("Please upload a logo image to preview vectorization.")
