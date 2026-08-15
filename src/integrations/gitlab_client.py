# src/integrations/gitlab_client.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import os
import requests


def get_gitlab_base_url() -> str:
    """
    Get GitLab base URL from env.
    If no env, default to public gitlab.com.
    Example:
      https://gitlab.com
      https://gitlab.your-company.local
    """
    base = os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
    return base.rstrip("/")


def get_gitlab_token() -> Optional[str]:
    """Get the GitLab personal access token from the environment."""
    return os.environ.get("GITLAB_TOKEN")


def require_gitlab_token() -> str:
    """Return GITLAB_TOKEN or raise a clear configuration error."""
    token = get_gitlab_token()
    if not token:
        raise RuntimeError(
            "GITLAB_TOKEN is not set. Export it from a local secrets file before "
            "using the real GitLab integration."
        )
    return token


def list_gitlab_projects_via_rest() -> List[str]:
    """
    Very simple function: use GitLab REST API to list user projects.

    It uses env var GITLAB_TOKEN as PRIVATE-TOKEN header.
    Only read access (read_api scope) is enough.

    Return list of project names like:
      ["group1 / repoA", "group2 / repoB", ...]
    """
    token = require_gitlab_token()
    base_url = get_gitlab_base_url()
    headers = {"PRIVATE-TOKEN": token}
    # membership=true => only projects you are member
    url = f"{base_url}/api/v4/projects?membership=true&simple=true&per_page=100"

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    names: List[str] = [
        p.get("name_with_namespace") or p.get("name", "") for p in data
    ]
    return names


@dataclass
class MockRepo:
    """Small repository object used by the public CLI demo."""
    name: str


class MockGitService:
    """Privacy-safe Git service used by src.mcp.main."""

    def list_repos(self) -> List[MockRepo]:
        return [
            MockRepo(name="portfolio-site"),
            MockRepo(name="rpi-lab-notes"),
            MockRepo(name="mcp-qwen3-rpi-gitlab-assistant"),
        ]

    def create_issue(self, repo_name: str, title: str, body: str) -> str:
        issue_slug = title.lower().replace(" ", "-")
        return f"mock://gitlab/{repo_name}/issues/{issue_slug}"
