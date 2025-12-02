"""
Script para iniciar o servidor de impressão em background (sem janela)
Arquivo .pyw executa sem mostrar terminal
"""
import subprocess
import sys
from pathlib import Path

# Diretório do script
script_dir = Path(__file__).parent

# Executar print_server_calibri.py sem mostrar janela
subprocess.Popen([
    sys.executable, 
    str(script_dir / 'print_server_calibri.py')
], 
creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
cwd=script_dir
)