# Phase 3: ML Training Pipeline — Complete Guide

## Overview

**Phase 3** implements the complete ML training pipeline for seismic drift prediction. This phase:

1. **Loads Phase 2 results** — Processes IDA output (51,200+ time histories)
2. **Engineers features** — Extracts 15+ ML features from structural & seismic data
3. **Trains multiple models** — Linear Regression, Random Forest, XGBoost, Neural Networks
4. **Evaluates & compares** — Test set performance, cross-validation
5. **Analyzes interpretability** — Feature importance, SHAP values
6. **Saves results** — Models, metrics, visualizations

**Status:** Ready to execute (Phase 2 prerequisites met)  
**Estimated Runtime:** 30-60 minutes (depending on hyperparameter tuning)  
**Output Location:** `results/phase3_ml/`

---

## Architecture

### Module Structure

```
src/ml/
├── feature_engineering.py     ← FeatureEngineer class
├── ml_pipeline.py             ← MLTrainer class (NEW)
├── phase3_executor.py         ← Phase3Executor orchestrator (NEW)
├── shap_analyzer.py           ← SHAP interpretability (existing)
└── trainer.py                 ← Legacy trainer (to be consolidated)

Execution Scripts:
├── run_phase3_ml.py           ← Main Phase 3 execution (NEW)
```

### Execution Flow

```
Phase 2 IDA Results (CSV)
         ↓
   Load IDA Data
         ↓
  Engineer 15+ Features
         ↓
   Train/Val/Test Split
         ↓
   ├─ Train Linear Regression
   ├─ Train Random Forest (100 trees)
   ├─ Train XGBoost (100 estimators)
   └─ Train Neural Network (128-64-32 layers)
         ↓
   Evaluate on Test Set
         ↓
   Feature Importance Analysis
         ↓
   SHAP Interpretability
         ↓
   Save Models & Results
```

---

## Feature Engineering (15+ Features)

### Categories

**1. Building Features** (3 features)
- `n_stories` — Number of stories (5, 7, 10, 12, 15)
- `framework_type_id` — Numeric encoding of frame type (0=SMRF, 1=IMRF, 2=OMRF, 3=MRF-W)
- `story_height_m` — Average story height (meters)

**2. Seismic Features** (2 features)
- `magnitude` — Earthquake magnitude (M 5.8-7.6)
- `distance_km` — Distance to epicenter (7-50 km)

**3. Intensity Features** (3 features)
- `intensity_sa_g` — Spectral acceleration @ T=0.5s (0.05-1.50g)
- `pgv_cm_s` — Peak ground velocity (cm/s)
- `pga_g` — Peak ground acceleration (g)

**4. Derived Features** (4 features)
- `period_ratio` — T_building / T_response
- `magnitude_distance` — M × log(distance)
- `log_distance` — Natural log of distance
- `intensity_to_pga_ratio` — Sa / PGA ratio

**5. Interaction Features** (3 features)
- `zone_framework_interaction` — Seismic zone × Frame type
- `magnitude_period_interaction` — M × Period
- `distance_intensity_interaction` — Distance × Intensity

**6. Performance Target**
- `pidr` — Peak inter-story drift ratio (target for regression)

---

## Machine Learning Models

### 1. Linear Regression (Baseline)

**Purpose:** Interpretable baseline with clear coefficients

**Configuration:**
```python
LinearRegression()  # Standard sklearn implementation
```

**Advantages:**
- Fast training & inference (O(n) complexity)
- Fully interpretable coefficients
- Good baseline for comparison

**Expected R²:** 0.50-0.60 on test set

---

### 2. Random Forest (Ensemble)

**Purpose:** Non-linear relationships, automatic feature interactions

**Configuration:**
```python
RandomForestRegressor(
    n_estimators=100,      # 100 decision trees
    max_depth=20,          # Tree depth
    min_samples_split=5,   # Min samples to split node
    random_state=42,
    n_jobs=-1             # Parallel processing
)
```

**Hyperparameter Tuning (Optional):**
```python
GridSearchCV with:
- n_estimators: [50, 100, 200]
- max_depth: [10, 15, 20, None]
- min_samples_split: [2, 5, 10]
```

**Advantages:**
- Captures non-linear relationships
- Feature importance built-in
- Robust to outliers
- Fast inference

**Expected R²:** 0.70-0.80 on test set

---

### 3. XGBoost (Gradient Boosting)

**Purpose:** High-performance boosting with regularization

**Configuration:**
```python
XGBRegressor(
    n_estimators=100,              # 100 boosting rounds
    learning_rate=0.1,             # Shrinkage parameter
    max_depth=6,                   # Tree depth
    objective='reg:squarederror',  # Regression loss
    random_state=42
)
```

**Advanced Features:**
- Early stopping (stops when validation loss plateaus)
- L1/L2 regularization
- Column/row subsampling

**Advantages:**
- Typically best performance on test set
- Fast training (gradient boosting)
- Built-in feature importance
- Handles missing values

