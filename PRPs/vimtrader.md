name: "Base PRP Template v2 - Context-Rich with Validation Loops"
description: |

## Purpose
Template optimized for AI agents to implement features with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Be sure to follow all rules in GEMINI.md and CLAUDE.md

---

## Goal
To create a Neovim plugin that allows a user to visually edit a pandas DataFrame of OHLCV data as an ASCII stock chart using functional programming principles with the buffer as the single source of truth.

## Why
- **Business value and user impact**: This tool will dramatically accelerate the process of creating and customizing test data for developers of automated trading strategies.
- **Integration with existing features**: The plugin will be invoked from a Python script, operating on a pandas DataFrame object in the buffer.
- **Problems this solves and for whom**: It solves the cumbersome and non-intuitive process of manually creating OHLCV data for testing trading algorithms. It is for Python developers and quantitative analysts who build and test these strategies.
- **Architectural principles**: Uses functional programming with immutable data structures, pure functions, and buffer-as-source-of-truth to eliminate state synchronization issues.

## What
A user, while working in a Python script, will place their cursor on a pandas DataFrame variable containing OHLCV data. By running a Vim command, a new window will open, displaying an ASCII representation of the data. The user can then navigate and modify the chart using key commands, and the underlying DataFrame in the original Python buffer will be updated through functional transformations that maintain data integrity and eliminate caching issues.

### Success Criteria
- [x] A user can invoke the plugin on a pandas DataFrame, opening a new edit window.
- [x] The edit window displays a properly scaled ASCII candlestick chart.
- [x] Interactive chart editing with navigation and candle value adjustments.
- [x] Functional programming architecture with pure functions and immutable data.
- [x] **Functional State Management**: Buffer-as-source-of-truth architecture implemented.
- [x] **Real-time Buffer Sync**: Changes in chart editor update the buffer content immediately.
- [x] **Stateless Editor**: Editor derives all state from buffer content on each operation.
- [x] **Immutable Data Flow**: All transformations use pure functions returning new data.
- [x] **Error Recovery**: System gracefully handles parsing errors and maintains buffer integrity.
- [x] **Performance**: Efficient buffer parsing and updating for responsive editing.

