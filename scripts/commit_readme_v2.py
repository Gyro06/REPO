import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    branch = "main"
    file_path = "README.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    commit_message = "Update README.md from local workspace"

    client = GitHubClient()
    try:
        print("Committing README.md to main...")
        result = client.commit_multiple_files(repo, branch, commit_message, [{"path": file_path, "content": content}])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
