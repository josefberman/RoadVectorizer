"""
Example: generate a synthetic road-like density map and convert it to a graph.

Run from the project root:

    python examples/example_usage.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib

# Use a non-interactive backend so the script works headlessly
matplotlib.use("Agg")

# Ensure the package is importable when running from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from road_vectorizer import build_graph, plot_graph_overlay


def make_synthetic_density(
    size: int = 200,
    road_width: int = 6,
    noise_level: float = 0.05,
) -> np.ndarray:
    """Create a simple synthetic 2D density map with road-like structures.

    The map contains:
    * A horizontal road
    * A vertical road
    * Two diagonal roads
    * A curved road (quarter-circle arc)

    All roads have Gaussian cross-section profiles and additive noise.
    """
    density = np.zeros((size, size), dtype=np.float64)
    yy, xx = np.mgrid[0:size, 0:size]
    sigma = road_width / 2.0

    # --- Straight roads ---------------------------------------------------
    # Horizontal road at row = size // 3
    h_row = size // 3
    density += np.exp(-((yy - h_row) ** 2) / (2 * sigma**2))

    # Vertical road at col = size // 2
    v_col = size // 2
    density += np.exp(-((xx - v_col) ** 2) / (2 * sigma**2))

    # Diagonal road from top-left to bottom-right
    density += np.exp(-((yy - xx) ** 2) / (2 * (sigma * np.sqrt(2)) ** 2)) * 0.8

    # Diagonal road from top-right to bottom-left
    density += (
        np.exp(-((yy - (size - 1 - xx)) ** 2) / (2 * (sigma * np.sqrt(2)) ** 2))
        * 0.6
    )

    # --- Curved road (arc) ------------------------------------------------
    cx, cy, radius = size * 0.75, size * 0.75, size * 0.30
    dist_from_arc = np.abs(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - radius)
    # Keep only the top-left quadrant of the circle
    arc_mask = (xx < cx) & (yy < cy)
    arc = np.exp(-(dist_from_arc**2) / (2 * sigma**2)) * arc_mask * 0.9
    density += arc

    # --- Noise ------------------------------------------------------------
    rng = np.random.default_rng(42)
    density += rng.normal(0, noise_level, density.shape)
    density = np.clip(density, 0, None)

    return density


def main() -> None:
    print("Generating synthetic density map …")
    density = make_synthetic_density(size=200)

    print("Building graph …")
    G = build_graph(density, prune_length=3, merge_distance=5)

    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")

    # Print per-edge info
    print("\nEdge details:")
    for u, v, data in G.edges(data=True):
        print(
            f"  {u} — {v}  |  weight={data['weight']:.3f}  "
            f"max_density={data['max_density']:.3f}  length={data['length']}"
        )

    out_path = Path(__file__).resolve().parent / "output.png"
    print(f"\nSaving overlay to {out_path}")
    plot_graph_overlay(density, G, save_path=out_path, show=False)
    print("Done ✓")


if __name__ == "__main__":
    main()
