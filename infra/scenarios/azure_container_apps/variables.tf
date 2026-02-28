variable "name" {
  description = "Specifies the base name for resources"
  type        = string
  default     = "azurecontainerapps"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "japaneast"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    scenario        = "azure_container_apps"
    owner           = "ks6088ts"
    SecurityControl = "Ignore"
    CostControl     = "Ignore"
  }
}

variable "enable_log_analytics" {
  description = "Whether to create a Log Analytics Workspace and attach it to the Container Apps Environment"
  type        = bool
  default     = false
}

# =============================================================================
# Monolith Container App
# =============================================================================

variable "container_image" {
  description = "Docker image for the monolith service (API + Copilot CLI)"
  type        = string
  default     = "docker.io/ks6088ts/template-github-copilot:latest"

  validation {
    condition     = length(var.container_image) > 0
    error_message = "Container image must not be empty."
  }
}

variable "environment_variables" {
  description = "Environment variables for the monolith container (non-sensitive)"
  type        = map(string)
  default     = {}
}

variable "secret_environment_variables" {
  description = "Sensitive environment variables for the monolith container (stored as secrets)"
  type        = map(string)
  default     = {}
  sensitive   = true
}
