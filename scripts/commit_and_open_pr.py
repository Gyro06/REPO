import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    branch = "pr-1"
    file_path = "pr-1-marker.txt"
    content = "This is a marker file for PR 1."
    commit_message = "Add marker file for PR 1"
    title = "PR 1: Add marker file"
    body = "Adds a small marker file to create PR 1."

    client = GitHubClient()
    try:
        print("Committing file to branch...")
        result = client.commit_multiple_files(repo, branch, commit_message, [{"path": file_path, "content": content}])
        print(json.dumps(result, ensure_ascii=False, indent=2))

        print("Creating pull request...")
        pr = client.create_pull_request(repo, title=title, head=branch, base="main", body=body, draft=False)
        print(json.dumps(pr, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
