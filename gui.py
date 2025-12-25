#!/usr/bin/env python3
import tkinter as tk
from mesh import MeshNetwork


class MeshGUIFancy:
    
    def __init__(self, mesh: MeshNetwork, node_radius: int = 18,
                 padding: int = 60, spacing: int = 90):
        self.mesh = mesh
        self.node_radius = node_radius
        self.padding = padding
        self.spacing = spacing

        self.root = tk.Tk()
        self.root.title("Mesh Network Simulator")

        self.top_bar = tk.Frame(self.root, bg="#181825")
        self.top_bar.pack(fill="x")

        self.cancel_btn = tk.Button(self.top_bar, text="Cancel Routing",
                                    bg="#f38ba8", fg="#1e1e2e",
                                    font=("Segoe UI", 10, "bold"),
                                    command=self.reset_routing)
        self.cancel_btn.pack(side="left", padx=10, pady=5)
        
        self.reroute_btn = tk.Button(self.top_bar, text="Reroute",
                                    bg="#94e2d5", fg="#1e1e2e",
                                    font=("Segoe UI", 10, "bold"),
                                    command=self.redraw_paths)
        self.reroute_btn.pack(side="left", padx=5, pady=5)
        

        self.routing_algo = tk.StringVar()
        self.routing_algo.set("XY")
        self.algo_label = tk.Label(self.top_bar, text="Algo:", fg="#cdd6f4", bg="#181825")
        self.algo_label.pack(side="left", padx=(20, 5))
        self.algo_menu = tk.OptionMenu(self.top_bar, self.routing_algo, 
                                       "XY", "YX", "Both", "minimal-oblivious", 
                                       "detour", "HPRA", command=self.on_algo_change)
        self.algo_menu.config(bg="#313244", fg="#cdd6f4", 
                              activebackground="#45475a", activeforeground="#cdd6f4")
        self.algo_menu["menu"].config(bg="#313244", fg="#cdd6f4")
        self.algo_menu.pack(side="left", padx=5, pady=5)

        self.info_label = tk.Label(self.top_bar, text="Click on a node to select source",
                                   fg="#cdd6f4", bg="#181825")
        self.info_label.pack(side="left", padx=20)

        width = padding * 2 + (mesh.cols - 1) * spacing
        height = padding * 2 + (mesh.rows - 1) * spacing

        self.canvas = tk.Canvas(self.root, width=width, height=height,
                                bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.positions = {}
        self.node_items = {}
        self.src_node = None
        self.dst_node = None

        self.draw_background_grid()
        self.draw_mesh()

    def reset_routing(self):
        self.src_node = None
        self.dst_node = None
        self.canvas.delete("path_xy")
        self.canvas.delete("path_yx")
        self.canvas.delete("path_minimal1")
        self.canvas.delete("path_minimal2")
        self.canvas.delete("path_detour1")
        self.canvas.delete("path_detour2")
        self.canvas.delete("path_p1")
        self.canvas.delete("path_p2")
        self.info_label.config(text=f"Click on a node to select source (Algo: {self.routing_algo.get()})")

    def compute_position(self, row, col):
        return self.padding + (col - 1) * self.spacing, self.padding + (row - 1) * self.spacing

    def draw_background_grid(self):
        self.canvas.delete("grid")
        w = int(self.canvas.winfo_width() or 1)
        h = int(self.canvas.winfo_height() or 1)
        spacing = 30
        for x in range(0, w, spacing):
            self.canvas.create_line(x, 0, x, h, fill="#313244", tags="grid")
        for y in range(0, h, spacing):
            self.canvas.create_line(0, y, w, h, fill="#313244", tags="grid")

    def draw_mesh(self, redraw_paths_flag=True):
        self.canvas.delete("node_items")
        self.canvas.delete("link")
        self.positions.clear()
        self.node_items.clear()

        for node in self.mesh.nodes:
            self.positions[node.id] = self.compute_position(node.row, node.col)

        for a, b in self.mesh.links:
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#585b70", width=2,tags="link")

        for node in self.mesh.nodes:
            x, y = self.positions[node.id]
            r = self.node_radius
            

            node_color = "#89b4fa"

            
            shadow = self.canvas.create_oval(x - r + 3, y - r + 3, x + r + 3, y + r + 3,
                                             fill="#11111b", outline="",tags="node_items")
            item = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                           fill=node_color, outline="#b4befe", width=2,
                                           tags=(f"node_{node.id}","node_items"))

            node_label = f"{node.col},{node.row}"

            text_color = "#ffffff"
            font_size = 9
            text = self.canvas.create_text(x, y, text=node_label,
                                           fill=text_color, font=("Segoe UI", font_size, "bold"),tags="node_items")
            self.node_items[node.id] = (item, text, shadow)
            self.canvas.tag_bind(item, "<Button-1>", lambda e, n=node: self.on_node_click(n))

        if self.src_node and self.dst_node and redraw_paths_flag:
            self.redraw_paths(update_congestion=False)

    def draw_path_xy(self, path):
        for a, b in zip(path[:-1], path[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill="#f38ba8", width=4, tags="path_xy")

    def draw_path_yx(self, path):
        for a, b in zip(path[:-1], path[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2,
                                    fill="#94e2d5", width=4, tags="path_yx")
    
    def draw_path_minimal_oblivious(self, path1, path2):
        for a, b in zip(path1[:-1], path1[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#18c0f3", width=4, tags="path_minimal1")
        for a, b in zip(path2[:-1], path2[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#f31823", width=4, tags="path_minimal2")
    
    def draw_path_detour(self, path1, path2):
        for a, b in zip(path1[:-1], path1[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#18c0f3", width=4, tags="path_detour1")
        for a, b in zip(path2[:-1], path2[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#f31823", width=4, tags="path_detour2")

    def draw_path_HPRA(self, path1, path2):
        for a, b in zip(path1[:-1], path1[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#18c0f3", width=4, tags="path_p1")
        for a, b in zip(path2[:-1], path2[1:]):
            x1, y1 = self.positions[a.id]
            x2, y2 = self.positions[b.id]
            self.canvas.create_line(x1, y1, x2, y2, fill="#f31823", width=4, tags="path_p2")

    def redraw_paths(self, update_congestion=False):
        self.canvas.delete("path_xy")
        self.canvas.delete("path_yx")
        self.canvas.delete("path_minimal1")
        self.canvas.delete("path_minimal2")
        self.canvas.delete("path_detour1")
        self.canvas.delete("path_detour2")
        self.canvas.delete("path_p1")
        self.canvas.delete("path_p2")
        if not (self.src_node and self.dst_node):
            return
        algo = self.routing_algo.get()
        if algo == "XY":
            xy = self.mesh.compute_xy_path(self.src_node, self.dst_node)
            self.draw_path_xy(xy)
            hops = len(xy) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row})  "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row})  "
                     f"Hops(XY): {hops}  Algo: XY"
            )
        elif algo == "YX":
            yx = self.mesh.compute_yx_path(self.src_node, self.dst_node)
            self.draw_path_yx(yx)
            hops = len(yx) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row})  "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row})  "
                     f"Hops(YX): {hops}  Algo: YX"
            )
        elif algo == "Both":
            xy = self.mesh.compute_xy_path(self.src_node, self.dst_node)
            yx = self.mesh.compute_yx_path(self.src_node, self.dst_node)
            self.draw_path_xy(xy)
            self.draw_path_yx(yx)
            hops_xy = len(xy) - 1
            hops_yx = len(yx) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row})  "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row})  "
                     f"Hops(XY): {hops_xy}  Hops(YX): {hops_yx}  Algo: Both"
            )
        elif algo == "minimal-oblivious":
            path1, path2 = self.mesh.compute_minimal_oblivious_path(self.src_node, self.dst_node)
            self.draw_path_minimal_oblivious(path1=path1, path2=path2)
            hops_minimal = len(path1) + len(path2) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row}) "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row}) "
                     f"Hops(minimal-oblivious): {hops_minimal} Algo: minimal-oblivious "
            )
        elif algo == "detour":
            path1, path2 = self.mesh.compute_detour_path(self.src_node, self.dst_node)
            self.draw_path_detour(path1=path1, path2=path2)
            hops_minimal = len(path1) + len(path2) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row}) "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row}) "
                     f"Hops(detour): {hops_minimal} Algo: detour "
            )
        elif algo == "HPRA":
            path1, path2, mode= self.mesh.compute_HPRA_path(
                self.src_node, self.dst_node,p=0.5
            )
            self.draw_path_HPRA(path1=path1, path2=path2)
            hops_minimal = len(path1) + len(path2) - 1
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row}) "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row}) "
                     f"Hops(p): {hops_minimal} Algo: p Mode:{mode} p={0.5:.3f}"
            )

    def on_algo_change(self, value):
        if self.src_node and self.dst_node:
            self.redraw_paths()
        else:
            self.info_label.config(
                text=f"Click on a node to select source (Algo: {self.routing_algo.get()})"
            )

    def on_node_click(self, node):
        if self.src_node is None or (self.src_node and self.dst_node):
            self.src_node = node
            self.dst_node = None
            self.canvas.delete("path_xy")
            self.canvas.delete("path_yx")
            self.info_label.config(
                text=f"Source selected: ({node.col},{node.row}) - choose destination (Algo: {self.routing_algo.get()})"
            )
        else:
            self.dst_node = node
            if self.dst_node.id == self.src_node.id:
                self.reset_routing()
                return
            self.redraw_paths(update_congestion=True)

    def on_node_enter(self, node):
        item, text, shadow = self.node_items[node.id]
        self.canvas.itemconfigure(item, fill="#f9e2af", outline="#f38ba8")
        self.canvas.itemconfigure(text, fill="#1e1e2e")
        algo = self.routing_algo.get()
        if self.src_node and not self.dst_node:
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row})  "
                     f"Hover: ({node.col},{node.row})  Algo: {algo}"
            )
        elif self.src_node and self.dst_node:
            self.info_label.config(
                text=f"Source: ({self.src_node.col},{self.src_node.row})  "
                     f"Dest: ({self.dst_node.col},{self.dst_node.row})  "
                     f"Hover: ({node.col},{node.row})  Algo: {algo}"
            )
        else:
            self.info_label.config(
                text=f"Hover: ({node.col},{node.row})  Algo: {algo}"
            )

    def on_node_leave(self, node):
        item, text, shadow = self.node_items[node.id]
        self.canvas.itemconfigure(item, fill="#89b4fa", outline="#b4befe")
        self.canvas.itemconfigure(text, fill="#1e1e2e")
        if self.src_node and self.dst_node:
            self.redraw_paths()
        elif self.src_node and not self.dst_node:
            self.info_label.config(
                text=f"Source selected: ({self.src_node.col},{self.src_node.row}) - choose destination (Algo: {self.routing_algo.get()})"
            )
        else:
            self.info_label.config(
                text=f"Click on a node to select source (Algo: {self.routing_algo.get()})"
            )

    def on_resize(self, event):
        self.draw_background_grid()
        self.draw_mesh(redraw_paths_flag=False)

    def run(self):
        self.root.mainloop()

