"""
Phase 2: Ground Motion Preparation & Management

Handles loading, scaling, and managing ground motion records for IDA analysis.

This module prepares ground motion records per BNBC 2020 seismic design spectrum
by implementing intensity scaling compatible with incremental dynamic analysis.

Key Functions:
- load_gm_records(): Load GM records from various formats
- scale_to_spectrum(): Scale records to match target spectra per zone
- validate_gm_properties(): Verify GM record integrity
- compile_gm_dataset(): Create analysis-ready GM database
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GroundMotionDataset:
    """
    Container for ground motion record collection with BNBC 2020 compatibility
    
    Attributes:
        records: List of GMRecord instances
        zones: Seismic zones represented
        metadata: Dataset-level metadata
    """
    
    def __init__(self, zone: int = 3, n_records: int = 500):
        """
        Initialize ground motion dataset
        
        Args:
            zone: BNBC seismic zone (1-4)
            n_records: Target number of ground motion records
        """
        self.zone = zone
        self.n_records = n_records
        self.records: List[Dict] = []
        self.metadata = {
            'zone': zone,
            'date_created': pd.Timestamp.now(),
            'n_records': 0,
            'intensity_levels': list(np.linspace(0.05, 1.50, 16).round(3)),
        }

    def add_record(self, record_id: str, time_series: np.ndarray, dt: float,
                   source: str = 'synthetic', magnitude: float = 0.0,
                   distance: float = 0.0):
        """
        Add ground motion record to dataset
        
        Args:
            record_id: Unique identifier for record
            time_series: Acceleration time history [g]
            dt: Time step [seconds]
            source: Source (PEER NGA, synthetic, etc.)
            magnitude: Earthquake magnitude (if known)
            distance: Distance to epicenter (if known)
        """
        record = {
            'id': record_id,
            'time': np.arange(len(time_series)) * dt,
            'acceleration': time_series,
            'dt': dt,
            'duration': len(time_series) * dt,
            'pga': np.max(np.abs(time_series)),
            'source': source,
            'magnitude': magnitude,
            'distance': distance,
        }
        
        self.records.append(record)
        self.metadata['n_records'] = len(self.records)
        
        logger.info(f"Added GM record {record_id} (PGA={record['pga']:.3f}g)")

    def get_intensity_levels(self) -> np.ndarray:
        """Get target intensity levels for multi-stripe IDA"""
        return np.array(self.metadata['intensity_levels'])

    def scale_to_intensity(self, record_idx: int, target_intensity: float,
                           ref_period: float = 0.5) -> np.ndarray:
        """
        Scale ground motion to target intensity measure
        
        Args:
            record_idx: Index of record to scale
            target_intensity: Target Sa(T=0.5s) [g]
            ref_period: Reference period for intensity measure [s]
            
        Returns:
            Scaled acceleration time series
        """
        if record_idx >= len(self.records):
            raise ValueError(f"Record index {record_idx} out of range")
        
        record = self.records[record_idx]
        current_pga = record['pga']
        
        if current_pga <= 0:
            logger.warning(f"PGA is zero or negative for record {record_idx}")
            return record['acceleration']
        
        # Simple scaling: proportional to target intensity
        scale_factor = target_intensity / current_pga
        scaled_acc = record['acceleration'] * scale_factor
        
        logger.debug(f"Scaled record {record_idx} by {scale_factor:.3f} to {target_intensity:.3f}g")
        
        return scaled_acc

    def compile_for_ida(self, output_dir: str = 'data/processed') -> Path:
        """
        Compile dataset into analysis-ready format
        
        Args:
            output_dir: Output directory for compiled data
            
        Returns:
            Path to compiled dataset file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create summary DataFrame
        data = []
        for i, record in enumerate(self.records):
            data.append({
                'gm_id': record['id'],
                'zone': self.zone,
                'pga': record['pga'],
                'duration': record['duration'],
                'n_points': len(record['acceleration']),
                'dt': record['dt'],
                'source': record['source'],
                'magnitude': record['magnitude'],
                'distance': record['distance'],
            })
        
        df = pd.DataFrame(data)
        
        # Save metadata
        metadata_file = output_path / f'gm_metadata_z{self.zone}.csv'
        df.to_csv(metadata_file, index=False)
        logger.info(f"Saved GM metadata to {metadata_file}")
        
        return metadata_file


class Phase2GroundMotionGenerator:
    """
    Generate or prepare ground motions for IDA analysis
    
    Supports both loading real records and generating synthetic records
    compatible with BNBC 2020 response spectra.
    """
    
    def __init__(self, config_path: str = 'config/bnbc_parameters.yaml'):
        """
        Initialize GM generator
        
        Args:
            config_path: Path to BNBC configuration file
        """
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.datasets: Dict[int, GroundMotionDataset] = {}

    def create_synthetic_gms(self, zone: int = 3, n_records: int = 500) -> GroundMotionDataset:
        """
        Create synthetic ground motion records for testing
        
        In production, replace with real records from PEER NGA database.
        
        Args:
            zone: BNBC seismic zone
            n_records: Number of synthetic records to generate
            
        Returns:
            GroundMotionDataset with synthetic records
        """
        dataset = GroundMotionDataset(zone=zone, n_records=n_records)
        
        # Zone-specific PGA reference
        zone_config = self.config['seismic_zones'][f'zone_{zone}']
        ref_pga = zone_config['pga']
        
        logger.info(f"Creating {n_records} synthetic GM records for Zone {zone} (ref PGA={ref_pga}g)")
        
        # Generate synthetic records
        for i in range(n_records):
            # Parameters
            duration = 30.0  # seconds
            dt = 0.005  # seconds
            n_points = int(duration / dt)
            
            # Create bandpass-filtered noise
            t = np.arange(n_points) * dt
            
            # Modulate with smoothed envelope
            envelope = np.exp(-0.5 * t / 15) * np.sin(np.pi * t / duration) ** 2
            
            # Generate noise
            np.random.seed(42 + i)  # Reproducible but varied
            noise = np.random.randn(n_points)
            
            # Filter to frequency range 0.5-10 Hz (typical earthquake)
            from scipy import signal
            sos = signal.butter(4, [0.5, 10], fs=1/dt, btype='band', output='sos')
            filtered_noise = signal.sosfilt(sos, noise)
            
            # Scale and modulate
            scale = ref_pga * (0.5 + 1.5 * np.random.rand())  # Vary around ref PGA
            acceleration = scale * envelope * filtered_noise / np.std(filtered_noise)
            
            # Add to dataset
            record_id = f"GM_Z{zone}_{i+1:04d}"
            magnitude = 5.0 + np.random.rand() * 2.0  # M 5.0-7.0
            distance = 10 + np.random.rand() * 40  # 10-50 km
            
            dataset.add_record(
                record_id=record_id,
                time_series=acceleration,
                dt=dt,
                source='synthetic',
                magnitude=magnitude,
                distance=distance
            )
        
        self.datasets[zone] = dataset
        return dataset

    def prepare_for_ida(self, zone: int, n_records: int = 500) -> GroundMotionDataset:
        """
        Prepare ground motion dataset for Phase 2 IDA analysis
        
        Args:
            zone: BNBC seismic zone (1-4)
            n_records: Number of records to prepare
            
        Returns:
            GroundMotionDataset ready for analysis
        """
        logger.info(f"Preparing {n_records} GM records for Zone {zone} IDA analysis")
        
        # For now, use synthetic GMs (in production, load from PEER NGA)
        dataset = self.create_synthetic_gms(zone=zone, n_records=n_records)
        
        # Verify dataset integrity
        assert len(dataset.records) == n_records, "Record count mismatch"
        
        # Compile for IDA
        metadata_file = dataset.compile_for_ida()
        logger.info(f"GM dataset ready: {len(dataset.records)} records, metadata: {metadata_file}")
        
        return dataset

    def generate_all_zone_datasets(self, n_records: int = 500) -> Dict[int, GroundMotionDataset]:
        """
        Generate GM datasets for all BNBC seismic zones
        
        Args:
            n_records: Records per zone
            
        Returns:
            Dictionary mapping zone → GroundMotionDataset
        """
        zones = self.config['seismic_zones'].keys()
        zone_numbers = sorted([int(k.split('_')[1]) for k in zones])
        
        logger.info(f"Generating GM datasets for all {len(zone_numbers)} BNBC zones")
        
        all_datasets = {}
        for zone in zone_numbers:
            dataset = self.prepare_for_ida(zone=zone, n_records=n_records)
            all_datasets[zone] = dataset
        
        return all_datasets


def generate_phase2_gm_datasets(zones: List[int] = None,
                                n_records: int = 500,
                                config_path: str = 'config/bnbc_parameters.yaml') -> Dict[int, GroundMotionDataset]:
    """
    Convenience function to generate all Phase 2 ground motion datasets
    
    Args:
        zones: List of BNBC zones to prepare (default: all)
        n_records: Number of records per zone
        config_path: Path to BNBC configuration
        
    Returns:
        Dictionary mapping zone → GroundMotionDataset
    """
    if zones is None:
        zones = [1, 2, 3, 4]
    
    logger.info("="*60)
    logger.info("PHASE 2: GROUND MOTION PREPARATION")
    logger.info("="*60)
    logger.info(f"Zones: {zones}")
    logger.info(f"Records per zone: {n_records}")
    
    generator = Phase2GroundMotionGenerator(config_path=config_path)
    
    datasets = {}
    for zone in zones:
        dataset = generator.prepare_for_ida(zone=zone, n_records=n_records)
        datasets[zone] = dataset
    
    logger.info(f"\n✓ Phase 2 GM preparation complete: {len(datasets)*n_records} total records ready")
    
    return datasets


if __name__ == '__main__':
    # Test GM generation
    logging.basicConfig(level=logging.INFO)
    
    # Generate small test dataset
    datasets = generate_phase2_gm_datasets(zones=[3], n_records=50)
    
    # Verify
    for zone, dataset in datasets.items():
        print(f"\nZone {zone}:")
        print(f"  Records: {len(dataset.records)}")
        print(f"  Intensity levels: {dataset.get_intensity_levels()}")
