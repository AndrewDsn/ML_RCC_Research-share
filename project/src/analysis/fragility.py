"""Fragility Curve Module

Generates seismic fragility curves for RC buildings under BNBC 2020.

Features:
- Log-normal fragility curve fitting
- Performance level thresholds (IO, LS, CP)
- Zone-specific fragility curves
- Damage state estimation
- Uncertainty quantification (dispersion beta)

References:
- FEMA P-58 (Seismic Performance Assessment)
- BNBC 2020 Section 3.2 (Seismic Fragility)
- Vamvatsikos & Cornell (2002) - IDA methodology
- "Uncertainty Quantification in Seismic Fragility Analysis" (2020)

Usage:
    from src.analysis.fragility import FragilityAnalyzer

    # Initialize analyzer
    analyzer = FragilityAnalyzer()

    # Compute fragility curves
    fragility = analyzer.compute_fragility(
        ida_results_df,
        pidr_thresholds=[0.01, 0.025, 0.04]
    )

    # Generate plots
    analyzer.plot_fragility_curves(fragility, save_path='results/fragility.png')
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
import os

logger = logging.getLogger('fragility')


class FragilityAnalyzer:
    """
    Fragility curve analyzer for seismic performance assessment
    """

    def __init__(self, damping: float = 0.05):
        """
        Initialize fragility analyzer

        Args:
            damping: Damping ratio (default 0.05 = 5%)
        """
        self.damping = damping
        self.performance_levels = {
            'IO': {'threshold': 0.01, 'description': 'Immediate Occupancy'},
            'LS': {'threshold': 0.025, 'description': 'Life Safety'},
            'CP': {'threshold': 0.04, 'description': 'Collapse Prevention'},
            'CO': {'threshold': 0.10, 'description': 'Collapse'}
        }

        self.performance_levels['LS']['threshold'] = 0.025

    def compute_fragility_parameters(self, ida_df: pd.DataFrame,
                                     pidr_threshold: float,
                                     sa_column: str = 'intensity',
                                     pidr_column: str = 'pidr') -> Dict[str, float]:
        """
        Compute fragility curve parameters using Cloud Analysis method

        Fits log-normal distribution to IDA results at given PIDR threshold.

        Args:
            ida_df: IDA results DataFrame
            pidr_threshold: PIDR threshold for fragility curve
            sa_column: Column name for spectral acceleration
            pidr_column: Column name for PIDR

        Returns:
            Dictionary with fragility parameters (theta, beta)
        """
        # Filter data where PIDR exceeds threshold
        df = ida_df.copy()
        df['exceeds'] = df[pidr_column] >= pidr_threshold

        # Get Sa values for exceedance events
        sa_values = df.loc[df['exceeds'], sa_column]

        if len(sa_values) < 3:
            logger.warning(f"Not enough exceedances for PIDR={pidr_threshold:.4f}")
            return {'theta': np.nan, 'beta': np.nan, 'n_exceedances': len(sa_values)}

        # Log-linear regression in log-log space
        # ln(PIDR) = a + b * ln(Sa) + epsilon
        sa_log = np.log(sa_values)
        pidr_log = np.log(df.loc[df['exceeds'], pidr_column])

        # Fit linear model
        slope, intercept, r_value, p_value, std_err = stats.linregress(sa_log, pidr_log)

        # Compute theta (median Sa at which P(PIDR > threshold) = 0.5)
        # At the threshold: ln(threshold) = a + b * ln(theta)
        # ln(theta) = (ln(threshold) - a) / b
        ln_theta = (np.log(pidr_threshold) - intercept) / slope
        theta = np.exp(ln_theta)

        # Compute dispersion (beta)
        # beta = std[ln(PIDR_i) - (a + b * ln(Sa_i))]
        predictions = intercept + slope * sa_log
        residuals = pidr_log - predictions
        beta = np.std(residuals, ddof=2)  # ddof=2 for 2 parameters

        return {
            'theta': float(theta),
            'beta': float(beta),
            'r_squared': float(r_value ** 2),
            'n_exceedances': len(sa_values),
            'n_total': len(df),
            'exceedance_rate': float(len(sa_values) / len(df))
        }

    def compute_fragility_curve(self, theta: float, beta: float,
                                sa_range: np.ndarray) -> np.ndarray:
        """
        Compute fragility curve probabilities

        P(LS | Sa) = Φ[(ln(Sa) - ln(θ)) / β]

        Args:
            theta: Median Sa at 50% exceedance
            beta: Log-standard deviation
            sa_range: Spectral acceleration values

        Returns:
            Probabilities of exceeding threshold at each Sa
        """
        # Log-normal CDF
        # P(X > x) = 1 - Φ[(ln(x) - μ) / σ] = Φ[(μ - ln(x)) / σ]
        # For fragility: P(exceed | Sa) = Φ[(ln(θ) - ln(Sa)) / β]
        # = Φ[(ln(θ/Sa)) / β]

        ln_sa = np.log(sa_range)
        ln_theta = np.log(theta)

        # Standardized values
        z = (ln_theta - ln_sa) / beta

        # Standard normal CDF
        probabilities = stats.norm.cdf(z)

        return probabilities

    def compute_all_fragility_parameters(self, ida_df: pd.DataFrame,
                                         pidr_thresholds: List[float],
                                         sa_column: str = 'intensity',
                                         pidr_column: str = 'pidr') -> pd.DataFrame:
        """
        Compute fragility parameters for multiple thresholds

        Args:
            ida_df: IDA results DataFrame
            pidr_thresholds: List of PIDR thresholds
            sa_column: Column name for spectral acceleration
            pidr_column: Column name for PIDR

        Returns:
            DataFrame with fragility parameters for each threshold
        """
        results = []

        for threshold in pidr_thresholds:
            params = self.compute_fragility_parameters(
                ida_df, threshold, sa_column, pidr_column
            )
            params['pidr_threshold'] = threshold
            results.append(params)

        return pd.DataFrame(results)

    def compute_zone_fragility(self, ida_df: pd.DataFrame,
                               zone_column: str = 'zone',
                               sa_column: str = 'intensity',
                               pidr_column: str = 'pidr') -> Dict[str, pd.DataFrame]:
        """
        Compute fragility curves for each seismic zone

        Args:
            ida_df: IDA results DataFrame
            zone_column: Column name for seismic zone
            sa_column: Column name for spectral acceleration
            pidr_column: Column name for PIDR

        Returns:
            Dictionary mapping zone to fragility parameters DataFrame
        """
        zones = ida_df[zone_column].unique()
        zone_fragility = {}

        for zone in zones:
            zone_df = ida_df[ida_df[zone_column] == zone]
            logger.info(f"Computing fragility for zone {zone}: {len(zone_df)} records")

            thresholds = [0.01, 0.025, 0.04]  # IO, LS, CP
            zone_fragility[zone] = self.compute_all_fragility_parameters(
                zone_df, thresholds, sa_column, pidr_column
            )

        return zone_fragility

    def compute_damage_state(self, pidr: float) -> Dict[str, bool]:
        """
        Determine damage state for given PIDR

        Args:
            pidr: Peak Inter-Story Drift Ratio

        Returns:
            Dictionary with damage state flags
        """
        return {
            'no_damage': pidr < self.performance_levels['IO']['threshold'],
            'minor_damage': (self.performance_levels['IO']['threshold'] <= pidr <
                            self.performance_levels['LS']['threshold']),
            'moderate_damage': (self.performance_levels['LS']['threshold'] <= pidr <
                               self.performance_levels['CP']['threshold']),
            'extensive_damage': (self.performance_levels['CP']['threshold'] <= pidr <
                                self.performance_levels['CO']['threshold']),
            'collapse': pidr >= self.performance_levels['CO']['threshold']
        }

    def compute_probability_of_exceedance(self, sa: float,
                                           theta: float,
                                           beta: float) -> float:
        """
        Compute probability of exceeding a performance level

        P(PIDR > threshold | Sa) = Φ[(ln(θ) - ln(Sa)) / β]

        Args:
            sa: Spectral acceleration
            theta: Median Sa for 50% exceedance
            beta: Log-standard deviation

        Returns:
            Probability of exceedance
        """
        ln_sa = np.log(sa)
        ln_theta = np.log(theta)

        z = (ln_theta - ln_sa) / beta
        return float(stats.norm.cdf(z))


def compute_fragility_curve(sa_values: np.ndarray,
                           theta: float,
                           beta: float) -> np.ndarray:
    """
    Compute fragility curve (probability vs Sa)

    Args:
        sa_values: Spectral acceleration values
        theta: Median Sa for 50% exceedance
        beta: Log-standard deviation

    Returns:
        Probabilities of exceeding threshold
    """
    ln_sa = np.log(sa_values)
    ln_theta = np.log(theta)
    z = (ln_theta - ln_sa) / beta
    return stats.norm.cdf(z)


def plot_fragility_curves(sa_values: np.ndarray,
                         fragility_params: pd.DataFrame,
                         performance_levels: Dict[str, float],
                         save_path: Optional[str] = None,
                         format: str = 'png',
                         dpi: int = 300) -> None:
    """
    Plot fragility curves

    Args:
        sa_values: Spectral acceleration range
        fragility_params: DataFrame with fragility parameters
        performance_levels: Dictionary mapping level to PIDR threshold
        save_path: Path to save plot (optional)
        format: Image format
        dpi: Resolution
    """
    plt.figure(figsize=(12, 8))

    # Color map for performance levels
    colors = {
        'IO': '#2ecc71',   # Green
        'LS': '#f1c40f',   # Yellow
        'CP': '#e74c3c',   # Red
        'CO': '#c0392b'    # Dark red
    }

    # Plot curves
    for _, row in fragility_params.iterrows():
        pidr_threshold = row['pidr_threshold']
        theta = row['theta']
        beta = row['beta']

        # Find performance level for this threshold
        level = None
        for lvl, data in performance_levels.items():
            if abs(data['threshold'] - pidr_threshold) < 0.001:
                level = lvl
                break

        if level is None:
            level = f'T{pidr_threshold:.3f}'

        # Compute fragility curve
        probabilities = compute_fragility_curve(sa_values, theta, beta)

        # Plot
        plt.plot(sa_values, probabilities, '-', color=colors.get(level, 'blue'),
                linewidth=2, label=f'{level} (θ={theta:.3f}, β={beta:.3f})')

    plt.xlabel('Spectral Acceleration Sa(T1) [g]')
    plt.ylabel('Probability of Exceedance')
    plt.title('Seismic Fragility Curves')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.xlim(left=0)
    plt.ylim(bottom=0, top=1.05)

    # Add vertical lines at common intensities
    for sa in [0.1, 0.2, 0.3, 0.5, 1.0]:
        plt.axvline(x=sa, color='gray', linestyle='--', alpha=0.5)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
        logger.info(f"Fragility curves saved to {save_path}")

    plt.show()


def plot_zone_fragility_comparison(zone_fragility: Dict[str, pd.DataFrame],
                                  save_path: Optional[str] = None,
                                  format: str = 'png',
                                  dpi: int = 300) -> None:
    """
    Plot fragility curves comparing multiple zones

    Args:
        zone_fragility: Dictionary mapping zone to fragility DataFrame
        save_path: Path to save plot (optional)
        format: Image format
        dpi: Resolution
    """
    # Create figure with subplots (one per zone)
    n_zones = len(zone_fragility)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    colors = {
        'IO': '#2ecc71',
        'LS': '#f1c40f',
        'CP': '#e74c3c'
    }

    for idx, (zone, params_df) in enumerate(zone_fragility.items()):
        ax = axes[idx]
        sa_range = np.linspace(0.01, 1.5, 200)

        # Plot each performance level
        for _, row in params_df.iterrows():
            if row['pidr_threshold'] > 0.1:  # Skip CO
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

            probabilities = compute_fragility_curve(sa_range, theta, beta)
            ax.plot(sa_range, probabilities, '-', color=colors[level],
                   linewidth=2, label=level)

        ax.set_xlabel('Spectral Acceleration Sa(T1) [g]')
        ax.set_ylabel('Probability')
        ax.set_title(f'Seismic Zone {zone} - Fragility Curves')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0, top=1.05)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
        logger.info(f"Zone fragility comparison saved to {save_path}")

    plt.show()


def export_fragility_table(fragility_params: pd.DataFrame,
                           output_path: str) -> None:
    """
    Export fragility parameters to LaTeX/CSV table

    Args:
        fragility_params: Fragility parameters DataFrame
        output_path: Output file path
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Prepare table
    table_df = fragility_params.copy()
    table_df['performance_level'] = table_df['pidr_threshold'].apply(
        lambda x: 'IO' if abs(x - 0.01) < 0.001 else ('LS' if abs(x - 0.025) < 0.001 else 'CP')
    )

    table_df['theta_pct'] = table_df['theta'] * 100
    table_df['beta_pct'] = table_df['beta'] * 100

    # Reorder columns
    table_df = table_df[['theta', 'beta', 'r_squared', 'n_exceedances', 'n_total', 'exceedance_rate']]

    # Save
    table_df.to_csv(output_path, index_label='performance_level')

    # Generate LaTeX table
    latex_path = output_path.replace('.csv', '.tex')
    with open(latex_path, 'w') as f:
        f.write(table_df.to_latex(index=True, float_format='%.4f'))

    logger.info(f"Fragility table exported to {output_path}")
    logger.info(f"LaTeX table exported to {latex_path}")


# Default Sa range for fragility curves
DEFAULT_SA_RANGE = np.linspace(0.01, 1.5, 200)

# Default performance level thresholds
DEFAULT_PERFORMANCE_LEVELS = {
    'IO': {'threshold': 0.01, 'description': 'Immediate Occupancy'},
    'LS': {'threshold': 0.025, 'description': 'Life Safety'},
    'CP': {'threshold': 0.04, 'description': 'Collapse Prevention'},
    'CO': {'threshold': 0.10, 'description': 'Collapse'}
}


__all__ = [
    'FragilityAnalyzer',
    'compute_fragility_curve',
    'plot_fragility_curves',
    'plot_zone_fragility_comparison',
    'export_fragility_table',
    'DEFAULT_SA_RANGE',
    'DEFAULT_PERFORMANCE_LEVELS'
]
