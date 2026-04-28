"""
Phase 3: ML Model Trainer

Trains and evaluates multiple ML models for drift prediction:
- Linear Regression (baseline)
- Random Forest
- XGBoost
- Neural Networks (TensorFlow)

Includes model selection, hyperparameter optimization, and evaluation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
import logging
import joblib
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score, GridSearchCV
import xgboost as xgb

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


class MLTrainer:
    """
    Train and evaluate multiple ML models for PIDR prediction.
    
    Models:
    - LinearRegression: Baseline for interpretability
    - RandomForest: Non-linear, good for feature importance
    - XGBoost: High performance gradient boosting
    - NeuralNetwork: Deep learning (if TensorFlow available)
    """
    
    def __init__(self, output_dir: str = "models/ml_models"):
        """
        Initialize ML trainer.
        
        Args:
            output_dir: Directory to save trained models
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.histories = {}  # For NN training history
        self.best_model = None
        self.best_model_name = None
    
    def train_linear_regression(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None
    ) -> Dict:
        """
        Train linear regression baseline model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
        
        Returns:
            Model evaluation metrics dictionary
        """
        logger.info("Training Linear Regression...")
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        metrics = {
            'model_type': 'LinearRegression',
            'train_r2': r2_score(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
        }
        
        if X_val is not None and y_val is not None:
            y_pred_val = model.predict(X_val)
            metrics['val_r2'] = r2_score(y_val, y_pred_val)
            metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_pred_val))
            metrics['val_mae'] = mean_absolute_error(y_val, y_pred_val)
        
        self.models['LinearRegression'] = model
        
        logger.info(f"  Train R²: {metrics['train_r2']:.4f}")
        if 'val_r2' in metrics:
            logger.info(f"  Val R²: {metrics['val_r2']:.4f}")
        
        return metrics
    
    def train_random_forest(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        n_estimators: int = 100,
        max_depth: int = 20,
        hyperparameter_tune: bool = False
    ) -> Dict:
        """
        Train Random Forest model.
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            n_estimators: Number of trees
            max_depth: Max tree depth
            hyperparameter_tune: Perform grid search
        
        Returns:
            Model metrics dictionary
        """
        logger.info("Training Random Forest...")
        
        if hyperparameter_tune:
            logger.info("  Performing hyperparameter tuning...")
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5, 10],
            }
            rf = GridSearchCV(
                RandomForestRegressor(random_state=42),
                param_grid,
                cv=5,
                n_jobs=-1
            )
            rf.fit(X_train, y_train)
            model = rf.best_estimator_
            logger.info(f"  Best params: {rf.best_params_}")
        else:
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        metrics = {
            'model_type': 'RandomForest',
            'train_r2': r2_score(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
        }
        
        if X_val is not None and y_val is not None:
            y_pred_val = model.predict(X_val)
            metrics['val_r2'] = r2_score(y_val, y_pred_val)
            metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_pred_val))
            metrics['val_mae'] = mean_absolute_error(y_val, y_pred_val)
        
        self.models['RandomForest'] = model
        
        logger.info(f"  Train R²: {metrics['train_r2']:.4f}")
        if 'val_r2' in metrics:
            logger.info(f"  Val R²: {metrics['val_r2']:.4f}")
        
        return metrics
    
    def train_xgboost(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 6
    ) -> Dict:
        """
        Train XGBoost model.
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            n_estimators: Number of boosting rounds
            learning_rate: Shrinkage parameter
            max_depth: Max tree depth
        
        Returns:
            Model metrics dictionary
        """
        logger.info("Training XGBoost...")
        
        eval_set = None
        if X_val is not None and y_val is not None:
            eval_set = [(X_val, y_val)]
        
        model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            objective='reg:squarederror',
            random_state=42,
            early_stopping_rounds=10 if eval_set else None,
        )
        model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False
        )
        
        y_pred_train = model.predict(X_train)
        metrics = {
            'model_type': 'XGBoost',
            'train_r2': r2_score(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
        }
        
        if X_val is not None and y_val is not None:
            y_pred_val = model.predict(X_val)
            metrics['val_r2'] = r2_score(y_val, y_pred_val)
            metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_pred_val))
            metrics['val_mae'] = mean_absolute_error(y_val, y_pred_val)
        
        self.models['XGBoost'] = model
        
        logger.info(f"  Train R²: {metrics['train_r2']:.4f}")
        if 'val_r2' in metrics:
            logger.info(f"  Val R²: {metrics['val_r2']:.4f}")
        
        return metrics
    
    def train_neural_network(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None,
        hidden_layers: Tuple[int] = (128, 64, 32),
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict:
        """
        Train Neural Network with TensorFlow/Keras.
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            hidden_layers: Neurons per layer
            epochs: Training epochs
            batch_size: Batch size
        
        Returns:
            Model metrics dictionary
        """
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, skipping Neural Network")
            return {}
        
        logger.info("Training Neural Network...")
        
        n_features = X_train.shape[1]
        
        # Build model
        model = keras.Sequential([
            layers.Dense(hidden_layers[0], activation='relu', input_shape=(n_features,)),
            layers.Dropout(0.2),
            layers.Dense(hidden_layers[1], activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(hidden_layers[2], activation='relu'),
            layers.Dense(1)  # Output layer
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        # Validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        # Train
        history = model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )
        
        y_pred_train = model.predict(X_train, verbose=0).flatten()
        metrics = {
            'model_type': 'NeuralNetwork',
            'train_r2': r2_score(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
        }
        
        if X_val is not None and y_val is not None:
            y_pred_val = model.predict(X_val, verbose=0).flatten()
            metrics['val_r2'] = r2_score(y_val, y_pred_val)
            metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_pred_val))
            metrics['val_mae'] = mean_absolute_error(y_val, y_pred_val)
        
        self.models['NeuralNetwork'] = model
        self.histories['NeuralNetwork'] = history
        
        logger.info(f"  Train R²: {metrics['train_r2']:.4f}")
        if 'val_r2' in metrics:
            logger.info(f"  Val R²: {metrics['val_r2']:.4f}")
        
        return metrics
    
    def train_all_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray = None,
        y_val: np.ndarray = None
    ) -> pd.DataFrame:
        """
        Train all available models and return comparison table.
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
        
        Returns:
            DataFrame with metrics for all models
        """
        logger.info("="*70)
        logger.info("TRAINING ALL MODELS")
        logger.info("="*70)
        
        results = []
        
        # Train each model
        results.append(self.train_linear_regression(X_train, y_train, X_val, y_val))
        results.append(self.train_random_forest(X_train, y_train, X_val, y_val))
        results.append(self.train_xgboost(X_train, y_train, X_val, y_val))
        results.append(self.train_neural_network(X_train, y_train, X_val, y_val))
        
        results_df = pd.DataFrame(results)
        
        # Find best model by validation R²
        if 'val_r2' in results_df.columns:
            best_idx = results_df['val_r2'].idxmax()
        else:
            best_idx = results_df['train_r2'].idxmax()
        
        self.best_model_name = results_df.loc[best_idx, 'model_type']
        self.best_model = self.models[self.best_model_name]
        
        logger.info("\n" + "="*70)
        logger.info("MODEL COMPARISON")
        logger.info("="*70)
        logger.info(results_df.to_string())
        logger.info(f"\nBest Model: {self.best_model_name}")
        logger.info("="*70)
        
        return results_df
    
    def evaluate_on_test_set(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> pd.DataFrame:
        """
        Evaluate all models on test set.
        
        Args:
            X_test: Test features
            y_test: Test targets
        
        Returns:
            Test evaluation metrics
        """
        logger.info("Evaluating models on test set...")
        
        results = []
        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            if isinstance(y_pred, pd.DataFrame):
                y_pred = y_pred.values.flatten()
            
            results.append({
                'model': name,
                'test_r2': r2_score(y_test, y_pred),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'test_mae': mean_absolute_error(y_test, y_pred),
            })
        
        test_df = pd.DataFrame(results)
        
        logger.info("\nTest Set Results:")
        logger.info(test_df.to_string())
        
        return test_df
    
    def save_models(self) -> None:
        """Save all trained models to disk"""
        logger.info(f"Saving models to {self.output_dir}...")
        
        for name, model in self.models.items():
            try:
                if name == 'NeuralNetwork' and TENSORFLOW_AVAILABLE:
                    model.save(self.output_dir / f"{name.lower()}.h5")
                else:
                    joblib.dump(model, self.output_dir / f"{name.lower()}.pkl")
                logger.info(f"  ✓ {name} saved")
            except Exception as e:
                logger.warning(f"  ✗ Failed to save {name}: {e}")
    
    def get_feature_importance(self, feature_names: List[str] = None) -> Dict:
        """
        Get feature importance from tree-based models.
        
        Args:
            feature_names: Feature names for labeling
        
        Returns:
            Dictionary with importances per model
        """
        importances = {}
        
        if 'RandomForest' in self.models:
            rf = self.models['RandomForest']
            importances['RandomForest'] = pd.DataFrame({
                'feature': feature_names or range(len(rf.feature_importances_)),
                'importance': rf.feature_importances_
            }).sort_values('importance', ascending=False)
        
        if 'XGBoost' in self.models:
            xgb_model = self.models['XGBoost']
            importances['XGBoost'] = pd.DataFrame({
                'feature': feature_names or range(len(xgb_model.feature_importances_)),
                'importance': xgb_model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        return importances
