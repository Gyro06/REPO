from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    path: str = Field(description="Path to the file in the repository")
    ref: str | None = Field(default=None, description="Branch, tag, or commit SHA")


class SearchCodeInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    query: str = Field(description="Search query")


class CreateBranchInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    new_branch: str = Field(description="Name of the new branch to create")
    from_branch: str = Field(default="main", description="Source branch name")


class FileChange(BaseModel):
    path: str = Field(description="Repository-relative file path")
    content: str = Field(description="Full replacement file content")
    mode: str = Field(default="100644", description="Git file mode")
    type: str = Field(default="blob", description="Git tree entry type")


class CommitFilesInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    branch: str = Field(description="Target branch to advance")
    commit_message: str = Field(description="Git commit message")
    files: list[FileChange] = Field(description="Files to include in one commit")


class OpenPullRequestInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    title: str = Field(description="PR title")
    head: str = Field(description="Source branch")
    base: str = Field(default="main", description="Target base branch")
    body: str = Field(default="", description="PR body")
    draft: bool = Field(default=True, description="Create PR as draft")

class ListRepoTreeInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    path: str = Field(default="", description="Optional directory path")
    ref: str | None = Field(default=None, description="Branch, tag, or commit SHA")

class GetPullRequestInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    pull_number: int = Field(description="Pull request number")


class ListPullRequestsInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    state: str = Field(default="open", description="open, closed, or all")
    sort: str = Field(default="created", description="created, updated, popularity, long-running")
    direction: str = Field(default="desc", description="asc or desc")
    per_page: int = Field(default=20, description="Maximum number of pull requests to return")

class CompareBranchInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    base: str = Field(description="Base branch or ref")
    head: str = Field(description="Head branch or ref")

class ListPullRequestFilesInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    pull_number: int = Field(description="Pull request number")
    per_page: int = Field(default=100, description="Maximum number of files to return")


class ListPullRequestCommitsInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    pull_number: int = Field(description="Pull request number")
    per_page: int = Field(default=100, description="Maximum number of commits to return per page")


class DeleteBranchInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    branch_name: str = Field(description="Branch name to delete")
    expected_head_sha: str | None = Field(default=None, description="Optional expected head SHA to verify before deletion")

class CheckExistingOpenPRInput(BaseModel):
    repo_full_name: str = Field(description="GitHub repository in owner/repo format")
    head: str = Field(description="Source branch")
    base: str = Field(default="main", description="Target base branch")