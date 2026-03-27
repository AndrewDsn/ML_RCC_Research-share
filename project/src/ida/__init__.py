"""Incremental Dynamic Analysis (IDA) Module

This module implements the IDA pipeline for evaluating seismic response of
RC buildings under scaled ground motions.

Key Classes:
- IDAAnalysis: Main IDA analysis controller
- GroundMotionScaler: Scales ground motions to target intensity measures
- IDARecorder: Collects and processes IDA results

Key Functions:
- run_ida: Execute IDA for a building-ground motion pair
- extract_pidr: Extract peak inter-story drift ratios from analysis
- plot_ida_curve: Visualize IDA curves

Usage:
    from src.ida import IDAAnalysis
    
    ida = IDAAnalysis(
        model=frame,
        gm_record='data/raw/gm_z3_001.csv',
        intensity_range=(0.05, 1.50),
        step=0.10
    )
    pidr_curve = ida.run()
    ida.plot_ida_curve()
"""

__all__ = []
