# Analysis Method Plan
## ASCE 41-23 & FEMA P-58 Compliant Seismic Analysis Framework

**Date Created:** March 28, 2026  
**Last Updated:** March 28, 2026  
**Status:** Integrated in src/analysis/ module  
**Reference Standards:**
- ASCE 7-22 (Seismic Design of Buildings)
- ASCE 41-23 (Seismic Evaluation & Retrofit)
- FEMA P-58 (Performance-Based Seismic Assessment)

---

## Table of Contents

1. [Analysis Framework Overview](#1-analysis-framework-overview)
2. [Phase-by-Phase Integration](#2-phase-by-phase-integration)
3. [Method 1: Response Spectrum Analysis (RSA)](#3-method-1-response-spectrum-analysis-rsa)
4. [Method 2: Time History Analysis (THA)](#4-method-2-time-history-analysis-tha)
5. [Method 3: Pushover Analysis](#5-method-3-pushover-analysis)
6. [Method 4: P-Delta Effects & Stability](#6-method-4-p-delta-effects--stability)
7. [Method 5: Plastic Hinge Analysis](#7-method-5-plastic-hinge-analysis)
8. [Method 6: Combined Multi-Method Analysis](#8-method-6-combined-multi-method-analysis)
9. [Configuration File Specifications](#9-configuration-file-specifications)
10. [Uncertainty Quantification & Sensitivity](#10-uncertainty-quantification--sensitivity)

---

## 1. Analysis Framework Overview

### 1.1 Six Integrated Analysis Methods

The project employs **six synergistic seismic analysis methods** integrated within the Phase 2 data generation pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: IDA & Seismic Response Data Generation            │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─ Design-Level Elastic Analysis ──────────────────────────────┐
│  [1] Response Spectrum Analysis (RSA)                        │
│      → Modal extraction → Force distribution → Design checks │
└──────────────────────────────────────────────────────────────┘
         ↓
┌─ Nonlinear Dynamic Response (PRIMARY) ────────────────────────┐
│  [2] Time History Analysis (THA) + Geometric Nonlinearity    │
│      → [4] P-Delta Effects: stability index θ                │
│      → [5] Plastic Hinge Formation: damage tracking          │
│      → [6] Combined: ensemble of methods                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Output: Peak responses (PIDR, PGA, Hinge rotations)  │  │
│  │         Performance level assessment                  │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         ↓
┌─ Pushover (Capacity-Based) ──────────────────────────────────┐
│  [3] Static Nonlinear Pushover                               │
│      → [4] P-Delta included in analysis                      │
│      → Load distribution: inverted triangle (1st mode)       │
│      → Performance point identification (CSM)                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Output: Capacity curve, ductility, overstrength       │  │
│  │         Comparison with THA predictions               │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
         ↓
┌─ Performance Assessment ─────────────────────────────────────┐
│  [5] Plastic Hinge Analysis → FEMA 356 Performance Levels   │
│      → IO (Immediate Occupancy): δ < 1%, minimal damage      │
│      → LS (Life Safety): δ < 2.5%, some damage but stable    │
│      → CP (Collapse Prevention): δ < 4%, near collapse       │
└──────────────────────────────────────────────────────────────┘
         ↓
       DATA: 5,000–10,000 IDA records for ML training
```

### 1.2 Method Classification

| Method | Category | Time Domain | Linearity | Output |
|---|---|---|---|---|
| **RSA** | Elastic design | Frequency | Linear | Design forces, periods, modes |
| **THA** | Dynamic (Primary) | Time | Nonlinear | PIDR, peak responses, hysteresis |
| **Pushover** | Capacity-based | Pseudo-static | Nonlinear | Capacity curve, overdrive, ductility |
| **P-Delta** | Geometric effects | Integrated | Nonlinear | Stability index θ, geometric stiffness |
| **Plastic Hinge** | Damage tracking | Time/Step | Nonlinear | Hinge rotations, damage index, performance level |
| **Combined** | Ensemble/Multi-stripe | Multiple | Nonlinear | Ensemble responses, uncertainty bounds |

---

## 2. Phase-by-Phase Integration

### Phase 2 Data Generation Workflow

```python
for building_id in [frame_5s, frame_7s, ..., frame_15s]:
    for zone in [Zone_I, Zone_II, Zone_III, Zone_IV]:
        
        # Step 1: Design-Level Elastic Analysis
        rsa = ResponseSpectrumAnalysis(building, zone)
        modal_props = rsa.extract_modal_properties()  # T1, φ1, M_eff
        design_forces = rsa.distribute_forces()       # story shears, moments
        
        # Step 2: Load Ground Motion Records
        for gm_id in range(1, 501):  # 500 ground motions per zone
            gm = load_ground_motion(zone, gm_id)
            
            # Intensity Scaling Loop (Multi-Stripe Analysis)
            for intensity_level in [0.05, 0.15, 0.25, ..., 1.50] g:
                
                # Scale GM to target intensity
                gm_scaled = scale_to_intensity(gm, intensity_level)
                
                # Step 3: Time History Analysis (THA) with P-Delta
                tha = TimeHistoryAnalysis(building, gm_scaled)
                
                # Integrated within THA:
                # - Newmark-β integration (dt=0.005 s, 50 sec duration)
                # - P-Delta effects computed each step (θ tracking)
                # - Plastic hinge detector running simultaneously
                
                peak_responses = tha.run()  # PIDR, PGA, velocity
                
                # Step 4: Extract Plastic Hinge Data
                hinge_analysis = PlasticHingeAnalysis(tha.hinge_states)
                performance_level = hinge_analysis.assess_performance()
                damage_index = hinge_analysis.compute_damage(park_ang=True)
                
                # Step 5: Optional Pushover Comparison
                pushover = PushoverAnalysis(building, first_mode_shape=rsa.φ1)
                capacity_curve = pushover.run()
                performance_point = pushover.csc_method(hinge_analysis.pidr)
                
                # Step 6: Record Multi-Method Result
                result = {
                    'building_id': building_id,
                    'zone': zone,
                    'gm_id': gm_id,
                    'sa_intensity': intensity_level,
                    'pidr': peak_responses['pidr'],
                    'pga': peak_responses['pga'],
                    'performance_level': performance_level,
                    'damage_index': damage_index,
                    'pdelta_theta_max': tha.stability_index_max,
                    # Optional:
                    'pushover_capacity': capacity_curve.base_shear_max,
                    'ductility': capacity_curve.ductility,
                    'rsa_design_force': design_forces['base_shear']
                }
                
                # Append to dataset
                ida_results.append(result)

# Final dataset: ida_results.csv with 5,000–10,000 records
```

---

## 3. Method 1: Response Spectrum Analysis (RSA)

### 3.1 Purpose & Application

**Use:** Design-level elastic seismic analysis per BNBC 2020 Section 3.2 and ASCE 7-22 Chapter 11.

**Deliverables:**
1. Fundamental period T₁ (validation of empirical formulas)
2. Modal properties (participation factors, effective mass)
3. Design base shear (code-level estimate)
4. Story shear & moment distributions
5. Design-level drift profiles
6. Comparison with THA results

### 3.2 Implementation Specification

#### Modal Analysis

```
Eigenvalue Problem:
  [K - ω²M] Φ = 0

where:
  K = global stiffness matrix (from OpenSees model)
  M = mass matrix (lumped diagonal per floor)
  ω_i = circular frequency of mode i
  Φ_i = eigenvector (mode shape)

Number of Modes: Extract 20 modes (capture 90%+ of mass)

Implementation (OpenSeesPy):
  ops.modal_analysis(20)  # Extract first 20 eigenmodes
  
Compute for each mode:
  - T_i = 2π / ω_i (period)
  - Γ_i = (Σ M_j × Φ_ij) / (Σ M_j × Φ²_ij)  (participation factor)
  - M_eff_i = Γ²_i × (Σ M_j × Φ²_ij)  (effective modal mass)
  - Compute % mass participation: Σ M_eff / Σ M_total
```

#### Design Response Spectrum

**BNBC 2020 Design Spectrum:**

```
Spectral Acceleration S_a(T) depends on:
  - Seismic Zone: Z = 0.12, 0.18, 0.24, 0.36
  - Site Class: A, B, C, D, E (default: C for Bangladesh)
  - Importance Factor: I = 1.0–1.25
  - Damping: ζ = 5% (standard for RC)

BNBC 2020 Spectrum Formula (5% damping):
  
  For T < T_c (short period):
    S_a(T) = Z × I × [0.044 × (1 + (T/T_s)²)] × g
  
  For T_c ≤ T < T_l (intermediate):
    S_a(T) = Z × I × 0.044 × g  (plateau)
  
  For T ≥ T_l (long period):
    S_a(T) = Z × I × (0.044 × T_l / T) × g

where:
  T_s = short period corner (depends on site class)
  T_c = code period corner (~0.5 × T_l for Zone III)
  T_l = long period corner (~2–3 sec for Bangladesh soil)
  g = 9.81 m/s²

Key Constants for Zone III (f_c' = 30 MPa):
  Z = 0.24 (seismic coefficient)
  T_l ≈ 2.5 seconds (typical)
  S_a(T=0.5s) ≈ 0.024 × g ≈ 0.24 m/s²
```

#### Modal Force Distribution

```
Lateral force at floor i in mode n:
  F_i,n = (Γ_n × S_a(T_n)) × (M_i × Φ_i,n)

Combine all modes using CQC rule:
  F_i,combined = √(Σ_n Σ_m ρ_nm × F_i,n × F_i,m)

where:
  ρ_nm = correlation coefficient between modes n and m
  = (8 × ζ²) / [(1 - (ω_n/ω_m)²)² + 16 × ζ² × (ω_n/ω_m)]

Typically: ρ_nm ≈ 0.3–0.9 for adjacent modes
```

#### Normalization & Base Shear Check

```
Total Base Shear from RSA:
  V_RSA = Σ_n Γ_n × S_a(T_n) × M_eff_n

Compare with BNBC Code Minimum:
  V_min = 0.044 × Z × I × W / R
  
Adjust if V_RSA < V_min:
  V_design = max(V_RSA, V_min)  (apply 85% rule adjustment per ASCE 7)
```

### 3.3 Output & Validation

| Output | Symbol | Value (Example: 10-story SMRF, Zone III) |
|---|---|---|
| Fundamental Period | T₁ | ~0.85 sec |
| Mode 1 Participation | Γ₁ | ~0.88 (88% mass) |
| Design Spectrum @ T₁ | S_a(T₁) | ~0.20 m/s² |
| Design Base Shear | V_base | ~0.20 W (20% of weight) |
| Design Story Drift | δ_design | ~1.5–2.0% (code limit 2.5%) |

### 3.4 Configuration (analysis_config.yaml)

```yaml
response_spectrum_analysis:
  enabled: true
  modal_analysis:
    n_modes: 20
    cutoff_mass_ratio: 0.90       # minimum 90% mass participation
    eigenvalue_solver: 'full'      # or 'band'
    
  design_spectrum:
    standard: 'BNBC 2020'          # Bangladesh code
    damping_ratio: 0.05            # 5% damping
    site_class: 'C'                # Default soil class
    
  combination_method: 'CQC'        # Complete Quadratic Combination
  drift_limit: 0.025               # 2.5% (code-level check)
  
  output:
    save_modal_properties: true
    save_design_forces: true
    plot_response_spectrum: true
```

---

## 4. Method 2: Time History Analysis (THA)

### 4.1 Purpose & Application

**Use:** Primary seismic analysis method for IDA data generation. Produces peak responses (PIDR, PGA) and damage measures for ML training.

**Key Features:**
- Nonlinear dynamic analysis with material inelasticity
- Incremental ground motion scaling (multi-stripe IDA)
- Integrated P-Delta tracking
- Plastic hinge monitoring
- Hysteresis energy dissipation

### 4.2 Ground Motion Scaling

#### Intensity Measure Selection

```
Primary IM: Spectral Acceleration S_a(T₁)
  - Compute fundamental period T₁ from modal analysis
  - Use S_a(T₁) as intensity measure for scaling
  - Rationale: Spectral acceleration at building's period is most relevant for response

Scaling Procedure:
  1. Load original ground motion acceleration time series: a_gm(t)
  2. Compute its response spectrum: Sa_gm(T)
  3. Extract target intensity: Sa_gm(T₁) = current spectrum value
  4. Compute scale factor: λ = Sa_target / Sa_gm(T₁)
  5. Scaled acceleration: a_scaled(t) = λ × a_gm(t)
  6. Verify: compute response spectrum of scaled motion, check Sa(T₁) ≈ Sa_target

Multi-Stripe Scheme:
  Sa_target ∈ [0.05, 0.10, 0.15, 0.20, 0.25, ..., 1.50] g
  Total: 16 intensity levels per ground motion
  For 500 GMs × 16 levels × 5 buildings × 4 zones = 160,000 analyses (reduced to 40,000 for Phase 2)
```

#### Ground Motion Database

```
Source: PEER NGA-West2 Database (or equivalent for Bangladesh)

Selection Criteria per BNBC 2020 Chapter 3.3:
  - At least 3 ground motion records per intensity level
  - Magnitude: 4.5 ≤ M ≤ 7.5
  - Distance: r < 30 km
  - Vs30 > 300 m/s (Site Class C equivalent)
  - Orientation: Use GMROI component (RotD50 preferred)

Simplified Approach (Current):
  - Use generic GM set (15–30 records representative of Bangladesh seismicity)
  - Scale to all 16 intensity levels
  - Apply to all buildings/zones (conservative assumption)
```

### 4.3 Time Integration Scheme

#### Newmark-β Method

```
Recurrence Relations (Newmark-β integration):
  
  Displacement increment:
    Δu_n+1 = Δt × v_n + Δt²/2 × [(1 - 2β) × a_n + 2β × a_n+1]
  
  Velocity increment:
    Δv_n+1 = Δt × [(1 - γ) × a_n + γ × a_n+1]

Parameters (Numerically Stable):
  β = 0.25 (Newmark's constant acceleration)
  γ = 0.50 (average acceleration)
  
Properties:
  - Unconditionally stable (A-stable)
  - 2nd-order accurate
  - No spurious damping
  - Suitable for nonlinear dynamics

Time Step: Δt = 0.005 s (200 Hz sampling)
  - Captures high frequencies (up to 100 Hz for ground motions)
  - Resolves plastic hinge dynamics
  - Computational cost: ~10,000 steps × 50 sec = 500,000 force evaluations per run
  
Duration: 50 seconds (includes P- and S-waves + coda)
```

#### Rayleigh Damping

```
Proportional Damping Model:
  C = α × M + β × K
  
Modal Damping:
  2 × ζ_n × M_n × ω_n = α × M_n + β × K_n
  
Solve for α and β using two target modes (typically n=1, 2):
  α = (2 × ζ × ω_1 × ω_2) / (ω_1 + ω_2)
  β = 2 × ζ / (ω_1 + ω_2)
  
where ζ = 0.05 (5% damping, typical for RC structures)

Verification:
  ζ_n = (α/2/ω_n) + (β × ω_n / 2)
  Check ζ_n ≈ 0.05 for modes 1–5
  Avoid excessive damping at high frequencies
```

### 4.4 Nonlinear Solver

#### Convergence Criteria

```
Newton-Raphson Iteration (each time step):
  
  Unbalanced Force:
    ΔR = F_ext - F_int(u)
  
  Correction:
    Δu = [K_tang]^(-1) × ΔR
  
  Update:
    u_i+1 = u_i + Δu
    Repeat until ||ΔR|| < tolerance

Tolerance:
  Displacement tolerance: 1e-8 × characteristic length
  Force tolerance: 1e-8 × characteristic load
  Maximum iterations: 100
  
Failure Handling:
  - If convergence fails: reduce time step (adaptive)
  - Record warning but continue analysis
  - Flag timestep in output for post-processing review
```

### 4.5 Output: Peak Inter-Story Drift Ratio (PIDR)

#### Definition & Computation

```
Story Drift:
  δ_i = |u_i+1 - u_i|  (lateral displacement difference over height h_i)

Drift Ratio:
  DR_i = δ_i / h_i

Peak Inter-Story Drift Ratio (PIDR):
  PIDR = max(DR_i) over all stories and all time steps
  
Example:
  - Story 5: δ = 85 mm, h = 3500 mm
  - DR_5 = 85 / 3500 = 0.0243 = 2.43%
  - If this is maximum over entire building & time history
  - PIDR = 2.43%
```

#### Performance Limits (FEMA/ASCE 41-23)

| Performance Level | PIDR Threshold | Hinge Rotation | Structural Status |
|---|---|---|---|
| **IO** (Immediate Occupancy) | < 1.0% | < 0.5% chord rot. | Elastic, minimal damage |
| **LS** (Life Safety) | < 2.5% | < 2.0% chord rot. | Some damage, repairable |
| **CP** (Collapse Prevention) | < 4.0% | < 3.0% chord rot. | Severe damage, near collapse |
| **Collapse** | > 4.0% | > 3.0% chord rot. | Building unsafe |

### 4.6 Configuration (analysis_config.yaml)

```yaml
time_history_analysis:
  enabled: true
  
  ground_motion:
    database: 'PEER_NGA_West2'
    n_records: 500                 # or 30 for preliminary
    scaling_method: 'Sa_intensity' # Scale to Sa(T1)
    intensity_levels: [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
                       0.45, 0.50, 0.60, 0.75, 0.90, 1.20, 1.35, 1.50]
  
  integration:
    method: 'Newmark'
    beta: 0.25                     # Constant acceleration
    gamma: 0.50                    # Average acceleration
    time_step: 0.005               # seconds (200 Hz)
    duration: 50.0                 # seconds
    
  damping:
    type: 'Rayleigh'
    damping_ratio: 0.05            # 5% in modes 1 & 2
    
  solver:
    tolerance_disp: 1.0e-8
    tolerance_force: 1.0e-8
    max_iterations: 100
    adaptive_time_step: false      # or true for difficult cases
    
  outputs:
    save_floor_displacements: true
    save_element_forces: true
    save_hinge_states: true        # For plastic hinge analysis
    compute_pidr: true
    compute_pga_pv: true           # Peak ground accel/velocity
```

---

## 5. Method 3: Pushover Analysis

### 5.1 Purpose & Application

**Use:** Capacity-based evaluation of structural ductility and overstrength. Provides alternative verification of plastic hinge locations vs. THA predictions.

**Key Outputs:**
- Capacity curve (base shear vs. roof displacement)
- Yield displacement, plastic displacement, ductility
- Overstrength factor (actual/expected yield)
- Performance point (Capacity Spectrum Method)

### 5.2 Loading Pattern

#### Inverted Triangle (First Mode)

```
Lateral Force Distribution:
  F_i = W_i × φ_i,1 / (Σ W_j × φ_j,1)

from Modal Analysis:
  Sum modal forces = base shear
  Proportional to first mode shape φ₁ and floor mass
  
Example (5-story building, uniform floors):
  Mode shape φ₁: [0.10, 0.22, 0.32, 0.42, 0.50] (normalized)
  Floor masses: [M, M, M, M, M]
  
  Lateral forces at each floor (relative):
    [0.10M, 0.22M, 0.32M, 0.42M, 0.50M]
  Applied incrementally until:
    a) Global instability (θ ≥ 0.20)
    b) First story mechanism forms
    c) Roof displacement reaches 8% story height
```

#### Load Control vs. Displacement Control

```
Phase 1: Load Control (Small Displacement)
  Increment lateral force by small steps
  Measure base shear and roof displacement
  Continue until P-Delta effects become significant (θ > 0.05)

Phase 2: Displacement Control (Post-Yield)
  Switch to displacement control (roof displacement as control parameter)
  Reduces convergence issues in softening region
  Continue until convergence fails or force drops to near zero
  
Continuation: Bifurcation following
  If P-Delta dominates, switch to "branch-following" method
  Track limit point on post-yield softening curve
```

### 5.3 Capacity Spectrum Method (CSM)

#### Performance Point Identification

```
Capacity Curve:
  Plot base shear V vs. spectral displacement S_d
  where S_d = roof displacement × (T₁ / 2π)² / g
  
  Normalize by building mass:
    S_a = V / W  (spectral acceleration, "strength")
    S_d = roof_disp × (proportional factor)  (spectral displacement)
  
1. Equivalent Single-Degree-of-Freedom (SDOF) System:
    V_SDOF = V building / Γ₁
    where Γ₁ = (Σ M_j × φ₁,j)² / (Σ M_j × φ²₁,j)
    
2. Demand Spectrum:
    From RSA with reduced damping ζ_eff = ζ_elastic + contribution from inelasticity
    Iterate: assume displacement, compute ductility, update damping, check convergence
    
3. Intersection:
    Find crossing of demand curve and capacity curve (operating point)
    This is the performance point
    
4. Extract Drift:
    From performance point displacement, back-calculate building roof drift
    Estimate story drifts assuming plastic hinge locations
    Compare with THA results for validation
```

### 5.4 Configuration (analysis_config.yaml)

```yaml
pushover_analysis:
  enabled: true
  
  load_pattern:
    type: 'inverted_triangle'      # or 'uniform', 'first_mode'
    mode: 1                         # Use mode shape from modal analysis
    
  load_control:
    initial_step: 0.01 × W          # Small force increment
    max_steps: 500
    
  displacement_control:
    target_displacement: 0.08 × total_height
    increment: 0.001 × target
    
  p_delta:
    enabled: true                   # Include in analysis
    theta_limit: 0.20               # Stop if θ > 0.20
    
  performance_point:
    method: 'CSM'                   # Capacity Spectrum Method
    damping_adjustment: true        # Adjust for inelasticity
    
  output:
    save_capacity_curve: true
    plot_pushover_result: true
    save_performance_point: true
```

---

## 6. Method 4: P-Delta Effects & Stability

### 6.1 Importance & Triggering

**When P-Delta Matters:**
- Tall buildings (H > 20 m) with lateral displacements
- Soft-story frames (weak first story)
- Flexible structures (T > 1.0 sec)
- High seismic demand leading to large drifts (PIDR > 2%)

**Stability Index (θ):**
```
θ = (P_story × Δ) / (V_story × h_story)

Interpretation:
  θ < 0.05:  P-Delta negligible (< 5% moment increase)
  0.05 < θ < 0.10:  Include in analysis
  0.10 < θ < 0.20:  Major effects, explicit computation required
  θ > 0.20:  Story instability, building may collapse

BNBC 2020 Limit: θ_max = 0.10 (design requirement)
```

### 6.2 Implementation in OpenSees

#### Geometric Transformation

```
OpenSeesPy Syntax:
  ops.geomTransf('PDelta', id)  # Enables corotational P-Delta
  ops.element('nonlinearBeamColumn', eid, iNode, jNode,
              npf, sectTag, transfTag, ...)
              
Effect:
  - Computes element rotation & curvature
  - Updates element stiffness for axial force P
  - Geometric stiffness K_g = P / L × [quadratic terms]
  - Nonlinear strain-displacement relations
  
Verification:
  After each time step, compute θ for critical floors
  Flag if θ approaches 0.10 (potential instability)
```

#### Stability Index Computation

```python
def compute_stability_index(story):
    P_story = sum(weights above story)
    V_story = story shear from analysis
    delta = lateral displacement (story drift)
    h_story = story height
    
    theta = (P_story * delta) / (V_story * h_story)
    
    if theta > 0.20:
        raise InstabilityWarning(f"Story {story}: θ = {theta:.3f} > 0.20")
    return theta
```

### 6.3 Configuration (analysis_config.yaml)

```yaml
pdelta_analysis:
  enabled: true
  
  geometric_transformation: 'PDelta'  # Corotational
  
  stability_index:
    compute: true
    report_frequency: 10              # Check every 10 steps
    warning_threshold: 0.10           # Alert if θ > 0.10
    failure_threshold: 0.20           # Stop if θ > 0.20
    
  output:
    save_stability_index: true        # Record θ vs time
    save_geometric_stiffness: false   # Advanced
```

---

## 7. Method 5: Plastic Hinge Analysis

### 7.1 Purpose & Definition

**Plastic Hinge:** Concentrated region where plastic curvature develops under cyclic loading, typically at beam-column joints and column bases.

**FEMA 356 Modeling (Section 5):**
- Hinges assigned as zero-length elements at expected plastic locations
- Moment-rotation (M-θ) relationships based on reinforcement & concrete strength
- Backbone curve (monotonic) + cyclic unloading rules
- Acceptance criteria define damage states: IO, LS, CP

### 7.2 Hinge Location Rules

```
Beam Plastic Hinges:
  Location: At each end of beam element (at face of column joint)
  Distance from joint face: L_hinge ≈ h_beam / 2 (effective hinge length)
  Hinge region depth: ~h_beam / 6 (concentrated curvature)

Column Plastic Hinges:
  Location: At base (above foundation) & at stories with soft-story effect
  Distance from joint center: estimated by moment diagram
  Additional: at column top if moment demand high

Joint Shear Hinges:
  Location: At beam-column joints (internal shear hinge)
  Represents joint shear failure vs. member flexure failure
  Threshold: Based on joint shear capacity (Section 7 of this plan)
```

### 7.3 Moment-Rotation Relationships

#### Backbone Curve (ASCE 41-23 Section 7)

For RC beam-columns (f'c = 30 MPa, fy = 500 MPa):

```
Yield Moment: M_y = Z × f_y × (1 - k × P / (f'c × A_g))
  where Z = plastic section modulus
        k = 0.5 (typically)
        P = axial load
        A_g = gross area

Yield Rotation: θ_y = L_v × M_y / (6 × E_I)
  where L_v = shear span (distance to inflection point)
        E = 200,000 MPa
        I = moment of inertia

Maximum Moment: M_max ≈ 1.15 × M_y (strain hardening)
Maximum Rotation: θ_max = θ_y × μ_Δ (ductility-dependent)
  Ductility: μ_Δ = (θ_max - θ_y) / θ_y

For SMRF (heavy confinement): μ_Δ ≈ 10–15
For OMRF (light confinement): μ_Δ ≈ 3–5
For Non-Sway (no confinement): μ_Δ ≈ 1–2

Residual Moment: M_res ≈ 0.2–0.3 × M_y (strength after softening)
```

#### Cyclic Behavior (Menegotto-Pinto Model)

```
Pinching Effect:
  - Strength degradation with increasing amplitude
  - Stiffness degradation due to concrete damage
  - Energy dissipation (hysteresis area) ∝ ductility demand

Rules:
  1. Unload along elastic slope initially
  2. Rebound with reduced stiffness
  3. Cross zero with reduced strength
  4. Rebound from other direction with further reduction
  5. Continue cycling with progressive degradation

Implementation:
  Use FEMA 356 or ASCE 41-23 tabulated values (Chapter 7, Tables)
  For each hinge: provide backbone curve points + unloading rules
```

### 7.4 Performance Level Assessment

```
Chord Rotation Limits (ASCE 41-23 Table 7-5):

BEAMS (RC Special MRF):
  Immediate Occupancy (IO):      θ ≤ 0.005  (0.5%)
  Life Safety (LS):              θ ≤ 0.015  (1.5%)
  Collapse Prevention (CP):      θ ≤ 0.025  (2.5%)

COLUMNS (RC Special MRF):
  Immediate Occupancy (IO):      θ ≤ 0.005  (0.5%)
  Life Safety (LS):              θ ≤ 0.010  (1.0%)
  Collapse Prevention (CP):      θ ≤ 0.020  (2.0%)

JOINTS:
  Based on internal shear stress ratio (Section 6 of this plan)

Algorithm:
  1. Extract peak hinge rotation from THA time history
  2. Compare with IO threshold:
       If max(|θ|) > θ_LS and < θ_CP: Performance = LS
       If max(|θ|) > θ_CP: Performance = CP (or Collapse)
  3. Aggregate over all hinges: building performance = worst hinge status
```

### 7.5 Damage Index (Park-Ang Method)

```
Damage Index:
  DI = δ_m / δ_u + λ × E_hys / (f_y × δ_u)

where:
  δ_m = maximum deformation reached
  δ_u = deformation capacity (at failure)
  E_hys = cumulative hysteretic energy dissipated
  f_y = yield strength
  λ ≈ 0.05–0.15 (weighting factor, typically 0.15 for RC)
  
Interpretation:
  DI < 0.40: Minor damage
  0.40 ≤ DI < 0.80: Moderate damage
  0.80 ≤ DI < 1.00: Severe damage
  DI ≥ 1.00: Collapse
  
Output: Record DI for each hinge element in dataset
```

### 7.6 Configuration (bnbc_parameters.yaml)

```yaml
plastic_hinge:
  enabled: true
  
  hinge_properties:
    backbone_curve: 'ASCE_41_23'   # Table 7-6 for RC beams/columns
    cyclic_model: 'modified_Menegotto_Pinto'
    
  acceptance_criteria:
    beam_io: 0.005
    beam_ls: 0.015
    beam_cp: 0.025
    column_io: 0.005
    column_ls: 0.010
    column_cp: 0.020
    joint_ductility: 4.0
    
  damage_assessment:
    method: 'Park_Ang'
    weighting_factor_lambda: 0.15
    
  output:
    save_hinge_rotations: true
    compute_damage_index: true
    output_performance_level: true
```

---

## 8. Method 6: Combined Multi-Method Analysis

### 8.1 Purpose: Ensemble & Multi-Stripe Framework

**Objective:** Synthesize outputs from all 5 methods into:
1. Unified dataset for ML training
2. Ensemble predictions with uncertainty bounds
3. Sensitivity analysis for framework type comparison
4. Multi-stripe IDA curves (intensity vs. PIDR)

### 8.2 Multi-Stripe IDA

```
Incremental Dynamic Analysis (IDA):
  
Definition:
  For each ground motion record:
    1. Scale to 16 intensity levels: Sa ∈ [0.05, ..., 1.50] g
    2. Run THA for each scaled record
    3. Extract PIDR vs. Sa
    4. Plot as single curve
    
Results:
  - One IDA curve = one GM + one building
  - Set of 500+ curves = cloud of building responses
  - Median + 16th/84th percentiles define fragility
  
Data Point:
  (Sa_intensity, PIDR) → input for ML model
  500 GMs × 16 levels × 5 buildings × 4 frameworks × 4 zones = 640,000 points
  (realistic, but reduced to 40,000 for Phase 2)
```

### 8.3 Cross-Method Validation

```
Comparison Matrix:
  
  THA-PIDR vs. Pushover Ductility:
    Correlation expected: R² > 0.7
    High correlation indicates consistent capacity estimate
    
  THA Peak Response vs. RSA Design Force:
    Usually THA > RSA (dynamics amplify response)
    Check if amplification factor reasonable (1.2–1.5×)
    
  P-Delta Stability Index:
    Track maximum θ for each analysis
    Correlate with PIDR: large PIDR → higher θ (expected)
    Flag anomalies (e.g., high PIDR with low θ → modeling error)
    
  Plastic Hinge Performance Level:
    Cross-check with PIDR threshold
    PIDR > 1.0% should correlate with hinges beyond IO
    Consistency validates hinge modeling
```

### 8.4 Framework Comparison

```
Performance Gradient Calculation:

For each building × zone combination:

1. Run IDA for all 4 framework types (Non-Sway, OMRF, IMRF, SMRF)
2. Extract median PIDR at each intensity level
3. Compute performance gradient vs. Non-Sway:
   
   PG = (PIDR_Non-Sway - PIDR_Framework) / PIDR_Non-Sway × 100%
   
   PG > 0:   Framework is better than Non-Sway
   PG < 0:   Framework is worse (unexpected)
   
4. Framework Complexity Index (FCI):
   FCI = (Reinf_Volume_Framework / Reinf_Volume_Non-Sway) × Cost_Factor
   
   FCI ≈ 1.0:  Non-Sway
   FCI ≈ 1.15: OMRF (15% more materials)
   FCI ≈ 1.30: IMRF
   FCI ≈ 1.50: SMRF
   
5. Cost-Benefit Ratio:
   CBR = PG / FCI
   
   Higher CBR = optimal framework (best performance per cost)
   Identify "sweet spot" where CBR is maximized
```

### 8.5 Configuration (analysis_config.yaml)

```yaml
combined_analysis:
  enabled: true
  
  multi_stripe:
    n_ground_motions: 500          # or 30 preliminary
    intensity_levels: 16           # Sa from 0.05 to 1.50 g
    
  ensemble:
    methods: ['THA', 'Pushover', 'Plastic_Hinge']
    generate_uncertainty_bounds: true
    
  cross_method_validation:
    enabled: true
    threshold_correlations: 0.70   # Minimum acceptable R²
    
  framework_comparison:
    compare_frameworks: true
    frameworks: ['nonsway', 'omrf', 'imrf', 'smrf']
    compute_performance_gradient: true
    compute_cost_benefit: true
    
  output:
    save_ida_curves: true
    save_fragility_medians: true
    plot_ensemble_results: true
    export_comparison_tables: true
```

---

## 9. Configuration File Specifications

### 9.1 analysis_config.yaml Structure

```yaml
# Complete configuration for all 6 analysis methods
# See Section 8 for examples of each method's config

analysis_framework:
  version: '1.0'
  date_created: '2026-03-28'
  standards: ['BNBC 2020', 'ASCE 7-22', 'ASCE 41-23']
  
  # [Sections for each method: RSA, THA, Pushover, P-Delta, Plastic Hinge, Combined]
  # [Detailed config blocks provided above]
```

### 9.2 bnbc_parameters.yaml Enhancements

```yaml
plastic_hinge:
  backbone_properties:
    RC_beam_smrf:
      material: 'f_c_30_MPa, f_y_500_MPa'
      moment_yield: 'computed from section'
      rotation_yield: [0.002, 0.004, 0.006]  # θ_y range
      rotation_capacities:
        io: 0.005
        ls: 0.015
        cp: 0.025
        collapse: 0.035
      
    RC_column_smrf:
      # Similar structure, adjusted for columns
      
  performance_levels:
    immediate_occupancy:
      pidr_limit: 0.01
      damage_description: 'Minimal - no visible cracks'
    life_safety:
      pidr_limit: 0.025
      damage_description: 'Moderate - repairable damage'
    collapse_prevention:
      pidr_limit: 0.04
      damage_description: 'Severe - near failure'
      
  acceptance_criteria:
    asce_41_23:
      table_7_5_beams: true
      table_7_5_columns: true
      joint_shear_ratios: [0.25, 0.20]  # interior, exterior
```

---

## 10. Uncertainty Quantification & Sensitivity

### 10.1 Ground Motion Variability (Aleatory)

```
Source: Different ground motion records at same intensity
  
Example:
  Building A, Sa(T₁) = 0.50 g, 500 different GMs
  
  Results:
    PIDR_mean = 2.1%
    PIDR_median = 1.9%
    PIDR_16th_percentile = 0.8%
    PIDR_84th_percentile = 3.5%
    
  Fragility Curve Output:
    P(PIDR > 2.5% | Sa = 0.50g) = integral from 2.5% to ∞
                                 ≈ 0.30 (30% probability)
```

### 10.2 Model Uncertainty (Epistemic)

**Sources:**
1. Material property variation (f'c ± 5%, fy ± 3%)
2. Section sizing approximations
3. Damping model assumptions (±20% variation)
4. Hinge model idealization

**Sensitivity Study:**
```
Parametric analysis: vary each parameter by ±10%
  Measure impact on PIDR
  Rank by sensitivity: which parameter most affects response?
  
Example Results (5-story SMRF, Sa = 0.50g):
  Base case PIDR = 2.1%
  
  Vary damping:          PIDR ∈ [1.8%, 2.4%]  (14% range)
  Vary f'c:             PIDR ∈ [2.0%, 2.3%]  (15% range)
  Vary column size:     PIDR ∈ [1.5%, 2.8%]  (87% range) — most sensitive
  Vary yield strength:  PIDR ∈ [1.9%, 2.4%]  (26% range)
```

### 10.3 Output Dataset Structure

```
ida_results.csv:
  
  Columns:
  - building_id: frame_5s_smrf (building identifier)
  - zone: 3 (BNBC 2020 zone)
  - framework_type: 'smrf' (framework classification)
  - gm_id: 1–500 (ground motion record number)
  - sa_intensity: 0.05, 0.10, ..., 1.50 (g, spectral acceleration)
  - pidr: 0.0087 (peak inter-story drift ratio, 0.87%)
  - pga: 0.24 (peak ground acceleration, g)
  - pv: 0.45 (peak ground velocity, m/s)
  - pdelta_theta_max: 0.085 (maximum stability index)
  - hinge_performance_level: 'LS' (Life Safety, from plastic hinges)
  - damage_index_mean: 0.52 (Park-Ang average across hinges)
  - rsa_base_shear: 180.5 (kN, from RSA design method)
  - pushover_capacity_base_shear: 220.0 (kN, from pushover)
  - pushover_ductility: 4.5
  
  Rows:
  - 500 GMs × 16 intensity levels × 5 buildings × 4 frames × 4 zones
  = 1,280,000 total (scaled to 40,000 for Phase 2 pilot)
```

---

## References

1. **BNBC 2020** — Bangladesh National Building Code, Part 2 (Structural Design)
2. **ASCE 7-22** — Minimum Design Loads and Associated Criteria for Buildings
3. **ASCE 41-23** — Seismic Evaluation and Retrofit of Existing Buildings
4. **FEMA P-58** — Seismic Performance Assessment of Buildings (7 volumes)
5. **FEMA 356** — Prestandard and Commentary for Seismic Rehabilitation of Buildings
6. **OpenSeesPy Documentation** — Python interface to OpenSees structural dynamics engine
7. **Vamvatsikos & Cornell (2002)** — Incremental Dynamic Analysis and its application to performance-based earthquake engineering

---

**Document Version:** 1.0  
**Status:** Complete implementation specification for Phase 2 analysis  
**Next Step:** Migrate analysis modules from src/analysis/ into Phase 2 IDA pipeline orchestration script
