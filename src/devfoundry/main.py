#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from devfoundry.crew import DevFoundry
from devfoundry.workspace.manager import Workspace
from devfoundry.workspace.context import initialize_workspace

project_name = "todo_manager"

workspace = Workspace(project_name)

initialize_workspace(workspace)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

requirements = """
Create a todo list management system.

The system should allow users to:
- Add tasks
- Remove tasks
- Mark tasks as completed
- List all tasks
- List only completed tasks
- List only pending tasks

Each task should have:
- ID
- Description
- Completion status

The system should be fully self-contained and testable."""
module_name = "todo_manager.py"
class_name = "TodoManager"


def run():
    """
    Run the research crew.
    """
    inputs = {
        "project_name": project_name,
        "run_id": workspace.run_id,
        "requirements": requirements,
        "module_name": module_name,
        "class_name": class_name,
        "ui_framework": "Gradio"
    }

    # Create and run the crew
    result = DevFoundry(workspace=workspace).crew().kickoff(inputs=inputs)
    workspace.write(
    "reports/final_output.md",
    str(result)
)


if __name__ == "__main__":
    run()