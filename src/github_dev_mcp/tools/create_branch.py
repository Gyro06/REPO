from github_dev_mcp.schemas.github import CreateBranchInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(name="create_branch", description="Create a branch in an allowed GitHub repository")
    def create_branch(input: CreateBranchInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.create_branch(input.repo_full_name, input.new_branch, input.from_branch)
            audit.log("create_branch", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("create_branch", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise