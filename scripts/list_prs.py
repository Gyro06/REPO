import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.config import settings
import httpx


def main():
    repo = "Gyro06/REPO"
    owner, repo_name = repo.split("/", 1)
    url = f"{settings.github_api_url.rstrip('/')}/repos/{owner}/{repo_name}/pulls"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    params = {"state": "all", "per_page": 100}
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            prs = response.json()
            print(json.dumps(prs, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
