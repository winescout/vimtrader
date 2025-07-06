import pandas as pd

def render_chart(df: pd.DataFrame) -> str:
    """
    Renders a pandas DataFrame of OHLCV data as an ASCII candlestick chart.

    Args:
        df (pd.DataFrame): DataFrame with OHLCV data (Open, High, Low, Close, Volume).
                           Expected columns: 'Open', 'High', 'Low', 'Close'.

    Returns:
        str: ASCII representation of the candlestick chart.
    """
    if df.empty:
        return "No data to render."

    # Define chart parameters
    chart_height = 10  # Number of rows for the chart
    candle_width = 3   # Number of columns per candle (e.g., |█|)

    # ASCII characters for rendering
    BULLISH_BODY = '█'
    BEARISH_BODY = '▄'
    WICK = '│'
    EMPTY = ' '

    # Calculate min and max prices for scaling
    min_price = df['Low'].min()
    max_price = df['High'].max()

    if max_price == min_price:
        # Handle flat line case
        return "Price range is flat, cannot render meaningful chart."

    # Initialize chart grid
    # Each row is a list of characters, initialized with spaces
    chart_grid = [[EMPTY for _ in range(len(df) * candle_width)] for _ in range(chart_height)]

    def price_to_row(price):
        # Map price to a row index (0 is top, chart_height-1 is bottom)
        normalized_price = (price - min_price) / (max_price - min_price)
        row = int((1 - normalized_price) * (chart_height - 1))
        return max(0, min(chart_height - 1, row)) # Ensure within bounds

    # Iterate through each candle and draw it on the grid
    for i, (index, row) in enumerate(df.iterrows()):
        open_price = row['Open']
        high_price = row['High']
        low_price = row['Low']
        close_price = row['Close']

        col_start = i * candle_width + 1 # Center the candle in its 3-char width

        # Convert prices to row indices
        open_row = price_to_row(open_price)
        high_row = price_to_row(high_price)
        low_row = price_to_row(low_price)
        close_row = price_to_row(close_price)

        # Draw wick (High to Low)
        for r in range(min(high_row, low_row), max(high_row, low_row) + 1):
            chart_grid[r][col_start] = WICK

        # Draw body (Open to Close)
        body_top_row = min(open_row, close_row)
        body_bottom_row = max(open_row, close_row)
        
        body_char = BULLISH_BODY if close_price >= open_price else BEARISH_BODY

        for r in range(body_top_row, body_bottom_row + 1):
            chart_grid[r][col_start] = body_char

    # Convert grid to string
    chart_string = "\n".join(["".join(row) for row in chart_grid])
    return chart_string

if __name__ == '__main__':
    # Example usage for testing
    data = {
        'Open': [100, 105, 110, 108, 112],
        'High': [108, 112, 115, 110, 118],
        'Low': [98, 103, 107, 105, 109],
        'Close': [105, 110, 108, 112, 115],
        'Volume': [1000, 1200, 900, 1500, 1100]
    }
    sample_df = pd.DataFrame(data)
    print("Sample Chart:")
    print(render_chart(sample_df))

    # Bearish example
    bearish_data = {
        'Open': [110, 105, 100],
        'High': [112, 108, 102],
        'Low': [105, 100, 95],
        'Close': [105, 100, 98],
        'Volume': [500, 600, 700]
    }
    bearish_df = pd.DataFrame(bearish_data)
    print("\nBearish Chart:")
    print(render_chart(bearish_df))

    # Flat data example
    flat_data = {
        'Open': [100, 100],
        'High': [100, 100],
        'Low': [100, 100],
        'Close': [100, 100],
        'Volume': [100, 100]
    }
    flat_df = pd.DataFrame(flat_data)
    print("\nFlat Chart:")
    print(render_chart(flat_df))