## All Needed Context

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- url: [Official API docs URL]
  why: [Specific sections/methods you'll need]
  
- file: [path/to/example.py]
  why: [Pattern to follow, gotchas to avoid]
  
- doc: [Library documentation URL] 
  section: [Specific section about common pitfalls]
  critical: [Key insight that prevents common errors]

- docfile: [PRPs/ai_docs/file.md]
  why: [docs that the user has pasted in to the project]

```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash

```

### Desired Codebase tree with files to be added and responsibility of file
```bash
.
├── examples/
│   └── test_dataframe.py # Manual testing file for the plugin
├── lua/
│   └── vimtrader/
│       ├── init.lua  # (Now empty, or can be removed if not needed for other requires)
│       └── main.lua    # Main plugin logic in Lua
├── plugin/
│   └── vimtrader.lua # Neovim plugin entrypoint for automatic sourcing
├── python/
│   └── vimtrader/
│       ├── __init__.py
│       ├── chart.py  # ASCII chart rendering and scaling
│       └── editor.py # Handles user input and DataFrame manipulation
└── tests/
    ├── conftest.py
    └── test_chart.py # Unit tests for the chart rendering
```

### Known Gotchas of our codebase & Library Quirks
```python
# CRITICAL: This project requires the following Python libraries:
# - pandas: For DataFrame manipulation.
# - pynvim: For communication between Neovim and Python.

# CRITICAL: The `pynvim` library requires a specific setup to allow Neovim to
# find and communicate with the correct Python executable. This usually involves
# setting `g:python3_host_prog` in your Neovim configuration.
```

## Implementation Blueprint

### Data models and structure

Create the core data models, we ensure type safety and consistency.
```python
Examples: 
 - orm models
 - pydantic models
 - pydantic schemas
 - pydantic validators

```

### list of tasks to be completed to fullfill the PRP in the order they should be completed

```yaml
Task 1: Setup the project structure:
  - [x] CREATE the directories and empty files defined in the Desired Codebase tree section.

Task 2: Implement the chart rendering:
  - [x] CREATE the `chart.py` module.
  - [x] IMPLEMENT the logic to take a pandas DataFrame and render it as an ASCII chart.

Task 3: Implement the editor:
  - [x] CREATE the `editor.py` module.
  - [x] IMPLEMENT the logic to handle user input and modify the DataFrame.

Task 4: Create the Neovim plugin:
  - CREATE the Lua code to connect to the Python backend.
  - IMPLEMENT the logic to display the chart in a new window.

Task 5: Write unit tests:
  - [x] CREATE tests for the `chart.py` module.
  - [x] CREATE tests for the `editor.py` module.

Task 6: Implement functional state management:
  - [x] CREATE functional state management module with immutable data structures
  - [x] IMPLEMENT buffer-as-source-of-truth architecture
  - [x] ADD pure functions for parsing DataFrames from buffer content
  - [x] IMPLEMENT command pattern for editor actions
  - [x] ADD buffer update functions that maintain data integrity
  - [x] INTEGRATE functional state management with existing Neovim plugin

Task 7: Implement intelligent OHLC constraint handling:
  - [x] DESIGN smart constraint logic for Open/Close reaching High/Low boundaries
  - [x] IMPLEMENT automatic High/Low extension when Open/Close values exceed bounds
  - [x] CREATE comprehensive unit tests for all OHLC constraint scenarios
  - [x] UPDATE apply_candle_adjustment function with intelligent constraint handling
  - [x] VALIDATE constraint logic maintains proper OHLC relationships

Task 8: Implement theme-aware color integration:
  - [ ] RESEARCH Neovim theme detection and color extraction methods
  - [ ] DESIGN theme-aware color mapping for bullish/bearish candles
  - [ ] IMPLEMENT automatic theme detection (light/dark background)
  - [ ] CREATE semantic color linking to theme's success/error colors
  - [ ] ADD support for popular themes (gruvbox, catppuccin, tokyonight, etc.)
  - [ ] IMPLEMENT fallback colors for unknown themes
  - [ ] UPDATE chart highlighting to use theme-aware colors
  - [ ] CREATE unit tests for theme color integration

Task 9: Enhance chart display with Unicode and colors:
  - [ ] RESEARCH Unicode box-drawing characters for better chart aesthetics
  - [ ] IMPLEMENT Unicode candlestick rendering with proper wick characters
  - [ ] ADD color support for bullish (green) and bearish (red) candles
  - [ ] DESIGN enhanced chart symbols (filled vs hollow candles)
  - [ ] IMPLEMENT gradient or intensity-based coloring for volume
  - [ ] CREATE configuration options for ASCII vs Unicode rendering
  - [ ] UPDATE chart rendering module with Unicode support
  - [ ] CREATE visual tests for Unicode character display

Task 10: Implement bar insertion and deletion functionality:
  - [ ] DESIGN bar insertion/deletion logic for DataFrame manipulation
  - [ ] IMPLEMENT insert bar to the left of current position
  - [ ] IMPLEMENT insert bar to the right of current position
  - [ ] IMPLEMENT delete current bar functionality
  - [ ] ADD key bindings for bar manipulation (i=insert left, a=append right, dd=delete)
  - [ ] CREATE intelligent default values for new bars based on neighboring candles
  - [ ] UPDATE chart rendering to handle dynamic candle count changes
  - [ ] CREATE comprehensive unit tests for bar insertion/deletion scenarios
```


### Per task pseudocode as needed added to each task
```python

# Task 7: Intelligent OHLC Constraint Handling
def apply_intelligent_ohlc_constraints(ohlc_values, adjustment_type, new_value):
    """
    PATTERN: Intelligent constraint handling for OHLC relationships
    
    Rules:
    1. When Open reaches High -> extend High to match Open
    2. When Open reaches Low -> extend Low to match Open  
    3. When Close reaches High -> extend High to match Close
    4. When Close reaches Low -> extend Low to match Close
    5. High must always be >= max(Open, Close, Low)
    6. Low must always be <= min(Open, Close, High)
    """
    open_val, high_val, low_val, close_val = ohlc_values
    
    if adjustment_type == 'open':
        if new_value >= high_val:
            # Open reaches/exceeds High -> extend High
            return (new_value, new_value, low_val, close_val)
        elif new_value <= low_val:
            # Open reaches/goes below Low -> extend Low
            return (new_value, high_val, new_value, close_val)
        else:
            # Normal adjustment
            return (new_value, high_val, low_val, close_val)
            
    elif adjustment_type == 'close':
        if new_value >= high_val:
            # Close reaches/exceeds High -> extend High
            return (open_val, new_value, low_val, new_value)
        elif new_value <= low_val:
            # Close reaches/goes below Low -> extend Low
            return (open_val, high_val, new_value, new_value)
        else:
            # Normal adjustment
            return (open_val, high_val, low_val, new_value)
            
    elif adjustment_type == 'high':
        # High must be at least max(Open, Close, Low)
        min_high = max(open_val, close_val, low_val)
        adjusted_high = max(new_value, min_high)
        return (open_val, adjusted_high, low_val, close_val)
        
    elif adjustment_type == 'low':
        # Low must be at most min(Open, Close, High)
        max_low = min(open_val, close_val, high_val)
        adjusted_low = min(new_value, max_low)
        return (open_val, high_val, adjusted_low, close_val)

# Test scenarios for comprehensive coverage
OHLC_TEST_SCENARIOS = [
    # Basic valid adjustments
    {'ohlc': (100, 110, 90, 105), 'adjust': 'open', 'direction': 1, 'expected': (101, 110, 90, 105)},
    
    # Open reaching High boundary
    {'ohlc': (100, 110, 90, 105), 'adjust': 'open', 'new_val': 110, 'expected': (110, 110, 90, 105)},
    {'ohlc': (100, 110, 90, 105), 'adjust': 'open', 'new_val': 115, 'expected': (115, 115, 90, 105)},
    
    # Open reaching Low boundary  
    {'ohlc': (100, 110, 90, 105), 'adjust': 'open', 'new_val': 90, 'expected': (90, 110, 90, 105)},
    {'ohlc': (100, 110, 90, 105), 'adjust': 'open', 'new_val': 85, 'expected': (85, 110, 85, 105)},
    
    # Close reaching High boundary
    {'ohlc': (100, 110, 90, 105), 'adjust': 'close', 'new_val': 110, 'expected': (100, 110, 90, 110)},
    {'ohlc': (100, 110, 90, 105), 'adjust': 'close', 'new_val': 115, 'expected': (100, 115, 90, 115)},
    
    # Close reaching Low boundary
    {'ohlc': (100, 110, 90, 105), 'adjust': 'close', 'new_val': 90, 'expected': (100, 110, 90, 90)},
    {'ohlc': (100, 110, 90, 105), 'adjust': 'close', 'new_val': 85, 'expected': (100, 110, 85, 85)},
    
    # High/Low constraint validation
    {'ohlc': (100, 110, 90, 105), 'adjust': 'high', 'new_val': 95, 'expected': (100, 105, 90, 105)},  # High < Close
    {'ohlc': (100, 110, 90, 105), 'adjust': 'low', 'new_val': 115, 'expected': (100, 110, 100, 105)},  # Low > Open
]

# Task 6: Interactive editing resolution system
class EditingResolution:
    def __init__(self, base_resolution=0.25):
        self.base_resolution = base_resolution  # Minimum price increment
        self.adaptive_mode = True  # Auto-adjust based on price range
    
    def calculate_resolution(self, price_range):
        # PATTERN: Adaptive resolution based on price range
        if self.adaptive_mode:
            if price_range < 10:
                return 0.25  # Fine resolution for small ranges
            elif price_range < 100:
                return 1.0   # Medium resolution
            else:
                return 10.0  # Coarse resolution for large ranges
        return self.base_resolution
    
    def snap_to_grid(self, price, resolution):
        # CRITICAL: Snap prices to resolution grid
        return round(price / resolution) * resolution

# Cursor-to-price mapping
def cursor_to_price(cursor_row, chart_height, min_price, max_price):
    # PATTERN: Inverse of price_to_row function in chart.py
    normalized_position = (chart_height - 1 - cursor_row) / (chart_height - 1)
    return min_price + normalized_position * (max_price - min_price)

# Edit granularity controls
EDIT_MODES = {
    'fine': 0.25,     # For precise adjustments
    'normal': 1.0,    # Standard editing
    'coarse': 10.0,   # Quick large adjustments
    'adaptive': None  # Auto-adjust based on price range
}

# Key bindings for candle manipulation
KEY_BINDINGS = {
    'h': 'move_left',         # Navigate to previous candle
    'l': 'move_right',        # Navigate to next candle
    'k': 'move_up',           # Move cursor up (higher price)
    'j': 'move_down',         # Move cursor down (lower price)
    'H': 'extend_high',       # Extend upper wick
    'L': 'extend_low',        # Extend lower wick
    'O': 'adjust_open',       # Adjust open price
    'C': 'adjust_close',      # Adjust close price
    '+': 'increase_resolution', # Increase edit precision
    '-': 'decrease_resolution'  # Decrease edit precision
}
```

### Integration Points
```yaml
NEOVIM_CONFIG:
  - add to: init.vim or init.lua
  - pattern: "let g:python3_host_prog = '/path/to/python'"
  - note: "Required for pynvim communication"
  
PYTHON_ENVIRONMENT:
  - dependencies: "pandas, pynvim"
  - pattern: "pip install pandas pynvim"
  - note: "Must be in same environment as g:python3_host_prog"
  
PLUGIN_REGISTRATION:
  - command: ":UpdateRemotePlugins"
  - pattern: "Run after installing/updating Python plugin code"
  - note: "Required for Neovim to recognize new remote plugin functions"

CHART_RESOLUTION:
  - configuration: "User-configurable resolution settings"
  - adaptive_mode: "Auto-adjust precision based on price range"
  - manual_modes: "Fine (0.25), Normal (1.0), Coarse (10.0)"
  - real_time_sync: "Immediate DataFrame updates on chart modifications"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check src/new_feature.py --fix  # Auto-fix what's possible
mypy src/new_feature.py              # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE test_new_feature.py with these test cases:
def test_happy_path():
    """Basic functionality works"""
    result = new_feature("valid_input")
    assert result.status == "success"

def test_validation_error():
    """Invalid input raises ValidationError"""
    with pytest.raises(ValidationError):
        new_feature("")

def test_external_api_timeout():
    """Handles timeouts gracefully"""
    with mock.patch('external_api.call', side_effect=TimeoutError):
        result = new_feature("valid")
        assert result.status == "error"
        assert "timeout" in result.message
```

```bash
# Run and iterate until passing:
uv run pytest test_new_feature.py -v
# If failing: Read error, understand root cause, fix code, re-run (never mock to pass)
```

### Level 3: Integration Test
```bash
# Start the service
uv run python -m src.main --dev

# Test the endpoint
curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'

# Expected: {"status": "success", "data": {...}}
# If error: Check logs at logs/app.log for stack trace
```

## Final validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Manual test successful: [specific curl/command]
- [ ] Error cases handled gracefully
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"  
- ❌ Don't ignore failing tests - fix them
- ❌ Don't use sync functions in async context
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific
