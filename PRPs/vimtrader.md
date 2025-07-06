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
- [ ] A user can invoke the plugin on a pandas DataFrame, opening a new edit window.
- [ ] The edit window displays a properly scaled ASCII candlestick chart.
- [ ] The user can navigate between bars (left/right) and select parts of a bar (up/down).
- [ ] Key commands are implemented for:
    - [ ] Growing/shrinking the upper wick.
    - [ ] Growing/shrinking the lower wick.
    - [ ] Growing/shrinking the body.
    - [ ] Moving the entire candle up/down.
    - [ ] Adding a new bullish/bearish candle to the left/right.
- [ ] Changes made in the ASCII chart are reflected back into the original pandas DataFrame.

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
│       ├── init.lua  # Neovim plugin entrypoint
│       └── main.lua    # Main plugin logic in Lua
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
  - CREATE the `editor.py` module.
  - IMPLEMENT the logic to handle user input and modify the DataFrame.

Task 4: Create the Neovim plugin:
  - CREATE the Lua code to connect to the Python backend.
  - IMPLEMENT the logic to display the chart in a new window.

Task 5: Write unit tests:
  - CREATE tests for the `chart.py` module.
  - CREATE tests for the `editor.py` module.
```


### Per task pseudocode as needed added to each task
```python

# Task 1
# Pseudocode with CRITICAL details dont write entire code
async def new_feature(param: str) -> Result:
    # PATTERN: Always validate input first (see src/validators.py)
    validated = validate_input(param)  # raises ValidationError
    
    # GOTCHA: This library requires connection pooling
    async with get_connection() as conn:  # see src/db/pool.py
        # PATTERN: Use existing retry decorator
        @retry(attempts=3, backoff=exponential)
        async def _inner():
            # CRITICAL: API returns 429 if >10 req/sec
            await rate_limiter.acquire()
            return await external_api.call(validated)
        
        result = await _inner()
    
    # PATTERN: Standardized response format
    return format_response(result)  # see src/utils/responses.py
```

### Integration Points
```yaml
DATABASE:
  - migration: "Add column 'feature_enabled' to users table"
  - index: "CREATE INDEX idx_feature_lookup ON users(feature_id)"
  
CONFIG:
  - add to: config/settings.py
  - pattern: "FEATURE_TIMEOUT = int(os.getenv('FEATURE_TIMEOUT', '30'))"
  
ROUTES:
  - add to: src/api/routes.py  
  - pattern: "router.include_router(feature_router, prefix='/feature')"
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
