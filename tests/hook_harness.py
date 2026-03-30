from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRE_COMMIT = REPO_ROOT / "pre-commit"
POST_COMMIT = REPO_ROOT / "post-commit"
FAKE_MVN = Path(__file__).resolve().with_name("fake_mvn.py")


class TempGitRepo:
    def __init__(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory(prefix="maven-spotless-hooks-")
        self.root = Path(self._tempdir.name) / "repo"
        self.bin_dir = self.root / ".test-bin"
        self.env = os.environ.copy()

    def __enter__(self) -> "TempGitRepo":
        self.root.mkdir()
        self.bin_dir.mkdir()
        self._create_fake_maven_wrappers()
        self._prepare_environment()
        self.git("init")
        self.git("config", "user.email", "hooks@example.com")
        self.git("config", "user.name", "Hook Harness")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        self._install_hooks()
        self.commit("Initial commit", mode="noop", allow_empty=True)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._tempdir.cleanup()

    def _prepare_environment(self) -> None:
        self.env["PATH"] = str(self.bin_dir) + os.pathsep + self.env.get("PATH", "")
        self.env["FAKE_MVN_PY"] = str(FAKE_MVN)
        self.env["GIT_TERMINAL_PROMPT"] = "0"
        self.env["HOOK_TEST_PYTHON"] = "python" if os.name == "nt" else "python3"

    def _create_fake_maven_wrappers(self) -> None:
        shell_wrapper = textwrap.dedent(
            """\
            #!/bin/sh
            PYTHON_CMD="${HOOK_TEST_PYTHON:-python3}"
            exec "$PYTHON_CMD" "$FAKE_MVN_PY" "$@"
            """
        )
        cmd_wrapper = textwrap.dedent(
            """\
            @echo off
            %HOOK_TEST_PYTHON% "%FAKE_MVN_PY%" %*
            """
        )

        self._write_file(self.bin_dir / "mvn", shell_wrapper)
        self._write_file(self.bin_dir / "mvn.cmd", cmd_wrapper, newline="\r\n")
        self._write_file(self.root / "mvnw", shell_wrapper)
        self._write_file(self.root / "mvnw.cmd", cmd_wrapper, newline="\r\n")
        self._make_executable(self.bin_dir / "mvn")
        self._make_executable(self.root / "mvnw")

    def _install_hooks(self) -> None:
        hooks_dir = self.root / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        for source, destination_name in ((PRE_COMMIT, "pre-commit"), (POST_COMMIT, "post-commit")):
            destination = hooks_dir / destination_name
            destination.write_bytes(source.read_bytes())
            self._make_executable(destination)

    @staticmethod
    def _write_file(path: Path, contents: str, newline: str = "\n") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8", newline=newline)

    @staticmethod
    def _make_executable(path: Path) -> None:
        path.chmod(path.stat().st_mode | 0o755)

    def run(self, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            list(args),
            cwd=self.root,
            env=env or self.env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if check and result.returncode != 0:
            raise AssertionError(self.format_failure(args, result))
        return result

    def git(self, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return self.run("git", *args, check=check, env=env)

    def commit(
        self,
        message: str,
        *,
        mode: str = "staged",
        allow_empty: bool = False,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        env = self.env.copy()
        env["FAKE_MVN_MODE"] = mode
        command = ["git", "commit", "--no-gpg-sign"]
        if allow_empty:
            command.append("--allow-empty")
        command.extend(["-m", message])
        return self.run(*command, check=check, env=env)

    def write_file(self, relative_path: str, contents: str) -> None:
        self._write_file(self.root / relative_path, contents)

    def read_file(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def head_file(self, relative_path: str) -> str:
        return self.git("show", f"HEAD:{relative_path}").stdout

    def status_lines(self) -> list[str]:
        output = self.git("status", "--short", "--untracked-files=no").stdout.strip()
        return output.splitlines() if output else []

    def stash_list(self) -> str:
        return self.git("stash", "list").stdout

    def unmerged_files(self) -> list[str]:
        output = self.git("diff", "--name-only", "--diff-filter=U").stdout.strip()
        return output.splitlines() if output else []

    @staticmethod
    def format_failure(command: tuple[str, ...], result: subprocess.CompletedProcess[str]) -> str:
        command_text = " ".join(command)
        return f"Command failed: {command_text}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"


class HookHarnessTest(unittest.TestCase):
    def test_formats_staged_files_before_commit(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "BAD   \n")
            repo.git("add", "staged.txt")

            result = repo.commit("Format staged file", mode="staged")

            self.assertEqual(result.returncode, 0, repo.format_failure(("git", "commit"), result))
            self.assertEqual(repo.head_file("staged.txt"), "GOOD\n")
            self.assertEqual(repo.status_lines(), [])

    def test_tracked_unstaged_changes_follow_current_restore_flow(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "ORIGINAL\n")
            repo.write_file("notes.txt", "VALUE=BASE BAD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("staged.txt", "BAD   \n")
            repo.git("add", "staged.txt")
            repo.write_file("notes.txt", "VALUE=UNSTAGED BAD\n")

            result = repo.commit("Commit staged file only", mode="staged")

            self.assertEqual(result.returncode, 0, repo.format_failure(("git", "commit"), result))
            self.assertEqual(repo.head_file("staged.txt"), "GOOD\n")
            # The current hook flow restores tracked unstaged changes via stash
            # pop, then re-runs formatting and commits the result.
            self.assertEqual(repo.head_file("notes.txt"), "VALUE=UNSTAGED GOOD\n")
            self.assertEqual(repo.read_file("notes.txt"), "VALUE=UNSTAGED GOOD\n")
            self.assertEqual(repo.status_lines(), [])

    def test_preserves_existing_user_stash_entries(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "ORIGINAL\n")
            repo.write_file("notes.txt", "GOOD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("notes.txt", "USER STASH BAD\n")
            repo.git("stash", "push", "-m", "user-stash")
            repo.write_file("staged.txt", "BAD\n")
            repo.git("add", "staged.txt")

            result = repo.commit("Commit with existing stash", mode="staged")

            self.assertEqual(result.returncode, 0, repo.format_failure(("git", "commit"), result))
            self.assertIn("user-stash", repo.stash_list())
            self.assertEqual(repo.head_file("staged.txt"), "GOOD\n")

    def test_resolves_stash_pop_conflicts_and_finishes_commit(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "GOOD\n")
            repo.write_file("notes.txt", "VALUE=BASE BAD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("staged.txt", "BAD   \n")
            repo.git("add", "staged.txt")
            repo.write_file("notes.txt", "VALUE=UNSTAGED BAD\n")

            result = repo.commit("Exercise conflict path", mode="conflict")

            self.assertEqual(result.returncode, 0, repo.format_failure(("git", "commit"), result))
            self.assertEqual(repo.unmerged_files(), [])
            self.assertEqual(repo.head_file("staged.txt"), "GOOD\n")
            self.assertEqual(repo.head_file("notes.txt"), "VALUE=UNSTAGED GOOD\n")
            self.assertEqual(repo.status_lines(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
