# MCP Server Continuity File

## Overview

This repository contains a local-first Model Context Protocol (MCP) server built using:

- FastMCP
- Python
- GitHub REST API
- PostgreSQL (for audit logging and policy tracking)
- VS Code MCP integration (stdio transport)

The server enables programmatic GitHub workflows through MCP tools.

---

## Current Capabilities

### Repository Interaction
- read_file
- search_code
- list_repo_tree

### Branching & Commits
- create_branch (validated naming: feature/, bugfix/, chore/)
- commit_files (multi-file commits via Git trees API)
- direct commits to default branch are blocked

### Pull Requests
- open_pull_request (with duplicate PR detection)
- get_pull_request
- list_pull_requests
- compare_branch_to_base

### Safety & Governance
- repo allowlist enforcement
- audit logging to PostgreSQL
- branch naming validation
- duplicate PR prevention
- main branch protection (no direct commits)

---

## Architecture

### Structure


src/github_dev_mcp/
├── server.py
├── config.py
├── db.py
├── logging_config.py
├── schemas/
├── services/
├── tools/
├── prompts/


### Key Components

- **Tools** → MCP-exposed capabilities (modular via register pattern)
- **Services** → GitHub + DB logic
- **Schemas** → Pydantic models for tool inputs
- **Audit Service** → Logs all tool executions
- **Repo Policy Service** → Enforces repo/org restrictions

---

## Environment Configuration

`.env` (local only, not committed)

```env
GITHUB_TOKEN=***
GITHUB_ALLOWED_ORG=Gyro06
GITHUB_ALLOWED_REPOS=Gyro06/REPO
GITHUB_DEFAULT_BASE_BRANCH=main
POSTGRES_HOST=localhost
POSTGRES_DB=github_dev_mcp
POSTGRES_USER=postgres
POSTGRES_PASSWORD=***
MCP Integration
VS Code uses .vscode/mcp.json
Transport: stdio
Server started via:
python -m github_dev_mcp.server
Tools accessed through VS Code Chat (Agent mode)
Completed Features (Phase 1 & 2)
Core GitHub CRUD operations
Multi-file commit support
PR lifecycle support
Repo discovery
Branch safety rules
Audit logging
Duplicate PR prevention
In Progress / Next Steps
Immediate Next Builds
list_pull_request_files
check_existing_open_pr_for_branch (completed in client, ensure tool wired)
get_combined_status_for_ref
update_pull_request
Short-Term Enhancements
list_pull_request_commits
branch cleanup (delete_branch with safety)
PR auto-summary generation
prompt-based workflows
Medium-Term
convert to remote MCP server (SSE / HTTP)
deploy to cloud host
introduce GitHub App auth (replace PAT)
add caching layer
implement idempotency keys
Known Constraints
Uses PAT (will migrate to GitHub App)
PostgreSQL required for audit logging
VS Code MCP required for local usage
No retry/backoff logic yet
No rate limit handling yet
Testing Status

Manually validated:

branch creation
commit (multi-file)
PR creation
PR retrieval
PR listing
branch protection
duplicate PR prevention

Pending:

automated tests
failure case coverage
load behavior
How to Resume Work in New Chat

Provide:

This file (MCP_CONTINUITY.md)
Current goal (e.g., "continue build with PR file inspection tools")

Suggested prompt:

I am building a Python FastMCP GitHub server. Here is my continuity file. Continue from next steps and generate exact file updates.
Notes
Modular tool architecture is working correctly
Import issues resolved (module vs function pattern)
VS Code MCP lifecycle understood (reload required)
Secrets properly handled via .env
Owner

Local personal MCP development environment
Primary repo: Gyro06/REPO
