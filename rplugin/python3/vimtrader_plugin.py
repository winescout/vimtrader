#!/usr/bin/env python3
"""
VimTrader Neovim Remote Plugin

This module provides the Python backend for the VimTrader Neovim plugin.
It handles chart rendering and DataFrame manipulation through RPC calls.
Uses functional programming style with pure functions and immutable data.
"""

import sys
import os
from typing import Optional, Tuple, Dict, Any, List
import pandas as pd
import pynvim

# Add the project's python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
python_path = os.path.join(project_root, 'python')
if python_path not in sys.path:
    sys.path.insert(0, python_path)


# Pure functions for data operations
def create_sample_dataframe() -> pd.DataFrame:
    """
    Create a sample OHLCV DataFrame for testing.
    
    Returns:
        pd.DataFrame: Sample data with mixed bullish/bearish candles
    """
    sample_data = {
        'Open': [100, 105, 110, 108, 112, 115, 113, 118, 120, 117],
        'High': [108, 112, 115, 110, 118, 120, 116, 122, 125, 121],
        'Low': [98, 103, 107, 105, 109, 113, 111, 116, 118, 115],
        'Close': [105, 110, 108, 112, 115, 113, 118, 120, 117, 119],
        'Volume': [1000, 1200, 900, 1500, 1100, 1300, 1000, 1600, 1400, 1200]
    }
    return pd.DataFrame(sample_data)


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate that a DataFrame has required OHLC columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_columns = ['Open', 'High', 'Low', 'Close']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    return True, None


def determine_candle_types(df: pd.DataFrame) -> List[str]:
    """
    Determine bullish/bearish type for each candle.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        List of 'B' for bullish, 'R' for bearish candles
    """
    candle_types = []
    for _, row in df.iterrows():
        is_bullish = row['Close'] >= row['Open']
        candle_types.append('B' if is_bullish else 'R')
    return candle_types


