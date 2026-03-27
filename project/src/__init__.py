"""
Seismic Drift Research - ML-Based Prediction of RC Buildings Under BNBC 2020

A comprehensive Python framework for:
- Structural modeling of RC moment-resisting frames in OpenSeesPy
- Incremental Dynamic Analysis (IDA) for seismic response evaluation
- Machine Learning surrogate models for peak inter-story drift prediction
- Seismic fragility curve generation
- SHAP-based feature importance analysis

Project Structure:
- src.modeling: OpenSeesPy structural models and BNBC compliance
- src.ida: IDA analysis pipeline and ground motion processing
- src.ml: ML model training, evaluation, and hyperparameter optimization
- src.utils: Helper functions and utilities
- src.visualization: Plotting and visualization routines
"""

__version__ = "0.1.0"
__author__ = "Research Team"
__license__ = "MIT"

# Optional: expose commonly used imports
try:
    from . import modeling, ida, ml, utils, visualization
except ImportError as e:
    print(f"Warning: Could not import all submodules: {e}")
