# International Conference on Electrical, Computer and Mechanical Engineering (EESCONF)

## EHPRA: Enhanced Hybrid Probabilistic Routing Algorithm with Smart Detour for Fault- and Congestion-Aware 2D Mesh NoC

**Amir Ahkbari**
MSc. student of Amirkabir University of Technology

**Hosein Khoojooyan**
MSc. student of Amirkabir University of Technology

**Dr. Mohsen Tarighi**
Professor at Amirkabir University of Technology

### Abstract
Network-on-Chip (NoC) routing in many-core systems must satisfy two conflicting requirements: low-latency packet delivery and resilience against congestion-induced failures in heavily used links. This paper presents EHPRA (Enhanced Hybrid Probabilistic Routing Algorithm), a lightweight extension of HPRA for 2D mesh NoCs that introduces a Smart Detour mechanism to improve routing quality under hotlink and hotspot traffic conditions. Unlike random detour approaches, EHPRA evaluates multiple intermediate candidates and selects the least congested path using a destination-aware congestion score plus a hop penalty. The algorithm preserves HPRA’s probabilistic adaptation concept while improving path selection quality through local link-usage history. A simulation framework on a 16×16 mesh compares EHPRA against HPRA, Minimal-Oblivious, Random Detour, and XY routing over one million trials per scenario. Results show that EHPRA achieves the lowest fault counts in both hotspot (150,320) and hotlink (213,375) tests. Compared with HPRA, EHPRA reduces faults by 10.29% in hotspot traffic and 27.20% in hotlink traffic. Although EHPRA may increase average hops versus strictly minimal algorithms, it provides the best reliability-latency trade-off, achieving the minimum weighted overall cost across all compared methods.

**Keywords:** Network-on-Chip, 2D Mesh, Adaptive Routing, Fault Tolerance, Congestion Awareness, Smart Detour, HPRA, EHPRA

## 1. Introduction
As the number of on-chip cores grows, the communication fabric becomes a dominant performance bottleneck in many-core processors. Two-dimensional mesh topologies remain popular due to layout regularity, scalability, and implementation simplicity. However, deterministic minimal routing, such as XY, tends to overuse specific links in non-uniform traffic patterns and is therefore vulnerable to congestion and repeated link-level faults.

In practical NoC workloads, two stress patterns are frequently studied: (i) **hotlink traffic**, where repeated communication saturates a fixed source-destination corridor, and (ii) **hotspot traffic**, where many sources communicate with one destination region. Both patterns can create persistent high-risk links that are repeatedly affected by congestion and dynamic faults.

The previously published Hybrid Probabilistic Routing Algorithm (HPRA) addressed this issue by switching between minimal and detour routing according to an adaptive probability parameter \(p\). While HPRA improves robustness, its detour component still relies on relatively simple path construction and can produce suboptimal intermediate-node choices.

This paper proposes **EHPRA**, which replaces random detour behavior with a **Smart Detour** policy that evaluates multiple candidate detours based on local link-usage history and destination-aware weighting. The central hypothesis is that better detour-node selection can significantly reduce fault exposure under hotspot/hotlink conditions while preserving algorithmic simplicity suitable for hardware-oriented routing logic.

The main contributions are:
1. A Smart Detour candidate-evaluation mechanism integrated into probabilistic hybrid routing.
2. A destination-aware congestion score that prioritizes decongestion near the destination (especially useful in hotspot traffic).
3. Reproducible simulation-based evaluation against four baselines (HPRA, Minimal, Detour, XY) under fault-injected traffic.
4. Quantitative evidence that EHPRA provides the best reliability-cost trade-off in both tested scenarios.

## 2. Related Routing Approaches
### 2.1 Deterministic Minimal Routing (XY)
XY routing follows dimension-ordered minimal paths and is deadlock-safe in regular meshes. Its simplicity is valuable, but repeated traffic flows overload fixed links.

### 2.2 Minimal-Oblivious Routing
Minimal-oblivious routing uses randomized intermediate points while remaining in minimal-path constraints. It provides path diversity but lacks explicit congestion awareness.

