"""
Realistic Shipyard Scenario: Ship Block Production

Scenario:
    A 65-meter bulk carrier is under construction at the shipyard.
    Block 12 (engine room section) steel parts need to be cut.

    Stock plate: 12000x3000mm, 12mm thick, DH36 marine grade steel.
    Cutting method: CNC plasma (kerf width: 3mm).

This example uses real shipyard terminology and dimensions
to demonstrate the optimizer's practical value.

Author: Ahmet Yusuf GENCER
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.nesting_engine import NestingEngine
from src.visualization import NestingVisualizer


def main():
    print("=" * 60)
    print("  SHIP BLOCK-12 CUTTING PLAN OPTIMIZATION")
    print("  Vessel: 65m Bulk Carrier | Steel: DH36 | t=12mm")
    print("=" * 60)

    # Initialize engine with standard shipyard plate
    engine = NestingEngine(
        plate_width=12000,
        plate_height=3000,
        plate_thickness=12,
        kerf_width=3.0
    )

    # Realistic ship parts for Block-12 (engine room)
    ship_parts = [
        # Hull shell panels
        {"label": "SHL-01",  "width": 3500, "height": 2200, "qty": 1},
        {"label": "SHL-02",  "width": 3200, "height": 2000, "qty": 1},

        # Bulkhead sections
        {"label": "BHD-01",  "width": 2800, "height": 1800, "qty": 1},
        {"label": "BHD-02",  "width": 1500, "height": 1200, "qty": 2},

        # Deck plates
        {"label": "DK-01",   "width": 2500, "height": 1500, "qty": 1},
        {"label": "DK-02",   "width": 2000, "height": 1000, "qty": 1},

        # Longitudinal stiffeners
        {"label": "LONG-01", "width": 4000, "height": 200,  "qty": 3},
        {"label": "LONG-02", "width": 3500, "height": 180,  "qty": 4},

        # Transverse frames
        {"label": "FR-01",   "width": 800,  "height": 400,  "qty": 3},
        {"label": "FR-02",   "width": 600,  "height": 350,  "qty": 4},

        # Brackets
        {"label": "BRK-01",  "width": 300,  "height": 300,  "qty": 6},
        {"label": "BRK-02",  "width": 250,  "height": 200,  "qty": 8},

        # Seat plates
        {"label": "SEAT-01", "width": 400,  "height": 250,  "qty": 4},
    ]

    engine.add_parts_from_list(ship_parts)

    total_parts = sum(p.get("qty", 1) for p in ship_parts)
    print(f"\n  Total parts to cut: {total_parts}")

    # Run optimization
    result = engine.run(
        population_size=100,
        generations=300,
        verbose=True,
        seed=42
    )

    # Compare with naive approach
    comparison = engine.compare_with_naive(result)
    print(f"\n  Comparison:")
    print(f"     Sequential    : {comparison['naive_utilization']}% utilization")
    print(f"     GA Optimized  : {comparison['optimized_utilization']}% utilization")
    print(f"     Improvement   : +{comparison['improvement_percent']}%")

    # Save visualizations
    os.makedirs("docs/results", exist_ok=True)
    viz = NestingVisualizer()

    viz.plot_nesting_layout(
        result,
        save_path="docs/results/cutting_plan.png",
        title="Block-12 Cutting Plan (DH36, t=12mm)"
    )

    viz.plot_convergence(
        result,
        save_path="docs/results/convergence.png"
    )

    viz.plot_comparison(
        comparison,
        save_path="docs/results/comparison.png"
    )

    print("\n  Visualizations saved to docs/results/")


if __name__ == "__main__":
    main()
