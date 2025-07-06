# VimTrader

A Neovim plugin for visually editing pandas DataFrames as ASCII candlestick charts. This tool is designed to help developers and quantitative analysts create and customize test data for automated trading strategies.

## Features

- **Visual DataFrame Editing**: Convert pandas DataFrames to ASCII candlestick charts
- **Interactive Chart Window**: Navigate and modify charts with key commands
- **Real-time Updates**: Changes in the chart are reflected back to the original DataFrame
- **Multiple Chart Types**: Support for various market data patterns (bullish, bearish, volatile)

## Installation

### Prerequisites

- Neovim with Python 3 support
- Python 3.7 or higher
- pandas
- pynvim

### Setup

1. **Install Python dependencies**:
   ```bash
   pip install pandas pynvim numpy
   ```

2. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd vimtrader
   ```

3. **Install the plugin**:
   - Copy the plugin directory to your Neovim plugin directory, or
   - Add the project directory to your Neovim runtimepath

4. **Register the remote plugin**:
   ```vim
   :UpdateRemotePlugins
   ```

5. **Restart Neovim**

### Troubleshooting

If you encounter issues with Python communication:

1. **Check Python path**: Ensure Neovim can find your Python executable:
   ```vim
   :echo has('python3')
   ```

2. **Set Python host program** (if needed):
   ```vim
   let g:python3_host_prog = '/path/to/your/python'
   ```

3. **Verify pynvim installation**:
   ```bash
   python -c "import pynvim; print('pynvim works!')"
   ```

## Usage

### Basic Usage

1. **Open a Python file** with pandas DataFrames (or use the provided example):
   ```vim
   :edit examples/test_dataframe.py
   ```

2. **Run the chart command**:
   ```vim
   :VimtraderChart
   ```

3. **The chart window will open** showing a sample ASCII candlestick chart.

### Chart Window Controls

- `q` or `ESC`: Close chart window
- `r`: Refresh chart
- `i`: Show Python environment info

### Testing the Installation

You can test the plugin using the provided example file:

```bash
# Test the chart rendering directly
python examples/test_dataframe.py

# Or test within Neovim
# 1. Open examples/test_dataframe.py in Neovim
# 2. Run :VimtraderChart
```

## Project Structure

```
vimtrader/
├── lua/vimtrader/          # Lua plugin logic
│   ├── init.lua
│   └── main.lua
├── plugin/                 # Plugin entry point
│   └── vimtrader.lua
├── rplugin/python3/        # Python remote plugin
│   └── vimtrader_plugin.py
├── python/vimtrader/       # Python modules
│   ├── __init__.py
│   ├── chart.py           # Chart rendering logic
│   └── editor.py          # DataFrame editing logic
├── examples/              # Test files
│   └── test_dataframe.py
└── tests/                 # Unit tests
    ├── conftest.py
    └── test_chart.py
```

## Development

### Running Tests

```bash
# Run Python tests
pytest tests/

# Test chart rendering
python python/vimtrader/chart.py

# Test with sample data
python examples/test_dataframe.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Architecture

The plugin consists of:

1. **Lua Frontend**: Handles Neovim UI and user interactions
2. **Python Backend**: Processes DataFrames and renders ASCII charts
3. **RPC Communication**: Uses pynvim for Lua-Python communication

## Future Features

- [ ] Real DataFrame variable detection and editing
- [ ] Interactive chart editing with key commands
- [ ] Support for different chart types (line, bar, etc.)
- [ ] Export functionality for modified DataFrames
- [ ] Integration with popular trading libraries

## License

MIT License