# Sistema de Etiquetas Montagem

Sistema web para geração e impressão de etiquetas de montagem usando impressora Zebra ZD220 (45x10mm) com fonte **Calibri Bold**.

## 🎯 Funcionalidades

- 🔍 **Busca por código de barras**: Digite ou escaneie códigos no formato PBS12345
- 📷 **Scanner de câmera**: Use a câmera do dispositivo para ler códigos de barras
- 🖨️ **Impressão com Calibri Bold**: Imprime etiquetas usando fonte Calibri Bold (não fonte padrão Zebra)
- 📱 **Interface responsiva**: Funciona em desktop, tablet e mobile
- 🎯 **Busca automática**: Separa peça e OP do código de barras automaticamente
- 🔄 **Impressão remota**: Suporta impressão local (Windows) e remota (Linux → Windows)
- 🗄️ **Integração PostgreSQL**: Busca dados em banco PostgreSQL corporativo

## 🏗️ Arquitetura do Sistema

### Modo Local (Windows)
```
[Navegador] → [app.py] → [send_to_printer.py] → [Impressora Zebra]
                ↓
         [PostgreSQL]
```

### Modo Remoto (Linux → Windows)
```
[Navegador] → [app.py Linux] → [print_server_calibri.py Windows] → [send_to_printer.py] → [Impressora Zebra]
                ↓                           ↓
         [PostgreSQL]              [Gera imagem Calibri]
```

## 📋 Como Funciona

1. **Código de barras**: Usuário escaneia ou digita código no formato `PBS12345`
2. **Separação**: Sistema separa em `PBS` (peça) e `12345` (OP)
3. **Busca no banco**: 
   - Busca `serial_number` na tabela `controle_serial_number`
   - Busca `projeto` e `veículo` na tabela `dados_uso_geral.dados_op`
4. **Geração da imagem**: Converte texto em imagem usando fonte Calibri Bold
5. **Conversão ZPL**: Converte imagem em comando ZPL (^GFA)
6. **Impressão**: Envia para impressora Zebra via Windows Print Spooler

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
# Linux/Docker (requirements.txt)
flask
psycopg2-binary
python-dotenv
Pillow
requests
cryptography
gunicorn

# Windows (requirements-windows.txt)
# Adicione: pywin32
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Banco de Dados PostgreSQL
DB_HOST=seu_host_postgres
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PSW=sua_senha
DB_PORT=sua_porta

# Servidor de Impressão (para modo remoto)
PRINTER_SERVER_URL=http://10.150.20.123:9021
```

### 3. Executar Aplicação Principal

```bash
# Aplicação web (porta 9020)
python app.py
```

Acesse: `https://10.150.20.123:9020` ou `https://localhost:9020`

### 4. Executar Servidor de Impressão (Windows)

