"""
road_vectorizer — Convert 2D density histograms into weighted NetworkX graphs.

Quick start::

    import numpy as np
    from road_vectorizer import build_graph, plot_graph_overlay

    density = np.load("my_density_map.npy")
    G = build_graph(density)
    plot_graph_overlay(density, G)
"""

from .graph_builder import build_graph, compute_road_coverage
from .visualization import plot_graph_overlay

__all__ = ["build_graph", "compute_road_coverage", "plot_graph_overlay"]
