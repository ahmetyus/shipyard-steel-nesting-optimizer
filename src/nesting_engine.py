"""
High-Level Nesting Engine API

Designed to match the shipyard production workflow:
1. Receive part list (from production planning)
2. Get stock plate dimensions (from warehouse)
3. Run optimization
4. Output cutting plan

Author: Ahmet Yusuf GENCER
"""

from typing import List
from .models import SteelPart, SteelPlate, NestingResult
from .genetic_algorithm import GeneticNestingOptimizer
from .fitness import calculate_waste_cost


class NestingEngine:
    """
    Shipyard production line nesting engine.

    Usage:
        engine = NestingEngine()
        engine.add_part("Frame-1", 800, 400, quantity=4)
        engine.add_part("BHD-Panel", 2000, 1500)
        result = engine.run()
        print(result.summary())
    """

    def __init__(
        self,
        plate_width: float = 12000,
        plate_height: float = 3000,
        plate_thickness: float = 10,
        kerf_width: float = 3.0
    ):
        self.plate = SteelPlate(
            width=plate_width,
            height=plate_height,
            thickness=plate_thickness,
            kerf_width=kerf_width
        )
        self.parts: List[SteelPart] = []

    def add_part(
        self,
        label: str,
        width: float,
        height: float,
        quantity: int = 1,
        can_rotate: bool = True
    ):
        """Add parts to the cutting list"""
        for i in range(quantity):
            part_label = f"{label}" if quantity == 1 else f"{label}-{i+1}"
            self.parts.append(SteelPart(
                width=width,
                height=height,
                label=part_label,
                thickness=self.plate.thickness,
                can_rotate=can_rotate
            ))

    def add_parts_from_list(self, parts_data: List[dict]):
        """
        Bulk add parts.

        Format:
        [
            {"label": "FR-1", "width": 800, "height": 400, "qty": 4},
            {"label": "BHD-1", "width": 2000, "height": 1500, "qty": 1},
        ]
        """
        for p in parts_data:
            self.add_part(
                label=p["label"],
                width=p["width"],
                height=p["height"],
                quantity=p.get("qty", 1),
                can_rotate=p.get("can_rotate", True)
            )

    def run(
        self,
        population_size: int = 80,
        generations: int = 200,
        verbose: bool = True,
        seed: int = None
    ) -> NestingResult:
        """Run the optimization"""

        if not self.parts:
            raise ValueError("Part list is empty. Use add_part() first.")

        optimizer = GeneticNestingOptimizer(
            population_size=population_size,
            generations=generations,
            seed=seed
        )

        result = optimizer.optimize(self.parts, self.plate, verbose=verbose)

        if verbose:
            print(result.summary())

            cost = calculate_waste_cost(self.plate, result.placements)
            print(f"  Cost Analysis:")
            print(f"     Plate weight     : {cost['plate_total_weight_kg']:.1f} kg")
            print(f"     Used material    : {cost['used_weight_kg']:.1f} kg")
            print(f"     Wasted material  : {cost['waste_weight_kg']:.1f} kg")
            print(f"     Waste cost       : ${cost['waste_cost_usd']:.2f}")
            print(f"     (Unit price      : ${cost['steel_unit_price_usd_kg']}/kg)\n")

        return result

    def compare_with_naive(self, result: NestingResult) -> dict:
        """
        Compare GA result with naive sequential placement.
        Demonstrates the value of optimization to engineers.
        """
        naive_optimizer = GeneticNestingOptimizer(
            population_size=1,
            generations=1,
            seed=0
        )
        naive_result = naive_optimizer.optimize(
            self.parts, self.plate, verbose=False
        )

        improvement = result.utilization_rate - naive_result.utilization_rate

        return {
            "naive_utilization": round(naive_result.utilization_rate, 1),
            "optimized_utilization": round(result.utilization_rate, 1),
            "improvement_percent": round(improvement, 1),
            "naive_waste": round(naive_result.waste_rate, 1),
            "optimized_waste": round(result.waste_rate, 1),
        }
