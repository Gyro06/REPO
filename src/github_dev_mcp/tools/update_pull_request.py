from github_dev_mcp.schemas.pull_requests import UpdatePullRequestInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="update_pull_request",
        description="Update a pull request (title, body, base, state) in an allowed GitHub repository",
    )
    def update_pull_request(input: UpdatePullRequestInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)

            # Guard: require at least one field to update
            if not any([input.title, input.body, input.base, input.state]):
                raise ValueError("At least one field (title, body, base, state) must be provided to update the pull request")

            result = github.update_pull_request(
                input.repo_full_name,
                input.pull_number,
                title=input.title,
                body=input.body,
                base=input.base,
                state=input.state,
            )
            audit.log("update_pull_request", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("update_pull_request", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise
