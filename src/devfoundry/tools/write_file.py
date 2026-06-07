import logging
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import PrivateAttr


logger = logging.getLogger(__name__)


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = """
    Write content into the workspace.

    Creates or overwrites the specified file.
    """

    _workspace = PrivateAttr()

    def __init__(self, workspace):
        super().__init__()
        self._workspace = workspace

    def _run(self, path: str, content: str) -> str:
        logger.info(
            "[WRITE_FILE] Requested write to '%s'",
            path,
        )

        try:
            content_size = len(content)

            logger.info(
                "[WRITE_FILE] Content size: %s chars",
                content_size,
            )

            preview = content[:500]

            logger.debug(
                "[WRITE_FILE] Content preview:\n%s",
                preview,
            )

            # Check whether file already exists
            file_exists = False

            try:
                self._workspace.read(path)
                file_exists = True
            except Exception:
                pass

            logger.info(
                "[WRITE_FILE] File exists: %s",
                file_exists,
            )

            self._workspace.write(path, content)

            logger.info(
                "[WRITE_FILE] Successfully wrote '%s'",
                path,
            )

            return f"""
Successfully wrote file.

Path:
{path}

Characters Written:
{content_size}

Operation:
{"OVERWRITE" if file_exists else "CREATE"}
"""

        except PermissionError as e:

            logger.exception(
                "[WRITE_FILE] Permission denied for '%s'",
                path,
            )

            return f"""
Failed to write file.

Path:
{path}

Reason:
Permission denied

Error:
{str(e)}
"""

        except IsADirectoryError as e:

            logger.exception(
                "[WRITE_FILE] Attempted to write to directory '%s'",
                path,
            )

            return f"""
Failed to write file.

'{path}' is a directory, not a file.
"""

        except Exception as e:

            logger.exception(
                "[WRITE_FILE] Unexpected error writing '%s'",
                path,
            )

            return f"""
Failed to write file.

Path:
{path}

Error:
{str(e)}
"""