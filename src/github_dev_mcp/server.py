from fastmcp import FastMCP

from github_dev_mcp.logging_config import configure_logging
from github_dev_mcp.tools import (
    read_file,
    search_code,
    create_branch,
    commit_files,
    open_pull_request,
)


def build_server() -> FastMCP:
    configure_logging()

    mcp = FastMCP(
        name="GitHub Dev MCP",
        instructions=(
            "Tools for reading files, searching code, creating branches, "
            "committing multiple file changes in a single commit, and opening "
            "pull requests in approved GitHub repositories."
        ),
    )

    read_file.register(mcp)
    search_code.register(mcp)
    create_branch.register(mcp)
    commit_files.register(mcp)
    open_pull_request.register(mcp)

    return mcp


def main() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    main()