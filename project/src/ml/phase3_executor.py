"""
Phase 3 ML Executor

Complete ML pipeline orchestrator:
1. Load Phase 2 IDA results
2. Engineer features
3. Train all models
4. Evaluate and compare
5. Generate SHAP analysis
6. Save results and models

This is the entry point for Phase 3: ML Training Pipeline
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from typing import Dict, Tuple, Optional

from src.ml.feature_engineering import FeatureEngineer, prepare_training_data
from src.ml.ml_pipeline import MLTrainer
from src.utils.logger import ProjectLogger

logger = logging.getLogger(__name__)


class Phase3Config:
    """Configuration for Phase 3 ML training"""
    
    def __init__(
        self,
        phase2_results_file: str = "results/phase2_ida_results.csv",
        output_dir: str = "results/phase3_ml",
        test_size: float = 0.2,
        validation_size: float = 0.15,
        train_all_models: bool = True,
        use_hyperparameter_tuning: bool = False,
        random_seed: int = 42
    ):
        self.phase2_results_file = phase2_results_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_size = test_size
        self.validation_size = validation_size
        self.train_all_models = train_all_models
        self.use_hyperparameter_tuning = use_hyperparameter_tuning
        self.random_seed = random_seed
        
        np.random.seed(random_seed)


class Phase3Executor:
    """
    Execute complete Phase 3 ML training pipeline
    
    Workflow:
    1. load_phase2_results() → Load IDA data
    2. engineer_features() → Extract ML features
    3. prepare_training_data() → Split into train/val/test
    4. train_models() → Train all model types
    5. evaluate_models() → Test set evaluation
    6. analyze_results() → SHAP, feature importance, plots
    7. save_results() → Export all outputs
    """
    
    def __init__(self, config: Phase3Config):
        """Initialize Phase 3 executor with configuration"""
        self.config = config
        self.logger = ProjectLogger(__name__)
        
        # Pipeline state
        self.ida_data = None
        self.engineered_data = None
        self.train_test_split = None
        self.feature_engineer = None
        self.trainer = None
        self.results = {}
    
    def load_phase2_results(self) -> pd.DataFrame:
        """
        Load Phase 2 IDA results (output from Phase2Executor)
        
        Expected columns:
        - building_id, story_count, framework_type, seismic_zone
        - gm_record_id, magnitude, distance_km
        - intensity_sa_g, pgv_cm_s, pga_g
        - pidr, max_floor_accel_g, residual_drift
        - damage_state (IO/LS/CP)
        
        Returns:
            Phase 2 IDA results DataFrame
        """
        self.logger.info(f"Loading Phase 2 results from {self.config.phase2_results_file}")
        
        if not Path(self.config.phase2_results_file).exists():
            self.logger.error(f"File not found: {self.config.phase2_results_file}")
            raise FileNotFoundError(f"Phase 2 results file not found")
        
        self.ida_data = pd.read_csv(self.config.phase2_results_file)
        
        self.logger.info(f"Loaded {len(self.ida_data)} IDA records")
        self.logger.info(f"Columns: {self.ida_data.columns.tolist()}")
        self.logger.info(f"Shape: {self.ida_data.shape}")
        
        return self.ida_data
    
    def engineer_features(self) -> pd.DataFrame:
        """
        Extract ML features from Phase 2 IDA results
        
        Feature categories:
        1. Building features (n_stories, framework_type, zone)
        2. Seismic features (magnitude, distance)
        3. Intensity features (Sa, PGV, PGA)
        4. Derived features (computed from above)
        5. Interaction features (zone × framework interactions)
        
        Returns:
            Engineered features DataFrame
        """
        self.logger.info("Engineering ML features...")
        
        if self.ida_data is None:
            self.load_phase2_results()
        
        self.feature_engineer = FeatureEngineer()
        self.engineered_data = self.feature_engineer.engineer_features(self.ida_data)
        
        self.logger.info(f"Generated {self.engineered_data.shape[1]} features")
        self.logger.info(f"Features:\n{self.engineered_data.columns.tolist()}")
        
        return self.engineered_data
    
    def prepare_training_data(self) -> Dict:
        """
        Prepare training/validation/test split with scaling
        
        Split strategy:
        - Test set: {test_size}% (20% default)
        - Validation set: {validation_size}% of training (15% default)
        - Training set: remaining (~65%)
        
        Scaling: StandardScaler (fit on train, apply to val/test)
        
        Returns:
            Dictionary with keys:
            - 'X_train', 'y_train'
            - 'X_val', 'y_val'
            - 'X_test', 'y_test'
            - 'scaler': FeatureEngineer with fitted scaler
            - 'feature_names': List of feature names
        """
        self.logger.info("Preparing training/validation/test data...")
        
        if self.engineered_data is None:
            self.engineer_features()
        
        # Use prepare_training_data from feature engineering
        train_test_split, feature_engineer = prepare_training_data(
            self.engineered_data,
            test_size=self.config.test_size,
            validation_size=self.config.validation_size,
            random_seed=self.config.random_seed
        )
        
        self.train_test_split = train_test_split
        self.feature_engineer = feature_engineer
        
        self.logger.info(f"Train set: {train_test_split['X_train'].shape[0]} samples")
        self.logger.info(f"Val set:   {train_test_split['X_val'].shape[0]} samples")
        self.logger.info(f"Test set:  {train_test_split['X_test'].shape[0]} samples")
        
        return train_test_split
    
    def train_models(self) -> pd.DataFrame:
        """
        Train all ML models
        
        Models trained:
        1. Linear Regression (baseline, interpretable)
        2. Random Forest (multi-tree, feature importance)
        3. XGBoost (gradient boosting, high performance)
        4. Neural Network (deep learning, if TensorFlow available)
        
        Returns:
            Model comparison DataFrame with train/val metrics
        """
        self.logger.info("Training ML models...")
        
        if self.train_test_split is None:
            self.prepare_training_data()
        
        X_train = self.train_test_split['X_train']
        y_train = self.train_test_split['y_train']
        X_val = self.train_test_split['X_val']
        y_val = self.train_test_split['y_val']
        
        self.trainer = MLTrainer(output_dir=str(self.config.output_dir / "models"))
        
        results_df = self.trainer.train_all_models(
            X_train, y_train,
            X_val, y_val
        )
        
        self.results['model_comparison'] = results_df
        
        return results_df
    
    def evaluate_models(self) -> pd.DataFrame:
        """
        Evaluate all trained models on test set
        
        Returns:
            Test evaluation metrics for all models
        """
        self.logger.info("Evaluating models on test set...")
        
        if self.trainer is None:
            self.train_models()
        
        X_test = self.train_test_split['X_test']
        y_test = self.train_test_split['y_test']
        
        test_results = self.trainer.evaluate_on_test_set(X_test, y_test)
        self.results['test_results'] = test_results
        
        return test_results
    
    def analyze_feature_importance(self) -> Dict:
        """
        Analyze feature importance from tree-based models
        
        Tree models analyzed:
        - Random Forest
        - XGBoost
        
        Returns:
            Dictionary with feature importance DataFrames
        """
        self.logger.info("Analyzing feature importance...")
        
        if self.trainer is None:
            self.train_models()
        
        feature_names = self.train_test_split.get('feature_names', None)
        importances = self.trainer.get_feature_importance(feature_names)
        self.results['feature_importance'] = importances
        
        for model_name, imp_df in importances.items():
            self.logger.info(f"\n{model_name} Top 10 Features:")
            self.logger.info(imp_df.head(10).to_string())
        
        return importances
    
    def generate_shap_analysis(self):
        """
        Generate SHAP analysis for model interpretability
        
        Requires shap package: pip install shap
        Creates:
        - SHAP summary plots
        - SHAP force plots
        - Feature interaction analysis
        
        Note: Has optional dependency on SHAP
        """
        try:
            import shap
        except ImportError:
            self.logger.warning("SHAP not installed, skipping SHAP analysis. "
                              "Install with: pip install shap")
            return
        
        self.logger.info("Generating SHAP analysis...")
        
        X_test = self.train_test_split['X_test']
        
        # For tree-based models
        for model_name in ['RandomForest', 'XGBoost']:
            if model_name not in self.trainer.models:
                continue
            
            model = self.trainer.models[model_name]
            self.logger.info(f"Computing SHAP values for {model_name}...")
            
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X_test)
                
                # Store for later visualization
                self.results[f'shap_{model_name}'] = {
                    'explainer': explainer,
                    'shap_values': shap_values
                }
                
                self.logger.info(f"  ✓ SHAP analysis complete for {model_name}")
            except Exception as e:
                self.logger.warning(f"  ✗ SHAP analysis failed for {model_name}: {e}")
    
    def save_results(self) -> None:
        """Save all Phase 3 results to output directory"""
        self.logger.info("Saving Phase 3 results...")
        output_dir = self.config.output_dir
        
        # Save model comparison
        if 'model_comparison' in self.results:
            csv_path = output_dir / "model_comparison.csv"
            self.results['model_comparison'].to_csv(csv_path, index=False)
            self.logger.info(f"  ✓ Model comparison → {csv_path.relative_to('.')}")
        
        # Save test results
        if 'test_results' in self.results:
            csv_path = output_dir / "test_results.csv"
            self.results['test_results'].to_csv(csv_path, index=False)
            self.logger.info(f"  ✓ Test results → {csv_path.relative_to('.')}")
        
        # Save feature importance
        if 'feature_importance' in self.results:
            for model_name, imp_df in self.results['feature_importance'].items():
                csv_path = output_dir / f"feature_importance_{model_name}.csv"
                imp_df.to_csv(csv_path, index=False)
                self.logger.info(f"  ✓ {model_name} importance → {csv_path.relative_to('.')}")
        
        # Save trained models
        if self.trainer:
            self.trainer.save_models()
            self.logger.info(f"  ✓ Models saved to {self.trainer.output_dir.relative_to('.')}")
        
        # Save configuration summary
        summary = {
            'phase': 3,
            'model_types': list(self.trainer.models.keys()) if self.trainer else [],
            'best_model': self.trainer.best_model_name if self.trainer else None,
            'n_features': self.engineered_data.shape[1] if self.engineered_data is not None else 0,
            'n_train': len(self.train_test_split['X_train']) if self.train_test_split else 0,
            'n_val': len(self.train_test_split['X_val']) if self.train_test_split else 0,
            'n_test': len(self.train_test_split['X_test']) if self.train_test_split else 0,
        }
        
        json_path = output_dir / "phase3_summary.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"  ✓ Summary → {json_path.relative_to('.')}")
    
    def run_full_pipeline(self) -> None:
        """
        Execute complete Phase 3 pipeline
        
        Sequential steps:
        1. Load Phase 2 IDA results
        2. Engineer features
        3. Prepare training data
        4. Train all models
        5. Evaluate on test set
        6. Analyze feature importance
        7. Generate SHAP analysis
        8. Save all results
        """
        self.logger.info("="*70)
        self.logger.info("PHASE 3: ML TRAINING PIPELINE")
        self.logger.info("="*70)
        
        try:
            self.load_phase2_results()
            self.engineer_features()
            self.prepare_training_data()
            self.train_models()
            self.evaluate_models()
            self.analyze_feature_importance()
            self.generate_shap_analysis()
            self.save_results()
            
            self.logger.info("="*70)
            self.logger.info("PHASE 3 COMPLETE")
            self.logger.info(f"Best Model: {self.trainer.best_model_name}")
            self.logger.info(f"Results saved to: {self.config.output_dir.relative_to('.')}")
            self.logger.info("="*70)
        
        except Exception as e:
            self.logger.error(f"Phase 3 failed: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    # Example usage
    config = Phase3Config(
        phase2_results_file="results/phase2_ida_results.csv",
        output_dir="results/phase3_ml",
    )
    
    executor = Phase3Executor(config)
    executor.run_full_pipeline()
