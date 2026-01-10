# Renovate Bot - Configuration Examples by Technology

A comprehensive guide to Renovate Bot configurations for various programming languages, DevOps tools, and infrastructure components.

## Table of Contents

- [Programming Languages](#programming-languages)
  - [Python](#python)
  - [Go](#go)
  - [Java](#java)
  - [JavaScript/Node.js](#javascriptnodejs)
  - [PHP/Laravel](#phplaravelcomposer)
- [Container & Orchestration](#container--orchestration)
  - [Docker Images](#docker-images)
  - [Kubernetes](#kubernetes)
  - [Helm Charts](#helm-charts)
- [Infrastructure as Code](#infrastructure-as-code)
  - [Terraform](#terraform)
  - [Ansible](#ansible)
  - [CloudFormation](#cloudformation)
- [AWS Services](#aws-services)
  - [AWS Lambda Runtimes](#aws-lambda-runtimes)
  - [RDS Engine Versions](#rds-engine-versions)
  - [ElastiCache Versions](#elasticache-versions)

---

## Programming Languages

### Python

#### Basic Python Dependencies

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "packageRules": [
    {
      "description": "Auto-merge Python patch updates",
      "matchDatasources": ["pypi"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Group all Python minor and patch updates",
      "matchDatasources": ["pypi"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "Python dependencies (non-major)"
    },
    {
      "description": "Separate PRs for Python major updates",
      "matchDatasources": ["pypi"],
      "matchUpdateTypes": ["major"],
      "groupName": null
    },
    {
      "description": "Pin Python package versions",
      "matchDatasources": ["pypi"],
      "rangeStrategy": "pin"
    }
  ]
}
```

#### Python Version Updates

```json
{
  "packageRules": [
    {
      "description": "Track Python runtime version in Dockerfile",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["python"],
      "matchUpdateTypes": ["major"],
      "enabled": true,
      "labels": ["python-upgrade", "breaking-change"]
    },
    {
      "description": "Python minor version auto-update",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["python"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    }
  ]
}
```

#### Python: Specific Packages Scheduling

```json
{
  "packageRules": [
    {
      "description": "Limit AWS SDK updates (boto3, botocore)",
      "matchPackagePatterns": ["^boto"],
      "schedule": ["before 5am on monday"],
      "groupName": "AWS SDK"
    },
    {
      "description": "Pin Django versions for stability",
      "matchPackageNames": ["django"],
      "matchUpdateTypes": ["major"],
      "enabled": false
    },
    {
      "description": "Group all FastAPI ecosystem updates",
      "matchPackagePatterns": ["^fastapi", "^starlette", "^pydantic"],
      "groupName": "FastAPI ecosystem"
    }
  ]
}
```

---

### Go

#### Go Dependencies (go.mod)

```json
{
  "packageRules": [
    {
      "description": "Auto-merge Go patch updates",
      "matchDatasources": ["go"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Group Go minor updates",
      "matchDatasources": ["go"],
      "matchUpdateTypes": ["minor"],
      "groupName": "Go dependencies (minor)"
    },
    {
      "description": "Separate major Go dependency updates",
      "matchDatasources": ["go"],
      "matchUpdateTypes": ["major"],
      "labels": ["go-major-update"]
    }
  ]
}
```

#### Go Version Updates

```json
{
  "packageRules": [
    {
      "description": "Track Go version in go.mod",
      "matchManagers": ["gomod"],
      "matchDepTypes": ["golang"],
      "enabled": true
    },
    {
      "description": "Update Go Docker images",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["golang", "go"],
      "automerge": false,
      "labels": ["golang-version"]
    },
    {
      "description": "Pin Go version to stable releases",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["golang"],
      "allowedVersions": "!/rc/"
    }
  ]
}
```

---

### Java

#### Maven Dependencies

```json
{
  "packageRules": [
    {
      "description": "Group Spring Boot dependencies",
      "matchManagers": ["maven"],
      "matchPackagePatterns": ["^org.springframework"],
      "groupName": "Spring Framework"
    },
    {
      "description": "Auto-merge Java test dependencies patches",
      "matchManagers": ["maven"],
      "matchDepTypes": ["test"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Limit JUnit updates",
      "matchManagers": ["maven"],
      "matchPackagePatterns": ["^org.junit"],
      "schedule": ["every weekend"]
    }
  ]
}
```

#### Gradle Dependencies

```json
{
  "packageRules": [
    {
      "description": "Group all Kotlin dependencies",
      "matchManagers": ["gradle"],
      "matchPackagePatterns": ["^org.jetbrains.kotlin"],
      "groupName": "Kotlin"
    },
    {
      "description": "Android SDK version tracking",
      "matchManagers": ["gradle"],
      "matchPackageNames": ["com.android.tools.build:gradle"],
      "labels": ["android"]
    }
  ]
}
```

#### Java Runtime Versions

```json
{
  "packageRules": [
    {
      "description": "Track Java Docker images",
      "matchDatasources": ["docker"],
      "matchPackagePatterns": ["^openjdk", "^eclipse-temurin", "^amazoncorretto"],
      "groupName": "Java runtime",
      "schedule": ["before 5am on the first day of the month"]
    }
  ]
}
```

---

### JavaScript/Node.js

#### NPM/Yarn Dependencies

```json
{
  "packageRules": [
    {
      "description": "Group all ESLint packages",
      "matchManagers": ["npm"],
      "matchPackagePatterns": ["^eslint", "^@typescript-eslint/"],
      "groupName": "ESLint"
    },
    {
      "description": "Auto-merge dev dependencies patches",
      "matchManagers": ["npm"],
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Pin production dependencies",
      "matchManagers": ["npm"],
      "matchDepTypes": ["dependencies"],
      "rangeStrategy": "pin"
    },
    {
      "description": "Group React ecosystem",
      "matchManagers": ["npm"],
      "matchPackagePatterns": ["^react", "^@testing-library/react"],
      "groupName": "React"
    }
  ]
}
```

#### Node.js Version

```json
{
  "packageRules": [
    {
      "description": "Track Node.js Docker images",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["node"],
      "automerge": false,
      "labels": ["nodejs-version"]
    },
    {
      "description": "Node.js LTS versions only",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["node"],
      "allowedVersions": "/^(18|20|22)\\./",
      "versioning": "node"
    },
    {
      "description": "Update .nvmrc file",
      "matchManagers": ["nvm"],
      "enabled": true
    }
  ]
}
```

---

### PHP/Laravel/Composer

#### Composer Dependencies

```json
{
  "packageRules": [
    {
      "description": "Group Laravel framework packages",
      "matchManagers": ["composer"],
      "matchPackagePatterns": ["^laravel/", "^illuminate/"],
      "groupName": "Laravel Framework"
    },
    {
      "description": "Auto-merge Composer dev dependencies",
      "matchManagers": ["composer"],
      "matchDepTypes": ["require-dev"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Pin production Composer packages",
      "matchManagers": ["composer"],
      "matchDepTypes": ["require"],
      "rangeStrategy": "pin"
    },
    {
      "description": "Symfony components grouping",
      "matchManagers": ["composer"],
      "matchPackagePatterns": ["^symfony/"],
      "groupName": "Symfony components"
    }
  ]
}
```

#### PHP Version

```json
{
  "packageRules": [
    {
      "description": "Track PHP Docker images",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["php"],
      "labels": ["php-version"]
    },
    {
      "description": "Only stable PHP releases",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["php"],
      "allowedVersions": "!/rc|beta|alpha/"
    }
  ]
}
```

---

## Container & Orchestration

### Docker Images

#### General Docker Image Updates

```json
{
  "packageRules": [
    {
      "description": "Enable Docker image updates",
      "matchDatasources": ["docker"],
      "enabled": true
    },
    {
      "description": "Group base OS images",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["ubuntu", "debian", "alpine", "amazonlinux"],
      "groupName": "Base OS images",
      "schedule": ["before 5am on monday"]
    },
    {
      "description": "Pin Docker images to specific versions",
      "matchDatasources": ["docker"],
      "rangeStrategy": "pin"
    },
    {
      "description": "Use digest pinning for production images",
      "matchDatasources": ["docker"],
      "matchFileNames": ["**/production/**"],
      "pinDigests": true
    }
  ]
}
```

#### Docker Compose Updates

```json
{
  "packageRules": [
    {
      "description": "Update docker-compose service images",
      "matchManagers": ["docker-compose"],
      "enabled": true,
      "automerge": false
    },
    {
      "description": "Group database images in docker-compose",
      "matchManagers": ["docker-compose"],
      "matchPackageNames": ["postgres", "mysql", "redis", "mongodb"],
      "groupName": "Database images"
    }
  ]
}
```

#### Dockerfile Multi-stage Builds

```json
{
  "packageRules": [
    {
      "description": "Update build stage base images",
      "matchManagers": ["dockerfile"],
      "matchFileNames": ["**/Dockerfile"],
      "enabled": true,
      "labels": ["docker", "base-image"]
    }
  ]
}
```

---

### Kubernetes

#### Kubernetes Cluster Versions

```json
{
  "regexManagers": [
    {
      "description": "Track Kubernetes cluster versions in Terraform",
      "fileMatch": ["(^|/)terraform/.*\\.tf$"],
      "matchStrings": [
        "cluster_version\\s*=\\s*\"(?<currentValue>.*?)\"\\s*#\\s*renovate:\\s*datasource=(?<datasource>.*?)\\s+depName=(?<depName>.*?)"
      ],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "kubernetes/kubernetes"
    },
    {
      "description": "Track EKS cluster versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "version\\s*=\\s*\"(?<currentValue>\\d+\\.\\d+)\".*?#.*?eks"
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "amazon-eks",
      "versioningTemplate": "loose"
    }
  ],
  "packageRules": [
    {
      "description": "Kubernetes version updates with caution",
      "matchDatasources": ["github-releases", "endoflife-date"],
      "matchPackageNames": ["kubernetes/kubernetes", "amazon-eks"],
      "labels": ["kubernetes-upgrade", "review-required"],
      "automerge": false
    }
  ]
}
```

#### Kubernetes Manifests (Container Images)

```json
{
  "regexManagers": [
    {
      "description": "Update container images in Kubernetes YAML",
      "fileMatch": ["(^|/)kubernetes/.*\\.ya?ml$"],
      "matchStrings": [
        "image:\\s*(?<depName>.*?):(?<currentValue>.*?)\\s"
      ],
      "datasourceTemplate": "docker"
    }
  ],
  "packageRules": [
    {
      "description": "Group Kubernetes workload images",
      "matchFileNames": ["kubernetes/**"],
      "groupName": "Kubernetes workload images"
    }
  ]
}
```

---

### Helm Charts

#### Helm Chart Dependencies

```json
{
  "helm-values": {
    "fileMatch": ["(^|/)values\\.ya?ml$"]
  },
  "packageRules": [
    {
      "description": "Update Helm chart dependencies",
      "matchManagers": ["helmv3"],
      "enabled": true
    },
    {
      "description": "Group all monitoring stack Helm charts",
      "matchManagers": ["helmv3"],
      "matchPackagePatterns": ["prometheus", "grafana", "loki", "tempo"],
      "groupName": "Monitoring stack"
    },
    {
      "description": "Auto-merge Helm chart patch versions",
      "matchManagers": ["helmv3"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Track image tags in Helm values.yaml",
      "matchManagers": ["helm-values"],
      "matchFileNames": ["**/values.yaml"],
      "enabled": true
    }
  ]
}
```

#### Helm Chart Versions in ArgoCD

```json
{
  "regexManagers": [
    {
      "description": "Track Helm chart versions in ArgoCD applications",
      "fileMatch": ["(^|/)argocd/.*\\.ya?ml$"],
      "matchStrings": [
        "chart:\\s*(?<depName>.*?)\\n.*?targetRevision:\\s*(?<currentValue>.*?)\\n"
      ],
      "datasourceTemplate": "helm"
    }
  ]
}
```

---

## Infrastructure as Code

### Terraform

#### Terraform Version

```json
{
  "regexManagers": [
    {
      "description": "Track Terraform version in version files",
      "fileMatch": ["(^|/)\\.terraform-version$"],
      "matchStrings": ["(?<currentValue>.*?)\\n"],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "hashicorp/terraform",
      "extractVersionTemplate": "^v(?<version>.*)$"
    },
    {
      "description": "Track required_version in Terraform files",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "required_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "hashicorp/terraform",
      "extractVersionTemplate": "^v(?<version>.*)$"
    }
  ],
  "packageRules": [
    {
      "description": "Terraform version updates",
      "matchDatasources": ["github-releases"],
      "matchPackageNames": ["hashicorp/terraform"],
      "labels": ["terraform-version"],
      "schedule": ["before 5am on the first day of the month"]
    }
  ]
}
```

#### Terraform Modules

```json
{
  "packageRules": [
    {
      "description": "Update Terraform modules from registry",
      "matchManagers": ["terraform"],
      "enabled": true
    },
    {
      "description": "Group AWS Terraform modules",
      "matchManagers": ["terraform"],
      "matchPackagePatterns": ["^terraform-aws-modules/"],
      "groupName": "AWS Terraform modules"
    },
    {
      "description": "Pin Terraform module versions",
      "matchManagers": ["terraform"],
      "rangeStrategy": "pin"
    },
    {
      "description": "Track private Terraform modules from GitHub",
      "matchManagers": ["terraform"],
      "matchPackagePatterns": ["^github.com/your-org/"],
      "enabled": true
    }
  ]
}
```

#### Terraform Provider Versions

```json
{
  "packageRules": [
    {
      "description": "Auto-update Terraform providers",
      "matchManagers": ["terraform"],
      "matchDepTypes": ["provider"],
      "enabled": true
    },
    {
      "description": "Group AWS provider updates",
      "matchManagers": ["terraform"],
      "matchPackageNames": ["hashicorp/aws"],
      "groupName": "Terraform AWS provider",
      "schedule": ["every weekend"]
    },
    {
      "description": "Pin provider versions in production",
      "matchManagers": ["terraform"],
      "matchFileNames": ["**/production/**/*.tf"],
      "matchDepTypes": ["provider"],
      "rangeStrategy": "pin"
    }
  ]
}
```

---

### Ansible

#### Ansible Version

```json
{
  "regexManagers": [
    {
      "description": "Track Ansible version in requirements.txt",
      "fileMatch": ["(^|/)requirements\\.txt$"],
      "matchStrings": [
        "ansible\\s*==\\s*(?<currentValue>.*?)\\n"
      ],
      "datasourceTemplate": "pypi",
      "depNameTemplate": "ansible"
    }
  ],
  "packageRules": [
    {
      "description": "Ansible core updates",
      "matchPackageNames": ["ansible", "ansible-core"],
      "labels": ["ansible-version"]
    }
  ]
}
```

#### Ansible Galaxy Roles

```json
{
  "packageRules": [
    {
      "description": "Update Ansible Galaxy roles",
      "matchManagers": ["ansible-galaxy"],
      "enabled": true
    },
    {
      "description": "Group Ansible role updates",
      "matchManagers": ["ansible-galaxy"],
      "groupName": "Ansible Galaxy roles"
    },
    {
      "description": "Pin Ansible role versions",
      "matchManagers": ["ansible-galaxy"],
      "rangeStrategy": "pin"
    }
  ]
}
```

---

### CloudFormation

#### CloudFormation Template Updates

```json
{
  "regexManagers": [
    {
      "description": "Track AMI IDs in CloudFormation templates",
      "fileMatch": ["(^|/)cloudformation/.*\\.(yaml|yml|json)$"],
      "matchStrings": [
        "ImageId:\\s*(?<currentValue>ami-[a-f0-9]+)\\s*#\\s*renovate:\\s*(?<depName>.*?)"
      ],
      "datasourceTemplate": "aws-ami",
      "packageNameTemplate": "{{{depName}}}"
    },
    {
      "description": "Track Lambda runtime versions in CloudFormation",
      "fileMatch": ["(^|/).*\\.(yaml|yml)$"],
      "matchStrings": [
        "Runtime:\\s*(?<depName>python|nodejs|java|dotnet|ruby|go)(?<currentValue>\\d+(?:\\.\\d+)?)"
      ],
      "datasourceTemplate": "docker",
      "packageNameTemplate": "amazon/aws-lambda-{{{depName}}}"
    }
  ]
}
```

---

## AWS Services

### AWS Lambda Runtimes

#### Lambda Runtime Versions

```json
{
  "regexManagers": [
    {
      "description": "Track Lambda runtime in serverless.yml",
      "fileMatch": ["(^|/)serverless\\.ya?ml$"],
      "matchStrings": [
        "runtime:\\s*(?<depName>python|nodejs|java|dotnet|ruby|go)(?<currentValue>\\d+(?:\\.\\d+)?)"
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "aws-lambda-{{{depName}}}"
    },
    {
      "description": "Track Lambda runtime in SAM templates",
      "fileMatch": ["(^|/)template\\.ya?ml$", "(^|/)sam.*\\.ya?ml$"],
      "matchStrings": [
        "Runtime:\\s*(?<depName>python|nodejs|java|dotnet|ruby|go)(?<currentValue>[\\d.]+)"
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "aws-lambda-{{{depName}}}"
    },
    {
      "description": "Track Lambda runtime in Terraform",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "runtime\\s*=\\s*\"(?<depName>python|nodejs|java|dotnet|ruby|go)(?<currentValue>[\\d.]+)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "aws-lambda-{{{depName}}}"
    }
  ],
  "packageRules": [
    {
      "description": "Lambda runtime updates - review required",
      "matchDatasources": ["endoflife-date"],
      "matchPackagePatterns": ["^aws-lambda-"],
      "labels": ["lambda-runtime", "review-required"],
      "automerge": false
    }
  ]
}
```

#### Lambda Layer Versions

```json
{
  "regexManagers": [
    {
      "description": "Track Lambda layer ARNs",
      "fileMatch": ["(^|/)serverless\\.ya?ml$", "(^|/).*\\.tf$"],
      "matchStrings": [
        "arn:aws:lambda:[^:]+:[^:]+:layer:(?<depName>[^:]+):(?<currentValue>\\d+)"
      ],
      "datasourceTemplate": "aws-lambda-layer",
      "packageNameTemplate": "{{{depName}}}"
    }
  ]
}
```

---

### RDS Engine Versions

#### RDS Database Versions in Terraform

```json
{
  "regexManagers": [
    {
      "description": "Track RDS PostgreSQL versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"postgres\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "postgresql",
      "versioningTemplate": "loose"
    },
    {
      "description": "Track RDS MySQL versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"mysql\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "mysql",
      "versioningTemplate": "loose"
    },
    {
      "description": "Track RDS MariaDB versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"mariadb\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "mariadb",
      "versioningTemplate": "loose"
    }
  ],
  "packageRules": [
    {
      "description": "RDS engine updates - careful review",
      "matchDatasources": ["endoflife-date"],
      "matchPackageNames": ["postgresql", "mysql", "mariadb"],
      "labels": ["rds-version", "database-upgrade", "review-required"],
      "automerge": false,
      "schedule": ["before 5am on the first day of the month"]
    }
  ]
}
```

#### Aurora Versions

```json
{
  "regexManagers": [
    {
      "description": "Track Aurora PostgreSQL versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"aurora-postgresql\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "amazon-rds-postgresql"
    },
    {
      "description": "Track Aurora MySQL versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"aurora-mysql\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "amazon-rds-mysql"
    }
  ]
}
```

---

### ElastiCache Versions

#### ElastiCache Redis & Memcached

```json
{
  "regexManagers": [
    {
      "description": "Track ElastiCache Redis versions in Terraform",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"redis\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "redis/redis",
      "extractVersionTemplate": "^(?<version>\\d+\\.\\d+)"
    },
    {
      "description": "Track ElastiCache Memcached versions",
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine\\s*=\\s*\"memcached\"[\\s\\S]*?engine_version\\s*=\\s*\"(?<currentValue>.*?)\""
      ],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "memcached/memcached",
      "extractVersionTemplate": "^(?<version>\\d+\\.\\d+\\.\\d+)"
    }
  ],
  "packageRules": [
    {
      "description": "ElastiCache version updates",
      "matchPackageNames": ["redis/redis", "memcached/memcached"],
      "labels": ["elasticache-version", "cache-upgrade"],
      "automerge": false,
      "schedule": ["before 5am on monday"]
    }
  ]
}
```

---

## Advanced Configurations

### Complete Multi-Stack Example

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:recommended",
    ":dependencyDashboard",
    ":rebaseStalePrs"
  ],
  "labels": ["dependencies", "renovate"],
  "timezone": "UTC",
  "schedule": ["after 10pm every weekday", "before 5am every weekday"],
  
  "regexManagers": [
    {
      "fileMatch": ["(^|/)\\.terraform-version$"],
      "matchStrings": ["(?<currentValue>.*?)\\n"],
      "datasourceTemplate": "github-releases",
      "depNameTemplate": "hashicorp/terraform",
      "extractVersionTemplate": "^v(?<version>.*)$"
    },
    {
      "fileMatch": ["(^|/).*\\.tf$"],
      "matchStrings": [
        "engine_version\\s*=\\s*\"(?<currentValue>.*?)\"\\s*#\\s*renovate:\\s*(?<depName>.*?)"
      ],
      "datasourceTemplate": "endoflife-date",
      "depNameTemplate": "{{{depName}}}"
    }
  ],
  
  "packageRules": [
    {
      "description": "Auto-merge Python patch updates",
      "matchDatasources": ["pypi"],
      "matchUpdateTypes": ["patch"],
      "automerge": true
    },
    {
      "description": "Group Python dependencies",
      "matchDatasources": ["pypi"],
      "matchUpdateTypes": ["minor", "patch"],
      "groupName": "Python dependencies (non-major)"
    },
    {
      "description": "Group all Docker base images",
      "matchDatasources": ["docker"],
      "matchPackageNames": ["python", "node", "golang", "openjdk"],
      "groupName": "Base Docker images",
      "schedule": ["before 5am on monday"]
    },
    {
      "description": "Kubernetes and Helm updates",
      "matchManagers": ["helmv3", "kubernetes"],
      "labels": ["k8s"],
      "automerge": false
    },
    {
      "description": "Terraform modules and providers",
      "matchManagers": ["terraform"],
      "labels": ["terraform"],
      "schedule": ["every weekend"]
    },
    {
      "description": "AWS Lambda runtime - critical review",
      "matchPackagePatterns": ["^aws-lambda-"],
      "labels": ["critical", "lambda-runtime"],
      "automerge": false,
      "reviewers": ["team:platform-team"]
    },
    {
      "description": "Database version updates - very careful",
      "matchPackageNames": ["postgresql", "mysql", "mariadb", "redis"],
      "labels": ["database-upgrade", "review-required"],
      "minimumReleaseAge": "7 days",
      "automerge": false
    }
  ],
  
  "vulnerabilityAlerts": {
    "labels": ["security"],
    "automerge": true,
    "schedule": ["at any time"]
  }
}
```

---

## Best Practices by Technology

### Python
- Pin versions in production (`requirements.txt`)
- Auto-merge patches for low-risk updates
- Schedule AWS SDK updates to reduce noise
- Group minor/patch updates together

### Go
- Use semantic versioning for modules
- Pin to specific versions in production
- Review major updates carefully

### Java/Maven/Gradle
- Group framework updates (Spring, Jakarta)
- Separate test vs production dependencies
- Review plugin updates separately

### JavaScript/Node.js
- Pin production dependencies
- Auto-merge devDependencies patches
- Use LTS Node.js versions only
- Group ecosystem packages (React, Vue, Angular)

### Docker
- Use digest pinning for production
- Group base images by purpose
- Schedule base OS updates weekly
- Test images in staging first

### Terraform
- Pin module versions in production
- Review provider updates separately
- Schedule weekly for non-critical updates
- Use version constraints wisely

### Kubernetes
- Test cluster upgrades in dev first
- Review breaking changes carefully
- Keep at least N-2 versions
- Update one minor version at a time

### AWS Services
- Minimum 7-day release age for RDS
- Review Lambda runtime migrations
- Monitor EOL dates for services
- Test database upgrades in non-prod first

---

## Troubleshooting

### No Updates Detected

Check if the manager is enabled:
```json
{
  "packageRules": [
    {
      "matchManagers": ["your-manager"],
      "enabled": true
    }
  ]
}
```

### Too Many Updates

Use grouping and scheduling:
```json
{
  "packageRules": [
    {
      "groupName": "all-minor-patch",
      "matchUpdateTypes": ["minor", "patch"],
      "schedule": ["every weekend"]
    }
  ]
}
```

### Custom Version Patterns

Use regex managers for non-standard formats:
```json
{
  "regexManagers": [
    {
      "fileMatch": ["your-file-pattern"],
      "matchStrings": ["your-regex"],
      "datasourceTemplate": "datasource-type",
      "depNameTemplate": "package-name"
    }
  ]
}
```

---

## Resources

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [Package Rules](https://docs.renovatebot.com/configuration-options/#packagerules)
- [Regex Managers](https://docs.renovatebot.com/modules/manager/regex/)
- [Preset Configs](https://docs.renovatebot.com/presets-config/)
- [End-of-Life Dates](https://endoflife.date/)

---

**Last Updated:** January 2026
