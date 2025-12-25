# EHPRA: Enhanced Hybrid Probabilistic Routing Algorithm for 2D Mesh NoC

This repository contains the **reference implementation, simulator, and evaluation framework** for **EHPRA (Enhanced Hybrid Probabilistic Routing Algorithm)**, a congestion- and fault-aware routing algorithm for 2D Mesh Network-on-Chip (NoC) architectures.

EHPRA is a direct extension of the previously published **HPRA** algorithm and introduces a **Smart Detour mechanism** to significantly improve routing behavior under both **hotlink** and **hotspot** traffic patterns.

---

## 📌 Key Contributions

EHPRA enhances HPRA through the following contributions:

- **Smart Detour Routing**: evaluates multiple detour candidates and selects the least congested path instead of using random detours
- **Destination-centric congestion awareness** for hotspot traffic
- **Joint fault and congestion adaptation** while remaining lightweight
- **Explainable heuristic design** (no ML, no global state)
- Full experimental comparison with baseline routing algorithms

---

## 🧠 Implemented Routing Algorithms

The simulator supports the following routing schemes:

| Algorithm | Description |
|---------|-------------|
| **XY** | Deterministic minimal routing (X then Y) |
| **Minimal-Oblivious** | Two-phase minimal routing via random intermediate |
| **Detour** | Random detour routing outside bounding box |
| **HPRA** | Hybrid Probabilistic Routing Algorithm (baseline) |
| **EHPRA** | Enhanced HPRA with Smart Detour (this work) |

---

## 🚀 What Is Smart Detour?

Unlike conventional detour routing, which selects an intermediate node randomly, **Smart Detour**:

1. Generates multiple candidate detour intermediates
2. Builds a routing path for each candidate
3. Scores each path using historical link congestion and hop count
4. Selects the detour with the minimum congestion-aware cost

This mechanism enables EHPRA to:
- bypass hot links efficiently in hotlink traffic
- enter hotspot regions from less congested directions

A detailed explanation is provided in the accompanying documentation file:

```
Smart Detour Explanation (EHPRA)
```

---

## 📁 Project Structure

```
.
├── routing.py        # Routing algorithms (XY, HPRA, EHPRA, Smart Detour)
├── mesh.py           # 2D mesh topology and routing interface
├── models.py         # Core data structures (Node)
├── tests.py          # Fault injection, simulations, and evaluation
├── gui.py            # Interactive mesh visualization (optional)
├── main.py           # GUI entry point
├── README.md         # This file
```

---

## ▶️ Running the Simulator

### 1) Install Dependencies

```bash
pip install numpy matplotlib
```

(tkinter is usually bundled with Python)

---

### 2) Run Interactive GUI (Optional)

```bash
python main.py
```

The GUI allows you to:
- select source and destination nodes
- switch between routing algorithms
- visually compare routing paths

---

### 3) Run Experimental Evaluation

```bash
python tests.py
```

This will:
- compare **XY, Minimal, Detour, HPRA, and EHPRA**
- evaluate both **Hotlink** and **Hotspot** traffic patterns
- generate bar charts and performance plots

Results are saved in the `Results/` directory.

---

## 📊 Evaluation Metrics

The following metrics are collected:

- **Total Fault Count**
- **Average Hop Count**
- **Overall Cost** (weighted combination of faults and hops)
- **Probability evolution (p)** for HPRA and EHPRA

Overall Cost is computed as:

```
Cost = w_fault × normalized_faults + w_hop × normalized_hops
```

---

## 🧪 Traffic Patterns

- **Hotlink**: fixed source–destination pair with persistent traffic
- **Hotspot**: multiple random sources communicating with a single destination

Both patterns are standard benchmarks for NoC routing evaluation.

---

## 📖 Research Context

This repository is intended for:

- Network-on-Chip (NoC) routing research
- Fault-tolerant and congestion-aware routing studies
- Reproducible experimental evaluation
- Extension toward journal-quality publications

EHPRA is designed to remain **lightweight and hardware-feasible**, relying only on simple counters and deterministic routing primitives.

---

## 📜 Citation

If you use this code or build upon it in academic work, please cite:

```
A. Akhbari, H. Khoojooyan, M. Tarighi,
"HPRA: Hybrid Probabilistic Routing Algorithm for 2D Mesh NoC",
International Conference on Electrical, Computer and Mechanical Engineering.
```

(An updated citation for EHPRA will be added upon publication.)

---

## ✨ Notes

- EHPRA is a **research-oriented simulator**, not a hardware-optimized router
- The design emphasizes clarity, reproducibility, and explainability
- Extensions to 3D Mesh and QoS-aware routing are natural future directions

---

## 🔧 License

This project is provided for **research and educational use**.
Please provide appropriate attribution when using or extending the code.