def adjust_candle_value(df: pd.DataFrame, candle_index: int, value_type: str, 
                       direction: int) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Adjust a specific OHLC value for a candle, returning new DataFrame.
    
    Args:
        df: Original DataFrame
        candle_index: 0-based index of candle to adjust
        value_type: 'high', 'low', 'open', or 'close'
        direction: 1 for increase, -1 for decrease
        
    Returns:
        Tuple of (new_dataframe, error_message)
    """
    # Validate inputs
    if candle_index < 0 or candle_index >= len(df):
        return df, f"Candle index {candle_index} out of range"
    
    if value_type not in ['high', 'low', 'open', 'close']:
        return df, f"Invalid value type: {value_type}"
    
    if direction not in [1, -1]:
        return df, f"Invalid direction: {direction}"
    
    # Create a copy to maintain immutability
    new_df = df.copy()
    
    # Calculate adjustment
    adjustment = 1.0 * direction
    column_name = value_type.capitalize()
    current_value = new_df.iloc[candle_index][column_name]
    new_value = current_value + adjustment
    
    # Apply OHLC validation constraints
    if value_type == 'high':
        # High should be >= max(Open, Close) and >= Low
        min_high = max(new_df.iloc[candle_index]['Open'], 
                      new_df.iloc[candle_index]['Close'], 
                      new_df.iloc[candle_index]['Low'])
        new_value = max(new_value, min_high)
    elif value_type == 'low':
        # Low should be <= min(Open, Close) and <= High
        max_low = min(new_df.iloc[candle_index]['Open'], 
                     new_df.iloc[candle_index]['Close'], 
                     new_df.iloc[candle_index]['High'])
        new_value = min(new_value, max_low)
    
    # Update the value
    new_df.iloc[candle_index, new_df.columns.get_loc(column_name)] = new_value
    
    return new_df, None


def get_ohlc_values(df: pd.DataFrame, candle_index: int) -> Tuple[Optional[Dict[str, float]], Optional[str]]:
    """
    Get OHLC values for a specific candle.
    
    Args:
        df: DataFrame with OHLC data
        candle_index: 0-based index of candle
        
    Returns:
        Tuple of (ohlc_dict, error_message)
    """
    if candle_index < 0 or candle_index >= len(df):
        return None, f"Candle index {candle_index} out of range"
    
    candle_data = df.iloc[candle_index]
    return {
        'open': float(candle_data['Open']),
        'high': float(candle_data['High']),
        'low': float(candle_data['Low']),
        'close': float(candle_data['Close'])
    }, None


def format_ohlc_string(ohlc_values: Dict[str, float]) -> str:
    """
    Format OHLC values as a string.
    
    Args:
        ohlc_values: Dictionary with open, high, low, close values
        
    Returns:
        Formatted string
    """
    return f"open:{ohlc_values['open']:.1f},high:{ohlc_values['high']:.1f},low:{ohlc_values['low']:.1f},close:{ohlc_values['close']:.1f}"


def get_python_environment_info() -> str:
    """
    Get Python environment information for debugging.
    
    Returns:
        Formatted string with environment info
    """
    info = [
        f"Python version: {sys.version}",
        f"Python executable: {sys.executable}",
        f"Current working directory: {os.getcwd()}",
        f"Project root: {project_root}",
        f"Python path includes: {python_path}",
        f"Pandas version: {pd.__version__}"
    ]
    return "\n".join(info)


# Plugin state management (minimal mutable state)
_plugin_state = {
    'current_dataframe': None
}


def get_current_dataframe() -> Optional[pd.DataFrame]:
    """Get the current DataFrame from plugin state."""
    return _plugin_state.get('current_dataframe')


def set_current_dataframe(df: pd.DataFrame) -> None:
    """Set the current DataFrame in plugin state."""
    _plugin_state['current_dataframe'] = df.copy() if df is not None else None


@pynvim.plugin
class VimTraderPlugin:
    """VimTrader plugin for Neovim using functional programming style."""
    
    def __init__(self, nvim):
        """Initialize the plugin."""
        self.nvim = nvim
        # Initialize with sample data
        set_current_dataframe(create_sample_dataframe())
        self.nvim.out_write("VimTrader plugin initialized\n")
    
    @pynvim.function('VimtraderGetDummyChartString', sync=True)
    def get_dummy_chart_string(self, args):
        """
        Returns a dummy chart string for testing RPC communication.
        
        Returns:
            str: A simple test string to verify RPC is working.
        """
        return "VimTrader Python backend is working!\n\nTest ASCII Chart:\n│ │ │\n█ ▄ █\n│ │ │"
    
    @pynvim.function('VimtraderTest', sync=True)
    def test_simple(self, args):
        """
        Simple test function that just returns a string.
        """
        return "Test successful!"
    
    @pynvim.function('VimtraderRenderChart')
    def render_chart_from_json(self, args):
        """
        Render a chart from JSON DataFrame data.
        
        Args:
            args: List containing JSON string representation of DataFrame
            
        Returns:
            str: ASCII representation of the candlestick chart
        """
        try:
            if not args or not args[0]:
                return "Error: No data provided"
            
            df = pd.read_json(args[0])
            is_valid, error_msg = validate_dataframe(df)
            if not is_valid:
                return f"Error: {error_msg}"
            
            from vimtrader.chart import render_chart
            return render_chart(df)
            
        except Exception as e:
            return f"Error rendering chart: {str(e)}"
    
    @pynvim.function('VimtraderGetSampleChart', sync=True)
    def get_sample_chart(self, args):
        """
        Generate a sample chart for testing.
        
        Returns:
            str: ASCII representation of a sample candlestick chart
        """
        try:
            from vimtrader.chart import render_chart
            
            df = get_current_dataframe()
            if df is None:
                df = create_sample_dataframe()
                set_current_dataframe(df)
            
            return render_chart(df)
            
        except ImportError as e:
            return f"Error importing chart module: {str(e)}"
        except Exception as e:
            return f"Error generating sample chart: {str(e)}"
    
    @pynvim.function('VimtraderGetCandleTypes', sync=True)
    def get_candle_types(self, args):
        """
        Get bullish/bearish info for each candle.
        
        Returns:
            str: Comma-separated list of 'B' for bullish, 'R' for bearish
        """
        try:
            df = get_current_dataframe()
            if df is None:
                return "B,B,B,B,B"  # Default fallback
            
            candle_types = determine_candle_types(df)
            return ','.join(candle_types)
            
        except Exception:
            return "B,B,B,B,B"  # Fallback on error
    
    @pynvim.function('VimtraderGetPythonInfo', sync=True)
    def get_python_info(self, args):
        """
        Get Python environment information for debugging.
        
        Returns:
            str: Python version and path information
        """
        try:
            return get_python_environment_info()
        except Exception as e:
            return f"Error getting Python info: {str(e)}"
    
    @pynvim.function('VimtraderAdjustCandle', sync=True)
    def adjust_candle(self, args):
        """
        Adjust a specific value (High, Low, Open, Close) for a candle.
        
        Args:
            args: List containing [candle_index, value_type, direction]
                  candle_index: int (0-based index of candle)
                  value_type: str ('high', 'low', 'open', 'close')
                  direction: int (1 for increase, -1 for decrease)
        
        Returns:
            str: Updated ASCII chart with modified data
        """
        try:
            if len(args) != 3:
                return "Error: Expected 3 arguments (candle_index, value_type, direction)"
            
            candle_index, value_type, direction = args
            
            # Validate inputs
            if not isinstance(candle_index, int) or candle_index < 0:
                return f"Error: Invalid candle index: {candle_index}"
            
            current_df = get_current_dataframe()
            if current_df is None:
                current_df = create_sample_dataframe()
            
            # Apply adjustment using pure function
            new_df, error_msg = adjust_candle_value(current_df, candle_index, value_type, direction)
            if error_msg:
                return f"Error: {error_msg}"
            
            # Update state with new DataFrame
            set_current_dataframe(new_df)
            
            # Re-render the chart
            from vimtrader.chart import render_chart
            return render_chart(new_df)
            
        except Exception as e:
            return f"Error adjusting candle: {str(e)}"
    
    @pynvim.function('VimtraderGetPriceAtPosition', sync=True)
    def get_price_at_position(self, args):
        """
        Get the price value at a specific candle and chart position.
        
        Args:
            args: List containing [candle_index, row_position]
                  candle_index: int (0-based index of candle)
                  row_position: int (0-based row position in chart)
        
        Returns:
            str: Format "value_type:price" (e.g., "high:115.5")
        """
        try:
            if len(args) != 2:
                return "Error: Expected 2 arguments (candle_index, row_position)"
            
            candle_index, row_position = args
            
            # Validate inputs
            if not isinstance(candle_index, int) or candle_index < 0:
                return f"Error: Invalid candle index: {candle_index}"
            
            if not isinstance(row_position, int) or row_position < 0:
                return f"Error: Invalid row position: {row_position}"
            
            df = get_current_dataframe()
            if df is None:
                return "Error: No data available"
            
            ohlc_values, error_msg = get_ohlc_values(df, candle_index)
            if error_msg:
                return f"Error: {error_msg}"
            
            # Calculate chart parameters (matching chart.py)
            chart_height = 10
            min_price = df['Low'].min()
            max_price = df['High'].max()
            
            if max_price == min_price:
                return "close:100.0"  # Fallback for flat data
            
            # Convert row position to price (inverse of price_to_row in chart.py)
            normalized_position = (chart_height - 1 - row_position) / (chart_height - 1)
            cursor_price = min_price + normalized_position * (max_price - min_price)
            
            # Determine which OHLC value is closest to cursor position
            price_distances = {
                'high': abs(cursor_price - ohlc_values['high']),
                'low': abs(cursor_price - ohlc_values['low']),
                'open': abs(cursor_price - ohlc_values['open']),
                'close': abs(cursor_price - ohlc_values['close'])
            }
            
            # Find the closest value
            closest_type = min(price_distances.keys(), key=lambda k: price_distances[k])
            closest_price = ohlc_values[closest_type]
            
            return f"{closest_type}:{closest_price:.1f}"
            
        except Exception as e:
            return f"Error getting price at position: {str(e)}"
    
    @pynvim.function('VimtraderGetOHLCValues', sync=True)
    def get_ohlc_values_rpc(self, args):
        """
        Get OHLC values for a specific candle.
        
        Args:
            args: List containing [candle_index]
                  candle_index: int (0-based index of candle)
        
        Returns:
            str: Format "open:xxx,high:xxx,low:xxx,close:xxx"
        """
        try:
            if len(args) != 1:
                return "Error: Expected 1 argument (candle_index)"
            
            candle_index = args[0]
            
            if not isinstance(candle_index, int) or candle_index < 0:
                return f"Error: Invalid candle index: {candle_index}"
            
            df = get_current_dataframe()
            if df is None:
                return "Error: No data available"
            
            ohlc_values, error_msg = get_ohlc_values(df, candle_index)
            if error_msg:
                return f"Error: {error_msg}"
            
            return format_ohlc_string(ohlc_values)
            
        except Exception as e:
            return f"Error getting OHLC values: {str(e)}"