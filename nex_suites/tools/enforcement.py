"""
Enforcement patterns for ensuring AI compliance with task requirements.
"""
from typing import List, Dict, Any


class EnforcementPatterns:
    """Collection of enforcement patterns for AI task completion."""
    
    @staticmethod
    def simple_reminder(task: str) -> str:
        """Simple one-line reminder."""
        return f"\n\n🛑 CLAUDE, YOU MUST NOW: {task}. DO NOT SUMMARIZE - CREATE THE TABLE!"
    
    @staticmethod
    def todo_list_pattern(tasks: List[str]) -> str:
        """TODO list pattern with checkboxes."""
        todo = """
================================================================================
📋 AI TODO LIST - MUST COMPLETE ALL TASKS
================================================================================
"""
        for i, task in enumerate(tasks, 1):
            todo += f"□ TASK {i}: {task}\n"
        
        todo += """
❌ FAILURE: Skipping any task
✅ SUCCESS: Completing all tasks in order

[START YOUR WORK BELOW]
"""
        return todo
    
    @staticmethod
    def contract_pattern(requirements: Dict[str, Any]) -> str:
        """Contract-based enforcement."""
        contract = """
┌─────────────────────────────────────────────────┐
│           📜 AI EXECUTION CONTRACT              │
├─────────────────────────────────────────────────┤
│                                                 │
│ I, the AI, hereby agree to:                    │
│                                                 │"""
        
        for i, (key, value) in enumerate(requirements.items(), 1):
            contract += f"\n│ {i}. ☐ {value:<40} │"
        
        contract += """
│                                                 │
│ Failure to complete = Contract breach           │
│                                                 │
│ Signed: _______________ (AI must execute)      │
└─────────────────────────────────────────────────┘

FULFILL CONTRACT BY EXECUTING NOW:
"""
        return contract
    
    @staticmethod
    def step_by_step_pattern(steps: List[Dict[str, str]]) -> str:
        """Step-by-step execution pattern."""
        output = ""
        total_steps = len(steps)
        
        for i, step in enumerate(steps, 1):
            output += f"""
STEP {i}/{total_steps}: {step.get('title', 'Execute')}
{'-' * 50}
{step.get('instruction', '')}

Complete this step before moving to step {i+1 if i < total_steps else 'completion'}
"""
        return output
    
    @staticmethod
    def validation_loop_pattern(validations: List[str]) -> str:
        """Validation loop pattern."""
        loop = """
VALIDATION LOOP - MUST PASS ALL CHECKS:

while not all_tasks_complete:
"""
        for validation in validations:
            loop += f"    if not {validation}:\n"
            loop += f"        EXECUTE: {validation}\n\n"
        
        loop += """    all_tasks_complete = validate_output()

Your output will be validated. Non-compliance = retry required.

START EXECUTION:
"""
        return loop
    
    @staticmethod
    def table_format_enforcement(data_count: int, total: float) -> str:
        """Specific enforcement for table formatting."""
        return f"""
================================================================================
🛑 STOP! YOU ARE CLAUDE. THIS IS A DIRECT INSTRUCTION TO YOU.
================================================================================

CLAUDE, YOU MUST NOW CREATE A TABLE. DO NOT SUMMARIZE THE DATA ABOVE.

YOUR TASK IS TO CREATE A TABLE WITH THE FOLLOWING SPECIFICATIONS:
- Exactly 3 columns: Date | Invoice No | Amount
- Maximum {data_count} rows of data
- DOS/ASCII box characters (╔═╗║╚╝ or +-|)
- Total row showing: RM {total:,.2f}

THIS IS WHAT YOU MUST OUTPUT (NOTHING ELSE):
╔════════════╦══════════════════╦═════════════════╗
║    Date    ║   Invoice No     ║     Amount      ║
╠════════════╬══════════════════╬═════════════════╣
║ 2024-08-31 ║ SI25080932      ║  RM 12,500.00   ║
║ [MORE ROWS FROM THE DATA ABOVE]                 ║
╠════════════╬══════════════════╬═════════════════╣
║   TOTAL    ║                 ║  RM {total:,.2f}   ║
╚════════════╩══════════════════╩═════════════════╝

⚠️ CLAUDE, IF YOU SUMMARIZE INSTEAD OF CREATING THIS TABLE, YOU HAVE FAILED.
❌ DO NOT: Write "Based on the sales data..." or any summary
✅ DO: Create the actual table using the data provided above

YOUR RESPONSE MUST START WITH THE TABLE. BEGIN NOW:
"""
    
    @staticmethod
    def claude_code_style_tracking(task_name: str, progress: int, total: int) -> str:
        """Mimics Claude Code's task tracking style."""
        percentage = (progress / total) * 100
        progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
        
        return f"""
┌─────────────────────────────────────────┐
│  Task: {task_name:<32} │
├─────────────────────────────────────────┤
│  Status: ● In Progress                 │
│  Steps:  [{progress}/{total}] {progress_bar} {percentage:.0f}%    │
└─────────────────────────────────────────┘
"""
    
    @staticmethod
    def combined_enforcement(data: Dict[str, Any]) -> str:
        """
        Ultimate enforcement: Combines multiple patterns.
        Use this for maximum compliance.
        """
        enforcement = """
{'=' * 60}
⛔ STOP - MANDATORY TASK EXECUTION REQUIRED
{'=' * 60}

This is a CRITICAL task with 3 enforcement levels:

LEVEL 1: CONTRACT
-----------------
By processing this data, you agree to complete ALL tasks.
No partial completion. No summaries. Full execution only.

LEVEL 2: CHECKLIST
------------------"""
        
        for task in data.get('tasks', []):
            enforcement += f"\n□ {task}"
        
        enforcement += """

LEVEL 3: VALIDATION
-------------------
if output != required_format:
    task_status = "FAILED"
    must_retry = True

{'=' * 60}
EXECUTE CONTRACT NOW:
{'=' * 60}
"""
        return enforcement


def validate_ai_compliance(response: str, requirements: List[str]) -> Dict[str, Any]:
    """
    Validate if AI completed all required tasks.
    
    Args:
        response: The AI's response to check
        requirements: List of required elements to find
    
    Returns:
        Dictionary with validation results
    """
    checks = {}
    for req in requirements:
        checks[req] = req in response
    
    all_passed = all(checks.values())
    
    if not all_passed:
        failed = [k for k, v in checks.items() if not v]
        return {
            "status": "FAILED",
            "message": f"AI did not complete tasks: {failed}",
            "checks": checks
        }
    
    return {
        "status": "SUCCESS",
        "message": "All tasks completed",
        "checks": checks
    }