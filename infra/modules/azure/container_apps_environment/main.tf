resource "azurerm_container_app_environment" "this" {
  name                       = "env-${var.name}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id
  logs_destination           = var.log_analytics_workspace_id != null ? "log-analytics" : ""
  tags                       = var.tags
}
