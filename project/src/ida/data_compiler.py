"""Data Compiler Module

Compiles IDA results into ML-ready datasets with feature engineering.

Features:
- Merge results from multiple IDA runs
- Feature engineering (structural + seismic features)
- Data validation and QC
- Dataset splitting (train/test)
- Format conversion (CSV, HDF5)

References:
- BNBC 2020 Section 3.2 (Seismic Parameters)
- ASCE 7-22 Chapter 11 (Seismic Design)
- Vamvatsikos & Cornell (2002) - IDA methodology

Usage:
    from src.ida.data_compiler import compile_dataset, EngineerFeatures

    # Compile results from multiple files
    df = compile_dataset([
        'data/raw/ida_results_zone1.csv',
        'data/raw/ida_results_zone2.csv'
    ])

    # Engineer features
    engine = EngineerFeatures()
    df_features = engine.transform(df)

    # Save to different formats
    df_features.to_csv('data/processed/ida_master.csv')
    df_features.to_hdf('data/processed/ida_master.h5', key='data')
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging
import os

logger = logging.getLogger('data_compiler')


class FeatureEngineer:
    """
    Feature engineering for seismic drift prediction

    Creates features from raw IDA results:
    - Structural features (period, height, section properties)
    - Seismic features (intensity, zone, PGA)
    - Target features (log(PIDR), performance level)
    """

    def __init__(self):
        """Initialize feature engineer"""
        self.feature_names_ = None
        self.target_feature_ = 'ln_pidr'

    def fit(self, df: pd.DataFrame) -> 'FeatureEngineer':
        """Fit feature engineer (identity for now)"""
        self.feature_names_ = self._get_feature_names(df)
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe with engineered features

        Args:
            df: Input dataframe

        Returns:
            Dataframe with engineered features
        """
        df_out = df.copy()

        # Check if already has engineered features
        if 'ln_pidr' in df_out.columns:
            logger.info("Features already engineered, returning copy")
            return df_out

        # Create log-transformed target
        if 'peak_interstory_drift_ratio' in df_out.columns:
            df_out['ln_pidr'] = np.log(
                df_out['peak_interstory_drift_ratio'].clip(lower=1e-6)
            )
        elif 'pidr' in df_out.columns:
            df_out['ln_pidr'] = np.log(df_out['pidr'].clip(lower=1e-6))

        # Create log-transformed intensity
        if 'intensity' in df_out.columns:
            df_out['ln_sa'] = np.log(df_out['intensity'].clip(lower=1e-6))

        # Create categorical features
        if 'framework' in df_out.columns:
            df_out = pd.get_dummies(df_out, columns=['framework'], prefix='fw')

        if 'performance_level' in df_out.columns:
            df_out['is_early_failure'] = df_out['performance_level'].isin(['CP', 'collapse']).astype(int)

        return df_out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform"""
        return self.fit(df).transform(df)

    def _get_feature_names(self, df: pd.DataFrame) -> List[str]:
        """Get list of feature column names"""
        # Structural features
        structural = ['n_stories', 'total_height', 'fundamental_period',
                      'column_area', 'beam_area', 'reinforcement_ratio']

        # Seismic features
        seismic = ['seismic_zone_coeff', 'response_mod_factor', 'importance_factor',
                   'ln_sa', 'pga', 'pgv']

        # Framework-specific features
        framework_specific = ['confinement_factor', 'transverse_reinf_ratio']

        # All features
        features = [f for f in structural + seismic + framework_specific
                   if f in df.columns]

        return features


def compile_dataset(filepaths: Union[str, List[str]],
                   framework_filter: Optional[List[str]] = None,
                   min_records: int = 100) -> pd.DataFrame:
    """
    Compile IDA results from multiple files

    Args:
        filepaths: List of file paths or single directory path
        framework_filter: List of framework types to include
        min_records: Minimum records required per file

    Returns:
        Combined DataFrame
    """
    if isinstance(filepaths, str):
        if os.path.isdir(filepaths):
            # Get all CSV files in directory
            filepaths = list(Path(filepaths).glob('*.csv'))
        else:
            filepaths = [filepaths]

    dataframes = []
    for filepath in filepaths:
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {filepath}: {len(df)} records")

            # Filter by framework if specified
            if framework_filter is not None and 'framework' in df.columns:
                df = df[df['framework'].isin(framework_filter)]

            # Check minimum records
            if len(df) >= min_records:
                dataframes.append(df)
            else:
                logger.warning(f"Skipping {filepath}: only {len(df)} records")

        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")

    if not dataframes:
        raise ValueError("No valid data files found")

    # Combine
    combined = pd.concat(dataframes, ignore_index=True)

    # Remove duplicates
    if 'task_id' in combined.columns:
        combined = combined.drop_duplicates(subset=['task_id'])

    logger.info(f"Combined dataset: {len(combined)} total records")

    return combined


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features for ML training

    Args:
        df: Raw IDA results DataFrame

    Returns:
        DataFrame with engineered features
    """
    df_out = df.copy()

    # Target variable - log(PIDR)
    if 'pidr' in df_out.columns:
        df_out['ln_pidr'] = np.log(df_out['pidr'].clip(lower=1e-6))
    elif 'peak_interstory_drift_ratio' in df_out.columns:
        df_out['ln_pidr'] = np.log(df_out['peak_interstory_drift_ratio'].clip(lower=1e-6))

    # Log-transform intensity
    if 'intensity' in df_out.columns:
        df_out['ln_sa'] = np.log(df_out['intensity'].clip(lower=1e-6))

    # Period estimation from height
    if 'total_height' in df_out.columns and 'fundamental_period' not in df_out.columns:
        # BNBC 2020 approximate formula: T = 0.0466 * H^0.90
        df_out['fundamental_period'] = 0.0466 * df_out['total_height'] ** 0.90

    # Seismic zone coefficient
    zone_mapping = {
        'zone_1': 0.12, 'zone_I': 0.12, 'Z1': 0.12,
        'zone_2': 0.18, 'zone_II': 0.18, 'Z2': 0.18,
        'zone_3': 0.24, 'zone_III': 0.24, 'Z3': 0.24,
        'zone_4': 0.36, 'zone_IV': 0.36, 'Z4': 0.36
    }

    if 'zone' in df_out.columns:
        df_out['seismic_zone_coeff'] = df_out['zone'].map(zone_mapping).fillna(0.24)

    # Response modification factor (R)
    if 'framework' in df_out.columns:
        r_mapping = {
            'nonsway': 1.5, 'omrf': 3.0, 'imrf': 4.0, 'smrf': 5.0
        }
        df_out['response_mod_factor'] = df_out['framework'].map(r_mapping).fillna(3.0)

    # Importance factor (default 1.0)
    if 'importance_factor' not in df_out.columns:
        df_out['importance_factor'] = 1.0

    # Column area (from section dimensions)
    if 'column_width' in df_out.columns and 'column_depth' in df_out.columns:
        df_out['column_area'] = df_out['column_width'] * df_out['column_depth']

    # Reinforcement ratio (placeholder - would be from actual design)
    if 'reinforcement_ratio' not in df_out.columns:
        # Default based on framework
        if 'framework' in df_out.columns:
            rho_map = {'nonsway': 0.01, 'omrf': 0.015, 'imrf': 0.02, 'smrf': 0.025}
            df_out['reinforcement_ratio'] = df_out['framework'].map(rho_map).fillna(0.015)

    return df_out


