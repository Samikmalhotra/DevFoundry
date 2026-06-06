from pathlib import Path
from datetime import datetime
import re


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name).lower()


class Workspace:
    def __init__(
        self,
        project_name: str,
        run_id: str | None = None,
        root: str = "workspace",
    ):
        self.project_name = normalize_name(project_name)

        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.run_id = run_id

        self.root = (
            Path(root)
            / self.project_name
            / self.run_id
        )

        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, relative_path: str) -> Path:
        return self.root / relative_path

    def write(self, relative_path: str, content: str):
        file_path = self.path(relative_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            content,
            encoding="utf-8",
        )

    def read(self, relative_path: str) -> str:
        return self.path(relative_path).read_text(
            encoding="utf-8"
        )

    def exists(self, relative_path: str) -> bool:
        return self.path(relative_path).exists()

    def list_files(self):
        return [
            p.relative_to(self.root)
            for p in self.root.rglob("*")
            if p.is_file()
        ]