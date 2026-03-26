# GitHub Dev MCP

Local-first MCP server for GitHub development workflows.

## Features

- Read files from GitHub
- Search code in GitHub
- Create branches
- Commit multiple files in one commit
- Open draft pull requests

## Local setup

1. Create a virtual environment
2. Install dependencies
3. Configure `.env`
4. Run the SQL migration
5. Start the server
6. Register it in VS Code using `.vscode/mcp.json`

## Notes

- Repository access is restricted by owner and optional repo allowlist.
- Multi-file commits use GitHub Git database APIs.
- This server is intended for local-first development before later remote deployment.