# Guia de Instalação

## 🐳 Instalação via Docker (Linux - Recomendado)

### Pré-requisitos
- Docker instalado
- Docker Compose instalado
- Acesso ao banco PostgreSQL

### Passo a Passo

1. **Clone ou copie os arquivos do projeto**
```bash
cd /opt/apps/etiquetas-montagem
```

2. **Configure o arquivo `.env`**
```bash
nano .env
```

Adicione:
```env
DB_HOST=seu_host_postgres
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PSW=sua_senha
DB_PORT=5432
PRINTER_SERVER_URL=http://10.150.20.123:9021
```

3. **Build e iniciar**
```bash
docker-compose build --no-cache
docker-compose up -d
```

4. **Verificar logs**
```bash
docker-compose logs -f
```

5. **Testar**
```bash
curl -k https://10.150.20.123:9020/
```

## 💻 Instalação Manual (Windows)

### Pré-requisitos
- Python 3.9 ou superior
- Impressora Zebra instalada
- Acesso ao banco PostgreSQL

### Passo a Passo

1. **Instalar dependências**
```bash
pip install -r requirements-windows.txt
```

2. **Configurar `.env`**
Crie arquivo `.env` com:
```env
DB_HOST=seu_host_postgres
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PSW=sua_senha
DB_PORT=5432
```

3. **Iniciar aplicação web**
```bash
python app.py
```

4. **Iniciar servidor de impressão** (em outro terminal)
```bash
python print_server_calibri.py
```

5. **Testar**
Acesse: `https://10.150.20.123:9020`

## 🔧 Configuração Avançada

### Gunicorn (Produção Linux)

Edite `docker-compose.yml`:
```yaml
environment:
  - GUNICORN_WORKERS=4        # Número de workers
  - GUNICORN_THREADS=4        # Threads por worker
  - GUNICORN_TIMEOUT=120      # Timeout em segundos
```

### SSL/HTTPS

Os certificados são gerados automaticamente na primeira execução.

Para usar certificados próprios:
1. Substitua `cert.pem` e `key.pem`
2. Reinicie a aplicação

### Banco de Dados

Estrutura necessária:

```sql
-- Tabela de serial numbers
CREATE TABLE public.controle_serial_number (
    id SERIAL PRIMARY KEY,
    serial_number VARCHAR(50) NOT NULL,
    part_number VARCHAR(50) NOT NULL,
    op VARCHAR(20) NOT NULL,
    peca VARCHAR(10) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dados de OP
CREATE TABLE dados_uso_geral.dados_op (
    op VARCHAR(20) PRIMARY KEY,
    planta VARCHAR(50),
    codigo_veiculo VARCHAR(50),
    modelo VARCHAR(100)
);

-- Índices para performance
CREATE INDEX idx_serial_peca_op ON public.controle_serial_number(peca, op);
CREATE INDEX idx_op ON dados_uso_geral.dados_op(op);
```

## 🖨️ Configuração da Impressora (Windows)

### Instalar Driver Zebra

1. Baixe em: https://www.zebra.com/br/pt/support-downloads.html
2. Instale o driver ZDesigner ZD220-203dpi ZPL
3. Configure nome como "Zebra PU"
4. Teste página de impressão

### Calibrar Impressora

```bash
python calibrar_impressora.py
```

Ou manualmente:
1. Desligue a impressora
2. Segure botão FEED
3. Ligue (ainda segurando)
4. Solte após LED piscar
5. Aguarde calibração

## 🔍 Verificação Pós-Instalação

### Docker
```bash
# Status do container
docker ps

# Logs
docker-compose logs -f

# Teste de conexão
curl -k https://10.150.20.123:9020/
```

### Windows
```bash
# Teste de impressora
python teste_impressao.py

# Diagnóstico
python diagnostico_impressora.py

# Teste de conexão com banco
python -c "from app import get_db_connection; print(get_db_connection())"
```

## 🚨 Problemas Comuns

### Docker: "pywin32 not found"
**Solução**: Use `requirements.txt` (sem pywin32) para Docker

### Windows: "Module not found"
**Solução**: Use `requirements-windows.txt`
```bash
pip install -r requirements-windows.txt
```

### "Cannot connect to database"
**Solução**: Verifique `.env` e conectividade
```bash
# Testar conexão
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### "Port 9020 already in use"
**Solução**: Pare processo existente
```bash
# Linux
lsof -ti:9020 | xargs kill -9

# Windows
netstat -ano | findstr :9020
taskkill /PID <PID> /F
```

### "Certificado SSL inválido"
**Solução**: Aceite certificado self-signed no navegador ou:
```bash
# Regenerar certificados
rm cert.pem key.pem
# Reiniciar aplicação (gera novos)
```

## 📊 Monitoramento

### Logs
```bash
# Docker
docker-compose logs -f

# Windows
# Logs aparecem no console
```

### Health Check
```bash
# Aplicação
curl -k https://10.150.20.123:9020/

# Servidor de impressão (Windows)
curl http://10.150.20.123:9021/health
```

### Métricas
```bash
# Docker
docker stats etiquetas-montagem

# Logs de acesso
tail -f logs/access.log

# Logs de erro
tail -f logs/error.log
```

## 🔄 Atualização

Ver: `ATUALIZAR_APLICACAO.md`

## 📝 Suporte

Para problemas:
1. Verifique logs
2. Execute scripts de diagnóstico
3. Consulte documentação em `/docs`
4. Contate TI

---

**Versão**: 2.0  
**Última atualização**: Novembro 2025