### 2.3 Random Detour Routing
Detour routing sends packets through intermediate nodes outside the source-destination bounding box. This increases path diversity and bypass opportunities, but random intermediate selection often creates long or inefficient routes.

### 2.4 HPRA
HPRA combines minimal-oblivious and detour routing probabilistically. The mode selection probability \(p\) increases after faults in minimal mode and decays over time, giving adaptive exploration behavior.

### 2.5 Gap Addressed by EHPRA
The remaining gap is **detour quality**: HPRA decides *when* to detour, but not optimally *where* to detour. EHPRA fills this gap by adding path scoring and candidate ranking with lightweight local statistics.

## 3. Proposed Method: EHPRA
### 3.1 Baseline Hybrid Framework
Like HPRA, EHPRA maintains two routing options per packet:
- Minimal-oblivious path
- Detour path

A random draw with probability \(p\) selects detour mode. The value of \(p\) is adjusted online using fault feedback:
- If a fault occurs while using minimal mode, \(p\) increases by \(p_{up}\).
- If a fault occurs while using detour mode, \(p\) decreases by \(p_{down}\).
- A small decay \(p_{decay}\) is continuously applied.

This mechanism preserves HPRA’s adaptive mode control.

### 3.2 Smart Detour Candidate Generation
For each source-destination pair, EHPRA computes the bounding box and generates up to \(k\) candidate intermediate nodes, mostly outside the bounding box, with detour radius influenced by \(p\):
\[
\Delta = \max\left(1, \left\lfloor p \cdot \max(R,C) \cdot k_\Delta \right\rfloor\right)
\]
where \(R\) and \(C\) are mesh dimensions.

Higher \(p\) thus allows wider exploration.

### 3.3 Congestion-Aware Path Scoring
For each candidate intermediate node, EHPRA builds a full path and computes score:
\[
\text{Score}(P) = \sum_{(u,v)\in P} w(u,v)\cdot U(u,v) + \lambda \cdot H(P)
\]
where:
- \(U(u,v)\): historical link usage count,
- \(H(P)\): hop count of path \(P\),
- \(\lambda\): hop penalty coefficient,
- \(w(u,v)\): destination-aware weight.

Destination-aware weighting is defined by Manhattan distance \(d\) from link endpoints to destination:
\[
w(u,v)=1+\frac{6}{d+1}
\]
Therefore, congested links near the destination are penalized more strongly, improving hotspot behavior.

### 3.4 Fault Injection and Adaptation
During simulation, periodically selected “hot” links are marked faulty for a fixed duration. A packet incurs a fault event when its chosen route traverses the active faulty link. These fault observations drive the adaptive probability update described above.

## 4. Experimental Setup
### 4.1 Topology and Traffic
- Topology: 16×16 2D mesh.
- Hotlink: fixed source (2,3) and destination (5,6).
- Hotspot: random source nodes targeting destination (8,8).

### 4.2 Compared Algorithms
1. EHPRA (proposed)
2. HPRA
3. Minimal-oblivious
4. Random detour
5. XY

### 4.3 Simulation Parameters
- Trials per algorithm per scenario: 1,000,000
- Fault period: every 10 trials
- Fault duration: 5 trials
- Hot threshold for candidate faulty links: 3
- Probability adaptation: \(p_{up}=0.01, p_{down}=0.01, p_{decay}=0.0005\)

### 4.4 Evaluation Metrics
- Total fault count
- Average hop count
- Weighted overall cost:
\[
\text{Cost} = w_f\cdot \frac{F}{F_{max}} + w_h\cdot \frac{H}{H_{max}},\quad w_f=0.8,\; w_h=0.2
\]
Lower cost is better.

## 5. Results and Discussion
### 5.1 Hotspot Traffic Results
| Algorithm | Total Faults | Avg Hops |
|---|---:|---:|
| EHPRA | 150,320 | 13.02 |
| HPRA | 167,566 | 10.07 |
| Minimal | 193,770 | 10.03 |
| Detour | 232,711 | 25.43 |
| XY | 250,971 | 9.03 |

Key observations:
- EHPRA achieves the lowest fault count (150,320), reducing faults by **10.29%** versus HPRA.
- EHPRA also reduces faults by **22.42%** vs Minimal and **40.10%** vs XY.
- Hop count increases compared with minimal paths, but weighted cost remains best due to dominant reliability gains.

### 5.2 Hotlink Traffic Results
| Algorithm | Total Faults | Avg Hops |
|---|---:|---:|
| EHPRA | 213,375 | 12.66 |
| HPRA | 293,112 | 14.09 |
| Minimal | 375,388 | 8.00 |
| Detour | 458,702 | 28.83 |
| XY | 499,995 | 7.00 |

Key observations:
- EHPRA provides the best reliability again, reducing faults by **27.20%** vs HPRA.
- Fault reduction reaches **43.16%** vs Minimal and **57.32%** vs XY.
- In hotlink traffic, EHPRA even improves hops compared with HPRA (12.66 vs 14.09), indicating that smart detours can be both safer and shorter than uninformed detours.

### 5.3 Overall Cost Analysis
Using \(w_f=0.8\) and \(w_h=0.2\):
- Hotspot cost: EHPRA = **0.5816**, HPRA = 0.6133, Minimal = 0.6965, Detour = 0.9418, XY = 0.8710.
- Hotlink cost: EHPRA = **0.4292**, HPRA = 0.5667, Minimal = 0.6561, Detour = 0.9339, XY = 0.8486.

EHPRA ranks first in both scenarios, confirming that destination-aware smart detour selection improves reliability without unacceptable path inflation.

### 5.4 Discussion
EHPRA’s behavior reflects a practical design principle: in fault-prone and congestion-prone NoC regions, reducing repeated traversal of hot links can outweigh strict shortest-path preference. The algorithm remains lightweight because it uses simple counters and local heuristics rather than global optimization or machine learning inference.

Potential limitations include sensitivity to parameter tuning (e.g., \(\lambda\), candidate count \(k\), and adaptation rates). Future work should analyze parameter robustness across larger traffic suites and hardware-level cycle-accurate models.

## 6. Conclusions
This paper introduced EHPRA, an enhancement to HPRA that combines probabilistic mode adaptation with a congestion-aware Smart Detour mechanism. Experimental results on a 16×16 mesh under one million-trial hotspot and hotlink scenarios show consistent superiority in fault reduction and weighted routing cost over HPRA, Minimal, Detour, and XY routing. EHPRA is especially effective in reducing vulnerability to repeated hot-link failures by selecting detour paths using destination-aware link-usage scoring.

Given its low computational complexity and strong reliability gains, EHPRA is a promising candidate for practical adaptive NoC routing where fault resilience is as important as latency.

## Acknowledgments
The authors acknowledge the support of the research environment and simulation framework developed at Amirkabir University of Technology for this study.

## Nomenclature
- \(p\): Probability of selecting detour mode
- \(p_{up}\): Increment in \(p\) after fault in minimal mode
- \(p_{down}\): Decrement in \(p\) after fault in detour mode
- \(p_{decay}\): Continuous decay term of \(p\)
- \(U(u,v)\): Historical usage of link \((u,v)\)
- \(\lambda\): Hop-count penalty coefficient
- \(F\): Total faults
- \(H\): Average hops

## References
[1] A. Akhbari, H. Khoojooyan, and M. Tarighi, “HPRA: Hybrid Probabilistic Routing Algorithm for 2D Mesh NoC,” International Conference on Electrical, Computer and Mechanical Engineering.

[2] W. J. Dally and B. Towles, *Principles and Practices of Interconnection Networks*. San Francisco, CA, USA: Morgan Kaufmann, 2004.

[3] L. Benini and G. De Micheli, “Networks on chips: A new SoC paradigm,” *Computer*, vol. 35, no. 1, pp. 70–78, 2002.

[4] J. Duato, S. Yalamanchili, and L. Ni, *Interconnection Networks: An Engineering Approach*. San Francisco, CA, USA: Morgan Kaufmann, 2002.
