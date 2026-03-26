from github_dev_mcp.schemas.github import SearchCodeInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(name="search_code", description="Search code in an allowed GitHub repository")
    def search_code(input: SearchCodeInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.search_code(input.repo_full_name, input.query)
            audit.log("search_code", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("search_code", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise