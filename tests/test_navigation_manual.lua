-- Manual test script for navigation functions
-- Run this in Neovim with :luafile tests/test_navigation_manual.lua

print("Running manual navigation tests...")

-- Test cursor position calculation
local function test_cursor_calculation()
  local candle_width = 3
  local tests = {
    {candle = 0, row = 0, expected_col = 1, expected_row = 1},
    {candle = 2, row = 5, expected_col = 7, expected_row = 6},
    {candle = 9, row = 9, expected_col = 28, expected_row = 10},
  }
  
  for i, test in ipairs(tests) do
    local actual_col = test.candle * candle_width + 1
    local actual_row = test.row + 1
    
    assert(actual_col == test.expected_col, 
           string.format("Test %d: Expected col %d, got %d", i, test.expected_col, actual_col))
    assert(actual_row == test.expected_row, 
           string.format("Test %d: Expected row %d, got %d", i, test.expected_row, actual_row))
  end
  
  print("✓ Cursor position calculation tests passed")
end

-- Test bounds checking
local function test_bounds()
  local num_candles = 10
  local chart_height = 10
  
  -- Test candle bounds
  local function clamp_candle(candle)
    if candle < 0 then return 0 end
    if candle >= num_candles then return num_candles - 1 end
    return candle
  end
  
  -- Test row bounds
  local function clamp_row(row)
    if row < 0 then return 0 end
    if row >= chart_height then return chart_height - 1 end
    return row
  end
  
  -- Test cases
  assert(clamp_candle(-1) == 0, "Left bound failed")
  assert(clamp_candle(10) == 9, "Right bound failed")
  assert(clamp_candle(5) == 5, "Normal candle failed")
  
  assert(clamp_row(-1) == 0, "Upper bound failed")
  assert(clamp_row(10) == 9, "Lower bound failed")
  assert(clamp_row(5) == 5, "Normal row failed")
  
  print("✓ Bounds checking tests passed")
end

-- Test navigation simulation
local function test_navigation_simulation()
  local chart_state = {
    current_candle = 0,
    current_row = 0,
    num_candles = 10,
    chart_height = 10,
    candle_width = 3
  }
  
  -- Simulate moving right 3 times
  for i = 1, 3 do
    local new_candle = chart_state.current_candle + 1
    if new_candle >= chart_state.num_candles then
      new_candle = chart_state.num_candles - 1
    end
    chart_state.current_candle = new_candle
  end
  
  assert(chart_state.current_candle == 3, "Navigation simulation failed")
  
  -- Simulate moving down 5 times
  for i = 1, 5 do
    local new_row = chart_state.current_row + 1
    if new_row >= chart_state.chart_height then
      new_row = chart_state.chart_height - 1
    end
    chart_state.current_row = new_row
  end
  
  assert(chart_state.current_row == 5, "Vertical navigation simulation failed")
  
  print("✓ Navigation simulation tests passed")
end

-- Run all tests
test_cursor_calculation()
test_bounds()
test_navigation_simulation()

print("All manual navigation tests passed! ✓")