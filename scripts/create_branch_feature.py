import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    new_branch = "feature/mcp-validation-test"
    from_branch = "main"
    client = GitHubClient()
    try:
        result = client.create_branch(repo, new_branch, from_branch)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))

if __name__ == "__main__":
    main()
