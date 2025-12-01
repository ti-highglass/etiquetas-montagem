from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras
import re
import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress
import ssl
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import platform

app = Flask(__name__)

# Carregar variáveis do .env
load_dotenv()

def get_db_connection():
    """Conecta ao banco PostgreSQL"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PSW'),
        port=os.getenv('DB_PORT', 5432)
    )
    return conn

def parse_barcode(barcode):
    """Separa o código de barras em peça e OP"""
    # Remove espaços e converte para maiúsculo
    barcode = barcode.strip().upper()
    
    # Padrão: letras seguidas de números (ex: PBS12345)
    match = re.match(r'^([A-Z]+)(\d+)$', barcode)
    if match:
        peca = match.group(1)  # string
        op = match.group(2)    # string que será convertida para int na query
        return peca, op
    
    return None, None

def search_serial_number(peca, op):
    """Busca o serial_number na tabela baseado na peça e OP, e busca projeto/veículo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"[DEBUG] Buscando no banco: peca='{peca}', op='{op}'", flush=True)
        
        # Buscar serial number
        cursor.execute('''
            SELECT serial_number, peca, op
            FROM public.controle_serial_number 
            WHERE peca = %s AND op = %s
            ORDER BY created DESC
            LIMIT 1
        ''', (peca, op))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        print(f"[DEBUG] Serial encontrado: {result}", flush=True)
        
        # Buscar projeto e veículo na tabela dados_uso_geral.dados_op
        print(f"[DEBUG] Buscando projeto e veículo para OP: {op}", flush=True)
        
        cursor.execute('''
            SELECT codigo_veiculo, modelo
            FROM dados_uso_geral.dados_op
            WHERE planta = 'Jarinu' AND op = %s
            LIMIT 1
        ''', (op,))
        
        op_data = cursor.fetchone()
        conn.close()
        
        # Montar resultado
        resultado = {
            'serial_number': result[0],
            'peca': result[1], 
            'op': result[2],
            'projeto': None,
            'veiculo': None
        }
        
        if op_data:
            resultado['projeto'] = op_data[0]  # codigo_veiculo
            resultado['veiculo'] = op_data[1]  # modelo
            print(f"[DEBUG] Projeto: {op_data[0]}, Veículo: {op_data[1]}", flush=True)
        else:
            print(f"[DEBUG] Nenhum projeto/veículo encontrado para OP {op}", flush=True)
        
        return resultado
        
    except Exception as e:
        print(f"[DEBUG] Erro na busca no banco: {str(e)}", flush=True)
        return None

def text_to_zpl_image(text, font_path=r"C:\Windows\Fonts\calibrib.ttf", font_size=27):
    """Converte texto com fonte Calibri em imagem ZPL (espelhado horizontalmente)"""
    try:
        print(f"[DEBUG] Texto original: {text}", flush=True)
        
        # Criar fonte (tamanho 27)
        font = ImageFont.truetype(font_path, font_size)
        
        # Calcular tamanho do texto
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Adicionar padding
        padding = 10
        img_width = text_width + (padding * 2)
        img_height = text_height + (padding * 2)
        
        # Criar imagem em branco (1 bit - preto e branco)
        image = Image.new('1', (img_width, img_height), 1)  # 1 = branco
        draw = ImageDraw.Draw(image)
        
        # Desenhar texto normal
        x = padding
        y = padding - bbox[1]  # Ajustar baseline
        draw.text((x, y), text, font=font, fill=0)  # 0 = preto
        
        print(f"[DEBUG] Texto desenhado (normal, sem espelhamento): {text}", flush=True)
        
        # Converter para bytes ZPL
        # Calcular bytes por linha (arredondado para múltiplo de 8)
        bytes_per_row = (img_width + 7) // 8
        total_bytes = bytes_per_row * img_height
        
        # Converter imagem para hex
        hex_data = []
        for y in range(img_height):
            row_bytes = []
            for x in range(0, img_width, 8):
                byte_val = 0
                for bit in range(8):
                    if x + bit < img_width:
                        pixel = image.getpixel((x + bit, y))
                        if pixel == 0:  # Preto
                            byte_val |= (1 << (7 - bit))
                row_bytes.append(f"{byte_val:02X}")
            hex_data.append(''.join(row_bytes))
        
        hex_string = ''.join(hex_data)
        
        # Calcular posição para centralizar na etiqueta (360 dots de largura)
        x_pos = (360 - img_width) // 2
        y_pos = 15
        
        # Criar comando ZPL
        zpl = (
            f"^XA"
            f"^FO{x_pos},{y_pos}"
            f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_string}"
            f"^FS"
            f"^XZ"
        )
        
        print(f"[DEBUG] Imagem gerada: {img_width}x{img_height} pixels", flush=True)
        print(f"[DEBUG] Posição: X={x_pos}, Y={y_pos}", flush=True)
        
        return zpl
        
    except Exception as e:
        print(f"[DEBUG] Erro ao gerar imagem: {str(e)}", flush=True)
        return None

