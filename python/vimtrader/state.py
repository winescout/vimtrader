"""
Functional state management for VimTrader.

This module provides pure functions for managing state between the buffer
content and the chart editor using functional programming principles.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import pandas as pd
import re


@dataclass(frozen=True)
class EditorState:
    """
    Immutable state representing the current editor session.
    
    The buffer content is the single source of truth.
    All other state is derived from it.
    """
    buffer_content: str
    variable_name: str
    file_path: str
    cursor_position: Tuple[int, int] = (0, 0)


@dataclass(frozen=True)
class EditorCommand:
    """Immutable command representing an editor action."""
    command_type: str  # 'adjust_candle', 'move_cursor', etc.
    parameters: Dict[str, Any]


@dataclass(frozen=True)
class ParseResult:
    """Result of parsing a DataFrame from buffer content."""
    success: bool
    dataframe: Optional[pd.DataFrame]
    error_message: Optional[str]


def parse_dataframe_from_buffer(buffer_content: str, variable_name: str, file_path: str = '<buffer>') -> ParseResult:
    """
    Pure function to extract a DataFrame from buffer content.
    
    Args:
        buffer_content: The full text content of the buffer
        variable_name: Name of the DataFrame variable to extract
        file_path: Path to the file (used for __file__ variable)
        
    Returns:
        ParseResult with success status and DataFrame or error
    """
    try:
        # Create execution environment with comprehensive imports
        import datetime
        import numpy as np
        from datetime import datetime as dt, date, timedelta
        
        # Common imports for data analysis
        exec_globals = {
            'pd': pd,
            'pandas': pd,
            'datetime': datetime,  # The datetime module
            'dt': dt,              # datetime.datetime class
            'date': date,
            'timedelta': timedelta,
            'np': np,
            'numpy': np,
            '__name__': '__main__',
            '__file__': file_path,  # Provide the actual file path
            '__doc__': None,        # Document string
            '__package__': None,    # Package name
            '__builtins__': __builtins__
        }
        
        # Handle datetime imports - provide the actual module with shortcuts
        import datetime as datetime_module
        exec_globals['datetime'] = datetime_module
        
        # Also add common shortcuts directly to the global namespace for convenience
        exec_globals['now'] = datetime_module.datetime.now
        exec_globals['today'] = datetime_module.datetime.today
        exec_globals['utcnow'] = datetime_module.datetime.utcnow
        exec_locals = {}
        
        # Try to add other common modules if available
        try:
            import math
            exec_globals['math'] = math
        except ImportError:
            pass
            
        try:
            import random
            exec_globals['random'] = random
        except ImportError:
            pass
            
        try:
            import os
            exec_globals['os'] = os
        except ImportError:
            pass
            
        try:
            import sys
            exec_globals['sys'] = sys
        except ImportError:
            pass
        
        # Execute the buffer content safely, suppressing stdout
        import io
        import contextlib
        
        try:
            # Capture and suppress stdout during execution
            with contextlib.redirect_stdout(io.StringIO()):
                exec(buffer_content, exec_globals, exec_locals)
        except AttributeError as e:
            # Handle common datetime usage errors
            error_msg = str(e)
            if ("has no attribute 'now'" in error_msg and "datetime" in error_msg) or \
               ("has no attribute 'today'" in error_msg and "datetime" in error_msg):
                # User is trying to use datetime.now() instead of datetime.datetime.now()
                # Add a custom datetime module that supports this pattern
                import types
                custom_datetime = types.ModuleType('datetime')
                
                # Copy all original datetime module contents
                import datetime as original_datetime
                for attr in dir(original_datetime):
                    if not attr.startswith('_'):
                        setattr(custom_datetime, attr, getattr(original_datetime, attr))
                
                # Add shortcuts for common patterns
                custom_datetime.now = original_datetime.datetime.now
                custom_datetime.today = original_datetime.datetime.today
                custom_datetime.utcnow = original_datetime.datetime.utcnow
                
                # Replace in globals and retry with stdout suppression
                exec_globals['datetime'] = custom_datetime
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(buffer_content, exec_globals, exec_locals)
            else:
                raise
        
        # Extract the specific DataFrame
        if variable_name in exec_locals:
            df = exec_locals[variable_name]
        elif variable_name in exec_globals:
            df = exec_globals[variable_name]
        else:
            # Provide helpful debugging information
            available_vars = []
            for name, value in exec_locals.items():
                if not name.startswith('_'):
                    available_vars.append(f"{name}({type(value).__name__})")
            for name, value in exec_globals.items():
                if not name.startswith('_') and name not in ['pd', 'pandas', 'datetime', 'np', 'numpy', 'math', 'random', 'os', 'sys', 'dt', 'date', 'timedelta', 'now', 'today', 'utcnow']:
                    available_vars.append(f"{name}({type(value).__name__})")
            
            # Filter for DataFrames specifically
            dataframe_vars = [var for var in available_vars if 'DataFrame' in var]
            
            if dataframe_vars:
                available_msg = f"Available DataFrames: {', '.join(dataframe_vars)}"
            elif available_vars:
                available_msg = f"No DataFrames containing OHLC data found. Available variables: {', '.join(available_vars)}"
            else:
                available_msg = "No DataFrames containing OHLC data found"
            
            return ParseResult(
                success=False,
                dataframe=None,
                error_message=f"Variable '{variable_name}' not found. {available_msg}"
            )
        
        # Validate it's a DataFrame
        if not isinstance(df, pd.DataFrame):
            return ParseResult(
                success=False,
                dataframe=None,
                error_message=f"Variable '{variable_name}' is not a pandas DataFrame"
            )
        
        # Validate required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ParseResult(
                success=False,
                dataframe=None,
                error_message=f"DataFrame missing required columns: {missing_columns}"
            )
        
        return ParseResult(
            success=True,
            dataframe=df.copy(),  # Return immutable copy
            error_message=None
        )
        
    except AttributeError as e:
        # Handle datetime-specific AttributeErrors separately
        error_msg = str(e)
        if ("has no attribute 'now'" in error_msg and "datetime" in error_msg) or \
           ("has no attribute 'today'" in error_msg and "datetime" in error_msg):
            return ParseResult(
                success=False,
                dataframe=None,
                error_message=f"Datetime usage error: Use 'datetime.datetime.now()' instead of 'datetime.now()'. Error: {str(e)}"
            )
        else:
            return ParseResult(
                success=False,
                dataframe=None,
                error_message=f"Error parsing buffer: {str(e)}"
            )
    except Exception as e:
        return ParseResult(
            success=False,
            dataframe=None,
            error_message=f"Error parsing buffer: {str(e)}"
        )


def find_dataframe_definition(buffer_content: str, variable_name: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Find the line range where a DataFrame is defined.
    
    Args:
        buffer_content: Buffer content to search
        variable_name: Variable name to find
        
    Returns:
        Tuple of (start_line, end_line) or (None, None) if not found
    """
    lines = buffer_content.split('\n')
    
    for i, line in enumerate(lines):
        # Look for DataFrame assignment
        if f"{variable_name} = pd.DataFrame(" in line:
            start_line = i
            
            # Count brackets to find end of definition
            bracket_count = line.count('(') - line.count(')')
            end_line = i
            
            while end_line < len(lines) - 1 and bracket_count > 0:
                end_line += 1
                next_line = lines[end_line]
                bracket_count += next_line.count('(') - next_line.count(')')
            
            return start_line, end_line
    
    return None, None


