# MCP Tools with TODO Enforcement

## Overview
This directory contains MCP tools with integrated TODO enforcement to ensure AI models complete required formatting tasks instead of summarizing data.

## Tools Available

### Sales Tools (`sales.py`)

#### 1. `get_sales` - Full TODO Tracking
- Complete task tracking with visual progress
- Step-by-step task completion monitoring
- Detailed enforcement with validation
- Best for: Production use where compliance is critical

#### 2. `get_sales_detail` - Invoice Details Tool
- Retrieves detailed invoice information
- Includes customer details and line items
- Standard MCP tool implementation

## TODO Enforcement System

### Components

1. **TaskTracker** (`task_tracker.py`)
   - Tracks task completion
   - Generates enforcement prompts
   - Monitors progress

## Usage Examples

### Running the Tools
```bash
# Start the MCP server
uv run main.py

# Use the sales tools:
"august sales"           # Uses get_sales (with TODO tracking)
"invoice SI25080001"     # Uses get_sales_detail (invoice details)
```

### Expected Output
Instead of a summary, you should see a formatted table:
```
╔════════════╦══════════════════╦═════════════════╗
║    Date    ║   Invoice No     ║     Amount      ║
╠════════════╬══════════════════╬═════════════════╣
║ 2025-08-25 ║ 2508000981      ║  RM 2,394.00    ║
║ 2025-08-25 ║ 2508000982      ║  RM   320.00    ║
╚════════════╩══════════════════╩═════════════════╝
```

## Testing

### Test Scripts
- `test_sales.py` - Tests enforcement patterns
- `test_get_sales.py` - Tests actual tool outputs

### Run Tests
```bash
# Test enforcement patterns
uv run python test_sales.py

# Test tool outputs
uv run python test_get_sales.py
```

## How It Works

1. **Tool receives request** (e.g., "august sales")
2. **Fetches data** from database
3. **Adds TODO enforcement** to output
4. **Returns to Claude** with explicit instructions
5. **Claude creates table** instead of summarizing

## Key Features

- **Direct Instructions**: Explicitly addresses "CLAUDE"
- **Clear Requirements**: Specifies exact format needed
- **Failure Warnings**: States consequences of non-compliance
- **Visual Emphasis**: Uses 🛑 symbols for attention
- **Progressive Enforcement**: Three levels of strength

## Troubleshooting

### If Claude Still Summarizes:
1. Check tool output isn't truncated
2. Verify MCP client passes full output
3. Review the TaskTracker enforcement prompts

### Common Issues:
- **Import errors**: Check paths in sales.py
- **Database errors**: Verify DB connection
- **No enforcement**: Ensure modules are imported

## Adding TODO Enforcement to New Tools

```python
from tools.task_tracker import TaskTracker

@mcp.tool(name="your_tool")
async def your_tool(param: str, *, context: Context) -> str:
    # Initialize tracker
    tracker = TaskTracker()
    tracker.add_task("TASK1", "First task")
    
    # Do work and mark complete
    result = do_something()
    tracker.mark_complete("TASK1")
    
    # Add enforcement
    enforcement = tracker.get_todo_enforcement()
    return result + enforcement
```

## Files

- `sales.py` - Sales tools with enforcement
- `task_tracker.py` - Task tracking system
- `TODO_IMPLEMENTATION.md` - Detailed documentation
- `SOLUTION.md` - Problem analysis and solution
- Test files for validation