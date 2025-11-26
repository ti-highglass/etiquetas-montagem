from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import subprocess
import os
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress
import ssl

app = Flask(__name__)

# Configuração do banco de dados
DATABASE = 'controle_serial.db'



def get_db_connection():
    """Conecta ao banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def parse_barcode(barcode):
    """Separa o código de barras em peça e OP"""
    # Remove espaços e converte para maiúsculo
    barcode = barcode.strip().upper()
    
    # Padrão: letras seguidas de números (ex: PBS12345)
    match = re.match(r'^([A-Z]+)(\d+)$', barcode)
    if match:
        peca = match.group(1)
        op = match.group(2)
        return peca, op
    
    return None, None

def search_serial_number(peca, op):
    """Busca o serial_number na tabela baseado na peça e OP"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT serial_number, part_number, peca, op, created_at 
        FROM controle_serial_number 
        WHERE peca = ? AND op = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (peca, op))
    
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None

def print_label(serial_number):
    """Imprime etiqueta contínua com serial centralizado"""
    try:
        # Comando ZPL para etiqueta contínua 45x10mm com serial centralizado
        zpl_command = f"""^XA
^PW320
^LL80
^FO160,40^A0N,30,30^FH^FD{serial_number}^FS
^XZ"""
        
        # Comando para imprimir usando o send_to_printer.py
        cmd = [
            'python', 'send_to_printer.py',
            '--text', zpl_command
        ]
        
        # Executa o comando no diretório do script
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            return True, "Etiqueta impressa na impressora padrão"
        else:
            return False, f"Erro na impressão: {result.stderr}"
            
    except Exception as e:
        return False, f"Erro ao executar impressão: {str(e)}"

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/buscar', methods=['POST'])
def buscar():
    """Endpoint para buscar dados baseado no código de barras"""
    try:
        data = request.get_json()
        codigo_barras = data.get('codigoBarras', '').strip()
        
        if not codigo_barras:
            return jsonify({'error': 'Código de barras não informado'}), 400
        
        # Separa peça e OP do código de barras
        peca, op = parse_barcode(codigo_barras)
        
        if not peca or not op:
            return jsonify({'error': 'Formato de código de barras inválido. Use o formato: PBS12345'}), 400
        
        # Busca o serial number
        resultado = search_serial_number(peca, op)
        
        if not resultado:
            return jsonify({'error': f'Nenhum registro encontrado para Peça: {peca}, OP: {op}'}), 404
        
        return jsonify({
            'success': True,
            'data': resultado,
            'peca': peca,
            'op': op
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/imprimir', methods=['POST'])
def imprimir():
    """Endpoint para imprimir etiqueta"""
    try:
        data = request.get_json()
        serial_number = data.get('serialNumber', '').strip()
        
        if not serial_number:
            return jsonify({'error': 'Serial number não informado'}), 400
        
        # Imprime a etiqueta
        success, message = print_label(serial_number)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/buscar-e-imprimir', methods=['POST'])
def buscar_e_imprimir():
    """Endpoint que busca e imprime diretamente"""
    try:
        data = request.get_json()
        codigo_barras = data.get('codigoBarras', '').strip()
        
        if not codigo_barras:
            return jsonify({'error': 'Código de barras não informado'}), 400
        
        # Separa peça e OP do código de barras
        peca, op = parse_barcode(codigo_barras)
        
        if not peca or not op:
            return jsonify({'error': 'Formato de código de barras inválido. Use o formato: PBS12345'}), 400
        
        # Busca o serial number
        resultado = search_serial_number(peca, op)
        
        if not resultado:
            return jsonify({'error': f'Nenhum registro encontrado para Peça: {peca}, OP: {op}'}), 404
        
        serial_number = resultado['serial_number']
        
        # Imprime a etiqueta
        success, message = print_label(serial_number)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Etiqueta impressa com sucesso',
                'data': resultado,
                'peca': peca,
                'op': op
            })
        else:
            return jsonify({'error': f'Erro na impressão: {message}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

def generate_self_signed_cert():
    """Gera certificados SSL self-signed usando cryptography"""
    # Gerar chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Criar certificado
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "SP"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "SP"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Opera"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Salvar chave privada
    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Salvar certificado
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

if __name__ == '__main__':
    # Verificar se certificados existem
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("⚠️  Certificados SSL não encontrados. Gerando certificados self-signed...")
        try:
            generate_self_signed_cert()
            print("✅ Certificados gerados com sucesso!")
        except ImportError:
            print("⚠️  Biblioteca cryptography não encontrada. Rodando sem HTTPS...")
            app.run(debug=True, host='0.0.0.0', port=9020)
            exit()
    
    # Criar contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    print("🚀 Iniciando Sistema de Etiquetas Montagem...")
    print("📱 Acesse: https://localhost:9020")
    print("🔗 Na rede local: https://[seu-ip]:9020")
    print("\n⚠️  Para parar o servidor, pressione Ctrl+C\n")
    
    app.run(debug=True, host='0.0.0.0', port=9020, ssl_context=context)