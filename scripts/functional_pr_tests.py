import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "src")))
from github_dev_mcp.services.github_client import GitHubClient


def main():
    repo = "Gyro06/REPO"
    pr_number = 1
    ref = "main"

    client = GitHubClient()

    print("== List PR files ==")
    try:
        files = client.list_pull_request_files(repo, pr_number)
        print(json.dumps(files, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

    print("\n== Get combined status for ref ==")
    try:
        status = client.get_combined_status_for_ref(repo, ref)
        print(json.dumps(status, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

    print("\n== Update PR title ==")
    try:
        updated = client.update_pull_request(repo, pr_number, title="Refine PR tooling")
        print(json.dumps(updated, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))


if __name__ == '__main__':
    main()
