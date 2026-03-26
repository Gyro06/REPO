from github_dev_mcp.schemas.github import ListPullRequestsInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="list_pull_requests",
        description="List pull requests from an allowed GitHub repository",
    )
    def list_pull_requests(input: ListPullRequestsInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.list_pull_requests(
                repo_full_name=input.repo_full_name,
                state=input.state,
                sort=input.sort,
                direction=input.direction,
                per_page=input.per_page,
            )
            audit.log("list_pull_requests", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("list_pull_requests", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise