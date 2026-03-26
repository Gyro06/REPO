import os, sys, json
sys.path.insert(0, os.path.abspath('src'))
from github_dev_mcp.services.github_client import GitHubClient

content = open('README.md','r',encoding='utf-8').read()
client = GitHubClient()
res = client.commit_multiple_files('Gyro06/REPO','main','Update README.md',[{'path':'README.md','content':content}])
print(json.dumps(res))
