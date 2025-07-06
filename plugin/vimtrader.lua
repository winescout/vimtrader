local vim = vim

-- Bootstrap the vimtrader module
_G.vimtrader = require("vimtrader.main")

-- Define a user command to open the chart
vim.api.nvim_create_user_command(
  "VimtraderChart",
  function(opts)
    _G.vimtrader.open_chart(opts.fargs[1])
  end,
  {
    nargs = '?',
    complete = "file",
    desc = "Open Vimtrader Chart for a DataFrame variable",
  }
)

-- Define a command to test plugin registration
vim.api.nvim_create_user_command(
  "VimtraderTest",
  function()
    _G.vimtrader.test_plugin()
  end,
  {
    desc = "Test VimTrader plugin registration",
  }
)