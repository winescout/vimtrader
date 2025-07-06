local M = {}
local vim = vim

function M.open_chart(df_variable_name)
  -- This function will be called from Neovim
  -- It will eventually get the DataFrame from the Python process
  -- and display the ASCII chart in a new buffer.

  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_option(buf, 'bufhidden', 'wipe')

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
  end
  
  setup_keybindings()
end

function M.refresh_chart()
  -- Refresh the current chart
  local ok, chart_string = pcall(vim.fn.VimtraderGetSampleChart)
  if ok and type(chart_string) == "string" then
    vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(chart_string, '\n'))
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

return M