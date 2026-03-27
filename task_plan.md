# Task Plan & Progress Tracking
## ML-Based Seismic Drift Prediction of RC Buildings Under BNBC 2020

**Date Created:** March 27, 2026  
**Last Updated:** March 27, 2026  
**Current Phase:** Phase 1 — Structural Modeling (Ready to Begin)  
**Python Version:** 3.12.1  
**Status:** ✅ **PROJECT INFRASTRUCTURE COMPLETE**

---

## Executive Summary

The ML-Based Seismic Drift Research project is a 4-phase research initiative to develop Python-native machine learning surrogate models for predicting peak inter-story drift ratio (PIDR) of RC moment-resisting frame buildings designed under BNBC 2020. 

**Current Status:** All project infrastructure (directories, configuration files, dependencies) has been successfully initialized. The environment is ready to begin Phase 1 implementation.

---

## Completed Tasks (March 27, 2026)

### ✅ Environment Setup
- [x] Created Python 3.12.1 virtual environment (`.venv/`)
- [x] Upgraded pip, setuptools, wheel to latest versions
- [x] Installed all 95+ project dependencies from `requirements.txt`
- [x] Verified critical imports: OpenSeesPy, TensorFlow, XGBoost, SHAP, scikit-learn

### ✅ Project Infrastructure
- [x] Created complete directory structure (22 directories):
  - `config/` — Configuration files for BNBC and analysis parameters
  - `src/` (5 submodules) — modeling, ida, ml, utils, visualization
  - `data/` (3 subdirs) — raw, processed, metadata
  - `models/` (3 subdirs) — openseespy, ml_models, checkpoints
  - `results/` (3 subdirs) — figures, reports, tables
  - `notebooks/` (4 subdirs) — organized by analysis phase
  - `tests/` — Unit and integration tests

### ✅ Configuration Files
- [x] `pyproject.toml` — Full project metadata, dependencies, tool configurations
  - Black, isort, mypy, pytest, coverage all configured
  - Optional dependency groups: dev, jupyter, ml, viz, docs, dev-all
  - Python 3.9+ support (running on 3.12.1)

- [x] `requirements.txt` — Pinned versions of 40+ packages including:
  - Scientific: NumPy, SciPy, Pandas, Scikit-learn
  - ML/DL: XGBoost, LightGBM, TensorFlow/Keras, SHAP
  - Structural: OpenSeesPy 3.8.0
  - Dev/Test: pytest, black, flake8, mypy, isort
  - Tracking: MLflow, Optuna
  - Viz: Matplotlib, Seaborn, Plotly, Folium

- [x] `config/bnbc_parameters.yaml` — BNBC 2020 reference data:
  - Seismic zones I–IV with PGA, Z_coeff, regional mappings
  - Site classifications A–E with Vs30 ranges and amplification factors
  - Building response modification factors (R) for RC SMRF
  - Design response spectrum parameters
  - Default material properties (concrete & steel)
  - Gravity load factors and floor height defaults

- [x] `config/analysis_config.yaml` — IDA and ML settings:
  - IDA parameters: IM (Sa @ T=0.5s), range (0.05–1.50g), time step (0.005s)
  - Convergence tolerances (1e-8), recording intervals
  - ML data split: 80/20 train/test, 5-fold CV
  - Model hyperparameters (RF, XGBoost, ANN)
  - SHAP analysis configuration
  - MLflow experiment tracking (optional)
  - Output format specifications (PNG @ 300 DPI, CSV/Excel tables)

### ✅ Python Module Structure
- [x] `src/__init__.py` — Top-level package with version info and submodule imports
- [x] `src/modeling/__init__.py` — OpenSeesPy RC frame models (SMRF)
- [x] `src/ida/__init__.py` — IDA analysis pipeline and ground motion processing
- [x] `src/ml/__init__.py` — ML model training, evaluation, SHAP analysis
- [x] `src/utils/__init__.py` — Helper functions and utilities
- [x] `src/visualization/__init__.py` — Plotting and visualization routines
- [x] `tests/__init__.py` — Test suite (ready for Phase 1 tests)

