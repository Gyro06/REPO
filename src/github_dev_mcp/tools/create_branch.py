import re

from github_dev_mcp.schemas.github import CreateBranchInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


ALLOWED_BRANCH_PATTERNS = [
    r"^feature\/[a-zA-Z0-9._-]+$",
    r"^bugfix\/[a-zA-Z0-9._-]+$",
    r"^chore\/[a-zA-Z0-9._-]+$",
]


def is_valid_branch_name(branch_name: str) -> bool:
    return any(re.match(pattern, branch_name) for pattern in ALLOWED_BRANCH_PATTERNS)


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="create_branch",
        description="Create a branch in an allowed GitHub repository",
    )
    def create_branch(input: CreateBranchInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)

            print(f"DEBUG create_branch new_branch={input.new_branch!r}")

            if not is_valid_branch_name(input.new_branch):
                raise ValueError(
                    "Branch name must start with feature/, bugfix/, or chore/ "
                    "and contain only letters, numbers, dots, underscores, or dashes."
                )

            result = github.create_branch(input.repo_full_name, input.new_branch, input.from_branch)
            audit.log("create_branch", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("create_branch", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise