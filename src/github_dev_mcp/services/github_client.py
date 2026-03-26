import base64
from typing import Any

import httpx

from github_dev_mcp.config import settings


class GitHubClient:

    def find_open_pull_request_for_branch(
        self,
        repo_full_name: str,
        head: str,
        base: str,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(
                f"/repos/{owner}/{repo}/pulls",
                params={
                    "state": "open",
                    "head": f"{owner}:{head}",
                    "base": base,
                    "per_page": 20,
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "count": len(data),
                "pull_requests": [
                    {
                        "number": pr["number"],
                        "title": pr["title"],
                        "state": pr["state"],
                        "draft": pr.get("draft", False),
                        "head": pr["head"]["ref"],
                        "base": pr["base"]["ref"],
                        "html_url": pr["html_url"],
                    }
                    for pr in data
                ],
            }

    def list_pull_request_files(
        self,
        repo_full_name: str,
        pull_number: int,
        per_page: int = 100,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(
                f"/repos/{owner}/{repo}/pulls/{pull_number}/files",
                params={"per_page": per_page},
            )
            response.raise_for_status()
            data = response.json()
            return {
                "count": len(data),
                "files": [
                    {
                        "filename": item.get("filename"),
                        "status": item.get("status"),
                        "additions": item.get("additions"),
                        "deletions": item.get("deletions"),
                        "changes": item.get("changes"),
                        "blob_url": item.get("blob_url"),
                        "raw_url": item.get("raw_url"),
                        "patch": item.get("patch"),
                    }
                    for item in data
                ],
            }

    def list_pull_request_commits(self, repo_full_name: str, pull_number: int, per_page: int = 100) -> list[dict[str, Any]]:
        """List commits for a pull request, paginated.

        Returns a normalized list of commits with keys: sha, message, author_name,
        author_email, committer_name, committer_email, html_url, parents, committed_at
        """
        owner, repo = repo_full_name.split("/", 1)
        commits: list[dict[str, Any]] = []
        page = 1
        with self._client() as client:
            while True:
                response = client.get(
                    f"/repos/{owner}/{repo}/pulls/{pull_number}/commits",
                    params={"per_page": per_page, "page": page},
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                for entry in data:
                    commit = entry.get("commit", {})
                    author = commit.get("author") or {}
                    committer = commit.get("committer") or {}
                    commits.append(
                        {
                            "sha": entry.get("sha"),
                            "message": commit.get("message"),
                            "author_name": author.get("name"),
                            "author_email": author.get("email"),
                            "committer_name": committer.get("name"),
                            "committer_email": committer.get("email"),
                            "committed_at": commit.get("committer", {}).get("date"),
                            "html_url": entry.get("html_url"),
                            "parents": [p.get("sha") for p in entry.get("parents", [])],
                        }
                    )
                if len(data) < per_page:
                    break
                page += 1
        return commits

    def compare_refs(self, repo_full_name: str, base: str, head: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/compare/{base}...{head}")
            response.raise_for_status()
            data = response.json()
            return {
                "status": data.get("status"),
                "ahead_by": data.get("ahead_by"),
                "behind_by": data.get("behind_by"),
                "total_commits": data.get("total_commits"),
                "html_url": data.get("html_url"),
                "files": [
                    {
                        "filename": f.get("filename"),
                        "status": f.get("status"),
                        "additions": f.get("additions"),
                        "deletions": f.get("deletions"),
                        "changes": f.get("changes"),
                    }
                    for f in data.get("files", [])
                ],
                "commits": [
                    {
                        "sha": c.get("sha"),
                        "message": c.get("commit", {}).get("message", "").splitlines()[0],
                    }
                    for c in data.get("commits", [])
                ],
            }

    def list_pull_requests(
        self,
        repo_full_name: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        per_page: int = 20,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(
                f"/repos/{owner}/{repo}/pulls",
                params={
                    "state": state,
                    "sort": sort,
                    "direction": direction,
                    "per_page": per_page,
                },
            )
            response.raise_for_status()
            data = response.json()
            return {
                "count": len(data),
                "pull_requests": [
                    {
                        "number": pr["number"],
                        "title": pr["title"],
                        "state": pr["state"],
                        "draft": pr.get("draft", False),
                        "head": pr["head"]["ref"],
                        "base": pr["base"]["ref"],
                        "user": pr["user"]["login"],
                        "html_url": pr["html_url"],
                    }
                    for pr in data
                ],
            }

    def get_pull_request(self, repo_full_name: str, pull_number: int) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}")
            response.raise_for_status()
            return response.json()

    def list_directory(self, repo_full_name: str, path: str = "", ref: str | None = None) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        params = {"ref": ref} if ref else None
        endpoint = f"/repos/{owner}/{repo}/contents/{path}" if path else f"/repos/{owner}/{repo}/contents"
        with self._client() as client:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):
                data = [data]

            return {
                "path": path,
                "ref": ref,
                "entries": [
                    {
                        "name": item.get("name"),
                        "path": item.get("path"),
                        "type": item.get("type"),
                        "sha": item.get("sha"),
                    }
                    for item in data
                ],
            }
        
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

    def get_branch_info(self, repo_full_name: str, branch: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/branches/{branch}")
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

    def get_repo(self, repo_full_name: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()

    def delete_branch(self, repo_full_name: str, branch_name: str) -> dict[str, Any]:
        """Delete a branch ref. Caller must perform safety checks before calling.

        Returns a normalized dict with deletion outcome and former SHA.
        """
        owner, repo = repo_full_name.split("/", 1)
        # get the ref (will raise if not found)
        ref = self.get_branch_ref(repo_full_name, branch_name)
        former_sha = ref.get("object", {}).get("sha")

        with self._client() as client:
            response = client.delete(f"/repos/{owner}/{repo}/git/refs/heads/{branch_name}")
            # GitHub returns 204 No Content on success
            if response.status_code in (200, 202, 204):
                return {
                    "deleted": True,
                    "repo_full_name": repo_full_name,
                    "branch_name": branch_name,
                    "former_sha": former_sha,
                }
            else:
                response.raise_for_status()

    def list_pull_request_files(self, repo_full_name: str, pull_number: int, per_page: int = 100) -> list[dict[str, Any]]:
        owner, repo = repo_full_name.split("/", 1)
        files: list[dict[str, Any]] = []
        page = 1
        with self._client() as client:
            while True:
                response = client.get(f"/repos/{owner}/{repo}/pulls/{pull_number}/files", params={"per_page": per_page, "page": page})
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                for entry in data:
                    files.append(
                        {
                            "sha": entry.get("sha"),
                            "filename": entry.get("filename"),
                            "status": entry.get("status"),
                            "additions": entry.get("additions"),
                            "deletions": entry.get("deletions"),
                            "changes": entry.get("changes"),
                            "blob_url": entry.get("blob_url"),
                            "raw_url": entry.get("raw_url"),
                            "contents_url": entry.get("contents_url"),
                            "patch": entry.get("patch"),
                        }
                    )
                # stop if fewer than per_page returned
                if len(data) < per_page:
                    break
                page += 1
        return files

    def resolve_ref_to_sha(self, repo_full_name: str, ref: str) -> str:
        """Resolve a branch, tag, or short/long SHA to a commit SHA.

        Resolution order: raw SHA -> branch -> tag -> commit lookup
        """
        # fast-path: looks like a full SHA
        if isinstance(ref, str) and len(ref) == 40 and all(c in "0123456789abcdefABCDEF" for c in ref):
            return ref

        owner, repo = repo_full_name.split("/", 1)
        with self._client() as client:
            # branch
            try:
                response = client.get(f"/repos/{owner}/{repo}/git/ref/heads/{ref}")
                response.raise_for_status()
                return response.json()["object"]["sha"]
            except Exception:
                pass

            # tag
            try:
                response = client.get(f"/repos/{owner}/{repo}/git/ref/tags/{ref}")
                response.raise_for_status()
                return response.json()["object"]["sha"]
            except Exception:
                pass

            # try commit lookup
            try:
                response = client.get(f"/repos/{owner}/{repo}/git/commits/{ref}")
                response.raise_for_status()
                return response.json()["sha"]
            except Exception as exc:
                raise ValueError(f"Unable to resolve ref '{ref}' to a commit SHA: {exc}")

    def get_combined_status_for_ref(self, repo_full_name: str, ref: str) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        sha = self.resolve_ref_to_sha(repo_full_name, ref)
        with self._client() as client:
            response = client.get(f"/repos/{owner}/{repo}/commits/{sha}/status")
            response.raise_for_status()
            data = response.json()
            return {
                "ref": ref,
                "sha": sha,
                "state": data.get("state"),
                "total_count": data.get("total_count", 0),
                "statuses": data.get("statuses", []),
            }

    def update_pull_request(
        self,
        repo_full_name: str,
        pull_number: int,
        title: str | None = None,
        body: str | None = None,
        base: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        owner, repo = repo_full_name.split("/", 1)
        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if base is not None:
            payload["base"] = base
        if state is not None:
            payload["state"] = state

        if not payload:
            raise ValueError("No update fields provided for pull request")

        with self._client() as client:
            response = client.patch(f"/repos/{owner}/{repo}/pulls/{pull_number}", json=payload)
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