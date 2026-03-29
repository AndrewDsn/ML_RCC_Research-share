"""Visualization Module for Seismic Drift Research

Plotting utilities for IDA results, fragility curves, SHAP analysis,
and framework comparison figures.

Features:
- IDA curve plotting (multi-stripe)
- Fragility curve generation
- Framework comparison plots
- SHAP visualization
- Publication-ready figures (300 DPI)

Usage:
    from src.visualization.plot_ida import plot_ida_curves
    from src.visualization.plot_fragility import plot_fragility_curves
    from src.visualization.plot_frameworks import plot_framework_comparison

    # Plot IDA curves
    plot_ida_curves(ida_results, save_path='results/ida_curves.png')

    # Plot fragility curves
    plot_fragility_curves(fragility_params, save_path='results/fragility.png')

    # Framework comparison
    plot_framework_comparison(fw_results, save_path='results/framework_comparison.png')
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats as scipy_stats
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
import os

logger = logging.getLogger('visualization')


def setup_plotting(style: str = 'seaborn-v0_8-whitegrid',
                   font_size: int = 12) -> None:
    """
    Setup matplotlib plotting style

    Args:
        style: Matplotlib style
        font_size: Font size for plots
    """
    plt.style.use(style)
    plt.rcParams.update({
        'font.size': font_size,
        'axes.labelsize': font_size,
        'axes.titlesize': font_size + 2,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'legend.fontsize': font_size - 1,
        'figure.titlesize': font_size + 4
    })


def save_figure(fig, save_path: str, format: str = 'png', dpi: int = 300,
                bbox_inches: str = 'tight') -> None:
    """
    Save figure with consistent settings

    Args:
        fig: Matplotlib figure
        save_path: Output file path
        format: Image format
        dpi: Resolution
        bbox_inches: Bounding box settings
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, format=format, dpi=dpi, bbox_inches=bbox_inches)
    logger.info(f"Figure saved to {save_path}")


# ============================================================================
# IDA Curve Plots
# ============================================================================

def plot_ida_curves(ida_df: pd.DataFrame,
                    building_ids: Optional[List[str]] = None,
                    sa_column: str = 'intensity',
                    pidr_column: str = 'pidr',
                    framework_column: str = 'framework',
                    save_path: Optional[str] = None,
                    dpi: int = 300) -> None:
    """
    Plot IDA curves (PIDR vs Sa)

    Args:
        ida_df: IDA results DataFrame
        building_ids: List of building IDs to plot (None = all)
        sa_column: Column name for spectral acceleration
        pidr_column: Column name for PIDR
        framework_column: Column name for framework type
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Filter to buildings if specified
    if building_ids is not None:
        ida_df = ida_df[ida_df['building_id'].isin(building_ids)]

    # Group by building and plot
    group_cols = ['building_id']
    if framework_column in ida_df.columns:
        group_cols.append(framework_column)

    groups = ida_df.groupby(group_cols)

    colors = plt.cm.tab10(np.linspace(0, 1, len(groups)))

    for (group, color) in zip(groups, colors):
        name = group if isinstance(group, str) else ' - '.join(map(str, group))
        data = group[1]

        # Sort by intensity
        data = data.sort_values(sa_column)

        ax.plot(data[sa_column], data[pidr_column] * 100, '-', color=color,
               linewidth=2, label=name, alpha=0.8)

    ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
    ax.set_ylabel('Peak Inter-Story Drift Ratio [%]')
    ax.set_title('Incremental Dynamic Analysis (IDA) Curves')
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0.)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


def plot_ida_summary(ida_df: pd.DataFrame,
                     sa_column: str = 'intensity',
                     pidr_column: str = 'pidr',
                     framework_column: str = 'framework',
                     save_path: Optional[str] = None,
                     dpi: int = 300) -> None:
    """
    Plot IDA summary: median curves with 16th/84th percentile bands

    Args:
        ida_df: IDA results DataFrame
        sa_column: Column name for spectral acceleration
        pidr_column: Column name for PIDR
        framework_column: Column name for framework type
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Group by framework
    if framework_column in ida_df.columns:
        groups = ida_df.groupby(framework_column)
        colors = {'nonsway': '#333', 'omrf': '#e74c3c',
                 'imrf': '#f39c12', 'smrf': '#3498db'}
    else:
        groups = [('All', ida_df)]
        colors = {'All': 'blue'}

    for framework, data in groups:
        # Sort and group by intensity
        data = data.sort_values(sa_column)

        # Compute median and percentiles
        summary = data.groupby(sa_column)[pidr_column].agg(
            ['median', lambda x: np.percentile(x, 16),
             lambda x: np.percentile(x, 84)]
        ).rename(columns={'median': 'median', '<lambda>': 'p16', '<lambda_0>': 'p84'})

        # Get color
        color = colors.get(framework, 'blue')

        # Plot median
        ax.plot(summary.index, summary['median'] * 100, '-', color=color,
               linewidth=2, label=framework)

        # Plot band
        ax.fill_between(summary.index, summary['p16'] * 100, summary['p84'] * 100,
                       color=color, alpha=0.2)

    ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
    ax.set_ylabel('PIDR [%]')
    ax.set_title('IDA Summary: Median and Percentile Bands')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


