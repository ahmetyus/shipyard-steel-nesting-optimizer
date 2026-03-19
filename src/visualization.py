"""
Cutting Plan Visualization Module

Generates:
1. Cutting plan layout (colored rectangles on plate)
2. GA convergence chart (generation vs fitness)
3. Comparison bar chart (naive vs optimized)

Author: Ahmet Yusuf GENCER
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Optional
from .models import NestingResult


COLORS = [
    '#2196F3', '#4CAF50', '#FF9800', '#9C27B0',
    '#F44336', '#00BCD4', '#FFEB3B', '#795548',
    '#E91E63', '#3F51B5', '#8BC34A', '#FF5722',
    '#607D8B', '#009688', '#CDDC39', '#673AB7',
    '#03A9F4', '#FFC107', '#FF4081', '#536DFE',
]


class NestingVisualizer:
    """Cutting plan visualization tools"""

    @staticmethod
    def plot_nesting_layout(
        result: NestingResult,
        save_path: Optional[str] = None,
        title: str = "Steel Plate Cutting Plan",
        show_labels: bool = True,
        figsize: tuple = (16, 6)
    ):
        """
        Visualize the cutting plan.
        Gray = waste area, Colored rectangles = parts.
        """
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        plate = result.plate

        plate_rect = patches.Rectangle(
            (0, 0), plate.width, plate.height,
            linewidth=2, edgecolor='#333333',
            facecolor='#E0E0E0', label='Waste Area'
        )
        ax.add_patch(plate_rect)

        for i, placement in enumerate(result.placements):
            color = COLORS[i % len(COLORS)]
            w = placement.actual_width
            h = placement.actual_height

            rect = patches.Rectangle(
                (placement.x, placement.y), w, h,
                linewidth=1, edgecolor='#333333',
                facecolor=color, alpha=0.8
            )
            ax.add_patch(rect)

            if show_labels:
                label = placement.part.label or f"P{i+1}"
                cx = placement.x + w / 2
                cy = placement.y + h / 2
                font_size = min(8, max(4, min(w, h) / 120))
                ax.text(
                    cx, cy, label,
                    ha='center', va='center',
                    fontsize=font_size, fontweight='bold',
                    color='white',
                    bbox=dict(boxstyle='round,pad=0.1',
                              facecolor='black', alpha=0.3)
                )

        ax.set_xlim(-100, plate.width + 100)
        ax.set_ylim(-100, plate.height + 100)
        ax.set_aspect('equal')
        ax.set_xlabel('Width (mm)', fontsize=11)
        ax.set_ylabel('Height (mm)', fontsize=11)

        title_full = (
            f"{title}\n"
            f"Plate: {plate.width}x{plate.height}mm | "
            f"Parts: {result.parts_placed_count} | "
            f"Utilization: {result.utilization_rate:.1f}% | "
            f"Waste: {result.waste_rate:.1f}%"
        )
        ax.set_title(title_full, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.2)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.close()
        return fig

    @staticmethod
    def plot_convergence(
        result: NestingResult,
        save_path: Optional[str] = None,
        figsize: tuple = (10, 5)
    ):
        """Plot GA convergence chart"""
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        generations = range(len(result.best_fitness_history))
        fitness_pct = [f * 100 for f in result.best_fitness_history]

        ax.plot(generations, fitness_pct,
                color='#2196F3', linewidth=2,
                label='Best Utilization Rate')
        ax.fill_between(generations, fitness_pct,
                        alpha=0.1, color='#2196F3')

        if fitness_pct:
            ax.axhline(y=fitness_pct[-1], color='red',
                       linestyle='--', alpha=0.5,
                       label=f'Final: {fitness_pct[-1]:.1f}%')

        ax.set_xlabel('Generation', fontsize=11)
        ax.set_ylabel('Material Utilization (%)', fontsize=11)
        ax.set_title('Genetic Algorithm Convergence',
                     fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.close()
        return fig

    @staticmethod
    def plot_comparison(
        comparison: dict,
        save_path: Optional[str] = None,
        figsize: tuple = (8, 5)
    ):
        """Naive vs Optimized comparison bar chart"""
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        methods = ['Sequential\n(No Optimization)', 'Genetic Algorithm\n(Optimized)']
        utilization = [comparison['naive_utilization'],
                       comparison['optimized_utilization']]
        waste = [comparison['naive_waste'],
                 comparison['optimized_waste']]

        x = np.arange(len(methods))
        width = 0.35

        bars1 = ax.bar(x - width/2, utilization, width,
                       label='Utilization (%)', color='#4CAF50', alpha=0.8)
        bars2 = ax.bar(x + width/2, waste, width,
                       label='Waste (%)', color='#F44336', alpha=0.8)

        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                    f'{bar.get_height():.1f}%', ha='center', fontweight='bold')
        for bar in bars2:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                    f'{bar.get_height():.1f}%', ha='center', fontweight='bold')

        ax.set_ylabel('Rate (%)', fontsize=11)
        ax.set_title(
            f'Optimization Comparison\n'
            f'(Improvement: +{comparison["improvement_percent"]:.1f}% utilization)',
            fontsize=13, fontweight='bold'
        )
        ax.set_xticks(x)
        ax.set_xticklabels(methods)
        ax.legend()
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.2, axis='y')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.close()
        return fig
