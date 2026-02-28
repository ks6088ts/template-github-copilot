resource "azurerm_container_app" "this" {
  name                         = "app-${var.name}"
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = var.revision_mode
  tags                         = var.tags

  template {
    container {
      name   = "app-${var.name}"
      image  = var.container_image
      cpu    = var.cpu
      memory = var.memory

      dynamic "env" {
        for_each = var.environment_variables
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.secret_environment_variables
        content {
          name        = env.key
          secret_name = lower(replace(env.key, "_", "-"))
        }
      }
    }

    min_replicas = var.min_replicas
    max_replicas = var.max_replicas
  }

  dynamic "secret" {
    for_each = var.secret_environment_variables
    content {
      name  = lower(replace(secret.key, "_", "-"))
      value = secret.value
    }
  }

  dynamic "ingress" {
    for_each = var.enable_ingress ? [1] : []
    content {
      external_enabled = var.external_enabled
      target_port      = var.target_port
      traffic_weight {
        percentage      = 100
        latest_revision = true
      }
    }
  }
}
