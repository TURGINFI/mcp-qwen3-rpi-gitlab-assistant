from dataclasses import dataclass
from typing import List

@dataclass
class RepoInfo:
    name: str
    default_branch: str

class MockGitService:
    """
    Mocked Git service integration.
    Replace with a real GitLab/GitHub integration in private code if needed,
    but never commit tokens/URLs.
    """
    def list_repos(self) -> List[RepoInfo]:
        return [
            RepoInfo(name="demo-repo-1", default_branch="main"),
            RepoInfo(name="demo-repo-2", default_branch="master"),
        ]

    def create_issue(self, repo_name: str, title: str, body: str) -> str:
        # Return a fake issue URL
        return f"https://example.git.service/{repo_name}/-/issues/123"
