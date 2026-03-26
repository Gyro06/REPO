from github_dev_mcp.schemas.github import DeleteBranchInput
from github_dev_mcp.services.audit_service import AuditService
from github_dev_mcp.services.github_client import GitHubClient
from github_dev_mcp.services.repo_policy_service import RepoPolicyService


def register(mcp):
    github = GitHubClient()
    audit = AuditService()
    policy = RepoPolicyService()

    @mcp.tool(name="delete_branch", description="Safely delete a branch from an allowed repository")
    def delete_branch(input: DeleteBranchInput) -> dict:
        try:
            policy.ensure_repo_allowed(input.repo_full_name)

            if not input.branch_name or not input.branch_name.strip():
                raise ValueError("branch_name is required")

            blacklisted = {"main", "master", "develop", "dev"}
            if input.branch_name in blacklisted:
                raise ValueError(f"Refusing to delete blacklisted branch name '{input.branch_name}'")

            repo_meta = github.get_repo(input.repo_full_name)
            default_branch = repo_meta.get("default_branch")

            # cannot delete default
            if input.branch_name == default_branch:
                raise ValueError(f"Refusing to delete the default branch '{default_branch}'")

            # ensure branch exists
            try:
                branch_ref = github.get_branch_ref(input.repo_full_name, input.branch_name)
            except Exception:
                raise ValueError(f"Branch '{input.branch_name}' not found")

            former_sha = branch_ref.get("object", {}).get("sha")

            # verify expected head if provided
            if input.expected_head_sha:
                if input.expected_head_sha != former_sha:
                    raise ValueError("expected_head_sha does not match current branch head")

            # check protection
            branch_info = github.get_branch_info(input.repo_full_name, input.branch_name)
            was_protected = bool(branch_info.get("protected", False))
            if was_protected:
                raise ValueError(f"Refusing to delete protected branch '{input.branch_name}'")

            # check merged status: compare default_branch...branch
            compare = github.compare_refs(input.repo_full_name, default_branch, input.branch_name)
            # conservative: treat 'behind' or 'identical' as merged
            was_merged = compare.get("status") in ("behind", "identical")
            if not was_merged:
                raise ValueError(f"Branch '{input.branch_name}' does not appear merged into '{default_branch}'; refusing to delete")

            # perform delete
            deletion = github.delete_branch(input.repo_full_name, input.branch_name)

            result = {
                "deleted": deletion.get("deleted", False),
                "repo_full_name": input.repo_full_name,
                "branch_name": input.branch_name,
                "former_sha": former_sha,
                "default_branch": default_branch,
                "was_protected": was_protected,
                "was_merged": was_merged,
            }

            audit.log("delete_branch", input.repo_full_name, input.model_dump(), result, "success")

            return result
        except Exception as exc:
            # best-effort to include former_sha if available
            payload = input.model_dump()
            try:
                payload.setdefault("_former_sha", former_sha)
            except Exception:
                pass
            audit.log("delete_branch", input.repo_full_name, payload, None, "error", str(exc))
            raise
