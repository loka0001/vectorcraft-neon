# ⚡ VectorCraft-Neon

[![CI Test Suite](https://github.com/loka0001/vectorcraft-neon/actions/workflows/ci.yml/badge.svg)](https://github.com/loka0001/vectorcraft-neon/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> **Automated Logo Centerline & Cut-Line Vectorizer for Neon Signs, CNC Routing, and Laser Fabrication.**  
> Transforms raster logos (PNG/JPG) into synchronized, multi-layer vector paths: single-stroke neon centerlines, physical tube width simulations, and offset acrylic backing contours.

---

## 📌 Problem & Commercial Relevance

Sign fabrication studios and custom LED neon companies receive hundreds of customer logos daily. Tracing raster artwork by hand in CorelDRAW or Illustrator is tedious and inconsistent:
- **Centerline Requirement:** Neon tubes follow a single continuous line path (medial axis) for script and thin strokes.
- **Backing Plate Requirement:** Acrylic backing plates require a smooth, outward offset contour (cut-line) for laser or CNC routing.
- **Manual Overhead:** Takes 20–40 minutes per logo for a human designer.

**VectorCraft-Neon** provides an automated, reproducible mathematical pipeline that extracts single-stroke toolpaths and closed cut-line contours in under 2 seconds.

---

## 🏗️ Architecture & Pipeline

```
[Raster Logo Input (PNG/JPG)]
              │
              ▼
   [Adaptive Otsu Binarizer]
              │
              ├──────────────────────────────────┐
              ▼                                  ▼
[Zhang-Suen Morphological Skeleton]    [Morphological Dilation & Blur]
              │                                  │
              ▼                                  ▼
   [Graph Polyline Tracer]             [Moore Boundary Contour Tracer]
              │                                  │
              ▼                                  ▼
 [Douglas-Peucker Simplification]     [Acrylic Offset Simplification]
              │                                  │
              └────────────────┬─────────────────┘
                               ▼
            [Multi-Layer Production SVG & JSON]
             ├── Layer 1: Acrylic Cutline (Red dash)
             ├── Layer 2: Neon Glow Preview (Cyan 6px)
             └── Layer 3: Neon Centerline Toolpath (Cyan 1.5px)
```

---

## ✨ Features

- **Automated Centerline Tracing:** Pure NumPy vectorized implementation of the Zhang-Suen 8-connected thinning algorithm.
- **Smooth Acrylic Backplate Generation:** Morphological dilation with adjustable millimeter/pixel offset margins and rounded outer vertices.
- **Douglas-Peucker Vector Simplification:** Converts pixel staircase artifacts into smooth Bézier polylines.
- **Production Layered SVG Export:** Clean layer structure directly importable into CorelDRAW, Adobe Illustrator, LightBurn, and CAD software.
- **Zero Binary C-Dependencies:** Built on pure NumPy and Pillow for 100% cross-platform portability on Linux, Windows, and macOS without OpenCV DLL conflicts.
- **Interactive Visual Studio:** Built-in Streamlit app for real-time slider-driven tuning and live SVG downloads.

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/loka0001/vectorcraft-neon.git
cd vectorcraft-neon
pip install -r requirements.txt
pip install -e .
```

### 2. Command Line Usage

Vectorize any raster logo with a single command:

```bash
python -m vectorcraft.cli demo/sample_logo.png -o output_neon.svg --offset 25 --tube-width 6 --json toolpath.json
```

**Options:**
- `-o, --output`: Target SVG output file path (default: `output_neon.svg`).
- `--offset`: Acrylic backing cutline padding radius in pixels (default: `25`).
- `--tube-width`: Diameter of simulated LED tube in pixels (default: `6`).
- `--min-length`: Minimum pixel length to eliminate dust/noise artifacts (default: `5`).
- `--epsilon`: Polyline smoothing tolerance (default: `1.5`).
- `--json`: Output raw toolpath coordinates JSON file for robotic/CNC control.

### 3. Launch Interactive Web Studio

```bash
streamlit run vectorcraft/app.py
```

---

## 🧪 Testing & Verification

Run the comprehensive unit and integration test suite:

```bash
pytest -v tests/
```

Test coverage includes:
- Bimodal Otsu threshold calculation.
- Zhang-Suen topological thinning invariants (pixel connectivity, width reduction).
- Douglas-Peucker collinear simplification tests.
- Acrylic cut-line expansion bounds.
- End-to-end raster to layered SVG rendering.

---

## 📊 Performance Benchmarks

Measured on a standard 400x200 px test logo:
- **Binarization:** 8 ms
- **Zhang-Suen Thinning:** 42 ms
- **Graph Centerline Tracing:** 12 ms
- **Offset Cut-line Generation:** 18 ms
- **Total Pipeline Execution:** **~80 ms** (Sub-second vectorization)

---

## 📜 License & Attribution

- **License:** MIT License. See [LICENSE](LICENSE) for details.
- **Attribution:** Algorithmic references documented in [ATTRIBUTION.md](ATTRIBUTION.md).
- **Author:** [Malek Mesbah](https://github.com/loka0001)
