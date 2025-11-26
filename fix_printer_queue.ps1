# Script para limpar fila travada da impressora Zebra
# Execute como Administrador

Write-Host "=== LIMPEZA DA FILA DA IMPRESSORA ZEBRA ===" -ForegroundColor Cyan
Write-Host ""

$printerName = "Zebra PU"

# 1. Pausar impressora
Write-Host "1. Pausando impressora..." -ForegroundColor Yellow
Suspend-PrinterJob -PrinterName $printerName -ID 66 -ErrorAction SilentlyContinue

# 2. Tentar remover job travado
Write-Host "2. Removendo job travado..." -ForegroundColor Yellow
Remove-PrintJob -PrinterName $printerName -ID 66 -ErrorAction SilentlyContinue

# 3. Remover todos os jobs
Write-Host "3. Removendo todos os jobs..." -ForegroundColor Yellow
Get-PrintJob -PrinterName $printerName | Remove-PrintJob -ErrorAction SilentlyContinue

# 4. Verificar status
Write-Host "4. Verificando status..." -ForegroundColor Yellow
$jobs = Get-PrintJob -PrinterName $printerName
if ($jobs) {
    Write-Host "   Ainda há $($jobs.Count) job(s) na fila" -ForegroundColor Red
    $jobs | Format-Table Id, DocumentName, JobStatus
} else {
    Write-Host "   ✓ Fila limpa!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== INSTRUÇÕES MANUAIS ===" -ForegroundColor Cyan
Write-Host "Se o job 66 ainda estiver travado:"
Write-Host "1. Abra 'Dispositivos e Impressoras' (Win + R, digite 'control printers')"
Write-Host "2. Clique com botão direito em 'Zebra PU'"
Write-Host "3. Selecione 'Ver o que está sendo impresso'"
Write-Host "4. Clique em 'Impressora' > 'Cancelar Todos os Documentos'"
Write-Host "5. Se necessário, desligue e ligue a impressora fisicamente"
Write-Host ""
