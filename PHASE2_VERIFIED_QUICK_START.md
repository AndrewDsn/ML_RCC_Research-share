# Phase 2 Verified Records Execution Guide
## Quick Start for Full IDA Campaign with PEER NGA-West 2 Records

### 📋 Quick Execute
```bash
# Inside project directory
cd project

# Run Phase 2 with verified records (8 PEER NGA records per zone)
python -c "
import sys
sys.path.insert(0, '.')
from src.ida.phase2_executor import Phase2Executor
executor = Phase2Executor('config/analysis_config.yaml')
results = executor.run_full_campaign(n_gm_per_zone=8, use_verified=True)
print(f'✓ Phase 2 Complete: {len(results):,} records generated')
"
```

### 📊 Campaign Configuration
- **Mode:** Verified PEER NGA-West 2 earthquake records
- **Ground Motions:** 8 verified records per seismic zone (32 total)
- **Buildings:** 80 parametric RC frames
  - Heights: 5, 7, 10, 12, 15 stories
  - Types: Non-Sway, OMRF, IMRF, SMRF  
  - Zones: I, II, III, IV (BNBC 2020)
  - **Total:** 5 × 4 = 20 building types × 4 zones = 80 models
  
- **Intensity Levels:** 16 levels per GM
  - Range: Sa 0.05g → 1.50g (T=0.5s)
  - Step: ~0.10g
  
- **Total Records Generated:** ~51,200 time histories
  - Formula: 20 buildings × 4 zones × 8 GMs × 16 intensities = 51,200
  - File size: ~100-150 MB

### ⏱️ Execution Time Estimates
| Hardware | Time | Notes |
|----------|------|-------|
| **8-core Workstation** | 8-12 hours | Local execution, parallel-friendly |
| **16-core Workstation** | 4-6 hours | Better parallelization |
| **64-core Cloud (AWS c5.16x)** | 2-3 hours | Recommended for production |
| **Single-core (Sequential)** | 18-24 hours | Not recommended |

### 📍 Verified Records per Zone

**Zone I (Low Hazard)** - 8 records, M 6.2-7.1, R 8-50 km
- Northridge 1994 (2 stations)
- Loma Prieta 1989 (2 stations)
- Kobe 1995
- Duzce 1999
- Chi-Chi 1999
- Irpinia 1980

**Zone II (Moderate Hazard)** - 8 records, M 6.2-7.6, R 7-44 km
- Northridge 1994 (2 stations)
- Loma Prieta 1989 (2 stations)
- Duzce 1999
- Kobe 1995
- Chi-Chi 1999
- San Fernando 1971

**Zone III (High Hazard)** - 12 records, M 5.8-7.6, R 8-48 km
- Northridge 1994 (2 stations)
- Loma Prieta 1989
- Chi-Chi 1999 (2 stations)
- Duzce 1999
- Kobe 1995
- San Fernando 1971
- Kern County 1952
- Friuli 1976
- Umbria-Marche 1997

**Zone IV (Very High Hazard)** - 12 records, M 5.8-7.5, R 8-43 km
- Loma Prieta 1989
- Duzce 1999
- Kobe 1995
- Chi-Chi 1999 (2 stations)
- San Fernando 1971
- Kern County 1952
- Northridge 1994
- Friuli 1976
- Umbria-Marche 1997
- Irpinia 1980

### ✅ Pre-Execution Checklist
- [ ] Phase 1 models generated (80 in models/openseespy/)
- [ ] Configuration files present (config/bnbc_parameters.yaml, analysis_config.yaml)
- [ ] Output directories created (data/processed/, results/)
- [ ] OpenSeesPy installed and working
- [ ] Python 3.9+ environment activated

### 📁 Output Files
After execution, check:
```
data/processed/
├── ida_results_verified.csv          # Master results (100-150 MB)
└── phase2_campaign_stats.json        # Campaign statistics
```

### 🔍 Expected Output Format
Each row in `ida_results_verified.csv`:
```
building_id, zone, gm_id, intensity(Sa_g), pidr, pga(g), pgv(cm/s), 
residual_drift, damage_state, element_id_max_strain, max_strain_value, ...
```

Example:
```
frame_10s_smrf_z3, 3, LP_FMSJ_03, 0.25, 0.0145, 0.182, 12.5,
0.002, LS, col_10_1, 0.0321, ...
```

### 🚀 Next Steps After Phase 2
1. Validate results (convergence rate, PIDR distributions)
2. Generate statistics report
3. Proceed to Phase 3: ML model training
   - Feature engineering
   - Model training (LR, RF, XGBoost, ANN)
   - SHAP importance analysis

---

**Documentation Created:** April 22, 2026  
**Phase Status:** Ready for Execution  
**Estimated Campaign Duration:** 8-12 hours (8-core) | 2-3 hours (64-core cloud)
