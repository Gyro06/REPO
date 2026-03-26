from fastmcp import FastMCP

from github_dev_mcp.logging_config import configure_logging
from github_dev_mcp.tools import (
    read_file,
    search_code,
    create_branch,
    commit_files,
    open_pull_request,
    get_pull_request,
    list_repo_tree,
    list_pull_requests,
    compare_branch_to_base,
    list_pull_request_files,
)


def build_server() -> FastMCP:
    configure_logging()

    mcp = FastMCP(
        name="GitHub Dev MCP",
        instructions=(
            "Tools for reading files, searching code, creating branches, "
            "listing repository contents, committing multiple file changes "
            "in a single commit, and opening or retrieving pull requests "
            "in approved GitHub repositories."
        ),
    )

    read_file.register(mcp)
    search_code.register(mcp)
    create_branch.register(mcp)
    commit_files.register(mcp)
    open_pull_request.register(mcp)
    get_pull_request.register(mcp)
    list_repo_tree.register(mcp)
    list_pull_requests.register(mcp)
    compare_branch_to_base.register(mcp)
    list_pull_request_files.register(mcp)
    # PR tooling: status and updates
    from github_dev_mcp.tools import get_combined_status_for_ref, update_pull_request

    get_combined_status_for_ref.register(mcp)
    update_pull_request.register(mcp)

    # New PR/branch tools
    from github_dev_mcp.tools import list_pull_request_commits, delete_branch

    list_pull_request_commits.register(mcp)
    delete_branch.register(mcp)

    return mcp


def main() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    main()