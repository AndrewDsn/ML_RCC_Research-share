# 🚀 PHASE 2: START HERE

**Status:** ✅ **READY TO EXECUTE NOW**  
**Date:** April 22, 2026  
**Campaign:** Full Verified Records (PEER NGA-West 2)  
**Expected Duration:** 8-12 hours (8-core) | 1-3 hours (64-core cloud)

---

## ⚡ QUICK START (1 Command to Run Everything)

```bash
cd /workspaces/ML_RCC_Research-share/project
python run_phase2_full.py
```

**That's it!** This command will:
1. ✅ Generate 80 Phase 1 models (30-60 sec)
2. ✅ Run pilot test (2-5 min) 
3. ✅ Execute full verified campaign (8-12 hours)
4. ✅ Save results to `data/processed/ida_results_verified.csv`

---

## 📊 What This Does

### Generates:
- **80 parametric RC buildings** (5 heights × 4 frameworks × 4 BNBC zones)

### Uses:
- **32-40 verified earthquake records** from PEER NGA-West 2
  - Northridge, Loma Prieta, Kobe, Chi-Chi, Duzce, San Fernando, etc.
  - Real seismic events with realistic magnitude/distance/site parameters

### Performs:
- **Multi-stripe Incremental Dynamic Analysis (IDA)**
- 16 intensity levels per ground motion (0.05-1.50g @ T=0.5s)
- Nonlinear dynamic time history analysis
- Complex damage state classification

### Produces:
- **~51,200 time history records**
- CSV file: `ida_results_verified.csv` (100-150 MB)
- Columns: building_id, zone, gm_id, intensity, pidr, pga, damage_state, ...
- **Ready for Phase 3 ML model training**

---

## ⏱️ Timing

| Hardware | Time |
|----------|------|
| **8-core Workstation** | 8-12 hours ✅ Standard |
| **16-core CPU** | 4-6 hours 🚀 Faster |
| **64-core Cloud** | 1-3 hours ⭐ **RECOMMENDED** |

### Cost on Cloud:
- AWS c5.16xlarge: ~$10-15 for 2-3 hours
- Google Cloud n1-highmem-64: ~$15-20 for 2-3 hours
- **Total ROI:** Save 6-10 hours of local compute time

---

## 📋 System Requirements

✅ Verified:
- Python 3.9+
- 8+ GB RAM (16+ GB recommended)
- Disk space: 50 GB available (for models + data + results)
- ~20 GB for final CSV output

✅ Dependencies installed? Check:
```bash
cd /workspaces/ML_RCC_Research-share/project
python -c "import numpy, pandas, scipy, openseespy; print('✓ All packages ready')"
```

---

## 🎯 Execution Steps (Automated)

When you run `python run_phase2_full.py`:

### Step 1: Phase 1 Models (30-60 sec)
```
[STEP 1/3] GENERATE PHASE 1 PARAMETRIC RC MODELS
✓ Generated 80 parametric models
  - 5 heights (5, 7, 10, 12, 15 stories)
  - 4 frameworks (Non-Sway, OMRF, IMRF, SMRF)
  - 4 zones (Zone I-IV per BNBC 2020)
Output: models/openseespy/ (80 JSON files)
```

### Step 2: Pilot Test (2-5 min)
```
[STEP 2/3] QUICK PILOT TEST - VALIDATE INFRASTRUCTURE
Running with reduced dataset:
  - 2 GMs per zone (8 total)
  - 2 intensity levels
✓ Pilot generated 32-64 records
  - Validates GM loader
  - Validates IDA runner
  - Validates data pipeline
Output: Partial CSV (test data)
```

### Step 3: Full Campaign (8-12 hours)
```
[STEP 3/3] FULL VERIFIED CAMPAIGN
Starting multi-stripe IDA analysis:
  - 80 buildings
  - 8 verified GMs per zone (32 total)
  - 16 intensity levels per GM
  - ~51,200 total time histories

[Processing: 1/80] frame_5s_nonsway_z1 → 128 records
[Processing: 2/80] frame_5s_nonsway_z2 → 128 records
...
[Processing: 80/80] frame_15s_smrf_z4 → 128 records

✓ CAMPAIGN COMPLETE!
Total Records: 51,200
Output File: data/processed/ida_results_verified.csv (125 MB)
Campaign Duration: 8h 34m
```

