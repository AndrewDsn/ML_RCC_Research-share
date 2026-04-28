#!/usr/bin/env python3
"""
Phase 3 ML Training Pipeline - Quick Execution Script

Run complete ML training pipeline:
1. Load Phase 2 IDA results
2. Engineer features
3. Train all models (LR, RF, XGBoost, NN)
4. Evaluate and compare
5. SHAP analysis
6. Save results

Prerequisite: Complete Phase 2 first (run_phase2_full.py)
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from src.ml.phase3_executor import Phase3Executor, Phase3Config
from src.utils.logger import ProjectLogger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Execute Phase 3 ML training pipeline"""
    
    logger = ProjectLogger(__name__)
    
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: ML TRAINING PIPELINE")
    logger.info("="*80 + "\n")
    
    # Configuration
    config = Phase3Config(
        phase2_results_file="results/phase2_ida_results.csv",
        output_dir="results/phase3_ml",
        test_size=0.2,              # 20% test set
        validation_size=0.15,       # 15% validation of training
        train_all_models=True,      # Train all 4 model types
        use_hyperparameter_tuning=False,  # Set True for more tuning
        random_seed=42
    )
    
    logger.info("Configuration:")
    logger.info(f"  Phase 2 Results:  {config.phase2_results_file}")
    logger.info(f"  Output Directory: {config.output_dir}")
    logger.info(f"  Test Size:        {config.test_size*100:.0f}%")
    logger.info(f"  Validation Size:  {config.validation_size*100:.0f}%")
    logger.info(f"  Random Seed:      {config.random_seed}")
    logger.info("")
    
    # Check if Phase 2 results exist
    if not Path(config.phase2_results_file).exists():
        logger.error(f"Phase 2 results not found: {config.phase2_results_file}")
        logger.error("Please complete Phase 2 first by running: python run_phase2_full.py")
        return 1
    
    # Execute Phase 3
    try:
        executor = Phase3Executor(config)
        executor.run_full_pipeline()
        
        logger.info("\n" + "="*80)
        logger.info("✓ PHASE 3 COMPLETE")
        logger.info("="*80)
        logger.info("\nNext Steps:")
        logger.info("  1. Review model comparison in: results/phase3_ml/model_comparison.csv")
        logger.info("  2. Check test results in:      results/phase3_ml/test_results.csv")
        logger.info("  3. Examine feature importance: results/phase3_ml/feature_importance_*.csv")
        logger.info("  4. View plots in:              results/phase3_ml/plots/")
        logger.info("\nTo proceed to Phase 4 (Fragility Curves):")
        logger.info("  python execute_phase4.py")
        logger.info("="*80 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Phase 3 execution failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