### ✅ Git & Documentation Setup
- [x] `.gitignore` — Comprehensive rules to exclude:
  - Virtual environments (`.venv/`)
  - Generated data (data/raw, data/processed, *.csv, *.h5)
  - Models and checkpoints (models/ml_models, *.pkl, *.joblib)
  - Results (results/figures, results/reports, *.png, *.pdf)
  - IDE files, Python cache, Jupyter checkpoints
  - Logs, temporary files, system files

- [x] `.github/copilot-instructions.md` — AI agent customization:
  - Project context, research goal, key features
  - Technology stack overview
  - Phase status and deliverables
  - Configuration file descriptions
  - Code conventions and patterns
  - Common workflows with code examples
  - Git practices and commit message format
  - Building code references & next steps

---

## Current Status & Verification

### Environment Status
```bash
✓ Python 3.12.1 active
✓ Virtual environment: /workspaces/ML_RCC_Research-share/project/.venv
✓ All 95+ dependencies installed successfully
✓ Critical imports verified:
  - openseespy.opensees
  - pandas
  - scikit-learn
  - tensorflow (CPU mode, no CUDA)
  - xgboost
  - shap
```

### Project Structure Status
```
project/
├── config/
│   ├── bnbc_parameters.yaml     ✓ (BNBC 2020 seismic zones, materials, design factors)
│   └── analysis_config.yaml     ✓ (IDA & ML hyperparameters)
├── src/
│   ├── modeling/                ✓ (Ready for Phase 1 - RC frame models)
│   ├── ida/                     ✓ (Ready for Phase 2 - IDA pipeline)
│   ├── ml/                      ✓ (Ready for Phase 3 - ML training)
│   ├── utils/                   ✓ (Ready for support functions)
│   └── visualization/           ✓ (Ready for plotting utilities)
├── data/
│   ├── raw/                     ✓ (Empty - ready for ground motion records)
│   ├── processed/               ✓ (Empty - ready for cleaned datasets)
│   └── metadata/                ✓ (Empty - ready for schema files)
├── models/
│   ├── openseespy/              ✓ (Ready for OpenSeesPy model templates)
│   ├── ml_models/               ✓ (Ready for trained models)
│   └── checkpoints/             ✓ (Ready for TensorFlow checkpoints)
├── results/
│   ├── figures/                 ✓ (Ready for plots & publication figures)
│   ├── reports/                 ✓ (Ready for analysis reports)
│   └── tables/                  ✓ (Ready for CSV/Excel exports)
├── notebooks/
│   ├── 01_data_exploration/     ✓ (Ready for EDA)
│   ├── 02_ida_analysis/         ✓ (Ready for IDA results)
│   ├── 03_ml_training/          ✓ (Ready for ML model development)
│   └── 04_results_analysis/     ✓ (Ready for final analysis)
├── tests/                       ✓ (Ready for pytest suite)
├── pyproject.toml               ✓ (Full metadata & tool configs)
├── requirements.txt             ✓ (All dependencies pinned)
└── .gitignore                   ✓ (Configured for large files, generated artifacts)
```

---

## Phase Breakdown & Timeline

### Phase 1: Structural Modeling ← **CURRENT**
**Status:** ✅ Infrastructure Ready | ⏳ Implementation Pending  
**Duration:** ~1–2 weeks  
**Deliverables:**
- [ ] `src/modeling/rc_frame.py` — Base RCFrame class
  - [ ] Properties: n_stories, story_height, column_section, beam_section, period
  - [ ] Methods: apply_gravity_loads(), apply_lateral_loads(), analyze(), save_model()
  - [ ] Constructor validation and error handling
  
- [ ] `src/modeling/materials.py` — Material definitions
  - [ ] Concrete01/Concrete02 for unconfined & confined concrete
  - [ ] Steel01/Steel02 for reinforcement
  - [ ] Default BNBC material properties from config
  
- [ ] `src/modeling/bnbc_compliance.py` — Design verification
  - [ ] Base shear calculation per BNBC 2020
  - [ ] Period estimation (Ta = Ct * h^0.75)
  - [ ] Story drift validation (max 2.5% for RC SMRF)
  - [ ] Strength reduction factor application (φ)
  
