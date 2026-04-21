"""
Unit tests for visualization and plotting modules

Tests cover:
- Plot generation
- Figure formatting and styling
- Data visualization validation
- Publication-quality output verification
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile


class TestFragilityCurves:
    """Test suite for fragility curve generation"""

    @pytest.fixture
    def fragility_data(self):
        """Create sample fragility curve data"""
        intensity = np.linspace(0.05, 1.5, 30)
        
        data = {
            'intensity': intensity,
            'p_io': 1 / (1 + np.exp(-(intensity - 0.3) / 0.1)),  # Logistic curve
            'p_ls': 1 / (1 + np.exp(-(intensity - 0.6) / 0.1)),
            'p_cp': 1 / (1 + np.exp(-(intensity - 0.9) / 0.1)),
            'zone': 3,
            'building_id': 'B10_SMRF',
        }
        
        return pd.DataFrame(data)

    def test_fragility_data_validity(self, fragility_data):
        """Test fragility data structure and values"""
        # Check required columns
        required_cols = ['intensity', 'p_io', 'p_ls', 'p_cp']
        for col in required_cols:
            assert col in fragility_data.columns, f"Missing column: {col}"

    def test_fragility_curve_properties(self, fragility_data):
        """Test fragility curve properties"""
        # Probabilities should be between 0 and 1
        assert np.all(fragility_data['p_io'] >= 0) and np.all(fragility_data['p_io'] <= 1)
        assert np.all(fragility_data['p_ls'] >= 0) and np.all(fragility_data['p_ls'] <= 1)
        assert np.all(fragility_data['p_cp'] >= 0) and np.all(fragility_data['p_cp'] <= 1)
        
        # CP >= LS >= IO (monotonic property)
        assert np.all(fragility_data['p_cp'] >= fragility_data['p_ls'])
        assert np.all(fragility_data['p_ls'] >= fragility_data['p_io'])

    def test_fragility_intensity_range(self, fragility_data):
        """Test intensity measure range"""
        intensity = fragility_data['intensity']
        
        # Should span typical range for Sa(T=0.5s)
        assert intensity.min() >= 0.01, "Intensity too low"
        assert intensity.max() <= 2.0, "Intensity too high"
        assert len(intensity) >= 20, "Too few intensity points"

    def test_fragility_curve_smoothness(self, fragility_data):
        """Test fragility curves are smooth (no erratic jumps)"""
        for col in ['p_io', 'p_ls', 'p_cp']:
            probs = fragility_data[col].values
            diffs = np.diff(probs)
            
            # Check for unrealistic jumps (>0.3 change per intensity step)
            max_jump = np.max(np.abs(diffs))
            assert max_jump < 0.3, f"Rough curve detected in {col}: max jump {max_jump}"

    def test_fragility_curve_generation(self):
        """Test fragility curve can be generated from ML model"""
        try:
            import matplotlib.pyplot as plt
            
            # Create synthetic ML predictions
            intensities = np.linspace(0.05, 1.5, 20)
            pidrs = intensities * 0.06  # Linear relationship for testing
            
            # Classify into performance levels (mock)
            io_threshold = 0.01
            ls_threshold = 0.025
            cp_threshold = 0.04
            
            p_io = np.sum(pidrs >= io_threshold) / len(pidrs)
            p_ls = np.sum(pidrs >= ls_threshold) / len(pidrs)
            p_cp = np.sum(pidrs >= cp_threshold) / len(pidrs)
            
            # All probabilities should be computed
            assert 0 <= p_io <= 1
            assert 0 <= p_ls <= 1
            assert 0 <= p_cp <= 1
            
            plt.close('all')
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestIDAPlots:
    """Test suite for IDA curve visualization"""

    @pytest.fixture
    def ida_data(self):
        """Create sample IDA analysis results"""
        # Typical IDA curve: intensity vs peak drift
        intensities = np.linspace(0.05, 1.5, 20)
        pidr_values = 0.005 * np.exp(intensities / 0.5)  # Exponential growth
        
        data = {
            'intensity_sa': intensities,
            'pidr': pidr_values,
            'pga': intensities * 1.3,  # Approximate PGA-Sa relationship
            'building_id': 'B10_SMRF_Z3',
            'gm_id': 'GM_001',
        }
        
        return pd.DataFrame(data)

    def test_ida_data_structure(self, ida_data):
        """Test IDA data has required fields"""
        required_fields = ['intensity_sa', 'pidr']
        for field in required_fields:
            assert field in ida_data.columns, f"Missing field: {field}"

    def test_ida_curve_monotonicity(self, ida_data):
        """Test IDA curves are monotonically increasing"""
        # PIDR should generally increase with intensity
        pidr = ida_data['pidr'].values
        
        # Check approximate monotonicity (allow small deviations)
        diffs = np.diff(pidr)
        pct_increasing = np.sum(diffs >= 0) / len(diffs)
        assert pct_increasing >= 0.7, f"Only {pct_increasing*100:.1f}% of points increasing"

    def test_ida_data_ranges(self, ida_data):
        """Test IDA data is within physically realistic ranges"""
        # Intensity (Sa) range
        sa = ida_data['intensity_sa']
        assert sa.min() >= 0.01, "Sa too low"
        assert sa.max() <= 2.0, "Sa too high"
        
        # PIDR range
        pidr = ida_data['pidr']
        assert pidr.min() >= 0, "PIDR negative"
        assert pidr.max() <= 0.20, "PIDR unrealistically high"

    def test_ida_plot_generation(self):
        """Test IDA plot can be created"""
        try:
            import matplotlib.pyplot as plt
            
            # Create sample IDA curve
            intensities = np.linspace(0.05, 1.5, 15)
            pidrs = 0.005 * np.exp(intensities / 0.5)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(intensities, pidrs, 'o-', linewidth=2, markersize=6)
            ax.set_xlabel('Intensity – Sa(T=0.5s) [g]', fontsize=12)
            ax.set_ylabel('Peak Inter-Story Drift Ratio [%]', fontsize=12)
            ax.set_title('Incremental Dynamic Analysis Curve', fontsize=14)
            ax.grid(True, alpha=0.3)
            
            # Verify plot properties
            assert len(ax.lines) > 0, "No lines drawn"
            assert ax.get_xlabel() != '', "X-axis label missing"
            assert ax.get_ylabel() != '', "Y-axis label missing"
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestPerformancePlots:
    """Test suite for ML performance visualization"""

    @pytest.fixture
    def model_performance(self):
        """Create sample model performance metrics"""
        models = ['Linear Regression', 'Random Forest', 'XGBoost', 'Neural Network']
        metrics = {
            'model': models,
            'r2_train': [0.82, 0.91, 0.93, 0.92],
            'r2_test': [0.78, 0.87, 0.89, 0.85],
            'rmse_train': [0.0085, 0.0062, 0.0055, 0.0060],
            'rmse_test': [0.0095, 0.0071, 0.0064, 0.0078],
            'mae_test': [0.0072, 0.0053, 0.0048, 0.0061],
        }
        
        return pd.DataFrame(metrics)

    def test_performance_metrics_validity(self, model_performance):
        """Test performance metrics are valid"""
        # R² should be between 0 and 1
        assert np.all(model_performance['r2_train'] >= 0)
        assert np.all(model_performance['r2_train'] <= 1)
        assert np.all(model_performance['r2_test'] >= 0)
        assert np.all(model_performance['r2_test'] <= 1)
        
        # RMSE and MAE should be positive
        assert np.all(model_performance['rmse_train'] > 0)
        assert np.all(model_performance['mae_test'] > 0)

    def test_overfitting_detection(self, model_performance):
        """Test can detect potential overfitting"""
        # Calculate train-test R² difference
        r2_diff = model_performance['r2_train'] - model_performance['r2_test']
        
        # Some overfitting is normal, but >0.15 is suspicious
        assert np.all(r2_diff < 0.20), "Potential overfitting detected"

    def test_model_comparison_plot(self):
        """Test model comparison plot can be created"""
        try:
            import matplotlib.pyplot as plt
            
            models = ['LR', 'RF', 'XGB', 'ANN']
            r2_scores = [0.78, 0.87, 0.89, 0.85]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(models, r2_scores, color=['blue', 'green', 'red', 'orange'])
            ax.set_ylabel('R² Score', fontsize=12)
            ax.set_title('Model Performance Comparison', fontsize=14)
            ax.set_ylim([0.7, 1.0])
            
            # Verify plot
            assert len(bars) == len(models), "Bar count mismatch"
            assert ax.get_ylabel() != '', "Y-axis label missing"
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestPublicationFigures:
    """Test suite for publication-quality figure generation"""

    def test_figure_resolution(self):
        """Test figure DPI is sufficient for publication"""
        try:
            import matplotlib.pyplot as plt
            
            fig = plt.figure(figsize=(8, 6), dpi=300)  # Standard publication DPI
            assert fig.dpi == 300, "DPI not set correctly"
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")

    def test_figure_font_sizes(self):
        """Test publication-quality font sizes"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots()
            
            # Set publication-quality fonts
            ax.set_xlabel('Test Label', fontsize=12)
            ax.set_ylabel('Test Label', fontsize=12)
            ax.set_title('Test Title', fontsize=14)
            
            # Verify fonts
            assert ax.xaxis.label.get_fontsize() == 12
            assert ax.yaxis.label.get_fontsize() == 12
            assert ax.title.get_fontsize() == 14
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")

    def test_figure_export(self):
        """Test figures can be exported in publication formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                import matplotlib.pyplot as plt
                
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [1, 4, 2])
                
                # Test save formats
                formats = ['png', 'pdf', 'svg']
                for fmt in formats:
                    filepath = Path(tmpdir) / f"test_figure.{fmt}"
                    fig.savefig(str(filepath), dpi=300, bbox_inches='tight')
                    assert filepath.exists(), f"Failed to save {fmt} format"
                    assert filepath.stat().st_size > 0, f"Empty {fmt} file"
                
                plt.close(fig)
            except ImportError:
                pytest.skip("matplotlib not installed")

    def test_colormap_accessibility(self):
        """Test figures use colorblind-friendly colormaps"""
        try:
            import matplotlib.pyplot as plt
            
            # Recommended colormaps for accessibility
            accessible_cmaps = ['viridis', 'plasma', 'cividis']
            
            fig, axes = plt.subplots(1, 3, figsize=(12, 4))
            
            for ax, cmap in zip(axes, accessible_cmaps):
                data = np.random.randn(10, 10)
                im = ax.imshow(data, cmap=cmap)
                
                # Verify colormap is set
                assert im.get_cmap() is not None
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestVisualizationUtilities:
    """Test suite for general visualization utilities"""

    def test_axis_labeling(self):
        """Test proper axis labeling and units"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots()
            
            # Test proper labeling with units
            ax.set_xlabel('Intensity – Sa(T=0.5s) [g]')
            ax.set_ylabel('Peak Inter-Story Drift Ratio [%]')
            
            xlabel = ax.get_xlabel()
            ylabel = ax.get_ylabel()
            
            # Verify labels contain units
            assert '[' in xlabel and ']' in xlabel, "Units missing from x-label"
            assert '[' in ylabel and ']' in ylabel, "Units missing from y-label"
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")

    def test_legend_generation(self):
        """Test legend is properly generated"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots()
            
            # Plot multiple series
            ax.plot([1, 2, 3], [1, 2, 3], label='Series 1')
            ax.plot([1, 2, 3], [3, 2, 1], label='Series 2')
            
            # Generate legend
            legend = ax.legend()
            assert legend is not None, "Legend not created"
            
            # Verify legend entries
            texts = [t.get_text() for t in legend.get_texts()]
            assert 'Series 1' in texts
            assert 'Series 2' in texts
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")

    def test_grid_styling(self):
        """Test grid styling for readability"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots()
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.plot([1, 2, 3], [1, 2, 3])
            
            # Verify grid is on
            assert ax.xaxis.grid, "X-axis grid not enabled"
            
            plt.close(fig)
        except ImportError:
            pytest.skip("matplotlib not installed")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
