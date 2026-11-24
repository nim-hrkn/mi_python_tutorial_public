from mcp.server.mcpserver import MCPServer
import subprocess
import os
from pathlib import Path

mcp = MCPServer(name="filesystem-server")

ALLOWED_ROOT = Path(os.environ.get("MCP_ALLOWED_ROOT", Path.cwd())).resolve()


def validate_path(path: str):

    realpath = Path(path).resolve()

    if not realpath.is_relative_to(ALLOWED_ROOT):
        raise ValueError(f"Access denied: {realpath}")

    return realpath


@mcp.tool()
def show_tree(directory: str, level: int = 1) -> str:
    """
    directory を level 階層まで tree 表示する。
    """

    if level < 1:
        return "Error: level must be >= 1"

    if level > 10:
        return "Error: level too large"

    try:
        path = validate_path(directory)

    except Exception as e:
        return str(e)

    result = subprocess.run(
        ["tree", "-L", str(level), path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return result.stderr

    return result.stdout


@mcp.tool()
def cat_file(filename: str) -> str:
    """
    file 内容を返す。
    """

    try:
        path = validate_path(filename)

    except Exception as e:
        return str(e)

    if not os.path.isfile(path):
        return f"Not a file: {path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
