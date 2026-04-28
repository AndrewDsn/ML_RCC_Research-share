# Phase 2 Full Verified Campaign - Execution Status & Instructions

## 📋 Current Status (April 22, 2026)

✅ **READY TO EXECUTE**
- Phase 1 infrastructure complete
- Phase 2 verified records system ready
- Pilot test infrastructure prepared
- Full campaign orchestration complete

---

## 🚀 Execution Sequence

### Step 1: Generate Phase 1 Models
**What:** Create 80 parametric RC frame templates
**Time:** 30-60 seconds
**Command:**
```bash
cd project
python -c "from src.modeling.phase1_generator import generate_phase1_models; models = generate_phase1_models('models/openseespy'); print(f'✓ Generated {len(models)} models')"
```

**Output:** 80 JSON files in `models/openseespy/`
- Format: `frame_{height}s_{framework}_z{zone}.json`
- Example: `frame_10s_smrf_z3.json`

---

### Step 2: Run Pilot Test
**What:** 2-minute validation with 2 GMs/zone
**Time:** 2-5 minutes
**Command:**
```bash
cd project
python -c "
from src.ida.phase2_executor import Phase2Executor
executor = Phase2Executor('config/analysis_config.yaml')
results = executor.run_full_campaign(n_gm_per_zone=2, sample_gm_per_building=2, use_verified=True)
print(f'✓ Pilot: {len(results)} records')
"
```

**Expected Output:** 32-64 records validating infrastructure
**Validates:** GMloader, IDA runner, data pipeline

---

### Step 3: Full Verified Campaign
**What:** Complete campaign with all verified records
**Time:** 8-12 hours (8-core) | 2-3 hours (64-core cloud)
**Command:**
```bash
cd project
python -c "
from src.ida.phase2_executor import Phase2Executor
executor = Phase2Executor('config/analysis_config.yaml')
results = executor.run_full_campaign(n_gm_per_zone=8, use_verified=True)
print(f'✓ Complete: {len(results):,} records generated')
"
```

**Expected Output:** `ida_results_verified.csv` (~51,200 records, 100-150 MB)

---

## 📊 Campaign Details

### Phase 1 Models
| Parameter | Value |
|-----------|-------|
| Stories | 5, 7, 10, 12, 15 |
| Frameworks | Non-Sway, OMRF, IMRF, SMRF |
| Zones | I, II, III, IV |
| Total Models | 80 |
| Compliance | BNBC 2020 |

### Verified Ground Motions (PEER NGA-West 2)
| Zone | Records | Magnitude Range | Distance (km) | Sources |
|------|---------|-----------------|---------------|---------|
| I (Low) | 8 | M 6.2-7.1 | 8-50 | Northridge, LP, Kobe, Chi-Chi, Duzce, Irpinia |
| II (Moderate) | 8 | M 6.2-7.6 | 7-44 | Northridge, LP, Duzce, Kobe, Chi-Chi, SF |
| III (High) | 12 | M 5.8-7.6 | 8-48 | Multiple events + Kern County, Friuli, Umbria |
| IV (Very High) | 12 | M 5.8-7.5 | 8-43 | Multiple events + additional high-magnitude records |

**Total GMs:** 32-40 verified records across all zones

### IDA Configuration
- **Intensity Measure:** Sa @ T=0.5s, ζ=5%
- **Intensity Range:** 0.05g → 1.50g
- **Step Size:** ~0.10g (16 levels)
- **Analysis Duration:** 20 seconds post-earthquake
- **Time Step:** 0.005 seconds
- **Convergence Tolerance:** 1.0e-8

### Expected Output
- **Total Records:** 80 buildings × 32 GMs × 16 intensities = ~40,960 records (achievable)
  - Includes some zone-specific variations
  - Actual: ~51,200 if all combinations complete
- **File Format:** CSV with columns:
  - building_id, zone, gm_id, intensity_sa_g
  - pidr, pga_g, pgv_cm_s, residual_drift
  - damage_state, element_max_strain, convergence_info
- **File Size:** 100-150 MB
- **Execution Time:**
  - 8-core: 8-12 hours
  - 16-core: 4-6 hours
  - 64-core cloud: 1-2 hours (recommended)

---

## 💻 Running the Full Sequence

### All-in-One Master Script
```bash
cd /workspaces/ML_RCC_Research-share/project
python run_phase2_full.py
```
This executes all 3 steps sequentially:
1. Generate Phase 1 models
2. Run pilot test
3. Execute full campaign

**Total Time:** 8-12+ hours (depending on hardware)

### Step-by-Step (Manual)
```bash
cd project

# Step 1: Phase 1 models (30-60 sec)
python execute_phase2_demo.py

# When complete, full results saved to:
# - models/openseespy/ (80 models)
# - data/processed/ida_results_verified.csv (51,200+ records)
```

---

## 📁 File Structure After Execution

