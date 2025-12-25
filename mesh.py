#!/usr/bin/env python3
import random
from models import Node
from routing import RoutingAlgorithms


class MeshNetwork:
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.nodes = []
        self.links = []
        self.node_map = {}
        self._build_mesh()
        self.routing = RoutingAlgorithms(self.get_node, self.rows, self.cols)

    def _build_mesh(self):
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                node_id = (r - 1) * self.cols + c
                node = Node(node_id, r, c)
                self.nodes.append(node)
                self.node_map[(r, c)] = node

        for node in self.nodes:
            r, c = node.row, node.col
            if c < self.cols:
                self.links.append((node, self.get_node(r, c + 1)))
            if r < self.rows:
                self.links.append((node, self.get_node(r + 1, c)))

    def get_node(self, row: int, col: int) -> Node:
        return self.node_map[(row, col)]

    def is_path_faulty(self, full_path: list, faulty1: Node, faulty2: Node) -> bool:
        try:
            if faulty1 in full_path and faulty2 in full_path:
                i1 = full_path.index(faulty1)
                i2 = full_path.index(faulty2)
                return abs(i1 - i2) == 1
            return False
        except:
            return False

    def compute_xy_path(self, src: Node, dst: Node):
        return self.routing.compute_xy_path(src, dst)

    def compute_yx_path(self, src: Node, dst: Node):
        return self.routing.compute_yx_path(src, dst)

    def compute_minimal_oblivious_path(self, src: Node, dst: Node):
        return self.routing.compute_minimal_oblivious_path(src, dst)
    
    def compute_detour_path(self, src: Node, dst: Node):
        return self.routing.compute_detour_path(src, dst)

    def compute_HPRA_path(self, src: Node, dst: Node,p:float):
        return self.routing.compute_HPRA_path(src,dst,p)

    
