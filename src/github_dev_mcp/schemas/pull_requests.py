from pydantic import BaseModel, Field


class GetPullRequestInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    pull_number: int = Field(..., ge=1, description="Pull request number")


class ListPullRequestsInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    state: str = Field("open", description="PR state: open, closed, or all")
    base: str | None = Field(None, description="Optional base branch filter")
    head: str | None = Field(None, description="Optional head branch filter")


class CompareBranchToBaseInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    base: str = Field(..., description="Base branch or ref")
    head: str = Field(..., description="Head branch or ref")


class ListPullRequestFilesInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    pull_number: int = Field(..., ge=1, description="Pull request number")


class GetCombinedStatusForRefInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    ref: str = Field(..., description="Commit SHA, branch name, or tag to resolve before status lookup")


class UpdatePullRequestInput(BaseModel):
    repo_full_name: str = Field(..., description="Full repository name, e.g. Gyro06/REPO")
    pull_number: int = Field(..., ge=1, description="Pull request number")
    title: str | None = Field(None, description="Updated PR title")
    body: str | None = Field(None, description="Updated PR body/description")
    base: str | None = Field(None, description="Updated base branch")
    state: str | None = Field(None, description="PR state: open or closed")
