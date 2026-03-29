"""SHAP Analyzer Module

SHAP (SHapley Additive exPlanations) feature importance analysis for
seismic drift prediction models.

Features:
- TreeExplainer for RF and XGBoost models
- SHAP value computation
- Summary plots (beeswarm, bar, dependence)
- Feature interaction analysis
- Framework-specific SHAP analysis

References:
- Lundberg & Lee (2017) - A Unified Approach to Interpreting Model Predictions
- SHAP documentation: https://shap.readthedocs.io
- BNBC 2020 Section 3.2 (Seismic Parameters)

Usage:
    from src.ml.shap_analyzer import SHAPAnalyzer
    from src.ida.data_compiler import create_ml_dataset
    from sklearn.ensemble import RandomForestRegressor

    # Load and prepare data
    df = create_ml_dataset(raw_df)

    # Train model
    X = df.drop('ln_pidr', axis=1)
    y = df['ln_pidr']

    model = RandomForestRegressor(n_estimators=300)
    model.fit(X, y)

    # SHAP analysis
    analyzer = SHAPAnalyzer(model, X)
    shap_values = analyzer.compute_shap_values(X)

    # Generate plots
    analyzer.summary_plot()
    analyzer.dependence_plot('ln_sa')
    analyzer.feature_importance()
"""

import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
import os

logger = logging.getLogger('shap_analyzer')


