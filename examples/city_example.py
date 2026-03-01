"""
Realistic city road network example — inspired by an organic urban map.

Features:
  - Major arterial roads (curved, high density)
  - Collector roads connecting arterials
  - Minor residential streets
  - Organic curves and irregular intersections
  - Dead-end cul-de-sacs
  - A ring/bypass road
  - Varying road widths and densities
  - Realistic noise

Run:  python examples/city_example.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from road_vectorizer import build_graph, plot_graph_overlay


def draw_line(density, r0, c0, r1, c1, sigma, intensity=1.0):
    """Gaussian-blurred straight line segment."""
    yy, xx = np.mgrid[0:density.shape[0], 0:density.shape[1]]
    length = max(abs(r1 - r0), abs(c1 - c0), 1)
    for t in np.linspace(0, 1, int(length * 1.5)):
        r = r0 + t * (r1 - r0)
        c = c0 + t * (c1 - c0)
        density += intensity * np.exp(
            -(((yy - r) ** 2 + (xx - c) ** 2) / (2 * sigma ** 2))
        )


def draw_polyline(density, points, sigma, intensity=1.0):
    """Draw connected line segments through a list of (row, col) waypoints."""
    for i in range(len(points) - 1):
        draw_line(density, points[i][0], points[i][1],
                  points[i + 1][0], points[i + 1][1], sigma, intensity)


def draw_arc(density, cx, cy, radius, a0, a1, sigma, intensity=1.0):
    """Gaussian-blurred circular arc."""
    yy, xx = np.mgrid[0:density.shape[0], 0:density.shape[1]]
    n = max(int(abs(a1 - a0) * radius * 1.5), 40)
    for angle in np.linspace(a0, a1, n):
        r = cy + radius * np.sin(angle)
        c = cx + radius * np.cos(angle)
        density += intensity * np.exp(
            -(((yy - r) ** 2 + (xx - c) ** 2) / (2 * sigma ** 2))
        )


def make_city_density(size: int = 600) -> np.ndarray:
    """Generate an organic city-like road density map."""
    density = np.zeros((size, size), dtype=np.float64)
    S = size

    # ════════════════════════════════════════════════════════════════
    # MAJOR ARTERIALS — wide, high intensity, curved
    # ════════════════════════════════════════════════════════════════
    sigma_major = 4.0
    I_major = 1.3

    # A1: Horizontal arterial curving through the upper third
    draw_polyline(density, [
        (150, 0), (140, 80), (130, 160), (135, 240),
        (150, 320), (155, 400), (145, 480), (140, S),
    ], sigma_major, I_major)

    # A2: Horizontal arterial through the lower third
    draw_polyline(density, [
        (430, 0), (440, 100), (435, 200), (420, 300),
        (425, 400), (440, 500), (445, S),
    ], sigma_major, I_major)

    # A3: Vertical arterial on the left side
    draw_polyline(density, [
        (0, 120), (80, 115), (150, 120), (250, 130),
        (350, 125), (430, 120), (S, 115),
    ], sigma_major, I_major)

    # A4: Vertical arterial through the middle
    draw_polyline(density, [
        (0, 310), (100, 305), (150, 310), (250, 320),
        (350, 315), (430, 310), (S, 305),
    ], sigma_major, I_major)

    # A5: Vertical arterial on the right side
    draw_polyline(density, [
        (0, 500), (100, 495), (200, 500), (300, 510),
        (400, 505), (S, 500),
    ], sigma_major, I_major)

    # A6: Large diagonal road from top-left to bottom-right
    draw_polyline(density, [
        (30, 0), (100, 80), (200, 200), (300, 310),
        (430, 420), (S, 520),
    ], sigma_major * 0.9, I_major * 0.9)

    # ════════════════════════════════════════════════════════════════
    # RING ROAD — partial bypass arc
    # ════════════════════════════════════════════════════════════════
    draw_arc(density, 300, 280, 200, 0.8, 2.8, 3.5, 1.0)

    # ════════════════════════════════════════════════════════════════
    # COLLECTOR ROADS — medium width and density
    # ════════════════════════════════════════════════════════════════
    sigma_coll = 3.0
    I_coll = 0.8

    # C1: Curve from upper-left intersection to mid-right
    draw_polyline(density, [
        (140, 120), (120, 180), (100, 220), (90, 280),
        (100, 350), (130, 400), (150, 480),
    ], sigma_coll, I_coll)

    # C2: Road connecting lower-left to center
    draw_polyline(density, [
        (430, 120), (400, 170), (370, 200), (330, 240),
        (300, 310),
    ], sigma_coll, I_coll)

    # C3: Road from upper-middle down and curving right
    draw_polyline(density, [
        (150, 310), (200, 330), (250, 360),
        (300, 400), (350, 440), (400, 500),
    ], sigma_coll, I_coll)

    # C4: Short connector between two verticals
    draw_polyline(density, [
        (280, 130), (275, 200), (280, 280), (285, 310),
    ], sigma_coll, I_coll)

    # C5: Curved road in upper area
    draw_polyline(density, [
        (60, 310), (50, 370), (55, 430), (80, 500),
    ], sigma_coll, I_coll)

    # C6: Road from bottom-center going right
    draw_polyline(density, [
        (500, 310), (490, 370), (470, 430), (445, 500),
    ], sigma_coll, I_coll)

    # ════════════════════════════════════════════════════════════════
    # MINOR / RESIDENTIAL STREETS — thin, low density
    # ════════════════════════════════════════════════════════════════
    sigma_minor = 2.2
    I_minor = 0.5

    # R1–R8: small connecting streets
    draw_polyline(density, [(150, 120), (200, 130), (280, 130)],
                  sigma_minor, I_minor)
    draw_polyline(density, [(200, 200), (220, 250), (250, 310)],
                  sigma_minor, I_minor)
    draw_polyline(density, [(350, 315), (380, 360), (400, 400)],
                  sigma_minor, I_minor)
    draw_polyline(density, [(100, 350), (130, 310)],
                  sigma_minor, I_minor)
    draw_polyline(density, [(370, 200), (350, 250), (320, 310)],
                  sigma_minor, I_minor * 0.8)
    draw_polyline(density, [(340, 130), (330, 180), (320, 240)],
                  sigma_minor, I_minor * 0.7)
    draw_polyline(density, [(80, 500), (120, 500), (150, 480)],
                  sigma_minor, I_minor)
    draw_polyline(density, [(440, 500), (460, 540), (470, 570)],
                  sigma_minor, I_minor * 0.6)

    # ════════════════════════════════════════════════════════════════
    # DEAD-END STUBS — cul-de-sacs
    # ════════════════════════════════════════════════════════════════
    draw_line(density, 250, 130, 250, 60, sigma_minor, I_minor * 0.5)
    draw_line(density, 430, 120, 470, 60, sigma_minor, I_minor * 0.5)
    draw_line(density, 55, 430, 20, 450, sigma_minor, I_minor * 0.5)
    draw_line(density, 530, 310, 570, 340, sigma_minor, I_minor * 0.4)
    draw_line(density, 400, 400, 380, 450, sigma_minor, I_minor * 0.5)

    # ════════════════════════════════════════════════════════════════
    # NOISE — realistic background clutter
    # ════════════════════════════════════════════════════════════════
    rng = np.random.default_rng(123)
    density += rng.normal(0, 0.025, density.shape)
    density = np.clip(density, 0, None)

    return density


def main() -> None:
    print("Generating city road density map (600×600) …")
    density = make_city_density(size=600)

    print("Building graph …")
    G = build_graph(density, prune_length=5, merge_distance=5, min_edge_weight=10)

    print(f"  Nodes : {G.number_of_nodes()}")
    print(f"  Edges : {G.number_of_edges()}")

    # Summary
    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    print(f"  Weight range: {min(weights):.2f} – {max(weights):.2f}")

    out_path = Path(__file__).resolve().parent / "city_output.png"
    print(f"\nSaving overlay to {out_path}")
    plot_graph_overlay(
        density, G,
        save_path=out_path,
        show=False,
        title="City road network — graph overlay",
        node_size=25,
        edge_width=2.0,
        edge_cmap="plasma",
    )
    print("Done ✓")


if __name__ == "__main__":
    main()
