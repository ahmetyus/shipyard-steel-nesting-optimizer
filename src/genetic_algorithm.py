"""
Genetic Algorithm Engine for 2D Nesting Optimization

The steel plate cutting (nesting) problem is NP-hard.
Genetic Algorithm is widely used in the shipbuilding industry
for this type of optimization.

Chromosome structure:
    Each individual = [part_placement_order, rotation_flags]

Operators:
    Selection  : Tournament (k=3)
    Crossover  : Order Crossover (OX) - preserves permutation validity
    Mutation   : Swap (order) + Flip (rotation)
    Elitism    : Top 10% survive unchanged
"""

import random
from typing import List, Tuple
from .models import SteelPart, SteelPlate, PlacedPart, NestingResult
from .fitness import combined_fitness


class Chromosome:
    """
    Represents one candidate cutting plan.

    Genes:
        order     : permutation of part indices (placement priority)
        rotations : boolean list (rotate each part 90 degrees or not)
    """

    def __init__(self, order: List[int], rotations: List[bool]):
        self.order = order
        self.rotations = rotations
        self.fitness_score: float = 0.0
        self.placements: List[PlacedPart] = []

    @classmethod
    def random(cls, num_parts: int) -> 'Chromosome':
        order = list(range(num_parts))
        random.shuffle(order)
        rotations = [random.choice([True, False]) for _ in range(num_parts)]
        return cls(order, rotations)

    def copy(self) -> 'Chromosome':
        c = Chromosome(self.order.copy(), self.rotations.copy())
        c.fitness_score = self.fitness_score
        c.placements = self.placements.copy()
        return c


class BLFPlacer:
    """
    Bottom-Left-Fill (BLF) placement heuristic.

    Places each part at the lowest, then leftmost available position.
    This matches how CNC cutting machines typically operate in shipyards
    (starting from bottom-left corner of the plate).

    The algorithm:
    1. Generate candidate positions (corners of existing parts)
    2. Sort by Y (bottom first), then X (left first)
    3. Try each position, check for overlaps and plate bounds
    4. Place at first valid position
    """

    def __init__(self, plate: SteelPlate):
        self.plate = plate
        self.kerf = plate.kerf_width

    def place_parts(
        self,
        parts: List[SteelPart],
        order: List[int],
        rotations: List[bool]
    ) -> Tuple[List[PlacedPart], List[SteelPart]]:
        """
        Place parts on plate according to given order and rotations.

        Returns:
            (placed_parts, unplaced_parts)
        """
        placements: List[PlacedPart] = []
        unplaced: List[SteelPart] = []

        for idx in order:
            part = parts[idx]
            rotated = rotations[idx] and part.can_rotate

            w = part.height if rotated else part.width
            h = part.width if rotated else part.height

            position = self._find_best_position(w, h, placements)

            if position is not None:
                placements.append(PlacedPart(
                    part=part, x=position[0], y=position[1], rotated=rotated
                ))
            else:
                # Try the other rotation
                if part.can_rotate:
                    w2, h2 = h, w
                    position2 = self._find_best_position(w2, h2, placements)
                    if position2 is not None:
                        placements.append(PlacedPart(
                            part=part, x=position2[0], y=position2[1],
                            rotated=not rotated
                        ))
                        continue
                unplaced.append(part)

        return placements, unplaced

    def _find_best_position(
        self,
        width: float,
        height: float,
        existing: List[PlacedPart]
    ):
        """Find the best bottom-left position for a part"""

        # Candidate anchor points
        candidates = [(0, 0)]

        for p in existing:
            candidates.append((p.right + self.kerf, 0))
            candidates.append((0, p.top + self.kerf))
            candidates.append((p.right + self.kerf, p.y))
            candidates.append((p.x, p.top + self.kerf))

        # Sort: bottom first (Y), then left first (X)
        candidates.sort(key=lambda c: (c[1], c[0]))

        # Remove duplicates
        seen = set()
        unique_candidates = []
        for c in candidates:
            key = (round(c[0], 1), round(c[1], 1))
            if key not in seen:
                seen.add(key)
                unique_candidates.append(c)

        for cx, cy in unique_candidates:
            # Check plate bounds
            if cx + width > self.plate.width + 0.01:
                continue
            if cy + height > self.plate.height + 0.01:
                continue

            # Check overlaps with existing parts
            has_overlap = False
            for ep in existing:
                if self._rectangles_overlap(
                    cx, cy, width, height,
                    ep.x, ep.y, ep.actual_width, ep.actual_height
                ):
                    has_overlap = True
                    break

            if not has_overlap:
                return (cx, cy)

        return None

    def _rectangles_overlap(
        self,
        x1, y1, w1, h1,
        x2, y2, w2, h2
    ) -> bool:
        """Check if two rectangles overlap (with kerf margin)"""
        k = self.kerf
        if x1 + w1 + k <= x2 or x2 + w2 + k <= x1:
            return False
        if y1 + h1 + k <= y2 or y2 + h2 + k <= y1:
            return False
        return True


