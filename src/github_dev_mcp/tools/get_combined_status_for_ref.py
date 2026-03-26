from github_dev_mcp.schemas.pull_requests import GetCombinedStatusForRefInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="get_combined_status_for_ref",
        description="Get combined commit status for a branch/tag/SHA in an allowed GitHub repository",
    )
    def get_combined_status_for_ref(input: GetCombinedStatusForRefInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.get_combined_status_for_ref(input.repo_full_name, input.ref)
            audit.log("get_combined_status_for_ref", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("get_combined_status_for_ref", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise
