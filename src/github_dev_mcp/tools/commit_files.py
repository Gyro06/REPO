from github_dev_mcp.schemas.github import CommitFilesInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService
from github_dev_mcp.config import settings


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="commit_files",
        description="Create one Git commit containing changes to multiple files in an allowed GitHub repository branch",
    )
    def commit_files(input: CommitFilesInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)

            if input.branch == settings.github_default_base_branch:
                raise ValueError(
                    f"Direct commits to {settings.github_default_base_branch} are not allowed. "
                    "Create a feature branch first."
                )

            result = github.commit_multiple_files(
                repo_full_name=input.repo_full_name,
                branch=input.branch,
                commit_message=input.commit_message,
                files=[file_change.model_dump() for file_change in input.files],
            )

            audit.log("commit_files", input.repo_full_name, input.model_dump(), result, "success")
            return result

        except Exception as exc:
            audit.log("commit_files", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise