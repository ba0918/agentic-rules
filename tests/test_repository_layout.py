import subprocess
from pathlib import PurePosixPath

from conftest import REPO_ROOT


def tracked_files():
    listing = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    )
    return [PurePosixPath(line) for line in listing.stdout.splitlines()]


def test_only_the_skills_directory_holds_skill_documents():
    # gh skill finds SKILL.md outside skills/ as well, so a skill document
    # anywhere else is offered to consumers as an installable skill.
    stray = [
        path.as_posix()
        for path in tracked_files()
        if path.name == "SKILL.md" and path.parts[0] != "skills"
    ]
    assert stray == []
