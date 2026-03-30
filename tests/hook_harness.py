from __future__ import annotations

import difflib
import os
import shutil
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
        self.real_git = shutil.which("git", path=self.env.get("PATH"))
        if self.real_git is None:
            raise RuntimeError("Unable to locate git for the hook harness.")

    def __enter__(self) -> "TempGitRepo":
        self.root.mkdir()
        self.bin_dir.mkdir()
        self._create_fake_git_wrappers()
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
        self.env["REAL_GIT"] = self.real_git

    def _create_fake_git_wrappers(self) -> None:
        shell_wrapper = textwrap.dedent(
            """\
            #!/bin/sh
            case "${HOOK_TEST_FAIL_GIT_STEP:-}" in
              diff_binary)
                if [ "$1" = "diff" ] && [ "$2" = "--binary" ] && [ "$3" = "--" ]; then
                  echo "simulated git diff --binary failure" >&2
                  exit 17
                fi
                ;;
              restore_worktree)
                if [ "$1" = "restore" ] && [ "$2" = "--worktree" ] && [ "$3" = "--" ]; then
                  echo "simulated git restore --worktree failure" >&2
                  exit 18
                fi
                ;;
              add_pathspec)
                if [ "$1" = "add" ] && [ "$3" = "--pathspec-file-nul" ]; then
                  case "$2" in
                    --pathspec-from-file=*)
                      echo "simulated git add --pathspec-from-file failure" >&2
                      exit 19
                      ;;
                  esac
                fi
                ;;
              apply_restore)
                if [ "$1" = "apply" ] && [ "$2" = "--whitespace=nowarn" ]; then
                  echo "simulated git apply restore failure" >&2
                  exit 20
                fi
                ;;
            esac
            exec "$REAL_GIT" "$@"
            """
        )
        cmd_wrapper = textwrap.dedent(
            """\
            @echo off
            setlocal
            if "%HOOK_TEST_FAIL_GIT_STEP%"=="diff_binary" if "%~1"=="diff" if "%~2"=="--binary" if "%~3"=="--" (
              >&2 echo simulated git diff --binary failure
              exit /b 17
            )
            if "%HOOK_TEST_FAIL_GIT_STEP%"=="restore_worktree" if "%~1"=="restore" if "%~2"=="--worktree" if "%~3"=="--" (
              >&2 echo simulated git restore --worktree failure
              exit /b 18
            )
            echo %~2 | findstr /B /C:"--pathspec-from-file=" >nul
            if "%HOOK_TEST_FAIL_GIT_STEP%"=="add_pathspec" if "%~1"=="add" if not errorlevel 1 if "%~3"=="--pathspec-file-nul" (
              >&2 echo simulated git add --pathspec-from-file failure
              exit /b 19
            )
            if "%HOOK_TEST_FAIL_GIT_STEP%"=="apply_restore" if "%~1"=="apply" if "%~2"=="--whitespace=nowarn" (
              >&2 echo simulated git apply restore failure
              exit /b 20
            )
            "%REAL_GIT%" %*
            """
        )

        self._write_file(self.bin_dir / "git", shell_wrapper)
        self._write_file(self.bin_dir / "git.cmd", cmd_wrapper, newline="\r\n")
        self._make_executable(self.bin_dir / "git")

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
        hook_path_prefix = str(self.bin_dir).replace("\\", "/").replace('"', '\\"')
        for source, destination_name in ((PRE_COMMIT, "pre-commit"), (POST_COMMIT, "post-commit")):
            destination = hooks_dir / destination_name
            source_text = source.read_text(encoding="utf-8")
            hook_body = source_text.split("\n", 1)[1] if source_text.startswith("#!/bin/sh\n") else source_text
            destination.write_text(
                textwrap.dedent(
                    f"""\
                    #!/bin/sh
                    PATH="{hook_path_prefix}:$PATH"
                    export PATH
                    {hook_body}
                    """
                ),
                encoding="utf-8",
                newline="\n",
            )
            self._make_executable(destination)

    @staticmethod
    def _write_file(path: Path, contents: str, newline: str = "\n") -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8", newline=newline)

    @staticmethod
    def _make_executable(path: Path) -> None:
        path.chmod(path.stat().st_mode | 0o755)

    def run(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            list(args),
            cwd=self.root,
            env=env or self.env,
            check=False,
            text=True,
            input=input_text,
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
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = self.env.copy()
        env["FAKE_MVN_MODE"] = mode
        if extra_env:
            env.update(extra_env)
        command = ["git", "commit", "--no-gpg-sign"]
        if allow_empty:
            command.append("--allow-empty")
        command.extend(["-m", message])
        return self.run(*command, check=check, env=env)

    def write_file(self, relative_path: str, contents: str) -> None:
        self._write_file(self.root / relative_path, contents)

    def stage_partial_file(
        self,
        relative_path: str,
        *,
        base_contents: str,
        staged_contents: str,
        worktree_contents: str,
    ) -> None:
        self.write_file(relative_path, worktree_contents)
        patch = "".join(
            difflib.unified_diff(
                base_contents.splitlines(keepends=True),
                staged_contents.splitlines(keepends=True),
                fromfile=f"a/{relative_path}",
                tofile=f"b/{relative_path}",
            )
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", delete=False) as patch_file:
            patch_file.write(patch)
            patch_path = patch_file.name

        try:
            self.run(
                "git",
                "apply",
                "--cached",
                patch_path,
                check=True,
                env=self.env | {"LC_ALL": "C"},
            )
        finally:
            Path(patch_path).unlink(missing_ok=True)

    def read_file(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def head_file(self, relative_path: str) -> str:
        return self.git("show", f"HEAD:{relative_path}").stdout

    def status_lines(self) -> list[str]:
        output = self.git("status", "--short", "--untracked-files=no").stdout.rstrip("\n")
        return output.splitlines() if output else []

    def stash_list(self) -> str:
        return self.git("stash", "list").stdout

    def unmerged_files(self) -> list[str]:
        output = self.git("diff", "--name-only", "--diff-filter=U").stdout.strip()
        return output.splitlines() if output else []

    @staticmethod
    def combined_output(result: subprocess.CompletedProcess[str]) -> str:
        return result.stdout + result.stderr

    @staticmethod
    def extract_recovery_patch_path(output: str) -> Path | None:
        prefix = "[git pre-commit hook] - Hidden changes patch: "
        for line in output.splitlines():
            if line.startswith(prefix):
                return Path(line[len(prefix) :].strip())
        return None

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

    def test_preserves_fully_unstaged_tracked_changes_outside_commit(self) -> None:
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
            self.assertEqual(repo.head_file("notes.txt"), "VALUE=BASE BAD\n")
            # Pre-commit keeps the fully unstaged tracked file out of HEAD.
            # Post-commit still formats the restored working-tree copy.
            self.assertEqual(repo.read_file("notes.txt"), "VALUE=UNSTAGED GOOD\n")
            self.assertEqual(repo.status_lines(), [" M notes.txt"])
            self.assertEqual(repo.unmerged_files(), [])

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

    def test_promotes_partially_staged_files_before_formatting(self) -> None:
        with TempGitRepo() as repo:
            base_contents = "FIRST=ORIGINAL\nSECOND=ORIGINAL\n"
            repo.write_file("partial.txt", base_contents)
            repo.git("add", "partial.txt")
            repo.commit("Seed partial file", mode="noop")

            repo.stage_partial_file(
                "partial.txt",
                base_contents=base_contents,
                staged_contents="FIRST=BAD\nSECOND=ORIGINAL\n",
                worktree_contents="FIRST=BAD\nSECOND=UNSTAGED BAD\n",
            )

            result = repo.commit("Commit partially staged file", mode="staged")

            self.assertEqual(result.returncode, 0, repo.format_failure(("git", "commit"), result))
            self.assertEqual(repo.head_file("partial.txt"), "FIRST=GOOD\nSECOND=UNSTAGED GOOD\n")
            self.assertEqual(repo.status_lines(), [])

    def test_aborts_when_promoting_partially_staged_files_fails(self) -> None:
        with TempGitRepo() as repo:
            base_contents = "FIRST=ORIGINAL\nSECOND=ORIGINAL\n"
            repo.write_file("partial.txt", base_contents)
            repo.git("add", "partial.txt")
            repo.commit("Seed partial file", mode="noop")

            repo.stage_partial_file(
                "partial.txt",
                base_contents=base_contents,
                staged_contents="FIRST=BAD\nSECOND=ORIGINAL\n",
                worktree_contents="FIRST=BAD\nSECOND=UNSTAGED BAD\n",
            )

            result = repo.commit(
                "Fail partial promotion",
                mode="staged",
                check=False,
                extra_env={"HOOK_TEST_FAIL_GIT_STEP": "add_pathspec"},
            )

            output = repo.combined_output(result)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Failed to promote partially staged files. Please refresh your index and try again.", output)
            self.assertEqual(repo.head_file("partial.txt"), base_contents)
            self.assertEqual(repo.read_file("partial.txt"), "FIRST=BAD\nSECOND=UNSTAGED BAD\n")

    def test_aborts_when_building_recovery_patch_fails(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "ORIGINAL\n")
            repo.write_file("notes.txt", "VALUE=BASE BAD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("staged.txt", "BAD\n")
            repo.git("add", "staged.txt")
            repo.write_file("notes.txt", "VALUE=UNSTAGED BAD\n")

            result = repo.commit(
                "Fail patch generation",
                mode="staged",
                check=False,
                extra_env={"HOOK_TEST_FAIL_GIT_STEP": "diff_binary"},
            )

            output = repo.combined_output(result)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Failed to build a recovery patch for fully unstaged tracked changes. Aborting commit!", output)
            self.assertEqual(repo.head_file("staged.txt"), "ORIGINAL\n")
            self.assertEqual(repo.head_file("notes.txt"), "VALUE=BASE BAD\n")
            self.assertEqual(repo.read_file("notes.txt"), "VALUE=UNSTAGED BAD\n")

    def test_preserves_recovery_patch_when_hiding_fully_unstaged_changes_fails(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "ORIGINAL\n")
            repo.write_file("notes.txt", "VALUE=BASE BAD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("staged.txt", "BAD\n")
            repo.git("add", "staged.txt")
            repo.write_file("notes.txt", "VALUE=UNSTAGED BAD\n")

            result = repo.commit(
                "Fail hide fully unstaged changes",
                mode="staged",
                check=False,
                extra_env={"HOOK_TEST_FAIL_GIT_STEP": "restore_worktree"},
            )

            output = repo.combined_output(result)
            recovery_patch = repo.extract_recovery_patch_path(output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Preserving recovery artifacts at", output)
            self.assertIn("Failed to temporarily hide fully unstaged tracked changes. Aborting commit!", output)
            self.assertIsNotNone(recovery_patch)
            assert recovery_patch is not None
            try:
                self.assertTrue(recovery_patch.exists())
                self.assertIn("notes.txt", recovery_patch.read_text(encoding="utf-8"))
                self.assertIn("+VALUE=UNSTAGED BAD", recovery_patch.read_text(encoding="utf-8"))
            finally:
                shutil.rmtree(recovery_patch.parent, ignore_errors=True)

    def test_preserves_recovery_patch_when_restoring_hidden_changes_fails(self) -> None:
        with TempGitRepo() as repo:
            repo.write_file("staged.txt", "ORIGINAL\n")
            repo.write_file("notes.txt", "VALUE=BASE BAD\n")
            repo.git("add", "staged.txt", "notes.txt")
            repo.commit("Seed tracked files", mode="noop")

            repo.write_file("staged.txt", "BAD\n")
            repo.git("add", "staged.txt")
            repo.write_file("notes.txt", "VALUE=UNSTAGED BAD\n")

            result = repo.commit(
                "Fail restore fully unstaged changes",
                mode="staged",
                check=False,
                extra_env={"HOOK_TEST_FAIL_GIT_STEP": "apply_restore"},
            )

            output = repo.combined_output(result)
            recovery_patch = repo.extract_recovery_patch_path(output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Preserving recovery artifacts at", output)
            self.assertIn("Failed to restore fully unstaged tracked changes.", output)
            self.assertIn("You can re-apply the patch manually with: git apply", output)
            self.assertIsNotNone(recovery_patch)
            assert recovery_patch is not None
            try:
                self.assertTrue(recovery_patch.exists())
                self.assertIn("notes.txt", recovery_patch.read_text(encoding="utf-8"))
                self.assertEqual(repo.head_file("staged.txt"), "ORIGINAL\n")
                self.assertEqual(repo.head_file("notes.txt"), "VALUE=BASE BAD\n")
            finally:
                shutil.rmtree(recovery_patch.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
