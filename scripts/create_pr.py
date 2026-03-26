import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    new_branch = "pr-1"
    base_branch = "main"
    title = "PR 1: Changes from pr-1"
    body = "Automated PR created by script."

    client = GitHubClient()
    try:
        # create branch on remote
        print(f"Creating branch {new_branch} from {base_branch}...")
        client.create_branch(repo, new_branch, base_branch)
        print("Branch created.")

        # create pull request
        print("Creating pull request...")
        pr = client.create_pull_request(repo, title=title, head=new_branch, base=base_branch, body=body, draft=False)
        print(json.dumps(pr, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
