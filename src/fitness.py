"""
Fitness Functions for Genetic Algorithm

In shipyard optimization, we aim to:
1. Maximize material utilization (minimize waste)
2. Keep parts compact (minimize cutting head movement)
3. Reduce overall cost (steel is expensive)

Steel density: 7850 kg/m3
Typical steel price: ~800 USD/ton (varies by grade)
"""

from typing import List
from .models import SteelPlate, PlacedPart


def material_utilization_fitness(
    plate: SteelPlate,
    placements: List[PlacedPart]
) -> float:
    """
    Primary fitness: material utilization ratio.
    Score 0.0 to 1.0 where 1.0 = zero waste (perfect).
    """
    if not placements:
        return 0.0
    used_area = sum(p.part.area for p in placements)
    return used_area / plate.area


def compactness_fitness(
    plate: SteelPlate,
    placements: List[PlacedPart]
) -> float:
    """
    Compactness score: how tightly parts are packed.
    Ratio of used area to bounding box area.
    Higher = parts closer together = less cutting movement.
    """
    if not placements:
        return 0.0
    max_right = max(p.right for p in placements)
    max_top = max(p.top for p in placements)
    bounding_area = max_right * max_top
    if bounding_area == 0:
        return 0.0
    used_area = sum(p.part.area for p in placements)
    return used_area / bounding_area


def combined_fitness(
    plate: SteelPlate,
    placements: List[PlacedPart],
    w_utilization: float = 0.7,
    w_compactness: float = 0.3
) -> float:
    """
    Weighted combined fitness function.

    Weights tuned for shipyard priorities:
    - 70%: material utilization (cost driven)
    - 30%: compactness (cutting time)
    """
    f1 = material_utilization_fitness(plate, placements)
    f2 = compactness_fitness(plate, placements)
    return w_utilization * f1 + w_compactness * f2


def calculate_waste_cost(
    plate: SteelPlate,
    placements: List[PlacedPart],
    steel_price_per_kg: float = 0.80,  # USD/kg
    steel_density: float = 7850         # kg/m3
) -> dict:
    """
    Calculate waste cost in real currency.

    Uses actual steel density (7850 kg/m3) and market price
    to give engineers a concrete cost figure.

    Returns:
        dict with weight and cost breakdown
    """
    plate_volume_m3 = (
        (plate.width / 1000) *
        (plate.height / 1000) *
        (plate.thickness / 1000)
    )
    plate_weight_kg = plate_volume_m3 * steel_density

    utilization = material_utilization_fitness(plate, placements)
    waste_ratio = 1 - utilization

    waste_weight_kg = plate_weight_kg * waste_ratio
    waste_cost = waste_weight_kg * steel_price_per_kg
    used_weight_kg = plate_weight_kg * utilization

    return {
        "plate_total_weight_kg": round(plate_weight_kg, 2),
        "used_weight_kg": round(used_weight_kg, 2),
        "waste_weight_kg": round(waste_weight_kg, 2),
        "waste_rate_percent": round(waste_ratio * 100, 1),
        "waste_cost_usd": round(waste_cost, 2),
        "steel_unit_price_usd_kg": steel_price_per_kg
    }
