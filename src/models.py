"""
Shipyard Steel Plate Nesting Optimizer - Data Models

Defines steel parts and plates used in ship construction.
Uses real shipyard terminology and standard dimensions.

Terminology:
    Shell    = Hull outer plates (Tekne kabugu)
    Bulkhead = Watertight partition walls (Perde)
    Deck     = Floor/ceiling plates (Guverte)
    Frame    = Transverse structural members (Posta)
    Kerf     = Width of material lost during cutting (Kesim agzi)
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SteelPart:
    """
    Represents a single steel part to be cut.

    In shipbuilding, these are typically:
    - Hull shell panels
    - Bulkhead sections
    - Deck plates
    - Longitudinal stiffeners
    - Transverse frames
    - Brackets and seat plates
    """
    width: float
    height: float
    part_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    label: str = ""
    thickness: float = 0
    quantity: int = 1
    can_rotate: bool = True

    placed_x: Optional[float] = None
    placed_y: Optional[float] = None
    is_rotated: bool = False

    @property
    def area(self) -> float:
        """Area in mm^2"""
        return self.width * self.height

    @property
    def effective_width(self) -> float:
        """Actual width considering rotation"""
        return self.height if self.is_rotated else self.width

    @property
    def effective_height(self) -> float:
        """Actual height considering rotation"""
        return self.width if self.is_rotated else self.height

    def fits_in(self, available_w: float, available_h: float) -> bool:
        """Check if part fits in given space, considering rotation"""
        if self.effective_width <= available_w and self.effective_height <= available_h:
            return True
        if self.can_rotate:
            if self.effective_height <= available_w and self.effective_width <= available_h:
                return True
        return False

    def __repr__(self):
        name = self.label or self.part_id
        return f"Part({name}: {self.width}x{self.height}mm)"


@dataclass
class SteelPlate:
    """
    Represents a stock steel plate.

    Standard shipbuilding plate sizes:
    - 6000 x 2000 mm
    - 12000 x 2500 mm
    - 12000 x 3000 mm (most common)
    - 16000 x 3200 mm
    """
    width: float = 12000
    height: float = 3000
    thickness: float = 10
    plate_id: str = field(default_factory=lambda: str(uuid.uuid4())[:6])
    kerf_width: float = 3.0  # plasma cutting kerf (mm)

    @property
    def area(self) -> float:
        return self.width * self.height

    def __repr__(self):
        return f"Plate({self.plate_id}: {self.width}x{self.height}mm, t={self.thickness}mm)"


@dataclass
class PlacedPart:
    """A part that has been placed on a plate"""
    part: SteelPart
    x: float
    y: float
    rotated: bool = False

    @property
    def actual_width(self) -> float:
        return self.part.height if self.rotated else self.part.width

    @property
    def actual_height(self) -> float:
        return self.part.width if self.rotated else self.part.height

    @property
    def right(self) -> float:
        return self.x + self.actual_width

    @property
    def top(self) -> float:
        return self.y + self.actual_height

    def overlaps(self, other: 'PlacedPart', kerf: float = 3.0) -> bool:
        """Check if two placed parts overlap (including kerf allowance)"""
        if self.right + kerf <= other.x:
            return False
        if other.right + kerf <= self.x:
            return False
        if self.top + kerf <= other.y:
            return False
        if other.top + kerf <= self.y:
            return False
        return True


@dataclass
class NestingResult:
    """Optimization result containing the cutting plan"""
    plate: SteelPlate
    placements: List[PlacedPart] = field(default_factory=list)
    unplaced_parts: List[SteelPart] = field(default_factory=list)
    generation_count: int = 0
    best_fitness_history: list = field(default_factory=list)

    @property
    def used_area(self) -> float:
        return sum(p.part.area for p in self.placements)

    @property
    def utilization_rate(self) -> float:
        """Material utilization percentage"""
        if self.plate.area == 0:
            return 0
        return (self.used_area / self.plate.area) * 100

    @property
    def waste_rate(self) -> float:
        """Waste percentage"""
        return 100 - self.utilization_rate

    @property
    def parts_placed_count(self) -> int:
        return len(self.placements)

    def summary(self) -> str:
        return (
            f"\n{'='*55}\n"
            f"  CUTTING PLAN RESULTS\n"
            f"{'='*55}\n"
            f"  Plate size       : {self.plate.width} x {self.plate.height} mm\n"
            f"  Plate area       : {self.plate.area / 1e6:.2f} m2\n"
            f"  Parts placed     : {self.parts_placed_count}\n"
            f"  Used area        : {self.used_area / 1e6:.2f} m2\n"
            f"  Utilization rate : {self.utilization_rate:.1f}%\n"
            f"  Waste rate       : {self.waste_rate:.1f}%\n"
            f"  Unplaced parts   : {len(self.unplaced_parts)}\n"
            f"{'='*55}\n"
        )
