local M = {}
local vim = vim

-- Chart state for interactive editing
local chart_state = {
  current_candle = 0,    -- Current candle index (0-based)
  current_row = 0,       -- Current row position in chart
  chart_height = 10,     -- Height of the chart
  num_candles = 0,       -- Total number of candles
  candle_width = 3,      -- Width of each candle in characters
  variable_name = nil,   -- DataFrame variable name for buffer-based state
  source_file = nil,     -- Original Python file path
}

function M.open_chart(df_variable_name)
  -- This function will be called from Neovim
  -- It will get the DataFrame from the Python process using buffer content
  -- and display the ASCII chart in a new buffer.

  -- Auto-detect variable name if not provided
  if not df_variable_name or df_variable_name == "" then
    df_variable_name = M.get_variable_under_cursor()
  end

  -- Check if we have a variable name
  if not df_variable_name or df_variable_name == "" then
    vim.notify("No DataFrame containing OHLC data found. Place cursor on a DataFrame variable or specify one with :VimtraderChart <variable_name>", vim.log.levels.ERROR)
    return
  end

  -- Store the variable name and source file for buffer-based operations
  chart_state.variable_name = df_variable_name
  chart_state.source_file = vim.api.nvim_buf_get_name(0)  -- Current buffer (the Python file)

  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(buf, 'bufhidden', 'wipe')
  vim.api.nvim_buf_set_option(buf, 'filetype', 'vimtrader')

  -- Make an RPC call to the Python backend to get chart string from buffer
  local ok, chart_string
  if chart_state.variable_name and chart_state.variable_name ~= "" then
    ok, chart_string = pcall(vim.fn.VimtraderGetDataFrameChart, chart_state.variable_name)
  else
    -- Fallback to sample chart if no variable name provided
    ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
  end
  
  if not ok then
    chart_string = "Error: Could not communicate with Python backend.\n\nPlease ensure:\n1. pynvim is installed (pip install pynvim)\n2. Run :UpdateRemotePlugins in Neovim\n3. Restart Neovim\n\nError details: " .. tostring(chart_string)
  end

  -- Ensure chart_string is a string before splitting
  if type(chart_string) ~= "string" then
    chart_string = "Error: Received unexpected data type from Python backend.\n\nExpected string, got: " .. type(chart_string) .. "\n\nPlease check that the remote plugin is properly registered.\nRun :UpdateRemotePlugins and restart Neovim."
  end

  -- Set the buffer content with the received chart string
  local chart_lines = vim.split(chart_string, '\n')
  
  -- Add key map help at the bottom
  local help_lines = {
    "",
    "H/J=high, K/L=low, O/P=open, C/V=close",
    "Other: q/ESC=quit, r=refresh, i=info"
  }
  
  -- Combine chart and help lines
  for _, line in ipairs(help_lines) do
    table.insert(chart_lines, line)
  end
  
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, chart_lines)
  
  -- Set up syntax highlighting for chart elements
  M.setup_chart_highlighting(buf)

  local win = vim.api.nvim_open_win(buf, true, {
    relative = 'editor',
    width = 80,
    height = 23,  -- Increased height for help lines
    row = math.floor((vim.o.lines - 23) / 2),
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
    
    -- Candle manipulation key bindings
    vim.keymap.set('n', 'H', function() M.adjust_candle_value('high', 1) end, opts)    -- Increase High
    vim.keymap.set('n', 'J', function() M.adjust_candle_value('high', -1) end, opts)   -- Decrease High
    vim.keymap.set('n', 'K', function() M.adjust_candle_value('low', 1) end, opts)     -- Increase Low
    vim.keymap.set('n', 'L', function() M.adjust_candle_value('low', -1) end, opts)    -- Decrease Low
    vim.keymap.set('n', 'O', function() M.adjust_candle_value('open', 1) end, opts)    -- Increase Open
    vim.keymap.set('n', 'P', function() M.adjust_candle_value('open', -1) end, opts)   -- Decrease Open
    vim.keymap.set('n', 'C', function() M.adjust_candle_value('close', 1) end, opts)   -- Increase Close
    vim.keymap.set('n', 'V', function() M.adjust_candle_value('close', -1) end, opts)  -- Decrease Close
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
  -- Refresh the current chart using buffer content
  local ok, chart_string
  if chart_state.variable_name and chart_state.variable_name ~= "" then
    ok, chart_string = pcall(vim.fn.VimtraderGetDataFrameChart, chart_state.variable_name)
  else
    -- Fallback to sample chart
    ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
  end
  if ok and type(chart_string) == "string" then
    local buf = vim.api.nvim_get_current_buf()
    local chart_lines = vim.split(chart_string, '\n')
    
    -- Add key map help at the bottom
    local help_lines = {
      "",
      "H/J=high, K/L=low, O/P=open, C/V=close",
      "Other: q/ESC=quit, r=refresh, i=info"
    }
    
    -- Combine chart and help lines
    for _, line in ipairs(help_lines) do
      table.insert(chart_lines, line)
    end
    
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, chart_lines)
    M.setup_chart_highlighting(buf)  -- Re-apply highlighting after refresh
    M.update_cursor_position(buf)    -- Re-apply cursor position and OHLC legend
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
  
  -- Define highlight group for OHLC legend
  vim.cmd('highlight VimtraderOHLCLegend guifg=#00ff00 guibg=NONE ctermfg=green ctermbg=NONE')
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
  local buf = vim.api.nvim_get_current_buf()
  M.update_cursor_position(buf)
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
  local buf = vim.api.nvim_get_current_buf()
  M.update_cursor_position(buf)
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
  
  -- Add OHLC legend for current candle
  M.update_ohlc_legend(buf)
end

function M.update_ohlc_legend(buf)
  -- Validate buffer parameter
  if not buf or not vim.api.nvim_buf_is_valid(buf) then
    buf = vim.api.nvim_get_current_buf()
  end
  
  -- Get OHLC values for current candle using buffer state
  local ok, ohlc_data = false, nil
  if chart_state.variable_name and chart_state.variable_name ~= "" and chart_state.source_file then
    ok, ohlc_data = pcall(vim.fn.VimtraderGetOHLCValues, chart_state.current_candle, chart_state.variable_name, chart_state.source_file)
  end
  
  -- If buffer-based OHLC failed, try sample data as fallback (for testing)
  if not ok or not ohlc_data or type(ohlc_data) ~= "string" or ohlc_data:match("^Error:") then
    -- Create a simple sample OHLC legend for display
    local sample_ohlc = {
      open = 100.0 + chart_state.current_candle * 2,
      high = 108.0 + chart_state.current_candle * 2,
      low = 98.0 + chart_state.current_candle * 2,
      close = 105.0 + chart_state.current_candle * 2
    }
    ohlc_data = string.format("open:%.1f,high:%.1f,low:%.1f,close:%.1f", 
                              sample_ohlc.open, sample_ohlc.high, sample_ohlc.low, sample_ohlc.close)
    ok = true
  end
  
  if ok and type(ohlc_data) == "string" and not ohlc_data:match("^Error:") then
    -- Parse OHLC data (format: "open:xxx,high:xxx,low:xxx,close:xxx")
    local open, high, low, close = ohlc_data:match("open:([^,]+),high:([^,]+),low:([^,]+),close:([^,]+)")
    
    if open and high and low and close then
      -- Create namespace for OHLC legend
      local ns_id = vim.api.nvim_create_namespace('vimtrader_ohlc_legend')
      
      -- Clear existing legend
      vim.api.nvim_buf_clear_namespace(buf, ns_id, 0, -1)
      
      -- Format the legend text
      local legend_text = string.format("[o:%.1f h:%.1f l:%.1f c:%.1f]", 
                                       tonumber(open) or 0, 
                                       tonumber(high) or 0, 
                                       tonumber(low) or 0, 
                                       tonumber(close) or 0)
      
      -- Position legend safely at the end of the help section
      local buf_lines = vim.api.nvim_buf_line_count(buf)
      local legend_row = math.max(0, buf_lines - 1)  -- Last line of buffer
      
      -- Add virtual text showing OHLC legend at end of line
      vim.api.nvim_buf_set_extmark(buf, ns_id, legend_row, 0, {
        virt_text = {{" " .. legend_text, 'VimtraderOHLCLegend'}},
        virt_text_pos = 'eol',  -- End of line instead of overlay
        priority = 150
      })
    end
  else
    -- Debug: Show why OHLC legend failed
    if not ok then
      -- RPC call failed
      vim.schedule(function()
        vim.notify("OHLC legend RPC call failed: " .. tostring(ohlc_data), vim.log.levels.DEBUG)
      end)
    elseif type(ohlc_data) ~= "string" then
      -- Wrong data type
      vim.schedule(function()
        vim.notify("OHLC legend got wrong data type: " .. type(ohlc_data), vim.log.levels.DEBUG)
      end)
    elseif ohlc_data and ohlc_data:match("^Error:") then
      -- Error response
      vim.schedule(function()
        vim.notify("OHLC legend error: " .. ohlc_data, vim.log.levels.DEBUG)
      end)
    end
  end
end

-- Candle manipulation functions
function M.adjust_candle_value(value_type, direction)
  -- Adjust High, Low, Open, or Close value for current candle
  -- value_type: 'high', 'low', 'open', 'close'
  -- direction: 1 for increase, -1 for decrease
  
  -- Use buffer-based state management with source file path
  local ok, result
  if chart_state.variable_name and chart_state.variable_name ~= "" and chart_state.source_file then
    ok, result = pcall(vim.fn.VimtraderAdjustCandle, chart_state.current_candle, value_type, direction, chart_state.variable_name, chart_state.source_file)
  else
    -- Fallback: use default variable name without file path (will try current buffer)
    ok, result = pcall(vim.fn.VimtraderAdjustCandle, chart_state.current_candle, value_type, direction, chart_state.variable_name or "df")
  end
  
  if ok and type(result) == "string" then
    -- Update the chart display with new data
    local buf = vim.api.nvim_get_current_buf()
    local chart_lines = vim.split(result, '\n')
    
    -- Add key map help at the bottom
    local help_lines = {
      "",
      "H/J=high, K/L=low, O/P=open, C/V=close",
      "Other: q/ESC=quit, r=refresh, i=info"
    }
    
    -- Combine chart and help lines
    for _, line in ipairs(help_lines) do
      table.insert(chart_lines, line)
    end
    
    vim.api.nvim_buf_set_lines(buf, 0, -1, false, chart_lines)
    M.setup_chart_highlighting(buf)
    M.update_cursor_position(buf)  -- Maintain cursor position and update legend after update
  else
    local error_msg = "Error adjusting candle: " .. tostring(result)
    
    -- If session creation failed, get detailed error info
    if string.match(tostring(result), "Could not create editor session") then
      local debug_ok, debug_result = pcall(vim.fn.VimtraderGetLastError)
      if debug_ok and debug_result then
        error_msg = error_msg .. "\n\nDebug info: " .. debug_result
      end
    end
    
    vim.notify(error_msg, vim.log.levels.ERROR)
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

-- Function to get the variable name under the cursor
function M.get_variable_under_cursor()
  -- Get current cursor position
  local cursor = vim.api.nvim_win_get_cursor(0)
  local row = cursor[1] - 1  -- Convert to 0-based indexing
  local col = cursor[2]
  
  -- Get the current line
  local line = vim.api.nvim_buf_get_lines(0, row, row + 1, false)[1]
  if not line then
    return nil
  end
  
  -- Find the word under the cursor
  -- Look for Python variable pattern (letters, numbers, underscore)
  local start_col = col
  local end_col = col
  
  -- Find start of word
  while start_col > 0 and string.match(string.sub(line, start_col, start_col), "[%w_]") do
    start_col = start_col - 1
  end
  start_col = start_col + 1
  
  -- Find end of word
  while end_col <= #line and string.match(string.sub(line, end_col + 1, end_col + 1), "[%w_]") do
    end_col = end_col + 1
  end
  
  -- Extract the variable name
  if start_col <= end_col then
    local variable_name = string.sub(line, start_col, end_col)
    -- Make sure it's a valid Python identifier (starts with letter or underscore)
    if string.match(variable_name, "^[%a_][%w_]*$") then
      return variable_name
    end
  end
  
  return nil
end

return M