```
project/
├── models/
│   └── openseespy/
│       ├── frame_5s_nonsway_z1.json      ✓ 80 models total
│       ├── frame_5s_nonsway_z2.json
│       ├── frame_5s_nonsway_z3.json
│       ├── frame_5s_nonsway_z4.json
│       ├── frame_5s_omrf_z1.json
│       └── ... (80 files total)
│
├── data/
│   └── processed/
│       ├── ida_results_verified.csv        ✓ Main output (100-150 MB)
│       └── phase2_campaign_stats.json      ✓ Statistics summary
│
└── results/
    ├── logs/
    │   └── phase2_execution_*.log          ✓ Detailed logs
    └── ida_results/
        └── campaign_summary.txt            ✓ Summary report
```

---

## ✅ Verification Checklist

Before starting:
- [ ] Phase 1 directory exists: `project/models/openseespy/`
- [ ] Data directory exists: `project/data/processed/`
- [ ] Config files present: `config/bnbc_parameters.yaml`, `analysis_config.yaml`
- [ ] Python 3.9+ environment active
- [ ] Critical packages installed: numpy, pandas, scipy

After Phase 1:
- [ ] 80 model JSON files created in `models/openseespy/`
- [ ] Each model has 5-15 story buildings

After Pilot Test:
- [ ] 32-64 records generated
- [ ] No convergence errors (or minimal)
- [ ] PIDR values reasonable (0.005-0.05 range typical)

After Full Campaign:
- [ ] 40,000+ records generated (expect 51,200)
- [ ] `ida_results_verified.csv` present (~100-150 MB)
- [ ] Campaign statistics logged
- [ ] Execution time logged

---

## 🔍 Monitoring Execution

### Check Progress
While execution is running:
```bash
# Monitor file size growth
tail -f project/data/processed/ida_results_verified.csv | wc -l

# Check logs
tail -f project/results/logs/phase2_execution_*.log

# Monitor system resources
top -p $(pgrep -f "python.*execute")  # If on local machine
```

### Expected Log Messages
```
INFO: Loading Phase 1 models...
INFO: ✓ Loaded 80 Phase 1 models
INFO: Preparing verified ground motion records...
INFO: ✓ Prepared ground motion datasets for 4 zones
INFO: Starting multi-stripe IDA analysis...
INFO: Processing building 1/80: frame_5s_nonsway_z1
...
INFO: Results saved: data/processed/ida_results_verified.csv (51200 rows)
INFO: PHASE 2 EXECUTION COMPLETE
```

---

## 🚨 Troubleshooting

### Issue: "No models found"
**Solution:** Ensure Phase 1 generation ran successfully
```bash
ls -la project/models/openseespy/ | wc -l  # Should show ~82 (80 models + .gitignore)
```

### Issue: "Verified records insufficient"
**Solution:** The VerifiedGMLoader has fallback records, but ensure it's initialized
```bash
python -c "from src.ida.verified_gm_loader import VerifiedGMLoader; loader = VerifiedGMLoader(); print(loader.summary_stats())"
```

### Issue: "OpenSeesPy not found" (Demo Mode)
**Solution:** This is expected in some environments. Demo mode will create synthetic data for testing ML pipeline.

### Issue: Long execution time
**Recommendation:** Use cloud computing
- AWS c5.16xlarge: 64 cores → 1-2 hours
- Google Cloud n1-highmem-64: 64 CPU → 1-2 hours
- Estimated cost: $10-20 for full campaign

---

## 📈 Next Steps (Phase 3)

Once `ida_results_verified.csv` is generated:

1. **Load data:**
   ```python
   import pandas as pd
   data = pd.read_csv('data/processed/ida_results_verified.csv')
   print(f"Dataset: {len(data)} records, {len(data.columns)} features")
   ```

2. **Feature engineering** (building + seismic parameters)

3. **ML model training:**
   - Linear Regression baseline
   - Random Forest (50-200 trees)
   - XGBoost (50-200 boosting rounds)
   - Neural Network (2-3 hidden layers, 64-128 neurons)

4. **Model evaluation:**
   - Cross-validation (k-fold)
   - Test set performance (R², RMSE, MAE)
   - SHAP importance analysis

5. **Fragility curves:**
   - Classify PIDR into damage states (IO, LS, CP, Collapse)
   - Generate probability curves
   - Visualize per zone and building type

---

## 🎯 Success Criteria

Once complete, verify:
- ✅ 40,000-52,000 records in `ida_results_verified.csv`
- ✅ All columns present (building_id, zone, pidr, damage_state, etc.)
- ✅ PIDR values in expected range (0.001-0.10)
- ✅ No missing values (NaN count < 1%)
- ✅ Damage state distribution reasonable:
  - No Damage: ~30-40%
  - IO: ~25-35%
  - LS: ~15-25%
  - CP: ~5-15%
  - Collapse: <5%

---

**Ready to Execute? Run:**
```bash
cd /workspaces/ML_RCC_Research-share/project
python run_phase2_full.py
```

**Estimated Total Time:** 8-12 hours on 8-core | 1-3 hours on 64-core cloud

**Questions?** Check individual module documentation:
- Phase 1: `src/modeling/rc_frame.py`, `phase1_generator.py`
- Phase 2: `src/ida/phase2_executor.py`, `verified_gm_loader.py`
- Config: `config/bnbc_parameters.yaml`, `analysis_config.yaml`
