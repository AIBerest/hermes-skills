#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const https = require("https");
const { URL } = require("url");
const { spawnSync } = require("child_process");

const PROXY_ENV_KEYS = [
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
];

class DeployError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = "DeployError";
    this.endpoint = options.endpoint || null;
    this.status = Number.isInteger(options.status) ? options.status : null;
    this.body = options.body || null;
  }

  toJSON() {
    const payload = { error: this.message };
    if (this.endpoint) payload.endpoint = this.endpoint;
    if (this.status !== null) payload.status = this.status;
    if (this.body) payload.body = this.body;
    return payload;
  }
}

function shorten(text, limit = 500) {
  if (!text) return "";
  const compact = String(text).trim().replace(/\s+/g, " ");
  return compact.length <= limit ? compact : `${compact.slice(0, limit)}...`;
}

function buildChildEnv() {
  const env = { ...process.env };
  for (const key of PROXY_ENV_KEYS) delete env[key];
  if (!env.GIT_TERMINAL_PROMPT) env.GIT_TERMINAL_PROMPT = "0";
  return env;
}

function runCmd(args, cwd, env, options = {}) {
  const check = options.check !== false;
  const proc = spawnSync(args[0], args.slice(1), {
    cwd,
    env,
    encoding: "utf8",
  });

  if (proc.error) {
    throw new DeployError(`Command failed: ${args.join(" ")}`, {
      body: shorten(proc.error.message || String(proc.error)),
    });
  }

  const status = typeof proc.status === "number" ? proc.status : 1;
  if (check && status !== 0) {
    throw new DeployError(`Command failed: ${args.join(" ")}`, {
      body: shorten(proc.stderr || proc.stdout),
    });
  }

  return { status, stdout: proc.stdout || "", stderr: proc.stderr || "" };
}

function requestJson(method, urlString, headers = {}, jsonBody = null, timeoutMs = 20000) {
  return new Promise((resolve, reject) => {
    let urlObj;
    try {
      urlObj = new URL(urlString);
    } catch (err) {
      reject(new DeployError("Invalid URL", { endpoint: `${method} ${urlString}`, body: shorten(err.message) }));
      return;
    }

    const body = jsonBody !== null ? Buffer.from(JSON.stringify(jsonBody), "utf8") : null;
    const req = https.request(
      {
        method,
        hostname: urlObj.hostname,
        port: urlObj.port || 443,
        path: `${urlObj.pathname}${urlObj.search}`,
        headers: {
          ...headers,
          ...(body
            ? {
                "Content-Type": "application/json",
                "Content-Length": body.length,
              }
            : {}),
        },
        timeout: timeoutMs,
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const text = Buffer.concat(chunks).toString("utf8");
          let parsed = text;
          try {
            parsed = text ? JSON.parse(text) : {};
          } catch (_) {
            parsed = text;
          }

          const status = Number(res.statusCode || 0);
          if (status >= 400) {
            reject(
              new DeployError("HTTP request failed", {
                endpoint: `${method} ${urlString}`,
                status,
                body: shorten(text),
              })
            );
            return;
          }
          resolve({ status, text, parsed });
        });
      }
    );

    req.on("timeout", () => req.destroy(new Error("timeout")));
    req.on("error", (err) => {
      reject(
        new DeployError("Network error during HTTP request", {
          endpoint: `${method} ${urlString}`,
          body: shorten(err.message),
        })
      );
    });

    if (body) req.write(body);
    req.end();
  });
}

