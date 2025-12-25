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

    def compute_detour_path_smart(self,src: Node,dst: Node,p: float,link_usage: dict,k_candidates: int = 12,lam: float = 0.2,):

        # --- Helper: bounding box of (src, dst)
        min_row = min(src.row, dst.row)
        max_row = max(src.row, dst.row)
        min_col = min(src.col, dst.col)
        max_col = max(src.col, dst.col)

        # --- Helper: compute path score (congestion + hop penalty)
        def path_score(full_path):
            if not full_path or len(full_path) == 1:
                return 0.0

            def manhattan(n1, n2):
                return abs(n1.row - n2.row) + abs(n1.col - n2.col)

            congestion = 0.0
            for u, v in zip(full_path, full_path[1:]):
                key = tuple(sorted((u.id, v.id)))
                base = float(link_usage.get(key, 0))

                # distance-to-dst weighting (hotspot-friendly)
                d = min(manhattan(u, dst), manhattan(v, dst))
                # هرچه به dst نزدیک‌تر، وزن بیشتر
                w = 1.0 + (1.0 / (d + 1.0)) * 6.0   # 1 تا حدود 7
                congestion += w * base

            hops = len(full_path) - 1
            return congestion + lam * hops

        # --- Candidate generation:
        # Use p to control detour distance (bigger p => further detour)
        max_dim = max(self.rows, self.cols)
        k = 0.6  # same spirit as your compute_detour_path_minimal
        delta = int(p * max_dim * k)

        # Make sure delta is at least 1 so we actually go outside the box sometimes
        # (especially if p is small)
        delta = max(1, delta)

        candidates = []
        seen = set()

        # We try to generate intermediates outside bounding box.
        # If mesh is too small or box covers all rows/cols, we fall back safely.
        tries = 0
        max_tries = k_candidates * 10

        while len(candidates) < k_candidates and tries < max_tries:
            tries += 1
        
            # فقط یکی از محورها را خارج کن تا detour کنترل‌شده باشد
            if random.random() < 0.5:
                # خارج کردن ستون، ردیف را داخل محدوده src/dst نگه دار
                if random.random() < 0.5:
                    colinter = min_col - delta
                else:
                    colinter = max_col + delta
                rowinter = random.randint(min_row, max_row)
            else:
                # خارج کردن ردیف، ستون را داخل محدوده src/dst نگه دار
                if random.random() < 0.5:
                    rowinter = min_row - delta
                else:
                    rowinter = max_row + delta
                colinter = random.randint(min_col, max_col)
        
            rowinter = max(1, min(self.rows, rowinter))
            colinter = max(1, min(self.cols, colinter))

            # We want it ideally outside the bounding box; if clamping brings it back in,
            # we still allow but try other samples too.
            key_rc = (rowinter, colinter)
            if key_rc in seen:
                continue
            seen.add(key_rc)
            candidates.append(key_rc)

        # Fallback: if we could not generate enough distinct candidates,
        # add a few "edge" candidates near borders (still deterministic-ish)
        if not candidates:
            border_points = [
                (1, 1),
                (1, self.cols),
                (self.rows, 1),
                (self.rows, self.cols),
            ]
            for rc in border_points:
                if rc not in seen:
                    candidates.append(rc)
                    seen.add(rc)
                if len(candidates) >= k_candidates:
                    break

        # --- Evaluate each candidate and pick best
        best_score = float("inf")
        best_path1 = None
        best_path2 = None

        for (r_i, c_i) in candidates:
            inter = self.get_node(r_i, c_i)

            # Build path via intermediate.
            # You can choose XY for both legs (consistent with your other functions),
            # or add small heuristics similar to compute_detour_path().
            path1 = self.compute_xy_path(src, inter)
            path2 = self.compute_xy_path(inter, dst)

            full_path = path1 + path2[1:] if path2 else path1  # avoid double-count inter
            score = path_score(full_path)

            if score < best_score:
                best_score = score
                best_path1 = path1
                best_path2 = path2

        # Safety fallback: in unexpected cases return classic detour
        if best_path1 is None or best_path2 is None:
            return self.compute_detour_path(src, dst)

        return best_path1, best_path2

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

    def compute_EHPRA_path(self, src: Node, dst: Node,p:float,link_usage:dict):
        minimal_path1, minimal_path2 = self.compute_minimal_oblivious_path(src, dst)
        detour_path1, detour_path2 = self.compute_detour_path_smart(src, dst,p,link_usage=link_usage)

        r = random.random()
        if r < p:
            path1, path2 = detour_path1, detour_path2
            mode = "detour"
        else:
            path1, path2 = minimal_path1, minimal_path2
            mode = "minimal"
        return path1, path2, mode