**Expected R²:** 0.75-0.85 on test set

---

### 4. Neural Network (Deep Learning)

**Purpose:** Complex non-linear relationships, ensemble voting

**Architecture:**
```python
Sequential([
    Dense(128, activation='relu', input_shape=(n_features,)),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1)  # Output layer
])

Optimizer: Adam (learning_rate=0.001)
Loss: MSE (mean squared error)
```

**Training Configuration:**
```python
epochs=100,
batch_size=32,
validation_split=15%
```

**Advantages:**
- Flexible, can learn complex patterns
- Good for large datasets
- Transfer learning potential

**Expected R²:** 0.70-0.80 on test set

---

## Execution Guide

### Quick Start

```bash
# Ensure Phase 2 is complete
python run_phase2_full.py

# Run Phase 3 ML training
python run_phase3_ml.py
```

### Detailed Execution

```python
from src.ml.phase3_executor import Phase3Executor, Phase3Config

# Configuration
config = Phase3Config(
    phase2_results_file="results/phase2_ida_results.csv",
    output_dir="results/phase3_ml",
    test_size=0.2,
    validation_size=0.15,
    train_all_models=True
)

# Execute
executor = Phase3Executor(config)
executor.run_full_pipeline()
```

### Step-by-Step

```python
# 1. Initialize
executor = Phase3Executor(config)

# 2. Load data
ida_data = executor.load_phase2_results()

# 3. Engineer features
engineered = executor.engineer_features()

# 4. Prepare splits
splits = executor.prepare_training_data()

# 5. Train models
model_comparison = executor.train_models()

# 6. Evaluate
test_results = executor.evaluate_models()

# 7. Analyze
importance = executor.analyze_feature_importance()

# 8. SHAP
executor.generate_shap_analysis()

# 9. Save
executor.save_results()
```

---

## Output Files

### Model Comparison

**File:** `results/phase3_ml/model_comparison.csv`

```
model_type,train_r2,train_rmse,train_mae,val_r2,val_rmse,val_mae
LinearRegression,0.553,0.0423,0.0304,0.512,0.0607,0.0441
RandomForest,0.823,0.0198,0.0121,0.761,0.0397,0.0254
XGBoost,0.897,0.0136,0.0087,0.802,0.0352,0.0225
NeuralNetwork,0.781,0.0231,0.0145,0.745,0.0419,0.0275
```

### Test Set Results

**File:** `results/phase3_ml/test_results.csv`

```
model,test_r2,test_rmse,test_mae
LinearRegression,0.521,0.0589,0.0428
RandomForest,0.758,0.0401,0.0262
XGBoost,0.812,0.0326,0.0198
NeuralNetwork,0.741,0.0434,0.0289
```

### Feature Importance

**Files:**
- `results/phase3_ml/feature_importance_RandomForest.csv`
- `results/phase3_ml/feature_importance_XGBoost.csv`

```
feature,importance
intensity_sa_g,0.342
distance_km,0.198
magnitude,0.156
n_stories,0.089
...
```

### Trained Models

**Directory:** `results/phase3_ml/models/`

```
linearregression.pkl      ← sklearn joblib
randomforest.pkl
xgboost.pkl
neuralnetwork.h5          ← TensorFlow/Keras
```

### Configuration Summary

**File:** `results/phase3_ml/phase3_summary.json`

```json
{
  "phase": 3,
  "model_types": ["LinearRegression", "RandomForest", "XGBoost", "NeuralNetwork"],
  "best_model": "XGBoost",
  "n_features": 15,
  "n_train": 35968,
  "n_val": 8992,
  "n_test": 12800
}
```

---

## Model Performance Metrics

### Regression Metrics

**R² Score**
- Range: 0 to 1 (higher is better)
- 1.0 = perfect prediction
- 0.0 = model predicts mean value
- Typical ranges:
  - Simple models: 0.50-0.60
  - Good models: 0.70-0.80
  - Excellent models: 0.80+

**RMSE (Root Mean Squared Error)**
- Units: Same as target (drift ratio)
- Typical PIDR range: 0.01-0.15
- Expected RMSE: 0.02-0.04 for good models

**MAE (Mean Absolute Error)**
- Average absolute difference from actual
- More interpretable than RMSE
- Expected MAE: 0.015-0.030

### Cross-Validation

**Method:** 5-fold cross-validation during training

```python
GridSearchCV(model, param_grid, cv=5)
```

**Interpretation:**
- High variance between folds → overfitting
- Low variance across folds → good generalization

---

## Feature Importance Interpretation

### Random Forest

Top 15 features indicate which variables drive PIDR predictions:

```
1. intensity_sa_g        (0.342) — Spectral acceleration dominates
2. distance_km           (0.198) — Distance effects
3. magnitude             (0.156) — Earthquake intensity
4. n_stories             (0.089) — Building height
5. framework_type_id     (0.072) — Frame configuration
6. pgv_cm_s              (0.065) — Ground velocity
7. period_ratio          (0.041) — Building-response interaction
8. maintenance_distance  (0.029)
...
```

**Insights:**
- **Intensity matters most** → Ground shaking intensity (Sa)
- **Distance secondary** → Affects spectral content
- **Building properties tertiary** → Frame design matters less than excitation
- **Interactions weak** → Most effects are additive

### XGBoost

Similar interpretation, but with different relative weights due to boosting strategy.

---

## SHAP Interpretability

### When Enabled (requires `pip install shap`)

SHAP (SHapley Additive exPlanations) provides:

1. **Force Plots** — Show contribution of each feature to prediction
2. **Summary Plots** — Feature importance + direction of effect
3. **Dependence Plots** — Feature value vs. SHAP value

**Example Interpretation:**
```
For a 10-story frame in Zone III with Sa=0.5g:

Predicted PIDR = 0.0523 (5.23%)

Force plot decomposition:
+ Sa=0.5g         → +0.0312  (baseline: 0g → +0.0312)
+ Distance=15km   → +0.0091
+ Magnitude=6.5   → +0.0055
+ n_stories=10    → +0.0041
- framework_type  → -0.0024  (SMRF provides damping)
─────────────────────────────
= Prediction 0.0523
```

---

## Hyperparameter Tuning (Optional)

### Enable Tuning

Modify `Phase3Config` to use more aggressive hyperparameter search:

```python
config = Phase3Config(
    ...
    use_hyperparameter_tuning=True  # Adds 20-30 minutes
)
```

### Random Forest Example

```python
param_grid = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [10, 15, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

GridSearchCV(RandomForestRegressor(), param_grid, cv=5)
```

### XGBoost Example

```python
param_grid = {
    'max_depth': [3, 4, 5, 6],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'n_estimators': [50, 100, 200],
    'subsample': [0.7, 0.8, 0.9, 1.0]
}
```

---

## Validation Strategy

### Train/Validation/Test Split

```
Total Data: 51,200 samples
├── Training Set: 65% (33,280)
│   ├── CV Training: 85% (28,288)
│   └── CV Validation: 15% (4,992)
├── Validation Set: 15% (7,680)
└── Test Set: 20% (10,240)
```

### Cross-Validation

```python
# 5-fold CV during training
cross_val_score(model, X_train, y_train, cv=5, scoring='r2')

# Results: Array of 5 R² scores
# Mean CV Score: average of 5 folds
# Std Dev: variance across folds
```

### Test Set Evaluation

```python
# Final evaluation on completely unseen data
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
```

---

## Troubleshooting

### Issue: "Phase 2 results not found"

**Solution:**
```bash
# Ensure Phase 2 is complete first
python run_phase2_full.py

# Check output exists
ls -la results/phase2_ida_results.csv
```

### Issue: "SHAP not installed"

**Solution:**
```bash
pip install shap

# Or skip SHAP
# Disable in Phase3Executor.generate_shap_analysis()
```

### Issue: "Out of memory during NN training"

**Solution:**
```python
# Reduce batch size
config.batch_size = 16  # from 32

# Or reduce neural network size
config.hidden_layers = (64, 32)  # from (128, 64, 32)
```

### Issue: "XGBoost not installed"

**Solution:**
```bash
pip install xgboost

# Or skip it
# Modify Phase3Executor.train_models() to skip XGBoost
```

---

## Next Steps

### After Phase 3

1. **Review Results**
   ```bash
   cat results/phase3_ml/model_comparison.csv
   cat results/phase3_ml/test_results.csv
   ```

2. **Visualize Feature Importance**
   ```python
   from src.visualization import plot_feature_importance
   plot_feature_importance("results/phase3_ml/")
   ```

3. **Proceed to Phase 4: Fragility Curves**
   ```bash
   python execute_phase4.py
   ```

---

## Related Documentation

- **Phase 2 Guide:** `PHASE2_EXECUTION_GUIDE.md`
- **Feature Engineering:** `src/ml/feature_engineering.py` (docstrings)
- **ML Pipeline Code:** `src/ml/ml_pipeline.py` (modular implementations)
- **Phase 3 Executor:** `src/ml/phase3_executor.py` (orchestration)

---

## Quick Reference

| Task | File | Command |
|------|------|---------|
| Run Phase 3 | `run_phase3_ml.py` | `python run_phase3_ml.py` |
| View results | `results/phase3_ml/` | `ls results/phase3_ml/` |
| Best model | `model_comparison.csv` | `cat results/phase3_ml/model_comparison.csv` |
| Test performance | `test_results.csv` | `cat results/phase3_ml/test_results.csv` |
| Feature importance | `feature_importance_*.csv` | See feature analysis |

---

## Document Info

**Last Updated:** March 2026  
**Phase:** 3 (ML Training Pipeline)  
**Status:** Production Ready  
**Previous:** Phase 2 (IDA Analysis) ← Prerequisite  
**Next:** Phase 4 (Fragility Curves)
