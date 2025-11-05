"""
Dijkstra's Path Finder (GUI) - Varanasi example
Save as: dijkstra_varanasi_gui.py
Requires: networkx, matplotlib
Run: python dijkstra_varanasi_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# ---------------------------
# Graph data (Varanasi + nearby cities)
# Distances here are illustrative — replace with real values if you want.
# ---------------------------
GRAPH_DATA = {
    'Varanasi': {'Sarnath': 10, 'Prayagraj': 125, 'Jaunpur': 55, 'Mirzapur': 75, 'Ghazipur': 70, 'Bhadohi': 40},
    'Sarnath': {'Varanasi': 10, 'Jaunpur': 65, 'Ghazipur': 80},
    'Prayagraj': {'Varanasi': 125, 'Mirzapur': 90},
    'Jaunpur': {'Varanasi': 55, 'Sarnath': 65, 'Ghazipur': 70},
    'Mirzapur': {'Varanasi': 75, 'Prayagraj': 90, 'Bhadohi': 60},
    'Ghazipur': {'Varanasi': 70, 'Jaunpur': 70},
    'Bhadohi': {'Varanasi': 40, 'Mirzapur': 60}
}

# ---------------------------
# Dijkstra implementation
# ---------------------------
def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    distances[start] = 0
    heap = [(0, start)]
    while heap:
        dist_u, u = heapq.heappop(heap)
        if dist_u > distances[u]:
            continue
        for v, w in graph[u].items():
            alt = dist_u + w
            if alt < distances[v]:
                distances[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))
    return distances, prev

def get_path(prev, start, target):
    if prev[target] is None and start != target:
        return None
    path = []
    u = target
    while u is not None:
        path.append(u)
        u = prev[u]
    path.reverse()
    if path[0] == start:
        return path
    return None

# ---------------------------
# GUI / Visualization
# ---------------------------
class DijkstraGUI:
    def __init__(self, master, graph_data):
        self.master = master
        self.master.title("Dijkstra's Path Finder - Varanasi")
        self.graph_data = graph_data
        self.G = nx.Graph()
        self._build_graph()

        # Top frame: controls
        ctrl = ttk.Frame(master, padding=8)
        ctrl.pack(side='top', fill='x')

        ttk.Label(ctrl, text="Start:").pack(side='left')
        self.start_var = tk.StringVar(value=list(self.graph_data.keys())[0])
        self.start_cb = ttk.Combobox(ctrl, textvariable=self.start_var, values=list(self.graph_data.keys()), state='readonly', width=15)
        self.start_cb.pack(side='left', padx=(5, 12))

        ttk.Label(ctrl, text="Target:").pack(side='left')
        self.target_var = tk.StringVar(value=list(self.graph_data.keys())[1])
        self.target_cb = ttk.Combobox(ctrl, textvariable=self.target_var, values=list(self.graph_data.keys()), state='readonly', width=15)
        self.target_cb.pack(side='left', padx=(5, 12))

        run_btn = ttk.Button(ctrl, text="Find Shortest Path", command=self.run_dijkstra)
        run_btn.pack(side='left', padx=4)

        reset_btn = ttk.Button(ctrl, text="Reset View", command=self.reset_view)
        reset_btn.pack(side='left', padx=4)

        # Bottom frame: matplotlib canvas
        self.fig, self.ax = plt.subplots(figsize=(7,5))
        plt.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.05)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # layout positions for consistent drawing
        self.pos = self._compute_positions()
        self._draw_graph()

    def _build_graph(self):
        for u, nbrs in self.graph_data.items():
            for v, w in nbrs.items():
                self.G.add_edge(u, v, weight=w)

    def _compute_positions(self):
        # Use spring layout seeded for stable positions; you can set custom positions to align with a real map
        pos = nx.spring_layout(self.G, seed=42)
        # Move 'Varanasi' to approximate center for clarity (optional)
        if 'Varanasi' in pos:
            pos['Varanasi'] = (0.0, 0.0)
        return pos

    def _draw_graph(self, highlight_path=None):
        self.ax.clear()
        # Draw edges with labels
        nx.draw_networkx_edges(self.G, pos=self.pos, ax=self.ax)
        nx.draw_networkx_nodes(self.G, pos=self.pos, ax=self.ax, node_size=600, node_color='lightblue')
        nx.draw_networkx_labels(self.G, pos=self.pos, ax=self.ax, font_size=9)
        # edge labels (weights)
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos=self.pos, edge_labels=edge_labels, ax=self.ax, font_size=8)
        # highlight path edges/nodes if provided
        if highlight_path and len(highlight_path) >= 2:
            path_edges = list(zip(highlight_path, highlight_path[1:]))
            nx.draw_networkx_nodes(self.G, pos=self.pos, nodelist=highlight_path, ax=self.ax, node_color='orange', node_size=700)
            nx.draw_networkx_edges(self.G, pos=self.pos, edgelist=path_edges, ax=self.ax, width=3.0, edge_color='red')
        self.ax.set_title("Varanasi Area - Shortest Path Visualization")
        self.ax.axis('off')
        self.canvas.draw()

    def run_dijkstra(self):
        start = self.start_var.get()
        target = self.target_var.get()
        if start == target:
            messagebox.showinfo("Info", "Start and Target are same: distance 0.")
            self._draw_graph(highlight_path=[start])
            return
        distances, prev = dijkstra(self.graph_data, start)
        if distances[target] == float('inf'):
            messagebox.showwarning("No path", f"No path from {start} to {target}")
            return
        path = get_path(prev, start, target)
        # show a small popup with distance & path
        msg = f"Shortest path: {' -> '.join(path)}\nDistance: {distances[target]}"
        messagebox.showinfo("Result", msg)
        # draw graph with highlighted path
        self._draw_graph(highlight_path=path)

    def reset_view(self):
        self._draw_graph()

# ---------------------------
# Main
# ---------------------------
def main():
    root = tk.Tk()
    app = DijkstraGUI(root, GRAPH_DATA)
    root.mainloop()

if __name__ == "__main__":
    main()