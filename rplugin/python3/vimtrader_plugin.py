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


# Functional state management
from vimtrader.state import (
    EditorState,
    EditorCommand,
    ParseResult,
    parse_dataframe_from_buffer,
    update_buffer_with_dataframe,
    handle_editor_command,
    get_current_dataframe as get_dataframe_from_state,
    create_editor_state,
    create_candle_adjustment_command,
    create_cursor_movement_command
)

# Plugin state management (minimal mutable state for editor sessions)
_editor_sessions = {}  # session_id -> EditorState
_last_session_error = None  # Store last session creation error for debugging


def get_buffer_content(nvim, file_path: str) -> Optional[str]:
    """Get content from the buffer."""
    try:
        for buf in nvim.buffers:
            if buf.name == file_path:
                return '\n'.join(buf[:])
        return None
    except Exception:
        return None


def update_buffer_content(nvim, file_path: str, new_content: str) -> bool:
    """Update buffer content with new data."""
    try:
        for buf in nvim.buffers:
            if buf.name == file_path:
                lines = new_content.split('\n')
                buf[:] = lines
                return True
        return False
    except Exception:
        return False


def get_or_create_session(nvim, variable_name: str) -> Optional[str]:
    """Get or create an editor session, returning session ID."""
    try:
        # Get current buffer info
        current_file = nvim.current.buffer.name
        if not current_file:
            # Debug: No file name available
            return None
        if not current_file.endswith('.py'):
            # Debug: Not a Python file
            return None
        
        # Get buffer content
        buffer_content = get_buffer_content(nvim, current_file)
        if buffer_content is None:
            # Debug: Could not read buffer content
            return None
        
        # Create session ID
        session_id = f"{current_file}:{variable_name}"
        
        # Create or update editor state
        editor_state = create_editor_state(buffer_content, variable_name, current_file)
        _editor_sessions[session_id] = editor_state
        
        return session_id
        
    except Exception as e:
        # Debug: Log the actual error for troubleshooting
        import traceback
        error_details = traceback.format_exc()
        # Store error for debugging (could be retrieved by a debug function)
        _last_session_error = f"Session creation failed: {str(e)}\n{error_details}"
        return None


def get_or_create_session_with_file(nvim, variable_name: str, file_path: str) -> Optional[str]:
    """Get or create an editor session with explicit file path, returning session ID."""
    try:
        # Validate file path
        if not file_path or not file_path.endswith('.py'):
            _last_session_error = f"Invalid file path: {file_path}"
            return None
        
        # Get buffer content
        buffer_content = get_buffer_content(nvim, file_path)
        if buffer_content is None:
            _last_session_error = f"Could not read buffer content from: {file_path}"
            return None
        
        # Create session ID
        session_id = f"{file_path}:{variable_name}"
        
        # Create or update editor state
        editor_state = create_editor_state(buffer_content, variable_name, file_path)
        _editor_sessions[session_id] = editor_state
        
        return session_id
        
    except Exception as e:
        # Debug: Log the actual error for troubleshooting
        import traceback
        error_details = traceback.format_exc()
        # Store error for debugging (could be retrieved by a debug function)
        _last_session_error = f"Session creation failed: {str(e)}\n{error_details}"
        return None


def get_session_dataframe(session_id: str) -> ParseResult:
    """Get DataFrame from session state."""
    if session_id not in _editor_sessions:
        return ParseResult(False, None, "Session not found")
    
    state = _editor_sessions[session_id]
    return get_dataframe_from_state(state)


