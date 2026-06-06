from crewai.tools import BaseTool
from pydantic import PrivateAttr

class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Write content into workspace"
    _workspace = PrivateAttr()

    def __init__(self, workspace):
        super().__init__()
        self._workspace = workspace

    def _run(self, path: str, content: str):
        self._workspace.write(path, content)