- [ ] Implement 5 building templates:
  - [ ] 5-story SMRF (T ≈ 0.5s)
  - [ ] 7-story SMRF (T ≈ 0.7s)
  - [ ] 10-story SMRF (T ≈ 1.0s)
  - [ ] 12-story SMRF (T ≈ 1.2s)
  - [ ] 15-story SMRF (T ≈ 1.5s)
  
- [ ] OpenSeesPy model setup:
  - [ ] Fiber sections for columns (Concrete + rebars)
  - [ ] Fiber sections for beams (Concrete + rebars)
  - [ ] Geometric nonlinearity (P-Delta transformation)
  - [ ] Node recorders (displacement, drift)
  - [ ] Element recorders (force, stress)
  
- [ ] Model verification:
  - [ ] Verify modal properties (period, mode shapes)
  - [ ] Gravity analysis stability
  - [ ] Lateral load distribution
  - [ ] Conservation of mass and energy
  
- [ ] Save templates:
  - [ ] models/openseespy/frame_5s_z1.json → models/openseespy/frame_15s_z4.json
  - [ ] Each zone × story combination

**Key Files:** `src/modeling/rc_frame.py`, `src/modeling/materials.py`, `src/modeling/bnbc_compliance.py`  
**Dependencies:** OpenSeesPy, PyYAML, NumPy, Pandas  
**Tests:** `tests/test_rc_frame.py`, `tests/test_bnbc_compliance.py`

---

### Phase 2: IDA Analysis & Data Generation
**Status:** ⏳ Awaits Phase 1  
**Duration:** ~2–3 weeks  
**Deliverables:**
- Ground motion record preparation (PEER, NGA database)
- Ground motion scaling per BNBC 2020 response spectrum
- IDA pipeline implementation
- PIDR extraction for all building-zone combinations
- Dataset compilation (CSV, HDF5 format)
- Data validation & QC checks

**Key Files:** `src/ida/ida_analysis.py`, `src/ida/gm_scaler.py`  
**Output:** `data/processed/ida_results.csv` (~20,000 records)

---

### Phase 3: Machine Learning Pipeline
**Status:** ⏳ Awaits Phase 2 data  
**Duration:** ~2–3 weeks  
**Deliverables:**
- Feature engineering (structural + seismic)
- Train/test set preparation
- Model training: LR, RF, XGBoost, ANN
- Hyperparameter optimization (Optuna)
- Model evaluation (R², RMSE, MAE, cross-validation)
- SHAP analysis for feature importance
- Best model selection and save

**Key Files:** `src/ml/trainer.py`, `src/ml/evaluator.py`, `src/ml/shap_analyzer.py`  
**Output:** `models/ml_models/{best_model}`, `results/shap_analysis_*.png`

---

### Phase 4: Fragility Curves & Publication
**Status:** ⏳ Awaits Phase 3  
**Duration:** ~1–2 weeks  
**Deliverables:**
- Performance level definitions (IO, LS, CP)
- Fragility curve generation
- Visualization (PNG, PDF quality)
- Publication-ready tables
- Paper figures and results summary
- Final report & reproducibility verification

**Key Files:** `src/visualization/fragility_curves.py`  
**Output:** `results/figures/fragility_*.pdf`, `results/tables/results_summary.xlsx`

---

## Next Immediate Action Items

### 🚀 START HERE: Phase 1 — Begin Structural Modeling (This Week)

#### Step 1: Review BNBC Configuration
```bash
cd /workspaces/ML_RCC_Research-share/project
source .venv/bin/activate
cat config/bnbc_parameters.yaml  # Review seismic zones & design factors
cat config/analysis_config.yaml   # Review IDA parameters
```

#### Step 2: Create Base RC Frame Class (`src/modeling/rc_frame.py`)
**Implement:**
- `RCFrame` class with:
  - Constructor: `__init__(n_stories, story_height, zone, bnbc_params, ...)`
  - Properties for column/beam dimensions, rebar ratios
  - Methods: `apply_gravity_loads()`, `validate_bnbc_compliance()`, `save_model()`
  - Fiber section definitions (Concrete01/02 + Steel01/02)
  - Geometric nonlinearity (P-Delta, corotational transformation)

