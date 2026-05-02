terraform {
  required_version = ">= 1.0.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  description = "Azure region donde se desplegarán los recursos"
  type        = string
  default     = "eastus"
}

variable "project_name" {
  description = "Prefijo para los recursos de Azure"
  type        = string
  default     = "enmaskapp"
}

locals {
  normalized_name = regexreplace(lower(var.project_name), "[^a-z0-9]", "")
  storage_name    = substring("${local.normalized_name}${random_id.storage.hex}", 0, 24)
}

resource "random_id" "storage" {
  byte_length = 4
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.project_name}-rg"
  location = var.location
}

resource "azurerm_app_service_plan" "asp" {
  name                = "${var.project_name}-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Basic"
    size = "B1"
  }
}

resource "azurerm_linux_web_app" "backend" {
  name                = "${var.project_name}-api"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_app_service_plan.asp.id

  site_config {
    linux_fx_version = "PYTHON|3.12"
    app_command_line = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "WEBSITES_PORT"                      = "8000"
    "PYTHONUNBUFFERED"                   = "1"
    "REPOSITORY_BACKEND"                 = "memory"
  }
}

resource "azurerm_storage_account" "site" {
  name                     = local.storage_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_blob_public_access = true

  static_website {
    index_document = "index.html"
    error_404_document = "index.html"
  }
}

output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "backend_app_service_name" {
  value = azurerm_linux_web_app.backend.name
}

output "backend_url" {
  value = "https://${azurerm_linux_web_app.backend.default_site_hostname}"
}

output "frontend_static_site_url" {
  value = azurerm_storage_account.site.primary_web_endpoint
}
