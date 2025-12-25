#!/usr/bin/env python3

import random
import matplotlib.pyplot as plt
import numpy as np
from numpy.matlib import maximum
from collections import defaultdict
from mesh import MeshNetwork
from collections import deque
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm

random.seed(74)
np.random.seed(74)

def add_bar_labels(ax, values, fmt, fontsize=11):
    ymax = max(values)
    ax.set_ylim(0, ymax * 1.15)

    for i, v in enumerate(values):
        ax.text(
            i,
            v + 0.03 * ymax,
            fmt.format(v),
            ha="center",
            va="bottom",
            fontsize=fontsize,
            clip_on=False
        )

def plot_results(title_prefix,
                 result_prob,
                 result_min,
                 result_det,
                 result_xy,
                 w_fault=0.8,
                 w_hop=0.2):
    labels = ["HPRA", "Minimal", "Detour", "XY"]

    avg_hops = [
        result_prob["avg_hops"],
        result_min["avg_hops"],
        result_det["avg_hops"],
        result_xy["avg_hops"],
    ]

    total_faults = [
        result_prob["total_faults"],
        result_min["total_faults"],
        result_det["total_faults"],
        result_xy["total_faults"],
    ]

    max_faults = max(total_faults)
    max_hops = max(avg_hops)

    faults_norm = [f / max_faults for f in total_faults]
    hops_norm = [h / max_hops for h in avg_hops]

    overall_cost = [
        w_fault * fn + w_hop * hn
        for fn, hn in zip(faults_norm, hops_norm)
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0][0]
    bars = ax.bar(labels, avg_hops, color=["#4F81BD", "#C0504D", "#9BBB59", "#FF9900"])
    ax.set_title(f"{title_prefix} - Average Hop Count")
    ax.set_ylabel("Avg hops")
    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, avg_hops, "{:.2f}", fontsize=11)

    ax = axes[0][1]
    bars = ax.bar(labels, total_faults, color=["#4F81BD", "#C0504D", "#9BBB59", "#FF9900"])
    ax.set_title(f"{title_prefix} - Fault Count")
    ax.set_ylabel("Faults")
    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, total_faults, "{:.0f}", fontsize=11)

    ax = axes[1][0]
    p_vals = np.array(result_prob["p_values"])

    if len(p_vals) > 0:
        step = max(1, len(p_vals) // 2000)
        p_down = p_vals[::step]
        x_down = np.arange(len(p_down)) * step

        window = 5
        p_smooth = np.convolve(p_down, np.ones(window)/window, mode="same")

        ax.scatter(x_down, p_smooth, s=10, color="#1f77b4", alpha=0.8)
    else:
        ax.text(0.5, 0.5, "No p-values", ha="center", va="center")

    ax.set_title(f"{title_prefix} - P Value Evolution (Scatter)")
    ax.set_xlabel("Trial")
    ax.set_ylabel("p")
    ax.grid(True, alpha=0.3)

    ax = axes[1][1]
    bars = ax.bar(labels, overall_cost,
                  color=["#4F81BD", "#C0504D", "#9BBB59", "#FF9900"])
    ax.set_title(f"{title_prefix} - Overall Cost")
    ax.set_ylabel("Cost (Lower is Better)")
    ax.grid(axis="y", alpha=0.3)

    add_bar_labels(ax, overall_cost, "{:.3f}", fontsize=11)

    plt.savefig(f"Results/{title_prefix}-figure.pdf", bbox_inches="tight")
    plt.tight_layout()
    plt.show()

    print("\n=== SUMMARY ===")
    for name, r in zip(labels, [result_prob, result_min, result_det, result_xy]):
        print(f"{name:15} -> faults={r['total_faults']}, avg hops={r['avg_hops']:.2f}")

def simulate_algorithm(
        traffic_pattern: str,
        alg_name: str,
        mesh,
        src,
        dst,
        trials=1_000_000,
        fault_period=10,
        fault_duration=5,
        hot_threshold=3,
        dynamic_src_fn=None,
        p_up=0.01,
        p_down=0.01,
        p_decay=0.0005,
    ):

    routing = mesh.routing
    id_to_node = {node.id: node for node in mesh.nodes}

    def manhattan(a, b):
        return abs(a.row - b.row) + abs(a.col - b.col)

    link_usage = defaultdict(int)
    current_faulty_link = None
    remaining_fault_trials = 0

    hops_per_trial = []
    faults_per_trial = []
    p_values = []

    fault_count = 0
    p = 0.0

    for t in range(1, trials + 1):

        if dynamic_src_fn is not None:
            curr_src = dynamic_src_fn()
        else:
            curr_src = src

        had_fault = 0

        if alg_name == "HPRA":
            path1, path2, mode = routing.compute_HPRA_path(curr_src, dst, p)

        elif alg_name == "minimal":
            path1, path2 = routing.compute_minimal_oblivious_path(curr_src, dst)

        elif alg_name == "detour":
            path1, path2 = routing.compute_detour_path(curr_src, dst)

        elif alg_name == "xy":
            full = routing.compute_xy_path(curr_src, dst)
            path1, path2 = full, []

        else:
            raise ValueError("Unknown algorithm")

        full_path = path1 + path2

        for u, v in zip(full_path, full_path[1:]):
            key = tuple(sorted((u.id, v.id)))
            link_usage[key] += 1

        if current_faulty_link is not None:
            f1, f2 = current_faulty_link
            if mesh.is_path_faulty(full_path, f1, f2):
                had_fault = 1
                fault_count += 1

                if alg_name == "HPRA":
                    if mode == "minimal":
                        p = min(1.0, p + p_up)
                    else:
                        p = max(0.0, p - p_down)

            remaining_fault_trials -= 1
            if remaining_fault_trials <= 0:
                current_faulty_link = None

        if alg_name == "HPRA":
            p = max(0.0, p - p_decay)
            p_values.append(p)

        hops_per_trial.append(len(full_path))
        faults_per_trial.append(had_fault)

        if t % fault_period == 0:
            candidates = []
            for (id1, id2), cnt in link_usage.items():
                if cnt > hot_threshold:
                    n1 = id_to_node[id1]
                    n2 = id_to_node[id2]
                    dist = min(manhattan(n1, dst), manhattan(n2, dst))
                    candidates.append((dist, -cnt, n1, n2))
            if candidates:
                candidates.sort(key=lambda x: (x[0], x[1]))
                _, _, n1, n2 = candidates[0]
                current_faulty_link = (n1, n2)
                remaining_fault_trials = fault_duration

        if t % 20000 == 0:
            print(f"[{traffic_pattern}] Trial {t} for {alg_name}")

    return {
        "faults_per_trial": faults_per_trial,
        "hops_per_trial": hops_per_trial,
        "p_values": p_values,
        "total_faults": fault_count,
        "avg_hops": float(np.mean(hops_per_trial)),
    }

def simulate_algorithm_heatmap(
        traffic_pattern: str,
        alg_name: str,
        mesh,
        src,
        dst,
        trials=50000,
        fault_period=10,
        fault_duration=5,
        hot_threshold=3,
        dynamic_src_fn=None,
        p_up=0.01,
        p_down=0.01,
        p_decay=0.0005):

    routing = mesh.routing
    id_to_node = {node.id: node for node in mesh.nodes}

    usage = np.zeros((mesh.rows, mesh.cols), dtype=int)
    link_usage = defaultdict(int)

    current_faulty_link = None
    remaining_fault_trials = 0

    p = 0.0
    fault_count = 0

    def manhattan(a, b):
        return abs(a.row - b.row) + abs(a.col - b.col)

    for t in range(1, trials + 1):

        curr_src = dynamic_src_fn() if dynamic_src_fn else src
        had_fault = 0

        if alg_name == "HPRA":
            path1, path2, mode = routing.compute_HPRA_path(curr_src, dst, p)
        elif alg_name == "minimal":
            path1, path2 = routing.compute_minimal_oblivious_path(curr_src, dst)
        elif alg_name == "detour":
            path1, path2 = routing.compute_detour_path(curr_src, dst)
        elif alg_name == "xy":
            full = routing.compute_xy_path(curr_src, dst)
            path1, path2 = full, []
        else:
            raise ValueError(f"Unknown algorithm: {alg_name}")

        full_path = path1 + path2

        for node in full_path:
            usage[node.row - 1, node.col - 1] += 1

        for u, v in zip(full_path, full_path[1:]):
            link_usage[tuple(sorted((u.id, v.id)))] += 1

        if current_faulty_link:
            f1, f2 = current_faulty_link
            if mesh.is_path_faulty(full_path, f1, f2):
                had_fault = 1
                fault_count += 1
                if alg_name == "HPRA":
                    if mode == "minimal":
                        p = min(1.0, p + p_up)
                    else:
                        p = max(0.0, p - p_down)
            remaining_fault_trials -= 1
            if remaining_fault_trials <= 0:
                current_faulty_link = None

        if alg_name == "HPRA":
            p = max(0.0, p - p_decay)

        if t % fault_period == 0:
            candidates = []
            for (id1, id2), cnt in link_usage.items():
                if cnt > hot_threshold:
                    n1 = id_to_node[id1]
                    n2 = id_to_node[id2]
                    dist = min(manhattan(n1, dst), manhattan(n2, dst))
                    candidates.append((dist, -cnt, n1, n2))

            if candidates:
                candidates.sort(key=lambda x: (x[0], x[1]))
                _, _, n1, n2 = candidates[0]
                current_faulty_link = (n1, n2)
                remaining_fault_trials = fault_duration

        if t % (trials // 5) == 0:
            print(f"[Heatmap SIM][{traffic_pattern}] {alg_name}: {t}/{trials}")

    return usage

def test_heatmap_all_algorithms(traffic_pattern="Hotlink", trials=50000):
    print("\n=== Heatmap Test Started ===")

    mesh = MeshNetwork(16, 16)

    if traffic_pattern == "Hotlink":
        src = mesh.get_node(2, 3)
        dst = mesh.get_node(5, 6)
        dynamic_src = None

    elif traffic_pattern == "Hotspot":
        dst = mesh.get_node(mesh.rows // 2, mesh.cols // 2)

        def dynamic_src():
            while True:
                n = random.choice(mesh.nodes)
                if n.id != dst.id:
                    return n

        src = None

    else:
        raise ValueError("traffic_pattern must be Hotlink or Hotspot")

    algorithms = ["HPRA", "minimal", "detour", "xy"]
    usage_maps = {}

    for alg in algorithms:
        print(f"[SIM] Running {alg} ...")
        usage_maps[alg] = simulate_algorithm_heatmap(
            traffic_pattern,
            alg,
            mesh,
            src,
            dst,
            trials=trials,
            dynamic_src_fn=dynamic_src
        )

    vmax = max(usage_maps[a].max() for a in algorithms)
    cmap = "viridis"

    for alg in algorithms:

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)

        usage = usage_maps[alg]

        im = ax.imshow(
            usage,
            origin='upper',
            cmap='viridis',
            norm=LogNorm(vmin=1, vmax=vmax),
            interpolation='nearest',
            aspect='equal'
        )

        ax.set_aspect('equal')
        ax.set_adjustable('box')

        ax.set_title(f"{traffic_pattern} - {alg.capitalize()} Routing Heatmap", fontsize=16)
        ax.set_xlabel("Column (1–16)", fontsize=12)
        ax.set_ylabel("Row (1–16)", fontsize=12)

        ax.set_xticks(np.arange(16))
        ax.set_xticklabels(np.arange(1, 17), fontsize=10)

        ax.set_yticks(np.arange(16))
        ax.set_yticklabels(np.arange(1, 17), fontsize=10)

        ax.set_xticks(np.arange(16) - 0.5, minor=True)
        ax.set_yticks(np.arange(16) - 0.5, minor=True)
        ax.grid(which='minor', linestyle=':', color='white', linewidth=0.5)

        cbar = fig.colorbar(im, fraction=0.046, pad=0.04)
        cbar.set_label("Node Visit Frequency", fontsize=12)

        plt.savefig(f"Results/{traffic_pattern}-{alg}-heatmap.pdf", bbox_inches="tight")
        plt.tight_layout()
        plt.show()

    print("\n=== Heatmap Test Finished ===")

def test_hotlink_four_algorithms():
    mesh = MeshNetwork(16, 16)
    src = mesh.get_node(2, 3)
    dst = mesh.get_node(5, 6)

    result_prob = simulate_algorithm("Hotlink", "HPRA", mesh, src, dst)
    result_min  = simulate_algorithm("Hotlink", "minimal", mesh, src, dst)
    result_det  = simulate_algorithm("Hotlink", "detour", mesh, src, dst)
    result_xy   = simulate_algorithm("Hotlink", "xy", mesh, src, dst)

    plot_results("Hotlink", result_prob, result_min, result_det, result_xy)

def test_hotspot_four_algorithms():
    mesh = MeshNetwork(16, 16)
    dst = mesh.get_node(8, 8)

    def random_src():
        while True:
            n = random.choice(mesh.nodes)
            if n.id != dst.id:
                return n

    result_prob = simulate_algorithm("Hotspot", "HPRA", mesh, None, dst, dynamic_src_fn=random_src)
    result_min  = simulate_algorithm("Hotspot", "minimal", mesh, None, dst, dynamic_src_fn=random_src)
    result_det  = simulate_algorithm("Hotspot", "detour", mesh, None, dst, dynamic_src_fn=random_src)
    result_xy   = simulate_algorithm("Hotspot", "xy", mesh, None, dst, dynamic_src_fn=random_src)

    plot_results("Hotspot", result_prob, result_min, result_det, result_xy)

def test_hotlink_hotspot_compare():

    mesh = MeshNetwork(rows=16, cols=16)

    src_hl = mesh.get_node(row=2, col=3)
    dst_hl = mesh.get_node(row=5, col=6)

    result_prob_hl = simulate_algorithm("Hotlink","HPRA", mesh, src_hl, dst_hl)
    result_min_hl  = simulate_algorithm("Hotlink","minimal",mesh, src_hl, dst_hl)
    result_det_hl  = simulate_algorithm("Hotlink","detour",mesh, src_hl, dst_hl)

    result_hotlink = {
        "prob": result_prob_hl,
        "min":  result_min_hl,
        "det":  result_det_hl
    }

    dst_hs = mesh.get_node(row=(mesh.rows // 2), col=(mesh.cols // 2))

    def random_src():
        while True:
            n = random.choice(mesh.nodes)
            if n.id != dst_hs.id:
                return n

    result_prob_hs = simulate_algorithm("Hotspot","HPRA", mesh, None, dst_hs, dynamic_src_fn=random_src)
    result_min_hs  = simulate_algorithm("Hotspot","minimal",mesh, None, dst_hs, dynamic_src_fn=random_src)
    result_det_hs  = simulate_algorithm("Hotspot","detour",mesh, None, dst_hs, dynamic_src_fn=random_src)

    result_hotspot = {
        "prob": result_prob_hs,
        "min":  result_min_hs,
        "det":  result_det_hs
    }

    plot_results("Hotlink",result_prob_hl,result_min_hl,result_det_hl)
    plot_results("Hotspot",result_prob_hs,result_min_hs,result_det_hs)

    print("\n========== SUMMARY ==========")
    print("Hotlink:")
    print(f"  HPRA: faults={result_prob_hl['total_faults']}, avg hops={result_prob_hl['avg_hops']:.2f}")
    print(f"  Minimal:       faults={result_min_hl['total_faults']}, avg hops={result_min_hl['avg_hops']:.2f}")
    print(f"  Detour:        faults={result_det_hl['total_faults']}, avg hops={result_det_hl['avg_hops']:.2f}")

    print("\nHotspot:")
    print(f"  HPRA: faults={result_prob_hs['total_faults']}, avg hops={result_prob_hs['avg_hops']:.2f}")
    print(f"  Minimal:       faults={result_min_hs['total_faults']}, avg hops={result_min_hs['avg_hops']:.2f}")
    print(f"  Detour:        faults={result_det_hs['total_faults']}, avg hops={result_det_hs['avg_hops']:.2f}")


test_hotlink_four_algorithms()
test_hotspot_four_algorithms()
test_heatmap_all_algorithms("Hotlink",trials=1_000_000)
test_heatmap_all_algorithms("Hotspot",trials=1_000_000)