def print_to_remote_printer(serial_number, printer_server_url):
    """Envia serial para servidor Windows gerar imagem com Calibri e imprimir"""
    try:
        print(f"[DEBUG] ========================================", flush=True)
        print(f"[DEBUG] IMPRESSÃO REMOTA COM CALIBRI", flush=True)
        print(f"[DEBUG] ========================================", flush=True)
        print(f"[DEBUG] Servidor: {printer_server_url}", flush=True)
        print(f"[DEBUG] Serial: {serial_number}", flush=True)
        print(f"[DEBUG] Endpoint: {printer_server_url}/print-calibri", flush=True)
        
        # Criar endpoint customizado para gerar com Calibri
        response = requests.post(
            f"{printer_server_url}/print-calibri",
            json={"serial": serial_number},
            timeout=15
        )
        
        print(f"[DEBUG] Status Code: {response.status_code}", flush=True)
        print(f"[DEBUG] Response: {response.text}", flush=True)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[DEBUG] Resposta do servidor: {result}", flush=True)
            return True, f"Etiqueta impressa na impressora {result.get('printer', 'remota')}"
        else:
            print(f"[DEBUG] Erro {response.status_code}, tentando método padrão...", flush=True)
            # Fallback: enviar ZPL simples
            zpl_fallback = (
                f"^XA"
                f"^LH0,0"
                f"^FO0,20"
                f"^A0N,29,29"
                f"^FB360,1,0,C,0"
                f"^FD{serial_number}^FS"
                f"^PQ1"
                f"^XZ"
            )
            response = requests.post(
                f"{printer_server_url}/print",
                json={"text": zpl_fallback},
                timeout=10
            )
            if response.status_code == 200:
                return True, "Etiqueta impressa (fonte padrão)"
            return False, f"Erro no servidor: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "Timeout ao conectar com servidor de impressão"
    except requests.exceptions.ConnectionError:
        return False, "Não foi possível conectar ao servidor de impressão. Verifique se está rodando."
    except Exception as e:
        return False, f"Erro ao enviar para impressora remota: {str(e)}"

