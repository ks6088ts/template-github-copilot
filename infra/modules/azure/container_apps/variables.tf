variable "name" {
  description = "Base name for the Container App"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "container_app_environment_id" {
  description = "ID of the Container App Environment"
  type        = string
}

variable "container_image" {
  description = "Docker image to deploy"
  type        = string
}

variable "cpu" {
  description = "CPU cores allocated to the container"
  type        = number
  default     = 0.25
}

variable "memory" {
  description = "Memory allocated to the container"
  type        = string
  default     = "0.5Gi"
}

variable "min_replicas" {
  description = "Minimum number of replicas"
  type        = number
  default     = 0
}

variable "max_replicas" {
  description = "Maximum number of replicas"
  type        = number
  default     = 3
}

variable "revision_mode" {
  description = "Revision mode for the Container App"
  type        = string
  default     = "Single"
}

variable "enable_ingress" {
  description = "Whether to enable ingress"
  type        = bool
  default     = true
}

variable "external_enabled" {
  description = "Whether ingress is externally enabled"
  type        = bool
  default     = true
}

variable "target_port" {
  description = "Target port for ingress"
  type        = number
  default     = 80
}

variable "environment_variables" {
  description = "Environment variables for the container (non-sensitive)"
  type        = map(string)
  default     = {}
}

variable "secret_environment_variables" {
  description = "Sensitive environment variables for the container (stored as secrets)"
  type        = map(string)
  default     = {}
  sensitive   = true
}
