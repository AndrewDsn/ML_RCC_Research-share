# Project Recreation Guide
## ML-Based Seismic Drift Research

**Last Updated:** March 27, 2026  
**Purpose:** Complete documentation for recreating this project in another directory

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Technologies & Dependencies](#technologies--dependencies)
4. [Setup Instructions](#setup-instructions)
5. [Configuration Files](#configuration-files)
6. [Project Metadata](#project-metadata)
7. [Docker Setup](#docker-setup)
8. [Next Steps](#next-steps)

---

## Project Overview

### Research Objective
Develop a Python-native machine learning surrogate model to predict peak inter-story drift ratio (PIDR) of reinforced concrete (RC) moment frame buildings designed under Bangladesh National Building Code (BNBC) 2020. The model will be trained on OpenSeesPy incremental dynamic analysis (IDA) data across all four seismic zones of Bangladesh.

### Key Features
- **Structural Modeling:** Parametric RC SMRF models (5-15 stories) compliant with BNBC 2020
- **Analysis Method:** Incremental Dynamic Analysis (IDA) using OpenSeesPy
- **ML Models:** Linear Regression, Random Forest, XGBoost, TensorFlow/ANN
- **Interpretability:** SHAP analysis for feature importance
- **Code Compliance:** BNBC 2020 seismic zone parameters and design procedures
- **Reproducibility:** Fully open-source, containerized environment

---

## Directory Structure

```
ML-Based_Seismic_Drift_Research/
├── LICENSE                           # MIT License
├── README.md                         # Research master plan
├── task_plan.md                      # Task planning & progress tracking
├── recreation.md                     # THIS FILE
│
├── docs/                             # Documentation and building codes
│   ├── BuildingCodes/
│   │   ├── BNBC/                     # Bangladesh National Building Code
│   │   └── US/
│   │       └── ASCE-7-22/            # ASCE 7-22 seismic design
│   └── NL-Codes/
│       └── FEMA-P-58/                # FEMA fragility curves reference
│
├── project-docs/
│   └── dev-info.md                   # Development setup guide
│
└── project/                          # Main Python project
    ├── README.md                     # Project description
    ├── pyproject.toml                # Project metadata and build config
    ├── requirements.txt              # Python dependencies
    ├── Dockerfile                    # Docker containerization
    ├── docker-compose.yml            # Multi-container orchestration
    ├── .gitignore                    # Git ignore rules
    │
    ├── config/                       # Configuration files
    │   ├── bnbc_parameters.yaml      # BNBC 2020 seismic parameters
    │   └── analysis_config.yaml      # IDA and ML training configuration
    │
    ├── data/                         # Data directory (git-ignored)
    │   ├── raw/                      # Original seismic records and building data
    │   ├── processed/                # Cleaned, normalized datasets
    │   └── metadata/                 # Data schemas and descriptions
    │
    ├── models/                       # Trained models and structures (git-ignored)
    │   ├── openseespy/               # OpenSeesPy structural model templates
    │   ├── ml_models/                # Trained ML models (LR, RF, XGBoost, ANN)
    │   └── checkpoints/              # Training checkpoints and best models
    │
    ├── notebooks/                    # Jupyter notebooks for development
    │   ├── 01_data_exploration/      # EDA and data understanding
    │   ├── 02_ida_analysis/          # IDA pipeline and results
    │   ├── 03_ml_training/           # Model training and evaluation
    │   └── 04_results_analysis/      # Final results and visualization
    │
    ├── results/                      # Generated outputs (git-ignored)
    │   ├── figures/                  # Plots, fragility curves, visualizations
    │   ├── reports/                  # Analysis reports and summaries
    │   └── tables/                   # Result tables in CSV/Excel format
    │
    ├── src/                          # Main Python source code
    │   ├── __init__.py
    │   ├── modeling/                 # OpenSeesPy wrapper and model functions
    │   │   └── __init__.py
    │   ├── ida/                      # IDA analysis pipeline
    │   │   └── __init__.py
    │   ├── ml/                       # ML model training and evaluation
    │   │   └── __init__.py
    │   ├── utils/                    # Helper and utility functions
    │   │   └── __init__.py
    │   └── visualization/            # Plotting and visualization utilities
    │       └── __init__.py
    │
    └── tests/                        # Unit and integration tests
        └── __init__.py
```

---

## Technologies & Dependencies

### Core Scientific Stack
- **NumPy** (≥1.24.0) - Numerical computing
- **SciPy** (≥1.10.0) - Scientific computing and algorithms
- **SymPy** (≥1.12) - Symbolic mathematics
- **scikit-spatial** (≥8.0.0) - Spatial data structures

### Machine Learning
- **scikit-learn** (≥1.3.0) - Classical ML algorithms
- **XGBoost** (≥2.0.0) - Gradient boosting
- **LightGBM** (≥4.0.0) - Fast gradient boosting
- **TensorFlow** (≥2.13.0, <3.0.0) - Deep learning
- **Keras** (≥2.13.0) - Neural networks
- **SHAP** (≥0.42.0) - Model interpretability

### Structural Analysis
- **OpenSeesPy** (≥3.5.0) - Python interface to OpenSees FEA framework

### Data Processing
- **pandas** (≥2.0.0) - Data manipulation and analysis
- **h5py** (≥3.9.0) - HDF5 file handling
- **openpyxl** (≥3.1.0) - Excel file support
- **PyYAML** (≥6.0) - YAML configuration parsing

### Visualization
- **Matplotlib** (≥3.7.0) - 2D plotting
- **Seaborn** (≥0.12.0) - Statistical visualization
- **Plotly** (≥5.14.0) - Interactive visualizations
- **Folium** (≥0.14.0) - Geographic maps (optional)

### Development & Testing
- **Jupyter** / **JupyterLab** (≥4.0.0) - Interactive notebooks
- **IPython** (≥8.10.0) - Enhanced Python REPL
- **pytest** (≥7.4.0) - Testing framework
- **pytest-cov** (≥4.1.0) - Coverage reporting
- **black** (≥23.0.0) - Code formatting
- **flake8** (≥6.0.0) - Code linting
- **mypy** (≥1.4.0) - Static type checking
- **pylint** (≥2.17.0) - Code analysis

### Experiment & Model Tracking
- **MLflow** (≥2.0.0) - ML experiment tracking
- **Optuna** (≥3.0.0) - Hyperparameter optimization
- **joblib** (≥1.3.0) - Parallel processing

### Utilities
- **dask** (≥2023.9.0) - Distributed computing
- **tqdm** (≥4.66.0) - Progress bars
- **Sphinx** (≥7.0.0) - Documentation building

---

## Setup Instructions

### 1. Clone or Copy the Repository

```bash
# If starting fresh:
git clone <repository-url> ML-Based_Seismic_Drift_Research
cd ML-Based_Seismic_Drift_Research/project
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3.9+ -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

**Dependencies Installation Time:** ~5-10 minutes (depends on system and internet speed)

### 4. Verify Installation

```bash
# Test Python imports
python -c "import numpy, scipy, pandas, scikit-learn, xgboost, tensorflow, openseespy; print('All imports successful!')"

# Test Jupyter
jupyter --version

# Run tests (if any exist)
pytest tests/ -v
```

### 5. Optional: Docker Setup

```bash
# Build and run with Docker Compose
cd ..  # Move to repository root
docker-compose up --build

# Access Jupyter at: http://localhost:8888
# Token: seismic-drift
```

---

## Configuration Files

### 1. `config/bnbc_parameters.yaml`

Contains BNBC 2020 seismic zone parameters:
- **Zone I:** PGA = 0.05g (Very low hazard)
- **Zone II:** PGA = 0.10g (Low hazard)
- **Zone III:** PGA = 0.15g (Moderate hazard - Dhaka region)
- **Zone IV:** PGA = 0.20g (High hazard - Chittagong region)

Each zone includes:
- Base shear coefficients for RC buildings
- Site class defaults
- Importance factors
- Design spectra

**Usage:** Import in structural modeling code to load zone-specific parameters

### 2. `config/analysis_config.yaml`

Contains IDA and ML pipeline configuration:

**IDA Parameters:**
- Intensity Measure: Spectral Acceleration (Sa) at T = 0.5s
- Intensity Range: 0.05g to 1.50g, incremented by 0.10g
- Time Step: 0.005 seconds
- Convergence Tolerance: 1e-8

**ML Training Parameters:**
- Train/Test Split: 80/20
- Validation Split: 15%
- Feature Scaler: StandardScaler
- Model hyperparameters for Random Forest (200 estimators, max_depth=20)

**Usage:** Load configuration in IDA and training scripts using PyYAML

### 3. `pyproject.toml`

Project metadata:
```toml
[project]
name = "seismic-drift-research"
version = "0.1.0"
description = "ML-Based Seismic Drift Prediction of RC Buildings Under BNBC 2020"
requires-python = ">=3.9"
```

Includes optional dependency groups:
- `dev` - Development tools (pytest, black, flake8, mypy)
- `docs` - Documentation (Sphinx)
- `gpu` - GPU support for TensorFlow

---

## Project Metadata

### Repository Information
- **Repository:** ML-Based_Seismic_Drift_Research
- **Owner:** scientificpagala-dev
- **License:** MIT
- **Python Version:** ≥3.9
- **Current Version:** 0.1.0

### Authors & Contact
- Research Team
- Email: research@example.com

### Referenced Standards
- **BNBC 2020** - Bangladesh National Building Code (Seismic Provisions)
- **ASCE 7-22** - Seismic Design of Buildings (US Standard)
- **FEMA P-58** - Seismic Performance Assessment of Buildings

---

## Docker Setup

### Why Docker?
- Ensures consistent environment across different machines
- Includes pre-configured Jupyter Lab, PostgreSQL, and MLflow
- Eliminates "works on my machine" problems
- Suitable for reproducible research papers

### Key Services in `docker-compose.yml`

**1. Jupyter Service**
- **Port:** 8888
- **Token:** seismic-drift
- **Base Image:** python:3.11-slim
- **Volumes:** data, notebooks, models, results, src, config
- **Default Command:** Starts Jupyter Lab

**2. PostgreSQL (Optional)**
- **Port:** 5432
- **Database:** mlflow
- **Username:** mlflow
- **Password:** mlflow_password
- **Usage:** Backend for MLflow experiment tracking

**3. MLflow (Optional)**
- **Port:** 5000
- **Purpose:** Track experiments, log models, and manage artifacts
- **Configuration:** Connected to PostgreSQL for persistence

### Running with Docker

```bash
# Build and start services
docker-compose up --build

# Access Jupyter Lab
# http://localhost:8888
# Token: seismic-drift

# Access MLflow UI
# http://localhost:5000
```

### Dockerfile Details

- **Base Image:** `python:3.11-slim`
- **System Dependencies:** build-essential, git, cmake, gfortran, BLAS, LAPACK
- **Working Directory:** `/app`
- **Volumes:** `/app/data`, `/app/results`, `/app/models`
- **Environment Variables:**
  - PYTHONUNBUFFERED=1 (Unbuffered Python output)
  - JUPYTER_ENABLE_LAB=yes (Enable Jupyter Lab)

---

## Next Steps

### Phase 1: Structural Modeling (Ready to Begin)
1. Create OpenSeesPy model base class in `src/modeling/`
2. Load BNBC parameters from config
3. Define parametric functions for 5, 7, 10, 12, 15-story SMRF buildings
4. Validate models against BNBC design procedures
5. Test with gravity + lateral loads

### Phase 2: IDA Analysis & Data Generation (Awaiting Phase 1)
1. Prepare/acquire ground motion records for 4 seismic zones
2. Implement ground motion scaling per BNBC
3. Create IDA pipeline in `src/ida/`
4. Run IDA for each building-zone combination
5. Extract PIDR, accelerations, velocities
6. Compile into structured dataset (CSV, HDF5)

### Phase 3: Machine Learning Pipeline (Awaiting Phase 2)
1. Prepare training dataset with feature engineering
2. Train models: LR, RF, XGBoost, ANN
3. Perform hyperparameter optimization with Optuna
4. Evaluate model performance (R², RMSE, MAE)
5. SHAP analysis for feature importance

### Phase 4: Fragility Curves & Results (Awaiting Phase 3)
1. Define IO, LS, CP performance levels
2. Generate seismic fragility curves
3. Create publication-quality visualizations
4. Generate analysis reports

---

## Quick Commands Reference

```bash
# Activate virtual environment
source project/.venv/bin/activate

# Install/update dependencies
pip install -r project/requirements.txt

# Start Jupyter Lab (local development)
jupyter lab --notebook-dir=project/notebooks

# Run tests
pytest project/tests/ -v --cov=src

# Format code with black
black project/src project/tests

# Check code style
flake8 project/src project/tests

# Type checking
mypy project/src

# Docker setup
docker-compose up --build

# View available commands in task_plan.md
cat task_plan.md
```

---

## Checklist for Recreation

- [ ] Clone/copy repository to new location
- [ ] Create Python virtual environment (3.9+)
- [ ] Install dependencies from requirements.txt
- [ ] Verify all imports work
- [ ] Review `project-docs/dev-info.md` for detailed setup
- [ ] Review `config/bnbc_parameters.yaml` for seismic zones
- [ ] Review `config/analysis_config.yaml` for IDA/ML parameters
- [ ] (Optional) Build Docker image and start services
- [ ] Review `task_plan.md` for project phases and progress
- [ ] Begin Phase 1: Structural Modeling

---

## Additional Resources

- **README.md:** Full research methodology and objectives
- **task_plan.md:** Detailed task breakdown and progress tracking
- **project-docs/dev-info.md:** Development environment guide
- **docs/BuildingCodes/:** Reference building codes and standards

---

**Document Version:** 1.0  
**Last Updated:** March 27, 2026  
**Status:** Project infrastructure setup complete, ready for Phase 1 implementation
