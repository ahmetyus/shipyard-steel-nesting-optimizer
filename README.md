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
git clone https://github.com/ahmetyus/shipyard-steel-nesting-optimizer.git
cd shipyard-steel-nesting-optimizer
pip install -r requirements.txt
python examples/ship_block_example.py
```

---

## Usage

```python
from src import NestingEngine, NestingVisualizer

# Standard shipyard plate: 12m x 3m, 12mm DH36 steel
engine = NestingEngine(
    plate_width=12000,   # mm
    plate_height=3000,   # mm
    plate_thickness=12,  # mm
    kerf_width=3.0       # mm (plasma cutting)
)

# Add ship structural parts
engine.add_part("Shell-1", width=3500, height=2200)
engine.add_part("Frame-1", width=800, height=400, quantity=4)
engine.add_part("Bracket", width=300, height=300, quantity=6)

# Run genetic algorithm optimization
result = engine.run(population_size=100, generations=300)
print(result.summary())

# Generate cutting plan visualization
viz = NestingVisualizer()
viz.plot_nesting_layout(result, save_path="cutting_plan.png")
viz.plot_convergence(result, save_path="convergence.png")
```

---

## Algorithm

```
1. ENCODE     → Each solution = [part_order_permutation, rotation_flags]
2. INITIALIZE → Random population of N chromosomes
3. DECODE     → BLF placement: arrange parts bottom-left on plate
4. EVALUATE   → Fitness = 0.7 × utilization + 0.3 × compactness
5. SELECT     → Tournament selection (k=3)
6. CROSSOVER  → Order Crossover (OX) preserving permutation validity
7. MUTATE     → Swap mutation (order) + Flip mutation (rotation)
8. ELITISM    → Top 10% survive unchanged to next generation
9. REPEAT     → Steps 3–8 for G generations
```

---

## Project Structure

```
shipyard-steel-nesting-optimizer/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── src/
│   ├── __init__.py                # Package exports
│   ├── models.py                  # SteelPart, SteelPlate, PlacedPart, NestingResult
│   ├── genetic_algorithm.py       # GA engine + BLF placer (core algorithm)
│   ├── nesting_engine.py          # High-level API for shipyard workflow
│   ├── fitness.py                 # Fitness functions + cost analysis
│   └── visualization.py          # Matplotlib cutting plan plots
├── examples/
│   └── ship_block_example.py      # 65m bulk carrier Block-12 scenario
├── tests/
│   └── test_nesting.py            # Unit tests (pytest)
└── docs/
    └── results/                   # Generated output images
```

---

## Why This Matters

```
A typical 65m cargo vessel:
  → Uses ~800 tons of steel plates
  → Industry average waste: ~20% = 160 tons wasted
  → With GA optimization: ~12% = 96 tons wasted
  → Steel saved: 64 tons
  → At $800/ton: $51,200 saved per vessel

A shipyard building 5 vessels/year saves ~$250,000 annually
just from better nesting — with no hardware investment.
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core language |
| NumPy | Numerical operations |
| Matplotlib | Cutting plan visualization |
| Pytest | Unit testing |

---

## Running Tests

```bash
pytest tests/test_nesting.py -v
```

---

## Future Improvements

- [ ] Support for irregular (non-rectangular) parts
- [ ] Multi-plate optimization (bin packing across multiple plates)
- [ ] Integration with shipyard CAD/CAM systems (DXF export)
- [ ] Web-based interface for production planning teams
- [ ] Support for different cutting methods (plasma, laser, oxy-fuel)

---

## Author

**Ahmet Yusuf GENCER**
Software Engineering Student

Interested in AI/ML applications for the maritime and shipbuilding industry.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
