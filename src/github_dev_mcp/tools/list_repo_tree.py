from github_dev_mcp.schemas.github import ListRepoTreeInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="list_repo_tree",
        description="List files and directories in an allowed GitHub repository path"
    )
    def list_repo_tree(input: ListRepoTreeInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.list_directory(input.repo_full_name, input.path, input.ref)
            audit.log("list_repo_tree", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("list_repo_tree", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise