variable "name" {
  description = "Specifies the name"
  type        = string
  default     = "azuremicrosoftfoundry"
}

variable "location" {
  description = "Specifies the location"
  type        = string
  default     = "eastus2"
}

variable "tags" {
  description = "Specifies the tags"
  type        = map(string)
  default = {
    scenario        = "azure_microsoft_foundry"
    owner           = "ks6088ts"
    SecurityControl = "Ignore"
    CostControl     = "Ignore"
  }
}

variable "model_deployments" {
  description = "Specifies the model deployments for Microsoft Foundry"
  type = list(object({
    format   = optional(string, "OpenAI")
    name     = string
    model    = string
    version  = string
    sku_name = optional(string, "GlobalStandard")
    capacity = number
  }))
  default = [
    {
      name     = "gpt-5.1"
      model    = "gpt-5.1"
      version  = "2025-11-13"
      capacity = 450
    },
    {
      name     = "gpt-5"
      model    = "gpt-5"
      version  = "2025-08-07"
      capacity = 450
    },
    {
      name     = "gpt-4o"
      model    = "gpt-4o"
      version  = "2024-11-20"
      capacity = 450
    },
    {
      name     = "text-embedding-3-large"
      model    = "text-embedding-3-large"
      version  = "1"
      capacity = 450
    },
    {
      name     = "text-embedding-3-small"
      model    = "text-embedding-3-small"
      version  = "1"
      capacity = 450
    }
  ]
}

variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.storage_account_tier)
    error_message = "Storage account tier must be Standard or Premium."
  }
}

variable "storage_account_replication_type" {
  description = "Storage account replication type"
  type        = string
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.storage_account_replication_type)
    error_message = "Replication type must be one of: LRS, GRS, RAGRS, ZRS, GZRS, RAGZRS."
  }
}

variable "deploy_search" {
  description = "Whether to deploy Azure AI Search"
  type        = bool
  default     = false
}

variable "search_sku" {
  description = "The pricing tier of the Azure AI Search service"
  type        = string
  default     = "free"

  validation {
    condition     = contains(["free", "basic", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], var.search_sku)
    error_message = "The search_sku must be one of the following values: free, basic, standard, standard2, standard3, storage_optimized_l1, storage_optimized_l2."
  }
}

variable "search_replica_count" {
  description = "Replicas distribute search workloads across the service"
  type        = number
  default     = 1

  validation {
    condition     = var.search_replica_count >= 1 && var.search_replica_count <= 12
    error_message = "The search_replica_count must be between 1 and 12."
  }
}

variable "search_partition_count" {
  description = "Partitions allow for scaling of document count as well as faster indexing"
  type        = number
  default     = 1

  validation {
    condition     = contains([1, 2, 3, 4, 6, 12], var.search_partition_count)
    error_message = "The search_partition_count must be one of the following values: 1, 2, 3, 4, 6, 12."
  }
}
