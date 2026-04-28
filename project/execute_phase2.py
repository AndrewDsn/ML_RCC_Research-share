#!/usr/bin/env python3
"""Quick Phase 2 Verified Records Execution"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.ida.phase2_executor import Phase2Executor
from src.utils.logger import ProjectLogger
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

print("\n" + "="*80)
print("PHASE 2: IDA ANALYSIS WITH VERIFIED RECORDS")
print("="*80)

try:
    # Initialize executor
    executor = Phase2Executor("config/analysis_config.yaml")
    
    # Run with verified records (8 GMs per zone, 16 intensity levels)
    print("\nExecuting Phase 2 with verified PEER NGA-West 2 records...")
    print("Configuration: 8 GMs/zone × 4 zones × 80 buildings × 16 intensities")
    print("Expected: ~51,200 total time histories\n")
    
    results = executor.run_full_campaign(
        n_gm_per_zone=8,  # 8 verified records per zone
        use_verified=True  # Use PEER NGA records
    )
    
    print(f"\n✓ Phase 2 Complete! Generated {len(results):,} records")
    print(f"Results saved to: data/processed/ida_results_verified.csv")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
