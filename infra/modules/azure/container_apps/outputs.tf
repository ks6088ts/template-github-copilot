output "app_id" {
  description = "ID of the Container App"
  value       = azurerm_container_app.this.id
}

output "app_name" {
  description = "Name of the Container App"
  value       = azurerm_container_app.this.name
}

output "app_fqdn" {
  description = "FQDN of the Container App"
  value       = var.enable_ingress ? azurerm_container_app.this.ingress[0].fqdn : null
}

output "app_url" {
  description = "Full URL to access the Container App"
  value       = var.enable_ingress ? "https://${azurerm_container_app.this.ingress[0].fqdn}" : null
}

output "identity_principal_id" {
  description = "Principal ID of the system-assigned managed identity"
  value       = try(azurerm_container_app.this.identity[0].principal_id, null)
}
