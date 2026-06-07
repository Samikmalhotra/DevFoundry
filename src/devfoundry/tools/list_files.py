from pathlib import Path

from crewai.tools import BaseTool
from pydantic import PrivateAttr


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = (
        "List files and directories in the workspace. "
        "Optionally provide a path relative to the workspace root."
    )

    _workspace = PrivateAttr()

    def __init__(self, workspace):
        super().__init__()
        self._workspace = workspace

    def _run(self, path: str = "."):
        root = Path(self._workspace.root)
        target = root / path

        if not target.exists():
            return f"Path does not exist: {path}"

        entries = []

        for item in sorted(target.iterdir()):
            prefix = "[DIR]" if item.is_dir() else "[FILE]"
            entries.append(f"{prefix} {item.relative_to(root)}")

        return "\n".join(entries)