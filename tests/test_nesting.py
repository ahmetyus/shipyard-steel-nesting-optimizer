"""
Unit tests for the nesting optimizer.

Run with: pytest tests/test_nesting.py -v

Author: Ahmet Yusuf GENCER
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models import SteelPart, SteelPlate, PlacedPart
from src.fitness import material_utilization_fitness, calculate_waste_cost
from src.nesting_engine import NestingEngine


class TestSteelPart:

    def test_area_calculation(self):
        part = SteelPart(width=1000, height=500)
        assert part.area == 500000

    def test_rotation_dimensions(self):
        part = SteelPart(width=1000, height=500, can_rotate=True)
        part.is_rotated = True
        assert part.effective_width == 500
        assert part.effective_height == 1000

    def test_fits_in_space(self):
        part = SteelPart(width=500, height=300)
        assert part.fits_in(600, 400) is True
        assert part.fits_in(400, 200) is False


class TestPlacedPart:

    def test_right_and_top(self):
        part = SteelPart(width=1000, height=500)
        placed = PlacedPart(part=part, x=100, y=200)
        assert placed.right == 1100
        assert placed.top == 700

    def test_overlap_detection(self):
        p1 = SteelPart(width=500, height=500)
        p2 = SteelPart(width=500, height=500)
        placed1 = PlacedPart(part=p1, x=0, y=0)
        placed2 = PlacedPart(part=p2, x=200, y=200)
        assert placed1.overlaps(placed2) is True

    def test_no_overlap(self):
        p1 = SteelPart(width=500, height=500)
        p2 = SteelPart(width=500, height=500)
        placed1 = PlacedPart(part=p1, x=0, y=0)
        placed2 = PlacedPart(part=p2, x=600, y=600)
        assert placed1.overlaps(placed2) is False


class TestFitness:

    def test_empty_placement_returns_zero(self):
        plate = SteelPlate(width=12000, height=3000)
        assert material_utilization_fitness(plate, []) == 0.0

    def test_full_coverage_returns_one(self):
        plate = SteelPlate(width=1000, height=1000)
        part = SteelPart(width=1000, height=1000)
        placement = PlacedPart(part=part, x=0, y=0)
        score = material_utilization_fitness(plate, [placement])
        assert abs(score - 1.0) < 0.001

    def test_half_coverage(self):
        plate = SteelPlate(width=1000, height=1000)
        part = SteelPart(width=500, height=1000)
        placement = PlacedPart(part=part, x=0, y=0)
        score = material_utilization_fitness(plate, [placement])
        assert abs(score - 0.5) < 0.001


class TestWasteCost:

    def test_full_waste_calculation(self):
        plate = SteelPlate(width=12000, height=3000, thickness=10)
        result = calculate_waste_cost(plate, [], steel_price_per_kg=0.80)
        assert result["waste_rate_percent"] == 100.0
        assert result["waste_weight_kg"] > 0
        assert result["waste_cost_usd"] > 0

    def test_zero_waste(self):
        plate = SteelPlate(width=1000, height=1000, thickness=10)
        part = SteelPart(width=1000, height=1000)
        placement = PlacedPart(part=part, x=0, y=0)
        result = calculate_waste_cost(plate, [placement])
        assert result["waste_rate_percent"] == 0.0


class TestNestingEngine:

    def test_add_parts(self):
        engine = NestingEngine()
        engine.add_part("TEST", 500, 300, quantity=3)
        assert len(engine.parts) == 3

    def test_add_parts_from_list(self):
        engine = NestingEngine()
        engine.add_parts_from_list([
            {"label": "A", "width": 500, "height": 300, "qty": 2},
            {"label": "B", "width": 800, "height": 400, "qty": 1},
        ])
        assert len(engine.parts) == 3

    def test_basic_optimization_runs(self):
        engine = NestingEngine(
            plate_width=2000,
            plate_height=1000,
            plate_thickness=10
        )
        engine.add_part("A", 800, 400, quantity=2)
        engine.add_part("B", 500, 300, quantity=3)

        result = engine.run(
            population_size=20,
            generations=50,
            verbose=False,
            seed=42
        )
        assert result.utilization_rate > 0
        assert result.parts_placed_count > 0

    def test_comparison_shows_improvement(self):
        engine = NestingEngine(
            plate_width=3000,
            plate_height=2000,
            plate_thickness=10
        )
        engine.add_part("X", 800, 600, quantity=4)
        engine.add_part("Y", 500, 400, quantity=6)

        result = engine.run(
            population_size=40,
            generations=100,
            verbose=False,
            seed=42
        )
        comparison = engine.compare_with_naive(result)
        assert comparison["optimized_utilization"] >= comparison["naive_utilization"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
