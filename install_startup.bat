@echo off
echo Configurando servidor para iniciar automaticamente...

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "current_dir=%~dp0"

echo Criando atalho na pasta de inicialização...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%startup_folder%\Servidor Impressao Etiquetas.lnk'); $Shortcut.TargetPath = '%current_dir%start_print_server.pyw'; $Shortcut.WorkingDirectory = '%current_dir%'; $Shortcut.Save()"

echo ✅ Servidor configurado para iniciar automaticamente
echo O servidor será iniciado toda vez que o Windows iniciar
echo.
echo Para remover: delete o arquivo "Servidor Impressao Etiquetas.lnk" da pasta Startup
pause