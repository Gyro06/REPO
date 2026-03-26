from github_dev_mcp.schemas.github import OpenPullRequestInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="open_pull_request",
        description="Open a draft pull request in an allowed GitHub repository",
    )
    def open_pull_request(input: OpenPullRequestInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)

            existing = github.find_open_pull_request_for_branch(
                repo_full_name=input.repo_full_name,
                head=input.head,
                base=input.base,
            )

            if existing["count"] > 0:
                result = {
                    "message": "An open pull request already exists for this branch pair.",
                    "existing_pull_requests": existing["pull_requests"],
                }
                audit.log("open_pull_request", input.repo_full_name, input.model_dump(), result, "success")
                return result

            result = github.create_pull_request(
                repo_full_name=input.repo_full_name,
                title=input.title,
                head=input.head,
                base=input.base,
                body=input.body,
                draft=input.draft,
            )

            audit.log("open_pull_request", input.repo_full_name, input.model_dump(), result, "success")
            return result

        except Exception as exc:
            audit.log("open_pull_request", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise