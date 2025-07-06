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
  -- Refresh the current chart
  local ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
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
  
  -- Get OHLC values for current candle
  local ok, ohlc_data = pcall(vim.fn.VimtraderGetOHLCValues, chart_state.current_candle)
  
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
      
      -- Position legend in bottom right of chart area (around row 9, right-aligned)
      local legend_row = 9  -- Near bottom of 10-row chart
      local chart_width = 30  -- Approximate chart width
      local legend_col = math.max(0, chart_width - string.len(legend_text))
      
      -- Add virtual text showing OHLC legend
      vim.api.nvim_buf_set_extmark(buf, ns_id, legend_row, legend_col, {
        virt_text = {{legend_text, 'VimtraderOHLCLegend'}},
        virt_text_pos = 'overlay',
        priority = 150
      })
    end
  end
end

-- Candle manipulation functions
function M.adjust_candle_value(value_type, direction)
  -- Adjust High, Low, Open, or Close value for current candle
  -- value_type: 'high', 'low', 'open', 'close'
  -- direction: 1 for increase, -1 for decrease
  
  local ok, result = pcall(vim.fn.VimtraderAdjustCandle, chart_state.current_candle, value_type, direction)
  
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

return M