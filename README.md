# 🚢 Shipyard Steel Plate Nesting Optimizer

> AI-powered 2D nesting optimization for shipbuilding steel plate cutting using Genetic Algorithm. Minimizes material waste in CNC plasma/laser cutting operations.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## The Problem

In shipbuilding, steel plates are cut into hundreds of uniquely shaped parts per vessel. Poor part arrangement on stock plates leads to **15–25% material waste**. For a single vessel consuming 500+ tons of steel, even a **5% improvement in utilization saves tens of thousands of dollars**.

## The Solution

This project implements a **Genetic Algorithm (GA)** combined with a **Bottom-Left-Fill (BLF)** placement heuristic to find near-optimal arrangements of ship structural parts on standard steel plates.

The optimizer considers:
- Part rotation (0° / 90°)
- Cutting kerf width (plasma/laser/oxy-fuel)
- Real steel plate dimensions used in shipyards
- Actual material cost calculations

---

## Results

| Metric | Sequential Placement | GA Optimized | Improvement |
|--------|:---:|:---:|:---:|
| Material Utilization | ~65–70% | ~82–88% | **+15–20%** |
| Waste Rate | ~30–35% | ~12–18% | **-15–20%** |
| Cost Saving (per plate) | — | — | **~$50–120** |

> For a 65m bulk carrier using ~400 plates, total saving: **$20,000–48,000**

---

## Features

- 🧬 **Genetic Algorithm** — Tournament selection, Order Crossover (OX), swap & flip mutation
- 📐 **Bottom-Left-Fill** — Industry-standard placement heuristic for 2D bin packing
- 🔄 **Part Rotation** — Automatic 90° rotation to find better fits
- 🔥 **Kerf Allowance** — Accounts for plasma/laser cutting width (default 3mm)
- 📊 **Visualization** — Cutting plan layout, convergence chart, comparison chart
- 💰 **Cost Analysis** — Real-world waste cost in USD using steel density (7850 kg/m³)
- ⚖️ **Benchmarking** — Side-by-side comparison with naive sequential placement
- 🧪 **Unit Tests** — Comprehensive test coverage with pytest

---

## Shipyard Terminology

| English | Turkish | Description |
|---------|---------|-------------|
| Shell | Tekne Kabuğu | Hull outer plating |
| Bulkhead | Perde | Watertight partition walls |
| Deck | Güverte | Horizontal floor/ceiling plates |
| Frame | Posta | Transverse structural members |
| Stiffener | Berkitme | Longitudinal reinforcement |
| Bracket | Braket | Connection / gusset plates |
| Kerf | Kesim Ağzı | Material removed during cutting |
| Nesting | Yerleştirme | Arranging parts on stock plate |
| DH36 | DH36 | High-strength marine grade steel |

---

## Quick Start

```bash
git clone https://github.com/AhmetYusufGENCER/shipyard-steel-nesting-optimizer.git
cd shipyard-steel-nesting-optimizer
pip install -r requirements.txt
python examples/ship_block_example.py