class SHAPAnalyzer:
    """
    SHAP feature importance analyzer for seismic drift models
    """

    def __init__(self, model, X_background: pd.DataFrame,
                 feature_names: Optional[List[str]] = None):
        """
        Initialize SHAP analyzer

        Args:
            model: Trained ML model (RF, XGBoost, etc.)
            X_background: Background dataset for SHAP (used for kernel explainer)
            feature_names: List of feature names (auto-detect if None)
        """
        self.model = model
        self.X_background = X_background
        self.feature_names = feature_names or X_background.columns.tolist()

        # SHAP values storage
        self.shap_values = None
        self.explainer = None

    def _get_explainer(self, X: pd.DataFrame):
        """Get appropriate SHAP explainer for model type"""
        model_type = type(self.model).__name__

        # Tree-based models: use TreeExplainer
        if model_type in ['RandomForestRegressor', 'XGBRegressor',
                          'GradientBoostingRegressor', 'CatBoostRegressor']:
            return shap.TreeExplainer(self.model, X, feature_perturbation="interventional")

        # Linear models: use KernelExplainer
        elif model_type in ['LinearRegression', 'Ridge', 'Lasso']:
            return shap.LinearExplainer(self.model, X)

        # Default: use KernelExplainer
        else:
            return shap.KernelExplainer(self.model.predict, X, link="logit")

    def compute_shap_values(self, X: pd.DataFrame, **kwargs) -> np.ndarray:
        """
        Compute SHAP values for input data

        Args:
            X: Input features
            **kwargs: Additional arguments for explainer.shap_values()

        Returns:
            SHAP values array
        """
        if self.explainer is None:
            self.explainer = self._get_explainer(self.X_background)

        logger.info(f"Computing SHAP values for {len(X)} samples...")

        self.shap_values = self.explainer.shap_values(X, **kwargs)

        # Handle multi-output case (return SHAP values for first output)
        if isinstance(self.shap_values, list):
            self.shap_values = self.shap_values[0]

        logger.info(f"SHAP values computed: shape {self.shap_values.shape}")

        return self.shap_values

    def get_feature_importance(self, method: str = 'mean_abs') -> pd.DataFrame:
        """
        Get feature importance from SHAP values

        Args:
            method: Importance method ('mean_abs', 'mean_sq', 'max')

        Returns:
            DataFrame with feature importances
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        # Compute importance based on method
        if method == 'mean_abs':
            importance = np.abs(self.shap_values).mean(axis=0)
        elif method == 'mean_sq':
            importance = (self.shap_values ** 2).mean(axis=0)
        elif method == 'max':
            importance = np.abs(self.shap_values).max(axis=0)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return importance_df

    def summary_plot(self, save_path: Optional[str] = None,
                     format: str = 'png', dpi: int = 300) -> None:
        """
        Generate SHAP summary plot (beeswarm)

        Args:
            save_path: Path to save plot (optional)
            format: Image format
            dpi: Resolution
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        # Create figure
        plt.figure(figsize=(10, 8))

        # Create beeswarm plot
        shap.summary_plot(
            self.shap_values,
            self.X_background,
            feature_names=self.feature_names,
            show=False
        )

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Summary plot saved to {save_path}")

        plt.show()

    def bar_plot(self, save_path: Optional[str] = None,
                 format: str = 'png', dpi: int = 300,
                 max_display: int = 20) -> None:
        """
        Generate SHAP bar plot of feature importance

        Args:
            save_path: Path to save plot (optional)
            format: Image format
            dpi: Resolution
            max_display: Maximum features to display
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        # Create figure
        plt.figure(figsize=(10, 8))

        # Create bar plot
        shap.summary_plot(
            self.shap_values,
            self.X_background,
            feature_names=self.feature_names,
            plot_type='bar',
            show=False
        )

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Bar plot saved to {save_path}")

        plt.show()

    def dependence_plot(self, feature: str, save_path: Optional[str] = None,
                        format: str = 'png', dpi: int = 300) -> None:
        """
        Generate SHAP dependence plot for a feature

        Args:
            feature: Feature name to plot
            save_path: Path to save plot (optional)
            format: Image format
            dpi: Resolution
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        if feature not in self.feature_names:
            raise ValueError(f"Feature '{feature}' not found in feature names")

        # Create figure
        plt.figure(figsize=(10, 8))

        # Find feature index
        feature_idx = self.feature_names.index(feature)

        # Create dependence plot
        shap.dependence_plot(
            feature_idx,
            self.shap_values,
            self.X_background,
            feature_names=self.feature_names,
            show=False
        )

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Dependence plot saved to {save_path}")

        plt.show()

    def interaction_plot(self, feature: str, save_path: Optional[str] = None,
                         format: str = 'png', dpi: int = 300) -> None:
        """
        Generate SHAP interaction plot

        Args:
            feature: Feature name to analyze interactions
            save_path: Path to save plot (optional)
            format: Image format
            dpi: Resolution
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        if feature not in self.feature_names:
            raise ValueError(f"Feature '{feature}' not found in feature names")

        # Create figure
        plt.figure(figsize=(10, 8))

        # Find feature index
        feature_idx = self.feature_names.index(feature)

        # Create interaction plot
        shap.dependence_plot(
            feature_idx,
            self.shap_values,
            self.X_background,
            feature_names=self.feature_names,
            interaction_index='auto',
            show=False
        )

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Interaction plot saved to {save_path}")

        plt.show()

    def waterfall_plot(self, sample_idx: int, save_path: Optional[str] = None,
                       format: str = 'png', dpi: int = 300) -> None:
        """
        Generate SHAP waterfall plot for a single prediction

        Args:
            sample_idx: Index of sample to explain
            save_path: Path to save plot (optional)
            format: Image format
            dpi: Resolution
        """
        if self.shap_values is None:
            raise ValueError("SHAP values not computed. Call compute_shap_values() first.")

        # Get expected value
        expected_value = self.explainer.expected_value
        if isinstance(expected_value, list):
            expected_value = expected_value[0]

        # Get SHAP values for this sample
        shap_vals = self.shap_values[sample_idx]

        # Create waterfall plot
        plt.figure(figsize=(12, 8))

        # Create waterfall manually
        features_df = pd.DataFrame({
            'feature': self.feature_names,
            'shap_value': shap_vals
        }).sort_values('shap_value', key=abs, ascending=True)

        # Calculate cumulative SHAP values
        features_df['cumulative'] = features_df['shap_value'].cumsum()
        features_df['base'] = features_df['cumulative'] - features_df['shap_value']

        # Create waterfall bars
        colors = ['#ff6b6b' if v < 0 else '#4ecdc4' for v in features_df['shap_value']]

        y_pos = range(len(features_df))
        plt.barh(y_pos, features_df['shap_value'], left=features_df['base'], color=colors)
        plt.axvline(x=expected_value, color='black', linestyle='--', label=f'Expected ({expected_value:.4f})')

        plt.yticks(y_pos, features_df['feature'])
        plt.xlabel('SHAP Value')
        plt.title(f'Waterfall Plot - Sample {sample_idx}')
        plt.grid(axis='x', alpha=0.3)
        plt.legend()

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"Waterfall plot saved to {save_path}")

        plt.show()

    def generate_all_plots(self, output_dir: str, X: pd.DataFrame,
                           sample_size: int = 100) -> Dict[str, str]:
        """
        Generate all SHAP plots and return paths

        Args:
            output_dir: Output directory
            X: Input features for analysis
            sample_size: Number of samples for plots

        Returns:
            Dictionary of plot names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)

        # Use subset of data for plots (faster)
        if len(X) > sample_size:
            X_sample = X.sample(n=sample_size, random_state=42)
        else:
            X_sample = X

        # Compute SHAP values if not already done
        if self.shap_values is None:
            self.compute_shap_values(X_sample)

        plots = {}

        # Summary plot (beeswarm)
        plots['summary_beeswarm'] = os.path.join(output_dir, 'shap_summary_beeswarm.png')
        self.summary_plot(save_path=plots['summary_beeswarm'])

        # Bar plot
        plots['bar_importance'] = os.path.join(output_dir, 'shap_bar_importance.png')
        self.bar_plot(save_path=plots['bar_importance'])

        # Dependence plots for top features
        importance_df = self.get_feature_importance()
        top_features = importance_df.head(5)['feature'].tolist()

        for feature in top_features:
            plot_key = f'dependence_{feature}'
            plots[plot_key] = os.path.join(output_dir, f'shap_dependence_{feature}.png')
            self.dependence_plot(feature, save_path=plots[plot_key])

        # Interaction plot for top feature
        if top_features:
            plots['interaction_top'] = os.path.join(output_dir, f'shap_interaction_{top_features[0]}.png')
            self.interaction_plot(top_features[0], save_path=plots['interaction_top'])

        return plots


