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
        from devfoundry.observability.event_bus import event_bus
        from devfoundry.observability import event_types

        if event_bus.is_run_cancelled():
            raise RuntimeError("Run cancelled by user")

        event_bus.publish(event_types.TOOL_STARTED, {
            "tool": "list_files",
            "path": path
        })
        try:
            res = self._run_internal(path)
            event_bus.publish(event_types.TOOL_COMPLETED, {
                "tool": "list_files",
                "path": path
            })
            return res
        except Exception as e:
            event_bus.publish(event_types.TOOL_FAILED, {
                "tool": "list_files",
                "path": path,
                "error": str(e)
            })
            raise e

    def _run_internal(self, path: str = "."):
        root = Path(self._workspace.root)
        target = root / path

        if not target.exists():
            return f"Path does not exist: {path}"

        entries = []

        for item in sorted(target.iterdir()):
            prefix = "[DIR]" if item.is_dir() else "[FILE]"
            entries.append(f"{prefix} {item.relative_to(root)}")

        return "\n".join(entries)