class GeneticNestingOptimizer:
    """
    Genetic Algorithm optimizer for steel plate nesting.

    Parameters are tuned for shipyard industry:
    - Population: 80 (fast convergence)
    - Generations: 200 (acceptable computation time)
    - Mutation: 15% (maintain diversity)
    - Elitism: 10% (preserve best solutions)
    """

    def __init__(
        self,
        population_size: int = 80,
        generations: int = 200,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.15,
        elite_ratio: float = 0.10,
        seed: int = None
    ):
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_count = max(2, int(population_size * elite_ratio))

        if seed is not None:
            random.seed(seed)

    def optimize(
        self,
        parts: List[SteelPart],
        plate: SteelPlate,
        verbose: bool = True
    ) -> NestingResult:
        """
        Run the genetic algorithm optimization.

        Args:
            parts  : list of steel parts to cut
            plate  : stock steel plate
            verbose: print progress updates

        Returns:
            NestingResult with optimal cutting plan
        """
        n = len(parts)
        placer = BLFPlacer(plate)

        # Initial population
        population = [Chromosome.random(n) for _ in range(self.population_size)]

        for chromo in population:
            self._evaluate(chromo, parts, plate, placer)

        best_ever = max(population, key=lambda c: c.fitness_score).copy()
        fitness_history = [best_ever.fitness_score]

        if verbose:
            print(f"\n{'='*55}")
            print(f"  GENETIC NESTING OPTIMIZATION")
            print(f"{'='*55}")
            print(f"  Parts count   : {n}")
            print(f"  Plate size    : {plate.width} x {plate.height} mm")
            print(f"  Population    : {self.population_size}")
            print(f"  Generations   : {self.generations}")
            print(f"{'='*55}\n")

        for gen in range(self.generations):
            new_population = []

            # Elitism: keep best individuals
            population.sort(key=lambda c: c.fitness_score, reverse=True)
            for i in range(self.elite_count):
                new_population.append(population[i].copy())

            # Generate new individuals
            while len(new_population) < self.population_size:
                parent1 = self._tournament_select(population)
                parent2 = self._tournament_select(population)

                if random.random() < self.crossover_rate:
                    child1, child2 = self._order_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()

                self._mutate(child1)
                self._mutate(child2)

                self._evaluate(child1, parts, plate, placer)
                self._evaluate(child2, parts, plate, placer)

                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)

            population = new_population

            gen_best = max(population, key=lambda c: c.fitness_score)
            if gen_best.fitness_score > best_ever.fitness_score:
                best_ever = gen_best.copy()

            fitness_history.append(best_ever.fitness_score)

            if verbose and (gen + 1) % 25 == 0:
                rate = best_ever.fitness_score * 100
                print(f"   Generation {gen+1:>4d} | "
                      f"Utilization: {rate:.1f}% | "
                      f"Waste: {100-rate:.1f}%")

        # Final placement with best chromosome
        final_placements, unplaced = placer.place_parts(
            parts, best_ever.order, best_ever.rotations
        )

        if verbose:
            print(f"\n   Optimization complete!")

        return NestingResult(
            plate=plate,
            placements=final_placements,
            unplaced_parts=unplaced,
            generation_count=self.generations,
            best_fitness_history=fitness_history
        )

    def _evaluate(self, chromo, parts, plate, placer):
        """Evaluate a chromosome's fitness"""
        placements, _ = placer.place_parts(
            parts, chromo.order, chromo.rotations
        )
        chromo.placements = placements
        chromo.fitness_score = combined_fitness(plate, placements)

    def _tournament_select(self, population, k=3):
        """Tournament selection: pick best from k random individuals"""
        tournament = random.sample(population, min(k, len(population)))
        return max(tournament, key=lambda c: c.fitness_score)

    def _order_crossover(self, p1, p2):
        """
        Order Crossover (OX): suitable for permutation chromosomes.
        Preserves relative order of genes.
        """
        n = len(p1.order)
        start, end = sorted(random.sample(range(n), 2))

        def ox(parent1, parent2):
            child_order = [-1] * n
            child_order[start:end+1] = parent1.order[start:end+1]

            fill_values = [v for v in parent2.order if v not in child_order]
            idx = 0
            for i in range(n):
                if child_order[i] == -1:
                    child_order[i] = fill_values[idx]
                    idx += 1

            child_rot = [
                parent1.rotations[i] if random.random() < 0.5
                else parent2.rotations[i]
                for i in range(n)
            ]
            return Chromosome(child_order, child_rot)

        return ox(p1, p2), ox(p2, p1)

    def _mutate(self, chromo):
        """
        Mutation operators:
        1. Swap: exchange placement order of two parts
        2. Rotation flip: toggle rotation of a random part
        """
        n = len(chromo.order)

        if random.random() < self.mutation_rate:
            i, j = random.sample(range(n), 2)
            chromo.order[i], chromo.order[j] = chromo.order[j], chromo.order[i]

        if random.random() < self.mutation_rate:
            idx = random.randint(0, len(chromo.rotations) - 1)
            chromo.rotations[idx] = not chromo.rotations[idx]