def compare_framework_shap(analyzer_dict: Dict[str, SHAPAnalyzer],
                           output_dir: str) -> None:
    """
    Compare SHAP analysis across framework types

    Args:
        analyzer_dict: Dictionary mapping framework -> SHAPAnalyzer
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect feature importances
    all_importances = []

    for framework, analyzer in analyzer_dict.items():
        importance_df = analyzer.get_feature_importance()
        importance_df['framework'] = framework
        all_importances.append(importance_df)

    # Combine
    combined = pd.concat(all_importances, ignore_index=True)

    # Plot comparison
    plt.figure(figsize=(14, 10))

    # Pivot for plotting
    pivot = combined.pivot_table(
        index='feature',
        columns='framework',
        values='importance',
        aggfunc='mean'
    )

    # Normalize by framework
    pivot_normalized = pivot.div(pivot.sum(axis=1), axis=0)

    # Plot
    pivot_normalized.plot(kind='bar', figsize=(14, 8))
    plt.ylabel('Normalized Importance')
    plt.title('SHAP Feature Importance Comparison by Framework')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Framework')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_framework_comparison.png'), dpi=300)
    plt.close()

    logger.info(f"Framework SHAP comparison saved to {output_dir}")


def save_shap_results(analyzer: SHAPAnalyzer, output_dir: str) -> None:
    """
    Save SHAP analysis results

    Args:
        analyzer: SHAPAnalyzer with computed values
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)

    # Save feature importance
    importance_df = analyzer.get_feature_importance()
    importance_df.to_csv(os.path.join(output_dir, 'shap_feature_importance.csv'), index=False)

    # Save SHAP values
    shap_df = pd.DataFrame(
        analyzer.shap_values,
        columns=analyzer.feature_names
    )
    shap_df.to_csv(os.path.join(output_dir, 'shap_values.csv'), index=False)

    # Save summary statistics
    summary = {
        'mean_shap': analyzer.shap_values.mean(axis=0).tolist(),
        'std_shap': analyzer.shap_values.std(axis=0).tolist(),
        'min_shap': analyzer.shap_values.min(axis=0).tolist(),
        'max_shap': analyzer.shap_values.max(axis=0).tolist()
    }

    import json
    with open(os.path.join(output_dir, 'shap_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"SHAP results saved to {output_dir}")


__all__ = [
    'SHAPAnalyzer',
    'compare_framework_shap',
    'save_shap_results'
]
