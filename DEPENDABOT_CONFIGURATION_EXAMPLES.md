# GitHub Dependabot - Configuration Examples by Technology

A comprehensive collection of Dependabot configurations for various programming languages, DevOps tools, and infrastructure components.

## Table of Contents

- [Programming Languages](#programming-languages)
  - [Python](#python)
  - [Go](#go)
  - [Java](#java)
  - [JavaScript/Node.js](#javascriptnodejs)
  - [PHP/Laravel](#phplaravelcomposer)
  - [Ruby](#ruby)
  - [Rust](#rust)
- [Container & Orchestration](#container--orchestration)
  - [Docker](#docker)
  - [GitHub Actions](#github-actions)
- [Infrastructure as Code](#infrastructure-as-code)
  - [Terraform](#terraform)
- [Additional Ecosystems](#additional-ecosystems)
  - [.NET](#net)
  - [Gradle/Maven](#gradlemaven)

---

## Programming Languages

### Python

#### Basic Python Configuration

```yaml
version: 2
updates:
  # Basic Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:00"
      timezone: "Asia/Jakarta"
```

#### Python with Grouping

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    # Group all minor and patch updates
    groups:
      python-minor-patch:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
```

#### Python: Separate Dev and Production

```yaml
version: 2
updates:
  # Production dependencies
  - package-ecosystem: "pip"
    directory: "/requirements"
    schedule:
      interval: "monthly"  # Less frequent for production
    labels:
      - "dependencies"
      - "production"
    reviewers:
      - "team:platform-team"
    groups:
      production-deps:
        patterns:
          - "*"
        update-types:
          - "patch"  # Only patches for production
    
  # Development dependencies
  - package-ecosystem: "pip"
    directory: "/requirements-dev"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "development"
    groups:
      dev-deps:
        patterns:
          - "*"
```

#### Python: Framework-Specific Grouping

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Group FastAPI ecosystem
      fastapi-stack:
        patterns:
          - "fastapi"
          - "pydantic"
          - "uvicorn"
          - "starlette"
      
      # Group Django ecosystem
      django-stack:
        patterns:
          - "django*"
          - "djangorestframework"
      
      # Group AWS SDK (frequent updates)
      aws-sdk:
        patterns:
          - "boto3"
          - "botocore"
        update-types:
          - "minor"
          - "patch"
      
      # Group testing tools
      testing-tools:
        patterns:
          - "pytest*"
          - "coverage"
          - "mock"
```

#### Python: Ignore Specific Versions

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    ignore:
      # Skip Django 4.x (not ready to migrate)
      - dependency-name: "django"
        versions: ["4.x"]
      
      # Never update this legacy package
      - dependency-name: "old-legacy-lib"
      
      # Skip major updates for stable packages
      - dependency-name: "celery"
        update-types: ["version-update:semver-major"]
      
      # Skip boto3 entirely (too frequent)
      - dependency-name: "boto3"
      - dependency-name: "botocore"
```

#### Python: Multiple Apps/Services

```yaml
version: 2
updates:
  # API Service
  - package-ecosystem: "pip"
    directory: "/services/api"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "api-service"
      - "dependencies"
    groups:
      api-dependencies:
        patterns: ["*"]
        update-types: ["minor", "patch"]
  
  # Worker Service
  - package-ecosystem: "pip"
    directory: "/services/worker"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "worker-service"
      - "dependencies"
    groups:
      worker-dependencies:
        patterns: ["*"]
        update-types: ["minor", "patch"]
  
  # Background Jobs
  - package-ecosystem: "pip"
    directory: "/services/jobs"
    schedule:
      interval: "weekly"
      day: "tuesday"
    labels:
      - "jobs-service"
      - "dependencies"
```

---

### Go

#### Basic Go Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "go"
```

#### Go: Multiple Modules

```yaml
version: 2
updates:
  # Main application
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      go-dependencies:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
  
  # CLI tool
  - package-ecosystem: "gomod"
    directory: "/cmd/cli"
    schedule:
      interval: "weekly"
    groups:
      cli-dependencies:
        patterns:
          - "*"
```

#### Go: Framework Grouping

```yaml
version: 2
updates:
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Gin web framework
      gin-framework:
        patterns:
          - "github.com/gin-gonic/*"
      
      # gRPC stack
      grpc-stack:
        patterns:
          - "google.golang.org/grpc"
          - "google.golang.org/protobuf"
          - "github.com/grpc-ecosystem/*"
      
      # Database drivers
      database-drivers:
        patterns:
          - "gorm.io/gorm"
          - "gorm.io/driver/*"
          - "github.com/go-sql-driver/*"
      
      # AWS SDK
      aws-sdk-go:
        patterns:
          - "github.com/aws/aws-sdk-go-v2*"
```

#### Go: Version Pinning

```yaml
version: 2
updates:
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    # Pin to specific minor versions
    ignore:
      - dependency-name: "k8s.io/*"
        update-types: ["version-update:semver-major"]
      
      - dependency-name: "golang.org/x/*"
        update-types: ["version-update:semver-major"]
```

---

### Java

#### Maven Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "wednesday"
    labels:
      - "dependencies"
      - "java"
      - "maven"
```

#### Maven: Spring Boot Grouping

```yaml
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Spring Framework
      spring-framework:
        patterns:
          - "org.springframework*"
      
      # Spring Boot
      spring-boot:
        patterns:
          - "org.springframework.boot*"
      
      # Testing
      testing-deps:
        patterns:
          - "org.junit*"
          - "org.mockito*"
          - "org.assertj*"
      
      # Database
      database-deps:
        patterns:
          - "com.h2database*"
          - "org.postgresql*"
          - "mysql*"
```

#### Gradle Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "gradle"
    groups:
      gradle-dependencies:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
```

#### Gradle: Android App

```yaml
version: 2
updates:
  # Main app module
  - package-ecosystem: "gradle"
    directory: "/app"
    schedule:
      interval: "weekly"
    groups:
      # AndroidX libraries
      androidx-libs:
        patterns:
          - "androidx.*"
      
      # Google Play Services
      google-services:
        patterns:
          - "com.google.android.gms*"
          - "com.google.firebase*"
      
      # Kotlin
      kotlin-libs:
        patterns:
          - "org.jetbrains.kotlin*"
      
      # Testing
      testing-libs:
        patterns:
          - "junit*"
          - "org.robolectric*"
    
    ignore:
      # Don't update Android Gradle Plugin automatically
      - dependency-name: "com.android.tools.build:gradle"
```

---

### JavaScript/Node.js

#### NPM Basic Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "javascript"
```

#### NPM: Separate Dependencies

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Production dependencies - be careful
      production-deps:
        dependency-type: "production"
        update-types:
          - "patch"
      
      # Development dependencies - more liberal
      development-deps:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"
```

#### NPM: Framework Grouping (React)

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # React ecosystem
      react-ecosystem:
        patterns:
          - "react"
          - "react-dom"
          - "react-router*"
          - "@testing-library/react"
      
      # Build tools
      build-tools:
        patterns:
          - "webpack*"
          - "babel*"
          - "@babel/*"
      
      # Linting & Formatting
      code-quality:
        patterns:
          - "eslint*"
          - "@typescript-eslint/*"
          - "prettier"
      
      # Testing
      testing-tools:
        patterns:
          - "jest"
          - "@testing-library/*"
          - "vitest"
```

#### NPM: Monorepo (Multiple package.json)

```yaml
version: 2
updates:
  # Root workspace
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      workspace-deps:
        patterns: ["*"]
  
  # Frontend package
  - package-ecosystem: "npm"
    directory: "/packages/frontend"
    schedule:
      interval: "weekly"
    labels:
      - "frontend"
    groups:
      frontend-deps:
        patterns: ["*"]
        update-types: ["minor", "patch"]
  
  # Backend package
  - package-ecosystem: "npm"
    directory: "/packages/backend"
    schedule:
      interval: "weekly"
    labels:
      - "backend"
    groups:
      backend-deps:
        patterns: ["*"]
        update-types: ["minor", "patch"]
```

#### NPM: Next.js App

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Next.js framework
      nextjs-framework:
        patterns:
          - "next"
          - "react"
          - "react-dom"
      
      # UI Components
      ui-components:
        patterns:
          - "@headlessui/*"
          - "@heroicons/*"
          - "tailwindcss"
          - "autoprefixer"
          - "postcss"
      
      # API & Data
      api-data:
        patterns:
          - "axios"
          - "swr"
          - "react-query"
```

---

### PHP/Laravel/Composer

#### Composer Basic Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "composer"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "php"
```

#### Composer: Laravel Application

```yaml
version: 2
updates:
  - package-ecosystem: "composer"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      # Laravel framework
      laravel-framework:
        patterns:
          - "laravel/*"
          - "illuminate/*"
      
      # Laravel ecosystem
      laravel-ecosystem:
        patterns:
          - "spatie/*"
          - "barryvdh/*"
      
      # Symfony components
      symfony-components:
        patterns:
          - "symfony/*"
      
      # Development tools
      dev-tools:
        dependency-type: "development"
        patterns:
          - "phpunit/*"
          - "mockery/*"
          - "nunomaduro/*"
    
    ignore:
      # Don't auto-update Laravel major versions
      - dependency-name: "laravel/framework"
        update-types: ["version-update:semver-major"]
```

#### Composer: Separate Environments

```yaml
version: 2
updates:
  # Production dependencies
  - package-ecosystem: "composer"
    directory: "/"
    schedule:
      interval: "monthly"  # Less frequent for production
    groups:
      production-deps:
        dependency-type: "production"
        update-types:
          - "patch"  # Only security patches
    labels:
      - "production"
      - "dependencies"
  
  # Development dependencies
  - package-ecosystem: "composer"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-deps:
        dependency-type: "development"
        update-types:
          - "minor"
          - "patch"
    labels:
      - "development"
      - "dependencies"
```

---

### Ruby

#### Bundler Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "bundler"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "ruby"
```

#### Bundler: Rails Application

```yaml
version: 2
updates:
  - package-ecosystem: "bundler"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Rails framework
      rails-framework:
        patterns:
          - "rails"
          - "actionpack"
          - "actionview"
          - "activerecord"
          - "activesupport"
      
      # Testing
      testing-gems:
        patterns:
          - "rspec*"
          - "factory_bot*"
          - "faker"
      
      # Development tools
      dev-tools:
        patterns:
          - "rubocop*"
          - "pry*"
    
    ignore:
      - dependency-name: "rails"
        update-types: ["version-update:semver-major"]
```

---

### Rust

#### Cargo Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "rust"
```

#### Cargo: Workspace

```yaml
version: 2
updates:
  # Main crate
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      rust-dependencies:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"
  
  # CLI tool crate
  - package-ecosystem: "cargo"
    directory: "/crates/cli"
    schedule:
      interval: "weekly"
```

---

## Container & Orchestration

### Docker

#### Basic Dockerfile Updates

```yaml
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"
```

#### Docker: Multiple Dockerfiles

```yaml
version: 2
updates:
  # Production Dockerfile
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"  # Less frequent for production
    labels:
      - "docker"
      - "production"
    open-pull-requests-limit: 3
  
  # Development Dockerfile
  - package-ecosystem: "docker"
    directory: "/docker/dev"
    schedule:
      interval: "weekly"
    labels:
      - "docker"
      - "development"
  
  # CI/CD Dockerfile
  - package-ecosystem: "docker"
    directory: "/.github/docker"
    schedule:
      interval: "weekly"
    labels:
      - "docker"
      - "ci-cd"
```

#### Docker: Group Base Images

```yaml
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Group Python base images
      python-images:
        patterns:
          - "python*"
      
      # Group Node.js images
      node-images:
        patterns:
          - "node*"
      
      # Group database images
      database-images:
        patterns:
          - "postgres*"
          - "mysql*"
          - "redis*"
          - "mongodb*"
      
      # Group OS base images
      os-images:
        patterns:
          - "ubuntu"
          - "debian"
          - "alpine"
```

#### Docker: Ignore Specific Tags

```yaml
version: 2
updates:
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    ignore:
      # Don't update to latest tag (too risky)
      - dependency-name: "python"
        versions: ["latest"]
      
      # Stay on Python 3.11.x
      - dependency-name: "python"
        versions: ["3.12", "3.13"]
      
      # Don't update alpine versions
      - dependency-name: "alpine"
        update-types: ["version-update:semver-major"]
```

#### Docker Compose

```yaml
version: 2
updates:
  # Docker Compose files
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "docker-compose"
    groups:
      compose-services:
        patterns:
          - "*"
```

---

### GitHub Actions

#### Basic GitHub Actions

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "github-actions"
      - "ci-cd"
```

#### GitHub Actions: Grouped

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "github-actions"
      - "dependencies"
    groups:
      # Group all GitHub Actions updates
      github-actions:
        patterns:
          - "*"
    open-pull-requests-limit: 5
```

#### GitHub Actions: Separate by Type

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Official GitHub actions
      github-official-actions:
        patterns:
          - "actions/*"
      
      # Third-party actions
      third-party-actions:
        patterns:
          - "*"
        exclude-patterns:
          - "actions/*"
```

---

## Infrastructure as Code

### Terraform

#### Basic Terraform Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "terraform"
      - "infrastructure"
```

#### Terraform: Multiple Environments

```yaml
version: 2
updates:
  # Production infrastructure
  - package-ecosystem: "terraform"
    directory: "/terraform/production"
    schedule:
      interval: "monthly"  # Less frequent
    labels:
      - "terraform"
      - "production"
    reviewers:
      - "team:platform-team"
    groups:
      terraform-production:
        patterns:
          - "*"
        update-types:
          - "patch"  # Only patches
  
  # Staging infrastructure
  - package-ecosystem: "terraform"
    directory: "/terraform/staging"
    schedule:
      interval: "weekly"
    labels:
      - "terraform"
      - "staging"
    groups:
      terraform-staging:
        patterns:
          - "*"
  
  # Development infrastructure
  - package-ecosystem: "terraform"
    directory: "/terraform/dev"
    schedule:
      interval: "weekly"
    labels:
      - "terraform"
      - "development"
```

#### Terraform: Provider Grouping

```yaml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # AWS provider
      aws-provider:
        patterns:
          - "hashicorp/aws"
      
      # AWS modules
      aws-modules:
        patterns:
          - "terraform-aws-modules/*"
      
      # Google Cloud
      google-provider:
        patterns:
          - "hashicorp/google"
          - "hashicorp/google-beta"
      
      # Kubernetes
      kubernetes-provider:
        patterns:
          - "hashicorp/kubernetes"
          - "hashicorp/helm"
```

#### Terraform: Ignore Major Versions

```yaml
version: 2
updates:
  - package-ecosystem: "terraform"
    directory: "/"
    schedule:
      interval: "weekly"
    ignore:
      # Don't auto-update major AWS provider versions
      - dependency-name: "hashicorp/aws"
        update-types: ["version-update:semver-major"]
      
      # Don't update specific modules
      - dependency-name: "terraform-aws-modules/vpc/aws"
        update-types: ["version-update:semver-major"]
```

---

## Additional Ecosystems

### .NET

#### NuGet Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "dotnet"
```

#### NuGet: ASP.NET Core

```yaml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # ASP.NET Core framework
      aspnetcore-framework:
        patterns:
          - "Microsoft.AspNetCore*"
          - "Microsoft.Extensions*"
      
      # Entity Framework
      entity-framework:
        patterns:
          - "Microsoft.EntityFrameworkCore*"
      
      # Testing
      testing-packages:
        patterns:
          - "xunit*"
          - "Moq"
          - "FluentAssertions"
```

---

### Gradle/Maven

#### Maven: Spring Cloud

```yaml
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Spring Cloud
      spring-cloud:
        patterns:
          - "org.springframework.cloud*"
      
      # Netflix OSS
      netflix-oss:
        patterns:
          - "com.netflix.*"
      
      # AWS SDK
      aws-sdk:
        patterns:
          - "com.amazonaws*"
          - "software.amazon.awssdk*"
```

---

## Complete Multi-Language Example

### Full-Stack Application

```yaml
version: 2

# Global settings
updates:
  # ==================== FRONTEND ====================
  
  # React Frontend
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:00"
    labels:
      - "dependencies"
      - "frontend"
    reviewers:
      - "team:frontend-team"
    open-pull-requests-limit: 5
    groups:
      react-ecosystem:
        patterns:
          - "react"
          - "react-dom"
          - "react-router*"
      development-tools:
        dependency-type: "development"
        patterns:
          - "*"
  
  # ==================== BACKEND ====================
  
  # Python FastAPI Backend
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "03:00"
    labels:
      - "dependencies"
      - "backend"
      - "python"
    reviewers:
      - "team:backend-team"
    groups:
      fastapi-stack:
        patterns:
          - "fastapi"
          - "pydantic"
          - "uvicorn"
        update-types:
          - "minor"
          - "patch"
      aws-sdk:
        patterns:
          - "boto3"
          - "botocore"
    ignore:
      - dependency-name: "boto3"
        update-types: ["version-update:semver-major"]
  
  # ==================== INFRASTRUCTURE ====================
  
  # Terraform Infrastructure
  - package-ecosystem: "terraform"
    directory: "/infrastructure"
    schedule:
      interval: "monthly"  # Less frequent for infra
    labels:
      - "terraform"
      - "infrastructure"
    reviewers:
      - "team:platform-team"
    groups:
      aws-modules:
        patterns:
          - "terraform-aws-modules/*"
    ignore:
      - dependency-name: "hashicorp/aws"
        update-types: ["version-update:semver-major"]
  
  # ==================== CONTAINERS ====================
  
  # Docker Images
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "docker"
    groups:
      base-images:
        patterns:
          - "python"
          - "node"
          - "nginx"
  
  # ==================== CI/CD ====================
  
  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "github-actions"
      - "ci-cd"
    groups:
      all-actions:
        patterns:
          - "*"
```

---

## Advanced Patterns

### Security-First Configuration

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"  # Check daily for security
    labels:
      - "dependencies"
      - "security"
    open-pull-requests-limit: 10
    # Allow all updates for security
    groups:
      security-updates:
        patterns:
          - "*"
```

### Monorepo Strategy

```yaml
version: 2
updates:
  # Root workspace
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      workspace-deps:
        patterns: ["*"]
  
  # Package 1
  - package-ecosystem: "npm"
    directory: "/packages/api"
    schedule:
      interval: "weekly"
    labels: ["api-service"]
  
  # Package 2
  - package-ecosystem: "npm"
    directory: "/packages/web"
    schedule:
      interval: "weekly"
    labels: ["web-app"]
  
  # Package 3
  - package-ecosystem: "npm"
    directory: "/packages/shared"
    schedule:
      interval: "weekly"
    labels: ["shared-lib"]
```

### Conservative Production Strategy

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "monthly"  # Infrequent updates
      day: "monday"
      time: "02:00"
    labels:
      - "dependencies"
      - "production"
      - "review-required"
    reviewers:
      - "team:senior-engineers"
    assignees:
      - "tech-lead"
    milestone: 4
    open-pull-requests-limit: 3
    groups:
      patch-updates-only:
        patterns:
          - "*"
        update-types:
          - "patch"  # Only patches
    ignore:
      # Never auto-update major versions
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
```

---

## Troubleshooting Configurations

### Debug Configuration

```yaml
version: 2
updates:
  # Minimal config for testing
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"  # Run daily to test quickly
    open-pull-requests-limit: 1  # Limit to one PR
    labels:
      - "test-dependabot"
```

### High-Frequency Testing

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
      time: "09:00"  # Specific time for testing
    open-pull-requests-limit: 20
```

---

## Best Practices Summary

### For Python Projects
✅ Group FastAPI/Django ecosystems  
✅ Separate boto3 due to frequent updates  
✅ Use patch-only for production  
✅ Monthly schedule for stable projects

### For JavaScript Projects
✅ Separate production vs dev dependencies  
✅ Group framework ecosystems (React, Vue, Angular)  
✅ Use stricter rules for production  
✅ Weekly updates for active development

### For Docker
✅ Monthly updates for production images  
✅ Pin to specific major versions  
✅ Group by base image type  
✅ Test in staging first

### For Terraform
✅ Monthly updates for production  
✅ Ignore major provider versions  
✅ Group modules by cloud provider  
✅ Require manual review

### For GitHub Actions
✅ Group all actions together  
✅ Weekly updates sufficient  
✅ Review breaking changes carefully

---

## Resources

- [Dependabot Configuration Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Supported Ecosystems](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#package-ecosystem)
- [GitHub Advisory Database](https://github.com/advisories)
- [Dependabot Commands](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/managing-pull-requests-for-dependency-updates)

---

**Last Updated:** January 2026
