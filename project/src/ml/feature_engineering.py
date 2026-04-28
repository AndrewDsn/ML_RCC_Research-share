"""
Phase 3: Feature Engineering for ML Model Training

Generates and preprocesses features from Phase 2 IDA results for machine learning.

Input: ida_results_verified.csv from Phase 2
Output: Structured feature matrix ready for model training

Feature Categories:
- Building characteristics (height, framework type, zone)
- Seismic parameters (magnitude, distance, ground motion properties)
- Site characteristics (Vs30, site class)
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generates ML features from Phase 2 IDA results.
    
    Feature categories:
    1. Building features: n_stories, framework, zone
    2. Seismic features: magnitude, distance, pga
    3. GM intensity: intensity (Sa), pgv
    4. Derived features: period ratios, seismic demand indicators
    """
    
    def __init__(self):
        """Initialize feature engineer"""
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.n_features = None
        self.is_fitted = False
    
    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all features from IDA results.
        
        Args:
            data: DataFrame from Phase 2 (ida_results_verified.csv)
        
        Returns:
            DataFrame with engineered features
        """
        features = pd.DataFrame()
        
        # 1. Building features
        features['n_stories'] = self._extract_stories(data['building_id'])
        features['framework_type'] = self._extract_framework(data['building_id'])
        features['zone'] = data['zone'].astype(int)
        
        # 2. Seismic features (from GM metadata if available)
        if 'magnitude' in data.columns:
            features['magnitude'] = data['magnitude'].fillna(data['magnitude'].median())
        else:
            features['magnitude'] = self._infer_magnitude_from_gm(data['gm_id'])
        
        if 'distance_km' in data.columns:
            features['distance_km'] = data['distance_km'].fillna(data['distance_km'].median())
        else:
            features['distance_km'] = self._infer_distance_from_gm(data['gm_id'])
        
        # 3. Ground motion intensity
        features['intensity_sa_g'] = data['intensity_sa_g']
        if 'pgv_cm_s' in data.columns:
            features['pgv_cm_s'] = data['pgv_cm_s'].fillna(0)
        if 'pga_g' in data.columns:
            features['pga_g'] = data['pga_g'].fillna(0)
        
        # 4. Computed features
        features['period_ratio'] = features['intensity_sa_g'] / (features['distance_km'] + 1)
        features['magnitude_distance'] = features['magnitude'] * features['distance_km']
        features['log_distance'] = np.log10(features['distance_km'] + 1)
        
        # 5. Building-zone interaction
        features['zone_framework_id'] = features['zone'] * 100 + self._framework_to_id(features['framework_type'])
        
        self.feature_names = features.columns.tolist()
        self.n_features = len(self.feature_names)
        
        logger.info(f"Generated {self.n_features} features: {self.feature_names}")
        
        return features
    
    def _extract_stories(self, building_ids: pd.Series) -> pd.Series:
        """Extract number of stories from building ID"""
        return building_ids.str.extract(r'frame_(\d+)s', expand=False).astype(int)
    
    def _extract_framework(self, building_ids: pd.Series) -> pd.Series:
        """Extract framework type from building ID"""
        return building_ids.str.extract(r'frame_\d+s_(\w+)_z', expand=False)
    
    def _framework_to_id(self, frameworks: pd.Series) -> pd.Series:
        """Convert framework names to numeric IDs"""
        mapping = {'nonsway': 1, 'omrf': 2, 'imrf': 3, 'smrf': 4}
        return frameworks.map(mapping).fillna(1).astype(int)
    
    def _infer_magnitude_from_gm(self, gm_ids: pd.Series) -> np.ndarray:
        """Infer magnitude from GM record ID"""
        # Mapping of common GM IDs to approximate magnitudes
        gm_magnitude_map = {
            'NR': 6.7, 'LP': 6.9, 'KB': 6.9, 'CC': 7.6, 'DZ': 7.1,
            'SF': 6.6, 'KC': 7.5, 'FR': 6.5, 'UM': 5.8, 'IR': 6.9
        }
        return gm_ids.str[:2].map(gm_magnitude_map).fillna(6.8)
    
    def _infer_distance_from_gm(self, gm_ids: pd.Series) -> np.ndarray:
        """Infer distance from GM record ID"""
        # Mapping of GM IDs to approximate Rjb distances
        gm_distance_map = {
            'NR_NHS': 8.5, 'NR_SBW': 13.2, 'LP_AP2': 14.1, 'LP_GA1': 14.7,
            'KB_KJM': 1.5, 'CC_CH006': 50.5, 'DZ_LAM': 8.0, 'IR_STU': 14.6
        }
        gm_prefix = gm_ids.str[:8]
        distances = gm_prefix.map(gm_distance_map)
        return distances.fillna(20.0)  # Default if not found
    
    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Fit scaler and transform features.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Scaled feature array
        """
        X_scaled = self.scaler.fit_transform(X[self.feature_names])
        self.is_fitted = True
        logger.info(f"Fitted scaler on {len(X)} samples, {self.n_features} features")
        return X_scaled
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """
        Transform features using fitted scaler.
        
        Args:
            X: Feature DataFrame
        
        Returns:
            Scaled feature array
        """
        if not self.is_fitted:
            raise ValueError("Must call fit_transform first")
        return self.scaler.transform(X[self.feature_names])


def prepare_training_data(
    data: pd.DataFrame,
    test_size: float = 0.2,
    validation_size: float = 0.15,
    random_state: int = 42,
    target_col: str = 'pidr'
) -> Tuple[Dict, FeatureEngineer]:
    """
    Prepare train/validation/test splits for ML training.
    
    Args:
        data: IDA results DataFrame
        test_size: Test set fraction
        validation_size: Validation set fraction (of training set)
        random_state: Random seed
        target_col: Target column name (e.g., 'pidr')
    
    Returns:
        Tuple of (data_dict, feature_engineer)
    
    Example:
        data_dict, fe = prepare_training_data(
            pd.read_csv('ida_results_verified.csv')
        )
        X_train, y_train = data_dict['X_train'], data_dict['y_train']
    """
    
    # Feature engineering
    fe = FeatureEngineer()
    X = fe.engineer_features(data)
    y = data[target_col].values
    
    # Remove rows with missing targets
    valid_idx = ~np.isnan(y)
    X = X[valid_idx]
    y = y[valid_idx]
    
    # Train/test split
    from sklearn.model_selection import train_test_split
    
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Train/validation split
    val_size_adj = validation_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adj, random_state=random_state
    )
    
    # Fit scaler on training set only
    X_train_scaled = fe.fit_transform(X_train)
    X_val_scaled = fe.transform(X_val)
    X_test_scaled = fe.transform(X_test)
    
    data_dict = {
        'X_train': X_train_scaled,
        'y_train': y_train,
        'X_val': X_val_scaled,
        'y_val': y_val,
        'X_test': X_test_scaled,
        'y_test': y_test,
        'feature_names': fe.feature_names,
        'train_split': len(X_train) / len(X),
        'val_split': len(X_val) / len(X),
        'test_split': len(X_test) / len(X),
    }
    
    logger.info(f"Data preparation complete:")
    logger.info(f"  Train: {len(X_train)} ({data_dict['train_split']:.1%})")
    logger.info(f"  Val:   {len(X_val)} ({data_dict['val_split']:.1%})")
    logger.info(f"  Test:  {len(X_test)} ({data_dict['test_split']:.1%})")
    logger.info(f"  Features: {fe.n_features}")
    
    return data_dict, fe
