#!/usr/bin/env python3
"""Cross-platform deploy runner for the deploy-github-vercel skill.

Runs in two modes:
- github: steps 1-4 (GitHub only)
- all: steps 1-11 (GitHub + Vercel)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


PROXY_ENV_KEYS = [
    "ALL_PROXY",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "GIT_HTTP_PROXY",
    "GIT_HTTPS_PROXY",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "git_http_proxy",
    "git_https_proxy",
]


@dataclass
class DeployError(Exception):
    message: str
    endpoint: Optional[str] = None
    status: Optional[int] = None
    body: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"error": self.message}
        if self.endpoint:
            payload["endpoint"] = self.endpoint
        if self.status is not None:
            payload["status"] = self.status
        if self.body:
            payload["body"] = self.body
        return payload


def shorten(text: Optional[str], limit: int = 500) -> str:
    if not text:
        return ""
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "..."


def build_child_env() -> Dict[str, str]:
    child = os.environ.copy()
    for key in PROXY_ENV_KEYS:
        child.pop(key, None)
    child.setdefault("GIT_TERMINAL_PROMPT", "0")
    return child


def run_cmd(
    args: List[str],
    cwd: str,
    env: Dict[str, str],
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode != 0:
        raise DeployError(
            message=f"Command failed: {' '.join(args)}",
            body=shorten(proc.stderr or proc.stdout),
        )
    return proc


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    timeout: int = 20,
) -> Tuple[int, str, Any]:
    body_data = None
    if json_body is not None:
        body_data = json.dumps(json_body).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=body_data,
        headers=headers or {},
        method=method,
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed: Any
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = raw
            return resp.status, raw, parsed
    except urllib.error.HTTPError as exc:
        err_raw = exc.read().decode("utf-8", errors="replace")
        raise DeployError(
            message="HTTP request failed",
            endpoint=f"{method} {url}",
            status=exc.code,
            body=shorten(err_raw),
        ) from exc
    except urllib.error.URLError as exc:
        raise DeployError(
            message="Network error during HTTP request",
            endpoint=f"{method} {url}",
            body=shorten(str(exc.reason)),
        ) from exc


def read_env_file(repo_path: str) -> Dict[str, str]:
    env_path = os.path.join(repo_path, ".env")
    if not os.path.isfile(env_path):
        raise DeployError("Missing .env in current repository root")

    env_map: Dict[str, str] = {}
    with open(env_path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            env_map[key] = value
    return env_map


def validate_required_keys(env_map: Dict[str, str], mode: str) -> None:
    required = ["GITHUB_USERNAME", "GITHUB_TOKEN"]
    if mode == "all":
        required += ["GITHUB_APP_INSTALLATION_ID", "VERCEL_TOKEN"]
    missing = [k for k in required if not env_map.get(k)]
    if missing:
        raise DeployError("Missing required keys: " + ", ".join(missing))


def normalize_repo_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return normalized


def ensure_env_not_tracked_and_ignored(repo_path: str, child_env: Dict[str, str]) -> None:
    env_path = os.path.join(repo_path, ".env")
    if not os.path.isfile(env_path):
        return

    tracked = run_cmd(
        ["git", "ls-files", "--error-unmatch", ".env"],
        cwd=repo_path,
        env=child_env,
        check=False,
    ).returncode == 0
    if tracked:
        raise DeployError("Refusing to continue: .env is tracked by git")

    ignored = run_cmd(
        ["git", "check-ignore", ".env"],
        cwd=repo_path,
        env=child_env,
        check=False,
    ).returncode == 0
    if ignored:
        return

    ignore_path = os.path.join(repo_path, ".gitignore")
    lines: List[str] = []
    if os.path.isfile(ignore_path):
        with open(ignore_path, "r", encoding="utf-8") as handle:
            lines = [ln.rstrip("\r\n") for ln in handle]
    if ".env" not in lines:
        with open(ignore_path, "a", encoding="utf-8") as handle:
            if lines:
                handle.write("\n")
            handle.write(".env\n")


def preflight(repo_path: str, env_map: Dict[str, str], mode: str, child_env: Dict[str, str]) -> None:
    run_cmd(["git", "--version"], cwd=repo_path, env=child_env)

    test_path = os.path.join(repo_path, ".codex-write-test")
    try:
        with open(test_path, "w", encoding="utf-8") as handle:
            handle.write("ok")
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)

    git_dir = os.path.join(repo_path, ".git")
    if os.path.isdir(git_dir):
        lock_test = os.path.join(git_dir, ".codex-lock-test")
        try:
            with open(lock_test, "w", encoding="utf-8") as handle:
                handle.write("ok")
        except OSError as exc:
            raise DeployError(
                "No write access inside .git. Fix permissions and retry."
            ) from exc
        finally:
            if os.path.exists(lock_test):
                os.remove(lock_test)

    gh_headers = {
        "Authorization": f"token {env_map['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "deploy-github-vercel-skill",
    }
    http_request("GET", "https://api.github.com/user", headers=gh_headers)

    if mode == "all":
        vc_headers = {"Authorization": f"Bearer {env_map['VERCEL_TOKEN']}"}
        http_request("GET", "https://api.vercel.com/v2/user", headers=vc_headers)


def ensure_git_repo(repo_path: str, child_env: Dict[str, str], username: str) -> None:
    inside = run_cmd(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=repo_path,
        env=child_env,
        check=False,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        run_cmd(["git", "init"], cwd=repo_path, env=child_env)

    name_cfg = run_cmd(
        ["git", "config", "user.name"], cwd=repo_path, env=child_env, check=False
    )
    if name_cfg.returncode != 0 or not name_cfg.stdout.strip():
        run_cmd(["git", "config", "user.name", username], cwd=repo_path, env=child_env)

    email_cfg = run_cmd(
        ["git", "config", "user.email"], cwd=repo_path, env=child_env, check=False
    )
    if email_cfg.returncode != 0 or not email_cfg.stdout.strip():
        run_cmd(
            ["git", "config", "user.email", f"{username}@users.noreply.github.com"],
            cwd=repo_path,
            env=child_env,
        )

    has_commit = run_cmd(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=repo_path,
        env=child_env,
        check=False,
    ).returncode == 0
    if not has_commit:
        ensure_env_not_tracked_and_ignored(repo_path, child_env)
        run_cmd(["git", "add", "."], cwd=repo_path, env=child_env)
        run_cmd(
            ["git", "commit", "--allow-empty", "-m", "Initial commit"],
            cwd=repo_path,
            env=child_env,
        )


def github_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "deploy-github-vercel-skill",
    }


def create_or_reuse_github_repo(
    username: str, token: str, repo_name: str
) -> Tuple[Dict[str, Any], bool]:
    payload = {"name": repo_name, "private": True, "auto_init": False}
    headers = github_headers(token)
    try:
        _, _, parsed = http_request(
            "POST",
            "https://api.github.com/user/repos",
            headers=headers,
            json_body=payload,
        )
        return parsed, True
    except DeployError as exc:
        if exc.status != 422:
            raise
        _, _, parsed = http_request(
            "GET",
            f"https://api.github.com/repos/{username}/{repo_name}",
            headers=headers,
        )
        return parsed, False


def set_origin_and_push(
    repo_path: str,
    child_env: Dict[str, str],
    clone_url: str,
    token: str,
) -> None:
    origin = run_cmd(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_path,
        env=child_env,
        check=False,
    )
    if origin.returncode != 0 or not origin.stdout.strip():
        run_cmd(["git", "remote", "add", "origin", clone_url], cwd=repo_path, env=child_env)
    elif origin.stdout.strip() != clone_url:
        run_cmd(
            ["git", "remote", "set-url", "origin", clone_url],
            cwd=repo_path,
            env=child_env,
        )

    run_cmd(["git", "branch", "-M", "main"], cwd=repo_path, env=child_env)

    token_pair = f"x-access-token:{token}".encode("ascii")
    basic = base64.b64encode(token_pair).decode("ascii")
    run_cmd(
        [
            "git",
            "-c",
            f"http.https://github.com/.extraheader=AUTHORIZATION: basic {basic}",
            "push",
            "-u",
            "origin",
            "main",
        ],
        cwd=repo_path,
        env=child_env,
    )


def add_team_param(url: str, team_id: Optional[str]) -> str:
    if not team_id:
        return url
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    query["teamId"] = [team_id]
    rebuilt = parsed._replace(query=urllib.parse.urlencode(query, doseq=True))
    return urllib.parse.urlunparse(rebuilt)


def vercel_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def grant_github_app_access(token: str, installation_id: str, repository_id: int) -> None:
    status, _, _ = http_request(
        "PUT",
        f"https://api.github.com/user/installations/{installation_id}/repositories/{repository_id}",
        headers=github_headers(token),
    )
    if status != 204:
        raise DeployError(
            message="Unexpected status while granting GitHub App access",
            endpoint="PUT /user/installations/{id}/repositories/{repo_id}",
            status=status,
        )


def get_or_create_vercel_project(
    vercel_token: str,
    team_id: Optional[str],
    repo_name: str,
    owner_repo: str,
) -> Dict[str, Any]:
    headers = vercel_headers(vercel_token)
    get_url = add_team_param(f"https://api.vercel.com/v9/projects/{repo_name}", team_id)
    try:
        _, _, parsed = http_request("GET", get_url, headers=headers)
        return parsed
    except DeployError as exc:
        if exc.status != 404:
            raise

    create_url = add_team_param("https://api.vercel.com/v9/projects", team_id)
    payload = {
        "name": repo_name,
        "framework": None,
        "gitRepository": {"type": "github", "repo": owner_repo},
    }
    _, _, parsed = http_request("POST", create_url, headers=headers, json_body=payload)
    return parsed


def wait_for_deployment(
    vercel_token: str,
    team_id: Optional[str],
    project_id: str,
    timeout_seconds: int = 360,
    poll_seconds: int = 12,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    headers = vercel_headers(vercel_token)
    deadline = time.time() + timeout_seconds
    deployment: Optional[Dict[str, Any]] = None

    while time.time() < deadline:
        list_url = add_team_param(
            f"https://api.vercel.com/v6/deployments?projectId={project_id}&limit=1",
            team_id,
        )
        _, _, parsed = http_request("GET", list_url, headers=headers)
        deployments = parsed.get("deployments") if isinstance(parsed, dict) else None
        if deployments:
            deployment = deployments[0]
            break
        time.sleep(poll_seconds)

    if not deployment:
        raise DeployError("Timed out waiting for deployment to appear")

    deployment_id = deployment.get("uid") or deployment.get("id")
    if not deployment_id:
        raise DeployError("Deployment appeared but has no id")

    while time.time() < deadline:
        details_url = add_team_param(
            f"https://api.vercel.com/v13/deployments/{deployment_id}",
            team_id,
        )
        _, _, details = http_request("GET", details_url, headers=headers)
        ready_state = details.get("readyState")
        if ready_state == "READY":
            return deployment, details
        if ready_state in {"ERROR", "CANCELED"}:
            inspector = details.get("inspectorUrl") or ""
            raise DeployError(
                message=f"Deployment failed with state {ready_state}",
                body=shorten(inspector),
            )
        time.sleep(poll_seconds)

    raise DeployError("Timed out waiting for deployment to become READY")


def verify_site_health(deployment_url: str) -> Dict[str, Any]:
    target = deployment_url
    if not deployment_url.startswith("http://") and not deployment_url.startswith("https://"):
        target = f"https://{deployment_url}"

    status, raw, _ = http_request("GET", target, headers={"User-Agent": "deploy-health-check"})
    has_html = ("<html" in raw.lower()) or ("<title" in raw.lower())
    ok = 200 <= status < 300 and has_html
    return {"ok": ok, "status": status, "url": target}


def run_deploy(mode: str, repo_path: str) -> Dict[str, Any]:
    repo_path = os.path.abspath(repo_path)
    child_env = build_child_env()
    env_map = read_env_file(repo_path)
    validate_required_keys(env_map, mode)

    preflight(repo_path, env_map, mode, child_env)

    username = env_map["GITHUB_USERNAME"]
    token = env_map["GITHUB_TOKEN"]
    input_repo_name = env_map.get("REPO_NAME") or os.path.basename(repo_path)
    repo_name = normalize_repo_name(input_repo_name)
    if not repo_name:
        raise DeployError("Resolved REPO_NAME is empty after normalization")

    ensure_git_repo(repo_path, child_env, username)
    gh_repo, created = create_or_reuse_github_repo(username, token, repo_name)
    clone_url = gh_repo["clone_url"]
    set_origin_and_push(repo_path, child_env, clone_url, token)

    result: Dict[str, Any] = {
        "mode": mode,
        "repo_name": repo_name,
        "github_repo_url": gh_repo.get("html_url", f"https://github.com/{username}/{repo_name}"),
        "github_full_name": gh_repo.get("full_name", f"{username}/{repo_name}"),
        "github_repository_id": gh_repo.get("id"),
        "created": created,
        "branch": "main",
        "skipped_steps": [],
    }

    if mode == "github":
        result["skipped_steps"] = [
            {"steps": "5-11", "reason": "Mode is github (GitHub-only flow)."}
        ]
        return result

    installation_id = env_map["GITHUB_APP_INSTALLATION_ID"]
    repository_id = int(gh_repo["id"])
    grant_github_app_access(token, installation_id, repository_id)

    team_id = env_map.get("VERCEL_TEAM_ID") or None
    vercel_token = env_map["VERCEL_TOKEN"]
    project = get_or_create_vercel_project(
        vercel_token=vercel_token,
        team_id=team_id,
        repo_name=repo_name,
        owner_repo=gh_repo.get("full_name", f"{username}/{repo_name}"),
    )
    project_id = project.get("id")
    if not project_id:
        raise DeployError("Vercel project response has no id")

    latest_deploy, deploy_details = wait_for_deployment(
        vercel_token=vercel_token,
        team_id=team_id,
        project_id=project_id,
    )
    deployment_url = (
        deploy_details.get("url")
        or latest_deploy.get("url")
        or deploy_details.get("alias", [None])[0]
    )
    if not deployment_url:
        raise DeployError("Deployment completed but URL was not found")

    health = verify_site_health(deployment_url)

    result.update(
        {
            "vercel_project_id": project_id,
            "vercel_project_name": project.get("name", repo_name),
            "deployment_url": deployment_url,
            "deployment_status": deploy_details.get("readyState"),
            "site_health_check": health,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy current repository to GitHub/Vercel.")
    parser.add_argument("mode", choices=["github", "all"], help="Deploy mode")
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    args = parser.parse_args()

    try:
        output = run_deploy(mode=args.mode, repo_path=args.repo_path)
    except DeployError as exc:
        print(json.dumps(exc.to_dict(), ensure_ascii=False))
        return 1
    except Exception as exc:  # pragma: no cover - defensive surface for runner failures
        print(json.dumps({"error": f"Unexpected error: {exc}"}, ensure_ascii=False))
        return 1

    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
