module "random_string" {
  source = "../../modules/common/random_string"
}

# =============================================================================
# Resource Group
# =============================================================================

module "resource_group" {
  source = "../../modules/azure/resource_group"

  name     = "${var.name}-${module.random_string.result}"
  location = var.location
  tags     = var.tags
}

# =============================================================================
# Microsoft Foundry
# =============================================================================

module "microsoft_foundry" {
  source = "../../modules/azure/microsoft_foundry"

  name              = "msfoundry${module.random_string.result}"
  resource_group_id = module.resource_group.id
  location          = var.location
  tags              = var.tags
  model_deployments = var.model_deployments
}

# =============================================================================
# Storage Account
# =============================================================================

module "storage" {
  source = "../../modules/azure/storage"

  name                     = "st${module.random_string.result}"
  storage_account_name     = replace("st${module.random_string.result}", "-", "")
  resource_group_name      = module.resource_group.name
  location                 = module.resource_group.location
  tags                     = var.tags
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type
  is_hns_enabled           = true
  create_queue             = true
}

# =============================================================================
# Azure AI Search
# =============================================================================

module "search" {
  count  = var.deploy_search ? 1 : 0
  source = "../../modules/azure/search"

  search_service_name = "search${module.random_string.result}"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
  sku                 = var.search_sku
  replica_count       = var.search_replica_count
  partition_count     = var.search_partition_count
}
