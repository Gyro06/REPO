from github_dev_mcp.schemas.github import ListPullRequestCommitsInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="list_pull_request_commits",
        description="List commits for a pull request from an allowed GitHub repository",
    )
    def list_pull_request_commits(input: ListPullRequestCommitsInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            commits = github.list_pull_request_commits(
                repo_full_name=input.repo_full_name, pull_number=input.pull_number, per_page=input.per_page
            )
            result = {"commit_count": len(commits), "commits": commits}
            audit.log("list_pull_request_commits", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("list_pull_request_commits", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise
