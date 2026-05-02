# Despliegue en Azure desde la terminal

Esta guía explica los pasos para desplegar el proyecto `EnmascaradoDatos` en Azure usando Terraform y Azure CLI. El despliegue cubre:

- Infraestructura con Terraform
- Backend Python en Azure App Service
- Frontend React/Vite como sitio estático en Azure Storage

> Este flujo está diseñado para ejecutarse enteramente desde la terminal.

## 1. Requisitos previos

Asegúrate de tener instalado y configurado:

- `terraform` >= 1.0
- `az` (Azure CLI)
- `npm` / `node` para construir el frontend
- `python` 3.12 para construir el backend

También debes haber iniciado sesión en Azure:

```powershell
az login
```

## 2. Inicializar Terraform

Desde la raíz del proyecto:

```powershell
cd C:\Users\HP\Desktop\EnmascaradoDatos
terraform init
```

## 3. Crear la infraestructura en Azure

Puedes revisar primero el plan y luego aplicarlo:

```powershell
terraform plan -out=plan.tfplan
terraform apply "plan.tfplan"
```

Si quieres aplicar directamente con variables personalizadas:

```powershell
terraform apply -var="location=eastus" -var="project_name=enmaskapp"
```

Al completarse, Terraform mostrará los valores de salida.

## 4. Obtener los nombres/URLs generados

Después de aplicar Terraform, guarda estos valores:

```powershell
terraform output -raw backend_app_service_name
terraform output -raw backend_url
terraform output -raw frontend_static_site_url
```

También necesitarás el nombre del `Resource Group`:

```powershell
terraform output -raw resource_group
```

## 5. Construir y empaquetar el backend

Desde la carpeta `backend`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea un ZIP con todo el backend:

```powershell
cd ..\backend
Compress-Archive -Path * -DestinationPath ..\backend.zip -Force
```

> Si tu terminal tiene `zip`, puedes usar `zip -r ..\backend.zip .` en su lugar.

## 6. Desplegar el backend en Azure App Service

Usa el nombre del App Service generado por Terraform:

```powershell
$rg = "$(terraform output -raw resource_group)"
$appName = "$(terraform output -raw backend_app_service_name)"
az webapp deployment source config-zip --resource-group $rg --name $appName --src ..\backend.zip
```

### 6.1 Configurar CORS para el frontend estático

Una vez que tengas la URL del sitio estático, agrégala a `BACKEND_CORS_ORIGINS`:

```powershell
$frontendUrl = "$(terraform output -raw frontend_static_site_url)"
az webapp config appsettings set --resource-group $rg --name $appName --settings BACKEND_CORS_ORIGINS=$frontendUrl
```

Si quieres mantener el valor en memoria para el backend, asegúrate también de que esté definido:

```powershell
az webapp config appsettings set --resource-group $rg --name $appName --settings REPOSITORY_BACKEND=memory
```

## 7. Construir el frontend

Desde la carpeta `frontend`:

```powershell
cd ..\frontend
npm ci
npm run build
```

Esto generará la carpeta `dist`.

## 8. Desplegar el frontend estático en Azure Storage

Obtén el nombre de la cuenta de almacenamiento desde Terraform si lo agregas como salida, o busca el valor en `main.tf`.

Usa el siguiente comando para publicar el contenido de `dist` en el contenedor `$web`:

```powershell
$storageAccount = "<NOMBRE_DE_LA_CUENTA_DE_ALMACENAMIENTO>"
az storage blob upload-batch --account-name $storageAccount --source .\dist --destination '$web' --auth-mode login
```

Si necesitas la clave de storage:

```powershell
az storage account keys list --resource-group $rg --account-name $storageAccount --output table
```

## 9. Verificar el despliegue

Abre el frontend publicado en el navegador con la URL:

```powershell
terraform output -raw frontend_static_site_url
```

También puedes verificar el backend con:

```powershell
terraform output -raw backend_url
```

## 10. Notas importantes

- El backend está configurado para ejecutarse en `PYTHON|3.12`.
- El frontend se sirve como un sitio estático de Azure Storage.
- Si el backend necesita persistencia real, cambia `REPOSITORY_BACKEND` y añade la configuración de la base de datos en App Service.
- Ajusta el nombre del proyecto con `-var="project_name=<tu-nombre>"` en Terraform si quieres otro prefijo.

---

Con estos pasos deberías poder desplegar la aplicación desde tu terminal usando Azure y Terraform.
