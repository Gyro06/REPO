from github_dev_mcp.schemas.github import CompareBranchInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(
        name="compare_branch_to_base",
        description="Compare two refs in an allowed GitHub repository",
    )
    def compare_branch_to_base(input: CompareBranchInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)
            result = github.compare_refs(
                repo_full_name=input.repo_full_name,
                base=input.base,
                head=input.head,
            )
            audit.log("compare_branch_to_base", input.repo_full_name, input.model_dump(), result, "success")
            return result
        except Exception as exc:
            audit.log("compare_branch_to_base", input.repo_full_name, input.model_dump(), None, "error", str(exc))
            raise