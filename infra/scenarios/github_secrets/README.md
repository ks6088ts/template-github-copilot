# GitHub Secrets and Environment Setup

> **Navigation:** [README](../../../README.md) > [Getting Started](../../../docs/copilot_report_forge/getting_started.md) > GitHub Secrets
>
> **Previous step:** [Azure GitHub OIDC](../azure_github_oidc/README.md)

This Terraform scenario creates and manages GitHub repository environment secrets using the GitHub provider. It sets up secrets for a specified GitHub repository environment, which can be used in GitHub Actions workflows.

## Architecture

```mermaid
flowchart LR
    subgraph Terraform["Terraform"]
        TF["GitHub Provider"]
    end

    subgraph GitHub["GitHub Repository"]
        ENV["Environment<br/>e.g. dev"]
        SEC["Environment Secrets<br/>- ARM_CLIENT_ID<br/>- ARM_SUBSCRIPTION_ID<br/>- ARM_TENANT_ID<br/>- ARM_USE_OIDC<br/>- COPILOT_GITHUB_TOKEN<br/>- SLACK_WEBHOOK_URL"]
        GA["GitHub Actions<br/>Workflow"]
    end

    TF -->|"Create/Update"| ENV
    TF -->|"Manage"| SEC
    GA -->|"Read Secrets"| SEC
```

## Prerequisites

- Terraform CLI (>= 1.6.0)
- GitHub account with repository admin access
- A GitHub Personal Access Token (PAT) with `repo` and `admin:org` scopes (or fine-grained token with environment secrets permission)
- Outputs from the [Azure GitHub OIDC](../azure_github_oidc/README.md) scenario (Step 1)

## How to Use

```shell
# (Optional) Create backend.tf for remote state storage
cat <<EOF > backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "YOUR_RESOURCE_GROUP_NAME"
    storage_account_name = "YOUR_STORAGE_ACCOUNT_NAME"
    container_name       = "YOUR_CONTAINER_NAME"
    key                  = "github_secrets.template-github-copilot_dev.tfstate"
  }
}
EOF

# Set environment variables if Azure backend is used
export ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv)

# Log in to Azure (required for Azure backend)
az login

# (Optional) Confirm the details for the currently logged-in user
az ad signed-in-user show

# --- Gather values from Step 1 (azure_github_oidc) ---
APPLICATION_NAME="template-github-copilot_dev"
APPLICATION_ID=$(az ad sp list --display-name "$APPLICATION_NAME" --query "[0].appId" --output tsv)
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
TENANT_ID=$(az account show --query tenantId --output tsv)

# --- GitHub authentication ---
# Set GITHUB_TOKEN for the GitHub Terraform provider
export GITHUB_TOKEN="YOUR_GITHUB_PAT"

# COPILOT_GITHUB_TOKEN is a separate PAT used by Copilot CLI in GitHub Actions
COPILOT_GITHUB_TOKEN="YOUR_COPILOT_GITHUB_TOKEN"

# SLACK_WEBHOOK_URL is the Slack incoming webhook URL for notifications. e.g. https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL"

cat <<EOF > terraform.tfvars
github_owner = "ks6088ts"
repository_name = "template-github-copilot"
environment_name = "dev"
actions_environment_secrets = [
  {
    name  = "ARM_CLIENT_ID"
    value = "$APPLICATION_ID"
  },
  {
    name  = "ARM_SUBSCRIPTION_ID"
    value = "$SUBSCRIPTION_ID"
  },
  {
    name  = "ARM_TENANT_ID"
    value = "$TENANT_ID"
  },
  {
    name  = "ARM_USE_OIDC"
    value = "true"
  },
  {
    name  = "COPILOT_GITHUB_TOKEN"
    value = "$COPILOT_GITHUB_TOKEN"
  },
  {
    name  = "SLACK_WEBHOOK_URL"
    value = "$SLACK_WEBHOOK_URL"
  }
]
EOF

# Initialize Terraform
terraform init

# Format check (matches CI)
terraform fmt -check

# Validate configuration
terraform validate

# Plan the deployment
terraform plan

# Apply the deployment
terraform apply -auto-approve

# Confirm the output
terraform output

# Destroy the deployment (when no longer needed)
terraform destroy -auto-approve
```

## Outputs

| Output                               | Description                                       |
| ------------------------------------ | ------------------------------------------------- |
| `github_repository_environment_name` | Name of the created GitHub repository environment |
