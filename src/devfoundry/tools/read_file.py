from crewai.tools import BaseTool
from pydantic import PrivateAttr

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read content from workspace"
    _workspace = PrivateAttr()

    def __init__(self, workspace):
        super().__init__()
        self._workspace = workspace

    def _run(self, path: str) -> str:
        try:
            return self._workspace.read(path)

        except FileNotFoundError:
            available_files = self._workspace.list_files()

            preview = "\n".join(available_files[:50])

            return f"""
            File not found: {path}

            Available files:

            {preview}

            Choose one of the available files instead of inventing a path.
            """