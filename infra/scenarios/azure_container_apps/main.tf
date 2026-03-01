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
# Log Analytics Workspace (optional)
# =============================================================================

module "log_analytics" {
  count  = var.enable_log_analytics ? 1 : 0
  source = "../../modules/azure/log_analytics"

  name                = var.name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  tags                = var.tags
}

# =============================================================================
# Container Apps Environment
# =============================================================================

module "container_apps_environment" {
  source = "../../modules/azure/container_apps_environment"

  name                       = var.name
  resource_group_name        = module.resource_group.name
  location                   = module.resource_group.location
  tags                       = var.tags
  log_analytics_workspace_id = var.enable_log_analytics ? module.log_analytics[0].id : null
}

# =============================================================================
# Monolith Container App (API + Copilot CLI in a single image)
# =============================================================================

module "monolith" {
  source = "../../modules/azure/container_apps"

  name                         = var.name
  resource_group_name          = module.resource_group.name
  tags                         = var.tags
  container_app_environment_id = module.container_apps_environment.id
  container_image              = var.container_image
  cpu                          = 0.5
  memory                       = "1Gi"
  min_replicas                 = 0
  max_replicas                 = 3
  target_port                  = 8000
  environment_variables        = var.environment_variables
  secret_environment_variables = var.secret_environment_variables
}

# =============================================================================
# Role Assignments for Managed Identity
# =============================================================================

data "azurerm_subscription" "this" {
}

resource "azurerm_role_assignment" "contributor" {
  scope                = data.azurerm_subscription.this.id
  role_definition_name = "Contributor"
  principal_id         = module.monolith.identity_principal_id
}

resource "azurerm_role_assignment" "storage_blob_data_contributor" {
  scope                = data.azurerm_subscription.this.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = module.monolith.identity_principal_id
}

resource "azurerm_role_assignment" "storage_blob_delegator" {
  scope                = data.azurerm_subscription.this.id
  role_definition_name = "Storage Blob Delegator"
  principal_id         = module.monolith.identity_principal_id
}

resource "azurerm_role_assignment" "cognitive_services_openai_user" {
  scope                = data.azurerm_subscription.this.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.monolith.identity_principal_id
}