def print_label(serial_number):
    """Imprime etiqueta contínua com serial centralizado usando Calibri"""
    try:
        print(f"[DEBUG] Preparando impressão do serial: {serial_number}", flush=True)
        print(f"[DEBUG] Sistema operacional: {platform.system()}", flush=True)
        
        # Tentar gerar imagem com Calibri (tamanho 29, espelhado)
        # No Linux, não tem Calibri, então usa fonte padrão
        if platform.system() == "Windows":
            zpl_command = text_to_zpl_image(serial_number, font_size=29)
        else:
            zpl_command = None
        
        # Se falhar ou estiver no Linux, usar fonte padrão como fallback
        if not zpl_command:
            print(f"[AVISO] Usando fonte padrão ZPL", flush=True)
            zpl_command = (
                f"^XA"
                f"^LH0,0"
                f"^FO0,20"
                f"^A0N,29,29"
                f"^FB360,1,0,C,0"
                f"^FD{serial_number}^FS"
                f"^PQ1"
                f"^XZ"
            )
        
        print(f"[DEBUG] Comando ZPL gerado ({len(zpl_command)} bytes)", flush=True)
        
        # Verificar se está no Linux e deve usar impressão remota
        # Configurar o IP do servidor de impressão Windows
        PRINTER_SERVER_URL = os.getenv('PRINTER_SERVER_URL', 'http://10.150.20.40:9021')
        
        if platform.system() == "Linux":
            # Impressão remota via HTTP - envia serial para Windows gerar com Calibri
            print(f"[DEBUG] Linux detectado - usando impressão remota com Calibri", flush=True)
            return print_to_remote_printer(serial_number, PRINTER_SERVER_URL)
        else:
            # Impressão local (Windows)
            print(f"[DEBUG] Windows detectado - usando impressão local", flush=True)
            cmd = [
                'python', 'send_to_printer.py',
                '--text', zpl_command
            ]
            
            print(f"[DEBUG] Executando comando: {' '.join(cmd)}", flush=True)
            
            # Executa o comando no diretório do script
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            print(f"[DEBUG] Return code: {result.returncode}", flush=True)
            print(f"[DEBUG] Stdout: {result.stdout}", flush=True)
            print(f"[DEBUG] Stderr: {result.stderr}", flush=True)
            
            if result.returncode == 0:
                return True, "Etiqueta impressa na impressora padrão"
            else:
                return False, f"Erro na impressão: {result.stderr}"
            
    except Exception as e:
        print(f"[DEBUG] Exceção na impressão: {str(e)}", flush=True)
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
        
        print(f"[DEBUG] Recebido código: {codigo_barras}", flush=True)
        
        if not codigo_barras:
            return jsonify({'error': 'Código de barras não informado'}), 400
        
        # Separa peça e OP do código de barras
        peca, op = parse_barcode(codigo_barras)
        print(f"[DEBUG] Peça: {peca}, OP: {op}", flush=True)
        
        if not peca or not op:
            return jsonify({'error': 'Formato de código de barras inválido. Use o formato: PBS12345'}), 400
        
        # Busca o serial number
        resultado = search_serial_number(peca, op)
        
        if not resultado:
            print(f"[BUSCA] Nenhum registro encontrado para Peça: {peca}, OP: {op}", flush=True)
            return jsonify({'error': f'Nenhum registro encontrado para Peça: {peca}, OP: {op}'}), 404
        
        print(f"[BUSCA] Serial encontrado: {resultado['serial_number']} para Peça: {peca}, OP: {op}", flush=True)
        
        return jsonify({
            'success': True,
            'data': resultado,
            'peca': peca,
            'op': op
        })
        
    except Exception as e:
        print(f"[ERRO] {str(e)}", flush=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/imprimir', methods=['POST'])
def imprimir():
    """Endpoint para imprimir etiqueta"""
    try:
        data = request.get_json()
        serial_number = data.get('serialNumber', '').strip()
        
        if not serial_number:
            return jsonify({'error': 'Serial number não informado'}), 400
        
        print(f"[IMPRESSÃO] Iniciando impressão do serial: {serial_number}", flush=True)
        
        # Imprime a etiqueta
        success, message = print_label(serial_number)
        
        if success:
            print(f"[IMPRESSÃO] Sucesso: {serial_number} - {message}")
            return jsonify({'success': True, 'message': message})
        else:
            print(f"[IMPRESSÃO] Erro: {serial_number} - {message}")
            return jsonify({'error': message}), 500
            
    except Exception as e:
        print(f"[IMPRESSÃO] Erro interno: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/test-printer', methods=['GET'])
def test_printer():
    """Endpoint para testar a impressora"""
    try:
        print(f"[TEST] Testando impressora...", flush=True)
        
        # Teste simples
        test_zpl = "^XA^FO50,50^A0N,50,50^FDTeste^FS^XZ"
        
        cmd = ['python', 'send_to_printer.py', '--text', test_zpl]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(f"[TEST] Return code: {result.returncode}", flush=True)
        print(f"[TEST] Stdout: {result.stdout}", flush=True)
        print(f"[TEST] Stderr: {result.stderr}", flush=True)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Teste de impressora executado'})
        else:
            return jsonify({'error': f'Erro no teste: {result.stderr}'}), 500
            
    except Exception as e:
        print(f"[TEST] Erro: {str(e)}", flush=True)
        return jsonify({'error': f'Erro no teste: {str(e)}'}), 500

@app.route('/buscar-e-imprimir', methods=['POST'])
def buscar_e_imprimir():
    """Endpoint que busca e imprime diretamente"""
    try:
        data = request.get_json()
        codigo_barras = data.get('codigoBarras', '').strip()
        
        if not codigo_barras:
            return jsonify({'error': 'Código de barras não informado'}), 400
        
        print(f"[BUSCAR-IMPRIMIR] Código de barras: {codigo_barras}", flush=True)
        
        # Separa peça e OP do código de barras
        peca, op = parse_barcode(codigo_barras)
        
        if not peca or not op:
            return jsonify({'error': 'Formato de código de barras inválido. Use o formato: PBS12345'}), 400
        
        # Busca o serial number
        resultado = search_serial_number(peca, op)
        
        if not resultado:
            print(f"[BUSCAR-IMPRIMIR] Nenhum registro encontrado para Peça: {peca}, OP: {op}")
            return jsonify({'error': f'Nenhum registro encontrado para Peça: {peca}, OP: {op}'}), 404
        
        serial_number = resultado['serial_number']
        print(f"[BUSCAR-IMPRIMIR] Serial encontrado: {serial_number} - Iniciando impressão", flush=True)
        
        # Imprime a etiqueta
        success, message = print_label(serial_number)
        
        if success:
            print(f"[BUSCAR-IMPRIMIR] Sucesso: Serial {serial_number} impresso")
            return jsonify({
                'success': True,
                'message': f'Serial {serial_number} enviado para impressão',
                'serial': serial_number,
                'data': resultado,
                'peca': peca,
                'op': op
            })
        else:
            print(f"[BUSCAR-IMPRIMIR] Erro na impressão: {message}")
            return jsonify({'error': f'Erro na impressão: {message}'}), 500
            
    except Exception as e:
        print(f"[BUSCAR-IMPRIMIR] Erro interno: {str(e)}")
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

# Gerar certificados SSL se não existirem (para Gunicorn)
if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
    print("⚠️  Certificados SSL não encontrados. Gerando certificados self-signed...")
    try:
        generate_self_signed_cert()
        print("✅ Certificados gerados com sucesso!")
    except Exception as e:
        print(f"⚠️  Erro ao gerar certificados: {e}")

if __name__ == '__main__':
    # Criar contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    print("🚀 Iniciando Sistema de Etiquetas Montagem...")
    print("📱 Acesse: https://10.150.20.123:9020")
    print("\n⚠️  Para parar o servidor, pressione Ctrl+C\n")
    
    app.run(debug=True, host='0.0.0.0', port=9020, ssl_context=context)