"""
Functional chart rendering module for VimTrader.

This module provides pure functions for rendering pandas DataFrames 
as ASCII candlestick charts using functional programming principles.
"""

from typing import List, Tuple, Callable
import pandas as pd


# Chart constants (immutable)
CHART_HEIGHT = 10
CANDLE_WIDTH = 3
BULLISH_BODY = '^'
BEARISH_BODY = 'v'
WICK = '|'
EMPTY = ' '


def calculate_price_range(df: pd.DataFrame) -> Tuple[float, float]:
    """
    Calculate the min and max prices from OHLC data.
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        Tuple of (min_price, max_price)
    """
    return df['Low'].min(), df['High'].max()


def create_price_to_row_mapper(min_price: float, max_price: float, 
                              chart_height: int = CHART_HEIGHT) -> Callable[[float], int]:
    """
    Create a function that maps prices to chart row indices.
    
    Args:
        min_price: Minimum price in the dataset
        max_price: Maximum price in the dataset
        chart_height: Height of the chart in rows
        
    Returns:
        Function that maps price to row index
    """
    if max_price == min_price:
        # For flat data, return middle row
        return lambda price: chart_height // 2
    
    def price_to_row(price: float) -> int:
        """Map price to a row index (0 is top, chart_height-1 is bottom)."""
        normalized_price = (price - min_price) / (max_price - min_price)
        row = int((1 - normalized_price) * (chart_height - 1))
        return max(0, min(chart_height - 1, row))
    
    return price_to_row


def create_empty_chart_grid(num_candles: int, chart_height: int = CHART_HEIGHT, 
                           candle_width: int = CANDLE_WIDTH) -> List[List[str]]:
    """
    Create an empty chart grid filled with spaces.
    
    Args:
        num_candles: Number of candles to accommodate
        chart_height: Height of the chart in rows
        candle_width: Width allocated per candle
        
    Returns:
        2D list representing the chart grid
    """
    width = num_candles * candle_width
    return [[EMPTY for _ in range(width)] for _ in range(chart_height)]


def get_candle_ohlc(row: pd.Series) -> Tuple[float, float, float, float]:
    """
    Extract OHLC values from a DataFrame row.
    
    Args:
        row: Pandas Series with OHLC data
        
    Returns:
        Tuple of (open, high, low, close)
    """
    return (
        float(row['Open']),
        float(row['High']),
        float(row['Low']),
        float(row['Close'])
    )


def determine_candle_character(open_price: float, close_price: float) -> str:
    """
    Determine the character to use for a candle body.
    
    Args:
        open_price: Opening price
        close_price: Closing price
        
    Returns:
        Character representing bullish or bearish candle
    """
    return BULLISH_BODY if close_price >= open_price else BEARISH_BODY


def draw_wick_on_grid(grid: List[List[str]], col: int, high_row: int, low_row: int) -> None:
    """
    Draw a wick (vertical line) on the chart grid.
    
    Args:
        grid: Chart grid to modify
        col: Column to draw in
        high_row: Row index for high price
        low_row: Row index for low price
    """
    start_row = min(high_row, low_row)
    end_row = max(high_row, low_row)
    
    for r in range(start_row, end_row + 1):
        grid[r][col] = WICK


def draw_body_on_grid(grid: List[List[str]], col: int, open_row: int, 
                     close_row: int, body_char: str) -> None:
    """
    Draw a candle body on the chart grid.
    
    Args:
        grid: Chart grid to modify
        col: Column to draw in
        open_row: Row index for open price
        close_row: Row index for close price
        body_char: Character to use for the body
    """
    start_row = min(open_row, close_row)
    end_row = max(open_row, close_row)
    
    for r in range(start_row, end_row + 1):
        grid[r][col] = body_char


