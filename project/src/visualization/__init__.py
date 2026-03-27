"""Visualization Module

This module provides plotting and visualization utilities for:
- IDA curves
- Fragility curves
- SHAP feature importance plots
- Model performance comparisons
- Seismic response time histories

Key Functions:
- plot_ida_curves: Create IDA curve plots
- plot_fragility_curves: Generate fragility diagrams
- plot_shap_summary: SHAP summary and dependence plots
- plot_performance_comparison: Compare model metrics

Usage:
    from src.visualization import plot_ida_curves, plot_fragility_curves
    
    plot_ida_curves(data, save_path='results/figures/')
    plot_fragility_curves(models, zones=['Z1', 'Z2', 'Z3', 'Z4'])
"""

__all__ = []