**Pseudocode:**
```python
from openseespy import opensees as ops
import yaml

class RCFrame:
    def __init__(self, n_stories, story_height, zone, bnbc_params):
        self.n_stories = n_stories
        self.story_height = story_height
        self.zone = zone
        self.bnbc_params = bnbc_params
        self.model = None
    
    def create_model(self):
        # Initialize OpenSeesPy model
        ops.wipe()
        ops.model('basic', '-ndm', 2, '-ndf', 3)
        # Define materials, sections, elements, constraints
        # ... (see detailed implementation tasks below)
    
    def apply_gravity_loads(self):
        # Apply floor loads + self-weight
        # Run eigenvalue analysis for period verification
    
    def validate_bnbc_compliance(self):
        # Check: base shear, story drift < 2.5%, mass distribution
    
    def save_model(self, filepath):
        # Save model to JSON or pickle for Phase 2 reuse
```

#### Step 3: Create BNBC Material Definitions (`src/modeling/materials.py`)
**Implement:**
- Concrete material (Concrete01 with softening)
- Steel rebar material (Steel01 with Bauschinger effect)
- Default properties from `config/bnbc_parameters.yaml`
- Helper functions for expected strength calculations

#### Step 4: Create BNBC Compliance Checker (`src/modeling/bnbc_compliance.py`)
**Implement:**
- Base shear calculator: V = Cs × W
- Period formula: Ta = 0.07 × h^0.75 (for RC)
- Story drift check: δmax ≤ 0.025 × story_height
- Design force checks (flexure, shear, torsion)

#### Step 5: Create 5 Building Templates
**For each heights (5, 7, 10, 12, 15 stories):**
1. Instantiate `RCFrame` with typical dimensions:
   - Column: 400mm × 400mm RC section
   - Beam: 300mm × 500mm RC section
   - Rebar: 2% for columns, 1.5% for beams
   - f'c = 28 MPa (typical Bangladesh RC)
   
2. Apply gravity loads and verify period
3. Save as template: `models/openseespy/frame_{n}s_z{zone}.json`
4. Document in notebook: `notebooks/01_data_exploration/01_validate_frame_models.ipynb`

#### Step 6: Write Unit Tests (`tests/test_rc_frame.py`)
**Test:**
- Model instantiation with valid/invalid inputs
- Gravity load application
- BNBC compliance for expected violations
- Save/load cycle integrity
- Period estimation accuracy

#### Step 7: Documentation
**Create:**
- Docstrings for all classes and methods
- `docs/phase1_structural_modeling.md` with figures
- Example usage notebook: `notebooks/01_data_exploration/01_validate_frame_models.ipynb`

---

## Key Reminders & Best Practices

### Code Quality
- Follow **PEP 8** and **Google Python style guide**
- Use **type hints** for function signatures
- Write **comprehensive docstrings** (parameter types, return types, usage examples)
- Run **black** for formatting: `black src/`
- Run **flake8** for linting: `flake8 src/`
- Run **mypy** for type checking: `mypy src/`

### Testing
- Use **pytest** for unit tests: `pytest tests/ -v`
- Target **>80% code coverage**: `pytest tests/ --cov=src --cov-report=html`
- Fixtures for reusable test data (e.g., `bnbc_config`, `sample_frame`)
- Integration tests for multi-module workflows

### Version Control
- **Commit frequently** with descriptive messages:
  ```
  Phase 1: Create RCFrame class with gravity load application
  
  - Initialize OpenSeesPy model with nodeID tagging scheme
  - Define Concrete01/Steel01 materials from BNBC defaults
  - Implement gravity load application per floor height
  - Add validation against BNBC 2020 design constraints
  ```

- **Push to GitHub** after completing each deliverable
- Use **task_plan.md** to track progress

### File Organization
- Keep models in **`src/modeling/`** (no monolithic scripts)
- Use **relative imports**: `from src.modeling import RCFrame`
- Load configs via **PyYAML**: `yaml.safe_load(open('config/...'))`
- Save results to **`results/`** (never hardcode paths)

