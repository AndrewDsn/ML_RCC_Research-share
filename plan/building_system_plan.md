# Building System Plan
## Parametric RC Moment Frame Models for BNBC 2020 Seismic Analysis

**Date Created:** March 28, 2026  
**Last Updated:** March 28, 2026  
**Status:** Ready for Phase 1 Implementation  
**Reference Standards:**
- BNBC 2020 (Bangladesh National Building Code 2020)
- ASCE 7-22 (American Society of Civil Engineers)
- ACI 318-19 (Concrete Design Code)

---

## Table of Contents

1. [Building System Overview](#1-building-system-overview)
2. [Framework Types & Classifications](#2-framework-types--classifications)
3. [Parametric Geometric Specifications](#3-parametric-geometric-specifications)
4. [Material Properties & BNBC Compliance](#4-material-properties--bnbc-compliance)
5. [Design Criteria by Framework Type](#5-design-criteria-by-framework-type)
6. [Reinforcement Design Requirements](#6-reinforcement-design-requirements)
7. [Joint Shear Design](#7-joint-shear-design)
8. [OpenSeesPy Implementation Specifications](#8-openseespy-implementation-specifications)
9. [Model Verification & Validation](#9-model-verification--validation)
10. [Building Templates & Numbering Scheme](#10-building-templates--numbering-scheme)

---

## 1. Building System Overview

### 1.1 Research Scope
The project develops parametric 2D RC Special Moment-Resisting Frame (SMRF) buildings with comparative analysis of four framework types:
1. **Non-Sway Frames** (R=1.5) — Minimal detailing, load-bearing walls
2. **Ordinary Moment Resisting Frames (OMRF)** (R=3) — Light confinement, basic shear reinforcement
3. **Intermediate Moment Resisting Frames (IMRF)** (R=4) — Moderate confinement, partial joint detailing
4. **Special Moment Resisting Frames (SMRF)** (R=5) — Heavy confinement, full joint detailing per ASCE 41-23

### 1.2 Building Characteristics
- **Type:** Reinforced Concrete Moment-Resisting Frames (2D analysis)
- **Story Counts:** 5, 7, 10, 12, 15 stories
- **Occupancy:** Standard commercial/residential buildings
- **Design Basis:** BNBC 2020 seismic design per Zone III (Medium seismic hazard, Dhaka region)
- **Seismic Zones Analyzed:** All four BNBC 2020 zones (I, II, III, IV)

### 1.3 Structural System
- **Lateral System:** Special Moment Resisting Frame (SMRF) × 2 directions
- **Vertical System:** Reinforced concrete columns + gravity loads
- **Diaphragms:** Rigid floor diaphragms (2D simplification)
- **Foundation:** Fixed at base (fully fixed, 0 displacement & rotation)

---

## 2. Framework Types & Classifications

### 2.1 Non-Sway Frames
| Parameter | Value | Notes |
|---|---|---|
| Response Modification Factor (R) | 1.5 | BNBC 2020 Table 2-1 |
| Importance Factor (I) | 1.0–1.25 | Occupancy-dependent |
| Deflection Amplification (Cd) | 1.25 | Minimal ductility |
| System Overstrenght (Ω₀) | 2.0 | Conservative |
| Confinement Type | None | Standard concrete |
| Transverse Reinforcement | Minimum code spacing | No special seismic detailing |
| Joint Detailing | Not required | Standard gravity design rules |
| P-Delta Analysis | Optional (usually neglect) | θ < 0.05 assumed |

**Design Approach:** Essentially gravity load-bearing construction with minimal earthquake provisions. Suitable for very low seismic hazard zones or very stiff buildings where drift is negligible.

### 2.2 Ordinary Moment Resisting Frames (OMRF)
| Parameter | Value | Notes |
|---|---|---|
| Response Modification Factor (R) | 3.0 | BNBC 2020 Table 2-1 |
| Importance Factor (I) | 1.0–1.25 | Occupancy-dependent |
| Deflection Amplification (Cd) | 3.0 | Moderate ductility |
| System Overstrenght (Ω₀) | 3.0 | Standard |
| Confinement Type | Light confinement | Lightly confined concrete |
| Transverse Reinforcement Spacing | φ8 @ 300mm | Standard spacing |
| Joint Detailing | Limited | Reduced shear reinforcement |
| P-Delta Analysis | Required | θ < 0.10 allowed |

**Design Approach:** Basic moment resisting frame design per BNBC 2020 Chapter 2. Moderate confinement provides some ductility. Code-minimum detailing for standard seismic design. Transition point between gravity-dominant and earthquake-resistant design.

### 2.3 Intermediate Moment Resisting Frames (IMRF)
| Parameter | Value | Notes |
|---|---|---|
| Response Modification Factor (R) | 4.0 | BNBC 2020 Table 2-1 |
| Importance Factor (I) | 1.0–1.25 | Occupancy-dependent |
| Deflection Amplification (Cd) | 4.0 | Enhanced ductility |
| System Overstrenght (Ω₀) | 3.5 | Increased |
| Confinement Type | Moderate confinement | Mander confinement model |
| Transverse Reinforcement Spacing | φ10 @ 200mm | Tighter spacing |
| Joint Detailing | Partial | Enhanced joint shear reinforcement |
| P-Delta Analysis | Required | θ < 0.10 allowed |

**Design Approach:** Balanced moment resisting frame with improved ductility. Suitable for moderate to high seismic zones. Enhanced material confinement improves cyclic performance and energy dissipation capacity.

### 2.4 Special Moment Resisting Frames (SMRF)
| Parameter | Value | Notes |
|---|---|---|
| Response Modification Factor (R) | 5.0 (5.5 for Perimeter) | BNBC 2020 Table 2-1, ASCE 41-23 |
| Importance Factor (I) | 1.0–1.25 | Occupancy-dependent |
| Deflection Amplification (Cd) | 5.5 | maximum ductility |
| System Overstrenght (Ω₀) | 4.0 | Strong system |
| Confinement Type | Heavy Mander confinement | Maximum confinement factor |
| Transverse Reinforcement Spacing | φ12 @ 150mm | Minimum spacing for high ductility |
| Joint Detailing | Full detailing | Complete ASCE 41-23 compliance |
| P-Delta Analysis | Required | θ < 0.10 allowed |

**Design Approach:** High-ductility moment resisting frame design per ASCE 41-23 Section 7 and BNBC 2020 Chapter 2.7. Maximum lateral load resistance with controlled plastic hinge formation. Suitable for all seismic zones and critical facilities. Full plastic hinge design specifications implemented.

---

## 3. Parametric Geometric Specifications

### 3.1 Standard Building Dimensions

#### Story Heights & Typical Floor Plan
```
Story Height Configuration:
- First Floor (Ground Floor): 4.0 m (includes 1.5 m clear for mechanical/parking)
- Intermediate Floors (2–N): 3.5 m (typical office/residential)
- Roof: 3.0 m (smaller span, less equipment)
- Total Building Height: 
  * 5-story:  4.0 + 4×3.5 + 3.0 = 22.0 m
  * 7-story:  4.0 + 6×3.5 + 3.0 = 30.0 m
  * 10-story: 4.0 + 9×3.5 + 3.0 = 44.5 m
  * 12-story: 4.0 + 11×3.5 + 3.0 = 51.5 m
  * 15-story: 4.0 + 14×3.5 + 3.0 = 62.0 m

Span Lengths (Bay Widths):
- Typical transverse direction: 6.0 m (5 bays)
- Typical longitudinal direction: 6.0 m (4 bays)
- Total footprint: 30 m (transverse) × 24 m (longitudinal) ≈ 720 m²
```

#### 3D Frame Configuration
```
Number of Bays:
- Transverse (E-W): 5 bays × 6.0 m = 30 m total span
- Longitudinal (N-S): 4 bays × 6.0 m = 24 m total span
- 2D Analysis: One representative transverse frame (5 columns, 4 bays)
- Frame discretization: Rigid joint connections per BNBC 2020
```

### 3.2 Column Section Design

#### Sizing Logic (per BNBC 2020 Section 2.7.5 — Column Demand/Capacity Ratio)
```
Column Dimension Selection:
P-M Interaction diagrams → DC_ratio = (P_E_max + M_E_max) / (P_n + M_n) ≤ 1.0
Typical column sizes selected for DC_ratio ≈ 0.60–0.75 (avoid overly large columns)

By Building Height:
5-story:    400 × 400 mm (typical low-rise frame)
7-story:    450 × 450 mm (intermediate rise)
10-story:   500 × 500 mm (medium-rise frame)
12-story:   550 × 550 mm (high-rise frame)
15-story:   600 × 600 mm (tall frame, higher demand)

Reinforcement Configuration by Framework Type:

Non-Sway / OMRF:
  - Longitudinal: 8Φ16 (ρ_l = 1.25 %) — minimum
  - Clear cover: 40 mm
  - Ties: Φ10 @ 300 mm (light confinement)
  - Confinement factor: κ_s = 0.70

IMRF:
  - Longitudinal: 12Φ20 (ρ_l = 1.88 %) — enhanced
  - Clear cover: 40 mm
  - Ties: Φ10 @ 200 mm (moderate confinement)
  - Confinement factor: κ_s = 0.85

SMRF:
  - Longitudinal: 16Φ25 (ρ_l = 2.50 %) — maximum
  - Clear cover: 40 mm
  - Ties: Φ12 @ 150 mm (heavy confinement)
  - Confinement factor: κ_s = 1.00 (Mander confinement: f_cc' = f_c' × [2.254 × √(1 + 7.94 × κ_s) − 2 × κ_s − 1.254])
```

### 3.3 Beam Section Design

#### Sizing Logic
```
Beam sections selected per BNBC 2020 Section 2.7.4 (Beam-Column Joint Performance):
Beams typically sized shallower than columns to encourage plastic hinge formation in beams (not columns).

By Building Height:
All Stories:  300 × 500 mm (width × depth, standard commercial)
- Typical residential/office beam depth/span ratio ≈ 1/15–1/20
- For 6.0 m span: depth = 300–400 mm (500 mm selected for safety margin)

Reinforcement Configuration by Framework Type:

Non-Sway / OMRF:
  - Top: 3Φ16 (ρ_top = 0.48 %)
  - Bottom: 4Φ20 (ρ_bot = 0.85 %)
  - Stirrups: Φ8 @ 200 mm (light)
  
IMRF:
  - Top: 4Φ20 (ρ_top = 0.85 %)
  - Bottom: 5Φ20 (ρ_bot = 1.06 %)
  - Stirrups: Φ10 @ 150 mm (moderate)

SMRF:
  - Top: 5Φ25 (ρ_top = 1.31 %)
  - Bottom: 6Φ25 (ρ_bot = 1.57 %)
  - Stirrups: Φ12 @ 100 mm (heavy — confined plastic hinge zone)
```

---

## 4. Material Properties & BNBC Compliance

### 4.1 Concrete Material Properties

#### Grade & Strength (per BNBC 2020 Section 2.1)
| Property | Value | Notes |
|---|---|---|
| Concrete Grade | M30 (f'c = 30 MPa) | Standard for seismic design in Bangladesh |
| Elastic Modulus | Ec = 25,000 MPa | = 4700√f'c per BNBC 2020 |
| Density | ρ_c = 2400 kg/m³ | Standard reinforced concrete |
| Poisson's Ratio | ν = 0.20 | Typical for concrete |

#### Uniaxial Stress-Strain Model
**Concrete01 (Unconfined, Non-Sway/OMRF):**
```
Parameters:
- fpc = -30.0 MPa (peak stress, negative for compression)
- epsc0 = -0.002 (strain at peak stress)
- fpcu = -6.0 MPa (residual strength, ~20% of f'c)
- epsU = -0.006 (ultimate strain)

Model Behavior:
- Linear on loading to peak
- Linear unloading with full recovery
- Parabolic on reload (Karsan-Jirsa effect)
- Conservative for non-confined concrete
```

**Concrete02 (Confined, IMRF/SMRF):**
```
Parameters (Mander Confinement Model):
- fpc = -30.0 MPa (unconfined peak)
- fcc' ≈ -36–40 MPa (confined peak, depends on κ_s)
- epsc0 = -0.002 (unconfined strain at peak)
- epscc ≈ -0.004–0.005 (confined strain at peak, higher for confined)
- fpcu = -6.0 MPa (residual)
- epsU = -0.010 (ultimate strain, larger for confined)
- λ = 0.1 (degradation parameter)

Confined Strength Coefficient:
κ_s = sum(A_st × f_yh) / (b × s × f_c') — usually 0.7–1.2
where A_st = area of one tie leg, f_yh = yield of steel, s = tie spacing
```

### 4.2 Steel Material Properties

#### Reinforcement Grade (per BNBC 2020 & ACI 318-19)
| Property | Value | Notes |
|---|---|---|
| Steel Grade | Fe500 (Grade 60, ASTM A706 equivalent) | Seismic-grade rebar |
| Yield Strength | f_y = 500 MPa | Standard 500 MPa steel |
| Elastic Modulus | E_s = 200,000 MPa | Steel Young's modulus |
| Strain Hardening | 0.015 | ~1.5% hardening strain |

#### Uniaxial Stress-Strain Model
**Steel01 (Elastic-Plastic, Ordinary Design):**
```
Parameters:
- Fy = 500.0 MPa (yield strength)
- E0 = 200,000 MPa (elastic modulus)
- b = 0.01 (strain-hardening ratio, 1%)

Model Behavior:
- Linear elastic to yield (ε = Fy/E0 = 0.0025)
- Perfect plastic beyond yield with small hardening
- Same hardening on reload
- Conservative cyclic model
```

**Steel02 (Menegotto-Pinto, Cyclic Seismic Design):**
```
Parameters:
- Fy = 500.0 MPa (yield)
- E0 = 200,000 MPa (elastic modulus)
- b = 0.01 (hardening ratio)
- R0 = 18.5 (initial curvature, controls Baushinger effect)
- cR1 = 0.925 (curvature parameter 1)
- cR2 = 0.15 (curvature parameter 2)

Model Behavior:
- Captures strain reversal ("Baushinger effect")
- Pinching at zero stress under cyclic loading
- Realistic for earthquake-induced cyclic strains
- Provides accurate energy dissipation
```

### 4.3 Gravity Loads & Design Loads

#### Dead Load (Permanent)
| Component | Load (kN/m²) | Notes |
|---|---|---|
| Concrete floor slab | 6.0 | 200 mm slab, ρ_c = 2400 kg/m³ |
| Ceiling + Mechanical | 1.5 | Suspended ceiling, ducts, pipes |
| Floor Finish | 1.5 | Tiles, screed, waterproofing |
| Partition Walls | 1.0 | Typical lightweight partitions |
| **Total Dead Load (D)** | **10.0** | Typical office building |

#### Live Load (Temporary)
| Occupancy | Load (kN/m²) | Notes |
|---|---|---|
| Office | 2.5 | BNBC 2020 Table 4-1 |
| Residential | 2.0 | BNBC 2020 Table 4-1 |
| Roof | 0.75 | BNBC 2020 Table 4-1 |

#### Design Gravity Load (for IDA)
```
Floor Load = 1.0 × D + 0.2 × L = 10.0 + 0.5 = 10.5 kN/m²
(This corresponds to 2/3 live load reduction per gravity design standards)
Applied as distributed beam loads in OpenSeesPy model.

Total Gravity Load Intensity (Seismic Design):
w = 10.5 kN/m² × beam tributary area
For 6.0 m bays: w = 10.5 × 6.0 ≈ 63 kN/m (distributed linearly on beams)
```

---

## 5. Design Criteria by Framework Type

### 5.1 Base Shear Calculation (BNBC 2020 Section 3.2)

```
V_base = C_s × W
where:
  C_s = max(0.044 × Z × I / R, 0.01 × Z × I)       [BNBC 2020 Eq. 3-2]
  Z = Seismic Zone Coefficient
  I = Importance Factor (≈ 1.0)
  R = Response Modification Factor (framework-dependent)
  W = Total Seismic Weight

Framework-Specific R Factors:

Non-Sway Frames:          R = 1.5
OMRF:                     R = 3.0
IMRF:                     R = 4.0
SMRF:                     R = 5.0 (5.5 for perimeter frames)

Seismic Zone Coefficients (BNBC 2020):
Zone I:   Z = 0.12
Zone II:  Z = 0.18
Zone III: Z = 0.24 (Dhaka, Medium seismic hazard)
Zone IV:  Z = 0.36 (Chittagong, High seismic hazard)

Example Calculation (5-story SMRF, Zone III):
T ≈ 0.075 × h^(3/4) ≈ 0.075 × (22)^(3/4) ≈ 0.65 sec
S_a(T) = interpolate from design response spectrum
C_s = 0.044 × 0.24 × 1.0 / 5.0 = 0.00211 (or minimum 0.01 × 0.24 = 0.0024)
V_base = max(0.00211, 0.0024) × W = 0.0024 × W
```

### 5.2 Distribution of Lateral Forces (BNBC 2020 Section 3.2)

```
Lateral force at floor i:
F_i = (V_base × w_i × h_i) / Σ(w_j × h_j)

where:
  w_i = seismic weight at floor i
  h_i = height of floor i above base
  Σ(w_j × h_j) = sum over all floors

Story Shear:
V_i = Σ F_j (force and all above)

Story Moment (overturning moment at base):
M_base = Σ F_i × (H - h_i)

Design Shear Capacity Check:
φ × V_c ≥ V_design  (per ACI 318 design guide)
where φ = 0.75 (shear capacity factor)
```

### 5.3 Second-Order (P-Delta) Effects (BNBC 2020 Section 3.2.7)

```
Stability Index: θ = (P_total × Δ) / (V_story × h_story)

where:
  P_total = total story weight above
  Δ = lateral story drift
  V_story = story shear force
  h_story = story height

Allowable Limits (BNBC 2020):
- θ < 0.10: P-Delta effects included in base shear calculation
- 0.10 ≤ θ < 0.20: P-Delta effects must be explicitly computed
- θ ≥ 0.20: Building is unstable or requires redesign

OpenSeesPy Implementation:
- Use "PDelta" transformation for geometric nonlinearity
- Compute θ after each analysis step
- Flag stories where θ > 0.10 for detailed review
```

---

## 6. Reinforcement Design Requirements

### 6.1 Longitudinal Reinforcement Ratio Limits (BNBC 2020 / ACI 318)

```
Minimum ρ_l,min = 0.01 (1% of gross section area)
Maximum ρ_l,max = 0.08 (8% of gross section area)

SMRF Specific (ASCE 41-23 Section 7.2):
- ρ_l,min = 0.01 (same as minimum)
- ρ_l,max ≤ 0.06 (6% for seismic ductility)
- Longitudinal bars in beams:
  * At least 2 bars must continue through joint zone
  * Anchorage length: l_d = 0.4 × d_b × f_y / √f_c' ≈ 47 × d_b  [mm]
  * For Φ25 bar: l_d ≈ 1175 mm (> 40 × bar diameter)
```

### 6.2 Transverse Reinforcement (Ties/Stirrups) — Confinement

```
Spacing Limits by Framework Type:

Non-Sway:
  - s_max = 16 × d_l = 256 mm (Φ16 bars)
  - Typically: Φ10 @ 300 mm

OMRF:
  - s_max = 12 × d_l = 192 mm
  - Typically: Φ10 @ 300 mm (basic seismic detailing)

IMRF:
  - s_max = 8 × d_l = 128 mm (BNBC 2020 § 2.7.4)
  - Typically: Φ10 @ 200 mm

SMRF:
  - s_max = 6 × d_l = 150 mm (ASCE 41-23 § 7.2.2)
  - Plastic hinge zone (up to 2h_c above joint): Φ12 @ 100 mm
  - Outside plastic hinge zone: Φ12 @ 150 mm
  - Confinement effectiveness: κ_s = 0.9–1.0+ for SMRF
```

### 6.3 Beam-Column Joint Reinforcement

```
Internal Joint Shear Stress (per BNBC 2020 § 2.7.5):

τ_jh = V_jh / (b_c × h_c)

where:
  V_jh = internal joint shear force
  b_c, h_c = column width and height
  
Maximum allowable τ_jh (ASCE 41-23):
  - Interior joints (4 beams): 0.25 × √f_c' (MPa)
  - Exterior joints (2 beams): 0.20 × √f_c' (MPa)
  For f_c' = 30 MPa:
    - Interior: τ_jh,max ≈ 13.7 MPa
    - Exterior: τ_jh,max ≈ 11.0 MPa

SMRF Joint Detailing (ASCE 41-23):
- Horizontal joint reinforcement: Φ12 @ 100 mm (full confining cage)
- Vertical reinforcement through joint: mandatory for SMRF
- Joint confinement effectiveness: κ_j ≈ 0.85–0.95
```

---

## 7. Joint Shear Design

### 7.1 Joint Shear Force Calculation

```
Interior Joint Shear Force:
V_jh = T_1 + T_2 - V_col

where:
  T_1, T_2 = tension forces in top and bottom beam bars
  V_col = column shear within joint zone
  
Exterior Joint Shear Force:
V_jh = T_beam - V_col (only one beam contributing tension)

Simplified Upper Bound (Conservative):
V_jh ≈ f_y × A_s,1 + f_y × A_s,2
where A_s,1, A_s,2 are top and bottom beam reinforcement areas
```

### 7.2 Joint Shear Reinforcement

```
Required Tie Area (ASCE 41-23 § 7.2.5):

A_sh = (V_jh - φ × 0.075 × √f_c' × b_c × h_c) / (φ × 0.5 × f_y)

Practical Detailing for SMRF:
- Interior joint: Horizontal + Vertical confining ties
  * Minimum: 4 legs of Φ12 ties @ 100 mm spacing
  * Effective area: A_sh,eff ≈ 4 × (π × 6²) ≈ 452 mm²

- Exterior joint: 3-sided confinement (open side to wall)
  * Minimum: 3 legs of Φ12 @ 100 mm
  * Plus perimeter beam stirrups extending into joint
```

---

## 8. OpenSeesPy Implementation Specifications

### 8.1 Model Creation Workflow

```python
# Pseudo-code workflow in src/modeling/rc_frame.py

1. Create RCFrame instance:
   frame = RCFrame(
       n_stories=10,
       framework_type='smrf',  # or 'nonsway', 'omrf', 'imrf'
       config_path='config/bnbc_parameters.yaml'
   )

2. Set geometric properties:
   frame.set_geometry(
       story_height=3.5,
       bay_width=6.0,
       n_bays=5,
       column_size=(500, 500),   # mm
       beam_size=(300, 500)      # mm
   )

3. Define materials:
   frame.create_model()  # Calls _create_concrete_materials, _create_steel_materials

4. Create structure:
   frame._create_nodes()       # 2D node grid: (n_stories+1) × (n_bays+1) nodes
   frame._create_elements()    # Columns + beams with nonlinearBeamColumn elements
   frame._apply_boundary_conditions()  # Fix base nodes

5. Apply loads & analyze:
   frame.apply_gravity_loads(floor_load=10.5, roof_load=8.5)  # in kN/m²
   ops.analyze(...)  # Gravity analysis first

6. Save verified model:
   frame.save_model('models/openseespy/frame_10s_smrf_z3.json')
```

### 8.2 Node Numbering Scheme

```
Node ID Format: FFBB  
where:
  FF = floor number (00 = base/foundation, 01 = 1st floor, ..., 15 = 15th floor)
  BB = bay/column line (00, 01, 02, ..., 05 for 5 bays)

Example (10-story building):
  Story 0 (Base):   Nodes 0000, 0001, 0002, ..., 0005 (6 col lines)
  Story 1:          Nodes 0100, 0101, 0102, ..., 0105
  Story 2:          Nodes 0200, 0201, 0202, ..., 0205
  ...
  Story 10 (Roof):  Nodes 1000, 1001, 1002, ..., 1005

3 DOF per node: [1=X-displacement, 2=Y-displacement, 3=Z-rotation]
(2D model: motion only in X direction, but notation uses standard 3DOF)
```

### 8.3 Element Numbering Scheme

```
Column Elements:
  Element ID: FFCC  (Story FF, Column/Bay CC)
  Range: 0001–0055 (for 10-story, 5-column-line frame)
  Nodes: (FF,CC) → (FF+1,CC)

Beam Elements:
  Element ID: FFBB  (Story FF, Beam/Bay BB)
  Range: 0101–0140 (for 10-story, 4-bay frame [beams between 5 columns])
  Nodes: (FF,BB) → (FF,BB+1)
```

### 8.4 Material-Section Mapping

```
Fiber Section ID:  Material Assemblage
  1001–1015:       Column fiber sections (Story 1–15)
  2001–2015:       Beam fiber sections (Story 1–15, assumes uniform per floor)

Each fiber section contains:
  - Concrete fibers (divided into confined + unconfined core)
  - Steel reinforcement represented by equivalent steel fibers
  - Area mapping: total_area = concrete + steel areas
```

### 8.5 Analysis Parameters

```
Gravity Analysis (Load Application):
  - Linear static analysis
  - Single load step (implicit integration)
  - Convergence tolerance: 1e−8 on displacement

Dynamic (Seismic) Analysis:
  - Newmark-β integration scheme
  - β = 0.25, γ = 0.50 (numerically stable, γ = 0.5)
  - Time step: Δt = 0.005 seconds (200 steps/second)
  - Ground motion duration: 50 seconds (10,000 load steps)
  - Convergence tolerance: 1e−8 (nonlinear solver)
  - Maximum iterations: 100 (Newton-Raphson)
  
Damping:
  - Rayleigh damping (proportional to M and K)
  - ζ = 5% in first two modes (typical for RC structures)
  - ω_1, ω_2 computed from modal analysis
  - Rayleigh coefficients: α, β → M^(-1)K + αM + βK
```

### 8.6 Recorders (Results Output)

```
Standard Recorders for Each Model:

A. Node Recorders (Displacements):
   ops.recorder('Node', '-file', '.../floor_displacements.out',
                '-node', *floor_nodes, '-dof', 1, 'disp')
   
B. Reaction Recorders (Base Forces):
   ops.recorder('Reaction', '-file', '.../base_reactions.out',
                '-node', base_nodes, '-dof', [1,2,3], 'reaction')

C. Element Recorders (Internal Forces):
   ops.recorder('Element', '-file', '.../element_forces.out',
                '-ele', *element_ids, 'globalForce')

D. Section/Material Recorders (Stress-Strain):
   ops.recorder('Section', '-file', '.../hinge_rotations.out',
                '-ele', *plastic_hinge_elements, 'deformation')

Output File Format: Single column of values, one value per load step
Processing: Read with numpy/pandas → compute peak responses, cumulative damage indices
```

---

## 9. Model Verification & Validation

### 9.1 Verification Checks (After Model Creation)

| Check | Criterion | Tool |
|---|---|---|
| **Node Existence** | All (n_stories+1) × (n_bays+1) nodes created | ops.nodeCoord() |
| **Element Count** | Columns: n_stories × (n_bays+1); Beams: n_stories × n_bays | ops.elementType() |
| **Boundary Conditions** | Base nodes fixed (U_x=U_y=U_z=R_z=0) | ops.nodeDisp() after constraint |
| **Gravity Load** | Total vertical load applied = sum of floor loads + roof | Force equilibrium |
| **Material Definition** | All materials defined in ModelState, material IDs unique | ops.testNorm() |
| **Section Assignment** | Each element linked to correct fiber section | ops.sectionTag() |

### 9.2 Validation Checks (Post-Analysis)

| Check | Criterion | Success Indicator |
|---|---|---|
| **Static Equilibrium** | P_base = total gravity weight | Error < 1% |
| **Fundamental Period** | T ≈ 0.075 × h^(3/4) ± 10% | Close empirical match |
| **Base Shear** | V ≈ C_s × W (seismic) | Within BNBC range |
| **Peak Drift** | PIDR < 4% (no collapse) | Model is stable |
| **Positive Energy Dissipation** | Energy in = Energy out + Hysteretic loss | Energy balance correct |
| **Hinge Formation Sequence** | Plastic hinges form at expected locations | Capacity design verified |

### 9.3 Reference Solution Comparison

```
Validation against published results:

For a 5-story SMRF with f'c=30 MPa, fy=500 MPa, section 400×400 mm:
Expected Fundamental Period (Empirical, BNBC):
  T = 0.075 × (22)^(3/4) ≈ 0.65 seconds

Expected Base Shear (Zone III, R=5):
  V_base = 0.0024 × W ≈ 0.24 W  [per BNBC 2020]
  where W = total seismic weight

Expected Peak Story Drift under Design-Level Seismic (PGA ≈ 0.25g):
  PIDR ≈ 1.0–1.5% (for SMRF under moderate seismic demand)
  PIDR ≈ 2.0–3.0% (for SMRF under strong seismic demand)
```

---

## 10. Building Templates & Numbering Scheme

### 10.1 Template Nomenclature

```
File naming convention:
  frame_{n_stories}s_{framework}_z{zone}.json
  
Examples:
  - frame_5s_nonsway_z1.json   (5-story Non-Sway, Zone I)
  - frame_10s_omrf_z3.json     (10-story OMRF, Zone III)
  - frame_15s_smrf_z4.json     (15-story SMRF, Zone IV)

Master Templates (n_stories, framework combinations):

STORY COUNTS:
- 5 stories  (Low-rise, 22 m height)
- 7 stories  (Low-rise, 30 m height)
- 10 stories (Medium-rise, 44.5 m height)
- 12 stories (High-rise, 51.5 m height)
- 15 stories (High-rise, 62 m height)

FRAMEWORK TYPES:
- nonsway   (R=1.5, minimum detailing)
- omrf      (R=3.0, light confinement)
- imrf      (R=4.0, moderate confinement)
- smrf      (R=5.0, heavy confinement)

SEISMIC ZONES:
- z1, z2, z3, z4 (BNBC 2020 Zones I, II, III, IV)

Total Master Templates: 5 × 4 × 4 = 80 variants
```

### 10.2 Geometric Parameters Summary Table

| Story Count | Total Height (m) | Bay Count | Floor Area (m²) | Typical Weight (MN) |
|---|---|---|---|---|
| 5 | 22.0 | 5 | 720 | 18–22 |
| 7 | 30.0 | 5 | 720 | 24–30 |
| 10 | 44.5 | 5 | 720 | 34–43 |
| 12 | 51.5 | 5 | 720 | 41–52 |
| 15 | 62.0 | 5 | 720 | 51–65 |

### 10.3 Reinforcement Summary (SMRF)

| Story Count | Col Section | Col Reinf | Beam Section | Beam Reinf (Top/Bot) |
|---|---|---|---|---|
| 5 | 400×400 | 8Φ25 | 300×500 | 5Φ25 / 6Φ25 |
| 7 | 450×450 | 12Φ25 | 300×500 | 5Φ25 / 6Φ25 |
| 10 | 500×500 | 12Φ25 | 300×500 | 5Φ25 / 6Φ25 |
| 12 | 550×550 | 16Φ25 | 300×500 | 6Φ25 / 7Φ25 |
| 15 | 600×600 | 16Φ25 | 300×550 | 6Φ25 / 7Φ25 |

---

## References

1. **BNBC 2020** — Bangladesh National Building Code
   - Part 2 (Chapter 2–3): Structural Design & Seismic Provisions
   - Section 2.1: Material specifications
   - Section 2.7: Special seismic detailing for MRFs
   - Section 3.2: Seismic analysis & design

2. **ASCE 7-22** — Minimum Design Loads and Associated Criteria for Buildings and Other Structures
   - Chapter 11: Seismic design general procedures
   - Chapter 12: Seismic design requirements for building structures

3. **ASCE 41-23** — Seismic Evaluation and Retrofit of Existing Buildings
   - Chapter 7: Special moment-resisting frames
   - Appendix: Plastic hinge properties & acceptance criteria

4. **ACI 318-19** — Building Code Requirements for Structural Concrete and Commentary

5. **FEMA 356** — Prestandard and Commentary for Seismic Rehabilitation of Buildings
   - Section 5: Plastic hinge modeling & damage assessment

6. **FEMA P-58** — Seismic Performance Assessment of Buildings (Volumes 1–7)

---

**Document Version:** 1.0  
**Status:** Ready for Phase 1 Implementation  
**Next Step:** Begin creating parametric models in src/modeling/rc_frame.py with multi-framework support
