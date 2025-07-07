#!/usr/bin/env python3
"""
Test DataFrame for VimTrader Plugin

This file contains sample pandas DataFrames for testing the VimTrader plugin.
To use:
1. Open this file in Neovim
2. Place cursor on a DataFrame variable (e.g., 'sample_df')
3. Run :VimtraderChart to visualize the data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Simple test DataFrame
sample_df = pd.DataFrame({
    'Open': [76, 105, 110, 108, 112, 115, 113, 118, 120, 117],
    'High': [11, 112, 115, 110, 118, 120, 116, 122, 125, 121],
    'Low': [1, 103, 107, 105, 109, 113, 111, 116, 118, 115],
    'Close': [105, 110, 108, 112, 115, 113, 118, 120, 117, 119],
    'Volume': [1000, 1200, 900, 1500, 1100, 1300, 1000, 1600, 1400, 1200]
})

# Bearish trend DataFrame
bearish_df = pd.DataFrame({
    'Open': [109, 115, 110, 105, 100, 95, 90, 85, 80, 75],
    'High': [125, 118, 112, 108, 103, 98, 93, 88, 83, 78],
    'Low': [118, 112, 107, 102, 97, 92, 87, 82, 77, 72],
    'Close': [115, 110, 105, 100, 95, 90, 85, 80, 75, 70],
    'Volume': [1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400]
})

# Bullish trend DataFrame
bullish_df = pd.DataFrame({
    'Open': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125],
    'High': [87, 92, 97, 102, 107, 112, 117, 122, 127, 132],
    'Low': [78, 83, 88, 93, 98, 103, 108, 113, 118, 123],
    'Close': [85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
    'Volume': [2000, 1900, 1800, 1700, 1600, 1500, 1400, 1300, 1200, 1100]
})

# Volatile DataFrame with mixed patterns
volatile_df = pd.DataFrame({
    'Open': [100, 110, 95, 105, 90, 115, 85, 120, 80, 125],
    'High': [115, 120, 108, 118, 105, 128, 98, 135, 93, 140],
    'Low': [95, 105, 88, 98, 82, 110, 78, 115, 72, 120],
    'Close': [110, 95, 105, 90, 115, 85, 120, 80, 125, 75],
    'Volume': [3000, 3200, 2800, 3100, 2900, 3300, 2700, 3400, 2600, 3500]
})

# Generate realistic time-based DataFrame
def generate_realistic_data(days=30, start_price=100):
    """Generate realistic OHLCV data with random walk."""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
    current_price = start_price
    
    for i in range(days):
        # Random walk for opening price
        if i > 0:
            current_price = closes[-1] * (1 + np.random.normal(0, 0.02))
        
        open_price = current_price
        
        # Generate daily range
        daily_range = abs(np.random.normal(0, 0.03)) * open_price
        direction = np.random.choice([-1, 1])
        
        high_price = open_price + daily_range * np.random.uniform(0.5, 1.0)
        low_price = open_price - daily_range * np.random.uniform(0.5, 1.0)
        close_price = open_price + direction * daily_range * np.random.uniform(0.3, 0.8)
        
        # Ensure high is highest and low is lowest
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        # Generate volume (higher volume on bigger moves)
        volume = int(np.random.normal(1000, 200) * (1 + abs(close_price - open_price) / open_price * 10))
        
        opens.append(round(open_price, 2))
        highs.append(round(high_price, 2))
        lows.append(round(low_price, 2))
        closes.append(round(close_price, 2))
        volumes.append(max(volume, 100))
    
    return pd.DataFrame({
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    })

# Generate realistic test data
realistic_df = generate_realistic_data(20, 150)

# Test the chart rendering directly
if __name__ == "__main__":
    import sys
    import os
    
    # Add the python directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    python_path = os.path.join(project_root, 'python')
    if python_path not in sys.path:
        sys.path.insert(0, python_path)
    
    from vimtrader.chart import render_chart
    
    print("Sample DataFrame Chart:")
    print(render_chart(sample_df))
    
    print("\n" + "="*50 + "\n")
    
    print("Bearish DataFrame Chart:")
    print(render_chart(bearish_df))
    
    print("\n" + "="*50 + "\n")
    
    print("Bullish DataFrame Chart:")
    print(render_chart(bullish_df))
    
    print("\n" + "="*50 + "\n")
    
    print("Volatile DataFrame Chart:")
    print(render_chart(volatile_df))
    
    print("\n" + "="*50 + "\n")
    
    print("Realistic DataFrame Chart:")
    print(render_chart(realistic_df.drop('Date', axis=1)))  # Drop date column for chart
