local M = {}
local vim = vim

-- Chart state for interactive editing
local chart_state = {
  current_candle = 0,    -- Current candle index (0-based)
  current_row = 0,       -- Current row position in chart
  chart_height = 10,     -- Height of the chart
  num_candles = 0,       -- Total number of candles
  candle_width = 3,      -- Width of each candle in characters
}

function M.open_chart(df_variable_name)
  -- This function will be called from Neovim
  -- It will eventually get the DataFrame from the Python process
  -- and display the ASCII chart in a new buffer.

  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(buf, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(buf, 'filetype', 'vimtrader')

  -- Make an RPC call to the Python backend to get chart string
  -- Use vim.fn.VimtraderGetSampleChart for now (will be replaced with real DataFrame data)
  local ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
  
  if not ok then
    chart_string = "Error: Could not communicate with Python backend.\n\nPlease ensure:\n1. pynvim is installed (pip install pynvim)\n2. Run :UpdateRemotePlugins in Neovim\n3. Restart Neovim\n\nError details: " .. tostring(chart_string)
  end

  -- Ensure chart_string is a string before splitting
  if type(chart_string) ~= "string" then
    chart_string = "Error: Received unexpected data type from Python backend.\n\nExpected string, got: " .. type(chart_string) .. "\n\nPlease check that the remote plugin is properly registered.\nRun :UpdateRemotePlugins and restart Neovim."
  end

  -- Set the buffer content with the received chart string
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, vim.split(chart_string, '\n'))
  
  -- Set up syntax highlighting for chart elements
  M.setup_chart_highlighting(buf)

  local win = vim.api.nvim_open_win(buf, true, {
    relative = 'editor',
    width = 80,
    height = 20,
    row = math.floor((vim.o.lines - 20) / 2),
    col = math.floor((vim.o.columns - 80) / 2),
    border = 'single',
  })

  vim.api.nvim_win_set_option(win, 'winhl', 'Normal:Normal,FloatBorder:FloatBorder')
  
  -- Set up keybindings for the chart window
  local function setup_keybindings()
    local opts = { noremap = true, silent = true, buffer = buf }
    vim.keymap.set('n', 'q', '<cmd>close<cr>', opts)
    vim.keymap.set('n', '<ESC>', '<cmd>close<cr>', opts)
    vim.keymap.set('n', 'r', function() M.refresh_chart() end, opts)
    vim.keymap.set('n', 'i', function() M.show_python_info() end, opts)
    
    -- Interactive navigation - candle-by-candle movement
    vim.keymap.set('n', 'h', function() M.move_to_candle(-1) end, opts)  -- Previous candle
    vim.keymap.set('n', 'l', function() M.move_to_candle(1) end, opts)   -- Next candle
    vim.keymap.set('n', 'j', function() M.move_cursor_vertical(1) end, opts)   -- Move down
    vim.keymap.set('n', 'k', function() M.move_cursor_vertical(-1) end, opts)  -- Move up
  end
  
  setup_keybindings()
  
  -- Initialize chart state
  chart_state.num_candles = 10  -- Sample data has 10 candles
  chart_state.current_candle = 0
  chart_state.current_row = 0
  
  -- Position cursor at first candle
  M.update_cursor_position(buf, win)
  
  -- Add a test: manually color the first few characters to verify highlighting works
  vim.schedule(function()
    local test_ns = vim.api.nvim_create_namespace('test_highlights')
    vim.api.nvim_buf_add_highlight(buf, test_ns, 'VimtraderBullish', 0, 0, 5)  -- First 5 chars green
    vim.api.nvim_buf_add_highlight(buf, test_ns, 'VimtraderBearish', 1, 0, 5)  -- Second line first 5 chars red
  end)
end

function M.refresh_chart()
  -- Refresh the current chart
  local ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
  if ok and type(chart_string) == "string" then
    local buf = vim.api.nvim_get_current_buf()
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, vim.split(chart_string, '\n'))
    M.setup_chart_highlighting(buf)  -- Re-apply highlighting after refresh
  else
    local error_msg = "Error refreshing chart: " .. tostring(chart_string)
    if type(chart_string) ~= "string" then
      error_msg = error_msg .. "\nData type: " .. type(chart_string)
    end
    vim.notify(error_msg, vim.log.levels.ERROR)
  end
end

function M.show_python_info()
  -- Show Python environment info for debugging
  local ok, info = pcall(vim.fn.VimtraderGetPythonInfo)
  if ok and type(info) == "string" then
    vim.notify(info, vim.log.levels.INFO)
  else
    vim.notify("Error getting Python info: " .. tostring(info) .. "\nType: " .. type(info), vim.log.levels.ERROR)
  end
end

function M.test_plugin()
  -- Test if the remote plugin functions are available
  local functions_to_test = {
    'VimtraderTest',
    'VimtraderGetDummyChartString',
    'VimtraderGetSampleChart',
    'VimtraderGetPythonInfo'
  }
  
  local results = {}
  for _, func_name in ipairs(functions_to_test) do
    local ok, result = pcall(vim.fn[func_name])
    local result_preview = ""
    if ok and type(result) == "string" then
      result_preview = " -> " .. string.sub(result, 1, 30) .. (string.len(result) > 30 and "..." or "")
    end
    table.insert(results, func_name .. ": " .. (ok and "OK" or "FAILED") .. " (type: " .. type(result) .. ")" .. result_preview)
  end
  
  vim.notify("Plugin Function Test Results:\n" .. table.concat(results, "\n"), vim.log.levels.INFO)
end

function M.setup_chart_highlighting(buf)
  -- Clear any syntax highlighting to show plain ASCII
  vim.api.nvim_buf_call(buf, function()
    vim.cmd('syntax clear')
  end)
end

-- Interactive navigation functions
function M.move_to_candle(direction)
  -- Move to previous (-1) or next (1) candle
  local new_candle = chart_state.current_candle + direction
  
  -- Bounds checking
  if new_candle < 0 then
    new_candle = 0
  elseif new_candle >= chart_state.num_candles then
    new_candle = chart_state.num_candles - 1
  end
  
  chart_state.current_candle = new_candle
  M.update_cursor_position()
end

function M.move_cursor_vertical(direction)
  -- Move cursor up (-1) or down (1)
  local new_row = chart_state.current_row + direction
  
  -- Bounds checking
  if new_row < 0 then
    new_row = 0
  elseif new_row >= chart_state.chart_height then
    new_row = chart_state.chart_height - 1
  end
  
  chart_state.current_row = new_row
  M.update_cursor_position()
end

function M.update_cursor_position(buf, win)
  -- Calculate cursor position based on current candle and row
  local col = chart_state.current_candle * chart_state.candle_width + 1  -- Center of candle
  local row = chart_state.current_row
  
  -- Set cursor position in the window
  if win and vim.api.nvim_win_is_valid(win) then
    vim.api.nvim_win_set_cursor(win, {row + 1, col})  -- Vim uses 1-based indexing
  else
    -- If no window provided, use current window
    local current_win = vim.api.nvim_get_current_win()
    if vim.api.nvim_win_is_valid(current_win) then
      vim.api.nvim_win_set_cursor(current_win, {row + 1, col})
    end
  end
end

-- Remove the complex highlighting function since we're using syntax highlighting now

function M.apply_alternating_colors(buf)
  -- Apply colors based on actual candle types from Python
  if not vim.api.nvim_buf_is_valid(buf) then
    return
  end
  
  -- Create a dedicated namespace for our highlights
  local ns_id = vim.api.nvim_create_namespace('vimtrader_highlights')
  
  -- Clear existing highlights in our namespace
  vim.api.nvim_buf_clear_namespace(buf, ns_id, 0, -1)
  
  -- Get candle type information from Python
  local ok, candle_types_str = pcall(vim.fn.VimtraderGetCandleTypes)
  
  if not ok or type(candle_types_str) ~= "string" then
    -- Fallback to simple alternating colors
    M.apply_simple_alternating_colors_with_namespace(buf, ns_id)
    return
  end
  
  -- Parse candle types (B for bullish, R for bearish)
  local candle_types = {}
  for candle_type in string.gmatch(candle_types_str, "[^,]+") do
    table.insert(candle_types, string.upper(string.gsub(candle_type, "%s", "")))  -- Clean whitespace and uppercase
  end
  
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  
  -- Color each candle as a complete unit
  for candle_idx, candle_type in ipairs(candle_types) do
    local highlight_group = nil
    if candle_type == 'B' then
      highlight_group = 'VimtraderBullish'
    elseif candle_type == 'R' then
      highlight_group = 'VimtraderBearish'
    end
    
    if highlight_group then
      -- Calculate the column range for this candle (3 chars wide, centered at pos 1)
      local candle_center_col = (candle_idx - 1) * 3 + 1  -- Center column (where █ should be)
      
      -- Apply color to all █ characters in this candle's column
      for line_num, line in ipairs(lines) do
        if #line > candle_center_col and string.sub(line, candle_center_col + 1, candle_center_col + 1) == '█' then
          vim.api.nvim_buf_add_highlight(buf, ns_id, highlight_group, line_num - 1, candle_center_col, candle_center_col + 1)
        end
      end
    end
  end
end

function M.apply_simple_alternating_colors_with_namespace(buf, ns_id)
  -- Simple fallback: color candles by column in alternating pattern
  local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
  
  -- Color each candle column separately
  for candle_idx = 0, 9 do  -- Assume max 10 candles
    local candle_center_col = candle_idx * 3 + 1  -- Center column for this candle
    local highlight_group = candle_idx % 2 == 0 and 'VimtraderBullish' or 'VimtraderBearish'
    
    -- Apply color to all █ characters in this candle's column
    for line_num, line in ipairs(lines) do
      if #line > candle_center_col and string.sub(line, candle_center_col + 1, candle_center_col + 1) == '█' then
        vim.api.nvim_buf_add_highlight(buf, ns_id, highlight_group, line_num - 1, candle_center_col, candle_center_col + 1)
      end
    end
  end
end

return M