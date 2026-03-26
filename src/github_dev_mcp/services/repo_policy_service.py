from github_dev_mcp.config import settings


class RepoPolicyService:
    def ensure_repo_allowed(self, repo_full_name: str) -> None:
        if "/" not in repo_full_name:
            raise ValueError("repo_full_name must be in owner/repo format")

        owner, _repo = repo_full_name.split("/", 1)

        if owner.lower() != settings.github_allowed_org.lower():
            raise ValueError(f"Repository owner '{owner}' is not allowed")

        if settings.allowed_repos and repo_full_name not in settings.allowed_repos:
            raise ValueError(f"Repository '{repo_full_name}' is not in the allowlist")