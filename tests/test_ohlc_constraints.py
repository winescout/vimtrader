#!/usr/bin/env python3
"""
Unit tests for OHLC constraint handling in VimTrader.

Tests the intelligent constraint logic where Open/Close reaching High/Low
boundaries automatically extend the High/Low values to maintain valid OHLC.
"""

import pytest
import pandas as pd
import sys
import os

# Add the python directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
python_path = os.path.join(project_root, 'python')
sys.path.insert(0, python_path)

from vimtrader.state import apply_candle_adjustment


class TestOHLCConstraints:
    """Test suite for intelligent OHLC constraint handling."""
    
    def setup_method(self):
        """Set up test DataFrame with known OHLC values."""
        self.test_df = pd.DataFrame({
            'Open': [100.0, 105.0, 110.0],
            'High': [110.0, 115.0, 120.0], 
            'Low': [90.0, 95.0, 100.0],
            'Close': [105.0, 110.0, 115.0],
            'Volume': [1000, 1200, 1500]
        })
    
    def test_basic_open_adjustment_within_bounds(self):
        """Test normal Open adjustment that stays within High/Low bounds."""
        # Open: 100 -> 101, should stay within bounds (High: 110, Low: 90)
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'open', 1)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 101.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_basic_close_adjustment_within_bounds(self):
        """Test normal Close adjustment that stays within High/Low bounds."""
        # Close: 105 -> 106, should stay within bounds (High: 110, Low: 90)
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'close', 1)
        
        assert error is None
        assert result_df.iloc[0]['Close'] == 106.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Open'] == 100.0  # Unchanged
    
    def test_open_reaches_high_boundary_exact(self):
        """Test Open adjustment that exactly reaches the High boundary."""
        # Manually set Open to reach High exactly
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Open')] = 109.0  # One below High
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'open', 1)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 110.0
        assert result_df.iloc[0]['High'] == 110.0  # Should remain same
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_open_exceeds_high_boundary(self):
        """Test Open adjustment that exceeds High boundary -> High should extend."""
        # Set Open to 109, then increase by 2 to reach 111 (exceeds High: 110)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Open')] = 109.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'open', 2)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 111.0
        assert result_df.iloc[0]['High'] == 111.0  # Should extend to match Open
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_open_reaches_low_boundary_exact(self):
        """Test Open adjustment that exactly reaches the Low boundary."""
        # Set Open to 91, then decrease by 1 to reach 90 (exactly Low)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Open')] = 91.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'open', -1)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 90.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0    # Should remain same
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_open_goes_below_low_boundary(self):
        """Test Open adjustment that goes below Low boundary -> Low should extend."""
        # Set Open to 91, then decrease by 2 to reach 89 (below Low: 90)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Open')] = 91.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'open', -2)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 89.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 89.0    # Should extend to match Open
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_close_reaches_high_boundary_exact(self):
        """Test Close adjustment that exactly reaches the High boundary."""
        # Set Close to 109, then increase by 1 to reach 110 (exactly High)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Close')] = 109.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'close', 1)
        
        assert error is None
        assert result_df.iloc[0]['Close'] == 110.0
        assert result_df.iloc[0]['High'] == 110.0  # Should remain same
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Open'] == 100.0  # Unchanged
    
    def test_close_exceeds_high_boundary(self):
        """Test Close adjustment that exceeds High boundary -> High should extend."""
        # Set Close to 109, then increase by 2 to reach 111 (exceeds High: 110)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Close')] = 109.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'close', 2)
        
        assert error is None
        assert result_df.iloc[0]['Close'] == 111.0
        assert result_df.iloc[0]['High'] == 111.0  # Should extend to match Close
        assert result_df.iloc[0]['Low'] == 90.0    # Unchanged
        assert result_df.iloc[0]['Open'] == 100.0  # Unchanged
    
    def test_close_reaches_low_boundary_exact(self):
        """Test Close adjustment that exactly reaches the Low boundary."""
        # Set Close to 91, then decrease by 1 to reach 90 (exactly Low)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Close')] = 91.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'close', -1)
        
        assert error is None
        assert result_df.iloc[0]['Close'] == 90.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0    # Should remain same
        assert result_df.iloc[0]['Open'] == 100.0  # Unchanged
    
    def test_close_goes_below_low_boundary(self):
        """Test Close adjustment that goes below Low boundary -> Low should extend."""
        # Set Close to 91, then decrease by 2 to reach 89 (below Low: 90)
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Close')] = 91.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'close', -2)
        
        assert error is None
        assert result_df.iloc[0]['Close'] == 89.0
        assert result_df.iloc[0]['High'] == 110.0  # Unchanged
        assert result_df.iloc[0]['Low'] == 89.0    # Should extend to match Close
        assert result_df.iloc[0]['Open'] == 100.0  # Unchanged
    
    def test_high_adjustment_below_max_ohlc(self):
        """Test High adjustment that would go below max(Open, Close, Low) -> should be constrained."""
        # Try to set High to 95 (below Close: 105, Open: 100) 
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'high', -16)  # 110 - 16 = 94
        
        assert error is None
        # High should be constrained to max(Open:100, Close:105, Low:90) = 105
        assert result_df.iloc[0]['High'] == 105.0
        assert result_df.iloc[0]['Open'] == 100.0   # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0     # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_low_adjustment_above_min_ohlc(self):
        """Test Low adjustment that would go above min(Open, Close, High) -> should be constrained."""
        # Try to set Low to 101 (above Open: 100)
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'low', 12)  # 90 + 12 = 102
        
        assert error is None
        # Low should be constrained to min(Open:100, Close:105, High:110) = 100
        assert result_df.iloc[0]['Low'] == 100.0
        assert result_df.iloc[0]['Open'] == 100.0   # Unchanged
        assert result_df.iloc[0]['High'] == 110.0   # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_high_normal_increase(self):
        """Test normal High increase that maintains valid constraints."""
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'high', 1)
        
        assert error is None
        assert result_df.iloc[0]['High'] == 111.0   # 110 + 1
        assert result_df.iloc[0]['Open'] == 100.0   # Unchanged
        assert result_df.iloc[0]['Low'] == 90.0     # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_low_normal_decrease(self):
        """Test normal Low decrease that maintains valid constraints."""
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'low', -1)
        
        assert error is None
        assert result_df.iloc[0]['Low'] == 89.0     # 90 - 1
        assert result_df.iloc[0]['Open'] == 100.0   # Unchanged
        assert result_df.iloc[0]['High'] == 110.0   # Unchanged
        assert result_df.iloc[0]['Close'] == 105.0  # Unchanged
    
    def test_multiple_candle_independence(self):
        """Test that adjustments to one candle don't affect other candles."""
        # Adjust first candle's Open to exceed High boundary
        test_df = self.test_df.copy()
        test_df.iloc[0, test_df.columns.get_loc('Open')] = 109.0
        
        result_df, error = apply_candle_adjustment(test_df, 0, 'open', 2)  # 109 + 2 = 111
        
        assert error is None
        # First candle should be affected
        assert result_df.iloc[0]['Open'] == 111.0
        assert result_df.iloc[0]['High'] == 111.0  # Extended
        
        # Second and third candles should be unchanged
        assert result_df.iloc[1]['Open'] == 105.0
        assert result_df.iloc[1]['High'] == 115.0
        assert result_df.iloc[1]['Low'] == 95.0
        assert result_df.iloc[1]['Close'] == 110.0
        
        assert result_df.iloc[2]['Open'] == 110.0
        assert result_df.iloc[2]['High'] == 120.0
        assert result_df.iloc[2]['Low'] == 100.0
        assert result_df.iloc[2]['Close'] == 115.0
    
    def test_edge_case_all_equal_values(self):
        """Test constraint handling when all OHLC values are equal."""
        # Create a flat candle where O=H=L=C=100
        flat_df = pd.DataFrame({
            'Open': [100.0],
            'High': [100.0],
            'Low': [100.0],
            'Close': [100.0],
            'Volume': [1000]
        })
        
        # Increase Open by 1
        result_df, error = apply_candle_adjustment(flat_df, 0, 'open', 1)
        
        assert error is None
        assert result_df.iloc[0]['Open'] == 101.0
        assert result_df.iloc[0]['High'] == 101.0  # Should extend to match Open
        assert result_df.iloc[0]['Low'] == 100.0   # Unchanged
        assert result_df.iloc[0]['Close'] == 100.0  # Unchanged
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        # Invalid candle index
        result_df, error = apply_candle_adjustment(self.test_df, 10, 'open', 1)
        assert error is not None
        assert "out of range" in error
        
        # Invalid value type
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'invalid', 1)
        assert error is not None
        assert "Invalid value type" in error
        
        # Invalid direction (non-numeric)
        result_df, error = apply_candle_adjustment(self.test_df, 0, 'open', "invalid")
        assert error is not None
        assert "Invalid direction" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])