def validate_dataset(df: pd.DataFrame, min_pidr: float = 0.001,
                     max_pidr: float = 0.20) -> Dict[str, Any]:
    """
    Validate dataset quality

    Args:
        df: Dataset to validate
        min_pidr: Minimum acceptable PIDR
        max_pidr: Maximum acceptable PIDR

    Returns:
        Validation report dictionary
    """
    report = {
        'total_records': len(df),
        'valid_records': 0,
        'issues': [],
        'statistics': {}
    }

    # Check for required columns
    required_cols = ['pidr', 'intensity', 'framework']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        report['issues'].append(f"Missing columns: {missing}")
        return report

    # Check PIDR range
    pidr_range = df['pidr'].describe()
    report['statistics']['pidr'] = {
        'min': float(pidr_range['min']),
        'max': float(pidr_range['max']),
        'mean': float(pidr_range['mean']),
        'median': float(pidr_range['50%'])
    }

    if pidr_range['min'] < min_pidr:
        report['issues'].append(f"PIDR below minimum: {pidr_range['min']:.4f}")

    if pidr_range['max'] > max_pidr:
        report['issues'].append(f"PIDR above maximum: {pidr_range['max']:.4f}")

    # Check for NaN values
    nan_counts = df.isna().sum()
    if nan_counts.any():
        report['issues'].append(f"NaN values found: {nan_counts[nan_counts > 0].to_dict()}")

    # Check framework distribution
    if 'framework' in df.columns:
        fw_dist = df['framework'].value_counts()
        report['statistics']['framework_distribution'] = fw_dist.to_dict()

    # Check intensity coverage
    if 'intensity' in df.columns:
        intensity_range = df['intensity'].describe()
        report['statistics']['intensity'] = {
            'min': float(intensity_range['min']),
            'max': float(intensity_range['max']),
            'mean': float(intensity_range['mean'])
        }

    # Check for data balance
    if 'intensity' in df.columns and 'framework' in df.columns:
        # Count intensity levels per framework
        intensity_counts = df.groupby('framework')['intensity'].nunique()
        report['statistics']['intensity_coverage'] = intensity_counts.to_dict()

    report['valid_records'] = len(df) - len(report['issues'])

    return report


