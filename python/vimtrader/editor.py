import sys
import os

# Add the directory containing the 'vimtrader' package to sys.path
# This assumes editor.py is located at python/vimtrader/editor.py
# and the project root is at /Users/matthewclark/Desktop/python/vimtrader
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, os.path.join(project_root, 'python'))

import pandas as pd
import pynvim
from vimtrader.chart import render_chart

@pynvim.plugin
class VimtraderEditor:
    def __init__(self, nvim):
        self.nvim = nvim
        # Removed sys.path print from __init__

    @pynvim.function('VimtraderGetPythonSysPath')
    def get_python_sys_path(self, args):
        import sys
        return str(sys.path)

    @pynvim.function('VimtraderGetDummyChartString')
    def get_dummy_chart_string(self, args):
        """
        Returns a dummy chart string for testing RPC communication.
        """
        return "Dummy chart from Python backend!"

    # The existing functions will be part of this class or moved as needed
    # For now, keep them as standalone functions if they are not directly exposed via RPC
    def handle_input_and_modify_dataframe(self, df: pd.DataFrame, command: str) -> pd.DataFrame:
        """
        Handles user input commands to modify the pandas DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
            command (str): The command string from user input.

        Returns:
            pd.DataFrame: The modified DataFrame.
        """
        # Placeholder for editor logic
        self.nvim.out_write(f"Received command: {command}\n")
        return df

    def get_chart_display(self, df_json: str) -> str:
        """
        Receives a JSON string of a DataFrame, converts it to a DataFrame,
        renders it as an ASCII chart, and returns the chart string.

        Args:
            df_json (str): JSON string representation of the DataFrame.

        Returns:
            str: ASCII representation of the candlestick chart.
        """
        try:
            df = pd.read_json(df_json)
            return render_chart(df)
        except Exception as e:
            return f"Error rendering chart: {e}"
