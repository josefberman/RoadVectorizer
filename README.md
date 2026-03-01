# Road Vectorizer

Convert 2D density histograms (numpy arrays) into weighted, undirected
**NetworkX** graphs — with as few edges as possible.

## Quick start

```bash
pip install -r requirements.txt
```

```python
import numpy as np
from road_vectorizer import build_graph, plot_graph_overlay

density = np.load("my_density_map.npy")   # any 2D ndarray
G = build_graph(density)                   # → nx.Graph
plot_graph_overlay(density, G)             # visualise
```

## How it works

1. **Threshold** the density map (Otsu or manual) to separate road / non-road.
2. **Skeletonize** the binary mask to 1-pixel-wide centre-lines.
3. **Detect nodes** — pixels with ≠ 2 skeleton neighbours (junctions & endpoints).
4. **Trace edges** — walk the skeleton between node pairs, collecting density values.
5. **Build graph** — each path becomes one edge with `weight = mean density`.

## API

### `build_graph(density_map, threshold=None, dilate_radius=0, prune_length=0)`

Returns an `nx.Graph`. Key edge attributes:

| Attribute      | Meaning                         |
|----------------|---------------------------------|
| `weight`       | Mean density along the path     |
| `max_density`  | Peak density along the path     |
| `length`       | Number of pixels in the path    |
| `path`         | Ordered list of (row, col)      |

### `plot_graph_overlay(density_map, graph, **kwargs)`

Draws the density heatmap with graph nodes & edges overlaid.

## Example

```bash
python examples/example_usage.py
```

Generates a synthetic road map, builds the graph, and saves `examples/output.png`.