def dataframe_to_code(df: pd.DataFrame, variable_name: str) -> str:
    """
    Pure function to convert a DataFrame to Python code.
    
    Args:
        df: DataFrame to serialize
        variable_name: Variable name to use
        
    Returns:
        Python code string representing the DataFrame
    """
    # Create dictionary representation
    data_dict = {}
    for col in df.columns:
        values = df[col].tolist()
        # Format numbers appropriately
        formatted_values = []
        for val in values:
            if isinstance(val, (int, float)):
                if val == int(val):
                    formatted_values.append(str(int(val)))
                else:
                    formatted_values.append(f"{val:.1f}")
            else:
                formatted_values.append(repr(val))
        data_dict[col] = formatted_values
    
    # Generate code with proper formatting
    lines = [f"{variable_name} = pd.DataFrame({{"]
    for i, (col, values) in enumerate(data_dict.items()):
        comma = ',' if i < len(data_dict) - 1 else ''
        values_str = '[' + ', '.join(values) + ']'
        lines.append(f"    '{col}': {values_str}{comma}")
    lines.append("})")
    
    return '\n'.join(lines)


def update_buffer_with_dataframe(buffer_content: str, variable_name: str, 
                                df: pd.DataFrame) -> str:
    """
    Pure function to update buffer content with a new DataFrame.
    
    Args:
        buffer_content: Original buffer content
        variable_name: Variable name to update
        df: New DataFrame to insert
        
    Returns:
        Updated buffer content
    """
    lines = buffer_content.split('\n')
    start_line, end_line = find_dataframe_definition(buffer_content, variable_name)
    
    if start_line is None:
        # Variable not found, append at end
        new_code = dataframe_to_code(df, variable_name)
        return buffer_content + '\n\n' + new_code
    
    # Replace existing definition
    new_code = dataframe_to_code(df, variable_name)
    new_lines = new_code.split('\n')
    
    # Replace the lines
    updated_lines = lines[:start_line] + new_lines + lines[end_line + 1:]
    
    return '\n'.join(updated_lines)


