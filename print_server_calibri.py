"""Servidor de impressão com suporte a Calibri
Recebe serial number e gera imagem com Calibri Bold antes de imprimir
"""
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path

app = Flask(__name__)

def text_to_zpl_image(text, font_path=r"C:\Windows\Fonts\calibrib.ttf", font_size=29):
    """Converte texto com fonte Calibri em imagem ZPL (espelhado horizontalmente)"""
    try:
        print(f"[DEBUG] Texto original: {text}", flush=True)
        
        # Criar fonte
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
        
        # Espelhar horizontalmente
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        
        print(f"[DEBUG] Texto desenhado e espelhado: {text}", flush=True)
        
        # Converter para bytes ZPL
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
        
        # Criar comando ZPL com espelhamento horizontal
        zpl = (
            f"^XA"
            f"^PMY"
            f"^FO{x_pos},{y_pos}"
            f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_string}"
            f"^FS"
            f"^PQ1,0,1,Y"
            f"^XZ"
        )
        
        print(f"[DEBUG] Imagem gerada: {img_width}x{img_height} pixels")
        print(f"[DEBUG] Posição: X={x_pos}, Y={y_pos}")
        
        return zpl
        
    except Exception as e:
        print(f"[DEBUG] Erro ao gerar imagem: {str(e)}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({"status": "ok", "calibri": "enabled"})

@app.route('/print-calibri', methods=['POST'])
def print_calibri():
    """Endpoint para imprimir com Calibri"""
    try:
        data = request.get_json()
        serial = data.get('serial')
        
        if not serial:
            return jsonify({"error": "Serial não informado"}), 400
        
        print(f"[PRINT-CALIBRI] Recebido serial: {serial}")
        
        # Gerar ZPL com Calibri
        zpl_command = text_to_zpl_image(serial, font_size=29)
        
        if not zpl_command:
            return jsonify({"error": "Falha ao gerar imagem com Calibri"}), 500
        
        print(f"[PRINT-CALIBRI] ZPL gerado: {len(zpl_command)} bytes")
        
        # Imprimir usando send_to_printer.py
        script_dir = Path(__file__).parent.resolve()
        send_to_printer = script_dir / 'send_to_printer.py'
        cmd = ['python', str(send_to_printer), '--text', zpl_command]
        print(f"[PRINT-CALIBRI] Executando: {' '.join(cmd[:2])}")
        print(f"[PRINT-CALIBRI] Diretório: {script_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
        
        print(f"[PRINT-CALIBRI] Return code: {result.returncode}")
        print(f"[PRINT-CALIBRI] Stdout: {result.stdout}")
        print(f"[PRINT-CALIBRI] Stderr: {result.stderr}")
        
        if result.returncode == 0:
            return jsonify({
                "status": "ok",
                "printer": "Zebra PU",
                "font": "Calibri Bold",
                "size": len(zpl_command)
            })
        else:
            return jsonify({"error": f"Erro na impressão: {result.stderr}"}), 500
            
    except Exception as e:
        print(f"[PRINT-CALIBRI] Erro: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/print', methods=['POST'])
def print_zpl():
    """Endpoint padrão para imprimir ZPL direto"""
    try:
        data = request.get_json()
        zpl = data.get('text')
        
        if not zpl:
            return jsonify({"error": "ZPL não informado"}), 400
        
        print(f"[PRINT] Recebido ZPL: {len(zpl)} bytes")
        
        # Imprimir usando send_to_printer.py
        script_dir = Path(__file__).parent.resolve()
        send_to_printer = script_dir / 'send_to_printer.py'
        cmd = ['python', str(send_to_printer), '--text', zpl]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
        
        if result.returncode == 0:
            return jsonify({"status": "ok", "printer": "Zebra PU"})
        else:
            return jsonify({"error": f"Erro na impressão: {result.stderr}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("SERVIDOR DE IMPRESSÃO COM CALIBRI")
    print("="*60)
    print()
    print("Endpoints disponíveis:")
    print("  GET  /health         - Health check")
    print("  POST /print-calibri  - Imprimir com Calibri (envia serial)")
    print("  POST /print          - Imprimir ZPL direto")
    print()
    print("Iniciando servidor na porta 9021...")
    print()
    
    app.run(host='0.0.0.0', port=9021, debug=False)
