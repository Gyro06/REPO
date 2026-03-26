from github_dev_mcp.schemas.github import ReadFileInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(name="read_file", description="Read a file from an allowed GitHub repository")
    def read_file(input: ReadFileInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.get_file(input.repo_full_name, input.path, input.ref)
            audit.log("read_file", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("read_file", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise