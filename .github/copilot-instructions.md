---
name: ML-Based Seismic Drift Research
description: "An open-source research project developing Python ML surrogate models for seismic drift prediction of RC buildings under BNBC 2020. Use when working on: structural modeling, OpenSeesPy analysis, machine learning pipelines, fragility curves, data processing, or documentation for this project."
---

# ML-Based Seismic Drift Research — Agent Instructions

**Project:** ML-Based Seismic Drift Prediction of RC Buildings Under BNBC 2020  
**Repository:** ML_RCC_Research-share  
**Status:** Phase 1 (Structural Modeling) — Ready to Begin  
**Last Updated:** March 27, 2026

---

## Project Context

### Research Goal
Develop the first open-source, Python-native ML surrogate model to predict **peak inter-story drift ratio (PIDR)** of reinforced concrete (RC) moment frame buildings designed under **BNBC 2020**, trained on OpenSeesPy incremental dynamic analysis (IDA) data across all four seismic zones of Bangladesh.

### Key Features
- **Structural Models:** Parametric RC Special Moment Resisting Frames (SMRFs) — 5, 7, 10, 12, 15 stories
- **Analysis Method:** Incremental Dynamic Analysis (IDA) via OpenSeesPy
- **ML Models:** Linear Regression, Random Forest, XGBoost, Artificial Neural Networks (TensorFlow)
- **Interpretability:** SHAP analysis for feature importance
- **Compliance:** Full BNBC 2020 seismic zone parameters and design procedures
- **Reproducibility:** Fully containerized and open-source

### Target Paper
- **Title:** "ML Surrogate Models for Seismic Drift Prediction of Bangladesh RC Buildings Under BNBC 2020"
- **Target Journals:** MDPI *Buildings* (4–6 weeks), Elsevier *Structures* (8–12 weeks)
- **Length:** ~6000–7500 words
- **Figures/Tables:** IDA curves, fragility diagrams, feature importances (SHAP), performance metrics

---

## Project Structure & Key Directories

```
ML-Based_Seismic_Drift_Research/
├── .github/                          # This file + instructions
├── docs/                             # Building codes & references
│   ├── BuildingCodes/BNBC/          # Bangladesh National Building Code 2020
│   ├── BuildingCodes/US/ASCE-7-22/  # ASCE 7-22 seismic design standard
│   └── NL-Codes/FEMA-P-58/          # FEMA fragility curve reference
├── project/                          # Main Python project (activate venv here)
│   ├── config/                       # BNBC parameters & analysis configuration
│   ├── data/                         # Raw seismic records, processed datasets (git-ignored)
│   ├── src/                          # Main source code
│   │   ├── modeling/                 # OpenSeesPy structural models ← START HERE
│   │   ├── ida/                      # IDA pipeline & analysis
│   │   ├── ml/                       # ML model training & evaluation
│   │   ├── utils/                    # Helper functions
│   │   └── visualization/            # Plotting & visualization
│   ├── notebooks/                    # Jupyter notebooks for development
│   ├── models/                       # Trained ML & OpenSeesPy models (git-ignored)
│   ├── results/                      # Outputs: figures, reports, tables (git-ignored)
│   ├── tests/                        # Unit & integration tests
│   ├── Dockerfile & docker-compose.yml  # Container setup
│   ├── pyproject.toml                # Project metadata & dependencies
│   └── requirements.txt              # Python packages (install with: pip install -r...)
└── README.md, task_plan.md, recreation.md
```

---

## Technology Stack

### Core Scientific Computing
- **NumPy** — Numerical operations
- **SciPy** — Scientific algorithms
- **Pandas** — Data manipulation & analysis
- **Scikit-learn** — Classical ML algorithms (Linear Regression, Random Forest)

### Machine Learning & Deep Learning
- **XGBoost** — Gradient boosting models
- **TensorFlow + Keras** — Neural networks (ANN)
- **SHAP** (≥0.42.0) — Model interpretability & feature importance

### Structural Analysis
- **OpenSeesPy** (≥3.5.0) — Python interface to OpenSees (FEA framework for earthquake engineering)
  - Required for: Fiber-section RC elements, nonlinear analysis, dynamic equilibrium solver

### Data I/O & Configuration
- **PyYAML** — Parse configuration files (bnbc_parameters.yaml, analysis_config.yaml)
- **h5py** — HDF5 file handling for large datasets
- **openpyxl** — Excel export for results tables

### Visualization
- **Matplotlib** — Static plots (IDA curves, fragility diagrams)
- **Seaborn** — Statistical visualizations
- **Plotly** — Interactive plots (optional)

### Development & Testing
- **pytest** (≥7.4.0) — Testing framework
- **black** — Code formatting
- **flake8** — Linting
- **mypy** — Static type checking

### Experiment Tracking (Optional)
- **MLflow** — Experiment logging & model registry
- **Optuna** — Hyperparameter optimization

---

## Development Phases & Phases Status

### Phase 1: Structural Modeling ← **CURRENT PHASE**
**Status:** Ready to begin. No external dependencies.  
**Deliverables:**
- [ ] Create parametric RC SMRF base classes in `src/modeling/`
- [ ] Load BNBC 2020 seismic parameters from `config/bnbc_parameters.yaml`
- [ ] Implement 5, 7, 10, 12, 15-story models
- [ ] Define fiber-section RC elements (concrete + rebar)
- [ ] Apply gravity + lateral loads per BNBC 2020
- [ ] Validate models against code procedures
- [ ] Save verified models as templates

**Key Files to Create:**
- `src/modeling/rc_frame.py` — Base RC frame class
- `src/modeling/bnbc_compliance.py` — BNBC 2020 design checks
- `config/bnbc_parameters.yaml` — Seismic zone parameters (Z=0.12, 0.18, 0.24, 0.36)

**OpenSeesPy Specifics:**
- Use fiber sections for RC columns/beams (Concrete01/02 + Steel01/02 materials)
- Define geometric nonlinearity (P-Delta effects) for tall frames
- Recorder nodes: story drifts, base reactions, element stresses
- Time step for analysis: 0.005 seconds (from analysis_config.yaml)

---

### Phase 2: IDA Analysis & Data Generation
**Status:** Awaits Phase 1 completion.  
**Deliverables:**
- Prepare/acquire ground motion records for 4 seismic zones
- Implement ground motion scaling per BNBC 2020 spectrum
- Create IDA pipeline in `src/ida/`
- Run IDA for each building-zone combination (e.g., 5-story Zone III)
- Extract PIDR, peak accelerations, velocities
- Compile into structured dataset (CSV, HDF5)

---

### Phase 3: Machine Learning Pipeline
**Status:** Awaits Phase 2 data.  
**Deliverables:**
- Feature engineering (structural + seismic parameters)
- Train models: LR, RF, XGBoost, ANN
- Hyperparameter optimization (Optuna)
- Model evaluation (R², RMSE, MAE on test set)
- SHAP analysis for feature importance

---

### Phase 4: Fragility Curves & Results
**Status:** Awaits Phase 3 ML models.  
**Deliverables:**
- Define performance levels: IO (Immediate Occupancy), LS (Life Safety), CP (Collapse Prevention)
- Generate fragility curves using ML predictions
- Visualize curves for all zones
- Generate publication-quality figures & tables

---

## Configuration Files

### `config/bnbc_parameters.yaml`
**Purpose:** Central repository for BNBC 2020 seismic parameters.

**Structure:**
```yaml
seismic_zones:
  zone_1:
    pga: 0.05  # Peak Ground Acceleration (g)
    z_coeff: 0.12
    description: "Very low hazard"
  zone_2:
    pga: 0.10
    z_coeff: 0.18
    description: "Low hazard"
  zone_3:
    pga: 0.15
    z_coeff: 0.24
    description: "Moderate hazard (Dhaka region)"
  zone_4:
    pga: 0.20
    z_coeff: 0.36
    description: "High hazard (Chittagong region)"

site_classes:
  A:
    vs30: 1500  # Shear wave velocity (m/s)
  B:
    vs30: 760
  #... more

response_spectrum:
  # T, Sa(T) pairs for each zone
```

**Usage in Code:**
```python
import yaml
with open('config/bnbc_parameters.yaml') as f:
    bnbc = yaml.safe_load(f)
pga_zone3 = bnbc['seismic_zones']['zone_3']['pga']
```

### `config/analysis_config.yaml`
**Purpose:** IDA and ML training hyperparameters.

**Key Parameters:**
- **IDA:** Intensity measure (Sa @ T=0.5s), range (0.05g–1.50g), time step (0.005s), convergence tol (1e-8)
- **ML:** Train/test split (80/20), validation (15%), scaler (StandardScaler)
- **Random Forest:** 200 estimators, max_depth=20
- **Paths:** data_dir, model_dir, results_dir

---

## Essential Commands

### Setup & Environment
```bash
cd project
python3.9+ -m venv .venv
source .venv/bin/activate          # Unix/macOS
# .venv\Scripts\activate            # Windows

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Verification
```bash
# Test critical imports
python -c "import openseespy.opensees as ops; import pandas; import sklearn; print('✓ All imports OK')"

# Run tests
pytest tests/ -v --cov=src

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Jupyter Notebooks
```bash
# Start Jupyter Lab (development)
jupyter lab --notebook-dir=notebooks

# Or Docker
cd ..
docker-compose up --build
# Access at http://localhost:8888 (token: seismic-drift)
```

### Data & Results
```bash
# Structure created automatically by pipeline:
# data/raw/              — Ground motion records
# data/processed/        — Cleaned datasets (CSV/HDF5)
# models/ml_models/      — Trained sklearn/XGBoost/TensorFlow models
# results/figures/       — Publication-quality plots (PNG, PDF)
```

---

## Code Conventions & Patterns

### Structural Modeling (`src/modeling/`)
1. **Base Class:** `RCFrame` with properties for n_stories, story_height, column_section, beam_section
2. **Materials:** Concrete01/02 for concrete, Steel01/02 for rebar
3. **Element tagging:** Column ID = `floor*1000 + col_num`; Beam ID = `floor*2000 + beam_num`
4. **Gravity analysis:** Apply gravity loads first, then latload for lateral
5. **Recorders:** Capture node displacements, element forces every 10 steps minimum

### IDA Pipeline (`src/ida/`)
1. Load building model from `src/modeling/`
2. Scale ground motion record to target intensity (Sa)
3. Run nonlinear dynamic analysis for 10+ seconds post-earthquake
4. Extract maximum inter-story drift from recorder outputs
5. Store result: (building_id, zone, gm_id, sa_intensity, pidr)

### ML Training (`src/ml/`)
1. Normalize features with StandardScaler (fit on train, apply to test)
2. Split data: 80% train → 70% train + 15% validation, 20% test
3. Log hyperparameters & metrics to MLflow (optional)
4. Save model with joblib (sklearn) or .h5 (TensorFlow)
5. Generate SHAP values for feature importance

### Testing (`tests/`)
- Unit tests: model instantiation, parameter loading, feature engineering
- Integration tests: IDA pipeline end-to-end
- Use pytest fixtures for shared data/models

---

## Common Workflows

### 1. Creating a New RC Frame (Phase 1)
```python
from src.modeling import RCFrame
import yaml

# Load BNBC parameters
with open('config/bnbc_parameters.yaml') as f:
    bnbc = yaml.safe_load(f)

# Create 10-story frame
frame = RCFrame(
    n_stories=10,
    story_height=3.5,  # meters
    zone=3,  # Moderate hazard (Dhaka)
    bnbc_params=bnbc
)

# Apply gravity load, validate, save
frame.apply_gravity_loads()
frame.validate_bnbc_compliance()
frame.save_model('models/openseespy/frame_10s_z3.json')
```

### 2. Running IDA Analysis (Phase 2)
```python
from src.ida import IDAAnalysis
from src.modeling import RCFrame

frame = RCFrame.load('models/openseespy/frame_10s_z3.json')
ida = IDAAnalysis(
    model=frame,
    gm_record='data/raw/gm_z3_001.csv',
    intensity_range=(0.05, 1.50),
    step=0.10
)
pidr_curve = ida.run()
ida.plot_ida_curve()
```

### 3. Training an ML Model (Phase 3)
```python
from src.ml import MLTrainer
import pandas as pd

# Load processed data
data = pd.read_csv('data/processed/training_data.csv')
trainer = MLTrainer(data, config_path='config/analysis_config.yaml')

# Train models
models = trainer.train_all_models()  # LR, RF, XGBoost, ANN
trainer.evaluate_and_compare()
trainer.generate_shap_plots()

# Save best model
trainer.save_best_model('models/ml_models/')
```

---

## Agent Behavior & Tool Usage

### When Writing Code
- **Goal:** Implement features following Python best practices (PEP 8, type hints)
- **Files to check first:** `README.md` (research objectives), `recreation.md` (directory structure), `config/*.yaml` (parameters)
- **Always test locally:** Run test suite before committing
- **Document publicly-facing functions:** Include docstrings with parameter descriptions & return types

### When Encountering Errors
- **OpenSeesPy errors:** Check element/node IDs, constraint definitions, material properties
- **Data pipeline errors:** Validate CSV/HDF5 formats, check for missing values
- **ML training errors:** Check feature dimensions, class balance (if classification), data types

### When Making Code Changes
- Use the `recreation.md` as the source of truth for directory structure
- Update corresponding configuration files (e.g., paths in `analysis_config.yaml`)
- Run `pytest` before committing changes
- Update `task_plan.md` to reflect progress

### When Exploring the Codebase
- Start with `README.md` for research context
- Review `recreation.md` for project structure
- Check `src/__init__.py` files for module exports
- Look at `tests/` for usage examples of each module

---

## Important Parameters & Constants

### BNBC 2020 Seismic Zones
| Zone | PGA (g) | Z_coeff | Region |
|------|---------|---------|--------|
| Zone I | 0.05 | 0.12 | Small northern areas |
| Zone II | 0.10 | 0.18 | Most of Bangladesh |
| Zone III | 0.15 | 0.24 | Dhaka, central region |
| Zone IV | 0.20 | 0.36 | Chittagong, SE region |

### IDA Parameters (from `analysis_config.yaml`)
- **Intensity Measure:** Sa(T=0.5s)
- **Range:** 0.05g to 1.50g
- **Increment:** 0.10g (~16 runs per building-GM pair)
- **Time Step:** 0.005 seconds
- **Convergence Tolerance:** 1e-8

### ML Model Features (Expected)
- Building: n_stories, story_height, column_size, beam_size, steel_ratio
- Seismic: zone, pga, distance_to_fault (if available)
- Soil: site_class, vs30 (if available)
- **Target:** PIDR (inter-story drift ratio)

---

## Git & Repository Practices

### What to Commit
- ✅ Source code (`src/`, `tests/`)
- ✅ Configuration files (`config/*.yaml`)
- ✅ Notebooks demonstrating methodology (`notebooks/`)
- ✅ Documentation (`docs/`, `.github/`)
- ✅ `pyproject.toml`, `requirements.txt`, `Dockerfile`

### What NOT to Commit (in `.gitignore`)
- ❌ `.venv/` — Virtual environment
- ❌ `data/raw/`, `data/processed/` — Large datasets
- ❌ `models/`, `results/` — Generated artifacts (except templates)
- ❌ `*.pyc`, `__pycache__/` — Python cache
- ❌ `.env` — Environment variables

### Commit Messages
```
Phase [1|2|3|4]: [Feature] - Brief description

- Detailed explanation of changes
- Reference task_plan.md if applicable (e.g., "See task 1.2")
```

Example:
```
Phase 1: Implement OpenSeesPy RC frame base class

- Created RCFrame class with property validation
- Added BNBC 2020 compliance checks for zone parameters
- Implemented gravity load application & verification
- See task_plan.md § Phase 1, task 1.1
```

---

## Documentation & Notebooks

When creating Jupyter notebooks:
1. **Folder:** `notebooks/01_data_exploration/`, `notebooks/02_ida_analysis/`, etc.
2. **Format:** Markdown cells for explanation, code cells for execution
3. **Name:** Descriptive (e.g., `01_validate_frame_models.ipynb`)
4. **Outputs:** Save figures to `results/figures/` for later inclusion in paper

---

## Potential Blockers & Solutions

| Issue | Solution |
|-------|----------|
| OpenSeesPy installation fails | Ensure gfortran, BLAS, LAPACK are installed: `sudo apt-get install gfortran libblas-dev liblapack-dev` |
| Large IDA datasets cause memory issues | Use HDF5 format (h5py) instead of CSV; process in batches |
| TensorFlow GPU support not working | Check CUDA/cuDNN versions match TensorFlow; see TensorFlow docs |
| Model overfitting on small dataset | Use cross-validation (k-fold), regularization (L2), early stopping |
| SHAP computation is slow | Use TreeExplainer for tree-based models (faster than KernelExplainer) |

---

## Next Immediate Steps

1. **Review & Activate:** Source the Python virtual environment:
   ```bash
   cd project
   source .venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Setup:**
   ```bash
   python -c "import openseespy.opensees as ops; print('✓ OpenSeesPy ready')"
   ```

4. **Begin Phase 1 — Create OpenSeesPy Structural Models:**
   - Start with `src/modeling/rc_frame.py` (base class)
   - Load BNBC parameters from `config/bnbc_parameters.yaml`
   - Implement parametric 5, 7, 10, 12, 15-story SMRF models
   - See `README.md` § 5. Structural Modelling Plan for detailed requirements

5. **Track Progress:**
   - Update `task_plan.md` with completion status
   - Commit working code regularly with descriptive messages

---

## References & Further Reading

- **Project Documentation:**
  - `README.md` — Full research master plan & objectives
  - `task_plan.md` — Detailed task breakdown & progress tracking
  - `recreation.md` — Complete directory & dependency guide

- **BNBC 2020 Seismic Code:**
  - `docs/BuildingCodes/BNBC/` — Official standards & design procedures

- **OpenSeesPy Documentation:**
  - https://openseespydoc.readthedocs.io/
  - Check examples for fiber sections, nonlinear analysis

- **ML Interpretability:**
  - SHAP tutorials: https://shap.readthedocs.io/
  - Focus on TreeExplainer for Random Forest & XGBoost

---

**Document Version:** 1.0  
**Last Updated:** March 27, 2026  
**Status:** Agent instructions finalized; ready for development
