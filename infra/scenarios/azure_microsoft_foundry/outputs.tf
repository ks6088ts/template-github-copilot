output "resource_group_name" {
  value       = module.resource_group.name
  description = "created resource group name"
}

output "microsoft_foundry_account_name" {
  value       = module.microsoft_foundry.account_name
  description = "Microsoft Foundry account name"
}

output "microsoft_foundry_account_endpoint" {
  value       = module.microsoft_foundry.account_endpoint
  description = "Microsoft Foundry account endpoint"
}

output "microsoft_foundry_project_name" {
  value       = module.microsoft_foundry.project_name
  description = "Microsoft Foundry project name"
}

output "search_service_name" {
  value       = var.deploy_search ? module.search[0].name : null
  description = "Azure AI Search service name"
}

output "search_service_endpoint" {
  value       = var.deploy_search ? module.search[0].endpoint : null
  description = "Azure AI Search service endpoint"
}