# ============================================================================
# Fragility Curve Plots
# ============================================================================

def plot_fragility_curves(fragility_params: pd.DataFrame,
                          sa_range: Optional[np.ndarray] = None,
                          save_path: Optional[str] = None,
                          dpi: int = 300) -> None:
    """
    Plot fragility curves

    Args:
        fragility_params: Fragility parameters DataFrame
        sa_range: Spectral acceleration range (auto-computed if None)
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    if sa_range is None:
        sa_range = np.linspace(0.01, 1.5, 200)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Map performance levels to colors
    colors = {
        'IO': '#2ecc71',   # Green
        'LS': '#f1c40f',   # Yellow
        'CP': '#e74c3c',   # Red
        'CO': '#c0392b'    # Dark red
    }

    thresholds = {
        0.01: 'IO',
        0.025: 'LS',
        0.04: 'CP'
    }

    for _, row in fragility_params.iterrows():
        pidr_threshold = row['pidr_threshold']
        theta = row['theta']
        beta = row['beta']

        # Compute probability
        ln_sa = np.log(sa_range)
        ln_theta = np.log(theta)
        z = (ln_theta - ln_sa) / beta
        prob = scipy_stats.norm.cdf(z)

        # Get level
        level = thresholds.get(pidr_threshold, f'T{pidr_threshold:.3f}')

        ax.plot(sa_range, prob, '-', color=colors.get(level, 'blue'),
               linewidth=2, label=f'{level} (θ={theta:.3f}, β={beta:.3f})')

    ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
    ax.set_ylabel('Probability of Exceedance')
    ax.set_title('Seismic Fragility Curves')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0, top=1.05)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


def plot_zone_fragility_comparison(zone_params: Dict[str, pd.DataFrame],
                                   save_path: Optional[str] = None,
                                   dpi: int = 300) -> None:
    """
    Plot fragility curves for multiple zones

    Args:
        zone_params: Dictionary mapping zone to fragility DataFrame
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    zones = list(zone_params.keys())
    colors = {'IO': '#2ecc71', 'LS': '#f1c40f', 'CP': '#e74c3c'}

    for idx, zone in enumerate(zones):
        ax = axes[idx]
        params = zone_params[zone]
        sa_range = np.linspace(0.01, 1.5, 200)

        for _, row in params.iterrows():
            if row['pidr_threshold'] > 0.1:
                continue

            theta = row['theta']
            beta = row['beta']

            # Determine level
            if abs(row['pidr_threshold'] - 0.01) < 0.001:
                level = 'IO'
            elif abs(row['pidr_threshold'] - 0.025) < 0.001:
                level = 'LS'
            else:
                level = 'CP'

            # Compute probability
            ln_sa = np.log(sa_range)
            ln_theta = np.log(theta)
            z = (ln_theta - ln_sa) / beta
            prob = scipy_stats.norm.cdf(z)

            ax.plot(sa_range, prob, '-', color=colors[level], linewidth=2, label=level)

        ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
        ax.set_ylabel('Probability')
        ax.set_title(f'Seismic Zone {zone}')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0, top=1.05)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


# ============================================================================
# Framework Comparison Plots
# ============================================================================

