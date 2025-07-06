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
To create a Neovim plugin that allows a user to visually edit a pandas DataFrame of OHLCV data as an ASCII stock chart.

## Why
- **Business value and user impact**: This tool will dramatically accelerate the process of creating and customizing test data for developers of automated trading strategies.
- **Integration with existing features**: The plugin will be invoked from a Python script, operating on a pandas DataFrame object in memory.
- **Problems this solves and for whom**: It solves the cumbersome and non-intuitive process of manually creating OHLCV data for testing trading algorithms. It is for Python developers and quantitative analysts who build and test these strategies.

## What
A user, while working in a Python script, will place their cursor on a pandas DataFrame variable containing OHLCV data. By running a Vim command, a new window will open, displaying an ASCII representation of the data. The user can then navigate and modify the chart using key commands, and the underlying DataFrame in the original Python script will be updated in real-time.

### Success Criteria
- [x] A user can invoke the plugin on a pandas DataFrame, opening a new edit window.
- [x] The edit window displays a properly scaled ASCII candlestick chart.
- [ ] The user can navigate between bars (left/right) and select parts of a bar (up/down).
- [ ] Key commands are implemented for:
    - [ ] Growing/shrinking the upper wick.
    - [ ] Growing/shrinking the lower wick.
    - [ ] Growing/shrinking the body.
    - [ ] Moving the entire candle up/down.
    - [ ] Adding a new bullish/bearish candle to the left/right.
- [ ] Changes made in the ASCII chart are reflected back into the original pandas DataFrame.
- [ ] Interactive editing supports configurable resolution/precision for value adjustments.

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

Task 6: Implement interactive editing capabilities:
  - [ ] ADD cursor positioning and navigation (left/right between candles, up/down within candles)
  - [ ] IMPLEMENT configurable resolution system for price adjustments
  - [ ] ADD key bindings for candle manipulation (wick adjustment, body resizing, moving candles)
  - [ ] IMPLEMENT real-time DataFrame synchronization
```


### Per task pseudocode as needed added to each task
```python

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
