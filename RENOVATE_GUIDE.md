# Renovate Bot - Complete Guide

## Overview

This repository uses Renovate Bot to automatically manage dependency updates. Renovate scans your codebase for dependencies (Docker images, Python packages, npm packages, etc.) and creates pull requests to keep them up-to-date.

## Setup Structure

- **[renovate.json](renovate.json)** - Global configuration file that defines how Renovate behaves in this repository
- **[renovate-bot/](renovate-bot/)** - Folder containing self-hosted Renovate runner scripts

---

## How to Run Renovate Bot

### Prerequisites

1. **Docker** - Make sure Docker is installed and running
2. **GitHub Personal Access Token (PAT)** - Already configured in [renovate-bot/github-pat.txt](renovate-bot/github-pat.txt)
   - Token needs: `repo` (full control), `workflow` permissions

### Running the Bot

Navigate to the renovate-bot folder and execute:

```bash
cd renovate-bot
./run.sh
```

**What happens:**
1. The script reads your GitHub token from `github-pat.txt`
2. Launches Renovate in a Docker container
3. Mounts `config.js` to tell Renovate which repositories to scan
4. Processes your repository according to [renovate.json](renovate.json) configuration
5. Creates pull requests for dependency updates

### Dry Run Mode (Testing)

To test without creating actual PRs, uncomment the dry-run line in [run.sh](renovate-bot/run.sh):

```bash
# --dry-run=full
```

Change to:

```bash
  --dry-run=full
```

---

## Configuration Explained: renovate.json

### Schema Reference

```json
"$schema": "https://docs.renovatebot.com/renovate-schema.json"
```

**Purpose:** Provides IntelliSense and validation in your editor.

---

### Base Configuration

```json
"extends": [
  "config:recommended",
  ":dependencyDashboard",
  ":rebaseStalePrs"
]
```

#### `config:recommended`
- **What it does:** Applies Renovate's recommended defaults
- **Includes:**
  - Groups monorepo packages together
  - Schedules updates during off-peak hours
  - Enables semantic commit messages
  - Auto-detects package managers (pip, npm, Docker, etc.)

#### `:dependencyDashboard`
- **What it does:** Creates a "Dependency Dashboard" issue in your repository
- **Benefits:**
  - Single overview of all pending updates
  - Ability to trigger updates manually
  - Shows rate-limited or pending PRs
  - Easy way to reject specific updates

#### `:rebaseStalePrs`
- **What it does:** Automatically rebases PRs when base branch changes
- **Benefits:**
  - Keeps PRs up-to-date with main branch
  - Prevents merge conflicts
  - Ensures CI runs against latest code

---

### Labels

```json
"labels": ["dependencies", "renovate"]
```

**Purpose:** All Renovate PRs will be tagged with these labels for easy filtering.

---

### Package Rules

Package rules let you customize behavior for specific dependency types.

#### Rule 1: Enable Docker Updates

```json
{
  "matchCategories": ["docker"],
  "enabled": true
}
```

- **Target:** All Docker images in Dockerfiles, docker-compose.yaml, etc.
- **Action:** Ensures Docker dependency scanning is enabled
- **Example:** Updates `python:3.9` → `python:3.12` or specific image versions

---

#### Rule 2: Auto-merge Python Patch Updates

```json
{
  "matchDatasources": ["pypi"],
  "matchUpdateTypes": ["patch"],
  "automerge": true
}
```

- **Target:** Python packages from PyPI (in requirements.txt, pyproject.toml, etc.)
- **Scope:** Only patch updates (e.g., `1.2.3` → `1.2.4`)
- **Action:** Automatically merges PR if tests pass
- **Rationale:** Patch versions typically only include bug fixes, low risk

**Update Types:**
- `major`: `1.x.x` → `2.0.0` (breaking changes possible)
- `minor`: `1.1.x` → `1.2.0` (new features, backward compatible)
- `patch`: `1.1.1` → `1.1.2` (bug fixes only)

---

#### Rule 3: Group Python Minor/Patch Updates

```json
{
  "matchDatasources": ["pypi"],
  "matchUpdateTypes": ["minor", "patch"],
  "groupName": "all-minor-patch-python"
}
```

