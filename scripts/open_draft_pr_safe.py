import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.config import settings
import httpx

REPO = "Gyro06/REPO"
HEAD = "feature/mcp-test"
BASE = "main"
TITLE = "test pr"
BODY = "testing duplicate detection"


def get_prs():
    owner, repo = REPO.split('/',1)
    url = f"{settings.github_api_url.rstrip('/')}/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    params = {"state":"all","per_page":100}
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


def create_pr():
    owner, repo = REPO.split('/',1)
    url = f"{settings.github_api_url.rstrip('/')}/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"title": TITLE, "head": HEAD, "base": BASE, "body": BODY, "draft": True}
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def main():
    try:
        prs = get_prs()
        for pr in prs:
            if pr.get('head',{}).get('ref') == HEAD:
                print(json.dumps({"existing_pr": pr}, ensure_ascii=False, indent=2))
                return
        # no existing PR found
        pr = create_pr()
        print(json.dumps({"created_pr": pr}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == '__main__':
    main()
