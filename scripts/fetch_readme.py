import os
import sys
import json

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))

from github_dev_mcp.services.github_client import GitHubClient


def main():
    client = GitHubClient()
    try:
        result = client.get_file("Gyro06/REPO", "README.md", "main")
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    main()
