# Sistema de Etiquetas Montagem

Sistema web para geração de etiquetas de montagem usando impressora Zebra 45x10mm.

## Funcionalidades

- 🔍 **Busca por código de barras**: Digite ou escaneie códigos no formato PBS12345
- 📷 **Scanner de câmera**: Use a câmera do dispositivo para ler códigos de barras
- 🖨️ **Impressão direta**: Imprime etiquetas diretamente na impressora Zebra
- 📱 **Interface responsiva**: Funciona em desktop, tablet e mobile
- 🎯 **Busca automática**: Separa peça e OP do código de barras automaticamente

## Como funciona

1. **Código de barras**: O usuário escaneia ou digita um código no formato `PBS12345`
2. **Separação**: O sistema separa em `PBS` (peça) e `12345` (OP)
3. **Busca**: Procura na tabela `controle_serial_number` pelos valores de peça e OP
4. **Impressão**: Imprime o `serial_number` encontrado usando o template Zebra

## Instalação e Uso

```bash
# 1. Instalar dependências
pip install flask

# 2. Executar aplicação (HTTPS para câmera funcionar)
python app.py

# Nota: O sistema gerará certificados SSL automaticamente na primeira execução
# Aceite o aviso de segurança do navegador para certificado self-signed
```

## Estrutura do Banco de Dados

Tabela: `controle_serial_number`
```sql
CREATE TABLE controle_serial_number (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT NOT NULL,    -- Serial que será impresso
    part_number TEXT NOT NULL,      -- Número da peça
    op TEXT NOT NULL,              -- Ordem de produção
    peca TEXT NOT NULL,            -- Código da peça (ex: PBS)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Exemplos de Uso

### Códigos de barras de exemplo:
- `PBS12345` → Busca peça=PBS, op=12345
- `DEF12346` → Busca peça=DEF, op=12346
- `GHI12347` → Busca peça=GHI, op=12347

### Fluxo de trabalho:
1. Abra o sistema no navegador: `https://localhost:9020`
2. Digite ou escaneie o código de barras
3. O sistema mostra os dados encontrados
4. Clique em "Imprimir Etiqueta" para imprimir diretamente

## Configuração da Impressora

O sistema usa o arquivo `send_to_printer.py` para enviar comandos ZPL para a impressora Zebra. Certifique-se de que:

1. A impressora Zebra está instalada no Windows
2. O template `ZEBRA.prn` está configurado corretamente
3. A impressora está definida como padrão ou especificada no código

## Estrutura de Arquivos

```
etiquetas-montagem/
├── app.py                 # Aplicação Flask principal
├── send_to_printer.py    # Script de impressão Zebra
├── ZEBRA.prn            # Template da etiqueta Zebra
├── controle_serial.db   # Banco de dados SQLite
├── requirements.txt     # Dependências Python
├── templates/
│   └── index.html       # Interface web
└── static/
    ├── css/
    │   └── style.css    # Estilos CSS
    ├── js/
    │   └── app.js       # JavaScript frontend
    └── img/
        └── logo_opera.png
```

## API Endpoints

- `GET /` - Interface principal
- `POST /buscar` - Busca dados por código de barras
- `POST /imprimir` - Imprime etiqueta com serial específico
- `POST /buscar-e-imprimir` - Busca e imprime em uma operação

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **Banco de dados**: SQLite
- **Scanner**: ZXing JavaScript Library
- **Impressão**: Windows Print Spooler + ZPL

## Suporte

Para dúvidas ou problemas:
1. Verifique se a impressora Zebra está funcionando
2. Confirme que o banco de dados tem os dados necessários
3. Teste os códigos de barras de exemplo fornecidos

## Licença

Sistema desenvolvido para uso interno da Ópera.