import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.config import settings
import httpx


def main():
    owner_repo = "Gyro06/REPO"
    pr_number = 1
    owner, repo = owner_repo.split("/", 1)
    url = f"{settings.github_api_url.rstrip('/')}/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