def apply_candle_adjustment(df: pd.DataFrame, candle_index: int, 
                          value_type: str, direction: int) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Pure function to apply a candle adjustment to a DataFrame with intelligent constraint handling.
    
    Logic: When Open/Close change, High/Low automatically adjust to maintain valid OHLC:
    - high = max(open, close) if max(open, close) > high else high  
    - low = min(open, close) if min(open, close) < low else low
    
    Args:
        df: Original DataFrame
        candle_index: Index of candle to adjust
        value_type: 'high', 'low', 'open', or 'close'
        direction: 1 for increase, -1 for decrease
        
    Returns:
        Tuple of (new_dataframe, error_message)
    """
    # Validate inputs
    if candle_index < 0 or candle_index >= len(df):
        return df, f"Candle index {candle_index} out of range"
    
    if value_type not in ['high', 'low', 'open', 'close']:
        return df, f"Invalid value type: {value_type}"
    
    if not isinstance(direction, (int, float)):
        return df, f"Invalid direction: {direction}"
    
    # Create immutable copy
    new_df = df.copy()
    
    # Apply adjustment
    adjustment = 1.0 * direction
    column_name = value_type.capitalize()
    current_value = new_df.iloc[candle_index][column_name]
    new_value = current_value + adjustment
    
    # Update the primary value
    new_df.iloc[candle_index, new_df.columns.get_loc(column_name)] = new_value
    
    # Get updated OHLC values after the adjustment
    candle_open = new_df.iloc[candle_index]['Open']
    candle_close = new_df.iloc[candle_index]['Close']
    candle_high = new_df.iloc[candle_index]['High']
    candle_low = new_df.iloc[candle_index]['Low']
    
    # Apply intelligent constraint logic
    # High should be at least max(open, close)
    new_high = max(candle_open, candle_close) if max(candle_open, candle_close) > candle_high else candle_high
    new_df.iloc[candle_index, new_df.columns.get_loc('High')] = new_high
    
    # Low should be at most min(open, close)  
    new_low = min(candle_open, candle_close) if min(candle_open, candle_close) < candle_low else candle_low
    new_df.iloc[candle_index, new_df.columns.get_loc('Low')] = new_low
    
    return new_df, None


def handle_editor_command(state: EditorState, command: EditorCommand) -> Tuple[EditorState, Optional[str]]:
    """
    Pure function to handle an editor command and return new state.
    
    Args:
        state: Current editor state
        command: Command to execute
        
    Returns:
        Tuple of (new_state, error_message)
    """
    if command.command_type == 'adjust_candle':
        # Parse current DataFrame from buffer
        parse_result = parse_dataframe_from_buffer(state.buffer_content, state.variable_name, state.file_path)
        if not parse_result.success:
            return state, parse_result.error_message
        
        # Apply the adjustment
        new_df, error_msg = apply_candle_adjustment(
            parse_result.dataframe,
            command.parameters['candle_index'],
            command.parameters['value_type'],
            command.parameters['direction']
        )
        
        if error_msg:
            return state, error_msg
        
        # Update buffer with new DataFrame
        new_buffer_content = update_buffer_with_dataframe(
            state.buffer_content,
            state.variable_name,
            new_df
        )
        
        # Return new state
        new_state = EditorState(
            buffer_content=new_buffer_content,
            variable_name=state.variable_name,
            file_path=state.file_path,
            cursor_position=state.cursor_position
        )
        
        return new_state, None
    
    elif command.command_type == 'move_cursor':
        # Simple cursor movement
        new_position = (
            command.parameters['row'],
            command.parameters['col']
        )
        
        new_state = EditorState(
            buffer_content=state.buffer_content,
            variable_name=state.variable_name,
            file_path=state.file_path,
            cursor_position=new_position
        )
        
        return new_state, None
    
    else:
        return state, f"Unknown command type: {command.command_type}"


def get_current_dataframe(state: EditorState) -> ParseResult:
    """
    Pure function to get the current DataFrame from editor state.
    
    Args:
        state: Current editor state
        
    Returns:
        ParseResult with the current DataFrame
    """
    return parse_dataframe_from_buffer(state.buffer_content, state.variable_name, state.file_path)


def create_editor_state(buffer_content: str, variable_name: str, file_path: str) -> EditorState:
    """
    Pure function to create initial editor state.
    
    Args:
        buffer_content: Initial buffer content
        variable_name: DataFrame variable name
        file_path: Path to the file
        
    Returns:
        New EditorState
    """
    return EditorState(
        buffer_content=buffer_content,
        variable_name=variable_name,
        file_path=file_path,
        cursor_position=(0, 0)
    )


# Command constructors (pure functions)
def create_candle_adjustment_command(candle_index: int, value_type: str, direction: int) -> EditorCommand:
    """Create a candle adjustment command."""
    return EditorCommand(
        command_type='adjust_candle',
        parameters={
            'candle_index': candle_index,
            'value_type': value_type,
            'direction': direction
        }
    )


def create_cursor_movement_command(row: int, col: int) -> EditorCommand:
    """Create a cursor movement command."""
    return EditorCommand(
        command_type='move_cursor',
        parameters={
            'row': row,
            'col': col
        }
    )