"""
GitHub tool. WHY separate from the agent: the agent does *reasoning*, the tool
does *data fetching*. Splitting them means you can test the agent with mock data
now and swap in the real GitHub API later WITHOUT touching agent logic.

To go live: replace get_recent_activity() body with a call to
https://api.github.com/repos/{owner}/{repo}/pulls etc. Same return shape.
"""


def get_recent_activity() -> dict:
    """Returns a small, structured snapshot of repo activity (mocked)."""
    return {
        "merged_prs_last_week": 7,
        "open_issues": 12,
        "open_prs": 4,
        "recent_prs": [
            {"num": 231, "title": "Fix auth token refresh", "status": "merged"},
            {"num": 230, "title": "Add rate limiting", "status": "merged"},
            {"num": 229, "title": "Refactor payment module", "status": "open"},
        ],
        "critical_bugs": 1,
    }