def plot_framework_comparison(fw_df: pd.DataFrame,
                              pidr_column: str = 'pidr',
                              framework_column: str = 'framework',
                              intensity_column: str = 'intensity',
                              save_path: Optional[str] = None,
                              dpi: int = 300) -> None:
    """
    Plot multi-framework comparison

    Args:
        fw_df: Framework comparison results DataFrame
        pidr_column: Column name for PIDR
        framework_column: Column name for framework type
        intensity_column: Column name for intensity
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Top: PIDR vs Sa for each framework
    ax = axes[0, 0]
    colors = {'nonsway': '#333', 'omrf': '#e74c3c', 'imrf': '#f39c12', 'smrf': '#3498db'}

    for fw in fw_df[framework_column].unique():
        data = fw_df[fw_df[framework_column] == fw]
        data = data.sort_values(intensity_column)

        ax.plot(data[intensity_column], data[pidr_column] * 100, '-', color=colors.get(fw, 'gray'),
               linewidth=2, label=fw)

    ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
    ax.set_ylabel('PIDR [%]')
    ax.set_title('Framework Comparison: PIDR vs Sa')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Bottom left: Performance gradient
    ax = axes[0, 1]
    nonsway_median = fw_df[fw_df[framework_column] == 'nonsway'].groupby(intensity_column)[pidr_column].median()

    for fw in fw_df[framework_column].unique():
        if fw == 'nonsway':
            continue
        data = fw_df[fw_df[framework_column] == fw].groupby(intensity_column)[pidr_column].median()
        pg = (nonsway_median - data) / nonsway_median * 100
        ax.plot(pg.index, pg.values, '-', color=colors.get(fw, 'gray'),
               linewidth=2, label=fw)

    ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
    ax.set_ylabel('Performance Gradient vs Non-Sway [%]')
    ax.set_title('Performance Gradient')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Bottom right: Histogram of PIDR by framework
    ax = axes[1, 0]
    for fw in fw_df[framework_column].unique():
        data = fw_df[fw_df[framework_column] == fw][pidr_column] * 100
        ax.hist(data, bins=50, alpha=0.5, label=fw, density=True)

    ax.set_xlabel('PIDR [%]')
    ax.set_ylabel('Density')
    ax.set_title('PIDR Distribution by Framework')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Bottom right: Framework complexity vs performance
    ax = axes[1, 1]
    complexity = {'nonsway': 1.0, 'omrf': 1.3, 'imrf': 1.8, 'smrf': 2.5}
    perf_gradient = {}

    for fw in fw_df[framework_column].unique():
        data = fw_df[fw_df[framework_column] == fw].groupby(intensity_column)[pidr_column].median()
        if 'nonsway' in fw_df[framework_column].values:
            pg = (nonsway_median - data) / nonsway_median * 100
            perf_gradient[fw] = pg.mean()
        else:
            perf_gradient[fw] = 0

    x = [complexity.get(fw, 1.0) for fw in perf_gradient.keys()]
    y = list(perf_gradient.values())
    labels = list(perf_gradient.keys())

    ax.scatter(x, y, s=200, alpha=0.6)
    for label, xi, yi in zip(labels, x, y):
        ax.annotate(label, (xi, yi), textcoords="offset points", xytext=(5, 5))

    ax.set_xlabel('Framework Complexity Index')
    ax.set_ylabel('Avg Performance Gradient [%]')
    ax.set_title('Complexity vs Performance')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


# ============================================================================
# SHAP Visualization
# ============================================================================

def plot_shap_summary(shap_values: np.ndarray, feature_names: List[str],
                     save_path: Optional[str] = None, dpi: int = 300) -> None:
    """
    Plot SHAP summary plot

    Args:
        shap_values: SHAP values array
        feature_names: List of feature names
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Compute importance
    importance = np.abs(shap_values).mean(axis=0)

    # Create bar plot
    sorted_idx = np.argsort(importance)[::-1]
    features = [feature_names[i] for i in sorted_idx]
    importances = importance[sorted_idx]

    y_pos = range(len(features))
    ax.barh(y_pos, importances, color='steelblue')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features)
    ax.set_xlabel('SHAP Value (mean |importance|)')
    ax.set_title('Feature Importance (SHAP)')
    ax.invert_yaxis()

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


def plot_shap_dependence(shap_values: np.ndarray, feature_names: List[str],
                        X: pd.DataFrame, feature: str,
                        save_path: Optional[str] = None, dpi: int = 300) -> None:
    """
    Plot SHAP dependence plot for a feature

    Args:
        shap_values: SHAP values array
        feature_names: List of feature names
        X: Feature DataFrame
        feature: Feature name to plot
        save_path: Path to save plot (optional)
        dpi: Resolution
    """
    if feature not in feature_names:
        logger.warning(f"Feature '{feature}' not found")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    feature_idx = feature_names.index(feature)
    shap_for_feature = shap_values[:, feature_idx]
    feature_values = X[feature].values

    # Scatter plot
    scatter = ax.scatter(feature_values, shap_for_feature, c=feature_values,
                        cmap='viridis', alpha=0.5, s=10)

    ax.set_xlabel(feature)
    ax.set_ylabel('SHAP Value')
    ax.set_title(f'SHAP Dependence Plot: {feature}')
    plt.colorbar(scatter, label=feature)

    # Add line for trend
    if len(np.unique(feature_values)) > 10:
        import scipy.stats as stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(feature_values, shap_for_feature)
        x_line = np.linspace(feature_values.min(), feature_values.max(), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', linewidth=2, label=f'Slope={slope:.3f}')

    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()

    if save_path:
        save_figure(fig, save_path, dpi=dpi)

    plt.show()


# ============================================================================
# Utility Functions
# ============================================================================

def get_figure_dimensions(pages: str = 'a4', orientation: str = 'landscape') -> Tuple[float, float]:
    """
    Get figure dimensions for publication

    Args:
        pages: Page size ('a4', 'letter')
        orientation: Orientation ('landscape', 'portrait')

    Returns:
        (width, height) in inches
    """
    if pages == 'a4':
        if orientation == 'landscape':
            return 11.69, 8.27
        else:
            return 8.27, 11.69
    else:  # letter
        if orientation == 'landscape':
            return 11.0, 8.5
        else:
            return 8.5, 11.0


# ============================================================================
# Export all functions
# ============================================================================

__all__ = [
    'setup_plotting',
    'save_figure',
    'plot_ida_curves',
    'plot_ida_summary',
    'plot_fragility_curves',
    'plot_zone_fragility_comparison',
    'plot_framework_comparison',
    'plot_shap_summary',
    'plot_shap_dependence',
    'get_figure_dimensions'
]