@pynvim.plugin
class VimTraderPlugin:
    """VimTrader plugin for Neovim using functional programming style."""
    
    def __init__(self, nvim):
        """Initialize the plugin."""
        self.nvim = nvim
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
            
            # Use sample data for standalone testing
            df = create_sample_dataframe()
            return render_chart(df)
            
        except ImportError as e:
            return f"Error importing chart module: {str(e)}"
        except Exception as e:
            return f"Error generating sample chart: {str(e)}"
    
    @pynvim.function('VimtraderGetDataFrameChart', sync=True)
    def get_dataframe_chart(self, args):
        """
        Get chart for a specific DataFrame variable using buffer content.
        
        Args:
            args: List containing [variable_name]
        
        Returns:
            str: ASCII representation of the DataFrame as a candlestick chart
        """
        try:
            if len(args) != 1:
                return "Error: Expected 1 argument (variable_name)"
            
            variable_name = args[0]
            session_id = get_or_create_session(self.nvim, variable_name)
            if session_id is None:
                return "Error: Could not create editor session"
            
            # Get DataFrame from buffer
            parse_result = get_session_dataframe(session_id)
            if not parse_result.success:
                return f"Error: {parse_result.error_message}"
            
            # Render chart
            from vimtrader.chart import render_chart
            return render_chart(parse_result.dataframe)
            
        except Exception as e:
            return f"Error getting DataFrame chart: {str(e)}"
    
    @pynvim.function('VimtraderGetCandleTypes', sync=True)
    def get_candle_types(self, args):
        """
        Get bullish/bearish info for each candle.
        
        Returns:
            str: Comma-separated list of 'B' for bullish, 'R' for bearish
        """
        try:
            # Use sample data for testing
            df = create_sample_dataframe()
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
    
    @pynvim.function('VimtraderGetLastError', sync=True)
    def get_last_error(self, args):
        """
        Get the last session creation error for debugging.
        
        Returns:
            str: Last error details or "No recent errors"
        """
        global _last_session_error
        if _last_session_error:
            return _last_session_error
        else:
            return "No recent session errors"
    
    @pynvim.function('VimtraderAdjustCandle', sync=True)
    def adjust_candle(self, args):
        """
        Adjust a specific value (High, Low, Open, Close) for a candle using buffer state.
        
        Args:
            args: List containing [candle_index, value_type, direction, variable_name, file_path]
                  candle_index: int (0-based index of candle)
                  value_type: str ('high', 'low', 'open', 'close')
                  direction: int (1 for increase, -1 for decrease)
                  variable_name: str (name of DataFrame variable)
                  file_path: str (path to the source Python file)
        
        Returns:
            str: Updated ASCII chart with modified data
        """
        try:
            if len(args) not in [4, 5]:
                return "Error: Expected 4 or 5 arguments (candle_index, value_type, direction, variable_name, [file_path])"
            
            candle_index, value_type, direction, variable_name = args[:4]
            file_path = args[4] if len(args) == 5 else None
            
            # Validate inputs
            if not isinstance(candle_index, int) or candle_index < 0:
                return f"Error: Invalid candle index: {candle_index}"
            
            # Get or create session with explicit file path if provided
            if file_path:
                session_id = get_or_create_session_with_file(self.nvim, variable_name, file_path)
            else:
                session_id = get_or_create_session(self.nvim, variable_name)
                
            if session_id is None:
                return "Error: Could not create editor session"
            
            # Create command
            command = create_candle_adjustment_command(candle_index, value_type, direction)
            
            # Apply command using functional state management
            current_state = _editor_sessions[session_id]
            new_state, error_msg = handle_editor_command(current_state, command)
            
            if error_msg:
                return f"Error: {error_msg}"
            
            # Update session state
            _editor_sessions[session_id] = new_state
            
            # Update buffer with new content
            if not update_buffer_content(self.nvim, new_state.file_path, new_state.buffer_content):
                return "Error: Could not update buffer"
            
            # Get updated DataFrame and render chart
            parse_result = get_session_dataframe(session_id)
            if not parse_result.success:
                return f"Error: {parse_result.error_message}"
            
            from vimtrader.chart import render_chart
            return render_chart(parse_result.dataframe)
            
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
        Get OHLC values for a specific candle using buffer state.
        
        Args:
            args: List containing [candle_index, variable_name, file_path]
                  candle_index: int (0-based index of candle)
                  variable_name: str (name of DataFrame variable)
                  file_path: str (optional path to the source Python file)
        
        Returns:
            str: Format "open:xxx,high:xxx,low:xxx,close:xxx"
        """
        try:
            if len(args) not in [2, 3]:
                return "Error: Expected 2 or 3 arguments (candle_index, variable_name, [file_path])"
            
            candle_index, variable_name = args[:2]
            file_path = args[2] if len(args) == 3 else None
            
            if not isinstance(candle_index, int) or candle_index < 0:
                return f"Error: Invalid candle index: {candle_index}"
            
            # Get or create session with explicit file path if provided
            if file_path:
                session_id = get_or_create_session_with_file(self.nvim, variable_name, file_path)
            else:
                session_id = get_or_create_session(self.nvim, variable_name)
                
            if session_id is None:
                return "Error: Could not create editor session"
            
            # Get DataFrame from buffer
            parse_result = get_session_dataframe(session_id)
            if not parse_result.success:
                return f"Error: {parse_result.error_message}"
            
            ohlc_values, error_msg = get_ohlc_values(parse_result.dataframe, candle_index)
            if error_msg:
                return f"Error: {error_msg}"
            
            return format_ohlc_string(ohlc_values)
            
        except Exception as e:
            return f"Error getting OHLC values: {str(e)}"