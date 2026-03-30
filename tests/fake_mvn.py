#!/usr/bin/env python3
"""Small fake mvn entrypoint used by the hook harness tests.

The real hooks invoke `mvn spotless:apply`. For tests, we replace Maven with a
deterministic formatter that mutates files in controlled ways so we can assert
on hook behavior without pulling in Java, Maven, or Spotless.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def git_paths(repo: Path, *args: str) -> list[Path]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [repo / Path(item.decode("utf-8")) for item in result.stdout.split(b"\0") if item]


def normalize_content(content: str) -> str:
    normalized_lines = [
        line.rstrip().replace("BAD", "GOOD").replace("BASE", "FORMATTED")
        for line in content.splitlines()
    ]
    normalized = "\n".join(normalized_lines)

    if content.endswith(("\n", "\r\n")):
        return normalized + "\n"
    return normalized


def format_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return

    original = path.read_text(encoding="utf-8")
    updated = normalize_content(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8", newline="\n")


def paths_for_mode(repo: Path, mode: str) -> list[Path]:
    if mode == "noop":
        return []
    if mode in {"staged", "fail_after_format"}:
        return git_paths(repo, "diff", "--name-only", "HEAD", "-z")
    if mode == "conflict":
        return git_paths(repo, "ls-files", "-z")

    raise SystemExit(f"Unsupported FAKE_MVN_MODE: {mode}")


def main() -> int:
    if "spotless:apply" not in sys.argv[1:]:
        return 0

    repo = Path.cwd()
    mode = os.environ.get("FAKE_MVN_MODE", "staged")
    for path in paths_for_mode(repo, mode):
        format_file(path)
    if mode == "fail_after_format":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
