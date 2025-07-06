import pandas as pd
from vimtrader.chart import render_chart

def test_render_chart_empty_dataframe():
    """
    Test that render_chart handles an empty DataFrame gracefully.
    """
    df = pd.DataFrame()
    result = render_chart(df)
    assert result == "No data to render."

def test_render_chart_flat_data():
    """
    Test that render_chart handles flat price data.
    """
    data = {
        'Open': [100],
        'High': [100],
        'Low': [100],
        'Close': [100],
        'Volume': [100]
    }
    df = pd.DataFrame(data)
    result = render_chart(df)
    assert result == "Price range is flat, cannot render meaningful chart."

def test_render_chart_single_bullish_candle():
    """
    Test rendering of a single bullish candle.
    """
    data = {
        'Open': [100],
        'High': [105],
        'Low': [98],
        'Close': [104],
        'Volume': [1000]
    }
    df = pd.DataFrame(data)
    result = render_chart(df)
    # Basic check for expected characters and structure
    assert '█' in result  # Bullish body
    assert '│' in result  # Wick
    assert '\n' in result # Multiple lines for chart height
    # Further detailed checks would involve parsing the ASCII output or comparing to a known good string

def test_render_chart_single_bearish_candle():
    """
    Test rendering of a single bearish candle.
    """
    data = {
        'Open': [104],
        'High': [105],
        'Low': [98],
        'Close': [100],
        'Volume': [1000]
    }
    df = pd.DataFrame(data)
    result = render_chart(df)
    assert '▄' in result  # Bearish body
    assert '│' in result  # Wick
    assert '\n' in result

def test_render_chart_multiple_candles():
    """
    Test rendering of multiple candles.
    """
    data = {
        'Open': [100, 105, 110],
        'High': [108, 112, 115],
        'Low': [98, 103, 107],
        'Close': [105, 110, 108],
        'Volume': [1000, 1200, 900]
    }
    df = pd.DataFrame(data)
    result = render_chart(df)
    assert '█' in result
    assert '▄' in result
    assert '│' in result
    # More advanced checks would verify the relative positions of candles