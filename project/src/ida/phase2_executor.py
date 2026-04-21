"""
Phase 2 Executor: Orchestrates IDA Analysis Campaign

This module coordinates the complete Phase 2 (IDA Analysis & Data Generation) workflow:
1. Load/generate ground motion records for all BNBC seismic zones
2. Execute multi-stripe IDA analysis across all 80 parametric RC frame models
3. Compile results, validate quality, and generate summary statistics
4. Export master dataset for Phase 3 ML training

Usage:
    from src.ida.phase2_executor import Phase2Executor
    executor = Phase2Executor(config_path='config/analysis_config.yaml')
    results_df = executor.run_full_campaign(n_gm_per_zone=100)
    
Author: ML Seismic Drift Research Team
Created: April 21, 2026
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd
import yaml

from src.modeling.rc_frame import RCFrame
from src.ida.ground_motion_manager import Phase2GroundMotionGenerator
from src.ida.phase2_runner import Phase2IDAAnalyzer, IDAResult
from src.utils.logger import ProjectLogger


@dataclass
class Phase2Config:
    """Phase 2 execution configuration"""
    
    building_heights: List[int] = None
    framework_types: List[str] = None
    seismic_zones: List[int] = None
    n_gm_per_zone: int = 100  # GMs per zone
    intensity_levels: int = 16  # Sa levels (0.05-1.50g)
    models_dir: str = "models/openseespy"
    output_dir: str = "data/processed"
    config_path: str = "config/analysis_config.yaml"
    random_seed: int = 42
    
    def __post_init__(self):
        """Set defaults if not provided"""
        if self.building_heights is None:
            self.building_heights = [5, 7, 10, 12, 15]
        if self.framework_types is None:
            self.framework_types = ['nonsway', 'omrf', 'imrf', 'smrf']
        if self.seismic_zones is None:
            self.seismic_zones = [1, 2, 3, 4]


class Phase2Executor:
    """
    Orchestrates complete Phase 2 IDA Analysis campaign execution.
    
    Responsibilities:
    - Load all 80 parametric RC frame models from Phase 1
    - Generate or load ground motion records for all seismic zones
    - Execute multi-stripe IDA for each building-zone combination
    - Compile and validate results
    - Generate summary statistics and fragility data
    
    Attributes:
        config (Phase2Config): Execution configuration
        logger (ProjectLogger): Logging handler
        gm_generator (Phase2GroundMotionGenerator): GM generation module
        ida_analyzer (Phase2IDAAnalyzer): IDA execution module
    """
    
    def __init__(self, config_path: str = "config/analysis_config.yaml"):
        """
        Initialize Phase 2 Executor.
        
        Args:
            config_path: Path to analysis_config.yaml
        """
        self.config_path = config_path
        self.config = Phase2Config(config_path=config_path)
        
        # Initialize logger
        self.logger = ProjectLogger(
            name='phase2_executor',
            log_level='INFO',
            file_logging=True
        )
        
        # Initialize sub-modules
        self.gm_generator = Phase2GroundMotionGenerator(config_path)
        self.ida_analyzer = Phase2IDAAnalyzer(config_path)
        
        # Create output directory
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Phase2Executor initialized: {self.config}")
    
    def load_phase1_models(self) -> Dict[str, RCFrame]:
        """
        Load all 80 parametric RC frame models from Phase 1.
        
        Returns:
            Dictionary mapping model ID to RCFrame instance
            Key format: "frame_{n}s_{framework}_z{zone}"
        
        Raises:
            FileNotFoundError: If Phase 1 models not found
        """
        models_dir = Path(self.config.models_dir)
        
        if not models_dir.exists():
            self.logger.error(f"Models directory not found: {models_dir}")
            raise FileNotFoundError(f"Phase 1 models not found at {models_dir}")
        
        models = {}
        model_files = list(models_dir.glob("frame_*.json"))
        
        self.logger.info(f"Loading {len(model_files)} Phase 1 parametric models...")
        
        for model_file in model_files:
            try:
                frame = RCFrame.load_model(str(model_file))
                model_id = model_file.stem  # e.g., "frame_5s_smrf_z3"
                models[model_id] = frame
                self.logger.debug(f"Loaded model: {model_id}")
            except Exception as e:
                self.logger.warning(f"Failed to load {model_file}: {e}")
        
        self.logger.info(f"Successfully loaded {len(models)}/{len(model_files)} models")
        
        if len(models) != 80:
            self.logger.warning(f"Expected 80 models, loaded {len(models)}")
        
        return models
    
    def prepare_ground_motions(self) -> Dict[int, any]:
        """
        Generate ground motion datasets for all seismic zones.
        
        Returns:
            Dictionary mapping zone ID to GroundMotionDataset
        
        Note:
            Uses Phase2GroundMotionGenerator with synthetic GMs.
            For production, replace with PEER NGA database loader.
        """
        self.logger.info(
            f"Generating synthetic ground motions "
            f"({self.config.n_gm_per_zone} per zone, 4 zones)..."
        )
        
        gm_datasets = self.gm_generator.generate_all_zone_datasets(
            n_records=self.config.n_gm_per_zone
        )
        
        self.logger.info(f"Generated {len(gm_datasets)} zone datasets")
        for zone_id, gm_set in gm_datasets.items():
            pgas = [r['pga'] for r in gm_set.records]
            pga_min, pga_max = min(pgas), max(pgas)
            self.logger.info(
                f"  Zone {zone_id}: {len(gm_set.records)} records, "
                f"PGA range: {pga_min:.3f}-{pga_max:.3f}g"
            )
        
        return gm_datasets
    
    def run_building_ida_analysis(
        self,
        model_id: str,
        frame: RCFrame,
        gm_datasets: Dict[int, any],
        sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Execute multi-stripe IDA for a single building across all zones.
        
        Args:
            model_id: Building identifier (e.g., "frame_10s_smrf_z3")
            frame: RCFrame instance
            gm_datasets: Dictionary of GroundMotionDataset by zone
            sample_size: Limit number of GMs per zone (for testing). None = all.
        
        Returns:
            DataFrame with IDA results for this building
            Columns: building_id, zone, pidr, pga, damage_state, ...
        """
        # Extract zone from model_id
        zone = int(model_id.split('_z')[-1])
        
        # Get GM dataset for this zone
        if zone not in gm_datasets:
            self.logger.warning(f"No GM dataset for zone {zone}, skipping {model_id}")
            return pd.DataFrame()
        
        gm_dataset = gm_datasets[zone]
        
        self.logger.info(
            f"Running IDA: {model_id} (zone {zone}, {len(gm_dataset.records)} GMs × 16 intensities)"
        )
        
        try:
            # Create intensity levels for multi-stripe analysis
            intensity_levels = np.linspace(0.05, 1.50, self.config.intensity_levels)
            
            # Run multi-stripe IDA
            results_df = self.ida_analyzer.run_multi_stripe_ida(
                frame_model=frame,
                gm_dataset=gm_dataset,
                building_id=model_id,
                zone=zone,
                intensity_levels=intensity_levels
            )
            
            if not results_df.empty:
                self.logger.info(
                    f"Completed: {model_id} with {len(results_df)} records"
                )
            
            return results_df
            
        except Exception as e:
            self.logger.error(f"IDA failed for {model_id}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return pd.DataFrame()
    
    def run_full_campaign(
        self,
        n_gm_per_zone: Optional[int] = None,
        sample_gm_per_building: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Execute complete Phase 2 IDA analysis campaign.
        
        Arguments:
            n_gm_per_zone: Override GM count per zone (default: config value)
            sample_gm_per_building: Limit GMs per building for quick testing
                                   (default: None = all)
        
        Returns:
            Consolidated DataFrame with all IDA results (~7,500-10,000 rows)
        
        Example:
            executor = Phase2Executor()
            
            # Full campaign (production)
            results = executor.run_full_campaign(n_gm_per_zone=100)
            
            # Quick test (5 GMs per zone)
            results = executor.run_full_campaign(
                n_gm_per_zone=5,
                sample_gm_per_building=2
            )
        """
        start_time = datetime.now()
        self.logger.info("=" * 80)
        self.logger.info("PHASE 2 EXECUTOR: IDA ANALYSIS CAMPAIGN")
        self.logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
        
        # Override GM count if provided
        if n_gm_per_zone:
            self.config.n_gm_per_zone = n_gm_per_zone
        
        # Step 1: Load Phase 1 models
        self.logger.info("\n[Step 1/4] Loading Phase 1 parametric models...")
        models = self.load_phase1_models()
        
        if not models:
            self.logger.error("No models loaded. Aborting campaign.")
            return pd.DataFrame()
        
        # Step 2: Prepare ground motions
        self.logger.info("\n[Step 2/4] Preparing ground motion records...")
        gm_datasets = self.prepare_ground_motions()
        
        # Step 3: Execute IDA analysis
        self.logger.info("\n[Step 3/4] Executing multi-stripe IDA analysis...")
        all_results = []
        
        model_list = sorted(models.keys())
        total_models = len(model_list)
        
        for idx, model_id in enumerate(model_list, 1):
            self.logger.info(f"\nProcessing building {idx}/{total_models}: {model_id}")
            
            frame = models[model_id]
            building_results = self.run_building_ida_analysis(
                model_id=model_id,
                frame=frame,
                gm_datasets=gm_datasets,
                sample_size=sample_gm_per_building
            )
            
            if not building_results.empty:
                all_results.append(building_results)
        
        # Step 4: Compile and validate results
        self.logger.info("\n[Step 4/4] Compiling and validating results...")
        
        if all_results:
            master_results = pd.concat(all_results, ignore_index=True)
        else:
            self.logger.error("No results generated. Campaign failed.")
            return pd.DataFrame()
        
        # Save results
        output_path = self.output_dir / "ida_results.csv"
        master_results.to_csv(output_path, index=False)
        self.logger.info(f"Results saved: {output_path} ({len(master_results)} rows)")
        
        # Generate statistics
        self._generate_campaign_statistics(master_results)
        
        # Timing
        end_time = datetime.now()
        duration = end_time - start_time
        self.logger.info(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Total duration: {duration}")
        self.logger.info("=" * 80)
        
        return master_results
    
    def _generate_campaign_statistics(self, results_df: pd.DataFrame):
        """
        Generate and log summary statistics for IDA campaign.
        
        Args:
            results_df: Master results DataFrame
        """
        stats = {
            "total_analyses": len(results_df),
            "unique_buildings": results_df['building_id'].nunique(),
            "unique_zones": results_df['zone'].nunique(),
            "pidr_mean": results_df['pidr'].mean(),
            "pidr_median": results_df['pidr'].median(),
            "pidr_std": results_df['pidr'].std(),
            "pidr_min": results_df['pidr'].min(),
            "pidr_max": results_df['pidr'].max(),
            "damage_state_distribution": results_df['damage_state'].value_counts().to_dict()
        }
        
        # Log statistics
        self.logger.info("\n[ CAMPAIGN STATISTICS ]")
        self.logger.info(f"Total analyses: {stats['total_analyses']}")
        self.logger.info(f"Unique buildings: {stats['unique_buildings']}")
        self.logger.info(f"Unique zones: {stats['unique_zones']}")
        self.logger.info(f"PIDR statistics:")
        self.logger.info(f"  Mean: {stats['pidr_mean']:.6f}")
        self.logger.info(f"  Median: {stats['pidr_median']:.6f}")
        self.logger.info(f"  Std Dev: {stats['pidr_std']:.6f}")
        self.logger.info(f"  Range: [{stats['pidr_min']:.6f}, {stats['pidr_max']:.6f}]")
        self.logger.info(f"Damage state distribution:")
        for state, count in stats['damage_state_distribution'].items():
            pct = 100 * count / len(results_df)
            self.logger.info(f"  {state}: {count} ({pct:.1f}%)")
        
        # Save statistics to JSON
        stats_path = self.output_dir / "ida_campaign_statistics.json"
        with open(stats_path, 'w') as f:
            # Convert numpy types for JSON serialization
            json_stats = {}
            for k, v in stats.items():
                if isinstance(v, np.integer):
                    json_stats[k] = int(v)
                elif isinstance(v, np.floating):
                    json_stats[k] = float(v)
                else:
                    json_stats[k] = v
            json.dump(json_stats, f, indent=2)
        
        self.logger.info(f"Statistics saved: {stats_path}")


def run_phase2_campaign(
    config_path: str = "config/analysis_config.yaml",
    n_gm_per_zone: int = 100,
    sample_gm: Optional[int] = None
) -> pd.DataFrame:
    """
    Convenience function to run full Phase 2 campaign.
    
    Args:
        config_path: Path to analysis_config.yaml
        n_gm_per_zone: Ground motions per zone
        sample_gm: Sample GMs per building (for testing)
    
    Returns:
        Master IDA results DataFrame
    
    Usage:
        # Production run
        results = run_phase2_campaign(n_gm_per_zone=100)
        
        # Quick test
        results = run_phase2_campaign(n_gm_per_zone=5, sample_gm=2)
    """
    executor = Phase2Executor(config_path)
    return executor.run_full_campaign(
        n_gm_per_zone=n_gm_per_zone,
        sample_gm_per_building=sample_gm
    )


if __name__ == "__main__":
    """
    Run Phase 2 campaign from command line.
    
    Usage:
        python -m src.ida.phase2_executor
        
    Options (edit as needed):
        - n_gm_per_zone: Number of ground motions per zone
        - sample_gm_per_building: Sample limit for quick testing
    """
    # Quick test with 5 GMs per zone, 3 GMs per building
    results = run_phase2_campaign(
        n_gm_per_zone=5,
        sample_gm=3
    )
    
    print(f"\nPhase 2 campaign completed!")
    print(f"Total records: {len(results)}")
    print(f"\nFirst 10 rows:")
    print(results.head(10))
