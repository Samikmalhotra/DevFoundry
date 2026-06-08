from pathlib import Path
import logging

from crewai.tools import BaseTool
from pydantic import PrivateAttr


logger = logging.getLogger(__name__)


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = """
    Read a file from the workspace.

    If the file is unknown, use list_files first.
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
        from devfoundry.observability.event_bus import event_bus
        from devfoundry.observability import event_types

        if event_bus.is_run_cancelled():
            raise RuntimeError("Run cancelled by user")

        event_bus.publish(event_types.TOOL_STARTED, {
            "tool": "read_file",
            "path": path
        })
        try:
            res = self._run_internal(path, max_chars)
            event_bus.publish(event_types.TOOL_COMPLETED, {
                "tool": "read_file",
                "path": path
            })
            return res
        except Exception as e:
            event_bus.publish(event_types.TOOL_FAILED, {
                "tool": "read_file",
                "path": path,
                "error": str(e)
            })
            raise e

    def _run_internal(
        self,
        path: str,
        max_chars: int = 10000,
    ) -> str:

        logger.info(
            "[READ_FILE] Requested path='%s' max_chars=%s",
            path,
            max_chars,
        )

        if not path or not str(path).strip():
            logger.warning(
                "[READ_FILE] Empty path supplied"
            )

            return """
No file path was provided.

Use list_files to discover available files.
"""

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
                "",
            ]

            if truncated:
                result.extend([
                    f"WARNING: File truncated to {max_chars} chars.",
                    ""
                ])

            result.append(content)

            return "\n".join(result)

        except IsADirectoryError:

            logger.warning(
                "[READ_FILE] '%s' is a directory",
                path,
            )

            try:
                files = self._workspace.list_files(path)

                logger.info(
                    "[READ_FILE] Directory contains %s files",
                    len(files),
                )

                return f"""
'{path}' is a directory.

Directory contents:

{chr(10).join(files[:50])}
"""

            except Exception:
                logger.exception(
                    "[READ_FILE] Failed listing directory '%s'",
                    path,
                )

                return f"""
'{path}' appears to be a directory.

Unable to list contents.
"""

        except (
            FileNotFoundError,
            OSError,
            ValueError,
            RuntimeError,
        ) as e:

            logger.warning(
                "[READ_FILE] Unable to locate '%s': %s",
                path,
                str(e),
            )

            try:
                available = self._workspace.list_files()

                logger.info(
                    "[READ_FILE] Workspace contains %s files",
                    len(available),
                )

            except Exception:
                logger.exception(
                    "[READ_FILE] Failed listing workspace files"
                )

                available = []

            requested_name = Path(path).name.lower()

            suggestions = []

            if requested_name:
                suggestions = [
                    f
                    for f in available
                    if requested_name in f.lower()
                ]

            logger.info(
                "[READ_FILE] Suggestions: %s",
                suggestions[:10],
            )

            return f"""
File not found.

Requested:
{path}

Possible matches:
{chr(10).join(suggestions[:10]) or 'None'}

Available files:
{chr(10).join(available[:50]) or 'No files available'}

Use one of the available paths instead of inventing a path.
"""

        except Exception as e:

            logger.exception(
                "[READ_FILE] Unexpected error reading '%s'",
                path,
            )

            return f"""
Failed to read file.

Path:
{path}

Exception:
{type(e).__name__}

Message:
{str(e)}
"""