def split_dataset(df: pd.DataFrame, test_ratio: float = 0.20,
                  stratify_column: str = 'framework',
                  random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split dataset into train and test sets

    Args:
        df: Dataset to split
        test_ratio: Test set ratio
        stratify_column: Column for stratification
        random_state: Random seed

    Returns:
        (train_df, test_df)
    """
    # Check if stratification is possible
    if stratify_column not in df.columns:
        logger.warning(f"Stratification column '{stratify_column}' not found")
        stratify_column = None

    # Split
    train_df, test_df = train_test_split(
        df,
        test_size=test_ratio,
        random_state=random_state,
        stratify=df[stratify_column] if stratify_column else None
    )

    logger.info(f"Train: {len(train_df)} records, Test: {len(test_df)} records")

    return train_df, test_df


def save_dataset(df: pd.DataFrame, filepath: str,
                 format: str = 'csv') -> None:
    """
    Save dataset to file

    Args:
        df: Dataset to save
        filepath: Output file path
        format: Output format ('csv', 'hdf', 'parquet')
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'hdf':
        df.to_hdf(filepath, key='data', mode='w')
    elif format == 'parquet':
        df.to_parquet(filepath, index=False)

    logger.info(f"Dataset saved to {filepath}")


def create_ml_dataset(raw_df: pd.DataFrame,
                     feature_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Create ML-ready dataset from raw IDA results

    Args:
        raw_df: Raw IDA results
        feature_columns: List of feature columns (auto-detect if None)

    Returns:
        ML-ready DataFrame with features and target
    """
    # Engineer features
    df = engineer_features(raw_df)

    # Define feature columns
    if feature_columns is None:
        feature_columns = [
            'n_stories', 'total_height', 'fundamental_period',
            'column_area', 'reinforcement_ratio',
            'seismic_zone_coeff', 'response_mod_factor', 'importance_factor',
            'ln_sa'
        ]
        feature_columns = [col for col in feature_columns if col in df.columns]

    # Target
    target_col = 'ln_pidr'

    # Create final dataset
    X = df[feature_columns].copy()
    y = df[target_col].copy()

    # Combine
    df_ml = pd.concat([X, y], axis=1)

    return df_ml


# Default feature set for BNBC 2020 analysis
DEFAULT_FEATURES = [
    'n_stories',
    'total_height',
    'fundamental_period',
    'column_width',
    'column_depth',
    'beam_width',
    'beam_depth',
    'concrete_strength',
    'steel_yield',
    'reinforcement_ratio',
    'seismic_zone_coeff',
    'response_mod_factor',
    'importance_factor',
    'site_class',
    'ln_sa'
]

DEFAULT_TARGET = 'ln_pidr'


__all__ = [
    'FeatureEngineer',
    'compile_dataset',
    'engineer_features',
    'validate_dataset',
    'split_dataset',
    'save_dataset',
    'create_ml_dataset',
    'DEFAULT_FEATURES',
    'DEFAULT_TARGET'
]
