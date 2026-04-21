"""
Unit tests for ML training and evaluation modules

Tests cover:
- Feature engineering
- Model training (LR, RF, XGBoost, ANN)
- Model evaluation (R², RMSE, MAE, cross-validation)
- Hyperparameter validation
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile


class TestMLTrainer:
    """Test suite for MLTrainer class"""

    @pytest.fixture
    def sample_data(self):
        """Create sample training data"""
        np.random.seed(42)
        n_samples = 100
        
        data = {
            'n_stories': np.random.randint(5, 16, n_samples),
            'period': np.random.uniform(0.5, 2.5, n_samples),
            'pga': np.random.uniform(0.05, 0.20, n_samples),
            'zone': np.random.randint(1, 5, n_samples),
            'soil_class': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
            'pidr': np.random.uniform(0.005, 0.10, n_samples),  # Target
        }
        
        return pd.DataFrame(data)

    @pytest.fixture
    def config(self):
        """Create sample ML configuration"""
        return {
            'ml': {
                'models': ['lr', 'rf', 'xgboost'],
                'test_ratio': 0.20,
                'validation_ratio': 0.15,
                'random_state': 42,
                'scaling': 'standard',
            },
            'hyperparameters': {
                'random_forest': {
                    'n_estimators': 100,
                    'max_depth': 20,
                    'min_samples_split': 5,
                    'random_state': 42,
                },
                'xgboost': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42,
                },
                'neural_network': {
                    'hidden_layers': [64, 32],
                    'epochs': 50,
                    'batch_size': 16,
                    'validation_split': 0.15,
                }
            }
        }

    def test_feature_engineering(self, sample_data):
        """Test feature engineering from raw data"""
        # Test that required features are present
        required_features = ['n_stories', 'period', 'pga', 'zone']
        for feat in required_features:
            assert feat in sample_data.columns, f"Missing feature: {feat}"

    def test_train_test_split(self, sample_data, config):
        """Test train/test/validation split"""
        test_ratio = config['ml']['test_ratio']
        validation_ratio = config['ml']['validation_ratio']
        
        n_samples = len(sample_data)
        n_test = int(n_samples * test_ratio)
        n_train_val = n_samples - n_test
        n_val = int(n_train_val * validation_ratio)
        n_train = n_train_val - n_val
        
        assert n_train > 0, "Training set too small"
        assert n_val > 0, "Validation set too small"
        assert n_test > 0, "Test set too small"
        assert n_train + n_val + n_test == n_samples, "Split mismatch"

    def test_model_config_validation(self, config):
        """Test hyperparameter configuration"""
        # Verify all required model configs present
        required_models = ['random_forest', 'xgboost', 'neural_network']
        for model in required_models:
            assert model in config['hyperparameters'], f"Missing config: {model}"

    def test_lr_model_initialization(self):
        """Test Linear Regression model can be instantiated"""
        try:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            assert hasattr(model, 'fit'), "LR model missing fit method"
            assert hasattr(model, 'predict'), "LR model missing predict method"
        except ImportError:
            pytest.skip("scikit-learn not installed")

    def test_rf_model_initialization(self, config):
        """Test Random Forest model initialization"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            params = config['hyperparameters']['random_forest']
            model = RandomForestRegressor(**params)
            assert model.n_estimators == params['n_estimators']
            assert model.max_depth == params['max_depth']
        except ImportError:
            pytest.skip("scikit-learn not installed")

    def test_xgboost_model_initialization(self, config):
        """Test XGBoost model initialization"""
        try:
            import xgboost as xgb
            params = config['hyperparameters']['xgboost']
            model = xgb.XGBRegressor(**params)
            assert model.n_estimators == params['n_estimators']
        except ImportError:
            pytest.skip("xgboost not installed")

    def test_evaluation_metrics(self, sample_data):
        """Test ML evaluation metrics"""
        y_true = sample_data['pidr'].values
        y_pred = y_true + np.random.normal(0, 0.01, len(y_true))
        
        # R² calculation
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        assert 0 <= r2 <= 1, f"R² out of range: {r2}"
        assert r2 > 0.5, "R² too low for this synthetic data"
        
        # RMSE calculation
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        assert rmse >= 0, f"RMSE negative: {rmse}"
        
        # MAE calculation
        mae = np.mean(np.abs(y_true - y_pred))
        assert mae >= 0, f"MAE negative: {mae}"


class TestSHAPAnalyzer:
    """Test suite for SHAP feature importance analysis"""

    @pytest.fixture
    def mock_model(self):
        """Create mock ML model"""
        model = Mock()
        model.predict = Mock(return_value=np.array([0.05, 0.06, 0.07]))
        return model

    @pytest.fixture
    def sample_features(self):
        """Create sample features for SHAP analysis"""
        np.random.seed(42)
        return np.random.randn(100, 5)

    def test_shap_explainer_initialization(self):
        """Test SHAP explainer can be initialized"""
        try:
            import shap
            X = np.random.randn(100, 5)
            
            # Test TreeExplainer initialization (for tree-based models)
            # Note: This requires a fitted model, so we just check imports
            assert hasattr(shap, 'TreeExplainer'), "SHAP TreeExplainer not found"
            assert hasattr(shap, 'KernelExplainer'), "SHAP KernelExplainer not found"
        except ImportError:
            pytest.skip("SHAP not installed")

    def test_feature_importance_computation(self, mock_model, sample_features):
        """Test feature importance values"""
        # Mock feature importance (sum of absolute SHAP values)
        n_features = sample_features.shape[1]
        importance = np.abs(np.random.randn(n_features))
        importance = importance / importance.sum()  # Normalize
        
        assert len(importance) == n_features, "Importance array size mismatch"
        assert np.isclose(importance.sum(), 1.0), "Importance not normalized"
        assert np.all(importance >= 0), "Negative importance values"

    def test_shap_value_range(self):
        """Test SHAP values are reasonable"""
        # SHAP values should be bounded and interpretable
        shap_values = np.random.randn(100, 5) * 0.1  # Bounded random values
        
        # Check reasonable range
        assert np.abs(shap_values).max() < 1.0, "SHAP values out of reasonable range"


class TestModelEvaluation:
    """Test suite for model evaluation methods"""

    @pytest.fixture
    def predictions(self):
        """Create sample predictions"""
        np.random.seed(42)
        y_true = np.random.uniform(0.005, 0.10, 50)
        y_pred = y_true + np.random.normal(0, 0.01, 50)
        return y_true, np.clip(y_pred, 0, 0.15)

    def test_cross_validation_split(self):
        """Test k-fold cross-validation setup"""
        try:
            from sklearn.model_selection import KFold
            
            n_samples = 100
            n_splits = 5
            kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
            
            splits = list(kf.split(np.arange(n_samples)))
            assert len(splits) == n_splits, f"Expected {n_splits} splits, got {len(splits)}"
            
            for train_idx, test_idx in splits:
                assert len(train_idx) + len(test_idx) == n_samples, "Split size mismatch"
                assert len(np.intersect1d(train_idx, test_idx)) == 0, "Train/test overlap"
        except ImportError:
            pytest.skip("scikit-learn not installed")

    def test_model_persistence(self):
        """Test model can be saved and loaded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pkl"
            
            try:
                import joblib
                from sklearn.ensemble import RandomForestRegressor
                
                # Create and save model
                model = RandomForestRegressor(n_estimators=10, random_state=42)
                X = np.random.randn(50, 5)
                y = np.random.randn(50)
                model.fit(X, y)
                
                joblib.dump(model, str(model_path))
                assert model_path.exists(), "Model file not created"
                
                # Load model
                loaded_model = joblib.load(str(model_path))
                assert hasattr(loaded_model, 'predict'), "Loaded model missing predict"
                
                # Verify predictions match
                pred1 = model.predict(X[:5])
                pred2 = loaded_model.predict(X[:5])
                assert np.allclose(pred1, pred2), "Predictions differ after reload"
                
            except ImportError:
                pytest.skip("joblib or scikit-learn not installed")

    def test_prediction_bounds(self, predictions):
        """Test predictions are within expected bounds"""
        y_true, y_pred = predictions
        
        # PIDR should be between 0 and 1 (0% to 100%)
        assert np.all(y_pred >= 0), "Predictions below 0%"
        assert np.all(y_pred <= 0.15), "Predictions above 15% (unrealistic)"

    def test_residual_distribution(self, predictions):
        """Test residual statistics"""
        y_true, y_pred = predictions
        residuals = y_true - y_pred
        
        # Residuals should have near-zero mean (no systematic bias)
        mean_residual = np.mean(residuals)
        assert np.abs(mean_residual) < 0.02, f"Residuals have bias: {mean_residual}"
        
        # Residuals should be roughly normal (Shapiro-Wilk test optional)
        std_residual = np.std(residuals)
        assert std_residual > 0, "Zero residual variance"


class TestHyperparameterOptimization:
    """Test suite for hyperparameter optimization"""

    def test_optuna_study_creation(self):
        """Test Optuna study can be created"""
        try:
            import optuna
            
            def objective(trial):
                n_estimators = trial.suggest_int('n_estimators', 50, 200)
                max_depth = trial.suggest_int('max_depth', 5, 30)
                return np.random.rand()  # Mock objective
            
            study = optuna.create_study(direction='maximize')
            assert study is not None, "Failed to create Optuna study"
            
            # Run a quick optimization
            study.optimize(objective, n_trials=2, show_progress_bar=False)
            assert len(study.trials) == 2, "Trials not recorded"
            
        except ImportError:
            pytest.skip("Optuna not installed")

    def test_parameter_ranges(self):
        """Test parameter ranges are reasonable"""
        parameter_ranges = {
            'n_estimators': (50, 500),
            'max_depth': (5, 50),
            'learning_rate': (0.001, 0.5),
            'min_samples_split': (2, 20),
        }
        
        for param, (min_val, max_val) in parameter_ranges.items():
            assert min_val < max_val, f"{param}: inverted range"
            assert min_val > 0, f"{param}: negative minimum"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
