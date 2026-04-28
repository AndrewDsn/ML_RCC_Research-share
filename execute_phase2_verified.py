#!/usr/bin/env python3
"""
Execute Phase 2 IDA Campaign with Verified PEER NGA-West 2 Records
=====================================================================

This script orchestrates the full Phase 2 execution:
1. Generate Phase 1 models (if not exists)
2. Load verified ground motion records
3. Run multi-stripe IDA for all buildings across all zones
4. Compile and export results

Execution Time: 8-12 hours on 8-core machine | 2-3 hours on 64-core cloud
Output: ~51,200 time histories (~100-150 MB CSV file)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import traceback

# Add project to path
project_dir = Path(__file__).parent / "project"
sys.path.insert(0, str(project_dir))

def setup_directories():
    """Create required directories for Phase 2 execution."""
    dirs = [
        project_dir / "models" / "openseespy",
        project_dir / "data" / "raw" / "gm_verified",
        project_dir / "data" / "processed",
        project_dir / "results" / "ida_results",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✓ Directories created/verified")
    return dirs

def generate_phase1_models():
    """Generate Phase 1 parametric RC frame models."""
    print("\n" + "="*70)
    print("PHASE 1: GENERATING PARAMETRIC RC FRAME MODELS")
    print("="*70)
    
    try:
        from src.modeling.phase1_generator import generate_phase1_models
        
        models_dir = project_dir / "models" / "openseespy"
        existing_models = list(models_dir.glob("*.json"))
        
        if len(existing_models) >= 80:
            print(f"✓ Phase 1 models already exist ({len(existing_models)} models found)")
            return existing_models
        
        print("Generating 80 parametric models (5, 7, 10, 12, 15 stories)...")
        models = generate_phase1_models(output_dir=str(models_dir))
        print(f"✓ Generated {len(models)} Phase 1 models")
        return models
        
    except Exception as e:
        print(f"✗ Error generating Phase 1 models: {e}")
        traceback.print_exc()
        return []

def run_phase2_verified_campaign():
    """Execute Phase 2 IDA analysis with verified records."""
    print("\n" + "="*70)
    print("PHASE 2: IDA ANALYSIS WITH VERIFIED PEER NGA-WEST 2 RECORDS")
    print("="*70)
    
    try:
        from src.ida.phase2_executor import Phase2Executor, Phase2Config
        from src.utils.logger import ProjectLogger
        
        # Initialize logger
        log_dir = project_dir / "results" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        logger = ProjectLogger(log_dir=str(log_dir))
        
        # Configure Phase 2 campaign
        config = Phase2Config(
            building_stories=[5, 7, 10, 12, 15],
            frameworks=["Non-Sway", "OMRF", "IMRF", "SMRF"],
            seismic_zones=[1, 2, 3, 4],
            n_gm_per_zone=8,  # Reduced but verified records
            intensity_levels=16,
            use_verified=True,  # Use PEER NGA-West 2 records
            output_dir=str(project_dir / "data" / "processed"),
        )
        
        logger.info(f"Phase 2 Configuration:")
        logger.info(f"  - Buildings: {len(config.building_stories)} heights × {len(config.frameworks)} frameworks = {len(config.building_stories) * len(config.frameworks)} total")
        logger.info(f"  - Ground Motions: {config.n_gm_per_zone} verified records/zone × {len(config.seismic_zones)} zones = {config.n_gm_per_zone * len(config.seismic_zones)} total")
        logger.info(f"  - Intensities: {config.intensity_levels} levels per GM")
        logger.info(f"  - Expected Records: ~{len(config.building_stories) * len(config.frameworks) * config.n_gm_per_zone * len(config.seismic_zones) * config.intensity_levels:,} time histories")
        
        # Initialize executor
        executor = Phase2Executor(config, logger)
        
        # Load Phase 1 models
        logger.info("Loading Phase 1 models...")
        models = executor.load_phase1_models()
        logger.info(f"✓ Loaded {len(models)} Phase 1 models")
        
        # Prepare verified ground motions
        logger.info("Preparing verified PEER NGA-West 2 ground motion records...")
        gm_datasets = executor.prepare_ground_motions()
        logger.info(f"✓ Prepared ground motion datasets for {len(gm_datasets)} zones")
        
        # Run full campaign
        logger.info("Starting IDA multi-stripe analysis (this may take 8-12 hours)...")
        start_time = datetime.now()
        
        results = executor.run_full_campaign()
        
        elapsed = datetime.now() - start_time
        logger.info(f"✓ Phase 2 campaign completed in {elapsed}")
        
        # Generate statistics
        logger.info("Generating campaign statistics...")
        stats = executor._generate_campaign_statistics(results)
        
        # Export results
        results_file = Path(config.output_dir) / "ida_results_verified.csv"
        results.to_csv(results_file, index=False)
        logger.info(f"✓ Results exported: {results_file} ({results_file.stat().st_size / 1e6:.1f} MB)")
        
        # Export statistics
        stats_file = Path(config.output_dir) / "phase2_campaign_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"✓ Statistics exported: {stats_file}")
        
        logger.info("\n" + "="*70)
        logger.info("PHASE 2 EXECUTION COMPLETE")
        logger.info("="*70)
        logger.info(f"Total Records Generated: {len(results):,}")
        logger.info(f"Execution Time: {elapsed}")
        logger.info(f"Output File: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"✗ Error during Phase 2 execution: {e}")
        traceback.print_exc()
        return None

def main():
    """Main execution orchestrator."""
    print("\n" + "="*70)
    print("ML-BASED SEISMIC DRIFT PREDICTION - FULL PHASE 2 EXECUTION")
    print("Using Verified PEER NGA-West 2 Earthquake Records")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Setup directories
        setup_directories()
        
        # Generate Phase 1 models
        models = generate_phase1_models()
        if not models:
            print("✗ Phase 1 model generation failed. Aborting.")
            return False
        
        # Run Phase 2 verified campaign
        results = run_phase2_verified_campaign()
        if results is None:
            print("✗ Phase 2 execution failed. Check logs for details.")
            return False
        
        print(f"\n✓ Full execution complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except KeyboardInterrupt:
        print("\n✗ Execution interrupted by user")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
