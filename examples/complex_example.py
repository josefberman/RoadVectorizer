"""
Complex example: a realistic road-like density map featuring:
  - A grid of streets (varied density)
  - A roundabout
  - Curved / winding roads
  - T-junctions and dead-ends
  - Varying density levels per road
  - Background noise

Run from the project root:

    python examples/complex_example.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from road_vectorizer import build_graph, plot_graph_overlay


def draw_line(density, r0, c0, r1, c1, sigma, intensity=1.0):
    """Draw a Gaussian-blurred straight line segment on the density map."""
    yy, xx = np.mgrid[0:density.shape[0], 0:density.shape[1]]
    length = max(abs(r1 - r0), abs(c1 - c0), 1)
    for t in np.linspace(0, 1, length * 2):
        r = r0 + t * (r1 - r0)
        c = c0 + t * (c1 - c0)
        density += intensity * np.exp(
            -(((yy - r) ** 2 + (xx - c) ** 2) / (2 * sigma ** 2))
        )


def draw_arc(density, cx, cy, radius, angle_start, angle_end, sigma, intensity=1.0):
    """Draw a Gaussian-blurred circular arc on the density map."""
    yy, xx = np.mgrid[0:density.shape[0], 0:density.shape[1]]
    n_steps = int(abs(angle_end - angle_start) * radius * 2)
    for angle in np.linspace(angle_start, angle_end, max(n_steps, 50)):
        r = cy + radius * np.sin(angle)
        c = cx + radius * np.cos(angle)
        density += intensity * np.exp(
            -(((yy - r) ** 2 + (xx - c) ** 2) / (2 * sigma ** 2))
        )


def make_complex_density(size: int = 400) -> np.ndarray:
    """Build a complex synthetic road network density map.

    Features:
    - A main grid of 3 horizontal × 3 vertical roads
    - A roundabout at the center
    - A winding road going from left to the roundabout
    - A diagonal highway
    - A curved on-ramp / interchange
    - Dead-end stubs
    - Varying road intensities (major vs. minor roads)
    - Noise
    """
    density = np.zeros((size, size), dtype=np.float64)
    sigma = 3.0  # road half-width in pixels

    # ── Main grid ────────────────────────────────────────────────────
    # Horizontal roads at rows 80, 200, 320
    for row, intensity in [(80, 0.7), (200, 1.0), (320, 0.6)]:
        draw_line(density, row, 0, row, size - 1, sigma, intensity)

    # Vertical roads at cols 100, 200, 300
    for col, intensity in [(100, 0.8), (200, 1.0), (300, 0.7)]:
        draw_line(density, 0, col, size - 1, col, sigma, intensity)

    # ── Roundabout at centre (200, 200) ──────────────────────────────
    roundabout_r = 25
    draw_arc(density, 200, 200, roundabout_r, 0, 2 * np.pi, sigma, 0.9)

    # ── Diagonal highway: top-left to bottom-right ───────────────────
    draw_line(density, 30, 30, 370, 370, sigma * 1.3, 1.2)

    # ── Winding road from left edge to roundabout ────────────────────
    # Made up of several short arcs
    pts = [
        (250, 0), (250, 40), (240, 70), (220, 90),
        (210, 120), (205, 150), (200, 175),
    ]
    for i in range(len(pts) - 1):
        draw_line(density, pts[i][0], pts[i][1],
                  pts[i + 1][0], pts[i + 1][1], sigma, 0.8)

    # ── Curved on-ramp: from diagonal to the top horizontal ──────────
    draw_arc(density, 150, 130, 50, -0.5, 1.2, sigma, 0.6)

    # ── T-junction stub: dead-end going up from row 320, col 350 ─────
    draw_line(density, 320, 350, 260, 350, sigma, 0.5)

    # ── Another dead-end: small street from row 80, col 50 going down
    draw_line(density, 80, 50, 140, 50, sigma, 0.4)

    # ── Curved bypass road on the right side ─────────────────────────
    draw_arc(density, 350, 200, 60, -1.0, 1.0, sigma, 0.65)

    # ── Noise ────────────────────────────────────────────────────────
    rng = np.random.default_rng(42)
    density += rng.normal(0, 0.03, density.shape)
    density = np.clip(density, 0, None)

    return density


def main() -> None:
    print("Generating complex density map (400×400) …")
    density = make_complex_density(size=400)

    print("Building graph …")
    G = build_graph(density, prune_length=5, merge_distance=5)

    print(f"  Nodes : {G.number_of_nodes()}")
    print(f"  Edges : {G.number_of_edges()}")

    # Print summary
    print("\nEdge summary (top 30 by weight):")
    edges_sorted = sorted(G.edges(data=True), key=lambda e: e[2]["weight"], reverse=True)
    for u, v, data in edges_sorted[:30]:
        print(
            f"  {u} — {v}  |  weight={data['weight']:.3f}  "
            f"length={data['length']}"
        )
    if len(edges_sorted) > 30:
        print(f"  … and {len(edges_sorted) - 30} more edges")

    out_path = Path(__file__).resolve().parent / "complex_output.png"
    print(f"\nSaving overlay to {out_path}")
    plot_graph_overlay(
        density, G,
        save_path=out_path,
        show=False,
        title="Complex road network — graph overlay",
        node_size=30,
        edge_width=1.8,
    )
    print("Done ✓")


if __name__ == "__main__":
    main()
