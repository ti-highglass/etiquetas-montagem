"""
Script para parar o servidor de impressão
"""
import subprocess
import sys

def stop_print_server():
    """Para o servidor de impressão usando taskkill simples"""
    try:
        # Método simples: matar todos os processos python
        kill_cmd = ['taskkill', '/F', '/IM', 'python.exe']
        result = subprocess.run(kill_cmd, capture_output=True, text=True)
        
        if 'SUCCESS' in result.stdout or result.returncode == 0:
            print("✅ Processos Python terminados")
            return True
        
        print("⚠️ Nenhum processo Python encontrado")
        return False
        
    except Exception as e:
        print(f"❌ Erro ao parar servidor: {e}")
        return False

if __name__ == '__main__':
    stop_print_server()
    input("Pressione Enter para sair...")