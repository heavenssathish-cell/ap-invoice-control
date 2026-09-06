#!/usr/bin/env python3
"""Create a public GitHub repository and publish this static site to GitHub Pages.

This program uses only Python's standard library. It never saves or prints the
personal access token supplied at the prompt.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_ROOT = "https://api.github.com"
# This stable REST API version is supported by GitHub.com at the time of writing.
API_VERSION = "2022-11-28"
MAIN_BRANCH = "main"
SKIP_DIRECTORY_NAMES = {".git", "__pycache__", ".venv", "venv", "node_modules"}
SKIP_FILE_NAMES = {".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


class GitHubApiError(RuntimeError):
    """A GitHub API request failed."""


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "ap-invoice-control-github-pages-deployer",
        }

    def request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = None
        headers = dict(self.headers)
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(API_ROOT + endpoint, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=45) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read().decode("utf-8", errors="replace")
            try:
                details = json.loads(raw)
                message = details.get("message", raw)
                if details.get("errors"):
                    message = f"{message} ({details['errors']})"
            except json.JSONDecodeError:
                message = raw or error.reason
            raise GitHubApiError(f"{method} {endpoint} failed ({error.code}): {message}") from error
        except URLError as error:
            raise GitHubApiError(f"Could not reach GitHub: {error.reason}") from error

        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a public GitHub repository and publish a static site to GitHub Pages."
    )
    parser.add_argument(
        "--repo",
        default="ap-invoice-control",
        help="new repository name (default: ap-invoice-control)",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="folder containing index.html (default: the folder containing this script)",
    )
    parser.add_argument(
        "--pages-mode",
        choices=("branch", "workflow"),
        default="branch",
        help=(
            "branch publishes main/root directly (default); workflow enables the bundled "
            "GitHub Actions workflow after the next normal push"
        ),
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=120,
        help="how long to wait for the first branch-based Pages build (default: 120)",
    )
    return parser.parse_args()


def validate_source(source_dir: Path) -> Path:
    source_dir = source_dir.expanduser().resolve()
    if not source_dir.is_dir():
        raise ValueError(f"Source folder does not exist: {source_dir}")
    if not (source_dir / "index.html").is_file():
        raise ValueError(
            f"No index.html was found in {source_dir}. GitHub Pages needs index.html at the site root."
        )
    return source_dir


def should_upload(relative_path: Path) -> bool:
    if any(part in SKIP_DIRECTORY_NAMES for part in relative_path.parts[:-1]):
        return False
    if relative_path.name in SKIP_FILE_NAMES or relative_path.suffix.lower() in SKIP_SUFFIXES:
        return False
    # Never accidentally publish local environment files or credentials.
    if relative_path.name == ".env" or relative_path.name.startswith(".env."):
        return False
    return True


def collect_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for file_path in source_dir.rglob("*"):
        if file_path.is_symlink():
            raise ValueError(f"Symbolic links are not supported by this deployer: {file_path}")
        if not file_path.is_file():
            continue
        relative_path = file_path.relative_to(source_dir)
        if should_upload(relative_path):
            if file_path.stat().st_size > 95 * 1024 * 1024:
                raise ValueError(
                    f"{relative_path} is larger than 95 MiB. The GitHub Contents API cannot upload it."
                )
            files.append(file_path)

    if not files:
        raise ValueError("There are no files to upload.")

    # Commit the workflow after Pages has been enabled. Its special commit message
    # prevents an unnecessary initial workflow run while the repository is seeded.
    workflow = source_dir / ".github" / "workflows" / "deploy.yml"
    files.sort(key=lambda path: path.relative_to(source_dir).as_posix())
    if workflow in files:
        files.remove(workflow)
        files.append(workflow)
    return files


def get_existing_file_sha(client: GitHubClient, owner: str, repository: str, path: str) -> str | None:
    endpoint = f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/contents/{quote(path, safe='/')}"
    try:
        response = client.request("GET", endpoint)
    except GitHubApiError as error:
        if "(404)" in str(error):
            return None
        raise
    return response.get("sha")


def upload_file(
    client: GitHubClient,
    owner: str,
    repository: str,
    source_dir: Path,
    file_path: Path,
) -> None:
    relative_path = file_path.relative_to(source_dir).as_posix()
    encoded_content = base64.b64encode(file_path.read_bytes()).decode("ascii")
    payload: dict[str, Any] = {
        "message": f"Deploy {relative_path}",
        "content": encoded_content,
        "branch": MAIN_BRANCH,
    }
    existing_sha = get_existing_file_sha(client, owner, repository, relative_path)
    if existing_sha:
        payload["sha"] = existing_sha
    if relative_path == ".github/workflows/deploy.yml":
        payload["message"] = "Add GitHub Pages workflow [skip ci]"

    endpoint = (
        f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/contents/"
        f"{quote(relative_path, safe='/')}"
    )
    client.request("PUT", endpoint, payload)
    print(f"  Uploaded {relative_path}")


def ensure_main_branch(client: GitHubClient, owner: str, repository: str, default_branch: str) -> None:
    if default_branch == MAIN_BRANCH:
        return
    endpoint = (
        f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/branches/"
        f"{quote(default_branch, safe='')}/rename"
    )
    client.request("POST", endpoint, {"new_name": MAIN_BRANCH})


def enable_pages(
    client: GitHubClient, owner: str, repository: str, pages_mode: str
) -> dict[str, Any]:
    endpoint = f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/pages"
    if pages_mode == "branch":
        payload: dict[str, Any] = {
            "build_type": "legacy",
            "source": {"branch": MAIN_BRANCH, "path": "/"},
        }
    else:
        payload = {"build_type": "workflow"}

    try:
        return client.request("POST", endpoint, payload)
    except GitHubApiError as error:
        if "(409)" in str(error):
            print("GitHub Pages was already enabled; using its existing configuration.")
            return client.request("GET", endpoint)
        raise


def wait_for_pages(
    client: GitHubClient,
    owner: str,
    repository: str,
    initial_site: dict[str, Any],
    seconds: int,
) -> str:
    fallback_url = f"https://{owner}.github.io/{repository}/"
    site_url = initial_site.get("html_url") or fallback_url
    endpoint = f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/pages"
    deadline = time.monotonic() + max(0, seconds)

    while time.monotonic() < deadline:
        site = client.request("GET", endpoint)
        site_url = site.get("html_url") or site_url
        if site.get("status") == "built":
            return site_url
        time.sleep(5)
    return site_url


def main() -> int:
    args = parse_arguments()
    try:
        source_dir = validate_source(args.source_dir)
        files = collect_files(source_dir)
        if args.wait_seconds < 0:
            raise ValueError("--wait-seconds cannot be negative.")
    except ValueError as error:
        print(f"Setup error: {error}", file=sys.stderr)
        return 2

    print("GitHub token is requested securely and will not be stored.")
    token = getpass.getpass("GitHub Personal Access Token: ").strip()
    if not token:
        print("Setup error: a token is required.", file=sys.stderr)
        return 2

    client = GitHubClient(token)
    try:
        account = client.request("GET", "/user")
        owner = account["login"]
        created_repo = client.request(
            "POST",
            "/user/repos",
            {
                "name": args.repo,
                "description": "AP Invoice Control static web application",
                "private": False,
                "auto_init": True,
            },
        )
        repository = created_repo["name"]
        print(f"Created https://github.com/{owner}/{repository}")

        ensure_main_branch(client, owner, repository, created_repo.get("default_branch", MAIN_BRANCH))

        print(f"Uploading {len(files)} file(s)...")
        deferred_workflow: Path | None = None
        for file_path in files:
            if file_path.relative_to(source_dir).as_posix() == ".github/workflows/deploy.yml":
                deferred_workflow = file_path
                continue
            upload_file(client, owner, repository, source_dir, file_path)

        pages_site = enable_pages(client, owner, repository, args.pages_mode)
        if deferred_workflow:
            upload_file(client, owner, repository, source_dir, deferred_workflow)

        if args.pages_mode == "branch":
            print("GitHub Pages is publishing from main / (root). Waiting for the first build...")
            live_url = wait_for_pages(
                client, owner, repository, pages_site, args.wait_seconds
            )
        else:
            live_url = pages_site.get("html_url") or f"https://{owner}.github.io/{repository}/"
            print("GitHub Actions publishing is enabled. Push a normal commit to start its first deployment.")

        print(f"\nLive URL: {live_url}")
        print("Keep the repository public and revoke this temporary token when you are finished.")
        return 0
    except (GitHubApiError, KeyError, ValueError) as error:
        print(f"Deployment failed: {error}", file=sys.stderr)
        print(
            "No token was written to disk. If the repository was created, you can inspect or remove it in GitHub.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