def draw_single_candle(grid: List[List[str]], candle_index: int, 
                      ohlc: Tuple[float, float, float, float],
                      price_to_row: Callable[[float], int],
                      candle_width: int = CANDLE_WIDTH) -> None:
    """
    Draw a single candle on the chart grid.
    
    Args:
        grid: Chart grid to modify
        candle_index: Index of the candle (0-based)
        ohlc: Tuple of (open, high, low, close) prices
        price_to_row: Function to convert price to row index
        candle_width: Width allocated per candle
    """
    open_price, high_price, low_price, close_price = ohlc
    
    # Calculate column position (center of the candle's allocated space)
    col = candle_index * candle_width + 1
    
    # Convert prices to row indices
    open_row = price_to_row(open_price)
    high_row = price_to_row(high_price)
    low_row = price_to_row(low_price)
    close_row = price_to_row(close_price)
    
    # Draw wick first (so body can override if needed)
    draw_wick_on_grid(grid, col, high_row, low_row)
    
    # Draw body
    body_char = determine_candle_character(open_price, close_price)
    draw_body_on_grid(grid, col, open_row, close_row, body_char)


def grid_to_string(grid: List[List[str]]) -> str:
    """
    Convert a 2D character grid to a string.
    
    Args:
        grid: 2D list of characters
        
    Returns:
        String representation of the grid
    """
    return "\n".join("".join(row) for row in grid)


def validate_ohlc_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that a DataFrame has the required OHLC columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df.empty:
        return False, "No data to render."
    
    required_columns = ['Open', 'High', 'Low', 'Close']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    return True, ""


def render_chart(df: pd.DataFrame) -> str:
    """
    Render a pandas DataFrame of OHLCV data as an ASCII candlestick chart.
    
    This is the main entry point that coordinates all the pure functions
    to create a chart using functional programming principles.

    Args:
        df: DataFrame with OHLCV data (Open, High, Low, Close, Volume).
            Expected columns: 'Open', 'High', 'Low', 'Close'.

    Returns:
        str: ASCII representation of the candlestick chart.
    """
    # Validate input
    is_valid, error_message = validate_ohlc_dataframe(df)
    if not is_valid:
        return error_message
    
    # Calculate price range
    min_price, max_price = calculate_price_range(df)
    
    if max_price == min_price:
        return "Price range is flat, cannot render meaningful chart."
    
    # Create pure functions for this dataset
    price_to_row = create_price_to_row_mapper(min_price, max_price)
    
    # Initialize chart grid
    grid = create_empty_chart_grid(len(df))
    
    # Draw each candle using pure functions
    for i, (_, row) in enumerate(df.iterrows()):
        ohlc = get_candle_ohlc(row)
        draw_single_candle(grid, i, ohlc, price_to_row)
    
    # Convert to string
    return grid_to_string(grid)


def create_sample_chart_data() -> pd.DataFrame:
    """
    Create sample data for testing the chart rendering.
    
    Returns:
        DataFrame with sample OHLCV data
    """
    data = {
        'Open': [100, 105, 110, 108, 112],
        'High': [108, 112, 115, 110, 118],
        'Low': [98, 103, 107, 105, 109],
        'Close': [105, 110, 108, 112, 115],
        'Volume': [1000, 1200, 900, 1500, 1100]
    }
    return pd.DataFrame(data)


def create_bearish_chart_data() -> pd.DataFrame:
    """
    Create bearish sample data for testing.
    
    Returns:
        DataFrame with bearish OHLCV data
    """
    data = {
        'Open': [110, 105, 100],
        'High': [112, 108, 102],
        'Low': [105, 100, 95],
        'Close': [105, 100, 98],
        'Volume': [500, 600, 700]
    }
    return pd.DataFrame(data)


def create_flat_chart_data() -> pd.DataFrame:
    """
    Create flat sample data for testing edge cases.
    
    Returns:
        DataFrame with flat OHLCV data
    """
    data = {
        'Open': [100, 100],
        'High': [100, 100],
        'Low': [100, 100],
        'Close': [100, 100],
        'Volume': [100, 100]
    }
    return pd.DataFrame(data)


if __name__ == '__main__':
    # Example usage for testing
    print("Sample Chart:")
    sample_df = create_sample_chart_data()
    print(render_chart(sample_df))
    
    print("\nBearish Chart:")
    bearish_df = create_bearish_chart_data()
    print(render_chart(bearish_df))
    
    print("\nFlat Chart:")
    flat_df = create_flat_chart_data()
    print(render_chart(flat_df))