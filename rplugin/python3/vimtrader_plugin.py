#!/usr/bin/env python3
"""
VimTrader Neovim Remote Plugin

This module provides the Python backend for the VimTrader Neovim plugin.
It handles chart rendering and DataFrame manipulation through RPC calls.
"""

import sys
import os
import pandas as pd
import pynvim

# Add the project's python directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
python_path = os.path.join(project_root, 'python')
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Import will be done inside functions to avoid top-level import errors


@pynvim.plugin
class VimTraderPlugin:
    """VimTrader plugin for Neovim."""
    
    def __init__(self, nvim):
        """Initialize the plugin."""
        self.nvim = nvim
        self.current_dataframe = None
        # Log that the plugin is being initialized
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
            
            df_json = args[0]
            df = pd.read_json(df_json)
            
            # Validate required columns
            required_columns = ['Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return f"Error: Missing required columns: {missing_columns}"
            
            chart_string = render_chart(df)
            return chart_string
            
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
            # First try to import and use the render_chart function
            from vimtrader.chart import render_chart
            
            # Create sample OHLCV data with mixed bullish/bearish candles
            sample_data = {
                'Open': [100, 105, 110, 108, 112, 115, 113, 118, 120, 117],
                'High': [108, 112, 115, 110, 118, 120, 116, 122, 125, 121],
                'Low': [98, 103, 107, 105, 109, 113, 111, 116, 118, 115],
                'Close': [105, 110, 108, 112, 115, 113, 118, 120, 117, 119],
                'Volume': [1000, 1200, 900, 1500, 1100, 1300, 1000, 1600, 1400, 1200]
            }
            
            df = pd.DataFrame(sample_data)
            chart_string = render_chart(df)
            
            # Store candle type info for the Lua highlighting to use
            self.current_dataframe = df
            
            # Return the chart - colors will be applied by Lua highlighting
            return chart_string
            
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
        if self.current_dataframe is None:
            return "B,B,B,B,B"  # Default fallback
        
        try:
            candle_types = []
            for _, row in self.current_dataframe.iterrows():
                is_bullish = row['Close'] >= row['Open']
                candle_types.append('B' if is_bullish else 'R')
            
            return ','.join(candle_types)
            
        except Exception as e:
            return "B,B,B,B,B"  # Fallback on error
    
    @pynvim.function('VimtraderGetPythonInfo', sync=True)
    def get_python_info(self, args):
        """
        Get Python environment information for debugging.
        
        Returns:
            str: Python version and path information
        """
        try:
            info = []
            info.append(f"Python version: {sys.version}")
            info.append(f"Python executable: {sys.executable}")
            info.append(f"Current working directory: {os.getcwd()}")
            info.append(f"Project root: {project_root}")
            info.append(f"Python path includes: {python_path}")
            info.append(f"Pandas version: {pd.__version__}")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting Python info: {str(e)}"