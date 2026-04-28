#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Phase 1: Generate models
print("\n[1/3] PHASE 1: Generating 80 parametric RC models...")
try:
    from src.modeling.phase1_generator import generate_phase1_models
    models = generate_phase1_models(output_dir="models/openseespy")
    print(f"✓ Generated {len(models)} Phase 1 models\n")
except Exception as e:
    print(f"✗ Phase 1 failed: {e}\n")
    sys.exit(1)

# Phase 2a: Pilot test
print("[2/3] PHASE 2A: Running 2-5 minute pilot validation...")
try:
    from src.ida.phase2_executor import Phase2Executor
    executor = Phase2Executor("config/analysis_config.yaml")
    pilot = executor.run_full_campaign(n_gm_per_zone=2, sample_gm_per_building=2, use_verified=True)
    print(f"✓ Pilot generated {len(pilot)} records (validation successful)\n")
except Exception as e:
    print(f"✗ Pilot failed: {e}\n")
    sys.exit(1)

# Phase 2b: Full campaign
print("[3/3] PHASE 2B: Executing full verified campaign (8-12 hours)...")
try:
    executor = Phase2Executor("config/analysis_config.yaml")
    results = executor.run_full_campaign(n_gm_per_zone=8, use_verified=True)
    print(f"\n✓✓✓ COMPLETE! Generated {len(results):,} verified time histories")
    print(f"    Output: data/processed/ida_results_verified.csv\n")
except Exception as e:
    print(f"✗ Full campaign failed: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
