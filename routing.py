#!/usr/bin/env python3
import random
from typing import List, Tuple, Callable
from models import Node


class RoutingAlgorithms:
    
    def __init__(self, get_node_func: Callable[[int, int], Node], rows: int, cols: int):
        self.get_node = get_node_func
        self.rows = rows
        self.cols = cols
    
    def compute_xy_path(self, src: Node, dst: Node) -> List[Node]:
        path = [src]
        r, c = src.row, src.col
        dr, dc = dst.row, dst.col
        if c < dc:
            for x in range(c + 1, dc + 1):
                path.append(self.get_node(r, x))
        elif c > dc:
            for x in range(c - 1, dc - 1, -1):
                path.append(self.get_node(r, x))
        if r < dr:
            for y in range(r + 1, dr + 1):
                path.append(self.get_node(y, dc))
        elif r > dr:
            for y in range(r - 1, dr - 1, -1):
                path.append(self.get_node(y, dc))
        return path

    def compute_yx_path(self, src: Node, dst: Node) -> List[Node]:
        path = [src]
        r, c = src.row, src.col
        dr, dc = dst.row, dst.col
        if r < dr:
            for y in range(r + 1, dr + 1):
                path.append(self.get_node(y, c))
        elif r > dr:
            for y in range(r - 1, dr - 1, -1):
                path.append(self.get_node(y, c))
        if c < dc:
            for x in range(c + 1, dc + 1):
                path.append(self.get_node(dr, x))
        elif c > dc:
            for x in range(c - 1, dc - 1, -1):
                path.append(self.get_node(dr, x))
        return path

    def compute_minimal_oblivious_path(self, src: Node, dst: Node) -> Tuple[List[Node], List[Node]]:
        if src.col < dst.col:
            colintermediate = random.randint(src.col, dst.col)
        else:
            colintermediate = random.randint(dst.col, src.col)
        if src.row < dst.row:
            rowintermediate = random.randint(src.row, dst.row)
        else:
            rowintermediate = random.randint(dst.row, src.row)
        nodeintermediate = self.get_node(row=rowintermediate, col=colintermediate)
        path1 = self.compute_xy_path(src=src, dst=nodeintermediate)
        path2 = self.compute_xy_path(src=nodeintermediate, dst=dst)
        return path1, path2
    
    def compute_detour_path(self, src: Node, dst: Node):

        min_row = min(src.row, dst.row)
        max_row = max(src.row, dst.row)
        min_col = min(src.col, dst.col)
        max_col = max(src.col, dst.col)

        possible_cols = [c for c in range(1, self.cols + 1)
                         if c < min_col or c > max_col]

        if not possible_cols:
            possible_cols = [c for c in range(1, self.cols + 1) if c != src.col]

        colinter = random.choice(possible_cols)

        possible_rows = [r for r in range(1, self.rows + 1)
                         if r < min_row or r > max_row]

        if not possible_rows:
            possible_rows = [r for r in range(1, self.rows + 1) if r != src.row]

        rowinter = random.choice(possible_rows)

        nodeintermediate = self.get_node(rowinter, colinter)

        if nodeintermediate.col == dst.col:
            path1 = self.compute_yx_path(src, nodeintermediate)
        else:
            path1 = self.compute_xy_path(src, nodeintermediate)

        if nodeintermediate.row == src.row:
            path2 = self.compute_yx_path(nodeintermediate, dst)
        else:
            path2 = self.compute_xy_path(nodeintermediate, dst)

        return path1, path2

    def compute_detour_path_new(self, src: Node, dst: Node, p: float):

        min_row = min(src.row, dst.row)
        max_row = max(src.row, dst.row)
        min_col = min(src.col, dst.col)
        max_col = max(src.col, dst.col)

        max_dim = max(self.rows, self.cols)
        k = 0.6
        delta = int(p * max_dim * k)

        if random.random() < 0.5:
            colinter = min_col - delta
        else:
            colinter = max_col + delta

        if random.random() < 0.5:
            rowinter = min_row - delta
        else:
            rowinter = max_row + delta

        colinter = max(1, min(self.cols, colinter))
        rowinter = max(1, min(self.rows, rowinter))

        nodeinter = self.get_node(rowinter, colinter)

        path1 = self.compute_xy_path(src, nodeinter)
        path2 = self.compute_xy_path(nodeinter, dst)

        return path1, path2

    def compute_detour_path_minimal(self, src: Node, dst: Node, p: float):

        if p < 0.5:
            dx = dst.col - src.col
            dy = dst.row - src.row

            use_xy = abs(dx) >= abs(dy)

            if use_xy:
                path1 = self.compute_yx_path(src, dst)
            else:
                path1 = self.compute_xy_path(src, dst)

            return path1[:-1], [path1[-1]]

        min_row = min(src.row, dst.row)
        max_row = max(src.row, dst.row)
        min_col = min(src.col, dst.col)
        max_col = max(src.col, dst.col)

        max_dim = max(self.rows, self.cols)
        k = 0.6
        delta = int(p * max_dim * k)

        if random.random() < 0.5:
            colinter = min_col - delta
        else:
            colinter = max_col + delta

        if random.random() < 0.5:
            rowinter = min_row - delta
        else:
            rowinter = max_row + delta

        rowinter = max(1, min(self.rows, rowinter))
        colinter = max(1, min(self.cols, colinter))

        inter = self.get_node(rowinter, colinter)

        path1 = self.compute_xy_path(src, inter)
        path2 = self.compute_xy_path(inter, dst)

        return path1, path2

    def compute_HPRA_path(self, src: Node, dst: Node,p:float):
        minimal_path1, minimal_path2 = self.compute_minimal_oblivious_path(src, dst)
        detour_path1, detour_path2 = self.compute_detour_path_minimal(src, dst,p)

        r = random.random()
        if r < p:
            path1, path2 = detour_path1, detour_path2
            mode = "detour"
        else:
            path1, path2 = minimal_path1, minimal_path2
            mode = "minimal"
        return path1, path2, mode