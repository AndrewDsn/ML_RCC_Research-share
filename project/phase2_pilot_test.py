#!/usr/bin/env python3
"""
Phase 2 Pilot Test: Quick IDA Analysis Validation

This script runs a quick Phase 2 pilot test to validate:
1. Phase 1 model loading
2. Ground motion generation  
3. IDA analysis executor
4. Results compilation and statistics

Expected outcome: ~5-10 minutes, generates 100-200 IDA analysis records
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ida.phase2_executor import run_phase2_campaign
from src.utils.logger import ProjectLogger

def main():
    """Run Phase 2 pilot test"""
    logger = ProjectLogger(
        name='phase2_pilot',
        log_level='INFO',
        file_logging=True
    )
    
    logger.info("="*80)
    logger.info("PHASE 2 PILOT TEST: IDA ANALYSIS VALIDATION")
    logger.info("="*80)
    logger.info("\nConfiguration:")
    logger.info("  - Ground motions: 2 per zone (synthetic)")
    logger.info("  - Intensity levels: 16 (0.05-1.50g)")
    logger.info("  - Buildings sampled: variable (first GM only, 3 intensities)")
    logger.info("  - Expected records: ~50-100")
    logger.info("  - Expected duration: 2-5 minutes")
    logger.info("\nRunning...\n")
    
    try:
        # Run quick pilot: 2 GMs per zone, sample 2 per building
        results = run_phase2_campaign(
            config_path="config/analysis_config.yaml",
            n_gm_per_zone=2,
            sample_gm=2
        )
        
        if len(results) > 0:
            logger.info(f"\n✓ PILOT SUCCESSFUL!")
            logger.info(f"  Total records generated: {len(results)}")
            logger.info(f"  Unique buildings: {results['building_id'].nunique()}")
            logger.info(f"  Unique zones: {results['zone'].nunique()}")
            logger.info(f"\n  PIDR statistics:")
            logger.info(f"    Mean: {results['pidr'].mean():.6f}")
            logger.info(f"    Min:  {results['pidr'].min():.6f}")
            logger.info(f"    Max:  {results['pidr'].max():.6f}")
            logger.info(f"\n  Damage state distribution:")
            for state, count in results['damage_state'].value_counts().items():
                pct = 100*count/len(results)
                logger.info(f"    {state}: {count} ({pct:.1f}%)")
            
            logger.info(f"\n✓ Results saved to: data/processed/ida_results.csv")
            logger.info("✓ Statistics saved to: data/processed/ida_campaign_statistics.json")
            
            return 0
        else:
            logger.error("No results generated - test failed")
            return 1
            
    except Exception as e:
        logger.error(f"Pilot test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit(main())