### OpenSeesPy Tips
- **Node IDs:** `floor*100 + node_num` (e.g., floor 3, node 2 → 302)
- **Element IDs:** Column: `floor*1000 + col_num`, Beam: `floor*2000 + beam_num`
- **Fiber sections:** Use at least 8×8 fibers per cross-section for accuracy
- **Recorders:** Record displacement every 10 steps minimum; use `node()` recorder
- **Analysis:** Use **Newton–Raphson** with **NormDispIncr** test (tol = 1e-8)

### Data Integrity
- Always validate BNBC parameters are loaded correctly
- Check that self-weight + live loads total correctly (sum over all floors)
- Verify period is reasonable: T ≈ 0.07 × h^0.75 (within ±20%)
- Ensure modal properties match building classification

---

## Success Criteria for Phase 1 Completion

✅ **Code:**
- [ ] `src/modeling/rc_frame.py` implemented and tested
- [ ] 5 building templates created and saved
- [ ] 80%+ test coverage for modeling module
- [ ] All code passes black, flake8, mypy checks

✅ **Documentation:**
- [ ] Docstrings on all public functions
- [ ] Example usage in `notebooks/01_data_exploration/01_validate_frame_models.ipynb`
- [ ] Phase 1 progress documented in this task_plan.md

✅ **Verification:**
- [ ] Modal periods within expected range (T ≈ 0.07h^0.75)
- [ ] Gravity analysis converges without warnings
- [ ] BNBC compliance checks pass for valid models
- [ ] Models save/load cycle works correctly

✅ **Git:**
- [ ] All code committed with descriptive messages
- [ ] `.gitignore` preventing accidental commits of generated files
- [ ] README.md updated with Phase 1 completion status

---

## Resources & References

### Project Documentation
- **README.md** — Full research master plan, objectives, timeline
- **recreation.md** — Directory structure, dependencies, setup guide
- `.github/copilot-instructions.md` — Agent customization with full context

### BNBC 2020 References
- **docs/BuildingCodes/BNBC/** — Official Bangladesh National Building Code seismic provisions
- Key sections:
  - 3.2 — Seismic hazard and ground motion
  - 6.3 — Design response spectra
  - 8.3 — RC moment-resisting frame design

### OpenSeesPy Documentation
- **https://openseespydoc.readthedocs.io/**
- Key examples:
  - Fiber sections: `https://openseespydoc.readthedocs.io/en/latest/src/fiberLineIntegration.html`
  - Material models: `https://openseespydoc.readthedocs.io/en/latest/src/uniaxialMaterials.html`
  - Nonlinear analysis: `https://openseespydoc.readthedocs.io/en/latest/src/geomTimeSeries.html`

### ML & ML Interpretability
- **SHAP:** https://shap.readthedocs.io/ (focus on TreeExplainer for RF/XGBoost)
- **Optuna:** https://optuna.readthedocs.io/ (hyperparameter tuning)
- **TensorFlow:** https://www.tensorflow.org/api_docs (for ANN training)

---

## Contact & Support

- **Project Lead:** Research Team
- **Supervisor:** [Your Advisor]
- **Repository:** ML_RCC_Research-share (GitHub)
- **Status Updates:** Update this task_plan.md weekly

---

## Change Log

| Date | Phase | Status | Notes |
|------|-------|--------|-------|
| 2026-03-27 | Init | ✅ Complete | Infrastructure setup: dirs, config, deps, docs |
| 2026-03-27 | 1 | ⏳ Pending | Ready to begin RC frame modeling |
| TBD | 1 | ⏳ Pending | Base class implementation |
| TBD | 1 | ⏳ Pending | 5 building templates |
| TBD | 2 | ⏳ Pending | IDA analysis pipeline |
| TBD | 3 | ⏳ Pending | ML model training |
| TBD | 4 | ⏳ Pending | Fragility curves & publication |

---

**Document Version:** 1.0  
**Last Updated:** March 27, 2026, 14:30 UTC  
**Status:** Infrastructure Complete, Phase 1 Ready to Begin  
**Next Review:** After Phase 1 kickoff (within 1 week)