- **Target:** Python packages (minor and patch updates)
- **Action:** Combines multiple updates into a single PR
- **Example:** Instead of 10 separate PRs for 10 packages, creates 1 PR titled "Update all-minor-patch-python"
- **Benefits:**
  - Reduces PR noise
  - Easier to review and test related updates together
  - Fewer CI runs

---

#### Rule 4: AWS SDK Schedule

```json
{
  "matchPackageNames": ["boto3", "botocore"],
  "schedule": ["before 5am on monday"]
}
```

- **Target:** AWS SDK packages (boto3, botocore)
- **Action:** Only creates PRs before 5 AM on Mondays
- **Rationale:** 
  - boto3/botocore update very frequently (often daily)
  - Scheduling prevents constant PR spam
  - Monday morning timing allows review at start of week

**Schedule Syntax Examples:**
- `"after 10pm"` - After 10 PM any day
- `"before 5am on monday"` - Before 5 AM on Mondays only
- `"every weekend"` - Saturday and Sunday
- `"on friday and saturday"` - Friday and Saturday only

---

## How Renovate Works in Your Repository

### Detection

Renovate automatically scans these files in your repo:

1. **Python:** `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile`
2. **Docker:** `Dockerfile`, `docker-compose.yaml`, `.gitlab-ci.yml`
3. **JavaScript:** `package.json`, `package-lock.json`
4. **And many more...**

### Example Workflow

Based on your current configuration:

1. **Monday before 5 AM:**
   - Checks boto3/botocore for updates
   - Creates PR if updates available

2. **Anytime (default schedule):**
   - Scans all other Python dependencies
   - Groups minor/patch updates into one PR
   - Auto-merges patch updates after CI passes
   - Scans Docker images for updates
   - Creates individual PRs for major updates

3. **Dependency Dashboard:**
   - View all pending updates in one issue
   - Manually trigger updates by checking boxes

---

## Common Customizations

### Add More Package Rules

Want to auto-merge Docker patch updates too?

```json
{
  "matchCategories": ["docker"],
  "matchUpdateTypes": ["patch"],
  "automerge": true
}
```

### Disable Specific Packages

Never want to update a package?

```json
{
  "matchPackageNames": ["legacy-package"],
  "enabled": false
}
```

### Change Default Schedule

Run all updates only on weekends?

```json
{
  "schedule": ["every weekend"]
}
```

---

## Monitoring Renovate

### Check Status

1. **GitHub Issues:** Look for "Dependency Dashboard" issue
2. **Pull Requests:** Filter by label `renovate`
3. **Actions/CI:** Check if Renovate's CI checks pass

### Logs

When running locally, Docker container logs show:
- Detected dependencies
- Updates found
- PRs created or updated
- Errors or rate limits

---

## Troubleshooting

### No PRs Being Created

1. Check if onboarding PR was merged
2. Verify GitHub token has correct permissions
3. Check Dependency Dashboard for rate-limited updates

### Too Many PRs

1. Add more grouping rules
2. Adjust schedules
3. Use `automerge` for low-risk updates

### Auto-merge Not Working

1. Ensure repository settings allow auto-merge
2. Check branch protection rules
3. Verify CI checks are passing

---

## Best Practices

1. **Start Conservative:** Don't auto-merge until you trust your test suite
2. **Use Grouping:** Reduce PR noise by grouping related updates
3. **Schedule Heavy Updaters:** Packages like AWS SDKs update frequently
4. **Monitor Dashboard:** Regularly check Dependency Dashboard issue
5. **Review Major Updates:** Always manually review major version updates

---

## Resources

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Preset Configs](https://docs.renovatebot.com/presets-config/)
- [Package Rules](https://docs.renovatebot.com/configuration-options/#packagerules)

---

## Your Current Setup Summary

✅ **Enabled:** Docker, Python (PyPI)  
🤖 **Auto-merge:** Python patch updates only  
📦 **Grouped:** Python minor/patch updates  
📅 **Scheduled:** boto3/botocore (Monday mornings)  
🏷️ **Labels:** `dependencies`, `renovate`  
📊 **Dashboard:** Enabled  
🔄 **Auto-rebase:** Enabled
