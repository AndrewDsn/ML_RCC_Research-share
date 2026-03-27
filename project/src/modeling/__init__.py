"""OpenSeesPy Structural Modeling Module

This module provides classes and functions for creating parametric RC 
moment-resisting frame models (SMRF) in OpenSeesPy, compliant with 
BNBC 2020 seismic design provisions.

Key Classes:
- RCFrame: Base class for RC multi-story frames
- RCBeam, RCColumn: Individual structural elements
- BNBCCompliance: BNBC 2020 design verification

Usage:
    from src.modeling import RCFrame
    import yaml
    
    with open('config/bnbc_parameters.yaml') as f:
        bnbc = yaml.safe_load(f)
    
    frame = RCFrame(n_stories=10, story_height=3.5, zone=3, bnbc_params=bnbc)
    frame.apply_gravity_loads()
    frame.validate_bnbc_compliance()
    frame.save_model('models/openseespy/frame_10s_z3.json')
"""

__all__ = []
