"""
Context processors
"""

from pathlib import Path


def get_active_branch_and_commit(request):
    """
    Gets the active Git branch and latest Git commit for the admin UI
    """
    try:
        head_dir = Path(".") / ".git" / "HEAD"
        with head_dir.open("r") as f:
            head_branch = f.read().splitlines()
        for line in head_branch:
            if line[0:4] == "ref:":
                active_git_branch = line.partition("refs/heads/")[2]
            else:
                raise Exception
    except Exception as e:
        print(f"Failed to get GitBranch. Error: {e}")
        active_git_branch = "[branch name not found]"

    try:
        refs_dir = Path(".") / ".git" / "refs" / "heads" / active_git_branch
        with refs_dir.open("r") as f:
            latest_git_commit = f.read().splitlines()[0]

    except Exception as e:
        print(f"Failed to get commit hash. Error: {e}")
        latest_git_commit = "[latest commit hash not found]"

    return {
        "active_git_branch": active_git_branch,
        "latest_git_commit": latest_git_commit,
    }
