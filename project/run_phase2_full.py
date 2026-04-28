#!/usr/bin/env python3
"""
Master Phase 2 Execution: Full Verified Records Campaign
=========================================================

Complete workflow:
1. Generate Phase 1 parametric RC frame models (80 total)
2. Run quick pilot test (2 GMs/zone, 2 intensities - ~5 min validation)
3. Execute full verified Phase 2 campaign (8 GMs/zone × 16 intensities)

Total Time: ~8-12 hours (8-core) | 2-3 hours (64-core cloud)
Output: ida_results_verified.csv (~51,200 records, 100-150 MB)
"""

import sys
import json
import traceback
from pathlib import Path
from datetime import datetime, timedelta

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from src.modeling.phase1_generator import generate_phase1_models
from src.ida.phase2_executor import Phase2Executor
from src.utils.logger import ProjectLogger
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("\n" + "="*90)
print("MASTER PHASE 2 EXECUTION: FULL VERIFIED CAMPAIGN")
print("="*90)

# ============================================================================
# STEP 1: Generate Phase 1 Models
# ============================================================================
print("\n" + "="*90)
print("STEP 1: GENERATE PHASE 1 PARAMETRIC RC FRAME MODELS")
print("="*90)

try:
    models_dir = Path("models/openseespy")
    existing_models = list(models_dir.glob("frame_*.json"))
    
    if len(existing_models) >= 80:
        print(f"✓ Phase 1 models already exist ({len(existing_models)} found)")
        print(f"  Location: {models_dir}")
    else:
        print(f"Generating 80 parametric RC frame models...")
        print(f"  Heights: 5, 7, 10, 12, 15 stories")
        print(f"  Frameworks: Non-Sway (R=1.5), OMRF (R=3), IMRF (R=4), SMRF (R=5)")
        print(f"  Zones: Zone I, II, III, IV (BNBC 2020)")
        print(f"  Total: 5 × 4 × 4 = 80 models")
        
        models = generate_phase1_models(output_dir=str(models_dir))
        print(f"✓ Generated {len(models)} Phase 1 models")
        
except Exception as e:
    print(f"✗ Phase 1 generation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 2: Quick Pilot Test (Validation)
# ============================================================================
print("\n" + "="*90)
print("STEP 2: QUICK PILOT TEST - VALIDATE INFRASTRUCTURE")
print("="*90)
print("Running quick validation with reduced dataset:")
print("  - Ground Motions: 2 per zone (8 total across 4 zones)")
print("  - Buildings: 2 heights × 2 frameworks = 4 total")
print("  - Intensities: 2 levels (quick validation)")
print("  - Expected Time: 2-5 minutes")
print("  - Expected Records: ~32-64 records")

try:
    executor_pilot = Phase2Executor("config/analysis_config.yaml")
    
    print("\nRunning pilot verification...")
    results_pilot = executor_pilot.run_full_campaign(
        n_gm_per_zone=2,  # Minimal GMs for quick test
        sample_gm_per_building=2,  # Sample 2 intensities
        use_verified=True  # Use verified records
    )
    
    if len(results_pilot) > 0:
        print(f"✓ Pilot test successful!")
        print(f"  Records generated: {len(results_pilot)}")
        print(f"  Sample output saved: data/processed/ida_results_verified.csv (partial)")
    else:
        print(f"✗ Pilot test generated no results")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Pilot test failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 3: Full Verified Phase 2 Campaign
# ============================================================================
print("\n" + "="*90)
print("STEP 3: FULL VERIFIED PHASE 2 CAMPAIGN")
print("="*90)
print("Executing complete Phase 2 with all verified records:")
print("  - Ground Motions: 8 verified PEER NGA records per zone (32 total)")
print("  - Buildings: 80 parametric RC frames")
print("    • Heights: 5, 7, 10, 12, 15 stories")
print("    • Types: Non-Sway, OMRF, IMRF, SMRF")
print("    • Zones: I, II, III, IV")
print("  - Intensities: 16 levels per GM (Sa 0.05-1.50g)")
print("  - Total Time Histories: ~51,200 records")
print("  - Expected File Size: 100-150 MB")
print("  - Estimated Duration: 6-10 hours (8-core) | 1.5-2.5 hours (64-core cloud)")

start_campaign = datetime.now()

try:
    executor_full = Phase2Executor("config/analysis_config.yaml")
    
    print("\n" + "-"*90)
    print("Starting full campaign...")
    print("-"*90)
    
    results_full = executor_full.run_full_campaign(
        n_gm_per_zone=8,  # Full verified records
        use_verified=True  # Use PEER NGA records
    )
    
    campaign_time = datetime.now() - start_campaign
    
    if len(results_full) > 0:
        print("\n" + "="*90)
        print("✓ PHASE 2 CAMPAIGN COMPLETE!")
        print("="*90)
        print(f"Total Records Generated: {len(results_full):,}")
        print(f"Campaign Duration: {campaign_time}")
        print(f"Output File: data/processed/ida_results_verified.csv")
        print(f"File Size: {len(results_full) * 0.002:.1f} MB (estimated)")
        print(f"\nDataset Breakdown:")
        print(f"  - Buildings: 80 parametric RC frames")
        print(f"  - Ground Motions: 8 verified records/zone × 4 zones = 32 total")
        print(f"  - Intensity Levels: 16 per GM")
        print(f"  - Time Histories: {len(results_full):,}")
        print("="*90)
        
        # Print sample of results
        print(f"\nSample of generated data (first 5 rows):")
        print(results_full.head().to_string())
        
        # Summary statistics
        if 'pidr' in results_full.columns:
            print(f"\nPIDR Statistics:")
            print(f"  Min: {results_full['pidr'].min():.6f}")
            print(f"  Max: {results_full['pidr'].max():.6f}")
            print(f"  Mean: {results_full['pidr'].mean():.6f}")
            print(f"  Median: {results_full['pidr'].median():.6f}")
        
        print(f"\n✓ Ready for Phase 3: ML Model Training")
        print(f"  Next: Load ida_results_verified.csv for feature engineering and ML training")
        
    else:
        print(f"✗ Full campaign generated no results")
        sys.exit(1)
        
except KeyboardInterrupt:
    print("\n✗ Campaign interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"✗ Full campaign failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*90)
print("ALL STEPS COMPLETE!")
print("="*90)
print("✓ Phase 1: Parametric models generated")
print("✓ Phase 2: Pilot test validated")
print("✓ Phase 2: Full verified campaign executed")
print("\nNext Phase: Phase 3 - ML Model Training")
print("="*90 + "\n")
