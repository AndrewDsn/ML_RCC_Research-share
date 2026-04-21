"""
Phase 1: RC Frame Model Generator

Generates parametric RC moment-resisting frame models for all building heights
and framework types compliant with BNBC 2020.

Usage:
    python -c "from src.modeling.phase1_generator import generate_all_models; generate_all_models()"
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List
from .rc_frame import RCFrame

logger = logging.getLogger(__name__)


def generate_phase1_models(
    building_heights: List[int] = None,
    framework_types: List[str] = None,
    seismic_zones: List[int] = None,
    output_dir: str = 'models/openseespy',
    config_path: str = 'config/bnbc_parameters.yaml'
) -> Dict[str, str]:
    """
    Generate all Phase 1 RC frame models

    Args:
        building_heights: List of story counts [5, 7, 10, 12, 15]
        framework_types: List of frameworks ['nonsway', 'omrf', 'imrf', 'smrf']
        seismic_zones: List of zones [1, 2, 3, 4]
        output_dir: Output directory for model files
        config_path: Path to BNBC configuration

    Returns:
        Dictionary mapping model IDs to file paths
    """
    if building_heights is None:
        building_heights = [5, 7, 10, 12, 15]
    if framework_types is None:
        framework_types = ['nonsway', 'omrf', 'imrf', 'smrf']
    if seismic_zones is None:
        seismic_zones = [1, 2, 3, 4]

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load BNBC configuration
    with open(config_path, 'r') as f:
        bnbc_config = yaml.safe_load(f)

    models_created = {}
    total_models = len(building_heights) * len(framework_types) * len(seismic_zones)
    models_count = 0

    logger.info(f"Starting Phase 1: Model Generation")
    logger.info(f"Total models to generate: {total_models}")
    logger.info(f"Buildings: {building_heights}")
    logger.info(f"Frameworks: {framework_types}")
    logger.info(f"Seismic zones: {seismic_zones}")
    logger.info(f"Output directory: {output_dir}")

    for n_stories in building_heights:
        for framework_type in framework_types:
            for zone in seismic_zones:
                models_count += 1

                # Create model ID
                model_id = f"B{n_stories:02d}_{framework_type.upper()}_Z{zone}"

                try:
                    logger.info(f"[{models_count}/{total_models}] Generating {model_id}...")

                    # Create frame
                    frame = RCFrame(
                        n_stories=n_stories,
                        framework_type=framework_type,
                        config_path=config_path
                    )

                    # Set geometry (standard: 3.5m stories, 6m bays, 4 bays)
                    story_height = 3.5  # meters
                    bay_width = 6.0
                    n_bays = 4

                    # Framework-specific dimensions
                    if n_stories <= 5:
                        column_size = (400, 400)  # mm width x depth
                        beam_size = (300, 500)
                    elif n_stories <= 10:
                        column_size = (500, 500)
                        beam_size = (350, 550)
                    else:
                        column_size = (600, 600)
                        beam_size = (400, 600)

                    frame.set_geometry(
                        story_height=story_height,
                        bay_width=bay_width,
                        column_size=column_size,
                        beam_size=beam_size,
                        n_bays=n_bays
                    )

                    # Create OpenSeesPy model
                    frame.create_model()

                    # Apply gravity loads (4.0 kN/m² floor, 3.0 kN/m² roof)
                    frame.apply_gravity_loads(floor_load=4.0, roof_load=3.0)

                    # Get zone-specific base shear from BNBC
                    zone_config = bnbc_config.get('seismic_zones', {}).get(f'zone_{zone}', {})
                    pga = zone_config.get('pga', 0.10)
                    base_shear = pga * 9.81 * 1000 * n_stories * 3.5 / 10  # Simplified estimate

                    # Apply lateral loads (triangular distribution)
                    frame.apply_lateral_loads(base_shear=base_shear, distribution='linear')

                    # Save model to JSON
                    filename = f"frame_{n_stories}s_{framework_type}_z{zone}.json"
                    filepath = output_path / filename
                    frame.save_model(str(filepath))

                    models_created[model_id] = str(filepath)
                    logger.info(f"  ✓ {model_id} saved to {filepath}")

                except Exception as e:
                    logger.error(f"  ✗ Failed to generate {model_id}: {str(e)}", exc_info=True)
                    continue

    logger.info(f"\nPhase 1 Model Generation Complete")
    logger.info(f"Successfully created: {len(models_created)} / {total_models} models")

    return models_created


def generate_all_models():
    """
    Generate all Phase 1 models (convenience function for command-line execution)
    """
    models = generate_phase1_models()
    print(f"\nGenerated {len(models)} models:")
    for model_id, filepath in sorted(models.items()):
        print(f"  {model_id}: {filepath}")


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Generate models
    generate_all_models()
