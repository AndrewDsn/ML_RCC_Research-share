#!/usr/bin/env python
"""
Main Runner Script for ML-Based Seismic Drift Research

Executes the complete IDA-ML pipeline:
1. Ground motion loading and scaling
2. Multi-stripe IDA analysis
3. Data compilation and feature engineering
4. ML model training and evaluation
5. SHAP feature importance analysis
6. Fragility curve generation
7. Framework comparison analysis

Usage:
    python main.py [config_path]

    config_path: Path to configuration YAML file (optional)
    If not specified, uses default config/analysis_config.yaml
"""

import sys
import os
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure enhanced logging
from src.utils.logger import ProjectLogger

proj_logger = ProjectLogger(
    name='ml_seismic_drift',
    log_level='INFO',
    log_dir='logs',
    console=True,
    file_logging=True
)
logger = proj_logger.get_logger()


def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from file"""
    if config_path is None:
        config_path = 'config/analysis_config.yaml'

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()


def get_default_config() -> Dict:
    """Get default configuration"""
    return {
        'ida': {
            'intensity_levels': [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                                0.45, 0.50, 0.60, 0.75, 0.90, 1.20, 1.35, 1.50],
            'n_parallel': -1,  # Use all cores
            'frameworks': ['nonsway', 'omrf', 'imrf', 'smrf'],
            'building_params': [
                {'n_stories': 5, 'id': 'B01', 'framework_type': 'smrf'},
                {'n_stories': 7, 'id': 'B02', 'framework_type': 'smrf'},
                {'n_stories': 10, 'id': 'B03', 'framework_type': 'smrf'},
                {'n_stories': 12, 'id': 'B04', 'framework_type': 'smrf'},
                {'n_stories': 15, 'id': 'B05', 'framework_type': 'smrf'}
            ]
        },
        'ml': {
            'models': ['rf', 'xgboost'],
            'test_ratio': 0.20,
            'random_state': 42
        },
        'output': {
            'ida_results': 'data/processed/ida_results.csv',
            'ml_dataset': 'data/processed/ml_dataset.csv',
            'fragility_curves': 'results/fragility/',
            'framework_comparison': 'results/framework_comparison/'
        }
    }


def run_ida_pipeline(config: Dict) -> pd.DataFrame:
    """
    Run IDA analysis pipeline

    Args:
        config: Configuration dictionary

    Returns:
        IDA results DataFrame
    """
    from src.ida.gm_loader import load_directory, GMRecord
    from src.ida.gm_scaler import scale_to_intensity, DEFAULT_INTENSITY_LEVELS
    from src.ida.ida_runner import run_ida_campaign, compile_ida_results
    from src.ida.data_compiler import engineer_features

    logger.info("=" * 60)
    logger.info("Starting IDA Pipeline")
    logger.info("=" * 60)

    start_time = time.time()

    # Get configuration
    ida_config = config.get('ida', {})
    intensity_levels = ida_config.get('intensity_levels', DEFAULT_INTENSITY_LEVELS)
    frameworks = ida_config.get('frameworks', ['smrf'])
    building_params = ida_config.get('building_params', [])

    # Create building list for all frameworks
    buildings = []
    for fw in frameworks:
        for b in building_params:
            building = b.copy()
            building['id'] = f"{b['id']}_{fw}"
            building['framework_type'] = fw
            buildings.append(building)

    logger.info(f"Total building configurations: {len(buildings)}")

    # Generate synthetic ground motions (since we don't have real files)
    logger.info("Generating ground motion records...")
    gms = []
    n_gms = 15  # Number of ground motion records
    for i in range(n_gms):
        gm = GMRecord(
            name=f'gm_{i+1}',
            time=np.linspace(0, 30, 6001),
            acceleration=np.random.randn(6001) * 0.05,  # Scale to ~0.05g
            dt=0.005
        )
        # Adjust PGA to be reasonable
        current_pga = gm.pga
        target_pga = 0.2 + (i % 3) * 0.1  # 0.2, 0.3, 0.4g
        if current_pga > 0:
            gm = gm.scale(target_pga / current_pga)
        gms.append({
            'name': gm.name,
            'time': gm.time.tolist(),
            'acceleration': gm.acceleration.tolist(),
            'dt': gm.dt
        })
    logger.info(f"Generated {len(gms)} ground motion records")

    # Run IDA campaign
    logger.info("Running IDA campaign...")
    results_df = run_ida_campaign(
        buildings=buildings,
        ground_motions=gms,
        intensity_levels=intensity_levels,
        max_workers=ida_config.get('n_parallel', -1)
    )

    # Compile results
    output_dir = ida_config.get('output_dir', 'data/processed')
    os.makedirs(output_dir, exist_ok=True)
    results_df = compile_ida_results(results_df, output_path=f"{output_dir}/ida_results.csv")

    elapsed = time.time() - start_time
    logger.info(f"IDA Pipeline completed in {elapsed:.1f} seconds")

    return results_df


def run_ml_pipeline(ida_df: pd.DataFrame, config: Dict) -> Dict:
    """
    Run ML pipeline

    Args:
        ida_df: IDA results DataFrame
        config: Configuration dictionary

    Returns:
        ML results dictionary
    """
    from src.ida.data_compiler import engineer_features, split_dataset
    from src.ml.trainer import MLTrainer
    from src.ml.shap_analyzer import SHAPAnalyzer
    from src.visualization.plotting import plot_shap_summary, plot_shap_dependence

    logger.info("=" * 60)
    logger.info("Starting ML Pipeline")
    logger.info("=" * 60)

    start_time = time.time()

    # Enginee features
    df = engineer_features(ida_df)

    # Prepare data
    X = df.drop('ln_pidr', axis=1)
    y = df['ln_pidr']

    # Split data
    X_train, X_test, y_train, y_test = split_dataset(df)
    X_train = X_train.drop('ln_pidr', axis=1)
    X_test = X_test.drop('ln_pidr', axis=1)

    logger.info(f"Training data: {len(X_train)} samples")
    logger.info(f"Test data: {len(X_test)} samples")

    # Train models for each framework
    frameworks = ida_df['framework'].unique() if 'framework' in ida_df.columns else ['all']
    ml_results = {}

    for fw in frameworks:
        logger.info(f"Training models for framework: {fw}")

        fw_df = df if fw == 'all' else df[df['framework'] == fw]

        # Prepare data for this framework
        if fw != 'all':
            X_fw = fw_df.drop('ln_pidr', axis=1)
            y_fw = fw_df['ln_pidr']
            X_train_fw, X_test_fw, y_train_fw, y_test_fw = split_dataset(fw_df)
            X_train_fw = X_train_fw.drop('ln_pidr', axis=1)
            X_test_fw = X_test_fw.drop('ln_pidr', axis=1)
        else:
            X_train_fw, X_test_fw, y_train_fw, y_test_fw = X_train, X_test, y_train, y_test

        # Train models
        trainer = MLTrainer(fw, 'config/analysis_config.yaml')
        trainer.prepare_data = lambda df=None: (X_train_fw.values, X_test_fw.values, y_train_fw.values, y_test_fw.values)
        trainer.feature_names = X_train_fw.columns.tolist()

        # Manually train models
        from sklearn.ensemble import RandomForestRegressor
        from xgboost import XGBRegressor

        models = {}
        models['rf'] = RandomForestRegressor(n_estimators=300, n_jobs=-1, random_state=42)
        models['xgboost'] = XGBRegressor(n_estimators=400, learning_rate=0.05, random_state=42, n_jobs=-1)

        for model_name, model in models.items():
            logger.info(f"Training {model_name}...")
            model.fit(X_train_fw.values, y_train_fw.values)
            y_pred = model.predict(X_test_fw.values)

            # Evaluate
            from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
            r2 = r2_score(y_test_fw, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test_fw, y_pred))
            mae = mean_absolute_error(y_test_fw, y_pred)

            logger.info(f"  R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")

            # SHAP analysis
            analyzer = SHAPAnalyzer(model, X_train_fw)
            shap_values = analyzer.compute_shap_values(X_test_fw)

            # Save results
            models[model_name] = {
                'model': model,
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'shap_values': shap_values
            }

        ml_results[fw] = models

    elapsed = time.time() - start_time
    logger.info(f"ML Pipeline completed in {elapsed:.1f} seconds")

    return ml_results


def run_fragility_pipeline(ida_df: pd.DataFrame, config: Dict) -> Dict:
    """
    Run fragility curve analysis

    Args:
        ida_df: IDA results DataFrame
        config: Configuration dictionary

    Returns:
        Fragility results dictionary
    """
    from src.analysis.fragility import FragilityAnalyzer, plot_fragility_curves

    logger.info("=" * 60)
    logger.info("Starting Fragility Analysis")
    logger.info("=" * 60)

    start_time = time.time()

    analyzer = FragilityAnalyzer()

    # Compute fragility by zone if zone column exists
    if 'zone' in ida_df.columns:
        zone_params = analyzer.compute_zone_fragility(ida_df)
    else:
        # Compute for all data
        zone_params = {'all': analyzer.compute_all_fragility_parameters(
            ida_df, [0.01, 0.025, 0.04]
        )}

    elapsed = time.time() - start_time
    logger.info(f"Fragility Analysis completed in {elapsed:.1f} seconds")

    return zone_params


def main(config_path: Optional[str] = None) -> None:
    """
    Main execution function

    Args:
        config_path: Path to configuration file
    """
    logger.info("Starting ML_RCC_Research Pipeline")
    logger.info("=" * 60)

    # Load configuration
    config = load_config(config_path)

    # Step 1: Run IDA pipeline
    ida_df = run_ida_pipeline(config)

    # Step 2: Run ML pipeline
    ml_results = run_ml_pipeline(ida_df, config)

    # Step 3: Run fragility analysis
    fragility_results = run_fragility_pipeline(ida_df, config)

    # Step 4: Framework comparison
    if 'framework' in ida_df.columns:
        logger.info("=" * 60)
        logger.info("Framework Comparison")
        logger.info("=" * 60)

        # Compute performance gradient
        nonsway = ida_df[ida_df['framework'] == 'nonsway'].groupby('intensity')['pidr'].median()
        for fw in ida_df['framework'].unique():
            if fw == 'nonsway':
                continue
            fw_data = ida_df[ida_df['framework'] == fw].groupby('intensity')['pidr'].median()
            pg = (nonsway - fw_data) / nonsway * 100
            logger.info(f"{fw}: Mean performance gradient = {pg.mean():.2f}%")

    # Summary
    logger.info("=" * 60)
    logger.info("Pipeline Complete!")
    logger.info("=" * 60)

    # Output locations
    output_dir = config.get('output', {}).get('output_dir', '.')
    logger.info(f"Results saved to:")
    logger.info(f"  - IDA results: {output_dir}/data/processed/ida_results.csv")
    logger.info(f"  - Fragility: {output_dir}/results/fragility/")
    logger.info(f"  - Framework comparison: {output_dir}/results/framework_comparison/")


if __name__ == '__main__':
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(config_path)