function readEnvFile(repoPath) {
  const envPath = path.join(repoPath, ".env");
  if (!fs.existsSync(envPath)) {
    throw new DeployError("Missing .env in current repository root");
  }

  const envMap = {};
  const raw = fs.readFileSync(envPath, "utf8");
  for (const line of raw.split(/\r?\n/)) {
    const stripped = line.trim();
    if (!stripped || stripped.startsWith("#")) continue;
    const idx = stripped.indexOf("=");
    if (idx === -1) continue;
    const key = stripped.slice(0, idx).trim();
    const value = stripped.slice(idx + 1).trim().replace(/^['"]|['"]$/g, "");
    envMap[key] = value;
  }
  return envMap;
}

function validateRequiredKeys(envMap, mode) {
  const required = ["GITHUB_USERNAME", "GITHUB_TOKEN"];
  if (mode === "all") required.push("GITHUB_APP_INSTALLATION_ID", "VERCEL_TOKEN");

  const missing = required.filter((key) => !envMap[key]);
  if (missing.length) {
    throw new DeployError(`Missing required keys: ${missing.join(", ")}`);
  }
}

function normalizeRepoName(value) {
  return String(value || "")
    .replace(/[^A-Za-z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function ensureEnvNotTrackedAndIgnored(repoPath, childEnv) {
  if (!fs.existsSync(path.join(repoPath, ".env"))) return;

  const tracked = runCmd(["git", "ls-files", "--error-unmatch", ".env"], repoPath, childEnv, { check: false });
  if (tracked.status === 0) {
    throw new DeployError("Refusing to continue: .env is tracked by git");
  }

  const ignored = runCmd(["git", "check-ignore", ".env"], repoPath, childEnv, { check: false });
  if (ignored.status === 0) return;

  const ignorePath = path.join(repoPath, ".gitignore");
  let lines = [];
  if (fs.existsSync(ignorePath)) {
    lines = fs
      .readFileSync(ignorePath, "utf8")
      .split(/\r?\n/)
      .map((line) => line.trimEnd());
  }
  if (!lines.includes(".env")) {
    const prefix = lines.length > 0 && lines[lines.length - 1] !== "" ? "\n" : "";
    fs.appendFileSync(ignorePath, `${prefix}.env\n`, "utf8");
  }
}

function githubHeaders(token) {
  return {
    Authorization: `token ${token}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "deploy-github-vercel-skill",
  };
}

function vercelHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    "User-Agent": "deploy-github-vercel-skill",
  };
}

function addTeamParam(urlString, teamId) {
  if (!teamId) return urlString;
  const urlObj = new URL(urlString);
  urlObj.searchParams.set("teamId", teamId);
  return urlObj.toString();
}

async function preflight(repoPath, envMap, mode, childEnv) {
  runCmd(["git", "--version"], repoPath, childEnv);

  const writeTest = path.join(repoPath, ".codex-write-test");
  try {
    fs.writeFileSync(writeTest, "ok", "utf8");
  } finally {
    if (fs.existsSync(writeTest)) fs.unlinkSync(writeTest);
  }

  const gitDir = path.join(repoPath, ".git");
  if (fs.existsSync(gitDir) && fs.statSync(gitDir).isDirectory()) {
    const lockTest = path.join(gitDir, ".codex-lock-test");
    try {
      fs.writeFileSync(lockTest, "ok", "utf8");
    } catch (err) {
      throw new DeployError("No write access inside .git. Fix permissions and retry.");
    } finally {
      if (fs.existsSync(lockTest)) fs.unlinkSync(lockTest);
    }
  }

  await requestJson("GET", "https://api.github.com/user", githubHeaders(envMap.GITHUB_TOKEN));
  if (mode === "all") {
    await requestJson("GET", "https://api.vercel.com/v2/user", vercelHeaders(envMap.VERCEL_TOKEN));
  }
}

function ensureGitRepo(repoPath, childEnv, username) {
  const inside = runCmd(["git", "rev-parse", "--is-inside-work-tree"], repoPath, childEnv, { check: false });
  if (inside.status !== 0 || inside.stdout.trim() !== "true") {
    runCmd(["git", "init"], repoPath, childEnv);
  }

  const nameCfg = runCmd(["git", "config", "user.name"], repoPath, childEnv, { check: false });
  if (nameCfg.status !== 0 || !nameCfg.stdout.trim()) {
    runCmd(["git", "config", "user.name", username], repoPath, childEnv);
  }

  const mailCfg = runCmd(["git", "config", "user.email"], repoPath, childEnv, { check: false });
  if (mailCfg.status !== 0 || !mailCfg.stdout.trim()) {
    runCmd(["git", "config", "user.email", `${username}@users.noreply.github.com`], repoPath, childEnv);
  }

  const hasCommit = runCmd(["git", "rev-parse", "--verify", "HEAD"], repoPath, childEnv, { check: false }).status === 0;
  if (!hasCommit) {
    ensureEnvNotTrackedAndIgnored(repoPath, childEnv);
    runCmd(["git", "add", "."], repoPath, childEnv);
    runCmd(["git", "commit", "--allow-empty", "-m", "Initial commit"], repoPath, childEnv);
  }
}

async function createOrReuseGithubRepo(username, token, repoName) {
  const payload = { name: repoName, private: true, auto_init: false };
  try {
    const created = await requestJson("POST", "https://api.github.com/user/repos", githubHeaders(token), payload);
    return { repo: created.parsed, created: true };
  } catch (err) {
    if (!(err instanceof DeployError) || err.status !== 422) throw err;
    const existing = await requestJson(
      "GET",
      `https://api.github.com/repos/${username}/${repoName}`,
      githubHeaders(token)
    );
    return { repo: existing.parsed, created: false };
  }
}

function setOriginAndPush(repoPath, childEnv, cloneUrl, token) {
  const origin = runCmd(["git", "remote", "get-url", "origin"], repoPath, childEnv, { check: false });
  if (origin.status !== 0 || !origin.stdout.trim()) {
    runCmd(["git", "remote", "add", "origin", cloneUrl], repoPath, childEnv);
  } else if (origin.stdout.trim() !== cloneUrl) {
    runCmd(["git", "remote", "set-url", "origin", cloneUrl], repoPath, childEnv);
  }

  runCmd(["git", "branch", "-M", "main"], repoPath, childEnv);

  const basic = Buffer.from(`x-access-token:${token}`, "ascii").toString("base64");
  runCmd(
    [
      "git",
      "-c",
      `http.https://github.com/.extraheader=AUTHORIZATION: basic ${basic}`,
      "push",
      "-u",
      "origin",
      "main",
    ],
    repoPath,
    childEnv
  );
}

async function grantGithubAppAccess(token, installationId, repositoryId) {
  const res = await requestJson(
    "PUT",
    `https://api.github.com/user/installations/${installationId}/repositories/${repositoryId}`,
    githubHeaders(token)
  );
  if (res.status !== 204) {
    throw new DeployError("Unexpected status while granting GitHub App access", {
      endpoint: "PUT /user/installations/{id}/repositories/{repo_id}",
      status: res.status,
    });
  }
}

async function getOrCreateVercelProject(vercelToken, teamId, repoName, ownerRepo) {
  const getUrl = addTeamParam(`https://api.vercel.com/v9/projects/${repoName}`, teamId);
  try {
    const found = await requestJson("GET", getUrl, vercelHeaders(vercelToken));
    return found.parsed;
  } catch (err) {
    if (!(err instanceof DeployError) || err.status !== 404) throw err;
  }

  const createUrl = addTeamParam("https://api.vercel.com/v9/projects", teamId);
  const payload = {
    name: repoName,
    framework: null,
    gitRepository: { type: "github", repo: ownerRepo },
  };
  const created = await requestJson("POST", createUrl, vercelHeaders(vercelToken), payload);
  return created.parsed;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForDeployment(vercelToken, teamId, projectId, timeoutSeconds = 360, pollSeconds = 12) {
  const headers = vercelHeaders(vercelToken);
  const deadline = Date.now() + timeoutSeconds * 1000;
  let deployment = null;

  while (Date.now() < deadline) {
    const listUrl = addTeamParam(
      `https://api.vercel.com/v6/deployments?projectId=${encodeURIComponent(projectId)}&limit=1`,
      teamId
    );
    const listed = await requestJson("GET", listUrl, headers);
    const deployments = listed.parsed && listed.parsed.deployments;
    if (Array.isArray(deployments) && deployments.length > 0) {
      deployment = deployments[0];
      break;
    }
    await sleep(pollSeconds * 1000);
  }

  if (!deployment) {
    throw new DeployError("Timed out waiting for deployment to appear");
  }

  const deploymentId = deployment.uid || deployment.id;
  if (!deploymentId) {
    throw new DeployError("Deployment appeared but has no id");
  }

  while (Date.now() < deadline) {
    const detailsUrl = addTeamParam(`https://api.vercel.com/v13/deployments/${deploymentId}`, teamId);
    const detailsRes = await requestJson("GET", detailsUrl, headers);
    const details = detailsRes.parsed || {};
    const readyState = details.readyState;
    if (readyState === "READY") {
      return { latest: deployment, details };
    }
    if (readyState === "ERROR" || readyState === "CANCELED") {
      throw new DeployError(`Deployment failed with state ${readyState}`, {
        body: shorten(details.inspectorUrl || ""),
      });
    }
    await sleep(pollSeconds * 1000);
  }

  throw new DeployError("Timed out waiting for deployment to become READY");
}

async function verifySiteHealth(deploymentUrl) {
  let target = deploymentUrl;
  if (!/^https?:\/\//i.test(target)) target = `https://${target}`;
  const res = await requestJson("GET", target, { "User-Agent": "deploy-health-check" });
  const html = String(res.text || "").toLowerCase();
  const hasHtml = html.includes("<html") || html.includes("<title");
  return { ok: res.status >= 200 && res.status < 300 && hasHtml, status: res.status, url: target };
}

async function runDeploy(mode, repoPath) {
  const root = path.resolve(repoPath);
  const childEnv = buildChildEnv();
  const envMap = readEnvFile(root);
  validateRequiredKeys(envMap, mode);

  await preflight(root, envMap, mode, childEnv);

  const username = envMap.GITHUB_USERNAME;
  const token = envMap.GITHUB_TOKEN;
  const requestedRepoName = envMap.REPO_NAME || path.basename(root);
  const repoName = normalizeRepoName(requestedRepoName);
  if (!repoName) throw new DeployError("Resolved REPO_NAME is empty after normalization");

  ensureGitRepo(root, childEnv, username);
  const gh = await createOrReuseGithubRepo(username, token, repoName);
  const repo = gh.repo;
  setOriginAndPush(root, childEnv, repo.clone_url, token);

  const result = {
    mode,
    repo_name: repoName,
    github_repo_url: repo.html_url || `https://github.com/${username}/${repoName}`,
    github_full_name: repo.full_name || `${username}/${repoName}`,
    github_repository_id: repo.id || null,
    created: gh.created,
    branch: "main",
    skipped_steps: [],
  };

  if (mode === "github") {
    result.skipped_steps.push({ steps: "5-11", reason: "Mode is github (GitHub-only flow)." });
    return result;
  }

  await grantGithubAppAccess(token, envMap.GITHUB_APP_INSTALLATION_ID, Number(repo.id));
  const teamId = envMap.VERCEL_TEAM_ID || null;
  const project = await getOrCreateVercelProject(
    envMap.VERCEL_TOKEN,
    teamId,
    repoName,
    repo.full_name || `${username}/${repoName}`
  );

  if (!project.id) throw new DeployError("Vercel project response has no id");

  const deployment = await waitForDeployment(envMap.VERCEL_TOKEN, teamId, String(project.id));
  const details = deployment.details || {};
  const latest = deployment.latest || {};
  const aliases = Array.isArray(details.alias) ? details.alias : [];
  const deploymentUrl = details.url || latest.url || aliases[0];
  if (!deploymentUrl) throw new DeployError("Deployment completed but URL was not found");

  const health = await verifySiteHealth(deploymentUrl);
  result.vercel_project_id = project.id;
  result.vercel_project_name = project.name || repoName;
  result.deployment_url = deploymentUrl;
  result.deployment_status = details.readyState || null;
  result.site_health_check = health;

  return result;
}

function parseArgs(argv) {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { help: true };
  }

  const mode = argv[0];
  if (mode !== "github" && mode !== "all") {
    throw new DeployError("Mode must be 'github' or 'all'");
  }

  let repoPath = ".";
  for (let i = 1; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--repo-path") {
      if (i + 1 >= argv.length) throw new DeployError("Missing value for --repo-path");
      repoPath = argv[i + 1];
      i += 1;
      continue;
    }
    throw new DeployError(`Unknown argument: ${arg}`);
  }
  return { help: false, mode, repoPath };
}

function printHelp() {
  const lines = [
    "Usage:",
    "  node scripts/deploy.js <github|all> [--repo-path <path>]",
    "",
    "Examples:",
    "  node scripts/deploy.js github --repo-path .",
    "  node scripts/deploy.js all --repo-path /path/to/repo",
  ];
  process.stdout.write(`${lines.join("\n")}\n`);
}

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    const payload = err instanceof DeployError ? err.toJSON() : { error: `Unexpected error: ${err.message}` };
    process.stdout.write(`${JSON.stringify(payload)}\n`);
    process.exit(1);
    return;
  }

  if (parsed.help) {
    printHelp();
    process.exit(0);
    return;
  }

  try {
    const output = await runDeploy(parsed.mode, parsed.repoPath);
    process.stdout.write(`${JSON.stringify(output)}\n`);
    process.exit(0);
  } catch (err) {
    if (err instanceof DeployError) {
      process.stdout.write(`${JSON.stringify(err.toJSON())}\n`);
    } else {
      process.stdout.write(`${JSON.stringify({ error: `Unexpected error: ${err.message}` })}\n`);
    }
    process.exit(1);
  }
}

main();
