Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   NODO SOBERANO (LAUNCHER WINDOWS)   "
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Verificar dependencias
Write-Host "[1/3] Verificando librerias Python..." -ForegroundColor Green
pip install flask requests | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   -> Dependencias OK."
} else {
    Write-Host "   -> Error instalando dependencias." -ForegroundColor Red
    exit
}

# 2. Iniciar el Nodo Gateway (Backend) en segundo plano
Write-Host "[2/3] Arrancando el Motor Blockchain (Backend)..." -ForegroundColor Green
Write-Host "   -> Generando identidad y conectando a la red..."
Write-Host "   -> Logs: 'node_out.log' (Info) y 'node_err.log' (Errores)"

# CORRECCION: Separamos los archivos de log para evitar el error de bloqueo
$nodeProcess = Start-Process -FilePath "python" `
               -ArgumentList "main.py GATEWAY 8100" `
               -PassThru `
               -RedirectStandardOutput "node_out.log" `
               -RedirectStandardError "node_err.log" `
               -WindowStyle Hidden

# Esperar un poco a que el nodo arranque
Start-Sleep -Seconds 3

# Verificamos si el proceso existe y no ha terminado
if ($nodeProcess -and -not $nodeProcess.HasExited) {
    Write-Host "   -> Nodo activo (PID: $($nodeProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   -> El nodo fallo al iniciar. Revisa 'node_err.log' para ver el error." -ForegroundColor Red
    exit
}

# 3. Iniciar el Dashboard (Frontend)
Write-Host "[3/3] Iniciando Interfaz Grafica..." -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   -> ABRE EN TU NAVEGADOR: http://127.0.0.1:5000 " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Presiona CTRL+C para apagar todo."

try {
    # Ejecutamos el dashboard en primer plano
    python clients/web_dashboard/app.py
}
finally {
    # Bloque de limpieza: Se ejecuta al cerrar
    Write-Host "`n Deteniendo sistemas..." -ForegroundColor Red
    if ($nodeProcess -and -not $nodeProcess.HasExited) {
        Stop-Process -Id $nodeProcess.Id -Force
        Write-Host "   -> Nodo detenido."
    }
}