```bash
# Servidor de impressão com Calibri (porta 9021)
python print_server_calibri.py
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: `public.controle_serial_number`
```sql
CREATE TABLE public.controle_serial_number (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(50) NOT NULL,
    part_number VARCHAR(50) NOT NULL,
    op VARCHAR(20) NOT NULL,
    peca VARCHAR(10) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: `dados_uso_geral.dados_op`
```sql
CREATE TABLE dados_uso_geral.dados_op (
    op VARCHAR(20) PRIMARY KEY,
    planta VARCHAR(50),
    codigo_veiculo VARCHAR(50),  -- Projeto
    modelo VARCHAR(100)          -- Veículo
);
```

## 📁 Estrutura de Arquivos

```
etiquetas-montagem/
├── app.py                          # Aplicação Flask principal (porta 9020)
├── print_server_calibri.py         # Servidor de impressão com Calibri (porta 9021)
├── send_to_printer.py              # Script de impressão Zebra (Windows Print Spooler)
├── .env                            # Variáveis de ambiente (não versionado)
├── requirements.txt                # Dependências Python
├── cert.pem / key.pem             # Certificados SSL (gerados automaticamente)
├── controle_serial.db             # Banco SQLite (backup/desenvolvimento)
│
├── templates/
│   └── index.html                 # Interface web principal
│
├── static/
│   ├── css/
│   │   └── style.css              # Estilos CSS
│   ├── js/
│   │   └── app.js                 # JavaScript frontend
│   └── img/
│       └── logo_opera.png         # Logo da empresa
│
├── scripts/                        # Scripts auxiliares
│   ├── calibrar_impressora.py
│   ├── diagnostico_impressora.py
│   ├── teste_impressao.py
│   └── verificar_usb.py
│
└── docs/                          # Documentação
    ├── SOLUCAO_IMPRESSORA.md
    └── REFERENCIA_ESPELHAMENTO.md
```

## 🔌 API Endpoints

### Aplicação Principal (porta 9020)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Interface web principal |
| POST | `/buscar` | Busca dados por código de barras |
| POST | `/imprimir` | Imprime etiqueta com serial específico |
| POST | `/buscar-e-imprimir` | Busca e imprime em uma operação |
| GET | `/test-printer` | Testa impressora |

### Servidor de Impressão (porta 9021)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check do servidor |
| POST | `/print-calibri` | Imprime com fonte Calibri Bold |
| POST | `/print` | Imprime ZPL direto (sem Calibri) |

## 🖨️ Configuração da Impressora Zebra

### Requisitos
- **Modelo**: Zebra ZD220-203dpi ZPL
- **Driver**: ZDesigner ZD220-203dpi ZPL
- **Conexão**: USB (porta USB003)
- **Etiquetas**: 45mm x 10mm (360 dots x 80 dots @ 203dpi)
- **Modo**: Tear-Off (destacar manual)
- **Sensor**: Mark sensing ou Web sensing

### Instalação do Driver
1. Baixe o driver em: https://www.zebra.com/br/pt/support-downloads.html
2. Instale o driver ZDesigner ZD220-203dpi ZPL
3. Configure a impressora como "Zebra PU" (ou ajuste no código)
4. Teste com página de teste do Windows

### Calibração
Se as etiquetas não saírem ou saírem em branco:

```bash
# Método 1: Via script
python calibrar_impressora.py

# Método 2: Manual
# 1. Desligue a impressora
# 2. Segure o botão FEED
# 3. Ligue a impressora (ainda segurando)
# 4. Aguarde LED piscar e solte
# 5. Impressora vai calibrar automaticamente
```

### Diagnóstico
```bash
# Verificar status da impressora
python diagnostico_impressora.py

# Verificar conexão USB
python verificar_usb.py

# Testar impressão
python teste_impressao.py
```

## 🎨 Fonte Calibri Bold

O sistema usa **Calibri Bold** (calibrib.ttf) do Windows para gerar as etiquetas:
- Localização: `C:\Windows\Fonts\calibrib.ttf`
- Tamanho: 29pt (ajustável)
- Conversão: Texto → Imagem PIL → Hex ZPL (^GFA)
- Resultado: Etiquetas com fonte corporativa (não fonte Zebra padrão)

## 🔧 Exemplos de Uso

### Exemplo 1: Buscar e Imprimir via Web
1. Acesse `https://10.150.20.123:9020`
2. Digite ou escaneie: `PBS12345`
3. Sistema mostra:
   - Serial: `V04241125J00001`
   - Peça: `PBS`
   - OP: `12345`
   - Projeto: `514`
   - Veículo: `RAV4`
4. Clique em "Imprimir Etiqueta"

### Exemplo 2: Impressão via API
```python
import requests

# Buscar e imprimir
response = requests.post(
    'https://10.150.20.123:9020/buscar-e-imprimir',
    json={'codigoBarras': 'PBS12345'},
    verify=False
)
print(response.json())
```

### Exemplo 3: Impressão Direta com Calibri
```python
import requests

# Enviar para servidor de impressão
response = requests.post(
    'http://10.150.20.123:9021/print-calibri',
    json={'serial': 'ABC123'}
)
print(response.json())
```

## 🐛 Troubleshooting

### Problema: Etiquetas não saem
**Solução**: Calibre a impressora (veja seção Calibração)

### Problema: Etiquetas saem em branco
**Solução**: Ajuste escuridão (darkness)
```bash
python send_to_printer.py --text "^XA^SD15^XZ"
```

### Problema: Erro de conexão com banco
**Solução**: Verifique `.env` e conectividade com PostgreSQL

### Problema: Fonte Calibri não encontrada
**Solução**: Sistema usa fallback para fonte ZPL padrão automaticamente

### Problema: Certificado SSL inválido
**Solução**: Aceite o certificado self-signed no navegador ou regenere:
```bash
# Deletar certificados antigos
del cert.pem key.pem

# Reiniciar aplicação (gera novos)
python app.py
```

## 🔒 Segurança

- ✅ HTTPS obrigatório (certificado self-signed)
- ✅ Variáveis sensíveis em `.env` (não versionado)
- ✅ Validação de entrada (código de barras)
- ✅ Prepared statements (SQL injection protection)
- ⚠️ Servidor de desenvolvimento (não usar em produção sem WSGI)

## 🚀 Deploy em Produção

### Usando Gunicorn (Linux)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:9020 --certfile=cert.pem --keyfile=key.pem app:app
```

### Usando Docker
```bash
docker-compose up -d
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs da aplicação
tail -f app.log

# Ver logs do servidor de impressão
tail -f print_server.log
```

### Health Check
```bash
# Aplicação principal
curl https://localhost:9020/

# Servidor de impressão
curl http://localhost:9021/health
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.13, Flask
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **Banco de dados**: PostgreSQL (produção), SQLite (desenvolvimento)
- **Scanner**: ZXing JavaScript Library
- **Impressão**: Windows Print Spooler + ZPL
- **Imagem**: Pillow (PIL)
- **SSL**: cryptography
- **Windows API**: pywin32

## 📝 Licença

Sistema desenvolvido para uso interno da **Ópera Security**.

## 👥 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `/docs`
2. Execute scripts de diagnóstico em `/scripts`
3. Verifique logs da aplicação
4. Contate o time de TI

---

**Versão**: 1.0  
**Última atualização**: Novembro 2025  
**Desenvolvido por**: Ópera Security - TI