---

## 📁 Output

### After Execution:
```
project/data/processed/
└── ida_results_verified.csv          ✅ MAIN OUTPUT
    - 51,200 rows
    - 20+ columns
    - 100-150 MB CSV file
    - Ready for ML training
```

### Sample Data:
```
building_id,zone,gm_id,intensity_sa_g,pidr,pga_g,pgv_cm_s,damage_state
frame_5s_nonsway_z1,1,NR_NHS_01,0.05,0.0032,0.12,5.2,No Damage
frame_5s_nonsway_z1,1,NR_NHS_01,0.15,0.0098,0.28,14.3,IO
frame_5s_nonsway_z1,1,NR_NHS_01,0.25,0.0165,0.42,22.1,LS
frame_5s_nonsway_z1,1,NR_NHS_01,0.35,0.0258,0.58,31.5,LS
...
```

---

## ✅ How to Verify Success

### After ~8-12 hours:
```bash
cd /workspaces/ML_RCC_Research-share/project

# Check file exists and has content
ls -lh data/processed/ida_results_verified.csv
# Should show: ~100-150 MB file

# Check record count
wc -l data/processed/ida_results_verified.csv
# Should show: ~51,200 lines (+1 header)

# Check first few rows
head -5 data/processed/ida_results_verified.csv
# Should show: building_id, zone, gm_id, ... columns

# Check statistics
python -c "
import pandas as pd
data = pd.read_csv('data/processed/ida_results_verified.csv')
print(f'Records: {len(data):,}')
print(f'PIDR Min: {data[\"pidr\"].min():.6f}')
print(f'PIDR Max: {data[\"pidr\"].max():.6f}')
print(f'PIDR Mean: {data[\"pidr\"].mean():.6f}')
"
```

---

## 🚨 If Something Goes Wrong

### "Phase 1 models not generating"
→ Run manually: `python -c "from src.modeling.phase1_generator import generate_phase1_models; generate_phase1_models('models/openseespy')"`

### "OpenSeesPy not available" (Demo Mode)
→ This is OK! System will create demo data for testing. In production environment with OpenSeesPy, full analysis runs.

### "Slow execution"
→ Use cloud! 64-core cloud machine completes in 1-3 hours vs 8-12 hours locally.

### "Memory issues"
→ Add swap: `sudo fallocate -l 10G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`

---

## 📚 Full Documentation

If you need more details:
- `PHASE2_READY.md` - Production readiness status
- `PHASE2_EXECUTION_GUIDE.md` - Complete execution guide (8000+ words)
- `EXECUTION_CHECKLIST.md` - Step-by-step checklist
- `PHASE2_VERIFIED_QUICK_START.md` - Quick reference

---

## 🎯 Next Steps After Execution

Once `ida_results_verified.csv` is ready:

**Phase 3: ML Model Training**
```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Load dataset
data = pd.read_csv('data/processed/ida_results_verified.csv')

# Train model
X = data[['n_stories', 'framework', 'zone', 'magnitude', 'distance', 'pga']]
y = data['pidr']

model = RandomForestRegressor(n_estimators=100)
model.fit(X, y)

# Generate predictions for fragility curves
# Analyze feature importance with SHAP
```

---

## 📞 Questions?

Refer to:
- Module source code (well-documented)
- `config/bnbc_parameters.yaml` for BNBC details
- `config/analysis_config.yaml` for IDA settings
- Test files in `tests/` for usage examples

---

## 🚀 **READY? RUN THIS NOW:**

```bash
cd /workspaces/ML_RCC_Research-share/project
python run_phase2_full.py
```

**⏱️ Come back in 8-12 hours!**
(Or check progress: `tail -f results/logs/phase2_execution_*.log`)

---

**Status:** ✅ **ALL SYSTEMS GO**  
**Created:** April 22, 2026  
**Ready:** YES
