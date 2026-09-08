# Script para compilar el backend Python en un ejecutable usando PyInstaller
# Asume que estás en la raíz del proyecto.

Write-Host "Instalando dependencias de Python..."
pip install -r python/requirements.txt
pip install pyinstaller

Write-Host "Compilando con PyInstaller..."
pyinstaller --onefile python/api.py --name pdf-sidecar-x86_64-pc-windows-msvc

Write-Host "Moviendo ejecutable al directorio esperado por Tauri..."
$binDir = "src-tauri/bin"
if (!(Test-Path -Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir
}

Move-Item -Path "dist/pdf-sidecar-x86_64-pc-windows-msvc.exe" -Destination "$binDir/pdf-sidecar-x86_64-pc-windows-msvc.exe" -Force

Write-Host "Limpiando archivos de PyInstaller..."
Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist
Remove-Item -Force pdf-sidecar-x86_64-pc-windows-msvc.spec

Write-Host "Compilación de sidecar finalizada con éxito."
