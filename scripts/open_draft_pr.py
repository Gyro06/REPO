import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    branch = "feature/mcp-test"
    base = "main"
    title = "test pr"
    body = "testing duplicate detection"

    client = GitHubClient()
    try:
        # Check branch exists
        try:
            client.get_branch_ref(repo, branch)
            branch_exists = True
        except Exception:
            branch_exists = False

        if not branch_exists:
            print(f"Branch {branch} not found — creating from {base}...")
            client.create_branch(repo, branch, base)
            print("Branch created.")
        else:
            print(f"Branch {branch} already exists.")

        print("Creating draft pull request...")
        pr = client.create_pull_request(repo, title=title, head=branch, base=base, body=body, draft=True)
        print(json.dumps(pr, ensure_ascii=False, indent=2))

    except Exception as exc:
        print(json.dumps({"error": str(exc)}))

if __name__ == '__main__':
    main()
