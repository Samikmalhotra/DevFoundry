from pathlib import Path
import logging

from crewai.tools import BaseTool
from pydantic import PrivateAttr


logger = logging.getLogger(__name__)


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = """
    Read a file from the workspace.

    Use list_files first if you do not know the exact path.
    """

    _workspace = PrivateAttr()

    def __init__(self, workspace):
        super().__init__()
        self._workspace = workspace

    def _run(
        self,
        path: str,
        max_chars: int = 10000,
    ) -> str:

        logger.info(
            "[READ_FILE] Requested path='%s' max_chars=%s",
            path,
            max_chars,
        )

        try:
            content = self._workspace.read(path)

            original_size = len(content)

            logger.info(
                "[READ_FILE] Successfully read '%s' (%s chars)",
                path,
                original_size,
            )

            truncated = False

            if original_size > max_chars:
                logger.warning(
                    "[READ_FILE] Truncating '%s' from %s chars to %s chars",
                    path,
                    original_size,
                    max_chars,
                )

                content = content[:max_chars]
                truncated = True

            result = [
                f"FILE: {path}",
                f"SIZE: {original_size} chars",
                ""
            ]

            if truncated:
                result.append(
                    f"WARNING: File truncated to {max_chars} chars."
                )
                result.append("")

            result.append(content)

            return "\n".join(result)

        except FileNotFoundError:

            logger.warning(
                "[READ_FILE] File not found: '%s'",
                path,
            )

            available = self._workspace.list_files()

            logger.info(
                "[READ_FILE] Workspace contains %s files",
                len(available),
            )

            requested_name = Path(path).name.lower()

            suggestions = [
                f
                for f in available
                if requested_name in f.lower()
            ]

            logger.info(
                "[READ_FILE] Suggestions for '%s': %s",
                path,
                suggestions[:10],
            )

            return f"""
File not found: {path}

Possible matches:
{chr(10).join(suggestions[:10])}

Available files:
{chr(10).join(available[:50])}
"""

        except IsADirectoryError:

            logger.warning(
                "[READ_FILE] Agent attempted to read directory '%s'",
                path,
            )

            files = self._workspace.list_files(path)

            logger.info(
                "[READ_FILE] Directory '%s' contains %s files",
                path,
                len(files),
            )

            return f"""
'{path}' is a directory.

Contents:
{chr(10).join(files[:50])}
"""

        except Exception as e:

            logger.exception(
                "[READ_FILE] Unexpected error reading '%s'",
                path,
            )

            return f"""
Failed to read file: {path}

Error:
{str(e)}
"""