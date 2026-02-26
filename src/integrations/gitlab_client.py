# src/integrations/gitlab_client.py

from __future__ import annotations

from typing import List

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


def list_gitlab_projects_via_rest() -> List[str]:
    """
    Very simple function: use GitLab REST API to list user projects.

    It uses env var GITLAB_TOKEN as PRIVATE-TOKEN header.
    Only read access (read_api scope) is enough.

    Return list of project names like:
      ["group1 / repoA", "group2 / repoB", ...]
    """
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITLAB_TOKEN is not set, please set in ~/.secrets and source ~/.bashrc first."
        )

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