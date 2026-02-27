output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "container_app_environment_id" {
  description = "ID of the Container Apps Environment"
  value       = module.container_apps_environment.id
}

output "container_app_environment_name" {
  description = "Name of the Container Apps Environment"
  value       = module.container_apps_environment.name
}

# =============================================================================
# Monolith Container App
# =============================================================================

output "app_id" {
  description = "ID of the Monolith Container App"
  value       = module.monolith.app_id
}

output "app_name" {
  description = "Name of the Monolith Container App"
  value       = module.monolith.app_name
}

output "app_fqdn" {
  description = "FQDN of the Monolith Container App"
  value       = module.monolith.app_fqdn
}

output "app_url" {
  description = "Full URL to access the Monolith Container App"
  value       = module.monolith.app_url
}
