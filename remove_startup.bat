@echo off
echo Removendo servidor da inicialização automática...

set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcut_file=%startup_folder%\Servidor Impressao Etiquetas.lnk"

if exist "%shortcut_file%" (
    del "%shortcut_file%"
    echo ✅ Servidor removido da inicialização automática
) else (
    echo ⚠️ Atalho não encontrado na pasta de inicialização
)

pause