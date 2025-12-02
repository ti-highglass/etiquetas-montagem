"""
Teste de espelhamento direto via ZPL
"""
import subprocess
from pathlib import Path

def test_mirror():
    """Testa espelhamento via comando ZPL"""
    
    # ZPL com espelhamento forçado
    test_zpl = """^XA
^POI
^FO50,50
^A0N,50,50
^FDTESTE ESPELHADO^FS
^PQ1,0,1,Y
^XZ"""
    
    print("Testando espelhamento via ZPL...")
    print(f"ZPL: {test_zpl}")
    
    # Executar send_to_printer
    cmd = ['python', 'send_to_printer.py', '--text', test_zpl]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
    
    print(f"Return code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    
    if result.returncode == 0:
        print("✅ Comando enviado com sucesso")
        print("🖨️ Verifique se a etiqueta saiu ESPELHADA")
    else:
        print("❌ Erro no comando")

if __name__ == '__main__':
    test_mirror()