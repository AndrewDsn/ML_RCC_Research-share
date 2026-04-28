#!/usr/bin/env python3
"""
Phase 2 Verified Ground Motion Campaign Runner

Executes IDA analysis campaign using verified PEER NGA-West 2 earthquake records.

This script:
1. Loads 80 parametric RC frame models from Phase 1
2. Prepares verified ground motion records (8-12 per seismic zone)
3. Runs multi-stripe IDA analysis (16 intensity levels per record)
4. Generates master dataset for Phase 3 ML model training

Verified Dataset Characteristics:
- Total records: ~32-48 (8-12 per zone × 4 zones)
- Source: PEER NGA-West 2 (quality-controlled)
- Magnitude range: 5.8-7.6
- Distance range: 1.5-50 km
- Site classes: A-E (representative diversity)
- Total analysis count: 80 models × 40 GMs avg × 16 intensities = ~51,200 time histories

Execution Time Estimates:
- Single-core (laptop): 3-5 days
- 8-core workstation: 8-12 hours
- 64-core cloud (recommended): 2-3 hours
- With parallelization (4-8 processes): 1-2 hours

Output:
- data/processed/ida_results_verified.csv (~100-150 MB)
- Includes: PIDR, PGA, damage states, element strains for all analyses

Usage:
    # Basic execution with 8 verified records per zone
    python phase2_verified_runner.py
    
    # Custom record count
    python phase2_verified_runner.py --n-gm 5
    
    # Test run (quick validation)
    python phase2_verified_runner.py --n-gm 3 --sample-gm 2

Author: ML Seismic Drift Research Team
Created: April 22, 2026
"""

import argparse
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ida.phase2_executor import Phase2Executor
from src.utils.logger import ProjectLogger


def main():
    """Execute Phase 2 verified GM campaign."""
    
    parser = argparse.ArgumentParser(
        description="Phase 2 Verified Ground Motion IDA Campaign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Production run with 8 verified records per zone
  python phase2_verified_runner.py
  
  # Custom record count (5 per zone)
  python phase2_verified_runner.py --n-gm 5
  
  # Quick test (3 records per zone, sample 2 GMs per building)
  python phase2_verified_runner.py --n-gm 3 --sample-gm 2
        """
    )
    
    parser.add_argument(
        '--n-gm',
        type=int,
        default=8,
        help='Number of verified records per seismic zone (default: 8)'
    )
    
    parser.add_argument(
        '--sample-gm',
        type=int,
        default=None,
        help='Sample N records per building for quick testing (default: None = all)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/analysis_config.yaml',
        help='Path to analysis configuration file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = ProjectLogger(
        name='phase2_verified_runner',
        log_level='INFO',
        file_logging=True
    )
    
    logger.info("=" * 90)
    logger.info("PHASE 2 VERIFIED GROUND MOTION IDA CAMPAIGN")
    logger.info("=" * 90)
    logger.info(f"Configuration:")
    logger.info(f"  - Verified records/zone: {args.n_gm}")
    logger.info(f"  - Sample GMs per building: {args.sample_gm or 'All'}")
    logger.info(f"  - Config file: {args.config}")
    logger.info(f"  - Output directory: {args.output_dir}")
    logger.info("=" * 90)
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize Phase 2 Executor
        logger.info("\nInitializing Phase 2 Executor...")
        executor = Phase2Executor(config_path=args.config)
        
        # Execute verified records campaign
        logger.info("\nStarting verified ground motion IDA campaign...")
        logger.info(f"Expected output: ~{args.n_gm * 4 * 80 * 16:,} time histories")
        
        results_df = executor.run_full_campaign(
            n_gm_per_zone=args.n_gm,
            sample_gm_per_building=args.sample_gm,
            use_verified=True  # USE VERIFIED RECORDS
        )
        
        if results_df.empty:
            logger.error("Campaign failed: No results generated")
            return 1
        
        # Summary
        logger.info("\n" + "=" * 90)
        logger.info("CAMPAIGN SUMMARY")
        logger.info("=" * 90)
        logger.info(f"Total records generated: {len(results_df):,}")
        logger.info(f"Buildings analyzed: {results_df['building_id'].nunique()}")
        logger.info(f"Seismic zones: {sorted(results_df['zone'].unique())}")
        logger.info(f"PIDR statistics:")
        logger.info(f"  - Mean: {results_df['pidr'].mean():.4f}")
        logger.info(f"  - Median: {results_df['pidr'].median():.4f}")
        logger.info(f"  - Std Dev: {results_df['pidr'].std():.4f}")
        logger.info(f"  - Range: {results_df['pidr'].min():.4f} - {results_df['pidr'].max():.4f}")
        
        # Damage state distribution
        if 'damage_state' in results_df.columns:
            logger.info(f"Damage state distribution:")
            for state, count in results_df['damage_state'].value_counts().items():
                pct = 100 * count / len(results_df)
                logger.info(f"  - {state}: {count:,} ({pct:.1f}%)")
        
        logger.info("=" * 90)
        logger.info("✓ Phase 2 verified records campaign completed successfully!")
        logger.info("✓ Results saved to: data/processed/ida_results_verified.csv")
        logger.info("✓ Ready for Phase 3: ML model training")
        logger.info("=" * 90)
        
        return 0
        
    except Exception as e:
        logger.error(f"Campaign failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == '__main__':
    sys.exit(main())
