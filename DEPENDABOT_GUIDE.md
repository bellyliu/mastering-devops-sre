# GitHub Dependabot - Complete Guide

## Overview

GitHub Dependabot is a native GitHub feature that automatically keeps your dependencies up-to-date by creating pull requests when new versions are available. Unlike self-hosted tools, Dependabot runs entirely within GitHub's infrastructure with zero setup beyond a configuration file.

## What is Dependabot?

Dependabot is GitHub's built-in dependency management tool that:
- **Monitors** your project dependencies automatically
- **Detects** outdated packages and security vulnerabilities
- **Creates** pull requests with updates
- **Runs** on GitHub's infrastructure (no hosting required)
- **Integrates** seamlessly with GitHub Security features

### Key Differences: Dependabot vs Renovate Bot

| Feature | Dependabot | Renovate Bot |
|---------|-----------|--------------|
| **Hosting** | Built into GitHub | Self-hosted or cloud |
| **Setup** | Just add config file | Requires runner/service |
| **Cost** | Free on GitHub | Free (open source) |
| **Platform** | GitHub only | GitHub, GitLab, Bitbucket, etc. |
| **Config Flexibility** | Good | Extensive |
| **Grouping** | Supported | Advanced |
| **Scheduling** | Limited (daily, weekly, monthly) | Highly flexible (cron-like) |
| **Security Alerts** | Native integration | Via API |

---

## How Dependabot Works

### 1. **Configuration**
You create a `.github/dependabot.yml` file in your repository defining:
- Which package ecosystems to monitor (npm, pip, docker, etc.)
- Which directories to scan
- Update frequency
- Grouping rules
- Version update strategies

### 2. **Scanning**
Dependabot automatically:
- Scans your repository for dependency files
- Checks registries for newer versions
- Identifies security vulnerabilities (via GitHub Advisory Database)
- Compares current vs available versions

### 3. **Pull Request Creation**
When updates are found, Dependabot:
- Creates individual or grouped PRs
- Includes changelog and release notes
- Runs your CI/CD tests
- Provides compatibility scores
- Labels PRs appropriately

### 4. **Security Updates**
Dependabot Security Updates run separately and:
- Monitor GitHub Advisory Database
- Create **immediate** PRs for vulnerabilities
- Prioritize security patches
- Can auto-merge critical fixes

---

## Setup Structure

Your repository has two Dependabot configurations:

### Option 1: `.github/dependabot.yml` (Recommended)
```
.github/
└── dependabot.yml    # Active configuration
```
**Location:** `.github/dependabot.yml`  
**Status:** ✅ This is the official location GitHub reads from

### Option 2: `dependabot/dependabot.yml` (Reference/Backup)
```
dependabot/
└── dependabot.yml    # Backup or reference
```
**Location:** `dependabot/dependabot.yml`  
**Status:** ⚠️ Not read by GitHub, likely for documentation

**Note:** GitHub **only** reads from `.github/dependabot.yml`. The `dependabot/` folder configuration is ignored by GitHub but can serve as a template or backup.

---

## How to Enable Dependabot

### Prerequisites
- GitHub repository (public or private)
- Dependency files in your repo (`package.json`, `requirements.txt`, `Dockerfile`, etc.)

### Steps

1. **Create configuration file:**
   ```bash
   mkdir -p .github
   touch .github/dependabot.yml
   ```

2. **Add basic configuration:**
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "npm"
       directory: "/"
       schedule:
         interval: "weekly"
   ```

3. **Commit and push:**
   ```bash
   git add .github/dependabot.yml
   git commit -m "Configure Dependabot"
   git push
   ```

4. **Verify activation:**
   - Go to **Settings** → **Security & analysis** → **Dependabot**
   - Or check **Insights** → **Dependency graph** → **Dependabot**

---

## Configuration Explained: Your Current Setup

### File Location
```yaml
# File: .github/dependabot.yml
```

### Version Declaration
```yaml
version: 2
```
**Required.** Specifies Dependabot configuration schema version.

---

### 1. GitHub Actions Updates

```yaml
- package-ecosystem: "github-actions"
  directory: "/"
  schedule:
    interval: "weekly"
  groups:
    actions-dependencies:
      patterns:
        - "*"
```

#### Breakdown:

**`package-ecosystem: "github-actions"`**
- Monitors GitHub Actions workflows (`.github/workflows/*.yml`)
- Checks for action updates (e.g., `actions/checkout@v3` → `v4`)

**`directory: "/"`**
- Root directory to scan
- For actions, this finds `.github/workflows/` automatically

**`schedule.interval: "weekly"`**
- Checks for updates once per week
- Runs on Mondays at a random time (GitHub's default)
- Options: `daily`, `weekly`, `monthly`

**`groups.actions-dependencies`**
- **Combines** all GitHub Actions updates into **one PR**
- Instead of separate PRs for each action
- `patterns: ["*"]` = match all actions

**Benefits:**
- Less PR noise
- Easier to review related action updates together
- Single CI run instead of multiple

---

### 2. Python Dependencies (FastAPI MongoDB)

```yaml
- package-ecosystem: "pip"
  directory: "/applications/fast-api/mongodb/app"
  schedule:
    interval: "weekly"
    day: "monday"
    timezone: "Asia/Jakarta"
  groups:
    python-dependencies:
      patterns:
        - "*"
      update-types:
        - "minor"
        - "patch"
```

#### Breakdown:

**`package-ecosystem: "pip"`**
- Monitors Python dependencies
- Scans: `requirements.txt`, `Pipfile`, `setup.py`, `pyproject.toml`

**`directory: "/applications/fast-api/mongodb/app"`**
- Specific path to scan
- Looks for dependency files in this directory
- Must contain `requirements.txt` or similar

**`schedule`**
- `interval: "weekly"` - Check weekly
- `day: "monday"` - Specifically on Mondays
- `timezone: "Asia/Jakarta"` - Use Jakarta time (UTC+7)

**`groups.python-dependencies`**
- Group name: `python-dependencies`
- `patterns: ["*"]` - Match all packages
- `update-types: ["minor", "patch"]` - **Only** group minor and patch updates

**What this means:**
- **Minor/Patch updates** → Grouped into **1 PR** (e.g., `fastapi 0.110.0 → 0.111.0`)
- **Major updates** → **Separate PRs** (e.g., `pydantic 1.x → 2.x`)

---

### 3. Multiple Python Services

```yaml
# FastAPI - MySQL Service
- package-ecosystem: "pip"
  directory: "/applications/fast-api/mysql/app"
  schedule:
    interval: "weekly"
  groups:
    python-dependencies:
      patterns:
        - "*"
```

**Each service gets its own update configuration:**
- `/applications/fast-api/mongodb/app`
- `/applications/fast-api/mysql/app`
- `/applications/fast-api/postgresql`
- `/applications/fast-api/rabbitmq-pubsub`

**Why separate entries?**
- Each directory has its own `requirements.txt`
- Dependencies may differ between services
- Allows independent versioning
- Can have different schedules if needed

---

### 4. Docker Images

```yaml
- package-ecosystem: "docker"
  directory: "/applications/fast-api/postgresql"
  schedule:
    interval: "weekly"
```

#### Breakdown:

**`package-ecosystem: "docker"`**
- Monitors `Dockerfile` and `docker-compose.yml`
- Checks for base image updates (e.g., `python:3.11` → `3.12`)

**Example Dockerfile:**
```dockerfile
FROM python:3.11-slim
# Dependabot will detect python:3.11-slim
```

**What gets updated:**
- Base image tags
- Multi-stage build images
- Images in docker-compose services

---

## Dependabot Features

### 1. Version Updates
Automatically creates PRs for dependency updates based on schedule.

### 2. Security Updates
**Always enabled** for public repos, opt-in for private.
- Runs independently of version updates
- Creates PRs **immediately** when vulnerabilities detected
- Labeled with `security`

### 3. Grouped Updates
Combine related updates into single PR:
```yaml
groups:
  production-dependencies:
    patterns:
      - "fastapi"
      - "pydantic"
      - "uvicorn"
```

### 4. Version Strategies

**Default behavior:**
- Updates to latest compatible version within range
- Respects semantic versioning

**Custom strategies:**
```yaml
- package-ecosystem: "npm"
  versioning-strategy: "increase"  # Always increase version
  # or "widen" - expand version range
  # or "increase-if-necessary"
```

### 5. Ignore Conditions

Skip specific versions or dependencies:
```yaml
- package-ecosystem: "pip"
  directory: "/"
  ignore:
    - dependency-name: "django"
      versions: ["4.x"]  # Skip Django 4.x
    - dependency-name: "celery"  # Ignore completely
```

### 6. Reviewers & Assignees

Auto-assign team members:
```yaml
- package-ecosystem: "pip"
  directory: "/"
  reviewers:
    - "octocat"
    - "team-platform"
  assignees:
    - "dekribellyliu"
```

### 7. Labels

Custom PR labels:
```yaml
- package-ecosystem: "pip"
  directory: "/"
  labels:
    - "dependencies"
    - "python"
    - "automated"
```

### 8. Commit Messages

Customize commit format:
```yaml
- package-ecosystem: "pip"
  directory: "/"
  commit-message:
    prefix: "pip"
    prefix-development: "pip-dev"
    include: "scope"
```

Example commit:
```
pip: update fastapi from 0.110.0 to 0.111.0
```

### 9. Pull Request Limits

Control PR volume:
```yaml
- package-ecosystem: "npm"
  directory: "/"
  open-pull-requests-limit: 5  # Max 5 open PRs at once
```

### 10. Milestone

Attach to milestone:
```yaml
- package-ecosystem: "pip"
  directory: "/"
  milestone: 4  # Milestone number
```

---

## Understanding Your Current Configuration

### What's Being Monitored

| Ecosystem | Directory | Schedule | Grouping |
|-----------|-----------|----------|----------|
| GitHub Actions | `/` | Weekly | All actions → 1 PR |
| Python (MongoDB) | `/applications/fast-api/mongodb/app` | Monday (Jakarta) | Minor/Patch → 1 PR |
| Python (MySQL) | `/applications/fast-api/mysql/app` | Weekly | All → 1 PR |
| Python (PostgreSQL) | `/applications/fast-api/postgresql` | Weekly | All → 1 PR |
| Python (RabbitMQ) | `/applications/fast-api/rabbitmq-pubsub` | Weekly | All → 1 PR |
| Docker | `/applications/fast-api/postgresql` | Weekly | None (individual PRs) |

### Expected Behavior

**Monday morning (Jakarta time):**
- Dependabot checks MongoDB app dependencies
- Creates 1 grouped PR for minor/patch updates
- Separate PRs for major updates

**Weekly (random day):**
- Checks all other Python apps
- Checks Docker images
- Checks GitHub Actions

**Anytime (Security):**
- Immediate PRs for security vulnerabilities
- Labeled with `security`
- High priority

---

## Comparing Your Setup to Best Practices

### ✅ Good Practices You're Using

1. **Grouping** - Reduces PR noise
2. **Scheduled updates** - Predictable maintenance
3. **Specific directories** - Targets exact locations
4. **Multiple ecosystems** - Docker + Python + Actions

### 🔧 Potential Improvements

1. **Add `open-pull-requests-limit`** to prevent PR flood
2. **Add labels** for easier filtering
3. **Add reviewers** for auto-assignment
4. **Enable `allow` for specific packages only** (if needed)
5. **Add Docker for other services** (MySQL, MongoDB, RabbitMQ)
6. **Consider daily schedule** for critical apps

---

## Dependabot Commands

You can interact with Dependabot PRs using comments:

### Available Commands

```bash
@dependabot rebase           # Rebase PR
@dependabot recreate         # Recreate PR from scratch
@dependabot merge            # Merge PR (if tests pass)
@dependabot squash and merge # Squash and merge
@dependabot cancel merge     # Cancel auto-merge
@dependabot close            # Close PR and ignore this update
@dependabot ignore this major version      # Skip this major version
@dependabot ignore this minor version      # Skip this minor version
@dependabot ignore this dependency         # Never update this dependency
@dependabot reopen           # Reopen closed PR
```

### Example Usage

In a Dependabot PR comment:
```
@dependabot ignore this minor version
```

This tells Dependabot to skip this specific minor version but continue watching for other updates.

---

## Security Features

### Dependabot Security Updates

**Automatically enabled** for public repositories.

**How it works:**
1. GitHub scans your dependencies
2. Compares against GitHub Advisory Database
3. Creates immediate PR if vulnerability found
4. Labeled with `security`

**Enable for private repos:**
1. Go to **Settings** → **Security & analysis**
2. Enable **Dependabot security updates**

### Dependabot Alerts

View all security alerts:
1. Navigate to **Security** tab
2. Click **Dependabot alerts**
3. See vulnerable dependencies with severity

---

## Monitoring Dependabot

### Check Status

**Via GitHub UI:**
1. **Insights** → **Dependency graph** → **Dependabot**
2. Shows last check time and PR status

**Via Settings:**
1. **Settings** → **Security & analysis**
2. View Dependabot features status

### View Logs

**Dependabot Logs:**
1. Go to **Insights** → **Dependency graph** → **Dependabot**
2. Click on individual update check
3. View detailed logs (success/failure)

### Check Configuration

**Validate syntax:**
- GitHub validates on push
- Errors shown in **Insights** → **Dependency graph** → **Dependabot**
- Invalid config = Dependabot disabled

---

## Troubleshooting

### No PRs Being Created

**Possible causes:**
1. Dependencies already up-to-date
2. Config file in wrong location (must be `.github/dependabot.yml`)
3. Invalid YAML syntax
4. Directory doesn't exist or has no dependency files
5. Schedule hasn't run yet

**Solutions:**
- Check **Insights** → **Dependency graph** → **Dependabot** for errors
- Verify file location: `.github/dependabot.yml`
- Validate YAML syntax online
- Check directory paths are correct

### Too Many PRs

**Solutions:**
1. Use `groups` to combine updates
2. Reduce `open-pull-requests-limit`
3. Change schedule to `monthly`
4. Add `ignore` rules for stable packages

### PRs Not Merging

**Possible causes:**
1. CI/CD tests failing
2. Merge conflicts
3. Branch protection rules
4. Needs manual review

**Solutions:**
- Review test failures in PR
- Use `@dependabot rebase` to fix conflicts
- Check branch protection settings

### Security Updates Not Working

**Check:**
1. **Settings** → **Security & analysis**
2. Ensure **Dependabot security updates** is enabled
3. For private repos, must enable manually

---

## Best Practices

### 1. Start Conservative
```yaml
open-pull-requests-limit: 3  # Limit concurrent PRs
schedule:
  interval: "weekly"          # Not daily
```

### 2. Use Grouping
```yaml
groups:
  all-minor-patch:
    patterns: ["*"]
    update-types: ["minor", "patch"]
```

### 3. Add Labels
```yaml
labels:
  - "dependencies"
  - "automated"
  - "python"
```

### 4. Set Reviewers
```yaml
reviewers:
  - "team:platform-team"
```

### 5. Ignore Stable Versions
```yaml
ignore:
  - dependency-name: "legacy-package"
    versions: ["2.x", "3.x"]
```

### 6. Monitor High-Risk Dependencies
For security-critical packages, consider `daily` schedule:
```yaml
- package-ecosystem: "pip"
  directory: "/auth-service"
  schedule:
    interval: "daily"
```

### 7. Separate Production from Development
```yaml
# Production
- package-ecosystem: "pip"
  directory: "/production"
  schedule:
    interval: "monthly"
  
# Development
- package-ecosystem: "pip"
  directory: "/development"
  schedule:
    interval: "weekly"
```

---

## GitHub Actions Integration

### Auto-merge Dependabot PRs

Create `.github/workflows/dependabot-auto-merge.yml`:

```yaml
name: Dependabot Auto-merge
on: pull_request

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - name: Auto-merge patch updates
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Label Security PRs

```yaml
name: Label Dependabot PRs
on: pull_request

jobs:
  label:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - name: Add high-priority label for security
        if: contains(github.event.pull_request.labels.*.name, 'security')
        run: gh pr edit "$PR_URL" --add-label "high-priority"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Comparing Configurations

### Your Current Setup vs Optimized

#### Current (`.github/dependabot.yml`):
```yaml
- package-ecosystem: "pip"
  directory: "/applications/fast-api/mongodb/app"
  schedule:
    interval: "weekly"
  groups:
    python-dependencies:
      patterns: ["*"]
```

#### Optimized Version:
```yaml
- package-ecosystem: "pip"
  directory: "/applications/fast-api/mongodb/app"
  schedule:
    interval: "weekly"
    day: "monday"
    time: "03:00"
    timezone: "Asia/Jakarta"
  open-pull-requests-limit: 5
  labels:
    - "dependencies"
    - "python"
    - "mongodb-service"
  reviewers:
    - "team:backend-team"
  groups:
    python-dependencies:
      patterns: ["*"]
      update-types: ["minor", "patch"]
  ignore:
    - dependency-name: "boto3"
      update-types: ["version-update:semver-major"]
```

**Added benefits:**
- Specific time for updates (3 AM)
- PR limit to prevent overload
- Auto-labeling for filtering
- Auto-reviewer assignment
- Ignore major boto3 updates (too frequent)

---

## Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Configuration Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Supported Ecosystems](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem)
- [GitHub Advisory Database](https://github.com/advisories)
- [Dependabot Commands](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/managing-pull-requests-for-dependency-updates)

---

## Quick Reference

### Supported Package Ecosystems

- `bundler` - Ruby (Gemfile)
- `cargo` - Rust
- `composer` - PHP
- `docker` - Docker images
- `elm` - Elm
- `github-actions` - GitHub Actions
- `gitsubmodule` - Git submodules
- `gomod` - Go modules
- `gradle` - Java/Kotlin (Gradle)
- `maven` - Java (Maven)
- `mix` - Elixir
- `npm` - JavaScript/Node.js
- `nuget` - .NET
- `pip` - Python
- `pub` - Dart
- `terraform` - Terraform

### Schedule Intervals

- `daily` - Every day
- `weekly` - Once per week
- `monthly` - First day of month

### Update Types

- `version-update:semver-major` - Major versions (1.x → 2.x)
- `version-update:semver-minor` - Minor versions (1.1 → 1.2)
- `version-update:semver-patch` - Patch versions (1.1.1 → 1.1.2)

---

**Your Setup Summary:**

📍 **Location:** `.github/dependabot.yml` (Active)  
🔍 **Monitoring:** GitHub Actions, Python (4 services), Docker  
📅 **Schedule:** Weekly updates  
📦 **Grouping:** Enabled for actions and Python  
🔐 **Security:** Auto-enabled (GitHub native)  
✅ **Status:** Active and running
