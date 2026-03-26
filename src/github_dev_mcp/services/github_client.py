import base64
from typing import Any

import httpx

from github_dev_mcp.config import settings


class GitHubClient:
    def __init__(self) -> None:
        self.base_url = settings.github_api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, headers=self.headers, timeout=30.0)

    def get_file(self, repo_full_name: str, path: str, ref: str | None = None) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        params = {"ref": ref} if ref else None
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)
            response.raise_for_status()
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return {
                "path": data["path"],
                "sha": data["sha"],
                "content": content,
                "encoding": "utf-8",
            }

    def search_code(self, repo_full_name: str, query: str) -> dict[str, Any]:
        with self._client() as client:
            q = f"{query} repo:{repo_full_name}"
            response = client.get("/search/code", params={"q": q, "per_page": 20})
            response.raise_for_status()
            return response.json()

    def get_branch_ref(self, repo_full_name: str, branch: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
            response.raise_for_status()
            return response.json()

    def get_branch_sha(self, repo_full_name: str, branch: str) -> str:
        return self.get_branch_ref(repo_full_name, branch)["object"]["sha"]

    def get_commit(self, repo_full_name: str, commit_sha: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/git/commits/{commit_sha}")
            response.raise_for_status()
            return response.json()

    def create_branch(self, repo_full_name: str, new_branch: str, from_branch: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        source_sha = self.get_branch_sha(repo_full_name, from_branch)
        with self._client() as client:
            response = client.post(
                f"/repos/{owner}/{repo}/git/refs",
                json={"ref": f"refs/heads/{new_branch}", "sha": source_sha},
            )
            response.raise_for_status()
            return response.json()

    def create_blob(self, repo_full_name: str, content: str, encoding: str = "utf-8") -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.post(
                f"/repos/{owner}/{repo}/git/blobs",
                json={
                    "content": content,
                    "encoding": encoding,
                },
            )
            response.raise_for_status()
            return response.json()

    def create_tree(
        self,
        repo_full_name: str,
        base_tree_sha: str,
        tree_entries: list[dict[str, Any]],
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.post(
                f"/repos/{owner}/{repo}/git/trees",
                json={
                    "base_tree": base_tree_sha,
                    "tree": tree_entries,
                },
            )
            response.raise_for_status()
            return response.json()

    def create_commit(
        self,
        repo_full_name: str,
        message: str,
        tree_sha: str,
        parent_commit_sha: str,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.post(
                f"/repos/{owner}/{repo}/git/commits",
                json={
                    "message": message,
                    "tree": tree_sha,
                    "parents": [parent_commit_sha],
                },
            )
            response.raise_for_status()
            return response.json()

    def update_branch_ref(
        self,
        repo_full_name: str,
        branch: str,
        new_commit_sha: str,
        force: bool = False,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.patch(
                f"/repos/{owner}/{repo}/git/refs/heads/{branch}",
                json={
                    "sha": new_commit_sha,
                    "force": force,
                },
            )
            response.raise_for_status()
            return response.json()

    def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        head: str,
        base: str,
        body: str,
        draft: bool = True,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.post(
                f"/repos/{owner}/{repo}/pulls",
                json={
                    "title": title,
                    "head": head,
                    "base": base,
                    "body": body,
                    "draft": draft,
                },
            )
            response.raise_for_status()
            return response.json()

    def commit_multiple_files(
        self,
        repo_full_name: str,
        branch: str,
        commit_message: str,
        files: list[dict[str, str]],
    ) -> dict[str, Any]:
        branch_ref = self.get_branch_ref(repo_full_name, branch)
        parent_commit_sha = branch_ref["object"]["sha"]

        parent_commit = self.get_commit(repo_full_name, parent_commit_sha)
        base_tree_sha = parent_commit["tree"]["sha"]

        tree_entries: list[dict[str, Any]] = []
        created_blobs: list[dict[str, Any]] = []

        for file_change in files:
            blob = self.create_blob(repo_full_name, file_change["content"], encoding="utf-8")
            created_blobs.append(
                {
                    "path": file_change["path"],
                    "blob_sha": blob["sha"],
                }
            )
            tree_entries.append(
                {
                    "path": file_change["path"],
                    "mode": file_change.get("mode", "100644"),
                    "type": file_change.get("type", "blob"),
                    "sha": blob["sha"],
                }
            )

        new_tree = self.create_tree(repo_full_name, base_tree_sha, tree_entries)
        new_commit = self.create_commit(repo_full_name, commit_message, new_tree["sha"], parent_commit_sha)
        updated_ref = self.update_branch_ref(repo_full_name, branch, new_commit["sha"], force=False)

        return {
            "branch": branch,
            "parent_commit_sha": parent_commit_sha,
            "base_tree_sha": base_tree_sha,
            "created_blobs": created_blobs,
            "new_tree_sha": new_tree["sha"],
            "new_commit_sha": new_commit["sha"],
            "updated_ref": updated_ref,
        }